"""Esquemas de entrada/salida de la API (lo que ve el frontend)."""

import json
from datetime import date, datetime
from typing import Annotated, Literal

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
            raise ValueError("Debes confirmar que has leído la política de privacidad")
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

# Cursos de DAW y de las academias (Excel profesional) que se pueden guardar en la cuenta; tienen
# que coincidir con SYNCED_COURSES de frontend/js/catalog.js (tests/test_course_catalog.py).
# Además, "learn": el progreso por conceptos del núcleo educativo, "game": XP, racha y
# logros de la web, que antes solo vivían en el navegador, y "planner": el planificador diario
# (tiempo disponible, fechas de exámenes y entregas, tareas hechas, pospuestas o rechazadas) y
# "career": el itinerario profesional (unidades, evaluaciones, evidencias de proyecto y plan,
# DEC-012; los datos económicos no se guardan aquí: solo viven en el navegador).
# Lista cerrada: evita que un cliente cree documentos con nombres arbitrarios.
COURSES = (
    "sql",
    "js",
    "java",
    "entornos",
    "marcas",
    "programacion",
    "excel",
    "learn",
    "game",
    "planner",
    "career",
)


class PcapStateIn(BaseModel):
    data: dict
    # Versión que leyó la app. Si no coincide con la de la cuenta, 409 (otra pestaña guardó antes).
    # Sin ella se guarda sin comprobar, como hacían las versiones anteriores de la app.
    version: int | None = Field(default=None, ge=0)

    @field_validator("data")
    @classmethod
    def not_too_big(cls, data: dict) -> dict:
        if len(json.dumps(data)) > MAX_PCAP_STATE_BYTES:
            raise ValueError("Los datos de preparación son demasiado grandes")
        return data


class PcapStateOut(BaseModel):
    data: dict
    updated_at: datetime | None
    version: int = 0


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
    verified_exams: list[dict] = []
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


# ---------- Derechos de acceso comerciales ----------


class EntitlementOut(BaseModel):
    """Derecho activo de una cuenta. Nunca expone identificadores del proveedor de pago."""

    model_config = ConfigDict(from_attributes=True)

    feature_key: str
    starts_at: datetime
    ends_at: datetime | None


# ---------- Hitos verificados (#109) ----------

QuestionId = Annotated[str, Field(min_length=1, max_length=40)]
Option = Annotated[int, Field(ge=0, le=20)]


class VerifiedExamStart(BaseModel):
    """Simulacro empezado: el navegador pinta estas preguntas (ya tiene su texto en pcap.json)."""

    id: int
    exam_code: str
    question_ids: list[str]
    started_at: datetime
    deadline: datetime


class VerifiedExamAnswers(BaseModel):
    """Opciones marcadas por pregunta. Las que no aparecen cuentan como sin contestar."""

    answers: Annotated[
        dict[QuestionId, Annotated[list[Option], Field(max_length=10)]], Field(max_length=60)
    ]


class VerifiedExamOut(BaseModel):
    id: int
    exam_code: str
    status: str
    started_at: datetime
    finished_at: datetime | None
    correct: int | None
    total: int
    score: int | None
    passed: bool


class VerifiedSummary(BaseModel):
    pass_mark: int
    best_score: int | None
    passed: bool
    exams: list[VerifiedExamOut]


# ---------- IA (docs/architecture/NEXARO_INTEGRATION_CONTRACT.md) ----------
# extra="forbid": el navegador no puede elegir usuario, modelo, agente, temperatura ni prompt de
# sistema. Todo eso lo pone el servidor.


class AiTurn(BaseModel):
    """Un turno anterior de la conversación (solo vive en el navegador; PLD no lo guarda)."""

    model_config = ConfigDict(extra="forbid")

    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=2000)


def _not_blank(value: str, message: str) -> str:
    if not value.strip():
        raise ValueError(message)
    return value


class AiLessonRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # v1: solo el curso de Python, el único cuyas lecciones están en la base de datos (D-05)
    course: Literal["python"] = "python"
    lesson_slug: str = Field(min_length=1, max_length=50)
    # Solo si el alumno marca «Enviar mi código»: puede llevar datos personales
    code: str = Field(default="", max_length=8000)
    locale: Literal["es", "en"] = "es"
    # Optativa en los modos que no la necesitan (explicar un error, revisar código)
    question: str = Field(default="", max_length=2000)

    @field_validator("question")
    @classmethod
    def strip_question(cls, value: str) -> str:
        return value.strip()


class AiRequest(AiLessonRequest):
    question: str = Field(min_length=1, max_length=2000)

    @field_validator("question")
    @classmethod
    def question_not_blank(cls, value: str) -> str:
        return _not_blank(value, "Escribe tu pregunta")


class AiChatRequest(AiRequest):
    history: list[AiTurn] = Field(default_factory=list, max_length=6)


class AiHintRequest(AiRequest):
    # Pistas graduadas: de la idea general (1) a una guía paso a paso sin la solución (3)
    hint_level: int = Field(default=1, ge=1, le=3)


class AiErrorRequest(AiLessonRequest):
    # El error que mostró la consola. El runner ya lo limita al código del alumno (frontend/py)
    error: str = Field(min_length=1, max_length=4000)

    @field_validator("error")
    @classmethod
    def error_not_blank(cls, value: str) -> str:
        return _not_blank(value, "Falta el error que quieres entender")


class AiReviewRequest(AiLessonRequest):
    # Revisar código exige enviarlo: es texto, nadie lo ejecuta en el servidor
    code: str = Field(min_length=1, max_length=8000)

    @field_validator("code")
    @classmethod
    def code_not_blank(cls, value: str) -> str:
        return _not_blank(value, "Falta el código que quieres revisar")


class AiAnswer(BaseModel):
    """Lo que ve el alumno: texto generado por IA que nunca es la evaluación oficial."""

    answer: str
    mode: Literal["chat", "hint", "explain-error", "review-code"]
    ai_generated: Literal[True] = True
    official_evaluation: Literal[False] = False
    request_id: str
