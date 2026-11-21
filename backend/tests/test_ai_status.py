"""GET /api/v1/ai/status y el campo «ai» de /health (Fase 1 de la integración con NEXARO)."""

import httpx
import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr

from app.config import get_settings
from app.main import API_SECURITY_HEADERS, app
from app.nexaro_client import NexaroClient, NexaroConfigError
from tests.test_nexaro_client import MODEL, TOKEN

STATUS = "/api/v1/ai/status"


def test_status_needs_a_session(client):
    assert client.get(STATUS).status_code == 401


def test_disabled_by_default(client, auth_headers):
    response = client.get(STATUS, headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == {"enabled": False, "available": False, "modes": []}
    assert client.get("/api/v1/health").json()["ai"] is False
    for name, value in API_SECURITY_HEADERS.items():
        assert response.headers[name] == value


def test_enabled_and_available(client, auth_headers, fake_nexaro):
    response = client.get(STATUS, headers=auth_headers)
    assert response.json() == {
        "enabled": True,
        "available": True,
        "modes": ["chat", "hint", "explain-error", "review-code"],
    }
    assert client.get("/api/v1/health").json()["ai"] is True
    # No revela nada de NEXARO al navegador
    for private in ("127.0.0.1", "8080", MODEL, TOKEN, "qwen"):
        assert private not in response.text
    # El navegador no envía nada que llegue a NEXARO: ni su cookie ni su token
    for request in fake_nexaro.requests:
        assert "cookie" not in request.headers
        assert request.headers["Authorization"] == f"Bearer {TOKEN}"


def test_enabled_but_nexaro_down(client, auth_headers, fake_nexaro):
    fake_nexaro.error = httpx.ConnectError("apagado")
    response = client.get(STATUS, headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == {
        "enabled": True,
        "available": False,
        "modes": ["chat", "hint", "explain-error", "review-code"],
    }


def test_lifespan_creates_and_closes_the_client(monkeypatch):
    configured = get_settings()
    monkeypatch.setattr(configured, "nexaro_enabled", True)
    monkeypatch.setattr(configured, "nexaro_base_url", "http://127.0.0.1:8080")
    monkeypatch.setattr(configured, "nexaro_model", MODEL)
    monkeypatch.setattr(configured, "nexaro_service_token", SecretStr(TOKEN))
    with TestClient(app) as test_client:
        assert isinstance(app.state.nexaro, NexaroClient)
        assert test_client.get("/api/health").json()["ai"] is True
    assert app.state.nexaro is None


def test_invalid_config_stops_the_api(monkeypatch):
    configured = get_settings()
    monkeypatch.setattr(configured, "nexaro_enabled", True)
    monkeypatch.setattr(configured, "nexaro_base_url", "http://169.254.169.254")
    monkeypatch.setattr(configured, "nexaro_model", MODEL)
    with pytest.raises(NexaroConfigError), TestClient(app):
        pass  # pragma: no cover - no se llega: el arranque falla
