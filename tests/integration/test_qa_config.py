"""Configuración de despliegue coherente entre frontend (GitHub Pages) y backend (Render).

Sin red: se leen render.yaml, frontend/config.js, los <meta> de CSP y la configuración Pydantic.
"""

import re
from urllib.parse import urlparse

from conftest import (
    BACKEND,
    FRONTEND,
    client,  # noqa: F401  (fixture)
    read_csp,
    read_frontend_config,
    read_render_env,
)

ORIGIN = "http://localhost:5500"  # origen por defecto de la web en local (Settings.cors_origins)


def settings_fields() -> set[str]:
    from app.config import Settings

    return {name.upper() for name in Settings.model_fields}


def test_render_solo_declara_variables_que_lee_la_api():
    unknown = set(read_render_env()) - settings_fields() - {"PORT"}
    assert not unknown, f"render.yaml declara variables que la API ignora: {sorted(unknown)}"


def test_env_example_solo_documenta_variables_que_lee_la_api():
    text = (BACKEND / ".env.example").read_text(encoding="utf-8")
    keys = set(re.findall(r"^#?\s*([A-Z][A-Z0-9_]+)=", text, re.M))
    assert keys, "no se han encontrado variables en .env.example"
    assert keys <= settings_fields(), sorted(keys - settings_fields())


def test_produccion_no_lleva_secretos_en_render_yaml():
    env = read_render_env()
    for secret in ("DATABASE_URL", "BREVO_API_KEY", "SMTP_PASSWORD", "GOOGLE_CLIENT_ID"):
        assert env.get(secret) is None, (
            f"{secret} debe rellenarse en el panel de Render (sync: false)"
        )
    text = (FRONTEND.parent / "render.yaml").read_text(encoding="utf-8")
    assert re.search(r"- key: JWT_SECRET\s+generateValue: true", text), (
        "JWT_SECRET lo genera Render"
    )


def test_la_api_de_produccion_admite_el_origen_de_github_pages():
    env = read_render_env()
    origins = env["CORS_ORIGINS"]
    frontend = urlparse(env["FRONTEND_URL"])
    assert f"{frontend.scheme}://{frontend.netloc}" in origins
    assert "*" not in origins, "con cookies (allow_credentials) no se puede usar el comodín"


def test_el_frontend_apunta_a_la_api_que_despliega_render():
    config = read_frontend_config()
    api = urlparse(config["apiUrlProduction"])
    service = re.search(r"name:\s*(\S+)", (FRONTEND.parent / "render.yaml").read_text()).group(1)
    assert api.scheme == "https"
    assert api.netloc == f"{service}.onrender.com", (api.netloc, service)


def test_la_csp_de_la_web_permite_conectar_con_la_api_y_google():
    connect = read_csp("index.html")["connect-src"]
    config = read_frontend_config()
    assert config["apiUrlProduction"] in connect
    assert "https://accounts.google.com/gsi/" in connect


def test_la_csp_permite_la_version_de_pyodide_que_usa_la_web():
    runner = (FRONTEND / "js" / "python-runner.js").read_text(encoding="utf-8")
    version = re.search(r'PYODIDE_VERSION = "([^"]+)"', runner).group(1)
    cdn = f"https://cdn.jsdelivr.net/pyodide/v{version}/full/"
    csp = read_csp("index.html")
    assert cdn in csp["script-src"] and cdn in csp["connect-src"], f"la CSP no permite {cdn}"


def test_google_client_id_es_publico_y_con_formato_valido():
    client_id = read_frontend_config()["googleClientId"]
    assert re.fullmatch(r"\d+-[a-z0-9]+\.apps\.googleusercontent\.com", client_id), client_id
    # En el frontend solo puede ir el Client ID: nunca un client secret (GOCSPX-...)
    assert "GOCSPX" not in (FRONTEND / "config.js").read_text(encoding="utf-8")


def test_google_se_anuncia_solo_si_el_servidor_lo_tiene_configurado(client, monkeypatch):  # noqa: F811
    from types import SimpleNamespace

    import app.main as main

    assert client.get("/api/v1/health").json()["google"] is False
    monkeypatch.setattr(main, "get_settings", lambda: SimpleNamespace(google_client_id="1-x.apps"))
    assert client.get("/api/v1/health").json()["google"] is True


def test_cors_admite_el_origen_configurado_con_credenciales(client):  # noqa: F811
    response = client.options(
        "/api/v1/auth/login",
        headers={"Origin": ORIGIN, "Access-Control-Request-Method": "POST"},
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == ORIGIN
    assert response.headers["access-control-allow-credentials"] == "true"


def test_cors_rechaza_un_origen_desconocido(client):  # noqa: F811
    response = client.options(
        "/api/v1/auth/login",
        headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "POST"},
    )
    assert "access-control-allow-origin" not in response.headers
    simple = client.get("/api/v1/health", headers={"Origin": "https://evil.example"})
    assert "access-control-allow-origin" not in simple.headers


def test_cors_admite_la_cabecera_de_sesion_de_la_web(client):  # noqa: F811
    from app.session_cookie import MODE_HEADER

    response = client.options(
        "/api/v1/users/me",
        headers={
            "Origin": ORIGIN,
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": f"authorization,content-type,{MODE_HEADER.lower()}",
        },
    )
    assert response.status_code == 200, "la web no podría mandar X-PLD-Session (cookie de sesión)"
