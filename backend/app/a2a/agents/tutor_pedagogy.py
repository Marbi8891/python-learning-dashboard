"""Decisiones pedagógicas deterministas del Python Tutor (ADR-0036).

Sin modelo de lenguaje y sin red: qué tipo de consulta es, de qué concepto habla, qué nivel tiene
el alumno y con qué evidencia, si su respuesta a una pregunta de comprobación es correcta y qué
pista toca dar. Son reglas sencillas y comprobables con tests; el modelo (si lo hay) recibe sus
conclusiones como hechos, no tiene que adivinarlas.
"""

import re
import unicodedata
from dataclasses import dataclass
from typing import Literal

from app.a2a.conversation import Conversation
from app.services.curriculum import Curriculum, OutputExercise
from app.services.learning_context import LearnerContext

Level = Literal["inicial", "intermedio", "avanzado"]
LEVELS: tuple[Level, ...] = ("inicial", "intermedio", "avanzado")
Intent = Literal[
    "concepto",
    "depuracion",
    "pista",
    "solucion",
    "ejercicio",
    "comprobacion",
    "ambigua",
    "fuera_de_tema",
    "saludo",
]
# Intenciones que se responden siempre sin modelo: no gastan consultas ni dependen del proveedor
PREPARED_INTENTS: frozenset[str] = frozenset({"comprobacion", "ambigua", "fuera_de_tema", "saludo"})

# Puntos de evidencia (conceptos demostrados + lecciones con el ejercicio superado) por nivel
INTERMEDIATE_POINTS = 4
ADVANCED_POINTS = 12
MAX_HINTS = 3


def fold(text: str) -> str:
    """Minúsculas y sin tildes, para comparar palabras."""
    decomposed = unicodedata.normalize("NFKD", text.lower())
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def words(text: str) -> list[str]:
    return re.findall(r"[a-z_][a-z0-9_]*", fold(text))


_SOLUTION = re.compile(
    r"\b(soluci[oó]n|resu[eé]lve(lo|me)?|d[aá]me el c[oó]digo|hazlo t[uú]|hazme el ejercicio)\b",
    re.IGNORECASE,
)
_HINT = re.compile(
    r"\b(pista|pistas|no s[eé] (por d[oó]nde|c[oó]mo) (empezar|seguir)|me he atascado|"
    r"estoy atascad[oa])\b",
    re.IGNORECASE,
)
_EXERCISE = re.compile(
    r"\b(prop[oó]n\w*|quiero practicar|dame (otro|un) ejercicio|otro ejercicio|"
    r"ejercicio para practicar)\b",
    re.IGNORECASE,
)
_DEBUG = re.compile(
    r"\b(falla|fallo|error|errores|no funciona|no me funciona|no va|no compila|traceback|"
    r"excepci[oó]n|peta|se rompe)\b",
    re.IGNORECASE,
)
_LOGIC = re.compile(
    r"\b(no da (el|lo)|sale mal|da mal|deber[ií]a (dar|salir|mostrar|imprimir|devolver)|"
    r"esperaba|resultado (incorrecto|equivocado|raro)|no hace lo que|en vez de|en lugar de)\b",
    re.IGNORECASE,
)
_CONCEPTUAL = re.compile(
    r"\b(qu[eé] (es|son|significa|hace|hacen)|diferencia|para qu[eé]|c[oó]mo (funciona|se usa|uso)|"
    r"expl[ií]ca\w*|cu[aá]ndo (uso|se usa)|por qu[eé])\b",
    re.IGNORECASE,
)
_GREETING = re.compile(
    r"^\s*(hola|buenas|buenos d[ií]as|buenas tardes|buenas noches|hey|gracias|muchas gracias)\b"
    r"[\s!.,¡]*$",
    re.IGNORECASE,
)
_CONFUSED = re.compile(
    r"\b(no (lo )?entiendo|no me queda claro|m[aá]s despacio|paso a paso|otra vez|"
    r"expl[ií]camelo)\b",
    re.IGNORECASE,
)
_DONT_KNOW = re.compile(r"^\s*(no (lo )?s[eé]|ni idea|no tengo ni idea|no estoy segur[oa])\b", re.I)
_ANSWER_PREFIX = re.compile(
    r"^\s*(creo que|pienso que|supongo que|yo dir[ií]a|seguro que)?\s*"
    r"(muestra|imprime|sale|saldr[aá]|da|dar[aá]|el resultado es|la salida es|es)?\s*:?\s*",
    re.IGNORECASE,
)

