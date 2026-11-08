"""Gestión de errores de la API: siempre JSON con «detail», nunca HTML ni trazas internas."""

from conftest import auth_headers, client  # noqa: F401  (fixtures)


def test_ruta_inexistente_responde_404_en_json(client):  # noqa: F811
    response = client.get("/api/v1/no-existe")
    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/json")
    assert "detail" in response.json()


def test_metodo_no_permitido_responde_405(client):  # noqa: F811
    response = client.delete("/api/v1/health")
    assert response.status_code == 405
    assert "detail" in response.json()


def test_validacion_responde_422_con_el_campo(client):  # noqa: F811
    response = client.post("/api/v1/auth/register", json={"email": "no-es-un-email"})
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert isinstance(detail, list) and detail
    # El frontend (api.js, formatDetail) usa loc[-1] para señalar el campo del formulario
    assert all("loc" in item and "msg" in item for item in detail)


def test_json_mal_formado_responde_422_sin_traza(client):  # noqa: F811
    response = client.post(
        "/api/v1/auth/register",
        content=b"{no es json",
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 422
    assert "Traceback" not in response.text


def test_cuerpo_demasiado_grande_responde_413_en_json(client):  # noqa: F811
    from app.config import get_settings

    big = b"x" * (get_settings().max_body_bytes + 1)
    response = client.post("/api/v1/auth/login", content=big)
    assert response.status_code == 413
    assert response.json() == {"detail": "La peticion es demasiado grande"}


def test_recurso_inexistente_con_sesion_responde_404(client, auth_headers):  # noqa: F811
    response = client.get("/api/v1/lessons/qa-leccion-inexistente", headers=auth_headers)
    assert response.status_code == 404
    assert "detail" in response.json()


def test_las_respuestas_de_error_llevan_las_cabeceras_de_seguridad(client):  # noqa: F811
    response = client.get("/api/v1/no-existe")
    for header in ("X-Content-Type-Options", "Content-Security-Policy", "Cache-Control"):
        assert header in response.headers, header
