"""Panel del alumno: resumen de su actividad guardada en la cuenta.

Reúne en una sola petición lo que el panel necesita y solo está en el servidor (lecciones
completadas con su fecha, intentos de ejercicios, documentos sincronizados y el método del último
inicio de sesión). El resto del progreso (conceptos, PCAP, cursos de DAW, logros) ya llega por
/course-state y /pcap-state y se calcula en el navegador con el contenido, como hasta ahora.

El usuario sale siempre de la sesión validada (CurrentUser): ninguna ruta acepta un id de usuario.
"""

from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Query
from sqlalchemy import Boolean, cast, func, literal, null, select, union_all
from sqlalchemy.orm import Session

from app.deps import CurrentUser, DbSession
from app.models import (
    AccountEvent,
    CourseState,
    ExerciseAttempt,
    Lesson,
    LessonProgress,
    Module,
    PcapState,
)
from app.schemas import (
    DailyActivity,
    DashboardOut,
    DashboardUser,
    ExercisesSummary,
    LearningEvent,
    LearningEventPage,
    LessonRef,
    LessonsSummary,
    ModuleProgress,
    SyncedState,
)

router = APIRouter(prefix="/dashboard", tags=["panel"])

DAILY_DAYS = 30  # días de la gráfica de evolución
SIGN_IN_KINDS = {"login": "password", "login_google": "google"}

# Desfase de la hora local respecto a UTC en minutos (España: 60 o 120). Límites reales del mundo.
UtcOffset = Annotated[int, Query(ge=-720, le=840)]


def _utc(moment: datetime) -> datetime:
    """SQLite devuelve fechas sin zona horaria; se guardan siempre en UTC."""
    return moment if moment.tzinfo else moment.replace(tzinfo=UTC)


def _sign_in_method(db: Session, user_id: int) -> str | None:
    kind = db.scalar(
        select(AccountEvent.kind)
        .where(AccountEvent.user_id == user_id, AccountEvent.kind.in_(SIGN_IN_KINDS))
        .order_by(AccountEvent.id.desc())
        .limit(1)
    )
    return SIGN_IN_KINDS.get(kind) if kind else None


def _lessons(db: Session, user_id: int) -> LessonsSummary:
    done = dict(
        db.execute(
            select(LessonProgress.lesson_id, LessonProgress.completed_at).where(
                LessonProgress.user_id == user_id
            )
        ).all()
    )
    # Módulos y lecciones en dos consultas, en el orden del curso
    modules = list(db.scalars(select(Module).order_by(Module.position)))
    lessons = list(db.scalars(select(Lesson).order_by(Lesson.module_id, Lesson.position)))
    by_module: dict[int, list[Lesson]] = {}
    for lesson in lessons:
        by_module.setdefault(lesson.module_id, []).append(lesson)
    ordered = [lesson for module in modules for lesson in by_module.get(module.id, [])]
    pending = next((lesson for lesson in ordered if lesson.id not in done), None)
    return LessonsSummary(
        total=len(ordered),
        completed=sum(1 for lesson in ordered if lesson.id in done),
        last_completed_at=max(done.values()) if done else None,
        next_lesson=LessonRef(slug=pending.slug, title=pending.title) if pending else None,
        modules=[
            ModuleProgress(
                slug=module.slug,
                title=module.title,
                total=len(by_module.get(module.id, [])),
                completed=sum(1 for lesson in by_module.get(module.id, []) if lesson.id in done),
            )
            for module in modules
        ],
    )


def _exercises(db: Session, user_id: int) -> ExercisesSummary:
    attempts, passed, tried, solved, last = db.execute(
        select(
            func.count(ExerciseAttempt.id),
            func.count(ExerciseAttempt.id).filter(ExerciseAttempt.passed.is_(True)),
            func.count(ExerciseAttempt.lesson_id.distinct()),
            func.count(ExerciseAttempt.lesson_id.distinct()).filter(
                ExerciseAttempt.passed.is_(True)
            ),
            func.max(ExerciseAttempt.created_at),
        ).where(ExerciseAttempt.user_id == user_id)
    ).one()
    return ExercisesSummary(
        attempts=attempts,
        passed=passed,
        lessons_tried=tried,
        lessons_passed=solved,
        last_attempt_at=last,
    )


