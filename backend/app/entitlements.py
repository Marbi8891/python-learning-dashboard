"""Consulta y dependencias de derechos de acceso.

Los derechos se conceden en servidor. La ausencia de filas significa plan Free.
"""

from datetime import UTC, datetime

from fastapi import Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.deps import CurrentUser, DbSession
from app.models import Entitlement


def active_entitlements(
    db: Session, user_id: int, *, now: datetime | None = None
) -> list[Entitlement]:
    """Devuelve solo los derechos vigentes de una cuenta."""
    moment = now or datetime.now(UTC)
    return list(
        db.scalars(
            select(Entitlement)
            .where(
                Entitlement.user_id == user_id,
                Entitlement.starts_at <= moment,
                or_(Entitlement.ends_at.is_(None), Entitlement.ends_at > moment),
            )
            .order_by(Entitlement.feature_key)
        )
    )


def has_entitlement(
    db: Session, user_id: int, feature_key: str, *, now: datetime | None = None
) -> bool:
    """Comprueba un derecho sin aceptar datos de plan enviados por el navegador."""
    moment = now or datetime.now(UTC)
    return (
        db.scalar(
            select(Entitlement.id)
            .where(
                Entitlement.user_id == user_id,
                Entitlement.feature_key == feature_key,
                Entitlement.starts_at <= moment,
                or_(Entitlement.ends_at.is_(None), Entitlement.ends_at > moment),
            )
            .limit(1)
        )
        is not None
    )


def require_entitlement(feature_key: str):
    """Dependencia FastAPI reutilizable para proteger endpoints premium."""

    def dependency(user: CurrentUser, db: DbSession) -> None:
        if not has_entitlement(db, user.id, feature_key):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "entitlement_required",
                    "feature": feature_key,
                    "message": "Esta función requiere un plan compatible.",
                },
            )

    return Depends(dependency)
