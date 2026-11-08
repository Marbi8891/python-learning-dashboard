"""Fixtures de las pruebas QA de Python (tests/backend, tests/integration y tests/security).

Reutiliza las fixtures del backend (backend/tests/conftest.py: SQLite en memoria nueva por test,
límites de peticiones reiniciados). No hay una segunda copia que mantener: si cambian allí,
cambian aquí. Nunca se conectan a servicios de producción (Render, Neon, Google, Brevo).
"""

import importlib.util
import json
import os
import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
BACKEND = REPO / "backend"
FRONTEND = REPO / "frontend"
sys.path.insert(0, str(BACKEND))

# Sin variables de producción: aunque el equipo tenga un backend/.env, estas pruebas no lo leen
# (se ejecutan desde la raíz) y cualquier URL de red queda fuera
for _name in ("DATABASE_URL", "BREVO_API_KEY", "SMTP_HOST", "GOOGLE_CLIENT_ID"):
    os.environ.pop(_name, None)

_spec = importlib.util.spec_from_file_location(
    "backend_conftest", BACKEND / "tests" / "conftest.py"
)
backend_conftest = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(backend_conftest)

client = backend_conftest.client
auth_headers = backend_conftest.auth_headers
register = backend_conftest.register
login = backend_conftest.login
PASSWORD = backend_conftest.PASSWORD


@pytest.fixture(scope="session")
def openapi():
    """Esquema OpenAPI de la app (se genera en memoria: en producción no se publica)."""
    from app.main import app

    return app.openapi()


def read_frontend_config() -> dict[str, str]:
    """Valores literales de frontend/config.js (apiUrl de producción, googleClientId...)."""
    source = (FRONTEND / "config.js").read_text(encoding="utf-8")
    values = dict(re.findall(r'(\w+):\s*"([^"]*)"', source))
    prod = re.search(r':\s*"(https://[^"]+)"', source.split("apiUrl:")[-1])
    values["apiUrlProduction"] = prod.group(1) if prod else ""
    return values


def read_render_env() -> dict[str, str | None]:
    """Variables de entorno declaradas en render.yaml (None = se rellenan en el panel)."""
    text = (REPO / "render.yaml").read_text(encoding="utf-8")
    env: dict[str, str | None] = {}
    for block in re.split(r"\n\s*- key: ", text)[1:]:
        key = block.split("\n", 1)[0].strip()
        value = re.search(r"\n\s*value:\s*(.+)", block)
        env[key] = value.group(1).strip().strip("'\"") if value else None
    return env


def read_csp(html_file: str) -> dict[str, list[str]]:
    """CSP del <meta http-equiv> de una página, como {directiva: [fuentes]}."""
    html = (FRONTEND / html_file).read_text(encoding="utf-8")
    content = re.search(r'http-equiv="Content-Security-Policy"\s+content="([^"]+)"', html).group(1)
    policy = {}
    for part in content.split(";"):
        if part.strip():
            name, *sources = part.split()
            policy[name] = sources
    return policy


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))
