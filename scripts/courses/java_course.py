# ruff: noqa: E501
# (contenido didáctico: los textos largos van en una sola línea para poder leerlos y editarlos)
"""Curso de Java (módulo Programación de DAW) para la app Android (ADR-0016).

Cada pregunta de código se compila y ejecuta con el `java` del sistema (Java 17 en la CI) y su salida
se compara con la esperada.

- Si el código contiene `class Main`, es un programa completo.
- Si no, son sentencias que se ejecutan dentro de un `main` (con `import java.util.*;`).

Formato de salida: lo que imprime el programa; «(sin salida)» si no imprime nada;
«Error de compilación» si no compila; «Excepción: Nombre» si termina con una excepción (tras lo
que hubiera impreso antes).
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from course_builder import Block, Lesson, Q, main  # noqa: E402

# ---------------------------------------------------------------- ejecución

LAUNCHER = (
    "class Lanzador { public static void main(String[] a) throws Exception { Main.main(a); } }\n"
)
EXCEPTION = re.compile(r'Exception in thread "main" ([\w.$]+)')


def run_java(code: str) -> str:
    imports = [line for line in code.splitlines() if line.startswith("import ")]
    body = "\n".join(line for line in code.splitlines() if not line.startswith("import "))
    if "class Main" not in body:
        indented = "\n".join("        " + line for line in body.splitlines())
        body = f"class Main {{\n    public static void main(String[] args) throws Exception {{\n{indented}\n    }}\n}}\n"
    # El lanzador va primero: en modo «archivo fuente», java ejecuta el main de la primera clase
    source = "import java.util.*;\n" + "\n".join(imports) + "\n" + LAUNCHER + body
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "Programa.java"
        path.write_text(source, encoding="utf-8")
        env = {**os.environ, "LC_ALL": "C.UTF-8"}
        result = subprocess.run(
            ["java", "-Dfile.encoding=UTF-8", "-Dstdout.encoding=UTF-8", str(path)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=env,
            timeout=60,
        )
    out = "\n".join(line.rstrip() for line in result.stdout.strip("\n").splitlines())
    if result.returncode != 0:
        if "compilation failed" in result.stderr:
            return "Error de compilación"
        match = EXCEPTION.search(result.stderr)
        if not match:
            raise RuntimeError(f"fallo inesperado:\n{result.stderr}")
        name = "Excepción: " + match.group(1).rsplit(".", 1)[-1]
        return f"{out}\n{name}" if out else name
    return out or "(sin salida)"


def check_example(code: str) -> None:
    result = run_java(code)
    assert not result.startswith(("Error", "Excepción")), f"el ejemplo falla ({result}):\n{code}"


def cq(id: str, q: str, code: str, expect: str, wrong: list[str], explain: str) -> Q:
    code = code.strip()
    return Q(id=id, q=q, code=code, run=code, expect=expect, wrong=wrong, explain=explain)


def tq(id: str, q: str, options: list[str], answer: int, explain: str) -> Q:
    return Q(id=id, q=q, options=options, answer=answer, explain=explain)


QUE = "¿Qué muestra este código?"
OCURRE = "¿Qué ocurre al compilar y ejecutar este código?"
COMPILA = "Error de compilación"

DOCS = ("The Java Tutorials (Oracle)", "https://docs.oracle.com/javase/tutorial/java/")
API = ("Java SE 17 — API", "https://docs.oracle.com/en/java/javase/17/docs/api/")
JLS = ("Java Language Specification (SE 17)", "https://docs.oracle.com/javase/specs/jls/se17/html/")

# ---------------------------------------------------------------- bloque 1: fundamentos

L_TIPOS = Lesson(
    slug="java-tipos",
    title="Tipos, variables y operadores",
    theory="""
Java es de **tipado estático**: cada variable tiene un tipo que el compilador comprueba antes de ejecutar. Muchos errores se detectan al **compilar**, no al ejecutar.

**Tipos primitivos:** `int` (entero), `long` (entero grande), `double` (decimal), `boolean` (`true`/`false`) y `char` (un carácter entre comillas simples: `'a'`). Existen también `byte`, `short` y `float`. `String` no es primitivo: es una **clase** (siguiente lección).

Con `var` el compilador deduce el tipo (`var n = 5;` es un `int`), pero el tipo sigue siendo fijo.

**Operadores que caen en los exámenes:**
- `/` entre enteros es **división entera**: `7 / 2` da `3`. Si un operando es `double`, da `3.5`.
- `%` es el resto: `7 % 2` da `1`.
- `x++` devuelve el valor **y después** incrementa; `++x` incrementa **y después** devuelve.
- `+` con un `String` **concatena**, y se evalúa de izquierda a derecha: `1 + 2 + "3"` es `"33"`, pero `"1" + 2 + 3` es `"123"`.

**Conversiones (casting):**
- De un tipo pequeño a uno grande es automática: `double d = 5;`.
- Al revés hay que pedirla y se **trunca**: `(int) 9.99` da `9`. Sin el casting, `int n = 3.5;` **no compila**.
- Un `char` es un número: `'a' + 1` da `98`.

`final` declara una constante: `final int MAX = 10;` no se puede reasignar.
""",
    example="""
class Main {
    public static void main(String[] args) {
        int a = 7, b = 2;
        double media = (a + b) / 2.0;
        System.out.println(a / b + " " + a % b + " " + media);
        final int MAX = 10;
        System.out.println("Máximo: " + MAX);
    }
}
""",
    exercise="""
Escribe un programa que, dado un número de segundos (por ejemplo `3725`), muestre las horas, minutos y segundos que representa: `1 h 2 min 5 s`.

Usa solo división entera `/` y resto `%`.
""",
    starter='class Main {\n    public static void main(String[] args) {\n        int total = 3725;\n        int horas = total / 3600;\n        // ...\n        System.out.println(horas + " h ...");\n    }\n}',
    hint="Primero las horas (`total / 3600`), luego lo que sobra (`total % 3600`) repartido en minutos y segundos.",
    faq=[
        (
            "¿`int` o `Integer`?",
            "`int` es el primitivo. `Integer` es su clase envoltorio, necesaria en las colecciones (`ArrayList<Integer>`). Java convierte entre ambos solo (*autoboxing*).",
        ),
        (
            "¿Por qué `0.1 + 0.2` no da exactamente `0.3`?",
            "Porque `double` guarda los decimales en binario y algunos no son exactos. Para dinero se usa `BigDecimal`.",
        ),
    ],
    challenge=(
        "Conversor de temperatura",
        1,
        "Convierte `double celsius = 36.6;` a Fahrenheit (`celsius * 9 / 5 + 32`) y muestra el resultado redondeado a entero con un casting.",
        "class Main {\n    public static void main(String[] args) {\n        double celsius = 36.6;\n        // ...\n    }\n}",
        "Calcula en `double` y convierte al final: `(int) Math.round(f)` redondea; `(int) f` trunca.",
    ),
    questions=[
        cq(
            "java-01",
            QUE,
            'System.out.println(7 / 2 + " " + 7 % 2 + " " + 7 / 2.0);',
            "3 1 3.5",
            ["3.5 1 3.5", "3 1 3", "3 0.5 3.5"],
            "`7 / 2` son dos enteros: división entera, 3. El resto es 1. En `7 / 2.0` hay un `double`, así que da 3.5.",
        ),
        cq(
            "java-02",
            QUE,
            'System.out.println(1 + 2 + "3" + 4 + 5);',
            "3345",
            ["12345", "3312", "15"],
            'De izquierda a derecha: `1 + 2` es la suma 3; al llegar a `"3"` empieza la concatenación: "33", "334", "3345".',
        ),
        cq(
            "java-03",
            QUE,
            'int x = 5;\nint y = x++ + ++x;\nSystem.out.println(x + " " + y);',
            "7 12",
            ["7 11", "6 11", "7 13"],
            "`x++` usa 5 y deja x en 6; `++x` sube a 7 y usa 7. y = 5 + 7 = 12 y x termina en 7.",
        ),
        cq(
            "java-04",
            QUE,
            "double d = 9.99;\nint n = (int) d;\nSystem.out.println(n);",
            "9",
            ["10", "9.99", COMPILA],
            "El casting a `int` **trunca** (quita los decimales), no redondea.",
        ),
        cq(
            "java-05",
            OCURRE,
            "int n = 3.5;\nSystem.out.println(n);",
            COMPILA,
            ["3", "4", "3.5"],
            "Pasar de `double` a `int` puede perder información y Java no lo hace sin un casting explícito: el programa no compila.",
        ),
    ],
    quiz=[
        cq(
            "java-q01",
            QUE,
            "char c = 'a';\nSystem.out.println(c + 1);",
            "98",
            ["b", "a1", COMPILA],
            "Un `char` es un número (el código de 'a' es 97). Sumarle 1 da un `int`: 98. Para obtener 'b' habría que hacer `(char) (c + 1)`.",
        ),
        tq(
            "java-q02",
            "¿Qué tipo usarías para guardar un número de teléfono como 600111222?",
            [
                "String, porque no se opera con él y puede llevar prefijo o ceros delante",
                "int",
                "double",
                "long, siempre",
            ],
            0,
            "Solo se usan tipos numéricos para lo que se calcula. Un teléfono o un código postal son texto.",
        ),
    ],
    sources=[DOCS, JLS],
)

L_STRINGS = Lesson(
    slug="java-strings",
    title="String y sus métodos",
    theory="""
