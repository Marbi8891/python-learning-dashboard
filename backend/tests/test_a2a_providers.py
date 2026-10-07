"""Proveedores de modelo del tutor (ADR-0034): Anthropic, selección, límites de coste y privacidad.

Ningún test usa una API key real ni sale a Internet: la API de Anthropic se simula con un
transporte HTTP falso (`httpx2.MockTransport`), así que se prueba el SDK oficial de verdad.
"""

import asyncio
import json
import logging

import anthropic
import httpx2
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.a2a.agents.python_tutor import SYSTEM_PROMPT
from app.a2a.executors.python_tutor import LIMITED
from app.a2a.providers import MockModelProvider, ModelRequest
from app.a2a.providers.anthropic_provider import (
    API_URL,
    EFFORT,
    FALLBACK_BETA,
    TRUNCATED_NOTICE,
    AnthropicProvider,
)
from app.a2a.providers.base import (
    EmptyModelResponseError,
    MalformedModelResponseError,
    ModelConfigurationError,
    ModelRateLimitedError,
    ModelRefusedError,
    ModelRequestError,
    ModelTimeoutError,
    ModelUnavailableError,
)
from app.a2a.server import build_model_provider, mount_a2a
from app.config import Settings
from tests.test_a2a import answer_text, message, other_user, rpc, send, state

# Clave inventada: solo sirve para comprobar que nunca aparece donde no debe
FAKE_KEY = "clave-falsa-solo-para-tests-0123456789"
REQUEST = ModelRequest(system="Reglas del tutor", prompt="¿Qué es un bucle?", outline="Guía")


def reply(*blocks, stop_reason="end_turn", model="claude-opus-5-5"):
    return {
        "id": "msg_test",
        "type": "message",
        "role": "assistant",
        "model": model,
        "content": list(blocks),
        "stop_reason": stop_reason,
        "stop_sequence": None,
        "usage": {"input_tokens": 120, "output_tokens": 30},
    }


def text(value):
    return {"type": "text", "text": value}


class FakeAnthropic:
    """La API de Anthropic simulada: guarda cada petición y responde lo indicado."""

    def __init__(self, respond):
        self.respond = respond
        self.requests: list[httpx2.Request] = []

    async def __call__(self, request: httpx2.Request) -> httpx2.Response:
        self.requests.append(request)
        result = self.respond(request)
        if asyncio.iscoroutine(result):
            result = await result
        if isinstance(result, Exception):
            raise result
        if isinstance(result, httpx2.Response):
            return result
        return httpx2.Response(200, json=result)

    def bodies(self) -> list[dict]:
        return [json.loads(request.content) for request in self.requests]


def provider(api, model="claude-opus-5-5", timeout=5.0, max_tokens=1024):
    client = anthropic.DefaultAsyncHttpxClient(transport=httpx2.MockTransport(api))
    return AnthropicProvider(
        api_key=FAKE_KEY,
        model=model,
        max_tokens=max_tokens,
        timeout_seconds=timeout,
        http_client=client,
    )


def generate(api, **options):
    return asyncio.run(provider(api, **options).generate(REQUEST))


# ---------- Inicialización y configuración ----------


def test_anthropic_is_built_from_settings_with_its_limits():
    settings = Settings(
        a2a_mock_model=False,
        a2a_model_provider="anthropic",
        anthropic_api_key=FAKE_KEY,
        a2a_model="claude-sonnet-5-5",
        a2a_max_output_tokens=2000,
        a2a_model_timeout_seconds=20,
    )
    model = build_model_provider(settings)
    assert isinstance(model, AnthropicProvider)
    assert (model.name, model.model, model.max_tokens) == ("anthropic", "claude-sonnet-5-5", 2000)
    assert model.deadline_seconds == 40  # un reintento como mucho
    # La clave no se ve al imprimir la configuración ni el proveedor
    assert FAKE_KEY not in repr(settings) and FAKE_KEY not in str(settings.model_dump())
    assert FAKE_KEY not in repr(model)


