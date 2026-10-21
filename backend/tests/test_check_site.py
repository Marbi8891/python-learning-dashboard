"""Prueba de humo del sitio estático (scripts/check_site.py): lo que se publica en GitHub Pages."""

import shutil
import sys

from app.config import DEFAULT_LESSONS_FILE

FRONTEND = DEFAULT_LESSONS_FILE.parents[1]
sys.path.insert(0, str(FRONTEND.parent / "scripts"))
import check_site  # noqa: E402  (scripts/check_site.py)


def make_site(tmp_path, page: str, module: str = "export const ok = 1;\n"):
    site = tmp_path / "site"
    (site / "js").mkdir(parents=True)
    (site / "data").mkdir()
    (site / "index.html").write_text(page, encoding="utf-8")
    (site / "js" / "app.js").write_text(module, encoding="utf-8")
    (site / "manifest.webmanifest").write_text("{}", encoding="utf-8")
    return site


def test_the_real_frontend_passes():
    assert check_site.main([str(FRONTEND)]) == 0


def test_detects_absolute_and_missing_references(tmp_path, capsys):
    page = (
        '<link href="/css/base.css"><script src="js/app.js"></script>'
        '<a href="falta.html">x</a><a href="https://example.com">ok</a><a href="#/aprender">ok</a>'
    )
    assert check_site.main([str(make_site(tmp_path, page))]) == 1
    out = capsys.readouterr().out
    assert "«/css/base.css» es absoluta" in out
    assert "«falta.html» no existe" in out
    assert "example.com" not in out


def test_only_404_may_use_the_pages_prefix(tmp_path, capsys):
    site = make_site(tmp_path, '<script src="js/app.js"></script>')
    link = '<a href="/python-learning-dashboard/">inicio</a>'
    (site / "404.html").write_text(link, encoding="utf-8")
    (site / "otra.html").write_text(link, encoding="utf-8")
    assert check_site.main([str(site)]) == 1
    out = capsys.readouterr().out
    assert "404.html" not in out
    assert "otra.html" in out


def test_detects_broken_imports_syntax_and_json(tmp_path, capsys):
    module = 'import { x } from "./no-existe.js";\nconst = ;\n'
    site = make_site(tmp_path, '<script src="js/app.js"></script>', module)
    (site / "data" / "roto.json").write_text("{", encoding="utf-8")
    assert check_site.main([str(site)]) == 1
    out = capsys.readouterr().out
    assert "importa «./no-existe.js»" in out
    assert "data/roto.json" in out
    if shutil.which("node"):
        assert "SyntaxError" in out


def test_without_index_fails(tmp_path):
    assert check_site.main([str(tmp_path)]) == 1
