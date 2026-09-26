"""Cuenta del usuario: datos, exportación y borrado (RGPD)."""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import delete, select

from app.deps import CurrentUser, DbSession
from app.models import ExerciseAttempt, Lesson, LessonProgress, PasswordResetToken, User
from app.rate_limit import limit_auth_attempts
from app.routers.progress import list_progress
from app.schemas import PasswordConfirm, UserExport, UserOut
from app.security import verify_password

router = APIRouter(prefix="/api/users/me", tags=["cuenta"])


@router.get("", response_model=UserOut)
def read_me(user: CurrentUser) -> User:
    return user


@router.get("/export", response_model=UserExport)
def export_my_data(user: CurrentUser, db: DbSession) -> UserExport:
    """Todos los datos del usuario en JSON (derecho de acceso y portabilidad)."""
    attempts = db.execute(
        select(
            Lesson.slug, ExerciseAttempt.code, ExerciseAttempt.passed, ExerciseAttempt.created_at
        )
        .join(Lesson, Lesson.id == ExerciseAttempt.lesson_id)
        .where(ExerciseAttempt.user_id == user.id)
        .order_by(ExerciseAttempt.id)
    )
    return UserExport(
        user=UserOut.model_validate(user),
        privacy_accepted_at=user.privacy_accepted_at,
        progress=list_progress(db, user.id),
        attempts=[
            {"lesson_slug": slug, "code": code, "passed": passed, "created_at": created}
            for slug, code, passed, created in attempts
        ],
        exported_at=datetime.now(UTC),
    )


@router.post(
    "/delete",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(limit_auth_attempts)],
)
def delete_my_account(data: PasswordConfirm, user: CurrentUser, db: DbSession) -> Response:
    """Borra la cuenta y todos sus datos. Pide la contraseña para evitar borrados accidentales."""
    if not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Contraseña incorrecta")
    # Borrado explícito: no depende de que la base de datos aplique ON DELETE CASCADE
    # (SQLite no lo hace si no se activa PRAGMA foreign_keys).
    for model in (ExerciseAttempt, LessonProgress, PasswordResetToken):
        db.execute(delete(model).where(model.user_id == user.id))
    db.delete(user)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
