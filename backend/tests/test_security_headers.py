"""Cabeceras de seguridad de la API."""

from app.main import API_SECURITY_HEADERS


def test_api_responses_include_security_headers(client):
    response = client.get("/api/health")
    for name, value in API_SECURITY_HEADERS.items():
        assert response.headers[name] == value


def test_error_responses_include_security_headers(client):
    response = client.get("/api/users/me")  # sin token: 401
    assert response.status_code == 401
    assert response.headers["X-Content-Type-Options"] == "nosniff"


def test_non_api_paths_are_untouched(client):
    response = client.get("/docs")
    assert "X-Frame-Options" not in response.headers
