"""Esquemas de entrada/salida de la API (lo que ve el frontend)."""

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
    access_token: str
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


# ---------- Exportación de datos (RGPD, derecho de acceso y portabilidad) ----------


class UserExport(BaseModel):
    user: UserOut
    privacy_accepted_at: datetime | None
    progress: list[ProgressItem]
    attempts: list[dict]
    exported_at: datetime
