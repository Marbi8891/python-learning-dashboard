"""Tests for the versioned HTTP API surface."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAIN = ROOT / "backend" / "app" / "main.py"
API_JS = ROOT / "frontend" / "js" / "api.js"


def test_versioned_api_is_the_documented_surface():
    source = MAIN.read_text(encoding="utf-8")
    assert 'API_V1_PREFIX = "/api/v1"' in source
    assert "app.include_router(router, prefix=API_V1_PREFIX)" in source
    assert "include_in_schema=False" in source


def test_frontend_uses_api_v1_for_legacy_request_paths():
    source = API_JS.read_text(encoding="utf-8")
    assert 'export const API_V1_PREFIX = "/api/v1";' in source
    assert "API_V1_PREFIX + path.slice(4)" in source
