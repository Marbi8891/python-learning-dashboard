"""Cuenta del usuario: datos, exportación y borrado (RGPD)."""

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import delete, select

from app import activity
from app.deps import CurrentUser, DbSession
from app.models import (
    AccountEvent,
    CourseState,
    ExerciseAttempt,
    Lesson,
    LessonProgress,
    PasswordResetToken,
    PcapState,
    User,
)
from app.password_policy import weakness
from app.rate_limit import limit_auth_attempts
from app.routers import auth
from app.routers.progress import list_progress
from app.schemas import (
    ActivityOut,
    DeleteConfirm,
    PasswordChange,
    ProfileUpdate,
    Token,
    UserExport,
    UserOut,
)
from app.security import hash_password, verify_password
from app.security_events import Event, record
from app.session_cookie import issue_session

router = APIRouter(prefix="/users/me", tags=["cuenta"])


@router.get("", response_model=UserOut)
def read_me(user: CurrentUser) -> User:
    return user


@router.patch("", response_model=UserOut)
def update_me(data: ProfileUpdate, user: CurrentUser, request: Request, db: DbSession) -> User:
    """Cambiar el nombre que se muestra."""
    name = data.display_name.strip()
    if not name:
        raise HTTPException(status_code=422, detail="El nombre no puede estar vacío.")
    if name != user.display_name:
        user.display_name = name
        activity.log(db, user.id, "name_changed", request)
        db.commit()
    return user


@router.post("/password", response_model=Token, dependencies=[Depends(limit_auth_attempts)])
def change_password(
    data: PasswordChange, user: CurrentUser, request: Request, response: Response, db: DbSession
) -> Token:
    """Cambiar la contraseña sabiendo la actual. Cierra las demás sesiones y devuelve un token
    nuevo para seguir en esta."""
    if not verify_password(data.current_password, user.password_hash):
        record(Event.LOGIN_FAILED, request, user=user.id, action="password")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Contraseña actual incorrecta"
        )
    problem = weakness(data.new_password, user.email, user.display_name)
    if problem:
        raise HTTPException(status_code=422, detail=problem)
    user.password_hash = hash_password(data.new_password)
    user.token_version += 1  # los tokens de los demás dispositivos dejan de valer
    activity.log(db, user.id, "password_changed", request)
    db.commit()
    record(Event.PASSWORD_CHANGED, request, user=user.id)
    return issue_session(request, response, user.id, user.token_version)


@router.get("/activity", response_model=list[ActivityOut])
def my_activity(user: CurrentUser, db: DbSession) -> list[AccountEvent]:
    """Últimos inicios de sesión, intentos fallidos y cambios de la cuenta, para detectar accesos
    que no reconozcas."""
    return activity.recent(db, user.id)


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
        email_verified_at=user.email_verified_at,
        progress=list_progress(db, user.id),
        attempts=[
            {"lesson_slug": slug, "code": code, "passed": passed, "created_at": created}
            for slug, code, passed, created in attempts
        ],
        pcap=state.data if (state := db.get(PcapState, user.id)) else None,
        courses={
            c.course: c.data
            for c in db.scalars(select(CourseState).where(CourseState.user_id == user.id))
        },
        activity=[ActivityOut.model_validate(e) for e in activity.recent(db, user.id)],
        exported_at=datetime.now(UTC),
    )


# Un ID token de Google vale una hora; para borrar se exige uno recién emitido.
GOOGLE_CONFIRMATION_MAX_AGE = timedelta(minutes=10)


def _confirm_with_google(credential: str, user: User, request: Request) -> None:
    """La credencial debe ser de Google, reciente y del mismo email que la cuenta."""
    client_id = auth.get_settings().google_client_id
    if not client_id:
        raise HTTPException(
            status_code=503, detail="El inicio de sesión con Google no está configurado."
        )
    claims = auth.verify_google_credential(credential, client_id)
    issued_at = datetime.fromtimestamp(int(claims.get("iat", 0)), UTC)
    same_account = str(claims["email"]).strip().lower() == user.email
    if not same_account or datetime.now(UTC) - issued_at > GOOGLE_CONFIRMATION_MAX_AGE:
        record(Event.LOGIN_FAILED, request, user=user.id, action="delete")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Confirma con la misma cuenta de Google con la que entras.",
        )


@router.post(
    "/delete",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(limit_auth_attempts)],
)
def delete_my_account(
    data: DeleteConfirm, user: CurrentUser, request: Request, db: DbSession
) -> Response:
    """Borra la cuenta y todos sus datos. Pide la contraseña, o volver a entrar con Google en las
    cuentas creadas con Google (su contraseña es aleatoria y nadie la conoce), para evitar borrados
    accidentales o desde una sesión robada (T1539 → T1485)."""
    if data.google_credential is not None:
        _confirm_with_google(data.google_credential, user, request)
    elif not verify_password(data.password, user.password_hash):
        record(Event.LOGIN_FAILED, request, user=user.id, action="delete")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Contraseña incorrecta")
    # Borrado explícito: no depende de que la base de datos aplique ON DELETE CASCADE
    # (SQLite no lo hace si no se activa PRAGMA foreign_keys).
    for model in (
        ExerciseAttempt,
        LessonProgress,
        PasswordResetToken,
        PcapState,
        CourseState,
        AccountEvent,
    ):
        db.execute(delete(model).where(model.user_id == user.id))
    user_id = user.id
    db.delete(user)
    db.commit()
    record(Event.ACCOUNT_DELETED, request, user=user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
