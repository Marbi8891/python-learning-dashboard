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


# ---------- Explicación de errores para principiantes ----------


def _error_line(error: BaseException) -> int | None:
    """Línea del código del alumno donde se produjo el error."""
    if isinstance(error, SyntaxError) and error.filename == USER_FILE:
        return error.lineno
    lines = [f.lineno for f in traceback.extract_tb(error.__traceback__) if f.filename == USER_FILE]
    return lines[-1] if lines else None


def _syntax_hint(message: str) -> tuple[str, str]:
    if "never closed" in message or "unterminated" in message or "EOF" in message:
        return ("Falta cerrar algo",
                "Hay un paréntesis, corchete, llave o comillas que se abren y no se cierran. "
                "Cuenta que cada ( tenga su ) y cada comilla su pareja.")
    if "expected ':'" in message:
        return ("Faltan los dos puntos",
                "Las líneas que empiezan por `if`, `elif`, `else`, `for`, `while`, `def` o `class` "
                "terminan en dos puntos `:`.")
    if "Maybe you meant '=='" in message or "cannot assign" in message:
        return ("¿Querías comparar?",
                "Un solo `=` guarda un valor en una variable. Para comparar dos valores se usa `==`.")
    if "forgot a comma" in message:
        return ("¿Falta una coma?",
                "Entre los elementos de una lista, los argumentos de una función o los textos "
                "de un `print()` va una coma.")
    return ("Python no entiende cómo está escrita esta línea",
            "Revisa la línea señalada y la anterior: paréntesis, comillas, dos puntos y operadores.")


def explain_error(error: BaseException) -> dict | None:
    """Explica en español los errores más habituales. None si no hay explicación útil."""
    message = str(error)
    if isinstance(error, IndentationError):
        title, text = ("Problema de sangría",
                       "Python usa la sangría (los espacios al principio de la línea) para saber qué "
                       "va dentro de un `if`, `for`, `def`… Tras una línea que termina en `:` la "
                       "siguiente va 4 espacios más a la derecha, y las del mismo bloque, alineadas.")
    elif isinstance(error, SyntaxError):
        title, text = _syntax_hint(message)
    elif isinstance(error, UnboundLocalError):
        title, text = ("Variable usada antes de darle valor",
                       "Dentro de la función das valor a esa variable, así que Python la considera "
                       "local y todavía no tiene valor cuando la usas. Pásala como parámetro.")
    elif isinstance(error, NameError):
        name = getattr(error, "name", None) or "ese nombre"
        title, text = (f"`{name}` no existe (todavía)",
                       f"Usas `{name}`, pero Python no lo conoce. Causas típicas: está mal escrito "
                       "(las mayúsculas cuentan), no lo has creado antes de usarlo, o es un texto "
                       "y le faltan las comillas.")
    elif isinstance(error, TypeError):
        if "concatenate" in message or "unsupported operand" in message:
            title, text = ("Mezclas tipos que no se combinan",
                           "Por ejemplo, un texto y un número: `\"Edad: \" + 30`. Convierte uno de los "
                           "dos (`str(30)`) o usa una f-string: `f\"Edad: {30}\"`.")
        elif "not callable" in message:
            title, text = ("Eso no es una función",
                           "Pones paréntesis `()` detrás de algo que no es una función. ¿Has usado "
                           "el mismo nombre para una variable y una función?")
        elif "required positional argument" in message:
            title, text = ("Faltan datos al llamar a la función",
                           "La función necesita más argumentos de los que le pasas. Mira su `def`.")
        elif "positional argument" in message:
            title, text = ("Sobran datos al llamar a la función",
                           "Le pasas más argumentos de los que espera. Mira su `def`.")
        else:
            title, text = ("Operación no válida para ese tipo de dato",
                           "Comprueba el tipo de cada valor con `type()`.")
    elif isinstance(error, ValueError):
        if "invalid literal for int()" in message or "could not convert" in message:
            title, text = ("Ese texto no es un número",
                           "`int()` y `float()` solo convierten textos que parecen números: `\"42\"` "
                           "sí, pero `\"hola\"` o un texto vacío no. Revisa lo que escribiste en «Entrada».")
        else:
            title, text = ("Valor no válido", "El valor no sirve para esa operación.")
    elif isinstance(error, ZeroDivisionError):
        title, text = ("División entre cero",
                       "Ningún número se puede dividir entre 0. Comprueba el divisor con un `if` antes.")
    elif isinstance(error, IndexError):
        title, text = ("Esa posición no existe",
                       "Las posiciones empiezan en 0 y la última es `len(lista) - 1`.")
    elif isinstance(error, KeyError):
        title, text = ("Esa clave no está en el diccionario",
                       "Comprueba antes con `clave in diccionario` o usa `diccionario.get(clave)`.")
    elif isinstance(error, AttributeError):
        title, text = ("Ese valor no tiene ese método",
                       "Revisa el nombre y el tipo del valor: por ejemplo, `.append()` es de las "
                       "listas, no de los textos.")
    elif isinstance(error, EOFError):
        title, text = ("Faltan datos en «Entrada»",
                       "Tu programa usa `input()` más veces que líneas hay en «Entrada». "
                       "Escríbelos en «Entrada», uno por línea.")
    elif isinstance(error, ModuleNotFoundError):
        title, text = ("Paquete no disponible aquí",
                       "Ese paquete no está instalado en la consola del navegador. "
                       "Ejecuta este código en PyCharm.")
    elif isinstance(error, RecursionError):
        title, text = ("Una función se llama a sí misma sin fin",
                       "Revisa el caso que debe detener la recursión.")
    elif isinstance(error, FileNotFoundError):
        title, text = ("No se encuentra el archivo",
                       "Revisa el nombre y la ruta. En la consola solo existen los archivos que "
                       "crea tu propio código.")
    else:
        return None
    return {"title": title, "text": text, "line": _error_line(error)}


def run_code(code: str, stdin: str = "", name: str = "__main__") -> dict:
    """Ejecuta `code` con `stdin` como entrada. Devuelve salida, error y el espacio de nombres."""
    output = io.StringIO()
    namespace = {"__name__": name}
    old_stdin = sys.stdin
    sys.stdin = io.StringIO(stdin)
    error = None
    hint = None
    try:
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            exec(compile(code, USER_FILE, "exec"), namespace)
    except BaseException as exc:  # también SystemExit (exit()) y KeyboardInterrupt
        error = _format_error(exc, code)
        hint = explain_error(exc)
    finally:
        sys.stdin = old_stdin
    return {
        "output": output.getvalue()[:MAX_OUTPUT],
        "error": error,
        "hint": hint,
        "namespace": namespace,
    }


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
                           "output": result["output"], "error": result["error"],
                           "hint": result["hint"]}

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
    return json.dumps({"output": result["output"], "error": result["error"], "hint": result["hint"]})


def check_for_js(code: str, cases_json: str) -> str:
    return json.dumps(check_exercise(code, json.loads(cases_json)))
