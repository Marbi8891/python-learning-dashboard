"""¿Puede la API atender de verdad? Base de datos y migraciones (#111).

`/api/health` solo dice que el proceso está vivo: es lo que mira Render para reiniciar el
servicio, y no debe depender de la base de datos (si Neon tarda en despertar, Render entraría en
un bucle de reinicios). `/api/v1/ready` sí la comprueba y es lo que debe mirar un monitor externo:

- `database`: la base de datos responde a `SELECT 1`.
- `migrations`: el esquema está en la última migración de Alembic (`pending` si falta alguna).

Si algo falla responde 503 sin detalles internos; el detalle va al log del servidor.
"""

import logging
import time
from functools import lru_cache
from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

ALEMBIC_INI = Path(__file__).resolve().parents[1] / "alembic.ini"


@lru_cache
def expected_revision() -> str:
    """La última migración que trae el código desplegado."""
    return ScriptDirectory.from_config(Config(str(ALEMBIC_INI))).get_current_head()


def check(db: Session) -> tuple[bool, dict]:
    started = time.perf_counter()
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        logger.exception("ready: la base de datos no responde")
        return False, {"status": "error", "database": "error", "migrations": "unknown"}
    elapsed = round((time.perf_counter() - started) * 1000)
    try:
        current = db.execute(text("SELECT version_num FROM alembic_version")).scalar()
    except SQLAlchemyError:
        db.rollback()  # en PostgreSQL, una consulta fallida deja la transacción abortada
        current = None
    migrations = "ok" if current == expected_revision() else "pending"
    if migrations != "ok":
        logger.error("ready: esquema en %s, el código espera %s", current, expected_revision())
    ok = migrations == "ok"
    return ok, {
        "status": "ok" if ok else "error",
        "database": "ok",
        "migrations": migrations,
        "database_ms": elapsed,
    }
