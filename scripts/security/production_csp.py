"""CSP de la web publicada sin los orígenes de desarrollo.

`frontend/index.html` permite `http://127.0.0.1:8000` y `http://localhost:8000` en `connect-src`
porque en desarrollo y en los e2e la web (puerto 5500) habla con la API local (puerto 8000). En
GitHub Pages sobran: este script los quita de la copia que se publica, sin tocar el repositorio.

    python scripts/security/production_csp.py --check frontend   # solo comprueba (CI)
    python scripts/security/production_csp.py frontend            # reescribe la copia (despliegue)

Falla si queda algún origen `http:` en la CSP, si falta la CSP o si cambiaría algo más que esos
dos orígenes.
"""

import argparse
import re
import sys
from pathlib import Path

DEV_ORIGINS = ("http://127.0.0.1:8000", "http://localhost:8000")
CSP_META = re.compile(r'(<meta http-equiv="Content-Security-Policy" content=")([^"]*)(")')


def production_policy(policy: str) -> str:
    """La misma política sin los orígenes de desarrollo en ninguna directiva."""
    directives = []
    for directive in policy.split(";"):
        tokens = [t for t in directive.split() if t not in DEV_ORIGINS]
        if tokens:
            directives.append(" ".join(tokens))
    return "; ".join(directives)


def production_html(html: str) -> str:
    match = CSP_META.search(html)
    if match is None:
        raise ValueError("no hay <meta> Content-Security-Policy")
    policy = production_policy(match.group(2))
    insecure = [t for t in policy.split() if t.startswith("http:")]
    if insecure:
        raise ValueError(f"la CSP publicada tendría orígenes sin TLS: {', '.join(insecure)}")
    return html[: match.start(2)] + policy + html[match.end(2) :]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("site", type=Path, help="carpeta que se publica (frontend)")
    parser.add_argument("--check", action="store_true", help="comprueba sin escribir")
    options = parser.parse_args()
    target = options.site / "index.html"
    html = target.read_text(encoding="utf-8")
    try:
        published = production_html(html)
    except ValueError as error:
        print(f"production_csp: {error}", file=sys.stderr)
        return 1
    if not options.check:
        target.write_text(published, encoding="utf-8")
    removed = len(html) - len(published)
    print(f"production_csp: {target} sin orígenes de desarrollo ({removed} caracteres menos)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
