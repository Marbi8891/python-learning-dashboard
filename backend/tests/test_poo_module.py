"""Módulo de POO del núcleo por conceptos (frontend/data/learning.json, área `poo`).

build_learning.py --check ejecuta cada ejemplo y cada solución; aquí se comprueba la estructura
que ve la web: el índice de 10 unidades, los once apartados de cada unidad publicada, el banco de
preguntas y que las correspondencias con el currículo nunca se presenten como oficiales sin validar.
"""

import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest

from app.config import FRONTEND_DIR

DATA = json.loads((FRONTEND_DIR / "data" / "learning.json").read_text("utf-8"))
CATALOG = json.loads((FRONTEND_DIR / "data" / "curriculum" / "daw-cyl.json").read_text("utf-8"))
CRITERIA = {
    ce["id"]
    for module in CATALOG["modules"]
    for ra in module.get("learningOutcomes", [])
    for ce in ra["criteria"]
}
MODULE = next(m for m in DATA["modules"] if m["id"] == "poo")
CONCEPTS = {c["id"]: c for c in DATA["concepts"]}
EXERCISES = {e["id"]: e for e in DATA["exercises"]}
UNITS = [CONCEPTS[u["id"]] for u in MODULE["units"] if u["available"]]
FIELDS = ("objectives", "prior", "key", "sections", "guided", "autonomous", "selfcheck", "recap")
LEARNING = Path(__file__).resolve().parents[2] / "scripts" / "learning"


def test_index_has_ten_numbered_units_and_keeps_the_old_route():
    assert [u["number"] for u in MODULE["units"]] == list(range(1, 11))
    assert len({u["id"] for u in MODULE["units"]}) == 10
    # #/teoria/poo sigue existiendo: es la Unidad 2 y conserva su id (y el progreso de los alumnos)
    assert MODULE["units"][1]["id"] == "poo" and MODULE["units"][1]["available"]
    for unit in MODULE["units"]:
        assert unit["available"] == (unit["id"] in CONCEPTS)


def test_published_units_follow_the_module_order_in_the_path():
    # Sprints 2 y 3: Unidades 1-6 publicadas, encadenadas por prerrequisitos y en orden en la ruta
    published = [u["id"] for u in MODULE["units"] if u["available"]]
    assert published[:6] == [
        "poo-fundamentos",
        "poo",
        "poo-atributos-metodos",
        "poo-encapsulacion",
        "poo-herencia",
        "poo-polimorfismo",
    ]
    path = DATA["path"]
    assert [path.index(i) for i in published] == sorted(path.index(i) for i in published)
    assert CONCEPTS["poo"]["requires"] == ["poo-fundamentos"]
    assert CONCEPTS["poo-atributos-metodos"]["requires"] == ["poo"]
    assert CONCEPTS["poo-encapsulacion"]["requires"] == ["poo-atributos-metodos"]
    assert CONCEPTS["poo-herencia"]["requires"] == ["poo-atributos-metodos"]
    assert CONCEPTS["poo-polimorfismo"]["requires"] == ["poo-herencia"]
    for number, uid in enumerate(published, start=1):
        assert CONCEPTS[uid]["unit"] == {"module": "poo", "number": number}


@pytest.mark.parametrize("unit", UNITS, ids=lambda u: u["id"])
def test_unit_has_every_section(unit):
    assert unit["area"] == "poo"
    for field in FIELDS:
        assert unit.get(field), f"falta {field}"
    assert unit["errors"], "sin errores frecuentes"
    assert 0 < unit["pass"]["minScore"] <= 1 and unit["pass"]["text"]
    for section in unit["sections"]:
        assert section["id"].startswith(f"{unit['id']}.")
        assert section["theory"] and section["examples"]
        assert len(section["quiz"]) == 3
        for example in section["examples"]:
            assert "output" in example, "la salida de cada ejemplo se calcula al generar"


