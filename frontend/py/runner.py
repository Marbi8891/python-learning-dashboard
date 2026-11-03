"""Ejecuta el código del alumno y comprueba los ejercicios.

Se usa en el navegador (Pyodide, dentro de un Web Worker) y en los tests de CPython,
así que tiene que funcionar igual en los dos sitios: solo biblioteca estándar.
"""

import builtins
import contextlib
import io
import json
import sys
import traceback

USER_FILE = "<tu código>"
MAX_OUTPUT = 20_000
TRUNCATED_NOTE = f"\n… (salida recortada: solo se muestran los primeros {MAX_OUTPUT:,} caracteres)".replace(",", " ")

# Copia de las funciones integradas tal como estaban al cargar el runner (PY-03). Todas las
# ejecuciones comparten intérprete: si un programa cambia `builtins.print` o borra `len`, se deja
# como estaba al terminar, para que la consola y la corrección sigan funcionando.
_PRISTINE_BUILTINS = dict(vars(builtins))


class _LimitedOutput(io.TextIOBase):
    """Salida con tope (PY-04): guarda solo los primeros MAX_OUTPUT caracteres mientras se generan.
    Antes se guardaba todo y se recortaba al final: un bucle de print podía llenar la memoria."""

    def __init__(self) -> None:
        self._parts: list[str] = []
        self._size = 0
        self.truncated = False

    def writable(self) -> bool:
        return True

    def write(self, text: str) -> int:
        room = MAX_OUTPUT - self._size
        if room > 0:
            piece = text[:room]
            self._parts.append(piece)
            self._size += len(piece)
        if len(text) > max(room, 0):
            self.truncated = True
        return len(text)

    def getvalue(self) -> str:
        return "".join(self._parts)


def _snapshot() -> dict:
    return {"modules": dict(sys.modules), "recursion": sys.getrecursionlimit()}


def _restore(saved: dict) -> None:
    """Deja el intérprete como antes de ejecutar el código del alumno (PY-03)."""
    current = vars(builtins)
    for name in [name for name in current if name not in _PRISTINE_BUILTINS]:
        del current[name]
    for name, value in _PRISTINE_BUILTINS.items():
        if current.get(name) is not value:
            current[name] = value
    # Módulos que el programa borró o sustituyó en sys.modules (los nuevos se quedan en caché)
    for name, module in saved["modules"].items():
        if sys.modules.get(name) is not module:
            sys.modules[name] = module
    sys.setrecursionlimit(saved["recursion"])


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
    output = _LimitedOutput()
    namespace = {"__name__": name}
    saved = _snapshot()
    old_stdin = sys.stdin
    sys.stdin = io.StringIO(stdin)
    caught = None
    try:
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            exec(compile(code, USER_FILE, "exec"), namespace)
    except BaseException as exc:  # también SystemExit (exit()) y KeyboardInterrupt
        caught = exc
    finally:
        sys.stdin = old_stdin
        _restore(saved)
    # El error se describe con el intérprete ya restaurado (el programa pudo romper len, str…)
    error = _format_error(caught, code) if caught is not None else None
    hint = explain_error(caught) if caught is not None else None
    return {
        "output": output.getvalue(),
        "truncated": output.truncated,
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
        test_output = _LimitedOutput()
        sys.stdin, old_stdin = io.StringIO(""), sys.stdin
        saved = _snapshot()
        caught = None
        try:
            with contextlib.redirect_stdout(test_output):
                exec(compile(case["test"], "<tests>", "exec"), namespace)
        except BaseException as exc:
            caught = exc
        finally:
            sys.stdin = old_stdin
            _restore(saved)
        if isinstance(caught, AssertionError):
            return base | {"message": str(caught) or "Un test ha fallado.",
                           "output": result["output"], "error": None}
        if caught is not None:
            return base | {"message": f"Al probar tu código se produjo {type(caught).__name__}: {caught}",
                           "output": result["output"], "error": None}
    return {"passed": True, "case": len(cases), "total": len(cases),
            "message": "¡Todos los tests superados!"}


# ---------- Puntos de entrada para JavaScript (reciben y devuelven JSON) ----------

def run_for_js(code: str, stdin: str) -> str:
    result = run_code(code, stdin)
    output = result["output"] + (TRUNCATED_NOTE if result["truncated"] else "")
    return json.dumps({"output": output, "error": result["error"], "hint": result["hint"]})


def check_for_js(code: str, cases_json: str) -> str:
    return json.dumps(check_exercise(code, json.loads(cases_json)))
