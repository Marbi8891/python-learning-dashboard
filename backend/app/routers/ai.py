"""IA de apoyo al alumno con NEXARO AI (docs/architecture/NEXARO_INTEGRATION_CONTRACT.md).

- El alumno sale siempre de la sesión (CurrentUser); el cuerpo no acepta usuario, modelo ni agente.
- El contexto lo pone el servidor a partir de la lección (app/ai_context.py).
- La respuesta es texto generado por IA: ninguna ruta de este router escribe progreso, intentos,
  XP ni resultados oficiales, diga lo que diga el modelo.
- Si NEXARO falla, el alumno ve un mensaje genérico; el detalle de NEXARO no llega al navegador.
"""

import logging
from collections.abc import Callable
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool

from app.ai_context import chat_messages, clip_answer, hint_messages
from app.config import get_settings
from app.deps import CurrentUser, DbSession, get_lesson_or_404
from app.models import User
from app.nexaro_client import NexaroBusy, NexaroClient, NexaroUnavailable
from app.rate_limit import ai_limiter
from app.schemas import AiAnswer, AiChatRequest, AiHintRequest, AiRequest
from app.security_events import Event, record

logger = logging.getLogger("pld.ai")
router = APIRouter(prefix="/ai", tags=["ia"])

MODES = ["chat", "hint"]
UNAVAILABLE = "La IA no está disponible"
NOT_RESPONDING = "El tutor no responde ahora mismo. Vuelve a probar en un momento."
BUSY = "El tutor está ocupado. Espera un poco y vuelve a preguntar."


class AiStatus(BaseModel):
    enabled: bool
    available: bool
    # Modos que ofrece este servidor
    modes: list[str]


def nexaro_client(request: Request) -> NexaroClient | None:
    """El cliente que crea el lifespan, o None si la IA está desactivada."""
    return getattr(request.app.state, "nexaro", None)


@router.get("/status", response_model=AiStatus)
async def ai_status(user: CurrentUser, request: Request) -> AiStatus:
    """¿Puede el alumno usar la IA ahora? Pide sesión para no servir de sonda anónima hacia
    NEXARO, y no revela su URL, su versión, el modelo ni los agentes."""
    client = nexaro_client(request)
    if client is None:
        return AiStatus(enabled=False, available=False, modes=[])
    return AiStatus(enabled=True, available=await client.available(), modes=MODES)


async def _answer(
    mode: str,
    data: AiRequest,
    build: Callable,
    user: User,
    db: DbSession,
    request: Request,
) -> AiAnswer:
    client = nexaro_client(request)
    if client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=UNAVAILABLE)
    if not ai_limiter.hit(str(user.id)):
        record(Event.AI_LIMITED, request, user=user.id)
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=BUSY)
    # La consulta a la base de datos es síncrona: fuera del bucle de eventos
    lesson = await run_in_threadpool(get_lesson_or_404, db, data.lesson_slug)
    request_id = str(uuid4())
    try:
        answer = await client.chat(get_settings().nexaro_agent_tutor, build(lesson, data))
    except NexaroBusy:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=BUSY) from None
    except NexaroUnavailable:
        logger.warning("ai %s request_id=%s: NEXARO no responde", mode, request_id)
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, detail=NOT_RESPONDING) from None
    # Solo metadatos: ni la pregunta, ni el código, ni la respuesta
    logger.info("ai %s request_id=%s: respondida", mode, request_id)
    return AiAnswer(answer=clip_answer(answer), mode=mode, request_id=request_id)


@router.post("/chat", response_model=AiAnswer)
async def ai_chat(
    data: AiChatRequest, user: CurrentUser, db: DbSession, request: Request
) -> AiAnswer:
    """Tutor sobre la lección: explica conceptos y no da la solución completa del ejercicio."""
    return await _answer("chat", data, chat_messages, user, db, request)


@router.post("/hint", response_model=AiAnswer)
async def ai_hint(
    data: AiHintRequest, user: CurrentUser, db: DbSession, request: Request
) -> AiAnswer:
    """Pista graduada (hint_level 1-3) del ejercicio de la lección, sin la solución."""
    return await _answer("hint", data, hint_messages, user, db, request)
