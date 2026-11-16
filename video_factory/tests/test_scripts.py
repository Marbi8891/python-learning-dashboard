"""Guiones: el borrador sale del temario y el guion piloto está listo para producir."""

import pytest
from pydantic import ValidationError

from video_factory.catalog import load_sources
from video_factory.config import PRODUCTION
from video_factory.models import Bilingual, Scene, Script, Step, localize
from video_factory.render import SCENE_CLASS
from video_factory.scriptgen import draft_script, read_script, run_python_example
from video_factory.text import split_sentences
from video_factory.validate import code_problems

PILOT = "pcap-variables"


@pytest.fixture(scope="module")
def sources():
    return load_sources()


def test_a_draft_can_be_generated_for_every_lesson(sources):
    for source in sources.values():
        script = draft_script(source, run_examples=False)
        sections = {scene.section for scene in script.scenes}
        assert {"intro", "explanation", "example", "result", "exercise", "summary"} <= sections
        assert all(scene.type in SCENE_CLASS for scene in script.scenes)
        assert not code_problems(script, source), source.id


def test_a_draft_is_never_ready_without_english(sources):
    problems = draft_script(sources[PILOT], run_examples=False).problems()
    assert any("sin narración en en" in problem for problem in problems)


def test_draft_shows_the_real_output_of_the_example(sources):
    script = draft_script(sources[PILOT])
    terminal = next(scene for scene in script.scenes if scene.type == "terminal")
    assert terminal.output.splitlines()[0] == "Carlos tiene 30 años"


def test_example_that_fails_gives_no_output():
    assert run_python_example("raise SystemExit(3)") is None
    assert run_python_example("while True: pass", timeout=1) is None


def test_pilot_script_is_complete_and_faithful_to_the_lesson(sources):
    script = read_script(PRODUCTION / "scripts", PILOT)
    assert script.origin == "edited"
    assert script.problems() == []
    assert code_problems(script, sources[PILOT]) == []
    assert script.source_hash == sources[PILOT].fingerprint()


def test_pilot_has_the_same_sentences_in_both_languages():
    """Los pasos se sincronizan con el número de frase: tiene que coincidir en ES y EN."""
    script = read_script(PRODUCTION / "scripts", PILOT)
    for scene in script.scenes:
        spanish = split_sentences(scene.narration.es)
        english = split_sentences(scene.narration.en)
        assert len(spanish) == len(english), scene.id
        for step in scene.steps:
            assert step.sentence is None or step.sentence < len(spanish), scene.id


def test_code_not_in_the_lesson_is_reported(sources):
    script = read_script(PRODUCTION / "scripts", PILOT)
    script.scenes[3].code = 'print("Hello, World!")'
    assert "Hello, World!" in code_problems(script, sources[PILOT])[0]


def test_models_reject_bad_data():
    narration = Bilingual(es="Hola.", en="Hi.")
    with pytest.raises(ValidationError):
        Scene(id="Mal Id", type="title", section="intro", narration=narration)
    with pytest.raises(ValidationError):
        Scene(id="s1", type="hologram", section="intro", narration=narration)
    with pytest.raises(ValidationError):
        Step(at=0.8, until=0.2)
    scene = Scene(id="s1", type="title", section="intro", narration=narration)
    with pytest.raises(ValidationError):
        Script(lesson_id="x", title=narration, scenes=[scene, scene])


def test_localize_picks_the_language_at_any_depth():
    data = {"kicker": {"es": "Curso", "en": "Course"}, "items": [{"note": {"es": "a", "en": "b"}}]}
    assert localize(data, "en") == {"kicker": "Course", "items": [{"note": "b"}]}
