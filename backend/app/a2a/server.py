"""Montaje de los agentes A2A en la aplicación FastAPI existente (ADR-0034).

Cada agente vive bajo /a2a/<id>:
- GET  /a2a/<id>/.well-known/agent-card.json → Agent Card (pública: solo describe al agente).
- POST /a2a/<id>                              → JSON-RPC de A2A 1.0 (con sesión).
Además, /.well-known/agent-card.json (la ruta estándar de descubrimiento) sirve la del agente
principal, el Python Tutor.

El protocolo lo implementa el SDK oficial (`a2a-sdk`); aquí solo se añade lo del proyecto:
- Autenticación con la misma sesión que la API REST (`get_current_user`: Bearer o cookie).
- Límites: mensajes por usuario y minuto, y consultas al modelo por usuario y día y de todos los
  usuarios por minuto (el coste del proveedor no puede crecer sin tope).
- Las tareas de cada usuario solo las ve ese usuario (el «propietario» es el id de la sesión).
- El contexto de la llamada solo lleva lo imprescindible: nunca el token ni las cookies.

Tutor híbrido (ADR-0038): además del proveedor de siempre (modalidad gratuita), el tutor puede
tener una modalidad «IA avanzada» (A2A_ADVANCED_PROVIDER, OpenAI) con cuotas en la base de datos.
`GET /api/v1/tutor/modes` dice a la web qué modalidades hay y cuánta cuota le queda al alumno.

Para añadir un agente: su card, su agente y su executor, y una entrada en `AGENTS`.
"""

import logging
import uuid
from collections import OrderedDict
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from functools import partial
from typing import Literal

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
from pydantic import BaseModel

from app.a2a.agents.python_tutor import PythonTutorAgent
from app.a2a.cards.python_tutor import build_python_tutor_card
from app.a2a.executors.python_tutor import (
    BUDGET_STATE_KEY,
    CORRELATION_STATE_KEY,
    LEARNING_STATE_KEY,
    USAGE_STATE_KEY,
    AdvancedMode,
    PythonTutorExecutor,
)
from app.a2a.providers import AgentModelProvider, MockModelProvider
from app.config import Settings
from app.deps import CurrentUser, DbSession
from app.rate_limit import TOO_MANY, RateLimiter
from app.security_events import Event, record
from app.services.learning_context import load_learner_context
from app.services.tutor_usage import AdvancedLimits, UsageLedger

# El SDK escribe el cuerpo de cada petición en DEBUG: nunca debe llegar a los logs
logging.getLogger("a2a").setLevel(logging.WARNING)
logger = logging.getLogger("pld.a2a")

A2A_PREFIX = "/a2a"
# Tareas que se guardan por usuario (en memoria): las más recientes
TASKS_KEPT_PER_USER = 20
DAY = 24 * 60 * 60
ALL_USERS = "all"


@dataclass(frozen=True)
class AgentSpec:
    id: str
    build_card: Callable[[str, bool], AgentCard]
    build_executor: Callable[[AgentModelProvider, AdvancedMode | None], AgentExecutor]


AGENTS: tuple[AgentSpec, ...] = (
    AgentSpec(
        id=PythonTutorAgent.name,
        build_card=build_python_tutor_card,
        build_executor=lambda model, advanced: PythonTutorExecutor(
            PythonTutorAgent(model), advanced=advanced
        ),
    ),
)


