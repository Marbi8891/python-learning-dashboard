"""Renderizado: un clip por escena (con caché) y montaje final con FFmpeg."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from video_factory.config import PACKAGE, QUALITIES, REPO, Quality, Settings
from video_factory.media import MediaError, ffmpeg
from video_factory.models import Script, localize
from video_factory.text import digest

SCENE_CLASS = {
    "title": "TitleScene",
    "concept": "ConceptScene",
    "code": "CodeScene",
    "terminal": "TerminalScene",
    "variable": "VariableScene",
    "datatype": "DataTypeScene",
    "conditional": "ConditionalScene",
    "loop": "LoopScene",
    "function": "FunctionScene",
    "list": "ListScene",
    "dictionary": "DictionaryScene",
    "error": "ErrorScene",
    "exercise": "ExerciseScene",
    "summary": "SummaryScene",
}
SCENES_FILE = PACKAGE / "animation" / "scenes.py"
SUBTITLE_LANGUAGE = {"es": "spa", "en": "eng"}


class RenderError(RuntimeError):
    pass


def animation_version() -> str:
    """Huella del código de animación: si cambia, los clips en caché dejan de valer."""
    files = [SCENES_FILE, PACKAGE / "animation" / "theme.py"]
    return digest([path.read_text(encoding="utf-8") for path in files])[:12]


def scene_spec(script: Script, index: int, language: str, timeline: dict) -> dict:
    """Lo que necesita Manim para dibujar la escena, ya en el idioma del vídeo."""
    scene = script.scenes[index]
    timing = timeline["scenes"][index]
    if timing["id"] != scene.id:
        raise RenderError("El audio no corresponde a este guion: vuelve a generar el audio")
    return {
        "lesson_title": script.title.get(language),
        "index": index,
        "count": len(script.scenes),
        "type": scene.type,
        "heading": scene.heading.get(language),
        "code": scene.code,
        "code_language": scene.code_language,
        "output": scene.output,
        "steps": [localize(step.model_dump(exclude_none=True), language) for step in scene.steps],
        "data": localize(scene.data, language),
        "duration": timing["duration"],
        "sentences": [round(s["start"] - timing["start"], 3) for s in timing["sentences"]],
    }


def clip_path(
    settings: Settings, script: Script, index: int, language: str, quality: Quality, spec: dict
) -> Path:
    key = digest(
        [
            spec,
            quality.name,
            settings.renderer,
            animation_version(),
            settings.font_sans,
            settings.font_mono,
        ]
    )[:10]
    folder = settings.clips_dir(script.lesson_id, language, quality.name)
    return folder / f"{index + 1:02d}-{script.scenes[index].id}-{key}.mp4"


def _render_placeholder(spec: dict, quality: Quality, out_path: Path) -> None:
    """Clip liso de la duración exacta. Solo para probar el pipeline sin Manim."""
    source = f"color=c=0x101318:s={quality.width}x{quality.height}:r={quality.fps}"
    ffmpeg(
        "-f",
        "lavfi",
        "-i",
        source,
        "-t",
        f"{spec['duration']:.4f}",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        str(out_path),
    )


def _render_manim(spec: dict, quality: Quality, out_path: Path, settings: Settings) -> None:
    with tempfile.TemporaryDirectory(prefix="pld-manim-") as temporary:
        spec_file = Path(temporary) / "scene.json"
        spec_file.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
        environment = {
            **os.environ,
            "PLD_SCENE_SPEC": str(spec_file),
            "PLD_FONT_SANS": settings.font_sans,
            "PLD_FONT_MONO": settings.font_mono,
            "PYTHONPATH": os.pathsep.join(
                filter(None, [str(REPO), os.environ.get("PYTHONPATH", "")])
            ),
        }
        command = [
            sys.executable, "-m", "manim", "render",
            "--disable_caching", "--progress_bar", "none", "-v", "WARNING",
            "--media_dir", temporary,
            "--resolution", f"{quality.width},{quality.height}",
            "--fps", str(quality.fps),
            "--format", "mp4",
            "-o", "clip",
            str(SCENES_FILE), SCENE_CLASS[spec["type"]],
        ]  # fmt: skip
        done = subprocess.run(
            command, capture_output=True, text=True, env=environment, timeout=1800, check=False
        )
        produced = sorted(Path(temporary).rglob("clip.mp4"))
        if done.returncode != 0 or not produced:
            detail = (done.stderr or done.stdout).strip()[-1500:]
            raise RenderError(f"Manim no pudo renderizar la escena «{spec['type']}»:\n{detail}")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(produced[0]), out_path)


def render_clip(spec: dict, quality: Quality, out_path: Path, settings: Settings) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = out_path.with_name(f".{out_path.name}.partial.mp4")
    if settings.renderer == "placeholder":
        _render_placeholder(spec, quality, temporary)
    elif settings.renderer == "manim":
        _render_manim(spec, quality, temporary, settings)
    else:
        raise RenderError(f"Renderizador desconocido: «{settings.renderer}»")
    temporary.replace(out_path)  # un clip a medias nunca se confunde con uno terminado


def remove_stale_clips(current: Path) -> None:
    """Borra versiones anteriores del mismo clip (misma escena, otra huella)."""
    prefix = current.name.rsplit("-", 1)[0]
    for other in current.parent.glob(f"{prefix}-*.mp4"):
        if other != current:
            other.unlink()


def output_paths(settings: Settings, lesson_id: str, language: str, quality: Quality) -> dict:
    folder = settings.output_dir(quality.name)
    stem = f"{lesson_id}-{language}"
    return {
        "video": folder / f"{stem}.mp4",
        "subtitles": folder / f"{stem}.vtt",
        "transcript": folder / f"{stem}.txt",
        "thumbnail": folder / f"{stem}.jpg",
        "metadata": folder / f"{stem}.json",
    }


def assemble(
    script: Script,
    language: str,
    quality: Quality,
    timeline: dict,
    clips: list[Path],
    narration: Path,
    subtitles: Path,
    out_path: Path,
    settings: Settings,
) -> None:
    """Une los clips, la narración y los subtítulos en un MP4 (H.264 + AAC) para web."""
    arguments: list[str] = []
    for clip in clips:
        arguments += ["-i", str(clip)]
    audio_input = len(clips)
    arguments += ["-i", str(narration)]
    music = settings.music_file
    if music:
        if not Path(music).is_file():
            raise MediaError(f"No existe el archivo de música: {music}")
        arguments += ["-stream_loop", "-1", "-i", music]
    subtitle_input = audio_input + (2 if music else 1)
    arguments += ["-i", str(subtitles)]

    filters = []
    for index, timing in enumerate(timeline["scenes"]):
        # Cada clip se ajusta a la duración exacta de su narración: el último fotograma se
        # mantiene si la animación acabó antes y se recorta si se pasó.
        filters.append(
            f"[{index}:v]fps={quality.fps},scale={quality.width}:{quality.height}:flags=lanczos,"
            f"setsar=1,tpad=stop_mode=clone:stop_duration=4,trim=duration={timing['duration']},"
            f"setpts=PTS-STARTPTS[v{index}]"
        )
    joined = "".join(f"[v{index}]" for index in range(len(clips)))
    filters.append(f"{joined}concat=n={len(clips)}:v=1:a=0[video]")
    if music:
        filters.append(f"[{audio_input + 1}:a]volume={settings.music_volume_db}dB[music]")
        filters.append(f"[{audio_input}:a][music]amix=inputs=2:duration=first:normalize=0[audio]")
    else:
        filters.append(f"[{audio_input}:a]anull[audio]")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = out_path.with_name(f".{out_path.stem}.partial.mp4")
    ffmpeg(
        *arguments,
        "-filter_complex", ";".join(filters),
        "-map", "[video]", "-map", "[audio]", "-map", f"{subtitle_input}:0",
        "-c:v", "libx264", "-preset", quality.preset, "-crf", str(quality.crf),
        "-pix_fmt", "yuv420p", "-r", str(quality.fps),
        "-c:a", "aac", "-b:a", "160k", "-ar", "48000",
        "-c:s", "mov_text",
        "-metadata", f"title={script.title.get(language)}",
        "-metadata:s:a:0", f"language={SUBTITLE_LANGUAGE[language]}",
        "-metadata:s:s:0", f"language={SUBTITLE_LANGUAGE[language]}",
        "-t", f"{timeline['duration']:.3f}",
        "-movflags", "+faststart",
        str(temporary),
    )  # fmt: skip
    temporary.replace(out_path)


def make_thumbnail(video: Path, moment: float, out_path: Path) -> None:
    ffmpeg(
        "-ss",
        f"{moment:.2f}",
        "-i",
        str(video),
        "-frames:v",
        "1",
        "-vf",
        "scale=1280:720:flags=lanczos",
        "-q:v",
        "3",
        str(out_path),
    )


def quality_named(name: str) -> Quality:
    return QUALITIES[name]
