"""Cliente de NEXARO AI: configuración, errores y lectura del NDJSON (sin salir a la red)."""

import asyncio
import json
import logging

import httpx
import pytest
from pydantic import SecretStr

from app.config import Settings
from app.nexaro_client import (
    NexaroBusy,
    NexaroClient,
    NexaroConfigError,
    NexaroUnavailable,
    check_config,
    create_client,
)

TOKEN = "t" * 40
MODEL = "qwen2.5:7b"


def settings(**changes) -> Settings:
    values = {
        "nexaro_enabled": True,
        "nexaro_base_url": "http://127.0.0.1:8080",
        "nexaro_model": MODEL,
        **changes,
    }
    return Settings(_env_file=None, **values)


# --------------------------------------------------------------------------- configuración


def test_disabled_by_default_creates_no_client():
    assert Settings(_env_file=None).nexaro_enabled is False
    assert create_client(Settings(_env_file=None)) is None


def test_valid_local_config_returns_normalized_base_url():
    assert check_config(settings()) == "http://127.0.0.1:8080"
    assert check_config(settings(nexaro_base_url="http://localhost:8080/")) == (
        "http://localhost:8080"
    )


def test_docker_service_and_remote_https_need_a_token():
    docker = settings(nexaro_base_url="http://nexaro-ai:8080", nexaro_service_token=TOKEN)
    assert check_config(docker) == "http://nexaro-ai:8080"
    remote = settings(
        nexaro_base_url="https://ai.example.com",
        nexaro_allowed_hosts=["ai.example.com"],
        nexaro_service_token=TOKEN,
    )
    assert check_config(remote) == "https://ai.example.com"


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"nexaro_base_url": None}, "NEXARO_BASE_URL"),
        ({"nexaro_model": None}, "NEXARO_MODEL"),
        ({"nexaro_model": "a/b/c"}, "NEXARO_MODEL"),  # dos barras: otro registro (SSRF en Ollama)
        ({"nexaro_model": "x..y"}, "NEXARO_MODEL"),
        ({"nexaro_base_url": "http://127.0.0.1:puerto"}, "no es una URL"),
        ({"nexaro_base_url": "ftp://127.0.0.1"}, "http:// o https://"),
        ({"nexaro_base_url": "http://"}, "http:// o https://"),
        ({"nexaro_base_url": "http://u:p@127.0.0.1:8080"}, "credenciales"),
        ({"nexaro_base_url": "http://127.0.0.1:8080?a=1"}, "credenciales"),
        ({"nexaro_base_url": "http://127.0.0.1:8080/#x"}, "credenciales"),
        ({"nexaro_base_url": "http://127.0.0.1:8080/api"}, "ruta"),
        ({"nexaro_base_url": "http://169.254.169.254"}, "NEXARO_ALLOWED_HOSTS"),
        (
            {
                "nexaro_base_url": "http://ai.example.com",
                "nexaro_allowed_hosts": ["ai.example.com"],
                "nexaro_service_token": TOKEN,
            },
            "https://",
        ),
        ({"nexaro_service_token": "corto"}, "al menos"),
        ({"nexaro_base_url": "http://nexaro-ai:8080"}, "NEXARO_SERVICE_TOKEN"),
        ({"nexaro_base_url": "http://nexaro-ai:8080", "nexaro_service_token": ""}, "TOKEN"),
    ],
)
def test_invalid_config_is_rejected(changes, message):
    with pytest.raises(NexaroConfigError, match=message):
        check_config(settings(**changes))
    with pytest.raises(NexaroConfigError):
        create_client(settings(**changes))


def test_config_error_never_contains_the_token():
    with pytest.raises(NexaroConfigError) as error:
        check_config(settings(nexaro_base_url="http://169.254.169.254", nexaro_service_token=TOKEN))
    assert TOKEN not in str(error.value)


# --------------------------------------------------------------------------- NEXARO simulado


class FakeNexaro:
    """NEXARO v3 simulado: rutas reales (/api/health, /api/models, /api/chat)."""

    def __init__(self):
        self.requests: list[httpx.Request] = []
        self.health = httpx.Response(200, json={"status": "ok", "ollama": "connected"})
        self.models = httpx.Response(200, json={"models": [{"name": MODEL}, "basura"]})
        self.chat = httpx.Response(200, text=ndjson({"message": {"content": "Hola"}, "done": True}))
        self.error: Exception | None = None

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        if self.error:
            raise self.error
        response = {"/api/health": self.health, "/api/models": self.models}.get(
            request.url.path, self.chat
        )
        # Una copia nueva cada vez: el cuerpo de una respuesta solo se puede leer una vez
        return httpx.Response(
            response.status_code, headers=response.headers, content=response.content
        )


def ndjson(*events) -> str:
    return "".join((e if isinstance(e, str) else json.dumps(e)) + "\n" for e in events)


def run(coroutine):
    return asyncio.run(coroutine)


def make(fake: FakeNexaro, **changes) -> NexaroClient:
    return NexaroClient(settings(**changes), transport=httpx.MockTransport(fake))


async def call(client: NexaroClient, method: str, *args):
    try:
        return await getattr(client, method)(*args)
    finally:
        await client.aclose()


def available(fake: FakeNexaro, **changes) -> bool:
    return run(call(make(fake, **changes), "available"))


def chat(fake: FakeNexaro, **changes) -> str:
    messages = [{"role": "user", "content": "¿Qué es una lista?"}]
    return run(call(make(fake, **changes), "chat", "tutor-programacion", messages))


def test_available_when_healthy_and_model_installed():
    fake = FakeNexaro()
    assert available(fake) is True
    assert [r.url.path for r in fake.requests] == ["/api/health", "/api/models"]


