"""Ejecuta el código del alumno y comprueba los ejercicios.

Se usa en el navegador (Pyodide, dentro de un Web Worker) y en los tests de CPython,
así que tiene que funcionar igual en los dos sitios: solo biblioteca estándar.
"""

import builtins
import contextlib
import gc
import importlib
import io
import json
import operator
import os
import shutil
import sys
import tempfile
import traceback
import types
import warnings

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


# ---------- Aislamiento entre ejecuciones (PY-03, PLD-004) ----------
#
# Todas las ejecuciones comparten un intérprete: reiniciar Pyodide cuesta unos 2 s y aislar una
# ejecución, unos pocos ms (docs/AISLAMIENTO_PYTHON.md). Por eso no se reinicia: antes de cada
# ejecución se guarda lo que un programa puede cambiar y al terminar se deja como estaba. No es un
# sandbox de seguridad: evita que un ejercicio contamine los siguientes, no que un programa escrito
# para romper el intérprete lo consiga (si la restauración falla, la página crea un Worker nuevo).

_IMMUTABLE_TYPE = 1 << 8  # Py_TPFLAGS_IMMUTABLETYPE: tipos de C que no admiten setattr (int, list…)
_STREAMS = frozenset({"stdin", "stdout", "stderr"})  # los gestiona _execute (y pytest en las pruebas)
_MISSING = object()
# Las clases solo se copian de la biblioteca estándar: es lo único que se puede importar en la
# consola (no hay micropip) y así las pruebas en CPython no tocan las de FastAPI, pytest…
_STDLIB = frozenset(sys.stdlib_module_names)
_Failure = Exception  # sin buscarlo en builtins, que el programa pudo vaciar

# True si una restauración falló: run_for_js y check_for_js lo devuelven como "restart" y la página
# crea un Worker nuevo para la siguiente ejecución (frontend/js/python-runner.js)
_needs_restart = False


class _FunctionJournal:
    """Anota el valor anterior de __code__, __defaults__ y __kwdefaults__ de las funciones que cambia
    el programa. CPython avisa a los hooks de auditoría antes de cada uno de esos cambios
    («object.__setattr__»; asignar None avisa como «object.__delattr__»), así que no hace falta
    copiar en cada ejecución las ~4 000 funciones cargadas (unos 8 ms en Pyodide). Solo se anotan
    las de módulos que ya estaban cargados: las que define el alumno conservan sus cambios. Las
    clases no avisan (type.__setattr__ no se audita) y se copian en _snapshot."""

    def __init__(self) -> None:
        self.active = False
        self.skip: frozenset = frozenset()
        self.modules: dict = {}
        self.changes: dict = {}

    def __call__(self, event: str, args: tuple) -> None:
        if not self.active or event not in _FUNCTION_EVENTS or not isinstance(args[0], types.FunctionType):
            return
        function, part = args[0], args[1]
        owner = getattr(function, "__module__", None)
        if owner in self.skip or self.modules.get(owner) is None:
            return
        self.changes.setdefault((id(function), part), (function, part, getattr(function, part)))

    def start(self, modules: dict, skip: frozenset) -> None:
        self.modules, self.skip, self.changes, self.active = modules, skip, {}, True

    def undo(self, trash: list) -> None:
        self.active = False
        for function, part, before in reversed(list(self.changes.values())):
            trash.append(getattr(function, part))
            setattr(function, part, before)
        self.changes, self.modules = {}, {}


_FUNCTION_EVENTS = frozenset({"object.__setattr__", "object.__delattr__"})  # = None es un delattr
_journal = _FunctionJournal()
sys.addaudithook(_journal)  # no se puede quitar; con la anotación inactiva solo mira una variable


