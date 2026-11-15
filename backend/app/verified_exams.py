"""Simulacros del PCAP verificados por el servidor (#109).

El progreso del navegador (lecciones, aciertos, simulacros locales, XP) es orientativo: lo calcula
el propio navegador y el servidor solo lo guarda. Para lo que tenga valor fuera de la web (un
certificado, el seguimiento del piloto) hace falta algo que el servidor pueda comprobar:

- las 40 preguntas las elige el servidor, con el reparto por bloques del examen;
- la hora de inicio es la del servidor, y fuera de tiempo no se corrige;
- la nota la pone el servidor con las respuestas correctas de `frontend/data/pcap.json`;
- cada simulacro se entrega una sola vez: repetir la entrega devuelve la misma nota.

No es un examen vigilado: el banco es público y nadie mira la pantalla. «Verificado» quiere decir
corregido por el servidor, en su tiempo y sin poder inventar la nota, no que lo haya hecho la
persona sin ayuda. Así se explica en la web y en docs/HITOS_VERIFICADOS.md.
"""

from __future__ import annotations

import json
import random
from datetime import UTC, datetime, timedelta
from functools import lru_cache

from app.config import get_settings

# Margen para la red y el reloj del navegador: la web entrega sola al acabar el tiempo
GRACE = timedelta(minutes=2)
_random = random.SystemRandom()


@lru_cache
def bank() -> dict:
    """El examen y sus preguntas, por id (se lee una vez)."""
    data = json.loads(get_settings().pcap_file.read_text(encoding="utf-8"))
    return {
        "exam": data["exam"],
        "questions": {q["id"]: q for q in data["questions"]},
    }


def pick_questions() -> list[str]:
    """Tantas preguntas de cada bloque como tiene el examen real, en orden aleatorio."""
    exam, questions = bank()["exam"], bank()["questions"].values()
    picked: list[str] = []
    for block in exam["blocks"]:
        ids = [q["id"] for q in questions if q["block"] == block["slug"]]
        picked += _random.sample(ids, block["items"])
    _random.shuffle(picked)
    return picked


def deadline(started_at: datetime) -> datetime:
    return utc(started_at) + timedelta(minutes=bank()["exam"]["minutes"])


def utc(moment: datetime) -> datetime:
    """SQLite devuelve las fechas sin zona horaria; se guardan siempre en UTC."""
    return moment if moment.tzinfo else moment.replace(tzinfo=UTC)


def expired(started_at: datetime, now: datetime | None = None) -> bool:
    return (now or datetime.now(UTC)) > deadline(started_at) + GRACE


def answer_errors(question_ids: list[str], answers: dict[str, list[int]]) -> list[str]:
    """Qué tiene de imposible una entrega: preguntas que no son de este simulacro, opciones que no
    existen o repetidas, o más opciones marcadas de las que pide la pregunta."""
    allowed, questions = set(question_ids), bank()["questions"]
    errors = []
    for qid, chosen in answers.items():
        if qid not in allowed:
            errors.append(f"{qid}: no es una pregunta de este simulacro")
            continue
        q = questions[qid]
        if len(set(chosen)) != len(chosen):
            errors.append(f"{qid}: opción repetida")
        if any(not 0 <= option < len(q["options"]) for option in chosen):
            errors.append(f"{qid}: opción fuera de rango")
        if len(chosen) > len(q["answer"]):
            errors.append(f"{qid}: más opciones de las que pide la pregunta")
    return errors


def grade(question_ids: list[str], answers: dict[str, list[int]]) -> tuple[int, int]:
    """(aciertos, nota de 0 a 100). Sin contestar cuenta como fallo, como en el examen."""
    questions = bank()["questions"]
    correct = sum(
        sorted(answers.get(qid, [])) == sorted(questions[qid]["answer"]) for qid in question_ids
    )
    return correct, round(correct / len(question_ids) * 100)


def pass_mark() -> int:
    return bank()["exam"]["pass"]