def test_status_is_cached_so_it_is_not_a_probe():
    fake = FakeNexaro()
    client = make(fake)

    async def twice():
        try:
            return [await client.available(), await client.available()]
        finally:
            await client.aclose()

    assert run(twice()) == [True, True]
    assert len(fake.requests) == 2  # una sola comprobación


def test_requests_carry_the_service_token_but_no_browser_data():
    fake = FakeNexaro()
    available(fake, nexaro_service_token=TOKEN)
    for request in fake.requests:
        assert request.headers["Authorization"] == f"Bearer {TOKEN}"
        assert "origin" not in request.headers
        assert "cookie" not in request.headers


def test_no_authorization_header_without_token():
    fake = FakeNexaro()
    available(fake, nexaro_service_token=SecretStr(""))
    assert "authorization" not in fake.requests[0].headers


def test_untagged_model_matches_latest():
    fake = FakeNexaro()
    fake.models = httpx.Response(200, json={"models": [{"name": "llama3:latest"}]})
    assert available(fake, nexaro_model="llama3") is True


@pytest.mark.parametrize(
    ("health", "models"),
    [
        (httpx.Response(200, json={"status": "degraded"}), None),
        (httpx.Response(200, json=["ok"]), None),
        (httpx.Response(200, text="no es json"), None),
        (httpx.Response(500, json={"status": "ok"}), None),
        (httpx.Response(429), None),
        # Una redirección no se sigue (podría llevar a otro host)
        (httpx.Response(301, headers={"Location": "http://169.254.169.254/"}), None),
        (httpx.Response(200, text='{"status": "ok", "x": "' + "a" * 300_000 + '"}'), None),
        (None, httpx.Response(200, json={"models": [{"name": "otro:1b"}]})),
        (None, httpx.Response(200, json=[MODEL])),
        (None, httpx.Response(503)),
    ],
)
def test_unavailable_answers(health, models):
    fake = FakeNexaro()
    fake.health = health or fake.health
    fake.models = models or fake.models
    assert available(fake) is False
    assert all(r.url.host == "127.0.0.1" for r in fake.requests)


def test_network_errors_mean_unavailable():
    fake = FakeNexaro()
    fake.error = httpx.ConnectError("rechazada")
    assert available(fake) is False
    fake.error = httpx.ReadTimeout("lento")
    with pytest.raises(NexaroUnavailable):
        chat(fake)


def test_chat_sends_only_the_closed_body_and_joins_the_stream():
    fake = FakeNexaro()
    fake.chat = httpx.Response(
        200,
        text=ndjson(
            {"message": {"role": "assistant", "content": "Una lista "}, "done": False},
            "",
            {"message": {"content": "", "tool_calls": [{"function": {"name": "rm"}}]}},
            {"message": {"thinking": "secreto", "content": "es mutable."}},
            {"message": "raro"},
            {"done": True},
            {"message": {"content": " (después de done)"}},
        ),
    )
    assert chat(fake) == "Una lista es mutable."
    body = json.loads(fake.requests[0].content)
    assert body == {
        "model": MODEL,
        "agent_id": "tutor-programacion",
        "messages": [{"role": "user", "content": "¿Qué es una lista?"}],
    }


@pytest.mark.parametrize(
    "response",
    [
        # NEXARO avisa de los fallos de Ollama dentro del stream, con HTTP 200
        httpx.Response(200, text=ndjson({"message": {"content": "Hola"}}, {"error": "Ollama"})),
        httpx.Response(200, text=ndjson("no es json")),
        httpx.Response(200, text=ndjson("[1, 2]")),
        httpx.Response(200, text=ndjson({"done": True})),  # respuesta vacía
        httpx.Response(500, json={"detail": "Error interno"}),
        httpx.Response(400, json={"detail": "El modelo seleccionado no está instalado."}),
    ],
)
def test_chat_failures_raise_unavailable(response):
    fake = FakeNexaro()
    fake.chat = response
    with pytest.raises(NexaroUnavailable):
        chat(fake)


def test_chat_busy_is_reported_apart():
    fake = FakeNexaro()
    fake.chat = httpx.Response(429, json={"detail": "Hay demasiadas respuestas"})
    with pytest.raises(NexaroBusy):
        chat(fake)


def test_chat_stops_reading_a_too_long_answer():
    fake = FakeNexaro()
    line = {"message": {"content": "x" * 600}}
    fake.chat = httpx.Response(200, text=ndjson(*[line] * 10))
    answer = chat(fake, nexaro_max_response_bytes=2048)
    assert 0 < len(answer) < 2048


def test_logs_have_no_token_nor_content(caplog):
    caplog.set_level(logging.INFO, logger="pld.ai")
    fake = FakeNexaro()
    fake.chat = httpx.Response(200, text=ndjson({"message": {"content": "respuesta"}}))
    assert chat(fake, nexaro_service_token=TOKEN) == "respuesta"
    assert "POST /api/chat -> 200" in caplog.text
    for secret in (TOKEN, "respuesta", "lista"):
        assert secret not in caplog.text


def test_chat_does_not_queue_when_all_slots_are_busy():
    fake = FakeNexaro()
    client = make(fake, ai_max_concurrency=1)

    async def scenario():
        try:
            client._in_flight = 1  # otra respuesta en curso
            with pytest.raises(NexaroBusy):
                await client.chat("tutor-programacion", [{"role": "user", "content": "hola"}])
            client._in_flight = 0
            answer = await client.chat("tutor-programacion", [{"role": "user", "content": "x"}])
            return answer, client._in_flight
        finally:
            await client.aclose()

    assert run(scenario()) == ("Hola", 0)
    assert len(fake.requests) == 1  # la primera ni siquiera llegó a NEXARO
