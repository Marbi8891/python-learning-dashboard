"""Registro de eventos de seguridad para detectar ataques (MITRE ATT&CK M1047 «Audit», ADR-0023).

Cada evento es una línea JSON en el logger `pld.security` con la técnica ATT&CK que puede indicar,
para buscarlo y alertar en los logs de Render (o de cualquier recolector).

Privacidad (RGPD, minimización): nunca se registran emails, contraseñas, tokens ni IPs en claro.
La IP y el email se sustituyen por un seudónimo (HMAC con el secreto del servidor, truncado) que
permite correlacionar intentos del mismo origen o contra la misma cuenta sin revelar quién es.
"""

import hashlib
import hmac
import json
import logging
from enum import StrEnum

from fastapi import Request

from app.config import get_settings

logger = logging.getLogger("pld.security")


class Event(StrEnum):
    """Evento → técnica de ATT&CK Enterprise v19 que puede delatar."""

    LOGIN_FAILED = "auth.login_failed"  # T1110 Brute Force
    ACCOUNT_LOCKED = "auth.account_locked"  # T1110.001/.003 (y posible T1531 si es un abuso)
    RATE_LIMITED = "auth.rate_limited"  # T1110 / T1499.003 Application Exhaustion Flood
    LOGIN_OK = "auth.login_ok"  # T1078 Valid Accounts (base para detectar anomalías)
    TOKEN_FORGED = "auth.token_forged"  # T1606.001 Forge Web Credentials
    TOKEN_REVOKED_USED = "auth.token_revoked_used"  # T1550.001 / T1539 token robado reutilizado
    LOGOUT_ALL = "auth.logout_all"
    RESET_REQUESTED = "auth.password_reset_requested"  # T1098 Account Manipulation
    RESET_DONE = "auth.password_reset_done"  # T1098 Account Manipulation
    ACCOUNT_DELETED = "account.deleted"  # T1485 Data Destruction (si no lo pidió el titular)
    BODY_TOO_LARGE = "request.too_large"  # T1499.003 Application Exhaustion Flood


TECHNIQUE = {
    Event.LOGIN_FAILED: "T1110",
    Event.ACCOUNT_LOCKED: "T1110",
    Event.RATE_LIMITED: "T1110",
    Event.LOGIN_OK: "T1078",
    Event.TOKEN_FORGED: "T1606.001",
    Event.TOKEN_REVOKED_USED: "T1550.001",
    Event.LOGOUT_ALL: "T1550.001",
    Event.RESET_REQUESTED: "T1098",
    Event.RESET_DONE: "T1098",
    Event.ACCOUNT_DELETED: "T1485",
    Event.BODY_TOO_LARGE: "T1499.003",
}


# Actividad normal que sirve de contexto; el resto son señales de posible ataque (WARNING)
ROUTINE = {Event.LOGIN_OK, Event.LOGOUT_ALL, Event.RESET_DONE, Event.ACCOUNT_DELETED}


def pseudonym(value: str) -> str:
    """Seudónimo estable de un dato personal: mismo valor → mismo seudónimo, pero irreversible
    sin el secreto del servidor (no es un simple hash que se pueda atacar con un diccionario)."""
    key = (get_settings().jwt_secret or "sin-secreto").encode()
    return hmac.new(key, value.strip().lower().encode(), hashlib.sha256).hexdigest()[:16]


def record(event: Event, request: Request | None = None, **fields: object) -> None:
    """Escribe el evento. `fields` no debe llevar datos personales en claro: usa `pseudonym`."""
    from app.rate_limit import client_ip  # evita la importación circular

    entry: dict[str, object] = {"event": event.value, "attack": TECHNIQUE[event], **fields}
    if request is not None:
        entry["ip"] = pseudonym(client_ip(request))
        entry["path"] = request.url.path
    level = logging.INFO if event in ROUTINE else logging.WARNING
    logger.log(level, json.dumps(entry, ensure_ascii=False, sort_keys=True))
