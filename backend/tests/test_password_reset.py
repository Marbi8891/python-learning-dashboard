"""Recuperación de contraseña: rutas, token, caducidad y ataques contra el flujo.

El email nunca se envía: `outbox` sustituye a `send_email` y guarda destinatario, asunto y cuerpo.
"""

import hashlib
import json
import logging
import re
from datetime import UTC, datetime

import pytest

from app.config import get_settings
from app.rate_limit import auth_limiter
from app.routers import auth
from app.security_events import Event
from tests.conftest import PASSWORD, login, register

NEW_PASSWORD = "nueva-contraseña-456"
ROUTES = [  # (solicitud, confirmación): alias nuevo y ruta original (web y Android)
    ("/api/v1/auth/forgot-password", "/api/v1/auth/reset-password"),
    ("/api/auth/password-reset/request", "/api/auth/password-reset/confirm"),
]


@pytest.fixture
def outbox(monkeypatch):
    sent = []
    monkeypatch.setattr(
        "app.routers.auth.send_email",
        lambda to, subject, body: sent.append({"to": to, "subject": subject, "body": body}),
    )
    return sent


def _token(mail) -> str:
    return re.search(r"token=([\w-]+)", mail["body"]).group(1)


def _security_events(caplog):
    return [json.loads(r.message) for r in caplog.records if r.name == "pld.security"]


@pytest.mark.parametrize(("request_path", "confirm_path"), ROUTES)
def test_full_flow_on_both_routes(client, outbox, request_path, confirm_path):
    register(client)
    assert client.post(request_path, json={"email": "ana@example.com"}).status_code == 202
    mail = outbox[0]
    assert mail["to"] == "ana@example.com" and mail["subject"] == "Restablecer tu contraseña"
    link = re.search(r"\S+token=[\w-]+", mail["body"]).group(0)
    assert link.startswith(f"{get_settings().frontend_url}/#/restablecer?token=")
    assert PASSWORD not in mail["body"]  # el email solo lleva el enlace, nunca una contraseña

    done = client.post(confirm_path, json={"token": _token(mail), "new_password": NEW_PASSWORD})
    assert done.status_code == 204 and done.content == b""
    assert login(client, password=NEW_PASSWORD).status_code == 200


@pytest.mark.parametrize("email", ["", "no-es-un-email", "a" * 300 + "@example.com"])
def test_request_rejects_malformed_email(client, outbox, email):
    response = client.post("/api/v1/auth/forgot-password", json={"email": email})
    assert response.status_code == 422 and outbox == []


def test_request_answer_does_not_reveal_accounts(client, outbox):
    register(client)
    known = client.post("/api/v1/auth/forgot-password", json={"email": "ana@example.com"})
    unknown = client.post("/api/v1/auth/forgot-password", json={"email": "nadie@example.com"})
    assert (known.status_code, known.json()) == (unknown.status_code, unknown.json())
    assert len(outbox) == 1  # solo la cuenta que existe recibe el email


def test_token_is_stored_only_as_hash(client, outbox):
    register(client)
    client.post("/api/v1/auth/forgot-password", json={"email": "ana@example.com"})
    token = _token(outbox[0])
    assert len(token) >= 43  # 32 bytes aleatorios en base64url
    with client.engine.connect() as conn:
        rows = conn.exec_driver_sql("SELECT * FROM password_reset_tokens").all()
    assert len(rows) == 1
    assert token not in str(rows)
    assert hashlib.sha256(token.encode()).hexdigest() in str(rows)