# Palabras clave → concepto de learning.json. Gana el concepto con más coincidencias; si empatan,
# el que aparece antes aquí (más concreto).
CONCEPT_KEYWORDS: dict[str, tuple[str, ...]] = {
    "listas": ("lista", "listas", "list", "append", "array", "arrays", "arreglo", "arreglos"),
    "tuplas-conjuntos": ("tupla", "tuplas", "tuple", "conjunto", "conjuntos", "set"),
    "diccionarios": ("diccionario", "diccionarios", "dict", "clave", "claves", "keyerror"),
    "strings": ("string", "strings", "cadena", "cadenas", "str", "slicing", "upper", "split"),
    "acumuladores": ("acumulador", "acumuladores", "contador", "contadores"),
    "bucles": ("bucle", "bucles", "for", "while", "range", "iterar", "repetir", "vuelta"),
    "condicionales": ("if", "elif", "else", "condicional", "condicionales", "condicion"),
    "funciones": (
        "funcion",
        "funciones",
        "def",
        "return",
        "parametro",
        "parametros",
        "argumento",
        "argumentos",
    ),
    "excepciones": ("excepcion", "excepciones", "try", "except", "raise", "finally"),
    "poo": ("clase", "clases", "objeto", "objetos", "poo", "self", "herencia", "__init__"),
    "archivos": ("archivo", "archivos", "fichero", "ficheros", "open"),
    "modulos": ("modulo", "modulos", "import", "importar", "paquete", "biblioteca", "libreria"),
    "variables": ("variable", "variables", "asignar", "asignacion"),
    "tipos": ("tipo", "tipos", "int", "float", "bool", "booleano", "convertir", "entero"),
    "operadores": ("operador", "operadores", "resto", "and", "or", "not", "division"),
    "entrada-salida": ("input", "print", "fstring", "teclado", "pantalla"),
    "algoritmos": ("algoritmo", "algoritmos"),
    "pseudocodigo": ("pseudocodigo",),
    "trazado": ("traza", "trazado", "trazar"),
    "depuracion": ("depurar", "depuracion", "debug", "depurador"),
    "validacion": ("validar", "validacion"),
    "recorridos": ("recorrido", "recorridos", "maximo", "minimo"),
}
# Vocabulario de programación general: si no aparece nada de esto, la pregunta no es de Python
PROGRAMMING_WORDS = frozenset(
    word for keywords in CONCEPT_KEYWORDS.values() for word in keywords
) | frozenset(
    {
        "python",
        "programa",
        "programar",
        "programacion",
        "codigo",
        "ejercicio",
        "leccion",
        "consola",
        "metodo",
        "metodos",
        "sintaxis",
        "error",
        "errores",
        "indice",
        "valor",
        "valores",
        "salida",
        "entrada",
        "imprimir",
        "numpy",
        "pyodide",
        "pep",
        "pcap",
        "ejecutar",
        "compilar",
        "recursion",
        "lambda",
        "comprension",
        "iterador",
        "generador",
        "decorador",
        "test",
        "pytest",
        "sangria",
        "indentacion",
        "none",
        "true",
        "false",
    }
)

# Definiciones de los términos que más usa el tutor, para el nivel inicial
GLOSSARY: dict[str, str] = {
    "variable": "un nombre que apunta a un valor guardado en memoria.",
    "lista": "una colección ordenada de valores que se puede modificar, escrita entre `[` y `]`.",
    "indice": "la posición de un elemento; en Python se empieza a contar desde 0.",
    "funcion": "un bloque de código con nombre que se ejecuta al llamarlo con `()`.",
    "argumento": "el valor que se pasa a una función entre los paréntesis.",
    "metodo": "una función que pertenece a un tipo y se llama con un punto: `lista.append(3)`.",
    "bucle": "un bloque de código que se repite (`for` o `while`).",
    "tipo": "la clase de valor: `int` (entero), `float` (decimal), `str` (texto), `bool`.",
    "excepcion": "el error que Python lanza al ejecutar una línea que no puede completar.",
    "traceback": "el informe de error de Python; la última línea dice el tipo de error.",
    "sangria": "los espacios al principio de la línea, que marcan qué está dentro de un bloque.",
    "diccionario": "una colección de pares clave → valor, escrita entre `{` y `}`.",
    "booleano": "un valor que solo puede ser `True` o `False`.",
    "modulo": "un archivo de Python con funciones que se pueden reutilizar con `import`.",
    "parametro": "el nombre que recibe, dentro de la función, el valor que se le pasa.",
}