def build_model_provider(settings: Settings) -> AgentModelProvider:
    """El proveedor del modelo según la configuración. Falla al arrancar si es Anthropic sin clave
    o si la URL de Ollama no es válida.

    Para añadir otro proveedor (OpenAI…): su clase en `providers/`, un valor más en
    A2A_MODEL_PROVIDER y su rama aquí. Los agentes no cambian.
    """
    if settings.a2a_mock_model or settings.a2a_model_provider == "mock":
        return MockModelProvider()
    if settings.a2a_model_provider == "ollama":
        from app.a2a.providers.ollama_provider import DEFAULT_MODEL, OllamaProvider

        return OllamaProvider(
            base_url=settings.a2a_ollama_base_url,
            model=settings.a2a_model or DEFAULT_MODEL,
            max_tokens=settings.a2a_max_output_tokens,
            timeout_seconds=settings.a2a_model_timeout_seconds,
        )
    # Anthropic (de pago): solo si se ha elegido expresamente
    secret = settings.anthropic_api_key
    key = secret.get_secret_value().strip() if secret else ""
    if not key:
        raise RuntimeError(
            "A2A_MODEL_PROVIDER=anthropic necesita ANTHROPIC_API_KEY (variable de entorno o gestor "
            "de secretos). Para desarrollo y tests sin API key: A2A_MOCK_MODEL=true."
        )
    from app.a2a.providers.anthropic_provider import DEFAULT_MODEL, AnthropicProvider

    return AnthropicProvider(
        api_key=key,
        model=settings.a2a_model or DEFAULT_MODEL,
        max_tokens=settings.a2a_max_output_tokens,
        timeout_seconds=settings.a2a_model_timeout_seconds,
    )


