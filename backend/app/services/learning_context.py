"""Contexto educativo mínimo de un alumno, para los agentes (ADR-0034).

Minimización de datos (RGPD): solo lo que un tutor necesita para ayudar con una lección concreta.
Nada de email, nombre, historial, intentos anteriores ni otras lecciones. Además, el agente solo
envía al proveedor del modelo una parte (ver `PythonTutorAgent._prompt`): el progreso general
sirve para calcular el nivel, pero no sale del servidor. El usuario sale
siempre de la sesión, nunca del mensaje, así que un alumno no puede leer los datos de otro.
"""

from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Lesson, LessonProgress


@dataclass(frozen=True)
class LessonContext:
    slug: str
    title: str
    module_title: str
    exercise: str | None
    hint: str


@dataclass(frozen=True)
class LearnerContext:
    lessons_completed: int
    lessons_total: int
    lesson: LessonContext | None = None
    lesson_completed: bool = False


def load_learner_context(db: Session, user_id: int, lesson_slug: str | None) -> LearnerContext:
    """Progreso general y, si se indica una lección que existe, su estado para este usuario."""
    completed = db.scalar(
        select(func.count()).select_from(LessonProgress).where(LessonProgress.user_id == user_id)
    )
    total = db.scalar(select(func.count()).select_from(Lesson))
    lesson = db.scalar(select(Lesson).where(Lesson.slug == lesson_slug)) if lesson_slug else None
    if lesson is None:
        return LearnerContext(lessons_completed=completed, lessons_total=total)
    done = db.scalar(
        select(LessonProgress.id).where(
            LessonProgress.user_id == user_id, LessonProgress.lesson_id == lesson.id
        )
    )
    return LearnerContext(
        lessons_completed=completed,
        lessons_total=total,
        lesson=LessonContext(
            slug=lesson.slug,
            title=lesson.title,
            module_title=lesson.module.title,
            exercise=lesson.exercise,
            hint=(lesson.assistant or {}).get("hint", ""),
        ),
        lesson_completed=done is not None,
    )
