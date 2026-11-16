"""Narración: una frase cada vez, con caché, y una línea de tiempo con la duración real.

La duración de cada escena la marca el audio (más unas pausas), nunca al revés: la animación
se adapta después a esa línea de tiempo.
"""

from __future__ import annotations

import json
import math
import re
import wave
from pathlib import Path

from video_factory.config import PACKAGE, Settings
from video_factory.media import ffmpeg
from video_factory.models import Script
from video_factory.text import digest, split_sentences
from video_factory.tts import TTSEngine

RATE = 48_000
LEAD_IN = 0.45  # silencio antes de la primera frase de la escena
GAP = 0.35  # pausa entre frases
TAIL = 0.75  # silencio al final: da tiempo a leer la pantalla antes de cambiar
FRAME = 1 / 30  # las escenas duran un número entero de fotogramas a 30 fps (y a 15)
TIMELINE_VERSION = 1


def load_pronunciation(language: str) -> list[tuple[re.Pattern, str]]:
    data = json.loads((PACKAGE / "pronunciation.json").read_text(encoding="utf-8"))
    return [(re.compile(pattern), spoken) for pattern, spoken in data.get(language, {}).items()]


def spoken_text(sentence: str, rules: list[tuple[re.Pattern, str]]) -> str:
    for pattern, spoken in rules:
        sentence = pattern.sub(spoken, sentence)
    return sentence


def _read_pcm(path: Path) -> bytes:
    with wave.open(str(path), "rb") as wav:
        if (wav.getframerate(), wav.getnchannels(), wav.getsampwidth()) != (RATE, 1, 2):
            raise ValueError(f"{path.name} no está en 48 kHz mono de 16 bits")
        return wav.readframes(wav.getnframes())


def _write_pcm(path: Path, pcm: bytes) -> None:
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(RATE)
        wav.writeframes(pcm)


def _silence(seconds: float) -> bytes:
    return b"\x00\x00" * round(seconds * RATE)


def _sentence_pcm(
    sentence: str, language: str, engine: TTSEngine, settings: Settings, rules
) -> bytes:
    """Voz de una frase en el formato común (48 kHz, mono, 16 bits). Con caché."""
    spoken = spoken_text(sentence, rules)
    key = digest([engine.cache_key(language), language, spoken])[:24]
    cached = settings.cache_dir / "tts" / f"{key}.wav"
    if not cached.is_file():
        cached.parent.mkdir(parents=True, exist_ok=True)
        raw = cached.with_suffix(".raw.wav")
        engine.synthesize(spoken, language, raw)
        temporary = cached.with_suffix(".tmp.wav")
        ffmpeg(
            "-i",
            str(raw),
            "-ar",
            str(RATE),
            "-ac",
            "1",
            "-c:a",
            "pcm_s16le",
            str(temporary),
        )
        raw.unlink()
        temporary.replace(cached)
    return _read_pcm(cached)


def _write_normalized(path: Path, pcm: bytes) -> None:
    """Volumen normalizado (EBU R128, -16 LUFS, picos bajo -1,5 dB) sin cambiar la duración."""
    raw = path.with_suffix(".raw.wav")
    _write_pcm(raw, pcm)
    temporary = path.with_suffix(".tmp.wav")
    ffmpeg(
        "-i",
        str(raw),
        "-af",
        "loudnorm=I=-16:TP=-1.5:LRA=11",
        "-ar",
        str(RATE),
        "-ac",
        "1",
        "-c:a",
        "pcm_s16le",
        str(temporary),
    )
    leveled = _read_pcm(temporary)
    # El filtro puede variar unas muestras: se iguala para no descuadrar la línea de tiempo.
    leveled = leveled[: len(pcm)] + b"\x00" * max(len(pcm) - len(leveled), 0)
    _write_pcm(path, leveled)
    raw.unlink()
    temporary.unlink()


def timeline_path(settings: Settings, lesson_id: str, language: str) -> Path:
    return settings.audio_dir(lesson_id, language) / "timeline.json"


def narration_path(settings: Settings, lesson_id: str, language: str) -> Path:
    return settings.audio_dir(lesson_id, language) / f"narration_{language}.wav"


def audio_inputs(script: Script, language: str, engine: TTSEngine) -> str:
    """Huella de todo lo que cambia el audio: si coincide, no se vuelve a sintetizar."""
    narration = [scene.narration.get(language) for scene in script.scenes]
    rules = [(p.pattern, s) for p, s in load_pronunciation(language)]
    return digest(
        [TIMELINE_VERSION, engine.cache_key(language), narration, rules, LEAD_IN, GAP, TAIL]
    )


def build_narration(
    script: Script, language: str, engine: TTSEngine, settings: Settings, force: bool = False
) -> dict:
    """Genera narration_<idioma>.wav y timeline.json. Devuelve la línea de tiempo."""
    out_dir = settings.audio_dir(script.lesson_id, language)
    timeline_file = timeline_path(settings, script.lesson_id, language)
    wav_file = narration_path(settings, script.lesson_id, language)
    inputs = audio_inputs(script, language, engine)
    if not force and timeline_file.is_file() and wav_file.is_file():
        previous = json.loads(timeline_file.read_text(encoding="utf-8"))
        if previous.get("inputs") == inputs:
            return previous

    out_dir.mkdir(parents=True, exist_ok=True)
    rules = load_pronunciation(language)
    track = bytearray()
    scenes = []
    for scene in script.scenes:
        start = len(track) / 2 / RATE
        sentences = []
        scene_pcm = bytearray(_silence(LEAD_IN))
        for index, sentence in enumerate(split_sentences(scene.narration.get(language))):
            if index:
                scene_pcm += _silence(GAP)
            voice = _sentence_pcm(sentence, language, engine, settings, rules)
            begin = len(scene_pcm) / 2 / RATE
            scene_pcm += voice
            sentences.append(
                {
                    "text": sentence,
                    "start": round(start + begin, 3),
                    "end": round(start + len(scene_pcm) / 2 / RATE, 3),
                }
            )
        scene_pcm += _silence(TAIL)
        # La escena dura un número entero de fotogramas: vídeo y audio no se desfasan al unir.
        frames = math.ceil(len(scene_pcm) / 2 / RATE / FRAME - 1e-9)
        total_samples = round(frames * FRAME * RATE)
        scene_pcm += b"\x00\x00" * (total_samples - len(scene_pcm) // 2)
        track += scene_pcm
        scenes.append(
            {
                "id": scene.id,
                "start": round(start, 3),
                "duration": round(frames * FRAME, 4),
                "sentences": sentences,
            }
        )
    _write_normalized(wav_file, bytes(track))
    timeline = {
        "lesson_id": script.lesson_id,
        "language": language,
        "engine": engine.name,
        "voice": settings.voice(language),
        "inputs": inputs,
        "duration": round(len(track) / 2 / RATE, 3),
        "scenes": scenes,
    }
    timeline_file.write_text(json.dumps(timeline, ensure_ascii=False, indent=2), encoding="utf-8")
    return timeline
