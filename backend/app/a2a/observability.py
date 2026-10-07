"""Logs de los agentes A2A: una línea JSON por tarea en el logger `pld.a2a`.

Permiten saber qué agente y qué modelo atendieron qué tarea, cuánto tardó y cómo acabó. Nunca
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
) -> None:
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
    if error is not None:
        entry["error"] = type(error).__name__
    level = logging.ERROR if outcome == "failed" else logging.INFO
    logger.log(level, json.dumps(entry, ensure_ascii=False, sort_keys=True))
