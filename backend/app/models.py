"""Modelos de la base de datos."""

from sqlalchemy import ForeignKey, String, Text
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

    module: Mapped[Module] = relationship(back_populates="lessons")
