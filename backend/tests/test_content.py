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


@pytest.mark.parametrize(
    ("code", "stdin", "title", "line"),
    [
        ("if True:\nprint(1)", "", "Problema de sangría", 2),
        ("print('hola'", "", "Falta cerrar algo", 1),
        ("x = 1\nif x > 0\n    print(x)", "", "Faltan los dos puntos", 2),
        ("x = 1\nif x = 1:\n    pass", "", "¿Querías comparar?", 2),
        ("print('a' 'b' 1)", "", "¿Falta una coma?", 1),
        ("x = 1\ndef f():\n    x += 1\nf()", "", "Variable usada antes de darle valor", 3),
        ("x = 1\nprint(nombre)", "", "`nombre` no existe (todavía)", 2),
        ("edad = 30\nprint('Edad: ' + edad)", "", "Mezclas tipos que no se combinan", 2),
        ("print = 3\nprint(1)", "", "Eso no es una función", 2),
        ("def f(a, b):\n    pass\nf(1)", "", "Faltan datos al llamar a la función", 3),
        ("def f(a):\n    pass\nf(1, 2)", "", "Sobran datos al llamar a la función", 3),
        ("len(5)", "", "Operación no válida para ese tipo de dato", 1),
        ("edad = int(input())", "hola", "Ese texto no es un número", 1),
        ("import math\nmath.sqrt(-1)", "", "Valor no válido", 2),
        ("print(1 / 0)", "", "División entre cero", 1),
        ("[1, 2][5]", "", "Esa posición no existe", 1),
        ("{'a': 1}['b']", "", "Esa clave no está en el diccionario", 1),
        ("'hola'.append('!')", "", "Ese valor no tiene ese método", 1),
        ("input()", "", "Faltan datos en «Entrada»", 1),
        ("import modulo_que_no_existe_pld", "", "Paquete no disponible aquí", 1),
        ("def f():\n    return f()\nf()", "", "Una función se llama a sí misma sin fin", 2),
        ("open('no-existe.txt')", "", "No se encuentra el archivo", 1),
    ],
)
def test_errors_are_explained_in_spanish(code, stdin, title, line, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    hint = runner.run_code(code, stdin)["hint"]
    assert hint["title"] == title
    assert hint["text"]
    assert hint["line"] == line


def test_unexplained_errors_have_no_hint():
    assert runner.run_code("raise RuntimeError('x')")["hint"] is None
    assert runner.run_code("print(1)")["hint"] is None


def test_check_exercise_explains_errors():
    result = runner.check_exercise("print(x)", [{"test": "assert True"}])
    assert not result["passed"]
    assert result["hint"]["title"] == "`x` no existe (todavía)"


def test_course_sheet_is_complete():
    data = json.loads(DEFAULT_LESSONS_FILE.read_text(encoding="utf-8"))
    course = data["course"]
    assert course["title"] and course["tagline"] and course["level"]
    assert len(course["outcomes"]) >= 3
    assert course["requirements"]
    assert all(module["summary"] for module in data["modules"])
