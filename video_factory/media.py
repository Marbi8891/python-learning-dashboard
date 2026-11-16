"""Envoltorios de FFmpeg y ffprobe."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path


class MediaError(RuntimeError):
    pass


def require(tool: str) -> str:
    path = shutil.which(tool)
    if not path:
        raise MediaError(f"No encuentro «{tool}». Instala FFmpeg (macOS: brew install ffmpeg).")
    return path


def ffmpeg(*args: str, timeout: int = 3600) -> None:
    command = [require("ffmpeg"), "-hide_banner", "-loglevel", "error", "-y", *args]
    done = subprocess.run(command, capture_output=True, text=True, timeout=timeout, check=False)
    if done.returncode != 0:
        raise MediaError(f"FFmpeg falló: {done.stderr.strip()[-800:]}")


def ffmpeg_bytes(*args: str) -> bytes:
    command = [require("ffmpeg"), "-hide_banner", "-loglevel", "error", *args]
    done = subprocess.run(command, capture_output=True, timeout=300, check=False)
    if done.returncode != 0:
        raise MediaError(f"FFmpeg falló: {done.stderr.decode(errors='replace').strip()[-800:]}")
    return done.stdout


def probe(path: Path) -> dict:
    command = [
        require("ffprobe"),
        "-v",
        "error",
        "-show_format",
        "-show_streams",
        "-of",
        "json",
        str(path),
    ]
    done = subprocess.run(command, capture_output=True, text=True, timeout=120, check=False)
    if done.returncode != 0:
        raise MediaError(f"No se puede abrir {path.name}: {done.stderr.strip()[-400:]}")
    return json.loads(done.stdout)


def duration(path: Path) -> float:
    return float(probe(path)["format"]["duration"])
