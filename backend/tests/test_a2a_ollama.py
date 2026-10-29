"""Proveedor Ollama (modelo local): petición, errores, seguridad y privacidad.

Ninguno de estos tests necesita Ollama, un modelo descargado, Internet ni API keys: la API de
Ollama se simula con `httpx.MockTransport`. La prueba con un Ollama de verdad es opcional y está
en `test_a2a_ollama_integration.py` (RUN_OLLAMA_INTEGRATION_TESTS=true).
"""

import asyncio
import json
import logging

import httpx
import pytest

from app.a2a.agents.python_tutor import SYSTEM_PROMPT
from app.a2a.providers import MockModelProvider, ModelRequest
from app.a2a.providers.base import (
    TRUNCATED_NOTICE,
    EmptyModelResponseError,
    MalformedModelResponseError,
    ModelConfigurationError,
    ModelRequestError,
    ModelTimeoutError,
    ModelUnavailableError,
)
from app.a2a.providers.ollama_provider import (
    CONTEXT_TOKENS,
    DEFAULT_BASE_URL,
    DEFAULT_MODEL,
    UNAVAILABLE,
    OllamaProvider,
    check_base_url,
)
from app.a2a.server import build_model_provider
from app.config import Settings
from tests.test_a2a import message, other_user, rpc, send, state

REQUEST = ModelRequest(system="Reglas del tutor", prompt="¿Qué es un bucle?", outline="Guía")


def reply(content="Un bucle repite instrucciones.", done_reason="stop", model=DEFAULT_MODEL):
    return {
        "model": model,
        "message": {"role": "assistant", "content": content},
        "done": True,
        "done_reason": done_reason,
        "prompt_eval_count": 85,
        "eval_count": 40,
    }


class FakeOllama:
    """La API de Ollama simulada: guarda cada petición y responde lo indicado."""

    def __init__(self, respond):
        self.respond = respond
        self.requests: list[httpx.Request] = []

    async def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        result = self.respond(request)
        if asyncio.iscoroutine(result):
            result = await result
        if isinstance(result, Exception):
            raise result
        if isinstance(result, httpx.Response):
            return result
        return httpx.Response(200, json=result)

    def bodies(self) -> list[dict]:
        return [json.loads(request.content) for request in self.requests]


def provider(api, base_url=DEFAULT_BASE_URL, model=DEFAULT_MODEL, timeout=5.0):
    return OllamaProvider(
        base_url=base_url,
        model=model,
        max_tokens=1024,
        timeout_seconds=timeout,
        transport=httpx.MockTransport(api),
    )


def generate(api, **options):
    return asyncio.run(provider(api, **options).generate(REQUEST))


# ---------- Configuración ----------


def test_ollama_is_the_default_provider_and_needs_no_key():
    model = build_model_provider(Settings(a2a_mock_model=False, anthropic_api_key=None))
    assert isinstance(model, OllamaProvider)
    assert (model.name, model.model, model.base_url) == ("ollama", DEFAULT_MODEL, DEFAULT_BASE_URL)
    assert Settings.model_fields["a2a_ollama_base_url"].default == DEFAULT_BASE_URL


def test_url_and_model_come_from_the_settings():
    model = build_model_provider(
        Settings(
            a2a_mock_model=False,
            a2a_ollama_base_url="http://ollama.interno:11434/",
            a2a_model="qwen2.5-coder:14b",
            a2a_max_output_tokens=800,
            a2a_model_timeout_seconds=30,
        )
    )
    assert (model.base_url, model.model) == ("http://ollama.interno:11434", "qwen2.5-coder:14b")
    assert (model.max_tokens, model.timeout_seconds) == (800, 30)
    assert repr(model) == (
        "OllamaProvider(base_url='http://ollama.interno:11434', model='qwen2.5-coder:14b')"
    )