`String` es una **clase**: sus valores son objetos con métodos.

- `length()` da el número de caracteres.
- `charAt(i)` devuelve el carácter de la posición i, que empieza en 0.
- `substring(inicio, fin)` devuelve desde `inicio` hasta `fin` **sin incluirlo**.
- `indexOf("x")` da la posición de la primera aparición, o `-1` si no está.
- `toUpperCase()`, `toLowerCase()`, `trim()` y `replace(a, b)`.

**Inmutables:** ningún método cambia el String original; devuelven uno **nuevo**. `s.toUpperCase();` sin guardar el resultado no hace nada.

**Comparar:**
- `==` compara si dos variables apuntan al **mismo objeto**.
- `equals` compara el **contenido**. Usa siempre `equals` (o `equalsIgnoreCase`).
- Dos literales iguales suelen ser el mismo objeto, pero un `new String("hola")` no lo es.

**Convertir:** `Integer.parseInt("12")` da el `int` 12. Si el texto no es un número, lanza `NumberFormatException`. Al revés, `String.valueOf(12)` o `"" + 12`.

Para construir textos en un bucle, `StringBuilder` evita crear un String nuevo en cada vuelta.
""",
    example="""
class Main {
    public static void main(String[] args) {
        String ciclo = "Desarrollo de Aplicaciones Web";
        System.out.println(ciclo.length());
        System.out.println(ciclo.substring(0, 10).toUpperCase());
        System.out.println(ciclo.indexOf("Web"));
        System.out.println("daw".equals("DAW") + " " + "daw".equalsIgnoreCase("DAW"));
    }
}
""",
    exercise="""
Dado `String email = "ana.garcia@fp.es";`:

1. Muestra el **usuario** (lo que va antes de la `@`).
2. Muestra el **dominio** (lo que va después).
3. Comprueba si termina en `.es`.
""",
    starter='class Main {\n    public static void main(String[] args) {\n        String email = "ana.garcia@fp.es";\n        int arroba = email.indexOf("@");\n        // ...\n    }\n}',
    hint='Con la posición de la arroba: `substring(0, arroba)` y `substring(arroba + 1)`. Para el final, `endsWith(".es")`.',
    faq=[
        (
            "¿Por qué a veces `==` funciona con Strings?",
            "Porque Java reutiliza los literales iguales (*string pool*) y apuntan al mismo objeto. Con textos leídos del usuario o creados con `new`, no. No te fíes: usa `equals`.",
        ),
        (
            '¿`s.equals("x")` o `"x".equals(s)`?',
            "La segunda no falla si `s` es null: evita el `NullPointerException`.",
        ),
    ],
    challenge=(
        "Palíndromo",
        2,
        'Comprueba si una palabra se lee igual al revés (`"reconocer"`), sin distinguir mayúsculas.',
        'class Main {\n    public static void main(String[] args) {\n        String p = "Reconocer";\n        // ...\n    }\n}',
        "`new StringBuilder(p).reverse().toString()` da la palabra invertida; compárala con `equalsIgnoreCase`.",
    ),
    questions=[
        cq(
            "java-06",
            QUE,
            'String s = "Aplicaciones";\nSystem.out.println(s.length() + " " + s.charAt(0) + " " + s.substring(3, 7));',
            "12 A icac",
            ["12 A lica", "11 A icac", "12 p icac"],
            "12 caracteres. `charAt(0)` es el primero (posición 0). `substring(3, 7)` coge las posiciones 3, 4, 5 y 6, porque el 7 no se incluye: A-p-l-**i-c-a-c**-iones.",
        ),
        cq(
            "java-07",
            QUE,
            'String a = "hola";\nString b = new String("hola");\nSystem.out.println((a == b) + " " + a.equals(b));',
            "false true",
            ["true true", "false false", "true false"],
            "`new String` crea otro objeto: `==` compara referencias y da false. `equals` compara el contenido y da true.",
        ),
        cq(
            "java-08",
            QUE,
            'String s = "java";\ns.toUpperCase();\nSystem.out.println(s);',
            "java",
            ["JAVA", "Java", COMPILA],
            "Los String son **inmutables**: `toUpperCase()` devuelve uno nuevo que aquí se pierde. Habría que escribir `s = s.toUpperCase();`.",
        ),
        cq(
            "java-09",
            QUE,
            'System.out.println(Integer.parseInt("12") + Integer.parseInt("3"));',
            "15",
            ["123", "12 3", "Excepción: NumberFormatException"],
            "`parseInt` convierte cada texto en `int` y después se suman: 15.",
        ),
        cq(
            "java-10",
            OCURRE,
            'System.out.println(Integer.parseInt("12a"));',
            "Excepción: NumberFormatException",
            ["12", "0", COMPILA],
            'Compila (el texto podría venir del usuario), pero al ejecutar "12a" no es un número: lanza `NumberFormatException`.',
        ),
    ],
    quiz=[
        cq(
            "java-q03",
            QUE,
            'System.out.println("DAW".indexOf(\'W\') + " " + "DAW".indexOf(\'x\'));',
            "2 -1",
            ["3 0", "2 0", "3 -1"],
            "Las posiciones empiezan en 0: la W está en la 2. Si no aparece, `indexOf` devuelve -1.",
        ),
        tq(
            "java-q04",
            "¿Por qué hay que comparar Strings con `equals` y no con `==`?",
            [
                "`==` compara si son el mismo objeto; `equals` compara el contenido",
                "`==` no compila con Strings",
                "`equals` es más rápido",
                "Son equivalentes",
            ],
            0,
            "Dos textos iguales pueden ser objetos distintos en memoria.",
        ),
    ],
    sources=[DOCS, API],
)

# ---------------------------------------------------------------- bloque 2: control de flujo

L_CONTROL = Lesson(
    slug="java-condicionales",
    title="Condicionales y switch",
    theory="""
**if / else if / else** ejecuta un bloque u otro según una condición `boolean`. En Java la condición tiene que ser **booleana**: `if (x = 5)` no compila, porque es una asignación (`int`), no una comparación (`==`).

**Operadores lógicos:** `&&` (y), `||` (o) y `!` (no). Son de **cortocircuito**: en `a && b`, si `a` es falso, `b` ni se evalúa. Por eso `v != null && v.length > 0` es seguro.

**Operador ternario:** `condición ? valorSiCierto : valorSiFalso`, por ejemplo `int mayor = a > b ? a : b;`.

**switch clásico:** compara un valor con varios `case`. Si olvidas el `break`, la ejecución **sigue** por los case siguientes (*fall-through*). `default` recoge el resto.

**switch con flechas (Java 14+):** sin fall-through y puede devolver un valor:

`String tipo = switch (dia) { case "SAB", "DOM" -> "finde"; default -> "laborable"; };`

`switch` admite `int`, `char`, `String` y `enum`, pero no `double` ni `boolean`.
""",
    example="""
class Main {
    public static void main(String[] args) {
        int nota = 7;
        String texto;
        if (nota >= 9) texto = "Sobresaliente";
        else if (nota >= 7) texto = "Notable";
        else if (nota >= 5) texto = "Aprobado";
        else texto = "Suspenso";
        System.out.println(texto);

        String dia = "DOM";
        String tipo = switch (dia) {
            case "SAB", "DOM" -> "fin de semana";
            default -> "laborable";
        };
        System.out.println(tipo);
    }
}
""",
    exercise="""
Escribe el clásico **FizzBuzz** para un número `n`:

- si es múltiplo de 3 y de 5, muestra `FizzBuzz`;
- si solo de 3, `Fizz`;
- si solo de 5, `Buzz`;
- si no, el número.

