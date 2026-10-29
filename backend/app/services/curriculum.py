"""Contenido educativo revisado que usa el tutor: `frontend/data/learning.json`.

Es la misma fuente que la web y la app Android: 22 conceptos con su resumen, un ejemplo cuya
salida se comprueba en CI (`scripts/learning/build_learning.py --check`), los errores típicos de
cada concepto y los ejercicios. El tutor lo prefiere a inventar: si el curso ya explica algo, se
explica igual.

También calcula, sin red ni modelo, qué conceptos ha demostrado el alumno con sus ejercicios. Es
una versión reducida de `conceptStats` (frontend/js/learn/mastery.js) sobre el documento que la
web guarda en la cuenta (`/api/course-state/learn`). Ese documento lo escribe el cliente: se lee
con cuidado y cualquier dato con forma inesperada se ignora.
"""

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path

# Igual que en mastery.js: un error deja de estar activo tras 2 aciertos o 21 días sin repetirse
FIXED_STREAK = 2
ERROR_DAYS = 21
LEVEL_WEIGHT = {1: 1.0, 2: 1.5, 3: 2.0}
MASTERED_SCORE = 0.8
STRUGGLING_SCORE = 0.5


@dataclass(frozen=True)
class Misconception:
    id: str
    concept: str
    label: str
    why: str
    think: str
    avoid: str


@dataclass(frozen=True)
class Example:
    code: str
    output: str
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class OutputExercise:
    """«¿Qué muestra este programa?»: salida comprobada en CI y respuestas trampa conocidas."""

    id: str
    concept: str
    level: int
    code: str
    expect: str
    traps: dict[str, str]
    explain: str


@dataclass(frozen=True)
class Concept:
    id: str
    title: str
    summary: str
    when: str
    example: Example | None
    errors: tuple[str, ...]
    lessons: tuple[str, ...]
    related: tuple[str, ...]
    requires: tuple[str, ...] = ()
    # Teoría completa del concepto: la «explicación alternativa» del tutor
    theory: str = ""


@dataclass(frozen=True)
class Curriculum:
    concepts: dict[str, Concept]
    misconceptions: dict[str, Misconception]
    output_exercises: dict[str, tuple[OutputExercise, ...]]
    # Enunciados de ejercicios de programar, por concepto: (nivel, enunciado)
    code_exercises: dict[str, tuple[tuple[int, str], ...]]
    # Todos los ejercicios, por concepto: (id, nivel). Para calcular el dominio
    exercise_levels: dict[str, tuple[tuple[str, int], ...]]
    path: tuple[str, ...] = ()
    lesson_concepts: dict[str, tuple[str, ...]] = field(default_factory=dict)


def _text(value: object) -> str:
    return value if isinstance(value, str) else ""


def parse_curriculum(data: dict) -> Curriculum:
    concepts: dict[str, Concept] = {}
    misconceptions: dict[str, Misconception] = {}
    lesson_concepts: dict[str, list[str]] = {}
    for raw in data.get("concepts", []):
        example = raw.get("example") or None
        concept = Concept(
            id=raw["id"],
            title=raw["title"],
            summary=_text(raw.get("summary")),
            when=_text(raw.get("when")),
            example=Example(
                code=example["code"],
                output=_text(example.get("output")),
                notes=tuple(note for _, note in example.get("lines", [])),
            )
            if example
            else None,
            errors=tuple(error["id"] for error in raw.get("errors", [])),
            lessons=tuple(raw.get("lessons") or ()),
            related=tuple(raw.get("related") or ()),
            requires=tuple(raw.get("requires") or ()),
            theory=_text(raw.get("theory")),
        )
        concepts[concept.id] = concept
        for lesson in concept.lessons:
            lesson_concepts.setdefault(lesson, []).append(concept.id)
        for error in raw.get("errors", []):
            misconceptions[error["id"]] = Misconception(
                id=error["id"],
                concept=concept.id,
                label=_text(error.get("label")),
                why=_text(error.get("why")),
                think=_text(error.get("think")),
                avoid=_text(error.get("avoid")),
            )

    outputs: dict[str, list[OutputExercise]] = {}
    codes: dict[str, list[tuple[int, str]]] = {}
    levels: dict[str, list[tuple[str, int]]] = {}
    for raw in data.get("exercises", []):
        concept, level = raw["concept"], int(raw.get("level", 1))
        levels.setdefault(concept, []).append((raw["id"], level))
        # Solo los que no leen del teclado: su salida depende únicamente del código
        predictable = raw.get("code") and raw.get("expect") is not None and not raw.get("stdin")
        if raw.get("kind") == "output" and predictable:
            outputs.setdefault(concept, []).append(
                OutputExercise(
                    id=raw["id"],
                    concept=concept,
                    level=level,
                    code=raw["code"],
                    expect=raw["expect"],
                    traps=dict(raw.get("traps") or {}),
                    explain=_text(raw.get("explain")),
                )
            )
        elif raw.get("kind") == "code" and raw.get("q"):
            codes.setdefault(concept, []).append((level, raw["q"]))
    return Curriculum(
        concepts=concepts,
        misconceptions=misconceptions,
        output_exercises={key: tuple(value) for key, value in outputs.items()},
        code_exercises={key: tuple(value) for key, value in codes.items()},
        exercise_levels={key: tuple(value) for key, value in levels.items()},
        path=tuple(data.get("path") or concepts),
        lesson_concepts={key: tuple(value) for key, value in lesson_concepts.items()},
    )


