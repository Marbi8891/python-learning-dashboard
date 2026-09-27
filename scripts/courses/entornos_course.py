# ruff: noqa: E501
# (contenido didáctico: los textos largos van en una sola línea para poder leerlos y editarlos)
"""Curso de Entornos de desarrollo (módulo 0487 de DAW) para la app Android (ADR-0016, ADR-0019).

Sigue la UD1 «Desarrollo de software» del temario del centro. Casi todo es teoría. Las preguntas
con salida se ejecutan con Python, igual que los ejemplos, y se comprueba que la salida real es
la esperada. Las preguntas sobre fragmentos en otros lenguajes (Java, C, C++) no se ejecutan:
preguntan qué es el código, no lo que muestra.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from course_builder import Block, Lesson, Q, main  # noqa: E402

# ---------------------------------------------------------------- ejecución


def run_python(code: str) -> str:
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, timeout=10, check=False
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
    """Pregunta sobre un fragmento de código que no se ejecuta (qué lenguaje, qué paradigma…)."""
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
    """Ordenar líneas de un programa de Python."""
    return Q(id=id, q=q, code="___", expect=expect, explain=explain, kind="order", lines=lines)


QUE = "¿Qué muestra este código de Python?"

PY = ("Documentación oficial de Python", "https://docs.python.org/es/3/tutorial/")
JAVA = ("The Java Tutorials (Oracle)", "https://docs.oracle.com/javase/tutorial/")
SCRUM = (
    "La Guía Scrum (en español)",
    "https://scrumguides.org/docs/scrumguide/v2020/2020-Scrum-Guide-Spanish-European.pdf",
)
DOCKER = ("Docker — Get started", "https://docs.docker.com/get-started/")

# ---------------------------------------------------------------- lecciones

L_LENGUAJES = Lesson(
    slug="ent-lenguajes-y-programas",
    title="Lenguajes de programación y programas",
    theory="""
Un **lenguaje de programación** es un sistema para escribir instrucciones que el ordenador pueda ejecutar. Cada uno tiene su **sintaxis** (reglas de escritura). El mismo «Hola, mundo» se escribe distinto en cada lenguaje:

- Python: `print("Hola, mundo!")`
- Java: `System.out.println("Hola, mundo!");`
- C++: `std::cout << "Hola, mundo!" << std::endl;`
- JavaScript: `console.log("Hola, mundo!");`

**Los más usados:**
- **Java:** multiplataforma (el mismo programa funciona en distintos sistemas operativos). Aplicaciones empresariales, bancarias y Android. Su sintaxis es más estricta.
- **Python:** sintaxis sencilla, ideal para empezar. Web, análisis de datos, IA y automatización. Menos rendimiento que C++.
- **C++:** alto rendimiento y control de recursos. Videojuegos y software de sistemas. Más complejo.
- **JavaScript:** el lenguaje de la web en el navegador. Páginas interactivas.

No hay un «mejor» lenguaje: se elige el adecuado para cada proyecto. **Evolución:** C en los 70 (sistemas operativos), Java en los 90 (multiplataforma), Python y JavaScript en la última década (sencillez y flexibilidad).

Un **programa informático** es un conjunto de instrucciones para que el ordenador haga una tarea. Se organiza en bloques: **recibir datos, procesarlos y mostrar resultados**.

**Tipos de software:**
- **De sistema:** gestiona el hardware y los recursos. El sistema operativo (Windows, Linux).
- **De aplicación:** tareas concretas del usuario. Un procesador de textos, una app de pedidos.
- **De desarrollo:** para crear otros programas. Un IDE como Visual Studio o IntelliJ, un compilador.
""",
    example="""
# Un programa: recibe datos, los procesa y muestra el resultado
precios = [25, 15, 180]          # entrada
total = sum(precios) * 1.21      # proceso: suma con IVA
print(f"Total: {total:.2f} €")   # salida
""",
    exercise="""
Escribe un programa en Python que:

1. guarde en una lista las notas `[7, 4, 9, 6]`;
2. calcule la media;
3. muestre `Media: 6.5`.

