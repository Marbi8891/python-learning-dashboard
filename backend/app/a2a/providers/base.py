"""Interfaz común de los modelos de lenguaje.

Los agentes no dependen de ningún proveedor concreto: reciben un `AgentModelProvider`. Hoy existen
Ollama (modelo local, el predeterminado), Anthropic (opcional) y el simulado (desarrollo y
tests); para OpenAI basta con otra clase que implemente `generate` y lance las excepciones de aquí.
"""

from dataclasses import dataclass
from typing import Protocol

# Se añade a una respuesta que el modelo ha cortado por el límite de tokens
TRUNCATED_NOTICE = (
    "_(Respuesta recortada por longitud: pregúntame por la parte que te falte y sigo.)_"
)


@dataclass(frozen=True)
class ModelRequest:
    """Lo que el agente pide al modelo. Es TODO lo que sale hacia el proveedor.

    - system: instrucciones de comportamiento (tutor, no solucionador).
    - prompt: la pregunta del alumno con el contexto educativo mínimo.
    - outline: la guía que el propio agente ha preparado (conceptos, pista, siguiente paso). Un
      modelo real la recibe dentro del prompt; el simulado la devuelve tal cual.
    """

    system: str
    prompt: str
    outline: str


class AgentModelProvider(Protocol):
    name: str  # proveedor: «ollama», «anthropic», «mock»…
    model: str  # modelo concreto (para los logs y los metadatos de la respuesta)
    # Lo que ve el alumno si el modelo no está disponible (caído, lento o mal configurado)
    unavailable_message: str

    async def generate(self, request: ModelRequest) -> str:
        """Devuelve el texto de la respuesta. Los fallos se lanzan como `ModelProviderError`."""
        ...


class ModelProviderError(Exception):
    """Fallo del proveedor. Nunca lleva la petición, la respuesta ni credenciales: el nombre de la
    clase es todo lo que llega a los logs y el alumno solo ve un mensaje genérico."""


class ModelConfigurationError(ModelProviderError):
    """API key inválida o sin permisos, o modelo que no existe: lo tiene que arreglar quien
    despliega."""


class ModelTimeoutError(ModelProviderError):
    """El proveedor no ha respondido a tiempo."""


class ModelRateLimitedError(ModelProviderError):
    """El proveedor limita las peticiones de la cuenta (429)."""


class ModelUnavailableError(ModelProviderError):
    """Red caída o error del proveedor (5xx)."""


class ModelRequestError(ModelProviderError):
    """El proveedor rechaza la petición (4xx)."""


class ModelRefusedError(ModelProviderError):
    """El modelo se ha negado a responder."""


class EmptyModelResponseError(ModelProviderError):
    """Respuesta sin texto."""


class MalformedModelResponseError(ModelProviderError):
    """Respuesta con una forma inesperada."""
