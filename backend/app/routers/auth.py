"""Registro, login y usuario actual."""

from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError

from app import activity
from app.config import get_settings
from app.deps import CurrentUser, DbSession
from app.mailer import send_email
from app.models import PasswordResetToken, User
from app.password_policy import weakness
from app.rate_limit import TOO_MANY, limit_auth_attempts, login_failures, reset_requests
from app.schemas import PasswordResetConfirm, PasswordResetRequest, Token, UserCreate, UserOut
from app.security import (
    create_access_token,
    hash_password,
    hash_reset_token,
    needs_rehash,
    new_reset_token,
    verify_password,
)
from app.security_events import Event, pseudonym, record

router = APIRouter(prefix="/api", tags=["usuarios"])


@router.post(
    "/auth/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(limit_auth_attempts)],
)
def register(data: UserCreate, db: DbSession) -> User:
    _reject_weak(data.password, data.email, data.display_name)
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
def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()], request: Request, db: DbSession
) -> Token:
    """Login con formulario OAuth2: el campo `username` es el email.

    Además del límite por IP, una cuenta con demasiados fallos seguidos se bloquea un rato,
    aunque los intentos lleguen de muchas IPs distintas (ADR-0022)."""
    email = form.username.strip().lower()
    account = pseudonym(email)
    if login_failures.blocked(email):
        record(Event.ACCOUNT_LOCKED, request, account=account)
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=TOO_MANY)
    user = db.scalar(select(User).where(User.email == email))
    if not verify_password(form.password, user.password_hash if user else None):
        login_failures.record(email)
        record(Event.LOGIN_FAILED, request, account=account, known=user is not None)
        if user is not None:  # el titular lo verá en «Actividad de la cuenta» (ADR-0025)
            activity.log(db, user.id, "login_failed", request)
            db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    login_failures.clear(email)
    if needs_rehash(user.password_hash):  # hashes creados con parámetros anteriores
        user.password_hash = hash_password(form.password)
    activity.log(db, user.id, "login", request)
    db.commit()
    record(Event.LOGIN_OK, request, user=user.id)
    return Token(access_token=create_access_token(user.id, user.token_version))


@router.post("/auth/logout-all", status_code=status.HTTP_204_NO_CONTENT)
def logout_everywhere(user: CurrentUser, request: Request, db: DbSession) -> Response:
    """Cierra la sesión en todos los dispositivos: los tokens emitidos dejan de valer."""
    user.token_version += 1
    activity.log(db, user.id, "logout_all", request)
    db.commit()
    record(Event.LOGOUT_ALL, request, user=user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


RESET_ACCEPTED = {
    "detail": "Si el email está registrado, recibirás un enlace para cambiar la contraseña."
}


@router.post(
    "/auth/password-reset/request",
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(limit_auth_attempts)],
)
def request_password_reset(
    data: PasswordResetRequest, background: BackgroundTasks, request: Request, db: DbSession
) -> dict[str, str]:
    """Responde siempre igual, exista o no el email (no revela qué cuentas hay)."""
    user = db.scalar(select(User).where(User.email == data.email))
    record(Event.RESET_REQUESTED, request, account=pseudonym(data.email), known=user is not None)
    # Como mucho unos pocos emails por cuenta y cuarto de hora; la respuesta no cambia
    if user is not None and reset_requests.hit(data.email):
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
def confirm_password_reset(data: PasswordResetConfirm, request: Request, db: DbSession) -> Response:
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
    # Antes de gastar el enlace: si la contraseña no vale, se puede probar con otra
    _reject_weak(data.new_password, user.email, user.display_name)
    # Un solo uso incluso con dos peticiones a la vez: solo gana la que marca el enlace como usado
    claimed = db.execute(
        update(PasswordResetToken)
        .where(PasswordResetToken.id == reset.id, PasswordResetToken.used_at.is_(None))
        .values(used_at=now)
    )
    if claimed.rowcount != 1:  # pragma: no cover - carrera entre dos peticiones simultáneas
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El enlace no es válido o ha caducado. Pide uno nuevo.",
        )
    user.password_hash = hash_password(data.new_password)
    user.token_version += 1  # cierra todas las sesiones abiertas
    activity.log(db, user.id, "password_reset", request)
    db.commit()
    # Quien controla el email recupera el acceso aunque un atacante haya bloqueado la cuenta
    # a base de fallos (abuso del bloqueo, T1531 Account Access Removal)
    login_failures.clear(user.email)
    record(Event.RESET_DONE, request, user=user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def _as_utc(moment: datetime) -> datetime:
    """SQLite devuelve fechas sin zona horaria; las guardamos siempre en UTC."""
    return moment if moment.tzinfo else moment.replace(tzinfo=UTC)


def _reject_weak(password: str, email: str, name: str) -> None:
    """Contraseñas comunes o con datos personales: 422 con el motivo (ADR-0023, M1027)."""
    problem = weakness(password, email, name)
    if problem:
        raise HTTPException(status_code=422, detail=problem)
