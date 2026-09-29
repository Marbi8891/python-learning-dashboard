"""Detección y mitigación según MITRE ATT&CK (ADR-0023): eventos de seguridad y contraseñas."""

import json
import logging

import jwt
import pytest

from app.password_policy import weakness
from app.rate_limit import auth_limiter
from app.security import ALGORITHM, create_access_token, looks_forged
from app.security_events import TECHNIQUE, Event, pseudonym
from tests.conftest import PASSWORD, login, register


@pytest.fixture
def events(caplog):
    """Eventos del logger pld.security, ya decodificados."""
    caplog.set_level(logging.INFO, logger="pld.security")

    def collected():
        return [json.loads(r.message) for r in caplog.records if r.name == "pld.security"]

    return collected


def names(entries):
    return [e["event"] for e in entries]


def test_every_event_has_an_attack_technique():
    assert set(TECHNIQUE) == set(Event)
    assert all(t.startswith("T1") for t in TECHNIQUE.values())


def test_failed_logins_are_recorded_without_personal_data(client, events, caplog):
    register(client)
    login(client, password="incorrecta-000")
    [entry] = [e for e in events() if e["event"] == Event.LOGIN_FAILED]
    assert entry["attack"] == "T1110"
    assert entry["account"] == pseudonym("ana@example.com")
    assert entry["known"] is True
    assert entry["path"] == "/api/auth/login"
    assert "ana@example.com" not in caplog.text and "testclient" not in caplog.text
    assert "incorrecta-000" not in caplog.text


def test_pseudonyms_correlate_but_do_not_reveal():
    assert pseudonym("Ana@Example.com ") == pseudonym("ana@example.com")
    assert pseudonym("ana@example.com") != pseudonym("eva@example.com")
    assert len(pseudonym("ana@example.com")) == 16


def test_lockout_and_ip_limit_are_recorded(client, events, monkeypatch):
    from app.rate_limit import login_failures

    register(client)
    monkeypatch.setattr(login_failures, "max_calls", 1)
    login(client, password="incorrecta-000")
    login(client)  # cuenta bloqueada
    for _ in range(5):
        login(client)  # agota el límite por IP
    recorded = names(events())
    assert Event.ACCOUNT_LOCKED in recorded
    assert Event.RATE_LIMITED in recorded


def test_successful_login_and_logout_all_are_recorded(client, events):
    register(client)
    token = login(client).json()["access_token"]
    client.post("/api/auth/logout-all", headers={"Authorization": f"Bearer {token}"})
    recorded = names(events())
    assert Event.LOGIN_OK in recorded and Event.LOGOUT_ALL in recorded


def test_forged_tokens_are_detected(client, events):
    register(client)
    forged = jwt.encode({"sub": "1", "ver": 0, "exp": 9999999999}, "otro-secreto" * 4, ALGORITHM)
    assert client.get("/api/users/me", headers={"Authorization": f"Bearer {forged}"}).status_code
    assert names(events()) == [Event.TOKEN_FORGED]


def test_garbage_or_expired_tokens_are_not_called_forged():
    assert not looks_forged("esto-no-es-un-jwt")
    assert not looks_forged(create_access_token(1, 0))
    none_alg = jwt.encode({"sub": "1"}, key=None, algorithm="none")
    assert looks_forged(none_alg)


def test_revoked_tokens_being_reused_are_detected(client, events, auth_headers):
    client.post("/api/auth/logout-all", headers=auth_headers)
    assert client.get("/api/users/me", headers=auth_headers).status_code == 401
    assert Event.TOKEN_REVOKED_USED in names(events())


def test_account_deletion_is_recorded(client, events, auth_headers):
    bad = client.post("/api/users/me/delete", json={"password": "nope"}, headers=auth_headers)
    assert bad.status_code == 403
    auth_limiter.reset()
    ok = client.post("/api/users/me/delete", json={"password": PASSWORD}, headers=auth_headers)
    assert ok.status_code == 204
    entries = events()
    assert {"event": Event.LOGIN_FAILED, "action": "delete"}.items() <= entries[-2].items()
    assert entries[-1]["event"] == Event.ACCOUNT_DELETED


def test_reset_request_is_recorded_even_for_unknown_emails(client, events):
    client.post("/api/auth/password-reset/request", json={"email": "nadie@example.com"})
    [entry] = events()
    assert entry["event"] == Event.RESET_REQUESTED and entry["known"] is False


def test_oversized_body_is_recorded(client, events, auth_headers):
    from app.config import get_settings

    big = b"a" * (get_settings().max_body_bytes + 1)
    client.put(
        "/api/pcap-state", content=big, headers={**auth_headers, "Content-Type": "text/plain"}
    )
    assert Event.BODY_TOO_LARGE in names(events())


@pytest.mark.parametrize(
    ("password", "email", "name"),
    [
        ("Password123", "", ""),
        ("  contraseña  ", "", ""),
        ("aaaaaaaaaa", "", ""),
        ("abababababab", "", ""),
        ("1234567890", "", ""),
        ("9876543210", "", ""),
        ("mariagarcia2024", "maria.g@example.com", "María García"),
        ("luciaperez!!", "lucia@example.com", ""),
    ],
)
def test_weak_passwords_are_rejected(password, email, name):
    assert weakness(password, email, name)


@pytest.mark.parametrize(
    "password", [PASSWORD, "nueva-contraseña-456", "tortuga-azul-en-bici", "83920174"]
)
def test_reasonable_passwords_are_accepted(password):
    assert weakness(password, "ana@example.com", "Ana") is None


def test_register_rejects_common_and_personal_passwords(client):
    common = register(client, password="password123")
    assert common.status_code == 422
    assert "más usadas" in common.json()["detail"]
    personal = register(client, email="roberto@example.com", password="roberto-2026")
    assert personal.status_code == 422
    assert register(client).status_code == 201


def test_reset_with_weak_password_keeps_the_link_usable(client, monkeypatch):
    from tests.test_account import _request_reset_link

    register(client)
    token = _request_reset_link(client, monkeypatch)
    url = "/api/auth/password-reset/confirm"
    weak = client.post(url, json={"token": token, "new_password": "qwertyuiop"})
    assert weak.status_code == 422
    auth_limiter.reset()
    good = client.post(url, json={"token": token, "new_password": "tortuga-azul-en-bici"})
    assert good.status_code == 204


def test_password_reset_lifts_a_malicious_lockout(client, monkeypatch):
    from app.rate_limit import login_failures
    from tests.test_account import _request_reset_link

    register(client)
    monkeypatch.setattr(login_failures, "max_calls", 2)
    for _ in range(2):
        login(client, password="incorrecta-000")  # un atacante bloquea la cuenta
    auth_limiter.reset()
    assert login(client).status_code == 429
    token = _request_reset_link(client, monkeypatch)
    new = "tortuga-azul-en-bici"
    url = "/api/auth/password-reset/confirm"
    assert client.post(url, json={"token": token, "new_password": new}).status_code == 204
    auth_limiter.reset()
    assert login(client, password=new).status_code == 200
