"""Progreso del usuario: lecciones completadas."""

from fastapi import APIRouter, Response, status
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.deps import CurrentUser, DbSession, get_lesson_or_404
from app.models import Lesson, LessonProgress
from app.schemas import ProgressImport, ProgressItem

router = APIRouter(prefix="/api/progress", tags=["progreso"])


def list_progress(db: Session, user_id: int) -> list[ProgressItem]:
    # Una sola consulta con JOIN para obtener el slug de cada lección (sin N+1)
    rows = db.execute(
        select(Lesson.slug, LessonProgress.completed_at)
        .join(Lesson, Lesson.id == LessonProgress.lesson_id)
        .where(LessonProgress.user_id == user_id)
        .order_by(LessonProgress.completed_at)
    )
    return [ProgressItem(lesson_slug=slug, completed_at=done) for slug, done in rows]


def mark_completed(db: Session, user_id: int, lesson_id: int) -> LessonProgress:
    """Idempotente: si ya estaba completada, devuelve el registro existente."""
    stmt = select(LessonProgress).where(
        LessonProgress.user_id == user_id, LessonProgress.lesson_id == lesson_id
    )
    progress = db.scalar(stmt)
    if progress is None:
        db.add(LessonProgress(user_id=user_id, lesson_id=lesson_id))
        try:
            db.commit()
        except IntegrityError:  # otra petición simultánea la creó antes
            db.rollback()
        progress = db.scalar(stmt)
    return progress


@router.get("", response_model=list[ProgressItem])
def get_progress(user: CurrentUser, db: DbSession) -> list[ProgressItem]:
    return list_progress(db, user.id)


@router.put("/{slug}", response_model=ProgressItem)
def complete_lesson(slug: str, user: CurrentUser, db: DbSession) -> ProgressItem:
    lesson = get_lesson_or_404(db, slug)
    progress = mark_completed(db, user.id, lesson.id)
    return ProgressItem(lesson_slug=lesson.slug, completed_at=progress.completed_at)


@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
def uncomplete_lesson(slug: str, user: CurrentUser, db: DbSession) -> Response:
    lesson = get_lesson_or_404(db, slug)
    db.execute(
        delete(LessonProgress).where(
            LessonProgress.user_id == user.id, LessonProgress.lesson_id == lesson.id
        )
    )
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/import", response_model=list[ProgressItem])
def import_progress(data: ProgressImport, user: CurrentUser, db: DbSession) -> list[ProgressItem]:
    """Fusiona el progreso del navegador con el de la cuenta. Ignora slugs desconocidos."""
    slugs = set(data.lesson_slugs)
    lesson_ids = set(db.scalars(select(Lesson.id).where(Lesson.slug.in_(slugs))))
    done_ids = set(
        db.scalars(select(LessonProgress.lesson_id).where(LessonProgress.user_id == user.id))
    )
    db.add_all(
        LessonProgress(user_id=user.id, lesson_id=lesson_id) for lesson_id in lesson_ids - done_ids
    )
    db.commit()
    return list_progress(db, user.id)
