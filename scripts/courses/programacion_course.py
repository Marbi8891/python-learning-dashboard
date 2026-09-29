# ruff: noqa: E501
# (contenido didáctico: los textos largos van en una sola línea para poder leerlos y editarlos)
"""Curso de Programación (módulo 0485 de DAW, en Python) para la app Android (ADR-0020).

Sigue las unidades de trabajo UT1-UT9 del curso «DAW-Programacion» de César San Juan Pastor
(IES Arcipreste de Hita), publicado con licencia Creative Commons no comercial:
https://github.com/csanjuanp-ies/DAW-Programacion

La teoría y las preguntas son propias: siguen el orden y los contenidos de esas unidades, sin copiar
su texto. Donde los apuntes simplifican o se equivocan, se enseña lo correcto (ADR-0020).

Las preguntas con salida se ejecutan con Python en una carpeta temporal (las de ficheros escriben
allí) y se comprueba que la salida real es la esperada. Las de interfaces gráficas (PySide6) no se
ejecutan: preguntan qué hace el código.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from course_builder import Block, Lesson, Q, main  # noqa: E402

# ---------------------------------------------------------------- ejecución


def run_python(code: str) -> str:
    with tempfile.TemporaryDirectory() as folder:
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
            cwd=folder,
        )
    if result.returncode != 0:
        return "Error"
    return result.stdout.rstrip("\n")


def check_example(code: str) -> None:
    assert run_python(code) != "Error", f"el ejemplo falla:\n{code}"


# ---------------------------------------------------------------- ayudas


def tq(id: str, q: str, options: list[str], answer: int, explain: str) -> Q:
    """Pregunta teórica."""
    return Q(id=id, q=q, options=options, answer=answer, explain=explain)


def kq(id: str, q: str, code: str, options: list[str], answer: int, explain: str) -> Q:
    """Pregunta sobre un fragmento que no se ejecuta (pseudocódigo, interfaces gráficas…)."""
    return Q(id=id, q=q, code=code.strip("\n"), options=options, answer=answer, explain=explain)


def pq(id: str, q: str, code: str, expect: str, wrong: list[str], explain: str) -> Q:
    """Pregunta de Python: se ejecuta y la salida real tiene que ser `expect`."""
    return Q(id=id, q=q, code=code.strip("\n"), expect=expect, wrong=wrong, explain=explain)


def fq(id: str, q: str, code: str, accept: list[str], expect: str, explain: str) -> Q:
    """Completar el hueco `___`: cada respuesta aceptada se ejecuta y tiene que dar `expect`."""
    return Q(
        id=id,
        q=q,
        code=code.strip("\n"),
        expect=expect,
        explain=explain,
        kind="fill",
        accept=accept,
    )


def oq(id: str, q: str, lines: list[str], expect: str, explain: str) -> Q:
    """Ordenar las líneas de un programa."""
    return Q(id=id, q=q, code="___", expect=expect, explain=explain, kind="order", lines=lines)


def bq(id: str, code: str, bug: int, fix: str, target: str, explain: str) -> Q:
    """Encontrar la línea con el error: la corrección tiene que mostrar `target`."""
    q = f"Este programa debería mostrar `{target}`, pero falla o muestra otra cosa. ¿Qué línea tiene el error?"
    return Q(
        id=id,
        q=q,
        code=code.strip("\n"),
        explain=explain,
        kind="bug",
        bug=bug,
        fix=fix,
        target=target,
    )


QUE = "¿Qué muestra este código?"

APUNTES = (
    "DAW-Programacion · César San Juan Pastor (IES Arcipreste de Hita), CC BY-NC",
    "https://github.com/csanjuanp-ies/DAW-Programacion",
)
TUTORIAL = ("Tutorial oficial de Python (en español)", "https://docs.python.org/es/3/tutorial/")
PEP8 = ("PEP 8 — Guía de estilo para el código Python", "https://peps.python.org/pep-0008/")
PYSIDE = ("Qt for Python (PySide6) — documentación oficial", "https://doc.qt.io/qtforpython-6/")
PSEINT = ("PSeInt — intérprete de pseudocódigo", "https://pseint.sourceforge.net/")

# ================================================================ UT1

L_UT1 = Lesson(
    slug="prog-ut1-algoritmos",
    title="UT1 · Introducción, algoritmos y pseudocódigo",
    theory="""
**Un poco de historia:** el ábaco; la **Pascalina** de Blaise Pascal (1642), una calculadora mecánica; las **tarjetas perforadas** del telar de Jacquard (1802); la máquina diferencial de **Charles Babbage** (1822); la **máquina de Turing** de Alan Turing; el **ENIAC** (proyecto iniciado en 1943, unos 18.000 tubos de vacío) y el **transistor** (1947, laboratorios Bell).

**Software** según su función: **de sistema** (sistema operativo, controladores), **de programación** (compiladores, IDE) y **de aplicación** (lo que haremos casi siempre).

**Programar** es diseñar y codificar un algoritmo con las instrucciones de un lenguaje, respetando su sintaxis. Pasos: observar el problema → pensar soluciones **en papel** → elegir la mejor → implementarla → probarla.

**Paradigmas:**
- **Estructurada:** solo tres estructuras (**secuencial, alternativa e iterativa**), sin saltos incondicionales (`goto`).
- **Modular:** el programa se divide en funciones que funcionan como **cajas negras**, con **máxima cohesión y mínimo acoplamiento**.
- **Orientada a objetos:** el código se organiza en clases y objetos (UT4).

**Algoritmo:** conjunto **ordenado y finito** de operaciones que resuelve un problema, con entradas y salidas definidas. Tiene un número finito de pasos, termina en un tiempo finito y cada paso es **preciso, sin ambigüedad**. Elementos: datos (entero, real, lógico, carácter, cadena), constantes y variables, expresiones (operadores y operandos) y palabras reservadas. Esquema: **Entrada → Proceso → Salida**. No hay un único algoritmo para cada problema.

**Representación:**
- **Diagrama de flujo (ordinograma):** empieza arriba y termina abajo; los símbolos de inicio y fin aparecen **una sola vez**; el flujo va de arriba abajo y de izquierda a derecha; se evitan los cruces con conectores.
- **Pseudocódigo:** con **PSeInt**, un intérprete de pseudocódigo para estudiantes que además dibuja el diagrama de flujo. Asignación con `←`; estructuras `Si … Entonces … SiNo … FinSi`, `Mientras … Hacer … FinMientras`, `Para`, `Segun`; `Leer` y `Escribir`.

**Eficiencia:** en espacio (memoria) y en tiempo. El **orden de complejidad** dice cómo crece el coste al crecer los datos: `O(1)` constante, `O(log n)` logarítmico, `O(n)` lineal, `O(n log n)`, `O(n²)` cuadrático.

**Lenguajes:** de bajo nivel (máquina, ensamblador) y de alto nivel. Según su ejecución: **compilados** (los más rápidos, dependen de la arquitectura), **interpretados** y **mixtos** (compilan a **bytecode** que ejecuta una máquina virtual: ganan portabilidad; Java y Python).

**Documentación:** **interna** (comentarios y docstrings en el código) y **externa** (diseño, manual de usuario y de mantenimiento).

**Ciclo de vida clásico:** análisis → diseño → codificación y pruebas → implantación → mantenimiento. Solo una de las fases es escribir código.
""",
    example="""
# Pseudocódigo (PSeInt):  C <- A;  A <- B;  B <- C
a = 4
b = 2
print("Antes:", a, b)
c = a        # variable auxiliar
a = b
b = c
print("Después:", a, b)

# Par o impar:  Si (n % 2) = 0 Entonces Escribir "Par" SiNo Escribir "Impar" FinSi
n = 7
if n % 2 == 0:
    print("Par")
else:
    print("Impar")
""",
    exercise="""
Escribe en **pseudocódigo** (o en PSeInt) y después en Python un algoritmo que:

1. lea dos números;
2. muestre cuál es mayor o si son iguales.

Dibuja también su diagrama de flujo en papel: un solo inicio y un solo fin.
""",
    starter="a = 5\nb = 8\n\n# Si a > b ... SiNo Si b > a ... SiNo iguales\n",
    hint="Necesitas una alternativa anidada: `if a > b` … `elif b > a` … `else`.",
    faq=[
        (
            "¿Por qué programar primero en papel?",
            "Porque el problema difícil es el algoritmo, no la sintaxis. Si el algoritmo está mal en papel, estará mal en cualquier lenguaje.",
        ),
        (
            "¿O(n log n) es logarítmico?",
            "No exactamente: es «n por log n» (linealítmico). Crece más que O(n) y mucho menos que O(n²); es el coste de los buenos algoritmos de ordenación.",
        ),
    ],
    challenge=(
        "Traza",
        2,
        "Haz a mano la traza (tabla con el valor de cada variable tras cada instrucción) de: A=4, B=2, C=3; A←B; C←A; B←3; A←A*2; C←C−B.",
        "# A  B  C\n# 4  2  3\n",
        "Tras A←B, A vale 2; C←A copia ese 2. Al final: A=4, B=3, C=−1.",
    ),
    questions=[
        tq(
            "prog-01",
            "¿Qué es un algoritmo?",
            [
                "Un conjunto ordenado y finito de operaciones que resuelve un problema",
                "Cualquier programa escrito en Python",
                "Un diagrama con un inicio y varios finales",
                "Una lista de variables",
            ],
            0,
            "Además tiene entradas y salidas definidas, termina en un tiempo finito y cada paso es preciso.",
        ),
        tq(
            "prog-02",
            "¿Cuál NO es una característica de un algoritmo?",
            [
                "Puede tener pasos ambiguos si el programador los entiende",
                "Tiene un número finito de pasos",
                "Termina en un tiempo finito",
                "Puede tener varios datos de entrada y de salida",
            ],
            0,
            "Cada operación tiene que ser precisa y sin ambigüedad: el ordenador no interpreta intenciones.",
        ),
        tq(
            "prog-03",
            "¿Qué estructuras admite la programación estructurada?",
            [
                "Secuencial, alternativa e iterativa",
                "Secuencial, alternativa y saltos goto",
                "Solo bucles",
                "Clases, objetos y herencia",
            ],
            0,
            "Con esas tres se puede escribir cualquier algoritmo, sin saltos incondicionales.",
        ),
        tq(
            "prog-04",
            "En programación modular, cada función debe tener…",
            [
                "máxima cohesión y mínimo acoplamiento",
                "mínima cohesión y máximo acoplamiento",
                "acceso a todas las variables globales",
                "más de 200 líneas",
            ],
            0,
            "Cohesión: la función hace una sola cosa bien. Acoplamiento: depende lo menos posible de las demás. Así funciona como una caja negra.",
        ),
        tq(
            "prog-05",
            "¿Qué regla cumple un diagrama de flujo bien hecho?",
            [
                "Los símbolos de inicio y fin aparecen una sola vez",
                "Puede tener varios inicios",
                "El flujo va de abajo arriba",
                "Las líneas se cruzan para ahorrar espacio",
            ],
            0,
            "Se empieza arriba y se acaba abajo, el flujo va de arriba abajo y de izquierda a derecha, y los cruces se evitan con conectores.",
        ),
        tq(
            "prog-06",
            "¿Qué es PSeInt?",
            [
                "Un intérprete de pseudocódigo para estudiantes que también dibuja el diagrama de flujo",
                "Un compilador de Python",
                "Un sistema gestor de bases de datos",
                "Un IDE para Java",
            ],
            0,
            "Permite probar el algoritmo en pseudocódigo antes de pasarlo a un lenguaje real.",
        ),
        tq(
            "prog-07",
            "En pseudocódigo, ¿qué significa `C ← A`?",
            ["Asigna a C el valor de A", "Compara C con A", "C es menor que A", "Borra A"],
            0,
            "La flecha es la asignación. En Python se escribe `c = a`, y la comparación de igualdad es `==`.",
        ),
        tq(
            "prog-08",
            "Buscar un valor recorriendo una lista elemento a elemento tiene un coste…",
            ["O(n), lineal", "O(1), constante", "O(log n), logarítmico", "O(n²), cuadrático"],
            0,
            "En el peor caso hay que mirar los n elementos. Acceder por índice es O(1) y la búsqueda binaria en una lista ordenada, O(log n).",
        ),
        tq(
            "prog-09",
            "Java y Python compilan a bytecode que ejecuta una máquina virtual. Son lenguajes…",
            ["mixtos o intermedios", "compilados puros", "de bajo nivel", "ensambladores"],
            0,
            "El bytecode no depende del procesador: se gana portabilidad a cambio de algo de velocidad.",
        ),
        tq(
            "prog-10",
            "Los comentarios y docstrings del código son documentación…",
            ["interna", "externa", "de usuario", "de mantenimiento externa"],
            0,
            "La externa son los documentos aparte: diseño, manual de usuario y manual de mantenimiento.",
        ),
        tq(
            "prog-11",
            "¿Cuál es el orden del ciclo de vida clásico?",
            [
                "Análisis, diseño, codificación y pruebas, implantación, mantenimiento",
                "Codificación, análisis, diseño, mantenimiento",
                "Diseño, codificación, análisis, implantación",
                "Pruebas, análisis, codificación, diseño",
            ],
            0,
            "Del mantenimiento se puede volver al análisis para una nueva versión.",
        ),
        tq(
            "prog-12",
            "¿Qué inventó Blaise Pascal en 1642?",
            [
                "La Pascalina, una calculadora mecánica",
                "Las tarjetas perforadas",
                "La máquina de Turing",
                "El transistor",
            ],
            0,
            "Las tarjetas perforadas son de Jacquard (1802), la máquina de Turing de Alan Turing y el transistor de los laboratorios Bell (1947).",
        ),
        pq(
            "prog-13",
            "Es la traducción a Python del intercambio con variable auxiliar. " + QUE,
            """
a = 4
b = 2
c = a
a = b
b = c
print(a, b)
""",
            "2 4",
            ["4 2", "2 2", "4 4"],
            "La variable auxiliar guarda el valor de `a` antes de perderlo. Sin ella, `a = b; b = a` dejaría las dos a 2.",
        ),
        pq(
            "prog-14",
            "Traducción del pseudocódigo «mientras C <= A: Imprimir C; C ← C + 2». " + QUE,
            """
a = 7
c = 0
while c <= a:
    print(c)
    c = c + 2
""",
            "0\n2\n4\n6",
            ["0\n2\n4\n6\n8", "2\n4\n6", "0\n1\n2\n3\n4\n5\n6\n7"],
            "Tras imprimir 6, c pasa a 8, la condición 8 <= 7 es falsa y el bucle termina.",
        ),
        kq(
            "prog-15",
            "Si el usuario introduce 7, ¿qué escribe este pseudocódigo?",
            """
Algoritmo ParImpar
    Leer n
    Si (n % 2) = 0 Entonces
        Escribir "Par"
    SiNo
        Escribir "Impar"
    FinSi
FinAlgoritmo
""",
            ["Impar", "Par", "Nada", "Error"],
            0,
            "7 % 2 vale 1, distinto de 0, así que se ejecuta la rama SiNo. En pseudocódigo `=` compara; en Python sería `==`.",
        ),
    ],
    quiz=[
        tq(
            "prog-q01",
            "¿Qué tres partes tiene todo algoritmo?",
            [
                "Entrada, proceso y salida",
                "Inicio, bucle y fin",
                "Clase, objeto y método",
                "Análisis, diseño y código",
            ],
            0,
            "Es el esquema básico que se repite en cualquier programa.",
        ),
        tq(
            "prog-q02",
            "¿Existe un único algoritmo correcto para cada problema?",
            [
                "No: suele haber varios, y se elige el más adecuado",
                "Sí, siempre uno",
                "Sí, el más corto",
                "Depende del lenguaje",
            ],
            0,
            "Se evalúan las soluciones candidatas: si dan el resultado esperado, si son eficientes y qué pasa al crecer los datos.",
        ),
    ],
    sources=[APUNTES, PSEINT],
)

# ================================================================ UT2

L_UT2 = Lesson(
    slug="prog-ut2-elementos",
    title="UT2 · Elementos de un programa en Python",
    theory="""
**Python** lo creó **Guido van Rossum** (empezó en 1989); el nombre viene de los **Monty Python**. Python 3.0 (2008) rompió la compatibilidad con Python 2. Hoy lo gestiona la Python Software Foundation.

**Características:** tipado **fuerte y dinámico** (una variable puede apuntar a objetos de distinto tipo, pero no se mezclan tipos sin convertirlos); en Python **todo es un objeto**; interpretado, aunque antes **compila a bytecode** (`.pyc` en `__pycache__`) que ejecuta su máquina virtual; multiplataforma; enorme biblioteca estándar; recolector de basura; paquetes con **pip** (`pip install`, `pip install -U`, `pip uninstall`). Los **entornos virtuales** (`python -m venv ruta`) aíslan las dependencias de cada proyecto. IDE del curso: **PyCharm**.

**Sintaxis básica:**
- No hay `;` al final. Los bloques se abren con `:` y se marcan con la **indentación** (4 espacios; no mezclar tabuladores).
- Comentarios con `#`; los de varias líneas se simulan con `\"\"\"…\"\"\"`.
- Distingue mayúsculas y minúsculas. Una línea larga se parte con `\\` o dentro de paréntesis, corchetes o llaves.

