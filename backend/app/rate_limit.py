"""Límites de intentos en memoria (ventana deslizante), por IP y por cuenta (ADR-0022).

Suficiente para una sola instancia del servidor. Con varias instancias
habría que compartir el estado (por ejemplo, en Redis).
"""

import time
from collections import deque

from fastapi import HTTPException, Request, status

from app.config import get_settings

# Con más claves que esto se purgan las caducadas, para que la memoria no crezca sin límite
_SWEEP_ABOVE = 10_000


class RateLimiter:
    def __init__(self, max_calls: int, window_seconds: float = 60.0):
        self.max_calls = max_calls
        self.window_seconds = window_seconds
        self._hits: dict[str, deque[float]] = {}

    def _recent(self, key: str, now: float) -> deque[float]:
        hits = self._hits.get(key, deque())
        while hits and now - hits[0] > self.window_seconds:
            hits.popleft()
        return hits

    def _sweep(self, now: float) -> None:
        for key in [k for k in self._hits if not self._recent(k, now)]:
            del self._hits[key]

    def blocked(self, key: str) -> bool:
        """¿Ha agotado ya los intentos de la ventana? (sin contar uno nuevo)."""
        return len(self._recent(key, time.monotonic())) >= self.max_calls

    def record(self, key: str) -> None:
        now = time.monotonic()
        if len(self._hits) > _SWEEP_ABOVE:
            self._sweep(now)
        hits = self._recent(key, now)
        hits.append(now)
        self._hits[key] = hits

    def hit(self, key: str) -> bool:
        """Registra un intento. Devuelve False si se ha superado el límite."""
        if self.blocked(key):
            return False
        self.record(key)
        return True

    def clear(self, key: str) -> None:
        self._hits.pop(key, None)

    def reset(self) -> None:
        self._hits.clear()


_settings = get_settings()
auth_limiter = RateLimiter(_settings.auth_rate_limit_per_minute)
# Fallos de login por cuenta: frena la fuerza bruta repartida entre muchas IPs
login_failures = RateLimiter(
    _settings.login_failures_per_account, _settings.login_lockout_minutes * 60
)
# Peticiones de recuperación por email: evita llenar de correos la bandeja de alguien
reset_requests = RateLimiter(3, 15 * 60)

TOO_MANY = "Demasiados intentos. Espera un poco y vuelve a probar."


def client_ip(request: Request) -> str:
    """IP del cliente. Detrás de N proxies de confianza, cada uno AÑADE al final de
    X-Forwarded-For la IP que le conecta: la real es la N-ésima empezando por el final.
    Las anteriores las puede escribir el propio cliente, así que nunca se usan."""
    hops = get_settings().trusted_proxy_hops
    header = request.headers.get("x-forwarded-for", "")
    forwarded = [part.strip() for part in header.split(",") if part.strip()]
    if hops > 0 and len(forwarded) >= hops:
        return forwarded[-hops]
    return request.client.host if request.client else "unknown"


def limit_auth_attempts(request: Request) -> None:
    if not auth_limiter.hit(client_ip(request)):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=TOO_MANY)
