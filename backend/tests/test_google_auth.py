"""Pruebas del inicio de sesión con Google sin llamadas reales a Google."""

import time
from types import SimpleNamespace

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import User
from app.rate_limit import auth_limiter
from app.routers import auth
from tests.conftest import PASSWORD, login, register


def configure_google(monkeypatch, claims):
    monkeypatch.setattr(
        auth,
        "get_settings",
        lambda: SimpleNamespace(google_client_id="test-google-client-id"),
    )
    monkeypatch.setattr(auth, "verify_oauth2_token", lambda token, request, client_id: claims)


def test_google_login_creates_account_and_session(client, monkeypatch):
    configure_google(
        monkeypatch,
        {
            "email": "google@example.com",
            "email_verified": True,
            "name": "Google Alumno",
            "sub": "google-subject-123",
        },
    )
    response = client.post(
        "/api/v1/auth/google",
        json={"credential": "x" * 40, "accept_privacy": True},
    )
    assert response.status_code == 200
    assert response.json()["access_token"]
    me = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {response.json()['access_token']}"},
    )
    assert me.status_code == 200
    assert me.json()["email"] == "google@example.com"
    assert me.json()["display_name"] == "Google Alumno"


def test_google_login_reuses_existing_account(client, monkeypatch):
    assert register(client, email="ana@example.com", name="Ana").status_code == 201
    with Session(client.engine) as db:
        user = db.scalar(select(User).where(User.email == "ana@example.com"))
        user.privacy_accepted_at = None
        db.commit()
    configure_google(
        monkeypatch,
        {
            "email": "ANA@example.com",
            "email_verified": True,
            "name": "Otro nombre",
            "sub": "sub-1",
        },
    )
    response = client.post(
        "/api/v1/auth/google",
        json={"credential": "x" * 40, "accept_privacy": True},
    )
    assert response.status_code == 200
    me = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {response.json()['access_token']}"},
    )
    assert me.status_code == 200
    assert me.json()["display_name"] == "Ana"


def test_google_login_rejects_unverified_email(client, monkeypatch):
    configure_google(
        monkeypatch,
        {
            "email": "unverified@example.com",
            "email_verified": False,
            "name": "Alumno",
            "sub": "sub-2",
        },
    )
    response = client.post(
        "/api/v1/auth/google",
        json={"credential": "x" * 40, "accept_privacy": True},
    )
    assert response.status_code == 401


def test_google_login_requires_privacy_for_new_account(client, monkeypatch):
    configure_google(
        monkeypatch,
        {
            "email": "privacy@example.com",
            "email_verified": True,
            "name": "Alumno",
            "sub": "sub-3",
        },
    )
    response = client.post(
        "/api/v1/auth/google",
        json={"credential": "x" * 40, "accept_privacy": False},
    )
    assert response.status_code == 400


def test_google_login_rejects_invalid_id_token(client, monkeypatch):
    configure_google(monkeypatch, {})

    def invalid_token(token, request, client_id):
        raise ValueError("invalid token")

    monkeypatch.setattr(auth, "verify_oauth2_token", invalid_token)
    response = client.post(
        "/api/v1/auth/google",
        json={"credential": "x" * 40, "accept_privacy": True},
    )
    assert response.status_code == 401


def test_google_login_unconfigured(client, monkeypatch):
    monkeypatch.setattr(auth, "get_settings", lambda: SimpleNamespace(google_client_id=None))
    response = client.post(
        "/api/v1/auth/google",
        json={"credential": "x" * 40, "accept_privacy": True},
    )
    assert response.status_code == 503


def test_google_login_handles_concurrent_account_creation(client, monkeypatch):
    configure_google(
        monkeypatch,
        {
            "email": "race@example.com",
            "email_verified": True,
            "name": "Carrera",
            "sub": "sub-race",
        },
    )
    original_commit = Session.commit
    raised = False

    def conflict_once(session):
        nonlocal raised
        if not raised:
            raised = True
            raise IntegrityError("insert", {}, RuntimeError("duplicate email"))
        return original_commit(session)

    monkeypatch.setattr(Session, "commit", conflict_once)
    response = client.post(
        "/api/v1/auth/google",
        json={"credential": "x" * 40, "accept_privacy": True},
    )
    assert response.status_code == 409


# ---------- Borrar una cuenta de Google (su contraseña es aleatoria) ----------


