"""Contraseñas (Argon2) y tokens de acceso (JWT)."""

import hashlib
import secrets
from datetime import UTC, datetime, timedelta

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

from app.config import get_settings

ALGORITHM = "HS256"
MIN_SECRET_LENGTH = 32

_hasher = PasswordHasher()
# Se usa cuando el email no existe, para que el login tarde lo mismo
# y no revele qué emails están registrados (enumeración de usuarios).
_DUMMY_HASH = _hasher.hash("contrasena-ficticia-para-igualar-tiempos")


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str | None) -> bool:
    try:
        _hasher.verify(password_hash or _DUMMY_HASH, password)
    except (VerificationError, InvalidHashError):
        return False
    return password_hash is not None


def get_jwt_secret() -> str:
    secret = get_settings().jwt_secret
    if not secret or len(secret) < MIN_SECRET_LENGTH:
        raise RuntimeError(
            f"JWT_SECRET no configurado o demasiado corto (mínimo {MIN_SECRET_LENGTH} caracteres). "
            'Genera uno con: python -c "import secrets; print(secrets.token_urlsafe(48))"'
        )
    return secret


def create_access_token(user_id: int, token_version: int = 0) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": str(user_id),
        "ver": token_version,
        "iat": now,
        "exp": now + timedelta(minutes=get_settings().access_token_minutes),
    }
    return jwt.encode(payload, get_jwt_secret(), algorithm=ALGORITHM)


def decode_access_token(token: str) -> tuple[int, int] | None:
    """Devuelve (id de usuario, versión del token), o None si es inválido o ha caducado."""
    try:
        payload = jwt.decode(token, get_jwt_secret(), algorithms=[ALGORITHM])
        return int(payload["sub"]), int(payload.get("ver", 0))
    except (jwt.PyJWTError, KeyError, ValueError, TypeError):
        return None


def new_reset_token() -> tuple[str, str]:
    """Devuelve (token para el enlace, hash para guardar en la base de datos)."""
    token = secrets.token_urlsafe(32)
    return token, hash_reset_token(token)


def hash_reset_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()
