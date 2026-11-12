"""Calidad y coherencia de los cursos de DAW (frontend/data/courses/*), Fase D 6.4.

Los generadores (scripts/courses/<curso>_course.py --check) ya ejecutan cada respuesta de código.
Aquí se comprueba lo que no depende de ejecutar nada:

- Identificadores estables: el progreso del alumno se guarda por id (scripts/courses/ids.lock.json).
- Ningún contenido vacío y ninguna pregunta repetida dentro de un curso.
- Opciones bien formadas: sin repetir y con la respuesta dentro de la lista.
- Referencias: cada pregunta apunta a una unidad y una lección de su curso, y a un módulo del
  currículo. Los objetivos que citan un RA y sus criterios («RA2 a, d») citan unos que existen.
- Enlaces: los de las fuentes son https, y los enlaces internos llevan a rutas que existen.
- Soluciones: las que se publican no están vacías y su lección tiene ejercicio.
"""

import json
import re
from pathlib import Path

import pytest

from app.config import FRONTEND_DIR

COURSES_DIR = FRONTEND_DIR / "data" / "courses"
LOCK = Path(__file__).resolve().parents[2] / "scripts" / "courses" / "ids.lock.json"
CATALOG = json.loads((FRONTEND_DIR / "data" / "curriculum" / "daw-cyl.json").read_text("utf-8"))
OUTCOMES = {
    ra["id"]: {c["id"].rsplit("-", 1)[1] for c in ra["criteria"]}
    for module in CATALOG["modules"]
    for ra in module.get("learningOutcomes", [])
}


def load(course: str) -> tuple[list[dict], dict]:
    units = json.loads((COURSES_DIR / course / "lessons.json").read_text("utf-8"))["modules"]
    bank = json.loads((COURSES_DIR / course / "bank.json").read_text("utf-8"))
    return units, bank


COURSES = sorted(p.name for p in COURSES_DIR.iterdir() if p.is_dir())
DATA = {course: load(course) for course in COURSES}


def text(value) -> str:
    """Los textos del banco van por idioma ({"es": …, "en": …}); los de las lecciones, tal cual."""
    if isinstance(value, dict):
        return value.get("es") or ""
    return value or ""


def lessons_of(course: str) -> list[dict]:
    return [lesson for unit in DATA[course][0] for lesson in unit["lessons"]]


def module_of(course: str) -> str:
    return next(m["code"] for m in CATALOG["modules"] if course in m.get("platformCourses", []))


def test_every_course_is_registered():
    assert COURSES == ["entornos", "java", "js", "marcas", "programacion", "sql"]


def test_locked_ids_still_exist():
    """Un id registrado que desaparece borraría el progreso guardado con él sin avisar."""
    locked = json.loads(LOCK.read_text("utf-8"))
    for course, kinds in locked.items():
        units, bank = DATA[course]
        now = {
            "units": {u["slug"] for u in units},
            "lessons": {lesson["slug"] for u in units for lesson in u["lessons"]},
            "questions": {q["id"] for q in bank["questions"]},
        }
        for kind, ids in kinds.items():
            lost = [i for i in ids if i not in now[kind]]
            assert not lost, (
                f"{course}: {kind} que ya no existen (hace falta un plan de migración): {lost}"
            )


def test_new_ids_are_registered():
    locked = json.loads(LOCK.read_text("utf-8"))
    for course in COURSES:
        registered = set(locked.get(course, {}).get("questions", []))
        new = [q["id"] for q in DATA[course][1]["questions"] if q["id"] not in registered]
        assert not new, (
            f"{course}: ids nuevos sin registrar; ejecuta scripts/courses/lock_ids.py: {new[:5]}"
        )


@pytest.mark.parametrize("course", COURSES)
def test_ids_are_unique(course):
    units, bank = DATA[course]
    for ids in (
        [u["slug"] for u in units],
        [lesson["slug"] for lesson in lessons_of(course)],
        [q["id"] for q in bank["questions"]],
    ):
        assert len(ids) == len(set(ids))


@pytest.mark.parametrize("course", COURSES)
def test_lessons_have_no_empty_content(course):
    for lesson in lessons_of(course):
        for field in ("title", "theory", "example_code", "exercise", "starter"):
            assert text(lesson.get(field)).strip(), f"{lesson['slug']}: «{field}» vacío"
        challenge = lesson["challenge"]
        assert challenge["exercise"].strip() and challenge["starter"].strip(), (
            f"{lesson['slug']}: reto vacío"
        )
        assert lesson["sources"], f"{lesson['slug']}: sin fuentes"
        for item in lesson["quiz"]:
            options = [text(o).strip() for o in item["options"]]
            assert text(item["q"]).strip() and text(item["explain"]).strip(), lesson["slug"]
            assert all(options) and len(set(options)) == len(options), (
                f"{lesson['slug']}: opciones vacías o repetidas"
            )
            assert 0 <= item["answer"] < len(options), lesson["slug"]


