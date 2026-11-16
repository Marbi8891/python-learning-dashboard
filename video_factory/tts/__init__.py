"""Síntesis de voz detrás de una interfaz: el resto del sistema no sabe qué motor se usa."""

from __future__ import annotations

from video_factory.config import Settings
from video_factory.tts.base import TTSEngine, TTSError


def create_engine(settings: Settings) -> TTSEngine:
    """Crea el motor configurado en PLD_TTS_ENGINE (se importa solo el que se usa)."""
    name = settings.tts_engine
    if name == "kokoro":
        from video_factory.tts.kokoro import KokoroEngine

        return KokoroEngine(settings)
    if name == "command":
        from video_factory.tts.command import CommandEngine

        return CommandEngine(settings)
    if name == "silent":
        from video_factory.tts.silent import SilentEngine

        return SilentEngine(settings)
    raise TTSError(f"Motor TTS desconocido: «{name}» (usa kokoro, command o silent)")


__all__ = ["TTSEngine", "TTSError", "create_engine"]
