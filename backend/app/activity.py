"""Actividad de la cuenta que ve el propio usuario (ADR-0025).

Complementa el registro de seguridad del servidor (security_events.py): aquel es para detectar
ataques y va seudonimizado; este es para que la persona vea si alguien ha entrado en su cuenta.
Minimización de datos: solo el tipo de evento, la fecha y un dispositivo aproximado, sin IP.
"""

from fastapi import Request
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models import AccountEvent

KEPT = 20  # eventos que se conservan por usuario

KINDS = {
    "login",
    "login_failed",
    "password_changed",
    "password_reset",
    "logout_all",
    "name_changed",
}

_SYSTEMS = (
    ("android", "Android"),
    ("iphone", "iPhone"),
    ("ipad", "iPad"),
    ("windows", "Windows"),
    ("mac os", "Mac"),
    ("linux", "Linux"),
)
_BROWSERS = (
    ("edg/", "Edge"),
    ("opr/", "Opera"),
    ("firefox", "Firefox"),
    ("chrome", "Chrome"),
    ("safari", "Safari"),
    ("okhttp", "App Android"),
)


def device(request: Request | None) -> str:
    """«Android · Chrome», «Windows · Firefox»… a partir del User-Agent, sin guardarlo entero."""
    agent = (request.headers.get("user-agent", "") if request else "").lower()
    system = next((name for key, name in _SYSTEMS if key in agent), "")
    browser = next((name for key, name in _BROWSERS if key in agent), "")
    return " · ".join(part for part in (system, browser) if part) or "Dispositivo desconocido"


def log(db: Session, user_id: int, kind: str, request: Request | None = None) -> None:
    """Añade un evento y borra los más antiguos. Sin commit: va con la operación que lo causa."""
    db.add(AccountEvent(user_id=user_id, kind=kind, device=device(request)))
    db.flush()
    old = (
        select(AccountEvent.id)
        .where(AccountEvent.user_id == user_id)
        .order_by(AccountEvent.id.desc())
        .offset(KEPT)
    )
    db.execute(delete(AccountEvent).where(AccountEvent.id.in_(old)))


def recent(db: Session, user_id: int) -> list[AccountEvent]:
    return list(
        db.scalars(
            select(AccountEvent)
            .where(AccountEvent.user_id == user_id)
            .order_by(AccountEvent.id.desc())
        )
    )