Pruébalo con 9, 10, 15 y 7.
""",
    starter="class Main {\n    public static void main(String[] args) {\n        int n = 15;\n        // ...\n    }\n}",
    hint="Comprueba primero el caso más restrictivo (múltiplo de 3 **y** de 5); si no, nunca llegarías a él.",
    faq=[
        (
            "¿switch o if?",
            "`switch` va bien para comparar **un** valor con muchas constantes. Para rangos (`nota >= 5`) o condiciones distintas, usa if.",
        ),
        (
            "¿Qué es el fall-through?",
            "En el switch clásico, sin `break` se ejecutan también los case siguientes. A veces se usa a propósito para agrupar casos; el switch con flechas lo evita.",
        ),
    ],
    challenge=(
        "Días del mes",
        2,
        "Con un `switch` de flechas, devuelve los días de un mes (1-12) de un año no bisiesto.",
        "class Main {\n    public static void main(String[] args) {\n        int mes = 2;\n        int dias = switch (mes) {\n            // ...\n            default -> 0;\n        };\n        System.out.println(dias);\n    }\n}",
        "Agrupa los meses en un solo case: `case 4, 6, 9, 11 -> 30;`.",
    ),
    questions=[
        cq(
            "java-11",
            QUE,
            'int n = 15;\nif (n % 3 == 0 && n % 5 == 0) System.out.println("FizzBuzz");\nelse if (n % 3 == 0) System.out.println("Fizz");\nelse System.out.println(n);',
            "FizzBuzz",
            ["Fizz", "15", "Fizz\nFizzBuzz"],
            "15 es múltiplo de 3 y de 5: se cumple la primera condición y el resto de la cadena `else if` ya no se evalúa.",
        ),
        cq(
            "java-12",
            QUE,
            'int d = 2;\nswitch (d) {\n    case 1: System.out.print("L");\n    case 2: System.out.print("M");\n    case 3: System.out.print("X"); break;\n    default: System.out.print("?");\n}\nSystem.out.println();',
            "MX",
            ["M", "MX?", "LMX"],
            "Entra por `case 2` y, como no hay `break`, sigue por el `case 3` (*fall-through*) hasta el `break`.",
        ),
        cq(
            "java-13",
            QUE,
            'String dia = "SAB";\nString tipo = switch (dia) {\n    case "SAB", "DOM" -> "finde";\n    default -> "laborable";\n};\nSystem.out.println(tipo);',
            "finde",
            ["laborable", COMPILA, "SAB"],
            "El switch con flechas (Java 14+) admite varias etiquetas por caso y devuelve un valor. No tiene fall-through.",
        ),
        cq(
            "java-14",
            QUE,
            "int a = 4, b = 9;\nSystem.out.println(a > b ? a : b);",
            "9",
            ["4", "true", COMPILA],
            "El ternario devuelve `b` porque `a > b` es falso: es una forma corta de calcular el máximo.",
        ),
        cq(
            "java-15",
            OCURRE,
            'int x = 5;\nif (x = 5) {\n    System.out.println("cinco");\n}',
            COMPILA,
            ["cinco", "(sin salida)", "true"],
            "`x = 5` es una asignación y vale 5 (un `int`); un if necesita un `boolean`. En Java no compila, a diferencia de C.",
        ),
    ],
    quiz=[
        cq(
            "java-q05",
            QUE,
            'int[] v = null;\nif (v != null && v.length > 0) System.out.println("lleno");\nelse System.out.println("nada");',
            "nada",
            ["lleno", "Excepción: NullPointerException", COMPILA],
            "`&&` es de cortocircuito: como `v != null` es falso, `v.length` no llega a evaluarse y no hay NullPointerException.",
        ),
        tq(
            "java-q06",
            "En un switch clásico, ¿qué pasa si olvidas un `break`?",
            [
                "Se siguen ejecutando los case siguientes",
                "No compila",
                "Se ejecuta el default",
                "Se sale del switch igualmente",
            ],
            0,
            "Es el *fall-through*: sigue hasta el siguiente `break` o el final del switch.",
        ),
    ],
    sources=[DOCS, JLS],
)

L_BUCLES = Lesson(
    slug="java-bucles-arrays",
    title="Bucles y arrays",
    theory="""
**Bucles:**
- `for (int i = 0; i < n; i++)`: cuando sabes cuántas vueltas das.
- `while (condición)`: mientras se cumpla; puede no ejecutarse **ninguna** vez.
- `do { … } while (condición);`: se ejecuta **al menos una** vez, porque comprueba al final.
- `for (int x : array)`: el *for-each*, que recorre todos los elementos sin índice.
- `break` sale del bucle y `continue` salta a la siguiente vuelta.

**Arrays:** tamaño **fijo**, índices de `0` a `length - 1`.
- `int[] v = new int[3];` se llena con valores por defecto: `0` en números, `false` en boolean y `null` en objetos.
- `int[] v = {4, 8, 15};` crea y rellena a la vez.
- `v.length` es un atributo, sin paréntesis (en String, `length()` es un método).
- Un índice fuera de rango lanza `ArrayIndexOutOfBoundsException`.

**Los arrays son objetos:** `int[] b = a;` no copia el array. `a` y `b` apuntan al **mismo**, y cambiar uno cambia el otro. Para copiar, `Arrays.copyOf(a, a.length)`.

`Arrays.toString(v)` muestra el contenido (`[4, 8, 15]`) y `Arrays.sort(v)` lo ordena.
""",
    example="""
import java.util.Arrays;

class Main {
    public static void main(String[] args) {
        int[] notas = {7, 5, 9, 4, 8};
        int suma = 0, aprobados = 0;
        for (int n : notas) {
            suma += n;
            if (n >= 5) aprobados++;
        }
        Arrays.sort(notas);
        System.out.println(Arrays.toString(notas));
        System.out.println("Media: " + (double) suma / notas.length + ", aprobados: " + aprobados);
    }
}
""",
    exercise="""
Dado un array de enteros:

1. Encuentra el **mayor** y su **posición**.
2. Cuenta cuántos son **pares**.
3. Muéstralo **al revés** sin crear otro array.
""",
    starter="class Main {\n    public static void main(String[] args) {\n        int[] v = {3, 18, 7, 12, 5};\n        int mayor = v[0], pos = 0;\n        // ...\n    }\n}",
    hint="Para recorrerlo al revés: `for (int i = v.length - 1; i >= 0; i--)`.",
    faq=[
        (
            "¿Array o ArrayList?",
            "El array tiene tamaño fijo y admite primitivos. `ArrayList` crece sola y solo guarda objetos (`Integer`, no `int`). Se ve en el bloque de colecciones.",
        ),
        (
            "¿Por qué `System.out.println(v)` muestra algo como `[I@1b6d3586`?",
            "Porque imprime la referencia del objeto array. Para ver el contenido: `Arrays.toString(v)`.",
        ),
    ],
    challenge=(
        "Matriz traspuesta",
        3,
        "Crea una matriz `int[][] m = {{1, 2, 3}, {4, 5, 6}}` y construye su traspuesta de 3×2 con dos bucles anidados.",
        "class Main {\n    public static void main(String[] args) {\n        int[][] m = {{1, 2, 3}, {4, 5, 6}};\n        int[][] t = new int[3][2];\n        // ...\n    }\n}",
        "La traspuesta cambia filas por columnas: `t[j][i] = m[i][j]`.",
    ),
    questions=[
        cq(
            "java-16",
            QUE,
            'for (int i = 0; i < 10; i += 3) System.out.print(i + " ");\nSystem.out.println();',
            "0 3 6 9",
            ["0 3 6", "3 6 9", "0 3 6 9 12"],
            "Empieza en 0 y suma 3 mientras sea menor que 10: 0, 3, 6 y 9. Con 12 ya no entra.",
        ),
        cq(
            "java-17",
            QUE,
            'int[] v = {4, 8, 15};\nint s = 0;\nfor (int x : v) s += x;\nSystem.out.println(s + " " + v.length);',
            "27 3",
            ["27 2", "15 3", "4815 3"],
            "El for-each suma 4 + 8 + 15 = 27; `length` es el número de elementos (3), no el último índice (2).",
        ),
        cq(
            "java-18",
            OCURRE,
            "int[] v = new int[3];\nSystem.out.println(v[3]);",
            "Excepción: ArrayIndexOutOfBoundsException",
            ["0", "null", COMPILA],
            "Un array de 3 posiciones tiene índices 0, 1 y 2. Compila, pero al ejecutar `v[3]` se sale del rango.",
        ),
        cq(
            "java-19",
            QUE,
            "int i = 10;\nwhile (i > 0) {\n    i -= 4;\n}\nSystem.out.println(i);",
            "-2",
            ["2", "0", "-4"],
            "i pasa por 10, 6, 2 y -2. Con -2 la condición `i > 0` es falsa y el bucle termina.",
        ),
        cq(
            "java-20",
            QUE,
            "int n = 5;\ndo {\n    n++;\n} while (n < 3);\nSystem.out.println(n);",
            "6",
            ["5", "3", COMPILA],
            "`do-while` ejecuta el cuerpo **antes** de comprobar la condición: una vuelta como mínimo, aunque `5 < 3` sea falso.",
        ),
    ],
    quiz=[
        cq(
            "java-q07",
            QUE,
            "int[] a = {1, 2, 3};\nint[] b = a;\nb[0] = 99;\nSystem.out.println(a[0]);",
            "99",
            ["1", COMPILA, "0"],
            "`b = a` no copia el array: las dos variables apuntan al mismo objeto.",
        ),
        cq(
            "java-q08",
            QUE,
            "String[] nombres = new String[2];\nSystem.out.println(nombres[0]);",
            "null",
            ["0", "Excepción: NullPointerException", COMPILA],
            "Un array de objetos se inicializa con `null`. Imprimir null no falla; llamar a un método sobre él (`nombres[0].length()`), sí.",
        ),
    ],
    sources=[DOCS, API],
)

# ---------------------------------------------------------------- bloque 3: POO

L_CLASES = Lesson(
    slug="java-clases",
    title="Clases, objetos y constructores",
    theory="""
