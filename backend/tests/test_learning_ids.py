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
