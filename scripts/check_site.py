"""Prueba de humo del sitio estático antes de publicarlo en GitHub Pages.

GitHub Pages sirve la web en una subruta (`/python-learning-dashboard/`) y sin paso de build, así
que un enlace absoluto (`/js/app.js`), un archivo que falta o un JavaScript con un error de sintaxis
rompen la web publicada sin que ningún test lo note antes. Este script comprueba la carpeta tal
como se va a subir:

1. Las páginas HTML solo enlazan recursos locales con rutas relativas, y esos archivos existen.
2. Cada `import` relativo de los módulos de `js/` apunta a un archivo que existe.
3. Cada archivo `.js` tiene una sintaxis válida (`node --check`, si Node está instalado).
4. Cada `.json` de `data/` y el manifiesto se pueden leer.

    python scripts/check_site.py            # comprueba frontend/
    python scripts/check_site.py <carpeta>  # comprueba otra copia (p. ej. el artefacto)

Solo usa la biblioteca estándar. Sale con código 1 y la lista de problemas si encuentra alguno.
"""

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# href/src de las páginas; los <a href> a otras páginas también deben existir
REF = re.compile(r'\b(?:href|src)="([^"]+)"')
# import … from "./x.js", import "./x.js", import("./x.js") y new URL("./x.js", import.meta.url)
IMPORT = re.compile(r'(?:\bfrom\s*|\bimport\s*\(?\s*|new URL\(\s*)"(\.{1,2}/[^"]+)"')
EXTERNAL = ("http://", "https://", "mailto:", "tel:", "data:", "#", "javascript:")
# GitHub Pages sirve 404.html en cualquier ruta: es la única página que necesita rutas absolutas
PAGES_PREFIX = "/python-learning-dashboard/"
ABSOLUTE_ALLOWED = {"404.html"}


def local_target(ref: str) -> str | None:
    """Ruta local de una referencia, o None si es externa, un ancla o una plantilla."""
    if ref.startswith(EXTERNAL) or "${" in ref:
        return None
    return ref.split("#")[0].split("?")[0] or None


def check_pages(site: Path) -> list[str]:
    problems = []
    for page in sorted(site.glob("*.html")):
        for ref in REF.findall(page.read_text(encoding="utf-8")):
            target = local_target(ref)
            if target is None:
                continue
            if page.name in ABSOLUTE_ALLOWED and target.startswith(PAGES_PREFIX):
                target = target.removeprefix(PAGES_PREFIX) or "index.html"
            if target.startswith("/"):
                problems.append(f"{page.name}: «{ref}» es absoluta (falla en la subruta de Pages)")
            elif not (site / target).exists():
                problems.append(f"{page.name}: «{ref}» no existe")
    return problems


def check_imports(site: Path) -> list[str]:
    problems = []
    for script in sorted((site / "js").rglob("*.js")):
        for ref in IMPORT.findall(script.read_text(encoding="utf-8")):
            if not (script.parent / ref).resolve().exists():
                problems.append(f"{script.relative_to(site)}: importa «{ref}», que no existe")
    return problems


def check_syntax(site: Path) -> list[str]:
    node = shutil.which("node")
    if node is None:
        print("Aviso: Node no está instalado; no se comprueba la sintaxis de JavaScript.")
        return []
    problems = []
    for script in sorted(site.rglob("*.js")):
        if "vendor" in script.parts or "pyodide-local" in script.parts:
            continue  # código de terceros ya minificado
        # Los de js/ son módulos ES: se comprueban como tales aunque falte el package.json
        # (Node 22 da por buena la sintaxis de un archivo ambiguo con import y un error)
        module = ["--input-type=module"] if "js" in script.relative_to(site).parts else []
        result = subprocess.run(
            [node, *module, "--check"],
            input=script.read_text(encoding="utf-8"),
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            lines = result.stderr.splitlines()
            message = next((line for line in lines if "Error" in line), "error de sintaxis")
            problems.append(f"{script.relative_to(site)}: {message}")
    return problems


def check_json(site: Path) -> list[str]:
    problems = []
    for path in sorted([*(site / "data").rglob("*.json"), site / "manifest.webmanifest"]):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            problems.append(f"{path.relative_to(site)}: {error}")
    return problems


def main(argv: list[str]) -> int:
    site = Path(argv[0]) if argv else ROOT / "frontend"
    if not (site / "index.html").is_file():
        print(f"No hay index.html en {site}")
        return 1
    problems = check_pages(site) + check_imports(site) + check_syntax(site) + check_json(site)
    for problem in problems:
        print(f"✗ {problem}")
    if problems:
        print(f"{len(problems)} problemas en {site}")
        return 1
    print(f"Sitio correcto: {site}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
