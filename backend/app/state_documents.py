"""Documentos de progreso guardados enteros (PCAP y cursos), con control de versiones.

La app fusiona su copia local con la de la cuenta y sube el documento completo. Si dos pestañas o
dos dispositivos lo hacen a la vez, la última escritura borraría lo de la otra. Para evitarlo,
cada guardado dice qué versión leyó (`version`): si la de la cuenta ya es otra, se responde 409 y la
app vuelve a leer, fusiona y reintenta. La comprobación y el guardado van en una sola sentencia
UPDATE ... WHERE version = :leída, así que dos peticiones simultáneas no pueden ganar las dos.
"""

from fastapi import HTTPException, status
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import CourseState, PcapState
from app.schemas import PcapStateIn, PcapStateOut

Document = PcapState | CourseState

CONFLICT = "La cuenta ha cambiado desde otra pestaña o dispositivo: vuelve a leerla y fusiona"


def to_out(state: Document | None) -> PcapStateOut:
    if state is None:
        return PcapStateOut(data={}, updated_at=None, version=0)
    return PcapStateOut(data=state.data, updated_at=state.updated_at, version=state.version)


def _conflict() -> HTTPException:
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=CONFLICT)


def save(db: Session, model: type[Document], key: dict, body: PcapStateIn) -> PcapStateOut:
    """Guarda el documento de `model` con clave primaria `key` (p. ej. {"user_id": 1})."""
    identity = tuple(key.values()) if len(key) > 1 else next(iter(key.values()))
    state = db.get(model, identity)
    expected = body.version

    if state is None:
        if expected not in (None, 0):
            raise _conflict()  # la app leyó un documento que ya no existe
        state = model(**key, data=body.data, version=1)
        db.add(state)
        try:
            db.commit()
        except IntegrityError:  # otra petición lo creó a la vez
            db.rollback()
            raise _conflict() from None
        db.refresh(state)
        return to_out(state)

    conditions = [getattr(model, column) == value for column, value in key.items()]
    if expected is not None:
        conditions.append(model.version == expected)
    result = db.execute(
        update(model)
        .where(*conditions)
        .values(data=body.data, version=model.version + 1)
        .execution_options(synchronize_session=False)
    )
    if result.rowcount == 0:
        db.rollback()
        raise _conflict()
    db.commit()
    db.refresh(state)
    return to_out(state)
