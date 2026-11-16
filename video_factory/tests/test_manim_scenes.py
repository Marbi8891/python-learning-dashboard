"""Cada componente de animación se renderiza de verdad (solo si Manim está instalado)."""

import importlib.util
import shutil

import pytest

from video_factory.config import QUALITIES, Settings
from video_factory.media import duration, probe
from video_factory.render import SCENE_CLASS, render_clip
from video_factory.validate import MIN_DETAIL, frame_detail

pytestmark = pytest.mark.skipif(
    importlib.util.find_spec("manim") is None or not shutil.which("ffmpeg"),
    reason="Manim o FFmpeg no están instalados",
)

CODE = 'nombre = "Ana"\nfor letra in nombre:\n    print(letra)'
STEPS = [{"text": "Primer punto", "line": 1}, {"text": "Segundo punto", "line": 3, "index": 1}]
DATA = {
    "title": {"kicker": "Curso de prueba"},
    "concept": {"emphasis": "x = 1"},
    "code": {"filename": "programa.py", "run_at_sentence": 0},
    "terminal": {"command": "python programa.py"},
    "variable": {"assignments": [{"name": "x", "value": "1"}, {"name": "x", "value": "2"}]},
    "datatype": {"items": [{"value": "3", "type": "int"}, {"value": '"a"', "type": "str"}]},
    "conditional": {
        "condition": "edad >= 18",
        "branches": [{"label": "True", "body": "adulto"}, {"label": "False", "body": "menor"}],
        "taken": 0,
    },
    "loop": {"variable": "letra", "items": ["A", "n", "a"], "outputs": ["A", "n", "a"]},
    "function": {"name": "sumar", "params": ["a", "b"], "args": [2, 3], "result": 5},
    "list": {"name": "notas", "items": [7, 9, 5]},
    "dictionary": {"name": "alumno", "pairs": [["nombre", '"Ana"'], ["edad", 21]]},
    "error": {"error_type": "NameError", "message": "name 'x' is not defined", "fix": "Define x"},
    "exercise": {},
    "summary": {},
}


def test_every_scene_type_has_data_for_this_test():
    assert set(DATA) == set(SCENE_CLASS)


@pytest.mark.parametrize("scene_type", sorted(SCENE_CLASS))
def test_scene_renders_with_content_and_exact_length(scene_type, tmp_path):
    spec = {
        "lesson_title": "Lección de prueba",
        "index": 0,
        "count": 3,
        "type": scene_type,
        "heading": "Título de la escena",
        "code": CODE,
        "code_language": "python",
        "output": "A\nn\na",
        "steps": STEPS,
        "data": DATA[scene_type],
        "duration": 5.0,
        "sentences": [0.4, 2.5],
    }
    clip = tmp_path / f"{scene_type}.mp4"
    preview = QUALITIES["preview"]
    render_clip(spec, preview, clip, Settings(work_dir=tmp_path))
    picture = next(s for s in probe(clip)["streams"] if s["codec_type"] == "video")
    assert (picture["width"], picture["height"]) == (preview.width, preview.height)
    assert duration(clip) == pytest.approx(5.0, abs=0.15)
    assert frame_detail(clip, 4.5) > MIN_DETAIL
