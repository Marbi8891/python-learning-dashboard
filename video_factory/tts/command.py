"""Cualquier motor con línea de comandos (Piper, `say` de macOS, un proveedor externo…).

PLD_TTS_COMMAND es la orden, con estos huecos: {out} (WAV de salida), {voice}, {language} y
{text_file} (archivo con el texto). Si no aparece {text_file}, el texto se pasa por la entrada
estándar. Ejemplos:

    PLD_TTS_COMMAND=piper --model {voice} --output_file {out}
    PLD_TTS_COMMAND=say -v {voice} -o {out} --data-format=LEI16@24000 -f {text_file}
"""

from __future__ import annotations

import shlex
import subprocess
import tempfile
from pathlib import Path

from video_factory.config import Settings
from video_factory.tts.base import TTSError


class CommandEngine:
    name = "command"

    def __init__(self, settings: Settings) -> None:
        if not settings.tts_command:
            raise TTSError("PLD_TTS_ENGINE=command necesita PLD_TTS_COMMAND")
        self.settings = settings

    def cache_key(self, language: str) -> str:
        return f"command|{self.settings.tts_command}|{self.settings.voice(language)}"

    def synthesize(self, text: str, language: str, out_path: Path) -> None:
        with tempfile.NamedTemporaryFile("w", suffix=".txt", encoding="utf-8") as text_file:
            text_file.write(text)
            text_file.flush()
            values = {
                "out": str(out_path),
                "voice": self.settings.voice(language),
                "language": language,
                "text_file": text_file.name,
            }
            # Sin shell: el texto de la narración nunca se interpreta como una orden.
            command = [part.format(**values) for part in shlex.split(self.settings.tts_command)]
            uses_file = "{text_file}" in self.settings.tts_command
            done = subprocess.run(
                command,
                input=None if uses_file else text,
                capture_output=True,
                text=True,
                check=False,
            )
        if done.returncode != 0 or not out_path.is_file():
            raise TTSError(f"El motor TTS falló ({done.returncode}): {done.stderr.strip()[-400:]}")

    def close(self) -> None:
        pass
