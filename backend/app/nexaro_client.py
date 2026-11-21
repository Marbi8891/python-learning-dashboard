"""Cliente de servidor a servidor hacia NEXARO AI.

Contrato: docs/architecture/NEXARO_INTEGRATION_CONTRACT.md.

Solo lo usa el backend: el navegador nunca conoce la URL ni el token de NEXARO.

- La configuración se valida al arrancar (`check_config`): URL sin credenciales, sin ruta y con un
  host de la lista permitida (anti-SSRF), HTTPS fuera de la red local y token fuera de este equipo.
- Las peticiones no siguen redirecciones, no leen proxies del entorno, tienen tiempo de espera y
  un tope de bytes en la respuesta, y nunca llevan `Origin` ni las cookies del alumno.
- Nunca se registran el token, las cabeceras ni el cuerpo: solo la ruta, el estado y la duración.
- NEXARO responde al chat en NDJSON con HTTP 200 incluso cuando falla: una línea `{"error": ...}`
  es un fallo, no una respuesta (riesgo R-05).
"""

import json
import logging
import re
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any
from urllib.parse import urlsplit

import httpx

from app.config import Settings

logger = logging.getLogger("pld.ai")

LOOPBACK_HOSTS = frozenset({"127.0.0.1", "localhost", "::1"})
MIN_TOKEN_CHARS = 32
# El mismo formato que acepta NEXARO (nexaro/validation.py): [namespace/]modelo[:etiqueta]
_SEGMENT = r"[a-zA-Z0-9][a-zA-Z0-9._-]{0,79}"
_MODEL_RE = re.compile(rf"^(?:{_SEGMENT}/)?{_SEGMENT}(?::[a-zA-Z0-9][a-zA-Z0-9._-]{{0,79}})?$")
# La comprobación de estado no espera al modelo: basta con un tiempo corto
STATUS_TIMEOUT_SECONDS = 5.0
STATUS_CACHE_SECONDS = 30.0


class NexaroConfigError(RuntimeError):
    """Configuración de NEXARO no válida: la API no arranca (mejor que fallar con el alumno)."""


class NexaroUnavailable(Exception):
    """NEXARO no responde o devuelve algo que no se puede usar. El detalle no llega al navegador."""


class NexaroBusy(NexaroUnavailable):
    """NEXARO está generando demasiadas respuestas a la vez (429)."""


def is_valid_model_name(name: str) -> bool:
    return len(name) <= 120 and ".." not in name and bool(_MODEL_RE.match(name))


def check_config(settings: Settings) -> str:
    """Comprueba la configuración y devuelve la URL base normalizada. Lanza NexaroConfigError."""
    if not settings.nexaro_base_url:
        raise NexaroConfigError("NEXARO_ENABLED=true exige NEXARO_BASE_URL")
    if not settings.nexaro_model or not is_valid_model_name(settings.nexaro_model):
        raise NexaroConfigError("NEXARO_MODEL falta o no es un nombre de modelo válido")
    try:
        parts = urlsplit(settings.nexaro_base_url)
        parts.port  # noqa: B018 - lanza ValueError si el puerto no es válido
    except ValueError:
        raise NexaroConfigError("NEXARO_BASE_URL no es una URL válida") from None
    if parts.scheme not in ("http", "https") or not parts.hostname:
        raise NexaroConfigError("NEXARO_BASE_URL debe ser http:// o https:// con un host")
    if parts.username or parts.password or parts.query or parts.fragment:
        raise NexaroConfigError("NEXARO_BASE_URL no puede llevar credenciales, query ni fragmento")
    if parts.path not in ("", "/"):
        raise NexaroConfigError("NEXARO_BASE_URL no puede llevar ruta")
    host = parts.hostname.lower()
    if host not in {h.strip().lower() for h in settings.nexaro_allowed_hosts}:
        raise NexaroConfigError("El host de NEXARO_BASE_URL no está en NEXARO_ALLOWED_HOSTS")
    # Un nombre sin puntos es un servicio de la red Docker privada; el resto viaja por una red
    # que no controlamos y necesita TLS
    if parts.scheme == "http" and host not in LOOPBACK_HOSTS and "." in host:
        raise NexaroConfigError("NEXARO_BASE_URL necesita https:// fuera de la red local")
    token = settings.nexaro_service_token
    secret = token.get_secret_value() if token else ""
    if secret and len(secret) < MIN_TOKEN_CHARS:
        raise NexaroConfigError(
            f"NEXARO_SERVICE_TOKEN debe tener al menos {MIN_TOKEN_CHARS} caracteres"
        )
    if host not in LOOPBACK_HOSTS and not secret:
        raise NexaroConfigError("NEXARO fuera de este equipo exige NEXARO_SERVICE_TOKEN")
    return f"{parts.scheme}://{parts.netloc}"


