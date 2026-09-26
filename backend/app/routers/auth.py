"""Registro, login y usuario actual."""

from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError

from app.config import get_settings
from app.deps import DbSession
from app.mailer import send_email
from app.models import PasswordResetToken, User
from app.rate_limit import limit_auth_attempts
from app.schemas import PasswordResetConfirm, PasswordResetRequest, Token, UserCreate, UserOut
from app.security import (
    create_access_token,
    hash_password,
    hash_reset_token,
    new_reset_token,
    verify_password,
)

router = APIRouter(prefix="/api", tags=["usuarios"])


@router.post(
    "/auth/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(limit_auth_attempts)],
)
def register(data: UserCreate, db: DbSession) -> User:
    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        display_name=data.display_name.strip(),
        privacy_accepted_at=datetime.now(UTC),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:  # email único: la base de datos garantiza que no haya duplicados
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Ese email ya está registrado"
        ) from None
    db.refresh(user)
    return user


@router.post("/auth/login", response_model=Token, dependencies=[Depends(limit_auth_attempts)])
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], db: DbSession) -> Token:
    """Login con formulario OAuth2: el campo `username` es el email."""
    user = db.scalar(select(User).where(User.email == form.username.strip().lower()))
    if not verify_password(form.password, user.password_hash if user else None):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(access_token=create_access_token(user.id, user.token_version))


RESET_ACCEPTED = {
    "detail": "Si el email está registrado, recibirás un enlace para cambiar la contraseña."
}


@router.post(
    "/auth/password-reset/request",
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(limit_auth_attempts)],
)
def request_password_reset(
    data: PasswordResetRequest, background: BackgroundTasks, db: DbSession
) -> dict[str, str]:
    """Responde siempre igual, exista o no el email (no revela qué cuentas hay)."""
    user = db.scalar(select(User).where(User.email == data.email))
    if user is not None:
        settings = get_settings()
        db.execute(delete(PasswordResetToken).where(PasswordResetToken.user_id == user.id))
        token, token_hash = new_reset_token()
        expires = datetime.now(UTC) + timedelta(minutes=settings.password_reset_minutes)
        db.add(PasswordResetToken(user_id=user.id, token_hash=token_hash, expires_at=expires))
        db.commit()
        link = f"{settings.frontend_url.rstrip('/')}/#/restablecer?token={token}"
        body = (
            f"Hola, {user.display_name}:\n\n"
            f"Para elegir una contraseña nueva, abre este enlace (caduca en "
            f"{settings.password_reset_minutes} minutos):\n\n{link}\n\n"
            "Si no lo has pedido tú, ignora este mensaje: tu contraseña no cambiará."
        )
        # En segundo plano: la respuesta no tarda más si el email existe
        background.add_task(send_email, user.email, "Restablecer tu contraseña", body)
    return RESET_ACCEPTED


@router.post(
    "/auth/password-reset/confirm",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(limit_auth_attempts)],
)
def confirm_password_reset(data: PasswordResetConfirm, db: DbSession) -> Response:
    reset = db.scalar(
        select(PasswordResetToken).where(
            PasswordResetToken.token_hash == hash_reset_token(data.token)
        )
    )
    now = datetime.now(UTC)
    if reset is None or reset.used_at is not None or _as_utc(reset.expires_at) < now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El enlace no es válido o ha caducado. Pide uno nuevo.",
        )
    user = db.get(User, reset.user_id)
    user.password_hash = hash_password(data.new_password)
    user.token_version += 1  # cierra todas las sesiones abiertas
    reset.used_at = now
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def _as_utc(moment: datetime) -> datetime:
    """SQLite devuelve fechas sin zona horaria; las guardamos siempre en UTC."""
    return moment if moment.tzinfo else moment.replace(tzinfo=UTC)
