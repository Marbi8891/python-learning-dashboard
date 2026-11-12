"""Copia y restauración de la base de datos (scripts/ops/copia_bd.py, #111).

Las comprobaciones de seguridad (no enseñar contraseñas, no restaurar sin confirmar) se prueban
siempre. El ensayo completo (migrar, copiar, restaurar en otra base y comparar filas) necesita un
PostgreSQL con permiso para crear bases de datos y pg_dump: en CI se activa con
BACKUP_TEST_DATABASE_URL apuntando a la base `postgres` del servicio.
"""

import importlib.util
import os
import shutil
import subprocess
from pathlib import Path
from urllib.parse import urlsplit

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text

from app.config import Settings, get_settings

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "ops" / "copia_bd.py"
spec = importlib.util.spec_from_file_location("copia_bd", SCRIPT)
copia_bd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(copia_bd)


def test_urls_never_show_the_password():
    url = "postgresql+psycopg://alumno:s3cr3t@ep-x.eu.aws.neon.tech/pld?sslmode=require"
    assert copia_bd.libpq_url(url).startswith("postgresql://alumno:s3cr3t@")
    assert copia_bd.libpq_url("postgres://a:b@h/d") == "postgresql://a:b@h/d"
    assert "s3cr3t" not in copia_bd.masked(url)
    assert (
        copia_bd.masked(url)
        == "postgresql+psycopg://alumno:***@ep-x.eu.aws.neon.tech/pld?sslmode=require"
    )
    assert copia_bd.masked("postgresql://h/d") == "postgresql://h/d"
    error = 'connection to "postgresql://alumno:s3cr3t@ep-x/pld" failed'
    assert "s3cr3t" not in copia_bd.mask_all(error)
    assert copia_bd.database_name(url) == "pld"


def test_restore_needs_the_target_name_repeated(tmp_path):
    with pytest.raises(SystemExit, match="--confirmo pld_prueba"):
        copia_bd.restore(tmp_path / "x.dump", "postgresql://u:p@h/pld_prueba", "pld", False)


def test_restore_refuses_a_missing_backup(tmp_path):
    with pytest.raises(SystemExit, match="No existe la copia"):
        copia_bd.restore(tmp_path / "x.dump", "postgresql://u:p@h/pld_prueba", "pld_prueba", False)


ADMIN_URL = os.environ.get("BACKUP_TEST_DATABASE_URL")


@pytest.mark.skipif(not ADMIN_URL, reason="sin BACKUP_TEST_DATABASE_URL (solo en CI)")
def test_backup_and_restore_rehearsal(tmp_path, monkeypatch, capsys):
    assert shutil.which("pg_dump") and shutil.which("pg_restore"), "faltan pg_dump/pg_restore"
    admin = copia_bd.libpq_url(ADMIN_URL)
    base = admin.rsplit("/", 1)[0]
    origin, target = f"{base}/pld_copia_origen", f"{base}/pld_copia_destino"

    def sql(statement):
        subprocess.run(["psql", "--no-psqlrc", "-q", "-d", admin, "-c", statement], check=True)

    for name in ("pld_copia_origen", "pld_copia_destino"):
        sql(f"DROP DATABASE IF EXISTS {name}")
        sql(f"CREATE DATABASE {name}")
    try:
        monkeypatch.setattr(get_settings(), "database_url", Settings.use_psycopg_driver(origin))
        command.upgrade(Config("alembic.ini"), "head")
        engine = create_engine(Settings.use_psycopg_driver(origin))
        with engine.begin() as conn:
            conn.execute(
                text(
                    "INSERT INTO users (email, password_hash, display_name) "
                    "VALUES ('a@b.c', 'x', 'A')"
                )
            )
            conn.execute(
                text("INSERT INTO course_states (user_id, course, data) VALUES (1, 'sql', '{}')")
            )
        engine.dispose()

        dump = copia_bd.backup(origin, tmp_path / "copias")
        assert dump.is_file() and dump.with_suffix(".json").is_file()
        assert copia_bd.restore(dump, target, "pld_copia_destino", False)
        restored = copia_bd.row_counts(target)
        assert restored == copia_bd.row_counts(origin)
        assert restored["users"] == 1 and restored["course_states"] == 1
        assert "alembic_version" in restored  # la restaurada sabe en qué migración está

        # Una segunda vez sin --limpia no pisa la base que ya tiene tablas
        with pytest.raises(SystemExit, match="ya tiene tablas"):
            copia_bd.restore(dump, target, "pld_copia_destino", False)
        # Una copia alterada no se restaura
        dump.write_bytes(dump.read_bytes() + b"x")
        with pytest.raises(SystemExit, match="SHA-256"):
            copia_bd.restore(dump, target, "pld_copia_destino", True)
        password = urlsplit(admin).password
        assert f":{password}@" not in capsys.readouterr().out  # se enseña :***@
    finally:
        for name in ("pld_copia_origen", "pld_copia_destino"):
            sql(f"DROP DATABASE IF EXISTS {name} WITH (FORCE)")


# Lo que escribió pg_restore 18 contra PostgreSQL 16 en CI (#143)
NEWER_CLIENT_STDERR = (
    "pg_restore: error: could not execute query: ERROR:  "
    'unrecognized configuration parameter "transaction_timeout"\n'
    "Command was: SET transaction_timeout = 0;\n"
    "pg_restore: warning: errors ignored on restore: 1\n"
)


def fake_restore(tmp_path, monkeypatch, stderr):
    """Una copia válida y un pg_restore simulado que termina con `stderr` y código 1."""
    dump = tmp_path / "pld.dump"
    dump.write_bytes(b"copia")
    meta = {"sha256": copia_bd.sha256(dump), "tables": {"users": 1}}
    dump.with_suffix(".json").write_text(copia_bd.json.dumps(meta), encoding="utf-8")
    monkeypatch.setattr(copia_bd, "tool", lambda name: name)
    monkeypatch.setattr(copia_bd, "psql", lambda url, sql: [])  # destino vacío
    monkeypatch.setattr(copia_bd, "row_counts", lambda url: {"users": 1})
    monkeypatch.setattr(
        copia_bd.subprocess,
        "run",
        lambda args, **kw: subprocess.CompletedProcess(args, 1, "", stderr),
    )
    return dump


def test_restore_tolerates_settings_unknown_to_an_older_server(tmp_path, monkeypatch, capsys):
    dump = fake_restore(tmp_path, monkeypatch, NEWER_CLIENT_STDERR)
    assert copia_bd.restore(dump, "postgresql://u:p@h/pld_prueba", "pld_prueba", False)
    out = capsys.readouterr().out
    assert "no conoce transaction_timeout" in out
    assert "mismas filas" in out  # la comparación de filas es la que da la restauración por buena


def test_restore_stops_on_any_other_error(tmp_path, monkeypatch):
    stderr = NEWER_CLIENT_STDERR + (
        'pg_restore: error: could not execute query: ERROR:  relation "users" already exists\n'
    )
    dump = fake_restore(tmp_path, monkeypatch, stderr)
    with pytest.raises(SystemExit, match="already exists"):
        copia_bd.restore(dump, "postgresql://u:p@h/pld_prueba", "pld_prueba", False)


def test_restore_errors_classifies_lines():
    ignored, real = copia_bd.restore_errors(NEWER_CLIENT_STDERR)
    assert ignored == ["transaction_timeout"]
    assert real == []
    assert copia_bd.restore_errors("pg_restore: error: connection failed") == (
        [],
        ["pg_restore: error: connection failed"],
    )
