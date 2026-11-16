from __future__ import annotations

import shutil

import pytest

from video_factory.config import Settings

needs_ffmpeg = pytest.mark.skipif(not shutil.which("ffmpeg"), reason="FFmpeg no está instalado")


@pytest.fixture
def settings(tmp_path) -> Settings:
    """Configuración aislada: voz muda, clips lisos y todo lo pesado en una carpeta temporal."""
    return Settings(
        work_dir=tmp_path / "work",
        tts_engine="silent",
        renderer="placeholder",
        publish_dir=tmp_path / "public",
    )
