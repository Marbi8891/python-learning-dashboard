"""Evaluación pedagógica DETERMINISTA del Python Tutor (ADR-0036).

Recorre los casos versionados de `tutor_eval/casos.json` por la ruta real (HTTP → A2A → executor
→ agente) con el tutor sin modelo, y comprueba sus criterios «sin_ia»: intención, origen de la
respuesta, nivel, pregunta de comprobación, textos que deben estar o no y longitud.

Las respuestas de un modelo real no se pueden comprobar así: sus criterios («modelo» y
«rubrica») los aplica `scripts/a2a/eval_tutor.py`, fuera de la CI.
"""

import json
import re
from pathlib import Path

import pytest

from app.a2a.providers import MockModelProvider
from app.a2a.providers.base import ModelUnavailableError
from tests.test_a2a import rpc

CASES_FILE = Path(__file__).parent / "tutor_eval" / "casos.json"
SUITE = json.loads(CASES_FILE.read_text(encoding="utf-8"))
MOCK_FOOTER = re.compile(r"\n\n_Tutor sin IA:.*_$", re.DOTALL)
# Afirmar que se ha ejecutado el código («no lo he ejecutado» sí está permitido)
CLAIMS_EXECUTION = re.compile(r"(?<!no lo )\b(he|hemos) ejecutado\b", re.IGNORECASE)


def build_message(turn: dict, context_id: str | None) -> dict:
    data = {
        key: turn[field]
        for field, key in (("leccion", "lesson_slug"), ("codigo", "code"), ("error", "error"))
        if field in turn
    }
    parts = [{"text": turn["pregunta"]}]
    if data:
        parts.append({"data": data})
    message = {"messageId": f"m-{turn['pregunta'][:8]}", "role": "ROLE_USER", "parts": parts}
    if context_id:
        message["contextId"] = context_id
    return {"message": message}


def read(task: dict) -> tuple[str, dict, dict]:
    """Texto, metadatos del artefacto y metadatos del mensaje de estado."""
    if task.get("artifacts"):
        artifact = task["artifacts"][0]
        return artifact["parts"][0]["text"], artifact.get("metadata", {}), {}
    status = task["status"]["message"]
    return status["parts"][0]["text"], {}, status.get("metadata", {})


def test_the_suite_is_versioned_and_covers_the_required_cases():
    assert re.fullmatch(r"\d+\.\d+\.\d+", SUITE["version"])
    ids = [case["id"] for case in SUITE["casos"]]
    assert len(ids) == len(set(ids)) >= 18
    for number in range(1, 19):  # los 18 casos pedidos, numerados
        assert any(case_id.startswith(f"{number:02d}-") for case_id in ids)
    for case in SUITE["casos"]:
        assert all("pregunta" in turn and "sin_ia" in turn for turn in case["turnos"])


@pytest.mark.parametrize("case", SUITE["casos"], ids=lambda case: case["id"])
def test_case_without_model(case, client, auth_headers, monkeypatch):
    if case.get("proveedor") == "no_disponible":

        async def down(self, request):
            raise ModelUnavailableError()

        monkeypatch.setattr(MockModelProvider, "generate", down)
    lesson = case.get("preparacion", {}).get("ejercicio_superado")
    if lesson:
        url = f"/api/v1/lessons/{lesson}/attempts"
        assert client.post(url, json={"code": "x", "passed": True}, headers=auth_headers).is_success

    context_id = None
    for turn in case["turnos"]:
        expected = turn["sin_ia"]
        response = rpc(client, auth_headers, "SendMessage", build_message(turn, context_id))
        task = response.json()["result"]["task"]
        context_id = task["contextId"]
        text, meta, status_meta = read(task)
        where = f"{case['id']} · «{turn['pregunta']}»:\n{text}"

        assert task["status"]["state"] == expected.get("estado", "TASK_STATE_COMPLETED"), where
        if "motivo" in expected:
            assert status_meta.get("reason") == expected["motivo"], where
        for key, field in (
            ("intent", "intent"),
            ("source", "source"),
            ("nivel", "level"),
            ("espera_respuesta", "expects_answer"),
        ):
            if key in expected:
                assert meta.get(field) == expected[key], f"{key}: {meta}\n{where}"
        for fragment in expected.get("contiene", []):
            assert fragment in text, f"falta «{fragment}» en {where}"
        for fragment in expected.get("no_contiene", []):
            assert fragment not in text, f"sobra «{fragment}» en {where}"
        if "max_palabras" in expected:
            words = len(MOCK_FOOTER.sub("", text).split())
            assert words <= expected["max_palabras"], f"{words} palabras en {where}"
        # Transparencia: sin modelo, nunca se presenta como respuesta de una IA
        assert meta.get("source", "simulated") != "model", where
        assert not CLAIMS_EXECUTION.search(text), where
