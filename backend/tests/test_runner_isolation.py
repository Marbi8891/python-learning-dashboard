"""PY-03 y PY-04: el código del alumno no deja roto el intérprete y su salida tiene tope.

Todas las ejecuciones de la consola comparten un mismo intérprete (Pyodide en un Web Worker), así
que se prueban varias seguidas con el runner real (frontend/py/runner.py) en CPython."""

import gc
import json
import os
import sys
import tracemalloc

import pytest

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


# ---------- PLD-004: un ejercicio no contamina los siguientes ----------
# Cada prueba hace lo que haría un alumno sin querer en una ejecución y comprueba la siguiente.


def run(code, stdin=""):
    result = runner.run_code(code, stdin)
    assert not runner._needs_restart, "la restauración no debería fallar"
    return result


def passes(code, test):
    return runner.check_exercise(code, [{"test": test}])["passed"]


def output_of(code):
    result = run(code)
    assert result["error"] is None, result["error"]
    return result["output"]


def test_patching_a_module_function_does_not_reach_the_next_run():
    run("import math\nmath.sqrt = lambda x: 999\nprint(math.sqrt(16))")
    assert output_of("import math\nprint(math.sqrt(16))") == "4.0\n"


def test_deleting_or_adding_module_attributes_is_undone():
    run("import math\ndel math.pi\nmath.invento = 1")
    assert output_of("import math\nprint(math.pi > 3, hasattr(math, 'invento'))") == "True False\n"


def test_modules_imported_for_the_first_time_are_imported_again_clean():
    sys.modules.pop("colorsys", None)
    run("import colorsys\ncolorsys.rgb_to_hsv = None")
    assert "colorsys" not in sys.modules, "un módulo nuevo no se queda en caché con los cambios"
    assert output_of("import colorsys\nprint(colorsys.rgb_to_hsv(1, 0, 0))") == "(0.0, 1.0, 1)\n"


def test_classes_of_the_standard_library_are_restored():
    run(
        "import json\n"
        "json.JSONEncoder.default = lambda self, o: 'X'\n"
        "json.JSONEncoder.nuevo = 1\n"
        "del json.JSONDecoder.decode"
    )
    code = (
        "import json\n"
        "try:\n    json.dumps(object())\nexcept TypeError:\n    print('TypeError')\n"
        "print(hasattr(json.JSONEncoder, 'nuevo'), json.loads('[1]'))"
    )
    assert output_of(code) == "TypeError\nFalse [1]\n"


def test_functions_of_the_standard_library_are_restored():
    run(
        "import textwrap, json\n"
        "textwrap.dedent.__code__ = (lambda text: 'roto').__code__\n"
        "textwrap.shorten.__kwdefaults__ = {'placeholder': '!!!'}\n"
        "json.dumps.__kwdefaults__ = None"
    )
    code = (
        "import textwrap, json\n"
        "print(textwrap.dedent('  a'))\n"
        "print(textwrap.shorten('hola mundo azul', 10))\n"
        "print(json.dumps({'b': 1}))"
    )
    assert output_of(code) == 'a\nhola [...]\n{"b": 1}\n'


def test_the_students_own_classes_and_functions_keep_their_changes_for_the_tests():
    code = (
        "class Contador:\n    total = 0\n\n"
        "Contador.total = 5\nContador.extra = 'si'\n\n"
        "def saluda(nombre='mundo'):\n    return f'hola {nombre}'\n\n"
        "saluda.__defaults__ = ('alumno',)"
    )
    test = "assert Contador.total == 5 and Contador.extra == 'si'\nassert saluda() == 'hola alumno'"
    assert passes(code, test)


def test_the_tests_of_an_exercise_see_the_interpreter_restored():
    # El código no puede engañar a sus tests cambiando la biblioteca estándar
    code = "import math\nmath.sqrt = lambda x: 3\nr = 9 ** 0.5"
    assert passes(code, "import math\nassert math.sqrt(9) == r")
    wrong = "import math\nmath.sqrt = lambda x: 4\nr = 4"
    assert not passes(wrong, "import math\nassert math.sqrt(9) == r")


def test_sys_path_meta_path_and_sys_modules_are_restored():
    path, meta_path = list(sys.path), list(sys.meta_path)
    run(
        "import sys\n"
        "sys.path.insert(0, '/no/existe')\n"
        "class Rompe:\n    def find_spec(self, *args):\n        raise ImportError('roto')\n"
        "sys.meta_path.insert(0, Rompe())\n"
        "sys.modules['falso'] = type(sys)('falso')"
    )
    assert sys.path == path and sys.meta_path == meta_path
    assert "falso" not in sys.modules
    assert output_of("import statistics\nprint(statistics.mean([1, 3]))") == "2\n"


def test_reassigning_sys_lists_is_undone():
    path = sys.path
    run("import sys\nsys.path = []\nsys.argv = None")
    assert sys.path is path and isinstance(sys.argv, list)