Marca con comentarios la parte de entrada, la de proceso y la de salida.
""",
    starter="notas = [7, 4, 9, 6]  # entrada\n\n# proceso\n\n# salida\n",
    hint="La media es `sum(notas) / len(notas)`.",
    faq=[
        (
            "¿Un navegador es software de sistema o de aplicación?",
            "De aplicación: lo usas para una tarea concreta. El sistema operativo sobre el que funciona es software de sistema.",
        ),
        (
            "¿Qué lenguaje debería aprender primero?",
            "En DAW trabajarás con Java (Programación), SQL (Bases de datos), HTML/CSS y JavaScript. Python va bien para practicar la lógica.",
        ),
    ],
    challenge=(
        "Elige el lenguaje",
        1,
        "Para cada proyecto, elige un lenguaje y justifícalo: un videojuego 3D exigente, la web interactiva de una tienda, un script que renombra archivos y la app de un banco.",
        "# Videojuego: ...\n# Web de la tienda: ...\n# Script: ...\n# Banco: ...",
        "Rendimiento → C++. Navegador → JavaScript. Sencillez y automatización → Python. Empresa y multiplataforma → Java.",
    ),
    questions=[
        kq(
            "ent-01",
            "¿En qué lenguaje está escrito este fragmento?",
            'System.out.println("Hola, mundo!");',
            ["Java", "Python", "C++", "JavaScript"],
            0,
            "`System.out.println` es la forma de mostrar texto en Java. En JavaScript sería `console.log`.",
        ),
        kq(
            "ent-02",
            "¿En qué lenguaje está escrito este fragmento?",
            'std::cout << "Hola, mundo!" << std::endl;',
            ["C++", "Java", "Python", "JavaScript"],
            0,
            "`std::cout` y el operador `<<` son de C++.",
        ),
        kq(
            "ent-03",
            "¿En qué lenguaje está escrito este fragmento?",
            'console.log("Hola, mundo!");',
            ["JavaScript", "Java", "C++", "Python"],
            0,
            "`console.log` muestra texto en la consola del navegador o de Node.js.",
        ),
        tq(
            "ent-04",
            "¿Qué significa que Java es multiplataforma?",
            [
                "Que el mismo programa puede ejecutarse en distintos sistemas operativos",
                "Que se puede escribir con cualquier editor",
                "Que funciona solo en el navegador",
                "Que no necesita memoria",
            ],
            0,
            "El programa compilado funciona en cualquier sistema con la máquina virtual de Java (JVM).",
        ),
        tq(
            "ent-05",
            "Necesitas el máximo rendimiento para un videojuego. ¿Qué lenguaje de la unidad encaja mejor?",
            ["C++", "Python", "JavaScript", "SQL"],
            0,
            "C++ ofrece alto rendimiento y control de los recursos, a cambio de una sintaxis más compleja.",
        ),
        tq(
            "ent-06",
            "¿Qué desventaja se atribuye a Python frente a C++?",
            [
                "Menor rendimiento",
                "Sintaxis difícil de leer",
                "No sirve para análisis de datos",
                "Solo funciona en Windows",
            ],
            0,
            "Python es fácil de leer y muy versátil, pero suele ser más lento que un lenguaje compilado como C++.",
        ),
        tq(
            "ent-07",
            "El sistema operativo Windows es software…",
            ["de sistema", "de aplicación", "de desarrollo", "de ofimática"],
            0,
            "Gestiona el hardware y los recursos, y permite ejecutar los demás programas.",
        ),
        tq(
            "ent-08",
            "Visual Studio, IntelliJ o un compilador son software…",
            ["de desarrollo", "de sistema", "de aplicación", "de base de datos"],
            0,
            "Están pensados para programadores: escribir, depurar y probar código.",
        ),
        tq(
            "ent-09",
            "Microsoft Word es software…",
            ["de aplicación", "de sistema", "de desarrollo", "de red"],
            0,
            "Sirve para una tarea concreta del usuario: crear documentos.",
        ),
        pq(
            "ent-10",
            QUE,
            'precios = [25, 15, 10]\ntotal = sum(precios)\nprint(f"Total: {total}")',
            "Total: 50",
            ["Total: 25", "Total: {total}", "Error"],
            "Entrada (la lista), proceso (sumar) y salida (print). La `f` delante de las comillas sustituye `{total}` por su valor.",
        ),
        pq(
            "ent-11",
            QUE,
            "notas = [7, 4, 9, 6]\nmedia = sum(notas) / len(notas)\nprint(media)",
            "6.5",
            ["6", "26", "Error"],
            "26 / 4 = 6,5. En Python, `/` siempre da un número decimal.",
        ),
    ],
    quiz=[
        tq(
            "ent-q01",
            "¿Qué es la sintaxis de un lenguaje de programación?",
            [
                "Sus reglas de escritura",
                "La velocidad a la que se ejecuta",
                "El programa que lo traduce",
                "La lista de sus bibliotecas",
            ],
            0,
            "Por eso el mismo «Hola, mundo» se escribe distinto en cada lenguaje.",
        ),
        tq(
            "ent-q02",
            "¿Qué lenguaje es imprescindible para el desarrollo web en el navegador?",
            ["JavaScript", "C++", "Java", "Python"],
            0,
            "Es el que ejecutan los navegadores para hacer las páginas interactivas.",
        ),
    ],
    sources=[PY, JAVA],
)

L_TRADUCCION = Lesson(
    slug="ent-compilar-e-interpretar",
    title="Del código fuente al ejecutable",
    theory="""
El ordenador solo entiende **lenguaje máquina** (ceros y unos). El **código fuente**, el que escribes, hay que traducirlo.

**Etapas en un lenguaje compilado (como C++):**
1. **Código fuente:** `area.cpp`.
2. **Compilación:** el **compilador** (por ejemplo `g++`) comprueba los errores y traduce a **código objeto** (`area.o` o `.obj`), en lenguaje máquina pero aún no ejecutable.
3. **Ensamblado:** en algunos casos, un **ensamblador** convierte el código en instrucciones que el procesador ejecuta.
4. **Enlace (linking):** el **enlazador** une el código objeto con las **librerías** necesarias.
5. **Código ejecutable:** un archivo que el sistema operativo ejecuta directamente (`area.exe` en Windows, un binario en Linux).

