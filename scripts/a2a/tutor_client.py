"""Cliente A2A de ejemplo para el Python Tutor (ver docs/a2a.md).

Usa el cliente oficial del SDK (`a2a-sdk`): lee la Agent Card, inicia sesión en la API REST para
obtener el token y envía una pregunta por JSON-RPC (A2A 1.0).

    python scripts/a2a/tutor_client.py http://127.0.0.1:8000 tu@email.com "¿Qué es una tupla?"

La contraseña se pide por teclado (no se pasa como argumento para que no quede en el historial).
"""

import asyncio
import getpass
import sys

import httpx
from a2a.client import ClientConfig, create_client
from a2a.helpers import get_artifact_text, new_text_message
from a2a.types import Role, SendMessageRequest


async def ask(api: str, email: str, question: str) -> None:
    password = getpass.getpass(f"Contraseña de {email}: ")
    async with httpx.AsyncClient(timeout=30) as http:
        login = await http.post(
            f"{api}/api/v1/auth/login", data={"username": email, "password": password}
        )
        login.raise_for_status()
        token = login.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(timeout=60, headers=headers) as http:
        # La Agent Card (pública) dice dónde y cómo hablar con el agente
        client = await create_client(
            f"{api}/a2a/python-tutor", client_config=ClientConfig(httpx_client=http)
        )
        request = SendMessageRequest(message=new_text_message(question, role=Role.ROLE_USER))
        async for event in client.send_message(request):
            task = event.task
            if task.artifacts:
                print(get_artifact_text(task.artifacts[0]))
            else:
                print("Estado:", task.status.state)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    asyncio.run(ask(*sys.argv[1:]))
