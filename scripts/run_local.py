"""Ejecuta el Python Learning Dashboard en este ordenador.

Un solo proceso sirve la web y la API en http://127.0.0.1:<puerto>, solo accesible
desde este equipo. La primera vez crea la base de datos (backend/local.db) y una clave
secreta propia (backend/.local-secret). Tus datos no salen del ordenador; la consola
de Python necesita Internet la primera vez para descargar Pyodide.

Uso: doble clic en Iniciar-Dashboard.bat, o bien  python scripts/run_local.py
"""

import os
import secrets
import socket
import sys
import threading
import time
import urllib.request
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
SECRET_FILE = BACKEND / ".local-secret"
DATABASE = BACKEND / "local.db"
HOST = "127.0.0.1"  # solo este equipo: no se expone a la red local
PORTS = range(8000, 8020)


def local_secret() -> str:
    """Clave persistente: así las sesiones siguen valiendo tras reiniciar la app."""
    if not SECRET_FILE.exists():
        SECRET_FILE.write_text(secrets.token_urlsafe(48), encoding="utf-8")
    return SECRET_FILE.read_text(encoding="utf-8").strip()


def free_port() -> int:
    for port in PORTS:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            if probe.connect_ex((HOST, port)) != 0:
                return port
    sys.exit(f"No hay ningún puerto libre entre {PORTS.start} y {PORTS.stop - 1}.")


def open_browser_when_ready(url: str) -> None:
    for _ in range(60):
        try:
            with urllib.request.urlopen(f"{url}/api/health", timeout=1):
                break
        except OSError:
            time.sleep(0.5)
    if not os.environ.get("PLD_NO_BROWSER"):
        webbrowser.open(url)


def main() -> None:
    port = free_port()
    url = f"http://{HOST}:{port}"
    # Las variables de entorno tienen prioridad sobre backend/.env (el de desarrollo)
    os.environ.update(
        DATABASE_URL=f"sqlite:///{DATABASE.as_posix()}",
        JWT_SECRET=local_secret(),
        SERVE_FRONTEND="true",
        FRONTEND_URL=url,
        CORS_ORIGINS="[]",  # la web y la API comparten origen
    )
    os.chdir(BACKEND)  # alembic.ini y el paquete app están aquí
    sys.path.insert(0, str(BACKEND))

    import uvicorn
    from alembic.config import main as alembic

    from app.database import SessionLocal
    from app.seed import seed

    print("Preparando la base de datos…")
    alembic(["-q", "upgrade", "head"])
    with SessionLocal() as session:
        seed(session)

    print(
        "\n  Python Learning Dashboard funcionando en: " + url + "\n"
        "  (se abre solo en el navegador; si no, copia esa dirección)\n\n"
        "  Para cerrarlo: cierra esta ventana o pulsa Ctrl+C.\n"
    )
    threading.Thread(target=open_browser_when_ready, args=(url,), daemon=True).start()
    uvicorn.run("app.main:app", host=HOST, port=port, log_level="warning")


if __name__ == "__main__":
    main()