# Matices técnicos revisados a mano, para preguntas en las que es fácil equivocarse
PRECISION_NOTES: tuple[tuple[re.Pattern[str], str, str], ...] = (
    (
        re.compile(r"\b(array|arrays|arreglo|arreglos|numpy|vector)\b", re.IGNORECASE),
        "listas",
        "En Python lo que otros lenguajes llaman «array» se hace casi siempre con una **lista**, "
        "pero no son lo mismo:\n\n"
        "- **`list`** (integrada en Python): ordenada y modificable; puede mezclar tipos, como "
        '`[1, "a", 2.5]`, y crece con `append`.\n'
        "- **`array.array`** (módulo `array` de la biblioteca estándar): todos los elementos son "
        "del mismo tipo numérico, indicado con un código: `array('i', [1, 2, 3])` guarda "
        "enteros y ocupa menos memoria que una lista.\n"
        "- **`numpy.ndarray`** (biblioteca externa NumPy, hay que instalarla): arrays numéricos "
        "de una o más dimensiones con operaciones elemento a elemento. `np.array([1, 2]) * 2` "
        "da `array([2, 4])`, mientras que `[1, 2] * 2` da `[1, 2, 1, 2]`: con una lista, `*` "
        "repite la lista.\n\n"
        "En este curso se usan listas.",
    ),
)


@dataclass(frozen=True)
class LevelEstimate:
    level: Level
    basis: str  # de dónde sale el nivel, en palabras
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True)
class CheckResult:
    exercise: OutputExercise
    answer: str
    correct: bool
    misconception: str | None = None  # error típico que delata la respuesta, si se conoce
    unknown: bool = False  # «no lo sé»


def match_concept(curriculum: Curriculum, *texts: str | None) -> str | None:
    tokens = [token for text in texts if text for token in words(text)]
    best, best_score = None, 0
    for concept_id, keywords in CONCEPT_KEYWORDS.items():
        score = sum(token in keywords for token in tokens)
        if score > best_score and concept_id in curriculum.concepts:
            best, best_score = concept_id, score
    return best


def precision_note(question: str) -> tuple[str, str] | None:
    for pattern, concept, note in PRECISION_NOTES:
        if pattern.search(question):
            return concept, note
    return None


def is_programming(text: str) -> bool:
    return any(token in PROGRAMMING_WORDS for token in words(text)) or bool(
        re.search(r"[()\[\]{}=]|\.\w+\(", text)
    )


def looks_like_answer(question: str, conversation: Conversation | None) -> bool:
    """¿Responde el alumno a la pregunta de comprobación pendiente?"""
    if conversation is None or not conversation.pending_check or len(question) > 160:
        return False
    if _SOLUTION.search(question) or _HINT.search(question) or _EXERCISE.search(question):
        return False
    if _CONFUSED.search(question):  # «no lo entiendo» pide otra explicación, no es una respuesta
        return False
    return "¿" not in question and not question.rstrip().endswith("?")  # una pregunta nueva


def classify(
    question: str,
    *,
    code: str | None,
    error: str | None,
    errors: list[str],
    concept: str | None,
    conversation: Conversation | None,
) -> Intent:
    if not code and not error and looks_like_answer(question, conversation):
        return "comprobacion"
    if _SOLUTION.search(question):
        return "solucion"
    if _HINT.search(question):
        return "pista"
    if _EXERCISE.search(question):
        return "ejercicio"
    if code or error or errors or _DEBUG.search(question) or _LOGIC.search(question):
        return "depuracion"
    if _GREETING.match(question):
        return "saludo"
    if concept or _CONCEPTUAL.search(question) and is_programming(question):
        return "concepto"
    if conversation and conversation.concept and _CONFUSED.search(question):
        return "concepto"  # «no lo entiendo»: se vuelve a explicar el tema actual
    if is_programming(question):
        return "concepto"
    return "fuera_de_tema" if len(question.split()) >= 4 else "ambigua"


def describes_logic_error(question: str) -> bool:
    return bool(_LOGIC.search(question))


def is_confused(question: str) -> bool:
    return bool(_CONFUSED.search(question))


