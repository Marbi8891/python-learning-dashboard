"""Modo aplicación local: la API sirve la web con tipos MIME correctos y su propia config."""

import importlib
import mimetypes

from fastapi import FastAPI
from fastapi.testclient import TestClient

import app.main
from app.config import FRONTEND_DIR, get_settings
from app.local_site import mount_frontend


def make_client() -> TestClient:
    site = FastAPI()

    @site.get("/api/health")
    def health():
        return {"status": "ok"}

    mount_frontend(site, FRONTEND_DIR)
    return TestClient(site)


def test_serves_index_and_api_share_origin():
    client = make_client()
    index = client.get("/")
    assert index.status_code == 200
    assert "Python Learning Dashboard" in index.text
    assert client.get("/api/health").json() == {"status": "ok"}  # la API tiene prioridad


def test_local_config_points_to_same_origin():
    response = make_client().get("/config.js")
    assert response.headers["content-type"].startswith("text/javascript")
    assert "location.origin" in response.text
    assert response.headers["cache-control"] == "no-store"


def test_javascript_and_assets_have_correct_mime_types(monkeypatch):
    # Simula un registro de Windows roto: .js como text/plain
    mimetypes.add_type("text/plain", ".js")
    client = make_client()
    checks = {
        "/js/app.js": "text/javascript",
        "/css/base.css": "text/css",
        "/data/lessons.json": "application/json",
        "/fonts/inter-latin-400-normal.woff2": "font/woff2",
        "/favicon.svg": "image/svg+xml",
    }
    for path, mime in checks.items():
        response = client.get(path)
        assert response.status_code == 200, path
        assert response.headers["content-type"].startswith(mime), (path, response.headers)


def test_main_mounts_frontend_when_enabled(monkeypatch):
    monkeypatch.setattr(get_settings(), "serve_frontend", True)
    try:
        module = importlib.reload(app.main)
        with TestClient(module.app) as client:
            assert client.get("/").status_code == 200
            assert "location.origin" in client.get("/config.js").text
    finally:
        monkeypatch.setattr(get_settings(), "serve_frontend", False)
        importlib.reload(app.main)