@pytest.mark.parametrize(
    "url",
    [
        "file:///etc/passwd",
        "ftp://127.0.0.1:11434",
        "http://",
        "http://usuario:clave@127.0.0.1:11434",
        "http://127.0.0.1:11434/api/otra-cosa",
        "http://127.0.0.1:11434?destino=otro",
        "http://127.0.0.1:11434#x",
    ],
)
def test_only_plain_http_urls_are_accepted_for_ollama(url):
    with pytest.raises(ValueError):
        check_base_url(url)
    with pytest.raises(ValueError):
        build_model_provider(Settings(a2a_mock_model=False, a2a_ollama_base_url=url))


def test_mock_flag_wins_over_ollama():
    settings = Settings(a2a_mock_model=True, a2a_model_provider="ollama")
    assert isinstance(build_model_provider(settings), MockModelProvider)


# ---------- Petición a Ollama ----------


def test_request_goes_to_the_configured_url_with_model_and_minimal_prompt():
    api = FakeOllama(lambda _: reply())
    assert generate(api) == "Un bucle repite instrucciones."

    (request,) = api.requests
    assert str(request.url) == f"{DEFAULT_BASE_URL}/api/chat"
    assert request.method == "POST"
    # Ni API key ni cabeceras de autenticación: Ollama es local
    assert "authorization" not in request.headers and "x-api-key" not in request.headers
    assert json.loads(request.content) == {
        "model": DEFAULT_MODEL,
        "messages": [
            {"role": "system", "content": "Reglas del tutor"},
            {"role": "user", "content": "¿Qué es un bucle?"},
        ],
        "stream": False,
        "options": {"num_predict": 1024, "num_ctx": CONTEXT_TOKENS},
    }


def test_thinking_is_removed_and_truncation_is_announced():
    api = FakeOllama(lambda _: reply("<think>pienso…</think>\nRespuesta", done_reason="length"))
    assert generate(api) == f"Respuesta\n\n{TRUNCATED_NOTICE}"


def test_redirects_are_not_followed():
    api = FakeOllama(
        lambda _: httpx.Response(302, headers={"location": "http://169.254.169.254/latest"})
    )
    with pytest.raises(ModelRequestError):
        generate(api)
    assert len(api.requests) == 1


def test_environment_proxies_are_ignored(monkeypatch):
    monkeypatch.setenv("HTTP_PROXY", "http://proxy.malicioso:3128")
    monkeypatch.setenv("ALL_PROXY", "http://proxy.malicioso:3128")
    api = FakeOllama(lambda _: reply())
    generate(api)
    assert api.requests[0].url.host == "127.0.0.1"


# ---------- Errores ----------


@pytest.mark.parametrize(
    ("status", "failure"),
    [
        (404, ModelConfigurationError),  # modelo sin descargar
        (400, ModelRequestError),
        (500, ModelUnavailableError),
        (503, ModelUnavailableError),
    ],
)
def test_http_errors(status, failure):
    api = FakeOllama(lambda _: httpx.Response(status, json={"error": "detalle interno"}))
    with pytest.raises(failure) as raised:
        generate(api)
    assert "detalle interno" not in str(raised.value) and raised.value.__cause__ is None


def test_ollama_down_and_timeouts():
    def down(request):
        return httpx.ConnectError("conexión rechazada", request=request)

    def slow(request):
        return httpx.ReadTimeout("lento", request=request)

    async def hang(_):
        await asyncio.sleep(5)

    with pytest.raises(ModelUnavailableError):
        generate(FakeOllama(down))
    with pytest.raises(ModelTimeoutError):
        generate(FakeOllama(slow))
    with pytest.raises(ModelTimeoutError):  # el límite total corta aunque nada responda
        generate(FakeOllama(hang), timeout=0.05)


@pytest.mark.parametrize(
    ("respond", "failure"),
    [
        (lambda _: reply(""), EmptyModelResponseError),
        (lambda _: reply("   "), EmptyModelResponseError),
        (lambda _: reply("<think>solo pienso</think>"), EmptyModelResponseError),
        (lambda _: httpx.Response(200, text="no es json"), MalformedModelResponseError),
        (lambda _: [1, 2], MalformedModelResponseError),
        (lambda _: {"message": "texto"}, MalformedModelResponseError),
        (lambda _: {"message": {"content": 3}}, MalformedModelResponseError),
        (lambda _: {"done": True}, MalformedModelResponseError),
    ],
)
def test_empty_and_malformed_responses(respond, failure):
    with pytest.raises(failure):
        generate(FakeOllama(respond))


