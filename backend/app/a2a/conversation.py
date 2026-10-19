"""Memoria de cada conversación con el tutor (A2A `contextId`), solo en memoria (ADR-0036).

Para que el tutor siga el hilo necesita recordar unas pocas cosas de los turnos anteriores: de qué
concepto se hablaba, cuántas pistas ha dado, qué pregunta de comprobación ha hecho y si el alumno
la ha acertado. Nada más:

- No se guarda la conversación completa: de cada turno, la intención, el concepto y un extracto
  corto de la pregunta y de la respuesta (lo que se reenvía al modelo como contexto).
- Vive en memoria del proceso: se borra al reiniciar, caduca a las 2 horas sin uso y hay un máximo
  de conversaciones por usuario y en total. No va a la base de datos ni a los logs.
- La clave es el propietario de la sesión + el `contextId`: un alumno nunca lee la de otro aunque
  conozca su `contextId`.
"""

import time
from collections import OrderedDict, deque
from dataclasses import dataclass, field

TURNS_KEPT = 6
EXCERPT_QUESTION = 240
EXCERPT_ANSWER = 480
CONVERSATIONS_PER_USER = 5
CONVERSATIONS_TOTAL = 5_000
IDLE_SECONDS = 2 * 60 * 60


def excerpt(text: str, limit: int) -> str:
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


@dataclass(frozen=True)
class Turn:
    intent: str
    concept: str | None
    question: str  # extracto
    answer: str  # extracto


@dataclass
class Conversation:
    turns: deque[Turn] = field(default_factory=lambda: deque(maxlen=TURNS_KEPT))
    concept: str | None = None  # tema actual
    hints: dict[str, int] = field(default_factory=dict)  # pistas dadas por lección o concepto
    pending_check: str | None = None  # id del ejercicio de predicción que el tutor ha preguntado
    asked_checks: list[str] = field(default_factory=list)
    correct: list[str] = field(default_factory=list)  # conceptos comprobados en esta conversación
    wrong: list[str] = field(default_factory=list)  # conceptos en que ha fallado la comprobación
    gradual: bool = False

    def remember(self, turn: Turn) -> None:
        self.turns.append(turn)
        if turn.concept:
            self.concept = turn.concept


class ConversationStore:
    """Conversaciones recientes por propietario. Acotada en número, tamaño y tiempo."""

    def __init__(
        self,
        per_user: int = CONVERSATIONS_PER_USER,
        total: int = CONVERSATIONS_TOTAL,
        idle_seconds: float = IDLE_SECONDS,
        clock=time.monotonic,
    ):
        self.per_user = per_user
        self.total = total
        self.idle_seconds = idle_seconds
        self.clock = clock
        self._items: OrderedDict[tuple[str, str], tuple[float, Conversation]] = OrderedDict()

    def get(self, owner: str, context_id: str) -> Conversation:
        """La conversación (nueva si no existe o ha caducado). Se guarda al pedirla."""
        now = self.clock()
        self._expire(now)
        key = (owner, context_id)
        _, conversation = self._items.pop(key, (now, Conversation()))
        self._items[key] = (now, conversation)
        mine = [item for item in self._items if item[0] == owner]
        for old in mine[: max(0, len(mine) - self.per_user)]:
            del self._items[old]
        while len(self._items) > self.total:
            self._items.popitem(last=False)
        return conversation

    def _expire(self, now: float) -> None:
        while self._items:
            key, (seen, _) = next(iter(self._items.items()))
            if now - seen <= self.idle_seconds:
                return
            del self._items[key]

    def __len__(self) -> int:
        return len(self._items)
