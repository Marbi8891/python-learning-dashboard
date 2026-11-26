"""Control de versiones de los documentos de progreso bajo concurrencia real (PLD-003).

El guardado compara y escribe en una sola sentencia (UPDATE ... WHERE version = :leída). Que dos
peticiones simultáneas no puedan ganar las dos depende de cómo bloquea PostgreSQL las filas, así que
se prueba con PostgreSQL de verdad, no con SQLite: en CI se activa con STATE_TEST_DATABASE_URL.
Cada prueba usa su propio esquema, así que no choca con las demás pruebas que usan la misma base.
"""

import os
import threading
from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app import state_documents
from app.config import Settings
from app.models import CourseState, PcapState, User
from app.schemas import PcapStateIn

URL = os.environ.get("STATE_TEST_DATABASE_URL")
SCHEMA = "pld003_state_versions"
WORKERS = 16

pytestmark = pytest.mark.skipif(not URL, reason="sin STATE_TEST_DATABASE_URL (solo en CI)")


@pytest.fixture
def sessions():
    admin = create_engine(Settings.use_psycopg_driver(URL))
    with admin.begin() as conn:
        conn.execute(text(f"DROP SCHEMA IF EXISTS {SCHEMA} CASCADE"))
        conn.execute(text(f"CREATE SCHEMA {SCHEMA}"))
    engine = create_engine(
        Settings.use_psycopg_driver(URL),
        pool_size=WORKERS + 4,
        connect_args={"options": f"-csearch_path={SCHEMA}"},
    )
    for table in (User.__table__, PcapState.__table__, CourseState.__table__):
        table.create(engine)
    make = sessionmaker(bind=engine, expire_on_commit=False)
    with make() as db:
        for n in range(1, WORKERS + 1):
            db.add(User(id=n, email=f"a{n}@example.com", password_hash="x", display_name=f"A{n}"))
        db.commit()
    yield make
    engine.dispose()
    with admin.begin() as conn:
        conn.execute(text(f"DROP SCHEMA {SCHEMA} CASCADE"))
    admin.dispose()


def _save(make, user_id, data, version, model=PcapState, course=None):
    """Una petición PUT: su propia sesión, como cada petición de la API. Devuelve el código."""
    key = {"user_id": user_id} | ({"course": course} if course else {})
    with make() as db:
        try:
            out = state_documents.save(db, model, key, PcapStateIn(data=data, version=version))
        except HTTPException as error:
            return error.status_code, None
        return 200, out.version


def _read(make, user_id):
    with make() as db:
        return state_documents.to_out(db.get(PcapState, user_id))


def _at_once(count, fn):
    """Lanza `count` llamadas que arrancan a la vez (barrera) y devuelve sus resultados."""
    barrier = threading.Barrier(count)

    def run(n):
        barrier.wait()
        return fn(n)

    with ThreadPoolExecutor(max_workers=count) as pool:
        return list(pool.map(run, range(count)))


def test_many_tabs_with_the_same_version_only_one_wins(sessions):
    assert _save(sessions, 1, {"base": True}, 0) == (200, 1)
    results = _at_once(WORKERS, lambda n: _save(sessions, 1, {"tab": n}, 1))
    codes = [code for code, _ in results]
    assert codes.count(200) == 1 and codes.count(409) == WORKERS - 1
    current = _read(sessions, 1)
    winner = next(n for n, (code, _) in enumerate(results) if code == 200)
    assert current.version == 2 and current.data == {"tab": winner}


def test_many_first_saves_at_the_same_time_create_it_once(sessions):
    results = _at_once(WORKERS, lambda n: _save(sessions, 1, {"tab": n}, 0))
    codes = [code for code, _ in results]
    assert codes.count(200) == 1 and codes.count(409) == WORKERS - 1
    assert _read(sessions, 1).version == 1


def test_tabs_that_reread_and_merge_never_lose_anything(sessions):
    """Como la web: cada pestaña añade lo suyo y, si recibe 409, relee, fusiona y reintenta."""
    _save(sessions, 1, {"answers": []}, 0)

    def tab(n):
        for _ in range(WORKERS * 2):
            current = _read(sessions, 1)
            merged = sorted(set(current.data["answers"]) | {f"q{n}"})
            code, _ = _save(sessions, 1, {"answers": merged}, current.version)
            if code == 200:
                return True
        return False

    assert all(_at_once(WORKERS, tab))
    final = _read(sessions, 1)
    assert final.data["answers"] == sorted(f"q{n}" for n in range(WORKERS))
    assert final.version == WORKERS + 1  # un guardado por pestaña, ninguno pisado


def test_saves_without_version_never_overwrite_an_existing_document(sessions):
    """Clientes antiguos (sin versión) a la vez que una pestaña actual: ninguno pisa nada."""
    _save(sessions, 1, {"de": "actual"}, 0)
    results = _at_once(
        WORKERS,
        lambda n: (
            _save(sessions, 1, {"de": f"antigua{n}"}, None)
            if n
            else _save(sessions, 1, {"de": "actual+1"}, 1)
        ),
    )
    assert results[0] == (200, 2)
    assert all(code == 428 for code, _ in results[1:])
    assert _read(sessions, 1).data == {"de": "actual+1"}


def test_different_users_save_at_the_same_time_without_blocking_each_other(sessions):
    for n in range(1, WORKERS + 1):
        _save(sessions, n, {}, 0)
    results = _at_once(WORKERS, lambda n: _save(sessions, n + 1, {"mio": n + 1}, 1))
    assert results == [(200, 2)] * WORKERS
    assert all(_read(sessions, n).data == {"mio": n} for n in range(1, WORKERS + 1))


def test_courses_of_the_same_user_are_independent_under_concurrency(sessions):
    courses = ["sql", "js", "java", "marcas"]
    results = _at_once(
        len(courses), lambda n: _save(sessions, 1, {"c": n}, 0, CourseState, courses[n])
    )
    assert results == [(200, 1)] * len(courses)


def test_a_failed_save_rolls_back_and_leaves_the_connection_usable(sessions):
    _save(sessions, 1, {"v": 1}, 0)
    with sessions() as db:
        with pytest.raises(HTTPException) as stale:
            state_documents.save(db, PcapState, {"user_id": 1}, PcapStateIn(data={}, version=0))
        assert stale.value.status_code == 409
        # La misma sesión sigue sirviendo (hubo rollback) y guarda con la versión buena
        out = state_documents.save(db, PcapState, {"user_id": 1}, PcapStateIn(data={}, version=1))
        assert out.version == 2