"""Esquemas de entrada/salida de la API (lo que ve el frontend)."""

import json
from datetime import datetime
from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, EmailStr, Field, field_validator

# ---------- Lecciones ----------


class Source(BaseModel):
    title: str
    url: str


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


class Check(BaseModel):
    stdin: str = ""
    test: str


class FaqItem(BaseModel):
    q: str
    a: str


class Assistant(BaseModel):
    hint: str = ""
    faq: list[FaqItem] = []


class QuizQuestion(BaseModel):
    q: str
    options: list[str] = Field(min_length=2)
    answer: int = Field(ge=0)
    explain: str
    code: str | None = None


class Challenge(BaseModel):
    title: str
    stars: int = Field(ge=1, le=3)
    exercise: str
    starter: str
    stdin: str = ""
    checks: list[Check]
    hint: str = ""


class LessonDetail(LessonSummary):
    module_slug: str
    module_title: str
    theory: str | None
    example_code: str | None
    exercise: str | None
    sources: list[Source]
    starter: str | None
    example_stdin: str
    exercise_stdin: str
    example_in_browser: bool
    checks: list[Check]
    assistant: Assistant
    quiz: list[QuizQuestion]
    challenge: Challenge | None


# ---------- Usuarios y autenticación ----------

NormalizedEmail = Annotated[EmailStr, AfterValidator(lambda email: email.strip().lower())]


Password = Annotated[str, Field(min_length=8, max_length=128)]


class UserCreate(BaseModel):
    email: NormalizedEmail
    password: Password
    display_name: str = Field(min_length=1, max_length=80)
    accept_privacy: bool

    @field_validator("accept_privacy")
    @classmethod
    def must_accept(cls, accepted: bool) -> bool:
        if not accepted:
            raise ValueError("Debes aceptar la política de privacidad")
        return accepted


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    display_name: str
    created_at: datetime


class PasswordResetRequest(BaseModel):
    email: NormalizedEmail


class PasswordResetConfirm(BaseModel):
    token: str = Field(min_length=20, max_length=200)
    new_password: Password


class PasswordConfirm(BaseModel):
    password: str = Field(max_length=128)


class Token(BaseModel):
    # Sin token cuando va en la cookie HttpOnly (token_type "cookie", ADR-0033)
    access_token: str | None = None
    token_type: str = "bearer"


# ---------- Progreso ----------


class ProgressItem(BaseModel):
    lesson_slug: str
    completed_at: datetime


class ProgressImport(BaseModel):
    """Progreso guardado en el navegador antes de iniciar sesión."""

    lesson_slugs: list[str] = Field(max_length=500)


# ---------- Intentos de ejercicios ----------


class AttemptCreate(BaseModel):
    code: str = Field(max_length=20_000)
    passed: bool


class AttemptOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    passed: bool
    created_at: datetime


# ---------- Preparación del PCAP ----------

MAX_PCAP_STATE_BYTES = 200_000  # ~1000 simulacros y todas las respuestas caben de sobra

# Cursos de DAW de la app Android que se pueden guardar en la cuenta (ADR-0016 y ADR-0018),
# más "learn": el progreso por conceptos del núcleo educativo (ADR-0031).
# Lista cerrada: evita que un cliente cree documentos con nombres arbitrarios.
COURSES = ("sql", "js", "java", "entornos", "programacion", "learn")


class PcapStateIn(BaseModel):
    data: dict

    @field_validator("data")
    @classmethod
    def not_too_big(cls, data: dict) -> dict:
        if len(json.dumps(data)) > MAX_PCAP_STATE_BYTES:
            raise ValueError("Los datos de preparación son demasiado grandes")
        return data


class PcapStateOut(BaseModel):
    data: dict
    updated_at: datetime | None


# ---------- Exportación de datos (RGPD, derecho de acceso y portabilidad) ----------


class ProfileUpdate(BaseModel):
    display_name: str = Field(min_length=1, max_length=80)


class PasswordChange(BaseModel):
    current_password: str = Field(max_length=128)
    new_password: Password


class ActivityOut(BaseModel):
    """Un evento de «Actividad de la cuenta» (ADR-0025)."""

    model_config = ConfigDict(from_attributes=True)

    kind: str
    device: str
    created_at: datetime


class UserExport(BaseModel):
    user: UserOut
    privacy_accepted_at: datetime | None
    progress: list[ProgressItem]
    attempts: list[dict]
    pcap: dict | None = None
    courses: dict[str, dict] = {}
    activity: list[ActivityOut] = []
    exported_at: datetime