def test_mock_flag_wins_over_anthropic_so_tests_never_call_the_api():
    settings = Settings(a2a_mock_model=True, anthropic_api_key=FAKE_KEY)
    assert isinstance(build_model_provider(settings), MockModelProvider)


def test_provider_needs_a_key():
    with pytest.raises(ValueError):
        AnthropicProvider(api_key="  ", max_tokens=100, timeout_seconds=1)


def test_mock_provider_keeps_working():
    mock = MockModelProvider()
    assert (mock.name, mock.model) == ("mock", "mock")
    assert asyncio.run(mock.generate(REQUEST)).startswith("Guía")


def test_agent_card_never_has_the_key_or_the_mock_notice_in_production():
    app = FastAPI()
    mount_a2a(
        app,
        Settings(a2a_mock_model=False, a2a_model_provider="anthropic", anthropic_api_key=FAKE_KEY),
    )
    card = TestClient(app).get("/.well-known/agent-card.json")
    assert card.status_code == 200
    assert FAKE_KEY not in card.text
    assert "simulado" not in card.text and "anthropic" not in card.text.lower()


# ---------- Petición a Anthropic ----------


def test_request_uses_the_official_api_with_minimal_content():
    api = FakeAnthropic(lambda _: reply(text("Un bucle repite instrucciones.")))
    assert generate(api) == "Un bucle repite instrucciones."

    (request,) = api.requests
    assert str(request.url).startswith(f"{API_URL}/v1/messages")
    assert request.headers["x-api-key"] == FAKE_KEY  # solo en la cabecera hacia Anthropic
    assert request.headers["anthropic-beta"] == FALLBACK_BETA
    body = json.loads(request.content)
    assert body == {
        "model": "claude-opus-5-5",
        "max_tokens": 1024,
        "system": "Reglas del tutor",
        "messages": [{"role": "user", "content": "¿Qué es un bucle?"}],
        "output_config": {"effort": EFFORT},
        "fallbacks": "default",
    }  # sin metadata.user_id ni ningún otro dato del alumno


def test_models_without_server_fallback_do_not_send_it():
    api = FakeAnthropic(lambda _: reply(text("Hola"), model="claude-haiku-4-5"))
    generate(api, model="claude-haiku-4-5")
    assert "anthropic-beta" not in api.requests[0].headers
    assert "fallbacks" not in api.bodies()[0]


