"""Genera los JSON de un curso de la app Android (ADR-0016) y comprueba sus respuestas.

Cada curso se escribe en un script de Python (`sql_course.py`, ...) con sus bloques, lecciones
y preguntas. Las preguntas de código indican la salida que su autor espera (`expect`): el script
ejecuta el código de verdad y falla si la salida real es otra. Así ninguna respuesta correcta se
escribe «a ojo».

Salida, con el mismo formato que `frontend/data/pcap.json` y `lessons.json` para que la app
reutilice su lector: android/app/src/main/assets/courses/<id>/bank.json y .../lessons.json

Uso:  python scripts/courses/<curso>.py           (genera)
      python scripts/courses/<curso>.py --check   (CI: falla si los JSON no están al día)
"""

from __future__ import annotations

import json
import random
import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "android" / "app" / "src" / "main" / "assets" / "courses"


@dataclass
class Q:
    """Pregunta. Si tiene `run`, la correcta es la salida real de ejecutarlo (debe ser `expect`)."""

    id: str
    q: str
    explain: str
    options: list[str] = field(
        default_factory=list
    )  # preguntas teóricas: opciones con la correcta en `answer`
    answer: int = 0
    code: str | None = None  # lo que ve el alumno
    run: str | None = None  # lo que se ejecuta para comprobar (por defecto, `code`)
    expect: str | None = None  # salida esperada
    wrong: list[str] = field(default_factory=list)  # distractores de las preguntas de código


@dataclass
class Lesson:
    slug: str
    title: str
    theory: str
    example: str
    exercise: str
    starter: str
    hint: str
    faq: list[tuple[str, str]]
    challenge: tuple[
        str, int, str, str, str
    ]  # título, estrellas (1-3), enunciado, código de partida, pista
    questions: list[Q]  # banco (ruta, práctica y juego)
    quiz: list[Q]  # mini-quiz de la teoría
    sources: list[tuple[str, str]]


@dataclass
class Block:
    slug: str
    title: str
    summary: str
    weight: int
    lessons: list[Lesson]


def resolve(q: Q, runner: Callable[[str], str]) -> tuple[list[str], int]:
    """Opciones y respuesta. En las de código, ejecuta y comprueba la salida esperada."""
    if q.run is None and q.expect is None:
        assert 0 <= q.answer < len(q.options), f"{q.id}: respuesta fuera de rango"
        return q.options, q.answer
    actual = runner(q.run or q.code or "")
    if actual != q.expect:
        raise AssertionError(
            f"{q.id}: la salida real no es la esperada.\n"
            f"--- esperada ---\n{q.expect}\n--- real ---\n{actual}"
        )
    assert q.expect not in q.wrong, f"{q.id}: un distractor coincide con la respuesta"
    assert len(set(q.wrong)) == len(q.wrong) and len(q.wrong) >= 2, (
        f"{q.id}: distractores repetidos o insuficientes"
    )
    options = [*q.wrong, q.expect]
    random.Random(q.id).shuffle(options)  # orden estable entre ejecuciones
    return options, options.index(q.expect)


def build(
    course_id: str,
    blocks: list[Block],
    runner: Callable[[str], str],
    examples: Callable[[str], None],
) -> dict[str, str]:
    assert sum(b.weight for b in blocks) == 100, "los pesos de los bloques deben sumar 100"
    ids: set[str] = set()
    bank_questions, modules = [], []
    for block in blocks:
        lessons = []
        for lesson in block.lessons:
            examples(lesson.example)  # el ejemplo de la teoría también tiene que funcionar
            quiz = []
            for q in lesson.quiz:
                options, answer = resolve(q, runner)
                quiz.append(
                    {
                        "q": q.q,
                        "options": options,
                        "answer": answer,
                        "explain": q.explain,
                        **({"code": q.code} if q.code else {}),
                    }
                )
            for q in lesson.questions:
                assert q.id not in ids, f"id repetido: {q.id}"
                ids.add(q.id)
                options, answer = resolve(q, runner)
                bank_questions.append(
                    {
                        "id": q.id,
                        "block": block.slug,
                        "q": {"es": q.q, "en": q.q},
                        "code": q.code,
                        # Opciones de texto como {es, en}: la app no las muestra como código
                        "options": options
                        if q.expect is not None
                        else [{"es": o, "en": o} for o in options],
                        "answer": [answer],
                        "explain": {"es": q.explain, "en": q.explain},
                        "lesson": lesson.slug,
                    }
                )
            title, stars, text, starter, hint = lesson.challenge
            lessons.append(
                {
                    "slug": lesson.slug,
                    "title": lesson.title,
                    "theory": lesson.theory.strip(),
                    "example_code": lesson.example.strip(),
                    "exercise": lesson.exercise.strip(),
                    "starter": lesson.starter.strip() + "\n",
                    "quiz": quiz,
                    "challenge": {
                        "title": title,
                        "stars": stars,
                        "exercise": text.strip(),
                        "starter": starter.strip() + "\n",
                        "hint": hint,
                    },
                    "assistant": {
                        "hint": lesson.hint,
                        "faq": [{"q": a, "a": b} for a, b in lesson.faq],
                    },
                    "sources": [{"title": t, "url": u} for t, u in lesson.sources],
                }
            )
        modules.append(
            {"slug": block.slug, "title": block.title, "summary": block.summary, "lessons": lessons}
        )

    counts = {b.slug: sum(1 for q in bank_questions if q["block"] == b.slug) for b in blocks}
    bank = {
        "exam": {
            "code": course_id.upper(),
            "questions": 0,
            "minutes": 0,
            "pass": 0,
            "blocks": [
                {
                    "slug": b.slug,
                    "weight": b.weight,
                    "items": counts[b.slug],
                    "title": {"es": b.title, "en": b.title},
                }
                for b in blocks
            ],
        },
        "questions": bank_questions,
        "cards": [],
    }
    return {"bank.json": _dump(bank), "lessons.json": _dump({"modules": modules})}


def _dump(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, indent=1) + "\n"


def main(
    course_id: str,
    blocks: list[Block],
    runner: Callable[[str], str],
    examples: Callable[[str], None],
) -> None:
    files = build(course_id, blocks, runner, examples)
    folder = ASSETS / course_id
    if "--check" in sys.argv:
        stale = [
            name
            for name, text in files.items()
            if not (folder / name).exists() or (folder / name).read_text(encoding="utf-8") != text
        ]
        if stale:
            sys.exit(
                f"Curso {course_id}: {', '.join(stale)} no está al día. "
                f"Ejecuta: python scripts/courses/{course_id}_course.py"
            )
        print(f"Curso {course_id}: respuestas comprobadas y JSON al día.")
        return
    folder.mkdir(parents=True, exist_ok=True)
    for name, text in files.items():
        (folder / name).write_text(text, encoding="utf-8")
    total = json.loads(files["bank.json"])["questions"]
    print(
        f"Curso {course_id}: {len(total)} preguntas y "
        f"{sum(len(b.lessons) for b in blocks)} lecciones generadas en {folder}"
    )
