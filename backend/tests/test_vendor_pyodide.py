"""Python servido desde la propia web (RT-002): misma versión en todas partes, huellas y sin CDN."""

import hashlib
import json
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "web"))
import vendor_pyodide  # noqa: E402  (scripts/web/vendor_pyodide.py)


def test_same_version_in_the_web_package_json_and_the_lock():
    entry = vendor_pyodide.locked_package()
    assert entry["version"] == vendor_pyodide.web_version()
    assert entry["integrity"].startswith("sha512-")
    assert entry["resolved"].startswith("https://registry.npmjs.org/pyodide/")


def test_every_file_has_a_sha256():
    assert set(vendor_pyodide.PYODIDE_FILES) == {
        "pyodide.mjs",
        "pyodide.asm.mjs",
        "pyodide.asm.wasm",
        "python_stdlib.zip",
        "pyodide-lock.json",
    }
    assert all(len(h) == 64 for h in vendor_pyodide.PYODIDE_FILES.values())


def test_a_package_with_another_hash_is_rejected():
    with pytest.raises(vendor_pyodide.VendorError, match="sha512"):
        vendor_pyodide.check_integrity(b"otro paquete", "sha512-AAAA")


def fake_project(tmp_path: Path, content: bytes) -> Path:
    """Un proyecto mínimo con node_modules/pyodide cuyos archivos tienen `content`."""
    for name in ("package.json", "package-lock.json", "frontend/js/python-runner.js"):
        (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / name, tmp_path / name)
    package = tmp_path / "node_modules" / "pyodide"
    package.mkdir(parents=True)
    version = vendor_pyodide.web_version()
    (package / "package.json").write_text(json.dumps({"version": version}), encoding="utf-8")
    for name in vendor_pyodide.PYODIDE_FILES:
        (package / name).write_bytes(content)
    return tmp_path


def test_a_changed_file_is_not_copied(tmp_path):
    root = fake_project(tmp_path, b"codigo cambiado")
    with pytest.raises(vendor_pyodide.VendorError, match="sha256"):
        vendor_pyodide.vendor(root / "site", root)
    assert not (root / "site" / "pyodide").exists()


def test_copies_the_checked_files(tmp_path, monkeypatch):
    root = fake_project(tmp_path, b"python")
    digest = hashlib.sha256(b"python").hexdigest()
    monkeypatch.setattr(
        vendor_pyodide, "PYODIDE_FILES", dict.fromkeys(vendor_pyodide.PYODIDE_FILES, digest)
    )
    target = vendor_pyodide.vendor(root / "site", root)
    assert target == root / "site" / "pyodide" / f"v{vendor_pyodide.web_version()}"
    assert all((target / name).read_bytes() == b"python" for name in vendor_pyodide.PYODIDE_FILES)


def test_the_web_does_not_load_python_from_a_cdn():
    for name in ("frontend/index.html", "frontend/js/python-runner.js", "frontend/sw.js"):
        assert "cdn.jsdelivr.net" not in (ROOT / name).read_text(encoding="utf-8"), name