Una **clase** es una plantilla con **atributos** (datos) y **métodos** (comportamiento). Un **objeto** es una instancia concreta, creada con `new`.

**Constructor:** método especial con el mismo nombre que la clase y sin tipo de retorno. Se ejecuta al hacer `new`.
- Si no escribes ninguno, Java crea uno vacío por defecto. **En cuanto escribes uno**, ese constructor por defecto desaparece.
- Se pueden **sobrecargar** varios constructores con distintos parámetros. Uno puede llamar a otro con `this(…)`, que tiene que ser la primera línea.

**`this`** es el objeto actual. Hace falta cuando un parámetro se llama igual que un atributo: `this.nombre = nombre;`. Sin `this`, asignarías el parámetro a sí mismo.

**Referencias:** una variable de tipo clase guarda una **referencia** al objeto. `Contador b = a;` no crea otro objeto: `a` y `b` son el mismo. Una referencia puede ser `null`, y usarla lanza `NullPointerException`.

**toString():** si lo sobrescribes, `System.out.println(objeto)` muestra tu texto en lugar de algo como `Punto@1b6d3586`.

Los atributos sin inicializar valen `0`, `false` o `null` según su tipo.
""",
    example="""
class Alumno {
    String nombre;
    int nota;

    Alumno(String nombre, int nota) {
        this.nombre = nombre;
        this.nota = nota;
    }

    boolean aprobado() {
        return nota >= 5;
    }

    @Override
    public String toString() {
        return nombre + " (" + nota + ")";
    }
}

class Main {
    public static void main(String[] args) {
        Alumno a = new Alumno("Ana", 8);
        System.out.println(a + " aprobado: " + a.aprobado());
    }
}
""",
    exercise="""
Crea la clase `Producto` con `nombre`, `precio` y `stock`, con:

- un constructor con los tres datos;
- un método `valor()` que devuelva `precio * stock`;
- un `toString()` con el formato `Teclado - 25.0 € x 10`.

Crea dos productos en el main y muestra su valor.
""",
    starter="class Producto {\n    String nombre;\n    double precio;\n    int stock;\n    // constructor, valor() y toString()\n}\n\nclass Main {\n    public static void main(String[] args) {\n        // ...\n    }\n}",
    hint="En el constructor, `this.precio = precio;` distingue el atributo del parámetro.",
    faq=[
        (
            "¿Qué diferencia hay entre clase y objeto?",
            "La clase es el molde (`Alumno`); los objetos, cada alumno concreto creado con `new`. Puede haber miles de objetos de una clase.",
        ),
        (
            "¿Por qué `new Coche()` no compila si mi clase tiene constructor?",
            "Porque al escribir un constructor con parámetros, Java deja de crear el vacío. Si lo necesitas, escríbelo tú también.",
        ),
    ],
    challenge=(
        "Fracciones",
        3,
        "Crea la clase `Fraccion` (numerador y denominador) con un método `sumar(Fraccion otra)` que devuelva una **nueva** fracción, y un `toString()` como `3/4`.",
        "class Fraccion {\n    int num, den;\n    // ...\n}\n\nclass Main {\n    public static void main(String[] args) {\n        System.out.println(new Fraccion(1, 2).sumar(new Fraccion(1, 4)));\n    }\n}",
        "a/b + c/d = (a·d + c·b) / (b·d). Si quieres simplificarla, divide entre el máximo común divisor.",
    ),
    questions=[
        cq(
            "java-21",
            QUE,
            'class Contador {\n    int valor;\n    void sumar() { valor++; }\n}\n\nclass Main {\n    public static void main(String[] args) {\n        Contador a = new Contador();\n        Contador b = a;\n        a.sumar();\n        b.sumar();\n        System.out.println(a.valor + " " + b.valor);\n    }\n}',
            "2 2",
            ["1 1", "1 2", "2 1"],
            "`b = a` copia la **referencia**: solo hay un objeto Contador y se incrementa dos veces.",
        ),
        cq(
            "java-22",
            QUE,
            'class Alumno {\n    String nombre;\n    Alumno(String nombre) {\n        nombre = nombre;\n    }\n}\n\nclass Main {\n    public static void main(String[] args) {\n        System.out.println(new Alumno("Ana").nombre);\n    }\n}',
            "null",
            ["Ana", COMPILA, "(sin salida)"],
            "Sin `this`, `nombre = nombre` asigna el parámetro a sí mismo. El atributo se queda con su valor por defecto: null.",
        ),
        cq(
            "java-23",
            OCURRE,
            "class Coche {\n    String marca;\n    Coche(String marca) { this.marca = marca; }\n}\n\nclass Main {\n    public static void main(String[] args) {\n        Coche c = new Coche();\n        System.out.println(c.marca);\n    }\n}",
            COMPILA,
            ["null", "Excepción: NullPointerException", "Coche"],
            "Al definir `Coche(String marca)`, Java ya no crea el constructor vacío: `new Coche()` no compila.",
        ),
        cq(
            "java-24",
            QUE,
            'class Punto {\n    int x, y;\n    Punto(int x, int y) { this.x = x; this.y = y; }\n    @Override\n    public String toString() { return "(" + x + ", " + y + ")"; }\n}\n\nclass Main {\n    public static void main(String[] args) {\n        System.out.println(new Punto(2, 3));\n    }\n}',
            "(2, 3)",
            ["Punto@1b6d3586", "2 3", COMPILA],
            "`println` llama al `toString()` del objeto. Como está sobrescrito, muestra el texto propio.",
        ),
        cq(
            "java-25",
            OCURRE,
            "class Punto {\n    int x;\n}\n\nclass Main {\n    public static void main(String[] args) {\n        Punto p = null;\n        System.out.println(p.x);\n    }\n}",
            "Excepción: NullPointerException",
            ["0", "null", COMPILA],
            "Compila, pero `p` no apunta a ningún objeto: acceder a `p.x` lanza `NullPointerException`.",
        ),
    ],
    quiz=[
        tq(
            "java-q09",
            "¿Qué es un objeto?",
            [
                "Una instancia concreta de una clase, creada con `new`",
                "Un sinónimo de clase",
                "Un método especial",
                "Un tipo primitivo",
            ],
            0,
            "La clase define; el objeto existe en memoria con sus propios valores.",
        ),
        cq(
            "java-q10",
            QUE,
            "class Caja {\n    int ancho, alto;\n    Caja() { this(1, 1); }\n    Caja(int ancho, int alto) { this.ancho = ancho; this.alto = alto; }\n    int area() { return ancho * alto; }\n}\n\nclass Main {\n    public static void main(String[] args) {\n        System.out.println(new Caja().area() + new Caja(2, 5).area());\n    }\n}",
            "11",
            ["1", "10", "110"],
            "`Caja()` delega en el otro constructor con `this(1, 1)`: área 1. La otra caja tiene área 10. Se suman como enteros: 11.",
        ),
    ],
    sources=[DOCS, JLS],
)

L_ENCAP = Lesson(
    slug="java-encapsulacion",
    title="Encapsulación y static",
    theory="""
**Encapsulación:** los atributos se declaran `private` y se accede a ellos con métodos públicos (**getters** y **setters**). Así la clase **controla** su estado: un setter puede rechazar un saldo negativo o una edad imposible.

**Modificadores de acceso**, de más a menos restrictivo:
- `private`: solo la propia clase;
- sin modificador (*package-private*): las clases del mismo paquete;
- `protected`: el paquete y las subclases;
- `public`: cualquiera.

**`static`** pertenece a la **clase**, no a cada objeto:
- un atributo `static` es **compartido** por todos los objetos, como un contador de instancias;
- un método `static` se llama con el nombre de la clase (`Math.max(a, b)`) y **no puede usar atributos de instancia**, porque no hay un objeto concreto. Por eso desde `main`, que es static, no puedes usar un atributo normal sin crear antes un objeto.

**`final`:**
- en una variable o atributo, no se puede reasignar;
- en un método, no se puede sobrescribir;
- en una clase, no se puede heredar de ella (como `String`).

Una constante típica es `public static final double IVA = 0.21;`.
""",
    example="""
class Cuenta {
    private static int abiertas = 0;
    private final String titular;
    private double saldo;

    Cuenta(String titular) {
        this.titular = titular;
        abiertas++;
    }

