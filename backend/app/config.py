"""Configuración leída de variables de entorno o de backend/.env."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Fuente única del contenido: la comparten frontend (GitHub Pages) y backend
FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"
DEFAULT_LESSONS_FILE = FRONTEND_DIR / "data" / "lessons.json"
DEFAULT_PCAP_FILE = FRONTEND_DIR / "data" / "pcap.json"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./dev.db"
    lessons_file: Path = DEFAULT_LESSONS_FILE
    # Banco del PCAP: el servidor elige y corrige con él los simulacros verificados (#109)
    pcap_file: Path = DEFAULT_PCAP_FILE
    # Simulacros verificados que se pueden empezar por cuenta en 24 horas
    verified_exams_per_day: int = 5
    cors_origins: list[str] = [
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ]

    # Sin valor por defecto a propósito: la API se niega a arrancar sin él (ver main.py).
    jwt_secret: str | None = None
    # Client ID público de OAuth 2.0 (nunca un client secret en el frontend).
    google_client_id: str | None = None
    access_token_minutes: int = 30
    # La sesión de la web se renueva mientras se usa (AUTH-01), pero nunca dura más que esto desde
    # que se inició: en un equipo compartido no queda abierta indefinidamente
    session_max_hours: int = 12
    auth_rate_limit_per_minute: int = 5
    # Guardados de progreso por usuario y minuto (AUD-009). La web agrupa los cambios (uno cada
    # 1,5 s por almacén como mucho), así que un alumno real no llega; frena a quien llene la BD.
    write_rate_limit_per_minute: int = 120
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

    # Recuperación de contraseña. Sin BREVO_API_KEY ni SMTP_HOST no se envía el email.
    # SMTP_PORT 587: STARTTLS; 465: TLS directo (SMTPS).
    frontend_url: str = "http://localhost:5500"
    password_reset_minutes: int = 30
    # Clave de la API de Brevo: envía por HTTPS (Render gratis bloquea SMTP). Ver app/mailer.py
    brevo_api_key: str | None = None
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_from: str = "Python Learning Dashboard <no-reply@example.com>"

    # IA con NEXARO AI (docs/architecture/NEXARO_INTEGRATION_CONTRACT.md). Desactivada por defecto:
    # sin NEXARO_ENABLED=true no se llama nunca a NEXARO y la web no ofrece la IA. Solo el backend
    # conoce la URL y el token; el navegador nunca los ve. Se valida al arrancar (nexaro_client.py).
    nexaro_enabled: bool = False
    nexaro_base_url: str | None = None
    # Hosts a los que puede apuntar NEXARO_BASE_URL (anti-SSRF por configuración)
    nexaro_allowed_hosts: list[str] = ["127.0.0.1", "localhost", "nexaro-ai"]
    # Obligatorio si NEXARO no está en este equipo (NEXARO v3 aún no lo comprueba: NX-REQ-01)
    nexaro_service_token: SecretStr | None = None
    nexaro_model: str | None = None
    # Un modelo local en CPU tarda: es el tiempo máximo sin recibir datos de NEXARO
    nexaro_timeout_seconds: float = Field(default=120.0, gt=0, le=300)
    nexaro_max_response_bytes: int = Field(default=262_144, ge=1024, le=4_194_304)
    # Agente de NEXARO con las reglas del tutor (su prompt de sistema vive en NEXARO, no aquí)
    nexaro_agent_tutor: str = Field(default="tutor-programacion", pattern=r"^[a-zA-Z0-9_-]{1,64}$")
    # Preguntas a la IA por alumno y minuto: cada una ocupa la CPU del modelo durante segundos
    ai_rate_limit_per_minute: int = 10
    # Respuestas que PLD pide a la vez a NEXARO (NEXARO admite 2): la siguiente recibe 429 ya
    ai_max_concurrency: int = Field(default=2, ge=1, le=16)

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
