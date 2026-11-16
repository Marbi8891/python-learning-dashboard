"""Control de calidad automático de un vídeo terminado, con informe por lección."""

from __future__ import annotations

import json
import statistics
from datetime import UTC, datetime
from pathlib import Path

from video_factory.catalog import LessonSource
from video_factory.config import LANGUAGES, Quality, Settings
from video_factory.media import MediaError, duration, ffmpeg_bytes, probe
from video_factory.models import Script
from video_factory.render import output_paths
from video_factory.subtitles import validate_vtt

MAX_DRIFT = 0.5  # segundos de diferencia admitidos entre el vídeo y su narración
MIN_DETAIL = 4.0  # desviación típica de brillo por debajo de la cual un fotograma está «vacío»
MANUAL_CHECKLIST = [
    "Sincronización: lo que se dice coincide con lo que aparece en pantalla en cada escena.",
    "Pronunciación: los términos técnicos (print, f-string, PEP 8…) se entienden en ES y EN.",
    "Ritmo: no hay cortes bruscos ni silencios largos entre escenas.",
    "Legibilidad: el código y los textos se leen bien a 1080p y en una ventana pequeña.",
    "Subtítulos: aparecen a tiempo, sin faltas y con frases bien partidas.",
    "Exactitud didáctica: la explicación coincide con la teoría de la lección y no añade errores.",
    "Inglés: suena natural y transmite lo mismo que el español.",
]


def _check(name: str, ok: bool, detail: str = "") -> dict:
    return {"check": name, "ok": bool(ok), "detail": detail}


def code_problems(script: Script, source: LessonSource) -> list[str]:
    """Líneas de código del guion que no están en la lección (el vídeo no puede inventarlas)."""
    known = {line.strip() for line in source.code_corpus().splitlines()}
    corpus = source.code_corpus()
    problems = []
    for scene in script.scenes:
        shown = scene.code.splitlines()
        shown += [item.get("code", "") for item in scene.data.get("assignments", [])]
        for line in shown:
            line = line.strip()
            if line and line not in known and line not in corpus:
                problems.append(f"{scene.id}: «{line}» no aparece en la lección")
    return problems


def frame_detail(video: Path, moment: float) -> float:
    """Cuánta variación de brillo hay en un fotograma (≈0 = pantalla lisa, sin contenido)."""
    raw = ffmpeg_bytes("-ss", f"{moment:.2f}", "-i", str(video), "-frames:v", "1",
                       "-vf", "scale=96:54,format=gray", "-f", "rawvideo", "-")  # fmt: skip
    return statistics.pstdev(raw) if len(raw) > 1 else 0.0


def validate_language(
    script: Script, language: str, quality: Quality, settings: Settings, timeline: dict | None
) -> list[dict]:
    paths = output_paths(settings, script.lesson_id, language, quality)
    video = paths["video"]
    checks = [_check("El vídeo existe", video.is_file(), video.name)]
    if not video.is_file():
        return checks
    try:
        info = probe(video)
    except MediaError as error:
        return checks + [_check("El archivo puede abrirse", False, str(error))]
    checks.append(_check("El archivo puede abrirse", True))
    streams = {stream["codec_type"]: stream for stream in reversed(info["streams"])}
    picture, sound = streams.get("video"), streams.get("audio")
    if picture:
        size = f"{picture['width']}x{picture['height']}"
        wanted = f"{quality.width}x{quality.height}"
        checks.append(
            _check(
                "La resolución es correcta",
                size == wanted,
                f"{size} (≠ {wanted})" if size != wanted else size,
            )
        )
        numerator, _, denominator = picture.get("avg_frame_rate", "0/1").partition("/")
        fps = float(numerator) / float(denominator or 1) if float(denominator or 1) else 0.0
        checks.append(_check("El FPS es correcto", abs(fps - quality.fps) < 0.01, f"{fps:.2f}"))
        codec = f"{picture['codec_name']} {picture.get('pix_fmt')}"
        checks.append(_check("Vídeo en H.264 (yuv420p)", codec == "h264 yuv420p", codec))
    else:
        checks.append(_check("Hay pista de vídeo", False))
    checks.append(
        _check(
            "El audio existe (AAC)",
            bool(sound) and sound["codec_name"] == "aac",
            sound["codec_name"] if sound else "sin audio",
        )
    )

    length = float(info["format"]["duration"])
    if timeline:
        drift = abs(length - timeline["duration"])
        checks.append(
            _check(
                "La duración coincide con la narración",
                drift <= MAX_DRIFT,
                f"vídeo {length:.2f} s, narración {timeline['duration']:.2f} s",
            )
        )
        empty = []
        for scene in timeline["scenes"]:
            moment = min(scene["start"] + scene["duration"] * 0.8, length - 0.2)
            if frame_detail(video, moment) < MIN_DETAIL:
                empty.append(scene["id"])
        checks.append(_check("No hay escenas vacías", not empty, ", ".join(empty)))
    else:
        checks.append(_check("Existe la línea de tiempo del audio", False))

    subtitles = paths["subtitles"]
    if subtitles.is_file():
        problems = validate_vtt(subtitles.read_text(encoding="utf-8"), length)
        checks.append(_check("Los subtítulos son válidos", not problems, "; ".join(problems[:5])))
    else:
        checks.append(_check("Los subtítulos existen", False, subtitles.name))
    for name in ("transcript", "thumbnail"):
        checks.append(_check(f"Existe {paths[name].suffix}", paths[name].is_file()))
    return checks


