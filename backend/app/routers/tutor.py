"""Tutor de programación: reenvía la pregunta a NEXARO Personal AI en modo tutor (docs/TUTOR.md).

La clave de API de NEXARO solo vive aquí, en el backend; el navegador nunca la ve. El ejercicio se
lee de la base de datos (no lo manda el cliente) y la conversación de NEXARO viaja firmada para el
usuario que la empezó: todas las conversaciones son de la misma clave, así que sin la firma un
alumno podría continuar la de otro y el modelo recibiría su historial.
"""

import hashlib
import hmac

import httpx
from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, Field

from app.config import get_settings
from app.deps import CurrentUser, DbSession, get_lesson_or_404
from app.rate_limit import tutor_limiter
from app.security import get_jwt_secret
from app.security_events import Event, record

router = APIRouter(prefix="/tutor", tags=["tutor"])

UNAVAILABLE = "El tutor no está disponible"
NOT_RESPONDING = "El tutor no responde ahora mismo. Vuelve a probar en un momento."
BUSY = "El tutor está ocupado. Espera un poco y vuelve a preguntar."
# Delimitadores del contexto: el código del alumno no puede cerrarlos ni abrir otros
_TAGS = ("ejercicio", "codigo_del_alumno")


class TutorQuestion(BaseModel):
    lesson: str = Field(min_length=1, max_length=50)
    question: str = Field(min_length=1, max_length=2000)
    # NEXARO admite 12.000 caracteres por mensaje: código + pregunta + enunciado caben
    code: str = Field(default="", max_length=8000)
    conversation: str | None = Field(default=None, max_length=200)


class TutorAnswer(BaseModel):
    answer: str
    conversation: str


class TutorStatus(BaseModel):
    available: bool


# La comprobación de estado no espera al modelo: solo pregunta a NEXARO si Ollama y el modelo están
# listos (`/api/health`, público y con caché en NEXARO), así que basta un tiempo de espera corto.
STATUS_TIMEOUT_SECONDS = 5.0


def tutor_enabled() -> bool:
    """Las dos variables con valor (en docker-compose llegan vacías si no se definen)."""
    settings = get_settings()
    key = settings.nexaro_api_key
    return bool(settings.nexaro_url and key and key.get_secret_value())


def _signature(user_id: int, conversation_id: str) -> str:
    message = f"tutor:{user_id}:{conversation_id}".encode()
    return hmac.new(get_jwt_secret().encode(), message, hashlib.sha256).hexdigest()


def seal(user_id: int, conversation_id: str) -> str:
    return f"{conversation_id}.{_signature(user_id, conversation_id)}"


def unseal(user_id: int, token: str | None) -> str | None:
    """Id de la conversación si la firma es de este usuario; si no, None (empieza otra)."""
    conversation_id, _, signature = (token or "").rpartition(".")
    if conversation_id and hmac.compare_digest(signature, _signature(user_id, conversation_id)):
        return conversation_id
    return None


def _defang(text: str) -> str:
    for tag in _TAGS:
        text = text.replace(f"<{tag}", f"< {tag}").replace(f"</{tag}", f"</ {tag}")
    return text


def build_message(title: str, exercise: str | None, code: str, question: str) -> str:
    parts = [f"Lección: {title}"]
    if exercise:
        parts.append(f"<ejercicio>\n{_defang(exercise)}\n</ejercicio>")
    if code.strip():
        parts.append(f"<codigo_del_alumno>\n{_defang(code)}\n</codigo_del_alumno>")
    parts.append(f"Pregunta del alumno: {question}")
    return "\n\n".join(parts)


@router.get("/status", response_model=TutorStatus)
def tutor_status(user: CurrentUser) -> TutorStatus:
    """¿Responde NEXARO ahora mismo? Sirve para que la web muestre «conectado» o «no disponible»
    antes de preguntar. No usa la clave de API ni reenvía nada del alumno; pide sesión para que no
    sirva de sonda anónima hacia el equipo del autor."""
    settings = get_settings()
    if not tutor_enabled():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=UNAVAILABLE)
    assert settings.nexaro_url  # garantizado por tutor_enabled()
    try:
        response = httpx.get(
            settings.nexaro_url.rstrip("/") + "/api/health", timeout=STATUS_TIMEOUT_SECONDS
        )
    except httpx.HTTPError:
        return TutorStatus(available=False)
    return TutorStatus(available=response.status_code == status.HTTP_200_OK)


@router.post("", response_model=TutorAnswer)
def ask(data: TutorQuestion, user: CurrentUser, db: DbSession, request: Request) -> TutorAnswer:
    """Síncrono a propósito, como el resto de la API: mientras el modelo piensa, la petición ocupa
    un hilo del servidor y no el bucle de eventos. El límite por usuario acota cuántos a la vez."""
    settings = get_settings()
    if not tutor_enabled():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=UNAVAILABLE)
    if not tutor_limiter.hit(str(user.id)):
        record(Event.TUTOR_LIMITED, request, user=user.id)
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=BUSY)
    lesson = get_lesson_or_404(db, data.lesson)
    payload = {
        "message": build_message(lesson.title, lesson.exercise, data.code, data.question),
        "conversation_id": unseal(user.id, data.conversation),
        "mode": "tutor",
    }
    assert settings.nexaro_url and settings.nexaro_api_key  # garantizado por tutor_enabled()
    try:
        response = httpx.post(
            settings.nexaro_url.rstrip("/") + "/api/v1/chat",
            json=payload,
            headers={"Authorization": f"Bearer {settings.nexaro_api_key.get_secret_value()}"},
            timeout=settings.tutor_timeout_seconds,
        )
    except httpx.HTTPError:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, detail=NOT_RESPONDING) from None
    if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=BUSY)
    if response.status_code != status.HTTP_200_OK:
        # 401 (clave revocada), 404 (conversación borrada en NEXARO), 5xx...: el detalle de NEXARO
        # no se reenvía al navegador
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, detail=NOT_RESPONDING)
    body = response.json()
    return TutorAnswer(answer=body["answer"], conversation=seal(user.id, body["conversation_id"]))
