"""Interfaz de comandos: python -m video_factory <orden>."""

from __future__ import annotations

import argparse
import collections
import importlib.util
import logging
import shutil
import sys
import urllib.request

from video_factory.config import LANGUAGES, QUALITIES, Settings
from video_factory.media import MediaError
from video_factory.pipeline import DISK_MARGIN_MB, Factory, PipelineError, progress
from video_factory.render import RenderError
from video_factory.tts import TTSError

log = logging.getLogger("video_factory")


def _setup_logging(settings: Settings) -> None:
    settings.reports_dir.mkdir(parents=True, exist_ok=True)
    handlers = [
        logging.StreamHandler(sys.stderr),
        logging.FileHandler(settings.work_dir / "factory.log", encoding="utf-8"),
    ]
    handlers[0].setLevel(logging.INFO)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
        handlers=handlers,
    )


def _languages(args) -> tuple[str, ...]:
    return (args.language,) if getattr(args, "language", None) else LANGUAGES


def cmd_inventory(factory: Factory, args) -> int:
    catalog = factory.inventory()
    by_course = collections.Counter(entry.course for entry in catalog.lessons)
    minutes = sum(entry.estimated_minutes for entry in catalog.lessons)
    print(f"{len(catalog.lessons)} lecciones reales en {factory.settings.catalog_path}")
    for course, count in by_course.items():
        print(f"  {count:3d}  {course}")
    print(f"Duración estimada: {minutes:.0f} min por idioma")
    return 0


def cmd_script(factory: Factory, args) -> int:
    script = factory.script(args.lesson, force=args.force)
    problems = script.problems()
    print(f"Guion: {factory.settings.scripts_dir / (args.lesson + '.json')} ({script.origin})")
    if problems:
        print(f"Pendiente antes de producir ({len(problems)}):")
        for problem in problems[:12]:
            print(f"  - {problem}")
        return 1
    print("Completo en los dos idiomas.")
    return 0


def cmd_audio(factory: Factory, args) -> int:
    timelines = factory.audio(args.lesson, _languages(args), args.force, args.retries)
    for language, timeline in timelines.items():
        print(f"{language}: {timeline['duration']:.1f} s, {len(timeline['scenes'])} escenas")
    return 0


def cmd_render(factory: Factory, args) -> int:
    factory.check_disk([args.lesson], args.quality)
    for video in factory.render(
        args.lesson, _languages(args), args.quality, args.force, args.jobs, args.retries
    ):
        print(video)
    return 0


def _print_report(report: dict) -> None:
    checks = report["general"] + [c for cs in report["languages"].values() for c in cs]
    failed = [check for check in checks if not check["ok"]]
    print(
        f"{report['lesson_id']}: {'validación superada' if report['passed'] else 'NO superada'}"
        f" ({len(checks) - len(failed)}/{len(checks)} comprobaciones, calidad {report['quality']})"
    )
    for check in failed:
        print(f"  ✗ {check['check']}: {check['detail']}")


def cmd_build(factory: Factory, args) -> int:
    if args.dry_run:
        for step in factory.plan(args.lesson, args.quality):
            print(f"  {step}")
        print(f"Espacio estimado: {factory.estimate_mb([args.lesson], args.quality):.0f} MB")
        return 0
    factory.check_disk([args.lesson], args.quality)
    report = factory.build(args.lesson, args.quality, args.force, args.jobs, args.retries)
    _print_report(report)
    return 0 if report["passed"] else 1


