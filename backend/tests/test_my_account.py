"""«Mi cuenta» (ADR-0025): editar el perfil, cambiar la contraseña y ver la actividad."""

from app.rate_limit import auth_limiter
from tests.conftest import PASSWORD, login, register

URL = "/api/users/me"
NEW = "tortuga-azul-en-bici"
ANDROID = {"User-Agent": "Mozilla/5.0 (Linux; Android 15) AppleWebKit/537.36 Chrome/140.0 Mobile"}


def test_change_display_name(client, auth_headers):
    response = client.patch(URL, json={"display_name": "  Ana María  "}, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["display_name"] == "Ana María"
    assert client.get(URL, headers=auth_headers).json()["display_name"] == "Ana María"
    kinds = [e["kind"] for e in client.get(f"{URL}/activity", headers=auth_headers).json()]
    assert kinds[0] == "name_changed"
    # Sin cambios no se registra nada nuevo
    client.patch(URL, json={"display_name": "Ana María"}, headers=auth_headers)
    assert len(client.get(f"{URL}/activity", headers=auth_headers).json()) == len(kinds)


def test_display_name_must_not_be_blank(client, auth_headers):
    assert client.patch(URL, json={"display_name": "   "}, headers=auth_headers).status_code == 422
    assert client.patch(URL, json={"display_name": ""}, headers=auth_headers).status_code == 422


def test_change_password_keeps_this_session_and_closes_the_others(client, auth_headers):
    response = client.post(
        f"{URL}/password",
        json={"current_password": PASSWORD, "new_password": NEW},
        headers=auth_headers,
    )
    assert response.status_code == 200
    fresh = {"Authorization": f"Bearer {response.json()['access_token']}"}
    assert client.get(URL, headers=fresh).status_code == 200
    assert client.get(URL, headers=auth_headers).status_code == 401  # el token anterior ya no vale
    auth_limiter.reset()
    assert login(client, password=PASSWORD).status_code == 401
    auth_limiter.reset()
    assert login(client, password=NEW).status_code == 200


def test_change_password_needs_the_current_one_and_a_strong_new_one(client, auth_headers):
    wrong = client.post(
        f"{URL}/password",
        json={"current_password": "otra-cosa-123", "new_password": NEW},
        headers=auth_headers,
    )
    assert wrong.status_code == 403
    weak = client.post(
        f"{URL}/password",
        json={"current_password": PASSWORD, "new_password": "password123"},
        headers=auth_headers,
    )
    assert weak.status_code == 422
    assert "más usadas" in weak.json()["detail"]
    assert client.get(URL, headers=auth_headers).status_code == 200  # nada ha cambiado


def test_activity_shows_logins_failures_and_device_without_ip(client):
    register(client)
    client.post("/api/auth/login", data={"username": "ana@example.com", "password": "mal-000000"})
    auth_limiter.reset()
    token = client.post(
        "/api/auth/login",
        data={"username": "ana@example.com", "password": PASSWORD},
        headers=ANDROID,
    ).json()["access_token"]
    events = client.get(f"{URL}/activity", headers={"Authorization": f"Bearer {token}"}).json()
    assert [e["kind"] for e in events] == ["login", "login_failed"]
    assert events[0]["device"] == "Android · Chrome"
    assert events[1]["device"] == "Dispositivo desconocido"
    assert set(events[0]) == {"kind", "device", "created_at"}  # sin IP ni User-Agent completo


def test_activity_keeps_only_the_latest_events(client, auth_headers, monkeypatch):
    monkeypatch.setattr("app.activity.KEPT", 3)
    for n in range(5):
        client.patch(URL, json={"display_name": f"Ana {n}"}, headers=auth_headers)
    events = client.get(f"{URL}/activity", headers=auth_headers).json()
    assert len(events) == 3


def test_logout_all_and_reset_appear_in_activity(client, auth_headers):
    client.post("/api/auth/logout-all", headers=auth_headers)
    auth_limiter.reset()
    token = login(client).json()["access_token"]
    kinds = [
        e["kind"]
        for e in client.get(f"{URL}/activity", headers={"Authorization": f"Bearer {token}"}).json()
    ]
    assert kinds[:2] == ["login", "logout_all"]


def test_activity_is_exported_and_deleted_with_the_account(client, auth_headers):
    exported = client.get(f"{URL}/export", headers=auth_headers).json()
    assert exported["activity"][0]["kind"] == "login"
    client.post(f"{URL}/delete", json={"password": PASSWORD}, headers=auth_headers)
    with client.engine.connect() as conn:
        assert conn.exec_driver_sql("SELECT COUNT(*) FROM account_events").scalar_one() == 0


def test_device_names():
    from starlette.requests import Request

    from app.activity import device

    def ua(agent):
        return Request({"type": "http", "headers": [(b"user-agent", agent.encode())]})

    assert device(ua("Mozilla/5.0 (Windows NT 10.0) Firefox/140.0")) == "Windows · Firefox"
    assert device(ua("Mozilla/5.0 (iPhone; CPU iPhone OS 18) Safari/605")) == "iPhone · Safari"
    assert device(ua("Mozilla/5.0 (Windows NT 10.0) Chrome/140 Edg/140")) == "Windows · Edge"
    assert device(ua("okhttp/4.12.0")) == "App Android"
    assert device(None) == "Dispositivo desconocido"
