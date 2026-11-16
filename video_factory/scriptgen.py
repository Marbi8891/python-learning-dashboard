"""Generador de guiones: un borrador de escenas a partir del contenido real de la lección.

El borrador sale solo del temario (teoría, ejemplo, salida, ejercicio y resumen). La narración
en español es la teoría de la lección adaptada para leerse en voz alta; la inglesa no existe en
PLD, así que queda vacía y el guion no pasa a «scripted» hasta que alguien la escribe y la
revisa. Un guion editado (origin = "edited") nunca se sobrescribe sin --force.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

from video_factory.catalog import LessonSource
from video_factory.models import Bilingual, Scene, Script, Step
from video_factory.text import bold_terms, estimate_seconds, strip_markdown

EN_HEADINGS = {
    "Ejemplo": "Example",
    "Resultado": "Output",
    "Tu turno": "Your turn",
    "Resumen": "Summary",
}
MAX_BULLETS = 4


def _heading(spanish: str) -> Bilingual:
    return Bilingual(es=spanish, en=EN_HEADINGS.get(spanish, ""))


def _blocks(theory: str) -> list[tuple[str, str]]:
    """Trocea la teoría en bloques («text» o «code») respetando los bloques de código."""
    blocks: list[tuple[str, str]] = []
    for index, chunk in enumerate(re.split(r"```[a-zA-Z]*\n(.*?)```", theory, flags=re.S)):
        if index % 2:
            blocks.append(("code", chunk.rstrip("\n")))
            continue
        for paragraph in re.split(r"\n\s*\n", chunk):
            if paragraph.strip():
                blocks.append(("text", paragraph.strip()))
    return blocks


def _bullets(paragraph: str) -> list[str]:
    items = re.findall(r"^\s*(?:[-*]|\d+\.)\s+(.*)$", paragraph, flags=re.M)
    chosen = items or bold_terms(paragraph)
    return [strip_markdown(item).rstrip(".") for item in chosen[:MAX_BULLETS]]


def run_python_example(code: str, stdin: str = "", timeout: int = 10) -> str | None:
    """Ejecuta el ejemplo de la lección para enseñar su salida real (None si falla)."""
    try:
        done = subprocess.run(
            [sys.executable, "-I", "-c", code],
            input=stdin,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except (subprocess.TimeoutExpired, OSError):
        return None
    return done.stdout if done.returncode == 0 else None


def draft_script(source: LessonSource, run_examples: bool = True) -> Script:
    scenes: list[Scene] = []

    def add(scene_type: str, section: str, narration: str, **fields) -> None:
        scenes.append(
            Scene(
                id=f"s{len(scenes) + 1:02d}-{scene_type}",
                type=scene_type,
                section=section,
                estimated_seconds=estimate_seconds(narration),
                narration=Bilingual(es=narration),
                **fields,
            )
        )

    add(
        "title",
        "intro",
        f"{strip_markdown(source.title)} {strip_markdown(source.objective)}",
        heading=Bilingual(es=source.title),
        data={"kicker": {"es": f"{source.course} · {source.module}", "en": ""}},
    )

    heading = source.title
    for kind, block in _blocks(source.theory):
        if kind == "code":
            add(
                "code",
                "explanation",
                "",
                heading=Bilingual(es=heading),
                code=block,
                code_language=source.code_language,
                needs_edit=True,
            )
            continue
        title = re.match(r"^#+\s*(.+)$", block)
        if title:
            heading = strip_markdown(title.group(1)).rstrip(".")
            continue
        terms = bold_terms(block)
        add(
            "concept",
            "explanation",
            strip_markdown(block),
            heading=Bilingual(es=terms[0] if terms else heading),
            steps=[Step(text=Bilingual(es=item)) for item in _bullets(block)],
        )

    notes = [(line, strip_markdown(note)) for line, note in source.line_notes]
    add(
        "code",
        "example",
        " ".join(note for _, note in notes),
        heading=_heading("Ejemplo"),
        code=source.code,
        code_language=source.code_language,
        steps=[
            Step(line=line, text=Bilingual(es=note), sentence=index)
            for index, (line, note) in enumerate(notes)
        ],
        needs_edit=not notes,
    )

    output = source.output
    if output is None and run_examples and source.code_language == "python":
        output = run_python_example(source.code, source.stdin)
    add(
        "terminal",
        "result",
        "",
        heading=_heading("Resultado"),
        output=(output or "").rstrip("\n"),
        data={"command": "python programa.py" if source.code_language == "python" else ""},
        needs_edit=True,
    )

    add(
        "exercise",
        "exercise",
        strip_markdown(source.exercise),
        heading=_heading("Tu turno"),
        code=source.starter,
        code_language=source.code_language,
    )

    summary = [strip_markdown(item) for item in source.summary if item]
    summary = summary or [strip_markdown(term) for term in bold_terms(source.theory)[:MAX_BULLETS]]
    add(
        "summary",
        "summary",
        " ".join(item if item.endswith(".") else f"{item}." for item in summary),
        heading=_heading("Resumen"),
        steps=[Step(text=Bilingual(es=item.rstrip("."))) for item in summary[:5]],
    )

    return Script(
        lesson_id=source.id,
        title=Bilingual(es=source.title),
        course=Bilingual(es=f"{source.course} · {source.module}"),
        objectives=[Bilingual(es=strip_markdown(item)) for item in source.objectives],
        source_hash=source.fingerprint(),
        scenes=scenes,
    )


def script_path(scripts_dir: Path, lesson_id: str) -> Path:
    return scripts_dir / f"{lesson_id}.json"


def read_script(scripts_dir: Path, lesson_id: str) -> Script | None:
    path = script_path(scripts_dir, lesson_id)
    return Script.model_validate_json(path.read_text(encoding="utf-8")) if path.is_file() else None


def write_script(scripts_dir: Path, script: Script) -> Path:
    path = script_path(scripts_dir, script.lesson_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = script.model_dump(exclude_defaults=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path
