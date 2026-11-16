"""Texto: de Markdown a narración, división en frases y líneas de subtítulo."""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any

ABBREVIATIONS = ("p. ej.", "e.g.", "i.e.", "etc.", "vs.", "Sr.", "Sra.", "Dr.")
_SENTENCE_END = re.compile(r"(?<=[.!?…])[\"»”)]*\s+(?=[\"«“(¿¡A-ZÁÉÍÓÚÑ0-9])")


def digest(value: Any) -> str:
    """Huella estable de cualquier dato serializable: decide si hay que rehacer un paso."""
    raw = json.dumps(value, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def strip_markdown(text: str) -> str:
    """Deja el texto listo para leerse en voz alta: sin marcas de Markdown."""
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\*{1,2}([^*\n]+)\*{1,2}", r"\1", text)
    text = text.replace("`", "")
    text = re.sub(r"^\s*(?:[-*]|\d+\.)\s+", "", text, flags=re.M)
    text = re.sub(r"^#+\s*", "", text, flags=re.M)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    lines = [line if line[-1] in ".:;!?…" else f"{line}." for line in lines]
    return re.sub(r"\s+", " ", " ".join(lines)).strip()


def bold_terms(text: str) -> list[str]:
    """Términos que la lección destaca en negrita, sin repetir y en su orden."""
    seen: list[str] = []
    for term in re.findall(r"\*\*([^*\n]+)\*\*", text):
        term = term.strip(" :.").replace("`", "")
        if term and term.lower() not in {s.lower() for s in seen}:
            seen.append(term)
    return seen


def split_sentences(text: str) -> list[str]:
    """Divide en frases sin romper abreviaturas ni decimales."""
    protected = text.strip()
    for index, abbreviation in enumerate(ABBREVIATIONS):
        protected = protected.replace(abbreviation, f"\x00{index}\x00")
    parts = _SENTENCE_END.split(protected)
    sentences = []
    for part in parts:
        for index, abbreviation in enumerate(ABBREVIATIONS):
            part = part.replace(f"\x00{index}\x00", abbreviation)
        if part.strip():
            sentences.append(part.strip())
    return sentences


def split_cue(sentence: str, max_chars: int = 84) -> list[str]:
    """Trocea una frase larga en fragmentos parecidos que caben en dos líneas de subtítulo."""
    if len(sentence) <= max_chars:
        return [sentence]
    pieces = -(-len(sentence) // max_chars)
    target = len(sentence) / pieces
    chunks, current = [], ""
    for word in sentence.split():
        candidate = f"{current} {word}".strip()
        remaining = pieces - len(chunks)
        # Se corta al llegar al tamaño objetivo, o un poco antes si hay una coma: se lee mejor.
        at_pause = current.endswith((",", ";", ":")) and len(current) >= target * 0.7
        if current and remaining > 1 and (len(candidate) > target or at_pause):
            chunks.append(current)
            current = word
        else:
            current = candidate
    chunks.append(current)
    return chunks


def wrap_two_lines(text: str, max_line: int = 42) -> str:
    """Parte un subtítulo en dos líneas equilibradas si no cabe en una."""
    if len(text) <= max_line:
        return text
    words = text.split()
    best, best_gap = None, None
    for cut in range(1, len(words)):
        first, second = " ".join(words[:cut]), " ".join(words[cut:])
        gap = abs(len(first) - len(second))
        if best_gap is None or gap < best_gap:
            best, best_gap = f"{first}\n{second}", gap
    return best or text


def word_count(text: str) -> int:
    return len(re.findall(r"\w+", text))


def estimate_seconds(text: str, words_per_minute: int = 150) -> float:
    return round(word_count(text) / words_per_minute * 60 + 1.0, 1)
