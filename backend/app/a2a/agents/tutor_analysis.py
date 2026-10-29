"""Análisis estático del código y del texto del alumno para el Python Tutor.

Todo es LECTURA: el código se convierte en árbol sintáctico con `ast.parse`, que analiza el texto
pero no ejecuta nada (ni `exec`, ni `eval`, ni `compile` en modo ejecución, ni `subprocess`). Lo
único que se «evalúa» son literales con `ast.literal_eval` (números, textos, listas…), que no
pueden llamar a funciones.

Separa lo que es un HECHO (lo que dice el analizador de Python o el propio mensaje de error) de lo
que es una HIPÓTESIS (lo que probablemente pasará al ejecutarlo). El tutor nunca afirma que ha
ejecutado el código.
"""

import ast
import builtins
import difflib
import re
import warnings
from dataclasses import dataclass, field
from typing import Literal

ErrorKind = Literal["sintaxis", "ejecucion", "logica"]

SYNTAX_ERRORS = frozenset({"SyntaxError", "IndentationError", "TabError"})
BUILTINS = frozenset(dir(builtins)) | {"__name__", "__file__", "__doc__"}

_ERROR_NAME = re.compile(r"\b([A-Z][A-Za-z]*(?:Error|Exception))\b")
_LINE = re.compile(r"line (\d+)")

# Mensajes del analizador de Python (CPython 3.11–3.13) traducidos a una explicación para quien
# empieza. Se muestra también el mensaje original: es lo que verá en la consola.
SYNTAX_HINTS: tuple[tuple[str, str], ...] = (
    ("expected ':'", "falta `:` al final de la línea que abre el bloque (`if`, `for`, `def`…)"),
    ("never closed", "hay un paréntesis, corchete o llave que se abre y no se cierra"),
    ("unterminated string", "unas comillas se abren y no se cierran"),
    ("unterminated triple-quoted", "unas comillas triples se abren y no se cierran"),
    ("Maybe you meant '==' or ':='", "hay un `=` donde va una comparación: para comparar, `==`"),
    ("cannot assign to", "a la izquierda de `=` solo puede ir un nombre de variable"),
    ("Missing parentheses in call to 'print'", "`print` es una función: `print(valor)`"),
    ("expected an indented block", "después de la línea con `:` el bloque debe ir con sangría"),
    ("unexpected indent", "esa línea tiene sangría sin que la abra un bloque"),
    ("unindent does not match", "la sangría no coincide con la de las líneas anteriores"),
    ("inconsistent use of tabs", "se mezclan tabuladores y espacios en la sangría"),
    ("unmatched", "hay un cierre `)`, `]` o `}` que no corresponde a ninguna apertura"),
    ("invalid decimal literal", "un nombre no puede empezar por un número"),
    ("Perhaps you forgot a comma", "parece que falta una coma entre dos valores"),
)
_INCOMPLETE = ("never closed", "unexpected EOF", "expected an indented block", "unterminated")

# Métodos o funciones de otros lenguajes que no existen en Python, con su equivalente real
NOT_PYTHON: dict[str, str] = {
    "push": "En Python las listas no tienen `push`: se usa `lista.append(valor)`.",
    "length": "En Python no hay `.length`: se usa la función `len(objeto)`.",
    "size": "En Python no hay `.size()` para listas o textos: se usa `len(objeto)`.",
    "toUpperCase": "En Python es `texto.upper()`.",
    "toLowerCase": "En Python es `texto.lower()`.",
    "includes": "En Python se usa el operador `in`: `valor in lista`.",
    "contains": "En Python se usa el operador `in`: `valor in coleccion`.",
    "forEach": "En Python se recorre con `for elemento in lista:`.",
    "indexOf": "En Python es `lista.index(valor)` (lanza ValueError si no está).",
    "charAt": "En Python se usa el índice: `texto[posicion]`.",
    "trim": "En Python es `texto.strip()`.",
    "equals": "En Python se compara con `==`.",
    "println": "En Python se usa `print(valor)`.",
    "printf": 'En Python se usa `print()` con f-strings: `print(f"{valor}")`.',
    "echo": "En Python se usa `print(valor)`.",
    "parseInt": "En Python se convierte con `int(texto)`.",
    "toString": "En Python se convierte con `str(valor)`.",
}
_CALLED = re.compile(r"\.?\b([A-Za-z_]\w*)\s*\(")
_ATTRIBUTE = re.compile(r"\.([A-Za-z_]\w*)\b")
# «la función `nombre`», «el método lista.add()»: solo nombres escritos como código
_FUNCTION_WORD = re.compile(
    r"\b(?:funci[oó]n|m[eé]todo)\s+(?:`([A-Za-z_][\w.]*)(?:\(\))?`|([A-Za-z_][\w.]*)\(\))",
    re.IGNORECASE,
)
_TYPES = {
    "list": list,
    "lista": list,
    "str": str,
    "texto": str,
    "dict": dict,
    "set": set,
    "tuple": tuple,
    "int": int,
    "float": float,
}

