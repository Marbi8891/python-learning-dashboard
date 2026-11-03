"""Catálogo de recursos complementarios de DAW (frontend/data/resources.json).

Lo genera y valida scripts/resources/build_resources.py. Estas pruebas comprueban que el JSON
publicado es válido y que el validador detecta los errores típicos al ampliar el catálogo.
"""

import importlib.util
import json

from app.config import FRONTEND_DIR

SCRIPT = FRONTEND_DIR.parent / "scripts" / "resources" / "build_resources.py"
spec = importlib.util.spec_from_file_location("build_resources", SCRIPT)
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)

CATALOG = json.loads((FRONTEND_DIR / "data" / "resources.json").read_text("utf-8"))
GOOD = {
    "id": "res-prueba",
    "title": "Recurso de prueba",
    "modules": ["0373"],
    "lessons": ["marcas/mar-html-css"],
    "author": "Alguien",
    "url": "https://ejemplo.org/",
    "lang": "es",
    "type": "documentacion",
    "license": "CC BY 4.0",
    "reuse": "Citando al autor.",
    "access": "accesible",
    "quality": "alta",
    "description": "Para las pruebas.",
}


def test_published_catalog_is_valid_and_complete():
    assert builder.validate(CATALOG["resources"]) == []
    for resource in CATALOG["resources"]:
        assert resource["checked"] == CATALOG["checked"]
        assert resource["license"], resource["id"]  # nunca vacía: «No identificada» si no consta


def test_unverified_licences_are_said_not_invented():
    unknown = [r for r in CATALOG["resources"] if r["license"].startswith("No identificada")]
    assert unknown, "los recursos sin licencia declarada tienen que decirlo"
    only_linked = {"licencia-no-identificada", "no-verificado", "obsoleto"}
    assert all(r["access"] in only_linked for r in unknown)


def test_a_good_resource_passes():
    assert builder.validate([GOOD]) == []


def test_validator_catches_typical_mistakes():
    bad = [
        GOOD,
        {**GOOD},  # id repetido
        {**GOOD, "id": "res-http", "url": "http://ejemplo.org/"},
        {**GOOD, "id": "res-modulo", "modules": ["9999"]},
        {**GOOD, "id": "res-leccion", "lessons": ["marcas/no-existe"]},
        {**GOOD, "id": "res-sin-titulo", "title": " "},
        {**GOOD, "id": "res-tipo", "type": "video-viral"},
        {**GOOD, "id": "res-descarga", "access": "descargable"},
        {**GOOD, "id": "MAL"},
    ]
    problems = "\n".join(builder.validate(bad))
    for expected in (
        "res-prueba: id repetido",
        "res-http: «url» debe ser una URL https",
        "res-modulo: el módulo 9999 no está en el currículo",
        "res-leccion: la lección marcas/no-existe no existe",
        "res-sin-titulo: falta «title»",
        "res-tipo: tipo desconocido",
        "res-descarga: descargable sin URL de descarga",
        "MAL: id no válido",
    ):
        assert expected in problems
