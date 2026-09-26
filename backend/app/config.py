"""Configuración leída de variables de entorno o de backend/.env."""

from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Fuente única del contenido: la comparten frontend (GitHub Pages) y backend
FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"
DEFAULT_LESSONS_FILE = FRONTEND_DIR / "data" / "lessons.json"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./dev.db"
    lessons_file: Path = DEFAULT_LESSONS_FILE
    cors_origins: list[str] = [
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ]

    # Sin valor por defecto a propósito: la API se niega a arrancar sin él (ver main.py).
    jwt_secret: str | None = None
    access_token_minutes: int = 60
    auth_rate_limit_per_minute: int = 5

    # Recuperación de contraseña. Sin SMTP_HOST, el enlace se escribe en el log (modo desarrollo).
    frontend_url: str = "http://localhost:5500"
    password_reset_minutes: int = 30
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_from: str = "Python Learning Dashboard <no-reply@example.com>"

    # Modo aplicación local: la API sirve también la web (ver app/local_site.py)
    serve_frontend: bool = False
    frontend_dir: Path = FRONTEND_DIR

    @field_validator("database_url")
    @classmethod
    def use_psycopg_driver(cls, url: str) -> str:
        """Render y Heroku dan URLs postgres:// o postgresql://; SQLAlchemy necesita el driver."""
        for prefix in ("postgres://", "postgresql://"):
            if url.startswith(prefix):
                return "postgresql+psycopg://" + url.removeprefix(prefix)
        return url


@lru_cache
def get_settings() -> Settings:
    return Settings()
