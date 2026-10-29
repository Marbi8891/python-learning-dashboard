"""Evaluación pedagógica del Python Tutor con un modelo DE VERDAD (no es un test de CI).

Usa los mismos casos versionados que la CI (`backend/tests/tutor_eval/casos.json`), pero con el
modelo configurado: recorre cada caso turno a turno con el agente real (plan, prompt, proveedor y
memoria de la conversación), aplica los criterios automáticos «modelo» que debe cumplir cualquier
modelo y escribe un informe en Markdown con cada respuesta, su latencia y sus tokens, y la rúbrica
para que una PERSONA la revise. Los criterios subjetivos (claridad, calidad de la pista…) no se
puntúan solos: se dejan como casillas sin marcar.

Con Ollama (gratis, local; por defecto):

    ollama pull qwen2.5-coder:7b
    python scripts/a2a/eval_tutor.py
    python scripts/a2a/eval_tutor.py --model qwen2.5-coder:14b --cases 01 04 16

Con Anthropic (DE PAGO: solo si se elige expresamente; clave solo en el entorno):

    python scripts/a2a/eval_tutor.py --provider anthropic

Sin modelo (comprueba el propio script):

    python scripts/a2a/eval_tutor.py --provider mock
"""

import argparse
import asyncio
import json
import logging
import os
import re
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

from app.a2a.agents.python_tutor import PythonTutorAgent, TutorQuery  # noqa: E402
from app.a2a.conversation import Conversation  # noqa: E402
from app.a2a.providers import MockModelProvider  # noqa: E402
from app.a2a.providers.base import ModelProviderError  # noqa: E402
from app.services.learning_context import LearnerContext, LessonContext  # noqa: E402

CASES = BACKEND / "tests" / "tutor_eval" / "casos.json"
LESSONS = ROOT / "frontend" / "data" / "lessons.json"
CLAIMS_EXECUTION = re.compile(r"(?<!no lo )\b(he|hemos) ejecutado\b", re.IGNORECASE)


def build_provider(name: str, model: str | None, timeout: float):
    if name == "mock":
        return MockModelProvider()
    if name == "ollama":
        from app.a2a.providers.ollama_provider import (
            DEFAULT_BASE_URL,
            DEFAULT_MODEL,
            OllamaProvider,
        )

        return OllamaProvider(
            base_url=os.environ.get("A2A_OLLAMA_BASE_URL", DEFAULT_BASE_URL),
            model=model or os.environ.get("A2A_MODEL") or DEFAULT_MODEL,
            max_tokens=2048,
            timeout_seconds=timeout,
        )
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not key:
        sys.exit("--provider anthropic necesita ANTHROPIC_API_KEY en el entorno (es de pago).")
    from app.a2a.providers.anthropic_provider import DEFAULT_MODEL, AnthropicProvider

    return AnthropicProvider(
        api_key=key, model=model or DEFAULT_MODEL, max_tokens=2048, timeout_seconds=timeout
    )


def lesson_context(slug: str) -> LessonContext:
    data = json.loads(LESSONS.read_text(encoding="utf-8"))
    for module in data["modules"]:
        for lesson in module["lessons"]:
            if lesson["slug"] == slug:
                return LessonContext(
                    slug=slug,
                    title=lesson["title"],
                    module_title=module["title"],
                    exercise=lesson.get("exercise"),
                    hint=(lesson.get("assistant") or {}).get("hint", ""),
                )
    raise SystemExit(f"Lección desconocida en los casos: {slug}")


class TokenLog(logging.Handler):
    """Recoge los tokens de la línea `a2a.model` que escriben los proveedores (sin contenido)."""

    def __init__(self):
        super().__init__()
        self.entries: list[dict] = []

    def emit(self, record: logging.LogRecord) -> None:
        try:
            entry = json.loads(record.getMessage())
        except ValueError:
            return
        if entry.get("event") == "a2a.model":
            self.entries.append(entry)


def check_turn(turn: dict, text: str, source: str) -> list[tuple[str, bool]]:
    """Criterios automáticos para cualquier modelo: sin afirmar ejecuciones y transparente."""
    rules = turn.get("modelo", {})
    results = [
        ("No afirma haber ejecutado el código", not CLAIMS_EXECUTION.search(text)),
        ("Dice de dónde sale la respuesta (source)", source in {"model", "prepared", "simulated"}),
    ]
    lower = text.lower()
    results += [(f"Contiene «{f}»", f.lower() in lower) for f in rules.get("contiene", [])]
    missing = rules.get("no_contiene", [])
    results += [(f"No contiene «{f}»", f not in text) for f in missing]  # literal, como en la CI
    options = rules.get("contiene_alguno")
    if options:
        found = any(option.lower() in lower for option in options)
        results.append((f"Contiene alguno de {options}", found))
    return results


