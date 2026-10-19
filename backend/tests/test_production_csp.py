"""CSP de la web publicada (PLD-SEC-003): sin orígenes de desarrollo y sin debilitar nada más."""

import sys

import pytest

from app.config import DEFAULT_LESSONS_FILE

FRONTEND = DEFAULT_LESSONS_FILE.parents[1]
sys.path.insert(0, str(FRONTEND.parent / "scripts" / "security"))
import production_csp  # noqa: E402  (scripts/security/production_csp.py)


def directives(policy: str) -> dict[str, list[str]]:
    parsed = {}
    for directive in policy.split(";"):
        name, *sources = directive.split()
        parsed[name] = sources
    return parsed


def csp_of(html: str) -> str:
    return production_csp.CSP_META.search(html).group(2)


def test_published_csp_drops_only_the_development_origins():
    source = (FRONTEND / "index.html").read_text(encoding="utf-8")
    before = directives(csp_of(source))
    after = directives(csp_of(production_csp.production_html(source)))

    # Lo único que cambia: connect-src pierde la API local
    assert set(before["connect-src"]) - set(after["connect-src"]) == set(production_csp.DEV_ORIGINS)
    assert all(not s.startswith("http:") for sources in after.values() for s in sources)
    for name, sources in before.items():
        expected = [s for s in sources if s not in production_csp.DEV_ORIGINS]
        assert after[name] == expected, name
    # La web publicada sigue llegando a su API, a Google y a Pyodide
    for origin in (
        "https://pld-api.onrender.com",
        "https://accounts.google.com/gsi/",
        "https://cdn.jsdelivr.net/pyodide/v314.0.7/full/",
    ):
        assert origin in after["connect-src"]
    assert after["object-src"] == ["'none'"] and "'unsafe-eval'" not in after["script-src"]


def test_the_rest_of_the_page_is_untouched():
    source = (FRONTEND / "index.html").read_text(encoding="utf-8")
    published = production_csp.production_html(source)
    removed = sum(len(" " + origin) for origin in production_csp.DEV_ORIGINS)
    assert len(source) - len(published) == removed
    assert source.replace(" http://127.0.0.1:8000 http://localhost:8000", "") == published


def test_rejects_insecure_origins_or_a_missing_policy():
    meta = '<meta http-equiv="Content-Security-Policy" content="default-src \'self\'; {}">'
    with pytest.raises(ValueError, match="sin TLS"):
        production_csp.production_html(meta.format("connect-src 'self' http://evil.example"))
    with pytest.raises(ValueError, match="no hay"):
        production_csp.production_html("<html></html>")
    assert production_csp.production_policy("img-src http://localhost:8000; ") == "img-src"


def test_command_line_checks_and_rewrites_a_copy(tmp_path, monkeypatch, capsys):
    site = tmp_path / "site"
    site.mkdir()
    (site / "index.html").write_text((FRONTEND / "index.html").read_text(encoding="utf-8"))

    monkeypatch.setattr(sys, "argv", ["production_csp", "--check", str(site)])
    assert production_csp.main() == 0
    assert "http://localhost:8000" in (site / "index.html").read_text()

    monkeypatch.setattr(sys, "argv", ["production_csp", str(site)])
    assert production_csp.main() == 0
    assert "localhost:8000" not in (site / "index.html").read_text()
    assert "sin orígenes de desarrollo" in capsys.readouterr().out

    (site / "index.html").write_text("<html></html>")
    assert production_csp.main() == 1