def test_files_do_not_survive_to_the_next_run_nor_shadow_modules(monkeypatch):
    monkeypatch.syspath_prepend("")  # como en Pyodide: sys.path empieza por la carpeta actual
    code = (
        "with open('notas.txt', 'w') as f:\n    f.write('hola')\n"
        "with open('mi_modulo.py', 'w') as f:\n    f.write('x = 1')\n"
        "import mi_modulo\nprint(open('notas.txt').read(), mi_modulo.x)"
    )
    assert output_of(code) == "hola 1\n", "dentro de la ejecución, los archivos funcionan"
    result = run("import os\nprint(os.path.exists('notas.txt'))\nimport mi_modulo")
    assert result["output"] == "False\n"
    assert "ModuleNotFoundError" in result["error"]


def test_the_tests_of_a_case_can_read_the_files_the_code_created():
    code = "with open('salida.txt', 'w') as f:\n    f.write('42')"
    assert passes(code, "assert open('salida.txt').read() == '42'")


def test_working_directory_and_environment_are_restored():
    cwd, environ = os.getcwd(), dict(os.environ)
    run("import os\nos.chdir('/')\nos.environ['PLD_PRUEBA'] = '1'\nos.environ.pop('PATH', None)")
    assert os.getcwd() == cwd and dict(os.environ) == environ


def test_state_is_restored_even_after_an_error():
    result = run("import math\nmath.sqrt = None\nimport sys\nsys.setrecursionlimit(50)\n1 / 0")
    assert "ZeroDivisionError" in result["error"]
    assert output_of("import math\nprint(math.sqrt(4))") == "2.0\n"
    for ending in ("exit()", "raise KeyboardInterrupt"):
        run(f"import math\nmath.pi = 3\n{ending}")
        assert output_of("import math\nprint(math.pi > 3.1)") == "True\n"


def test_recursion_error_does_not_lower_the_limit():
    limit = sys.getrecursionlimit()
    result = run("import sys\nsys.setrecursionlimit(80)\ndef f(n):\n    return f(n + 1)\nf(0)")
    assert "RecursionError" in result["error"]
    assert sys.getrecursionlimit() == limit


@pytest.mark.filterwarnings("ignore::UserWarning")
def test_library_state_warnings_decimal_digits_and_gc():
    run(
        "import warnings, decimal, sys, gc\n"
        "warnings.simplefilter('error')\n"
        "decimal.getcontext().prec = 2\n"
        "sys.set_int_max_str_digits(640)\n"
        "gc.disable()"
    )
    assert gc.isenabled()
    code = (
        "import warnings, decimal\n"
        "warnings.warn('aviso')\n"
        "print(decimal.Decimal(1) / decimal.Decimal(3))\n"
        "print(len(str(10 ** 1000)))"
    )
    assert output_of(code).endswith("0.3333333333333333333333333333\n1001\n")


def test_seeding_random_in_one_run_does_not_fix_the_next_one():
    seeded = output_of("import random\nrandom.seed(1)\nprint(random.random())")
    after = {output_of("import random\nprint(random.random())") for _ in range(3)}
    assert seeded not in after


def test_trace_function_is_restored():
    before = sys.gettrace()
    run("import sys\nsys.settrace(lambda *a: None)")
    assert sys.gettrace() is before


def test_audit_hooks_cannot_be_added_from_the_console():
    real = sys.addaudithook
    result = run("import sys\nsys.addaudithook(lambda *a: None)")
    assert "RuntimeError" in result["error"], "un hook puesto no se podría quitar"
    assert sys.addaudithook is real


def test_many_consecutive_runs_stay_isolated():
    breakers = [
        "import math\nmath.sqrt = None",
        "import builtins\nbuiltins.len = None",
        "import sys\nsys.path.clear()",
        "import json\njson.loads = None",
        "open('x.txt', 'w').write('1')",
    ]
    for round_ in range(5):
        for breaker in breakers:
            run(breaker)
        code = (
            "import math, json, os\n"
            "print(math.sqrt(9), len('ab'), json.loads('1'), os.path.exists('x.txt'))"
        )
        assert output_of(code) == "3.0 2 1 False\n", f"vuelta {round_}"


def test_if_the_interpreter_cannot_be_restored_the_page_is_asked_to_restart(monkeypatch):
    monkeypatch.setattr(runner, "_needs_restart", False)
    # Borra su propia carpeta de trabajo: al terminar ya no se puede volver a ella
    code = "import os\nd = os.getcwd()\nos.chdir('/')\nos.rmdir(d)"
    answer = json.loads(runner.run_for_js(code, ""))
    assert answer["restart"] is True
    checked = runner.check_for_js("x = 1", json.dumps([{"test": "assert x == 1"}]))
    assert json.loads(checked)["restart"]
    monkeypatch.setattr(runner, "_needs_restart", False)
    assert json.loads(runner.run_for_js("print(1)", ""))["restart"] is False