# ---------- Logs ----------


def test_logs_have_usage_but_no_content(caplog):
    caplog.set_level(logging.DEBUG)
    generate(FakeOllama(lambda _: reply("Respuesta privada del modelo")))
    for content in ("¿Qué es un bucle?", "Reglas del tutor", "Respuesta privada"):
        assert content not in caplog.text
    (usage,) = [json.loads(r.getMessage()) for r in caplog.records if "a2a.model" in r.getMessage()]
    assert usage | {"ms": 0} == {
        "event": "a2a.model",
        "provider": "ollama",
        "model": DEFAULT_MODEL,
        "served_by": DEFAULT_MODEL,
        "stop_reason": "stop",
        "input_tokens": 85,
        "output_tokens": 40,
        "ms": 0,
    }


# ---------- De punta a punta: A2A → tutor → Ollama ----------


def use_ollama(monkeypatch, api):
    """El tutor de la app responde con OllamaProvider contra la API simulada."""
    real = provider(api)

    async def generate_with_ollama(self, request):
        return await real.generate(request)

    monkeypatch.setattr(MockModelProvider, "generate", generate_with_ollama)


def test_ollama_only_receives_the_session_users_educational_context(
    client, auth_headers, monkeypatch
):
    api = FakeOllama(lambda _: reply("Respuesta del tutor local"))
    use_ollama(monkeypatch, api)
    luis = other_user(client)
    client.post(
        "/api/v1/lessons/variables/attempts",
        json={"code": "print('codigo-guardado-de-luis')", "passed": True},
        headers=luis,
    )
    data = {"lesson_slug": "variables", "code": "x = 'codigo-de-ana'", "error": "NameError"}
    # El alumno no puede cambiar el destino ni el modelo: esos campos se rechazan
    hijack = {"base_url": "http://169.254.169.254", "model": "otro", "host": "evil"}
    rejected = send(client, auth_headers, "intento", hijack)
    assert state(rejected) == "TASK_STATE_REJECTED"
    assert state(send(client, auth_headers, "pregunta-de-ana", data)) == "TASK_STATE_COMPLETED"
    assert state(send(client, luis, "pregunta-de-luis", {"lesson_slug": "variables"})) == (
        "TASK_STATE_COMPLETED"
    )

    assert {str(request.url) for request in api.requests} == {f"{DEFAULT_BASE_URL}/api/chat"}
    ana_body, luis_body = api.bodies()  # el mensaje rechazado no llegó al modelo
    ana_prompt = ana_body["messages"][1]["content"]
    luis_prompt = luis_body["messages"][1]["content"]
    assert "pregunta-de-ana" in ana_prompt and "codigo-de-ana" in ana_prompt
    assert "Ejercicio superado: no." in ana_prompt
    assert "Ejercicio superado: sí." in luis_prompt
    assert "pregunta-de-ana" not in luis_prompt and "codigo-de-ana" not in luis_prompt
    for body in (ana_body, luis_body):
        sent = json.dumps(body, ensure_ascii=False)
        assert body["model"] == DEFAULT_MODEL
        assert body["messages"][0] == {"role": "system", "content": SYSTEM_PROMPT}
        for private in ("ana@example.com", "luis@example.com", "Luis", "codigo-guardado"):
            assert private not in sent
        assert "Bearer" not in sent and "eyJ" not in sent and "169.254" not in sent


def test_ollama_down_gives_a_friendly_message(client, auth_headers, monkeypatch):
    def down(request):
        return httpx.ConnectError("Connection refused [Errno 111]", request=request)

    use_ollama(monkeypatch, FakeOllama(down))
    monkeypatch.setattr(MockModelProvider, "unavailable_message", UNAVAILABLE)
    response = rpc(client, auth_headers, "SendMessage", message())
    assert state(response.json()) == "TASK_STATE_FAILED"
    assert "El tutor local no está disponible" in response.text
    assert "Errno" not in response.text and "11434" not in response.text
    # El resto de la API sigue funcionando
    assert client.get("/api/health").status_code == 200
