"""Límites de intentos por IP, por cuenta y por email de recuperación (#110).

Los de autenticación se guardan en PostgreSQL (tabla `rate_limits`), así que valen igual con una
instancia de la API que con varias. Cada intento es una sola sentencia atómica (INSERT … ON
CONFLICT DO UPDATE … WHERE count < límite): dos peticiones a la vez no pueden pasar las dos el
último hueco. Si la base de datos falla, se sigue limitando en la memoria de cada instancia.

El de guardados de progreso sigue en memoria: es muy frecuente y solo protege el espacio de la base
de datos, que ya cuida cada instancia por su lado.

Detalles en docs/auth.md («Límites de intentos compartidos»).
"""

import hashlib
import hmac
import logging
import math
import time
from collections import deque
from collections.abc import Callable

from fastapi import HTTPException, Request, status
from sqlalchemy import Connection, Engine, delete, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.exc import SQLAlchemyError

from app.config import get_settings

logger = logging.getLogger(__name__)

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


_INSERT = {"postgresql": pg_insert, "sqlite": sqlite_insert}
# Cada cuántos intentos una instancia borra las ventanas que ya no cuentan
_PURGE_EVERY = 200


def _default_engine() -> Engine:
    from app.database import engine  # al usarse: la configuración ya está leída

    return engine


_engine: Callable[[], Engine] = _default_engine


def set_engine(engine: Engine | None) -> None:
    """Las pruebas apuntan los límites a su base de datos; None vuelve a la de la app.

    Cada intento va en su propia transacción, aparte de la de la petición: cuenta aunque la
    petición falle después."""
    global _engine
    _engine = (lambda: engine) if engine is not None else _default_engine


class SharedRateLimiter(RateLimiter):
    """El mismo límite, compartido en la base de datos por todas las instancias.

    Ventana deslizante aproximada: cuenta los intentos de la ventana fija actual más la parte de la
    anterior que todavía cae dentro de la última `window_seconds`. Si la base de datos falla, usa
    la ventana en memoria de `RateLimiter` (cada instancia por su lado) y lo avisa en el log."""

    def __init__(self, scope: str, max_calls: int, window_seconds: float = 60.0):
        super().__init__(max_calls, window_seconds)
        self.scope = scope
        self._calls = 0

    def _key(self, key: str) -> str:
        """HMAC con el secreto del servidor: en la tabla no hay emails ni IPs en claro."""
        secret = (get_settings().jwt_secret or "sin-secreto").encode()
        return hmac.new(secret, f"{self.scope}:{key}".encode(), hashlib.sha256).hexdigest()

    def _windows(self) -> tuple[int, float]:
        """(inicio de la ventana fija actual, peso de la anterior)."""
        size = int(self.window_seconds)
        now = time.time()
        start = int(now // size) * size
        return start, 1 - (now - start) / size

    def _count(self, db: Connection, key: str, start: int) -> int:
        from app.models import RateLimitWindow as W

        found = db.scalar(
            select(W.count).where(W.scope == self.scope, W.key == key, W.window_start == start)
        )
        return found or 0

    def _room(self, db: Connection, key: str, start: int, weight: float) -> int:
        """Cuántos intentos caben aún en la ventana actual, descontando los de la anterior."""
        previous = self._count(db, key, start - int(self.window_seconds))
        return self.max_calls - math.floor(previous * weight)

    def _fallback(self, action: str) -> None:
        # Sin la clave ni el mensaje del error: podrían llevar datos de la conexión
        logger.warning("rate_limit %s: la base de datos no responde, límite en memoria", action)

    def blocked(self, key: str) -> bool:
        try:
            with _engine().begin() as db:
                start, weight = self._windows()
                hashed = self._key(key)
                return self._count(db, hashed, start) >= self._room(db, hashed, start, weight)
        except SQLAlchemyError:
            self._fallback("blocked")
            return super().blocked(key)

    def hit(self, key: str) -> bool:
        """Registra un intento si cabe, en una sola sentencia atómica. False si no cabe."""
        from app.models import RateLimitWindow as W

        try:
            with _engine().begin() as db:
                start, weight = self._windows()
                hashed = self._key(key)
                room = self._room(db, hashed, start, weight)
                if room < 1:
                    return False
                insert = _INSERT[db.dialect.name]
                statement = (
                    insert(W)
                    .values(scope=self.scope, key=hashed, window_start=start, count=1)
                    .on_conflict_do_update(
                        index_elements=[W.scope, W.key, W.window_start],
                        set_={"count": W.count + 1},
                        where=W.count < room,
                    )
                    .returning(W.count)
                )
                allowed = db.execute(statement).first() is not None
                self._calls += 1
                if self._calls % _PURGE_EVERY == 0:
                    self._purge(db, start)
                return allowed
        except SQLAlchemyError:
            self._fallback("hit")
            # Los métodos de RateLimiter, no los de esta clase, que volverían a la base de datos
            if RateLimiter.blocked(self, key):
                return False
            RateLimiter.record(self, key)
            return True

    def record(self, key: str) -> None:
        """Cuenta un intento en la base de datos compartida (si no está ya en el límite)."""
        self.hit(key)

    def _purge(self, db: Connection, start: int) -> None:
        from app.models import RateLimitWindow as W

        old = start - int(self.window_seconds)
        db.execute(delete(W).where(W.scope == self.scope, W.window_start < old))

    def clear(self, key: str) -> None:
        from app.models import RateLimitWindow as W

        super().clear(key)
        try:
            with _engine().begin() as db:
                db.execute(delete(W).where(W.scope == self.scope, W.key == self._key(key)))
        except SQLAlchemyError:
            self._fallback("clear")

    def reset(self) -> None:
        """Vacía el límite entero (para las pruebas)."""
        from app.models import RateLimitWindow as W

        super().reset()
        try:
            with _engine().begin() as db:
                db.execute(delete(W).where(W.scope == self.scope))
        except SQLAlchemyError:
            self._fallback("reset")


_settings = get_settings()
auth_limiter = SharedRateLimiter("auth_ip", _settings.auth_rate_limit_per_minute)
# Fallos de login por cuenta: frena la fuerza bruta repartida entre muchas IPs
login_failures = SharedRateLimiter(
    "login_account", _settings.login_failures_per_account, _settings.login_lockout_minutes * 60
)
# Peticiones de recuperación por email: evita llenar de correos la bandeja de alguien
reset_requests = SharedRateLimiter("reset_email", 3, 15 * 60)
# Guardados de progreso por usuario (AUD-009): la base de datos gratuita tiene poco espacio
write_limiter = RateLimiter(_settings.write_rate_limit_per_minute)

TOO_MANY = "Demasiados intentos. Espera un poco y vuelve a probar."
TOO_MANY_WRITES = (
    "Demasiados guardados seguidos. Tu progreso sigue en este navegador: se volverá a intentar."
)


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
        from app.security_events import Event, record  # evita la importación circular

        record(Event.RATE_LIMITED, request)
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=TOO_MANY)
