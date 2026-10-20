"""Logs de los agentes A2A: una línea JSON por tarea en el logger `pld.a2a`.

Permiten saber qué agente y qué modelo atendieron qué tarea, cuánto tardó, cómo acabó, de dónde
salió la respuesta (`source`: model, simulated o prepared), qué tipo de consulta era (`intent`) y,
si falló, por qué (`reason`). Con eso se calculan latencia, disponibilidad y tasa de fallos por
proveedor (ver docs/a2a.md, «Observabilidad»); los tokens van en la línea `a2a.model`. Nunca
llevan el texto de la pregunta, el prompt, el código, API keys, tokens, cookies ni datos
personales: el usuario va con seudónimo (como en `security_events`) y los errores solo con el
nombre de la excepción.
"""

import json
import logging
import time

from app.security_events import pseudonym

logger = logging.getLogger("pld.a2a")


def log_task(
    *,
    agent: str,
    provider: str,
    model: str,
    task_id: str,
    context_id: str,
    request_id: str | None,
    user: str,
    outcome: str,
    started: float,
    error: BaseException | None = None,
    **details: str | bool | None,
) -> None:
    """`details`: datos sin contenido del alumno (intent, source, level, reason…)."""
    entry: dict[str, object] = {
        "event": "a2a.task",
        "agent": agent,
        "provider": provider,
        "model": model,
        "task": task_id,
        "context": context_id,
        "request": request_id,
        "user": pseudonym(user),
        "outcome": outcome,
        "ms": round((time.perf_counter() - started) * 1000),
    }
    entry.update({key: value for key, value in details.items() if value is not None})
    if error is not None:
        entry["error"] = type(error).__name__
    level = logging.ERROR if outcome == "failed" else logging.INFO
    logger.log(level, json.dumps(entry, ensure_ascii=False, sort_keys=True))


def log_usage_error(error: BaseException) -> None:
    """La contabilidad del tutor híbrido ha fallado (la respuesta ya se ha dado): solo el tipo."""
    entry = {"event": "a2a.usage", "outcome": "failed", "error": type(error).__name__}
    logger.error(json.dumps(entry, ensure_ascii=False, sort_keys=True))
