"""Executor A2A del Python Tutor: del mensaje A2A a la respuesta, pasando por el agente.

Flujo de cada mensaje (A2A 1.x): tarea enviada → en curso → artefacto con la respuesta → completada.
Es el mismo esquema que necesitará el streaming: bastará con publicar más actualizaciones.

La lógica educativa está en `agents/python_tutor.py` y los datos del alumno los da el servicio
`services/learning_context.py`; aquí solo hay transporte, validación y manejo de errores.
"""

import asyncio
import time
from collections.abc import Callable

from a2a.helpers import get_data_parts, get_text_parts, new_task
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import Message, Part, TaskState
from pydantic import ValidationError

from app.a2a.agents.python_tutor import PythonTutorAgent, TutorQuery
from app.a2a.observability import log_task
from app.services.learning_context import LearnerContext

# Claves que la ruta de FastAPI deja en el contexto de la llamada (ver server.py)
LEARNING_STATE_KEY = "pld_learning_context"
CORRELATION_STATE_KEY = "pld_request_id"

LearningLoader = Callable[[str | None], LearnerContext]

INVALID_INPUT = (
    "No he podido leer tu mensaje. Escribe tu pregunta como texto (máximo 4000 caracteres) y, si "
    "quieres, añade un objeto JSON con lesson_slug, code, error o level."
)
FAILED = "El tutor no ha podido responder ahora mismo. Inténtalo de nuevo en unos segundos."
CANCELED = "Consulta cancelada."


class InvalidTutorMessage(ValueError):
    """El mensaje A2A no tiene la forma que espera el tutor."""


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
    def __init__(self, agent: PythonTutorAgent):
        self.agent = agent

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        started = time.perf_counter()
        state = context.call_context.state
        loader: LearningLoader | None = state.get(LEARNING_STATE_KEY)
        task = context.current_task or new_task(
            context.task_id,
            context.context_id,
            TaskState.TASK_STATE_SUBMITTED,
            history=[context.message] if context.message else [],
        )

        def log(outcome: str, error: BaseException | None = None) -> None:
            log_task(
                agent=self.agent.name,
                task_id=task.id,
                context_id=task.context_id,
                request_id=state.get(CORRELATION_STATE_KEY),
                user=context.call_context.user.user_name,
                outcome=outcome,
                started=started,
                error=error,
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
            await updater.start_work()
            answer = await self.agent.answer(query, learner)
        except asyncio.CancelledError:
            log("canceled")
            raise
        except InvalidTutorMessage as error:
            await updater.reject(updater.new_agent_message([Part(text=INVALID_INPUT)]))
            log("rejected", error)
            return
        except Exception as error:  # el detalle se queda en el log (solo el tipo), nunca al cliente
            await updater.failed(updater.new_agent_message([Part(text=FAILED)]))
            log("failed", error)
            return

        await updater.add_artifact(
            [Part(text=answer.text, media_type="text/plain")],
            name="respuesta",
            metadata={"level": answer.level, "model": answer.model},
        )
        await updater.complete()
        log("completed")

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        updater = TaskUpdater(event_queue, context.task_id, context.context_id)
        await updater.cancel(updater.new_agent_message([Part(text=CANCELED)]))