**Funciones de inicio:** `print(…, end="")` (por defecto `end` es un salto de línea), `input("texto")` (**siempre devuelve una cadena**: hay que convertirla con `int()` o `float()`), `str()`, `type()`, `dir()` (lista los métodos) y `pass` (bloque vacío).

**Identificadores:** empiezan por letra o `_`, y siguen letras, dígitos o `_`. Sin `-`, `$`, `@` ni espacios. **PEP 8:** clases `MiPunto`, variables y funciones `nombre_alumno`, `guardar_datos`, constantes `PI`.

**Operadores:**
- Aritméticos: `+ - * /` (**siempre da float**), `//` (división entera), `%` (resto), `**` (potencia).
- Comparación: `== != < <= > >=`, encadenables: `5 < x < 15`.
- Lógicos `and`, `or`, `not`, con **cortocircuito**: `0 or 10` da `10`; `0 and 10` da `0`.
- Pertenencia `in`, identidad `is` (para `None`), asignación compuesta `+=`, `-=`… y morsa `:=` (Python 3.8).

**Literales:** enteros (`0b101`, `0o17`, `0x1F`, `1_000`), reales, complejos, cadenas con `'` o `"`, triples comillas, secuencias de escape (`\\n`, `\\t`), `None`, `True`/`False`.

**Cadenas:** inmutables, índices desde 0 y negativos desde el final, **rebanadas** `s[inicio:fin:paso]` (el fin no se incluye; `s[::-1]` la invierte), `+` concatena y `*` repite. Formato con **f-strings**: `f"{precio:.2f}"`.

**Variables:** nombres que apuntan a objetos. Inmutables: números, cadenas, tuplas; mutables: listas, diccionarios, conjuntos. Asignación múltiple `a, b = b, a`. No hay constantes reales: se escriben en MAYÚSCULAS por convenio.
""",
    example="""
PI = 3.14159                      # constante por convenio
radio = float("2")                # input() devolvería una cadena: se convierte
area = PI * radio ** 2
print(f"Área: {area:.2f}")