    public void ingresar(double cantidad) {
        if (cantidad > 0) saldo += cantidad;
    }

    public double getSaldo() { return saldo; }
    public String getTitular() { return titular; }
    public static int getAbiertas() { return abiertas; }
}

class Main {
    public static void main(String[] args) {
        Cuenta c = new Cuenta("Ana");
        c.ingresar(100);
        c.ingresar(-50);
        System.out.println(c.getTitular() + ": " + c.getSaldo() + " (cuentas abiertas: " + Cuenta.getAbiertas() + ")");
    }
}
""",
    exercise="""
Encapsula la clase `Alumno`:

- `nombre` y `nota` privados;
- un `setNota` que solo acepte valores entre 0 y 10;
- un atributo `static` que cuente cuántos alumnos se han creado.
""",
    starter="class Alumno {\n    private String nombre;\n    private int nota;\n    // static int ...\n    // constructor, getters y setters\n}",
    hint="En el setter: `if (nota >= 0 && nota <= 10) this.nota = nota;`. El contador se incrementa en el constructor.",
    faq=[
        (
            "¿Hace falta un getter y un setter para cada atributo?",
            "No: solo los que otras clases necesiten. Un atributo sin setter es de solo lectura desde fuera, y eso a menudo es lo que quieres.",
        ),
        (
            "¿Por qué `main` es static?",
            "Porque la JVM lo llama sin crear ningún objeto de la clase.",
        ),
    ],
    challenge=(
        "Termostato",
        2,
        "Crea la clase `Termostato` con la temperatura privada, límites `static final` (MIN 15, MAX 30) y métodos `subir()` y `bajar()` que nunca se salgan de los límites.",
        "class Termostato {\n    static final int MIN = 15, MAX = 30;\n    private int temperatura = 20;\n    // ...\n}",
        "`temperatura = Math.min(MAX, temperatura + 1);` mantiene el valor dentro del límite.",
    ),
    questions=[
        cq(
            "java-26",
            QUE,
            'class Ticket {\n    static int emitidos = 0;\n    int numero;\n    Ticket() {\n        emitidos++;\n        numero = emitidos;\n    }\n}\n\nclass Main {\n    public static void main(String[] args) {\n        Ticket a = new Ticket();\n        Ticket b = new Ticket();\n        Ticket c = new Ticket();\n        System.out.println(a.numero + " " + c.numero + " " + Ticket.emitidos);\n    }\n}',
            "1 3 3",
            ["1 1 3", "3 3 3", "1 3 1"],
            "`emitidos` es static: uno solo, compartido, que llega a 3. `numero` es de cada objeto y guarda el valor en el momento de crearlo.",
        ),
        cq(
            "java-27",
            OCURRE,
            "class Cuenta {\n    private double saldo;\n}\n\nclass Main {\n    public static void main(String[] args) {\n        Cuenta c = new Cuenta();\n        c.saldo = 100;\n        System.out.println(c.saldo);\n    }\n}",
            COMPILA,
            ["100.0", "0.0", "Excepción: IllegalAccessException"],
            "`saldo` es private: solo se puede usar dentro de `Cuenta`. Desde `Main` no compila.",
        ),
        cq(
            "java-28",
            QUE,
            "class Cuenta {\n    private double saldo;\n    public void ingresar(double cantidad) {\n        if (cantidad > 0) saldo += cantidad;\n    }\n    public double getSaldo() { return saldo; }\n}\n\nclass Main {\n    public static void main(String[] args) {\n        Cuenta c = new Cuenta();\n        c.ingresar(50);\n        c.ingresar(-20);\n        c.ingresar(30);\n        System.out.println(c.getSaldo());\n    }\n}",
            "80.0",
            ["60.0", "80", "100.0"],
            "El método rechaza la cantidad negativa: 50 + 30 = 80. Es un `double`, así que se imprime 80.0. Eso es la encapsulación: la clase protege su estado.",
        ),
        cq(
            "java-29",
            OCURRE,
            "class Main {\n    int total = 5;\n    public static void main(String[] args) {\n        System.out.println(total);\n    }\n}",
            COMPILA,
            ["5", "0", "null"],
            "`total` es un atributo de instancia y `main` es static: no hay objeto del que leerlo. Habría que hacer `new Main().total`.",
        ),
        tq(
            "java-30",
            "¿Qué modificador permite usar un atributo **solo** desde su propia clase?",
            ["private", "protected", "public", "Sin modificador"],
            0,
            "`private` es el más restrictivo. Sin modificador se permite todo el paquete; `protected` añade las subclases.",
        ),
    ],
    quiz=[
        cq(
            "java-q11",
            OCURRE,
            "final int MAX = 10;\nMAX = 20;\nSystem.out.println(MAX);",
            COMPILA,
            ["20", "10", "Excepción: IllegalStateException"],
            "Una variable `final` no se puede reasignar: el compilador lo impide.",
        ),
        tq(
            "java-q12",
            "¿Para qué se ponen los atributos `private` con getters y setters?",
            [
                "Para que la clase controle cómo se leen y modifican sus datos",
                "Para que el programa vaya más rápido",
                "Porque Java lo exige",
                "Para poder heredar de la clase",
            ],
            0,
            "Es la encapsulación: puedes validar, cambiar la representación interna o hacer un dato de solo lectura sin romper a quien usa la clase.",
        ),
    ],
    sources=[DOCS, JLS],
)

# ---------------------------------------------------------------- bloque 4: herencia

L_HERENCIA = Lesson(
    slug="java-herencia",
    title="Herencia y polimorfismo",
    theory="""
Con `class Perro extends Animal`, `Perro` **hereda** los atributos y métodos de `Animal` y puede añadir más. Java solo permite heredar de **una** clase. Si no pones `extends`, la clase hereda de `Object`.

**Constructores:** el de la subclase llama primero al del padre, con `super(…)` explícito o `super()` implícito. Por eso en una cadena A → B → C los constructores se ejecutan en el orden A, B, C.

**Sobrescritura (override):** la subclase redefine un método del padre con la misma firma. `@Override` pide al compilador que compruebe que de verdad sobrescribes (y no creas uno nuevo por una errata). Con `super.metodo()` llamas a la versión del padre.

**Polimorfismo:**
- Una variable del tipo padre puede apuntar a un objeto hijo: `Animal a = new Perro();`.
- Al llamar a `a.sonido()`, se ejecuta la versión del **objeto real** (Perro), no la del tipo de la variable. Se decide en tiempo de ejecución.
- El **compilador** solo te deja llamar a métodos que existan en el **tipo de la variable**: `a.ladrar()` no compila si `ladrar` solo está en Perro.

**Casting e instanceof:**
- `(Perro) a` convierte la referencia hacia abajo. Si el objeto no es realmente un Perro, lanza `ClassCastException`.
- Compruébalo antes con `a instanceof Perro`.
""",
    example="""
class Empleado {
    protected String nombre;
    Empleado(String nombre) { this.nombre = nombre; }
    double sueldo() { return 1200; }
}

class Jefe extends Empleado {
    Jefe(String nombre) { super(nombre); }
    @Override
    double sueldo() { return super.sueldo() * 1.5; }
}

class Main {
    public static void main(String[] args) {
        Empleado[] plantilla = { new Empleado("Luis"), new Jefe("Ana") };
        for (Empleado e : plantilla) {
            System.out.println(e.nombre + ": " + e.sueldo());
        }
    }
}
""",
    exercise="""
Crea `Vehiculo` con un método `ruedas()` que devuelva 0, y las subclases `Coche` (4) y `Moto` (2), que lo sobrescriben.