def estimate_level(
    explicit: Level | None,
    learner: LearnerContext | None,
    concept: str | None = None,
    conversation: Conversation | None = None,
) -> LevelEstimate:
    """Nivel con su evidencia. Nunca sale solo del % global de lecciones completadas.

    1. Si el alumno lo elige, manda su elección.
    2. Si no, puntos de evidencia: conceptos demostrados en ejercicios + lecciones con el
       ejercicio superado (≥ 4 intermedio, ≥ 12 avanzado). Sin evidencia: inicial.
    3. Dificultades demostradas en el concepto de la pregunta bajan un nivel; en la conversación,
       fallar la comprobación lleva a inicial y acertarla sube un nivel.
    """
    if explicit:
        return LevelEstimate(explicit, "elegido por el alumno")
    evidence: list[str] = []
    points = 0
    if learner is not None:
        points = len(learner.mastered_concepts) + learner.lessons_passed
        if learner.mastered_concepts:
            evidence.append(f"{len(learner.mastered_concepts)} conceptos demostrados en ejercicios")
        if learner.lessons_passed:
            evidence.append(f"{learner.lessons_passed} lecciones con el ejercicio superado")
    index = 2 if points >= ADVANCED_POINTS else 1 if points >= INTERMEDIATE_POINTS else 0
    basis = (
        "evidencia de ejercicios"
        if points
        else "sin evidencia suficiente: se empieza por el nivel inicial"
    )
    if concept and learner is not None and concept in learner.struggling_concepts:
        index = max(0, index - 1)
        evidence.append("dificultades demostradas en este concepto")
    if concept and conversation is not None:
        if concept in conversation.wrong:
            index = 0
            evidence.append("ha fallado la comprobación de este concepto en la conversación")
        elif concept in conversation.correct:
            index = min(2, index + 1)
            evidence.append("ha acertado la comprobación de este concepto en la conversación")
    return LevelEstimate(LEVELS[index], basis, tuple(evidence))


def after_check(estimate: LevelEstimate, correct: bool) -> LevelEstimate:
    """El nivel se ajusta en el mismo turno en que el alumno responde a la comprobación."""
    index = min(2, LEVELS.index(estimate.level) + 1) if correct else 0
    note = "acaba de acertar la comprobación" if correct else "acaba de fallar la comprobación"
    return LevelEstimate(LEVELS[index], estimate.basis, (*estimate.evidence, note))


def _normalize_answer(text: str) -> str:
    text = re.sub(r"^```\w*\n?|\n?```$", "", text.strip())
    text = text.strip(" \t\n`\"'«»“”").rstrip(".").strip(" `\"'«»“”")
    return re.sub(r"\s+", "", text).casefold()


def evaluate_check(exercise: OutputExercise, answer: str) -> CheckResult:
    """Compara la respuesta con la salida comprobada en CI. Determinista: sin modelo."""
    if _DONT_KNOW.match(answer):
        return CheckResult(exercise, answer, False, unknown=True)
    candidates = {_normalize_answer(answer), _normalize_answer(_ANSWER_PREFIX.sub("", answer))}
    if _normalize_answer(exercise.expect) in candidates:
        return CheckResult(exercise, answer, True)
    for trap, misconception in exercise.traps.items():
        if _normalize_answer(trap) in candidates:
            return CheckResult(exercise, answer, False, misconception)
    return CheckResult(exercise, answer, False)


def pick_check(
    curriculum: Curriculum,
    concept: str | None,
    level: Level,
    asked: list[str],
    harder: bool = False,
) -> OutputExercise | None:
    """Una pregunta de predicción del concepto, adecuada al nivel y no repetida."""
    if not concept:
        return None
    options = [ex for ex in curriculum.output_exercises.get(concept, ()) if ex.id not in asked]
    top = {"inicial": 1, "intermedio": 2, "avanzado": 3}[level] + (1 if harder else 0)
    suitable = [ex for ex in options if ex.level <= top] or options
    if not suitable:
        return None
    return sorted(suitable, key=lambda ex: (-ex.level if harder else ex.level, ex.id))[0]


def glossary_for(text: str, skip: set[str], limit: int = 2) -> list[tuple[str, str]]:
    """Términos técnicos que aparecen en el texto y su definición (nivel inicial)."""
    present = set(words(text))
    found = []
    for term, definition in GLOSSARY.items():
        if term in skip:
            continue
        if term in present or f"{term}s" in present or f"{term}es" in present:
            found.append((term, definition))
    return found[:limit]
