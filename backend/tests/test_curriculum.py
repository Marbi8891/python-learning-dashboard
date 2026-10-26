"""Catálogo del currículo de DAW (frontend/data/curriculum/daw-cyl.json).

Protege los datos oficiales: si un cambio pierde un módulo, un RA o un criterio, o rompe una
referencia, estas pruebas fallan. El JSON lo genera scripts/curriculum/build_curriculum.py.
"""

import json
from pathlib import Path

import pytest

from app.config import FRONTEND_DIR

CATALOG = json.loads((FRONTEND_DIR / "data" / "curriculum" / "daw-cyl.json").read_text("utf-8"))
MODULES = {m["id"]: m for m in CATALOG["modules"]}
SOURCES = {s["id"] for s in CATALOG["sources"]}

# Número de resultados de aprendizaje de cada módulo técnico en el RD 405/2023 (anexo I)
OFFICIAL_OUTCOMES = {
    "0483": 7,
    "0484": 7,
    "0485": 9,
    "0373": 7,
    "0487": 6,
    "0612": 7,
    "0613": 9,
    "0614": 6,
    "0615": 6,
}


def test_all_modules_of_the_order_are_present():
    codes = {m["code"] for m in CATALOG["modules"] if m["code"]}
    assert codes == set(OFFICIAL_OUTCOMES) | {"0179", "1709", "1710", "1665", "1708", "0616"}
    assert {"optativo-1", "optativo-2"} <= set(MODULES)


def test_hours_match_the_order():
    assert sum(m["hours"] for m in CATALOG["modules"]) == CATALOG["cycle"]["hours"] == 2000
    assert sum(m["hours"] for m in CATALOG["modules"] if m["course"] == 1) == 986
    for course in (1, 2):
        weekly = sum(m["weeklyHours"] or 0 for m in CATALOG["modules"] if m["course"] == course)
        assert weekly == 30


@pytest.mark.parametrize("code", sorted(OFFICIAL_OUTCOMES))
def test_technical_modules_keep_every_outcome_and_criterion(code):
    module = MODULES[code]
    assert module["status"] == "oficial"
    assert [ra["number"] for ra in module["learningOutcomes"]] == list(
        range(1, OFFICIAL_OUTCOMES[code] + 1)
    )
    for ra in module["learningOutcomes"]:
        assert ra["text"] and ra["criteria"], ra["id"]
        assert all(c["text"] for c in ra["criteria"]), ra["id"]
    assert module["ects"] and module["stateMinHours"] and module["contents"]


def test_ids_are_unique():
    outcomes = [ra for m in CATALOG["modules"] for ra in m["learningOutcomes"]]
    ids = [ra["id"] for ra in outcomes] + [c["id"] for ra in outcomes for c in ra["criteria"]]
    assert len(ids) == len(set(ids))


def test_pending_modules_have_no_invented_data():
    for module in CATALOG["modules"]:
        if module["status"] == "pendiente":
            assert module["learningOutcomes"] == [] and module["ects"] is None, module["id"]


def test_every_reference_points_to_a_known_source_and_course():
    courses = {p.name for p in Path(FRONTEND_DIR / "data" / "courses").iterdir() if p.is_dir()}
    for module in CATALOG["modules"]:
        for ref in (module["source"], module["outcomesSource"]):
            assert ref is None or ref.split("#")[0] in SOURCES, (module["id"], ref)
        assert set(module["platformCourses"]) <= courses, module["id"]


def test_every_course_question_is_tagged_with_a_catalog_module():
    total = 0
    for bank in sorted(Path(FRONTEND_DIR / "data" / "courses").glob("*/bank.json")):
        questions = json.loads(bank.read_text("utf-8"))["questions"]
        total += len(questions)
        for q in questions:
            assert q.get("module") in MODULES, (bank.parent.name, q["id"])
    assert sum(m["platformQuestions"] for m in CATALOG["modules"]) == total


def test_platform_activities_are_marked_as_practice():
    assert "no son evaluaciones oficiales" in CATALOG["notice"]