class NexaroClient:
    """Un cliente HTTP compartido por toda la API (se crea y se cierra en el lifespan)."""

    def __init__(self, settings: Settings, transport: httpx.AsyncBaseTransport | None = None):
        base_url = check_config(settings)
        assert settings.nexaro_model  # garantizado por check_config
        self.model = settings.nexaro_model
        self.max_bytes = settings.nexaro_max_response_bytes
        headers = {}
        if settings.nexaro_service_token:
            secret = settings.nexaro_service_token.get_secret_value()
            if secret:
                headers["Authorization"] = f"Bearer {secret}"
        timeout = settings.nexaro_timeout_seconds
        self._client = httpx.AsyncClient(
            base_url=base_url,
            headers=headers,
            timeout=httpx.Timeout(connect=5.0, read=timeout, write=10.0, pool=5.0),
            follow_redirects=False,
            trust_env=False,  # sin proxies ni .netrc del entorno
            transport=transport,
        )
        self._status: tuple[float, bool] | None = None

    async def aclose(self) -> None:
        await self._client.aclose()

    @asynccontextmanager
    async def _stream(self, method: str, path: str, **kwargs: Any) -> AsyncIterator[httpx.Response]:
        started = time.monotonic()
        status = "error"
        try:
            async with self._client.stream(method, path, **kwargs) as response:
                status = str(response.status_code)
                if response.status_code == 429:
                    raise NexaroBusy
                if response.status_code != 200:
                    # 3xx incluidos: no se siguen redirecciones
                    raise NexaroUnavailable
                yield response
        except httpx.HTTPError:
            raise NexaroUnavailable from None
        finally:
            # Ni el cuerpo ni las cabeceras: solo lo necesario para operar el servicio
            elapsed = int((time.monotonic() - started) * 1000)
            logger.info("nexaro %s %s -> %s (%d ms)", method, path, status, elapsed)

    async def _get_json(self, path: str) -> Any:
        async with self._stream("GET", path, timeout=STATUS_TIMEOUT_SECONDS) as response:
            body = b""
            async for chunk in response.aiter_bytes():
                body += chunk
                if len(body) > self.max_bytes:
                    raise NexaroUnavailable
        try:
            return json.loads(body)
        except ValueError:
            raise NexaroUnavailable from None

    async def _check_available(self) -> bool:
        try:
            health = await self._get_json("/api/health")
            if not isinstance(health, dict) or health.get("status") != "ok":
                return False
            listing = await self._get_json("/api/models")
        except NexaroUnavailable:
            return False
        models = listing.get("models") if isinstance(listing, dict) else None
        names = {m.get("name") for m in models or [] if isinstance(m, dict)}
        tagged = self.model if ":" in self.model else f"{self.model}:latest"
        return self.model in names or tagged in names

    async def available(self) -> bool:
        """¿NEXARO responde y tiene el modelo instalado? Con caché corta: no es una sonda."""
        now = time.monotonic()
        if self._status is not None and now - self._status[0] < STATUS_CACHE_SECONDS:
            return self._status[1]
        result = await self._check_available()
        self._status = (now, result)
        return result

    async def chat(self, agent_id: str, messages: list[dict[str, str]]) -> str:
        """Respuesta completa del chat de NEXARO (NDJSON agregado). Solo roles user/assistant."""
        body = {"model": self.model, "agent_id": agent_id, "messages": messages}
        parts: list[str] = []
        received = 0
        async with self._stream("POST", "/api/chat", json=body) as response:
            async for line in response.aiter_lines():
                received += len(line.encode())
                if received > self.max_bytes:
                    break  # respuesta demasiado larga: se usa lo recibido
                if not line.strip():
                    continue
                try:
                    event = json.loads(line)
                except ValueError:
                    raise NexaroUnavailable from None
                if not isinstance(event, dict) or "error" in event:
                    raise NexaroUnavailable
                message = event.get("message")
                # Solo el texto: tool_calls, thinking y demás campos se ignoran
                content = message.get("content") if isinstance(message, dict) else None
                if isinstance(content, str):
                    parts.append(content)
                if event.get("done") is True:
                    break
        answer = "".join(parts).strip()
        if not answer:
            raise NexaroUnavailable
        return answer


def create_client(settings: Settings) -> NexaroClient | None:
    """El cliente si la IA está activada (validando la configuración); si no, None."""
    if not settings.nexaro_enabled:
        return None
    return NexaroClient(settings)