**Compilador o intérprete:**
- **Compilador:** traduce **todo** el programa antes de ejecutarlo. Después el ejecutable funciona **sin el código fuente**. C y C++.
- **Intérprete:** traduce y ejecuta **línea a línea** mientras el programa funciona. Si una línea tiene un error, el programa se detiene **al llegar a ella**. Python.
- **Java** combina los dos: `javac` compila a **bytecode** (`.class`) y la **máquina virtual de Java (JVM)** lo ejecuta. Por eso es multiplataforma.

**Virtualización:**
- **Máquina virtual (VM):** simula un ordenador completo, con su propio sistema operativo. Sirve para probar un programa en Linux desde Windows sin tocar el sistema principal.
- **Contenedor** (Docker): aísla el programa **sin simular un sistema operativo completo**. Es más ligero y facilita desplegar y escalar en servidores.
""",
    example="""
# Python es interpretado: las líneas anteriores al error sí se ejecutan
print("Línea 1")
print("Línea 2")
try:
    print(10 / 0)          # aquí se detendría el programa sin el try
except ZeroDivisionError:
    print("Error en la línea 3: el intérprete para aquí")
""",
    exercise="""
Instala Python y, si puedes, un compilador de C (`gcc`).

1. Escribe el mismo programa que sume del 1 al 5 en los dos lenguajes.
2. Ejecuta el de Python con `python suma.py`.
3. Compila el de C con `gcc suma.c -o suma` y ejecuta `./suma`.