_INJECTION = re.compile(
    r"(ignora|olvida|omite|salta(te)?)\s+(todas\s+)?(las\s+|tus\s+)?(instrucciones|reglas|normas)"
    r"|ignore\s+(all\s+)?(previous|prior|above|the)\s+(instructions|rules)"
    r"|(system|sistema)\s*prompt|prompt\s+del\s+sistema"
    r"|act[uú]a\s+como|eres\s+ahora|you\s+are\s+now|from\s+now\s+on"
    r"|(dame|da|escribe|muestra|revela)\s+(la\s+)?soluci[oó]n\s+(completa\s+)?(aunque|sin\s+pistas)"
    r"|(marca|considera|da)\s+(el\s+)?ejercicio\s+(como\s+)?(aprobado|superado|correcto)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class SyntaxProblem:
    line: int | None
    message: str  # el mensaje original del analizador
    explanation: str  # lo mismo explicado en español
    incomplete: bool


@dataclass(frozen=True)
class CodeFindings:
    """Resultado de leer el código. `facts` son ciertos; `hypotheses`, probables."""

    syntax: SyntaxProblem | None = None
    facts: tuple[str, ...] = ()
    hypotheses: tuple[str, ...] = ()
    misconceptions: tuple[str, ...] = ()  # ids de learning.json que encajan con lo visto
    suggestion: str | None = None  # el cambio pequeño que se propone probar
    incomplete: bool = False
    undefined: tuple[str, ...] = field(default=())

    @property
    def parsed(self) -> bool:
        return self.syntax is None


def parse(code: str) -> ast.Module | SyntaxProblem:
    """Árbol sintáctico o el problema de sintaxis. No ejecuta el código."""
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # SyntaxWarning de secuencias de escape, etc.
            return ast.parse(code)
    except SyntaxError as error:
        message = error.msg or "invalid syntax"
        explanation = next(
            (text for needle, text in SYNTAX_HINTS if needle in message),
            "Python no entiende la forma de esa línea; revisa también la anterior",
        )
        incomplete = any(needle in message for needle in _INCOMPLETE)
        return SyntaxProblem(error.lineno, message, explanation, incomplete)
    except (ValueError, RecursionError, MemoryError):  # bytes nulos, anidación extrema…
        return SyntaxProblem(None, "no se puede analizar", "el código no se puede analizar", False)


def _assigned_and_loaded(tree: ast.Module) -> tuple[set[str], list[ast.Name]]:
    assigned: set[str] = set()
    loaded: list[ast.Name] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            (assigned.add(node.id) if not isinstance(node.ctx, ast.Load) else loaded.append(node))
        elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
            assigned.add(node.name)
        elif isinstance(node, ast.arg):
            assigned.add(node.arg)
        elif isinstance(node, ast.alias):
            assigned.add((node.asname or node.name).split(".")[0])
        elif isinstance(node, ast.ExceptHandler) and node.name:
            assigned.add(node.name)
        elif isinstance(node, ast.Global | ast.Nonlocal):
            assigned.update(node.names)
        elif isinstance(node, ast.MatchAs | ast.MatchStar) and node.name:
            assigned.add(node.name)
    return assigned, loaded


def _first_top_level_assignment(tree: ast.Module) -> dict[str, int]:
    """Línea en que cada nombre se asigna por primera vez fuera de funciones y clases."""
    first: dict[str, int] = {}
    for statement in tree.body:
        if isinstance(statement, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
            first.setdefault(statement.name, statement.lineno)
            continue
        for node in ast.walk(statement):
            if isinstance(node, ast.Name) and not isinstance(node.ctx, ast.Load):
                first.setdefault(node.id, node.lineno)
            elif isinstance(node, ast.alias):
                first.setdefault((node.asname or node.name).split(".")[0], statement.lineno)
    return first


def _top_level_loads(tree: ast.Module) -> list[ast.Name]:
    loads = []
    for statement in tree.body:
        if isinstance(statement, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
            continue
        loads += [
            node
            for node in ast.walk(statement)
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)
        ]
    return loads


def _is_input_call(node: ast.AST) -> bool:
    return (
        isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "input"
    )


def _is_number(node: ast.AST) -> bool:
    return (
        isinstance(node, ast.Constant)
        and isinstance(node.value, int | float)
        and not isinstance(node.value, bool)
    )


def _type_findings(tree: ast.Module) -> tuple[list[str], list[str], set[str]]:
    """Mezclas de texto y número: seguras con literales, probables con `input()`."""
    facts, hypotheses, misconceptions = [], [], set()
    from_input = {
        target.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Assign) and _is_input_call(node.value)
        for target in node.targets
        if isinstance(target, ast.Name)
    }

    def is_text(node: ast.AST) -> bool:
        return isinstance(node, ast.Constant) and isinstance(node.value, str)

    def from_keyboard(node: ast.AST) -> bool:
        return _is_input_call(node) or (isinstance(node, ast.Name) and node.id in from_input)

    for node in ast.walk(tree):
        pairs = []
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add | ast.Sub | ast.Div):
            pairs.append((node.left, node.right, node.lineno))
        if isinstance(node, ast.Compare) and len(node.ops) == 1:
            if isinstance(node.ops[0], ast.Lt | ast.LtE | ast.Gt | ast.GtE):
                pairs.append((node.left, node.comparators[0], node.lineno))
        for left, right, line in pairs:
            if (is_text(left) and _is_number(right)) or (_is_number(left) and is_text(right)):
                facts.append(
                    f"Línea {line}: se combina un texto con un número. Al ejecutarse, Python "
                    "lanzará `TypeError`."
                )
                misconceptions.add("tipos.texto-numero")
            elif (from_keyboard(left) and _is_number(right)) or (
                _is_number(left) and from_keyboard(right)
            ):
                hypotheses.append(
                    f"Línea {line}: el valor viene de `input()`, que siempre devuelve texto "
                    "(`str`). Operarlo o compararlo con un número dará `TypeError`; conviértelo "
                    "antes con `int()` o `float()`."
                )
                misconceptions.add("entrada-salida.input-texto")
    return facts, hypotheses, misconceptions


