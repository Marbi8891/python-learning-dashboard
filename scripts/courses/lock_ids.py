"""Identificadores estables de los cursos de DAW (ids.lock.json).

El progreso del alumno se guarda por id: las respuestas de cada pregunta (`answers[id]`), las
lecciones completadas (`done`, por slug) y la última lección (`lastLesson`). Si un id desaparece o
cambia, el alumno pierde ese progreso sin aviso. Por eso backend/tests/test_daw_courses.py
comprueba que todo id de este archivo sigue existiendo.

Uso:
    python scripts/courses/lock_ids.py           # añade al registro los ids nuevos (nunca quita)
    python scripts/courses/lock_ids.py --check   # falla si hay ids nuevos sin registrar

Los itinerarios de la academia (frontend/data/academia, como Excel profesional) tienen su propio
registro, academia.lock.json, que comprueba backend/tests/test_excel_course.py.

Para quitar o renombrar un id hace falta un plan de migración (por ejemplo, copiar el progreso del
id antiguo al nuevo al cargar el curso). Entonces se edita este registro a mano en el mismo PR.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COURSES = ROOT / "frontend" / "data" / "courses"
LOCK = Path(__file__).with_name("ids.lock.json")
ACADEMY = ROOT / "frontend" / "data" / "academia"
ACADEMY_LOCK = Path(__file__).with_name("academia.lock.json")
REGISTRIES = ((COURSES, LOCK), (ACADEMY, ACADEMY_LOCK))


def current_ids(courses: Path = COURSES) -> dict[str, dict[str, list[str]]]:
    ids = {}
    for folder in sorted(p for p in courses.iterdir() if p.is_dir()):
        lessons = json.loads((folder / "lessons.json").read_text("utf-8"))["modules"]
        bank = json.loads((folder / "bank.json").read_text("utf-8"))
        ids[folder.name] = {
            "units": [unit["slug"] for unit in lessons],
            "lessons": [lesson["slug"] for unit in lessons for lesson in unit["lessons"]],
            "questions": [question["id"] for question in bank["questions"]],
        }
    return ids


def merged(locked: dict, now: dict) -> dict:
    """El registro solo crece: lo nuevo se añade al final y lo registrado no se toca."""
    result = {
        course: {kind: list(values) for kind, values in kinds.items()}
        for course, kinds in locked.items()
    }
    for course, kinds in now.items():
        target = result.setdefault(course, {})
        for kind, values in kinds.items():
            known = target.setdefault(kind, [])
            known.extend(v for v in values if v not in known)
    return result


def main() -> int:
    status = 0
    for courses, lock in REGISTRIES:
        locked = json.loads(lock.read_text("utf-8")) if lock.exists() else {}
        updated = merged(locked, current_ids(courses))
        total = sum(len(v) for k in updated.values() for v in k.values())
        if "--check" in sys.argv:
            if updated != locked:
                print(
                    f"{lock.name}: hay ids nuevos sin registrar:"
                    " ejecuta python scripts/courses/lock_ids.py"
                )
                status = 1
            else:
                print(f"{lock.name} al día: {total} ids")
            continue
        lock.write_text(
            json.dumps(updated, ensure_ascii=False, indent=1) + "\n", "utf-8", newline="\n"
        )
        print(f"{lock.name}: {total} ids")
    return status


if __name__ == "__main__":
    sys.exit(main())
