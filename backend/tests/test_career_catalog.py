"""Catálogo de itinerarios profesionales (frontend/data/career/*.json, DEC-012).

Lo genera y valida scripts/career/build_career.py. Estas pruebas comprueban que el JSON publicado
está al día y que el validador detecta los errores típicos al ampliar el itinerario.
"""

import copy
import importlib.util
import json
from types import SimpleNamespace

from app.config import FRONTEND_DIR

SCRIPT = FRONTEND_DIR.parent / "scripts" / "career" / "build_career.py"
spec = importlib.util.spec_from_file_location("build_career", SCRIPT)
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)

ROADMAP = json.loads((FRONTEND_DIR / "data" / "career" / "applied-ai-engineer.json").read_text())
REFS = builder.known_references()
FIELDS = (
    "ID VERSION TITLE SPECIALIZATION LEVELS CATEGORIES SALARY_SOURCE SALARY_BANDS DEFAULT_TARGET "
    "STAGES SKILLS PROJECTS CHECKLISTS ROLES MODULES"
).split()


def itinerary():
    """Copia editable del itinerario real."""
    return SimpleNamespace(**{f: copy.deepcopy(getattr(builder.applied_ai, f)) for f in FIELDS})


def problems_of(data) -> list[str]:
    problems = builder.Problems()
    builder.build(data, REFS, problems)
    return problems


def find(items, id_):
    return next(item for item in items if item["id"] == id_)


def test_published_catalog_is_valid_and_up_to_date():
    problems = builder.Problems()
    files, ids = builder.outputs(problems)
    assert problems == []
    for path, content in files.items():
        assert path.read_text("utf-8") == content, f"{path.name} no está al día"
    assert builder.merged_lock(builder.locked_ids(), ids) == builder.locked_ids()


def test_roadmap_has_the_eight_modules_and_the_four_levels():
    assert [m["id"] for m in ROADMAP["modules"]] == [f"m{i}" for i in range(1, 9)]
    assert [lv["id"] for lv in ROADMAP["levels"]] == [
        "fundamentos",
        "intermedio",
        "avanzado",
        "profesional",
    ]
    assert sum(s["months"] for s in ROADMAP["stages"]) == 36
    assert {r["id"] for r in ROADMAP["roles"]} >= {"applied-ai-engineer", "llm-engineer"}


def test_every_skill_needs_an_evaluable_source():
    """Leer una lección no puede subir una competencia: siempre hay evaluación o práctica."""
    for skill in ROADMAP["skills"]:
        sources = skill["sources"]
        assert sources["concepts"] or sources["blocks"] or sources["assessments"], skill["id"]
    data = itinerary()
    s = find(data.SKILLS, "py-async")
    s["sources"]["assessments"] = []
    assert any("sin fuente evaluable" in p for p in problems_of(data))


def test_risk_engine_is_not_linked_to_any_repository():
    """D7 pendiente: no se asocia a ARGOS ni a otro repositorio hasta que el autor lo confirme."""
    risk = find(ROADMAP["projects"], "nexaro-risk-engine")
    assert risk["repo"] is None and risk["pendingIdentity"] is True


def test_detects_broken_references():
    data = itinerary()
    find(data.MODULES, "m1")["units"][0]["links"].append({"kind": "concept", "id": "no-existe"})
    find(data.SKILLS, "sql")["sources"]["blocks"].append("sql:no-existe")
    find(data.ROLES, "llm-engineer")["skills"]["inventada"] = 0.5
    find(data.MODULES, "m2")["project"]["criteria"].append("no-existe")
    found = problems_of(data)
    assert any("enlace inexistente concept:no-existe" in p for p in found)
    assert any("bloque inexistente sql:no-existe" in p for p in found)
    assert any("competencia inexistente inventada" in p for p in found)
    assert any("criterio inexistente no-existe" in p for p in found)


def test_detects_prerequisite_cycles_and_invalid_prerequisites():
    data = itinerary()
    find(data.MODULES, "m1")["requires"] = ["m5"]
    find(data.MODULES, "m3")["requires"] = ["m3"]
    found = problems_of(data)
    assert any("ciclo de prerrequisitos" in p for p in found)
    assert any("prerrequisito inválido m3" in p for p in found)


def test_detects_duplicated_or_malformed_ids():
    data = itinerary()
    units = find(data.MODULES, "m1")["units"]
    units.append(copy.deepcopy(units[0]))
    units[1]["id"] = "M1 Errores"
    found = problems_of(data)
    assert any("id repetido: m1.poo" in p for p in found)
    assert any("formato inválido" in p for p in found)


