# ruff: noqa: E501
# (datos de la demo: cada entrada en una sola línea para leerla de un vistazo)
"""Genera frontend/data/demo/alex.json: los datos FICTICIOS del modo demostración.

Alex Developer no existe. No hay email ni ningún dato personal: solo progreso de ejemplo con el
mismo formato que guarda la web en el navegador (pld:completed, pld:game, pld:learn, pld:pcap,
pld:planner, pld:course:<id>, pld:cybersecurity:v1). La web lo carga en sessionStorage con el
prefijo «pld:demo:» (frontend/js/demo/demo-mode.js) y nunca lo mezcla con el progreso real.

Las fechas giran alrededor de ANCHOR. Al entrar en la demo se desplazan para que ANCHOR sea hoy,
así que la racha, el historial y los repasos pendientes tienen siempre la misma forma.

El script comprueba que cada lección, concepto, ejercicio, pregunta y semana existe en los datos
reales, para que la demo no se rompa al cambiar el temario.

Uso:  python scripts/demo/build_demo.py           (genera)
      python scripts/demo/build_demo.py --check   (CI: falla si no está al día o no es válido)
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "frontend" / "data"
OUT = DATA / "demo" / "alex.json"

ANCHOR = date(2026, 11, 20)
NOTICE = "Datos ficticios del modo demostración. Alex Developer no es una persona real."

# ---------- Lo que ha hecho Alex ----------

# Curso PCAP de la web: 6 lecciones completadas; «funciones» y «colecciones», pendientes
COMPLETED = ["variables", "tipos", "operadores", "input", "condicionales", "bucles"]
READ = [*COMPLETED, "funciones"]
QUIZ = {"variables": 3, "tipos": 3, "operadores": 2, "input": 3, "condicionales": 2, "bucles": 2}
FIRST_TRY = ["variables", "input"]
TRIED = [*COMPLETED, "funciones"]  # el ejercicio de funciones está empezado y sin superar
BADGES = [
    "hola-mundo",
    "primer-ejercicio",
    "a-la-primera",
    "cazabugs",
    "quiz-perfecto",
    "constancia",
    "primer-simulacro",
]
# Días con actividad (hace N días): 6 seguidos hasta hoy y algunos sueltos antes
ACTIVE_DAYS_AGO = [0, 1, 2, 3, 4, 5, 8, 9, 11, 14, 18, 22]

# Núcleo por conceptos: dominio distinto en cada uno, para que el motor recomiende cosas distintas.
# (caja de repaso, hace cuántos días se vio, en cuántos días toca repasarlo, aciertos de cada ejercicio)
MASTERED = "todos"  # todos los ejercicios del concepto, acertados: concepto dominado
CONCEPTS = {
    "variables": (4, 5, 6, MASTERED),
    "tipos": (3, 4, 4, MASTERED),
    "operadores": (
        2,
        4,
        -1,
        {"ope-01": [True, True], "ope-02": [False, True], "ope-03": [True, False]},
    ),
    "entrada-salida": (1, 3, -2, {"es-01": [True], "es-02": [False]}),
    "condicionales": (2, 1, 2, {"con-01": [True, True], "con-02": [True], "con-03": [False, True]}),
    "bucles": (1, 0, 1, {"buc-01": [True], "buc-02": [False, False]}),
}
READ_ONLY_CONCEPTS = ["funciones"]

# Preparación del PCAP: 14 preguntas respondidas y un simulacro (62 %, sin aprobar todavía)
PCAP_ANSWERED = 14
PCAP_EXAM = {"days_ago": 2, "correct": 26, "total": 42, "seconds": 3540}

# Otros cursos: lecciones completadas (hace N días)
COURSES = {
    "js": {"js-variables": 9, "js-coercion": 8, "js-funciones": 4},
    "sql": {"bd-tipos-y-modelos": 14, "sql-modelo-relacional": 11},
    "programacion": {},
}
CYBER_WEEKS = {"semana-01": 3}  # semana completada y nota del cuestionario (sobre 3)

# Planificador: 45 min al día; tareas hechas o pospuestas estos días
PLANNER_TASKS = {
    1: {"condicionales": "hecha", "operadores": "hecha"},
    2: {"tipos": "hecha", "entrada-salida": "pospuesta"},
    3: {"variables": "hecha"},
    5: {"operadores": "hecha", "tipos": "hecha"},
}
PLANNER_EXAMS = [
    {
        "id": "demo-pcap",
        "title": "Examen PCAP (ejemplo)",
        "module": "pcap",
        "days_ahead": 40,
        "kind": "examen",
    }
]


def day(days_ago: int) -> str:
    return (ANCHOR - timedelta(days=days_ago)).isoformat()


def at(days_ago: int, hour: int = 18, minute: int = 0) -> str:
    """Hora de tarde en UTC: lejos de medianoche, el día local no cambia en Europa ni América."""
    moment = datetime.combine(ANCHOR - timedelta(days=days_ago), datetime.min.time(), UTC)
    return (moment + timedelta(hours=hour, minutes=minute)).isoformat().replace("+00:00", ".000Z")


def load(path: Path) -> dict:
    return json.loads(path.read_text("utf-8"))


def require(ids: list[str], known: set[str], what: str) -> None:
    missing = sorted(set(ids) - known)
    if missing:
        raise SystemExit(f"La demo usa {what} que no existen: {', '.join(missing)}")


def build() -> dict:
    lessons = load(DATA / "lessons.json")
    lesson_titles = {
        lesson["slug"]: lesson["title"]
        for module in lessons["modules"]
        for lesson in module["lessons"]
    }
    learning = load(DATA / "learning.json")
    concepts = {concept["id"] for concept in learning["concepts"]}
    exercises = {exercise["id"]: exercise["concept"] for exercise in learning["exercises"]}
    pcap = load(DATA / "pcap.json")
    cyber = load(DATA / "cybersecurity" / "course.json")

    require(
        [*COMPLETED, *READ, *QUIZ, *FIRST_TRY, *TRIED],
        set(lesson_titles),
        "lecciones del curso PCAP",
    )
    require([*CONCEPTS, *READ_ONLY_CONCEPTS], concepts, "conceptos")
    by_concept: dict[str, list[str]] = {}
    for exercise in learning["exercises"]:
        by_concept.setdefault(exercise["concept"], []).append(exercise["id"])
    histories = {
        concept: {
            ex: [False, True] if i == 1 else [True] for i, ex in enumerate(by_concept[concept])
        }
        if spec == MASTERED
        else spec
        for concept, (_box, _last, _due, spec) in CONCEPTS.items()
    }
    for concept, history in histories.items():
        require(list(history), set(exercises), "ejercicios")
        wrong = [ex for ex in history if exercises[ex] != concept]
        if wrong:
            raise SystemExit(f"Ejercicios fuera del concepto {concept}: {', '.join(wrong)}")
    for course, done in COURSES.items():
        course_lessons = load(DATA / "courses" / course / "lessons.json")
        require(
            list(done),
            {
                lesson["slug"]
                for module in course_lessons["modules"]
                for lesson in module["lessons"]
            },
            f"lecciones de {course}",
        )
    require(list(CYBER_WEEKS), {week["id"] for week in cyber["weeks"]}, "semanas de ciberseguridad")

    # ---- pld:learn (núcleo por conceptos) ----
    ex_state: dict[str, dict] = {}
    log: list[dict] = []
    concept_state: dict[str, dict] = {}
    for concept, (box, last, due, _spec) in CONCEPTS.items():
        history = histories[concept]
        concept_state[concept] = {
            "box": box,
            "due": day(-due),
            "last": at(last, 18, 30),
            "read": at(last + 1, 17),
            "placed": None,
        }
        for n, (ex, results) in enumerate(history.items()):
            when = at(last, 18, 10 + n * 5)
            entry = {"h": results, "last": when, "n": len(results)}
            if True in results:
                entry["okAt"] = when
            ex_state[ex] = entry
            log.extend({"at": when, "ex": ex, "ok": ok, "err": None} for ok in results)
    for concept in READ_ONLY_CONCEPTS:
        concept_state[concept] = {
            "box": 0,
            "due": None,
            "last": None,
            "read": at(0, 17, 40),
            "placed": None,
        }
    log.sort(key=lambda item: item["at"])

    # ---- pld:pcap ----
    questions = [question["id"] for question in pcap["questions"]][:PCAP_ANSWERED]
    answers = {qid: ([True, True] if i % 3 else [False, True]) for i, qid in enumerate(questions)}
    exam = PCAP_EXAM
    score = round(exam["correct"] * 100 / exam["total"])

    feed = []
    for days_ago, slug in zip([22, 18, 14, 11, 9, 5], COMPLETED, strict=True):
        feed.append(
            {
                "kind": "attempt",
                "lesson_slug": slug,
                "lesson_title": lesson_titles[slug],
                "passed": True,
                "at": at(days_ago, 17, 50),
            }
        )
        feed.append(
            {
                "kind": "lesson_completed",
                "lesson_slug": slug,
                "lesson_title": lesson_titles[slug],
                "passed": None,
                "at": at(days_ago, 18),
            }
        )
    feed.append(
        {
            "kind": "attempt",
            "lesson_slug": "funciones",
            "lesson_title": lesson_titles["funciones"],
            "passed": False,
            "at": at(0, 17, 45),
        }
    )
    feed.sort(key=lambda item: item["at"], reverse=True)

    storage = {
        "pld:completed": COMPLETED,
        "pld:game": {
            "quiz": QUIZ,
            "read": READ,
            "passed": COMPLETED,
            "tried": TRIED,
            "firstTry": FIRST_TRY,
            "challenges": [],
            "days": sorted(day(n) for n in ACTIVE_DAYS_AGO),
            "flags": {"firstRun": True, "bugHunter": True, "lastRunFailed": True},
            # Los logros que ya cumplen estos datos (game.js los calcula): así no se «desbloquean» al entrar
            "badges": BADGES,
        },
        "pld:learn": {
            "ex": ex_state,
            "concepts": concept_state,
            "errors": {},
            "log": log,
            "exams": [],
        },
        "pld:pcap": {
            "lang": "es",
            "answers": answers,
            "exams": [
                {
                    "date": at(exam["days_ago"], 19),
                    "correct": exam["correct"],
                    "total": exam["total"],
                    "score": score,
                    "seconds": exam["seconds"],
                    "blocks": {},
                }
            ],
            "known": [],
            "bestCombo": 7,
            "flags": {"mastered": False, "ready": False, "allCards": False},
            "srs": {},
            "plan": {"examDate": day(-40)},
        },
        "pld:planner": {
            "v": 1,
            "minutes": 45,
            "minutesAt": at(20),
            "exams": [
                {
                    "id": e["id"],
                    "title": e["title"],
                    "module": e["module"],
                    "date": day(-e["days_ahead"]),
                    "kind": e["kind"],
                    "at": at(20),
                }
                for e in PLANNER_EXAMS
            ],
            "days": {
                day(n): {c: {"status": s, "at": at(n, 18, 45)} for c, s in tasks.items()}
                for n, tasks in PLANNER_TASKS.items()
            },
        },
        "pld:cybersecurity:v1": {
            "v": 2,
            "weeks": {week: {"done": True, "at": at(6, 19)} for week in CYBER_WEEKS},
            "quiz": {
                week: {"score": score_, "at": at(6, 19, 15)} for week, score_ in CYBER_WEEKS.items()
            },
        },
    }
    for course, done in COURSES.items():
        if not done:
            continue
        last_slug = min(done, key=done.get)
        storage[f"pld:course:{course}"] = {
            "lang": "es",
            "done": {slug: at(n, 19) for slug, n in done.items()},
            "lastLesson": {"slug": last_slug, "at": at(done[last_slug], 19, 5)},
        }

    return {
        "notice": NOTICE,
        "anchor": ANCHOR.isoformat(),
        "profile": {"display_name": "Alex Developer", "created_at": at(30, 10), "fictional": True},
        "feed": feed,
        "storage": storage,
    }


def main() -> None:
    text = json.dumps(build(), ensure_ascii=False, indent=1) + "\n"
    if "--check" in sys.argv:
        if not OUT.exists() or OUT.read_text("utf-8") != text:
            raise SystemExit(
                f"{OUT.relative_to(ROOT)} no está al día: ejecuta python scripts/demo/build_demo.py"
            )
        print(f"{OUT.relative_to(ROOT)} al día")
        return
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, "utf-8", newline="\n")  # LF también en Windows
    print(f"Generado {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