def _logic_findings(tree: ast.Module) -> tuple[list[str], set[str]]:
    """Patrones de errores lógicos frecuentes (sin excepción): siempre son hipótesis."""
    found, misconceptions = [], set()
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Assign)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Attribute)
            and node.value.func.attr in {"sort", "append", "reverse", "remove", "insert"}
        ):
            found.append(
                f"Línea {node.lineno}: `{node.value.func.attr}()` modifica la lista y devuelve "
                "`None`, así que la variable de la izquierda acabará valiendo `None`."
            )
            misconceptions.add("listas.sort-none")
        if isinstance(node, ast.For | ast.While):
            for statement in node.body:
                if isinstance(statement, ast.Return):
                    found.append(
                        f"Línea {statement.lineno}: hay un `return` directamente dentro del "
                        "bucle: la función terminará en la primera vuelta."
                    )
                    misconceptions.add("funciones.return-en-bucle")
                if (
                    isinstance(statement, ast.Assign)
                    and _is_number(statement.value)
                    and statement.value.value in (0, 1)
                ):
                    names = [t.id for t in statement.targets if isinstance(t, ast.Name)]
                    if names:
                        found.append(
                            f"Línea {statement.lineno}: `{names[0]}` se pone a "
                            f"{statement.value.value} en cada vuelta del bucle; si es un "
                            "acumulador, inicialízalo antes del bucle."
                        )
                        misconceptions.add("acumuladores.inicializa-dentro")
        if isinstance(node, ast.While) and isinstance(node.test, ast.Constant) and node.test.value:
            has_break = any(isinstance(inner, ast.Break) for inner in ast.walk(node))
            if not has_break:
                found.append(
                    f"Línea {node.lineno}: `while True` sin `break`: el bucle no terminará."
                )
                misconceptions.add("bucles.bucle-infinito")
    return found, misconceptions


