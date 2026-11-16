"""Catálogo de cursos por familias (Excel profesional, fase P0).

Los cursos de frontend/js/catalog.js (DAW y academias) guardan su progreso en
/api/course-state/{id}. Si un curso del catálogo faltara en `COURSES`, la cuenta rechazaría su
progreso con un 404 y el alumno lo perdería al cambiar de dispositivo.
"""

import re
from pathlib import Path

from app.schemas import COURSES

CATALOG = Path(__file__).resolve().parents[2] / "frontend" / "js" / "catalog.js"
CORE_STORES = {"learn", "game", "planner"}  # documentos del núcleo, no son cursos del catálogo


def catalog_ids() -> list[str]:
    return re.findall(r'^\s*id: "([a-z0-9-]+)"', CATALOG.read_text(encoding="utf-8"), re.M)


def test_catalog_and_backend_list_the_same_courses():
    ids = catalog_ids()
    assert "excel" in ids and "sql" in ids
    assert len(ids) == len(set(ids))
    assert set(ids) == set(COURSES) - CORE_STORES


def test_excel_progress_is_a_versioned_document(client, auth_headers):
    path = "/api/v1/course-state/excel"
    assert client.get(path, headers=auth_headers).json() == {
        "data": {},
        "updated_at": None,
        "version": 0,
    }
    first = client.put(path, json={"data": {"done": {}}, "version": 0}, headers=auth_headers)
    assert first.status_code == 200 and first.json()["version"] == 1
    # Otra pestaña que leyó la versión 0 no puede pisar lo guardado
    stale = client.put(path, json={"data": {}, "version": 0}, headers=auth_headers)
    assert stale.status_code == 409
    # Los documentos de los cursos de DAW siguen aparte
    assert client.get("/api/v1/course-state/sql", headers=auth_headers).json()["version"] == 0
    exported = client.get("/api/v1/users/me/export", headers=auth_headers).json()
    assert exported["courses"] == {"excel": {"done": {}}}
