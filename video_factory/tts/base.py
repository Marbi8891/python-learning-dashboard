from __future__ import annotations

from pathlib import Path
from typing import Protocol


class TTSError(RuntimeError):
    pass


class TTSEngine(Protocol):
    """Un motor de voz: escribe un WAV con el texto leído en el idioma pedido."""

    name: str

    def cache_key(self, language: str) -> str:
        """Todo lo que cambia el sonido (motor, voz, velocidad): invalida la caché de audio."""

    def synthesize(self, text: str, language: str, out_path: Path) -> None: ...

    def close(self) -> None:
        """Libera el modelo de la memoria."""
