"""Montaje de los agentes A2A en la aplicación FastAPI existente (ADR-0034).

Cada agente vive bajo /a2a/<id>:
- GET  /a2a/<id>/.well-known/agent-card.json → Agent Card (pública: solo describe al agente).
- POST /a2a/<id>                              → JSON-RPC de A2A 1.0 (con sesión).
Además, /.well-known/agent-card.json (la ruta estándar de descubrimiento) sirve la del agente
principal, el Python Tutor.

El protocolo lo implementa el SDK oficial (`a2a-sdk`); aquí solo se añade lo del proyecto:
- Autenticación con la misma sesión que la API REST (`get_current_user`: Bearer o cookie).
- Límite de mensajes por usuario y minuto.
- Las tareas de cada usuario solo las ve ese usuario (el «propietario» es el id de la sesión).
- El contexto de la llamada solo lleva lo imprescindible: nunca el token ni las cookies.

Para añadir un agente: su card, su agente y su executor, y una entrada en `AGENTS`.
"""

import logging
import uuid
from collections import OrderedDict
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from functools import partial

from a2a.auth.user import User as A2AUser
from a2a.extensions.common import HTTP_EXTENSION_HEADER, get_requested_extensions
from a2a.server.agent_execution import AgentExecutor
from a2a.server.context import ServerCallContext
from a2a.server.owner_resolver import resolve_user_scope
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import (
    ServerCallContextBuilder,
    add_a2a_routes_to_fastapi,
    create_agent_card_routes,
    create_jsonrpc_routes,
)
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCard, Task
from a2a.utils.constants import AGENT_CARD_WELL_KNOWN_PATH, VERSION_HEADER
from fastapi import APIRouter, FastAPI, HTTPException, Request, Response, status

from app.a2a.agents.python_tutor import PythonTutorAgent
from app.a2a.cards.python_tutor import build_python_tutor_card
from app.a2a.executors.python_tutor import (
    CORRELATION_STATE_KEY,
    LEARNING_STATE_KEY,
    PythonTutorExecutor,
)
from app.a2a.providers import AgentModelProvider, MockModelProvider
from app.config import Settings
from app.deps import CurrentUser, DbSession
from app.rate_limit import TOO_MANY, RateLimiter
from app.security_events import Event, record
from app.services.learning_context import load_learner_context

# El SDK escribe el cuerpo de cada petición en DEBUG: nunca debe llegar a los logs
logging.getLogger("a2a").setLevel(logging.WARNING)

A2A_PREFIX = "/a2a"
# Tareas que se guardan por usuario (en memoria): las más recientes
TASKS_KEPT_PER_USER = 20


@dataclass(frozen=True)
class AgentSpec:
    id: str
    build_card: Callable[[str, bool], AgentCard]
    build_executor: Callable[[AgentModelProvider], AgentExecutor]


AGENTS: tuple[AgentSpec, ...] = (
    AgentSpec(
        id=PythonTutorAgent.name,
        build_card=build_python_tutor_card,
        build_executor=lambda model: PythonTutorExecutor(PythonTutorAgent(model)),
    ),
)


def build_model_provider(settings: Settings) -> AgentModelProvider:
    """De momento solo existe el modelo simulado; un proveedor real se añadiría aquí."""
    if settings.a2a_mock_model:
        return MockModelProvider()
    raise RuntimeError(
        "A2A_ENABLED=true necesita un modelo. En esta versión solo existe el simulado de "
        "desarrollo: añade A2A_MOCK_MODEL=true (nunca en producción) o desactiva A2A."
    )


class SessionUser(A2AUser):
    """Usuario de la sesión de la API, visto desde el SDK de A2A."""

    def __init__(self, user_id: int, created_at: datetime):
        self.user_id = user_id
        self.created_at = created_at

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def user_name(self) -> str:
        # El SDK lo usa como propietario de las tareas: cada usuario solo ve las suyas. La fecha de
        # alta evita que una cuenta nueva que reciba el id de una borrada (SQLite puede reutilizar
        # ids) vea las tareas que aún estén en memoria.
        return f"user:{self.user_id}:{self.created_at.timestamp():.0f}"


