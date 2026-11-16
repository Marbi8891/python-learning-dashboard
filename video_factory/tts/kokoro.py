"""Kokoro (ONNX) en local y en CPU: no necesita GPU ni servicios externos."""

from __future__ import annotations

import wave
from pathlib import Path

from video_factory.config import Settings
from video_factory.tts.base import TTSError

MODEL_FILE = "kokoro-v1.0.int8.onnx"
VOICES_FILE = "voices-v1.0.bin"
RELEASE = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0"
# Tamaños aproximados, para avisar antes de descargar.
DOWNLOADS = {MODEL_FILE: 92_400_000, VOICES_FILE: 28_300_000}
ESPEAK_LANGUAGE = {"es": "es", "en": "en-us"}


class KokoroEngine:
    name = "kokoro"

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._model = None

    def cache_key(self, language: str) -> str:
        return f"kokoro|{MODEL_FILE}|{self.settings.voice(language)}|{self.settings.tts_speed}"

    def _load(self):
        if self._model is None:
            model = self.settings.models_dir / MODEL_FILE
            voices = self.settings.models_dir / VOICES_FILE
            if not model.is_file() or not voices.is_file():
                raise TTSError(
                    f"Faltan los modelos de Kokoro en {self.settings.models_dir}. "
                    "Descárgalos con: python -m video_factory models --download"
                )
            try:
                from kokoro_onnx import Kokoro
            except ImportError as error:
                raise TTSError("Falta el paquete kokoro-onnx (pip install kokoro-onnx)") from error
            self._model = Kokoro(str(model), str(voices))
        return self._model

    def synthesize(self, text: str, language: str, out_path: Path) -> None:
        samples, rate = self._load().create(
            text,
            voice=self.settings.voice(language),
            speed=self.settings.tts_speed,
            lang=ESPEAK_LANGUAGE[language],
        )
        pcm = (samples.clip(-1.0, 1.0) * 32767).astype("<i2").tobytes()
        with wave.open(str(out_path), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(rate)
            wav.writeframes(pcm)

    def close(self) -> None:
        self._model = None
