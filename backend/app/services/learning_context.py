"""Contexto educativo mínimo de un alumno, para los agentes (ADR-0034 y ADR-0036).

Minimización de datos (RGPD): solo lo que un tutor necesita para ayudar con una lección concreta.
Nada de email, nombre, el código de intentos anteriores ni el historial. Además, el agente solo
envía al proveedor del modelo una parte (ver `PythonTutorAgent._prompt`): las cuentas de evidencia
sirven para estimar el nivel, pero no salen del servidor. El usuario sale siempre de la sesión,
nunca del mensaje, así que un alumno no puede leer los datos de otro.

Evidencias (no se deduce dominio del % de lecciones completadas):
- Conceptos demostrados, con dificultades y errores típicos activos: de los ejercicios por
  conceptos que la web guarda en la cuenta (`course_states`, curso «learn»).
- Lecciones con el ejercicio superado: intentos con `passed` en `exercise_attempts`.
- De la lección elegida: si está completada y cuántos intentos lleva (sin su código).
"""

from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import CourseState, ExerciseAttempt, Lesson, LessonProgress
from app.services.curriculum import concept_evidence, get_curriculum

LEARN_COURSE = "learn"


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
    # Evidencias para el nivel y la adaptación (ver el docstring del módulo)
    mastered_concepts: tuple[str, ...] = ()
    struggling_concepts: tuple[str, ...] = ()
    active_errors: tuple[str, ...] = ()
    lessons_passed: int = 0
    lesson_attempts: int = 0
    lesson_failed_attempts: int = 0


def load_learner_context(db: Session, user_id: int, lesson_slug: str | None) -> LearnerContext:
    """Progreso, evidencias y, si se indica una lección que existe, su estado para este usuario."""
    completed = db.scalar(
        select(func.count()).select_from(LessonProgress).where(LessonProgress.user_id == user_id)
    )
    total = db.scalar(select(func.count()).select_from(Lesson))
    passed = db.scalar(
        select(func.count(func.distinct(ExerciseAttempt.lesson_id))).where(
            ExerciseAttempt.user_id == user_id, ExerciseAttempt.passed.is_(True)
        )
    )
    learn = db.get(CourseState, (user_id, LEARN_COURSE))
    evidence = concept_evidence(get_curriculum(), learn.data if learn else None)
    common = {
        "lessons_completed": completed,
        "lessons_total": total,
        "mastered_concepts": evidence.mastered,
        "struggling_concepts": evidence.struggling,
        "active_errors": evidence.active_errors,
        "lessons_passed": passed or 0,
    }
    lesson = db.scalar(select(Lesson).where(Lesson.slug == lesson_slug)) if lesson_slug else None
    if lesson is None:
        return LearnerContext(**common)
    done = db.scalar(
        select(LessonProgress.id).where(
            LessonProgress.user_id == user_id, LessonProgress.lesson_id == lesson.id
        )
    )
    attempts = db.execute(
        select(ExerciseAttempt.passed, func.count())
        .where(ExerciseAttempt.user_id == user_id, ExerciseAttempt.lesson_id == lesson.id)
        .group_by(ExerciseAttempt.passed)
    ).all()
    by_result = {bool(result): count for result, count in attempts}
    return LearnerContext(
        **common,
        lesson=LessonContext(
            slug=lesson.slug,
            title=lesson.title,
            module_title=lesson.module.title,
            exercise=lesson.exercise,
            hint=(lesson.assistant or {}).get("hint", ""),
        ),
        lesson_completed=done is not None,
        lesson_attempts=sum(by_result.values()),
        lesson_failed_attempts=by_result.get(False, 0),
    )
