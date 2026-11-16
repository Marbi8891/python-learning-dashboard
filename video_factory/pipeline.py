"""Orquestación: guion → audio → animación → montaje → validación, con caché y reanudación.

Cada paso comprueba la huella de sus entradas: si nada ha cambiado, no se repite. Por eso un
trabajo interrumpido se retoma lanzando otra vez la misma orden.
"""

from __future__ import annotations

import json
import logging
import shutil
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path

from video_factory import audio, render, scriptgen, subtitles, validate
from video_factory.catalog import LessonSource, build_catalog, load_sources, read_catalog
from video_factory.catalog import write_catalog as save_catalog
from video_factory.config import LANGUAGES, QUALITIES, Settings
from video_factory.models import STATUS_ORDER, Catalog, Script
from video_factory.text import digest
from video_factory.tts import create_engine

log = logging.getLogger("video_factory")

# Estimación de espacio por minuto de vídeo y por idioma (MB). Se afina con cada render real.
MB_PER_MINUTE = {"final": 9 + 9 + 6, "preview": 2 + 2 + 6}
DISK_MARGIN_MB = 1500


class PipelineError(RuntimeError):
    pass


def progress(items, description: str, total: int | None = None):
    try:
        from tqdm import tqdm
    except ImportError:
        return items
    return tqdm(items, desc=description, unit="paso", leave=False, total=total)


def retry(action, attempts: int, what: str):
    """Reintenta una operación que puede fallar por causas pasajeras (como mucho `attempts`)."""
    for attempt in range(1, attempts + 1):
        try:
            return action()
        except Exception as error:  # noqa: BLE001 - se registra y se relanza el último
            if attempt == attempts:
                raise
            log.warning("%s falló (intento %d de %d): %s", what, attempt, attempts, error)
            time.sleep(min(2**attempt, 10))


