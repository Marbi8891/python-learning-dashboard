"""Inventario de lecciones reales de PLD (no se inventa ninguna: todo sale de frontend/data)."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from video_factory.config import DATA
from video_factory.models import Catalog, CatalogEntry
from video_factory.text import bold_terms, digest, strip_markdown, word_count

COURSES = {
    # carpeta: (nombre del curso, lenguaje del código de ejemplo)
    "programacion": ("Programación (DAW)", "python"),
    "sql": ("Bases de datos (DAW)", "sql"),
    "java": ("Java (DAW)", "java"),
    "js": ("JavaScript (DAW)", "javascript"),
    "marcas": ("Lenguajes de marcas (DAW)", "python"),
    "entornos": ("Entornos de desarrollo (DAW)", "python"),
}
BASE_ANIMATIONS = [
    "TitleScene",
    "ConceptScene",
    "CodeScene",
    "TerminalScene",
    "ExerciseScene",
    "SummaryScene",
]
# Componente específico según el tema de la lección (solo código Python).
TOPIC_ANIMATIONS = [
    (r"variable|asignaci", "VariableScene"),
    (r"tipos", "DataTypeScene"),
    (r"condicional", "ConditionalScene"),
    (r"bucle|recorrido|acumulador", "LoopScene"),
    (r"funci", "FunctionScene"),
    (r"lista|coleccion|comprension", "ListScene"),
    (r"diccionario|coleccion", "DictionaryScene"),
    (r"excepci|error|depuraci|validaci", "ErrorScene"),
]


@dataclass
class LessonSource:
    """Una lección de PLD con la misma forma, venga del archivo que venga."""

    id: str
    family: str
    course: str
    module: str
    unit: str
    title: str
    theory: str
    code: str
    code_language: str
    exercise: str
    source: str
    level: str | None = None
    objective: str = ""
    line_notes: list[tuple[int, str]] = field(default_factory=list)
    output: str | None = None
    stdin: str = ""
    starter: str = ""
    summary: list[str] = field(default_factory=list)
    objectives: list[str] = field(default_factory=list)
    also_covers: list[str] = field(default_factory=list)

    def code_corpus(self) -> str:
        """Todo el código que la lección muestra: lo único que un vídeo puede enseñar."""
        return "\n".join([self.code, self.starter, self.theory, self.exercise])

    def fingerprint(self) -> str:
        return digest([self.title, self.theory, self.code, self.exercise, self.summary])


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _first_sentence(markdown: str) -> str:
    plain = strip_markdown(markdown)
    return re.split(r"(?<=[.!?])\s", plain, maxsplit=1)[0]


def _learn(data_dir: Path) -> list[LessonSource]:
    data = _read(data_dir / "learning.json")
    areas = {area["id"]: area["title"] for area in data["areas"]}
    first_exercise: dict[str, str] = {}
    for exercise in data["exercises"]:
        if exercise["kind"] == "code":
            first_exercise.setdefault(exercise["concept"], exercise["q"])
    for exercise in data["exercises"]:
        first_exercise.setdefault(exercise["concept"], exercise["q"])
    lessons = []
    for concept in data["concepts"]:
        example = concept["example"]
        sections = concept.get("sections") or []
        theory = concept.get("theory") or "\n\n".join(
            f"## {section['title']}\n\n{section['theory']}" for section in sections
        )
        if not theory:
            # Sin teoría propia: el concepto enlaza a una lección del PCAP, que ya tiene su vídeo.
            continue
        lessons.append(
            LessonSource(
                id=f"learn-{concept['id']}",
                family="learn",
                course="Aprender Python",
                module=areas[concept["area"]],
                unit=concept.get("ut") or concept["area"],
                title=concept["title"],
                theory=theory,
                code=example["code"],
                code_language="python",
                exercise=first_exercise.get(concept["id"], ""),
                source=f"frontend/data/learning.json#concepts/{concept['id']}",
                level=f"dificultad {concept['difficulty']}" if "difficulty" in concept else None,
                objective=concept["summary"],
                line_notes=[(line, note) for line, note in example.get("lines", [])],
                output=example.get("output"),
                summary=concept.get("recap") or [concept["summary"], concept.get("when", "")],
                objectives=concept.get("objectives") or [],
            )
        )
    return lessons


def _concepts_by_lesson(data_dir: Path) -> dict[str, list[str]]:
    """Conceptos de «Aprender» sin teoría propia, agrupados por la lección PCAP que los explica."""
    covered: dict[str, list[str]] = {}
    for concept in _read(data_dir / "learning.json")["concepts"]:
        if "theory" not in concept and not concept.get("sections"):
            for slug in concept.get("lessons", []):
                covered.setdefault(f"pcap-{slug}", []).append(concept["id"])
    return covered


def _course_lessons(path: Path, family: str, course: str, language: str, prefix: str, level):
    lessons = []
    for module in _read(path)["modules"]:
        for lesson in module["lessons"]:
            summary = lesson.get("summary") or []
            lessons.append(
                LessonSource(
                    id=f"{prefix}-{lesson['slug']}",
                    family=family,
                    course=course,
                    module=module["title"],
                    unit=module["slug"],
                    title=lesson["title"],
                    theory=lesson["theory"],
                    code=lesson["example_code"],
                    code_language=language,
                    exercise=lesson["exercise"],
                    source=f"{path.relative_to(DATA.parent.parent)}#{lesson['slug']}"
                    if path.is_relative_to(DATA.parent.parent)
                    else f"{path.name}#{lesson['slug']}",
                    level=level,
                    objective=(lesson.get("objectives") or [_first_sentence(lesson["theory"])])[0],
                    stdin=lesson.get("example_stdin", ""),
                    starter=lesson.get("starter", ""),
                    summary=summary if isinstance(summary, list) else [summary],
                    objectives=lesson.get("objectives") or [],
                )
            )
    return lessons


def load_sources(data_dir: Path = DATA) -> dict[str, LessonSource]:
    """Todas las lecciones reales con contenido para un vídeo, por id."""
    pcap_path = data_dir / "lessons.json"
    lessons = _learn(data_dir)
    lessons += _course_lessons(
        pcap_path, "pcap", "Curso PCAP", "python", "pcap", _read(pcap_path)["course"]["level"]
    )
    for folder, (course, language) in COURSES.items():
        path = data_dir / "courses" / folder / "lessons.json"
        prefix = "daw-" + folder
        lessons += _course_lessons(path, "daw", course, language, prefix, None)
    covered = _concepts_by_lesson(data_dir)
    for lesson in lessons:
        lesson.also_covers = covered.get(lesson.id, [])
    by_id = {lesson.id: lesson for lesson in lessons}
    if len(by_id) != len(lessons):
        raise ValueError("Hay lecciones con el mismo id en el temario")
    return by_id


def animations_for(source: LessonSource) -> list[str]:
    names = list(BASE_ANIMATIONS)
    if source.code_language == "python":
        haystack = f"{source.id} {source.title}".lower()
        for pattern, component in TOPIC_ANIMATIONS:
            if re.search(pattern, haystack) and component not in names:
                names.append(component)
    return names


def estimate_minutes(source: LessonSource) -> float:
    """Orientativa: la duración real la fija la narración cuando existe el guion."""
    seconds = word_count(strip_markdown(source.theory)) / 150 * 60
    seconds += 6 * len(source.code.splitlines()) + 40
    return round(min(max(seconds / 60, 2.0), 10.0), 1)


def entry_for(source: LessonSource) -> CatalogEntry:
    return CatalogEntry(
        id=source.id,
        family=source.family,
        course=source.course,
        module=source.module,
        unit=source.unit,
        lesson=source.title,
        level=source.level,
        objective=source.objective,
        estimated_minutes=estimate_minutes(source),
        concepts=bold_terms(source.theory)[:12],
        code=source.code,
        code_language=source.code_language,
        animations=animations_for(source),
        exercise=source.exercise,
        source=source.source,
        also_covers=source.also_covers,
        source_hash=source.fingerprint(),
    )


def build_catalog(previous: Catalog | None = None, data_dir: Path = DATA) -> Catalog:
    """Regenera el inventario y conserva el estado de producción de cada lección."""
    old = {entry.id: entry for entry in previous.lessons} if previous else {}
    lessons = []
    for source in load_sources(data_dir).values():
        entry = entry_for(source)
        if entry.id in old:
            entry.status, entry.error = old[entry.id].status, old[entry.id].error
        lessons.append(entry)
    return Catalog(lessons=lessons)


def read_catalog(path: Path) -> Catalog | None:
    return Catalog.model_validate_json(path.read_text(encoding="utf-8")) if path.is_file() else None


def write_catalog(catalog: Catalog, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(catalog.model_dump(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
