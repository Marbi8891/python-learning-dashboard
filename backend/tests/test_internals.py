"""Ramas internas: SMTP, límite de intentos, concurrencia, configuración y scripts."""

import runpy

import pytest
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app import database, mailer, seed
from app.config import Settings, get_settings
from app.models import Lesson, LessonProgress, User
from app.rate_limit import RateLimiter
from app.routers.progress import mark_completed
from app.security import get_jwt_secret, hash_password


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("postgres://u:p@h/db", "postgresql+psycopg://u:p@h/db"),
        ("postgresql://u:p@h/db", "postgresql+psycopg://u:p@h/db"),
        ("postgresql+psycopg://u:p@h/db", "postgresql+psycopg://u:p@h/db"),
        ("sqlite:///./dev.db", "sqlite:///./dev.db"),
    ],
)
def test_database_url_gets_psycopg_driver(url, expected):
    assert Settings(database_url=url).database_url == expected


def test_missing_or_short_jwt_secret_is_rejected(monkeypatch):
    for bad in (None, "corto"):
        monkeypatch.setattr(get_settings(), "jwt_secret", bad)
        with pytest.raises(RuntimeError, match="JWT_SECRET"):
            get_jwt_secret()


def test_rate_limiter_window_expires(monkeypatch):
    now = [1000.0]
    monkeypatch.setattr("app.rate_limit.time.monotonic", lambda: now[0])
    limiter = RateLimiter(max_calls=2, window_seconds=60)
    assert limiter.hit("ip") and limiter.hit("ip")
    assert not limiter.hit("ip")
    now[0] += 61  # pasa la ventana: los intentos antiguos caducan
    assert limiter.hit("ip")


def test_get_db_opens_and_closes_session(monkeypatch):
    closed = []

    class FakeSession:
        def close(self):
            closed.append(True)

    monkeypatch.setattr(database, "SessionLocal", FakeSession)
    generator = database.get_db()
    assert isinstance(next(generator), FakeSession)
    with pytest.raises(StopIteration):
        next(generator)
    assert closed == [True]


class FakeSMTP:
    sent = []
    fail = False

    def __init__(self, host, port, timeout):
        self.host, self.port = host, port

    def __enter__(self):
        if FakeSMTP.fail:
            raise OSError("servidor caído")
        return self

    def __exit__(self, *exc):
        return False

    def starttls(self):
        self.tls = True

    def login(self, user, password):
        self.credentials = (user, password)

    def send_message(self, message):
        FakeSMTP.sent.append((self, message))


@pytest.fixture
def smtp(monkeypatch):
    FakeSMTP.sent, FakeSMTP.fail = [], False
    monkeypatch.setattr(mailer.smtplib, "SMTP", FakeSMTP)
    settings = get_settings()
    monkeypatch.setattr(settings, "smtp_host", "smtp.example.com")
    monkeypatch.setattr(settings, "smtp_user", "usuario")
    monkeypatch.setattr(settings, "smtp_password", "clave")
    return FakeSMTP


def test_send_email_via_smtp_with_tls(smtp):
    mailer.send_email("ana@example.com", "Asunto", "Cuerpo")
    server, message = smtp.sent[0]
    assert server.tls and server.credentials == ("usuario", "clave")
    assert message["To"] == "ana@example.com" and message["Subject"] == "Asunto"


def test_send_email_failure_is_logged_not_raised(smtp, caplog):
    smtp.fail = True
    mailer.send_email("ana@example.com", "Asunto", "Cuerpo")  # no debe lanzar excepción
    assert "No se pudo enviar" in caplog.text


def test_mark_completed_survives_concurrent_insert(client):
    """Si otra petición inserta la misma fila entre el SELECT y el INSERT, no falla."""
    session = sessionmaker(bind=client.engine, expire_on_commit=False)()
    user = User(email="c@example.com", password_hash=hash_password("x" * 8), display_name="C")
    session.add(user)
    session.commit()
    lesson_id = session.scalar(select(Lesson.id).where(Lesson.slug == "variables"))
    session.add(LessonProgress(user_id=user.id, lesson_id=lesson_id))  # la "otra petición"
    session.commit()

    real_scalar = session.scalar
    calls = []

    def scalar_that_misses_first_time(stmt):
        calls.append(stmt)
        return None if len(calls) == 1 else real_scalar(stmt)

    session.scalar = scalar_that_misses_first_time
    progress = mark_completed(session, user.id, lesson_id)
    assert progress is not None and progress.lesson_id == lesson_id
    session.close()


def test_seed_script_entry_point(client, monkeypatch, capsys):
    monkeypatch.setattr(database, "SessionLocal", sessionmaker(bind=client.engine))
    runpy.run_path(seed.__file__, run_name="__main__")
    assert "Seed completado: 15 lecciones" in capsys.readouterr().out
