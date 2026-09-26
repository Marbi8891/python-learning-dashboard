"""Intentos de ejercicios del usuario."""

from fastapi import APIRouter, status
from sqlalchemy import select

from app.deps import CurrentUser, DbSession, get_lesson_or_404
from app.models import ExerciseAttempt
from app.routers.progress import mark_completed
from app.schemas import AttemptCreate, AttemptOut

router = APIRouter(prefix="/api/lessons/{slug}/attempts", tags=["ejercicios"])

HISTORY_LIMIT = 20


@router.post("", response_model=AttemptOut, status_code=status.HTTP_201_CREATED)
def create_attempt(
    slug: str, data: AttemptCreate, user: CurrentUser, db: DbSession
) -> ExerciseAttempt:
    """Registra un intento. Si ha superado los tests, la lección queda completada."""
    lesson = get_lesson_or_404(db, slug)
    attempt = ExerciseAttempt(
        user_id=user.id, lesson_id=lesson.id, code=data.code, passed=data.passed
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    if attempt.passed:
        mark_completed(db, user.id, lesson.id)
    return attempt


@router.get("", response_model=list[AttemptOut])
def list_attempts(slug: str, user: CurrentUser, db: DbSession) -> list[ExerciseAttempt]:
    lesson = get_lesson_or_404(db, slug)
    stmt = (
        select(ExerciseAttempt)
        .where(ExerciseAttempt.user_id == user.id, ExerciseAttempt.lesson_id == lesson.id)
        .order_by(ExerciseAttempt.id.desc())
        .limit(HISTORY_LIMIT)
    )
    return list(db.scalars(stmt))
