"""Executor A2A del Python Tutor: del mensaje A2A a la respuesta, pasando por el agente.

Flujo de cada mensaje (A2A 1.x): tarea enviada → en curso → artefacto con la respuesta → completada.
Es el mismo esquema que necesitará el streaming: bastará con publicar más actualizaciones.

La lógica educativa está en `agents/python_tutor.py` y los datos del alumno los da el servicio
`services/learning_context.py`; aquí solo hay transporte, validación y manejo de errores.

Tutor híbrido (ADR-0038): el alumno pide una modalidad («free» por defecto, o «advanced») y aquí se
decide si se le concede. La IA avanzada solo se usa si el backend la tiene activada, el mensaje
cabe en su límite de caracteres, necesita un modelo y queda cuota (`services/tutor_usage.py`). Si
no, se explica por qué y se ofrece la respuesta gratuita. Al revés nunca: una petición gratuita no
se convierte en una llamada de pago, ni siquiera si el proveedor gratuito falla.
"""

import asyncio
import time
from collections.abc import Callable
from dataclasses import dataclass

from a2a.helpers import get_data_parts, get_text_parts, new_task
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import Message, Part, TaskState
from pydantic import ValidationError

from app.a2a.agents.python_tutor import PythonTutorAgent, TutorPlan, TutorQuery
from app.a2a.conversation import ConversationStore
from app.a2a.observability import log_task, log_usage_error
from app.a2a.providers.base import (
    AgentModelProvider,
    ModelConfigurationError,
    ModelRateLimitedError,
    ModelTimeoutError,
    ModelUnavailableError,
)
from app.services.learning_context import LearnerContext
from app.services.tutor_usage import QuotaExceeded, Reservation, UsageLedger

# Claves que la ruta de FastAPI deja en el contexto de la llamada (ver server.py)
LEARNING_STATE_KEY = "pld_learning_context"
BUDGET_STATE_KEY = "pld_model_budget"
CORRELATION_STATE_KEY = "pld_request_id"
USAGE_STATE_KEY = "pld_tutor_usage"

LearningLoader = Callable[[str | None], LearnerContext]
TakeModelQuery = Callable[[], bool]  # gasta una consulta al modelo; False si no quedan

INVALID_INPUT = (
    "No he podido leer tu mensaje. Escribe tu pregunta como texto (máximo 4000 caracteres) y, si "
    "quieres, añade un objeto JSON con lesson_slug, code, error o level."
)
FAILED = "El tutor no ha podido responder ahora mismo. Inténtalo de nuevo en unos segundos."
LIMITED = (
    "Has llegado al límite de consultas al tutor por ahora. Mientras tanto, prueba tu código en la "
    "consola de la lección; podrás volver a preguntar más tarde."
)
CANCELED = "Consulta cancelada."
PROVIDER_LIMITED = (
    "El servicio de IA del tutor ha alcanzado su límite de uso por ahora. Inténtalo más tarde."
)
FALLBACK = "**Mientras tanto, esto es lo que puedo decirte sin IA:**"
# Tutor híbrido: por qué no se atiende una petición de IA avanzada (siempre con la alternativa)
FREE_INSTEAD = "**Respuesta del modo gratuito (sin IA de pago):**"
ADVANCED_UNAVAILABLE = (
    "La IA avanzada no está activada en este servidor, así que no se ha usado. Puedes seguir en "
    "el modo gratuito."
)
ADVANCED_USER_LIMIT = (
    "Has usado todas tus consultas de IA avanzada de hoy ({limit}). El contador se reinicia a "
    "medianoche (hora UTC). Mientras tanto, sigue en el modo gratuito: no tiene límite diario de "
    "este tipo."
)
ADVANCED_GLOBAL_LIMIT = (
    "La IA avanzada ha llegado a su límite de uso de hoy para todos los alumnos. Vuelve a "
    "intentarlo mañana o sigue en el modo gratuito."
)
ADVANCED_TOO_LONG = (
    "Tu mensaje es demasiado largo para la IA avanzada (máximo {limit} caracteres entre pregunta, "
    "código y error). Acórtalo o sigue en el modo gratuito."
)
# Fallos del proveedor de pago que no se cobran: la consulta se devuelve al alumno
NOT_CHARGED: tuple[type[BaseException], ...] = (ModelRateLimitedError, ModelConfigurationError)

