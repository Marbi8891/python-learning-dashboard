"""Límites de intentos compartidos en la base de datos (#110).

Las pruebas con SQLite cubren la lógica: dos instancias comparten el límite, la ventana deslizante,
la caducidad, el borrado de ventanas viejas y la vuelta a memoria si la base de datos falla. La de
concurrencia necesita PostgreSQL de verdad: en CI se activa con RATE_LIMIT_TEST_DATABASE_URL.
"""

import logging
import os
from concurrent.futures import ThreadPoolExecutor

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.pool import StaticPool

from app import rate_limit
from app.config import Settings
from app.models import RateLimitWindow
from app.rate_limit import SharedRateLimiter


@pytest.fixture
def engine():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    RateLimitWindow.__table__.create(engine)
    rate_limit.set_engine(engine)
    yield engine
    rate_limit.set_engine(None)
    engine.dispose()


@pytest.fixture
def clock(monkeypatch):
    now = [1_008_000.0]  # múltiplo de 60 y de 900: empieza justo al principio de una ventana
    monkeypatch.setattr(rate_limit.time, "time", lambda: now[0])
    return now


def rows(engine):
    with engine.connect() as conn:
        return conn.execute(select(RateLimitWindow)).all()


def test_two_instances_share_the_same_limit(engine, clock):
    """Dos procesos de la API con el mismo límite: entre los dos no pasan de 3."""
    first, second = SharedRateLimiter("auth_ip", 3), SharedRateLimiter("auth_ip", 3)
    results = [first.hit("203.0.113.7"), second.hit("203.0.113.7"), first.hit("203.0.113.7")]
    assert results == [True, True, True]
    assert not second.hit("203.0.113.7") and not first.hit("203.0.113.7")
    assert first.blocked("203.0.113.7") and second.blocked("203.0.113.7")
    assert second.hit("198.51.100.1")  # otra IP, otro contador
    first.record("198.51.100.1")
    assert second.hit("198.51.100.1") and second.blocked("198.51.100.1")
    assert SharedRateLimiter("otro", 3).hit("203.0.113.7")  # otro límite, otro contador


def test_a_blocked_key_does_not_keep_counting(engine, clock):
    limiter = SharedRateLimiter("auth_ip", 2)
    for _ in range(10):
        limiter.hit("ip")
    (row,) = rows(engine)
    assert row.count == 2  # al estar bloqueado no suma: no se alarga el bloqueo


def test_the_previous_window_still_counts_while_it_overlaps(engine, clock):
    limiter = SharedRateLimiter("auth_ip", 4)
    clock[0] += 50  # al final de una ventana: 4 intentos
    assert all(limiter.hit("ip") for _ in range(4))
    clock[0] += 15  # 5 s en la siguiente: 55 de los últimos 60 s son de la anterior
    assert limiter.hit("ip")  # floor(4 · 55/60) = 3 de la anterior: cabe 1 más
    assert limiter.blocked("ip") and not limiter.hit("ip")
    clock[0] += 40  # 45 s dentro: floor(4 · 15/60) = 1, así que caben 3 (ya hay 1)
    assert limiter.hit("ip") and limiter.hit("ip") and not limiter.hit("ip")
    clock[0] += 120  # dos ventanas después, todo olvidado
    assert all(limiter.hit("ip") for _ in range(4))


def test_a_full_previous_window_blocks_without_writing(engine, clock):
    limiter = SharedRateLimiter("auth_ip", 2)
    assert limiter.hit("ip") and limiter.hit("ip")
    clock[0] += 60  # justo al empezar la siguiente: la anterior pesa entera
    assert not limiter.hit("ip")
    assert len(rows(engine)) == 1  # ni siquiera crea la fila de la ventana nueva


def test_by_default_it_uses_the_app_database():
    from app.database import engine as app_engine

    rate_limit.set_engine(None)
    assert rate_limit._engine() is app_engine


def test_clear_frees_the_key_for_every_instance(engine, clock):
    first, second = (
        SharedRateLimiter("login_account", 2, 900),
        SharedRateLimiter("login_account", 2, 900),
    )
    first.hit("ana@example.com")
    first.hit("ana@example.com")
    assert second.blocked("ana@example.com")
    second.clear("ana@example.com")  # login correcto en la otra instancia
    assert not first.blocked("ana@example.com")
    first.hit("ana@example.com")
    first.reset()
    assert rows(engine) == []


def test_the_table_has_no_emails_or_ips(engine, clock):
    SharedRateLimiter("login_account", 5).hit("ana@example.com")
    SharedRateLimiter("auth_ip", 5).hit("203.0.113.7")
    stored = " ".join(f"{row.scope} {row.key}" for row in rows(engine))
    assert "ana" not in stored and "203.0.113" not in stored
    assert all(len(row.key) == 64 for row in rows(engine))  # HMAC-SHA256 en hexadecimal


def test_old_windows_are_purged(engine, clock, monkeypatch):
    monkeypatch.setattr(rate_limit, "_PURGE_EVERY", 1)
    limiter = SharedRateLimiter("auth_ip", 5)
    limiter.hit("vieja")
    clock[0] += 60
    limiter.hit("anterior")
    assert len(rows(engine)) == 2  # la ventana anterior todavía cuenta: no se borra
    clock[0] += 60
    limiter.hit("nueva")
    assert sorted(row.window_start for row in rows(engine)) == [1_008_060, 1_008_120]


def test_without_the_database_it_falls_back_to_memory(clock, caplog):
    broken = create_engine("sqlite:////no/existe/limites.db")
    rate_limit.set_engine(broken)
    try:
        limiter = SharedRateLimiter("auth_ip", 2)
        with caplog.at_level(logging.WARNING, logger="app.rate_limit"):
            assert limiter.hit("203.0.113.7") and limiter.hit("203.0.113.7")
            assert not limiter.hit("203.0.113.7")  # sigue limitando, en esta instancia
            assert limiter.blocked("203.0.113.7")
            limiter.clear("203.0.113.7")
            assert not limiter.blocked("203.0.113.7")
            limiter.reset()
        assert "límite en memoria" in caplog.text
        assert "203.0.113" not in caplog.text and "/no/existe" not in caplog.text
    finally:
        rate_limit.set_engine(None)
        broken.dispose()


CONCURRENCY_URL = os.environ.get("RATE_LIMIT_TEST_DATABASE_URL")


@pytest.mark.skipif(not CONCURRENCY_URL, reason="sin RATE_LIMIT_TEST_DATABASE_URL (solo en CI)")
def test_concurrent_attempts_never_exceed_the_limit_in_postgresql():
    """40 intentos a la vez desde 4 «instancias» contra un límite de 5: pasan 5 exactamente."""
    engine = create_engine(Settings.use_psycopg_driver(CONCURRENCY_URL), pool_size=20)
    RateLimitWindow.__table__.drop(engine, checkfirst=True)
    RateLimitWindow.__table__.create(engine)
    rate_limit.set_engine(engine)
    try:
        instances = [SharedRateLimiter("auth_ip", 5, 3600) for _ in range(4)]
        for _ in range(3):  # varias rondas, cada una con una clave nueva
            key = f"203.0.113.{_}"
            with ThreadPoolExecutor(max_workers=20) as pool:
                results = list(pool.map(lambda n, k=key: instances[n % 4].hit(k), range(40)))
            assert results.count(True) == 5
        with engine.connect() as conn:
            assert conn.scalar(select(func.max(RateLimitWindow.count))) == 5
    finally:
        rate_limit.set_engine(None)
        RateLimitWindow.__table__.drop(engine)
        engine.dispose()
