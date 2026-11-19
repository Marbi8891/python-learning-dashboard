"""Copia y restauración de la base de datos de PostgreSQL (Neon) con pg_dump y pg_restore (#111).

Uso (necesita las herramientas cliente de PostgreSQL, de la misma versión que el servidor o mayor):

  python scripts/ops/copia_bd.py copia --origen "$DATABASE_URL" --carpeta copias
  python scripts/ops/copia_bd.py restaura copias/pld-AAAAMMDD-HHMMSS.dump \\
      --destino "postgresql://…/pld_restaurada" --confirmo pld_restaurada [--limpia]
  python scripts/ops/copia_bd.py cuenta --url "postgresql://…"

- `copia` hace un volcado en formato personalizado (-Fc), comprueba que se puede leer
  (pg_restore --list) y guarda al lado un .json con las filas de cada tabla y el SHA-256.
- `restaura` vuelca la copia en otra base de datos y compara sus filas con las de la copia. Solo
  restaura si `--confirmo` repite el nombre de la base de datos de destino, y en una base con
  tablas solo con `--limpia`. Pensado para restaurar en una base aparte y comprobarla antes de
  cambiar `DATABASE_URL`: nunca encima de producción a la ligera.
- `cuenta` muestra las filas de cada tabla (para comparar a mano).

Las copias contienen datos personales (emails y progreso de los alumnos): se guardan cifradas o en
un sitio privado, nunca en el repositorio (`copias/` está en .gitignore) ni como artefacto público.
Las URLs no se muestran nunca con la contraseña.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

TABLES_SQL = (
    "SELECT table_name FROM information_schema.tables "
    "WHERE table_schema = 'public' AND table_type = 'BASE TABLE' ORDER BY 1"
)


def libpq_url(url: str) -> str:
    """pg_dump no entiende el prefijo de SQLAlchemy (`postgresql+psycopg://`)."""
    return re.sub(r"^postgres(ql)?(\+\w+)?://", "postgresql://", url)


def masked(url: str) -> str:
    parts = urlsplit(url)
    if parts.password:
        netloc = parts.netloc.replace(f":{parts.password}@", ":***@")
        return urlunsplit(parts._replace(netloc=netloc))
    return url


def database_name(url: str) -> str:
    return urlsplit(url).path.lstrip("/")


def tool(name: str) -> str:
    path = shutil.which(name)
    if not path:
        sys.exit(f"No encuentro {name}: instala las herramientas cliente de PostgreSQL.")
    return path


def run(args: list[str]) -> subprocess.CompletedProcess:
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode != 0:
        # pg_dump no escribe la contraseña en sus errores, pero por si acaso se enmascara
        sys.exit(f"Ha fallado {Path(args[0]).name}:\n{mask_all(result.stderr.strip())}")
    return result


def mask_all(text: str) -> str:
    return re.sub(r"(://[^:/@\s]+:)[^@\s]+@", r"\1***@", text)


# Un pg_dump más nuevo que el servidor escribe ajustes que el servidor no conoce (pg_dump 17+ pone
# `SET transaction_timeout = 0;` y PostgreSQL 16 no lo tiene). Ese error se puede ignorar: no toca
# datos y la comparación de filas lo confirma después. Cualquier otro error para la restauración.
UNKNOWN_SETTING = re.compile(r'unrecognized configuration parameter "(\w+)"')


def restore_errors(stderr: str) -> tuple[list[str], list[str]]:
    """Separa los errores de pg_restore en (ajustes desconocidos que se ignoran, errores reales)."""
    ignored, real = [], []
    for line in stderr.splitlines():
        if "error:" not in line:
            continue
        if found := UNKNOWN_SETTING.search(line):
            ignored.append(found.group(1))
        else:
            real.append(line.strip())
    return ignored, real


def psql(url: str, sql: str) -> list[str]:
    out = run([tool("psql"), "--no-psqlrc", "-At", "-d", url, "-c", sql]).stdout
    return [line for line in out.splitlines() if line]


def row_counts(url: str) -> dict[str, int]:
    tables = psql(url, TABLES_SQL)
    if not tables:
        return {}
    union = " UNION ALL ".join(f"SELECT '{t}', count(*) FROM \"{t}\"" for t in tables)
    return {name: int(n) for name, n in (line.split("|") for line in psql(url, union))}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def backup(origin: str, folder: Path) -> Path:
    url = libpq_url(origin)
    folder.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    target = folder / f"pld-{stamp}.dump"
    print(f"Copia de {masked(url)}")
    counts = row_counts(url)  # antes del volcado: si cambia algo entre medias, se verá al restaurar
    started = time.perf_counter()
    run([tool("pg_dump"), "-Fc", "--no-owner", "--no-acl", "-d", url, "-f", str(target)])
    seconds = time.perf_counter() - started
    entries = run([tool("pg_restore"), "--list", str(target)]).stdout.count("TABLE DATA")
    meta = {
        "file": target.name,
        "created_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "database": database_name(url),
        "bytes": target.stat().st_size,
        "sha256": sha256(target),
        "seconds": round(seconds, 2),
        "tables": counts,
    }
    target.with_suffix(".json").write_text(json.dumps(meta, indent=1) + "\n", encoding="utf-8")
    print(
        f"Hecha: {target} ({meta['bytes'] / 1e6:.1f} MB, {seconds:.1f} s, "
        f"{entries} tablas con datos, {sum(counts.values())} filas)"
    )
    return target


def restore(dump: Path, destination: str, confirm: str, clean: bool) -> bool:
    url = libpq_url(destination)
    name = database_name(url)
    if confirm != name:
        sys.exit(f"Para restaurar en «{name}» repite su nombre: --confirmo {name}")
    if not dump.is_file():
        sys.exit(f"No existe la copia {dump}")
    meta_path = dump.with_suffix(".json")
    meta = json.loads(meta_path.read_text("utf-8")) if meta_path.is_file() else None
    if meta and sha256(dump) != meta["sha256"]:
        sys.exit("La copia no coincide con su SHA-256: está dañada o la han cambiado.")
    if psql(url, TABLES_SQL) and not clean:
        sys.exit(f"«{name}» ya tiene tablas. Usa otra base vacía o añade --limpia (las borra).")
    print(f"Restaurando {dump.name} en {masked(url)}")
    started = time.perf_counter()
    args = [tool("pg_restore"), "--no-owner", "--no-acl", "-d", url]
    if clean:
        args += ["--clean", "--if-exists"]
    result = subprocess.run([*args, str(dump)], capture_output=True, text=True)
    if result.returncode != 0:
        ignored, real = restore_errors(result.stderr)
        if real or not ignored:
            sys.exit(f"Ha fallado pg_restore:\n{mask_all(result.stderr.strip())}")
        print(
            f"Aviso: el servidor no conoce {', '.join(sorted(set(ignored)))} (pg_restore más nuevo)"
        )
    seconds = time.perf_counter() - started
    counts = row_counts(url)
    print(f"Restaurada en {seconds:.1f} s: {sum(counts.values())} filas en {len(counts)} tablas")
    if not meta:
        print("Sin el .json de la copia no se pueden comparar las filas.")
        return True
    differ = {
        t: (meta["tables"].get(t), counts.get(t))
        for t in sorted(set(meta["tables"]) | set(counts))
        if meta["tables"].get(t) != counts.get(t)
    }
    if differ:
        for table, (expected, got) in differ.items():
            print(f"  {table}: la copia tenía {expected}, la restaurada tiene {got}")
        return False
    print("Todas las tablas tienen las mismas filas que la copia.")
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("copia")
    p.add_argument("--origen", required=True)
    p.add_argument("--carpeta", type=Path, default=Path("copias"))
    p = sub.add_parser("restaura")
    p.add_argument("copia", type=Path)
    p.add_argument("--destino", required=True)
    p.add_argument("--confirmo", required=True)
    p.add_argument("--limpia", action="store_true")
    p = sub.add_parser("cuenta")
    p.add_argument("--url", required=True)
    args = parser.parse_args(argv)
    if args.command == "copia":
        backup(args.origen, args.carpeta)
    elif args.command == "restaura":
        return 0 if restore(args.copia, args.destino, args.confirmo, args.limpia) else 1
    else:
        for table, n in row_counts(libpq_url(args.url)).items():
            print(f"{table}: {n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
