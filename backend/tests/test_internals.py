"""Ramas internas: SMTP, límite de intentos, concurrencia, configuración y scripts."""

import io
import json
import runpy
import ssl
import urllib.error
from types import SimpleNamespace

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
        ("postgres://u:p@h/db", "postgresql+psycopg://u:p@h/db?sslmode=require"),
        ("postgresql://u:p@h/db?a=1", "postgresql+psycopg://u:p@h/db?a=1&sslmode=require"),
        (
            "postgresql://u:p@h/db?sslmode=verify-full",
            "postgresql+psycopg://u:p@h/db?sslmode=verify-full",
        ),
        # Base de datos local o de docker-compose: sin TLS
        ("postgresql+psycopg://pld:pld@db:5432/pld", "postgresql+psycopg://pld:pld@db:5432/pld"),
        ("postgresql://u:p@localhost:5432/db", "postgresql+psycopg://u:p@localhost:5432/db"),
        ("sqlite:///./dev.db", "sqlite:///./dev.db"),
    ],
)
def test_database_url_gets_psycopg_driver_and_tls(url, expected):
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

    def starttls(self, context=None):
        self.tls = context

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
    # El certificado del servidor SMTP se verifica (contexto por defecto, ADR-0022)
    assert server.tls.verify_mode == ssl.CERT_REQUIRED and server.tls.check_hostname
    assert server.credentials == ("usuario", "clave")
    assert message["To"] == "ana@example.com" and message["Subject"] == "Asunto"


def test_send_email_failure_is_logged_not_raised(smtp, caplog):
    smtp.fail = True
    mailer.send_email("ana@example.com", "Asunto", "Cuerpo")  # no debe lanzar excepción
    assert "No se pudo enviar" in caplog.text
    assert "ana@example.com" not in caplog.text  # el email se enmascara en el log


def test_without_smtp_nothing_sensitive_is_logged(caplog):
    with caplog.at_level("WARNING", logger="pld.mailer"):
        mailer.send_email("ana@example.com", "Asunto", "token=secreto")
    assert "a***@example.com" in caplog.text
    assert "secreto" not in caplog.text and "ana@example.com" not in caplog.text


class FakeSMTPSSL(FakeSMTP):
    def __init__(self, host, port, timeout, context):
        super().__init__(host, port, timeout)
        self.tls = context

    def starttls(self, context=None):  # pragma: no cover - con SMTPS no se debe llamar
        raise AssertionError("SMTPS ya va cifrado: no se usa STARTTLS")


def test_send_email_on_port_465_uses_smtps(smtp, monkeypatch):
    monkeypatch.setattr(mailer.smtplib, "SMTP_SSL", FakeSMTPSSL)
    monkeypatch.setattr(get_settings(), "smtp_port", 465)
    mailer.send_email("ana@example.com", "Asunto", "Cuerpo")
    server, _ = smtp.sent[0]
    assert isinstance(server, FakeSMTPSSL) and server.port == 465
    assert server.tls.verify_mode == ssl.CERT_REQUIRED and server.tls.check_hostname


def test_test_email_command_sends_and_reports(smtp, capsys):
    assert mailer.main(["ana@example.com"]) == 0
    assert smtp.sent[0][1]["To"] == "ana@example.com"
    assert "a***@example.com" in capsys.readouterr().out


def test_test_email_command_shows_the_error(smtp, capsys):
    smtp.fail = True
    assert mailer.main(["ana@example.com"]) == 1
    assert "servidor caído" in capsys.readouterr().out


def test_test_email_command_without_smtp_or_recipient(capsys, monkeypatch):
    assert mailer.main(["ana@example.com"]) == 1
    assert "SMTP_HOST" in capsys.readouterr().out
    assert mailer.main([]) == 2
    monkeypatch.setattr("sys.argv", ["mailer.py"])
    with pytest.raises(SystemExit) as exit_info:  # python -m app.mailer sin argumentos
        runpy.run_path(mailer.__file__, run_name="__main__")
    assert exit_info.value.code == 2


class FakeResponse:
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


@pytest.fixture
def brevo(monkeypatch):
    """La API de Brevo simulada: guarda las peticiones; con `fail`, responde 401."""
    calls = SimpleNamespace(requests=[], fail=False)

    def fake_urlopen(request, timeout, context):
        calls.requests.append((request, context))
        if calls.fail:
            raise urllib.error.HTTPError(
                request.full_url, 401, "Unauthorized", {}, io.BytesIO(b'{"code":"unauthorized"}')
            )
        return FakeResponse()

    monkeypatch.setattr(mailer.urllib.request, "urlopen", fake_urlopen)
    settings = get_settings()
    monkeypatch.setattr(settings, "brevo_api_key", "clave-brevo")
    monkeypatch.setattr(settings, "smtp_host", "smtp.example.com")  # Brevo tiene prioridad
    monkeypatch.setattr(settings, "smtp_from", "Python Learning <yo@example.com>")
    return calls


def test_send_email_via_brevo_https(brevo):
    mailer.send_email("ana@example.com", "Asunto", "Cuerpo")
    request, context = brevo.requests[0]
    assert request.full_url == "https://api.brevo.com/v3/smtp/email"
    assert request.get_method() == "POST" and request.get_header("Api-key") == "clave-brevo"
    assert context.verify_mode == ssl.CERT_REQUIRED and context.check_hostname
    assert json.loads(request.data) == {
        "sender": {"name": "Python Learning", "email": "yo@example.com"},
        "to": [{"email": "ana@example.com"}],
        "subject": "Asunto",
        "textContent": "Cuerpo",
    }


def test_brevo_failure_is_logged_not_raised(brevo, caplog):
    brevo.fail = True
    mailer.send_email("ana@example.com", "Asunto", "token=secreto")
    assert "No se pudo enviar" in caplog.text
    assert "secreto" not in caplog.text and "ana@example.com" not in caplog.text


def test_brevo_sender_without_name_gets_a_default(brevo, monkeypatch):
    monkeypatch.setattr(get_settings(), "smtp_from", "yo@example.com")
    mailer.send_email("ana@example.com", "Asunto", "Cuerpo")
    sender = json.loads(brevo.requests[0][0].data)["sender"]
    assert sender == {"name": "Python Learning Dashboard", "email": "yo@example.com"}


def test_test_email_command_shows_brevo_error(brevo, capsys):
    assert mailer.main(["ana@example.com"]) == 0
    assert "(Brevo)" in capsys.readouterr().out
    brevo.fail = True
    assert mailer.main(["ana@example.com"]) == 1
    out = capsys.readouterr().out
    assert "401" in out and "unauthorized" in out  # el motivo que da Brevo


def test_health_reports_email_with_brevo_only(client, monkeypatch):
    monkeypatch.setattr(get_settings(), "brevo_api_key", "clave-brevo")
    assert client.get("/api/v1/health").json()["email"] is True


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
    assert "Seed completado: 27 lecciones" in capsys.readouterr().out


def test_postgres_engine_survives_idle_connections():
    # Neon suspende la base de datos sin uso: las conexiones del pool se comprueban antes de usarse
    url = Settings(
        database_url="postgresql://u:p@ep-x.eu-central-1.aws.neon.tech/pld?sslmode=require"
    ).database_url
    engine = database._make_engine(url)
    assert engine.pool._pre_ping is True
    assert engine.pool._recycle == 300
    assert engine.dialect.driver == "psycopg"