class SessionContextBuilder(ServerCallContextBuilder):
    """Contexto mínimo: usuario, versión de A2A, extensiones y el lector de datos educativos.

    No copia las cabeceras (el constructor por defecto del SDK guarda todas, incluidas
    `Authorization` y `Cookie`): así el token nunca llega a la capa de agentes.
    """

    def build(self, request: Request) -> ServerCallContext:
        state = {
            "headers": {VERSION_HEADER: request.headers.get(VERSION_HEADER, "")},
            LEARNING_STATE_KEY: request.state.pld_learning,
            CORRELATION_STATE_KEY: request.state.pld_request_id,
        }
        return ServerCallContext(
            user=SessionUser(request.state.pld_user.id, request.state.pld_user.created_at),
            state=state,
            requested_extensions=get_requested_extensions(
                request.headers.getlist(HTTP_EXTENSION_HEADER)
            ),
        )


class BoundedTaskStore(InMemoryTaskStore):
    """Tareas en memoria, con un máximo por usuario para que la memoria no crezca sin límite.

    Se pierden al reiniciar el servidor: son conversaciones de un momento, no datos del alumno.
    """

    def __init__(self, kept_per_owner: int = TASKS_KEPT_PER_USER):
        super().__init__()
        self.kept_per_owner = kept_per_owner
        self._order: dict[str, OrderedDict[str, None]] = {}

    async def save(self, task: Task, context: ServerCallContext) -> None:
        await super().save(task, context)
        order = self._order.setdefault(resolve_user_scope(context), OrderedDict())
        order[task.id] = None
        order.move_to_end(task.id)
        while len(order) > self.kept_per_owner:
            oldest, _ = order.popitem(last=False)
            await super().delete(oldest, context)


def mount_a2a(app: FastAPI, settings: Settings) -> None:
    """Añade las rutas A2A de todos los agentes a la app. Falla al arrancar si falta el modelo."""
    model = build_model_provider(settings)
    limiter = app.state.a2a_limiter = RateLimiter(settings.a2a_rate_limit_per_minute)
    base_url = settings.a2a_base_url.rstrip("/")
    for index, spec in enumerate(AGENTS):
        path = f"{A2A_PREFIX}/{spec.id}"
        card = spec.build_card(f"{base_url}{path}", settings.a2a_mock_model)
        handler = DefaultRequestHandler(
            agent_executor=spec.build_executor(model),
            task_store=BoundedTaskStore(),
            agent_card=card,
        )
        card_routes = create_agent_card_routes(card, card_url=f"{path}{AGENT_CARD_WELL_KNOWN_PATH}")
        if index == 0:  # el agente principal también en la ruta estándar de descubrimiento
            card_routes += create_agent_card_routes(card)
        add_a2a_routes_to_fastapi(app, agent_card_routes=card_routes)
        jsonrpc = create_jsonrpc_routes(
            handler, rpc_url=path, context_builder=SessionContextBuilder()
        )[0].endpoint
        app.include_router(_session_router(path, jsonrpc, limiter))


def _session_router(path: str, jsonrpc: Callable, limiter: RateLimiter) -> APIRouter:
    """Ruta JSON-RPC protegida con la sesión de la API (el SDK no la conoce)."""
    router = APIRouter(tags=["A2A: JSON-RPC"])

    @router.post(path, summary="A2A JSON-RPC 1.0 (requiere sesión)")
    async def a2a_jsonrpc(request: Request, user: CurrentUser, db: DbSession) -> Response:
        if not limiter.hit(f"user:{user.id}"):
            record(Event.RATE_LIMITED, request, user=user.id)
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=TOO_MANY)
        request.state.pld_user = user
        request.state.pld_learning = partial(load_learner_context, db, user.id)
        request.state.pld_request_id = str(uuid.uuid4())
        response = await jsonrpc(request)
        response.headers["X-Request-ID"] = request.state.pld_request_id
        return response

    return router