def validate_lesson(
    script: Script,
    source: LessonSource,
    quality: Quality,
    settings: Settings,
    timelines: dict[str, dict | None],
    render_errors: list[str] | None = None,
) -> dict:
    general = []
    problems = script.problems()
    general.append(
        _check("El guion está completo en los dos idiomas", not problems, "; ".join(problems[:5]))
    )
    wrong_code = code_problems(script, source)
    general.append(
        _check(
            "El código mostrado coincide con el de la lección",
            not wrong_code,
            "; ".join(wrong_code[:5]),
        )
    )
    current = script.source_hash == source.fingerprint()
    general.append(
        _check(
            "El guion corresponde a la versión actual de la lección",
            current,
            "" if current else "La lección cambió después de escribir el guion",
        )
    )
    general.append(
        _check("No hay errores de renderizado", not render_errors, "; ".join(render_errors or []))
    )
    languages = {
        language: validate_language(script, language, quality, settings, timelines.get(language))
        for language in LANGUAGES
    }
    everything = general + [check for checks in languages.values() for check in checks]
    return {
        "lesson_id": script.lesson_id,
        "quality": quality.name,
        "checked_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "passed": all(check["ok"] for check in everything),
        "general": general,
        "languages": languages,
        "manual_review": MANUAL_CHECKLIST,
    }


def report_paths(settings: Settings, lesson_id: str) -> tuple[Path, Path]:
    base = settings.reports_dir / lesson_id
    return base.with_suffix(".validation.json"), base.with_suffix(".validation.md")


def write_report(report: dict, settings: Settings) -> Path:
    json_path, markdown_path = report_paths(settings, report["lesson_id"])
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def rows(checks):
        return [
            f"- {'✅' if c['ok'] else '❌'} {c['check']}"
            + (f" — {c['detail']}" if c["detail"] else "")
            for c in checks
        ]

    lines = [
        f"# Validación de {report['lesson_id']}",
        "",
        f"- Calidad: `{report['quality']}`",
        f"- Fecha: {report['checked_at']}",
        f"- Resultado automático: **{'SUPERADA' if report['passed'] else 'NO SUPERADA'}**",
        "",
        "## Comprobaciones generales",
        *rows(report["general"]),
    ]
    for language, checks in report["languages"].items():
        lines += ["", f"## Vídeo en {language}", *rows(checks)]
    lines += ["", "## Revisión manual (antes de `review --approve`)"]
    lines += [f"- [ ] {item}" for item in report["manual_review"]]
    markdown_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return markdown_path


def read_report(settings: Settings, lesson_id: str) -> dict | None:
    json_path, _ = report_paths(settings, lesson_id)
    return json.loads(json_path.read_text(encoding="utf-8")) if json_path.is_file() else None


__all__ = ["duration", "validate_lesson", "write_report", "read_report", "code_problems"]
