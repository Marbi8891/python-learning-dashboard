"""Qué elementos de la estructura pedagógica tiene cada curso de DAW (Fase D, 6.2).

No genera nada ni falla: imprime una tabla en Markdown con cuántas lecciones de cada curso tienen
cada elemento, para decidir qué completar primero. Uso:

    python scripts/courses/audit_pedagogy.py
"""

from __future__ import annotations

import json
from pathlib import Path

COURSES = Path(__file__).resolve().parents[2] / "frontend" / "data" / "courses"

# Elemento de 6.2 → cómo se reconoce en una lección (None: la plataforma aún no tiene ese campo)
ELEMENTS = {
    "Objetivos": lambda lesson: bool(lesson.get("objectives")),
    "Conocimientos previos": None,
    "Explicación": lambda lesson: bool(lesson.get("theory", "").strip()),
    "Ejemplo comentado": lambda lesson: bool(lesson.get("example_code", "").strip()),
    "Ejercicio y reto (dos niveles)": lambda lesson: (
        bool(lesson.get("exercise")) and bool(lesson.get("challenge"))
    ),
    "Solución razonada": lambda lesson: bool(lesson.get("solution")),
    "Errores frecuentes": lambda lesson: bool(lesson.get("mistakes")),
    "Cuestionario": lambda lesson: bool(lesson.get("quiz")),
    "Criterios de superación": None,
    "Resumen para repasar": lambda lesson: bool(lesson.get("summary")),
    "Fuentes": lambda lesson: bool(lesson.get("sources")),
}


def main() -> None:
    rows = []
    for folder in sorted(p for p in COURSES.iterdir() if p.is_dir()):
        units = json.loads((folder / "lessons.json").read_text("utf-8"))["modules"]
        lessons = [lesson for unit in units for lesson in unit["lessons"]]
        cells = []
        for check in ELEMENTS.values():
            if check is None:
                cells.append("—")
                continue
            have = sum(check(lesson) for lesson in lessons)
            cells.append("✓" if have == len(lessons) else f"{have}/{len(lessons)}" if have else "✗")
        rows.append(f"| {folder.name} ({len(lessons)}) | " + " | ".join(cells) + " |")
    print("| Curso (lecciones) | " + " | ".join(ELEMENTS) + " |")
    print("|---|" + "---|" * len(ELEMENTS))
    print("\n".join(rows))
    print(
        "\n✓ todas las lecciones · n/N algunas · ✗ ninguna · — la plataforma aún no tiene ese campo"
    )


if __name__ == "__main__":
    main()