def google_account(client, monkeypatch, email="google@example.com"):
    """Crea la cuenta entrando con Google y devuelve las cabeceras de su sesión."""
    claims = {"email": email, "email_verified": True, "name": "G", "sub": "s"}
    configure_google(monkeypatch, claims)
    response = client.post(
        "/api/v1/auth/google", json={"credential": "x" * 40, "accept_privacy": True}
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def fresh_claims(email="google@example.com", age_seconds=0):
    issued = int(time.time()) - age_seconds
    return {"email": email, "email_verified": True, "sub": "s", "iat": issued}


def delete_with_google(client, headers):
    return client.post(
        "/api/v1/users/me/delete", json={"google_credential": "y" * 40}, headers=headers
    )


def test_google_account_can_be_deleted_by_confirming_with_google(client, monkeypatch):
    headers = google_account(client, monkeypatch)
    configure_google(monkeypatch, fresh_claims(email="GOOGLE@example.com"))
    assert delete_with_google(client, headers).status_code == 204
    assert client.get("/api/v1/users/me", headers=headers).status_code == 401
    with Session(client.engine) as db:
        assert db.scalar(select(User)) is None


def test_google_confirmation_must_be_from_the_same_account(client, monkeypatch):
    headers = google_account(client, monkeypatch)
    configure_google(monkeypatch, fresh_claims(email="otra@example.com"))
    response = delete_with_google(client, headers)
    assert response.status_code == 403
    assert client.get("/api/v1/users/me", headers=headers).status_code == 200


def test_google_confirmation_must_be_recent(client, monkeypatch):
    headers = google_account(client, monkeypatch)
    configure_google(monkeypatch, fresh_claims(age_seconds=11 * 60))
    assert delete_with_google(client, headers).status_code == 403
    configure_google(monkeypatch, {"email": "google@example.com", "email_verified": True})
    assert delete_with_google(client, headers).status_code == 403  # sin iat
    assert client.get("/api/v1/users/me", headers=headers).status_code == 200


def test_google_confirmation_rejects_an_invalid_token(client, monkeypatch):
    headers = google_account(client, monkeypatch)

    def invalid(token, request, client_id):
        raise ValueError("firma no válida")

    monkeypatch.setattr(auth, "verify_oauth2_token", invalid)
    assert delete_with_google(client, headers).status_code == 401
    assert client.get("/api/v1/users/me", headers=headers).status_code == 200


def test_google_confirmation_needs_google_configured(client, monkeypatch):
    headers = google_account(client, monkeypatch)
    monkeypatch.setattr(auth, "get_settings", lambda: SimpleNamespace(google_client_id=None))
    assert delete_with_google(client, headers).status_code == 503


def test_delete_needs_exactly_one_confirmation(client, auth_headers):
    for body in ({}, {"password": "x", "google_credential": "y" * 40}):
        response = client.post("/api/v1/users/me/delete", json=body, headers=auth_headers)
        assert response.status_code == 422


def test_delete_with_null_fields_is_refused(client, auth_headers):
    body = {"password": None, "google_credential": None}
    response = client.post("/api/v1/users/me/delete", json=body, headers=auth_headers)
    assert response.status_code == 422
    assert client.get("/api/v1/users/me", headers=auth_headers).status_code == 200


def test_delete_requires_an_open_session_even_with_google(client, monkeypatch):
    configure_google(monkeypatch, fresh_claims(email="g@example.com"))
    response = client.post("/api/v1/users/me/delete", json={"google_credential": "y" * 40})
    assert response.status_code == 401


# ---------- Pre-secuestro: Google en una cuenta de contraseña sin email verificado ----------


def test_google_login_on_unverified_account_voids_password_and_sessions(client, monkeypatch):
    # Alguien registra el email de Ana con su contraseña antes que ella
    assert register(client, email="ana@example.com", name="Ana").status_code == 201
    intruder = {"Authorization": f"Bearer {login(client).json()['access_token']}"}
    owner = google_account(client, monkeypatch, email="ana@example.com")
    # La contraseña y la sesión del intruso dejan de valer; Ana sigue dentro
    assert client.get("/api/v1/users/me", headers=intruder).status_code == 401
    assert login(client).status_code == 401
    assert client.get("/api/v1/users/me", headers=owner).status_code == 200
    kinds = [e["kind"] for e in client.get("/api/v1/users/me/activity", headers=owner).json()]
    assert "google_linked" in kinds
    exported = client.get("/api/v1/users/me/export", headers=owner).json()
    assert exported["email_verified_at"] is not None


def test_later_google_logins_do_not_close_sessions_again(client, monkeypatch):
    first = google_account(client, monkeypatch, email="nuevo@example.com")
    google_account(client, monkeypatch, email="nuevo@example.com")
    assert client.get("/api/v1/users/me", headers=first).status_code == 200


def test_password_set_by_email_link_survives_google_login(client, monkeypatch):
    sent = []
    monkeypatch.setattr(auth, "send_email", lambda to, subject, body: sent.append(body))
    assert register(client, email="ana@example.com", name="Ana").status_code == 201
    client.post("/api/v1/auth/password-reset/request", json={"email": "ana@example.com"})
    token = sent[0].split("token=")[1].split()[0]
    new = "otra-clave-muy-segura-789"
    done = client.post(
        "/api/v1/auth/password-reset/confirm", json={"token": token, "new_password": new}
    )
    assert done.status_code == 204
    session = {"Authorization": f"Bearer {login(client, password=new).json()['access_token']}"}
    google_account(client, monkeypatch, email="ana@example.com")
    auth_limiter.reset()  # todas las peticiones del test llegan desde la misma IP
    # El enlace llegó a su email: la contraseña es suya y no se anula
    assert login(client, password=new).status_code == 200
    assert client.get("/api/v1/users/me", headers=session).status_code == 200
    assert login(client, password=PASSWORD).status_code == 401
