"""Interfaz común de los modelos de lenguaje.

Los agentes no dependen de ningún proveedor concreto: reciben un `AgentModelProvider`. Para
conectar Anthropic, OpenAI o un modelo local basta con otra clase que implemente `generate`.
"""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ModelRequest:
    """Lo que el agente pide al modelo.

    - system: instrucciones de comportamiento (tutor, no solucionador).
    - prompt: la pregunta del alumno con el contexto educativo mínimo.
    - outline: la guía que el propio agente ha preparado (conceptos, pista, siguiente paso). Un
      modelo real la recibe dentro del prompt; el simulado la devuelve tal cual.
    """

    system: str
    prompt: str
    outline: str


class AgentModelProvider(Protocol):
    name: str

    async def generate(self, request: ModelRequest) -> str:
        """Devuelve el texto de la respuesta. Los errores se lanzan como excepciones."""
        ...