def test_base_url_cannot_be_redirected_from_the_environment(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_BASE_URL", "http://169.254.169.254")
    api = FakeAnthropic(lambda _: reply(text("Hola")))
    generate(api)
    assert api.requests[0].url.host == "api.anthropic.com"


def test_only_the_answer_after_a_fallback_counts():
    api = FakeAnthropic(
        lambda _: reply(
            {"type": "thinking", "thinking": "", "signature": "x"},
            text("respuesta parcial del modelo que se negó"),
            {"type": "fallback", "from_model": "claude-opus-5-5"},
            text("respuesta final"),
        )
    )
    assert generate(api) == "respuesta final"


def test_truncated_answers_say_so():
    api = FakeAnthropic(lambda _: reply(text("Primera parte"), stop_reason="max_tokens"))
    assert generate(api) == f"Primera parte\n\n{TRUNCATED_NOTICE}"


# ---------- Errores del proveedor ----------


@pytest.mark.parametrize(
    ("status", "failure"),
    [
        (400, ModelRequestError),
        (401, ModelConfigurationError),
        (403, ModelConfigurationError),
        (404, ModelConfigurationError),
        (429, ModelRateLimitedError),
        (500, ModelUnavailableError),
        (529, ModelUnavailableError),
    ],
)
def test_api_errors_become_provider_errors(status, failure):
    error = {"type": "error", "error": {"type": "x", "message": f"{FAKE_KEY} interno"}}
    api = FakeAnthropic(
        lambda _: httpx2.Response(status, json=error, headers={"retry-after-ms": "0"})
    )
    with pytest.raises(failure) as raised:
        generate(api)
    assert FAKE_KEY not in str(raised.value) and raised.value.__cause__ is None
    retried = status in (429, 500, 529)
    assert len(api.requests) == (2 if retried else 1)  # como mucho un reintento


def test_network_errors_and_timeouts():
    def down(request):
        return httpx2.ConnectError("sin red", request=request)

    def slow_read(request):
        return httpx2.ReadTimeout("lento", request=request)

    with pytest.raises(ModelUnavailableError):
        generate(FakeAnthropic(down))
    with pytest.raises(ModelTimeoutError):
        generate(FakeAnthropic(slow_read))


def test_a_hanging_call_is_cut_by_the_deadline():
    async def hang(_):
        await asyncio.sleep(5)

    with pytest.raises(ModelTimeoutError):
        generate(FakeAnthropic(hang), timeout=0.05)


@pytest.mark.parametrize(
    ("body", "failure"),
    [
        (reply(stop_reason="refusal"), ModelRefusedError),
        (reply(), EmptyModelResponseError),
        (reply(text("   ")), EmptyModelResponseError),
        (reply({"type": "thinking", "thinking": "", "signature": "x"}), EmptyModelResponseError),
        ({"type": "message", "content": "texto suelto"}, MalformedModelResponseError),
        (
            {"type": "message", "content": [{"type": "text", "text": 3}]},
            MalformedModelResponseError,
        ),
        ([1, 2, 3], MalformedModelResponseError),
        (httpx2.Response(200, text="<html>", headers={"content-type": "text/html"}), None),
    ],
)
def test_refused_empty_and_malformed_responses(body, failure):
    with pytest.raises(failure or MalformedModelResponseError):
        generate(FakeAnthropic(lambda _: body))


def test_responses_the_sdk_cannot_validate_are_malformed(monkeypatch):
    model = provider(FakeAnthropic(lambda _: reply(text("Hola"))))
    request = httpx2.Request("POST", f"{API_URL}/v1/messages")

    async def invalid(**_):
        response = httpx2.Response(200, request=request)
        raise anthropic.APIResponseValidationError(response=response, body=None)

    monkeypatch.setattr(model._client.beta.messages, "create", invalid)
    with pytest.raises(MalformedModelResponseError):
        asyncio.run(model.generate(REQUEST))


# ---------- Logs ----------


def test_logs_have_usage_but_never_the_key_or_the_content(caplog, monkeypatch):
    from anthropic._utils._logs import setup_logging

    caplog.set_level(logging.DEBUG)  # incluso con todo el detalle activado
    monkeypatch.setenv("ANTHROPIC_LOG", "debug")
    setup_logging()  # lo que hace el SDK al importarse con ANTHROPIC_LOG=debug
    generate(FakeAnthropic(lambda _: reply(text("Respuesta secreta del modelo"))))
    with pytest.raises(ModelRateLimitedError):
        generate(
            FakeAnthropic(lambda _: httpx2.Response(429, json={}, headers={"retry-after-ms": "0"}))
        )
    assert logging.getLogger("anthropic").level == logging.WARNING

    assert FAKE_KEY not in caplog.text
    for content in ("¿Qué es un bucle?", "Reglas del tutor", "Respuesta secreta"):
        assert content not in caplog.text
    usage = [json.loads(r.getMessage()) for r in caplog.records if "a2a.model" in r.getMessage()]
    assert usage[0] | {"ms": 0} == {
        "event": "a2a.model",
        "provider": "anthropic",
        "model": "claude-opus-5-5",
        "served_by": "claude-opus-5-5",
        "stop_reason": "end_turn",
        "input_tokens": 120,
        "output_tokens": 30,
        "provider_request": None,
        "ms": 0,
    }


# ---------- De punta a punta: privacidad entre usuarios ----------


@pytest.fixture
def anthropic_api(monkeypatch):
    """El tutor de la app responde con el proveedor de Anthropic contra la API simulada."""
    api = FakeAnthropic(lambda _: reply(text("Respuesta del tutor")))
    real = provider(api)

    async def generate_with_anthropic(self, request):
        return await real.generate(request)

    monkeypatch.setattr(MockModelProvider, "generate", generate_with_anthropic)
    return api


def test_the_provider_only_receives_the_session_users_data(client, auth_headers, anthropic_api):
    luis = other_user(client)
    client.post(
        "/api/v1/lessons/variables/attempts",
        json={"code": "print('codigo-guardado-de-luis')", "passed": True},
        headers=luis,
    )
    ana_data = {"lesson_slug": "variables", "code": "x = 'codigo-de-ana'", "error": "NameError"}
    ana = send(client, auth_headers, "pregunta-de-ana", ana_data)
    luis_result = send(client, luis, "pregunta-de-luis", {"lesson_slug": "variables"})
    assert answer_text(ana) == answer_text(luis_result) == "Respuesta del tutor"

    ana_body, luis_body = anthropic_api.bodies()
    ana_prompt = ana_body["messages"][0]["content"]
    luis_prompt = luis_body["messages"][0]["content"]
    assert "pregunta-de-ana" in ana_prompt and "codigo-de-ana" in ana_prompt
    assert "Ejercicio superado: no." in ana_prompt  # el progreso de Luis no cuenta para Ana
    assert "Ejercicio superado: sí." in luis_prompt
    assert "pregunta-de-ana" not in luis_prompt and "codigo-de-ana" not in luis_prompt
    for body in (ana_body, luis_body):
        sent = json.dumps(body, ensure_ascii=False)
        assert body["system"] == SYSTEM_PROMPT
        assert set(body) == {
            "model",
            "max_tokens",
            "system",
            "messages",
            "output_config",
            "fallbacks",
        }
        # Nada que identifique a nadie, ni intentos anteriores guardados, ni credenciales
        for private in ("ana@example.com", "luis@example.com", "Ana", "Luis", "codigo-guardado"):
            assert private not in sent
        assert "Bearer" not in sent and "eyJ" not in sent


def test_provider_errors_fail_the_task_with_a_generic_message(client, auth_headers, monkeypatch):
    api = FakeAnthropic(lambda _: httpx2.Response(401, json={"error": {"message": FAKE_KEY}}))
    real = provider(api)

    async def generate_with_anthropic(self, request):
        return await real.generate(request)

    monkeypatch.setattr(MockModelProvider, "generate", generate_with_anthropic)
    response = rpc(client, auth_headers, "SendMessage", message())
    assert state(response.json()) == "TASK_STATE_FAILED"
    assert MockModelProvider.unavailable_message in response.text  # clave inválida: no disponible
    assert FAKE_KEY not in response.text and "401" not in response.text


# ---------- Límites de coste ----------


def test_daily_limit_per_user_rejects_without_calling_the_model(client, auth_headers, monkeypatch):
    from app.main import app

    monkeypatch.setattr(app.state.a2a_budget.per_user, "max_calls", 2)
    calls = []

    async def counting(self, request):
        calls.append(request)
        return "respuesta"

    monkeypatch.setattr(MockModelProvider, "generate", counting)
    # Los mensajes no válidos no gastan consultas
    assert state(send(client, auth_headers, "x" * 5000)) == "TASK_STATE_REJECTED"
    assert state(send(client, auth_headers)) == "TASK_STATE_COMPLETED"
    assert state(send(client, auth_headers)) == "TASK_STATE_COMPLETED"
    limited = send(client, auth_headers)
    assert state(limited) == "TASK_STATE_REJECTED"
    assert LIMITED in json.dumps(limited, ensure_ascii=False)
    assert len(calls) == 2
    # Es por usuario: otro alumno sigue pudiendo preguntar
    assert state(send(client, other_user(client))) == "TASK_STATE_COMPLETED"


def test_global_limit_caps_all_users_together(client, auth_headers, monkeypatch):
    from app.main import app

    monkeypatch.setattr(app.state.a2a_budget.overall, "max_calls", 1)
    assert state(send(client, auth_headers)) == "TASK_STATE_COMPLETED"
    luis = other_user(client)
    assert state(send(client, luis)) == "TASK_STATE_REJECTED"
    # La consulta rechazada no cuenta en el límite diario de Luis
    assert not app.state.a2a_budget.per_user.blocked("user:2")
    assert len(app.state.a2a_budget.per_user._hits.get("user:2", ())) == 0