def cmd_build_all(factory: Factory, args) -> int:
    catalog = factory.catalog()
    lessons = [e.id for e in catalog.lessons if not args.family or e.family == args.family]
    if not args.include_published:
        lessons = [i for i in lessons if catalog.get(i).status not in ("reviewed", "published")]
    ready, skipped = [], []
    for lesson_id in lessons:
        try:
            factory.ready_script(lesson_id)
            ready.append(lesson_id)
        except PipelineError:
            skipped.append(lesson_id)
    needed = factory.estimate_mb(ready, args.quality)
    free = shutil.disk_usage(factory.settings.work_dir.parent).free / 1e6
    print(f"{len(ready)} lecciones con guion listo; {len(skipped)} sin guion completo (se omiten)")
    print(f"Espacio estimado: {needed:.0f} MB (libres: {free:.0f} MB)")
    if args.dry_run:
        for lesson_id in ready:
            print(f"- {lesson_id}")
            for step in factory.plan(lesson_id, args.quality):
                print(f"    {step}")
        return 0
    failures = 0
    for lesson_id in progress(ready, "lecciones"):
        try:
            # El espacio se comprueba antes de cada lección: el lote para a tiempo, no a medias.
            factory.check_disk([lesson_id], args.quality)
            report = factory.build(lesson_id, args.quality, args.force, args.jobs, args.retries)
            failures += not report["passed"]
        except (PipelineError, RenderError, TTSError, MediaError) as error:
            failures += 1
            log.error("%s: se omite y se sigue con la siguiente (%s)", lesson_id, error)
            if "Espacio insuficiente" in str(error):
                break
    print(f"Terminado: {len(ready) - failures} correctas, {failures} con errores (ver report)")
    return 1 if failures else 0


def cmd_validate(factory: Factory, args) -> int:
    report = factory.validate(args.lesson, args.quality)
    _print_report(report)
    return 0 if report["passed"] else 1


def cmd_review(factory: Factory, args) -> int:
    if not args.approve:
        print(
            f"Revisa la lista de video-production/reports/{args.lesson}.validation.md y repite "
            "con --approve."
        )
        return 1
    factory.review(args.lesson)
    print(f"{args.lesson}: revisada")
    return 0


def cmd_publish(factory: Factory, args) -> int:
    for path in factory.publish(args.lesson):
        print(path)
    return 0


def cmd_report(factory: Factory, args) -> int:
    catalog = factory.catalog()
    counts = collections.Counter(entry.status for entry in catalog.lessons)
    print(f"{len(catalog.lessons)} lecciones")
    for status, count in counts.most_common():
        print(f"  {count:3d}  {status}")
    for entry in catalog.lessons:
        if entry.status == "error":
            print(f"  ✗ {entry.id}: {entry.error}")
    work = factory.settings.work_dir
    used = sum(f.stat().st_size for f in work.rglob("*") if f.is_file()) if work.is_dir() else 0
    print(f"Espacio usado en {work}: {used / 1e6:.0f} MB")
    return 0


def cmd_models(factory: Factory, args) -> int:
    from video_factory.tts.kokoro import DOWNLOADS, RELEASE

    folder = factory.settings.models_dir
    missing = {name: size for name, size in DOWNLOADS.items() if not (folder / name).is_file()}
    if not missing:
        print(f"Modelos de Kokoro presentes en {folder}")
        return 0
    total = sum(missing.values()) / 1e6
    folder.mkdir(parents=True, exist_ok=True)
    free = shutil.disk_usage(folder).free / 1e6
    print(f"Faltan {len(missing)} archivos (~{total:.0f} MB). Espacio libre: {free:.0f} MB.")
    print("En uso, el modelo ocupa unos 500 MB de RAM.")
    if not args.download:
        print("Para descargarlos: python -m video_factory models --download")
        return 1
    if free < total + DISK_MARGIN_MB:
        print("No hay espacio suficiente: no se descarga nada.")
        return 1
    for name in missing:
        print(f"Descargando {name}…")
        partial = folder / f"{name}.partial"
        urllib.request.urlretrieve(f"{RELEASE}/{name}", partial)  # noqa: S310 - URL fija https
        partial.replace(folder / name)
    print("Hecho.")
    return 0


