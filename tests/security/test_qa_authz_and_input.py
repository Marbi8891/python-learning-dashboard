"""Autorización entre cuentas, validación de entradas y configuración segura por defecto."""

import pytest
from conftest import PASSWORD, client, login, register  # noqa: F401  (fixtures)


def token_for(client, email):  # noqa: F811
    register(client, email=email)
    return {"Authorization": f"Bearer {login(client, email=email).json()['access_token']}"}


@pytest.fixture
def two_users(client):  # noqa: F811
    from app.rate_limit import auth_limiter, login_failures, write_limiter

    ana = token_for(client, "ana@example.com")
    auth_limiter.reset()
    bea = token_for(client, "bea@example.com")
    for limiter in (auth_limiter, login_failures, write_limiter):
        limiter.reset()
    return ana, bea


@pytest.mark.parametrize("path", ["/api/v1/course-state/learn", "/api/v1/pcap-state"])
def test_una_cuenta_no_ve_el_estado_de_otra(client, two_users, path):  # noqa: F811
    ana, bea = two_users
    saved = client.put(path, json={"data": {"secreto": "de-ana"}}, headers=ana)
    assert saved.status_code == 200, saved.text
    other = client.get(path, headers=bea)
    assert other.status_code == 200
    assert "de-ana" not in other.text


def test_una_cuenta_no_ve_los_datos_personales_de_otra(client, two_users):  # noqa: F811
    ana, bea = two_users
    assert client.get("/api/v1/users/me", headers=bea).json()["email"] == "bea@example.com"
    export = client.get("/api/v1/users/me/export", headers=bea)
    assert export.status_code == 200 and "ana@example.com" not in export.text


def test_cerrar_todas_las_sesiones_invalida_el_token(client, two_users):  # noqa: F811
    ana, _ = two_users
    assert client.post("/api/v1/auth/logout-all", headers=ana).status_code in (200, 204)
    assert client.get("/api/v1/users/me", headers=ana).status_code == 401


@pytest.mark.parametrize(
    "payload",
    [
        {
            "email": "ana@example.com",
            "password": "corta",
            "display_name": "Ana",
            "accept_privacy": True,
        },
        {
            "email": "ana@example.com",
            "password": "x" * 129,
            "display_name": "Ana",
            "accept_privacy": True,
        },
        {
            "email": "ana@example.com",
            "password": PASSWORD,
            "display_name": "A" * 81,
            "accept_privacy": True,
        },
        {
            "email": "' OR 1=1 --",
            "password": PASSWORD,
            "display_name": "Ana",
            "accept_privacy": True,
        },
        {
            "email": "ana@example.com",
            "password": PASSWORD,
            "display_name": "",
            "accept_privacy": True,
        },
        {
            "email": "ana@example.com",
            "password": PASSWORD,
            "display_name": "Ana",
            "accept_privacy": False,
        },
    ],
    ids=[
        "password-corta",
        "password-larga",
        "nombre-largo",
        "email-inyeccion",
        "nombre-vacio",
        "sin-privacidad",
    ],
)
def test_registro_rechaza_entradas_no_validas(client, payload):  # noqa: F811
    assert client.post("/api/v1/auth/register", json=payload).status_code == 422


def test_curso_desconocido_no_se_guarda(client, two_users):  # noqa: F811
    ana, _ = two_users
    response = client.put("/api/v1/course-state/../../etc", json={"data": {}}, headers=ana)
    assert response.status_code in (404, 422)


def test_la_api_no_arranca_sin_un_jwt_secret_seguro(monkeypatch):
    from types import SimpleNamespace

    import app.security as security

    for secret in (None, "", "corto"):
        monkeypatch.setattr(
            security, "get_settings", lambda s=secret: SimpleNamespace(jwt_secret=s)
        )
        with pytest.raises(RuntimeError, match="JWT_SECRET"):
            security.get_jwt_secret()


def test_configuracion_segura_por_defecto():
    from app.config import Settings
    from app.main import app

    defaults = Settings.model_fields
    assert defaults["enable_docs"].default is False, "/docs no debe publicarse en producción"
    assert defaults["jwt_secret"].default is None, "no puede haber un secreto por defecto"
    assert app.debug is False
    assert app.openapi_url is None, "el mapa de la API no se publica sin ENABLE_DOCS"
    assert "*" not in defaults["cors_origins"].default


def test_la_cookie_de_sesion_es_segura(client):  # noqa: F811
    from app.session_cookie import MODE_HEADER

    register(client)
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "ana@example.com", "password": PASSWORD},
        headers={MODE_HEADER: "cookie"},
    )
    cookie = response.headers.get("set-cookie", "")
    assert cookie.startswith("__Host-"), (
        "el prefijo __Host- impide que un subdominio la sobrescriba"
    )
    for flag in ("Secure", "HttpOnly", "SameSite=None", "Path=/"):
        assert flag in cookie, flag


def test_la_imagen_docker_no_corre_como_root():
    from conftest import BACKEND

    dockerfile = (BACKEND / "Dockerfile").read_text(encoding="utf-8")
    assert "\nUSER app" in dockerfile
    assert "--reload" not in dockerfile
