"""Servidor estático de la web para los tests end-to-end (puerto 5500).

Es `python -m http.server` con HTTP/1.1. El de serie usa HTTP/1.0 y cierra la conexión después de
cada respuesta. En Windows, cuando Chromium pide el mismo archivo dos veces a la vez (app.js y
learn-app.js cargan data/lessons.json), una de las conexiones se cortaba (ERR_CONNECTION_RESET) y
la web no llegaba a pintar las lecciones.
"""

import functools
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

FRONTEND = Path(__file__).resolve().parents[1] / "frontend"


class Handler(SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5500
    handler = functools.partial(Handler, directory=str(FRONTEND))
    with ThreadingHTTPServer(("", port), handler) as server:
        server.serve_forever()
