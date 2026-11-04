"""Catálogo del Career Roadmap (scripts/career/, frontend/data/career/).

El progreso del alumno se guarda por id de fase, unidad, competencia, proyecto y criterio: si uno
desaparece o cambia, se pierde ese progreso sin aviso. El generador también valida que cada enlace
apunta a contenido que existe y que los prerrequisitos no forman ciclos.
"""

import importlib.util
import json
from pathlib import Path

from app.config import FRONTEND_DIR

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts" / "career"
spec = importlib.util.spec_from_file_location("build_career", SCRIPTS / "build_career.py")
build_career = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build_career)

DATA = FRONTEND_DIR / "data" / "career"


def test_generated_catalog_is_valid_and_up_to_date():
    files, ids, problems = build_career.build()
    assert problems == []
    for name, data in files.items():
        assert json.loads((DATA / name).read_text("utf-8")) == data, f"{name} no está al día"
    locked = json.loads((SCRIPTS / "ids.lock.json").read_text("utf-8"))
    assert build_career.merged_lock(locked, ids) == locked, "ids nuevos sin registrar"


def test_backend_junior_has_eight_phases_linked_to_real_content():
    roadmap = json.loads((DATA / "python-backend-junior.json").read_text("utf-8"))
    assert [p["id"] for p in roadmap["phases"]] == [
        "fundamentals",
        "professional-python",
        "databases",
        "backend",
        "testing",
        "frontend",
        "devops",
        "career",
    ]
    content = build_career.platform_content()
    for phase in roadmap["phases"]:
        assert phase["units"] and phase["objectives"]
        assert any(not u["pending"] for u in phase["units"]), f"{phase['id']}: todo pendiente"
        for unit in phase["units"]:
            assert unit["pending"] == (not unit["links"])
            for link in unit["links"]:
                assert link["ref"] in content[link["kind"]]
    categories = {s["category"] for s in roadmap["skills"]}
    assert categories <= set(roadmap["categories"])


def test_cycles_and_broken_links_are_rejected():
    assert build_career.find_cycle({"a": ["b"], "b": ["a"]}) == ["a", "b", "a"]
    assert build_career.find_cycle({"a": ["b"], "b": []}) is None
    roadmap = json.loads(json.dumps(build_career.ROADMAPS[0]))
    roadmap["phases"][0]["requires"] = ["career"]
    roadmap["phases"][0]["units"][0]["links"] = [["concept", "no-existe"], ["video", "x"]]
    roadmap["skills"][0]["sources"] = {}
    problems = build_career.Problems()
    build_career.build_roadmap(roadmap, build_career.platform_content(), problems)
    text = "\n".join(problems)
    assert "ciclo de prerrequisitos entre fases" in text
    assert "concept: no existe no-existe" in text
    assert "tipo de enlace desconocido: video" in text
    assert "sin fuentes de evidencias" in text


def test_locked_ids_still_exist():
    locked = json.loads((SCRIPTS / "ids.lock.json").read_text("utf-8"))
    _, ids, _ = build_career.build()
    for kind, values in locked.items():
        lost = [v for v in values if v not in ids[kind]]
        assert not lost, f"{kind} que ya no existen (hace falta un plan de migración): {lost}"