nombre = "Python"
print(nombre[0], nombre[-1], nombre[::-1])
print(7 / 2, 7 // 2, 7 % 2, 2 ** 10)
""",
    exercise="""
Escribe un programa que pida el peso (kg) y la estatura (m) y muestre el **índice de masa corporal** (peso / estatura²) con dos decimales.

Pruébalo con 70 y 1.75: debe salir 22.86.
""",
    starter='peso = float(input("Peso (kg)? "))\nestatura = float(input("Estatura (m)? "))\n\n# imc = ...\n',
    hint='`print(f"IMC: {imc:.2f}")`. Ojo: `:.2` serían dos cifras significativas, no dos decimales; hace falta `:.2f`.',
    faq=[
        (
            "¿Por qué `input()` + `input()` concatena en vez de sumar?",
            'Porque `input()` devuelve cadenas. `"2" + "3"` es `"23"`. Convierte primero: `int(input(...))`.',
        ),
        (
            "¿Python es débilmente tipado?",
            'No: es de tipado dinámico (el tipo va con el objeto, no con la variable) pero fuerte: `"3" + 4` da error en vez de convertir solo.',
        ),
    ],
    challenge=(
        "Fecha a trozos",
        2,
        "Dada una fecha como entero `ddmmaaaa` (por ejemplo 25122026), obtén día, mes y año solo con `//` y `%`.",
        "fecha = 25122026\n\n# dia = ...\n# mes = ...\n# anio = ...\n",
        "El año son los 4 últimos dígitos: `fecha % 10000`. El día: `fecha // 1000000`. El mes: `fecha // 10000 % 100`.",
    ),
    questions=[
        pq(
            "prog-16",
            QUE,
            "print(7 / 2, 7 // 2, 7 % 2, 7 ** 2)",
            "3.5 3 1 49",
            ["3 3 1 49", "3.5 3.5 1 14", "3.5 3 1 14"],
            "`/` siempre da float; `//` es la división entera, `%` el resto y `**` la potencia.",
        ),
        pq(
            "prog-17",
            QUE,
            "print(0 or 10, 0 and 10, 3 and 5)",
            "10 0 5",
            ["True False True", "10 0 3", "0 10 5"],
            "Cortocircuito: `or` devuelve el primer valor verdadero (o el último); `and` devuelve el primer valor falso (o el último).",
        ),
        pq(
            "prog-18",
            "`input()` siempre devuelve una cadena. Si el usuario escribe 5… " + QUE,
            'n = "5"   # lo que devolvería input()\nprint(n * 2, int(n) * 2)',
            "55 10",
            ["10 10", "55 55", "Error"],
            "Una cadena por 2 se repite; primero hay que convertirla con `int()`.",
        ),
        pq(
            "prog-19",
            QUE,
            'print("a", "b", end="-")\nprint("c")',
            "a b-c",
            ["a b\nc", "ab-c", "a-b-c"],
            "`print` separa los argumentos con un espacio (`sep`) y termina con `end`, que aquí es un guion en lugar del salto de línea.",
        ),
        pq(
            "prog-20",
            QUE,
            's = "Python"\nprint(s[0], s[-1], s[1:4], s[::-1])',
            "P n yth nohtyP",
            ["P n ytho nohtyP", "P o yth nohtyP", "y n yth Python"],
            "Índices desde 0, negativos desde el final; en la rebanada el fin (4) no se incluye; `[::-1]` recorre al revés.",
        ),
        pq(
            "prog-21",
            "Las cadenas son inmutables. " + QUE,
            's = "hola"\ntry:\n    s[0] = "H"\nexcept Exception as e:\n    print(type(e).__name__)',
            "TypeError",
            ["Hola", "hola", "IndexError"],
            'No se puede cambiar un carácter de una cadena. Se crea otra: `s = "H" + s[1:]`.',
        ),
        tq(
            "prog-22",
            "¿Cuál es un identificador válido en Python?",
            ["_total", "2dias", "mi-variable", "precio$"],
            0,
            "Empieza por letra o `_` y solo lleva letras, dígitos y `_`. El guion se leería como una resta.",
        ),
        tq(
            "prog-23",
            "Según PEP 8, ¿qué nombres son correctos?",
            [
                "Clase MiPunto, función guardar_datos, constante PI",
                "Clase mi_punto, función GuardarDatos, constante pi",
                "Clase MIPUNTO, función guardarDatos, constante Pi",
                "Todos valen igual",
            ],
            0,
            "Clases en CamelCase, funciones y variables en snake_case, constantes en MAYÚSCULAS.",
        ),
        pq(
            "prog-24",
            QUE,
            "print(type(6 / 3).__name__, type(6 // 3).__name__)",
            "float int",
            ["int int", "float float", "int float"],
            "Aunque la división sea exacta, `/` devuelve float (2.0). `//` entre enteros devuelve int.",
        ),
        pq(
            "prog-25",
            QUE,
            'precio = 3.14159\nprint(f"{precio:.2f} €")',
            "3.14 €",
            ["3.1 €", "3.14159 €", "{precio:.2f} €"],
            "`:.2f` redondea a dos decimales. Sin la `f`, `:.2` serían dos cifras significativas (3.1).",
        ),
        pq(
            "prog-26",
            QUE,
            "a, b = 1, 2\na, b = b, a\nprint(a, b)",
            "2 1",
            ["1 2", "2 2", "Error"],
            "Python evalúa primero el lado derecho (la tupla `b, a`) y luego asigna: intercambio sin variable auxiliar.",
        ),
        pq(
            "prog-27",
            QUE,
            "print(0b101, 0x1F, 1_000)",
            "5 31 1000",
            ["101 1F 1_000", "5 15 1000", "Error"],
            "`0b` es binario, `0x` hexadecimal y `_` solo separa dígitos para leerlos mejor.",
        ),
        tq(
            "prog-28",
            "¿Quién creó Python y de dónde viene su nombre?",
            [
                "Guido van Rossum; de los Monty Python",
                "James Gosling; de una serpiente",
                "Dennis Ritchie; de la mitología griega",
                "Guido van Rossum; de una serpiente",
            ],
            0,
            "Empezó en las navidades de 1989. Python 3.0 salió en 2008.",
        ),
        tq(
            "prog-29",
            "¿Qué significa que Python tiene tipado dinámico?",
            [
                "Que una misma variable puede apuntar a objetos de distinto tipo durante el programa",
                'Que convierte solo `"3" + 4` en 7',
                "Que no tiene tipos",
                "Que hay que declarar el tipo de cada variable",
            ],
            0,
            'El tipo va con el objeto. Además es fuerte: `"3" + 4` da TypeError en lugar de convertir solo.',
        ),
        tq(
            "prog-30",
            "¿Dónde guarda Python el bytecode compilado de los módulos?",
            [
                "En ficheros .pyc dentro de __pycache__",
                "En un .exe junto al programa",
                "En la memoria, sin guardarlo nunca",
                "En un .class",
            ],
            0,
            "Python se considera interpretado, pero antes compila a bytecode que ejecuta su máquina virtual. Los `.class` son de Java.",
        ),
        fq(
            "prog-31",
            "Completa con el operador que da la división entera.",
            "print(10 ___ 3)",
            ["//"],
            "3",
            "`10 / 3` daría 3.3333333333333335; `//` descarta los decimales.",
        ),
    ],
    quiz=[
        tq(
            "prog-q03",
            "¿Qué devuelve siempre `input()`?",
            ["Una cadena (str)", "Un entero", "El tipo que escriba el usuario", "None"],
            0,
            "Por eso casi siempre se escribe `int(input(...))` o `float(input(...))`.",
        ),
        tq(
            "prog-q04",
            "¿Cómo se marca un bloque en Python?",
            ["Con `:` y la indentación", "Con llaves {}", "Con begin y end", "Con punto y coma"],
            0,
            "La indentación forma parte de la sintaxis; PEP 8 pide 4 espacios.",
        ),
    ],
    sources=[APUNTES, TUTORIAL, PEP8],
)

# ================================================================ UT3

L_UT3_CONTROL = Lesson(
    slug="prog-ut3-control",
    title="UT3 · Estructuras de control y depuración",
    theory="""
Máxima del curso: **el código tiene que ser fácil de leer, no corto**, y se empieza siempre en papel.

**Condiciones:** expresiones que dan `True` o `False` con operadores de comparación, lógicos (`and`, `or` con cortocircuito, `not`), pertenencia (`in`) e identidad (`is`). Se pueden encadenar: `5 < x < 15`.

**Alternativas:** `if` / `elif` / `else` (solo el `if` es obligatorio). Condicional en una línea: `valor_si if condicion else valor_no`. Desde **Python 3.10** existe `match`/`case` (con `case _` como caso por defecto y `|` para varias opciones).

**range(inicio, fin, paso):** el **fin no se incluye**. `range(5)` → 0…4; `range(5, 10)` → 5…9; `range(0, 10, 3)` → 0, 3, 6, 9; `range(10, 0, -1)` cuenta hacia atrás.

**Bucles:**
- `for` recorre cualquier secuencia (cadena, lista, range…).
- `while` repite mientras se cumpla la condición: hay que cambiarla dentro, o será un **bucle infinito**.
- Los dos admiten `else`, que se ejecuta si el bucle termina **sin `break`** (útil para búsquedas, como comprobar si un número es primo).
- `break` sale del bucle; `continue` pasa a la siguiente vuelta. Python no tiene `goto`.
- Morsa en bucles: `while (linea := input()) != "FIN":`.

**Depuración (PyCharm):** se lanza con **Debug** en lugar de Run. **Punto de ruptura** (Ctrl+F8) en una línea ejecutable; **Step Over (F8)** ejecuta la línea sin entrar en las funciones; **Step Into (F7)** entra en ellas; **Step Out (Mayús+F8)** sale; se inspeccionan variables y se evalúan expresiones. Probar = inspeccionar el código + baterías de pruebas + pruebas unitarias, y cada corrección puede introducir errores nuevos.

**Docstrings (PEP 257):** cadena literal que va como **primera instrucción** de un módulo, clase o función. Primera línea: un resumen terminado en punto. Se consulta con `funcion.__doc__` o `help(funcion)`.

**Estilo (PEP 8):** 4 espacios, líneas de 79 caracteres como máximo, espacios alrededor de los operadores, dos líneas en blanco entre funciones de primer nivel.
""",
    example="""
def es_primo(n):
    \"\"\"Devuelve True si n es primo.\"\"\"
    for divisor in range(2, n):
        if n % divisor == 0:
            return False
    return n > 1

for numero in range(1, 20):
    if not es_primo(numero):
        continue            # los no primos se saltan
    print(numero, end=" ")
print()

nota = 7
match nota:
    case 9 | 10:
        print("Sobresaliente")
    case 7 | 8:
        print("Notable")
    case _:
        print("Otra nota")
""",
    exercise="""
Escribe un programa que pida números hasta que se introduzca un 0 y, al final, diga cuántos positivos y cuántos negativos había.

Usa `while` con el operador morsa `:=`.
""",
    starter='positivos = negativos = 0\nwhile (numero := int(input("Número? "))) != 0:\n    # ...\n    pass\nprint(positivos, negativos)\n',
    hint="Dentro del bucle: `if numero > 0: positivos += 1` y `elif numero < 0: negativos += 1`. El 0 no se cuenta: corta el bucle.",
    faq=[
        (
            "¿Para qué sirve el `else` de un bucle?",
            "Se ejecuta solo si el bucle acaba sin `break`. En una búsqueda: si el `for` termina sin encontrar (sin `break`), el `else` dice «no encontrado».",
        ),
        (
            "¿Puedo modificar la lista que recorro con for?",
            "Mejor no: al borrar o insertar elementos, el bucle puede saltarse algunos. Recorre una copia (`for x in lista[:]`) o crea una lista nueva.",
        ),
    ],
    challenge=(
        "Pirámide",
        2,
        "Pide un número de filas y dibuja una pirámide de asteriscos centrada: 1, 3, 5… asteriscos por fila.",
        "filas = 4\nfor fila in range(filas):\n    # espacios + asteriscos\n    pass\n",
        'En la fila i (desde 0) hay `filas - i - 1` espacios y `2 * i + 1` asteriscos: `print(" " * espacios + "*" * asteriscos)`.',
    ),
    questions=[
        pq(
            "prog-32",
            QUE,
            "print(list(range(0, 10, 3)))",
            "[0, 3, 6, 9]",
            ["[0, 3, 6, 9, 10]", "[3, 6, 9]", "[0, 3, 6]"],
            "Empieza en 0, avanza de 3 en 3 y se detiene antes de 10.",
        ),
        pq(
            "prog-33",
            QUE,
            "print(sum(range(5, 10)))",
            "35",
            ["45", "50", "30"],
            "5 + 6 + 7 + 8 + 9 = 35: el 10 no se incluye.",
        ),
        pq(
            "prog-34",
            "El `else` del `for` se ejecuta si no hubo `break`. " + QUE,
            """
n = 9
for divisor in range(2, n):
    if n % divisor == 0:
        print(n, "no es primo")
        break
else:
    print(n, "es primo")
""",
            "9 no es primo",
            ["9 es primo", "9 no es primo\n9 es primo", "Error"],
            "Con divisor 3 se cumple la condición, se imprime y `break` sale del bucle: el `else` ya no se ejecuta.",
        ),
        pq(
            "prog-35",
            QUE,
            """
pares = []
for i in range(6):
    if i % 2:
        continue
    pares.append(i)
print(pares)
""",
            "[0, 2, 4]",
            ["[1, 3, 5]", "[0, 2, 4, 6]", "[]"],
            "`i % 2` vale 1 (verdadero) para los impares: `continue` los salta antes de añadirlos.",
        ),
        pq(
            "prog-36",
            QUE,
            """
n = 10
pasos = 0
while n > 1:
    n //= 2
    pasos += 1
print(pasos)
""",
            "3",
            ["4", "5", "10"],
            "10 → 5 → 2 → 1: tres vueltas. Al llegar a 1, la condición es falsa.",
        ),
        pq(
            "prog-37",
            QUE,
            "x = 20\nprint(5 < x < 15, 5 < x)",
            "False True",
            ["True True", "True False", "Error"],
            "`5 < x < 15` equivale a `5 < x and x < 15`: 20 no es menor que 15.",
        ),
        pq(
            "prog-38",
            QUE,
            'edad = 17\nprint("mayor" if edad >= 18 else "menor")',
            "menor",
            ["mayor", "True", "Error"],
            "Es el condicional en una línea de Python: `valor_si if condición else valor_no`.",
        ),
        pq(
            "prog-39",
            "Condición de año bisiesto de los apuntes. " + QUE,
            """
anio = 1900
if not anio % 4 and (anio % 100 or not anio % 400):
    print("Bisiesto")
else:
    print("No bisiesto")
""",
            "No bisiesto",
            ["Bisiesto", "Error", "True"],
            "1900 es múltiplo de 4 y de 100, pero no de 400: no es bisiesto. `not anio % 4` es verdadero cuando el resto es 0.",
        ),
        pq(
            "prog-40",
            "Necesita Python 3.10 o posterior. " + QUE,
            """
dia = 6
match dia:
    case 6 | 7:
        print("Fin de semana")
    case _:
        print("Laborable")
""",
            "Fin de semana",
            ["Laborable", "6", "Error"],
            "`|` junta varios patrones en un `case`; `case _` recoge todo lo demás.",
        ),
        pq(
            "prog-41",
            "Simulamos lo que teclearía el usuario. " + QUE,
            """
teclado = iter(["ho", "la", "FIN", "extra"])
resultado = ""
while (linea := next(teclado)) != "FIN":
    resultado += linea
print(resultado)
""",
            "hola",
            ["holaFIN", "holaFINextra", "ho"],
            'La morsa asigna y compara a la vez. Al leer "FIN", el bucle termina y "extra" ni se lee.',
        ),
        tq(
            "prog-42",
            "En el depurador de PyCharm, ¿qué diferencia hay entre Step Over (F8) y Step Into (F7)?",
            [
                "Step Over ejecuta la línea sin entrar en las funciones; Step Into entra en ellas",
                "Son lo mismo",
                "Step Over salta hasta el final del programa",
                "Step Into borra el punto de ruptura",
            ],
            0,
            "Step Out (Mayús+F8) termina la función actual y vuelve a quien la llamó.",
        ),
        tq(
            "prog-43",
            "¿Qué es un docstring?",
            [
                "Una cadena literal que es la primera instrucción de un módulo, clase o función y la documenta",
                "Cualquier comentario con #",
                "Un fichero de documentación externa",
                "Una cadena con formato f",
            ],
            0,
            "Se lee con `__doc__` o `help()`. PEP 257 pide una primera línea de resumen acabada en punto.",
        ),
        tq(
            "prog-44",
            "Según PEP 8, ¿qué es correcto?",
            [
                "Indentar con 4 espacios y no pasar de 79 caracteres por línea",
                "Indentar con tabuladores y espacios mezclados",
                "Escribir todo en una sola línea",
                "Nombrar las funciones en MAYÚSCULAS",
            ],
            0,
            "Son convenciones de estilo: el código se lee muchas más veces de las que se escribe.",
        ),
        oq(
            "prog-45",
            "Ordena las líneas para sumar los pares del 1 al 10 (debe mostrar 30).",
            [
                "total = 0",
                "for n in range(1, 11):",
                "    if n % 2 == 0:",
                "        total += n",
                "print(total)",
            ],
            "30",
            "Inicializar, recorrer, filtrar, acumular y mostrar al final (fuera del bucle).",
        ),
        bq(
            "prog-46",
            """
suma = 0
for i in range(1, 5):
    suma += i
print(suma)
""",
            1,
            "for i in range(1, 6):",
            "15",
            "Para sumar del 1 al 5 el fin del range debe ser 6: el fin no se incluye. Con `range(1, 5)` suma 1 + 2 + 3 + 4 = 10.",
        ),
    ],
    quiz=[
        tq(
            "prog-q05",
            "¿Qué hace `continue` dentro de un bucle?",
            [
                "Salta a la siguiente vuelta",
                "Termina el bucle",
                "Termina el programa",
                "Repite la vuelta actual",
            ],
            0,
            "`break` es el que termina el bucle.",
        ),
        tq(
            "prog-q06",
            "¿Qué valores da `range(3)`?",
            ["0, 1, 2", "1, 2, 3", "0, 1, 2, 3", "3"],
            0,
            "Empieza en 0 y el fin no se incluye.",
        ),
    ],
    sources=[APUNTES, TUTORIAL, PEP8],
)

L_UT3_FUNCIONES = Lesson(
    slug="prog-ut3-funciones",
    title="UT3 · Programación modular y funciones",
    theory="""
**Programación modular:** descomponer el problema una y otra vez en subproblemas más simples, hasta que cada acción sea evidente. Cada subproblema se resuelve con una función.

**Función y procedimiento:** una función recibe parámetros, hace un proceso y **devuelve un resultado**; un procedimiento no devuelve nada. En Python no hay procedimientos: una función sin `return` devuelve **`None`**. Las funciones son objetos.

- Se definen con `def nombre(parametros):` y se llaman con `nombre(argumentos)`.
- `return a, b` devuelve **una tupla** con los dos valores.
- Recomendaciones del curso: funciones cortas (unas 25-30 líneas), sacar a funciones el código repetido, devolver uno o dos valores y, si se puede, un único `return` al final.

**Ámbito de las variables:**
- **local:** creada dentro de la función; desaparece al terminar.
- **global:** creada en el programa principal. Se puede **leer** desde una función, pero para **asignarla** hace falta `global nombre`.
- **nonlocal:** en una función dentro de otra, permite modificar la variable de la función que la contiene.
- Si una función asigna una variable sin declararla `global`, Python la trata como local en toda la función: usarla antes de asignarla da **UnboundLocalError**.

**Parámetros:** no llevan tipo. Los apuntes dicen que «en Python todos los parámetros son de entrada», y es cierto que **reasignar** un parámetro no cambia nada fuera. Pero si el argumento es **mutable** (una lista, un diccionario) y la función lo **modifica** (`append`, `lista[0] = …`), el cambio sí se ve fuera: se pasa una referencia al mismo objeto. Si no quieres eso, trabaja con una copia (`lista.copy()`).
""",
    example="""
def area_rectangulo(base, altura):
    \"\"\"Devuelve el área de un rectángulo.\"\"\"
    return base * altura


def min_max(valores):
    \"\"\"Devuelve el mínimo y el máximo de una lista.\"\"\"
    return min(valores), max(valores)


print(area_rectangulo(3, 4))
minimo, maximo = min_max([7, 2, 9])
print(minimo, maximo)

contador = 0

def incrementar():
    global contador
    contador += 1

incrementar()
incrementar()
print(contador)
""",
    exercise="""
Descompón el juego del **ahorcado** en funciones:

1. `elegir_palabra()` devuelve una palabra al azar de una lista;
2. `mostrar(palabra, letras)` devuelve la palabra con `_` en las letras no acertadas;
3. `ha_ganado(palabra, letras)` devuelve True o False.

Después escribe el programa principal que las use.
""",
    starter='import random\n\nPALABRAS = ["python", "daw", "variable"]\n\n\ndef elegir_palabra():\n    pass\n\n\ndef mostrar(palabra, letras):\n    pass\n',
    hint='`mostrar` puede construir la cadena con `" ".join(c if c in letras else "_" for c in palabra)`.',
    faq=[
        (
            "¿Por qué evitar las variables globales?",
            "Porque cualquier función puede cambiarlas y es difícil saber quién lo hizo. Pasa los datos como parámetros y devuelve resultados.",
        ),
        (
            "¿Qué devuelve una función sin return?",
            '`None`. Por eso `x = print("hola")` deja `x` a None.',
        ),
    ],
    challenge=(
        "Valor absoluto",
        1,
        "Escribe `absoluto(n)` sin usar `abs()`, con un único `return`, y pruébala con -5, 0 y 3.",
        "def absoluto(n):\n    pass\n",
        "`return n if n >= 0 else -n`.",
    ),
    questions=[
        pq(
            "prog-47",
            QUE,
            'def saluda():\n    print("hola")\n\nr = saluda()\nprint(r)',
            "hola\nNone",
            ["hola\nhola", "None", "hola"],
            "La función imprime, pero no tiene `return`: devuelve None.",
        ),
        pq(
            "prog-48",
            QUE,
            "def f():\n    return 1, 2\n\nr = f()\nprint(type(r).__name__, r)",
            "tuple (1, 2)",
            ["int 1", "list [1, 2]", "Error"],
            "Python no devuelve dos valores sueltos: los empaqueta en una tupla. Se desempaqueta con `a, b = f()`.",
        ),
        pq(
            "prog-49",
            "Ejemplo de ámbitos de los apuntes. " + QUE,
            """
g = 5

def mi_func():
    global g
    g = 6
    b = 6

    def interna():
        nonlocal b
        global g
        b = 7
        g = 8

    interna()
    print(b, g)

mi_func()
print(g)
""",
            "7 8\n8",
            ["6 6\n5", "7 8\n5", "6 8\n8"],
            "`nonlocal b` modifica la `b` de `mi_func`; `global g` modifica la `g` del programa principal.",
        ),
        pq(
            "prog-50",
            QUE,
            "g = 5\n\ndef f():\n    g = 6\n\nf()\nprint(g)",
            "5",
            ["6", "Error", "None"],
            "Sin `global`, la asignación crea una variable local `g` que desaparece al terminar la función.",
        ),
        pq(
            "prog-51",
            QUE,
            """
contador = 0

def incrementar():
    contador += 1

try:
    incrementar()
except Exception as e:
    print(type(e).__name__)
""",
            "UnboundLocalError",
            ["1", "0", "NameError"],
            "Como la función asigna `contador`, es local en toda la función, y `+=` necesita leerla antes de tener valor. Falta `global contador`.",
        ),
        pq(
            "prog-52",
            "Una lista es mutable. " + QUE,
            "def anadir(lista):\n    lista.append(4)\n\nnumeros = [1]\nanadir(numeros)\nprint(numeros)",
            "[1, 4]",
            ["[1]", "[4]", "None"],
            "La función recibe una referencia al mismo objeto y lo modifica: el cambio se ve fuera. Para evitarlo se trabaja con `lista.copy()`.",
        ),
        pq(
            "prog-53",
            QUE,
            "def cambiar(lista):\n    lista = [9]\n\nnumeros = [1]\ncambiar(numeros)\nprint(numeros)",
            "[1]",
            ["[9]", "[1, 9]", "Error"],
            "Reasignar el parámetro solo cambia a qué apunta el nombre local: el objeto de fuera no se toca. Por eso los apuntes dicen que los parámetros son de entrada.",
        ),
        tq(
            "prog-54",
            "Según los apuntes, ¿qué diferencia hay entre función y procedimiento en Python?",
            [
                "No hay procedimientos: una función sin return devuelve None",
                "Los procedimientos se definen con proc",
                "Las funciones no pueden recibir parámetros",
                "Los procedimientos devuelven siempre 0",
            ],
            0,
            "En otros lenguajes (Pascal, por ejemplo) sí se distinguen.",
        ),
        tq(
            "prog-55",
            "¿Qué es la programación modular?",
            [
                "Descomponer el problema en subproblemas más simples, cada uno resuelto por una función",
                "Escribir todo el programa en un único bloque",
                "Usar solo clases",
                "Programar sin funciones",
            ],
            0,
            "Se descompone hasta que cada acción sea inmediata de programar.",
        ),
        fq(
            "prog-56",
            "Completa la función para que devuelva el cuadrado.",
            "def cuadrado(n):\n    ___ n * n\n\nprint(cuadrado(4))",
            ["return"],
            "16",
            "Sin `return`, la función devolvería None y se imprimiría None.",
        ),
    ],
    quiz=[
        tq(
            "prog-q07",
            "¿Qué palabra permite asignar una variable global dentro de una función?",
            ["global", "nonlocal", "static", "public"],
            0,
            "`nonlocal` es para la variable de la función exterior, en funciones anidadas.",
        ),
        tq(
            "prog-q08",
            "`return a, b` devuelve…",
            ["una tupla (a, b)", "solo a", "una lista [a, b]", "un error"],
            0,
            "Se desempaqueta con `x, y = funcion()`.",
        ),
    ],
    sources=[APUNTES, TUTORIAL],
)

# ================================================================ UT4

L_UT4 = Lesson(
    slug="prog-ut4-poo",
    title="UT4 · Programación orientada a objetos",
    theory="""
La **POO** organiza el código en **clases**, a partir de las cuales se crean **objetos** que se relacionan entre sí mediante **mensajes** (llamadas a métodos). Nació con **Simula 67** (Oslo) y **Smalltalk** (Xerox PARC), y se popularizó en los 80 con C++ y las interfaces gráficas.

**Conceptos:**
- **Clase:** el molde. Describe los **atributos** (datos) y los **métodos** (comportamiento) comunes a un grupo de objetos.
- **Objeto:** una **instancia** concreta de una clase. Su **estado** es el valor de sus atributos en cada momento.
- **Constructor:** se ejecuta al crear el objeto para inicializarlo (en Python, `__init__`). **Destructor:** lo último que se ejecuta, para liberar recursos.
- **Visibilidad en UML:** `+` pública, `-` privada, `#` protegida (la clase y sus hijas). La parte pública es la **interfaz** de la clase.

**Propiedades de la POO:**
- **Abstracción:** quedarse con lo relevante e ignorar lo demás. Perro, Gato y Loro se generalizan en Animal.
- **Encapsulación:** reunir en una estructura los datos y las operaciones sobre esos datos. **Ocultación:** proteger los datos internos y exponer solo la interfaz.
- **Herencia:** una clase reutiliza lo declarado en otra. **Simple** (un padre, como en Java) o **múltiple** (varios, como en Python).
- **Polimorfismo:** la misma llamada da resultados distintos según la clase del objeto; se consigue **sobrescribiendo** los métodos heredados, y se resuelve en ejecución (enlace dinámico).
- **Sobrecarga:** varios métodos con el mismo nombre y distinta firma. En Java o C++ se resuelve al compilar. **Python no la tiene**: un segundo `def` con el mismo nombre sustituye al primero (se simula con parámetros por defecto o `*args`).

**Relaciones entre clases:**
- **Asociación:** una clase usa a otra (un Profesor imparte un Módulo).
- **Agregación:** una clase forma parte de otra, **pero no de forma exclusiva**; la parte puede existir por su cuenta (un Punto que usan un Polígono y un Círculo).
- **Composición:** agregación **exclusiva**; las partes no existen sin el todo (los Capítulos de una Temporada).

**Principios SOLID (Robert C. Martin):** responsabilidad única, **abierto/cerrado** (abierto a la extensión, cerrado a la modificación), sustitución de Liskov, segregación de interfaces e inversión de dependencias.

**Ventajas:** reutilización, mantenimiento y aislamiento de errores. **Inconvenientes:** cuesta cambiar la forma de pensar y no compensa en tareas muy simples.
""",
    example="""
class Punto:
    def __init__(self):
        self.x = 0
        self.y = 0


p1 = Punto()
p1.x = 2
p2 = p1            # p2 y p1 son el MISMO objeto (alias)
p2.x = 3
print(p1.x)        # 3
p2 = Punto()       # ahora p2 es otro objeto
p2.x = 4
print(p1.x, p2.x)  # 3 4
""",
    exercise="""
Dibuja el **diagrama de clases UML** de una plataforma de series:

- una Serie tiene varias Temporadas y cada Temporada varios Capítulos;
- de cada Actor interesa su nombre, y un actor puede salir en muchas series.

Indica qué relaciones son composición, agregación o asociación, y la visibilidad de los atributos.
""",
    starter="# Serie ◆── Temporada ◆── Capitulo   (composición)\n# Serie ──── Actor                     (¿...?)\n",
    hint="Un capítulo no existe sin su temporada (composición). Un actor existe aunque se borre la serie: asociación (o agregación).",
    faq=[
        (
            "¿Clase y objeto no son lo mismo?",
            "No: la clase es la definición (Coche) y el objeto, cada coche concreto que creas con ella. De una clase salen muchos objetos.",
        ),
        (
            "¿Sobrecarga y sobrescritura son lo mismo?",
            "No. Sobrecarga: mismo nombre y distinta firma en la misma clase. Sobrescritura: la clase hija redefine un método heredado con la misma firma; es la base del polimorfismo.",
        ),
    ],
    challenge=(
        "Hospital",
        3,
        "Diseña en UML: un Hospital tiene Plantas (composición); en cada planta hay Habitaciones; los Médicos (que existen fuera del hospital) atienden a Pacientes. Marca multiplicidades.",
        "# Hospital 1 ◆── * Planta\n# ...\n",
        "Pregúntate en cada relación: ¿la parte puede existir sin el todo? Si no, es composición.",
    ),
    questions=[
        tq(
            "prog-57",
            "¿Qué es una clase?",
            [
                "El molde que define los atributos y métodos de un grupo de objetos",
                "Un objeto concreto",
                "Una variable global",
                "Una función sin parámetros",
            ],
            0,
            "Los objetos son las instancias concretas creadas a partir de ese molde.",
        ),
        tq(
            "prog-58",
            "¿Qué es el estado de un objeto?",
            [
                "El valor de todos sus atributos en un momento dado",
                "Su nombre de clase",
                "La lista de sus métodos",
                "Si está en memoria o no",
            ],
            0,
            "Dos objetos de la misma clase tienen los mismos atributos pero, normalmente, distinto estado.",
        ),
        tq(
            "prog-59",
            "En un diagrama de clases UML, ¿qué indican `+`, `-` y `#`?",
            [
                "Pública, privada y protegida",
                "Suma, resta y comentario",
                "Estática, final y abstracta",
                "Constructor, destructor y método",
            ],
            0,
            "Protegida: accesible desde la clase y sus herederas.",
        ),
        tq(
            "prog-60",
            "¿Qué es la encapsulación?",
            [
                "Reunir en una única estructura los datos y las operaciones sobre esos datos",
                "Ignorar las características que no importan",
                "Heredar de varias clases",
                "Tener varios métodos con el mismo nombre",
            ],
            0,
            "Ignorar lo que no importa es la abstracción. Proteger los datos internos es la ocultación.",
        ),
        tq(
            "prog-61",
            "Generalizar Perro, Gato y Loro en una clase Animal con lo que comparten es un ejemplo de…",
            ["abstracción", "sobrecarga", "composición", "destrucción"],
            0,
            "Nos quedamos con lo relevante (nombre, edad, emitir sonido) e ignoramos los detalles de cada especie.",
        ),
        tq(
            "prog-62",
            "Un Capítulo solo existe dentro de su Temporada y pertenece a una sola. ¿Qué relación es?",
            ["Composición", "Agregación", "Asociación simple", "Herencia"],
            0,
            "Las partes pertenecen de forma exclusiva y no existen sin el todo: si se borra la temporada, se borran sus capítulos.",
        ),
        tq(
            "prog-63",
            "Un Punto lo usan a la vez un Polígono y un Círculo, y existe por su cuenta. ¿Qué relación es?",
            ["Agregación", "Composición", "Herencia", "Sobrecarga"],
            0,
            "Forma parte de otras clases, pero no de forma exclusiva.",
        ),
        tq(
            "prog-64",
            "¿Qué tipo de herencia tiene Python?",
            [
                "Múltiple: una clase puede tener varios padres",
                "Solo simple, como las clases de Java",
                "No tiene herencia",
                "Solo mediante interfaces",
            ],
            0,
            "`class Hija(Padre1, Padre2):`. Java solo permite un padre (y varias interfaces).",
        ),
        pq(
            "prog-65",
            "Python no tiene sobrecarga. " + QUE,
            """
def area(lado):
    return lado * lado

def area(base, altura):
    return base * altura

try:
    print(area(3))
except TypeError:
    print("TypeError")
""",
            "TypeError",
            ["9", "3", "None"],
            "El segundo `def` sustituye al primero: ya solo existe `area(base, altura)`, y falta un argumento. Se simula con parámetros por defecto: `def area(base, altura=None)`.",
        ),
        tq(
            "prog-66",
            "¿Cuál fue el primer lenguaje orientado a objetos?",
            ["Simula 67", "Java", "Python", "C"],
            0,
            "Después llegó Smalltalk (Xerox PARC). La POO se popularizó en los 80 con C++.",
        ),
        tq(
            "prog-67",
            "¿Qué dice el principio abierto/cerrado?",
            [
                "Una clase debe estar abierta a la extensión y cerrada a la modificación",
                "Todos los atributos deben ser públicos",
                "Una clase solo puede tener un método",
                "Hay que cerrar los ficheros al terminar",
            ],
            0,
            "Es la «O» de SOLID: se añade funcionalidad heredando o componiendo, sin tocar el código que ya funciona.",
        ),
        pq(
            "prog-68",
            "Ejemplo de los apuntes: dos variables pueden apuntar al mismo objeto. " + QUE,
            """
class Punto:
    def __init__(self):
        self.x = 0

p1 = Punto()
p1.x = 2
p2 = p1
p2.x = 3
print(p1.x)
p2 = Punto()
p2.x = 4
print(p1.x, p2.x)
""",
            "3\n3 4",
            ["2\n2 4", "3\n4 4", "2\n3 4"],
            "`p2 = p1` no copia: crea un alias del mismo objeto. `p2 = Punto()` crea otro objeto distinto.",
        ),
        tq(
            "prog-69",
            "¿Qué es el polimorfismo?",
            [
                "Que la misma llamada a un método dé resultados distintos según la clase del objeto",
                "Tener varios constructores",
                "Copiar un objeto",
                "Ocultar los atributos",
            ],
            0,
            "Se consigue sobrescribiendo en cada clase hija un método heredado: `animal.hablar()` ladra o maúlla según el objeto.",
        ),
    ],
    quiz=[
        tq(
            "prog-q09",
            "¿Qué es un objeto?",
            [
                "Una instancia de una clase",
                "El molde de una clase",
                "Un tipo de bucle",
                "Un módulo",
            ],
            0,
            "Se crea llamando a la clase: `p = Punto()`.",
        ),
        tq(
            "prog-q10",
            "¿Qué método inicializa los objetos en Python?",
            ["__init__", "El que se llama como la clase", "main", "__del__"],
            0,
            "En Java el constructor se llama como la clase; en Python es `__init__`. `__del__` es el destructor.",
        ),
    ],
    sources=[APUNTES, TUTORIAL],
)

# ================================================================ UT5

L_UT5_CLASES = Lesson(
    slug="prog-ut5-clases",
    title="UT5 · Clases, métodos y parámetros en Python",
    theory="""
**Definir una clase:** `class NombreClase:` y dentro sus métodos con `def`. El primer parámetro de cada método es **`self`**, una referencia al objeto actual (el `this` de Java); Python lo pasa solo. Los atributos se crean en **`__init__`** (el inicializador): `self.nombre = nombre`.

- **Atributos de instancia:** cada objeto tiene los suyos (`self.x`).
- **Atributos de clase:** se definen en el cuerpo de la clase y los comparten todos los objetos (`IVA = 21`). Ojo: `objeto.IVA = 10` no cambia el de la clase, **crea un atributo de instancia** que lo oculta.

**Visibilidad:** en Python todo es público. `_nombre` indica «no lo toques desde fuera» (convenio; el curso usa esta forma). `__nombre` activa el *name mangling*: desde fuera pasa a llamarse `_Clase__nombre`.

**Propiedades:** atributos que ejecutan código al leerlos o asignarlos (los getters y setters de otros lenguajes). Con `@property` para leer y `@nombre.setter` para asignar y validar. Sin setter, la propiedad es de solo lectura.

**Métodos especiales:** `__str__` (lo que muestra `print(objeto)`), `__repr__`, `__del__` (lo llama el recolector de basura; no está garantizado cuándo).

**Parámetros:**
- **Por defecto:** `def f(a, b=0)`. Van detrás de los obligatorios y **se evalúan una sola vez, al definir la función**. Por eso nunca se usa una lista como valor por defecto: se comparte entre llamadas. Se usa `None`.
- **Por nombre:** `resta(b=2, a=10)`.
- `*args` agrupa los argumentos posicionales sobrantes en una **tupla**; `**kwargs` agrupa los nombrados en un **diccionario**.
- `/` marca los parámetros solo posicionales y `*`, los solo por nombre: `def f(a, /, b, *, c)`.
- **Sugerencias de tipo:** `def doble(n: int) -> int:`. Documentan, pero **no obligan** ni convierten nada.
- **Lambda:** función anónima de una expresión: `lambda x: x + n`. Útil con `sorted`, `map` y `filter`.

Estilo de los apuntes: clases en CamelCase con sustantivos, métodos en snake_case que empiezan por verbo, y validar los datos en el constructor.
""",
    example="""
class Articulo:
    IVA = 21                                   # atributo de clase

    def __init__(self, nombre, precio=0):
        self.nombre = nombre
        self._precio = 0
        self.precio = precio                   # pasa por el setter

    @property
    def precio(self):
        return self._precio

    @precio.setter
    def precio(self, valor):
        if valor < 0:
            raise ValueError("El precio no puede ser negativo")
        self._precio = valor

    def get_pvp(self):
        return self.precio * (1 + Articulo.IVA / 100)

    def __str__(self):
        return f"{self.nombre}: {self.get_pvp():.2f} €"


teclado = Articulo("Teclado", 20)
print(teclado)
""",
    exercise="""
Crea la clase `Persona` con `nombre` y `edad`, y los métodos:

- `es_mayor_de_edad()` → True si tiene 18 o más;
- `es_jubilado()` → True si tiene 65 o más;
- `diferencia_edad(otra)` → los años de diferencia con otra persona (siempre positivos).

Valida en el constructor que la edad no sea negativa.
""",
    starter="class Persona:\n    def __init__(self, nombre, edad):\n        pass\n",
    hint="`diferencia_edad` es `abs(self.edad - otra.edad)`. Para validar: `if edad < 0: raise ValueError(...)`.",
    faq=[
        (
            "¿Uso `_` o `__` para lo privado?",
            "El curso recomienda un solo `_`: indica que es interno. `__` cambia el nombre (name mangling) y complica la herencia; no impide el acceso.",
        ),
        (
            "¿Por qué no `def f(lista=[])`?",
            "Porque esa lista se crea una vez al definir la función y se comparte entre todas las llamadas. Usa `lista=None` y dentro `if lista is None: lista = []`.",
        ),
    ],
    challenge=(
        "Rectángulo",
        2,
        "Clase `Rectangulo` definida por dos esquinas (x1, y1) y (x2, y2), con propiedades de solo lectura `ancho` y `alto` y métodos `area()` y `perimetro()`.",
        "class Rectangulo:\n    def __init__(self, x1, y1, x2, y2):\n        pass\n",
        "`ancho` es `abs(self.x2 - self.x1)`, como `@property` sin setter.",
    ),
    questions=[
        pq(
            "prog-70",
            QUE,
            """
class Persona:
    def __init__(self, nombre):
        self.nombre = nombre

    def saludar(self):
        return f"Hola, soy {self.nombre}"

p = Persona("Ana")
print(p.saludar())
""",
            "Hola, soy Ana",
            ["Hola, soy nombre", "Hola, soy self.nombre", "Error"],
            '`self` es el propio objeto `p`: `self.nombre` vale "Ana". Al llamar `p.saludar()`, Python pasa `p` como `self`.',
        ),
        pq(
            "prog-71",
            QUE,
            """
class Cuenta:
    def __init__(self):
        self.__saldo = 100

c = Cuenta()
print(c._Cuenta__saldo)
try:
    print(c.__saldo)
except AttributeError:
    print("AttributeError")
""",
            "100\nAttributeError",
            ["100\n100", "AttributeError\nAttributeError", "Error"],
            "El doble subrayado cambia el nombre a `_Cuenta__saldo` (name mangling). Sigue siendo accesible: no es privado de verdad.",
        ),
        pq(
            "prog-72",
            QUE,
            """
class Celsius:
    def __init__(self, grados):
        self.grados = grados

    @property
    def grados(self):
        return self._grados

    @grados.setter
    def grados(self, valor):
        if valor < -273.15:
            raise ValueError("Imposible")
        self._grados = valor

t = Celsius(25)
print(t.grados * 1.8 + 32)
try:
    t.grados = -300
except ValueError as e:
    print(e)
""",
            "77.0\nImposible",
            ["77.0\n-300", "25\nImposible", "Error"],
            "La asignación `t.grados = -300` pasa por el setter, que valida y lanza la excepción. Así se protege el dato sin cambiar cómo se usa.",
        ),
        pq(
            "prog-73",
            "Una propiedad sin setter es de solo lectura. " + QUE,
            """
class Circulo:
    def __init__(self, radio):
        self._radio = radio

    @property
    def radio(self):
        return self._radio

c = Circulo(2)
try:
    c.radio = 5
except AttributeError:
    print("AttributeError")
print(c.radio)
""",
            "AttributeError\n2",
            ["5", "AttributeError\n5", "2"],
            "Sin `@radio.setter` no se puede asignar: da AttributeError y el valor no cambia.",
        ),
        pq(
            "prog-74",
            "Ejemplo de los apuntes: los valores por defecto se evalúan al definir la función. "
            + QUE,
            "i = 5\n\ndef f(arg=i):\n    print(arg)\n\ni = 6\nf()",
            "5",
            ["6", "None", "Error"],
            "El valor por defecto se calcula una vez, cuando se ejecuta el `def`. Cambiar `i` después no le afecta.",
        ),
        pq(
            "prog-75",
            QUE,
            "def anadir(x, lista=[]):\n    lista.append(x)\n    return lista\n\nanadir(1)\nprint(anadir(2))",
            "[1, 2]",
            ["[2]", "[1]", "Error"],
            "La lista por defecto se crea una sola vez y se comparte entre llamadas. Solución: `lista=None` y crearla dentro.",
        ),
        pq(
            "prog-76",
            QUE,
            "def f(*args):\n    print(type(args).__name__, args)\n\nf(1, 2)",
            "tuple (1, 2)",
            ["list [1, 2]", "int 1 2", "Error"],
            "`*args` recoge los argumentos posicionales sobrantes en una tupla.",
        ),
        pq(
            "prog-77",
            QUE,
            "def f(**datos):\n    print(type(datos).__name__, datos)\n\nf(a=1, b=2)",
            "dict {'a': 1, 'b': 2}",
            ["tuple (1, 2)", "list ['a', 'b']", "Error"],
            "`**kwargs` recoge los argumentos pasados por nombre en un diccionario. Va siempre al final.",
        ),
        pq(
            "prog-78",
            QUE,
            "def resta(a, b):\n    return a - b\n\nprint(resta(b=2, a=10))",
            "8",
            ["-8", "Error", "12"],
            "Pasados por nombre, el orden de la llamada no importa: a = 10 y b = 2.",
        ),
        pq(
            "prog-79",
            "Las sugerencias de tipo no obligan. " + QUE,
            'def doble(n: int) -> int:\n    return n * 2\n\nprint(doble("ab"))',
            "abab",
            ["Error", "4", "None"],
            "Python no comprueba los tipos al ejecutar: las anotaciones documentan y ayudan al IDE o a herramientas como mypy.",
        ),
        pq(
            "prog-80",
            QUE,
            "def hacer_incrementador(n):\n    return lambda x: x + n\n\nsuma5 = hacer_incrementador(5)\nprint(suma5(10))",
            "15",
            ["10", "5", "Error"],
            "La lambda recuerda el `n` con el que se creó. `suma5` es una función que suma 5.",
        ),
        pq(
            "prog-81",
            QUE,
            """
class Punto:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return f"({self.x}, {self.y})"

print(Punto(1, 2))
""",
            "(1, 2)",
            ["Punto(1, 2)", "<__main__.Punto object>", "1 2"],
            "`print` llama a `__str__`. Sin él, se vería algo como `<__main__.Punto object at 0x…>`.",
        ),
        pq(
            "prog-82",
            QUE,
            "class Articulo:\n    IVA = 21\n\na = Articulo()\nb = Articulo()\na.IVA = 10\nprint(a.IVA, b.IVA, Articulo.IVA)",
            "10 21 21",
            ["10 10 10", "21 21 21", "10 10 21"],
            "`a.IVA = 10` crea un atributo de instancia solo en `a`, que oculta el de clase. Para cambiarlo para todos: `Articulo.IVA = 10`.",
        ),
        tq(
            "prog-83",
            "¿Qué es `self` en un método?",
            [
                "Una referencia al objeto sobre el que se llama el método",
                "El nombre de la clase",
                "Una palabra reservada que crea objetos",
                "Un atributo de clase",
            ],
            0,
            "Equivale al `this` de Java. Python lo pasa automáticamente: `p.saludar()` es `Persona.saludar(p)`.",
        ),
        fq(
            "prog-84",
            "Completa el primer parámetro del inicializador.",
            'class Coche:\n    def __init__(___, marca):\n        self.marca = marca\n\nprint(Coche("Seat").marca)',
            ["self"],
            "Seat",
            "El primer parámetro de todo método de instancia es la referencia al objeto; por convenio se llama `self`.",
        ),
    ],
    quiz=[
        tq(
            "prog-q11",
            "¿Dónde se crean normalmente los atributos de instancia?",
            [
                "En __init__, con self.nombre = valor",
                "Fuera de la clase",
                "En un atributo de clase",
                "En el import",
            ],
            0,
            "Así cada objeto tiene los suyos desde que se crea.",
        ),
        tq(
            "prog-q12",
            "¿Qué agrupa `**kwargs`?",
            [
                "Los argumentos pasados por nombre, en un diccionario",
                "Los posicionales, en una tupla",
                "Todos los argumentos, en una lista",
                "Solo los obligatorios",
            ],
            0,
            "`*args` es el que agrupa los posicionales en una tupla.",
        ),
    ],
    sources=[APUNTES, TUTORIAL],
)

L_UT5_MODULOS = Lesson(
    slug="prog-ut5-modulos-cadenas",
    title="UT5 · Módulos, paquetes, cadenas y expresiones regulares",
    theory="""
**Módulo:** un fichero `.py`. **Paquete:** una carpeta de módulos (con `__init__.py`, opcional desde Python 3.3, que puede definir `__all__`).

**Importar:**
- `import math` → se usa `math.sqrt(16)`;
- `from math import sqrt, pi` → se usa `sqrt(16)` sin prefijo;
- `import numpy as np` → alias;
- importaciones relativas dentro de un paquete: `from . import modulo`.

Al importar un módulo **se ejecuta** su código (las funciones y clases solo se definen). Por eso el programa principal se protege con `if __name__ == "__main__":` — `__name__` vale `"__main__"` solo en el fichero que se ejecuta directamente.

**Memoria:** Python cuenta las referencias de cada objeto y, cuando no queda ninguna, lo libera; el módulo `gc` (recolector generacional) limpia además las referencias circulares.

**Cadenas (str):** inmutables, en Unicode. Métodos: `upper`, `lower`, `capitalize`, `title`, `swapcase`, `strip`, `replace`, `split`, `join`, `count`, `find` (devuelve `-1` si no está; para comprobar suele bastar `in`), `startswith`, `endswith`, `isdigit`, `isalpha`, `center`. Ninguno cambia la cadena: **devuelven una nueva**.

**Expresiones regulares (módulo `re`):** se escriben como cadenas *raw* `r"…"`.
- Anclas `^` (inicio) y `$` (fin); clases `[abc]`, rangos `[a-z]`, negación `[^0-9]`; `\\d` dígito, `\\w` letra/dígito/_, `\\s` espacio, `.` cualquier carácter.
- Cuantificadores: `*` (0 o más), `+` (1 o más), `?` (0 o 1), `{n}`, `{n,m}`.
- Funciones: `re.match` (solo al **principio**), `re.search` (en cualquier sitio), `re.fullmatch` (la cadena entera), `re.findall` (lista de coincidencias), `re.sub` (reemplazar), `re.split`.

**math:** `ceil`, `floor`, `sqrt`, `pow`, `gcd`, `pi`, `e`, `log`, `sin`… Los apuntes presentan también **NumPy** (arrays), **Pandas** (Series y DataFrame) y **Matplotlib** (gráficas), que se instalan con pip.
""",
    example="""
import math
import re

def es_dni_valido(dni):
    \"\"\"8 dígitos y una letra mayúscula.\"\"\"
    return re.fullmatch(r"[0-9]{8}[A-Z]", dni) is not None

def main():
    print(math.sqrt(16), math.ceil(2.1))
    print(es_dni_valido("12345678Z"), es_dni_valido("1234Z"))
    frase = "  Aprender Python en DAW  "
    print(frase.strip().upper())
    print(re.findall(r"\\d+", "Tengo 2 gatos y 13 peces"))

if __name__ == "__main__":
    main()
""",
    exercise="""
Crea un módulo `utilidades.py` con:

1. `invertir(cadena)`;
2. `contar_palabras(cadena)`;
3. `es_palindromo(cadena)` (ignorando espacios y mayúsculas).

Impórtalo desde otro fichero y pruébalo con «Anita lava la tina».
""",
    starter='# utilidades.py\n\ndef invertir(cadena):\n    pass\n\n\nif __name__ == "__main__":\n    print(invertir("hola"))\n',
    hint='Palíndromo: `limpia = cadena.replace(" ", "").lower()` y `return limpia == limpia[::-1]`. Para contar palabras, `len(cadena.split())` (sin argumento, `split` ignora los espacios repetidos).',
    faq=[
        (
            "¿`re.match` o `re.search`?",
            "`match` solo busca al principio de la cadena; `search`, en cualquier posición. Para validar la cadena entera, `fullmatch`.",
        ),
        (
            '¿Por qué `r"\\d"` y no `"\\d"`?',
            "En una cadena normal la barra `\\` inicia secuencias de escape. Con `r` se queda tal cual, que es lo que espera `re`.",
        ),
    ],
    challenge=(
        "Contraseña segura",
        2,
        "Escribe `es_segura(clave)`: al menos 8 caracteres, una mayúscula, una minúscula y un dígito. Hazlo con `re.search` para cada condición.",
        "import re\n\ndef es_segura(clave):\n    pass\n",
        'Cuatro comprobaciones con `and`: `len(clave) >= 8`, `re.search(r"[A-Z]", clave)`, `r"[a-z]"` y `r"\\d"`.',
    ),
    questions=[
        pq(
            "prog-85",
            "El código se ejecuta directamente, no importado. " + QUE,
            "print(__name__)",
            "__main__",
            ["main", "None", "Error"],
            '`__name__` vale "__main__" en el fichero que se ejecuta; si el módulo se importa, vale el nombre del módulo.',
        ),
        pq(
            "prog-86",
            QUE,
            "import math\nprint(math.ceil(2.1), math.floor(2.9), math.sqrt(16))",
            "3 2 4.0",
            ["2 3 4", "3 2 4", "2 2 4.0"],
            "`ceil` redondea hacia arriba, `floor` hacia abajo y `sqrt` devuelve siempre un float.",
        ),
        pq(
            "prog-87",
            QUE,
            's = "  Hola Mundo  "\nprint(s.strip().lower().replace("mundo", "DAW"))',
            "hola DAW",
            ["Hola DAW", "  hola daw  ", "hola mundo"],
            "Cada método devuelve una cadena nueva y se encadenan: se quitan los espacios, se pasa a minúsculas y se reemplaza.",
        ),
        pq(
            "prog-88",
            QUE,
            'print("python".find("th"), "python".find("z"), "th" in "python")',
            "2 -1 True",
            ["2 None True", "3 -1 True", "2 0 False"],
            "`find` da la posición de la primera coincidencia o -1 si no la encuentra.",
        ),
        pq(
            "prog-89",
            QUE,
            'palabras = "uno  dos tres".split()\nprint(len(palabras), "-".join(palabras))',
            "3 uno-dos-tres",
            ["4 uno--dos-tres", "3 uno dos tres", "Error"],
            '`split()` sin argumento separa por cualquier cantidad de espacios. `split(" ")` daría una cadena vacía entre los dos espacios.',
        ),
        pq(
            "prog-90",
            QUE,
            'import re\nprint(re.findall(r"\\d+", "Tengo 2 gatos y 13 peces"))',
            "['2', '13']",
            ["['2', '1', '3']", "[2, 13]", "['Tengo', 'gatos']"],
            "`\\d+` es uno o más dígitos seguidos. `findall` devuelve una lista de cadenas.",
        ),
        pq(
            "prog-91",
            QUE,
            'import re\nprint(re.match(r"\\d", "a1") is None, re.search(r"\\d", "a1").group())',
            "True 1",
            ["False 1", "True a", "Error"],
            "`match` solo mira el principio (una «a»); `search` encuentra el 1 en cualquier posición.",
        ),
        pq(
            "prog-92",
            QUE,
            'import re\npatron = r"[0-9]{8}[A-Z]"\nprint(bool(re.fullmatch(patron, "12345678Z")), bool(re.fullmatch(patron, "1234567Z")))',
            "True False",
            ["True True", "False False", "False True"],
            "Ocho dígitos exactos y una mayúscula. El segundo solo tiene siete dígitos.",
        ),
        tq(
            "prog-93",
            "¿Qué es un paquete en Python?",
            [
                "Una carpeta que agrupa módulos (con __init__.py, opcional desde 3.3)",
                "Un único fichero .py",
                "Una clase con métodos estáticos",
                "Un entorno virtual",
            ],
            0,
            "Un módulo es un fichero `.py`; un paquete, una carpeta de módulos.",
        ),
        tq(
            "prog-94",
            "Tras `from math import sqrt`, ¿cómo se usa la raíz cuadrada?",
            ["sqrt(16)", "math.sqrt(16)", "math(16).sqrt", "import sqrt(16)"],
            0,
            "Con `import math` sería `math.sqrt(16)`.",
        ),
    ],
    quiz=[
        tq(
            "prog-q13",
            '¿Para qué sirve `if __name__ == "__main__":`?',
            [
                "Para que ese código solo se ejecute al lanzar el fichero directamente, no al importarlo",
                "Para declarar la función main obligatoria",
                "Para importar módulos",
                "Para capturar errores",
            ],
            0,
            "Al importar un módulo se ejecuta su código; con esta guarda, las pruebas o el programa principal no se lanzan.",
        ),
        tq(
            "prog-q14",
            "¿Los métodos de str modifican la cadena?",
            [
                "No: las cadenas son inmutables y devuelven una nueva",
                "Sí, siempre",
                "Solo upper y lower",
                "Solo si se usa self",
            ],
            0,
            "Por eso se escribe `s = s.upper()`.",
        ),
    ],
    sources=[APUNTES, TUTORIAL],
)

# ================================================================ UT6

L_UT6_COLECCIONES = Lesson(
    slug="prog-ut6-colecciones",
    title="UT6 · Listas, tuplas, diccionarios, conjuntos y recursividad",
    theory="""
**Secuencias:** contenedores **ordenados** que admiten repetidos, con índices desde 0 y negativos, rebanadas y las funciones `len`, `max`, `min`, `sum`, `sorted`, `zip`, `enumerate`, `in`.

**Listas** (mutables): `[]`, `list(iterable)` (ojo: `list("abc")` da 3 elementos y `["abc"]`, uno), comprensiones.
- Métodos: `append(x)`, `extend(iterable)`, `insert(i, x)`, `remove(x)` (la **primera** aparición), `pop(i)` (quita y **devuelve**; por defecto el último), `clear()`, `index(x)`, `count(x)`, `reverse()`, `copy()` (copia superficial, igual que `lista[:]`).
- `del lista[i]` borra sin devolver.
- `lista.sort()` ordena **en la misma lista** y devuelve `None`; `sorted(lista)` devuelve **una lista nueva**. Los dos admiten `key=` (una función, por ejemplo `str.lower` o una lambda) y `reverse=True`.
- `b = a` **no copia**: las dos variables son la misma lista.
- Listas de listas para matrices: `m[fila][columna]`. Para cálculo numérico de verdad, `numpy.array`.

**Tuplas** (inmutables): `(1, 2)`, `tuple(...)`. Para datos que no cambian; más ligeras que las listas.

**Diccionarios** (mutables): pares **clave → valor**; las claves deben ser inmutables (hashables). `d[clave]` da **KeyError** si no existe; `d.get(clave, defecto)` no falla. Métodos `keys()`, `values()`, `items()` (vistas que se actualizan solas), `pop`, `update`, `setdefault`, y `|` para unir (3.9).

**Conjuntos:** sin orden y **sin repetidos**. `set()` crea uno vacío (`{}` es un diccionario vacío). Operaciones: `|` unión, `&` intersección, `-` diferencia, `^` diferencia simétrica.

**Comprensiones:** `[expr for x in iterable if condición]`, `{k: v for …}`, `{x for …}`.

**Recursividad:** una función que se llama a sí misma. Necesita un **caso base** que detenga las llamadas y que cada llamada se acerque a él. Ventajas: código cercano a la definición matemática y elegante con estructuras recursivas (árboles). Inconvenientes: consume más memoria y tiempo (y Python limita la profundidad a unas 1000 llamadas). Úsala cuando simplifique de verdad.
""",
    example="""
notas = {"Ana": [7, 9], "Luis": [5, 6]}
notas["Eva"] = [8]
for alumno, lista in notas.items():
    print(alumno, sum(lista) / len(lista))

pares = [n for n in range(10) if n % 2 == 0]
print(pares)
print(sorted(["pera", "Uva", "manzana"], key=str.lower))

def factorial(n):
    if n <= 1:          # caso base
        return 1
    return n * factorial(n - 1)

print(factorial(5))
""",
    exercise="""
Con un diccionario, cuenta cuántas veces aparece cada palabra en un texto y muestra las 3 más frecuentes, de más a menos.

Pruébalo con: «el perro y el gato y el loro».
""",
    starter='texto = "el perro y el gato y el loro"\nfrecuencias = {}\n\n# for palabra in texto.split(): ...\n',
    hint="`frecuencias[p] = frecuencias.get(p, 0) + 1`. Luego `sorted(frecuencias.items(), key=lambda t: t[1], reverse=True)[:3]`.",
    faq=[
        (
            "¿`sort()` o `sorted()`?",
            "`sort()` cambia la lista y devuelve None, así que `x = lista.sort()` deja x a None. `sorted()` devuelve una lista nueva y deja la original igual.",
        ),
        (
            "¿Por qué `b = a` no copia la lista?",
            "Porque la asignación solo da otro nombre al mismo objeto. Para copiar: `a.copy()`, `a[:]` o `list(a)`; para listas anidadas, `copy.deepcopy(a)`.",
        ),
    ],
    challenge=(
        "Torres de Hanói",
        3,
        "Escribe `hanoi(discos, origen, auxiliar, destino)` recursiva que imprima los movimientos. Con 3 discos deben salir 7.",
        "def hanoi(discos, origen=1, auxiliar=2, destino=3):\n    pass\n",
        "Caso base: 1 disco se mueve directamente. Si no: mueve n-1 al auxiliar, el grande al destino y los n-1 del auxiliar al destino.",
    ),
    questions=[
        pq(
            "prog-95",
            QUE,
            "lista = [3, 1, 2]\nr = lista.sort()\nprint(r, lista)",
            "None [1, 2, 3]",
            ["[1, 2, 3] [1, 2, 3]", "[1, 2, 3] [3, 1, 2]", "None [3, 1, 2]"],
            "`sort()` ordena la propia lista y devuelve None. `sorted(lista)` devolvería una lista nueva.",
        ),
        pq(
            "prog-96",
            QUE,
            'print(sorted(["b", "A", "c"]), sorted(["b", "A", "c"], key=str.lower))',
            "['A', 'b', 'c'] ['A', 'b', 'c']",
            ["['b', 'A', 'c'] ['A', 'b', 'c']", "['A', 'c', 'b'] ['A', 'b', 'c']", "Error"],
            "Aquí coinciden: las mayúsculas van antes que las minúsculas y «A» ya es la primera. Con `key=str.lower` se compara sin distinguir mayúsculas.",
        ),
        pq(
            "prog-97",
            QUE,
            'print(len(list("abc")), len(["abc"]))',
            "3 1",
            ["1 1", "3 3", "1 3"],
            '`list()` recorre la cadena letra a letra; `["abc"]` es una lista con un solo elemento.',
        ),
        pq(
            "prog-98",
            QUE,
            "lista = [1, 2, 3, 2]\nlista.remove(2)\nx = lista.pop()\nprint(lista, x)",
            "[1, 3] 2",
            ["[1, 3, 2] 2", "[1, 2] 3", "[3] 2"],
            "`remove(2)` quita la primera aparición; `pop()` quita y devuelve el último (el otro 2).",
        ),
        pq(
            "prog-99",
            QUE,
            "a = [1, 2]\nb = a\nc = a.copy()\na.append(3)\nprint(b, c)",
            "[1, 2, 3] [1, 2]",
            ["[1, 2] [1, 2]", "[1, 2, 3] [1, 2, 3]", "[1, 2] [1, 2, 3]"],
            "`b` es la misma lista que `a` (alias); `c` es una copia independiente.",
        ),
        pq(
            "prog-100",
            QUE,
            't = (1, 2)\ntry:\n    t[0] = 5\nexcept TypeError:\n    print("TypeError")\nprint(t)',
            "TypeError\n(1, 2)",
            ["(5, 2)", "TypeError\n(5, 2)", "(1, 2)"],
            "Las tuplas son inmutables: no se puede cambiar un elemento.",
        ),
        pq(
            "prog-101",
            QUE,
            'precios = {"pera": 2}\nprint(precios.get("uva", 0), precios["pera"])\ntry:\n    print(precios["uva"])\nexcept KeyError:\n    print("KeyError")',
            "0 2\nKeyError",
            ["None 2\nNone", "0 2\n0", "Error"],
            "`get` devuelve el valor por defecto si la clave no existe; los corchetes lanzan KeyError.",
        ),
        pq(
            "prog-102",
            QUE,
            'frecuencia = {}\nfor letra in "banana":\n    frecuencia[letra] = frecuencia.get(letra, 0) + 1\nprint(frecuencia)',
            "{'b': 1, 'a': 3, 'n': 2}",
            ["{'a': 3, 'b': 1, 'n': 2}", "{'b': 1, 'a': 1, 'n': 1}", "Error"],
            "Los diccionarios conservan el orden de inserción (desde Python 3.7): b, a, n.",
        ),
        pq(
            "prog-103",
            QUE,
            "a = {1, 2, 3}\nb = {2, 3, 4}\nprint(sorted(a | b), sorted(a & b), sorted(a - b), sorted(a ^ b))",
            "[1, 2, 3, 4] [2, 3] [1] [1, 4]",
            [
                "[1, 2, 3, 4] [2, 3] [4] [1, 4]",
                "[1, 2, 2, 3, 3, 4] [2, 3] [1] [1, 4]",
                "[1, 2, 3, 4] [1, 4] [1] [2, 3]",
            ],
            "Unión, intersección, diferencia (en a y no en b) y diferencia simétrica (en uno solo de los dos).",
        ),
        pq(
            "prog-104",
            QUE,
            "print(type({}).__name__, type(set()).__name__, len({1, 1, 2}))",
            "dict set 2",
            ["set set 3", "dict dict 2", "set dict 3"],
            "`{}` es un diccionario vacío; el conjunto vacío es `set()`. Los repetidos se eliminan.",
        ),
        pq(
            "prog-105",
            QUE,
            "print([x ** 2 for x in range(6) if x % 2 == 0])",
            "[0, 4, 16]",
            ["[0, 1, 4, 9, 16, 25]", "[4, 16]", "[0, 2, 4]"],
            "Se filtran los pares (0, 2, 4) y se eleva cada uno al cuadrado.",
        ),
        pq(
            "prog-106",
            QUE,
            "print({x: x ** 2 for x in range(4)})",
            "{0: 0, 1: 1, 2: 4, 3: 9}",
            ["[0, 1, 4, 9]", "{0, 1, 4, 9}", "{1: 1, 2: 4, 3: 9}"],
            "Comprensión de diccionario: `clave: valor for …`.",
        ),
        pq(
            "prog-107",
            QUE,
            "def fibo(n):\n    if n <= 1:\n        return n\n    return fibo(n - 1) + fibo(n - 2)\n\nprint(fibo(7))",
            "13",
            ["8", "21", "Error"],
            "0, 1, 1, 2, 3, 5, 8, 13: fibo(7) es 13. El caso base (n <= 1) detiene la recursión.",
        ),
        pq(
            "prog-108",
            QUE,
            "matriz = [[1, 2, 3], [4, 5, 6]]\nprint(matriz[1][0], len(matriz), len(matriz[0]))",
            "4 2 3",
            ["2 2 3", "4 3 2", "1 2 3"],
            "`matriz[1]` es la segunda fila y `[0]`, su primer elemento. Hay 2 filas de 3 columnas.",
        ),
        pq(
            "prog-109",
            QUE,
            'for i, fruta in enumerate(["pera", "uva"], start=1):\n    print(i, fruta)',
            "1 pera\n2 uva",
            ["0 pera\n1 uva", "pera 1\nuva 2", "Error"],
            "`enumerate` da el índice y el elemento; los apuntes lo prefieren a `for i in range(len(lista))`.",
        ),
        oq(
            "prog-110",
            "Ordena las líneas del factorial recursivo (debe mostrar 120).",
            [
                "def factorial(n):",
                "    if n <= 1:",
                "        return 1",
                "    return n * factorial(n - 1)",
                "print(factorial(5))",
            ],
            "120",
            "Primero el caso base, después la llamada recursiva que se acerca a él.",
        ),
    ],
    quiz=[
        tq(
            "prog-q15",
            "¿Qué necesita siempre una función recursiva?",
            [
                "Un caso base que detenga las llamadas",
                "Un bucle while",
                "Una variable global",
                "Un atributo de clase",
            ],
            0,
            "Sin caso base se llama sin fin hasta dar RecursionError.",
        ),
        tq(
            "prog-q16",
            "¿Qué diferencia a una tupla de una lista?",
            [
                "La tupla es inmutable",
                "La tupla no tiene orden",
                "La tupla no admite repetidos",
                "Ninguna",
            ],
            0,
            "Los conjuntos son los que no tienen orden ni repetidos.",
        ),
    ],
    sources=[APUNTES, TUTORIAL],
)

L_UT6_HERENCIA = Lesson(
    slug="prog-ut6-herencia-excepciones",
    title="UT6 · Herencia, polimorfismo, excepciones y estructuras de datos",
    theory="""
**Herencia:** `class Hija(Padre):` o, con varios padres, `class Hija(Padre1, Padre2):`. Toda clase hereda al final de **`object`**. En el inicializador de la hija hay que llamar **al principio** al del padre: `super().__init__(...)`. Con herencia múltiple, Python sigue un orden fijo de búsqueda de métodos (MRO): de izquierda a derecha.

**Sobrescritura:** la hija redefine un método heredado; con `super().metodo()` puede reutilizar el del padre. **Polimorfismo:** la misma llamada (`animal.hablar()`) hace cosas distintas según la clase real del objeto.

**Tipo de un objeto:** `isinstance(objeto, Clase)` es verdadero también para las clases hijas; `type(objeto) is Clase` solo para la clase exacta.

**Atributos y métodos de clase y estáticos:**
- `@classmethod` recibe la clase (`cls`) y se usa, por ejemplo, para constructores alternativos: `return cls(...)`.
- `@staticmethod` no recibe ni `self` ni `cls`: es una función que vive dentro de la clase.

**Clases abstractas e interfaces:** `from abc import ABC, abstractmethod`. Un `@abstractmethod` obliga a las hijas a implementarlo, y la clase abstracta **no se puede instanciar**. Una interfaz, en Python, es una clase abstracta solo con métodos abstractos. `@final` (del módulo `typing`, 3.8) marca lo que no debe sobrescribirse, aunque lo comprueban herramientas como mypy, no el intérprete.

**Métodos mágicos:** `__str__`, `__len__`, `__eq__`, `__lt__`, `__add__` (el operador `+`), `__getitem__`, `__contains__` (`in`), `__iter__` y `__next__` (este último lanza `StopIteration` al acabar)…

**Generadores:** funciones con **`yield`**: devuelven un valor y **se pausan** hasta que se pide el siguiente.

**Excepciones:** errores durante la ejecución; todas derivan de `BaseException` (las normales, de `Exception`).
- `try` / `except Tipo as e` / `else` (si **no** hubo error) / `finally` (**siempre**).
- Un `except` captura también las excepciones hijas, así que **el orden importa**: primero las más concretas.
- `raise ValueError("mensaje")` lanza; `raise` a secas relanza. Excepciones propias: `class SaldoError(Exception): pass`.

**Estructuras de datos:** **pila** (LIFO) con una lista (`append` y `pop`); **cola** (FIFO) con `collections.deque` (`append` y `popleft`); **árboles** (cada nodo, un padre; binario si tiene como máximo 2 hijos) y **grafos** (con `networkx`).

**Pruebas unitarias (`unittest`):** una clase que hereda de `TestCase`, métodos que empiezan por `test_`, `setUp` antes de cada prueba y comprobaciones `assertEqual`, `assertTrue`, `assertRaises`.
""",
    example="""
from abc import ABC, abstractmethod


class Animal(ABC):
    def __init__(self, nombre):
        self.nombre = nombre

    @abstractmethod
    def hablar(self):
        pass

    def __str__(self):
        return f"{self.nombre} dice {self.hablar()}"


class Perro(Animal):
    def hablar(self):
        return "Guau"


class Gato(Animal):
    def hablar(self):
        return "Miau"


for animal in [Perro("Toby"), Gato("Misi")]:
    print(animal)           # polimorfismo

try:
    Animal("Nadie")
except TypeError:
    print("No se puede instanciar una clase abstracta")
""",
    exercise="""
Jerarquía de cuentas bancarias:

- `CuentaBancaria` (abstracta) con `iban`, `saldo` y los métodos `ingresar(cantidad)` y `retirar(cantidad)`;
- `CuentaCorriente`: puede quedarse en negativo hasta −50 €;
- `CuentaAhorro`: nunca en negativo.

Lanza una excepción propia `SaldoInsuficienteError` cuando no se pueda retirar, y captúrala en el programa principal.
""",
    starter="from abc import ABC, abstractmethod\n\n\nclass SaldoInsuficienteError(Exception):\n    pass\n\n\nclass CuentaBancaria(ABC):\n    pass\n",
    hint="Cada hija define un método abstracto `saldo_minimo()`. `retirar` comprueba `self.saldo - cantidad < self.saldo_minimo()` y lanza la excepción.",
    faq=[
        (
            "¿Se puede usar super() con herencia múltiple?",
            "Sí: `super()` sigue el orden MRO de la clase. Los apuntes llaman a cada padre por su nombre (`Padre.__init__(self, ...)`), lo que también funciona, pero entonces hay que pasar `self`.",
        ),
        (
            "¿`__x` en el padre se hereda?",
            "Sí, pero con el nombre cambiado (`_Padre__x`). Por eso el curso recomienda un solo guion bajo para lo interno.",
        ),
    ],
    challenge=(
        "Vector con operadores",
        2,
        "Crea la clase `Vector2D` con `__add__`, `__sub__`, `__eq__`, `__str__` y `__len__`, que devuelva el módulo redondeado a entero.",
        "class Vector2D:\n    def __init__(self, x, y):\n        pass\n",
        "`__add__` devuelve `Vector2D(self.x + otro.x, self.y + otro.y)`. `__len__` debe devolver un int: `round(math.hypot(self.x, self.y))`.",
    ),
    questions=[
        pq(
            "prog-111",
            QUE,
            """
class Persona:
    def __init__(self, nombre):
        self.nombre = nombre

    def __str__(self):
        return self.nombre

class Alumno(Persona):
    def __init__(self, nombre, nia):
        super().__init__(nombre)
        self.nia = nia

    def __str__(self):
        return f"{super().__str__()} (nia {self.nia})"

print(Alumno("Ana", 7))
""",
            "Ana (nia 7)",
            ["Ana", "(nia 7)", "Error"],
            "`super().__init__` inicializa la parte de Persona y `super().__str__()` reutiliza el método del padre en la sobrescritura.",
        ),
        pq(
            "prog-112",
            QUE,
            """
class Animal:
    def hablar(self):
        return "..."

class Perro(Animal):
    def hablar(self):
        return "Guau"

class Gato(Animal):
    def hablar(self):
        return "Miau"

for a in [Perro(), Gato(), Animal()]:
    print(a.hablar())
""",
            "Guau\nMiau\n...",
            ["...\n...\n...", "Guau\nGuau\nGuau", "Error"],
            "Polimorfismo: la misma llamada ejecuta el método de la clase real de cada objeto.",
        ),
        pq(
            "prog-113",
            QUE,
            "class Persona:\n    pass\n\nclass Alumno(Persona):\n    pass\n\na = Alumno()\nprint(isinstance(a, Persona), type(a) is Persona, isinstance(a, object))",
            "True False True",
            ["True True True", "False False True", "True False False"],
            "Un Alumno es también una Persona (y un object), pero su tipo exacto es Alumno.",
        ),
        pq(
            "prog-114",
            QUE,
            """
class Persona:
    ANIO_ACTUAL = 2026

    def __init__(self, nombre, edad):
        self.nombre = nombre
        self.edad = edad

    @classmethod
    def desde_anio(cls, nombre, anio):
        return cls(nombre, cls.ANIO_ACTUAL - anio)

    @staticmethod
    def es_adulto(edad):
        return edad >= 18

p = Persona.desde_anio("Ana", 2000)
print(p.edad, Persona.es_adulto(p.edad))
""",
            "26 True",
            ["2000 True", "26 False", "Error"],
            "El método de clase es un constructor alternativo (`cls(...)` crea el objeto). El estático no necesita objeto ni clase.",
        ),
        pq(
            "prog-115",
            QUE,
            """
from abc import ABC, abstractmethod

class Figura(ABC):
    @abstractmethod
    def area(self):
        pass

try:
    Figura()
except TypeError:
    print("TypeError")
""",
            "TypeError",
            ["None", "0", "Figura"],
            "Una clase con métodos abstractos sin implementar no se puede instanciar: sirve de molde para las hijas.",
        ),
        pq(
            "prog-116",
            QUE,
            """
class Punto:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, otro):
        return Punto(self.x + otro.x, self.y + otro.y)

    def __str__(self):
        return f"({self.x}, {self.y})"

