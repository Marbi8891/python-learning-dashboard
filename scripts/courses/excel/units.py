"""Piezas para escribir las unidades de Excel profesional (docs/excel-academy/CURRICULUM_M1_M2.md).

Tres tipos de ejercicio:
- T: test (`choice`), una opción correcta.
- R: «¿qué devuelve esta fórmula?» (`formula-result`). El resultado lo vuelve a calcular el motor.
- F: «escribe la fórmula» (`formula`). La solución tiene que pasar todas sus comprobaciones y cada
  error frecuente tiene que fallar alguna (lo comprueba el motor de fórmulas con Node).

Las unidades siguen la plantilla del currículo: objetivos, explicación, ejemplos resueltos,
ejercicio guiado, caso, test, criterios para superarla, errores frecuentes, resumen y fuentes con fecha.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from course_builder import Lesson, Q  # noqa: E402

CHECKED = "2026-11-17"  # fecha en que se consultaron las fuentes
SOURCE_NOTE = "Soporte de Microsoft, en español; consultado el 17/11/2026"


def T(qid: str, q: str, options: list[str], answer: int, explain: str) -> Q:
    """Pregunta de test con una sola respuesta correcta."""
    return Q(id=qid, q=q, explain=explain, options=options, answer=answer)


def R(
    qid: str,
    q: str,
    formula: str,
    answer: float | str | int,
    explain: str,
    *,
    grid: dict | None = None,
    sheet: str | None = None,
    cell: str | None = None,
    answer_input: str = "number",
    options: list | None = None,
    tolerance: float | None = None,
) -> Q:
    """«¿Qué devuelve esta fórmula?». Con `options` el alumno elige; si no, escribe el resultado."""
    excel: dict = {"grid": grid or {}, "formula": formula, "answer": answer}
    excel["input"] = "choice" if options is not None else answer_input
    if options is not None:
        excel["options"] = options
    for key, value in (("sheet", sheet), ("cell", cell), ("tolerance", tolerance)):
        if value is not None:
            excel[key] = value
    return Q(id=qid, q=q, explain=explain, kind="formula-result", excel=excel)


def F(
    qid: str,
    q: str,
    *,
    grid: dict,
    cell: str,
    expect: float | str,
    checks: list[dict],
    solution: str,
    mistakes: list[tuple[str, str]],
    hints: list[str],
    explain: str,
    sheet: str | None = None,
    tolerance: float | None = None,
    vary: list[str] | None = None,
) -> Q:
    """«Escribe la fórmula en la celda». `mistakes`: (fórmula equivocada, por qué falla)."""
    excel: dict = {
        "grid": grid,
        "cell": cell,
        "expect": expect,
        "checks": checks,
        "solution": {"formula": solution},
        "mistakes": [{"error": error, "fix": fix} for error, fix in mistakes],
        "hints": hints,
    }
    for key, value in (("sheet", sheet), ("tolerance", tolerance), ("vary", vary)):
        if value is not None:
            excel[key] = value
    return Q(id=qid, q=q, explain=explain, kind="formula", excel=excel)


def example(
    eid: str,
    title: str,
    formula: str,
    answer: float | str,
    explain: str,
    *,
    grid: dict | None = None,
    sheet: str | None = None,
    cell: str | None = None,
) -> dict:
    """Ejemplo resuelto con cuadrícula: el generador comprueba su resultado con el motor."""
    data = {
        "id": eid,
        "title": title,
        "grid": grid or {},
        "formula": formula,
        "input": "text" if isinstance(answer, str) else "number",
        "answer": answer,
        "explain": explain,
    }
    if sheet:
        data["sheet"] = sheet
    if cell:
        data["cell"] = cell
    return data


def note(title: str, text: str) -> dict:
    """Ejemplo resuelto sin fórmula (por ejemplo, contar las celdas de un rango)."""
    return {"title": title, "text": text}


def unit(
    slug: str,
    title: str,
    *,
    hours: float,
    level: int,
    requires: list[str],
    objectives: list[str],
    theory: str,
    examples: list[dict],
    guided: str,
    guided_steps: list[str],
    case: tuple[str, str],
    mistakes: list[tuple[str, str]],
    summary: list[str],
    faq: list[tuple[str, str]],
    sources: list[tuple[str, str]],
    questions: list[Q],
    required: list[str] | None = None,
    warning: str | None = None,
) -> Lesson:
    """Unidad completa. Los campos propios de Excel van en `excel` (los pinta excel/course.js)."""
    case_title, case_text = case
    excel: dict = {
        "hours": hours,
        "level": level,
        "requires": requires,
        "examples": examples,
        "guided": {"question": guided, "steps": guided_steps},
        "case": {"title": case_title, "text": case_text.strip()},
        "pass": {"test": 0.8, "required": required or []},
        "checked": CHECKED,
    }
    if warning:
        excel["warning"] = warning
    return Lesson(
        slug=slug,
        title=title,
        theory=theory,
        example="",
        exercise=case_text,
        starter="",
        hint=guided_steps[0],
        faq=faq,
        challenge=(case_title, level, case_text, "", guided_steps[-1]),
        questions=questions,
        quiz=[],
        sources=[(f"{name} ({SOURCE_NOTE})", url) for name, url in sources],
        objectives=objectives,
        mistakes=mistakes,
        summary=summary,
        excel=excel,
    )