def test_detects_incomplete_units_skills_and_stages():
    data = itinerary()
    m1 = find(data.MODULES, "m1")
    m1["units"][0].update(level="experto", objectives=[], skills=[])
    m1["units"][1].update(pending=False, links=[])
    m1["units"][2]["id"] = "m2.git"
    m1["assessment"]["pass"] = 0
    data.STAGES[0]["months"] = 0
    for stage in data.STAGES:
        stage["modules"] = [m for m in stage["modules"] if m != "m8"]
    found = problems_of(data)
    for text in (
        "nivel desconocido experto",
        "sin objetivos",
        "sin competencias",
        "no enlaza a nada",
        "debe empezar por «m1.»",
        "evaluación mal definida",
        "duración fuera de 1-24 meses",
        "módulo m8: no está en ninguna etapa",
    ):
        assert any(text in p for p in found), text


def test_detects_inconsistent_skills_criteria_and_roles():
    data = itinerary()
    find(data.SKILLS, "sql")["category"] = "magia"
    find(data.SKILLS, "sql")["title"] = {"es": "SQL"}
    # El criterio y la competencia deben declararse mutuamente
    find(data.SKILLS, "py-async")["sources"]["criteria"] = ["npa-rag-eval"]
    find(find(data.PROJECTS, "jobradar")["criteria"], "jr-conectores")["skills"].append("sql")
    find(data.ROLES, "llm-engineer").update(band="becario")
    find(data.ROLES, "llm-engineer")["skills"]["llm-evaluation"] = 1.5
    data.SALARY_BANDS[0]["max"] = 1000
    find(data.PROJECTS, "jobradar")["repo"] = "http://ejemplo.org"
    find(data.SKILLS, "py-async")["sources"]["concepts"] = ["no-existe"]
    find(data.SKILLS, "py-async")["sources"]["assessments"] = ["m9"]
    find(data.SKILLS, "py-async")["sources"]["checklists"] = ["no-existe"]
    find(data.MODULES, "m8")["project"]["checklists"] = ["no-existe"]
    found = problems_of(data)
    for text in (
        "categoría desconocida magia",
        "texto sin «es» y «en»",
        "el criterio npa-rag-eval no declara esta competencia",
        "la competencia sql no lo declara como fuente",
        "banda inexistente becario",
        "objetivo fuera de (0, 1]",
        "importes inválidos",
        "el repositorio debe ser https",
        "concepto inexistente no-existe",
        "evaluación inexistente m9",
        "lista inexistente no-existe",
    ):
        assert any(text in p for p in found), text


def test_detects_skills_no_unit_trains_and_criteria_of_unknown_modules():
    data = itinerary()
    for module in data.MODULES:
        for unit in module["units"]:
            unit["skills"] = [s for s in unit["skills"] if s != "py-async"] or ["py-oop"]
    criterion = find(find(data.PROJECTS, "jobradar")["criteria"], "jr-conectores")
    criterion["module"] = "m9"
    criterion["skills"].append("inventada")
    find(data.MODULES, "m4")["requires"] = ["m9"]
    find(data.MODULES, "m4")["units"] = []
    data.STAGES[0]["modules"].append("m9")
    found = problems_of(data)
    for text in (
        "competencia py-async: ninguna unidad la trabaja",
        "módulo inexistente m9",
        "competencia inexistente inventada",
        "prerrequisito inválido m9",
        "sin unidades",
    ):
        assert any(text in p for p in found), text


def test_lock_only_grows(tmp_path, monkeypatch, capsys):
    """Un id registrado que desaparece rompe el progreso guardado: el validador lo rechaza."""
    lock = tmp_path / "ids.lock.json"
    locked = builder.locked_ids()
    locked["applied-ai-engineer:units"] = [*locked["applied-ai-engineer:units"], "m1.borrada"]
    lock.write_text(json.dumps(locked))
    monkeypatch.setattr(builder, "LOCK", lock)
    assert builder.main(["--check"]) == 1
    assert "m1.borrada" in capsys.readouterr().err


def test_check_fails_when_output_is_stale_or_ids_are_unregistered(tmp_path, monkeypatch, capsys):
    lock = tmp_path / "ids.lock.json"
    monkeypatch.setattr(builder, "OUT", tmp_path / "career")
    monkeypatch.setattr(builder, "LOCK", lock)
    assert builder.main(["--check"]) == 1
    assert "No está al día" in capsys.readouterr().err

    assert builder.main([]) == 0  # genera en la carpeta temporal y crea el lock temporal
    assert builder.main(["--check"]) == 0
    lock.write_text(json.dumps({"roadmaps": ["applied-ai-engineer"]}))
    assert builder.main(["--check"]) == 1
    assert "ids nuevos sin registrar" in capsys.readouterr().err
