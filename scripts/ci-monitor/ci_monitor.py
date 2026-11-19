"""Monitor de GitHub Actions: diagnostica cada ejecución de CI y avisa con una incidencia.

Lo lanza `.github/workflows/ci-monitor.yml` cuando termina una ejecución del workflow «CI»
(evento `workflow_run`). También se puede usar a mano (ver docs/CI_CD_MONITORING.md):

    python scripts/ci-monitor/ci_monitor.py report --run-id 123 [--dry-run]
    python scripts/ci-monitor/ci_monitor.py diagnose --log-file fallo.log --job e2e

Qué hace con cada ejecución terminada:

- success: si había una incidencia abierta de esa rama, la cierra («fallo ya corregido»).
- cancelled / skipped: no abre nada (una ejecución cancelada no es un fallo).
- failure: lee los logs de los jobs fallidos, encuentra el primer error real, lo clasifica
  (código, configuración o externo) y calcula una firma. Abre una incidencia por rama o, si ya
  hay una, comenta: «recurrente» si la firma es la misma, «fallo nuevo» si es otra.
  Si la rama ya tiene un commit más nuevo que el de la ejecución, no abre nada: es un fallo de un
  commit anterior.

Seguridad: no ejecuta código de la rama que falló (solo lee su API y sus logs), solo usa el token
del workflow con permisos mínimos y trata los logs como datos (se citan en un bloque de código,
recortados). Solo usa la biblioteca estándar.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field

API = "https://api.github.com"
LABEL = "ci-monitor"
MARKER = "<!-- ci-monitor branch={branch} -->"
SIGNATURE_MARKER = "<!-- ci-monitor signature={signature} -->"
MAX_EXCERPT_LINES = 40
MAX_EXCERPT_CHARS = 6000

# --- Diagnóstico (sin red: se prueba con logs guardados) -------------------------------------

TIMESTAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z ?")
ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")

# Incidencias externas al proyecto: red, registros de paquetes, runners de GitHub
EXTERNAL = [
    r"ECONNRESET|ETIMEDOUT|EAI_AGAIN|ENOTFOUND|socket hang up",
    r"Could not resolve host|Temporary failure in name resolution",
    r"(npm ERR!|npm error) (network|code E(TIMEDOUT|CONNRESET|AI_AGAIN))",
    r"Failed to download|Download failure|failed to download",
    r"HTTP Error 5\d\d|returned error: 5\d\d|status code 5\d\d",
    r"50[234] (Bad Gateway|Service Unavailable|Gateway Time-?out)",
    r"API rate limit exceeded|secondary rate limit",
    r"The runner has received a shutdown signal|lost communication with the server",
    r"No space left on device",
    r"toomanyrequests|pull access denied|Error response from daemon",
]

# Errores de configuración de CI o del entorno (dependencias, versiones, variables)
CONFIGURATION = [
    r"Unknown permission",
    r"Executable doesn't exist|Please run the following command to download new browsers",
    r"ModuleNotFoundError|No module named|Cannot find module",
    r"Could not find a version that satisfies|ResolutionImpossible|npm ERR! (code )?ERESOLVE",
    r"Unable to resolve action|Invalid workflow file|is not a valid",
    r"environment variable .* (is )?(not set|missing)|KeyError: '[A-Z_]+'",
]

ERROR_LINE = re.compile(
    r"(##\[error\]|^\s*Error: |^E\s{2,}|Traceback \(most recent call last\)|AssertionError|"
    r"^FAILED |^\s*\d+\) \[(chromium|webkit|firefox)\] ›|npm ERR!|npm error |"
    r"^\s*✖|failed with exit code|Process completed with exit code [1-9])"
)

AREAS = [
    ("WebKit", r"\[webkit\]|--project=webkit|\bwebkit\b"),
    ("Firefox", r"\[firefox\]|\bfirefox\b"),
    ("E2E", r"\[chromium\]|playwright|e2e/"),
    ("Backend", r"pytest|\bbackend\b|ruff|alembic|sqlalchemy|fastapi"),
    ("Cursos", r"\bcursos\b|scripts/courses|_course\.py"),
    ("Dependencias", r"pip-audit|npm audit|npm ci|pip install"),
    ("Seguridad", r"pip-audit|npm audit|gitleaks|semgrep|bandit|vulnerab"),
    ("Base de datos", r"postgres|migration|alembic"),
    ("Frontend", r"tests/unit|node --test|frontend/"),
]


def clean(log: str) -> list[str]:
    """Líneas del log sin marcas de tiempo ni colores."""
    return [ANSI.sub("", TIMESTAMP.sub("", line)).rstrip() for line in log.splitlines()]


def first_error(lines: list[str]) -> tuple[int, str]:
    """Índice y texto del primer error real (no los ##[error] de resumen si hay uno anterior)."""
    for index, line in enumerate(lines):
        if ERROR_LINE.search(line) and not line.strip().startswith("##[error]Process completed"):
            return index, line.strip()
    for index, line in enumerate(lines):
        if ERROR_LINE.search(line):
            return index, line.strip()
    return -1, ""


def normalize(text: str) -> str:
    """Quita lo que cambia entre ejecuciones (números, ids, emails, rutas temporales)."""
    text = re.sub(r"[\w.+-]+@[\w-]+\.[\w.]+", "<email>", text)
    text = re.sub(r"\b[0-9a-f]{7,40}\b", "<hex>", text)
    text = re.sub(r"\d+(\.\d+)?", "<n>", text)
    text = re.sub(r"/(tmp|home/runner)/\S+", "<ruta>", text)
    return re.sub(r"\s+", " ", text).strip().lower()


@dataclass
class Diagnosis:
    job: str
    step: str
    kind: str  # "codigo", "configuracion" o "externo"
    areas: list[str]
    error: str
    excerpt: str
    test: str = ""
    signature: str = field(default="")

    def __post_init__(self) -> None:
        if not self.signature:
            base = f"{self.job}|{self.test}|{normalize(self.error)}"
            self.signature = hashlib.sha1(base.encode()).hexdigest()[:12]


def diagnose(log: str, job: str, step: str = "") -> Diagnosis:
    lines = clean(log)
    index, error = first_error(lines)
    text = "\n".join(lines)
    if any(re.search(p, text) for p in EXTERNAL) and not re.search(r"^\s*\d+\) \[", text, re.M):
        kind = "externo"
    elif any(re.search(p, text) for p in CONFIGURATION):
        kind = "configuracion"
    else:
        kind = "codigo"
    test_match = re.search(r"^\s*(?:\d+\) )?\[(chromium|webkit|firefox)\] › (.+?)\s*$", text, re.M)
    test = f"[{test_match.group(1)}] {test_match.group(2)}" if test_match else ""
    start = max(index - 3, 0) if index >= 0 else max(len(lines) - MAX_EXCERPT_LINES, 0)
    excerpt = "\n".join(lines[start : start + MAX_EXCERPT_LINES])[:MAX_EXCERPT_CHARS]
    # Las áreas salen del job, del paso y del error, no del log entero (que lo menciona todo)
    haystack = f"{job} {step}\n{test}\n{excerpt}"
    areas = [name for name, pattern in AREAS if re.search(pattern, haystack, re.I)] or ["CI"]
    error = re.sub(r"^##\[error\]\s*", "", error)
    if re.match(r"\d+\) \[", error):  # cabecera de Playwright: el mensaje va unas líneas después
        detail = next((x.strip() for x in lines[index + 1 : index + 15] if "Error: " in x), "")
        error = detail or error
    return Diagnosis(
        job=job, step=step, kind=kind, areas=areas, error=error, excerpt=excerpt, test=test
    )


def decide(conclusion: str, issue: dict | None, signatures: list[str], stale: bool) -> str:
    """Qué hacer con una ejecución terminada.

    - "validada": salió bien y no había incidencia abierta.
    - "corregido": salió bien y había una incidencia abierta (se cierra).
    - "cancelada": cancelada u omitida (no es un fallo).
    - "obsoleta": falló un commit que ya no es el último de la rama.
    - "nuevo": fallo sin incidencia abierta, o con firmas distintas a las ya anotadas.
    - "recurrente": las mismas firmas que ya tenía la incidencia abierta.
    """
    if conclusion == "success":
        return "corregido" if issue else "validada"
    if conclusion in {"cancelled", "skipped", "neutral", "action_required", "stale"}:
        return "cancelada"
    if stale:
        return "obsoleta"
    if issue is None:
        return "nuevo"
    known = set(
        re.findall(
            r"ci-monitor signature=([0-9a-f]{12})",
            issue.get("body", "") + issue.get("comments_text", ""),
        )
    )
    return "recurrente" if signatures and set(signatures) <= known else "nuevo"


def fence(text: str) -> str:
    """Cita un texto externo (logs) sin que pueda cerrar el bloque ni mencionar a nadie."""
    safe = text.replace("```", "ˋˋˋ").replace("@", "@​")
    return f"```text\n{safe}\n```"


KIND_TEXT = {
    "codigo": "Error del código o de un test",
    "configuracion": "Error de configuración (CI, dependencias o entorno)",
    "externo": "Incidencia externa (red, paquetes o runner de GitHub): suele bastar con relanzar",
}


def render(run: dict, decision: str, diagnoses: list[Diagnosis], attempt: int = 1) -> str:
    """Cuerpo de la incidencia o del comentario, en español."""
    head = run["head_sha"][:7]
    title = {
        "nuevo": "🔴 ERROR DETECTADO",
        "recurrente": f"🔁 FALLO RECURRENTE (intento {attempt})",
        "corregido": "✅ CORREGIDO",
        "validada": "✅ SUBIDA VALIDADA",
        "cancelada": "⚪ EJECUCIÓN CANCELADA",
        "obsoleta": "⚪ FALLO DE UN COMMIT ANTERIOR",
    }[decision]
    out = [
        f"### {title}",
        "",
        f"- Workflow: {run.get('name', 'CI')} · [ejecución {run['id']}]({run['html_url']})",
        f"- Rama: `{run['head_branch']}` · commit `{head}` · evento `{run.get('event', '')}`",
        f"- Resultado: `{run.get('conclusion')}`",
    ]
    for d in diagnoses:
        out += [
            "",
            f"#### Job `{d.job}`" + (f" · paso «{d.step}»" if d.step else ""),
            f"- Tipo: {KIND_TEXT[d.kind]}",
            f"- Áreas: {', '.join(d.areas)}",
        ]
        if d.test:
            out.append(f"- Test: `{d.test.replace('`', 'ˋ')}`")
        out += [
            f"- Primer error: `{d.error[:300].replace('`', 'ˋ')}`"
            if d.error
            else "- Primer error: (no localizado)",
            "",
            fence(d.excerpt),
            SIGNATURE_MARKER.format(signature=d.signature),
        ]
    if decision in {"nuevo", "recurrente"}:
        out += [
            "",
            "Para corregirlo con Claude Code: abre una sesión en esta rama y pídele «arregla la CI"
            " de esta incidencia». Sigue la sección «CI» de CLAUDE.md (máximo 3 ciclos por"
            " incidencia y sin saltar ni debilitar tests).",
        ]
    return "\n".join(out)


# --- GitHub (API REST con el token del workflow) ----------------------------------------------


class GitHub:
    def __init__(self, repo: str, token: str | None) -> None:
        self.repo = repo
        self.token = token

    def call(self, method: str, path: str, body: dict | None = None, raw: bool = False):
        url = path if path.startswith("http") else f"{API}/repos/{self.repo}{path}"
        data = json.dumps(body).encode() if body is not None else None
        request = urllib.request.Request(url, data=data, method=method)
        request.add_header("Accept", "application/vnd.github+json")
        if self.token:  # sin token solo se puede leer (repositorio público, --dry-run)
            request.add_header("Authorization", f"Bearer {self.token}")
        request.add_header("X-GitHub-Api-Version", "2022-11-28")
        request.add_header("User-Agent", "pld-ci-monitor")
        with urllib.request.urlopen(request, timeout=60) as response:  # noqa: S310 (URL fija de la API)
            payload = response.read()
        if raw:
            return payload.decode("utf-8", "replace")
        return json.loads(payload) if payload else None

    def failed_jobs(self, run_id: int) -> list[dict]:
        jobs = self.call("GET", f"/actions/runs/{run_id}/jobs?per_page=100")["jobs"]
        return [j for j in jobs if j.get("conclusion") == "failure"]

    def job_log(self, job_id: int) -> str:
        try:
            return self.call("GET", f"/actions/jobs/{job_id}/logs", raw=True)
        except urllib.error.HTTPError as error:
            return f"(no se pudo leer el log: HTTP {error.code})"

    def branch_head(self, branch: str) -> str | None:
        try:
            return self.call("GET", f"/branches/{urllib.request.quote(branch, safe='')}")["commit"][
                "sha"
            ]
        except urllib.error.HTTPError:
            return None  # rama de un fork o ya borrada

    def open_issue(self, branch: str) -> dict | None:
        marker = MARKER.format(branch=branch)
        issues = self.call("GET", f"/issues?state=open&labels={LABEL}&per_page=100") or []
        for issue in issues:
            if marker in (issue.get("body") or ""):
                comments = (
                    self.call("GET", f"/issues/{issue['number']}/comments?per_page=100") or []
                )
                issue["comments_text"] = "\n".join(c.get("body") or "" for c in comments)
                issue["attempts"] = 1 + sum(
                    "ci-monitor signature=" in (c.get("body") or "") for c in comments
                )
                return issue
        return None

    def ensure_label(self) -> None:
        try:
            self.call("GET", f"/labels/{LABEL}")
        except urllib.error.HTTPError:
            self.call(
                "POST",
                "/labels",
                {
                    "name": LABEL,
                    "color": "d73a4a",
                    "description": "Fallo de CI detectado por ci-monitor",
                },
            )


def report(gh: GitHub, run_id: int, dry_run: bool = False) -> str:
    run = gh.call("GET", f"/actions/runs/{run_id}")
    branch = run["head_branch"]
    issue = gh.open_issue(branch)
    diagnoses: list[Diagnosis] = []
    stale = False
    if run.get("conclusion") == "failure":
        for job in gh.failed_jobs(run_id):
            step = next(
                (s["name"] for s in job.get("steps", []) if s.get("conclusion") == "failure"), ""
            )
            diagnoses.append(diagnose(gh.job_log(job["id"]), job["name"], step))
        # Solo se compara con la rama si es de este repositorio (la de un fork puede llamarse igual)
        same_repo = (run.get("head_repository") or {}).get("full_name") == gh.repo
        head = gh.branch_head(branch) if same_repo else None
        stale = head is not None and head != run["head_sha"]
    decision = decide(run.get("conclusion") or "", issue, [d.signature for d in diagnoses], stale)
    attempt = (issue or {}).get("attempts", 0) + 1
    body = render(run, decision, diagnoses, attempt)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as handle:
            handle.write(body + "\n")
    print(body)
    if dry_run:
        number = issue["number"] if issue else "ninguna"
        print(f"\n(dry-run) decisión: {decision}; incidencia abierta: {number}")
        return decision
    if decision in {"nuevo", "recurrente"} and issue:
        gh.call("POST", f"/issues/{issue['number']}/comments", {"body": body})
    elif decision == "nuevo":
        gh.ensure_label()
        gh.call(
            "POST",
            "/issues",
            {
                "title": f"CI falla en {branch}",
                "labels": [LABEL],
                "body": MARKER.format(branch=branch) + "\n" + body,
            },
        )
    elif decision == "corregido":
        gh.call("POST", f"/issues/{issue['number']}/comments", {"body": body})
        gh.call(
            "PATCH", f"/issues/{issue['number']}", {"state": "closed", "state_reason": "completed"}
        )
    return decision


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    rep = sub.add_parser(
        "report", help="diagnostica una ejecución y abre, comenta o cierra la incidencia"
    )
    rep.add_argument("--run-id", type=int, required=True)
    rep.add_argument(
        "--repo", default=os.environ.get("GITHUB_REPOSITORY", "Marbi8891/python-learning-dashboard")
    )
    rep.add_argument(
        "--dry-run", action="store_true", help="no escribe en GitHub: solo muestra lo que haría"
    )
    diag = sub.add_parser("diagnose", help="diagnostica un log guardado (sin red)")
    diag.add_argument("--log-file", required=True)
    diag.add_argument("--job", default="")
    diag.add_argument("--step", default="")
    args = parser.parse_args(argv)

    if args.command == "diagnose":
        with open(args.log_file, encoding="utf-8", errors="replace") as handle:
            d = diagnose(handle.read(), args.job, args.step)
        print(json.dumps(d.__dict__, ensure_ascii=False, indent=2))
        return 0
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token and not args.dry_run:
        print("Falta GITHUB_TOKEN (o GH_TOKEN) para escribir en GitHub.", file=sys.stderr)
        return 2
    report(GitHub(args.repo, token), args.run_id, dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
