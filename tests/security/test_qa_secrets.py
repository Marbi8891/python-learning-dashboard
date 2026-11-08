"""Secretos y archivos que nunca deben estar en el repositorio.

Gitleaks (scripts/qa/security_scan.sh) busca secretos en el contenido; esto comprueba que las
protecciones de .gitignore siguen ahí y que ningún archivo de secretos está versionado.
"""

import re
import subprocess

import pytest
from conftest import FRONTEND, REPO

FORBIDDEN = re.compile(
    r"(^|/)(\.env(\.[^/]*)?|.*\.(pem|key|p12|jks|keystore)|\.local-secret|dev\.db)$"
)
ALLOWED = {".env.example", ".env.docker.example"}


def tracked_files() -> list[str]:
    out = subprocess.run(["git", "ls-files"], cwd=REPO, capture_output=True, text=True, check=True)
    return out.stdout.splitlines()


def test_ningun_archivo_de_secretos_esta_versionado():
    bad = [
        f for f in tracked_files() if FORBIDDEN.search(f) and f.rsplit("/", 1)[-1] not in ALLOWED
    ]
    assert not bad, (
        f"Archivos de secretos en Git: {bad}. Sácalos con git rm --cached y rota las claves."
    )


@pytest.mark.parametrize("pattern", [".env", "*.pem", "*.key", "backend/.local-secret", "*.db"])
def test_gitignore_protege_los_secretos(pattern):
    gitignore = (REPO / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert pattern in gitignore, f".gitignore ya no ignora {pattern}"


def test_env_example_no_trae_valores_reales():
    text = (REPO / "backend" / ".env.example").read_text(encoding="utf-8")
    for key in ("JWT_SECRET", "BREVO_API_KEY", "SMTP_PASSWORD"):
        match = re.search(rf"^#?\s*{key}=(.*)$", text, re.M)
        assert match is None or match.group(1).strip() == "", f"{key} tiene valor en .env.example"


def test_el_frontend_no_contiene_claves_privadas_ni_tokens():
    patterns = {
        "clave privada": r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
        "client secret de Google": r"GOCSPX-[A-Za-z0-9_-]{10,}",
        "token de GitHub": r"gh[pousr]_[A-Za-z0-9]{30,}",
        "clave de Brevo": r"xkeysib-[a-f0-9]{20,}",
        "JWT": r"eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}",
    }
    found = []
    for file in FRONTEND.rglob("*"):
        if file.is_file() and file.suffix in {".js", ".html", ".json", ".css", ".webmanifest"}:
            text = file.read_text(encoding="utf-8", errors="ignore")
            found += [
                f"{file.relative_to(REPO)}: {name}"
                for name, p in patterns.items()
                if re.search(p, text)
            ]
    assert not found, found


def test_gitleaks_tiene_configuracion_del_proyecto():
    config = (REPO / ".gitleaks.toml").read_text(encoding="utf-8")
    assert "useDefault = true" in config, "la configuración debe extender las reglas por defecto"
