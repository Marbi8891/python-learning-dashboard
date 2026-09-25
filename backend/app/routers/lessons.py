"""Endpoints de módulos y lecciones."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.database import get_db
from app.models import Lesson, Module
from app.schemas import LessonDetail, ModuleOut

router = APIRouter(prefix="/api", tags=["lecciones"])


@router.get("/modules", response_model=list[ModuleOut])
def list_modules(db: Session = Depends(get_db)) -> list[Module]:
    # selectinload: 2 consultas en total (módulos + lecciones), no una por módulo (N+1)
    stmt = select(Module).options(selectinload(Module.lessons)).order_by(Module.position)
    return list(db.scalars(stmt))


@router.get("/lessons/{slug}", response_model=LessonDetail)
def get_lesson(slug: str, db: Session = Depends(get_db)) -> LessonDetail:
    stmt = select(Lesson).options(joinedload(Lesson.module)).where(Lesson.slug == slug)
    lesson = db.scalar(stmt)
    if lesson is None:
        raise HTTPException(status_code=404, detail="Lección no encontrada")

    return LessonDetail(
        slug=lesson.slug,
        title=lesson.title,
        position=lesson.position,
        module_slug=lesson.module.slug,
        module_title=lesson.module.title,
        theory=lesson.theory,
        example_code=lesson.example_code,
        exercise=lesson.exercise,
    )
