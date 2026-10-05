"""Dependencias compartidas por los routers."""

from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Lesson, User
from app.security import decode_access_token, looks_forged
from app.security_events import Event, record
from app.session_cookie import cookie_token

# auto_error=False: si no hay cabecera Authorization, se mira la cookie de la web (ADR-0033)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

DbSession = Annotated[Session, Depends(get_db)]


def get_current_user(
    bearer: Annotated[str | None, Depends(oauth2_scheme)], request: Request, db: DbSession
) -> User:
    token = bearer or cookie_token(request)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    decoded = decode_access_token(token)
    user = db.get(User, decoded[0]) if decoded else None
    if decoded is None and looks_forged(token):
        record(Event.TOKEN_FORGED, request)
    elif user is not None and decoded[1] != user.token_version:
        # Token de antes de cerrar sesiones o cambiar la contraseña: posible token robado
        record(Event.TOKEN_REVOKED_USED, request, user=user.id)
    # Un token emitido antes de cambiar la contraseña deja de valer
    if user is None or decoded[1] != user.token_version:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión no válida o caducada",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_lesson_or_404(db: Session, slug: str) -> Lesson:
    lesson = db.scalar(select(Lesson).where(Lesson.slug == slug))
    if lesson is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lección no encontrada")
    return lesson
