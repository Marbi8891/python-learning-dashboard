"""Security-by-default regression tests for browser authentication."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
API_JS = ROOT / "frontend" / "js" / "api.js"


def test_access_token_is_not_persisted_in_browser_storage():
    source = API_JS.read_text(encoding="utf-8")
    assert "localStorage.getItem" not in source
    assert "localStorage.setItem" not in source
    assert "sessionStorage.getItem" not in source
    assert "sessionStorage.setItem" not in source
    assert "let accessToken = null" in source


def test_default_access_token_lifetime_is_short():
    from app.config import Settings

    assert Settings().access_token_minutes <= 30
