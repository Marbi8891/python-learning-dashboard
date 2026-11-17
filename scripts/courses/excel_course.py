"""Curso Excel profesional (familia academia): M01 y M02, 9 unidades y 111 ejercicios.

Diseño en docs/excel-academy/CURRICULUM_M1_M2.md. El contenido está en scripts/courses/excel/m01.py
y m02.py. Ningún resultado se escribe «a ojo»: el motor de fórmulas de la web (en Node) comprueba
cada ejemplo y cada ejercicio de fórmula, y este script comprueba los mínimos de cada unidad.

Los JSON van en frontend/data/academia/excel/ (no en data/courses/, que es de los cursos de DAW).

Uso:  python scripts/courses/excel_course.py           (genera)
      python scripts/courses/excel_course.py --check   (CI: falla si los JSON no están al día)
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "excel"))
from course_builder import ROOT, Block, Lesson, main  # noqa: E402
from m01 import UNITS as M01  # noqa: E402
from m02 import UNITS as M02  # noqa: E402

ACADEMY = ROOT / "frontend" / "data" / "academia"

# Volumen de cada unidad: (test, resultado, fórmula). CURRICULUM_M1_M2.md §8
VOLUME = {
    "xl1-interfaz": (8, 3, 0),
    "xl1-datos": (6, 5, 0),
    "xl1-formatos": (6, 5, 0),
    "xl1-referencias": (6, 4, 5),
    "xl1-archivos": (8, 0, 0),
    "xl2-operadores": (6, 6, 3),
    "xl2-estadisticas": (6, 5, 3),
    "xl2-contar": (6, 5, 3),
    "xl2-hojas": (6, 3, 3),
}
KIND = {"choice": 0, "formula-result": 1, "formula": 2}


def no_code(_: str) -> str:
    raise AssertionError("El curso de Excel no ejecuta código")


def no_example(_: str) -> None:
    """Los ejemplos de Excel van en `excel.examples` y los comprueba el motor de fórmulas."""


def check_unit(lesson: Lesson) -> None:
    """Mínimos de la plantilla de unidad (CURRICULUM_M1_M2.md §2)."""
    slug, excel = lesson.slug, lesson.excel
    counts = Counter(KIND[q.kind] for q in lesson.questions)
    volume = (counts[0], counts[1], counts[2])
    assert volume == VOLUME[slug], (
        f"{slug}: tiene {volume} ejercicios (T, R, F) y deben ser {VOLUME[slug]}"
    )
    assert len(lesson.objectives) >= 3, f"{slug}: hacen falta 3 objetivos"
    assert len(lesson.mistakes) >= 3, f"{slug}: hacen falta 3 errores frecuentes"
    assert len(lesson.summary) >= 3, f"{slug}: falta el resumen"
    assert excel["examples"], f"{slug}: falta un ejemplo resuelto"
    if counts[1] or counts[2]:
        assert any("formula" in e for e in excel["examples"]), f"{slug}: falta un ejemplo calculado"
    assert lesson.sources and all(u.startswith("https://") for _, u in lesson.sources), (
        f"{slug}: fuentes"
    )
    assert all("consultado el" in t for t, _ in lesson.sources), f"{slug}: fuentes sin fecha"
    ids = {q.id for q in lesson.questions}
    assert all(q.id.startswith(slug[:4]) for q in lesson.questions), f"{slug}: id con otro prefijo"
    assert excel["guided"]["question"] in ids, f"{slug}: el ejercicio guiado no es de la unidad"
    formulas = {q.id for q in lesson.questions if q.kind == "formula"}
    required = excel["pass"]["required"]
    assert set(required) <= formulas, (
        f"{slug}: los obligatorios tienen que ser ejercicios de fórmula"
    )
    assert bool(required) == bool(formulas), (
        f"{slug}: las unidades con fórmulas tienen obligatorios"
    )
    for q in lesson.questions:
        if q.kind == "choice":
            assert len(q.options) == len(set(q.options)) >= 3, f"{q.id}: opciones"
        if q.kind == "formula":
            assert q.excel["mistakes"] and q.excel["hints"], f"{q.id}: faltan errores o pistas"


def blocks() -> list[Block]:
    for lesson in M01 + M02:
        check_unit(lesson)
    return [
        Block(
            "xl-m01",
            "M01 · Fundamentos de Excel",
            "Moverse por un libro, introducir datos, formatos de número"
            " y referencias que se copian bien.",
            50,
            M01,
        ),
        Block(
            "xl-m02",
            "M02 · Fórmulas y funciones básicas",
            "Operadores y prioridad, SUMA, PROMEDIO, MIN, MAX, CONTAR, CONTARA,"
            " PRODUCTO, REDONDEAR y hojas.",
            50,
            M02,
        ),
    ]


if __name__ == "__main__":
    main("excel", blocks(), no_code, no_example, module=None, assets=ACADEMY)
