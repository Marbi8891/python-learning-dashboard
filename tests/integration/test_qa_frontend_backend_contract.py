"""Contrato entre el frontend (frontend/js) y la API FastAPI.

Se leen del código del frontend las llamadas reales (request("POST", "/api/auth/login"),
createDocSync({ path: ... })) y se comprueba que la API tiene esa ruta con ese método. Si alguien
renombra un endpoint en el backend y no en la web (o al revés), falla aquí y no en producción.
"""

import re

import pytest
from conftest import FRONTEND, auth_headers, client, login, register  # noqa: F401

JS_FILES = sorted((FRONTEND / "js").rglob("*.js"))
REQUEST = re.compile(r'request\(\s*"(GET|POST|PUT|PATCH|DELETE)"\s*,\s*(["`])(/api[^"`]*)\2')
DOC_SYNC = re.compile(r"createDocSync\(\{\s*path:\s*([\"`])(/api[^\"`]*)\1", re.S)


def to_api_v1(path: str) -> str:
    """La misma traducción que request() en frontend/js/api.js: /api/x → /api/v1/x."""
    path = path.split("?", 1)[0]
    if path.startswith("/api/v1/"):
        return path
    return "/api/v1" + path[4:]


def frontend_calls():
    calls = set()
    for file in JS_FILES:
        source = file.read_text(encoding="utf-8")
        rel = file.relative_to(FRONTEND).as_posix()
        for method, _q, path in REQUEST.findall(source):
            calls.add((method, to_api_v1(path), rel))
        for _q, path in DOC_SYNC.findall(source):
            # doc-sync.js hace GET para leer y PUT para guardar
            calls.add(("GET", to_api_v1(path), rel))
            calls.add(("PUT", to_api_v1(path), rel))
    return sorted(calls)


def matches(openapi_path: str, called: str) -> bool:
    """/api/v1/course-state/{course} encaja con /api/v1/course-state/${id} o .../learn."""
    pattern = re.sub(r"\\\{[^}]+\\\}", r"[^/]+", re.escape(openapi_path))
    concrete = re.sub(r"\$\{[^}]+\}", "x", called)
    return re.fullmatch(pattern, concrete) is not None


def test_el_frontend_hace_llamadas_a_la_api():
    assert len(frontend_calls()) >= 15, (
        "el extractor no encuentra las llamadas: ¿ha cambiado api.js?"
    )


@pytest.mark.parametrize(("method", "path", "source"), frontend_calls())
def test_cada_llamada_del_frontend_existe_en_la_api(openapi, method, path, source):
    candidates = [p for p in openapi["paths"] if matches(p, path)]
    assert candidates, f"{source}: {method} {path} no existe en la API"
    assert any(method.lower() in openapi["paths"][p] for p in candidates), (
        f"{source}: {method} {path} existe pero no admite {method}"
    )


def course_ids_used_by_frontend() -> set[str]:
    ids = set()
    store = (FRONTEND / "js" / "course-store.js").read_text(encoding="utf-8")
    block = store.split("export const DAW_COURSES = [", 1)[1].split("\n];", 1)[0]
    ids.update(re.findall(r'^\s*id:\s*"([\w-]+)"', block, re.M))
    for file in JS_FILES:
        if "/api/course-state/${COURSE}" in file.read_text(encoding="utf-8"):
            ids.update(re.findall(r'const COURSE = "([\w-]+)"', file.read_text(encoding="utf-8")))
    return ids


def test_los_cursos_que_sincroniza_la_web_los_acepta_la_api():
    from app.schemas import COURSES

    used = course_ids_used_by_frontend()
    assert {"learn", "game", "planner", "sql"} <= used, used
    assert used <= set(COURSES), (
        f"La API rechazaría (404) estos cursos: {sorted(used - set(COURSES))}"
    )


def test_health_tiene_los_campos_que_lee_la_web(client):  # noqa: F811
    # account.js: info.email (recuperación por email) e info.google («Continuar con Google»)
    body = client.get("/api/v1/health").json()
    assert body["status"] == "ok"
    assert isinstance(body["email"], bool) and isinstance(body["google"], bool)


def test_render_comprueba_una_ruta_de_salud_que_existe(client):  # noqa: F811
    from conftest import REPO

    health_path = re.search(r"healthCheckPath:\s*(\S+)", (REPO / "render.yaml").read_text()).group(
        1
    )
    assert client.get(health_path).status_code == 200


def test_login_devuelve_el_token_como_lo_lee_la_web(client):  # noqa: F811
    register(client)
    body = login(client).json()
    # account.js: const { access_token: token } = await request("POST", "/api/auth/login", ...)
    assert isinstance(body.get("access_token"), str) and body["access_token"]


def test_los_errores_422_traen_el_campo_que_marca_el_formulario(client):  # noqa: F811
    # api.js: detail.map((item) => item?.loc?.at(-1)) → nombre del campo (email, password...)
    detail = client.post("/api/v1/auth/register", json={}).json()["detail"]
    fields = {item["loc"][-1] for item in detail}
    assert {"email", "password"} <= fields


def test_course_state_guarda_y_devuelve_el_documento_versionado(client, auth_headers):  # noqa: F811
    # doc-sync.js: PUT {data, version} → respuesta con version; GET devuelve data y version
    saved = client.put(
        "/api/v1/course-state/learn",
        json={"data": {"qa": 1}, "version": None},
        headers=auth_headers,
    )
    assert saved.status_code == 200, saved.text
    assert isinstance(saved.json()["version"], int)
    loaded = client.get("/api/v1/course-state/learn", headers=auth_headers).json()
    assert loaded["data"] == {"qa": 1}
    assert loaded["version"] == saved.json()["version"]
