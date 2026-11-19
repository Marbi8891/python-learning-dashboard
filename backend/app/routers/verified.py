"""Hitos verificados: simulacros del PCAP que elige, cronometra y corrige el servidor (#109).

Cada ruta usa el usuario de la sesión: nadie puede empezar, entregar ni consultar los simulacros
de otra cuenta (el de otro usuario responde 404, igual que uno que no existe).
"""

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import func, select, update

from app import verified_exams as exams
from app.config import get_settings
from app.deps import CurrentUser, DbSession, WritingUser
from app.models import VerifiedExam
from app.schemas import (
    VerifiedExamAnswers,
    VerifiedExamOut,
    VerifiedExamStart,
    VerifiedSummary,
)

router = APIRouter(prefix="/verified", tags=["hitos verificados"])

HISTORY = 10


def _result(exam: VerifiedExam) -> VerifiedExamOut:
    return VerifiedExamOut(
        id=exam.id,
        exam_code=exam.exam_code,
        status=exam.status,
        started_at=exams.utc(exam.started_at),
        finished_at=exams.utc(exam.finished_at) if exam.finished_at else None,
        correct=exam.correct,
        total=len(exam.question_ids),
        score=exam.score,
        passed=exam.score is not None and exam.score >= exams.pass_mark(),
    )


def _own_exam(db: DbSession, user_id: int, exam_id: int) -> VerifiedExam:
    exam = db.get(VerifiedExam, exam_id)
    if exam is None or exam.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Simulacro no encontrado")
    return exam


@router.post("/pcap-exams", response_model=VerifiedExamStart, status_code=201)
def start_exam(user: WritingUser, db: DbSession) -> VerifiedExamStart:
    """Empieza un simulacro: el servidor elige las preguntas y apunta la hora. Uno en curso sin
    entregar queda abandonado (no cuenta). Como mucho unos pocos al día por cuenta."""
    now = datetime.now(UTC)
    started_today = db.scalar(
        select(func.count())
        .select_from(VerifiedExam)
        .where(VerifiedExam.user_id == user.id, VerifiedExam.started_at > now - timedelta(days=1))
    )
    if started_today >= get_settings().verified_exams_per_day:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Ya has empezado varios simulacros verificados hoy. Vuelve mañana o practica "
            "con el simulacro local.",
        )
    db.execute(
        update(VerifiedExam)
        .where(VerifiedExam.user_id == user.id, VerifiedExam.status == "open")
        .values(status="abandoned", finished_at=now)
    )
    exam = VerifiedExam(
        user_id=user.id,
        exam_code=exams.bank()["exam"]["code"],
        question_ids=exams.pick_questions(),
        started_at=now,
    )
    db.add(exam)
    db.commit()
    return VerifiedExamStart(
        id=exam.id,
        exam_code=exam.exam_code,
        question_ids=exam.question_ids,
        started_at=now,
        deadline=exams.deadline(now),
    )


@router.post("/pcap-exams/{exam_id}/answers", response_model=VerifiedExamOut)
def submit_answers(
    exam_id: int, data: VerifiedExamAnswers, user: WritingUser, db: DbSession
) -> VerifiedExamOut:
    """Entrega y corrige. Repetir la misma entrega devuelve la misma nota sin volver a corregir;
    otra entrega distinta de un simulacro ya corregido, o fuera de tiempo, se rechaza (409)."""
    exam = _own_exam(db, user.id, exam_id)
    if exam.status == "finished":
        if exam.answers == data.answers:
            return _result(exam)
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Este simulacro ya está entregado.")
    if exam.status != "open":
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Este simulacro ya no está en curso.")
    if errors := exams.answer_errors(exam.question_ids, data.answers):
        raise HTTPException(422, detail=errors[:10])
    now = datetime.now(UTC)
    if exams.expired(exam.started_at, now):
        db.execute(
            update(VerifiedExam)
            .where(VerifiedExam.id == exam.id, VerifiedExam.status == "open")
            .values(status="expired", finished_at=now)
        )
        db.commit()
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Se acabó el tiempo del simulacro.")
    correct, score = exams.grade(exam.question_ids, data.answers)
    # Solo la primera entrega pasa de «open» a «finished»: dos a la vez no corrigen dos veces
    changed = db.execute(
        update(VerifiedExam)
        .where(VerifiedExam.id == exam.id, VerifiedExam.status == "open")
        .values(
            status="finished",
            answers=data.answers,
            correct=correct,
            score=score,
            finished_at=now,
        )
    ).rowcount
    db.commit()
    db.refresh(exam)
    if not changed and exam.answers != data.answers:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Este simulacro ya está entregado.")
    return _result(exam)


@router.get("", response_model=VerifiedSummary)
def my_verified(user: CurrentUser, db: DbSession) -> VerifiedSummary:
    """Los simulacros corregidos por el servidor y si hay alguno aprobado."""
    finished = list(
        db.scalars(
            select(VerifiedExam)
            .where(VerifiedExam.user_id == user.id, VerifiedExam.status == "finished")
            .order_by(VerifiedExam.id.desc())
        )
    )
    best = max((exam.score for exam in finished), default=None)
    return VerifiedSummary(
        pass_mark=exams.pass_mark(),
        best_score=best,
        passed=best is not None and best >= exams.pass_mark(),
        exams=[_result(exam) for exam in finished[:HISTORY]],
    )