Anota qué archivos se generan en cada caso.
""",
    starter="# suma.py\nsuma = 0\nfor i in range(1, 6):\n    suma += i\nprint(suma)\n",
    hint="Python no genera ningún ejecutable: el intérprete lee `suma.py` cada vez. `gcc` genera el ejecutable `suma`, que funciona aunque borres `suma.c`.",
    faq=[
        (
            "¿Python no compila nada?",
            "CPython traduce internamente a bytecode (los `.pyc` de `__pycache__`) y lo interpreta. Para la unidad, se considera un lenguaje interpretado.",
        ),
        (
            "¿Docker sustituye a las máquinas virtuales?",
            "No siempre. Un contenedor comparte el núcleo del sistema anfitrión; si necesitas otro sistema operativo completo, sigue haciendo falta una VM.",
        ),
    ],
    challenge=(
        "Ordena el proceso",
        2,
        "Ordena y explica en una frase cada paso: enlazador, código fuente, ejecutable, compilador, código objeto. Indica qué archivo sale de cada uno en el ejemplo de `area.cpp`.",
        "# 1. Código fuente: area.cpp\n# 2. ...",
        "Fuente (area.cpp) → compilador → objeto (area.o) → enlazador + librerías → ejecutable (area.exe).",
    ),
    questions=[
        tq(
            "ent-12",
            "¿Qué genera el compilador a partir del código fuente en C++?",
            [
                "Código objeto (.o o .obj), que aún no es ejecutable",
                "Directamente el archivo .exe final, siempre",
                "Otra vez el código fuente, pero formateado",
                "Un archivo de texto con los errores",
            ],
            0,
            "Después, el enlazador une el código objeto con las librerías para formar el ejecutable.",
        ),
        tq(
            "ent-13",
            "¿Qué hace el enlazador (linker)?",
            [
                "Une el código objeto con las librerías para formar el ejecutable",
                "Traduce el código fuente línea a línea",
                "Comprueba la sintaxis del código fuente",
                "Crea una máquina virtual",
            ],
            0,
            "Traducir línea a línea es lo que hace un intérprete; comprobar la sintaxis, el compilador.",
        ),
        tq(
            "ent-14",
            "¿Cuál es el orden correcto?",
            [
                "Código fuente → compilación → código objeto → enlace → ejecutable",
                "Código objeto → código fuente → enlace → ejecutable",
                "Enlace → compilación → código fuente → ejecutable",
                "Código fuente → enlace → compilación → código objeto",
            ],
            0,
            "Primero se traduce (compilación) y después se une con las librerías (enlace).",
        ),
        tq(
            "ent-15",
            "¿Qué diferencia hay entre un compilador y un intérprete?",
            [
                "El compilador traduce todo antes de ejecutar; el intérprete traduce y ejecuta línea a línea",
                "El intérprete genera un .exe y el compilador no",
                "El compilador solo sirve para Python",
                "No hay ninguna diferencia",
            ],
            0,
            "Con un compilador obtienes un ejecutable que funciona sin el código fuente. Con un intérprete, necesitas el código y el intérprete cada vez.",
        ),
        kq(
            "ent-16",
            "Python es interpretado. ¿Qué ocurre al ejecutar este programa?",
            'print("A")\nprint("B")\nprint(10 / 0)\nprint("C")',
            [
                "Muestra A y B, y se detiene con un error en la tercera línea",
                "No muestra nada: el error se detecta antes de empezar",
                "Muestra A, B y C",
                "Muestra A, B, un aviso y después C",
            ],
            0,
            "El intérprete ejecuta línea a línea: A y B se muestran y el programa se detiene al llegar a la división por cero. Un compilador de C++ habría encontrado los errores de sintaxis antes de ejecutar nada.",
        ),
        kq(
            "ent-48",
            "¿Qué hace la primera de estas dos órdenes?",
            "javac Main.java\njava Main",
            [
                "Compila Main.java a bytecode (Main.class)",
                "Ejecuta el programa en la JVM",
                "Crea un Main.exe que solo funciona en Windows",
                "Interpreta el código fuente línea a línea",
            ],
            0,
            "`javac` es el compilador de Java y genera bytecode. La segunda orden, `java Main`, lo ejecuta en la máquina virtual (JVM).",
        ),
        kq(
            "ent-49",
            "¿Qué archivo obtienes con esta orden?",
            "g++ area.cpp -o area.exe",
            [
                "El ejecutable area.exe: g++ compila y enlaza en un solo paso",
                "Solo el código objeto area.o",
                "Otra copia de area.cpp",
                "Ninguno: g++ es un intérprete",
            ],
            0,
            "Con `-o`, g++ compila y llama al enlazador. Para quedarte solo con el código objeto se usa `g++ -c area.cpp`, que genera area.o.",
        ),
        pq(
            "ent-17",
            QUE,
            'try:\n    print("A")\n    print(10 / 0)\n    print("B")\nexcept ZeroDivisionError:\n    print("Error controlado")',
            "A\nError controlado",
            ["A\nB\nError controlado", "Error controlado", "Error"],
            "Se ejecuta A; la división por cero salta al `except`, así que B no se muestra. El programa termina bien.",
        ),
        tq(
            "ent-18",
            "¿Cómo se ejecuta un programa Java?",
            [
                "javac lo compila a bytecode (.class) y la máquina virtual de Java (JVM) lo ejecuta",
                "Se interpreta directamente el archivo .java línea a línea, sin compilar",
                "Se compila a un .exe que solo funciona en Windows",
                "Lo ejecuta el navegador",
            ],
            0,
            "El bytecode es el mismo para todos los sistemas: cada sistema tiene su JVM. Por eso Java es multiplataforma.",
        ),
        tq(
            "ent-19",
            "¿Qué diferencia a un contenedor de una máquina virtual?",
            [
                "El contenedor no simula un sistema operativo completo, así que es más ligero",
                "El contenedor simula un ordenador completo con su sistema operativo",
                "La máquina virtual es más ligera que el contenedor",
                "No se pueden ejecutar programas en un contenedor",
            ],
            0,
            "La VM simula un ordenador entero. El contenedor (por ejemplo con Docker) solo aísla el programa y lo que necesita.",
        ),
        tq(
            "ent-20",
            "Quieres probar tu programa en Linux desde un ordenador con Windows sin tocar tu sistema. ¿Qué usarías según la unidad?",
            ["Una máquina virtual", "Un enlazador", "Un fichero plano", "Un compilador de C++"],
            0,
            "La VM ejecuta otro sistema operativo en un entorno aislado.",
        ),
        kq(
            "ent-21",
            "Tras compilar este programa de C++ con g++, ¿necesitas el archivo area.cpp para ejecutar area.exe?",
            "#include <iostream>\nint main() {\n    double r = 2;\n    std::cout << 3.14159 * r * r << std::endl;\n    return 0;\n}",
            [
                "No: el ejecutable funciona sin el código fuente",
                "Sí: el ejecutable lee area.cpp cada vez",
                "Sí: hace falta el intérprete de C++",
                "Solo en Linux",
            ],
            0,
            "Es la gran diferencia con un lenguaje interpretado: el ejecutable ya está en lenguaje máquina.",
        ),
    ],
    quiz=[
        tq(
            "ent-q03",
            "¿Qué entiende directamente el procesador?",
            [
                "El lenguaje máquina",
                "El código fuente en Java",
                "El código en Python",
                "El pseudocódigo",
            ],
            0,
            "Todo lo demás hay que traducirlo con un compilador, un intérprete o ambos.",
        ),
        tq(
            "ent-q04",
            "¿Con qué herramienta se gestionan contenedores?",
            ["Docker", "g++", "javac", "Scrum"],
            0,
            "g++ y javac son compiladores; Scrum es una metodología ágil.",
        ),
    ],
    sources=[PY, JAVA, DOCKER],
)

L_PARADIGMAS = Lesson(
    slug="ent-paradigmas",
    title="Paradigmas de programación",
    theory="""
Un **paradigma** es un estilo de organizar el código para resolver problemas.

**Imperativo:** describe **paso a paso** cómo resolverlo. Secuencias de instrucciones, **variables que cambian** de valor y estructuras de control (`if`, `for`, `while`).

Ejemplo: `suma = 0` y un bucle `for i in range(1, 6): suma += i`.

**Orientado a objetos (POO):** el código se organiza en **clases** (el molde, con **atributos** y **métodos**) y **objetos** (instancias de la clase). Usa herencia y polimorfismo; favorece la reutilización y la modularidad. Ideal para proyectos grandes. Java es el ejemplo típico.

**Funcional:** se basa en **funciones puras** (sin efectos secundarios, no cambian el estado), datos **inmutables** y funciones como «**ciudadanos de primera clase**» (se pasan como argumento o se devuelven). Útil con grandes volúmenes de datos y en sistemas concurrentes.

