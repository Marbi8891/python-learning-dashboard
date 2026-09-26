"""Conexión a la base de datos y sesión por petición."""

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings


class Base(DeclarativeBase):
    pass


def _make_engine(url: str):
    if url.startswith("sqlite"):
        # SQLite necesita este ajuste para usarse desde los hilos de FastAPI
        return create_engine(url, connect_args={"check_same_thread": False})
    # PostgreSQL gestionado (Neon) suspende la base de datos sin uso y cierra las conexiones:
    # pre_ping descarta las conexiones muertas antes de usarlas en vez de devolver un error 500.
    return create_engine(url, pool_pre_ping=True, pool_recycle=300)


engine = _make_engine(get_settings().database_url)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Iterator[Session]:
    """Dependencia de FastAPI: abre una sesión y la cierra al terminar."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