print(Punto(1, 2) + Punto(3, 4))
""",
            "(4, 6)",
            ["(1, 2)(3, 4)", "Error", "(3, 8)"],
            "El operador `+` llama a `__add__`: sobrecarga de operadores con métodos mágicos.",
        ),
        pq(
            "prog-117",
            QUE,
            "def cuenta(n):\n    i = 0\n    while i < n:\n        yield i\n        i += 1\n\nprint(list(cuenta(3)))",
            "[0, 1, 2]",
            ["[1, 2, 3]", "3", "None"],
            "Cada `yield` entrega un valor y pausa la función hasta que se pide el siguiente.",
        ),
        pq(
            "prog-118",
            QUE,
            """
def dividir(a, b):
    try:
        r = a / b
    except ZeroDivisionError:
        print("Error: división por cero")
    else:
        print(r)
    finally:
        print("Fin")

dividir(1, 0)
dividir(4, 2)
""",
            "Error: división por cero\nFin\n2.0\nFin",
            [
                "Error: división por cero\n2.0\nFin",
                "Error: división por cero\nFin\n2.0",
                "Fin\nFin",
            ],
            "`else` solo se ejecuta si no hubo excepción; `finally`, siempre.",
        ),
        pq(
            "prog-119",
            "IndexError es hija de LookupError. " + QUE,
            'try:\n    [1][5]\nexcept LookupError:\n    print("Lookup")\nexcept IndexError:\n    print("Index")',
            "Lookup",
            ["Index", "Lookup\nIndex", "Error"],
            "El primer `except` compatible gana y captura también a las hijas. Las excepciones más concretas deben ir primero.",
        ),
        pq(
            "prog-120",
            QUE,
            """
