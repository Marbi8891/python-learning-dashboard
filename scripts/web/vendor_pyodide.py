"""Copia Python (Pyodide) a la web para servirlo desde el mismo origen, sin CDN externo (RT-002).

    python scripts/web/vendor_pyodide.py [carpeta-web]     (por defecto, frontend)

1. La versión es la de la web (PYODIDE_VERSION en frontend/js/python-runner.js) y debe ser
   la exacta de package.json.
2. Toma el paquete npm `pyodide` de node_modules/ si está, o lo descarga de la dirección de
   package-lock.json y comprueba su huella sha512 (`integrity`).
3. Comprueba la sha256 de cada archivo que carga la web (PYODIDE_FILES) y los deja en
   <carpeta-web>/pyodide/v<versión>/.

Falla si algo no cuadra, para no servir otro Python. La carpeta no va al repositorio
(.gitignore): la generan Pages, la comprobación de despliegue, las e2e y
scripts/run_local.py. No necesita Node.
"""

import base64
import hashlib
import io
import json
import re
import sys
import tarfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# Los archivos que carga la web y su sha256:
# se cambian solo al subir de versión, a la vez que package.json
PYODIDE_FILES = {
    "pyodide.mjs": "6f1d60f7bf529beb300f0f47983c921d3982363640ba20af0e38efdddbc66109",
    "pyodide.asm.mjs": "f7cdc8ece80678ceb712f8e65ebe6d3a83203a180c399865f49612a051693635",
    "pyodide.asm.wasm": "cc36e3cab04fdfc9a63ff13eb52eae2b911bf46c025cc7b281f394bd3de1d5e6",
    "python_stdlib.zip": "fa1957e5777068fc4f7437f96d860ae2fbe9c19732ba06c84e004ec16dd7dd7a",
    "pyodide-lock.json": "5dc2fc119108bc148c7457dc86e7675b5c87e1cafd420b9c34c1eaef7b36c010",
}


class VendorError(Exception):
    pass


def web_version(root: Path = ROOT) -> str:
    source = (root / "frontend" / "js" / "python-runner.js").read_text(encoding="utf-8")
    match = re.search(r'PYODIDE_VERSION = "([^"]+)"', source)
    if not match:
        raise VendorError("no encuentro PYODIDE_VERSION en frontend/js/python-runner.js")
    return match.group(1)


def locked_package(root: Path = ROOT) -> dict:
    """Versión, dirección y huella del paquete según package.json y package-lock.json."""
    wanted = json.loads((root / "package.json").read_text(encoding="utf-8"))["devDependencies"].get(
        "pyodide"
    )
    lock = json.loads((root / "package-lock.json").read_text(encoding="utf-8"))
    entry = lock["packages"].get("node_modules/pyodide")
    if not entry:
        raise VendorError("package-lock.json no tiene pyodide")
    if wanted != entry["version"]:
        raise VendorError(
            f"package.json pide pyodide {wanted} y package-lock.json tiene {entry['version']}"
        )
    return entry


def check_integrity(data: bytes, integrity: str) -> None:
    algorithm, _, expected = integrity.partition("-")
    if algorithm != "sha512":
        raise VendorError(f"huella {algorithm} no admitida (se espera sha512)")
    actual = base64.b64encode(hashlib.sha512(data).digest()).decode()
    if actual != expected:
        raise VendorError(
            "la huella sha512 del paquete descargado no coincide con package-lock.json"
        )


def package_files(entry: dict, root: Path = ROOT) -> dict[str, bytes]:
    """Los archivos de PYODIDE_FILES, de node_modules/ o del paquete descargado y comprobado."""
    local = root / "node_modules" / "pyodide"
    try:
        installed = json.loads((local / "package.json").read_text(encoding="utf-8"))["version"]
    except (OSError, ValueError, KeyError):
        installed = None
    if installed == entry["version"]:
        return {name: (local / name).read_bytes() for name in PYODIDE_FILES}
    print(f"Descargando Python (Pyodide {entry['version']}, unos 6 MB)…")
    with urllib.request.urlopen(entry["resolved"], timeout=120) as response:  # noqa: S310 (https de package-lock)
        data = response.read()
    check_integrity(data, entry["integrity"])
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
        files = {}
        for name in PYODIDE_FILES:
            member = archive.extractfile(f"package/{name}")
            if member is None:
                raise VendorError(f"el paquete no trae {name}")
            files[name] = member.read()
        return files


def vendor(site: Path, root: Path = ROOT) -> Path:
    version = web_version(root)
    entry = locked_package(root)
    if entry["version"] != version:
        raise VendorError(f"la web pide Pyodide {version} y package.json tiene {entry['version']}")
    target = site / "pyodide" / f"v{version}"
    ready = all(
        (target / name).is_file()
        and hashlib.sha256((target / name).read_bytes()).hexdigest() == digest
        for name, digest in PYODIDE_FILES.items()
    )
    if ready:
        return target
    files = package_files(entry, root)
    for name, digest in PYODIDE_FILES.items():
        actual = hashlib.sha256(files[name]).hexdigest()
        if actual != digest:
            raise VendorError(f"{name}: sha256 {actual}, se esperaba {digest}")
    target.mkdir(parents=True, exist_ok=True)
    for name, data in files.items():
        (target / name).write_bytes(data)
    return target


def main(argv: list[str]) -> int:
    site = Path(argv[1]).resolve() if len(argv) > 1 else ROOT / "frontend"
    try:
        target = vendor(site)
    except (VendorError, OSError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Python (Pyodide) listo y comprobado en {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
