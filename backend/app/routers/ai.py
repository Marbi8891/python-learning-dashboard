"""IA de apoyo al alumno con NEXARO AI (docs/architecture/NEXARO_INTEGRATION_CONTRACT.md).

Fase 1: solo el estado. Las rutas de generación (chat, pista, errores, revisión) llegan en las
fases siguientes. Nada de este router escribe progreso, intentos ni resultados oficiales.
"""

from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.deps import CurrentUser
from app.nexaro_client import NexaroClient

router = APIRouter(prefix="/ai", tags=["ia"])


class AiStatus(BaseModel):
    enabled: bool
    available: bool
    # Modos que ofrece este servidor; vacío hasta la Fase 2
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
    return AiStatus(enabled=True, available=await client.available(), modes=[])