Ejemplo: `print(sum(range(1, 6)))`, sin bucles ni variables que cambien.

**Declarativo:** dices **qué** quieres, no **cómo** conseguirlo. SQL es el ejemplo: `SELECT nombre FROM estudiantes WHERE edad > 18;` y el SGBD decide cómo buscarlo.

**Paradigmas mixtos:** muchos lenguajes modernos admiten varios. Python permite programar de forma imperativa, orientada a objetos o funcional; Java, desde la versión 8, añade lambdas y streams a la POO.
""",
    example="""
# El mismo problema en tres estilos: sumar del 1 al 5

# Imperativo: pasos y una variable que cambia
suma = 0
for i in range(1, 6):
    suma += i
print(suma)

# Funcional: una función aplicada a los datos, sin variables que cambien
print(sum(range(1, 6)))

# Orientado a objetos: una clase con su estado y sus métodos
class Contador:
    def __init__(self):
        self.total = 0

    def sumar(self, n):
        self.total += n

c = Contador()
for i in range(1, 6):
    c.sumar(i)
print(c.total)
""",
    exercise="""
Calcula el producto de los números del 1 al 5 (debe dar 120):

1. en estilo **imperativo**, con un bucle;
2. en estilo **funcional**, con `math.prod`;
3. en **POO**, con una clase `Multiplicador` que tenga un método `multiplicar(n)`.
""",
    starter="# 1. Imperativo\nproducto = 1\n\n# 2. Funcional\nimport math\n\n# 3. POO\nclass Multiplicador:\n    pass\n",
    hint="El imperativo empieza en 1 (no en 0) y multiplica en el bucle. El funcional es `math.prod(range(1, 6))`.",
    faq=[
        (
            "¿SQL es un lenguaje de programación?",
            "Es un lenguaje declarativo de consulta: describes el resultado y el SGBD decide cómo obtenerlo.",
        ),
        (
            "¿Qué paradigma usaré en Programación?",
            "Sobre todo imperativo y orientado a objetos, con Java. En Entorno cliente, JavaScript mezcla los tres.",
        ),
    ],
    challenge=(
        "Clasifica",
        2,
        "Di qué paradigma predomina en: un bucle while que acumula un total; `SELECT * FROM pedidos WHERE total > 100`; `map(lambda x: x * 2, datos)`; una clase `Coche` con el método `acelerar()`.",
        "# while que acumula: ...\n# SELECT: ...\n# map + lambda: ...\n# clase Coche: ...",
        "Imperativo, declarativo, funcional y orientado a objetos.",
    ),
    questions=[
        kq(
            "ent-22",
            "¿Qué paradigma sigue este código?",
            "suma = 0\nfor i in range(1, 6):\n    suma += i\nprint(suma)",
            ["Imperativo", "Funcional", "Declarativo", "Orientado a objetos"],
            0,
            "Describe los pasos uno a uno con un bucle y una variable que cambia de valor.",
        ),
        kq(
            "ent-23",
            "¿Qué paradigma sigue este código?",
            "print(sum(range(1, 6)))",
            ["Funcional", "Imperativo", "Declarativo", "Orientado a objetos"],
            0,
            "Aplica funciones a los datos sin variables que cambien: estilo funcional.",
        ),
        kq(
            "ent-24",
            "¿Qué paradigma sigue este código?",
            "SELECT nombre FROM estudiantes WHERE edad > 18;",
            ["Declarativo", "Imperativo", "Orientado a objetos", "Funcional"],
            0,
            "Dice qué datos quiere, no cómo buscarlos: eso lo decide el SGBD.",
        ),
        kq(
            "ent-25",
            "¿Qué paradigma sigue este código Java?",
            "class Coche {\n    String marca;\n    int velocidad;\n    void acelerar() { velocidad += 10; }\n}",
            ["Orientado a objetos", "Funcional", "Declarativo", "Ensamblador"],
            0,
            "Define una clase con atributos (marca, velocidad) y un método (acelerar).",
        ),
        pq(
            "ent-26",
            QUE,
            "suma = 0\nfor i in range(1, 6):\n    suma += i\nprint(suma)",
            "15",
            ["10", "5", "Error"],
            "range(1, 6) va del 1 al 5 (el 6 no se incluye): 1 + 2 + 3 + 4 + 5 = 15.",
        ),
        pq(
            "ent-27",
            QUE,
            "class Coche:\n    def __init__(self):\n        self.velocidad = 0\n\n    def acelerar(self):\n        self.velocidad += 10\n\nmi_coche = Coche()\nmi_coche.acelerar()\nmi_coche.acelerar()\nprint(mi_coche.velocidad)",
            "20",
            ["10", "0", "Error"],
            "El objeto guarda su estado: cada llamada a acelerar() suma 10 a su atributo velocidad.",
        ),
        pq(
            "ent-28",
            QUE,
            "def doble(x):\n    return x * 2\n\nnumeros = [1, 2, 3]\nprint(list(map(doble, numeros)))\nprint(numeros)",
            "[2, 4, 6]\n[1, 2, 3]",
            ["[2, 4, 6]\n[2, 4, 6]", "[1, 2, 3]\n[2, 4, 6]", "Error"],
            "La función `doble` se pasa como argumento a `map` (ciudadana de primera clase). La lista original no cambia: es el estilo funcional.",
        ),
        pq(
            "ent-29",
            QUE,
            "total = 0\n\ndef sumar(n):\n    global total\n    total += n\n\nsumar(5)\nsumar(5)\nprint(total)",
            "10",
            ["5", "0", "Error"],
            "Esta función **no es pura**: modifica una variable global (efecto secundario). La programación funcional evita justo esto.",
        ),
        tq(
            "ent-30",
            "¿Qué es una función pura?",
            [
                "La que, con los mismos datos, devuelve siempre lo mismo y no modifica nada fuera de ella",
                "Una función sin parámetros",
                "Una función que solo usa bucles",
                "Una función escrita en C",
            ],
            0,
            "Sin efectos secundarios: no cambia variables globales, ni ficheros, ni la pantalla.",
        ),
        tq(
            "ent-31",
            "En POO, ¿qué es un objeto?",
            [
                "Una instancia concreta de una clase",
                "El molde que define atributos y métodos",
                "Un tipo de bucle",
                "Una función pura",
            ],
            0,
            "La clase es el molde (Coche); el objeto, un coche concreto creado con `new Coche()`.",
        ),
        tq(
            "ent-32",
            "¿Por qué se dice que Python es multiparadigma?",
            [
                "Porque permite programar de forma imperativa, orientada a objetos o funcional",
                "Porque se ejecuta en varios sistemas operativos",
                "Porque tiene compilador e intérprete",
                "Porque se puede usar en la web",
            ],
            0,
            "Ejecutarse en varios sistemas es ser multiplataforma, que es otra cosa.",
        ),
        fq(
            "ent-33",
            "Completa la versión funcional para que muestre 15.",
            "print(___(range(1, 6)))",
            ["sum"],
            "15",
            "`sum` recibe los números del 1 al 5 y devuelve su suma, sin bucles ni variables que cambien.",
        ),
        oq(
            "ent-34",
            "Ordena las líneas de la versión imperativa para que muestre 15.",
            ["suma = 0", "for i in range(1, 6):", "    suma += i", "print(suma)"],
            "15",
            "Primero se inicializa la variable, después el bucle la actualiza y al final se muestra.",
        ),
    ],
    quiz=[
        tq(
            "ent-q05",
            "¿Qué paradigma se centra en «qué» quieres y no en «cómo» conseguirlo?",
            ["Declarativo", "Imperativo", "Orientado a objetos", "Estructurado"],
            0,
            "SQL es el ejemplo típico.",
        ),
        tq(
            "ent-q06",
            "¿Qué conceptos son propios de la POO?",
            [
                "Clases, objetos, herencia y polimorfismo",
                "Funciones puras e inmutabilidad",
                "SELECT, FROM y WHERE",
                "Compilador y enlazador",
            ],
            0,
            "Las funciones puras son del paradigma funcional; SELECT, del declarativo.",
        ),
    ],
    sources=[PY, JAVA],
)

L_FASES = Lesson(
    slug="ent-fases-y-agiles",
    title="Fases del desarrollo y metodologías ágiles",
    theory="""
