"""Modelos de datos (Pydantic): catálogo, guiones y escenas."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

Status = Literal[
    "pending",
    "scripted",
    "audio_ready",
    "animation_ready",
    "rendered",
    "reviewed",
    "published",
    "error",
]
STATUS_ORDER = [
    "pending",
    "scripted",
    "audio_ready",
    "animation_ready",
    "rendered",
    "reviewed",
    "published",
]
SceneType = Literal[
    "title",
    "concept",
    "code",
    "terminal",
    "variable",
    "datatype",
    "conditional",
    "loop",
    "function",
    "list",
    "dictionary",
    "error",
    "exercise",
    "summary",
]
Section = Literal["intro", "explanation", "example", "result", "exercise", "summary"]
REQUIRED_SECTIONS = ("intro", "explanation", "example", "result", "exercise", "summary")


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Bilingual(Strict):
    es: str = ""
    en: str = ""

    def get(self, language: str) -> str:
        return self.es if language == "es" else self.en


class Step(Strict):
    """Un elemento que aparece dentro de la escena (viñeta, línea resaltada, celda…)."""

    text: Bilingual | None = None
    line: int | None = Field(default=None, ge=1, description="Línea de código que se resalta")
    index: int | None = Field(default=None, ge=0, description="Posición en una lista o bucle")
    key: str | None = Field(default=None, description="Clave de diccionario o nombre de variable")
    sentence: int | None = Field(
        default=None, ge=0, description="Aparece al empezar esta frase de la narración (desde 0)"
    )
    at: float | None = Field(default=None, ge=0, le=1, description="Aparece en esta fracción")
    until: float | None = Field(default=None, ge=0, le=1, description="Desaparece en esta fracción")

    @model_validator(mode="after")
    def _order(self) -> Step:
        if self.at is not None and self.until is not None and self.until <= self.at:
            raise ValueError("'until' debe ser posterior a 'at'")
        return self


class Scene(Strict):
    id: str = Field(pattern=r"^[a-z0-9][a-z0-9-]*$")
    type: SceneType
    section: Section
    estimated_seconds: float = Field(default=0, ge=0)
    narration: Bilingual
    heading: Bilingual = Bilingual()
    code: str = ""
    code_language: str = "python"
    output: str = ""
    steps: list[Step] = []
    # Datos propios del componente (variables, elementos, ramas…). Un valor {"es":…, "en":…}
    # se traduce al idioma del vídeo.
    data: dict[str, Any] = {}
    visual_notes: str = ""
    needs_edit: bool = False


class Script(Strict):
    lesson_id: str
    title: Bilingual
    course: Bilingual = Bilingual()
    objectives: list[Bilingual] = []
    origin: Literal["generated", "edited"] = "generated"
    source_hash: str = ""
    scenes: list[Scene]

    @model_validator(mode="after")
    def _unique_ids(self) -> Script:
        ids = [scene.id for scene in self.scenes]
        if len(ids) != len(set(ids)):
            raise ValueError("Hay escenas con el mismo id")
        return self

    def problems(self) -> list[str]:
        """Motivos por los que el guion todavía no se puede producir."""
        found = []
        if not self.title.es or not self.title.en:
            found.append("Falta el título en algún idioma")
        missing = [
            s for s in REQUIRED_SECTIONS if s not in {scene.section for scene in self.scenes}
        ]
        if missing:
            found.append(f"Faltan secciones: {', '.join(missing)}")
        for scene in self.scenes:
            for language in ("es", "en"):
                if not scene.narration.get(language).strip():
                    found.append(f"Escena {scene.id}: sin narración en {language}")
            if scene.needs_edit:
                found.append(f"Escena {scene.id}: marcada para revisar (needs_edit)")
        return found


class CatalogEntry(Strict):
    id: str
    family: Literal["learn", "pcap", "daw"]
    course: str
    module: str
    unit: str
    lesson: str
    level: str | None = None
    objective: str
    estimated_minutes: float
    concepts: list[str]
    code: str
    code_language: str
    animations: list[str]
    exercise: str
    source: str
    also_covers: list[str] = Field(
        default=[], description="Conceptos de «Aprender» que se explican con este mismo vídeo"
    )
    source_hash: str
    status: Status = "pending"
    error: str = ""


class Catalog(Strict):
    version: int = 1
    lessons: list[CatalogEntry]

    def get(self, lesson_id: str) -> CatalogEntry:
        for entry in self.lessons:
            if entry.id == lesson_id:
                return entry
        raise KeyError(f"No existe la lección «{lesson_id}» en el catálogo")


def localize(value: Any, language: str) -> Any:
    """Sustituye cada {"es":…, "en":…} por el texto del idioma pedido."""
    if isinstance(value, dict):
        if value and set(value) <= {"es", "en"}:
            return value.get(language, "")
        return {key: localize(item, language) for key, item in value.items()}
    if isinstance(value, list):
        return [localize(item, language) for item in value]
    return value
