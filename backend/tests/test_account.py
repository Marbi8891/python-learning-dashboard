"""Privacidad (RGPD), exportación, borrado de cuenta y recuperación de contraseña."""

import re

from app.models import CourseState, ExerciseAttempt, LessonProgress, PcapState, User
from tests.conftest import PASSWORD, login, register


def test_register_requires_privacy_acceptance(client):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "x@example.com",
            "password": PASSWORD,
            "display_name": "X",
            "accept_privacy": False,
        },
    )
    assert response.status_code == 422


def test_export_contains_all_user_data(client, auth_headers):
    client.put("/api/progress/variables", headers=auth_headers)
    client.post(
        "/api/lessons/tipos/attempts",
        json={"code": "print(1)", "passed": False},
        headers=auth_headers,
    )
    data = client.get("/api/users/me/export", headers=auth_headers).json()
    assert data["user"]["email"] == "ana@example.com"
    assert data["privacy_accepted_at"] is not None
    assert [p["lesson_slug"] for p in data["progress"]] == ["variables"]
    assert data["attempts"][0]["lesson_slug"] == "tipos"
    assert "password_hash" not in str(data)


def test_delete_account_requires_password(client, auth_headers):
    response = client.post(
        "/api/users/me/delete", json={"password": "incorrecta"}, headers=auth_headers
    )
    assert response.status_code == 403
    assert client.get("/api/users/me", headers=auth_headers).status_code == 200


def test_delete_account_removes_everything(client, auth_headers):
    client.put("/api/progress/variables", headers=auth_headers)
    client.post(
        "/api/lessons/tipos/attempts", json={"code": "x", "passed": True}, headers=auth_headers
    )
    client.put("/api/pcap-state", json={"data": {"bestCombo": 3}}, headers=auth_headers)
    client.put("/api/course-state/java", json={"data": {"bestCombo": 1}}, headers=auth_headers)
    response = client.post(
        "/api/users/me/delete", json={"password": PASSWORD}, headers=auth_headers
    )
    assert response.status_code == 204
    assert client.get("/api/users/me", headers=auth_headers).status_code == 401
    with client.engine.connect() as conn:
        for model in (User, LessonProgress, ExerciseAttempt, PcapState, CourseState):
            count = conn.exec_driver_sql(f"SELECT COUNT(*) FROM {model.__tablename__}").scalar_one()
            assert count == 0, f"Quedan filas en {model.__tablename__}"
    # El email vuelve a estar libre
    assert register(client).status_code == 201


def _request_reset_link(client, monkeypatch, email="ana@example.com") -> str | None:
    """Pide el enlace y lo lee del email que se habría enviado (nunca del log, ADR-0022)."""
    sent = []
    monkeypatch.setattr("app.routers.auth.send_email", lambda to, subject, body: sent.append(body))
    response = client.post("/api/auth/password-reset/request", json={"email": email})
    assert response.status_code == 202
    match = re.search(r"token=([\w-]+)", sent[0]) if sent else None
    return match.group(1) if match else None


def test_reset_request_same_answer_for_unknown_email(client, caplog):
    register(client)
    known = client.post("/api/auth/password-reset/request", json={"email": "ana@example.com"})
    unknown = client.post("/api/auth/password-reset/request", json={"email": "nadie@example.com"})
    assert known.status_code == unknown.status_code == 202
    assert known.json() == unknown.json()


def test_password_reset_flow_invalidates_old_sessions(client, monkeypatch, auth_headers):
    token = _request_reset_link(client, monkeypatch)
    assert token, "El email de recuperación debe llevar el enlace"

    new_password = "nueva-contraseña-456"
    confirm = client.post(
        "/api/auth/password-reset/confirm", json={"token": token, "new_password": new_password}
    )
    assert confirm.status_code == 204
    # La sesión abierta antes del cambio ya no vale
    assert client.get("/api/users/me", headers=auth_headers).status_code == 401
    assert login(client).status_code == 401
    assert login(client, password=new_password).status_code == 200
    # El enlace es de un solo uso
    again = client.post(
        "/api/auth/password-reset/confirm", json={"token": token, "new_password": "otra-mas-789"}
    )
    assert again.status_code == 400


def test_reset_with_invalid_or_expired_token(client, monkeypatch):
    register(client)
    bad = client.post(
        "/api/auth/password-reset/confirm",
        json={"token": "x" * 43, "new_password": "nueva-contraseña-456"},
    )
    assert bad.status_code == 400

    token = _request_reset_link(client, monkeypatch)
    with client.engine.begin() as conn:
        conn.exec_driver_sql("UPDATE password_reset_tokens SET expires_at = '2000-01-01 00:00:00'")
    expired = client.post(
        "/api/auth/password-reset/confirm",
        json={"token": token, "new_password": "nueva-contraseña-456"},
    )
    assert expired.status_code == 400


def test_new_reset_request_invalidates_previous_link(client, monkeypatch):
    register(client)
    first = _request_reset_link(client, monkeypatch)
    second = _request_reset_link(client, monkeypatch)
    assert first != second
    old = client.post(
        "/api/auth/password-reset/confirm",
        json={"token": first, "new_password": "nueva-contraseña-456"},
    )
    assert old.status_code == 400
