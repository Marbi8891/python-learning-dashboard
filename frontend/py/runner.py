"""Ejecuta el código del alumno y comprueba los ejercicios.

Se usa en el navegador (Pyodide, dentro de un Web Worker) y en los tests de CPython,
así que tiene que funcionar igual en los dos sitios: solo biblioteca estándar.
"""

import contextlib
import io
import json
import sys
import traceback

USER_FILE = "<tu código>"
MAX_OUTPUT = 20_000


def _format_error(error: BaseException, code: str) -> str:
    """Traceback limitado al código del alumno (sin las líneas internas del runner)."""
    if isinstance(error, SyntaxError):
        return "".join(traceback.format_exception_only(type(error), error)).rstrip()
    source = code.splitlines()
    lines = ["Traceback (most recent call last):"]
    for frame in traceback.extract_tb(error.__traceback__):
        if frame.filename != USER_FILE or not frame.lineno:
            continue
        lines.append(f'  File "{USER_FILE}", line {frame.lineno}, in {frame.name}')
        if frame.lineno <= len(source):
            lines.append(f"    {source[frame.lineno - 1].strip()}")
    lines += traceback.format_exception_only(type(error), error)
    return "\n".join(line.rstrip() for line in lines)


def run_code(code: str, stdin: str = "", name: str = "__main__") -> dict:
    """Ejecuta `code` con `stdin` como entrada. Devuelve salida, error y el espacio de nombres."""
    output = io.StringIO()
    namespace = {"__name__": name}
    old_stdin = sys.stdin
    sys.stdin = io.StringIO(stdin)
    error = None
    try:
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            exec(compile(code, USER_FILE, "exec"), namespace)
    except BaseException as exc:  # también SystemExit (exit()) y KeyboardInterrupt
        error = _format_error(exc, code)
    finally:
        sys.stdin = old_stdin
    return {"output": output.getvalue()[:MAX_OUTPUT], "error": error, "namespace": namespace}


def check_exercise(code: str, cases: list[dict]) -> dict:
    """Ejecuta el código una vez por caso y lanza los tests de cada caso.

    Cada caso es {"stdin": str, "test": str}. Los tests son asserts que ven las
    variables del alumno, su salida (`__output__`) y su código fuente (`__code__`).
    El código se ejecuta con __name__ = "solucion": lo que esté dentro de
    `if __name__ == "__main__":` no se ejecuta durante la comprobación.
    """
    for number, case in enumerate(cases, start=1):
        stdin = case.get("stdin", "")
        result = run_code(code, stdin, name="solucion")
        base = {"passed": False, "case": number, "total": len(cases), "stdin": stdin}
        if result["error"]:
            return base | {"message": "Tu código da un error al ejecutarse.",
                           "output": result["output"], "error": result["error"]}

        namespace = result["namespace"]
        namespace.update(__output__=result["output"], __code__=code)
        test_output = io.StringIO()
        sys.stdin, old_stdin = io.StringIO(""), sys.stdin
        try:
            with contextlib.redirect_stdout(test_output):
                exec(compile(case["test"], "<tests>", "exec"), namespace)
        except AssertionError as exc:
            return base | {"message": str(exc) or "Un test ha fallado.",
                           "output": result["output"], "error": None}
        except BaseException as exc:
            return base | {"message": f"Al probar tu código se produjo {type(exc).__name__}: {exc}",
                           "output": result["output"], "error": None}
        finally:
            sys.stdin = old_stdin
    return {"passed": True, "case": len(cases), "total": len(cases),
            "message": "¡Todos los tests superados!"}


# ---------- Puntos de entrada para JavaScript (reciben y devuelven JSON) ----------

def run_for_js(code: str, stdin: str) -> str:
    result = run_code(code, stdin)
    return json.dumps({"output": result["output"], "error": result["error"]})


def check_for_js(code: str, cases_json: str) -> str:
    return json.dumps(check_exercise(code, json.loads(cases_json)))
