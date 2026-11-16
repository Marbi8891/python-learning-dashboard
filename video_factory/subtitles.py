"""Subtítulos WebVTT sincronizados con la narración real, y su validación."""

from __future__ import annotations

import re
from pathlib import Path

from video_factory.text import split_cue, wrap_two_lines

_TIME = re.compile(r"^(\d{2}):(\d{2}):(\d{2})\.(\d{3}) --> (\d{2}):(\d{2}):(\d{2})\.(\d{3})$")


def _stamp(seconds: float) -> str:
    total = round(seconds * 1000)
    hours, rest = divmod(total, 3_600_000)
    minutes, rest = divmod(rest, 60_000)
    secs, millis = divmod(rest, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


def cues_from_timeline(timeline: dict) -> list[tuple[float, float, str]]:
    """Una entrada por frase; las frases largas se reparten según su número de caracteres."""
    cues = []
    for scene in timeline["scenes"]:
        for sentence in scene["sentences"]:
            chunks = split_cue(sentence["text"])
            span = sentence["end"] - sentence["start"]
            total = sum(len(chunk) for chunk in chunks)
            cursor = sentence["start"]
            for chunk in chunks:
                end = cursor + span * len(chunk) / total
                cues.append((round(cursor, 3), round(end, 3), wrap_two_lines(chunk)))
                cursor = end
    return cues


def to_vtt(timeline: dict) -> str:
    lines = ["WEBVTT", ""]
    for number, (start, end, text) in enumerate(cues_from_timeline(timeline), start=1):
        lines += [str(number), f"{_stamp(start)} --> {_stamp(end)}", text, ""]
    return "\n".join(lines)


def to_transcript(timeline: dict) -> str:
    """Transcripción legible: un párrafo por escena."""
    paragraphs = [" ".join(s["text"] for s in scene["sentences"]) for scene in timeline["scenes"]]
    return "\n\n".join(paragraph for paragraph in paragraphs if paragraph) + "\n"


def write_vtt(timeline: dict, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(to_vtt(timeline), encoding="utf-8")
    return path


def validate_vtt(content: str, duration: float | None = None) -> list[str]:
    """Devuelve los problemas encontrados (lista vacía = subtítulos válidos)."""
    lines = content.replace("\r\n", "\n").split("\n")
    if not lines or lines[0].strip() != "WEBVTT":
        return ["El archivo no empieza por WEBVTT"]
    problems, cues, previous_end = [], 0, 0.0
    blocks = "\n".join(lines[1:]).strip().split("\n\n")
    for block in blocks:
        rows = [row for row in block.split("\n") if row.strip()]
        if not rows:
            continue
        timing_row = next((i for i, row in enumerate(rows) if "-->" in row), None)
        if timing_row is None:
            problems.append(f"Bloque sin tiempos: {rows[0][:40]!r}")
            continue
        match = _TIME.match(rows[timing_row].strip())
        if not match:
            problems.append(f"Tiempo mal escrito: {rows[timing_row]!r}")
            continue
        h1, m1, s1, ms1, h2, m2, s2, ms2 = (int(part) for part in match.groups())
        start = h1 * 3600 + m1 * 60 + s1 + ms1 / 1000
        end = h2 * 3600 + m2 * 60 + s2 + ms2 / 1000
        text = rows[timing_row + 1 :]
        cues += 1
        if end <= start:
            problems.append(f"Subtítulo {cues}: termina antes de empezar")
        if start < previous_end - 0.001:
            problems.append(f"Subtítulo {cues}: se solapa con el anterior")
        if not text:
            problems.append(f"Subtítulo {cues}: sin texto")
        if len(text) > 2:
            problems.append(f"Subtítulo {cues}: más de dos líneas")
        if duration is not None and end > duration + 0.25:
            problems.append(f"Subtítulo {cues}: termina después del vídeo")
        previous_end = end
    if cues == 0:
        problems.append("No hay ningún subtítulo")
    return problems
