"""Informe de QA en Markdown: reports/qa/latest-report.md.

Lee lo que han dejado los scripts de QA (reports/qa/results.jsonl, los logs de cada paso y los
JSON de pip-audit, npm audit, Bandit y Gitleaks) y el estado de Git. No ejecuta pruebas ni inventa
resultados: si un dato no está, el informe lo dice.

    python scripts/qa/report.py [--title "..."] [--output ruta.md] [--no-actions]

Estado final:
    PASS     todas las comprobaciones han pasado
    WARNING  nada falla, pero hay avisos o comprobaciones que no se han podido ejecutar (SKIP)
    FAIL     alguna comprobación falla: el cambio no se puede integrar
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = Path(os.environ.get("QA_REPORT_DIR", ROOT / "reports" / "qa"))

ICON = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️", "SKIP": "⏭️"}


def git(*args: str) -> str:
    try:
        out = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True)
        return out.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def load_results() -> list[dict]:
    path = REPORT_DIR / "results.jsonl"
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def load_json(name: str):
    path = REPORT_DIR / name
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8") or "null")
    except json.JSONDecodeError:
        return None


def test_counts(log: Path) -> tuple[int, int, int] | None:
    """(superadas, fallidas, saltadas) de un log de pytest, node --test o Playwright."""
    if not log.exists():
        return None
    text = log.read_text(encoding="utf-8", errors="replace")
    passed = failed = skipped = 0
    found = False
    pytest_line = re.findall(r"=+ (.*?(?:passed|failed|error).*?) in [\d.]+s", text) or re.findall(
        r"^(\d+ (?:passed|failed).*?) in [\d.]+s", text, re.MULTILINE
    )
    if pytest_line:
        found = True
        summary = pytest_line[-1]
        passed = sum(int(n) for n in re.findall(r"(\d+) passed", summary))
        failed = sum(int(n) for n in re.findall(r"(\d+) (?:failed|errors?)", summary))
        skipped = sum(int(n) for n in re.findall(r"(\d+) (?:skipped|xfailed)", summary))
    for key, value in re.findall(r"^# (pass|fail|skipped) (\d+)$", text, re.MULTILINE):
        found = True
        if key == "pass":
            passed += int(value)
        elif key == "fail":
            failed += int(value)
        else:
            skipped += int(value)
    if not pytest_line:
        for n, kind in re.findall(r"^\s+(\d+) (passed|failed|skipped|flaky)\b", text, re.MULTILINE):
            found = True
            if kind == "passed":
                passed += int(n)
            elif kind in ("failed", "flaky"):
                failed += int(n)
            else:
                skipped += int(n)
    return (passed, failed, skipped) if found else None


def vulnerabilities() -> list[str]:
    lines = []
    pip = load_json("pip-audit.json")
    if pip is not None:
        deps = pip.get("dependencies", pip) if isinstance(pip, dict) else pip
        vulns = [(d["name"], d["version"], v["id"]) for d in deps for v in d.get("vulns", [])]
        lines.append(f"pip-audit (requirements.txt): **{len(vulns)}**")
        lines += [f"  - {n} {ver}: {vid}" for n, ver, vid in vulns]
    else:
        lines.append("pip-audit: no ejecutado")
    npm = load_json("npm-audit.json")
    if npm is not None:
        meta = npm.get("metadata", {}).get("vulnerabilities", {})
        total = meta.get("total", 0)
        detail = ", ".join(f"{k}: {v}" for k, v in meta.items() if k != "total" and v)
        lines.append(f"npm audit: **{total}**" + (f" ({detail})" if detail else ""))
    else:
        lines.append("npm audit: no ejecutado")
    bandit = load_json("bandit.json")
    if bandit is not None:
        sev = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for issue in bandit.get("results", []):
            sev[issue["issue_severity"]] = sev.get(issue["issue_severity"], 0) + 1
        lines.append(
            f"Bandit (backend/app): **{sev['HIGH']} altas, {sev['MEDIUM']} medias**, "
            f"{sev['LOW']} bajas (las bajas se revisan, no bloquean)"
        )
    else:
        lines.append("Bandit: no ejecutado")
    leaks = [load_json("gitleaks-dir.json"), load_json("gitleaks-git.json")]
    if any(x is not None for x in leaks):
        found = [f for group in leaks if group for f in group]
        lines.append(f"Gitleaks (árbol de trabajo y commits nuevos): **{len(found)}**")
        # Solo archivo, línea y regla: nunca el valor (Gitleaks se ejecuta con --redact)
        lines += [f"  - {f.get('File')}:{f.get('StartLine')} ({f.get('RuleID')})" for f in found]
    else:
        lines.append("Gitleaks: no ejecutado")
    return lines


def repo_slug() -> str | None:
    url = git("remote", "get-url", "origin")
    match = re.search(r"github\.com[:/]([^/]+/[^/.]+?)(?:\.git)?$", url)
    return match.group(1) if match else None


def actions_status(sha: str) -> list[str]:
    """Estado de GitHub Actions del commit (API pública). Sin red o sin subir: se dice."""
    slug = repo_slug()
    if not slug:
        return ["No consultado: el remoto origin no es de GitHub"]
    if not git("branch", "-r", "--contains", sha):
        return ["El commit aún no está en GitHub: Actions se ejecutará al subirlo y abrir el PR"]
    request = urllib.request.Request(
        f"https://api.github.com/repos/{slug}/commits/{sha}/check-runs?per_page=100",
        headers={"Accept": "application/vnd.github+json", "User-Agent": "pld-qa-report"},
    )
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(request, timeout=10) as response:  # noqa: S310 (URL fija https)
            runs = json.load(response).get("check_runs", [])
    except Exception as error:  # noqa: BLE001 (sin red: el informe lo dice y sigue)
        return [f"No consultado ({type(error).__name__}): revisa la pestaña Checks del PR"]
    if not runs:
        return ["Sin ejecuciones para este commit todavía"]
    out = []
    for run in sorted(runs, key=lambda r: r["name"]):
        state = run["conclusion"] or run["status"]
        out.append(f"{run['name']}: {state}")
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", default="Informe de QA")
    parser.add_argument("--output", default=str(REPORT_DIR / "latest-report.md"))
    parser.add_argument("--no-actions", action="store_true", help="no consultar GitHub Actions")
    args = parser.parse_args()

    results = load_results()
    sha = git("rev-parse", "HEAD")
    branch = git("symbolic-ref", "--short", "-q", "HEAD") or os.environ.get(
        "GITHUB_HEAD_REF", "HEAD"
    )
    base = os.environ.get("QA_BASE") or os.environ.get("GITHUB_BASE_REF") or ""
    if not base:
        base = "develop" if git("rev-parse", "--verify", "-q", "origin/develop") else "main"
    merge_base = git("merge-base", f"origin/{base}", "HEAD") or git("merge-base", base, "HEAD")
    changed = git("diff", "--name-status", merge_base, "HEAD") if merge_base else ""
    dirty = git("status", "--porcelain", "--untracked-files=all")

    statuses = [r["status"] for r in results]
    if not results:
        verdict = "FAIL"
    elif "FAIL" in statuses:
        verdict = "FAIL"
    elif "WARN" in statuses or "SKIP" in statuses:
        verdict = "WARNING"
    else:
        verdict = "PASS"

    totals = [0, 0, 0]
    rows = []
    for r in results:
        counts = test_counts(ROOT / r["log"])
        if counts:
            totals = [a + b for a, b in zip(totals, counts, strict=True)]
        tests = f"{counts[0]} ✓ · {counts[1]} ✗ · {counts[2]} saltadas" if counts else ""
        detail = r["detail"].replace("|", "\\|").replace("\n", " ")[:300]
        rows.append(
            f"| {ICON.get(r['status'], '')} {r['status']} | {r['name']} | {tests} "
            f"| {r['seconds']} s | {detail} |"
        )

    failed_integration = [
        r
        for r in results
        if r["id"] in ("integration", "qa-python", "generated", "e2e") and r["status"] == "FAIL"
    ]
    now = datetime.now(UTC).astimezone()
    lines = [
        f"# {args.title}",
        "",
        f"**Resultado final: {verdict}**",
        "",
        "| Dato | Valor |",
        "|---|---|",
        f"| Fecha y hora | {now:%Y-%m-%d %H:%M:%S %Z} |",
        f"| Rama analizada | `{branch}` |",
        f"| Commit analizado | `{sha[:12]}` {git('log', '-1', '--format=%s', sha)} |",
        f"| Rama base | `{base}` (desde `{merge_base[:12]}`) |"
        if merge_base
        else f"| Rama base | `{base}` |",
        f"| Entorno | {'GitHub Actions' if os.environ.get('GITHUB_ACTIONS') else 'local'} |",
        f"| Comprobaciones | {statuses.count('PASS')} superadas, "
        f"{statuses.count('FAIL')} fallidas, {statuses.count('WARN')} con avisos, "
        f"{statuses.count('SKIP')} no ejecutadas |",
        f"| Pruebas | {totals[0]} superadas, {totals[1]} fallidas, {totals[2]} saltadas |",
        "",
        "## Comprobaciones ejecutadas",
        "",
        "| Estado | Comprobación | Pruebas | Tiempo | Detalle |",
        "|---|---|---|---|---|",
        *(rows or ["| ❌ | No se ha ejecutado ninguna comprobación | | | |"]),
        "",
        "Los logs completos están en `reports/qa/logs/` (no se suben a Git).",
        "",
        "## Archivos modificados",
        "",
        "```",
        changed or "(ninguno respecto a la base)",
        "```",
    ]
    if dirty:
        lines += ["", "Cambios sin commit (no los incluiría un push):", "", "```", dirty, "```"]
    lines += ["", "## Pruebas fallidas", ""]
    failed = [r for r in results if r["status"] == "FAIL"]
    lines += [f"- **{r['name']}**: {r['detail']}" for r in failed] or ["Ninguna."]
    lines += ["", "## Vulnerabilidades detectadas", "", *[f"- {v}" for v in vulnerabilities()]]
    lines += ["", "## Errores de integración", ""]
    lines += [f"- **{r['name']}**: {r['detail']}" for r in failed_integration] or ["Ninguno."]
    skipped = [r for r in results if r["status"] in ("SKIP", "WARN")]
    if skipped:
        lines += ["", "## Avisos y comprobaciones no ejecutadas", ""]
        lines += [
            f"- {r['status']} · **{r['name']}**: {r['detail'] or 'ver el log'}" for r in skipped
        ]
    lines += ["", "## Estado de GitHub Actions", ""]
    if args.no_actions or os.environ.get("GITHUB_ACTIONS"):
        lines.append(
            "Generado dentro de GitHub Actions: el estado está en la pestaña Checks del PR."
        )
    else:
        lines += [f"- {line}" for line in actions_status(sha)]
    lines += [
        "",
        "---",
        "Generado por `scripts/qa/report.py` a partir de resultados reales. "
        "PASS: todo superado · WARNING: revisar avisos · FAIL: no integrar.",
        "",
    ]
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")
    print(f"{verdict}: {output}")


if __name__ == "__main__":
    main()
