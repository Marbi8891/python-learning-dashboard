"""Validación manual del Python Tutor con Anthropic de verdad (ver docs/a2a.md).

Recorre la ruta real de la aplicación: HTTP → FastAPI → A2A (SDK oficial) → Python Tutor →
AgentModelProvider → AnthropicProvider → API de Anthropic, y vuelta. Arranca un uvicorn temporal
con una base de datos SQLite desechable, crea un alumno de prueba y hace 5 consultas (la primera
con el cliente oficial de A2A). Después revisa el log del servidor buscando secretos o contenido.

GASTA DINERO REAL (5 llamadas, con los límites de A2A_MAX_OUTPUT_TOKENS). No es un test de CI.

La clave se lee SOLO de la variable de entorno ANTHROPIC_API_KEY; no se pasa como argumento ni
se imprime. Por ejemplo, para que no quede en el historial de la terminal:

    read -rs ANTHROPIC_API_KEY && export ANTHROPIC_API_KEY
    python scripts/a2a/validate_anthropic.py            # modelo por defecto (A2A_MODEL)
    python scripts/a2a/validate_anthropic.py claude-opus-5-5
    unset ANTHROPIC_API_KEY
"""

import asyncio
import json
import os
import secrets
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import httpx
from a2a.client import ClientConfig, create_client
from a2a.helpers import get_artifact_text, new_text_message
from a2a.types import Role, SendMessageRequest, TaskState

BACKEND = Path(__file__).resolve().parents[2] / "backend"
TUTOR = "/a2a/python-tutor"
EMAIL = "validacion-tutor@example.com"
NAME = "Alumna Validación"

CASES = [
    (
        "Concepto",
        "Explícame qué diferencia hay entre una lista y una tupla en Python.",
        None,
    ),
    (
        "Error",
        "¿Por qué falla este código?",
        {
            "code": "numbers = [1, 2, 3]\nprint(numbers[5])",
            "error": 'Traceback (most recent call last):\n  File "main.py", line 2, in '
            "<module>\n    print(numbers[5])\nIndexError: list index out of range",
        },
    ),
    (
        "Depuración",
        (
            "Mi función debería devolver la media de la lista pero el resultado no cuadra. "
            "Analízala sin ejecutarla."
        ),
        {
            "code": "def media(valores):\n    total = 0\n    for v in valores:\n"
            "        total += v\n    return total / (len(valores) + 1)\n\nprint(media([2, 4, 6]))",
        },
    ),
    (
        "Ejercicio",
        "¿Cómo puedo abordar este ejercicio? No me des la solución, solo cómo empezar.",
        {"lesson_slug": "variables"},
    ),
    (
        "Solución",
        "Dame la solución completa: una función que cuente las vocales de un texto.",
        None,
    ),
]


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def start_server(workdir: Path, port: int, model: str | None) -> tuple[subprocess.Popen, Path]:
    env = {
        **os.environ,
        "DATABASE_URL": f"sqlite:///{workdir / 'validacion.db'}",
        "JWT_SECRET": secrets.token_urlsafe(48),
        "A2A_ENABLED": "true",
        "A2A_MOCK_MODEL": "false",
        "A2A_MODEL_PROVIDER": "anthropic",
        "A2A_BASE_URL": f"http://127.0.0.1:{port}",
        "ANTHROPIC_LOG": "debug",  # el peor caso: el proveedor debe silenciarlo igualmente
    }
    if model:
        env["A2A_MODEL"] = model
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=BACKEND,
        env=env,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        [sys.executable, "-m", "app.seed"],
        cwd=BACKEND,
        env=env,
        check=True,
        capture_output=True,
    )
    log = workdir / "server.log"
    server = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--port",
            str(port),
            "--log-level",
            "info",
        ],
        cwd=BACKEND,
        env=env,
        stdout=log.open("w"),
        stderr=subprocess.STDOUT,
    )
    for _ in range(60):
        try:
            if httpx.get(f"http://127.0.0.1:{port}/api/health").status_code == 200:
                return server, log
        except httpx.HTTPError:
            pass
        if server.poll() is not None:
            sys.exit(f"El servidor no arranca:\n{log.read_text()}")
        time.sleep(0.5)
    sys.exit("El servidor no responde")


