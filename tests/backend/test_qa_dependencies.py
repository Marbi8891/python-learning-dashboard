"""Dependencias del backend: instaladas, coherentes y con versiones acotadas."""

import re
import subprocess
import sys
from importlib.metadata import PackageNotFoundError, version

from conftest import BACKEND

REQ_LINE = re.compile(r"^([A-Za-z0-9_.-]+)(\[[^\]]+\])?\s*(.*)$")


def requirements(name: str):
    for raw in (BACKEND / name).read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if line and not line.startswith("-r"):
            yield REQ_LINE.match(line).groups()


def test_pip_check_sin_conflictos():
    result = subprocess.run([sys.executable, "-m", "pip", "check"], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr


def test_cada_dependencia_esta_instalada():
    missing = []
    for file in ("requirements.txt", "requirements-dev.txt"):
        for package, _extra, _spec in requirements(file):
            try:
                version(package)
            except PackageNotFoundError:
                missing.append(f"{file}: {package}")
    assert not missing, f"Instala con pip install -r backend/requirements-dev.txt: {missing}"


def test_las_dependencias_de_produccion_tienen_version_minima():
    """Sin versión mínima, un entorno nuevo podría instalar una versión con fallos conocidos."""
    loose = [
        p
        for p, _e, spec in requirements("requirements.txt")
        if ">=" not in spec and "==" not in spec
    ]
    assert not loose, loose


def test_la_imagen_docker_usa_requirements_txt():
    dockerfile = (BACKEND / "Dockerfile").read_text(encoding="utf-8")
    assert "pip install -r requirements.txt" in dockerfile
    assert "requirements-dev" not in dockerfile, "las herramientas de test no van a producción"
