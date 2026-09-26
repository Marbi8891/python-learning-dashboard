"""Arranca el backend para los tests end-to-end (Windows, Linux y macOS).

Base de datos SQLite desechable, migrada y con las lecciones cargadas.
El límite de intentos se relaja porque todos los tests llegan desde la misma IP.
Se ejecuta desde la carpeta backend (lo hace playwright.config.js).
"""

import os
import secrets
import sys
from pathlib import Path

sys.path.insert(0, os.getcwd())  # la carpeta backend, para importar "app"

DB = Path("e2e-test.db")
DB.unlink(missing_ok=True)
os.environ.update(
    DATABASE_URL=f"sqlite:///./{DB}",
    JWT_SECRET=secrets.token_urlsafe(48),
    CORS_ORIGINS='["http://localhost:5500"]',
    FRONTEND_URL="http://localhost:5500",
    AUTH_RATE_LIMIT_PER_MINUTE="1000",
)

import uvicorn  # noqa: E402
from alembic.config import main as alembic  # noqa: E402

from app.database import SessionLocal  # noqa: E402
from app.seed import seed  # noqa: E402

alembic(["upgrade", "head"])
with SessionLocal() as session:
    seed(session)
uvicorn.run("app.main:app", host="127.0.0.1", port=8000, log_level="warning")