def _snapshot(skip: frozenset) -> dict:
    """Foto de lo que un programa puede cambiar sin querer: módulos cargados, sus atributos y sus
    clases (de la biblioteca estándar), listas de sys, directorio, entorno y estado de random y
    decimal. `skip` es el __name__ del código del alumno ("__main__" o "solucion"): sus clases y
    funciones conservan los cambios."""
    modules = dict(sys.modules)
    saved = {"modules": modules, "sys": dict(vars(sys)), "recursion": sys.getrecursionlimit(),
             "trace": sys.gettrace(), "profile": sys.getprofile(), "cwd": os.getcwd(),
             "lists": [(lst, list(lst)) for lst in (sys.path, sys.meta_path, sys.path_hooks, sys.argv)],
             "importer_cache": dict(sys.path_importer_cache), "environ": dict(os.environ),
             "gc": gc.isenabled(), "dicts": [], "classes": []}
    for name, module in modules.items():
        if not isinstance(module, types.ModuleType) or module is builtins or module is sys:
            continue
        namespace = vars(module)
        saved["dicts"].append((namespace, dict(namespace)))
        if name in skip or name.partition(".")[0] not in _STDLIB:
            continue
        for value in list(namespace.values()):
            if isinstance(value, type) and not value.__flags__ & _IMMUTABLE_TYPE and value.__module__ == name:
                saved["classes"].append((value, dict(vars(value))))
    if hasattr(sys, "get_int_max_str_digits"):
        saved["int_digits"] = sys.get_int_max_str_digits()
    if "random" in modules and hasattr(modules["random"], "getstate"):
        saved["random"] = modules["random"].getstate()
    if "decimal" in modules:
        saved["decimal"] = modules["decimal"].getcontext().copy()
    _journal.start(modules, skip)
    return saved


def _unchanged(current, original: dict) -> bool:
    """¿Mismas claves y mismos objetos, en el mismo orden? Todo en C y por identidad (`is`): no
    llama al __eq__ de ningún objeto del alumno. Si el orden cambió, se restaura igualmente."""
    return (len(current) == len(original) and all(map(operator.is_, current, original))
            and all(map(operator.is_, current.values(), original.values())))


def _restore_dict(current: dict, original: dict, trash: list, keep=frozenset()) -> None:
    """Deja `current` con las mismas claves y objetos que `original` (compara por identidad)."""
    if not keep and _unchanged(current, original):
        return
    for name in [name for name in current if name not in original and name not in keep]:
        trash.append(current.pop(name))
    for name, value in original.items():
        if name not in keep and current.get(name, _MISSING) is not value:
            trash.append(current.get(name))
            current[name] = value


def _restore_class(cls: type, original: dict, trash: list) -> None:
    current = vars(cls)  # mappingproxy: solo se cambia con setattr y delattr
    if _unchanged(current, original):
        return
    for name in [name for name in current if name not in original]:
        trash.append(current[name])
        delattr(cls, name)
    for name, value in original.items():
        if current.get(name, _MISSING) is not value:
            trash.append(current.get(name))
            setattr(cls, name, value)


def _restore(saved: dict) -> None:
    """Deja el intérprete como antes de ejecutar el código del alumno (PY-03, PLD-004)."""
    global _needs_restart
    # Lo retirado se suelta al final: un __del__ del alumno no vuelve a cambiar lo ya restaurado
    trash: list = []
    try:
        _restore_builtins()
        _journal.undo(trash)
        # sys primero: si se reasignaron sys.path, sys.modules… vuelven los objetos originales
        _restore_dict(vars(sys), saved["sys"], trash, keep=_STREAMS)
        for namespace, original in saved["dicts"]:
            _restore_dict(namespace, original, trash)
        for lst, items in saved["lists"]:
            lst[:] = items
        _restore_dict(sys.path_importer_cache, saved["importer_cache"], trash)
        # Los módulos que el programa sustituyó o borró vuelven; los que importó por primera vez se
        # descartan: el siguiente programa los importa de nuevo, sin los cambios que les hiciera este
        _restore_dict(sys.modules, saved["modules"], trash)
        for cls, original in saved["classes"]:
            _restore_class(cls, original, trash)
        sys.setrecursionlimit(saved["recursion"])
        if "int_digits" in saved:
            sys.set_int_max_str_digits(saved["int_digits"])
        if sys.gettrace() is not saved["trace"]:
            sys.settrace(saved["trace"])
        if sys.getprofile() is not saved["profile"]:
            sys.setprofile(saved["profile"])
        if os.getcwd() != saved["cwd"]:
            os.chdir(saved["cwd"])
        if dict(os.environ) != saved["environ"]:
            os.environ.clear()
            os.environ.update(saved["environ"])
        (gc.enable if saved["gc"] else gc.disable)()
        if "random" in saved:
            sys.modules["random"].setstate(saved["random"])
        if "decimal" in saved:
            sys.modules["decimal"].setcontext(saved["decimal"])
    except _Failure:  # el programa dejó algo que no se puede deshacer desde Python
        _needs_restart = True
    finally:
        _journal.active = False
        trash.clear()


def _restore_builtins() -> None:
    """Vuelve a poner las funciones integradas. No usa ninguna (ni len, ni list…): el programa pudo
    borrarlas, y todo lo demás (también salir de los `with`) las necesita."""
    current = vars(builtins)
    for name in [name for name in current if name not in _PRISTINE_BUILTINS]:
        del current[name]
    for name, value in _PRISTINE_BUILTINS.items():
        if current.get(name, _MISSING) is not value:
            current[name] = value