def test_tampered_token_is_rejected(client, outbox):
    register(client)
    client.post("/api/v1/auth/forgot-password", json={"email": "ana@example.com"})
    token = _token(outbox[0])
    tampered = token[:-1] + ("A" if token[-1] != "A" else "B")
    response = client.post(
        "/api/v1/auth/reset-password", json={"token": tampered, "new_password": NEW_PASSWORD}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == auth.INVALID_LINK


def test_token_expires_exactly_at_expires_at(client, outbox, monkeypatch):
    register(client)
    client.post("/api/v1/auth/forgot-password", json={"email": "ana@example.com"})
    with client.engine.connect() as conn:
        stored = conn.exec_driver_sql("SELECT expires_at FROM password_reset_tokens").scalar_one()
    expires = datetime.fromisoformat(str(stored)).replace(tzinfo=UTC)

    class Frozen(datetime):
        @classmethod
        def now(cls, tz=None):
            return expires  # now == expires_at: ya no vale

    monkeypatch.setattr(auth, "datetime", Frozen)
    response = client.post(
        "/api/v1/auth/reset-password",
        json={"token": _token(outbox[0]), "new_password": NEW_PASSWORD},
    )
    assert response.status_code == 400


def test_token_of_a_missing_user_is_rejected(client, outbox):
    register(client)
    client.post("/api/v1/auth/forgot-password", json={"email": "ana@example.com"})
    with client.engine.begin() as conn:
        conn.exec_driver_sql("UPDATE password_reset_tokens SET user_id = 9999")
    response = client.post(
        "/api/v1/auth/reset-password",
        json={"token": _token(outbox[0]), "new_password": NEW_PASSWORD},
    )
    assert response.status_code == 400


def test_failed_reset_is_a_security_event(client, caplog):
    caplog.set_level(logging.INFO, logger="pld.security")
    client.post(
        "/api/v1/auth/reset-password", json={"token": "x" * 43, "new_password": NEW_PASSWORD}
    )
    entry = _security_events(caplog)[-1]
    assert entry["event"] == Event.RESET_FAILED and entry["attack"] == "T1110"


def test_guessing_tokens_hits_the_ip_limit(client):
    statuses = set()
    for _ in range(get_settings().auth_rate_limit_per_minute + 1):
        statuses.add(
            client.post(
                "/api/v1/auth/reset-password",
                json={"token": "x" * 43, "new_password": NEW_PASSWORD},
            ).status_code
        )
    assert 429 in statuses


@pytest.mark.parametrize(
    "headers",
    [
        {"Host": "evil.example"},
        {"X-Forwarded-Host": "evil.example", "X-Forwarded-Proto": "http"},
        {"Origin": "https://evil.example", "Referer": "https://evil.example/"},
    ],
)
def test_link_ignores_request_headers(client, outbox, headers):
    """Password reset poisoning: el enlace sale de FRONTEND_URL, no de la petición."""
    register(client)
    client.post("/api/v1/auth/forgot-password", json={"email": "ana@example.com"}, headers=headers)
    assert "evil.example" not in outbox[0]["body"]
    assert f"{get_settings().frontend_url}/#/restablecer?token=" in outbox[0]["body"]


def test_secrets_never_reach_logs_or_responses(client, outbox, caplog):
    caplog.set_level(logging.DEBUG)
    register(client)
    requested = client.post("/api/v1/auth/forgot-password", json={"email": "ana@example.com"})
    token = _token(outbox[0])
    done = client.post(
        "/api/v1/auth/reset-password", json={"token": token, "new_password": NEW_PASSWORD}
    )
    assert token not in requested.text and token not in done.text
    for secret in (token, NEW_PASSWORD, "ana@example.com"):
        assert secret not in caplog.text


def test_oversized_payloads_are_rejected(client):
    long_token = client.post(
        "/api/v1/auth/reset-password", json={"token": "x" * 5000, "new_password": NEW_PASSWORD}
    )
    long_password = client.post(
        "/api/v1/auth/reset-password", json={"token": "x" * 43, "new_password": "a" * 129}
    )
    huge = client.post(
        "/api/v1/auth/forgot-password",
        content=b'{"email": "' + b"a" * (get_settings().max_body_bytes + 1) + b'"}',
        headers={"Content-Type": "application/json"},
    )
    assert long_token.status_code == long_password.status_code == 422
    assert huge.status_code == 413


def test_second_use_after_success_is_rejected(client, outbox):
    register(client)
    client.post("/api/v1/auth/forgot-password", json={"email": "ana@example.com"})
    token = _token(outbox[0])
    first = client.post(
        "/api/v1/auth/reset-password", json={"token": token, "new_password": NEW_PASSWORD}
    )
    auth_limiter.reset()
    replay = client.post(
        "/api/v1/auth/reset-password", json={"token": token, "new_password": "otra-mas-789"}
    )
    assert (first.status_code, replay.status_code) == (204, 400)
    assert login(client, password="otra-mas-789").status_code == 401
    with client.engine.connect() as conn:
        used_at = conn.exec_driver_sql("SELECT used_at FROM password_reset_tokens").scalar_one()
    assert used_at is not None