def cmd_doctor(factory: Factory, args) -> int:
    settings = factory.settings
    problems = 0

    def line(ok: bool, text: str) -> None:
        nonlocal problems
        problems += not ok
        print(f"  {'✓' if ok else '✗'} {text}")

    line(sys.version_info >= (3, 11), f"Python {sys.version.split()[0]} (hace falta 3.11 o más)")
    for tool in ("ffmpeg", "ffprobe"):
        line(bool(shutil.which(tool)), f"{tool} en el PATH")
    for module, purpose in (
        ("pydantic", "modelos"),
        ("pygments", "resaltado de código"),
        ("manim", "animaciones"),
        ("kokoro_onnx", "voz Kokoro"),
    ):
        needed = not (module == "kokoro_onnx" and settings.tts_engine != "kokoro")
        found = importlib.util.find_spec(module) is not None
        line(found or not needed, f"paquete {module} ({purpose})" + ("" if found else " — falta"))
    if settings.tts_engine == "kokoro":
        from video_factory.tts.kokoro import DOWNLOADS

        for name in DOWNLOADS:
            line((settings.models_dir / name).is_file(), f"modelo {name} en {settings.models_dir}")
    settings.work_dir.mkdir(parents=True, exist_ok=True)
    free = shutil.disk_usage(settings.work_dir).free / 1e9
    line(free > 5, f"{free:.1f} GB libres en {settings.work_dir} (recomendado: más de 5 GB)")
    print(
        f"  · motor TTS: {settings.tts_engine} · voces: {settings.voice_es} / {settings.voice_en}"
    )
    print(f"  · renderizador: {settings.renderer}")
    print(f"  · fuentes: {settings.font_sans} / {settings.font_mono}")
    return 1 if problems else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m video_factory",
        description="PLD Video Factory: vídeos educativos bilingües a partir del temario de PLD.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    def add(name, function, help_text, lesson=False, language=False, quality=False, work=False):
        sub = commands.add_parser(name, help=help_text)
        sub.set_defaults(function=function)
        if lesson:
            sub.add_argument(
                "--lesson", required=True, help="id del catálogo, p. ej. pcap-variables"
            )
        if language:
            sub.add_argument("--language", choices=LANGUAGES, help="solo este idioma")
        if quality:
            sub.add_argument("--quality", choices=list(QUALITIES), default="final")
        if work:
            sub.add_argument("--force", action="store_true", help="rehacer aunque haya caché")
            sub.add_argument("--jobs", type=int, default=1, help="escenas renderizadas a la vez")
            sub.add_argument("--retries", type=int, default=2, help="intentos por paso")
        return sub

    add("inventory", cmd_inventory, "regenera video-production/catalog.json desde el temario")
    add("script", cmd_script, "crea o comprueba el guion de una lección", lesson=True).add_argument(
        "--force", action="store_true", help="regenerar el borrador (no pisa guiones editados)"
    )
    add("audio", cmd_audio, "sintetiza la narración", lesson=True, language=True, work=True)
    add(
        "render",
        cmd_render,
        "renderiza y monta el vídeo",
        lesson=True,
        language=True,
        quality=True,
        work=True,
    )
    add(
        "build",
        cmd_build,
        "guion + audio + render + validación",
        lesson=True,
        quality=True,
        work=True,
    ).add_argument("--dry-run", action="store_true", help="solo muestra el plan")
    everything = add(
        "build-all",
        cmd_build_all,
        "produce todas las lecciones con guion listo",
        quality=True,
        work=True,
    )
    everything.add_argument("--dry-run", action="store_true", help="solo muestra el plan")
    everything.add_argument("--family", choices=("learn", "pcap", "daw"))
    everything.add_argument("--include-published", action="store_true")
    add("validate", cmd_validate, "control de calidad e informe", lesson=True, quality=True)
    add("review", cmd_review, "marca la revisión manual", lesson=True).add_argument(
        "--approve", action="store_true"
    )
    add("publish", cmd_publish, "copia los archivos finales a la carpeta pública", lesson=True)
    add("report", cmd_report, "estado de producción de todo el catálogo")
    add("models", cmd_models, "comprueba o descarga los modelos de voz").add_argument(
        "--download", action="store_true"
    )
    add("doctor", cmd_doctor, "comprueba que el entorno está listo")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    settings = Settings.from_env()
    settings.work_dir.mkdir(parents=True, exist_ok=True)
    _setup_logging(settings)
    try:
        return args.function(Factory(settings), args)
    except (PipelineError, RenderError, TTSError, MediaError, KeyError) as error:
        log.error("%s", error.args[0] if isinstance(error, KeyError) else error)
        return 2
