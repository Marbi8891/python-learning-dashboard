"""Verifica la copia de frontend/ que se publicaría en GitHub Pages (deployment-check.yml).

    python scripts/qa/verify_pages_artifact.py _site

Comprueba, sin publicar nada:
  - que están los archivos que necesita la web (páginas, service worker, manifiesto, config)
  - que la CSP publicada no deja orígenes de desarrollo (localhost) ni http:
  - que cada archivo de la lista sin conexión (precache.js) existe en el artefacto
  - que no se cuelan restos de desarrollo o secretos (.env, claves, node_modules, enlaces, _pyo)
  - que el tamaño cabe con holgura en el límite de GitHub Pages (1 GB)
Sale con 1 si algo falla, con el archivo y la causa.
"""

import json
import re
import sys
from pathlib import Path

REQUIRED = [
    "index.html",
    "404.html",
    "privacidad.html",
    "aviso-legal.html",
    "config.js",
    "sw.js",
    "precache.js",
    "manifest.webmanifest",
    "favicon.svg",
    "robots.txt",
    "py/runner.py",
    "js/app.js",
    "js/pyodide-worker.js",
]
FORBIDDEN = re.compile(
    r"(^|/)(\.env(\..*)?|.*\.(pem|key|p12|jks|keystore|db|sqlite3?)|node_modules|_pyo|__pycache__|"
    r"\.DS_Store|Thumbs\.db|.*\.log)$"
)
MAX_BYTES = 100 * 1024 * 1024  # aviso muy por debajo de 1 GB: la web pesa unos pocos MB


def main(site: Path) -> int:
    errors: list[str] = []
    files = [p for p in site.rglob("*")]
    rel = {p.relative_to(site).as_posix() for p in files if p.is_file()}

    for name in REQUIRED:
        if name not in rel:
            errors.append(f"{name}: falta en el artefacto")

    for p in files:
        name = p.relative_to(site).as_posix()
        if p.is_symlink():
            errors.append(f"{name}: enlace simbólico (¿frontend/_pyo?): no se publica bien")
        elif FORBIDDEN.search(name):
            errors.append(f"{name}: no debe publicarse (desarrollo o secretos)")

    for page in sorted(site.glob("*.html")):
        html = page.read_text(encoding="utf-8")
        csp = re.search(r'http-equiv="Content-Security-Policy"\s+content="([^"]+)"', html)
        if not csp:
            errors.append(f"{page.name}: sin CSP")
            continue
        for bad in ("localhost", "127.0.0.1", "http:"):
            if bad in csp.group(1):
                errors.append(f"{page.name}: la CSP publicada contiene {bad}")

    precache = (site / "precache.js").read_text(encoding="utf-8") if "precache.js" in rel else ""
    match = re.search(r"self\.PLD_PRECACHE\s*=\s*(\[.*?\]);", precache, re.S)
    if not match:
        errors.append("precache.js: no se encuentra self.PLD_PRECACHE")
    else:
        for entry in json.loads(match.group(1)):
            if entry != "./" and entry not in rel:
                errors.append(
                    f"precache.js: «{entry}» no está en el artefacto (no se instalaría el SW)"
                )

    size = sum(p.stat().st_size for p in files if p.is_file() and not p.is_symlink())
    if size > MAX_BYTES:
        errors.append(f"el artefacto ocupa {size / 1e6:.0f} MB (más de {MAX_BYTES / 1e6:.0f} MB)")

    print(f"Artefacto: {len(rel)} archivos, {size / 1e6:.1f} MB")
    for error in errors:
        print(f"::error::{error}")
    if errors:
        print(f"{len(errors)} errores")
        return 1
    print("Artefacto de GitHub Pages correcto")
    return 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1] if len(sys.argv) > 1 else "frontend")))