def _no_audit_hooks(hook) -> None:
    raise RuntimeError("sys.addaudithook no está disponible en la consola: no se podría deshacer.")


@contextlib.contextmanager
def _isolated(name: str):
    """Ejecuta un bloque y deshace al terminar lo que haya cambiado en el intérprete."""
    saved = _snapshot(frozenset({name}))
    sys.addaudithook = _no_audit_hooks  # un hook de auditoría no se puede quitar una vez puesto
    try:
        with warnings.catch_warnings():  # filtros de warnings (simplefilter("error")…)
            yield
    finally:
        _restore(saved)  # también devuelve el sys.addaudithook de verdad


@contextlib.contextmanager
def _working_directory():
    """Cada ejecución (con los tests de su caso) trabaja en una carpeta temporal vacía que se borra
    al terminar: sus archivos no aparecen en el ejercicio siguiente ni tapan módulos de la
    biblioteca estándar (sys.path empieza por '', la carpeta actual)."""
    previous = os.getcwd()
    folder = tempfile.mkdtemp(prefix="pld-")
    os.chdir(folder)
    try:
        yield
    finally:
        os.chdir(previous)
        shutil.rmtree(folder, ignore_errors=True)
        importlib.invalidate_caches()


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


def _execute(code: str, stdin: str, name: str, *, filename: str = USER_FILE, namespace: dict | None = None,
             capture_stderr: bool = True) -> tuple[_LimitedOutput, dict, BaseException | None]:
    """Ejecuta `code` aislado (_isolated). Devuelve la salida, el espacio de nombres y el error."""
    output = _LimitedOutput()
    namespace = {"__name__": name} if namespace is None else namespace
    errors = output if capture_stderr else sys.stderr
    old_stdin = sys.stdin
    sys.stdin = io.StringIO(stdin)
    caught = None
    try:
        with _isolated(name), contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            try:
                exec(compile(code, filename, "exec"), namespace)
            finally:
                _restore_builtins()  # lo primero: salir de los `with` usa funciones integradas
    except BaseException as exc:  # también SystemExit (exit()) y KeyboardInterrupt
        caught = exc
    finally:
        sys.stdin = old_stdin
    return output, namespace, caught


def run_code(code: str, stdin: str = "", name: str = "__main__") -> dict:
    """Ejecuta `code` con `stdin` como entrada. Devuelve salida, error y el espacio de nombres."""
    with _working_directory():
        output, namespace, caught = _execute(code, stdin, name)
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
    Los tests de un caso se ejecutan con el intérprete ya restaurado (el código no puede engañarlos
    cambiando `len` o `math`), pero en la misma carpeta, para que vean los archivos que creó.
    """
    for number, case in enumerate(cases, start=1):
        stdin = case.get("stdin", "")
        base = {"passed": False, "case": number, "total": len(cases), "stdin": stdin}
        with _working_directory():
            output, namespace, caught = _execute(code, stdin, "solucion")
            if caught is None:
                namespace.update(__output__=output.getvalue(), __code__=code)
                _, _, failure = _execute(case["test"], "", "solucion", filename="<tests>",
                                         namespace=namespace, capture_stderr=False)
        if caught is not None:
            return base | {"message": "Tu código da un error al ejecutarse.",
                           "output": output.getvalue(), "error": _format_error(caught, code),
                           "hint": explain_error(caught)}
        if isinstance(failure, AssertionError):
            return base | {"message": str(failure) or "Un test ha fallado.",
                           "output": output.getvalue(), "error": None}
        if failure is not None:
            return base | {"message": f"Al probar tu código se produjo {type(failure).__name__}: {failure}",
                           "output": output.getvalue(), "error": None}
    return {"passed": True, "case": len(cases), "total": len(cases),
            "message": "¡Todos los tests superados!"}


# ---------- Puntos de entrada para JavaScript (reciben y devuelven JSON) ----------
# "restart": la restauración falló y la página tiene que crear un Worker nuevo antes de seguir.

def run_for_js(code: str, stdin: str) -> str:
    result = run_code(code, stdin)
    output = result["output"] + (TRUNCATED_NOTE if result["truncated"] else "")
    return json.dumps({"output": output, "error": result["error"], "hint": result["hint"],
                       "restart": _needs_restart})


def check_for_js(code: str, cases_json: str) -> str:
    return json.dumps(check_exercise(code, json.loads(cases_json)) | {"restart": _needs_restart})
