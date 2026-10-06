"""Validación manual del Python Tutor con un modelo de verdad (ver docs/a2a.md).

Recorre la ruta real de la aplicación: HTTP → FastAPI → A2A (SDK oficial) → Python Tutor →
AgentModelProvider → OllamaProvider (u otro) → modelo, y vuelta. Arranca un uvicorn temporal con
una base de datos SQLite desechable, crea un alumno de prueba y hace 5 consultas (concepto, error,
depuración, ejercicio y solución; la primera con el cliente oficial de A2A). Después revisa el log
del servidor buscando secretos o contenido y muestra los tokens usados. No es un test de CI.

Con Ollama (gratis, local; por defecto):

    ollama pull qwen2.5-coder:7b
    python scripts/a2a/validate_tutor.py
    python scripts/a2a/validate_tutor.py --model qwen2.5-coder:14b

Con Anthropic (DE PAGO: solo si se elige expresamente). La clave se lee SOLO de la variable de
entorno ANTHROPIC_API_KEY, nunca como argumento:

    read -rs ANTHROPIC_API_KEY && export ANTHROPIC_API_KEY
    python scripts/a2a/validate_tutor.py --provider anthropic
    unset ANTHROPIC_API_KEY
"""

import argparse
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


def read_log(log: Path) -> str:
    return log.read_text(encoding="utf-8", errors="replace")


def start_server(
    workdir: Path, port: int, provider: str, model: str | None
) -> tuple[subprocess.Popen, Path]:
    env = {
        **os.environ,
        "DATABASE_URL": f"sqlite:///{(workdir / 'validacion.db').as_posix()}",
        "PYTHONUTF8": "1",  # el log en UTF-8 también en Windows
        "JWT_SECRET": secrets.token_urlsafe(48),
        "A2A_ENABLED": "true",
        "A2A_MOCK_MODEL": "false",
        "A2A_MODEL_PROVIDER": provider,
        "A2A_BASE_URL": f"http://127.0.0.1:{port}",
        "ANTHROPIC_LOG": "debug",  # el peor caso: el proveedor debe silenciarlo igualmente
    }
    if provider == "ollama":
        # Un modelo local en CPU puede tardar varios minutos en la primera respuesta
        env.setdefault("A2A_MODEL_TIMEOUT_SECONDS", "600")
    else:
        env.pop("A2A_MODEL_TIMEOUT_SECONDS", None)
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
    with log.open("w", encoding="utf-8") as output:
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
            stdout=output,
            stderr=subprocess.STDOUT,
        )
    for _ in range(60):
        try:
            if httpx.get(f"http://127.0.0.1:{port}/api/health").status_code == 200:
                return server, log
        except httpx.HTTPError:
            pass
        if server.poll() is not None:
            sys.exit(f"El servidor no arranca:\n{read_log(log)}")
        time.sleep(0.5)
    sys.exit("El servidor no responde")


async def ask_with_official_client(api: str, token: str, question: str) -> str:
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(timeout=900, headers=headers) as http:
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


def check_ollama(model: str) -> None:
    """Antes de arrancar: ¿responde Ollama y tiene el modelo descargado?"""
    base = os.environ.get("A2A_OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
    try:
        tags = httpx.get(f"{base}/api/tags", timeout=5, trust_env=False).json()
    except (httpx.HTTPError, ValueError):
        sys.exit(f"Ollama no responde en {base}. Arráncalo (ollama serve o la app de Ollama).")
    names = {item.get("name") for item in tags.get("models", [])}
    if model not in names and f"{model}:latest" not in names:
        sys.exit(f"Falta el modelo {model} en Ollama. Descárgalo con: ollama pull {model}")
    print(f"Ollama responde en {base} y tiene {model}.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Valida el Python Tutor con un modelo real.")
    parser.add_argument("--provider", choices=["ollama", "anthropic"], default="ollama")
    parser.add_argument("--model", help="por defecto, el de A2A_MODEL o el del proveedor")
    args = parser.parse_args()
    model = args.model or os.environ.get("A2A_MODEL")
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if args.provider == "anthropic":
        if not key:
            sys.exit("Falta ANTHROPIC_API_KEY en el entorno (no la pases como argumento).")
        print("Aviso: Anthropic es de pago; estas 5 consultas gastan tokens.")
    else:
        check_ollama(model or "qwen2.5-coder:7b")
    password = secrets.token_urlsafe(16)

    # En Windows la base de datos puede seguir bloqueada un instante al borrar la carpeta
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        port = free_port()
        api = f"http://127.0.0.1:{port}"
        server, log = start_server(Path(tmp), port, args.provider, model)
        try:
            with httpx.Client(base_url=api, timeout=900) as http:
                card = http.get("/.well-known/agent-card.json").text
                print("Agent Card sin modo simulado:", "simulado" not in card)
                if key:
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

        text = read_log(log)
        print("\n=== Revisión del log del servidor ===")
        leaks = {
            "API key": key or "sin-clave-en-este-modo",
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
