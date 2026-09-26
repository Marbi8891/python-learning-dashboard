"""Límite de peticiones en memoria (ventana deslizante por IP).

Suficiente para una sola instancia del servidor. Con varias instancias
habría que compartir el estado (por ejemplo, en Redis).
"""

import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request, status

from app.config import get_settings


class RateLimiter:
    def __init__(self, max_calls: int, window_seconds: float = 60.0):
        self.max_calls = max_calls
        self.window_seconds = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def hit(self, key: str) -> bool:
        """Registra un intento. Devuelve False si se ha superado el límite."""
        now = time.monotonic()
        hits = self._hits[key]
        while hits and now - hits[0] > self.window_seconds:
            hits.popleft()
        if len(hits) >= self.max_calls:
            return False
        hits.append(now)
        return True

    def reset(self) -> None:
        self._hits.clear()


auth_limiter = RateLimiter(get_settings().auth_rate_limit_per_minute)


def limit_auth_attempts(request: Request) -> None:
    client_ip = request.client.host if request.client else "unknown"
    if not auth_limiter.hit(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Demasiados intentos. Espera un minuto.",
        )
