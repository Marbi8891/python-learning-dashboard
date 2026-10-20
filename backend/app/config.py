"""Configuración leída de variables de entorno o de backend/.env."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Fuente única del contenido: la comparten frontend (GitHub Pages) y backend
FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"
DEFAULT_LESSONS_FILE = FRONTEND_DIR / "data" / "lessons.json"
# Conceptos, ejemplos verificados y errores típicos: el contenido revisado que usa el tutor
DEFAULT_LEARNING_FILE = FRONTEND_DIR / "data" / "learning.json"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./dev.db"
    lessons_file: Path = DEFAULT_LESSONS_FILE
    learning_file: Path = DEFAULT_LEARNING_FILE
    cors_origins: list[str] = [
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ]

    # Sin valor por defecto a propósito: la API se niega a arrancar sin él (ver main.py).
    jwt_secret: str | None = None
    # Client ID público de OAuth 2.0 (nunca un client secret en el frontend).
    google_client_id: str | None = None
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

    # Agentes A2A (ADR-0034, docs/a2a.md). Desactivados por defecto.
    a2a_enabled: bool = False
    # URL pública de la API que se anuncia en la Agent Card (en Render, la de pld-api)
    a2a_base_url: str = "http://127.0.0.1:8000"
    # Proveedor del modelo de lenguaje: «ollama» (local y gratuito, el predeterminado),
    # «anthropic» (de pago: solo si se elige expresamente y hay ANTHROPIC_API_KEY) o «mock».
    a2a_model_provider: Literal["ollama", "anthropic", "mock"] = "ollama"
    # Modelo simulado para desarrollo y tests (sin modelo ni llamadas). Tiene prioridad sobre
    # A2A_MODEL_PROVIDER. Nunca en producción.
    a2a_mock_model: bool = False
    # Modelo del proveedor; vacío = el predeterminado de cada uno (qwen2.5-coder:7b en Ollama,
    # claude-opus-5-5 en Anthropic)
    a2a_model: str | None = None
    # Ollama es un servicio interno: su URL solo sale de aquí, nunca de una petición
    a2a_ollama_base_url: str = "http://127.0.0.1:11434"
    # Solo del entorno o del gestor de secretos; SecretStr evita que aparezca al imprimir la config
    anthropic_api_key: SecretStr | None = None
    # Límites: tokens de salida por respuesta (incluido el razonamiento del modelo) y segundos por
    # llamada al proveedor (un modelo local en CPU puede tardar más de un minuto)
    a2a_max_output_tokens: int = Field(default=4096, ge=256, le=32_000)
    a2a_model_timeout_seconds: float = Field(default=120.0, gt=0, le=600)
    # Mensajes al tutor por usuario y minuto; consultas al modelo por usuario y día, y de todos los
    # usuarios juntos por minuto (tope de gasto si muchas cuentas lo usan a la vez)
    a2a_rate_limit_per_minute: int = 20
    a2a_daily_limit_per_user: int = Field(default=100, ge=1)
    a2a_global_limit_per_minute: int = Field(default=60, ge=1)

    # Tutor híbrido (ADR-0038, docs/tutor-hibrido.md): modalidad «IA avanzada», aparte de la
    # gratuita (el proveedor de arriba). Desactivada por defecto: «none». «openai» es de pago y
    # necesita OPENAI_API_KEY y A2A_ADVANCED_MODEL; «mock» la simula sin IA (tests y pruebas e2e).
    a2a_advanced_provider: Literal["none", "openai", "mock"] = "none"
    # Solo del entorno o del gestor de secretos, nunca del navegador ni del repositorio
    openai_api_key: SecretStr | None = None
    # Modelo de OpenAI disponible en la cuenta. Sin valor por defecto: se elige expresamente
    a2a_advanced_model: str | None = None
    # Solo para modelos de razonamiento de OpenAI; vacío = no se envía
    a2a_advanced_reasoning_effort: Literal["none", "minimal", "low", "medium", "high"] | None = None
    # Límites de coste (valores iniciales, revisables): consultas por usuario y día, consultas de
    # todos los usuarios por día, caracteres de pregunta + código + error, tokens de salida y
    # segundos por llamada. Se cuentan en la base de datos (tabla tutor_usage), por día UTC.
    a2a_advanced_daily_limit_per_user: int = Field(default=10, ge=1, le=1_000)
    a2a_advanced_global_daily_limit: int = Field(default=200, ge=1, le=100_000)
    a2a_advanced_max_input_chars: int = Field(default=6_000, ge=200, le=24_000)
    a2a_advanced_max_output_tokens: int = Field(default=600, ge=64, le=4_000)
    a2a_advanced_timeout_seconds: float = Field(default=30.0, gt=0, le=120)

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
