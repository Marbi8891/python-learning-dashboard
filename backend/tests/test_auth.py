"""Registro, login, token y límite de intentos."""

from datetime import UTC, datetime, timedelta

import jwt

from app.security import ALGORITHM, get_jwt_secret
from tests.conftest import login, register


def test_register_returns_user_without_password(client):
    response = register(client, email="  Ana@Example.COM ")
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "ana@example.com"  # normalizado
    assert "password" not in body and "password_hash" not in body


def test_register_duplicate_email_conflict(client):
    register(client)
    assert register(client, email="ANA@example.com").status_code == 409


def test_register_validates_input(client):
    assert register(client, email="no-es-un-email").status_code == 422
    assert register(client, password="corta").status_code == 422


def test_password_is_stored_hashed(client):
    register(client)
    with client.engine.connect() as conn:
        stored = conn.exec_driver_sql("SELECT password_hash FROM users").scalar_one()
    assert stored.startswith("$argon2")


def test_login_and_me(client):
    register(client)
    token = login(client).json()["access_token"]
    me = client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["display_name"] == "Ana"


def test_login_wrong_password_and_unknown_email_same_error(client):
    register(client)
    wrong = login(client, password="otra-contraseña")
    unknown = login(client, email="nadie@example.com")
    assert wrong.status_code == unknown.status_code == 401
    assert wrong.json() == unknown.json()  # no revela qué emails existen


def test_protected_endpoint_rejects_missing_invalid_and_expired_tokens(client):
    assert client.get("/api/users/me").status_code == 401
    bad = {"Authorization": "Bearer token-falso"}
    assert client.get("/api/users/me", headers=bad).status_code == 401

    register(client)
    expired = jwt.encode(
        {"sub": "1", "exp": datetime.now(UTC) - timedelta(minutes=1)},
        get_jwt_secret(),
        algorithm=ALGORITHM,
    )
    headers = {"Authorization": f"Bearer {expired}"}
    assert client.get("/api/users/me", headers=headers).status_code == 401


def test_login_rate_limited(client):
    register(client)
    codes = [login(client, password="incorrecta-123").status_code for _ in range(5)]
    assert 429 in codes  # registro + 4 logins agotan el límite de 5 por minuto
