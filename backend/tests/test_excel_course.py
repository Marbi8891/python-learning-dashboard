"""Calidad y coherencia de Excel profesional (frontend/data/academia/excel/), M01-M05.

El generador (scripts/courses/excel_course.py --check) ya comprueba con el motor de fórmulas cada
ejemplo y cada ejercicio de fórmula, y los mínimos de cada unidad. Aquí se comprueba lo que no
depende del motor, como en test_daw_courses.py para los cursos de DAW:

- Identificadores estables (scripts/courses/academia.lock.json): el progreso se guarda por id.
- Volumen: 15 unidades y 190 ejercicios (CURRICULUM_M1_M2.md §8 y CURRICULUM_M3_M5.md §4).
- Ningún contenido vacío, ninguna pregunta repetida y opciones bien formadas y barajadas.
- Sin módulo oficial de DAW: el curso no se cuela en el currículo ni en los paneles de DAW.
- Fuentes https con fecha y enlaces internos a rutas que existen.
"""

import json
import re
from pathlib import Path

from app.config import FRONTEND_DIR

FOLDER = FRONTEND_DIR / "data" / "academia" / "excel"
LOCK = Path(__file__).resolve().parents[2] / "scripts" / "courses" / "academia.lock.json"
UNITS = json.loads((FOLDER / "lessons.json").read_text("utf-8"))["modules"]
BANK = json.loads((FOLDER / "bank.json").read_text("utf-8"))
LESSONS = [lesson for unit in UNITS for lesson in unit["lessons"]]
KINDS = {"choice", "formula-result", "formula"}


def text(value) -> str:
    return value.get("es", "") if isinstance(value, dict) else value or ""


def test_volume():
    assert [u["slug"] for u in UNITS] == ["xl-m01", "xl-m02", "xl-m03", "xl-m04", "xl-m05"]
    assert sum(b["weight"] for b in BANK["exam"]["blocks"]) == 100
    assert len(LESSONS) == 15
    kinds = [q.get("kind", "choice") for q in BANK["questions"]]
    assert len(kinds) == 190
    assert (kinds.count("choice"), kinds.count("formula-result"), kinds.count("formula")) == (
        98,
        59,
        33,
    )
    assert BANK["engine"], "falta la versión del motor que comprobó los ejercicios"


def test_locked_ids_still_exist_and_new_ones_are_registered():
    locked = json.loads(LOCK.read_text("utf-8"))["excel"]
    now = {
        "units": [u["slug"] for u in UNITS],
        "lessons": [lesson["slug"] for lesson in LESSONS],
        "questions": [q["id"] for q in BANK["questions"]],
    }
    for kind, ids in now.items():
        assert len(ids) == len(set(ids)), f"{kind} repetidos"
        lost = [i for i in locked[kind] if i not in ids]
        assert not lost, f"{kind} que ya no existen (hace falta un plan de migración): {lost}"
        new = [i for i in ids if i not in locked[kind]]
        assert not new, f"ids nuevos sin registrar; ejecuta scripts/courses/lock_ids.py: {new[:5]}"


def test_units_follow_the_template():
    for lesson in LESSONS:
        slug, excel = lesson["slug"], lesson["excel"]
        assert lesson["title"].strip() and lesson["theory"].strip(), slug
        assert len(lesson["objectives"]) >= 3 and len(lesson["mistakes"]) >= 3, slug
        assert lesson["summary"] and excel["examples"] and excel["case"]["text"].strip(), slug
        assert excel["hours"] > 0 and excel["level"] in (1, 2, 3), slug
        assert excel["guided"]["steps"], slug
        assert "module" not in lesson and "curriculum" not in lesson, f"{slug}: no es de DAW"


def test_questions_are_well_formed_and_not_repeated():
    lessons = {lesson["slug"] for lesson in LESSONS}
    seen = {}
    for q in BANK["questions"]:
        kind = q.get("kind", "choice")
        assert kind in KINDS, q["id"]
        assert text(q["q"]).strip() and text(q["explain"]).strip(), q["id"]
        assert q["lesson"] in lessons and q["block"] in {u["slug"] for u in UNITS}, q["id"]
        assert "module" not in q, f"{q['id']}: una academia no tiene módulo oficial de DAW"
        if kind == "choice":
            options = [text(o).strip() for o in q["options"]]
            assert len(options) >= 3 and len(set(options)) == len(options), q["id"]
            assert len(q["answer"]) == 1 and 0 <= q["answer"][0] < len(options), q["id"]
        else:
            assert q["excel"]["grid"] is not None, q["id"]
        if kind == "formula":
            excel = q["excel"]
            assert excel["solution"]["formula"].startswith("="), q["id"]
            assert excel["hints"] and excel["mistakes"] and excel["checks"], q["id"]
        key = (
            re.sub(r"\s+", " ", text(q["q"]).lower()),
            json.dumps(q.get("excel", {}).get("formula")),
            json.dumps(q.get("excel", {}).get("grid"), sort_keys=True),
        )
        assert key not in seen, f"{q['id']} repite la pregunta {seen.get(key)}"
        seen[key] = q["id"]


def test_the_right_answer_is_not_always_in_the_same_place():
    """Las opciones se barajan con una semilla fija (scripts/courses/excel/units.py, shuffled)."""
    positions = [q["answer"][0] for q in BANK["questions"] if q.get("kind", "choice") == "choice"]
    for position in set(positions):
        assert positions.count(position) < len(positions) / 2, f"la respuesta {position} domina"
    assert len(set(positions)) >= 3


def test_required_exercises_and_guided_exercise_belong_to_their_unit():
    by_id = {q["id"]: q for q in BANK["questions"]}
    for lesson in LESSONS:
        excel = lesson["excel"]
        assert by_id[excel["guided"]["question"]]["lesson"] == lesson["slug"]
        for qid in excel["pass"]["required"]:
            assert by_id[qid]["lesson"] == lesson["slug"] and by_id[qid]["kind"] == "formula", qid


def test_sources_are_https_and_dated_and_internal_links_exist():
    slugs = {lesson["slug"] for lesson in LESSONS}
    for lesson in LESSONS:
        assert lesson["sources"], lesson["slug"]
        for source in lesson["sources"]:
            assert source["url"].startswith("https://"), source["url"]
            assert "consultado el" in source["title"], source["title"]
    blob = json.dumps({"units": UNITS, "bank": BANK}, ensure_ascii=False)
    for url in re.findall(r"\]\(([^)\s]+)\)", blob):
        if url.startswith("#"):
            match = re.fullmatch(r"#/academia/excel(?:/([\w-]+)(?:/practica)?)?", url)
            assert match and (match.group(1) in (None, "repaso") or match.group(1) in slugs), url
        else:
            assert url.startswith("https://"), url


def test_excel_is_not_a_daw_course():
    """La carpeta de los cursos de DAW sigue siendo solo de DAW (RF-23)."""
    assert not (FRONTEND_DIR / "data" / "courses" / "excel").exists()
