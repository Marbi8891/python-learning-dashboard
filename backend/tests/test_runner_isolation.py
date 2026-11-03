"""PY-03 y PY-04: el código del alumno no deja roto el intérprete y su salida tiene tope.

Todas las ejecuciones de la consola comparten un mismo intérprete (Pyodide en un Web Worker), así
que se prueban varias seguidas con el runner real (frontend/py/runner.py) en CPython."""

import json
import sys
import tracemalloc

from app.config import DEFAULT_LESSONS_FILE

sys.path.insert(0, str(DEFAULT_LESSONS_FILE.parents[1] / "py"))
import runner  # noqa: E402  (frontend/py/runner.py)


def test_replacing_print_does_not_silence_the_next_runs():
    runner.run_code("import builtins\nbuiltins.print = lambda *a, **k: None")
    assert runner.run_code("print('hola')")["output"] == "hola\n"


def test_deleting_or_adding_builtins_is_undone():
    runner.run_code("import builtins\ndel builtins.len\nbuiltins.invento = 1")
    assert runner.run_code("print(len('abc'))")["output"] == "3\n"
    assert "NameError" in runner.run_code("invento")["error"]


def test_errors_are_described_even_if_the_program_broke_the_builtins():
    result = runner.run_code("import builtins\nbuiltins.str = None\nbuiltins.len = None\n1 / 0")
    assert "ZeroDivisionError" in result["error"]
    assert result["hint"] is not None


def test_recursion_limit_and_modules_are_restored():
    limit = sys.getrecursionlimit()
    runner.run_code("import sys\nsys.setrecursionlimit(60)\nsys.modules['json'] = None")
    assert sys.getrecursionlimit() == limit
    assert runner.run_code("import json\nprint(json.dumps([1]))")["output"] == "[1]\n"


def test_tests_of_an_exercise_cannot_break_the_interpreter_either():
    result = runner.check_exercise("x = 1", [{"test": "import builtins\nbuiltins.print = None"}])
    assert result["passed"]
    assert runner.run_code("print('sigue')")["output"] == "sigue\n"


def test_failed_and_broken_tests_still_report():
    assert runner.check_exercise("x = 1", [{"test": "assert x == 2, 'x vale 1'"}])["message"] == (
        "x vale 1"
    )
    message = runner.check_exercise("x = 1", [{"test": "1 / 0"}])["message"]
    assert "ZeroDivisionError" in message


def test_huge_output_is_capped_while_it_is_produced():
    code = "for i in range(400_000):\n    print('x' * 50)"
    tracemalloc.start()
    result = runner.run_code(code)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    assert len(result["output"]) == runner.MAX_OUTPUT
    assert result["truncated"] is True
    assert peak < 5_000_000, f"pico de memoria {peak} bytes: la salida no debería acumularse"


def test_the_console_says_when_the_output_was_cut():
    cut = json.loads(runner.run_for_js("print('x' * 30_000)", ""))
    assert cut["output"].endswith(runner.TRUNCATED_NOTE)
    assert "20 000" in runner.TRUNCATED_NOTE
    short = json.loads(runner.run_for_js("print('hola')", ""))
    assert short["output"] == "hola\n"


def test_output_exactly_at_the_limit_is_not_marked_as_cut():
    result = runner.run_code(f"print('x' * {runner.MAX_OUTPUT - 1})")
    assert len(result["output"]) == runner.MAX_OUTPUT
    assert result["truncated"] is False