class SaldoError(Exception):
    pass

def retirar(saldo, cantidad):
    if cantidad > saldo:
        raise SaldoError("Saldo insuficiente")
    return saldo - cantidad

try:
    retirar(50, 80)
except SaldoError as e:
    print(e)
""",
            "Saldo insuficiente",
            ["-30", "SaldoError", "Error"],
            "Una excepción propia hereda de Exception. `print(e)` muestra su mensaje.",
        ),
        pq(
            "prog-121",
            QUE,
            "from collections import deque\n\npila = [1, 2, 3]\ncola = deque([1, 2, 3])\nprint(pila.pop(), cola.popleft())",
            "3 1",
            ["1 3", "3 3", "1 1"],
            "Pila LIFO: sale el último en entrar. Cola FIFO: sale el primero. `deque.popleft()` es eficiente; `lista.pop(0)` no.",
        ),
        pq(
            "prog-122",
            QUE,
            'class A:\n    def quien(self):\n        return "A"\n\nclass B(A):\n    def quien(self):\n        return "B"\n\nclass C(A):\n    def quien(self):\n        return "C"\n\nclass D(B, C):\n    pass\n\nprint(D().quien())',
            "B",
            ["C", "A", "Error"],
            "Con herencia múltiple, Python busca de izquierda a derecha (MRO: D, B, C, A, object).",
        ),
        tq(
            "prog-123",
            "En unittest, ¿qué hace setUp?",
            [
                "Se ejecuta antes de cada método de prueba para preparar el entorno",
                "Se ejecuta una sola vez al final",
                "Define la clase que se prueba",
                "Compara dos valores",
            ],
            0,
            "Las pruebas son métodos que empiezan por `test_` en una clase que hereda de `unittest.TestCase`.",
        ),
        tq(
            "prog-124",
            "¿Qué hace `@final` del módulo typing?",
            [
                "Marca un método que no debe sobrescribirse; lo comprueban herramientas como mypy, no el intérprete",
                "Impide al intérprete ejecutar el método",
                "Convierte el método en estático",
                "Hace el atributo inmutable en ejecución",
            ],
            0,
            "Python no lanza ningún error al ejecutar si una hija lo sobrescribe: es una indicación para los analizadores de código.",
        ),
        bq(
            "prog-125",
            """
