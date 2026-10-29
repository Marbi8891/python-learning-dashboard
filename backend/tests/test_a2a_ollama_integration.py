"""Prueba opcional con un Ollama de verdad: A2A → Python Tutor → Ollama → modelo → respuesta.

No se ejecuta en CI ni por defecto. Para lanzarla, con Ollama en marcha y el modelo descargado:

    RUN_OLLAMA_INTEGRATION_TESTS=true python -m pytest tests/test_a2a_ollama_integration.py -s

Usa A2A_OLLAMA_BASE_URL y A2A_MODEL si están definidas (si no, los valores por defecto).
"""

import os

import pytest

from app.a2a.providers import MockModelProvider
from app.a2a.providers.ollama_provider import DEFAULT_BASE_URL, DEFAULT_MODEL, OllamaProvider
from tests.test_a2a import answer_text, send, state

pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_OLLAMA_INTEGRATION_TESTS") != "true",
    reason="Prueba con Ollama real: RUN_OLLAMA_INTEGRATION_TESTS=true",
)


def test_the_tutor_answers_with_the_local_model(client, auth_headers, monkeypatch):
    local = OllamaProvider(
        base_url=os.environ.get("A2A_OLLAMA_BASE_URL", DEFAULT_BASE_URL),
        model=os.environ.get("A2A_MODEL", DEFAULT_MODEL),
        max_tokens=1024,
        timeout_seconds=float(os.environ.get("A2A_MODEL_TIMEOUT_SECONDS", "300")),
    )

    async def generate_with_ollama(self, request):
        return await local.generate(request)

    # La app de los tests arranca con el modelo simulado: se sustituye por el local
    monkeypatch.setattr(MockModelProvider, "generate", generate_with_ollama)
    data = {"code": "numbers = [1, 2, 3]\nprint(numbers[5])", "error": "IndexError"}
    result = send(client, auth_headers, "¿Por qué falla este código?", data)

    assert state(result) == "TASK_STATE_COMPLETED"
    text = answer_text(result)
    print(f"\n--- Respuesta de {local.model} ---\n{text}")
    assert len(text) > 20
