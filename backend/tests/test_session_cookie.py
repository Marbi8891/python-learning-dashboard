"""Sesión de la web en una cookie HttpOnly (ADR-0033)."""

from app.session_cookie import COOKIE_NAME
from tests.conftest import PASSWORD, register

WEB = {"X-PLD-Session": "cookie"}


def web_login(client):
    form = {"username": "ana@example.com", "password": PASSWORD}
    return client.post("/api/v1/auth/login", data=form, headers=WEB)


def session_cookie(response) -> str:
    """Valor de la cookie de sesión. El cliente de tests usa http, así que no guarda cookies
    Secure por sí mismo: se envían a mano con la cabecera Cookie."""
    name, value = response.headers["set-cookie"].split(";")[0].split("=", 1)
    assert name == COOKIE_NAME
    return value


def with_cookie(value: str, headers=WEB) -> dict[str, str]:
    return {**headers, "Cookie": f"{COOKIE_NAME}={value}"}


def test_web_login_sets_an_httponly_cookie_and_returns_no_token(client):
    register(client)
    response = web_login(client)
    assert response.status_code == 200
    assert response.json() == {"access_token": None, "token_type": "cookie"}
    header = response.headers["set-cookie"]
    for attribute in ("HttpOnly", "Secure", "SameSite=None", "Partitioned", "Path=/"):
        assert attribute in header
    assert "Max-Age=1800" in header  # lo mismo que dura el token (30 minutos)
    me = client.get("/api/v1/users/me", headers=with_cookie(session_cookie(response)))
    assert me.status_code == 200
    assert me.json()["email"] == "ana@example.com"


def test_clients_without_the_header_still_get_a_bearer_token(client):
    # La app Android y los scripts no cambian
    register(client)
    response = client.post(
        "/api/auth/login", data={"username": "ana@example.com", "password": PASSWORD}
    )
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]
    assert "set-cookie" not in response.headers


def test_cookie_without_the_header_is_ignored(client):
    # CSRF: otra web puede hacer que el navegador envíe la cookie, pero no añadir la cabecera
    # sin pasar por CORS, que solo admite a la web del proyecto
    register(client)
    cookie = session_cookie(web_login(client))
    response = client.get("/api/v1/users/me", headers=with_cookie(cookie, headers={}))
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_logout_clears_the_cookie(client):
    response = client.post("/api/v1/auth/logout")
    assert response.status_code == 204
    header = response.headers["set-cookie"]
    assert f"{COOKIE_NAME}=;" in header
    assert "Max-Age=0" in header
    assert "Partitioned" in header  # sin él, el navegador no borraría la cookie particionada


def test_logout_all_also_clears_this_browser_cookie(client):
    register(client)
    cookie = session_cookie(web_login(client))
    response = client.post("/api/v1/auth/logout-all", headers=with_cookie(cookie))
    assert response.status_code == 204
    assert "Max-Age=0" in response.headers["set-cookie"]
    assert client.get("/api/v1/users/me", headers=with_cookie(cookie)).status_code == 401


def test_password_change_renews_the_cookie(client):
    register(client)
    old = session_cookie(web_login(client))
    response = client.post(
        "/api/v1/users/me/password",
        json={"current_password": PASSWORD, "new_password": "otra-contraseña-segura-456"},
        headers=with_cookie(old),
    )
    assert response.json() == {"access_token": None, "token_type": "cookie"}
    new = session_cookie(response)
    assert client.get("/api/v1/users/me", headers=with_cookie(new)).status_code == 200
    assert client.get("/api/v1/users/me", headers=with_cookie(old)).status_code == 401


def test_bearer_header_takes_precedence_over_the_cookie(client):
    register(client)
    cookie = session_cookie(web_login(client))
    headers = {**with_cookie(cookie), "Authorization": "Bearer no-es-un-token"}
    assert client.get("/api/v1/users/me", headers=headers).status_code == 401


def test_cors_allows_credentials_and_the_session_header(client):
    response = client.options(
        "/api/v1/users/me",
        headers={
            "Origin": "http://localhost:5500",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "x-pld-session",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-credentials"] == "true"
    assert response.headers["access-control-allow-origin"] == "http://localhost:5500"
    blocked = client.options(
        "/api/v1/users/me",
        headers={
            "Origin": "https://evil.example",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "x-pld-session",
        },
    )
    assert "access-control-allow-origin" not in blocked.headers