@pytest.mark.parametrize("unit", UNITS, ids=lambda u: u["id"])
def test_unit_exercises_are_complete_and_not_repeated(unit):
    own = [e for e in DATA["exercises"] if e["concept"] == unit["id"]]
    assert len(own) >= 8
    used = {i for s in unit["sections"] for i in s["quiz"]}
    used |= set(unit["guided"] + unit["autonomous"] + unit["selfcheck"] + unit["pass"]["required"])
    used |= set(unit.get("extras", []) + unit["bank"])
    assert {e["id"] for e in own} <= used, "hay ejercicios que no aparecen en la unidad"
    assert all(EXERCISES[i]["concept"] == unit["id"] for i in used)
    texts = [" ".join(f"{e['q']} {e.get('code') or ''}".lower().split()) for e in own]
    assert len(texts) == len(set(texts)), "preguntas repetidas"
    errors = {error["id"] for error in unit["errors"]}
    for ex in own:
        assert ex["explain"], f"{ex['id']}: sin explicación"
        if ex["kind"] == "choice":
            assert len(ex["options"]) == 4, f"{ex['id']}: debe tener 4 opciones"
            assert ex["options"][ex["answer"]]["error"] is None
        if ex["kind"] == "code":
            assert ex["solution"] and ex["hint"] and ex["checks"]
        tags = [o["error"] for o in ex.get("options", [])]
        tags += [c.get("error") for c in ex.get("checks", [])]
        for tag in tags:
            assert tag is None or tag in errors or tag.split(".")[0] in CONCEPTS


@pytest.mark.parametrize("unit", UNITS, ids=lambda u: u["id"])
def test_curriculum_mappings_have_status_source_and_date(unit):
    assert unit["curriculum"]
    for mapping in unit["curriculum"]:
        assert mapping["status"] in {"verified", "proposed", "unassigned"}
        assert mapping["source"].split("#")[0] in {s["id"] for s in CATALOG["sources"]}
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", mapping["reviewed"])
        if mapping["status"] != "unassigned":
            assert mapping["ce"] in CRITERIA
        if mapping["status"] == "verified":
            assert mapping["by"] not in ("", "plataforma"), "validar exige una persona"
    # Los CE del concepto son exactamente los de sus correspondencias asignadas
    assigned = [m["ce"] for m in unit["curriculum"] if m["status"] != "unassigned"]
    assert unit["ce"] == assigned


def test_poo_units_stay_out_of_the_daw_simulation_and_diagnostic():
    """El simulacro DAW y la prueba de nivel no cambian hasta decidirlo (Sprint 7)."""
    in_daw = {c for comp in DATA["daw"] for c in comp["concepts"]}
    assert not in_daw & {u["id"] for u in UNITS}


