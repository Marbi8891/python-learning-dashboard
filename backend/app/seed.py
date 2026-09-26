"""Carga frontend/data/lessons.json (ruta configurable con LESSONS_FILE) en la base de datos.

Es idempotente: crea lo que falta y actualiza lo que ya existe (por slug).
Uso (desde la carpeta backend):
    python -m app.seed
"""

import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import SessionLocal
from app.models import Lesson, Module


def seed(db: Session, data_file: Path | None = None) -> int:
    """Sincroniza módulos y lecciones. Devuelve el número de lecciones procesadas."""
    path = data_file or get_settings().lessons_file
    data = json.loads(path.read_text(encoding="utf-8"))

    # Cargar lo existente de una vez, en memoria, en vez de consultar dentro del bucle
    modules = {m.slug: m for m in db.scalars(select(Module))}
    lessons = {lesson.slug: lesson for lesson in db.scalars(select(Lesson))}

    count = 0
    for m_pos, m_data in enumerate(data["modules"], start=1):
        module = modules.get(m_data["slug"]) or Module(slug=m_data["slug"])
        module.title = m_data["title"]
        module.position = m_pos
        db.add(module)

        for l_pos, l_data in enumerate(m_data["lessons"], start=1):
            lesson = lessons.get(l_data["slug"]) or Lesson(slug=l_data["slug"])
            lesson.module = module
            lesson.title = l_data["title"]
            lesson.position = l_pos
            lesson.theory = l_data.get("theory")
            lesson.example_code = l_data.get("example_code")
            lesson.exercise = l_data.get("exercise")
            lesson.sources = l_data.get("sources", [])
            lesson.starter = l_data.get("starter")
            lesson.example_stdin = l_data.get("example_stdin", "")
            lesson.exercise_stdin = l_data.get("exercise_stdin", "")
            lesson.example_in_browser = l_data.get("example_in_browser", True)
            lesson.checks = l_data.get("checks", [])
            lesson.assistant = l_data.get("assistant", {})
            lesson.quiz = l_data.get("quiz", [])
            lesson.challenge = l_data.get("challenge", {})
            db.add(lesson)
            count += 1

    db.commit()
    return count


if __name__ == "__main__":
    # Requiere las tablas creadas: ejecuta antes "alembic upgrade head"
    with SessionLocal() as session:
        total = seed(session)
    print(f"Seed completado: {total} lecciones.")
