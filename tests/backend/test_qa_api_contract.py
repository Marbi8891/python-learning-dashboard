"""Contrato de la API FastAPI generado a partir de su propio OpenAPI.

Estas pruebas no se escriben endpoint a endpoint: recorren TODAS las rutas. Un endpoint nuevo queda
cubierto sin tocar nada, y uno que se salte la autenticación o devuelva errores sin formato falla.
"""

import re

import pytest
from conftest import auth_headers, client  # noqa: F401  (fixtures)

# Rutas que se pueden usar sin sesión. Añadir una aquí es una decisión de seguridad: revísala.
PUBLIC_OPERATIONS = {
    ("GET", "/api/v1/health"),
    ("GET", "/api/v1/modules"),
    ("GET", "/api/v1/lessons/{slug}"),
    ("POST", "/api/v1/auth/register"),
    ("POST", "/api/v1/auth/login"),
    ("POST", "/api/v1/auth/google"),
    ("POST", "/api/v1/auth/logout"),
    ("POST", "/api/v1/auth/password-reset/request"),
    ("POST", "/api/v1/auth/password-reset/confirm"),
}

METHODS = ("get", "post", "put", "patch", "delete")


def operations(schema):
    for path, item in schema["paths"].items():
        for method in METHODS:
            if method in item:
                yield method.upper(), path, item[method]


def concrete(path: str) -> str:
    """Ruta con valores de ejemplo en los parámetros ({slug} → qa-inexistente)."""
    return re.sub(r"\{[^}]+\}", "qa-inexistente", path)


def test_todas_las_rutas_cuelgan_de_api_v1(openapi):
    paths = list(openapi["paths"])
    assert paths, "la API no expone rutas"
    assert all(p.startswith("/api/v1/") for p in paths), [
        p for p in paths if not p.startswith("/api/v1/")
    ]


def test_las_rutas_publicas_son_exactamente_las_revisadas(openapi):
    public = {(m, p) for m, p, op in operations(openapi) if not op.get("security")}
    assert public == PUBLIC_OPERATIONS, (
        f"Nuevas rutas sin autenticación: {sorted(public - PUBLIC_OPERATIONS)}; "
        f"revisadas que ya no existen o piden sesión: {sorted(PUBLIC_OPERATIONS - public)}"
    )


def protected_operations():
    from app.main import app

    return sorted((m, p) for m, p, op in operations(app.openapi()) if op.get("security"))


@pytest.mark.parametrize(("method", "path"), protected_operations())
def test_ruta_protegida_sin_sesion_responde_401(client, method, path):  # noqa: F811
    response = client.request(method, concrete(path), json={})
    assert response.status_code == 401, (
        f"{method} {path} → {response.status_code} {response.text[:200]}"
    )
    assert "detail" in response.json()


@pytest.mark.parametrize(("method", "path"), protected_operations())
def test_ruta_protegida_con_token_falso_responde_401(client, method, path):  # noqa: F811
    forged = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIn0.firma-falsa"}
    response = client.request(method, concrete(path), json={}, headers=forged)
    assert response.status_code == 401, f"{method} {path} → {response.status_code}"


def test_cada_operacion_declara_su_respuesta(openapi):
    """Cada ruta documenta un esquema (Pydantic) o es 204: el frontend sabe qué JSON recibe."""
    missing = []
    for method, path, op in operations(openapi):
        responses = op["responses"]
        ok = next((responses[c] for c in ("200", "201", "202") if c in responses), None)
        content = (ok or {}).get("content", {}).get("application/json", {})
        if "204" not in op["responses"] and not content.get("schema"):
            missing.append(f"{method} {path}")
    assert not missing, missing


def test_los_cuerpos_de_entrada_son_modelos_pydantic(openapi):
    """Los JSON de entrada se validan con un modelo Pydantic ($ref), no con dict sueltos."""
    loose = []
    for method, path, op in operations(openapi):
        body = op.get("requestBody", {}).get("content", {})
        for media, spec in body.items():
            schema = spec.get("schema", {})
            if media == "application/json" and "$ref" not in schema and "allOf" not in schema:
                loose.append(f"{method} {path}")
    assert not loose, loose


def test_los_esquemas_de_pydantic_tienen_tipos(openapi):
    """Ningún campo de un esquema queda sin tipo (Any): el contrato con el frontend es explícito."""
    untyped = []
    for name, schema in openapi["components"]["schemas"].items():
        if name in ("ValidationError", "HTTPValidationError"):
            continue  # esquemas de FastAPI, no del proyecto
        for field, spec in schema.get("properties", {}).items():
            if not any(
                k in spec for k in ("type", "$ref", "anyOf", "allOf", "oneOf", "enum", "const")
            ):
                untyped.append(f"{name}.{field}")
    assert not untyped, untyped
