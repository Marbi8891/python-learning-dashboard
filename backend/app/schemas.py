"""Esquemas de entrada/salida de la API (lo que ve el frontend)."""

from pydantic import BaseModel, ConfigDict


class LessonSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    slug: str
    title: str
    position: int


class ModuleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    slug: str
    title: str
    position: int
    lessons: list[LessonSummary]


class LessonDetail(LessonSummary):
    module_slug: str
    module_title: str
    theory: str | None
    example_code: str | None
    exercise: str | None
