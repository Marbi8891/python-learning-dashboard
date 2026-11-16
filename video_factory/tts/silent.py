"""Motor mudo: silencio con la duración que tendría la lectura. Solo para pruebas y ensayos."""

from __future__ import annotations

import wave
from pathlib import Path

from video_factory.config import Settings
from video_factory.text import word_count

RATE = 24_000


class SilentEngine:
    name = "silent"

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def cache_key(self, language: str) -> str:
        return "silent"

    def synthesize(self, text: str, language: str, out_path: Path) -> None:
        seconds = max(word_count(text) / 2.6, 0.4)
        with wave.open(str(out_path), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(RATE)
            wav.writeframes(b"\x00\x00" * int(seconds * RATE))

    def close(self) -> None:
        pass
