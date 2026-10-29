"""Contabilidad y cuotas del tutor híbrido.

Cada respuesta del tutor se cuenta en la tabla `tutor_usage` por usuario, día (UTC) y modalidad:
- «advanced»: llamadas a la IA avanzada (de pago). Tienen cuota por usuario y día y un total de
  todos los usuarios por día. La consulta se reserva ANTES de llamar al proveedor, así que una
  avalancha de peticiones no puede pasarse del límite mientras esperan la respuesta.
- «free»: respuestas sin coste de proveedor (tutor sin IA, modelo simulado o Ollama local). Solo
  se cuentan: sus límites son los de siempre (server.py, `ModelBudget`).

Se guarda en la base de datos, no en memoria: un reinicio del servidor (Render lo hace a menudo)
no devuelve consultas de pago. Solo cuenta: ni preguntas, ni respuestas, ni código.

Las reservas se hacen con un cerrojo del proceso: con una sola instancia (el despliegue actual) el
límite es exacto. Con varias, dos peticiones simultáneas podrían pasarse en una consulta: queda
documentado en docs/tutor-hibrido.md.
"""

import threading
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, date, datetime
from typing import Literal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import TutorUsage

FREE = "free"
ADVANCED = "advanced"
UsageMode = Literal["free", "advanced"]

_lock = threading.Lock()


def utc_today() -> date:
    return datetime.now(UTC).date()


@dataclass(frozen=True)
class AdvancedLimits:
    per_user_daily: int
    global_daily: int


@dataclass(frozen=True)
class AdvancedQuota:
    """Lo que el alumno puede saber de su cuota (nunca el uso de los demás, solo si queda)."""

    limit: int
    used: int
    remaining: int
    global_available: bool


class QuotaExceeded(Exception):
    """No quedan consultas avanzadas: `scope` es «user» (las suyas) o «global» (las de todos)."""

    def __init__(self, scope: Literal["user", "global"]):
        super().__init__(scope)
        self.scope = scope


@dataclass(frozen=True)
class Reservation:
    day: date
    remaining: int  # consultas avanzadas que le quedan hoy, contando ya esta


class UsageLedger:
    """Cuotas y consumo de un usuario, con la sesión de base de datos de su petición."""

    def __init__(
        self,
        db: Session,
        user_id: int,
        limits: AdvancedLimits,
        today: Callable[[], date] = utc_today,
    ):
        self.db = db
        self.user_id = user_id
        self.limits = limits
        self.today = today

    def quota(self) -> AdvancedQuota:
        day = self.today()
        row = self.db.get(TutorUsage, (self.user_id, day, ADVANCED))
        used = row.requests if row else 0
        return AdvancedQuota(
            limit=self.limits.per_user_daily,
            used=used,
            remaining=max(0, self.limits.per_user_daily - used),
            global_available=self._total(day) < self.limits.global_daily,
        )

    def reserve_advanced(self) -> Reservation:
        """Gasta una consulta avanzada si queda en los dos límites; si no, `QuotaExceeded` y no se
        cuenta nada."""
        with _lock:
            day = self.today()
            row = self._row(day, ADVANCED)
            if row.requests >= self.limits.per_user_daily:
                self.db.rollback()
                raise QuotaExceeded("user")
            if self._total(day) >= self.limits.global_daily:
                self.db.rollback()
                raise QuotaExceeded("global")
            row.requests += 1
            self.db.commit()
            return Reservation(day, self.limits.per_user_daily - row.requests)

    def refund_advanced(self, reservation: Reservation) -> None:
        """Devuelve una consulta que el proveedor no ha llegado a atender (429, clave inválida):
        no se ha cobrado, así que tampoco cuenta para el alumno."""
        with _lock:
            row = self.db.get(TutorUsage, (self.user_id, reservation.day, ADVANCED))
            if row and row.requests > 0:
                row.requests -= 1
                self.db.commit()

    def add_tokens(
        self, reservation: Reservation, input_tokens: int | None, output_tokens: int | None
    ) -> None:
        """Tokens que ha informado el proveedor para una consulta avanzada ya reservada."""
        with _lock:
            row = self._row(reservation.day, ADVANCED)
            row.input_tokens += max(0, input_tokens or 0)
            row.output_tokens += max(0, output_tokens or 0)
            self.db.commit()

    def count_free(self, input_tokens: int | None = None, output_tokens: int | None = None) -> None:
        with _lock:
            row = self._row(self.today(), FREE)
            row.requests += 1
            row.input_tokens += max(0, input_tokens or 0)
            row.output_tokens += max(0, output_tokens or 0)
            self.db.commit()

    def _row(self, day: date, mode: UsageMode) -> TutorUsage:
        row = self.db.get(TutorUsage, (self.user_id, day, mode))
        if row is None:
            row = TutorUsage(
                user_id=self.user_id,
                day=day,
                mode=mode,
                requests=0,
                input_tokens=0,
                output_tokens=0,
            )
            self.db.add(row)
        return row

    def _total(self, day: date) -> int:
        return self.db.scalar(
            select(func.coalesce(func.sum(TutorUsage.requests), 0)).where(
                TutorUsage.day == day, TutorUsage.mode == ADVANCED
            )
        )
