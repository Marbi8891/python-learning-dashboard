"""Modelos de la base de datos."""

from datetime import datetime

from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
    true,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Module(Base):
    __tablename__ = "modules"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(50), unique=True)
    title: Mapped[str] = mapped_column(String(100))
    position: Mapped[int]

    lessons: Mapped[list["Lesson"]] = relationship(
        back_populates="module",
        order_by="Lesson.position",
        cascade="all, delete-orphan",
    )


class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(50), unique=True)
    module_id: Mapped[int] = mapped_column(ForeignKey("modules.id"), index=True)
    title: Mapped[str] = mapped_column(String(150))
    position: Mapped[int]
    theory: Mapped[str | None] = mapped_column(Text)
    example_code: Mapped[str | None] = mapped_column(Text)
    exercise: Mapped[str | None] = mapped_column(Text)
    sources: Mapped[list[dict[str, str]]] = mapped_column(JSON, default=list)
    starter: Mapped[str | None] = mapped_column(Text)
    example_stdin: Mapped[str] = mapped_column(Text, default="", server_default="")
    exercise_stdin: Mapped[str] = mapped_column(Text, default="", server_default="")
    example_in_browser: Mapped[bool] = mapped_column(default=True, server_default=true())
    checks: Mapped[list[dict[str, str]]] = mapped_column(
        JSON, default=list, server_default=text("'[]'")
    )
    assistant: Mapped[dict] = mapped_column(JSON, default=dict, server_default=text("'{}'"))
    quiz: Mapped[list[dict]] = mapped_column(JSON, default=list, server_default=text("'[]'"))
    challenge: Mapped[dict] = mapped_column(JSON, default=dict, server_default=text("'{}'"))

    module: Mapped[Module] = relationship(back_populates="lessons")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(254), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    display_name: Mapped[str] = mapped_column(String(80))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    privacy_accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    # Se incrementa al cambiar la contraseña: invalida todos los tokens emitidos antes
    token_version: Mapped[int] = mapped_column(default=0, server_default="0")


class LessonProgress(Base):
    """Lección completada por un usuario (como mucho una fila por pareja)."""

    __tablename__ = "lesson_progress"
    __table_args__ = (UniqueConstraint("user_id", "lesson_id", name="uq_progress_user_lesson"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id", ondelete="CASCADE"))
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class ExerciseAttempt(Base):
    """Intento de ejercicio. Los tests se ejecutan en el navegador (ver ADR-0003)."""

    __tablename__ = "exercise_attempts"
    __table_args__ = (Index("ix_attempts_user_lesson", "user_id", "lesson_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id", ondelete="CASCADE"))
    code: Mapped[str] = mapped_column(Text)
    passed: Mapped[bool]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class PasswordResetToken(Base):
    """Enlace de recuperación de contraseña. Se guarda solo el hash SHA-256 del token."""

    __tablename__ = "password_reset_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
