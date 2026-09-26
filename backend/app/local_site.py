"""Modo aplicación local: la API sirve también el frontend (un solo proceso y un solo puerto).

Se activa con SERVE_FRONTEND=true (lo hace scripts/run_local.py).
"""

import mimetypes
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles

# En Windows, el registro puede tener tipos MIME incorrectos (por ejemplo .js como text/plain)
# y el navegador rechaza entonces los módulos JavaScript. Se fijan los correctos.
MIME_TYPES = {
    ".js": "text/javascript",
    ".mjs": "text/javascript",
    ".css": "text/css",
    ".json": "application/json",
    ".svg": "image/svg+xml",
    ".woff2": "font/woff2",
    ".wasm": "application/wasm",
}

# La web y la API comparten origen: la API está en la misma dirección que la página.
LOCAL_CONFIG_JS = (
    "window.PLD_CONFIG = Object.assign({ apiUrl: location.origin }, window.PLD_CONFIG);\n"
)


def mount_frontend(app: FastAPI, directory: Path) -> None:
    for extension, mime in MIME_TYPES.items():
        mimetypes.add_type(mime, extension)

    @app.get("/config.js", include_in_schema=False)
    def local_config() -> Response:
        return Response(
            LOCAL_CONFIG_JS, media_type="text/javascript", headers={"Cache-Control": "no-store"}
        )

    # Se monta al final: las rutas /api/... tienen prioridad
    app.mount("/", StaticFiles(directory=directory, html=True), name="frontend")