async def ask_with_official_client(api: str, token: str, question: str) -> str:
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(timeout=120, headers=headers) as http:
        client = await create_client(f"{api}{TUTOR}", client_config=ClientConfig(httpx_client=http))
        request = SendMessageRequest(message=new_text_message(question, role=Role.ROLE_USER))
        async for event in client.send_message(request):
            task = event.task
            state = TaskState.Name(task.status.state)
            if task.artifacts:
                return f"[{state}] {get_artifact_text(task.artifacts[0])}"
        return f"[{state}] (sin artefacto)"


def ask_with_json_rpc(http: httpx.Client, question: str, data: dict | None) -> dict:
    parts = [{"text": question}] + ([{"data": data}] if data else [])
    body = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "SendMessage",
        "params": {
            "message": {
                "messageId": secrets.token_hex(8),
                "role": "ROLE_USER",
                "parts": parts,
            }
        },
    }
    return http.post(TUTOR, json=body, headers={"A2A-Version": "1.0"}).json()


def main() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY", "").strip():
        sys.exit("Falta ANTHROPIC_API_KEY en el entorno (no la pases como argumento).")
    key = os.environ["ANTHROPIC_API_KEY"]
    model = sys.argv[1] if len(sys.argv) > 1 else None
    password = secrets.token_urlsafe(16)

    with tempfile.TemporaryDirectory() as tmp:
        port = free_port()
        api = f"http://127.0.0.1:{port}"
        server, log = start_server(Path(tmp), port, model)
        try:
            with httpx.Client(base_url=api, timeout=120) as http:
                card = http.get("/.well-known/agent-card.json").text
                print("Agent Card sin modo simulado:", "simulado" not in card)
                print("Agent Card sin la clave:", key not in card)
                http.post(
                    "/api/auth/register",
                    json={
                        "email": EMAIL,
                        "password": password,
                        "display_name": NAME,
                        "accept_privacy": True,
                    },
                ).raise_for_status()
                token = http.post(
                    "/api/auth/login", data={"username": EMAIL, "password": password}
                ).json()["access_token"]
                http.headers["Authorization"] = f"Bearer {token}"

                title, question, _ = CASES[0]
                print(f"\n=== 1. {title} (cliente oficial A2A) ===")
                print(asyncio.run(ask_with_official_client(api, token, question)))
                for number, (title, question, data) in enumerate(CASES[1:], start=2):
                    print(f"\n=== {number}. {title} ===")
                    task = ask_with_json_rpc(http, question, data)["result"]["task"]
                    print("Estado:", task["status"]["state"])
                    for artifact in task.get("artifacts", []):
                        print("Metadatos:", artifact.get("metadata"))
                        print(artifact["parts"][0]["text"])
                    if not task.get("artifacts"):
                        print(json.dumps(task["status"], ensure_ascii=False))
        finally:
            server.terminate()
            server.wait(timeout=10)

        text = log.read_text()
        print("\n=== Revisión del log del servidor ===")
        leaks = {
            "API key": key,
            "JWT del alumno": token,
            "contraseña": password,
            "email": EMAIL,
            "nombre": NAME,
            "cabecera Authorization": "Bearer ",
            "pregunta": CASES[0][1],
            "código del alumno": "numbers[5]",
            "x-api-key": "x-api-key",
        }
        for label, value in leaks.items():
            print(f"{'FUGA' if value in text else 'ok  '} {label}")
        usage = [
            json.loads(line[line.index("{") :])
            for line in text.splitlines()
            if '"a2a.model"' in line
        ]
        tasks = [
            json.loads(line[line.index("{") :])
            for line in text.splitlines()
            if '"a2a.task"' in line
        ]
        print("Llamadas al modelo:", len(usage))
        print("Tokens de entrada:", sum(u["input_tokens"] or 0 for u in usage))
        print("Tokens de salida:", sum(u["output_tokens"] or 0 for u in usage))
        print("Modelos:", sorted({str(u["served_by"]) for u in usage}))
        print("Tareas:", [(t["outcome"], t.get("error"), t["ms"]) for t in tasks])


if __name__ == "__main__":
    main()
