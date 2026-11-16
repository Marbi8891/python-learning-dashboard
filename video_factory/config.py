"""Configuración: rutas, calidades y variables de entorno (sin valores secretos en el código)."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PACKAGE = Path(__file__).resolve().parent
DATA = REPO / "frontend" / "data"
PRODUCTION = REPO / "video-production"
LANGUAGES = ("es", "en")


@dataclass(frozen=True)
class Quality:
    name: str
    width: int
    height: int
    fps: int
    crf: int
    preset: str


QUALITIES = {
    # Vista previa: rápida, para revisar ritmo y contenido en un portátil sin GPU.
    "preview": Quality("preview", 854, 480, 15, 30, "veryfast"),
    # Final: 1080p a 30 fps, H.264 + AAC, apto para web.
    "final": Quality("final", 1920, 1080, 30, 20, "medium"),
}


def load_env_file(path: Path) -> None:
    """Lee un .env sencillo (CLAVE=valor). No pisa variables ya definidas."""
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


@dataclass
class Settings:
    work_dir: Path = PRODUCTION
    models_dir: Path = Path.home() / ".cache" / "pld-video-factory" / "models"
    tts_engine: str = "kokoro"
    voice_es: str = "ef_dora"
    voice_en: str = "af_heart"
    tts_speed: float = 1.0
    tts_command: str = ""
    renderer: str = "manim"
    music_file: str = ""
    music_volume_db: float = -26.0
    font_sans: str = "Helvetica Neue"
    font_mono: str = "Menlo"
    publish_dir: Path = field(default_factory=lambda: REPO / "frontend" / "videos")

    @classmethod
    def from_env(cls) -> Settings:
        load_env_file(PACKAGE / ".env")
        env = os.environ.get
        base = cls()
        return cls(
            work_dir=Path(env("PLD_VIDEO_WORK_DIR", str(base.work_dir))).expanduser(),
            models_dir=Path(env("PLD_TTS_MODELS_DIR", str(base.models_dir))).expanduser(),
            tts_engine=env("PLD_TTS_ENGINE", base.tts_engine),
            voice_es=env("PLD_TTS_VOICE_ES", base.voice_es),
            voice_en=env("PLD_TTS_VOICE_EN", base.voice_en),
            tts_speed=float(env("PLD_TTS_SPEED", str(base.tts_speed))),
            tts_command=env("PLD_TTS_COMMAND", ""),
            renderer=env("PLD_RENDERER", base.renderer),
            music_file=env("PLD_MUSIC_FILE", ""),
            music_volume_db=float(env("PLD_MUSIC_VOLUME_DB", str(base.music_volume_db))),
            font_sans=env("PLD_FONT_SANS", base.font_sans),
            font_mono=env("PLD_FONT_MONO", base.font_mono),
            publish_dir=Path(env("PLD_VIDEO_PUBLISH_DIR", str(base.publish_dir))).expanduser(),
        )

    def voice(self, language: str) -> str:
        return self.voice_es if language == "es" else self.voice_en

    # Lo que se versiona (pequeño y revisable) vive siempre en video-production/ del repo.
    @property
    def catalog_path(self) -> Path:
        return PRODUCTION / "catalog.json"

    @property
    def scripts_dir(self) -> Path:
        return PRODUCTION / "scripts"

    @property
    def reports_dir(self) -> Path:
        return PRODUCTION / "reports"

    # Lo pesado (audio, clips, MP4) va a work_dir, que puede estar fuera del repositorio.
    def audio_dir(self, lesson_id: str, language: str) -> Path:
        return self.work_dir / "audio" / lesson_id / language

    def clips_dir(self, lesson_id: str, language: str, quality: str) -> Path:
        return self.work_dir / "renders" / lesson_id / language / quality

    def output_dir(self, quality: str) -> Path:
        return self.work_dir / "renders" / ("final" if quality == "final" else "preview-out")

    @property
    def cache_dir(self) -> Path:
        return self.work_dir / ".cache"