async def run_case(agent: PythonTutorAgent, case: dict, tokens: TokenLog) -> list[str]:
    lines = [f"## {case['id']}", ""]
    if case.get("proveedor") == "no_disponible":
        return [*lines, "_No aplica con un modelo real: lo cubre la CI (test_tutor_eval.py)._", ""]
    conversation = Conversation()
    completed = case.get("preparacion", {}).get("ejercicio_superado")
    for number, turn in enumerate(case["turnos"], start=1):
        slug = turn.get("leccion")
        learner = None
        if slug:
            lesson = lesson_context(slug)
            learner = LearnerContext(0, 27, lesson=lesson, lesson_completed=slug == completed)
        query = TutorQuery(
            question=turn["pregunta"],
            lesson_slug=slug,
            code=turn.get("codigo"),
            error=turn.get("error"),
        )
        before = len(tokens.entries)
        started = time.perf_counter()
        try:
            answer = await agent.answer(query, learner, conversation)
            text, source, intent = answer.text, answer.source, answer.intent
        except ModelProviderError as error:
            text, source, intent = f"(el proveedor ha fallado: {type(error).__name__})", "-", "-"
        seconds = time.perf_counter() - started
        used = tokens.entries[before:]
        token_text = ", ".join(
            f"{e.get('input_tokens')} de entrada / {e.get('output_tokens')} de salida" for e in used
        )
        lines += [
            f"### Turno {number}: «{turn['pregunta']}»",
            "",
            f"Origen: `{source}` · tipo: `{intent}` · {seconds:.1f} s"
            + (f" · tokens: {token_text}" if token_text else ""),
            "",
            "```markdown",
            text.replace("```", "ʼʼʼ"),
            "```",
            "",
            "Comprobaciones automáticas:",
            "",
        ]
        lines += [f"- {'✅' if ok else '❌'} {name}" for name, ok in check_turn(turn, text, source)]
        rubric = turn.get("rubrica", [])
        if rubric:
            lines += ["", "Rúbrica (la revisa una persona):", ""]
            lines += [f"- [ ] {item}" for item in rubric]
        lines.append("")
    return lines


async def main() -> None:
    parser = argparse.ArgumentParser(description="Evalúa el Python Tutor con un modelo real.")
    parser.add_argument("--provider", choices=["ollama", "anthropic", "mock"], default="ollama")
    parser.add_argument("--model", help="por defecto, el de A2A_MODEL o el del proveedor")
    parser.add_argument("--timeout", type=float, default=300, help="segundos por respuesta")
    parser.add_argument("--cases", nargs="*", help="prefijos de los casos (por ejemplo 01 16)")
    parser.add_argument("--out", type=Path, default=ROOT / "tutor-eval-report.md")
    args = parser.parse_args()

    suite = json.loads(CASES.read_text(encoding="utf-8"))
    cases = [
        case
        for case in suite["casos"]
        if not args.cases or any(case["id"].startswith(prefix) for prefix in args.cases)
    ]
    provider = build_provider(args.provider, args.model, args.timeout)
    tokens = TokenLog()
    logging.getLogger("pld.a2a").addHandler(tokens)
    logging.getLogger("pld.a2a").setLevel(logging.INFO)

    agent = PythonTutorAgent(provider)
    report = [
        "# Evaluación del Python Tutor",
        "",
        f"- Casos: versión {suite['version']} ({len(cases)} de {len(suite['casos'])})",
        f"- Proveedor: {provider.name} · modelo: {provider.model}",
        f"- Fecha: {datetime.now(UTC):%Y-%m-%d %H:%M} UTC",
        "- Criterios: " + "; ".join(suite["criterios"]),
        "",
    ]
    for case in cases:
        print(f"→ {case['id']}", flush=True)
        report += await run_case(agent, case, tokens)
    failed = sum(line.startswith("- ❌") for line in report)
    report.insert(6, f"- Comprobaciones automáticas fallidas: {failed}")
    args.out.write_text("\n".join(report), encoding="utf-8")
    print(f"Informe: {args.out} ({failed} comprobaciones automáticas fallidas)")


if __name__ == "__main__":
    asyncio.run(main())