class Persona:
    def __init__(self, nombre):
        self.nombre = nombre
class Alumno(Persona):
    def __init__(self, nombre, nia):
        self.nia = nia
a = Alumno("Ana", 7)
print(a.nombre, a.nia)
""",
            5,
            "        super().__init__(nombre); self.nia = nia",
            "Ana 7",
            "El inicializador de Alumno no llama al del padre, así que el objeto no tiene `nombre` (AttributeError). Hay que empezar por `super().__init__(nombre)`.",
        ),
    ],
    quiz=[
        tq(
            "prog-q17",
            "¿Cuándo se ejecuta el bloque `finally`?",
            [
                "Siempre, haya o no excepción",
                "Solo si hay excepción",
                "Solo si no hay excepción",
                "Nunca si hay return",
            ],
            0,
            "Se usa para liberar recursos: cerrar ficheros o conexiones.",
        ),
        tq(
            "prog-q18",
            "¿De qué clase heredan todas las clases de Python?",
            ["object", "Exception", "type", "ABC"],
            0,
            "Es la raíz de la jerarquía; si no se indica padre, se hereda de object.",
        ),
    ],
    sources=[APUNTES, TUTORIAL],
)

# ================================================================ UT7

L_UT7 = Lesson(
    slug="prog-ut7-proyecto",
    title="UT7 · Proyecto: el juego de los códigos secretos",
    theory="""
La UT7 es un **proyecto integrador**: una **aventura conversacional** (se muestra un texto y se responde por teclado) para practicar comprensión lectora y matemáticas, ambientada en una galaxia lejana.

**Flujo del juego:** Inicio (se pulsa Intro) → Nivel 1 → … → Nivel 5 → **Ganar** → Fin. Una respuesta incorrecta en cualquier nivel lleva a **Perder** → Fin.

**Los cinco códigos** (con números aleatorios en cada partida):
1. **Sumatorio** de S1 a S2, ambos incluidos (S1 entre 1 y 10, S2 entre 20 y 30).
2. **Productorio** de P1 a P2, ambos incluidos (P1 entre 1 y 7, P2 entre 8 y 12).
3. **Factorial** de N/10 redondeado hacia abajo (N entre 50 y 100).
4. **1 si P es primo, 0 si no** (P entre 10 y 100).
5. **M! + S!** (M y S entre 5 y 10).

**Aleatoriedad (módulo random):** `random.random()` devuelve un real en **[0.0, 1.0)** (el 1 no se incluye); `random.randint(a, b)` un entero **con los dos extremos incluidos**; `random.choice(secuencia)` elige un elemento. Las preguntas de cada nivel se pueden guardar en listas o diccionarios y elegir con `choice`.