@pytest.mark.parametrize("course", COURSES)
def test_questions_are_well_formed_and_not_repeated(course):
    seen = {}
    for q in DATA[course][1]["questions"]:
        statement, explain = text(q["q"]).strip(), text(q["explain"]).strip()
        assert statement and explain, f"{q['id']}: enunciado o explicación vacíos"
        if q.get("kind") == "fill":
            assert q.get("accept") and all(a.strip() for a in q["accept"]), (
                f"{q['id']}: hueco sin respuestas aceptadas"
            )
        elif q.get("kind") == "order":
            assert len(q.get("lines", [])) >= 2, f"{q['id']}: ordenar sin líneas"
        else:
            options = [text(o).strip() for o in q["options"]]
            assert len(options) >= 2 and all(options), f"{q['id']}: opciones"
            # En «¿Qué línea tiene el error?» las opciones son líneas: «}» puede repetirse
            if "qué línea" not in statement.lower():
                assert len(set(options)) == len(options), f"{q['id']}: opciones repetidas"
            answers = (
                q["answer"] if isinstance(q["answer"], list) else [q["answer"]]
            )  # «elige dos»: lista
            assert answers and len(set(answers)) == len(answers), (
                f"{q['id']}: respuestas vacías o repetidas"
            )
            assert all(0 <= a < len(options) for a in answers), (
                f"{q['id']}: respuesta fuera de las opciones"
            )
        key = (re.sub(r"\s+", " ", statement.lower()), (q.get("code") or "").strip())
        assert key not in seen, f"{q['id']} repite la pregunta {seen.get(key)}"
        seen[key] = q["id"]


@pytest.mark.parametrize("course", COURSES)
def test_questions_point_to_their_unit_lesson_and_module(course):
    units, bank = DATA[course]
    unit_slugs = {u["slug"] for u in units}
    lesson_slugs = {lesson["slug"] for lesson in lessons_of(course)}
    modules = {m["code"] for m in CATALOG["modules"]}
    for q in bank["questions"]:
        assert q["block"] in unit_slugs, f"{q['id']}: unidad «{q['block']}» inexistente"
        assert q["lesson"] in lesson_slugs, f"{q['id']}: lección «{q['lesson']}» inexistente"
        assert q["module"] in modules, f"{q['id']}: módulo «{q['module']}» fuera del currículo"
    exam_blocks = {b["slug"] for b in bank["exam"]["blocks"]}
    assert exam_blocks <= unit_slugs


# «(RA2 a, d)», «(RA1 a-f)», «(RA4)»: un RA y, si acaso, letras o rangos de criterios
CITATION = re.compile(r"\bRA ?(\d+)((?: ?[a-z](?:-[a-z])?,?)*)(?=[).;\s])")


def cited_criteria(letters: str) -> list[str]:
    result = []
    for part in re.findall(r"[a-z](?:-[a-z])?", letters):
        start, _, end = part.partition("-")
        result.extend(chr(c) for c in range(ord(start), ord(end or start) + 1))
    return result


def test_citation_parser():
    found = [
        (m.group(1), cited_criteria(m.group(2)))
        for m in CITATION.finditer("Hacer X (RA1 a-c). Y (RA2 b, d). Z (RA4).")
    ]
    assert found == [("1", ["a", "b", "c"]), ("2", ["b", "d"]), ("4", [])]


@pytest.mark.parametrize("course", COURSES)
def test_cited_outcomes_and_criteria_exist(course):
    """Un objetivo que cita «RA6 e» tiene que citar un RA y un criterio del módulo que existan."""
    module = module_of(course)
    for lesson in lessons_of(course):
        for line in lesson.get("objectives", []):
            for match in CITATION.finditer(line):
                outcome = f"{module}-RA{match.group(1)}"
                assert outcome in OUTCOMES, f"{lesson['slug']}: cita {outcome}, que no existe"
                missing = set(cited_criteria(match.group(2))) - OUTCOMES[outcome]
                assert not missing, (
                    f"{lesson['slug']}: {outcome} no tiene los criterios {sorted(missing)}"
                )


INTERNAL_ROUTE = re.compile(
    r"#/(?:daw(?:/cursos|/curriculo(?:/\d{4})?|/(?P<course>[a-z]+)(?:/leccion/(?P<lesson>[\w-]+)|/practica/[\w-]+)?)?"
    r"|aprender|teoria(?:/[\w-]+)?|practicar|pcap(?:/[\w/-]+)?|leccion/[\w-]+|inicio|progreso|panel(?:/[\w-]+)?)$"
)


