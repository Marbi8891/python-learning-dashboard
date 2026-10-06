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
    access_token_minutes: int = 30
    auth_rate_limit_per_minute: int = 5
    # Fallos de login seguidos por cuenta antes de bloquearla un rato (aunque cambien de IP)
    login_failures_per_account: int = 10
    login_lockout_minutes: int = 15
    # Proxies de confianza delante de la API. En Render hay uno, que AÑADE la IP real del cliente al
    # final de X-Forwarded-For (lo anterior lo puede escribir cualquiera). 0 = conexión directa.
    trusted_proxy_hops: int = 0
    # Tamaño máximo del cuerpo de una petición (el estado del PCAP admite 200 KB)
    max_body_bytes: int = 300_000
    # Intentos de ejercicio que se guardan por usuario y lección (los más recientes)
    attempts_kept_per_lesson: int = 50
    # /docs y /openapi.json: útiles en desarrollo; en producción no se publica el mapa de la API
    enable_docs: bool = False

    # Recuperación de contraseña. Sin SMTP_HOST no se envía el email (ver app/mailer.py).
    # SMTP_PORT 587: STARTTLS; 465: TLS directo (SMTPS).
    frontend_url: str = "http://localhost:5500"
    password_reset_minutes: int = 30
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_from: str = "Python Learning Dashboard <no-reply@example.com>"

    # Agentes A2A (ADR-0034, docs/a2a.md). Desactivados por defecto: sin proveedor de modelo real,
    # solo se pueden activar con el modelo simulado de desarrollo (A2A_MOCK_MODEL=true).
    a2a_enabled: bool = False
    # URL pública de la API que se anuncia en la Agent Card (en Render, la de pld-api)
    a2a_base_url: str = "http://127.0.0.1:8000"
    a2a_mock_model: bool = False
    # Mensajes al tutor por usuario y minuto
    a2a_rate_limit_per_minute: int = 20

    # Modo aplicación local: la API sirve también la web (ver app/local_site.py)
    serve_frontend: bool = False
    frontend_dir: Path = FRONTEND_DIR

    @field_validator("database_url")
    @classmethod
    def use_psycopg_driver(cls, url: str) -> str:
        """Render y Heroku dan URLs postgres:// o postgresql://; SQLAlchemy necesita el driver.

        Además, una base de datos remota sin `sslmode` se conecta cifrada (sslmode=require):
        los datos personales no viajan nunca en claro entre la API y la base de datos."""
        for prefix in ("postgres://", "postgresql://"):
            if url.startswith(prefix):
                url = "postgresql+psycopg://" + url.removeprefix(prefix)
        if url.startswith("postgresql+psycopg://") and "sslmode=" not in url and not _is_local(url):
            url += ("&" if "?" in url else "?") + "sslmode=require"
        return url


def _is_local(url: str) -> bool:
    host = url.split("@")[-1].split("/")[0].split(":")[0]
    return host in {"localhost", "127.0.0.1", "db", "postgres", ""}


@lru_cache
def get_settings() -> Settings:
    return Settings()