**Cómo abordarlo:** una función por cálculo (`sumatorio`, `productorio`, `factorial`, `es_primo`), una función por nivel que genera los números, pregunta y devuelve si se acertó, y un programa principal que recorre los niveles y para al primer fallo.
""",
    example="""
import math
import random


def sumatorio(desde, hasta):
    return sum(range(desde, hasta + 1))


def es_primo(n):
    return n > 1 and all(n % d for d in range(2, int(n ** 0.5) + 1))


s1, s2 = random.randint(1, 10), random.randint(20, 30)
print(f"Nivel 1: suma de {s1} a {s2} = {sumatorio(s1, s2)}")
print("Nivel 2:", math.prod(range(5, 11)))
print("Nivel 3:", math.factorial(78 // 10))
print("Nivel 4:", 1 if es_primo(97) else 0)
print("Nivel 5:", math.factorial(7) + math.factorial(5))
""",
    exercise="""
Programa el juego completo:

- una función por nivel que genere los números con `random.randint`, muestre el texto, lea la respuesta y devuelva `True` o `False`;
- un bucle que recorra los niveles y pare al primer fallo;
- pantallas de Ganar y Perder, y «Gracias por jugar» al final.
""",
    starter='import random\n\n\ndef nivel_1():\n    s1 = random.randint(1, 10)\n    s2 = random.randint(20, 30)\n    respuesta = int(input(f"Suma de {s1} a {s2}? "))\n    return respuesta == sum(range(s1, s2 + 1))\n',
    hint="Guarda los niveles en una lista de funciones: `for nivel in [nivel_1, nivel_2, ...]: if not nivel(): ...`.",
    faq=[
        (
            "¿randint incluye el último número?",
            "Sí: `randint(1, 10)` puede dar 10. En cambio `range(1, 10)` y `random.randrange(1, 10)` no incluyen el 10.",
        ),
        (
            "¿Cómo compruebo si un número es primo de forma eficiente?",
            "Basta con probar divisores hasta la raíz cuadrada: si n tiene un divisor mayor que √n, también tiene uno menor.",
        ),
    ],
    challenge=(
        "Preguntas aleatorias",
        2,
        "Guarda 3 enunciados distintos por nivel en un diccionario `{nivel: [enunciados]}` y elige uno con `random.choice` en cada partida.",
        'import random\n\nENUNCIADOS = {\n    1: ["Chewbacca necesita...", "..."],\n}\n',
        "`random.choice(ENUNCIADOS[1])` devuelve uno de los textos del nivel 1.",
    ),
    questions=[
        pq(
            "prog-126",
            "Nivel 1: sumatorio de S1 = 10 a S2 = 20, ambos incluidos. " + QUE,
            "print(sum(range(10, 21)))",
            "165",
            ["155", "210", "30"],
            "10 + 11 + … + 20 = 165. Para incluir el 20, el range acaba en 21.",
        ),
        pq(
            "prog-127",
            "Nivel 2: productorio de 5 a 10. " + QUE,
            "import math\nprint(math.prod(range(5, 11)))",
            "151200",
            ["30240", "3628800", "45"],
            "5 × 6 × 7 × 8 × 9 × 10 = 151200.",
        ),
        pq(
            "prog-128",
            "Nivel 3 con N = 78. " + QUE,
            "import math\nn = 78\nprint(math.factorial(n // 10))",
            "5040",
            ["40320", "720", "78"],
            "78 // 10 = 7 (redondeo hacia abajo) y 7! = 5040.",
        ),
        pq(
            "prog-129",
            "Nivel 4. " + QUE,
            "def es_primo(p):\n    if p < 2:\n        return 0\n    for d in range(2, int(p ** 0.5) + 1):\n        if p % d == 0:\n            return 0\n    return 1\n\nprint(es_primo(97), es_primo(91))",
            "1 0",
            ["1 1", "0 0", "0 1"],
            "97 es primo; 91 = 7 × 13 no lo es.",
        ),
        pq(
            "prog-130",
            "Nivel 5 con M = 7 y S = 5. " + QUE,
            "import math\nprint(math.factorial(7) + math.factorial(5))",
            "5160",
            ["5040", "12", "5165"],
            "7! = 5040 y 5! = 120: la suma es 5160.",
        ),
        tq(
            "prog-131",
            "¿Qué valores puede devolver `random.random()`?",
            [
                "Un real entre 0.0 (incluido) y 1.0 (excluido)",
                "Un entero entre 0 y 1",
                "Un real entre 0 y 100",
                "Un real entre -1 y 1",
            ],
            0,
            "Para enteros se usa `randint(a, b)`, que sí incluye los dos extremos.",
        ),
        tq(
            "prog-132",
            "En el juego, ¿qué pasa si el jugador falla el código del nivel 3?",
            [
                "Va a la pantalla de Perder y después a Fin",
                "Repite el nivel 3",
                "Vuelve al nivel 1",
                "Pasa al nivel 4 con menos puntos",
            ],
            0,
            "Cualquier fallo lleva a Perder; acertar los cinco lleva a Ganar.",
        ),
        tq(
            "prog-133",
            "¿Qué función elige al azar un elemento de una lista?",
            [
                "random.choice(lista)",
                "random.random(lista)",
                "random.randint(lista)",
                "lista.random()",
            ],
            0,
            "Sirve para elegir el enunciado de cada nivel de entre varios.",
        ),
        fq(
            "prog-134",
            "Completa para sumar del 10 al 20, ambos incluidos.",
            "print(sum(range(10, ___)))",
            ["21"],
            "165",
            "El fin de range no se incluye: para llegar al 20 hay que poner 21.",
        ),
    ],
    quiz=[
        tq(
            "prog-q19",
            "¿`random.randint(1, 10)` puede devolver 10?",
            [
                "Sí, incluye los dos extremos",
                "No, nunca",
                "Solo con semilla",
                "Solo si se usa float",
            ],
            0,
            "A diferencia de `range`, `randint` incluye el final.",
        ),
    ],
    sources=[APUNTES, TUTORIAL],
)

# ================================================================ UT8

L_UT8 = Lesson(
    slug="prog-ut8-ficheros-bd",
    title="UT8 · Ficheros, serialización, bases de datos y XML",
    theory="""
La memoria principal se pierde al terminar el programa y es limitada: los **ficheros** guardan los datos en memoria secundaria.

**Tipos de acceso:** **secuencial** (el puntero avanza desde el principio, uno a uno) y **directo** (se salta a cualquier posición con `seek`). **Texto** (caracteres con una codificación; se leen como `str`) frente a **binario** (bytes tal cual están en memoria; se leen como `bytes`: imágenes, ejecutables).

**Trabajo con ficheros:** apertura → operaciones → **cierre**. Si no se cierra, lo escrito puede quedarse en el búfer y perderse.
- `open(ruta, modo, encoding="utf-8")`: especifica siempre la codificación (la de por defecto depende del sistema: cp1252 en Windows, UTF-8 en Linux).
- Modos: `r` leer (por defecto; error si no existe), `w` escribir (**crea o vacía** el fichero), `a` añadir al final, `x` crear (error si ya existe), `b` binario, `+` leer y escribir.
- **`with open(...) as f:`** cierra el fichero al salir del bloque, aunque haya un error (no captura la excepción: para eso, `try`).
- `write(texto)` devuelve los caracteres escritos y **no añade el salto de línea**; `read()` todo, `read(n)` hasta n caracteres, `readline()` una línea (con su `\\n`), `readlines()` la lista de líneas, `for linea in f` recorre línea a línea; al final, `read()` devuelve `""`. `seek` y `tell` mueven y dan la posición.

**Serialización:** convertir un objeto en bytes o texto para guardarlo o enviarlo, y reconstruir después **un clon**. Con `pickle` (`dumps`/`loads`, `dump`/`load`), o en formatos legibles como JSON o XML. No se pueden serializar ficheros abiertos, sockets ni conexiones.

**Sistema de ficheros:** `os` (`listdir`, `mkdir`, `remove`, `rename`, `getcwd`), `pathlib.Path` (rutas como objetos, independientes del sistema: `Path("datos") / "notas.txt"`) y `shutil` (`copy`, `move`, `rmtree`).

**Bases de datos desde Python:** el estándar **DB-API (PEP 249)**: conexión → cursor → `execute` → `fetchone`/`fetchall` → `commit` → cerrar. Drivers: `sqlite3` (incluido), `mysql.connector`, `psycopg2`… Pasa siempre los datos como **parámetros** (`?` en SQLite, `%s` en MySQL), nunca concatenando cadenas: así se evita la **inyección SQL**.

**XML:** con el paquete `xml`. **SAX** lee por eventos, una parte cada vez (poca memoria, sin volver atrás); **DOM** carga el documento entero como un árbol (acceso directo a cualquier nodo).
""",
    example="""
import pickle
import sqlite3
from pathlib import Path

ruta = Path("notas.txt")
with ruta.open("w", encoding="utf-8") as f:
    f.write("Ana 8\\n")
    f.write("Luis 6\\n")

with ruta.open(encoding="utf-8") as f:
    for linea in f:
        nombre, nota = linea.split()
        print(nombre, int(nota))

copia = pickle.loads(pickle.dumps({"Ana": [8, 9]}))
print(copia)

conexion = sqlite3.connect(":memory:")
cursor = conexion.cursor()
cursor.execute("CREATE TABLE alumnos (nombre TEXT, nota INTEGER)")
cursor.execute("INSERT INTO alumnos VALUES (?, ?)", ("Eva", 9))
conexion.commit()
print(cursor.execute("SELECT * FROM alumnos").fetchall())
conexion.close()
""",
    exercise="""
El fichero `alumnos.txt` tiene una línea por alumno: `nombre apellido nota1 nota2 nota3`.

1. Lee el fichero con `with` y calcula la media de cada alumno.
2. Escribe `medias.txt` con los alumnos ordenados de mayor a menor media.
3. Guarda también los resultados en una tabla de SQLite con parámetros `?`.
""",
    starter='from statistics import mean\n\nalumnos = []\nwith open("alumnos.txt", encoding="utf-8") as f:\n    for linea in f:\n        nombre, apellido, *notas = linea.split()\n        # ...\n',
    hint="`alumnos.append((mean(int(n) for n in notas), nombre, apellido))` y después `sorted(alumnos, reverse=True)`.",
    faq=[
        (
            "¿`with` captura los errores?",
            "No: garantiza que el fichero se cierra, pero la excepción sigue su camino. Si el fichero puede no existir, rodéalo con `try`/`except FileNotFoundError`.",
        ),
        (
            "¿Por qué no construir el SQL con f-strings?",
            "Porque si el dato contiene comillas o SQL, se ejecutaría como código (inyección SQL). Con parámetros, el driver lo trata siempre como dato.",
        ),
    ],
    challenge=(
        "Clínica veterinaria",
        3,
        "Carga al iniciar tres ficheros (clientes, mascotas y citas), trabaja en memoria con clases y guarda todo al salir. Después haz la misma versión con SQLite.",
        "class Cliente:\n    pass\n\n\nclass Mascota:\n    pass\n",
        "Separa en funciones: `cargar_datos()`, `guardar_datos()` y el menú. Cada línea del fichero se convierte en un objeto y viceversa.",
    ),
    questions=[
        pq(
            "prog-135",
            QUE,
            'with open("datos.txt", "w", encoding="utf-8") as f:\n    f.write("uno\\n")\n    f.write("dos\\n")\n\nwith open("datos.txt", encoding="utf-8") as f:\n    print(f.readlines())',
            "['uno\\n', 'dos\\n']",
            ["['uno', 'dos']", "uno\ndos", "['uno\\ndos\\n']"],
            "`readlines()` devuelve una lista con cada línea, incluido su salto de línea.",
        ),
        pq(
            "prog-136",
            QUE,
            'with open("f.txt", "w", encoding="utf-8") as f:\n    f.write("A")\nwith open("f.txt", "a", encoding="utf-8") as f:\n    f.write("B")\nwith open("f.txt", "w", encoding="utf-8") as f:\n    f.write("C")\nwith open("f.txt", encoding="utf-8") as f:\n    print(f.read())',
            "C",
            ["ABC", "AB", "CAB"],
            "`a` añade (queda «AB»), pero el último `w` vacía el fichero antes de escribir «C».",
        ),
        pq(
            "prog-137",
            QUE,
            'with open("f.txt", "w", encoding="utf-8") as f:\n    print(f.write("hola\\n"))',
            "5",
            ["4", "None", "hola"],
            "`write` devuelve cuántos caracteres escribió: 4 letras y el salto de línea.",
        ),
        pq(
            "prog-138",
            QUE,
            'with open("f.txt", "w", encoding="utf-8") as f:\n    f.write("abc")\nwith open("f.txt", encoding="utf-8") as f:\n    print(f.read())\n    print(repr(f.read()))',
            "abc\n''",
            ["abc\nabc", "abc\nNone", "Error"],
            "Tras leer todo, el puntero está al final: la siguiente lectura devuelve una cadena vacía.",
        ),
        pq(
            "prog-139",
            QUE,
            'open("f.txt", "w").close()\ntry:\n    open("f.txt", "x")\nexcept FileExistsError:\n    print("FileExistsError")',
            "FileExistsError",
            ["Nada", "FileNotFoundError", "Error"],
            "El modo `x` solo crea ficheros nuevos: si ya existe, falla. Evita machacar datos por accidente.",
        ),
        pq(
            "prog-140",
            QUE,
            'try:\n    with open("no_existe.txt", encoding="utf-8") as f:\n        print(f.read())\nexcept FileNotFoundError:\n    print("FileNotFoundError")',
            "FileNotFoundError",
            ["''", "None", "Se crea vacío"],
            "El modo `r` (por defecto) exige que el fichero exista. `with` no captura la excepción.",
        ),
        pq(
            "prog-141",
            QUE,
            'with open("f.txt", "w", encoding="utf-8") as f:\n    f.write("a\\nb\\nc\\n")\nlineas = 0\nwith open("f.txt", encoding="utf-8") as f:\n    for linea in f:\n        lineas += 1\nprint(lineas, f.closed)',
            "3 True",
            ["3 False", "4 True", "1 True"],
            "`for linea in f` recorre el fichero línea a línea. Al salir del `with`, el fichero queda cerrado.",
        ),
        pq(
            "prog-142",
            QUE,
            'with open("b.bin", "wb") as f:\n    f.write(bytes([65, 66]))\nwith open("b.bin", "rb") as f:\n    datos = f.read()\nprint(datos, type(datos).__name__)',
            "b'AB' bytes",
            ["AB str", "[65, 66] list", "b'65 66' bytes"],
            "En binario se leen bytes, no cadenas. 65 y 66 son los códigos de «A» y «B».",
        ),
        pq(
            "prog-143",
            QUE,
            'import pickle\ndatos = {"Ana": [8, 9]}\ncopia = pickle.loads(pickle.dumps(datos))\nprint(copia == datos, copia is datos)',
            "True False",
            ["True True", "False False", "False True"],
            "Deserializar crea un clon: tiene el mismo contenido (`==`) pero es otro objeto (`is` es False).",
        ),
        pq(
            "prog-144",
            "DB-API con sqlite3. " + QUE,
            'import sqlite3\ncon = sqlite3.connect(":memory:")\ncur = con.cursor()\ncur.execute("CREATE TABLE alumnos (nombre TEXT, edad INTEGER)")\ncur.execute("INSERT INTO alumnos VALUES (?, ?)", ("Ana", 20))\ncon.commit()\nfila = cur.execute("SELECT nombre, edad FROM alumnos").fetchone()\nprint(fila[0], fila[1])\ncon.close()',
            "Ana 20",
            ["('Ana', 20)", "Ana", "Error"],
            "`fetchone()` devuelve una fila como tupla. Los `?` reciben los valores de forma segura.",
        ),
        pq(
            "prog-145",
            "Un usuario malintencionado escribe como nombre `' OR '1'='1`. " + QUE,
            'import sqlite3\ncon = sqlite3.connect(":memory:")\ncon.execute("CREATE TABLE usuarios (nombre TEXT)")\ncon.execute("INSERT INTO usuarios VALUES (\'ana\')")\nentrada = "\' OR \'1\'=\'1"\nseguro = con.execute("SELECT COUNT(*) FROM usuarios WHERE nombre = ?", (entrada,)).fetchone()[0]\ninseguro = con.execute(f"SELECT COUNT(*) FROM usuarios WHERE nombre = \'{entrada}\'").fetchone()[0]\nprint(seguro, inseguro)',
            "0 1",
            ["0 0", "1 1", "Error"],
            "Con parámetros, la entrada se trata como texto y no coincide con nadie. Concatenada, la condición `OR '1'='1'` es siempre verdadera: inyección SQL.",
        ),
        pq(
            "prog-146",
            QUE,
            'from pathlib import Path\nruta = Path("datos") / "notas.txt"\nprint(ruta.name, ruta.suffix, ruta.parent.name)',
            "notas.txt .txt datos",
            ["notas .txt datos", "datos/notas.txt txt datos", "Error"],
            "`pathlib` trata las rutas como objetos y usa el separador correcto de cada sistema.",
        ),
        tq(
            "prog-147",
            "¿Qué caracteriza al acceso secuencial?",
            [
                "El puntero avanza desde el principio, de uno en uno",
                "Se salta a cualquier posición directamente",
                "Solo sirve para ficheros binarios",
                "Necesita una base de datos",
            ],
            0,
            "En el acceso directo se va a cualquier posición con `seek`.",
        ),
        tq(
            "prog-148",
            "¿Qué diferencia hay entre SAX y DOM para leer XML?",
            [
                "SAX lee por eventos, poco a poco; DOM carga el documento entero como un árbol",
                "SAX escribe y DOM lee",
                "DOM es solo para JSON",
                "Son lo mismo",
            ],
            0,
            "SAX gasta poca memoria pero no permite volver atrás; DOM permite ir a cualquier nodo.",
        ),
        tq(
            "prog-149",
            "¿Qué modo de apertura crea el fichero o lo vacía si ya existe?",
            ["w", "a", "r", "x"],
            0,
            "`a` añade al final, `r` solo lee y `x` falla si el fichero ya existe.",
        ),
        tq(
            "prog-150",
            "¿Qué estándar define la forma de acceder a bases de datos desde Python?",
            ["DB-API, en el PEP 249", "PEP 8", "JDBC", "ODBC de Python 2"],
            0,
            "Por eso sqlite3, mysql.connector o psycopg2 se usan casi igual: conexión, cursor, execute, fetch y commit.",
        ),
    ],
    quiz=[
        tq(
            "prog-q20",
            "¿Qué garantiza `with open(...) as f:`?",
            [
                "Que el fichero se cierra al salir del bloque, aunque haya un error",
                "Que no habrá errores",
                "Que el fichero existe",
                "Que se lee en binario",
            ],
            0,
            "No captura las excepciones: para eso hace falta `try`.",
        ),
        tq(
            "prog-q21",
            "¿Por qué hay que pasar los datos a SQL como parámetros?",
            [
                "Para evitar la inyección SQL",
                "Porque es más corto",
                "Porque SQLite no acepta texto",
                "Para no tener que hacer commit",
            ],
            0,
            "El driver trata el parámetro como dato, nunca como parte de la sentencia.",
        ),
    ],
    sources=[
        APUNTES,
        TUTORIAL,
        ("sqlite3 — DB-API 2.0 para SQLite", "https://docs.python.org/es/3/library/sqlite3.html"),
    ],
)

# ================================================================ UT9

L_UT9 = Lesson(
    slug="prog-ut9-interfaces",
    title="UT9 · Interfaces gráficas con Qt (PySide6)",
    theory="""
**Interfaz de usuario:** el espacio donde interactúan la persona y la máquina. Una **GUI** lo hace con ventanas, iconos y controles en vez de la línea de comandos. Debe ser fácil de usar, eficiente y agradable (diseño centrado en el usuario; en español, IPO: interacción persona-ordenador).

**Elementos de una GUI:** **contenedores** (agrupan componentes y los colocan con un *layout*), **componentes o widgets** (botones, cajas de texto, listas, menús), ventanas, barras de menú y **diálogos**.

**Programación dirigida por eventos:** el orden de ejecución lo deciden los **eventos** (un clic, una tecla, un temporizador). Hay una **fuente** (el control cuyo estado cambia), un **objeto evento** con la información, y un **oyente u objetivo** registrado en la fuente, que lo gestiona con una función *callback*. En Qt: un control emite una **señal** y se conecta a un **slot**: `boton.clicked.connect(self.saludar)`.

**Librerías:** Qt, GTK, wxWidgets, Tkinter. El curso usa **Qt con PySide6** (la mantiene la propia empresa de Qt; **PyQt** es de otra empresa: se puede usar cualquiera, pero no mezclarlas). **Tkinter** viene con Python y es sencilla, pero tiene menos controles. Qt tiene muchos widgets, señales y slots, **Qt Designer** para diseñar ventanas y una curva de aprendizaje mayor.

**Esquema de un programa PySide6:**
- `app = QApplication(sys.argv)`;
- una clase que hereda de `QWidget` o `QMainWindow` y crea los controles en su `__init__`;
- `ventana.show()`;
- `sys.exit(app.exec())`, que entra en el **bucle de eventos** (en versiones antiguas, `exec_()`).

**Módulos:** `QtWidgets` (ventanas y controles), `QtCore` (señales, temporizadores, tipos básicos), `QtGui` (iconos, fuentes, colores y, en Qt6, `QAction`). Los apuntes ponen algunos widgets en `QtGui`: eso era en Qt4; en PySide6 están en `QtWidgets`.

**Controles:** `QPushButton` (`clicked`), `QLineEdit` (`textChanged`, `text()`), `QLabel`, `QCheckBox` (`stateChanged`), `QRadioButton` (`isChecked()`), `QComboBox`, `QSlider` (`valueChanged`), `QProgressBar`, `QTableWidget`. Dentro de un slot, `self.sender()` devuelve el control que emitió la señal.

**QMainWindow:** barra de menús (`menuBar()`), barra de herramientas, barra de estado (`statusBar().showMessage(...)`) y widget central. **Diálogos:** `QMessageBox`, `QInputDialog`, `QFileDialog`, `QColorDialog`.

**Eventos de la ventana:** se tratan **sobrescribiendo métodos**, como `closeEvent(self, event)`, con `event.accept()` o `event.ignore()`.

**Layouts:** posicionamiento absoluto con `move(x, y)` (no se adapta al redimensionar ni a otras fuentes o sistemas) o, mejor, gestores: `QHBoxLayout`, `QVBoxLayout` y `QGridLayout` (`addWidget(widget, fila, columna)`).
""",
    example="""
# Sin ventana: la misma idea de señales y slots en Python puro
class Boton:
    def __init__(self, texto):
        self.texto = texto
        self._oyentes = []

    def connect(self, funcion):          # registrar un oyente
        self._oyentes.append(funcion)

    def click(self):                     # el usuario pulsa: se emite la señal
        for funcion in self._oyentes:
            funcion(self)


def saludar(fuente):
    print(f"Has pulsado «{fuente.texto}»")


aceptar = Boton("Aceptar")
aceptar.connect(saludar)
aceptar.click()
""",
    exercise="""
Con PySide6 (`pip install pyside6`), crea una ventana con:

- un `QLineEdit` donde escribir un número;
- un `QLabel` que diga «Par» o «Impar» cada vez que cambie el texto (`textChanged`);
- un `QGridLayout` para colocarlos.

Si el texto no es un número, la etiqueta debe decir «No es un número».
""",
    starter="import sys\nfrom PySide6.QtWidgets import QApplication, QGridLayout, QLabel, QLineEdit, QWidget\n\n\nclass Ventana(QWidget):\n    def __init__(self):\n        super().__init__()\n        # ...\n",
    hint="Conecta `self.entrada.textChanged.connect(self.comprobar)` y en `comprobar` usa `try: n = int(texto) except ValueError: ...`.",
    faq=[
        (
            "¿PySide6 o PyQt6?",
            "Son casi iguales. El curso usa PySide6 (licencia LGPL, de la empresa de Qt). No mezcles las dos en un mismo proyecto.",
        ),
        (
            "¿`exec()` o `exec_()`?",
            "En PySide6 se usa `app.exec()`. `exec_()` viene de cuando `exec` era palabra reservada en Python 2 y está obsoleto.",
        ),
    ],
    challenge=(
        "Login",
        3,
        "Ventana de inicio de sesión que lea usuarios de un fichero `usuario:clave`, oculte la contraseña (`setEchoMode(QLineEdit.EchoMode.Password)`) y muestre el resultado con un `QMessageBox`.",
        "from PySide6.QtWidgets import QLineEdit, QMessageBox\n",
        "Carga los usuarios en un diccionario al abrir la ventana. En un proyecto real, las contraseñas nunca se guardan en claro: se guarda su hash.",
    ),
    questions=[
        tq(
            "prog-151",
            "¿Qué es la programación dirigida por eventos?",
            [
                "Aquella en la que el orden de ejecución lo deciden los eventos, como los clics del usuario",
                "Un programa que se ejecuta de arriba abajo sin esperar",
                "Un tipo de bucle for",
                "Programar sin funciones",
            ],
            0,
            "El programa espera en un bucle de eventos y reacciona llamando a las funciones asociadas.",
        ),
        tq(
            "prog-152",
            "En el modelo de eventos, ¿quién gestiona el evento?",
            [
                "El oyente (objetivo), registrado en la fuente, mediante una callback",
                "La fuente, sin avisar a nadie",
                "El sistema operativo siempre",
                "El layout",
            ],
            0,
            "La fuente es el control cuyo estado cambia; el objeto evento lleva la información.",
        ),
        tq(
            "prog-153",
            "¿Qué ventaja tiene Tkinter frente a Qt?",
            [
                "Viene incluida con Python y su API es sencilla",
                "Tiene muchos más widgets avanzados",
                "Incluye Qt Designer",
                "Solo funciona en Windows",
            ],
            0,
            "Qt ofrece más controles, señales y slots y Qt Designer, a cambio de más curva de aprendizaje.",
        ),
        tq(
            "prog-154",
            "¿Qué diferencia hay entre PySide6 y PyQt6?",
            [
                "PySide6 la mantiene la empresa de Qt y PyQt otra empresa; se puede usar cualquiera, sin mezclarlas",
                "PySide6 es para Tkinter",
                "PyQt no usa señales",
                "PySide6 solo sirve para juegos",
            ],
            0,
            "Las dos envuelven la misma biblioteca Qt con una API casi idéntica.",
        ),
        kq(
            "prog-155",
            "¿Qué hace esta línea?",
            "self.boton.clicked.connect(self.saludar)",
            [
                "Conecta la señal clicked del botón con el método saludar, que se ejecutará en cada clic",
                "Ejecuta saludar una vez al crear el botón",
                "Crea un botón llamado saludar",
                "Cierra la ventana",
            ],
            0,
            "Es el mecanismo de señales y slots de Qt: `señal.connect(función)`. Sin paréntesis, porque se pasa la función, no su resultado.",
        ),
        kq(
            "prog-156",
            "¿Qué hace la última línea?",
            "app = QApplication(sys.argv)\nventana = Ventana()\nventana.show()\nsys.exit(app.exec())",
            [
                "Entra en el bucle de eventos y, al cerrarse, termina el programa con su código de salida",
                "Cierra la ventana inmediatamente",
                "Compila la interfaz",
                "Muestra la ventana por segunda vez",
            ],
            0,
            "El bucle espera eventos y los reparte a los controles hasta que se cierra la aplicación.",
        ),
        kq(
            "prog-157",
            "¿Dónde queda el botón?",
            "layout = QGridLayout()\nlayout.addWidget(etiqueta, 0, 0)\nlayout.addWidget(boton, 1, 2)",
            [
                "En la fila 1, columna 2 (contando desde 0)",
                "En la fila 2, columna 1",
                "En la posición (1, 2) en píxeles",
                "Encima de la etiqueta",
            ],
            0,
            "`addWidget(widget, fila, columna)`, empezando en 0. Se le pueden añadir cuántas filas y columnas ocupa.",
        ),
        tq(
            "prog-158",
            "¿Qué inconveniente tiene el posicionamiento absoluto con move(x, y)?",
            [
                "No se adapta al redimensionar la ventana ni a otras fuentes o sistemas",
                "No se puede usar en Qt",
                "Es más lento de ejecutar",
                "Borra los widgets",
            ],
            0,
            "Por eso se prefieren los layouts: QHBoxLayout, QVBoxLayout y QGridLayout.",
        ),
        kq(
            "prog-159",
            "Varios botones están conectados a este mismo método. ¿Qué devuelve `self.sender()`?",
            "def boton_pulsado(self):\n    boton = self.sender()\n    self.resultado.setText(boton.text())",
            [
                "El control que emitió la señal: el botón pulsado",
                "Siempre el primer botón",
                "La ventana principal",
                "None",
            ],
            0,
            "Así un solo slot sirve para toda una calculadora: se mira el texto del botón pulsado.",
        ),
        kq(
            "prog-160",
            "¿Qué ocurre si el usuario pulsa No?",
            'def closeEvent(self, event):\n    respuesta = QMessageBox.question(self, "Salir", "¿Seguro?")\n    if respuesta == QMessageBox.StandardButton.Yes:\n        event.accept()\n    else:\n        event.ignore()',
            [
                "La ventana no se cierra",
                "La ventana se cierra igualmente",
                "El programa lanza una excepción",
                "Se abre otra ventana",
            ],
            0,
            "Los eventos de la propia ventana se tratan sobrescribiendo métodos como `closeEvent`; `ignore()` cancela el cierre.",
        ),
        kq(
            "prog-161",
            "¿Cuándo se llama a `self.actualizar`?",
            "self.entrada = QLineEdit()\nself.entrada.textChanged.connect(self.actualizar)",
            [
                "Cada vez que cambia el texto de la caja",
                "Solo al pulsar Intro",
                "Al cerrar la ventana",
                "Una sola vez al crearla",
            ],
            0,
            "`textChanged` se emite con cada cambio y pasa el texto nuevo al slot. Para reaccionar solo a Intro está `returnPressed`.",
        ),
        tq(
            "prog-162",
            "En PySide6, ¿en qué módulo están QPushButton, QLineEdit y QMainWindow?",
            ["QtWidgets", "QtGui", "QtCore", "QtSql"],
            0,
            "Los apuntes los ponen en QtGui en algunos ejemplos, que es de Qt4. En Qt6, QtGui tiene iconos, fuentes y QAction; QtCore, señales y temporizadores.",
        ),
        pq(
            "prog-163",
            "Simulación en Python puro de una señal con dos oyentes. " + QUE,
            """
class Senal:
    def __init__(self):
        self.oyentes = []

    def connect(self, funcion):
        self.oyentes.append(funcion)

    def emit(self, valor):
        for funcion in self.oyentes:
            funcion(valor)

clicked = Senal()
clicked.connect(lambda v: print("Guardar", v))
clicked.connect(lambda v: print("Registrar", v))
clicked.emit(1)
""",
            "Guardar 1\nRegistrar 1",
            ["Guardar 1", "Registrar 1\nGuardar 1", "Error"],
            "Una señal puede tener varios oyentes: al emitirse, se llama a todos en el orden en que se conectaron.",
        ),
    ],
    quiz=[
        tq(
            "prog-q22",
            "¿Cómo se llama en Qt el mecanismo que une un evento con la función que lo atiende?",
            ["Señales y slots", "Try y except", "Getters y setters", "Import y from"],
            0,
            "`control.señal.connect(slot)`.",
        ),
        tq(
            "prog-q23",
            "¿Qué layout coloca los widgets en filas y columnas?",
            ["QGridLayout", "QHBoxLayout", "QVBoxLayout", "move(x, y)"],
            0,
            "QHBoxLayout los pone en horizontal y QVBoxLayout en vertical.",
        ),
    ],
    sources=[APUNTES, PYSIDE],
)

BLOCKS = [
    Block(
        "prog-ut1",
        "UT1 · Introducción y algoritmos",
        "Historia, software, paradigmas, algoritmos, diagramas de flujo, pseudocódigo, complejidad y ciclo de vida.",
        8,
        [L_UT1],
    ),
    Block(
        "prog-ut2",
        "UT2 · Elementos de un programa",
        "Python, sintaxis, E/S, identificadores, operadores, literales, cadenas y variables.",
        12,
        [L_UT2],
    ),
    Block(
        "prog-ut3",
        "UT3 · Estructuras de control y funciones",
        "if, match, for, while, break, continue, depuración, docstrings, funciones y ámbitos.",
        20,
        [L_UT3_CONTROL, L_UT3_FUNCIONES],
    ),
    Block(
        "prog-ut4",
        "UT4 · POO",
        "Clases, objetos, encapsulación, abstracción, herencia, relaciones, sobrecarga y polimorfismo.",
        8,
        [L_UT4],
    ),
    Block(
        "prog-ut5",
        "UT5 · POO en Python (I)",
        "Clases, propiedades, parámetros, módulos, cadenas y expresiones regulares.",
        15,
        [L_UT5_CLASES, L_UT5_MODULOS],
    ),
    Block(
        "prog-ut6",
        "UT6 · POO en Python (II) y estructuras de datos",
        "Listas, tuplas, diccionarios, conjuntos, recursividad, herencia, excepciones y estructuras.",
        17,
        [L_UT6_COLECCIONES, L_UT6_HERENCIA],
    ),
    Block(
        "prog-ut7",
        "UT7 · Proyecto",
        "El juego de los códigos secretos: sumatorio, productorio, factorial, primos y random.",
        5,
        [L_UT7],
    ),
    Block(
        "prog-ut8",
        "UT8 · Gestión de datos",
        "Ficheros de texto y binarios, with, pickle, pathlib, bases de datos con DB-API y XML.",
        10,
        [L_UT8],
    ),
    Block(
        "prog-ut9",
        "UT9 · Interfaces gráficas",
        "Eventos, señales y slots, PySide6, controles, diálogos y layouts.",
        5,
        [L_UT9],
    ),
]

if __name__ == "__main__":
    main("programacion", BLOCKS, run_python, check_example)