En el main, guarda varios vehículos en un array `Vehiculo[]` y suma todas sus ruedas.
""",
    starter="class Vehiculo {\n    int ruedas() { return 0; }\n}\n\n// class Coche extends Vehiculo { ... }\n\nclass Main {\n    public static void main(String[] args) {\n        Vehiculo[] garaje = { /* ... */ };\n    }\n}",
    hint="Gracias al polimorfismo, `v.ruedas()` ejecuta la versión de cada objeto real aunque el array sea de `Vehiculo`.",
    faq=[
        (
            "¿Sobrecarga o sobrescritura?",
            "**Sobrecarga:** mismo nombre y distintos parámetros, en la misma clase. **Sobrescritura:** misma firma, en una subclase, para cambiar el comportamiento.",
        ),
        (
            "¿Para qué sirve `protected`?",
            "Deja usar el atributo a las subclases (y al paquete), pero no a cualquier clase.",
        ),
    ],
    challenge=(
        "Nómina polimórfica",
        2,
        "Añade `Becario extends Empleado`, que cobra la mitad del sueldo base, y calcula el total de una plantilla mixta con un solo bucle.",
        "class Becario extends Empleado {\n    // ...\n}",
        "`return super.sueldo() / 2;` reutiliza el cálculo del padre.",
    ),
    questions=[
        cq(
            "java-31",
            QUE,
            'class Animal { String sonido() { return "..."; } }\nclass Perro extends Animal { @Override String sonido() { return "Guau"; } }\nclass Gato extends Animal { @Override String sonido() { return "Miau"; } }\n\nclass Main {\n    public static void main(String[] args) {\n        Animal[] zoo = { new Perro(), new Gato(), new Animal() };\n        for (Animal a : zoo) System.out.print(a.sonido() + " ");\n        System.out.println();\n    }\n}',
            "Guau Miau ...",
            ["... ... ...", "Guau Miau", COMPILA],
            "Polimorfismo: aunque las variables son de tipo Animal, se ejecuta el método del objeto real de cada posición.",
        ),
        cq(
            "java-32",
            QUE,
            'class A { A() { System.out.print("A"); } }\nclass B extends A { B() { System.out.print("B"); } }\nclass C extends B { C() { System.out.print("C"); } }\n\nclass Main {\n    public static void main(String[] args) {\n        new C();\n        System.out.println();\n    }\n}',
            "ABC",
            ["C", "CBA", "BC"],
            "Cada constructor llama primero a `super()`: se construye de la raíz hacia abajo, A, B y C.",
        ),
        cq(
            "java-33",
            QUE,
            "class Empleado { double sueldo() { return 1000; } }\nclass Jefe extends Empleado {\n    @Override\n    double sueldo() { return super.sueldo() * 1.5; }\n}\n\nclass Main {\n    public static void main(String[] args) {\n        Empleado e = new Jefe();\n        System.out.println(e.sueldo());\n    }\n}",
            "1500.0",
            ["1000.0", "1500", COMPILA],
            "El objeto es un Jefe: se ejecuta su versión, que reutiliza la del padre con `super.sueldo()`. Es un double: 1500.0.",
        ),
        cq(
            "java-34",
            OCURRE,
            'class Animal {}\nclass Perro extends Animal {\n    void ladrar() { System.out.println("Guau"); }\n}\n\nclass Main {\n    public static void main(String[] args) {\n        Animal a = new Perro();\n        a.ladrar();\n    }\n}',
            COMPILA,
            ["Guau", "Excepción: ClassCastException", "(sin salida)"],
            "El compilador solo mira el tipo de la variable (Animal), que no tiene `ladrar()`. Habría que hacer `((Perro) a).ladrar()`.",
        ),
        cq(
            "java-35",
            OCURRE,
            'class Animal {}\nclass Perro extends Animal {}\nclass Gato extends Animal {}\n\nclass Main {\n    public static void main(String[] args) {\n        Animal a = new Gato();\n        Perro p = (Perro) a;\n        System.out.println("ok");\n    }\n}',
            "Excepción: ClassCastException",
            ["ok", COMPILA, "null"],
            "El casting compila (un Animal *podría* ser un Perro), pero al ejecutar el objeto es un Gato: `ClassCastException`. Se evita comprobando antes con `instanceof`.",
        ),
    ],
    quiz=[
        cq(
            "java-q13",
            QUE,
            'class Animal {}\nclass Perro extends Animal {}\n\nclass Main {\n    public static void main(String[] args) {\n        Animal a = new Perro();\n        System.out.println((a instanceof Perro) + " " + (a instanceof Animal));\n    }\n}',
            "true true",
            ["true false", "false true", COMPILA],
            "Un Perro **es** un Animal: `instanceof` es cierto para su clase y para todas sus superclases.",
        ),
        tq(
            "java-q14",
            "¿Qué hace la anotación `@Override`?",
            [
                "Pide al compilador que compruebe que de verdad sobrescribes un método del padre",
                "Hace el método privado",
                "Obliga a las subclases a sobrescribirlo",
                "Nada, es un comentario",
            ],
            0,
            "Si te equivocas en el nombre o en los parámetros, sin `@Override` crearías otro método sin darte cuenta; con ella, no compila.",
        ),
    ],
    sources=[DOCS, JLS],
)

L_ABSTRACT = Lesson(
    slug="java-abstractas-interfaces",
    title="Clases abstractas e interfaces",
    theory="""
**Clase abstracta** (`abstract class Figura`): una clase incompleta que **no se puede instanciar**.
- Puede tener atributos, constructores y métodos normales, además de métodos `abstract` sin cuerpo (`abstract double area();`).
- Las subclases concretas **deben** implementarlos.
- Sirve para compartir código y obligar a completar una parte.

**Interfaz** (`interface Volador`): un **contrato** con los métodos que debe tener quien la implemente.
- Sus métodos son `public abstract` por defecto. Al implementarlos hay que declararlos **public**, porque no se puede reducir la visibilidad.
- Desde Java 8 puede tener métodos `default` (con cuerpo) y `static`.
- Una clase puede implementar **varias** interfaces (`class Pato extends Animal implements Volador, Nadador`), pero heredar de una sola clase.

**¿Cuál usar?**
- Clase abstracta cuando las subclases comparten estado o código ("es un").
- Interfaz para una capacidad que pueden tener clases sin relación ("puede hacer"): `Comparable`, `Runnable`…

Ninguna de las dos se instancia con `new`. Sí se pueden usar como **tipo** de variable (`Figura f = new Cuadrado(3);`), y ahí está la gracia del polimorfismo.
""",
    example="""
interface Pagable {
    double importe();
    default String recibo() { return "Total: " + importe(); }
}

abstract class Figura {
    abstract double area();
}

class Cuadrado extends Figura implements Pagable {
    private final double lado;
    Cuadrado(double lado) { this.lado = lado; }
    double area() { return lado * lado; }
    public double importe() { return area() * 10; }
}

class Main {
    public static void main(String[] args) {
        Cuadrado c = new Cuadrado(3);
        System.out.println(c.area());
        System.out.println(c.recibo());
    }
}
""",
    exercise="""
Crea la clase abstracta `Figura` con el método abstracto `area()` y un método normal `describir()` que devuelva `"Área: " + area()`.

Implementa `Circulo` y `Rectangulo` y muestra la descripción de ambos desde un array `Figura[]`.
""",
    starter='abstract class Figura {\n    abstract double area();\n    String describir() { return "Área: " + area(); }\n}\n\n// class Circulo extends Figura { ... }',
    hint="Para el área del círculo usa `Math.PI * r * r`.",
    faq=[
        (
            "¿Una interfaz puede tener atributos?",
            "Solo constantes: todo atributo de una interfaz es `public static final`.",
        ),
        (
            "¿Qué es una clase anónima?",
            "Una implementación sin nombre, creada al vuelo: `Volador v = new Volador() { public void volar() { … } };`. Con interfaces de un solo método se suele usar una lambda.",
        ),
    ],
    challenge=(
        "Ordenar con Comparable",
        3,
        "Haz que `Alumno` implemente `Comparable<Alumno>` para ordenar por nota y usa `Arrays.sort` sobre un array de alumnos.",
        "class Alumno implements Comparable<Alumno> {\n    String nombre;\n    int nota;\n    // ...\n    public int compareTo(Alumno otro) {\n        // ...\n    }\n}",
        "`compareTo` devuelve negativo, 0 o positivo: `return Integer.compare(nota, otro.nota);`.",
    ),
    questions=[
        cq(
            "java-36",
            OCURRE,
            "abstract class Figura {\n    abstract double area();\n}\n\nclass Main {\n    public static void main(String[] args) {\n        Figura f = new Figura();\n        System.out.println(f.area());\n    }\n}",
            COMPILA,
            ["0.0", "null", "Excepción: InstantiationException"],
            "Una clase abstracta no se puede instanciar con `new`: el compilador lo impide.",
        ),
        cq(
            "java-37",
            QUE,
            'abstract class Figura {\n    abstract double area();\n    String describir() { return "Superficie: " + area(); }\n}\n\nclass Cuadrado extends Figura {\n    double lado;\n    Cuadrado(double lado) { this.lado = lado; }\n    double area() { return lado * lado; }\n}\n\nclass Main {\n    public static void main(String[] args) {\n        System.out.println(new Cuadrado(3).describir());\n    }\n}',
            "Superficie: 9.0",
            ["Superficie: 9", COMPILA, "Superficie: 0.0"],
            "`describir()` está en la clase abstracta, pero llama a `area()`, que se resuelve en el objeto real (Cuadrado): 3 × 3 = 9.0.",
        ),
        cq(
            "java-38",
            QUE,
            'interface Saludador {\n    String nombre();\n    default String saludar() { return "Hola, " + nombre(); }\n}\n\nclass Robot implements Saludador {\n    public String nombre() { return "R2"; }\n}\n\nclass Main {\n    public static void main(String[] args) {\n        System.out.println(new Robot().saludar());\n    }\n}',
            "Hola, R2",
            ["Hola, null", COMPILA, "R2"],
            "Los métodos `default` tienen cuerpo en la interfaz y los heredan quienes la implementan.",
        ),
        cq(
            "java-39",
            OCURRE,
            'interface Volador {\n    void volar();\n}\n\nclass Pajaro implements Volador {\n    void volar() { System.out.println("vuela"); }\n}\n\nclass Main {\n    public static void main(String[] args) {\n        new Pajaro().volar();\n    }\n}',
            COMPILA,
            ["vuela", "(sin salida)", "Excepción: AbstractMethodError"],
            "Los métodos de una interfaz son public. Implementarlo sin `public` reduce su visibilidad y no compila.",
        ),
        tq(
            "java-40",
            "¿Cuál es una diferencia entre clase abstracta e interfaz en Java?",
            [
                "Una clase solo hereda de una clase, pero puede implementar varias interfaces",
                "Las interfaces se pueden instanciar",
                "Las clases abstractas no pueden tener métodos con cuerpo",
                "Las interfaces pueden tener constructores",
            ],
            0,
            "Por eso las interfaces sirven para dar varias capacidades a una misma clase.",
        ),
    ],
    quiz=[
        tq(
            "java-q15",
            "¿Se puede crear un objeto de una interfaz con `new`?",
            [
                "No; se crean objetos de clases que la implementan (o de una clase anónima)",
                "Sí, siempre",
                "Solo si tiene métodos default",
                "Solo si no tiene métodos",
            ],
            0,
            "La interfaz es un contrato, no una implementación. Sí se usa como tipo de variable.",
        ),
        cq(
            "java-q16",
            QUE,
            "interface Forma { double area(); }\nclass Cuadrado implements Forma { public double area() { return 4; } }\nclass Triangulo implements Forma { public double area() { return 3; } }\n\nclass Main {\n    public static void main(String[] args) {\n        Forma[] formas = { new Cuadrado(), new Triangulo() };\n        double total = 0;\n        for (Forma f : formas) total += f.area();\n        System.out.println(total);\n    }\n}",
            "7.0",
            ["7", "43", COMPILA],
            "La interfaz sirve de tipo común: el bucle suma 4 + 3 sin saber qué clase es cada objeto.",
        ),
    ],
    sources=[DOCS, JLS],
)

# ---------------------------------------------------------------- bloque 5: colecciones y excepciones

L_COLECCIONES = Lesson(
    slug="java-colecciones",
    title="ArrayList y HashMap",
    theory="""