# Motivo de cada fallo, en los metadatos del mensaje de estado: el cliente lo explica sin tener
# que leer el texto (la web distingue «no disponible», «límite» y «error temporal»).
REASONS: tuple[tuple[type[BaseException], str], ...] = (
    (ModelTimeoutError, "provider_timeout"),
    (ModelRateLimitedError, "provider_rate_limited"),
    (ModelConfigurationError, "provider_unavailable"),
    (ModelUnavailableError, "provider_unavailable"),
)


class InvalidTutorMessage(ValueError):
    """El mensaje A2A no tiene la forma que espera el tutor."""


class ModelBudgetExhausted(Exception):
    """No quedan consultas al modelo (por usuario y día, o de todos por minuto)."""


class AdvancedRefused(Exception):
    """No se concede la IA avanzada: `reason` es el motivo que verá el cliente."""

    def __init__(self, reason: str, text: str):
        super().__init__(reason)
        self.reason = reason
        self.text = text


@dataclass(frozen=True)
class AdvancedMode:
    """La modalidad «IA avanzada»: su proveedor y el límite de caracteres de entrada."""

    model: AgentModelProvider
    max_input_chars: int
    daily_limit: int


def input_chars(query: TutorQuery) -> int:
    return sum(len(text or "") for text in (query.question, query.code, query.error))


def parse_message(message: Message | None) -> TutorQuery:
    """Texto = pregunta; parte de datos opcional = lección, código, error y nivel.

    Se rechazan archivos y URLs: el tutor no descarga nada (sin SSRF) ni lee archivos.
    """
    if message is None:
        raise InvalidTutorMessage("sin mensaje")
    if any(part.HasField("raw") or part.HasField("url") for part in message.parts):
        raise InvalidTutorMessage("partes no admitidas")
    data = get_data_parts(message.parts)
    if len(data) > 1 or (data and not isinstance(data[0], dict)):
        raise InvalidTutorMessage("datos no válidos")
    fields = data[0] if data else {}
    try:
        return TutorQuery(question="\n".join(get_text_parts(message.parts)), **fields)
    except (ValidationError, TypeError) as error:
        raise InvalidTutorMessage("campos no válidos") from error


