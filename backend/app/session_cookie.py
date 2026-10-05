"""Sesión de la web en una cookie HttpOnly (ADR-0033).

La web pide este modo con la cabecera `X-PLD-Session: cookie`. Entonces el token no viaja en el
cuerpo de la respuesta: va en una cookie que JavaScript no puede leer, así que un XSS no puede
llevárselo para usarlo fuera del navegador (T1539). La sesión sobrevive además a recargar.

- `SameSite=None; Secure; Partitioned`: la web (GitHub Pages) y la API (Render) están en sitios
  distintos. Con `Partitioned` (CHIPS) la cookie solo vale cuando la API se usa desde la web.
- CSRF: la cookie solo se acepta si la petición trae también la cabecera. Una cabecera propia
  obliga al navegador a preguntar antes (preflight CORS), y CORS solo deja pasar a la web.

Los clientes sin esa cabecera (la app Android, scripts) siguen con `Authorization: Bearer`.
"""

from fastapi import Request, Response

from app.config import get_settings
from app.schemas import Token
from app.security import create_access_token

COOKIE_NAME = "__Host-pld_session"
MODE_HEADER = "X-PLD-Session"


def wants_cookie(request: Request) -> bool:
    return request.headers.get(MODE_HEADER) == "cookie"


def cookie_token(request: Request) -> str | None:
    """Token de la cookie, solo si la petición lo pide con la cabecera (protección CSRF)."""
    return request.cookies.get(COOKIE_NAME) if wants_cookie(request) else None


def issue_session(request: Request, response: Response, user_id: int, version: int) -> Token:
    """Token nuevo: en la cookie si la web lo pide; si no, en el cuerpo (Bearer)."""
    token = create_access_token(user_id, version)
    if not wants_cookie(request):
        return Token(access_token=token)
    _set(response, token, get_settings().access_token_minutes * 60)
    return Token(access_token=None, token_type="cookie")


def clear_session_cookie(response: Response) -> None:
    _set(response, "", 0)


def _set(response: Response, value: str, max_age: int) -> None:
    # A mano: set_cookie de Starlette solo admite Partitioned con Python 3.14 o posterior.
    # El JWT solo lleva caracteres válidos en una cookie (base64url y puntos).
    response.headers.append(
        "set-cookie",
        f"{COOKIE_NAME}={value}; Max-Age={max_age}; Path=/; Secure; HttpOnly; "
        "SameSite=None; Partitioned",
    )