def _placeholders(tree: ast.Module) -> list[int]:
    """Líneas con `...` o con funciones que solo tienen `pass`: el código está a medias."""
    lines = [
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and node.value is Ellipsis
    ]
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and all(
            isinstance(statement, ast.Pass) for statement in node.body
        ):
            lines.append(node.lineno)
    return sorted(set(lines))


def analyze_code(code: str) -> CodeFindings:
    """Lee el código (sin ejecutarlo) y devuelve hechos, hipótesis y el cambio que se propone."""
    tree = parse(code)
    if isinstance(tree, SyntaxProblem):
        where = f" en la línea {tree.line}" if tree.line else ""
        fact = (
            f"El analizador de Python encuentra un error de sintaxis{where}: «{tree.message}». "
            f"Significa que {tree.explanation}."
        )
        return CodeFindings(
            syntax=tree,
            facts=(fact,),
            suggestion=f"Corrige solo la línea {tree.line} y vuelve a ejecutarlo."
            if tree.line
            else "Corrige esa parte y vuelve a ejecutarlo.",
            incomplete=tree.incomplete,
        )

    facts = ["El código no tiene errores de sintaxis según el analizador de Python."]
    hypotheses: list[str] = []
    misconceptions: set[str] = set()
    suggestion = None

    assigned, loaded = _assigned_and_loaded(tree)
    undefined = sorted({name.id for name in loaded} - assigned - BUILTINS)
    for name in undefined:
        close = difflib.get_close_matches(name, sorted(assigned | BUILTINS), n=1, cutoff=0.8)
        guess = f" ¿Quizá querías escribir `{close[0]}`?" if close else ""
        hypotheses.append(
            f"`{name}` se usa pero no se crea en este código: si no viene de otra parte, Python "
            f"lanzará `NameError`.{guess}"
        )
        suggestion = suggestion or (
            f"Cambia `{name}` por `{close[0]}` y vuelve a ejecutarlo."
            if close
            else f"Asigna un valor a `{name}` antes de usarla y vuelve a ejecutarlo."
        )
    first = _first_top_level_assignment(tree)
    for node in _top_level_loads(tree):
        line = first.get(node.id)
        if line is not None and node.lineno < line and node.id not in BUILTINS:
            hypotheses.append(
                f"Línea {node.lineno}: `{node.id}` se usa antes de crearse (se asigna en la línea "
                f"{line}): Python lee de arriba abajo y lanzará `NameError`."
            )
            misconceptions.add("variables.orden-asignacion")
            suggestion = suggestion or (
                f"Mueve la asignación de `{node.id}` por encima de la línea {node.lineno}."
            )
            break

    type_facts, type_hypotheses, type_misconceptions = _type_findings(tree)
    facts += type_facts
    hypotheses += type_hypotheses
    misconceptions |= type_misconceptions
    if type_facts or type_hypotheses:
        suggestion = suggestion or "Convierte el texto a número con `int()` antes de operar."

    logic, logic_misconceptions = _logic_findings(tree)
    hypotheses += logic
    misconceptions |= logic_misconceptions

    placeholders = _placeholders(tree)
    if placeholders:
        lines = ", ".join(str(line) for line in placeholders)
        facts.append(f"El código está a medias: hay `...` o funciones vacías (líneas {lines}).")
        suggestion = suggestion or "Completa primero la línea marcada con `...`."

    return CodeFindings(
        facts=tuple(facts),
        hypotheses=tuple(hypotheses),
        misconceptions=tuple(sorted(misconceptions)),
        suggestion=suggestion,
        incomplete=bool(placeholders),
        undefined=tuple(undefined),
    )