class PythonTutorExecutor(AgentExecutor):
    def __init__(
        self,
        agent: PythonTutorAgent,
        conversations: ConversationStore | None = None,
        advanced: AdvancedMode | None = None,
    ):
        self.agent = agent
        # IA avanzada (de pago); None = desactivada en este servidor
        self.advanced = advanced
        # Memoria de cada conversación (contextId) de cada usuario, solo en memoria
        self.conversations = conversations or ConversationStore()

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        started = time.perf_counter()
        state = context.call_context.state
        loader: LearningLoader | None = state.get(LEARNING_STATE_KEY)
        budget: TakeModelQuery | None = state.get(BUDGET_STATE_KEY)
        usage: UsageLedger | None = state.get(USAGE_STATE_KEY)
        task = context.current_task or new_task(
            context.task_id,
            context.context_id,
            TaskState.TASK_STATE_SUBMITTED,
            history=[context.message] if context.message else [],
        )

        plan: TutorPlan | None = None
        model = self.agent.model  # el que responde: el gratuito salvo que se conceda la avanzada
        reservation: Reservation | None = None

        def log(outcome: str, error: BaseException | None = None, **details) -> None:
            if plan is not None:
                details |= {"intent": plan.intent, "level": plan.level.level}
            log_task(
                agent=self.agent.name,
                provider=model.name,
                model=model.model,
                task_id=task.id,
                context_id=task.context_id,
                request_id=state.get(CORRELATION_STATE_KEY),
                user=context.call_context.user.user_name,
                outcome=outcome,
                started=started,
                error=error,
                **details,
            )

        # Primero lo que necesita la sesión de base de datos de la petición; luego, la tarea
        try:
            query = parse_message(context.message)
            learner = await asyncio.to_thread(loader, query.lesson_slug) if loader else None
        except Exception as error:
            query, problem = None, error
        else:
            problem = None

        if context.current_task is None:
            await event_queue.enqueue_event(task)
        updater = TaskUpdater(event_queue, task.id, task.context_id)
        try:
            if problem is not None:
                raise problem
            owner = context.call_context.user.user_name
            conversation = self.conversations.get(owner, task.context_id)
            plan = self.agent.plan(query, learner, conversation)
            advanced = query.mode == "advanced"
            if advanced:
                self._check_advanced(query)
            # Solo gastan consulta los mensajes válidos que necesitan el modelo. La avanzada tiene
            # su propia cuota, en la base de datos; la gratuita, los límites de siempre
            if plan.needs_model and advanced:
                reservation = await self._reserve(usage)
                model = self.advanced.model
            elif plan.needs_model and budget is not None and not budget():
                raise ModelBudgetExhausted()
            await updater.start_work()
            answer = await self.agent.respond(plan, model)
        except asyncio.CancelledError:
            log("canceled")
            raise
        except AdvancedRefused as error:
            text = error.text
            if plan is not None:  # la respuesta gratuita, que sigue la conversación como cualquiera
                text = f"{text}\n\n{FREE_INSTEAD}\n\n{plan.prepared_text}"
                self.agent.remember(plan, self.agent.prepared_answer(plan))
                if usage is not None:
                    await self._safely(usage.count_free)
            await updater.reject(self._status(updater, text, error.reason))
            log("rejected", error, reason=error.reason)
            return
        except InvalidTutorMessage as error:
            await updater.reject(self._status(updater, INVALID_INPUT, "invalid_input"))
            log("rejected", error, reason="invalid_input")
            return
        except ModelBudgetExhausted as error:
            await updater.reject(self._status(updater, LIMITED, "limit_reached"))
            log("limited", error, reason="limit_reached")
            return
        except Exception as error:  # el detalle se queda en el log (solo el tipo), nunca al cliente
            reason = next((code for kind, code in REASONS if isinstance(error, kind)), "error")
            if reason == "error":
                text = FAILED
            else:
                text = (
                    PROVIDER_LIMITED
                    if reason == "provider_rate_limited"
                    else model.unavailable_message
                )
                if plan is not None:  # sin IA, el alumno no se queda sin nada
                    text = f"{text}\n\n{FALLBACK}\n\n{plan.prepared_text}"
            if reservation is not None and isinstance(error, NOT_CHARGED):
                await self._safely(usage.refund_advanced, reservation)
            await updater.failed(self._status(updater, text, reason))
            log("failed", error, reason=reason)
            return

        self.agent.remember(plan, answer)
        tokens = (getattr(answer, "input_tokens", None), getattr(answer, "output_tokens", None))
        if usage is not None:
            if reservation is not None:
                await self._safely(usage.add_tokens, reservation, *tokens)
            else:
                await self._safely(usage.count_free, *tokens)
        mode = "advanced" if reservation is not None else "free"
        extra = {"quota_remaining": reservation.remaining} if reservation is not None else {}
        await updater.add_artifact(
            [Part(text=answer.text, media_type="text/plain")],
            name="respuesta",
            metadata={
                "level": answer.level,
                "provider": answer.provider,
                "model": answer.model,
                "source": answer.source,
                "intent": answer.intent,
                "expects_answer": answer.expects_answer,
                "mode": mode,
                **extra,
            },
        )
        await updater.complete()
        log("completed", source=answer.source, mode=mode)

    def _check_advanced(self, query: TutorQuery) -> None:
        """¿Se puede atender en modalidad avanzada? Lo decide el servidor, no el cliente."""
        if self.advanced is None:
            raise AdvancedRefused("advanced_unavailable", ADVANCED_UNAVAILABLE)
        limit = self.advanced.max_input_chars
        if input_chars(query) > limit:
            raise AdvancedRefused("advanced_input_too_long", ADVANCED_TOO_LONG.format(limit=limit))

    async def _reserve(self, usage: UsageLedger | None) -> Reservation:
        if usage is None:  # sin contabilidad no hay forma de limitar el gasto: no se usa
            raise AdvancedRefused("advanced_unavailable", ADVANCED_UNAVAILABLE)
        try:
            return await asyncio.to_thread(usage.reserve_advanced)
        except QuotaExceeded as error:
            if error.scope == "user":
                limit = self.advanced.daily_limit if self.advanced else 0
                raise AdvancedRefused(
                    "advanced_limit_reached", ADVANCED_USER_LIMIT.format(limit=limit)
                ) from None
            raise AdvancedRefused("advanced_global_limit", ADVANCED_GLOBAL_LIMIT) from None

    @staticmethod
    async def _safely(action: Callable, *args) -> None:
        """La contabilidad nunca tumba una respuesta ya dada: un fallo solo va al log (el tipo)."""
        try:
            await asyncio.to_thread(action, *args)
        except Exception as error:
            log_usage_error(error)

    @staticmethod
    def _status(updater: TaskUpdater, text: str, reason: str) -> Message:
        return updater.new_agent_message([Part(text=text)], metadata={"reason": reason})

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        updater = TaskUpdater(event_queue, context.task_id, context.context_id)
        await updater.cancel(updater.new_agent_message([Part(text=CANCELED)]))
