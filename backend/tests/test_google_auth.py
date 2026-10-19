"""Pruebas del inicio de sesión con Google sin llamadas reales a Google."""

from types import SimpleNamespace

from app.routers import auth


def configure_google(monkeypatch, claims):
    monkeypatch.setattr(auth, "get_settings", lambda: SimpleNamespace(google_client_id="test-google-client-id"))
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
        "/api/auth/google",
        json={"credential": "x" * 40, "accept_privacy": True},
    )
    assert response.status_code == 200
    assert response.json()["access_token"]
    me = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {response.json()['access_token']}"},
    )
    assert me.status_code == 200
    assert me.json()["email"] == "google@example.com"
    assert me.json()["display_name"] == "Google Alumno"


def test_google_login_reuses_existing_account(client, monkeypatch):
    from tests.conftest import register

    assert register(client, email="ana@example.com", name="Ana").status_code == 201
    configure_google(
        monkeypatch,
        {"email": "ANA@example.com", "email_verified": True, "name": "Otro nombre", "sub": "sub-1"},
    )
    response = client.post(
        "/api/auth/google",
        json={"credential": "x" * 40, "accept_privacy": True},
    )
    assert response.status_code == 200
    me = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {response.json()['access_token']}"},
    )
    assert me.status_code == 200
    assert me.json()["display_name"] == "Ana"


def test_google_login_rejects_unverified_email(client, monkeypatch):
    configure_google(
        monkeypatch,
        {"email": "unverified@example.com", "email_verified": False, "name": "Alumno", "sub": "sub-2"},
    )
    response = client.post(
        "/api/auth/google",
        json={"credential": "x" * 40, "accept_privacy": True},
    )
    assert response.status_code == 401

def test_google_login_requires_privacy_for_new_account(client, monkeypatch):
    configure_google(
        monkeypatch,
        {"email": "privacy@example.com", "email_verified": True, "name": "Alumno", "sub": "sub-3"},
    )
    response = client.post(
        "/api/auth/google",
        json={"credential": "x" * 40, "accept_privacy": False},
    )
    assert response.status_code == 400


def test_google_login_rejects_invalid_id_token(client, monkeypatch):
    configure_google(monkeypatch, {})
    def invalid_token(token, request, client_id):
        raise ValueError("invalid token")
    monkeypatch.setattr(auth, "verify_oauth2_token", invalid_token)
    response = client.post(
        "/api/auth/google",
        json={"credential": "x" * 40, "accept_privacy": True},
    )
    assert response.status_code == 401


def test_google_login_unconfigured(client, monkeypatch):
    monkeypatch.setattr(auth, "get_settings", lambda: SimpleNamespace(google_client_id=None))
    response = client.post(
        "/api/auth/google",
        json={"credential": "x" * 40, "accept_privacy": True},
    )
    assert response.status_code == 503