Las **colecciones** (`java.util`) crecen solas, al contrario que los arrays. Solo guardan **objetos**: `ArrayList<Integer>`, nunca `ArrayList<int>`. Java convierte entre `int` e `Integer` automáticamente (*autoboxing*).

**ArrayList** (lista ordenada con índice):
- `add(x)` añade al final y `add(i, x)` inserta en la posición i;
- `get(i)`, `set(i, x)` y `size()`;
- `contains(x)` e `indexOf(x)`.
- **Cuidado con `remove`:** en una `ArrayList<Integer>`, `remove(1)` borra la **posición** 1, y `remove(Integer.valueOf(1))` borra el **valor** 1.
- `List.of(1, 2, 3)` crea una lista **inmutable**; para modificarla, cópiala en un `new ArrayList<>(…)`.

**HashMap** (pares clave → valor, sin claves repetidas):
- `put(clave, valor)` guarda o sustituye;
- `get(clave)` devuelve el valor, o **`null`** si la clave no existe;
- `getOrDefault(clave, porDefecto)`, `containsKey` y `remove`;
- se recorre con `for (var e : mapa.entrySet())`.
- El orden de un `HashMap` **no está garantizado**. `LinkedHashMap` mantiene el de inserción y `TreeMap` ordena por clave.

**No modifiques una lista mientras la recorres con for-each:** lanza `ConcurrentModificationException`. Usa `removeIf(x -> …)` o un `Iterator`.
""",
    example="""
import java.util.*;

class Main {
    public static void main(String[] args) {
        List<String> alumnos = new ArrayList<>(List.of("Ana", "Luis", "Eva"));
        alumnos.add("Juan");
        alumnos.removeIf(n -> n.startsWith("L"));
        System.out.println(alumnos + " " + alumnos.size());

        Map<String, Integer> notas = new TreeMap<>();
        notas.put("Ana", 8);
        notas.put("Eva", 9);
        notas.put("Ana", 10);
        System.out.println(notas + " " + notas.getOrDefault("Juan", 0));
    }
}
""",
    exercise="""
Cuenta cuántas veces aparece cada palabra en una frase y muéstralo ordenado alfabéticamente:

`"el perro y el gato y el raton"` → `{el=3, gato=1, perro=1, raton=1, y=2}`
""",
    starter='import java.util.*;\n\nclass Main {\n    public static void main(String[] args) {\n        String frase = "el perro y el gato y el raton";\n        Map<String, Integer> cuenta = new TreeMap<>();\n        for (String p : frase.split(" ")) {\n            // ...\n        }\n        System.out.println(cuenta);\n    }\n}',
    hint="`cuenta.put(p, cuenta.getOrDefault(p, 0) + 1);` suma uno a la cuenta de cada palabra.",
    faq=[
        (
            "¿`List` o `ArrayList` en la declaración?",
            "`List<String> l = new ArrayList<>();` es lo habitual: programas contra la interfaz y podrías cambiar la implementación sin tocar el resto.",
        ),
        (
            "¿HashMap o TreeMap?",
            "HashMap es más rápido, pero no garantiza el orden. TreeMap mantiene las claves ordenadas.",
        ),
    ],
    challenge=(
        "Agenda",
        2,
        "Con un `HashMap<String, String>` de nombre → teléfono, añade tres contactos, actualiza uno, borra otro y muestra el resto ordenado por nombre.",
        "import java.util.*;\n\nclass Main {\n    public static void main(String[] args) {\n        Map<String, String> agenda = new HashMap<>();\n        // ...\n    }\n}",
        "Para mostrarlo ordenado, `new TreeMap<>(agenda)` crea una copia con las claves en orden.",
    ),
    questions=[
        cq(
            "java-41",
            QUE,
            'ArrayList<String> l = new ArrayList<>();\nl.add("a");\nl.add("b");\nl.add("c");\nl.remove(1);\nl.add(0, "z");\nSystem.out.println(l + " " + l.size());',
            "[z, a, c] 3",
            ["[z, a, b, c] 4", "[a, c, z] 3", "[z, b, c] 3"],
            '`remove(1)` quita la posición 1 ("b") y `add(0, "z")` inserta al principio.',
        ),
        cq(
            "java-42",
            QUE,
            "ArrayList<Integer> n = new ArrayList<>(List.of(10, 20, 30));\nn.remove(1);\nn.remove(Integer.valueOf(10));\nSystem.out.println(n);",
            "[30]",
            ["[20, 30]", "[10, 30]", "[30, 10]"],
            "`remove(1)` borra la **posición** 1 (el 20); `remove(Integer.valueOf(10))` borra el **valor** 10. Queda [30].",
        ),
        cq(
            "java-43",
            QUE,
            'Map<String, Integer> votos = new TreeMap<>();\nfor (String v : new String[]{"rojo", "azul", "rojo", "rojo"}) {\n    votos.put(v, votos.getOrDefault(v, 0) + 1);\n}\nSystem.out.println(votos);',
            "{azul=1, rojo=3}",
            ["{rojo=3, azul=1}", "{azul=1, rojo=1}", "[azul, rojo]"],
            "`getOrDefault` da 0 la primera vez; cada voto suma 1. TreeMap ordena las claves alfabéticamente.",
        ),
        cq(
            "java-44",
            QUE,
            'Map<String, Integer> m = new HashMap<>();\nm.put("a", 1);\nSystem.out.println(m.get("b"));',
            "null",
            ["0", "Excepción: NoSuchElementException", COMPILA],
            "`get` de una clave inexistente devuelve null, sin excepción. Si lo guardas en un `int`, entonces sí fallaría (NullPointerException).",
        ),
        cq(
            "java-45",
            OCURRE,
            "List<Integer> l = new ArrayList<>(List.of(1, 2, 3, 4));\nfor (Integer x : l) {\n    if (x == 2) l.remove(x);\n}\nSystem.out.println(l);",
            "Excepción: ConcurrentModificationException",
            ["[1, 3, 4]", "[1, 2, 3, 4]", COMPILA],
            "Modificar una lista mientras la recorres con for-each lanza `ConcurrentModificationException`. Lo correcto es `l.removeIf(x -> x == 2)`.",
        ),
    ],
    quiz=[
        cq(
            "java-q17",
            OCURRE,
            "ArrayList<int> l = new ArrayList<>();\nl.add(1);\nSystem.out.println(l);",
            COMPILA,
            ["[1]", "[]", "Excepción: ClassCastException"],
            "Las colecciones solo guardan objetos: hay que usar la clase envoltorio `Integer`.",
        ),
        tq(
            "java-q18",
            "¿Qué colección usarías para guardar el teléfono de cada alumno y buscarlo por su nombre?",
            ["HashMap<String, String>", "ArrayList<String>", "String[]", "ArrayList<Integer>"],
            0,
            "Buscar por una clave es exactamente lo que hace un mapa, y es mucho más rápido que recorrer una lista.",
        ),
    ],
    sources=[DOCS, API],
)

L_EXCEPCIONES = Lesson(
    slug="java-excepciones",
    title="Excepciones",
    theory="""