def _load_builder():
    sys.path.insert(0, str(LEARNING))
    spec = importlib.util.spec_from_file_location("build_learning", LEARNING / "build_learning.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_validator_rejects_an_incomplete_unit(monkeypatch):
    builder = _load_builder()
    unit = next(c for c in builder.CONCEPTS if c["id"] == "poo")
    monkeypatch.setitem(unit, "objectives", [])
    monkeypatch.setitem(unit, "curriculum", [{**unit["curriculum"][0], "status": "oficial"}])
    quiet = {"output": "", "error": None, "passed": False}
    monkeypatch.setattr(builder, "execute", lambda *a, **k: quiet)
    problems = builder.Problems()
    builder.check_units(problems)
    assert any("falta el apartado objectives" in p for p in problems)
    assert any("estado no válido" in p for p in problems)


BANK_QTYPES = {"teoria": 3, "codigo": 3, "prediccion": 3, "error": 2, "solucion": 2, "diseno": 2}


@pytest.mark.parametrize("unit", UNITS, ids=lambda u: u["id"])
def test_unit_bank_has_fifteen_balanced_questions(unit):
    """Banco evaluable: 15 por unidad, 4 opciones, un porqué en cada distractor y reparto fijo."""
    bank = [EXERCISES[i] for i in unit["bank"]]
    assert len(bank) == 15 and len({q["id"] for q in bank}) == 15
    assert {t: sum(q["qtype"] == t for q in bank) for t in BANK_QTYPES} == BANK_QTYPES
    assert {n: sum(q["level"] == n for q in bank) for n in (1, 2, 3)} == {1: 5, 2: 6, 3: 4}
    for q in bank:
        assert q["kind"] == "choice" and q["bank"] is True and q["concept"] == unit["id"]
        assert len(q["options"]) == 4 and q["explain"]
        for i, option in enumerate(q["options"]):
            assert (i == q["answer"]) or option.get("why"), f"{q['id']}: distractor sin porqué"
        if q["qtype"] == "prediccion":
            assert q["code"], f"{q['id']}: una pregunta de predicción lleva código"


def test_bank_questions_are_only_those_listed_by_their_units():
    listed = {i for u in UNITS for i in u["bank"]}
    marked = {e["id"] for e in DATA["exercises"] if e.get("bank")}
    assert listed == marked
    assert len(listed) == 15 * len(UNITS)


@pytest.mark.parametrize("unit", UNITS, ids=lambda u: u["id"])
def test_unit_practices_references_and_main_exercise(unit):
    assert 4 <= len(unit["practices"]) <= 6
    assert all(p["text"] and p["why"] for p in unit["practices"])
    sources = MODULE["sources"]
    assert unit["references"], "cada unidad cita al menos una fuente"
    for reference in unit["references"]:
        source = sources[reference["source"]]
        # La normativa de FP no respalda conceptos de Python: solo aparece en el currículo
        assert source["kind"] == "python"
        assert source["url"].startswith("https://docs.python.org/es/3/")
        assert reference["section"] and reference["supports"]
        # Desde este entorno no se pueden abrir las fuentes: nada se presenta como comprobado
        assert reference["status"] == "pending"
    for section in unit["sections"]:
        for example in section["examples"]:
            assert example["origin"]["kind"] in {"original", "docs"}
    main = EXERCISES[unit["autonomous"][0]]
    assert main["kind"] == "code" and main["id"] in unit["pass"]["required"]
    assert all(EXERCISES[i]["kind"] == "code" for i in unit.get("extras", []))


def test_source_catalog_is_closed():
    assert set(MODULE["sources"]) == {
        "py-tutorial-classes",
        "py-faq-programming",
        "py-abc",
        "py-dataclasses",
        "rd-405-2023",
        "rd-659-2023",
    }


def test_validator_rejects_bad_bank_and_references(monkeypatch):
    builder = _load_builder()
    unit = next(c for c in builder.CONCEPTS if c["id"] == "poo")
    monkeypatch.setitem(unit, "bank", unit["bank"][:14])
    monkeypatch.setitem(
        unit,
        "references",
        [
            {
                "source": "rd-405-2023",
                "section": "Anexo I",
                "supports": ["clases"],
                "status": "pending",
            },
            {"source": "otra-web", "section": "x", "supports": ["y"], "status": "pending"},
            {
                "source": "py-faq-programming",
                "section": "x",
                "supports": ["y"],
                "status": "verified",
            },
        ],
    )
    monkeypatch.setitem(unit, "practices", unit["practices"][:2])
    quiet = {"output": "", "error": None, "passed": False}
    monkeypatch.setattr(builder, "execute", lambda *a, **k: quiet)
    problems = builder.Problems()
    builder.check_units(problems)
    assert any("exactamente 15 preguntas" in p for p in problems)
    assert any("la normativa de FP no respalda" in p for p in problems)
    assert any("fuera del catálogo" in p for p in problems)
    assert any("verified necesita quién" in p for p in problems)
    assert any("buenas prácticas son de 4 a 6" in p for p in problems)
    assert any("marcada bank pero fuera del banco" in p for p in problems)


def test_validator_checks_prediction_answers_against_the_real_output(monkeypatch):
    builder = _load_builder()
    question = next(e for e in builder.E if e["id"] == "poo1-15")
    wrong = {"output": "35 35\n", "error": None, "passed": False}
    monkeypatch.setattr(builder, "execute", lambda *a, **k: wrong)
    problems = builder.Problems()
    builder.check_units(problems)
    assert any(p.startswith(f"pregunta {question['id']}") and "salida real" in p for p in problems)
