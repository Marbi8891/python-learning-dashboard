"""Empezar simulacros verificados a la vez (PLD-001).

`start_exam` cuenta los simulacros del día y después inserta uno nuevo. Sin bloqueo, dos peticiones
simultáneas de la misma cuenta cuentan lo mismo, pasan las dos y se salta el límite diario.
Ahora cada inicio bloquea la fila de su usuario (`SELECT … FOR NO KEY UPDATE`): los de una misma
cuenta van de uno en uno y los de cuentas distintas no se esperan.

El bloqueo solo se puede demostrar con PostgreSQL: SQLite ignora `FOR UPDATE`. En CI estas pruebas
se activan con VERIFIED_TEST_DATABASE_URL; sin la variable se omiten (las de la lógica sin
concurrencia están en test_verified_exams.py y se ejecutan siempre).
"""

import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker

from app import verified_exams as exams
from app.config import Settings, get_settings
from app.database import Base
from app.models import User, VerifiedExam
from app.routers.verified import start_exam

URL = os.environ.get("VERIFIED_TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(not URL, reason="sin VERIFIED_TEST_DATABASE_URL (solo en CI)")

LIMIT = 3


@pytest.fixture
def pg(monkeypatch):
    """Una base PostgreSQL con las tablas de la app y un límite de 3 simulacros al día."""
    engine = create_engine(Settings.use_psycopg_driver(URL), pool_size=25, max_overflow=10)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    monkeypatch.setattr(get_settings(), "verified_exams_per_day", LIMIT)
    session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    yield session
    engine.dispose()
    engine = create_engine(Settings.use_psycopg_driver(URL))
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def slow_pick(monkeypatch):
    """Ensancha la ventana entre contar e insertar: sin bloqueo, la carrera sale siempre."""
    original = exams.pick_questions

    def slow():
        time.sleep(0.05)
        return original()

    monkeypatch.setattr(exams, "pick_questions", slow)


def new_user(session, email):
    with session() as db:
        user = User(email=email, password_hash="x", display_name=email.split("@")[0])
        db.add(user)
        db.commit()
        return user.id


def attempt(session, user_id, barrier=None):
    """Lo que hace una petición: carga el usuario (como la dependencia) y llama al endpoint."""
    with session() as db:
        user = db.get(User, user_id)
        if barrier is not None:
            barrier.wait()  # todas salen a la vez
        try:
            return start_exam(user, db).id
        except HTTPException as error:
            return error.status_code


def at_once(session, user_ids):
    barrier = threading.Barrier(len(user_ids))
    with ThreadPoolExecutor(max_workers=len(user_ids)) as pool:
        return list(pool.map(lambda uid: attempt(session, uid, barrier), user_ids))


def stored(session, user_id):
    with session() as db:
        return list(
            db.scalars(
                select(VerifiedExam.status)
                .where(VerifiedExam.user_id == user_id)
                .order_by(VerifiedExam.id)
            )
        )


def started(results):
    return [r for r in results if r != 429]


def test_two_simultaneous_requests_of_the_same_user(pg, slow_pick, monkeypatch):
    monkeypatch.setattr(get_settings(), "verified_exams_per_day", 1)
    ana = new_user(pg, "ana@example.com")
    results = at_once(pg, [ana, ana])
    assert results.count(429) == 1 and len(started(results)) == 1
    assert stored(pg, ana) == ["open"]


def test_many_simultaneous_requests_never_exceed_the_limit(pg, slow_pick):
    ana = new_user(pg, "ana@example.com")
    for _ in range(2):  # repetir la ráfaga cuando ya está en el límite no crea ninguno más
        results = at_once(pg, [ana] * 12)
        assert len(started(results)) == (LIMIT if _ == 0 else 0)
        assert results.count(429) == 12 - len(started(results))
    statuses = stored(pg, ana)
    assert len(statuses) == LIMIT
    assert statuses.count("open") == 1  # los anteriores quedaron abandonados, no abiertos


def test_reaching_exactly_the_limit_and_then_going_over(pg):
    ana = new_user(pg, "ana@example.com")
    for _ in range(LIMIT):
        assert attempt(pg, ana) != 429
    assert attempt(pg, ana) == 429
    assert stored(pg, ana) == ["abandoned"] * (LIMIT - 1) + ["open"]


def test_different_users_start_at_the_same_time(pg, slow_pick):
    users = [new_user(pg, f"alumno{n}@example.com") for n in range(8)]
    results = at_once(pg, users)
    assert 429 not in results and len(set(results)) == 8
    assert all(stored(pg, uid) == ["open"] for uid in users)


def test_one_user_waiting_does_not_block_another(pg):
    """Con el bloqueo de Ana retenido, Eva empieza igual; Ana espera hasta que se suelta."""
    ana, eva = new_user(pg, "ana@example.com"), new_user(pg, "eva@example.com")
    with pg() as holder:
        holder.scalar(select(User.id).where(User.id == ana).with_for_update(key_share=True))
        assert attempt(pg, eva) != 429  # otra fila: no espera
        done = []
        worker = threading.Thread(target=lambda: done.append(attempt(pg, ana)))
        worker.start()
        worker.join(timeout=0.5)
        assert worker.is_alive() and not done  # la misma fila: espera
        holder.rollback()
    worker.join(timeout=5)
    assert done and done[0] != 429
    assert stored(pg, ana) == ["open"] and stored(pg, eva) == ["open"]


def test_an_open_exam_is_abandoned_once_even_under_concurrency(pg, slow_pick, monkeypatch):
    monkeypatch.setattr(get_settings(), "verified_exams_per_day", 10)
    ana = new_user(pg, "ana@example.com")
    first = attempt(pg, ana)
    results = at_once(pg, [ana] * 4)
    assert 429 not in results
    with pg() as db:
        rows = {e.id: e.status for e in db.scalars(select(VerifiedExam))}
        open_ = [i for i, s in rows.items() if s == "open"]
    assert rows[first] == "abandoned"
    assert len(open_) == 1 and open_[0] == max(results)  # solo el último sigue en curso


def test_an_error_while_creating_rolls_back_and_releases_the_lock(pg, monkeypatch):
    ana = new_user(pg, "ana@example.com")
    previous = attempt(pg, ana)

    def broken():
        raise RuntimeError("fallo al elegir preguntas")

    monkeypatch.setattr(exams, "pick_questions", broken)
    with pytest.raises(RuntimeError):
        attempt(pg, ana)
    # Nada a medias: el anterior sigue abierto (el abandono también se deshizo) y no hay otro
    assert stored(pg, ana) == ["open"]
    monkeypatch.undo()
    monkeypatch.setattr(get_settings(), "verified_exams_per_day", LIMIT)
    # El bloqueo se soltó con el rollback: la siguiente petición entra sin esperar
    done = []
    worker = threading.Thread(target=lambda: done.append(attempt(pg, ana)))
    worker.start()
    worker.join(timeout=5)
    assert done and done[0] not in (429, previous)
    assert stored(pg, ana) == ["abandoned", "open"]


def test_an_account_deleted_meanwhile_gets_401_and_nothing_is_stored(pg):
    """La cuenta se borra entre la autenticación y el inicio: 401, sin error de clave ajena."""
    ana = new_user(pg, "ana@example.com")
    with pg() as db:
        user = db.get(User, ana)
        with pg() as other:  # otra sesión borra la cuenta antes de que esta empiece
            other.delete(other.get(User, ana))
            other.commit()
        with pytest.raises(HTTPException) as error:
            start_exam(user, db)
        assert error.value.status_code == 401
    with pg() as db:
        assert db.scalar(select(func.count()).select_from(VerifiedExam)) == 0