Una **excepción** es un error en tiempo de ejecución. Si nadie la captura, el programa termina y muestra la traza (*stack trace*).

```
try { … código que puede fallar … }
catch (ArithmeticException e) { … si falla de esa manera … }
finally { … se ejecuta SIEMPRE, falle o no … }
```

- Después de una excepción, el resto del bloque `try` **no** se ejecuta: salta al `catch` que corresponda.
- `finally` se ejecuta incluso si el try hace `return`. Se usa para cerrar recursos (o, mejor, *try-with-resources*).
- **Orden de los catch:** del más específico al más general. Poner `catch (Exception e)` antes de `catch (ArithmeticException e)` **no compila**, porque el segundo sería inalcanzable.
- Varios tipos en un catch: `catch (IOException | NumberFormatException e)`.

**Jerarquía:** `Throwable` se divide en `Error` (fallos graves de la JVM) y `Exception`.
- Las `RuntimeException` (`NullPointerException`, `ArithmeticException`, `ArrayIndexOutOfBoundsException`…) son **no comprobadas**: no hace falta declararlas.
- El resto de `Exception` (`IOException`…) son **comprobadas**: o las capturas o las declaras con `throws` en el método. Si no, **no compila**.

**Lanzar las tuyas:** `throw new IllegalArgumentException("mensaje");`. Una excepción propia hereda de `Exception` (comprobada) o de `RuntimeException` (no comprobada). `e.getMessage()` devuelve el mensaje.
""",
    example="""
class Main {
    static int dividir(int a, int b) {
        if (b == 0) throw new IllegalArgumentException("El divisor no puede ser 0");
        return a / b;
    }

    public static void main(String[] args) {
        try {
            System.out.println(dividir(10, 2));
            System.out.println(dividir(1, 0));
            System.out.println("Esto no se ejecuta");
        } catch (IllegalArgumentException e) {
            System.out.println("Error: " + e.getMessage());
        } finally {
            System.out.println("Fin");
        }
    }
}
""",
    exercise="""
Escribe un método `leerEdad(String texto)` que:

- convierta el texto a `int` con `Integer.parseInt`;
- lance `IllegalArgumentException` si la edad es negativa o mayor que 120.

En el main, pruébalo con `"25"`, `"abc"` y `"-3"` y captura cada error mostrando un mensaje claro.
""",
    starter='class Main {\n    static int leerEdad(String texto) {\n        int edad = Integer.parseInt(texto);\n        // ...\n        return edad;\n    }\n\n    public static void main(String[] args) {\n        for (String t : new String[]{"25", "abc", "-3"}) {\n            try {\n                System.out.println(leerEdad(t));\n            } catch (Exception e) {\n                // ...\n            }\n        }\n    }\n}',
    hint="`NumberFormatException` es una subclase de `IllegalArgumentException`: si quieres mensajes distintos, captúrala **antes**.",
    faq=[
        (
            "¿Comprobada o no comprobada?",
            "Comprobada (`extends Exception`) si quien llama puede y debe recuperarse, como un archivo que no existe. No comprobada (`extends RuntimeException`) para errores de programación, como un argumento inválido.",
        ),
        (
            "¿Está bien un `catch (Exception e) {}` vacío?",
            "Casi nunca: se traga el error y no te enteras. Como mínimo, registra el mensaje.",
        ),
    ],
    challenge=(
        "Excepción propia",
        3,
        "Crea `SaldoInsuficienteException extends Exception` y un método `retirar(double cantidad)` en `Cuenta` que la lance con un mensaje que indique cuánto falta. Captúrala en el main.",
        "class SaldoInsuficienteException extends Exception {\n    SaldoInsuficienteException(String mensaje) { super(mensaje); }\n}",
        "Como es comprobada, `retirar` tiene que declarar `throws SaldoInsuficienteException`.",
    ),
    questions=[
        cq(
            "java-46",
            QUE,
            'try {\n    int[] v = new int[2];\n    v[5] = 1;\n    System.out.println("A");\n} catch (ArrayIndexOutOfBoundsException e) {\n    System.out.println("B");\n} finally {\n    System.out.println("C");\n}\nSystem.out.println("D");',
            "B\nC\nD",
            ["A\nC\nD", "B\nD", "B\nC"],
            '`v[5]` lanza la excepción: "A" no llega a imprimirse. La captura el catch (B), después va finally (C) y el programa sigue (D).',
        ),
        cq(
            "java-47",
            QUE,
            'class Main {\n    static int f() {\n        try {\n            return 1;\n        } finally {\n            System.out.println("finally");\n        }\n    }\n    public static void main(String[] args) {\n        System.out.println(f());\n    }\n}',
            "finally\n1",
            ["1\nfinally", "1", "finally"],
            "`finally` se ejecuta antes de que el método termine, aunque haya un `return`. Luego el main imprime el valor devuelto.",
        ),
        cq(
            "java-48",
            OCURRE,
            'try {\n    System.out.println(10 / 0);\n} catch (Exception e) {\n    System.out.println("general");\n} catch (ArithmeticException e) {\n    System.out.println("division");\n}',
            COMPILA,
            ["general", "division", "general\ndivision"],
            "`Exception` ya captura `ArithmeticException`, así que el segundo catch es inalcanzable: no compila. El orden correcto va de específico a general.",
        ),
        cq(
            "java-49",
            OCURRE,
            'class Main {\n    static void leer() throws Exception {\n        throw new Exception("fallo");\n    }\n    public static void main(String[] args) {\n        leer();\n    }\n}',
            COMPILA,
            ["Excepción: Exception", "fallo", "(sin salida)"],
            "`Exception` es **comprobada**: `main` tiene que capturarla con try/catch o declarar `throws Exception`. Si no, no compila.",
        ),
        cq(
            "java-50",
            QUE,
            'class SaldoInsuficiente extends Exception {\n    SaldoInsuficiente(String mensaje) { super(mensaje); }\n}\n\nclass Main {\n    static void retirar(double saldo, double cantidad) throws SaldoInsuficiente {\n        if (cantidad > saldo) throw new SaldoInsuficiente("Faltan " + (cantidad - saldo) + " euros");\n    }\n    public static void main(String[] args) {\n        try {\n            retirar(50, 80);\n        } catch (SaldoInsuficiente e) {\n            System.out.println(e.getMessage());\n        }\n    }\n}',
            "Faltan 30.0 euros",
            ["Faltan 30 euros", "SaldoInsuficiente", "Excepción: SaldoInsuficiente"],
            "La excepción propia guarda el mensaje con `super(mensaje)` y el catch lo recupera con `getMessage()`. La resta de dos double da 30.0.",
        ),
    ],
    quiz=[
        cq(
            "java-q19",
            QUE,
            'try {\n    String s = null;\n    System.out.println(s.length());\n} catch (NullPointerException e) {\n    System.out.println("sin texto");\n}',
            "sin texto",
            ["0", "null", "Excepción: NullPointerException"],
            "Llamar a un método sobre null lanza `NullPointerException`, que aquí se captura.",
        ),
        tq(
            "java-q20",
            "¿Cuál de estas excepciones es **comprobada** (obliga a capturarla o declararla)?",
            [
                "IOException",
                "NullPointerException",
                "ArithmeticException",
                "ArrayIndexOutOfBoundsException",
            ],
            0,
            "Las otras tres heredan de `RuntimeException` y no son comprobadas.",
        ),
    ],
    sources=[DOCS, API],
)

BLOCKS = [
    Block("java-basico", "Fundamentos", "Tipos, operadores y String.", 20, [L_TIPOS, L_STRINGS]),
    Block(
        "java-control",
        "Control de flujo",
        "Condicionales, switch, bucles y arrays.",
        25,
        [L_CONTROL, L_BUCLES],
    ),
    Block(
        "java-poo",
        "Clases y objetos",
        "Constructores, encapsulación y static.",
        25,
        [L_CLASES, L_ENCAP],
    ),
    Block(
        "java-herencia",
        "Herencia e interfaces",
        "Polimorfismo, clases abstractas e interfaces.",
        20,
        [L_HERENCIA, L_ABSTRACT],
    ),
    Block(
        "java-colecciones",
        "Colecciones y excepciones",
        "ArrayList, HashMap y tratamiento de errores.",
        10,
        [L_COLECCIONES, L_EXCEPCIONES],
    ),
]

if __name__ == "__main__":
    main("java", BLOCKS, run_java, check_example)
