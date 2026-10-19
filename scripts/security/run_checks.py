"""Comprobaciones de seguridad locales del equipo AppSec (docs/security/SECURITY_TESTING.md).

Ejecuta las mismas herramientas gratuitas que la CI (`.github/workflows/security.yml` y `ci.yml`)
con la misma configuración. Las que no estén instaladas se saltan con la instrucción para
instalarlas: el script nunca falla por una herramienta ausente, solo por un hallazgo.

    python scripts/security/run_checks.py                  # todas
    python scripts/security/run_checks.py --only bandit,semgrep
    python scripts/security/run_checks.py --list

Nunca imprime secretos: Gitleaks va siempre con --redact y no se muestra el entorno.
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# nombre → (ejecutable, argumentos, carpeta, cómo instalarlo)
CHECKS = {
    "pip-audit": (
        "pip-audit",
        ["-r", "requirements.txt"],
        "backend",
        "pip install pip-audit",
    ),
    "npm-audit": ("npm", ["audit", "--audit-level=high"], ".", "instala Node 22 y ejecuta npm ci"),
    "bandit": (
        "bandit",
        ["-r", "app", "-ll", "-ii", "-q"],
        "backend",
        "pip install bandit==1.9.4",
    ),
    "semgrep": (
        "semgrep",
        ["scan", "--metrics=off", "--config", ".semgrep/", "--error", "-q"],
        ".",
        "pip install semgrep==1.181.0 (en Windows: usa WSL o Docker, semgrep/semgrep)",
    ),
    "gitleaks": (
        "gitleaks",
        ["git", "--redact", "--no-banner", "."],
        ".",
        "descarga el binario de https://github.com/gitleaks/gitleaks/releases (8.28.0)",
    ),
}


def run(name: str) -> str:
    executable, args, folder, install = CHECKS[name]
    found = shutil.which(executable)
    if found is None:
        print(f"[saltado] {name}: no está instalado. Para instalarlo: {install}")
        return "skipped"
    print(f"[{name}] {executable} {' '.join(args)}  (en {folder})", flush=True)
    # Lista de argumentos, sin shell: nada del entorno se interpreta ni se muestra
    result = subprocess.run([found, *args], cwd=ROOT / folder, check=False)
    status = "ok" if result.returncode == 0 else "fail"
    print(f"[{name}] {'sin hallazgos' if status == 'ok' else 'HALLAZGOS o error, revisa arriba'}")
    return status


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--only", help="lista separada por comas: " + ",".join(CHECKS))
    parser.add_argument("--list", action="store_true", help="muestra las comprobaciones y sale")
    options = parser.parse_args()
    if options.list:
        for name, (_, _, folder, install) in CHECKS.items():
            print(f"{name:10} en {folder:8} · instalar: {install}")
        return 0
    names = options.only.split(",") if options.only else list(CHECKS)
    unknown = [n for n in names if n not in CHECKS]
    if unknown:
        parser.error(f"comprobación desconocida: {', '.join(unknown)}")
    results = {name: run(name) for name in names}
    print("\nResumen: " + ", ".join(f"{name}={status}" for name, status in results.items()))
    return 1 if "fail" in results.values() else 0


if __name__ == "__main__":
    sys.exit(main())