**Fases del desarrollo de una aplicación:**
1. **Análisis de requisitos:** qué necesita el cliente. **Funcionales** (lo que hace: «permitir hacer un pedido») y **no funcionales** (cómo se comporta: «cargar en menos de 3 segundos»). Entrevistas, encuestas y el documento **ERS** (Especificación de Requisitos de Software).
2. **Diseño:** el **conceptual** define el «qué» (qué módulos habrá) y el **técnico**, el «cómo». Diagramas **UML**, como el de clases.
3. **Codificación:** se escribe el código, limpio y comentado.
4. **Pruebas y depuración:** comprobar que funciona y cumple los requisitos, a mano o automatizadas (**JUnit**, **Selenium**). **Depurar** es encontrar y corregir los errores.
5. **Documentación:** manuales de usuario, guías de instalación y documentación técnica.
6. **Explotación:** se despliega en el **entorno productivo** y se monitoriza.
7. **Mantenimiento:** corregir errores y añadir funciones (un método de pago nuevo).

Las fases están conectadas: un error en el análisis arrastra problemas al diseño, al código y a las pruebas.

**Cascada:** proceso **lineal**: todo el análisis, luego todo el diseño, el código y las pruebas. Funciona si los requisitos están claros desde el principio; se adapta mal a los cambios.

**Metodologías ágiles:** ciclos **cortos e iterativos**, colaboración constante, adaptación al cambio, **entregas incrementales** y retroalimentación continua.
- **Scrum:** **sprints** de 1 a 4 semanas. Roles: **Product Owner** (prioridades y objetivos), **Scrum Master** (que se sigan los principios, quita obstáculos) y **equipo de desarrollo**. El **backlog** es la lista priorizada de tareas; cada día hay una **daily stand-up**.
- **Kanban:** tablero visual con columnas (**Pendiente, En progreso, Completado**) y un **límite de tareas en progreso** para no saturar al equipo.
- **Extreme Programming (XP):** calidad del código: **programación en pareja**, **pruebas continuas** y **entregas frecuentes**.