def _daily(db: Session, user_id: int, now: datetime, offset: int) -> list[DailyActivity]:
    """Actividad por día (hora local del alumno) de los últimos DAILY_DAYS días."""
    shift = timedelta(minutes=offset)
    first_day = (now + shift).date() - timedelta(days=DAILY_DAYS - 1)
    since = datetime.combine(first_day, datetime.min.time(), tzinfo=UTC) - shift
    days: dict = {}

    def bucket(moment: datetime) -> dict:
        day = (_utc(moment) + shift).date()
        return days.setdefault(day, {"lessons_completed": 0, "attempts": 0, "passed": 0})

    for (moment,) in db.execute(
        select(LessonProgress.completed_at).where(
            LessonProgress.user_id == user_id, LessonProgress.completed_at >= since
        )
    ):
        bucket(moment)["lessons_completed"] += 1
    for moment, ok in db.execute(
        select(ExerciseAttempt.created_at, ExerciseAttempt.passed).where(
            ExerciseAttempt.user_id == user_id, ExerciseAttempt.created_at >= since
        )
    ):
        counts = bucket(moment)
        counts["attempts"] += 1
        counts["passed"] += int(ok)
    return [DailyActivity(day=day, **counts) for day, counts in sorted(days.items())]


def _synced(db: Session, user_id: int) -> list[SyncedState]:
    states = [
        SyncedState(key=course, updated_at=updated)
        for course, updated in db.execute(
            select(CourseState.course, CourseState.updated_at)
            .where(CourseState.user_id == user_id)
            .order_by(CourseState.course)
        )
    ]
    pcap = db.scalar(select(PcapState.updated_at).where(PcapState.user_id == user_id))
    if pcap is not None:
        states.insert(0, SyncedState(key="pcap", updated_at=pcap))
    return states


@router.get("", response_model=DashboardOut)
def get_dashboard(
    user: CurrentUser, db: DbSession, utc_offset_minutes: UtcOffset = 0
) -> DashboardOut:
    """Resumen del panel del alumno con sesión iniciada."""
    now = datetime.now(UTC)
    return DashboardOut(
        user=DashboardUser(
            display_name=user.display_name,
            email=user.email,
            created_at=user.created_at,
            sign_in_method=_sign_in_method(db, user.id),
        ),
        lessons=_lessons(db, user.id),
        exercises=_exercises(db, user.id),
        daily=_daily(db, user.id, now, utc_offset_minutes),
        synced=_synced(db, user.id),
        generated_at=now,
    )


@router.get("/activity", response_model=LearningEventPage)
def get_learning_activity(
    user: CurrentUser,
    db: DbSession,
    limit: Annotated[int, Query(ge=1, le=50)] = 20,
    offset: Annotated[int, Query(ge=0, le=10_000)] = 0,
) -> LearningEventPage:
    """Lecciones completadas e intentos, del más reciente al más antiguo."""
    completed = (
        select(
            literal("lesson_completed").label("kind"),
            Lesson.slug.label("slug"),
            Lesson.title.label("title"),
            cast(null(), Boolean).label("passed"),
            LessonProgress.completed_at.label("at"),
        )
        .join(Lesson, Lesson.id == LessonProgress.lesson_id)
        .where(LessonProgress.user_id == user.id)
    )
    attempts = (
        select(
            literal("attempt").label("kind"),
            Lesson.slug.label("slug"),
            Lesson.title.label("title"),
            ExerciseAttempt.passed.label("passed"),
            ExerciseAttempt.created_at.label("at"),
        )
        .join(Lesson, Lesson.id == ExerciseAttempt.lesson_id)
        .where(ExerciseAttempt.user_id == user.id)
    )
    feed = union_all(completed, attempts).subquery()
    rows = db.execute(
        select(feed).order_by(feed.c.at.desc(), feed.c.kind).limit(limit).offset(offset)
    )
    total = db.scalar(
        select(func.count()).select_from(LessonProgress).where(LessonProgress.user_id == user.id)
    ) + db.scalar(
        select(func.count()).select_from(ExerciseAttempt).where(ExerciseAttempt.user_id == user.id)
    )
    return LearningEventPage(
        items=[
            LearningEvent(
                kind=row.kind,
                lesson_slug=row.slug,
                lesson_title=row.title,
                passed=row.passed,
                at=row.at,
            )
            for row in rows
        ],
        total=total,
        limit=limit,
        offset=offset,
    )