@lru_cache
def load_curriculum(path: Path) -> Curriculum:
    """Se lee una vez por proceso. Sin el archivo, el tutor funciona sin contenido revisado."""
    try:
        return parse_curriculum(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, ValueError, KeyError, TypeError):
        return parse_curriculum({})


def get_curriculum() -> Curriculum:
    from app.config import get_settings

    return load_curriculum(get_settings().learning_file)


# ---------- Evidencias del alumno (documento «learn» de su cuenta) ----------


@dataclass(frozen=True)
class ConceptEvidence:
    """Lo que el alumno ha DEMOSTRADO en los ejercicios, por concepto. Nada se deduce del %."""

    mastered: tuple[str, ...] = ()  # ≥ 80 % de los ejercicios, con aplicación y sin errores
    struggling: tuple[str, ...] = ()  # intentados y < 50 % de acierto
    active_errors: tuple[str, ...] = ()  # errores típicos recientes y sin corregir


def _parse_time(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        moment = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return moment if moment.tzinfo else moment.replace(tzinfo=UTC)


def concept_evidence(
    curriculum: Curriculum, document: object, now: datetime | None = None
) -> ConceptEvidence:
    if not isinstance(document, dict):
        return ConceptEvidence()
    now = now or datetime.now(UTC)
    history = document.get("ex") if isinstance(document.get("ex"), dict) else {}
    errors = document.get("errors") if isinstance(document.get("errors"), dict) else {}
    concepts = document.get("concepts") if isinstance(document.get("concepts"), dict) else {}

    active: list[str] = []
    for error_id, entry in errors.items():
        if error_id not in curriculum.misconceptions or not isinstance(entry, dict):
            continue
        last = _parse_time(entry.get("last"))
        streak = entry.get("streak")
        if last and isinstance(streak, int) and streak < FIXED_STREAK:
            if (now - last).days <= ERROR_DAYS:
                active.append(error_id)
    active_concepts = {curriculum.misconceptions[error].concept for error in active}

    def last_ok(exercise_id: str) -> bool | None:
        entry = history.get(exercise_id)
        results = entry.get("h") if isinstance(entry, dict) else None
        if not isinstance(results, list) or not results:
            return None
        return results[-1] is True

    mastered, struggling = [], []
    for concept_id in curriculum.path:
        exercises = curriculum.exercise_levels.get(concept_id, ())
        total = earned = 0.0
        attempted = 0
        for exercise_id, level in exercises:
            weight = LEVEL_WEIGHT.get(level, 1.0)
            total += weight
            result = last_ok(exercise_id)
            attempted += result is not None
            earned += weight if result else 0
        score = earned / total if total else 0
        applied = [last_ok(exercise_id) for exercise_id, level in exercises if level >= 2]
        applied_ok = not applied or any(applied)
        entry = concepts.get(concept_id)
        placed = isinstance(entry, dict) and _parse_time(entry.get("placed")) is not None
        if placed or (
            attempted
            and score >= MASTERED_SCORE
            and applied_ok
            and concept_id not in active_concepts
        ):
            mastered.append(concept_id)
        elif attempted and score < STRUGGLING_SCORE:
            struggling.append(concept_id)
    return ConceptEvidence(tuple(mastered), tuple(struggling), tuple(active))
