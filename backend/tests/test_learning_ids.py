"""Ids estables del núcleo por conceptos (scripts/learning/ids.lock.json).

El progreso por conceptos (`pld:learn`) se guarda por id de concepto, de ejercicio y de error
típico. Si uno desaparece o cambia, el alumno pierde ese progreso sin aviso.
"""

import json
from pathlib import Path

from app.config import FRONTEND_DIR

LOCK = Path(__file__).resolve().parents[2] / "scripts" / "learning" / "ids.lock.json"
DATA = json.loads((FRONTEND_DIR / "data" / "learning.json").read_text("utf-8"))
NOW = {
    "concepts": {c["id"] for c in DATA["concepts"]},
    "exercises": {e["id"] for e in DATA["exercises"]},
    "errors": {error["id"] for c in DATA["concepts"] for error in c["errors"]},
}


def test_locked_ids_still_exist():
    locked = json.loads(LOCK.read_text("utf-8"))
    assert set(locked) == set(NOW)
    for kind, ids in locked.items():
        lost = [i for i in ids if i not in NOW[kind]]
        assert not lost, f"{kind} que ya no existen (hace falta un plan de migración): {lost}"


def test_new_ids_are_registered():
    locked = json.loads(LOCK.read_text("utf-8"))
    for kind, ids in NOW.items():
        new = sorted(ids - set(locked[kind]))
        assert not new, f"{kind}: ids sin registrar; ejecuta build_learning.py: {new[:5]}"


def test_knowledge_model_uses_official_criteria():
    """F1.4: cada concepto dice qué CE trabaja; RA y módulo salen de ellos y existen."""
    catalog = json.loads((FRONTEND_DIR / "data" / "curriculum" / "daw-cyl.json").read_text("utf-8"))
    outcomes = {
        ra["id"]: {ce["id"] for ce in ra["criteria"]}
        for module in catalog["modules"]
        for ra in module.get("learningOutcomes", [])
    }
    for concept in DATA["concepts"]:
        assert concept["ce"], f"{concept['id']}: sin criterios de evaluación"
        assert concept["module"] == "0485"
        assert set(concept["ra"]) == {c.rsplit("-", 1)[0] for c in concept["ce"]}
        for ce in concept["ce"]:
            assert ce in outcomes[ce.rsplit("-", 1)[0]], f"{concept['id']}: {ce} no existe"
        assert 1 <= concept["difficulty"] <= 3
        assert concept["importance"] == concept["daw"]
