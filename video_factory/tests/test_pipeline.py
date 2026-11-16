"""El pipeline completo con voz muda y clips lisos: no necesita Manim ni modelos de voz."""

import json
import wave

import pytest

from video_factory import audio, render
from video_factory.config import QUALITIES
from video_factory.media import probe
from video_factory.pipeline import Factory, PipelineError
from video_factory.scriptgen import read_script
from video_factory.tts import TTSError, create_engine

from .conftest import needs_ffmpeg

PILOT = "pcap-variables"


@pytest.fixture
def factory(settings, tmp_path, monkeypatch):
    """Fábrica con catálogo e informes en carpetas temporales (no toca los del repositorio)."""
    cls = type(settings)
    monkeypatch.setattr(cls, "catalog_path", property(lambda self: tmp_path / "catalog.json"))
    monkeypatch.setattr(cls, "reports_dir", property(lambda self: tmp_path / "reports"))
    return Factory(settings)


@needs_ffmpeg
def test_scene_length_follows_the_narration(factory):
    timelines = factory.audio(PILOT)
    script = read_script(factory.settings.scripts_dir, PILOT)
    for language, timeline in timelines.items():
        assert [scene["id"] for scene in timeline["scenes"]] == [s.id for s in script.scenes]
        cursor = 0.0
        for scene in timeline["scenes"]:
            assert scene["start"] == pytest.approx(cursor, abs=0.002)
            assert scene["duration"] * 30 == pytest.approx(round(scene["duration"] * 30), abs=0.01)
            last = scene["sentences"][-1]["end"]
            assert last <= scene["start"] + scene["duration"] - audio.TAIL + 0.05
            cursor += scene["duration"]
        path = audio.narration_path(factory.settings, PILOT, language)
        with wave.open(str(path)) as wav:
            assert wav.getnframes() / wav.getframerate() == pytest.approx(
                timeline["duration"], abs=0.01
            )
    assert factory.catalog().get(PILOT).status == "audio_ready"


@needs_ffmpeg
def test_audio_is_not_synthesized_again_if_nothing_changed(factory, monkeypatch):
    factory.audio(PILOT, languages=("es",))
    engine = create_engine(factory.settings)

    def fail(*args, **kwargs):
        raise AssertionError("no debería volver a sintetizar")

    monkeypatch.setattr(type(engine), "synthesize", fail)
    factory.audio(PILOT, languages=("es",))


@needs_ffmpeg
def test_full_build_produces_both_videos_and_a_report(factory):
    report = factory.build(PILOT, quality="preview")
    preview = QUALITIES["preview"]
    for language in ("es", "en"):
        paths = render.output_paths(factory.settings, PILOT, language, preview)
        assert all(path.is_file() for path in paths.values()), language
        codecs = {s["codec_type"]: s["codec_name"] for s in probe(paths["video"])["streams"]}
        assert codecs == {"video": "h264", "audio": "aac", "subtitle": "mov_text"}
        metadata = json.loads(paths["metadata"].read_text(encoding="utf-8"))
        assert metadata["language"] == language and metadata["duration"] > 60
        by_name = {check["check"]: check for check in report["languages"][language]}
        assert by_name["La duración coincide con la narración"]["ok"]
        assert by_name["Los subtítulos son válidos"]["ok"]
        # Los clips de prueba son lisos: el control de calidad tiene que darse cuenta.
        assert not by_name["No hay escenas vacías"]["ok"]
    assert not report["passed"]
    assert (factory.settings.reports_dir / f"{PILOT}.validation.md").is_file()


@needs_ffmpeg
def test_resuming_reuses_finished_clips(factory, monkeypatch):
    factory.audio(PILOT, languages=("es",))
    calls, recovered = [], []
    original = render.render_clip

    def flaky(spec, quality, out_path, settings):
        calls.append(spec["index"])
        if len(calls) == 4 and not recovered:
            raise render.RenderError("corte simulado")
        original(spec, quality, out_path, settings)

    monkeypatch.setattr(render, "render_clip", flaky)
    with pytest.raises(render.RenderError):
        factory.render(PILOT, languages=("es",), quality="preview", retries=1)
    finished = set(calls) - {3}
    calls.clear()
    recovered.append(True)
    factory.render(PILOT, languages=("es",), quality="preview", retries=1)
    assert 3 in calls and not finished & set(calls)  # solo se rehace lo que no terminó
    assert set(calls) | finished == set(range(10))
    calls.clear()
    factory.render(PILOT, languages=("es",), quality="preview")
    assert calls == []


def test_render_refuses_to_run_without_current_audio(factory):
    with pytest.raises(PipelineError, match="falta el audio"):
        factory.render(PILOT, quality="preview")


def test_a_lesson_without_finished_script_is_not_produced(factory):
    with pytest.raises(PipelineError, match="no hay guion"):
        factory.audio("pcap-tipos")
    with pytest.raises(PipelineError, match="no es una lección"):
        factory.script("py-001")


def test_nothing_is_published_without_review(factory):
    factory.inventory()
    with pytest.raises(PipelineError, match="hay que revisarla"):
        factory.publish(PILOT)
    with pytest.raises(PipelineError, match="no ha superado la validación"):
        factory.review(PILOT)
    assert factory.catalog().get(PILOT).status == "pending"


def test_status_only_moves_forward(factory):
    factory.inventory()
    factory.set_status(PILOT, "rendered")
    factory.set_status(PILOT, "scripted")
    assert factory.catalog().get(PILOT).status == "rendered"
    factory.set_status(PILOT, "error", "fallo")
    assert factory.catalog().get(PILOT).error == "fallo"


def test_low_disk_space_stops_before_starting(factory, monkeypatch):
    import shutil

    monkeypatch.setattr(shutil, "disk_usage", lambda path: shutil._ntuple_diskusage(10, 9, 10**8))
    with pytest.raises(PipelineError, match="Espacio insuficiente"):
        factory.check_disk([PILOT], "final")


def test_unknown_engine_and_missing_models_are_explained(settings):
    settings.tts_engine = "robot"
    with pytest.raises(TTSError, match="desconocido"):
        create_engine(settings)
    settings.tts_engine, settings.models_dir = "kokoro", settings.work_dir / "nada"
    with pytest.raises(TTSError, match="models --download"):
        create_engine(settings).synthesize("Hola", "es", settings.work_dir / "x.wav")


def test_pronunciation_changes_the_voice_text_only():
    rules = audio.load_pronunciation("es")
    assert audio.spoken_text("Sigue la guía PEP 8 con precio_total.", rules) == (
        "Sigue la guía pep ocho con precio total."
    )


def test_scene_spec_is_localized_and_timed(factory):
    script = read_script(factory.settings.scripts_dir, PILOT)
    scenes = [
        {"id": s.id, "start": 10.0 * i, "duration": 10.0,
         "sentences": [{"text": "x", "start": 10.0 * i + 0.5, "end": 10.0 * i + 2}]}
        for i, s in enumerate(script.scenes)
    ]  # fmt: skip
    spec = render.scene_spec(script, 1, "en", {"scenes": scenes})
    assert spec["heading"] == "What is a variable?"
    assert spec["sentences"] == [0.5] and spec["duration"] == 10.0
    assert spec["data"]["assignments"][0]["name"] == "nombre"
    scenes[1]["id"] = "otra"
    with pytest.raises(render.RenderError):
        render.scene_spec(script, 1, "en", {"scenes": scenes})
