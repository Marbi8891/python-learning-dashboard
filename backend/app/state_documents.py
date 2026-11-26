"""Documentos de progreso guardados enteros (PCAP y cursos), con control de versiones.

La app fusiona su copia local con la de la cuenta y sube el documento completo. Si dos pestañas o
dos dispositivos lo hacen a la vez, la última escritura borraría lo de la otra. Para evitarlo,
cada guardado dice qué versión leyó (`version`): si la de la cuenta ya es otra, se responde 409 y la
app vuelve a leer, fusiona y reintenta. La comprobación y el guardado van en una sola sentencia
UPDATE ... WHERE version = :leída, así que dos peticiones simultáneas no pueden ganar las dos.

Sin `version` (PLD-003): solo se acepta para crear el documento, porque entonces no hay nada que
pisar. Si el documento ya existe, se responde 428 (Precondition Required) en vez de sobrescribirlo
sin comprobar: así un cliente que no sabe qué versión leyó (una pestaña con una web anterior a #77,
un script) nunca borra en silencio lo guardado desde otro dispositivo. Sus datos no se pierden:
siguen en ese navegador y se fusionan al recargar la web. Ver docs/SYNC_VERSIONING.md.
"""

import logging

from fastapi import HTTPException, status
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import CourseState, PcapState
from app.schemas import PcapStateIn, PcapStateOut

Document = PcapState | CourseState

logger = logging.getLogger("pld.sync")

CONFLICT = "La cuenta ha cambiado desde otra pestaña o dispositivo: vuelve a leerla y fusiona"
VERSION_REQUIRED = (
    "Falta la versión leída (`version`): vuelve a leer la cuenta, fusiona y guarda con esa versión"
)


def to_out(state: Document | None) -> PcapStateOut:
    if state is None:
        return PcapStateOut(data={}, updated_at=None, version=0)
    return PcapStateOut(data=state.data, updated_at=state.updated_at, version=state.version)


def _describe(model: type[Document], key: dict) -> str:
    """Qué documento es, para los logs (sin datos del alumno: solo su id interno)."""
    return f"{model.__tablename__} " + " ".join(f"{name}={value}" for name, value in key.items())


def _conflict(model: type[Document], key: dict, reason: str, **versions: object) -> HTTPException:
    logger.info(
        "sync.conflict %s motivo=%s %s",
        _describe(model, key),
        reason,
        " ".join(f"{name}={value}" for name, value in versions.items()),
    )
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=CONFLICT)


def save(db: Session, model: type[Document], key: dict, body: PcapStateIn) -> PcapStateOut:
    """Guarda el documento de `model` con clave primaria `key` (p. ej. {"user_id": 1})."""
    identity = tuple(key.values()) if len(key) > 1 else next(iter(key.values()))
    state = db.get(model, identity)
    expected = body.version

    if state is None:
        if expected not in (None, 0):
            # la app leyó un documento que ya no existe (p. ej. se borró la cuenta en otra pestaña)
            raise _conflict(model, key, "no_existe", leida=expected, actual=0)
        state = model(**key, data=body.data, version=1)
        db.add(state)
        try:
            db.commit()
        except IntegrityError:  # otra petición lo creó a la vez
            db.rollback()
            raise _conflict(model, key, "creado_a_la_vez", leida=expected) from None
        db.refresh(state)
        return to_out(state)

    if expected is None:
        # Sin versión no se puede saber si pisaría lo de otro dispositivo: no se sobrescribe
        logger.warning(
            "sync.version_missing %s actual=%s: guardado sin versión rechazado (428)",
            _describe(model, key),
            state.version,
        )
        raise HTTPException(
            status_code=status.HTTP_428_PRECONDITION_REQUIRED, detail=VERSION_REQUIRED
        )

    conditions = [getattr(model, column) == value for column, value in key.items()]
    result = db.execute(
        update(model)
        .where(*conditions, model.version == expected)
        .values(data=body.data, version=model.version + 1)
        .execution_options(synchronize_session=False)
    )
    if result.rowcount == 0:
        seen = state.version  # la que había al leer; otra petición puede haberla subido después
        db.rollback()
        raise _conflict(model, key, "version_antigua", leida=expected, vista=seen)
    db.commit()
    db.refresh(state)
    return to_out(state)


# Respuestas de error del PUT de un documento, para la documentación OpenAPI
STATE_RESPONSES: dict[int | str, dict] = {
    409: {"description": "La cuenta cambió: vuelve a leerla, fusiona y reintenta"},
    428: {"description": "Falta `version` y el documento ya existe: no se sobrescribe"},
}
