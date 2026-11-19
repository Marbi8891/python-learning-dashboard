"""Tutor con IA para las dudas del alumno (ver app/tutor.py)."""

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app import tutor
from app.config import get_settings
from app.deps import CurrentUser, DbSession
from app.models import Lesson
from app.rate_limit import RateLimiter
from app.schemas import TutorAnswer, TutorQuestion

router = APIRouter(prefix="/tutor", tags=["tutor"])

# Por alumno: la capa gratuita del proveedor tiene un cupo que comparten todos
question_limiter = RateLimiter(get_settings().tutor_questions_per_hour, 60 * 60)

DISABLED = "El tutor con IA no está disponible ahora mismo. Usa las preguntas sugeridas."
TOO_MANY_QUESTIONS = "Has hecho muchas preguntas seguidas. Descansa un poco y vuelve en un rato."
PROVIDER_FAILED = "El tutor no ha podido contestar. Inténtalo de nuevo en unos segundos."


@router.post("/ask", response_model=TutorAnswer)
def ask_tutor(data: TutorQuestion, user: CurrentUser, db: DbSession) -> TutorAnswer:
    """Responde a una duda del alumno. Hace falta cuenta: así se puede limitar por persona."""
    if not tutor.tutor_enabled():
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=DISABLED)
    if not question_limiter.hit(str(user.id)):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=TOO_MANY_QUESTIONS
        )
    lesson = None
    if data.lesson_slug:
        lesson = db.scalar(select(Lesson).where(Lesson.slug == data.lesson_slug))
    try:
        answer = tutor.ask(data, lesson)
    except tutor.TutorUnavailable:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=PROVIDER_FAILED
        ) from None
    return TutorAnswer(answer=answer)