def build_advanced_mode(settings: Settings) -> AdvancedMode | None:
    """La modalidad «IA avanzada» del tutor híbrido, o None si no está activada.

    A diferencia del proveedor principal, una configuración incompleta no impide arrancar: la IA
    avanzada se queda desactivada (se avisa en el log, sin secretos) y el tutor gratuito sigue.
    """
    provider = settings.a2a_advanced_provider
    if provider == "none":
        return None
    if provider == "mock":
        model: AgentModelProvider = MockModelProvider()
    else:
        secret = settings.openai_api_key
        key = secret.get_secret_value().strip() if secret else ""
        name = (settings.a2a_advanced_model or "").strip()
        if not key or not name:
            missing = "OPENAI_API_KEY" if not key else "A2A_ADVANCED_MODEL"
            logger.error(
                f'{{"event": "a2a.config", "advanced": "disabled", "missing": "{missing}"}}'
            )
            return None
        from app.a2a.providers.openai_provider import OpenAIProvider

        model = OpenAIProvider(
            api_key=key,
            model=name,
            max_output_tokens=settings.a2a_advanced_max_output_tokens,
            timeout_seconds=settings.a2a_advanced_timeout_seconds,
            reasoning_effort=settings.a2a_advanced_reasoning_effort,
        )
    return AdvancedMode(
        model=model,
        max_input_chars=settings.a2a_advanced_max_input_chars,
        daily_limit=settings.a2a_advanced_daily_limit_per_user,
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
    """Contexto mínimo: usuario, versión de A2A, extensiones, el lector de datos educativos y el
    contador de consultas al modelo.

    No copia las cabeceras (el constructor por defecto del SDK guarda todas, incluidas
    `Authorization` y `Cookie`): así el token nunca llega a la capa de agentes.
    """

    def build(self, request: Request) -> ServerCallContext:
        state = {
            "headers": {VERSION_HEADER: request.headers.get(VERSION_HEADER, "")},
            LEARNING_STATE_KEY: request.state.pld_learning,
            BUDGET_STATE_KEY: request.state.pld_budget,
            CORRELATION_STATE_KEY: request.state.pld_request_id,
            USAGE_STATE_KEY: request.state.pld_usage,
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
    advanced = build_advanced_mode(settings)
    limits = AdvancedLimits(
        per_user_daily=settings.a2a_advanced_daily_limit_per_user,
        global_daily=settings.a2a_advanced_global_daily_limit,
    )
    limiter = app.state.a2a_limiter = RateLimiter(settings.a2a_rate_limit_per_minute)
    budget = app.state.a2a_budget = ModelBudget(
        per_user=RateLimiter(settings.a2a_daily_limit_per_user, window_seconds=DAY),
        overall=RateLimiter(settings.a2a_global_limit_per_minute),
    )
    base_url = settings.a2a_base_url.rstrip("/")
    executors = app.state.a2a_executors = {}
    for index, spec in enumerate(AGENTS):
        path = f"{A2A_PREFIX}/{spec.id}"
        card = spec.build_card(f"{base_url}{path}", model.name == MockModelProvider.name)
        executor = executors[spec.id] = spec.build_executor(model, advanced)
        handler = DefaultRequestHandler(
            agent_executor=executor,
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
        app.include_router(_session_router(path, jsonrpc, limiter, budget, limits))
    tutor = executors[PythonTutorAgent.name]
    app.include_router(_modes_router(tutor, limits, settings), prefix="/api/v1")


@dataclass(frozen=True)
class ModelBudget:
    """Consultas al modelo: por usuario y día, y de todos por minuto. Reutiliza el `RateLimiter`
    en memoria de la API (sin Redis): con varias instancias, cada una contaría por su cuenta."""

    per_user: RateLimiter
    overall: RateLimiter

    def take(self, user_id: int) -> bool:
        """Gasta una consulta si queda en los dos límites; si no, no cuenta ninguna."""
        key = f"user:{user_id}"
        if self.per_user.blocked(key) or self.overall.blocked(ALL_USERS):
            return False
        self.per_user.record(key)
        self.overall.record(ALL_USERS)
        return True


def _session_router(
    path: str,
    jsonrpc: Callable,
    limiter: RateLimiter,
    budget: ModelBudget,
    limits: AdvancedLimits,
) -> APIRouter:
    """Ruta JSON-RPC protegida con la sesión de la API (el SDK no la conoce)."""
    router = APIRouter(tags=["A2A: JSON-RPC"])

    @router.post(path, summary="A2A JSON-RPC 1.0 (requiere sesión)")
    async def a2a_jsonrpc(request: Request, user: CurrentUser, db: DbSession) -> Response:
        if not limiter.hit(f"user:{user.id}"):
            record(Event.RATE_LIMITED, request, user=user.id)
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=TOO_MANY)
        request.state.pld_user = user
        request.state.pld_learning = partial(load_learner_context, db, user.id)
        request.state.pld_budget = partial(budget.take, user.id)
        request.state.pld_usage = UsageLedger(db, user.id, limits)
        request.state.pld_request_id = str(uuid.uuid4())
        response = await jsonrpc(request)
        response.headers["X-Request-ID"] = request.state.pld_request_id
        return response

    return router


class FreeModeOut(BaseModel):
    available: bool = True
    provider: str
    simulated: bool  # respuestas preparadas con reglas, sin modelo de lenguaje


class AdvancedModeOut(BaseModel):
    available: bool
    provider: str | None = None
    simulated: bool = False  # modo de pruebas: «avanzada» sin IA real (A2A_ADVANCED_PROVIDER=mock)
    daily_limit: int | None = None
    used_today: int | None = None
    remaining: int | None = None
    global_available: bool | None = None  # si queda cuota común hoy (no cuánta)
    max_input_chars: int | None = None
    max_output_tokens: int | None = None


class TutorModesOut(BaseModel):
    default: Literal["free"] = "free"
    free: FreeModeOut
    advanced: AdvancedModeOut


def _modes_router(
    tutor: PythonTutorExecutor, limits: AdvancedLimits, settings: Settings
) -> APIRouter:
    """Qué modalidades ofrece el tutor y cuánta cuota avanzada le queda al alumno. Lo lee del
    executor: es el mismo que decide en cada mensaje, así que la web nunca ve otra cosa."""
    router = APIRouter(prefix="/tutor", tags=["Tutor híbrido"])

    @router.get("/modes", response_model=TutorModesOut, summary="Modalidades del tutor")
    def tutor_modes(user: CurrentUser, db: DbSession) -> TutorModesOut:
        model, advanced = tutor.agent.model, tutor.advanced
        free = FreeModeOut(provider=model.name, simulated=model.name == MockModelProvider.name)
        if advanced is None:
            return TutorModesOut(free=free, advanced=AdvancedModeOut(available=False))
        quota = UsageLedger(db, user.id, limits).quota()
        return TutorModesOut(
            free=free,
            advanced=AdvancedModeOut(
                available=True,
                provider=advanced.model.name,
                simulated=advanced.model.name == MockModelProvider.name,
                daily_limit=quota.limit,
                used_today=quota.used,
                remaining=quota.remaining,
                global_available=quota.global_available,
                max_input_chars=advanced.max_input_chars,
                max_output_tokens=settings.a2a_advanced_max_output_tokens,
            ),
        )

    return router
