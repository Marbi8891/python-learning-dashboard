"""Políticas CSP de las páginas de la web (GitHub Pages solo admite la CSP en <meta>)."""

import pytest
from conftest import FRONTEND, read_csp

PAGES = sorted(p.name for p in FRONTEND.glob("*.html"))


def test_hay_paginas_que_revisar():
    assert "index.html" in PAGES and len(PAGES) >= 3


@pytest.mark.parametrize("page", PAGES)
def test_cada_pagina_tiene_csp(page):
    assert read_csp(page), f"{page} no tiene <meta http-equiv=Content-Security-Policy>"


@pytest.mark.parametrize("page", PAGES)
def test_csp_bloquea_lo_basico(page):
    csp = read_csp(page)
    assert csp.get("default-src") == ["'self'"], csp.get("default-src")
    assert csp.get("object-src") == ["'none'"]
    assert csp.get("base-uri") == ["'self'"]
    assert "form-action" in csp


@pytest.mark.parametrize("page", PAGES)
def test_csp_no_permite_scripts_inseguros(page):
    scripts = read_csp(page).get("script-src", [])
    assert "'unsafe-inline'" not in scripts, "permitiría XSS con <script> inyectado"
    assert "'unsafe-eval'" not in scripts, "solo se admite 'wasm-unsafe-eval' (Pyodide)"
    for source in scripts:
        assert source not in ("*", "https:", "http:", "data:", "blob:"), (
            f"fuente demasiado amplia: {source}"
        )


@pytest.mark.parametrize("page", PAGES)
def test_csp_sin_comodines_en_conexiones(page):
    csp = read_csp(page)
    for directive in ("connect-src", "frame-src", "img-src", "worker-src"):
        for source in csp.get(directive, []):
            assert "*" not in source and source not in ("https:", "http:"), f"{directive} {source}"


def test_solo_la_app_carga_codigo_externo():
    """Las páginas legales y la 404 no necesitan Google ni Pyodide: solo 'self'."""
    for page in PAGES:
        if page != "index.html":
            assert read_csp(page)["script-src"] == ["'self'"], page