Herramientas: Trello o Jira para tableros y sprints.
""",
    example="""
# Un tablero Kanban mínimo con límite de tareas en progreso
tablero = {"Pendiente": ["Diseñar la interfaz", "Probar la búsqueda"], "En progreso": [], "Completado": []}
LIMITE = 1

def empezar(tarea):
    if len(tablero["En progreso"]) >= LIMITE:
        print(f"No se puede empezar «{tarea}»: límite de tareas en progreso")
        return
    tablero["Pendiente"].remove(tarea)
    tablero["En progreso"].append(tarea)

empezar("Diseñar la interfaz")
empezar("Probar la búsqueda")
print(tablero)
""",
    exercise="""
Vas a desarrollar la app de reservas de un gimnasio con Scrum.

1. Escribe 3 requisitos funcionales y 2 no funcionales.
2. Crea un backlog de 6 tareas ordenadas por prioridad.
3. Decide qué entra en el primer sprint de 2 semanas y quién hace de Product Owner.
""",
    starter="# Requisitos funcionales\n# 1. ...\n\n# Requisitos no funcionales\n# 1. ...\n\n# Backlog (de más a menos prioridad)\n# 1. ...\n",
    hint="Funcional: «el socio puede reservar una clase». No funcional: «la app funciona en móviles con Android 8 o superior». El primer sprint suele entregar algo pequeño que ya funcione, como el registro de socios.",
    faq=[
        (
            "¿Ágil significa sin documentación?",
            "No. Significa documentar lo necesario y priorizar el software que funciona, con entregas frecuentes que el cliente puede revisar.",
        ),
        (
            "¿Kanban tiene sprints?",
            "No: es un flujo continuo. Los sprints son de Scrum. Muchos equipos usan un tablero Kanban dentro de Scrum.",
        ),
    ],
    challenge=(
        "¿Cascada o ágil?",
        2,
        "Elige metodología para: (1) el software de un marcapasos con requisitos cerrados y certificación; (2) una startup que todavía está descubriendo qué quieren sus clientes. Justifícalo.",
        "# 1. Marcapasos: ...\n# 2. Startup: ...",
        "Requisitos estables y muy regulados → cascada. Mucha incertidumbre y cambios → ágil.",
    ),
    questions=[
        tq(
            "ent-35",
            "«La aplicación debe cargar en menos de tres segundos» es un requisito…",
            ["no funcional", "funcional", "de diseño técnico", "de mantenimiento"],
            0,
            "Describe cómo debe comportarse la aplicación, no qué hace. «Permitir hacer un pedido» sería funcional.",
        ),
        tq(
            "ent-36",
            "¿Qué documento organiza y detalla los requisitos?",
            [
                "La ERS (Especificación de Requisitos de Software)",
                "El backlog de Kanban",
                "El manual de usuario",
                "El diagrama de Gantt",
            ],
            0,
            "Se elabora en la fase de análisis, a partir de entrevistas, encuestas y reuniones con el cliente.",
        ),
        tq(
            "ent-37",
            "¿En qué fase se usan diagramas UML como el de clases?",
            ["Diseño", "Análisis de requisitos", "Explotación", "Mantenimiento"],
            0,
            "En el diseño se decide la estructura de la aplicación. UML permite representarla gráficamente.",
        ),
        tq(
            "ent-38",
            "¿Qué es depurar?",
            [
                "Identificar y corregir los errores del código",
                "Borrar el código que no se usa",
                "Documentar el código",
                "Desplegar la aplicación",
            ],
            0,
            "Forma parte de la fase de pruebas y depuración.",
        ),
        tq(
            "ent-39",
            "Los usuarios piden un nuevo método de pago en una app ya publicada. ¿En qué fase se hace?",
            ["Mantenimiento", "Análisis de requisitos", "Explotación", "Codificación inicial"],
            0,
            "El desarrollo no acaba con el despliegue: corregir errores y añadir funciones es mantenimiento.",
        ),
        tq(
            "ent-40",
            "¿Cuál es el orden correcto de las fases?",
            [
                "Análisis, diseño, codificación, pruebas, documentación, explotación y mantenimiento",
                "Diseño, análisis, pruebas, codificación, explotación y mantenimiento",
                "Codificación, pruebas, análisis, diseño y explotación",
                "Análisis, codificación, diseño, explotación y pruebas",
            ],
            0,
            "Primero se decide qué hay que hacer y cómo, después se construye y se prueba, y por último se pone en marcha y se mantiene.",
        ),
        tq(
            "ent-41",
            "En Scrum, ¿quién define las prioridades y los objetivos del proyecto?",
            [
                "El Product Owner",
                "El Scrum Master",
                "El equipo de desarrollo",
                "El cliente final, en la daily",
            ],
            0,
            "El Scrum Master se asegura de que se siga Scrum y quita obstáculos; el equipo hace el trabajo técnico.",
        ),
        tq(
            "ent-42",
            "¿Cuánto suele durar un sprint de Scrum?",
            [
                "Entre una y cuatro semanas",
                "Un día",
                "Entre seis y doce meses",
                "Lo que dure el proyecto",
            ],
            0,
            "Son ciclos cortos: al final de cada uno se enseña algo que funciona y se recoge la opinión del cliente.",
        ),
        tq(
            "ent-43",
            "¿Qué es el backlog?",
            [
                "La lista de tareas pendientes ordenadas por prioridad",
                "La reunión diaria del equipo",
                "El registro de errores del servidor",
                "El documento de requisitos no funcionales",
            ],
            0,
            "La reunión diaria es la daily stand-up.",
        ),
        tq(
            "ent-44",
            "¿Cuál es una regla principal de Kanban?",
            [
                "Limitar la cantidad de tareas en progreso",
                "Trabajar siempre en sprints de dos semanas",
                "Programar siempre en pareja",
                "No usar tableros",
            ],
            0,
            "Limitar el trabajo en curso mantiene un flujo constante y evita saturar al equipo. Los sprints son de Scrum y la programación en pareja, de XP.",
        ),
        tq(
            "ent-45",
            "¿Qué metodología se centra en la calidad del código con programación en pareja y pruebas continuas?",
            ["Extreme Programming (XP)", "Kanban", "Cascada", "Scrum"],
            0,
            "XP añade además entregas frecuentes de pequeñas partes funcionales.",
        ),
        tq(
            "ent-46",
            "¿Cuándo funciona bien el modelo en cascada?",
            [
                "Cuando los requisitos están muy claros desde el principio y apenas cambian",
                "Cuando los requisitos cambian constantemente",
                "Cuando el cliente quiere ver avances cada semana",
                "Nunca: está prohibido",
            ],
            0,
            "Es lineal: cada fase empieza cuando acaba la anterior, así que los cambios tardíos salen caros.",
        ),
        kq(
            "ent-50",
            "Este tablero organiza el trabajo del equipo. ¿Qué metodología refleja?",
            'Pendiente         | En progreso (máx. 2) | Completado\n"Pagar con tarjeta" | "Registro de socios" | "Pantalla de inicio"\n"Buscar clases"     |                      |',
            ["Kanban", "Cascada", "Extreme Programming", "Scrum sin sprints"],
            0,
            "Columnas por etapa y un límite de tareas en progreso: es un tablero Kanban.",
        ),
        kq(
            "ent-51",
            "¿En qué fase del desarrollo se escribe este código?",
            "@Test\nvoid totalConIva() {\n    assertEquals(121.0, Pedido.total(100.0), 0.001);\n}",
            ["Pruebas", "Análisis de requisitos", "Diseño", "Explotación"],
            0,
            "Es una prueba automatizada con JUnit: comprueba que el cálculo del total cumple lo esperado.",
        ),
        pq(
            "ent-47",
            "Un tablero Kanban con límite de 1 tarea en progreso. ¿Qué muestra este código?",
            'en_progreso = []\nLIMITE = 1\n\ndef empezar(tarea):\n    if len(en_progreso) >= LIMITE:\n        return "Bloqueada: " + tarea\n    en_progreso.append(tarea)\n    return "Empezada: " + tarea\n\nprint(empezar("Diseño"))\nprint(empezar("Pruebas"))',
            "Empezada: Diseño\nBloqueada: Pruebas",
            [
                "Empezada: Diseño\nEmpezada: Pruebas",
                "Bloqueada: Diseño\nEmpezada: Pruebas",
                "Error",
            ],
            "Con el límite de tareas en progreso, no se empieza una tarea nueva hasta terminar la que está en curso.",
        ),
    ],
    quiz=[
        tq(
            "ent-q07",
            "¿Qué caracteriza a las metodologías ágiles?",
            [
                "Ciclos cortos, entregas incrementales y adaptación al cambio",
                "Planificarlo todo al principio y no cambiar nada",
                "No hacer pruebas",
                "Trabajar sin cliente",
            ],
            0,
            "Frente a la cascada, priorizan la colaboración y la retroalimentación continua.",
        ),
        tq(
            "ent-q08",
            "¿Qué herramientas se usan para pruebas automatizadas según la unidad?",
            ["JUnit y Selenium", "Trello y Jira", "Docker y Hadoop", "g++ y javac"],
            0,
            "Trello y Jira sirven para gestionar tareas; Docker, para contenedores; g++ y javac son compiladores.",
        ),
    ],
    sources=[SCRUM, JAVA],
)

BLOCKS = [
    Block(
        "ent-lenguajes",
        "Lenguajes y programas",
        "Lenguajes más usados, programa informático y tipos de software.",
        25,
        [L_LENGUAJES],
    ),
    Block(
        "ent-traduccion",
        "Del código fuente al ejecutable",
        "Compilación, enlace, compiladores, intérpretes, máquinas virtuales y contenedores.",
        25,
        [L_TRADUCCION],
    ),
    Block(
        "ent-paradigmas",
        "Paradigmas de programación",
        "Imperativo, orientado a objetos, funcional, declarativo y mixto.",
        25,
        [L_PARADIGMAS],
    ),
    Block(
        "ent-ciclo-de-vida",
        "Fases del desarrollo y metodologías ágiles",
        "Del análisis al mantenimiento; cascada, Scrum, Kanban y XP.",
        25,
        [L_FASES],
    ),
]

if __name__ == "__main__":
    main("entornos", BLOCKS, run_python, check_example)
