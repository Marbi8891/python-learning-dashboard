"""Proveedor Anthropic (Claude) con el SDK oficial `anthropic` (Messages API).

Es el proveedor de producción del tutor (A2A_MODEL_PROVIDER=anthropic), pero el agente no lo
conoce: recibe un `AgentModelProvider` y le basta con `generate`.

Seguridad y privacidad:
- La API key llega del entorno o del gestor de secretos (ANTHROPIC_API_KEY, ver config.py) y solo
  se entrega al cliente del SDK. No se guarda en otro sitio, no se registra y no sale en `repr`.
- El destino es fijo (`API_URL`): ni la petición ni una variable como ANTHROPIC_BASE_URL pueden
  desviar las llamadas a otro servidor.
- Solo se envía `ModelRequest` (instrucciones, pregunta y contexto educativo mínimo). Ningún
  identificador del alumno: ni id, ni email, ni el campo `metadata.user_id` de la API.
- Los logs del SDK incluyen las peticiones en DEBUG (ANTHROPIC_LOG=debug): se fijan en WARNING.
- Coste acotado: `max_tokens`, un tiempo máximo por llamada y un único reintento.
"""

import asyncio
import json
import logging
import time

import anthropic

from app.a2a.providers.base import (
    EmptyModelResponseError,
    MalformedModelResponseError,
    ModelConfigurationError,
    ModelRateLimitedError,
    ModelRefusedError,
    ModelRequest,
    ModelRequestError,
    ModelTimeoutError,
    ModelUnavailableError,
)

logger = logging.getLogger("pld.a2a")

API_URL = "https://api.anthropic.com"
DEFAULT_MODEL = "claude-opus-5-5"
# Esfuerzo de razonamiento: respuestas de tutor, cortas; «medium» es el valor por defecto de
# Claude Opus 5.5, pero se fija aquí para que no cambie el coste si cambia el modelo.
EFFORT = "medium"
MAX_RETRIES = 1  # el SDK reintenta solo errores de red, 408, 409, 429 y 5xx
# Si el modelo rechaza una petición por sus filtros de seguridad, la API la repite con el modelo
# de respaldo que recomienda Anthropic (sin coste de integración). Solo la ofrecen estos modelos.
FALLBACK_BETA = "server-side-fallback-2026-07-01"
FALLBACK_MODELS = ("claude-opus-5", "claude-sonnet-5-5", "claude-fable-5")
TRUNCATED_NOTICE = (
    "_(Respuesta recortada por longitud: pregúntame por la parte que te falte y sigo.)_"
)


def quiet_sdk_logs() -> None:
    """Con ANTHROPIC_LOG=debug el SDK registra cada petición entera (el prompt, el código del
    alumno): sus logs se limitan a avisos y errores, sin contenido."""
    logging.getLogger("anthropic").setLevel(logging.WARNING)


quiet_sdk_logs()


class AnthropicProvider:
    name = "anthropic"

    def __init__(
        self,
        *,
        api_key: str,
        model: str = DEFAULT_MODEL,
        max_tokens: int,
        timeout_seconds: float,
        http_client: anthropic.DefaultAsyncHttpxClient | None = None,
    ):
        if not api_key.strip():
            raise ValueError("Falta la API key de Anthropic")
        quiet_sdk_logs()
        self.model = model
        self.max_tokens = max_tokens
        # Límite total, reintento incluido: una llamada nunca deja una tarea colgada
        self.deadline_seconds = timeout_seconds * (MAX_RETRIES + 1)
        self._client = anthropic.AsyncAnthropic(
            api_key=api_key,
            base_url=API_URL,
            timeout=timeout_seconds,
            max_retries=MAX_RETRIES,
            http_client=http_client,
        )

    def __repr__(self) -> str:  # sin la API key
        return f"AnthropicProvider(model={self.model!r})"

    async def generate(self, request: ModelRequest) -> str:
        params: dict[str, object] = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "system": request.system,
            "messages": [{"role": "user", "content": request.prompt}],
            "output_config": {"effort": EFFORT},
        }
        if self.model.startswith(FALLBACK_MODELS):
            params |= {"betas": [FALLBACK_BETA], "fallbacks": "default"}

        started = time.perf_counter()
        try:
            async with asyncio.timeout(self.deadline_seconds):
                response = await self._client.beta.messages.create(**params)
        # Se relanzan sin la excepción original (`from None`): puede llevar la petición
        except (TimeoutError, anthropic.APITimeoutError):
            raise ModelTimeoutError() from None
        except anthropic.APIConnectionError:
            raise ModelUnavailableError() from None
        except anthropic.RateLimitError:
            raise ModelRateLimitedError() from None
        except (
            anthropic.AuthenticationError,
            anthropic.PermissionDeniedError,
            anthropic.NotFoundError,
        ):
            raise ModelConfigurationError() from None
        except anthropic.APIStatusError as error:
            failure = ModelUnavailableError if error.status_code >= 500 else ModelRequestError
            raise failure() from None
        except anthropic.APIError:  # respuesta que el SDK no puede interpretar
            raise MalformedModelResponseError() from None

        text = _answer_text(response)
        _log_usage(self, response, started)
        return text


def _answer_text(response: object) -> str:
    """El texto de la respuesta, comprobando antes cómo ha terminado."""
    stop_reason = getattr(response, "stop_reason", None)
    if stop_reason == "refusal":
        raise ModelRefusedError()
    content = getattr(response, "content", None)
    if not isinstance(content, list):
        raise MalformedModelResponseError()
    texts: list[str] = []
    for block in content:
        kind = getattr(block, "type", None)
        if kind == "fallback":  # lo anterior era del modelo que se negó: no cuenta
            texts.clear()
        elif kind == "text":
            text = getattr(block, "text", None)
            if not isinstance(text, str):
                raise MalformedModelResponseError()
            if text.strip():
                texts.append(text.strip())
    if not texts:
        raise EmptyModelResponseError()
    answer = "\n\n".join(texts)
    if stop_reason == "max_tokens":
        answer += f"\n\n{TRUNCATED_NOTICE}"
    return answer


def _log_usage(provider: AnthropicProvider, response: object, started: float) -> None:
    """Consumo de la llamada, para vigilar el coste. Sin contenido de la petición ni respuesta."""
    usage = getattr(response, "usage", None)
    entry = {
        "event": "a2a.model",
        "provider": provider.name,
        "model": provider.model,
        "served_by": getattr(response, "model", None),
        "stop_reason": getattr(response, "stop_reason", None),
        "input_tokens": getattr(usage, "input_tokens", None),
        "output_tokens": getattr(usage, "output_tokens", None),
        "provider_request": getattr(response, "_request_id", None),
        "ms": round((time.perf_counter() - started) * 1000),
    }
    logger.info(json.dumps(entry, ensure_ascii=False, sort_keys=True, default=str))
