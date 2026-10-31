"""Esquemas de entrada/salida de la API (lo que ve el frontend)."""

import json
from datetime import date, datetime
from typing import Annotated

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)

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


class DeleteConfirm(BaseModel):
    """Confirmación del borrado: la contraseña o, en cuentas de Google, un ID token reciente."""

    password: str | None = Field(default=None, max_length=128)
    google_credential: str | None = Field(default=None, min_length=20, max_length=8192)

    @model_validator(mode="after")
    def one_confirmation(self) -> "DeleteConfirm":
        if (self.password is None) == (self.google_credential is None):
            raise ValueError("Confirma con tu contraseña o con Google")
        return self


class Token(BaseModel):
    # Sin token cuando va en la cookie HttpOnly (token_type "cookie")
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

# Cursos de DAW que se pueden guardar en la cuenta,
# más "learn": el progreso por conceptos del núcleo educativo y "game": XP, racha y
# logros de la web, que antes solo vivían en el navegador.
# Lista cerrada: evita que un cliente cree documentos con nombres arbitrarios.
COURSES = ("sql", "js", "java", "entornos", "programacion", "learn", "game")


MAX_STATE_DEPTH = 20  # los documentos reales llegan a 5 niveles (medido en las pruebas e2e)


def _too_deep(data: dict) -> bool:
    """¿Supera el anidamiento permitido? Iterativo: un JSON muy profundo no puede romperlo."""
    pending = [(data, 1)]
    while pending:
        node, level = pending.pop()
        children = (
            node.values() if isinstance(node, dict) else node if isinstance(node, list) else ()
        )
        if children and level >= MAX_STATE_DEPTH:
            return True
        pending.extend((child, level + 1) for child in children)
    return False


class PcapStateIn(BaseModel):
    data: dict

    @field_validator("data")
    @classmethod
    def not_too_big(cls, data: dict) -> dict:
        # Antes de serializar: con cientos de niveles, pydantic fallaba con un 500
        if _too_deep(data):
            raise ValueError("Los datos de preparación están demasiado anidados")
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
    """Un evento de «Actividad de la cuenta»."""

    model_config = ConfigDict(from_attributes=True)

    kind: str
    device: str
    created_at: datetime


class UserExport(BaseModel):
    user: UserOut
    privacy_accepted_at: datetime | None
    email_verified_at: datetime | None = None
    progress: list[ProgressItem]
    attempts: list[dict]
    pcap: dict | None = None
    courses: dict[str, dict] = {}
    activity: list[ActivityOut] = []
    exported_at: datetime


# ---------- Panel del alumno ----------


class DashboardUser(BaseModel):
    display_name: str
    email: str
    created_at: datetime
    # Método del último inicio de sesión registrado: "google", "password" o None si aún no hay
    sign_in_method: str | None


class LessonRef(BaseModel):
    slug: str
    title: str


class ModuleProgress(BaseModel):
    slug: str
    title: str
    total: int
    completed: int


class LessonsSummary(BaseModel):
    """Curso PCAP de la web: las lecciones están en la base de datos."""

    total: int
    completed: int
    last_completed_at: datetime | None
    next_lesson: LessonRef | None
    modules: list[ModuleProgress]


class ExercisesSummary(BaseModel):
    """Intentos guardados en la cuenta (los últimos de cada lección: attempts_kept_per_lesson)."""

    attempts: int
    passed: int
    lessons_tried: int
    lessons_passed: int
    last_attempt_at: datetime | None


class DailyActivity(BaseModel):
    day: date
    lessons_completed: int
    attempts: int
    passed: int


class SyncedState(BaseModel):
    """Documento de progreso guardado en la cuenta (PCAP, cursos de DAW, conceptos, logros)."""

    key: str
    updated_at: datetime | None


class DashboardOut(BaseModel):
    user: DashboardUser
    lessons: LessonsSummary
    exercises: ExercisesSummary
    daily: list[DailyActivity]
    synced: list[SyncedState]
    generated_at: datetime


class LearningEvent(BaseModel):
    kind: str  # "lesson_completed" | "attempt"
    lesson_slug: str
    lesson_title: str
    passed: bool | None
    at: datetime


class LearningEventPage(BaseModel):
    items: list[LearningEvent]
    total: int
    limit: int
    offset: int