class Factory:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings.from_env()
        self._sources: dict[str, LessonSource] | None = None

    # --- catálogo --------------------------------------------------------------------------
    @property
    def sources(self) -> dict[str, LessonSource]:
        if self._sources is None:
            self._sources = load_sources()
        return self._sources

    def catalog(self) -> Catalog:
        existing = read_catalog(self.settings.catalog_path)
        return existing or self.inventory()

    def inventory(self) -> Catalog:
        catalog = build_catalog(read_catalog(self.settings.catalog_path))
        save_catalog(catalog, self.settings.catalog_path)
        return catalog

    def set_status(self, lesson_id: str, status: str, error: str = "", force: bool = False):
        """Avanza el estado de la lección (nunca retrocede salvo error o `force`)."""
        catalog = self.catalog()
        entry = catalog.get(lesson_id)
        current = entry.status if entry.status in STATUS_ORDER else "pending"
        advancing = (
            STATUS_ORDER.index(status) > STATUS_ORDER.index(current) if status != "error" else True
        )
        if force or advancing or entry.status == "error":
            entry.status, entry.error = status, error
            save_catalog(catalog, self.settings.catalog_path)

    def source(self, lesson_id: str) -> LessonSource:
        if lesson_id not in self.sources:
            raise PipelineError(f"«{lesson_id}» no es una lección del temario de PLD")
        return self.sources[lesson_id]

    # --- guion -----------------------------------------------------------------------------
    def script(self, lesson_id: str, force: bool = False) -> Script:
        """Crea el borrador del guion si no existe. Un guion editado no se toca sin `force`."""
        existing = scriptgen.read_script(self.settings.scripts_dir, lesson_id)
        if existing and (existing.origin == "edited" or not force):
            if existing.origin == "edited" and force:
                log.warning("%s: guion editado a mano, no se regenera", lesson_id)
            script = existing
        else:
            script = scriptgen.draft_script(self.source(lesson_id))
            scriptgen.write_script(self.settings.scripts_dir, script)
        if not script.problems():
            self.set_status(lesson_id, "scripted")
        return script

    def ready_script(self, lesson_id: str) -> Script:
        script = scriptgen.read_script(self.settings.scripts_dir, lesson_id)
        if script is None:
            raise PipelineError(f"{lesson_id}: no hay guion. Ejecuta: script --lesson {lesson_id}")
        problems = script.problems()
        if problems:
            listed = "\n  - ".join(problems[:8])
            raise PipelineError(f"{lesson_id}: el guion no está listo para producir:\n  - {listed}")
        return script

    # --- audio -----------------------------------------------------------------------------
    def audio(self, lesson_id: str, languages=LANGUAGES, force=False, retries=2) -> dict:
        script = self.ready_script(lesson_id)
        engine = create_engine(self.settings)
        timelines = {}
        try:
            for language in languages:
                timelines[language] = retry(
                    lambda language=language: audio.build_narration(
                        script, language, engine, self.settings, force
                    ),
                    retries,
                    f"{lesson_id}: audio {language}",
                )
                log.info(
                    "%s: narración %s lista (%.1f s)",
                    lesson_id,
                    language,
                    timelines[language]["duration"],
                )
        finally:
            engine.close()  # el modelo de voz no se queda en memoria mientras se renderiza
        if set(LANGUAGES) <= set(self.timelines(lesson_id)):
            self.set_status(lesson_id, "audio_ready")
        return timelines

    def timelines(self, lesson_id: str) -> dict[str, dict]:
        found = {}
        for language in LANGUAGES:
            path = audio.timeline_path(self.settings, lesson_id, language)
            if path.is_file():
                found[language] = json.loads(path.read_text(encoding="utf-8"))
        return found

    # --- animación y montaje ---------------------------------------------------------------
    def render(
        self, lesson_id: str, languages=LANGUAGES, quality="final", force=False, jobs=1, retries=2
    ) -> list[Path]:
        script = self.ready_script(lesson_id)
        preset = QUALITIES[quality]
        timelines = self.timelines(lesson_id)
        engine = create_engine(self.settings)
        videos = []
        for language in languages:
            timeline = timelines.get(language)
            if not timeline or timeline.get("inputs") != audio.audio_inputs(
                script, language, engine
            ):
                raise PipelineError(
                    f"{lesson_id}: falta el audio actualizado en {language}. "
                    f"Ejecuta: audio --lesson {lesson_id} --language {language}"
                )
            specs = [
                render.scene_spec(script, i, language, timeline) for i in range(len(script.scenes))
            ]
            clips = [
                render.clip_path(self.settings, script, i, language, preset, spec)
                for i, spec in enumerate(specs)
            ]
            todo = [
                (spec, clip)
                for spec, clip in zip(specs, clips, strict=True)
                if force or not clip.is_file()
            ]

            def work(item, language=language):
                spec, clip = item
                retry(
                    lambda: render.render_clip(spec, preset, clip, self.settings),
                    retries,
                    f"{lesson_id}: escena {clip.name}",
                )
                render.remove_stale_clips(clip)

            if todo:
                log.info(
                    "%s [%s]: %d de %d escenas por renderizar",
                    lesson_id,
                    language,
                    len(todo),
                    len(clips),
                )
                with ThreadPoolExecutor(max_workers=max(jobs, 1)) as pool:
                    list(progress(pool.map(work, todo), f"{lesson_id} {language}", len(todo)))
            videos.append(self._assemble(script, language, preset, timeline, clips, force))
        if all(
            render.output_paths(self.settings, lesson_id, lang, QUALITIES["final"])[
                "video"
            ].is_file()
            for lang in LANGUAGES
        ):
            self.set_status(lesson_id, "animation_ready")
            self.set_status(lesson_id, "rendered")
        return videos

    def _assemble(self, script, language, preset, timeline, clips, force) -> Path:
        paths = render.output_paths(self.settings, script.lesson_id, language, preset)
        inputs = digest(
            [
                timeline["inputs"],
                [clip.name for clip in clips],
                preset.name,
                self.settings.music_file,
                self.settings.music_volume_db,
            ]
        )
        metadata = paths["metadata"]
        if not force and paths["video"].is_file() and metadata.is_file():
            if json.loads(metadata.read_text(encoding="utf-8")).get("inputs") == inputs:
                log.info("%s [%s]: vídeo al día, no se vuelve a montar", script.lesson_id, language)
                return paths["video"]
        subtitles.write_vtt(timeline, paths["subtitles"])
        paths["transcript"].write_text(subtitles.to_transcript(timeline), encoding="utf-8")
        narration = audio.narration_path(self.settings, script.lesson_id, language)
        render.assemble(
            script,
            language,
            preset,
            timeline,
            clips,
            narration,
            paths["subtitles"],
            paths["video"],
            self.settings,
        )
        title_scene = timeline["scenes"][0]
        render.make_thumbnail(
            paths["video"], title_scene["start"] + title_scene["duration"] - 0.4, paths["thumbnail"]
        )
        metadata.write_text(
            json.dumps(
                {
                    "lesson_id": script.lesson_id,
                    "language": language,
                    "title": script.title.get(language),
                    "course": script.course.get(language),
                    "objectives": [objective.get(language) for objective in script.objectives],
                    "duration": timeline["duration"],
                    "quality": preset.name,
                    "resolution": f"{preset.width}x{preset.height}",
                    "fps": preset.fps,
                    "tts_engine": timeline["engine"],
                    "voice": timeline["voice"],
                    "renderer": self.settings.renderer,
                    "music": bool(self.settings.music_file),
                    "scenes": [
                        {"id": s["id"], "start": s["start"], "duration": s["duration"]}
                        for s in timeline["scenes"]
                    ],
                    "files": {name: path.name for name, path in paths.items()},
                    "size_bytes": paths["video"].stat().st_size,
                    "produced_at": datetime.now(UTC).isoformat(timespec="seconds"),
                    "inputs": inputs,
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        log.info(
            "%s [%s]: %s (%.1f MB)",
            script.lesson_id,
            language,
            paths["video"].name,
            paths["video"].stat().st_size / 1e6,
        )
        return paths["video"]

    # --- validación y publicación ----------------------------------------------------------
    def validate(self, lesson_id: str, quality="final", render_errors=None) -> dict:
        script = scriptgen.read_script(self.settings.scripts_dir, lesson_id)
        if script is None:
            raise PipelineError(f"{lesson_id}: no hay guion que validar")
        report = validate.validate_lesson(
            script,
            self.source(lesson_id),
            QUALITIES[quality],
            self.settings,
            self.timelines(lesson_id),
            render_errors,
        )
        validate.write_report(report, self.settings)
        return report

    def review(self, lesson_id: str) -> None:
        """Marca la lección como revisada por una persona. Exige la validación automática."""
        report = validate.read_report(self.settings, lesson_id)
        if not report or not report["passed"] or report["quality"] != "final":
            raise PipelineError(f"{lesson_id}: no ha superado la validación en calidad final")
        self.set_status(lesson_id, "reviewed")

    def publish(self, lesson_id: str) -> list[Path]:
        """Copia los archivos finales a la carpeta de publicación. Exige revisión manual."""
        entry = self.catalog().get(lesson_id)
        if entry.status not in ("reviewed", "published"):
            raise PipelineError(
                f"{lesson_id}: está «{entry.status}»; hay que revisarla antes "
                "(review --lesson … --approve)"
            )
        report = self.validate(lesson_id)
        if not report["passed"]:
            raise PipelineError(f"{lesson_id}: no supera la validación; no se publica")
        copied = []
        self.settings.publish_dir.mkdir(parents=True, exist_ok=True)
        for language in LANGUAGES:
            paths = render.output_paths(self.settings, lesson_id, language, QUALITIES["final"])
            for path in paths.values():
                copied.append(Path(shutil.copy2(path, self.settings.publish_dir / path.name)))
        self.set_status(lesson_id, "published")
        return copied

    # --- lecciones completas ---------------------------------------------------------------
    def estimate_mb(self, lesson_ids: list[str], quality: str) -> float:
        catalog = self.catalog()
        minutes = sum(catalog.get(lesson_id).estimated_minutes for lesson_id in lesson_ids)
        return minutes * MB_PER_MINUTE[quality] * len(LANGUAGES)

    def check_disk(self, lesson_ids: list[str], quality: str) -> tuple[float, float]:
        needed = self.estimate_mb(lesson_ids, quality)
        self.settings.work_dir.mkdir(parents=True, exist_ok=True)
        free = shutil.disk_usage(self.settings.work_dir).free / 1e6
        if free < needed + DISK_MARGIN_MB:
            raise PipelineError(
                f"Espacio insuficiente: hacen falta unos {needed:.0f} MB (más {DISK_MARGIN_MB} MB "
                f"de margen) y quedan {free:.0f} MB en {self.settings.work_dir}"
            )
        return needed, free

    def build(self, lesson_id: str, quality="final", force=False, jobs=1, retries=2) -> dict:
        """Todo el proceso de una lección. Devuelve el informe de validación."""
        errors: list[str] = []
        try:
            self.script(lesson_id)
            self.audio(lesson_id, force=force, retries=retries)
            self.render(lesson_id, quality=quality, force=force, jobs=jobs, retries=retries)
        except Exception as error:
            errors.append(f"{type(error).__name__}: {error}")
            self.set_status(lesson_id, "error", errors[0][:500])
            log.error("%s: %s", lesson_id, errors[0])
            raise
        report = self.validate(lesson_id, quality, errors)
        if not report["passed"] and quality == "final":
            failed = [c["check"] for c in report["general"] if not c["ok"]]
            failed += [
                f"{lang}: {c['check']}"
                for lang, checks in report["languages"].items()
                for c in checks
                if not c["ok"]
            ]
            self.set_status(lesson_id, "error", "Validación: " + "; ".join(failed)[:450])
        return report

    def plan(self, lesson_id: str, quality: str) -> list[str]:
        """Qué haría `build` con esta lección, sin hacerlo (modo dry-run)."""
        steps = []
        script = scriptgen.read_script(self.settings.scripts_dir, lesson_id)
        if script is None:
            return ["guion: se generaría el borrador (después hay que revisarlo y traducirlo)"]
        problems = script.problems()
        if problems:
            return [f"guion: incompleto ({len(problems)} pendientes); no se produciría nada"]
        steps.append("guion: listo")
        engine = create_engine(self.settings)
        timelines = self.timelines(lesson_id)
        preset = QUALITIES[quality]
        for language in LANGUAGES:
            timeline = timelines.get(language)
            fresh = timeline and timeline.get("inputs") == audio.audio_inputs(
                script, language, engine
            )
            if not fresh:
                steps.append(f"audio {language}: se sintetizaría; después, render completo")
                continue
            steps.append(f"audio {language}: al día ({timeline['duration']:.0f} s)")
            pending = sum(
                not render.clip_path(
                    self.settings,
                    script,
                    i,
                    language,
                    preset,
                    render.scene_spec(script, i, language, timeline),
                ).is_file()
                for i in range(len(script.scenes))
            )
            steps.append(f"render {language}: {pending} de {len(script.scenes)} escenas pendientes")
        return steps
