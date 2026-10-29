"""Proveedor OpenAI con el SDK oficial `openai` (API de Responses), solo para la modalidad «IA
avanzada» del tutor híbrido.

Es opcional y de pago: solo se crea con A2A_ADVANCED_PROVIDER=openai, OPENAI_API_KEY y un modelo
elegido expresamente en A2A_ADVANCED_MODEL (no se fija ninguno por defecto: depende de la cuenta).
El agente no lo conoce: recibe un `AgentModelProvider` y le basta con `generate`.

Seguridad y privacidad:
- La API key llega del entorno o del gestor de secretos (OPENAI_API_KEY, ver config.py) y solo
  se entrega al cliente del SDK. No se guarda en otro sitio, no se registra y no sale en `repr`.
- El destino es fijo (`API_URL`): ni la petición ni una variable como OPENAI_BASE_URL pueden
  desviar las llamadas a otro servidor.
- `store=False`: se pide a OpenAI que no guarde la respuesta para consultarla después.
- Solo se envía `ModelRequest` (instrucciones, pregunta y contexto educativo mínimo). Ningún
  identificador del alumno: ni id, ni email, ni los campos `user` o `safety_identifier`.
- Los logs del SDK incluyen las peticiones en DEBUG (OPENAI_LOG=debug): se fijan en WARNING.
- Coste acotado: `max_output_tokens`, un tiempo máximo por llamada y sin reintentos: cada
  consulta reservada en la cuota es como mucho una llamada facturable.
"""

import asyncio
import json
import logging
import time

import openai

from app.a2a.providers.base import (
    TRUNCATED_NOTICE,
    EmptyModelResponseError,
    MalformedModelResponseError,
    ModelConfigurationError,
    ModelRateLimitedError,
    ModelRefusedError,
    ModelReply,
    ModelRequest,
    ModelRequestError,
    ModelTimeoutError,
    ModelUnavailableError,
)

logger = logging.getLogger("pld.a2a")

API_URL = "https://api.openai.com/v1"
MAX_RETRIES = 0  # un reintento podría cobrarse dos veces por una sola consulta de la cuota


def quiet_sdk_logs() -> None:
    """Con OPENAI_LOG=debug el SDK registra cada petición entera (el prompt, el código del
    alumno): sus logs se limitan a avisos y errores, sin contenido."""
    for name in ("openai", "openai._base_client"):
        logging.getLogger(name).setLevel(logging.WARNING)


quiet_sdk_logs()


class OpenAIProvider:
    name = "openai"
    unavailable_message = "La IA avanzada no está disponible ahora mismo."

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        max_output_tokens: int,
        timeout_seconds: float,
        reasoning_effort: str | None = None,
        http_client: openai.DefaultAsyncHttpxClient | None = None,
    ):
        if not api_key.strip():
            raise ValueError("Falta la API key de OpenAI")
        if not model.strip():
            raise ValueError("Falta el modelo de OpenAI")
        quiet_sdk_logs()
        self.model = model.strip()
        self.max_output_tokens = max_output_tokens
        self.reasoning_effort = reasoning_effort
        # Límite total: una llamada nunca deja una tarea colgada
        self.deadline_seconds = timeout_seconds * (MAX_RETRIES + 1)
        self._client = openai.AsyncOpenAI(
            api_key=api_key,
            base_url=API_URL,
            timeout=timeout_seconds,
            max_retries=MAX_RETRIES,
            http_client=http_client,
        )

    def __repr__(self) -> str:  # sin la API key
        return f"OpenAIProvider(model={self.model!r})"

    async def generate(self, request: ModelRequest) -> ModelReply:
        params: dict[str, object] = {
            "model": self.model,
            "instructions": request.system,
            "input": request.prompt,
            "max_output_tokens": self.max_output_tokens,
            "store": False,
        }
        if self.reasoning_effort:  # solo para modelos de razonamiento (ver docs/tutor-hibrido.md)
            params["reasoning"] = {"effort": self.reasoning_effort}

        started = time.perf_counter()
        try:
            async with asyncio.timeout(self.deadline_seconds):
                response = await self._client.responses.create(**params)
        # Se relanzan sin la excepción original (`from None`): puede llevar la petición
        except (TimeoutError, openai.APITimeoutError):
            raise ModelTimeoutError() from None
        except openai.APIConnectionError:
            raise ModelUnavailableError() from None
        except openai.RateLimitError:  # también «insufficient_quota» (sin saldo)
            raise ModelRateLimitedError() from None
        except (
            openai.AuthenticationError,
            openai.PermissionDeniedError,
            openai.NotFoundError,
        ):
            raise ModelConfigurationError() from None
        except openai.APIStatusError as error:
            failure = ModelUnavailableError if error.status_code >= 500 else ModelRequestError
            raise failure() from None
        except openai.APIError:  # respuesta que el SDK no puede interpretar
            raise MalformedModelResponseError() from None

        reply = _answer(response)
        _log_usage(self, response, started)
        return reply


def _answer(response: object) -> ModelReply:
    """El texto de la respuesta, comprobando antes cómo ha terminado."""
    status = getattr(response, "status", None)
    reason = getattr(getattr(response, "incomplete_details", None), "reason", None)
    if status == "incomplete" and reason == "content_filter":
        raise ModelRefusedError()
    if status not in {"completed", "incomplete"}:
        raise MalformedModelResponseError()
    output = getattr(response, "output", None)
    if not isinstance(output, list):
        raise MalformedModelResponseError()
    texts: list[str] = []
    for item in output:
        if getattr(item, "type", None) != "message":
            continue  # razonamiento u otros elementos: no son la respuesta
        for block in getattr(item, "content", None) or []:
            kind = getattr(block, "type", None)
            if kind == "refusal":
                raise ModelRefusedError()
            if kind == "output_text":
                text = getattr(block, "text", None)
                if not isinstance(text, str):
                    raise MalformedModelResponseError()
                if text.strip():
                    texts.append(text.strip())
    if not texts:
        raise EmptyModelResponseError()
    answer = "\n\n".join(texts)
    if status == "incomplete":  # recortada por max_output_tokens
        answer += f"\n\n{TRUNCATED_NOTICE}"
    usage = getattr(response, "usage", None)
    return ModelReply(
        answer,
        input_tokens=_int(getattr(usage, "input_tokens", None)),
        output_tokens=_int(getattr(usage, "output_tokens", None)),
    )


def _int(value: object) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _log_usage(provider: OpenAIProvider, response: object, started: float) -> None:
    """Consumo de la llamada, para vigilar el coste. Sin contenido de la petición ni respuesta."""
    usage = getattr(response, "usage", None)
    entry = {
        "event": "a2a.model",
        "provider": provider.name,
        "model": provider.model,
        "served_by": getattr(response, "model", None),
        "status": getattr(response, "status", None),
        "input_tokens": getattr(usage, "input_tokens", None),
        "output_tokens": getattr(usage, "output_tokens", None),
        "provider_request": getattr(response, "_request_id", None),
        "ms": round((time.perf_counter() - started) * 1000),
    }
    logger.info(json.dumps(entry, ensure_ascii=False, sort_keys=True, default=str))
