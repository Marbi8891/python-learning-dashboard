"""La política de privacidad describe el sistema real (docs/AUDITORIA_LEGAL.md, A-04).

Si cambia el código (duración de la sesión, Google, almacenamiento en el navegador, cookies),
estas pruebas obligan a actualizar también privacidad.html.
"""

import re

from app.config import DEFAULT_LESSONS_FILE, Settings

FRONTEND = DEFAULT_LESSONS_FILE.parents[1]


def policy_text() -> str:
    html = (FRONTEND / "privacidad.html").read_text(encoding="utf-8")
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def test_session_duration_matches_the_code():
    minutes = Settings.model_fields["access_token_minutes"].default
    text = policy_text()
    assert f"{minutes} minutos" in text
    for wrong in ("a la hora", "una hora", "60 minutos"):
        assert wrong not in text


def test_google_sign_in_is_described_when_configured():
    config = (FRONTEND / "config.js").read_text(encoding="utf-8")
    client_id = re.search(r'googleClientId:\s*"([^"]*)"', config).group(1)
    text = policy_text()
    if client_id:
        assert "Google" in text
        assert "g_state" in text  # cookie que puede dejar el botón de Google


def test_recovery_emails_are_not_described_as_disabled():
    text = policy_text()
    assert "no están activados" not in text
    assert "proveedor de envío de correo" in text


def test_every_browser_storage_key_is_covered_by_the_policy():
    """La política explica las claves que empiezan por «pld:»: no puede haber otras."""
    declared = re.compile(r'(?:KEY|PREFIX)\s*=\s*"([^"]*)"')
    keys = {
        value
        for path in (FRONTEND / "js").rglob("*.js")
        for value in declared.findall(path.read_text(encoding="utf-8"))
        if not value.startswith(("#", "/"))  # rutas de la app y de la API, no almacenamiento
    }
    assert keys, "no se han encontrado claves de almacenamiento"
    assert all(key.startswith("pld:") for key in keys), sorted(keys)
    assert "pld:" in policy_text()


def test_service_worker_caches_are_described():
    sw = (FRONTEND / "sw.js").read_text(encoding="utf-8")
    text = policy_text()
    assert "pld-site-" in sw and "pld-site-" in text
    assert '"pld-pyodide"' in sw and "pld-pyodide" in text


def test_no_claim_of_a_single_cookie():
    assert "Una sola cookie" not in policy_text()
    aviso = (FRONTEND / "aviso-legal.html").read_text(encoding="utf-8")
    assert "una cookie técnica de sesión" not in aviso
