"""Proveedor Ollama: un modelo de lenguaje local y gratuito (A2A_MODEL_PROVIDER=ollama).

Es el proveedor predeterminado del tutor. Habla con la API HTTP de Ollama (`POST /api/chat`) con
`httpx`, que ya instala el SDK de A2A: no hace falta ninguna librería más. El agente no lo conoce:
recibe un `AgentModelProvider` y le basta con `generate`.

Seguridad:
- Ollama es un servicio interno: solo lo llama el backend, nunca el navegador.
- Su URL y el modelo salen solo de la configuración (A2A_OLLAMA_BASE_URL, A2A_MODEL). Nada de la
  petición del alumno puede cambiarlos (sin SSRF), no se siguen redirecciones y no se usan los
  proxies del entorno.
- No necesita API key. Solo se envía `ModelRequest`: instrucciones, pregunta y contexto educativo
  mínimo, sin datos que identifiquen al alumno.
- El backend no descarga modelos: los instala a mano quien despliega (`ollama pull <modelo>`).
"""

import asyncio
import json
import logging
import re
import time
from urllib.parse import urlsplit

import httpx

from app.a2a.providers.base import (
    TRUNCATED_NOTICE,
    EmptyModelResponseError,
    MalformedModelResponseError,
    ModelConfigurationError,
    ModelRequest,
    ModelRequestError,
    ModelTimeoutError,
    ModelUnavailableError,
)

logger = logging.getLogger("pld.a2a")

DEFAULT_BASE_URL = "http://127.0.0.1:11434"
DEFAULT_MODEL = "qwen2.5-coder:7b"
# Ventana de contexto: el prompt más largo que admite el tutor (pregunta, código y error al
# máximo) cabe en unos 8000 tokens. El valor por defecto de Ollama es menor y recortaría el inicio.
CONTEXT_TOKENS = 8192
UNAVAILABLE = (
    "El tutor local no está disponible ahora mismo. Comprueba que Ollama está en marcha con el "
    "modelo configurado e inténtalo de nuevo."
)
# Algunos modelos locales escriben su razonamiento entre <think> y </think>: no es la respuesta
_THINKING = re.compile(r"<think>.*?</think>", re.DOTALL)


def check_base_url(url: str) -> str:
    """URL de Ollama de la configuración: http(s), con host y sin usuario, ruta ni parámetros."""
    parts = urlsplit(url)
    if (
        parts.scheme not in {"http", "https"}
        or not parts.hostname
        or parts.username
        or parts.password
        or parts.path not in {"", "/"}
        or parts.query
        or parts.fragment
    ):
        raise ValueError("A2A_OLLAMA_BASE_URL debe ser como http://127.0.0.1:11434")
    return url.rstrip("/")


class OllamaProvider:
    name = "ollama"
    unavailable_message = UNAVAILABLE

    def __init__(
        self,
        *,
        base_url: str = DEFAULT_BASE_URL,
        model: str = DEFAULT_MODEL,
        max_tokens: int,
        timeout_seconds: float,
        transport: httpx.AsyncBaseTransport | None = None,
    ):
        self.base_url = check_base_url(base_url)
        self.model = model
        self.max_tokens = max_tokens
        self.timeout_seconds = timeout_seconds
        self._transport = transport  # para los tests

    def __repr__(self) -> str:
        return f"OllamaProvider(base_url={self.base_url!r}, model={self.model!r})"

    async def generate(self, request: ModelRequest) -> str:
        body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": request.system},
                {"role": "user", "content": request.prompt},
            ],
            "stream": False,
            "options": {"num_predict": self.max_tokens, "num_ctx": CONTEXT_TOKENS},
        }
        started = time.perf_counter()
        try:
            async with (
                asyncio.timeout(self.timeout_seconds),
                httpx.AsyncClient(
                    base_url=self.base_url,
                    timeout=self.timeout_seconds,
                    follow_redirects=False,
                    trust_env=False,  # sin proxies del entorno: Ollama es local
                    transport=self._transport,
                ) as client,
            ):
                response = await client.post("/api/chat", json=body)
        # Se relanzan sin la excepción original (`from None`): puede llevar la petición
        except (TimeoutError, httpx.TimeoutException):
            raise ModelTimeoutError() from None
        except httpx.HTTPError:  # Ollama apagado, red, protocolo…
            raise ModelUnavailableError() from None

        data = _json(response)
        text = _answer_text(data)
        _log_usage(self, data, started)
        return text


def _json(response: httpx.Response) -> dict:
    if response.status_code == 404:  # modelo sin descargar (ollama pull) o URL que no es Ollama
        raise ModelConfigurationError()
    if response.status_code >= 500:
        raise ModelUnavailableError()
    if response.status_code != 200:
        raise ModelRequestError()
    try:
        data = response.json()
    except ValueError:
        raise MalformedModelResponseError() from None
    if not isinstance(data, dict):
        raise MalformedModelResponseError()
    return data


def _answer_text(data: dict) -> str:
    message = data.get("message")
    content = message.get("content") if isinstance(message, dict) else None
    if not isinstance(content, str):
        raise MalformedModelResponseError()
    answer = _THINKING.sub("", content).strip()
    if not answer:
        raise EmptyModelResponseError()
    if data.get("done_reason") == "length":
        answer += f"\n\n{TRUNCATED_NOTICE}"
    return answer


def _log_usage(provider: OllamaProvider, data: dict, started: float) -> None:
    """Tokens y duración de la llamada. Sin contenido de la petición ni de la respuesta."""
    entry = {
        "event": "a2a.model",
        "provider": provider.name,
        "model": provider.model,
        "served_by": data.get("model"),
        "stop_reason": data.get("done_reason"),
        "input_tokens": data.get("prompt_eval_count"),
        "output_tokens": data.get("eval_count"),
        "ms": round((time.perf_counter() - started) * 1000),
    }
    logger.info(json.dumps(entry, ensure_ascii=False, sort_keys=True, default=str))