@pytest.mark.parametrize("course", COURSES)
def test_links_are_https_or_known_routes(course):
    lessons = lessons_of(course)
    blob = json.dumps(DATA[course], ensure_ascii=False)
    for lesson in lessons:
        for source in lesson["sources"]:
            assert source["url"].startswith("https://"), f"{lesson['slug']}: {source['url']}"
            assert source["title"].strip()
    for url in re.findall(r"\]\(([^)\s]+)\)", blob):
        if url.startswith("#"):
            match = INTERNAL_ROUTE.match(url)
            assert match, f"{course}: enlace interno a una ruta que no existe: {url}"
            if match.group("lesson"):
                target = match.group("course")
                assert match.group("lesson") in {lesson["slug"] for lesson in lessons_of(target)}, (
                    url
                )
        else:
            assert url.startswith("https://"), f"{course}: enlace sin https: {url}"


@pytest.mark.parametrize("course", COURSES)
def test_published_solutions_are_complete(course):
    for lesson in lessons_of(course):
        solution = lesson.get("solution")
        if solution is None:
            continue
        assert solution["code"].strip() and solution["explain"].strip(), (
            f"{lesson['slug']}: solución vacía"
        )
        assert lesson["exercise"].strip(), f"{lesson['slug']}: solución sin ejercicio"
        assert solution["code"].strip() != lesson["starter"].strip(), (
            f"{lesson['slug']}: la solución es la plantilla"
        )


# ---------- Correspondencia con los RA y CE oficiales (#106, curriculum_map.py) ----------

STATUSES = {"verified", "proposed", "unassigned"}
CRITERIA = {f"{ra}-{letter}" for ra, letters in OUTCOMES.items() for letter in letters}


def check_mapping(where: str, ce: list[str], status: str, module: str) -> None:
    assert status in STATUSES, f"{where}: estado «{status}» desconocido"
    assert (status == "unassigned") == (not ce), f"{where}: «unassigned» va sin CE, y solo él"
    assert len(set(ce)) == len(ce), f"{where}: CE repetido"
    for ce_id in ce:
        assert ce_id in CRITERIA, f"{where}: {ce_id} no existe en el currículo oficial"
        assert ce_id.startswith(f"{module}-"), f"{where}: {ce_id} no es del módulo {module}"


@pytest.mark.parametrize("course", COURSES)
def test_lessons_map_to_existing_criteria_of_their_module(course):
    module = module_of(course)
    for lesson in lessons_of(course):
        cur = lesson["curriculum"]
        check_mapping(lesson["slug"], cur["ce"], cur["status"], module)
        assert cur["ra"] == sorted({c.rsplit("-", 1)[0] for c in cur["ce"]}), lesson["slug"]
        assert cur["source"], f"{lesson['slug']}: la correspondencia no dice de dónde sale"
        # Verificado = lo ha revisado un docente: tiene que constar quién y cuándo
        assert bool(cur["reviewed"]) == (cur["status"] == "verified"), lesson["slug"]


@pytest.mark.parametrize("course", COURSES)
def test_every_question_has_a_mapping_consistent_with_its_lesson(course):
    lessons = {lesson["slug"]: lesson["curriculum"] for lesson in lessons_of(course)}
    for q in DATA[course][1]["questions"]:
        cur = q["curriculum"]
        check_mapping(q["id"], cur["ce"], cur["status"], q["module"])
        # Una pregunta no puede estar más verificada que su lección si hereda sus CE
        if cur["ce"] == lessons[q["lesson"]]["ce"]:
            assert cur["status"] == lessons[q["lesson"]]["status"], q["id"]


@pytest.mark.parametrize("course", COURSES)
def test_criteria_cited_in_objectives_are_in_the_mapping(course):
    """Si un objetivo cita «RA2 a, d», la correspondencia de la lección incluye esos CE."""
    module = module_of(course)
    for lesson in lessons_of(course):
        mapped = set(lesson["curriculum"]["ce"])
        for line in lesson.get("objectives", []):
            for match in CITATION.finditer(line):
                cited = {f"{module}-RA{match.group(1)}-{x}" for x in cited_criteria(match.group(2))}
                assert cited <= mapped, f"{lesson['slug']}: faltan {sorted(cited - mapped)}"


def test_every_question_is_mapped_to_some_criterion():
    """Las 520 preguntas tienen algún CE (hoy todos «proposed»: ningún docente lo ha revisado)."""
    statuses = {
        q["curriculum"]["status"] for course in COURSES for q in DATA[course][1]["questions"]
    }
    assert statuses <= STATUSES
    assert "unassigned" not in statuses, "hay preguntas sin correspondencia con ningún CE"
