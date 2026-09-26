"""Calidad del contenido: se ejecuta el mismo motor que usa la consola del navegador.

- Todos los ejemplos ejecutables en el navegador funcionan sin errores.
- Ninguna plantilla supera los tests (si no, el ejercicio no comprobaría nada).
- Los tests de cada ejercicio son Python válido.

Las soluciones de referencia NO están en el repositorio para no dar las respuestas
a quien estudia (ver ADR-0004).
"""

import json
import sys

import pytest

from app.config import DEFAULT_LESSONS_FILE

sys.path.insert(0, str(DEFAULT_LESSONS_FILE.parents[1] / "py"))
import runner  # noqa: E402  (frontend/py/runner.py)

LESSONS = [
    lesson
    for module in json.loads(DEFAULT_LESSONS_FILE.read_text(encoding="utf-8"))["modules"]
    for lesson in module["lessons"]
]
IDS = [lesson["slug"] for lesson in LESSONS]
# Los ejemplos de Flask y pytest usan paquetes externos: se ejecutan en PyCharm, no en el navegador
BROWSER_EXAMPLES = [lesson for lesson in LESSONS if lesson["example_in_browser"]]


def test_only_external_package_examples_are_browser_excluded():
    excluded = {lesson["slug"] for lesson in LESSONS if not lesson["example_in_browser"]}
    assert excluded == {"pytest", "flask"}


@pytest.mark.parametrize(
    "lesson", BROWSER_EXAMPLES, ids=[lesson["slug"] for lesson in BROWSER_EXAMPLES]
)
def test_example_runs_in_browser_engine(lesson, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = runner.run_code(lesson["example_code"], lesson["example_stdin"])
    assert result["error"] is None, result["error"]
    assert result["output"], "El ejemplo debería mostrar algo"


@pytest.mark.parametrize("lesson", LESSONS, ids=IDS)
def test_starter_does_not_pass(lesson, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert not runner.check_exercise(lesson["starter"], lesson["checks"])["passed"]


@pytest.mark.parametrize("lesson", LESSONS, ids=IDS)
def test_checks_are_valid_python(lesson):
    for case in lesson["checks"]:
        compile(case["test"], "<tests>", "exec")


def test_runner_reports_errors_with_student_line():
    result = runner.run_code("def f(x):\n    return 1 / x\n\nf(0)\n")
    assert "line 2, in f" in result["error"] and "return 1 / x" in result["error"]
    assert "ZeroDivisionError" in result["error"]


def test_runner_gives_stdin_and_detects_missing_input():
    assert runner.run_code("print(input('?') * 2)", "ab")["output"] == "?abab\n"
    assert "EOFError" in runner.run_code("input()")["error"]


def test_check_skips_main_block():
    code = 'x = 1\nif __name__ == "__main__":\n    x = 2\n'
    assert runner.check_exercise(code, [{"test": "assert x == 1"}])["passed"]


# ---------- Mini-quiz y retos ----------


@pytest.mark.parametrize("lesson", LESSONS, ids=IDS)
def test_quiz_is_well_formed(lesson):
    assert len(lesson["quiz"]) == 3, "Cada lección tiene 3 preguntas"
    for question in lesson["quiz"]:
        assert question["q"] and question["explain"], "Pregunta y explicación obligatorias"
        assert len(question["options"]) == 4 and len(set(question["options"])) == 4
        assert 0 <= question["answer"] < 4
        if "code" in question:
            compile(question["code"], "<quiz>", "exec")


@pytest.mark.parametrize("lesson", LESSONS, ids=IDS)
def test_challenge_starter_does_not_pass(lesson, tmp_path, monkeypatch):
    challenge = lesson["challenge"]
    assert challenge["title"] and challenge["hint"] and 1 <= challenge["stars"] <= 3
    for case in challenge["checks"]:
        compile(case["test"], "<tests>", "exec")
    monkeypatch.chdir(tmp_path)
    assert not runner.check_exercise(challenge["starter"], challenge["checks"])["passed"]