# ---------- Errores ----------


def detect_errors(*texts: str | None) -> list[str]:
    """Nombres de excepciones de Python mencionados, sin repetir y en orden de aparición."""
    found = _ERROR_NAME.findall("\n".join(t for t in texts if t))
    return list(dict.fromkeys(found))


def error_kind(errors: list[str], logic_described: bool) -> ErrorKind | None:
    """Sintaxis (no llega a ejecutarse), ejecución (excepción) o lógica (sale mal, sin error)."""
    if any(name in SYNTAX_ERRORS for name in errors):
        return "sintaxis"
    if errors:
        return "ejecucion"
    return "logica" if logic_described else None


def error_line(error: str | None) -> int | None:
    """Última línea del traceback que cita el alumno (la que señala Python)."""
    lines = _LINE.findall(error or "")
    return int(lines[-1]) if lines else None


# ---------- Texto del alumno ----------


def mentions_injection(*texts: str | None) -> bool:
    """Instrucciones dirigidas al tutor escondidas en la pregunta, el código o el error."""
    return any(_INJECTION.search(text) for text in texts if text)


def unknown_apis(question: str, code: str | None) -> list[tuple[str, str]]:
    """Funciones o métodos que no existen en Python (o no son integrados) y su equivalente."""
    found: dict[str, str] = {}
    for text in (question, code or ""):
        for name in _CALLED.findall(text) + _ATTRIBUTE.findall(text):
            if name in NOT_PYTHON:
                found.setdefault(name, NOT_PYTHON[name])
    defined: set[str] = set()
    if code:
        tree = parse(code)
        if isinstance(tree, ast.Module):
            defined = _assigned_and_loaded(tree)[0]
    for quoted, called in _FUNCTION_WORD.findall(question):
        owner, _, name = (quoted or called).rpartition(".")
        kind = _TYPES.get(owner)
        if name in NOT_PYTHON:
            found.setdefault(name, NOT_PYTHON[name])
        elif kind is not None:
            if not hasattr(kind, name):
                found.setdefault(
                    name,
                    f"El tipo `{kind.__name__}` no tiene ningún método `{name}`. Puedes ver los "
                    f"que tiene con `help({kind.__name__})` en la consola.",
                )
        elif (
            name not in BUILTINS
            and name not in defined
            and not _is_known_method(name)
            and len(name) > 2
        ):
            found.setdefault(
                name,
                f"`{name}` no es una función integrada de Python ni un método de sus tipos "
                "básicos. Si es tuya o de una biblioteca, enséñame su definición o el `import`.",
            )
    return list(found.items())


def _is_known_method(name: str) -> bool:
    return any(hasattr(kind, name) for kind in (list, str, dict, set, tuple, int, float))


_PRINT = re.compile(r"print\((.{1,200}?)\)\s*$")


def literal_print_output(text: str) -> tuple[str, str] | None:
    """Si el alumno pregunta qué hace `print(<literales>)`, la salida exacta, sin ejecutar nada.

    `ast.literal_eval` solo admite literales (números, textos, listas, tuplas, diccionarios,
    conjuntos, booleanos y None): no llama a funciones, así que es seguro. `print` muestra cada
    argumento con `str()` separado por un espacio.
    """
    candidates = re.findall(r"`([^`]+)`", text) or [text]
    for candidate in candidates:
        match = _PRINT.search(candidate.strip().rstrip("?¿ "))
        if not match:
            continue
        source = match.group(0)
        try:
            call = ast.parse(source.strip(), mode="eval").body
        except (SyntaxError, ValueError, RecursionError, MemoryError):
            continue
        if not isinstance(call, ast.Call) or call.keywords:
            continue
        try:
            values = [ast.literal_eval(argument) for argument in call.args]
            output = " ".join(str(value) for value in values)
        except (ValueError, TypeError, SyntaxError, RecursionError, MemoryError):
            continue
        return source.strip(), output
    return None
