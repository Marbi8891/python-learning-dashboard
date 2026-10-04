# ruff: noqa: E501
"""Ejercicios del núcleo educativo, etiquetados por concepto y por error típico (ADR-0031).

Tipos (`kind`):
- choice: elegir una opción. Cada opción incorrecta puede llevar el error que delata.
- output: escribir lo que muestra un programa (trazado). `expect` se comprueba ejecutándolo;
          `traps` asocia salidas incorrectas frecuentes con su error.
- fill:   completar el hueco `___`. Con `expect`, se ejecuta el código completado.
- order:  ordenar líneas (de código o de pseudocódigo).
- bug:    señalar la línea con el error. Se ejecuta el código corregido (`fix`) y debe dar `expect`.
- code:   escribir el programa. `solution` debe superar los `checks` (los mismos que ve el
          alumno, con runner.py); cada `wrong` es una solución típica equivocada que debe fallar
          en el caso indicado, para asegurar que los tests detectan ese error.

`daw: True` marca los ejercicios con formato de examen de Programación (entran en simulacros).
`level`: 1 comprensión · 2 aplicación · 3 problema completo.
"""

from textwrap import dedent


def c(text: str) -> str:
    return dedent(text).strip("\n")


def choice(
    id, concept, q, options, answer, explain, code=None, level=1, daw=True, code_options=False
):
    return {
        "id": id,
        "concept": concept,
        "kind": "choice",
        "level": level,
        "daw": daw,
        "q": q,
        "code": c(code) if code else None,
        "options": [{"text": t, "error": e} for t, e in options],
        "answer": answer,
        "explain": explain,
        "codeOptions": code_options,
    }


def output(
    id,
    concept,
    code,
    expect,
    explain,
    traps=None,
    q="¿Qué muestra este programa?",
    stdin="",
    level=1,
    daw=True,
):
    return {
        "id": id,
        "concept": concept,
        "kind": "output",
        "level": level,
        "daw": daw,
        "q": q,
        "code": c(code),
        "stdin": stdin,
        "expect": expect,
        "traps": traps or {},
        "explain": explain,
    }


def fill(id, concept, q, code, accept, explain, expect=None, traps=None, level=1, daw=True):
    return {
        "id": id,
        "concept": concept,
        "kind": "fill",
        "level": level,
        "daw": daw,
        "q": q,
        "code": c(code),
        "accept": accept,
        "expect": expect,
        "traps": traps or {},
        "explain": explain,
    }


def order(id, concept, q, lines, explain, expect=None, pseudo=False, error=None, level=2, daw=True):
    return {
        "id": id,
        "concept": concept,
        "kind": "order",
        "level": level,
        "daw": daw,
        "q": q,
        "lines": lines,
        "expect": expect,
        "pseudo": pseudo,
        "error": error,
        "explain": explain,
    }


def bug(id, concept, q, code, line, fix, expect, error, explain, stdin="", level=2, daw=True):
    return {
        "id": id,
        "concept": concept,
        "kind": "bug",
        "level": level,
        "daw": daw,
        "q": q,
        "code": c(code),
        "stdin": stdin,
        "line": line,
        "fix": fix,
        "expect": expect,
        "error": error,
        "explain": explain,
    }


def code(id, concept, q, starter, solution, checks, explain, hint, wrong=(), level=2, daw=True):
    return {
        "id": id,
        "concept": concept,
        "kind": "code",
        "level": level,
        "daw": daw,
        "q": q,
        "starter": c(starter),
        "solution": c(solution),
        "checks": checks,
        "hint": hint,
        "explain": explain,
        "_wrong": [(c(w), case) for w, case in wrong],
    }


def case(test, stdin="", error=None):
    return {"stdin": stdin, "test": c(test), "error": error}


E = []  # todos los ejercicios

# ================================================================== ALGORITMOS
E += [
    choice(
        "alg-01",
        "algoritmos",
        "Enunciado: «Pide el precio de un producto y las unidades, y muestra el total con un 21 % de IVA». ¿Cuál es la **entrada**?",
        [
            ("El precio y las unidades", None),
            ("El total con IVA", "algoritmos.sin-entrada-salida"),
            ("El 21 %", "algoritmos.sin-entrada-salida"),
            ("La multiplicación", "algoritmos.sin-entrada-salida"),
        ],
        0,
        "La entrada son los datos que da el usuario: precio y unidades. El 21 % es una constante del problema y el total es la **salida**.",
    ),
    choice(
        "alg-02",
        "algoritmos",
        "¿Cuál de estos pasos **no** es válido en un algoritmo?",
        [
            ("Repetir hasta que el resultado parezca correcto", None),
            ("Si n es par, dividir n entre 2", "algoritmos.pasos-ambiguos"),
            ("Sumar 1 al contador", "algoritmos.pasos-ambiguos"),
            ("Leer un número entero", "algoritmos.pasos-ambiguos"),
        ],
        0,
        "«Parezca correcto» es ambiguo: el ordenador necesita una condición precisa y comprobable. Los demás pasos son concretos.",
    ),
    choice(
        "alg-03",
        "algoritmos",
        "Un algoritmo calcula la media de las notas dividiendo la suma entre la cantidad. ¿Qué caso límite hay que comprobar?",
        [
            ("Que no haya ninguna nota", None),
            ("Que haya exactamente 3 notas", "algoritmos.sin-caso-limite"),
            ("Que las notas sean enteras", "algoritmos.sin-caso-limite"),
            ("Que la suma sea par", "algoritmos.sin-caso-limite"),
        ],
        0,
        "Sin notas, la cantidad es 0 y la división falla. Los casos límite son los extremos: vacío, 0, negativos, un solo elemento.",
    ),
    order(
        "alg-04",
        "algoritmos",
        "Ordena los pasos del algoritmo para calcular el precio final con descuento.",
        [
            "Leer el precio",
            "Leer el porcentaje de descuento",
            "Calcular descuento ← precio × porcentaje / 100",
            "Calcular final ← precio − descuento",
            "Escribir final",
        ],
        "Primero se leen los datos, después se calculan los valores intermedios en orden (el final usa el descuento) y por último se escribe.",
        pseudo=True,
        error="algoritmos.pasos-ambiguos",
        level=1,
    ),
]

# ================================================================== VARIABLES
E += [
    output(
        "var-01",
        "variables",
        """
        a = 3
        b = a
        a = 10
        print(b)
        """,
        "3",
        "`b = a` copia en `b` el valor que tiene `a` **en ese momento** (3). Cambiar `a` después no afecta a `b`.",
        traps={"10": "variables.orden-asignacion"},
    ),
    output(
        "var-02",
        "variables",
        """
        x = 5
        x = x * 2
        x = x - 3
        print(x)
        """,
        "7",
        "Cada línea evalúa la derecha con el valor actual: 5 × 2 = 10; después 10 − 3 = 7.",
        traps={"2": "variables.orden-asignacion", "5": "variables.orden-asignacion"},
    ),
    output(
        "var-03",
        "variables",
        """
        a = 1
        b = 2
        a = b
        b = a
        print(a, b)
        """,
        "2 2",
        "Tras `a = b`, a vale 2. Entonces `b = a` vuelve a guardar 2 en b. Para **intercambiar** hace falta una variable auxiliar o `a, b = b, a`.",
        traps={"2 1": "variables.orden-asignacion", "1 2": "variables.orden-asignacion"},
        level=2,
    ),
    choice(
        "var-04",
        "variables",
        "¿Qué hace la línea `total == 100`?",
        [
            ("Compara y no guarda nada: el resultado (True o False) se pierde", None),
            ("Guarda 100 en total", "variables.asigna-compara"),
            ("Da un error de sintaxis", "variables.asigna-compara"),
            ("Suma 100 a total", "variables.asigna-compara"),
        ],
        0,
        "`==` pregunta si dos valores son iguales. Como línea suelta no cambia nada. Para guardar el valor se usa un solo `=`.",
    ),
    output(
        "var-05",
        "variables",
        """
        nombre = "Luis"
        print("nombre")
        print(nombre)
        """,
        "nombre\nLuis",
        "Con comillas es el texto literal «nombre»; sin comillas, el valor de la variable.",
        traps={"Luis\nLuis": "variables.nombre-texto", "nombre\nnombre": "variables.nombre-texto"},
    ),
    fill(
        "var-06",
        "variables",
        "Completa para intercambiar los valores de `a` y `b` en una sola línea.",
        """
        a = 1
        b = 2
        a, b = ___
        print(a, b)
        """,
        ["b, a", "b,a", "(b, a)"],
        "La asignación múltiple evalúa primero toda la derecha (2, 1) y después la reparte.",
        expect="2 1",
        level=2,
    ),
]

# ================================================================== TIPOS
E += [
    output(
        "tip-01",
        "tipos",
        """
        a = "4"
        b = "2"
        print(a + b)
        """,
        "42",
        "Son textos: `+` los concatena. Para sumarlos habría que convertirlos con `int()`.",
        traps={"6": "tipos.texto-numero"},
    ),
    output(
        "tip-02",
        "tipos",
        """
        print(7 / 2)
        print(7 // 2)
        print(6 / 2)
        """,
        "3.5\n3\n3.0",
        "`/` siempre devuelve float, aunque la división sea exacta (6 / 2 = 3.0). `//` da el cociente entero.",
        traps={"3.5\n3\n3": "tipos.division-float", "3\n3\n3": "tipos.division-float"},
    ),
    choice(
        "tip-03",
        "tipos",
        '¿Qué ocurre al ejecutar `print("Edad: " + 20)`?',
        [
            ("TypeError: no se puede concatenar str con int", None),
            ("Muestra «Edad: 20»", "tipos.texto-numero"),
            ("Muestra «Edad: »", "tipos.texto-numero"),
            ("Muestra 20", "tipos.texto-numero"),
        ],
        0,
        '`+` entre un str y un int no está definido. Soluciones: `"Edad: " + str(20)` o `f"Edad: {20}"`.',
    ),
    output(
        "tip-04",
        "tipos",
        """
        activo = "False"
        if activo:
            print("entra")
        else:
            print("no entra")
        """,
        "entra",
        '`"False"` es un texto no vacío, y todo texto no vacío cuenta como verdadero. El booleano es `False` sin comillas.',
        traps={"no entra": "tipos.bool-texto"},
        level=2,
    ),
    fill(
        "tip-05",
        "tipos",
        "Completa para que el programa muestre 15.",
        """
        texto = "10"
        print(___(texto) + 5)
        """,
        ["int"],
        "Hay que convertir el texto a número antes de sumar.",
        expect="15",
        traps={"str": "tipos.texto-numero"},
    ),
]

# ================================================================== OPERADORES
E += [
    output(
        "ope-01",
        "operadores",
        "print(2 + 3 * 2 ** 2)",
        "14",
        "Primero la potencia (2 ** 2 = 4), luego la multiplicación (3 × 4 = 12) y por último la suma (2 + 12).",
        traps={
            "100": "operadores.prioridad",
            "20": "operadores.prioridad",
            "38": "operadores.prioridad",
        },
    ),
    output(
        "ope-02",
        "operadores",
        """
        n = 47
        print(n // 10, n % 10)
        """,
        "4 7",
        "`// 10` quita la última cifra (4) y `% 10` se queda con ella (7). Es un truco habitual para separar cifras.",
        traps={"4.7 7": "tipos.division-float", "7 4": "operadores.modulo"},
    ),
    choice(
        "ope-03",
        "operadores",
        '¿Qué condición es verdadera **solo** los fines de semana (`dia` vale "sabado" o "domingo")?',
        [
            ('dia == "sabado" or dia == "domingo"', None),
            ('dia == "sabado" and dia == "domingo"', "operadores.and-or"),
            ('dia == "sabado" or "domingo"', "operadores.and-or"),
            ('dia == ("sabado" and "domingo")', "operadores.and-or"),
        ],
        0,
        'Basta con que se cumpla una de las dos: `or`. Cada lado del `or` debe ser una comparación completa: `dia == "sabado" or "domingo"` siempre es verdadero, porque "domingo" es un texto no vacío.',
        level=2,
        code_options=True,
    ),
    choice(
        "ope-04",
        "operadores",
        "¿Qué expresión comprueba si `n` es múltiplo de 3?",
        [
            ("n % 3 == 0", None),
            ("n / 3 == 0", "operadores.modulo"),
            ("n // 3 == 0", "operadores.modulo"),
            ("n % 3 == 1", "operadores.modulo"),
        ],
        0,
        "Un número es múltiplo de 3 cuando el resto de dividirlo entre 3 es 0.",
        code_options=True,
    ),
    output(
        "ope-05",
        "operadores",
        """
        edad = 15
        print(edad >= 12 and edad < 18)
        print(not edad > 10 or edad == 15)
        """,
        "True\nTrue",
        "15 está entre 12 y 17: True. En la segunda, `not` se aplica a `edad > 10` (False) y después `or edad == 15` es True.",
        traps={"True\nFalse": "operadores.prioridad"},
        level=2,
    ),
    fill(
        "ope-06",
        "operadores",
        "Completa la condición «la nota está entre 0 y 10, ambos incluidos».",
        """
        nota = 10
        print(0 ___ nota <= 10)
        """,
        ["<="],
        "Python permite encadenar comparaciones: `0 <= nota <= 10`.",
        expect="True",
        traps={"<": "operadores.rango-encadenado"},
    ),
]

# ================================================================== ENTRADA Y SALIDA
E += [
    choice(
        "es-01",
        "entrada-salida",
        "El usuario escribe 5. ¿Qué muestra el programa?",
        [
            ("55", None),
            ("10", "entrada-salida.input-texto"),
            ("Error", "entrada-salida.input-texto"),
            ("5", "entrada-salida.input-texto"),
        ],
        0,
        '`input()` devuelve el texto "5" y `n * 2` repite el texto: "55". Para multiplicar hay que convertirlo: `int(input())`.',
        code="""
           n = input("Número: ")
           print(n * 2)
           """,
        level=2,
    ),
    output(
        "es-02",
        "entrada-salida",
        """
        precio = 3.14159
        print(f"Precio: {precio:.2f} €")
        """,
        "Precio: 3.14 €",
        "`:.2f` formatea con 2 decimales (redondeando).",
        traps={"Precio: 3.14159 €": "entrada-salida.formato-salida"},
    ),
    output(
        "es-03",
        "entrada-salida",
        """
        print("A", "B", sep="-", end="!")
        print("C")
        """,
        "A-B!C",
        "`sep` cambia el separador entre valores y `end` lo que se escribe al final (por defecto, un salto de línea). Como el primer print termina en «!», «C» sigue en la misma línea.",
        traps={
            "A-B!\nC": "entrada-salida.formato-salida",
            "A B!C": "entrada-salida.formato-salida",
        },
        level=2,
    ),
    code(
        "es-04",
        "entrada-salida",
        "Pide dos números enteros (cada uno en una línea) y muestra exactamente `Suma: X` con su suma.",
        """
         a = input()
         b = input()
         """,
        """
         a = int(input())
         b = int(input())
         print(f"Suma: {a + b}")
         """,
        [
            case(
                'assert __output__.strip() == "Suma: 7", f"Con 3 y 4 se esperaba «Suma: 7» y tu programa muestra «{__output__.strip()}»"',
                "3\n4\n",
                "entrada-salida.input-texto",
            ),
            case(
                'assert __output__.strip() == "Suma: -1", "Prueba con números negativos: -5 y 4 debe dar «Suma: -1»"',
                "-5\n4\n",
            ),
        ],
        "`input()` devuelve texto: hay que convertir cada dato con `int()` antes de sumar, y respetar el formato exacto de la salida.",
        "Convierte en la misma línea: `a = int(input())`.",
        wrong=[
            (
                """
                 a = input()
                 b = input()
                 print(f"Suma: {a + b}")
                 """,
                1,
            )
        ],
        level=1,
    ),
]

# ================================================================== CONDICIONALES
E += [
    output(
        "con-01",
        "condicionales",
        """
        nota = 10
        if nota >= 5:
            print("Aprobado")
        elif nota >= 9:
            print("Sobresaliente")
        else:
            print("Suspenso")
        """,
        "Aprobado",
        "Se ejecuta la **primera** rama verdadera: `10 >= 5` ya lo es, así que el `elif` ni se mira. Las condiciones deben ir de la más exigente a la más general.",
        traps={
            "Sobresaliente": "condicionales.orden-elif",
            "Aprobado\nSobresaliente": "condicionales.if-separados",
        },
    ),
    output(
        "con-02",
        "condicionales",
        """
        x = 7
        if x > 5:
            print("mayor que 5")
        if x > 3:
            print("mayor que 3")
        """,
        "mayor que 5\nmayor que 3",
        "Son dos `if` independientes: se evalúan los dos y los dos se cumplen.",
        traps={"mayor que 5": "condicionales.if-separados"},
    ),
    output(
        "con-03",
        "condicionales",
        """
        t = 30
        if t > 25:
            print("calor")
        print("fin")
        """,
        "calor\nfin",
        '`print("fin")` no está sangrado: no depende del `if` y se ejecuta siempre.',
        traps={"calor": "condicionales.sangria"},
    ),
    bug(
        "con-04",
        "condicionales",
        "Una nota de 5 debe dar «Aprobado». ¿Qué línea tiene el error?",
        """
        nota = 5
        if nota > 5:
            print("Aprobado")
        else:
            print("Suspenso")
        """,
        2,
        "if nota >= 5:",
        "Aprobado",
        "condicionales.frontera",
        "«Aprobado desde 5» incluye el 5: hace falta `>=`. Los valores frontera son los que más fallan.",
    ),
    code(
        "con-05",
        "condicionales",
        'Escribe la función `clasificar(edad)` que devuelva `"menor"` si la edad es menor de 18, `"adulto"` si está entre 18 y 64 y `"senior"` a partir de 65.',
        """
         def clasificar(edad):
             ...
         """,
        """
         def clasificar(edad):
             if edad < 18:
                 return "menor"
             elif edad < 65:
                 return "adulto"
             else:
                 return "senior"
         """,
        [
            case('assert clasificar(10) == "menor", "clasificar(10) debe devolver \\"menor\\""'),
            case(
                'assert clasificar(18) == "adulto", "18 años ya es \\"adulto\\": revisa la frontera"',
                error="condicionales.frontera",
            ),
            case(
                'assert clasificar(64) == "adulto" and clasificar(65) == "senior", "64 es \\"adulto\\" y 65 ya es \\"senior\\""',
                error="condicionales.frontera",
            ),
            case(
                'assert clasificar(90) == "senior", "clasificar(90) debe devolver \\"senior\\""',
                error="condicionales.orden-elif",
            ),
        ],
        "Una cadena if/elif/else con las fronteras exactas: `< 18`, `< 65` y el resto. Como solo se ejecuta la primera rama verdadera, en el `elif` ya sabemos que la edad es al menos 18.",
        "Empieza por el caso más bajo. En el `elif` no hace falta repetir `edad >= 18`.",
        wrong=[
            (
                """
                 def clasificar(edad):
                     if edad < 18:
                         return "menor"
                     elif edad <= 18:
                         return "adulto"
                     return "senior"
                 """,
                3,
            ),
            (
                """
                 def clasificar(edad):
                     if edad <= 18:
                         return "menor"
                     elif edad < 65:
                         return "adulto"
                     return "senior"
                 """,
                2,
            ),
        ],
    ),
    choice(
        "con-06",
        "condicionales",
        "¿Cuántas ramas de una cadena `if / elif / elif / else` pueden ejecutarse en una misma pasada?",
        [
            ("Exactamente una", None),
            ("Todas las que sean verdaderas", "condicionales.if-separados"),
            ("Ninguna o una", "condicionales.if-separados"),
            ("Depende del número de elif", "condicionales.if-separados"),
        ],
        0,
        "Con `else` siempre se ejecuta exactamente una rama: la primera verdadera o, si ninguna lo es, el `else`. Sin `else` podrían ser cero.",
    ),
]

# ================================================================== BUCLES
E += [
    output(
        "buc-01",
        "bucles",
        """
        for i in range(2, 6):
            print(i, end=" ")
        """,
        "2 3 4 5",
        "`range(2, 6)` empieza en 2 y termina **antes** de 6.",
        traps={"2 3 4 5 6": "bucles.range-fin", "3 4 5": "bucles.uno-de-mas"},
    ),
    output(
        "buc-02",
        "bucles",
        """
        n = 0
        while n < 10:
            n = n + 3
        print(n)
        """,
        "12",
        "La condición se comprueba **antes** de cada vuelta: con n = 9 aún se cumple, se suma 3 y n pasa a 12. Después 12 < 10 es falso y se sale.",
        traps={"9": "bucles.condicion-salida", "10": "bucles.condicion-salida"},
        level=2,
    ),
    output(
        "buc-03",
        "bucles",
        """
        for i in range(10, 0, -3):
            print(i, end=" ")
        """,
        "10 7 4 1",
        "Con paso negativo, `range` cuenta hacia atrás y se detiene antes de llegar a 0.",
        traps={"10 7 4 1 0": "bucles.range-fin", "10 7 4": "bucles.uno-de-mas"},
        level=2,
    ),
    choice(
        "buc-04",
        "bucles",
        'Quieres repetir **hasta que** el usuario escriba "salir". ¿Qué condición va en el `while`?',
        [
            ('while respuesta != "salir":', None),
            ('while respuesta == "salir":', "bucles.condicion-salida"),
            ('while "salir":', "bucles.condicion-salida"),
            ('while respuesta = "salir":', "variables.asigna-compara"),
        ],
        0,
        'El `while` lleva la condición para **seguir**: mientras la respuesta NO sea "salir". «Hasta que X» se escribe `while not X`.',
        code_options=True,
    ),
    bug(
        "buc-05",
        "bucles",
        "Este programa debería mostrar 5, 4, 3, 2, 1 pero no termina nunca. ¿Qué línea falla?",
        """
        n = 5
        while n > 0:
            print(n)
            n + 1
        """,
        4,
        "    n = n - 1",
        "5\n4\n3\n2\n1",
        "bucles.bucle-infinito",
        "`n + 1` calcula un valor pero no lo guarda, y además va en la dirección contraria. Hay que **actualizar** la variable de la condición: `n = n - 1`.",
    ),
    fill(
        "buc-06",
        "bucles",
        "Completa para mostrar los números del 1 al 5, ambos incluidos.",
        """
        for i in range(1, ___):
            print(i)
        """,
        ["6"],
        "`range(a, b)` no incluye b: para llegar a 5 hay que poner 6.",
        expect="1\n2\n3\n4\n5",
        traps={"5": "bucles.range-fin"},
    ),
    output(
        "buc-07",
        "bucles",
        """
        for i in range(1, 10):
            if i % 4 == 0:
                break
            if i % 2 == 0:
                continue
            print(i)
        """,
        "1\n3",
        "Con i = 2 se salta (continue); con i = 3 se muestra; con i = 4 se sale del bucle (break) antes de mostrar nada más.",
        traps={"1\n3\n5\n7\n9": "trazado.intencion", "1\n3\n4": "trazado.intencion"},
        level=3,
    ),
]

# ================================================================== ACUMULADORES
E += [
    output(
        "acu-01",
        "acumuladores",
        """
        for n in [3, 5, 2]:
            suma = 0
            suma = suma + n
        print(suma)
        """,
        "2",
        "`suma = 0` está **dentro** del bucle: se reinicia en cada vuelta y solo queda el último valor (0 + 2).",
        traps={"10": "acumuladores.inicializa-dentro"},
    ),
    bug(
        "acu-02",
        "acumuladores",
        "Debería calcular 1 × 2 × 3 × 4 = 24, pero muestra 0. ¿Qué línea falla?",
        """
        producto = 0
        for i in range(1, 5):
            producto = producto * i
        print(producto)
        """,
        1,
        "producto = 1",
        "24",
        "acumuladores.producto-cero",
        "Un producto acumulado empieza en 1 (el elemento neutro de la multiplicación). Empezar en 0 hace que todo dé 0.",
    ),
    output(
        "acu-03",
        "acumuladores",
        """
        notas = [8, 3, 5, 4]
        aprobados = 0
        for nota in notas:
            if nota >= 5:
                aprobados += 1
        print(aprobados)
        """,
        "2",
        "El contador solo aumenta cuando la nota es al menos 5: 8 y 5.",
        traps={"4": "acumuladores.cuenta-todo", "1": "condicionales.frontera"},
    ),
    code(
        "acu-04",
        "acumuladores",
        "Escribe `media_positivos(numeros)`: devuelve la media de los números **mayores que 0** de la lista. Si no hay ninguno, devuelve 0.",
        """
         def media_positivos(numeros):
             ...
         """,
        """
         def media_positivos(numeros):
             suma = 0
             cuantos = 0
             for n in numeros:
                 if n > 0:
                     suma += n
                     cuantos += 1
             if cuantos == 0:
                 return 0
             return suma / cuantos
         """,
        [
            case(
                'assert media_positivos([4, -2, 6]) == 5, "Con [4, -2, 6] la media de los positivos es (4 + 6) / 2 = 5"',
                error="acumuladores.cuenta-todo",
            ),
            case(
                'assert media_positivos([1, 2, 3, 4]) == 2.5, "Con [1, 2, 3, 4] la media es 2.5: ¿calculas la media después del bucle?"',
                error="acumuladores.media-dentro",
            ),
            case(
                'assert media_positivos([-1, 0, -5]) == 0, "Si no hay positivos debe devolver 0 (y no dividir entre 0)"',
                error="acumuladores.media-dentro",
            ),
            case(
                'assert media_positivos([]) == 0, "Con la lista vacía debe devolver 0"',
                error="algoritmos.sin-caso-limite",
            ),
        ],
        "Dos acumuladores inicializados fuera del bucle (la suma y el contador), actualizados solo cuando el número es positivo, y la división **después** del bucle, protegida contra el 0.",
        "Necesitas una suma y un contador. ¿Qué pasa si el contador acaba en 0?",
        wrong=[
            (
                """
                 def media_positivos(numeros):
                     suma = 0
                     for n in numeros:
                         if n > 0:
                             suma += n
                     return suma / len(numeros) if numeros else 0
                 """,
                1,
            ),
            (
                """
                 def media_positivos(numeros):
                     suma = 0
                     cuantos = 0
                     for n in numeros:
                         if n > 0:
                             suma += n
                             cuantos += 1
                     return suma / cuantos
                 """,
                3,
            ),
        ],
        level=2,
    ),
    fill(
        "acu-05",
        "acumuladores",
        "Completa para calcular la suma de los números del 1 al 10.",
        """
        total = ___
        for i in range(1, 11):
            total += i
        print(total)
        """,
        ["0"],
        "Una suma acumulada empieza en 0.",
        expect="55",
        traps={"1": "acumuladores.producto-cero"},
    ),
    code(
        "acu-06",
        "acumuladores",
        "Pide números enteros (uno por línea) hasta que el usuario escriba 0. Después muestra `Cantidad: X` y `Suma: Y` (sin contar el 0).",
        "",
        """
         cantidad = 0
         suma = 0
         n = int(input())
         while n != 0:
             cantidad += 1
             suma += n
             n = int(input())
         print(f"Cantidad: {cantidad}")
         print(f"Suma: {suma}")
         """,
        [
            case(
                'assert "Cantidad: 3" in __output__ and "Suma: 12" in __output__, f"Con 5, 4, 3 y 0 se esperaba Cantidad: 3 y Suma: 12. Tu salida:\\n{__output__}"',
                "5\n4\n3\n0\n",
                "acumuladores.cuenta-todo",
            ),
            case(
                'assert "Cantidad: 0" in __output__ and "Suma: 0" in __output__, "Si el primer número es 0, no hay ninguno: Cantidad: 0 y Suma: 0"',
                "0\n",
                "bucles.condicion-salida",
            ),
        ],
        "Patrón «leer hasta un valor centinela»: se lee el primer número antes del bucle, se procesa dentro y se vuelve a leer al final de cada vuelta. El 0 nunca se cuenta.",
        "Lee el primer número antes del `while`; la condición es `n != 0`; dentro, actualiza contador y suma y lee el siguiente.",
        wrong=[
            (
                """
                 cantidad = 0
                 suma = 0
                 n = 1
                 while n != 0:
                     n = int(input())
                     cantidad += 1
                     suma += n
                 print(f"Cantidad: {cantidad}")
                 print(f"Suma: {suma}")
                 """,
                1,
            )
        ],
        level=3,
    ),
]

# ================================================================== VALIDACIÓN
E += [
    choice(
        "val-01",
        "validacion",
        "Quieres repetir la pregunta mientras la edad **no** sea válida (válida: de 0 a 120). ¿Qué condición usas?",
        [
            ("while edad < 0 or edad > 120:", None),
            ("while edad < 0 and edad > 120:", "validacion.or-and"),
            ("while 0 <= edad <= 120:", "validacion.condicion-invertida"),
            ("while edad > 0 or edad < 120:", "validacion.or-and"),
        ],
        0,
        "El bucle de validación se repite mientras el dato es incorrecto: por debajo de 0 **o** por encima de 120. Con `and` nunca sería verdadero.",
        code_options=True,
    ),
    bug(
        "val-02",
        "validacion",
        "Si el usuario escribe 15, el programa se queda colgado. ¿Qué línea falta corregir?",
        """
        nota = int(input())
        while nota < 0 or nota > 10:
            print("Nota no válida")
            nota = nota
        print("OK")
        """,
        4,
        "    nota = int(input())",
        "Nota no válida\nOK",
        "validacion.no-repide",
        "Dentro del bucle hay que volver a pedir el dato; si no, la variable no cambia y el bucle es infinito.",
        stdin="15\n5\n",
        level=2,
    ),
    code(
        "val-03",
        "validacion",
        "Pide una nota entera hasta que esté entre 0 y 10 (ambos incluidos). Cada vez que no sea válida, muestra `Nota no válida`. Al final muestra `Nota: X`.",
        """
         nota = int(input())
         """,
        """
         nota = int(input())
         while nota < 0 or nota > 10:
             print("Nota no válida")
             nota = int(input())
         print(f"Nota: {nota}")
         """,
        [
            case(
                'assert __output__.count("Nota no válida") == 2 and "Nota: 7" in __output__, f"Con 11, -1 y 7 se esperaban 2 avisos y «Nota: 7». Tu salida:\\n{__output__}"',
                "11\n-1\n7\n",
                "validacion.condicion-invertida",
            ),
            case(
                'assert "Nota no válida" not in __output__ and "Nota: 10" in __output__, "10 es una nota válida: no debe mostrar el aviso"',
                "10\n",
                "condicionales.frontera",
            ),
            case(
                'assert "Nota no válida" not in __output__ and "Nota: 0" in __output__, "0 es una nota válida"',
                "0\n",
                "condicionales.frontera",
            ),
        ],
        "La condición del `while` describe la nota **incorrecta**, y dentro del bucle se vuelve a pedir.",
        "Condición: `nota < 0 or nota > 10`. No olvides el `input()` dentro del bucle.",
        wrong=[
            (
                """
                 nota = int(input())
                 while nota <= 0 or nota >= 10:
                     print("Nota no válida")
                     nota = int(input())
                 print(f"Nota: {nota}")
                 """,
                2,
            )
        ],
        level=2,
    ),
    output(
        "val-04",
        "validacion",
        """
        for texto in ["12", "doce", " 7"]:
            print(texto.isdigit(), end=" ")
        """,
        "True False False",
        "`isdigit()` es True solo si **todos** los caracteres son cifras. Un espacio ya no lo es: limpia antes con `strip()`.",
        traps={"True False True": "validacion.condicion-invertida"},
        level=2,
    ),
]

# ================================================================== FUNCIONES
E += [
    output(
        "fun-01",
        "funciones",
        """
        def doble(n):
            print(n * 2)

        x = doble(4)
        print(x)
        """,
        "8\nNone",
        "La función **muestra** 8 pero no **devuelve** nada, así que devuelve None y eso es lo que se guarda en x.",
        traps={"8\n8": "funciones.print-en-vez-de-return", "8": "funciones.print-en-vez-de-return"},
        level=2,
    ),
    bug(
        "fun-02",
        "funciones",
        "`contiene([1, 2, 3], 3)` debería devolver True, pero devuelve False. ¿Qué línea falla?",
        """
        def contiene(lista, x):
            for elemento in lista:
                if elemento == x:
                    return True
                return False
        print(contiene([1, 2, 3], 3))
        """,
        5,
        "    return False",
        "True",
        "funciones.return-en-bucle",
        "El `return False` está dentro del bucle: termina la función en la primera vuelta. Debe ir **después** del bucle, cuando ya se han revisado todos.",
    ),
    output(
        "fun-03",
        "funciones",
        """
        def saludo(nombre, saludo="Hola"):
            return f"{saludo}, {nombre}"

        print(saludo("Ana"))
        print(saludo("Luis", "Buenas"))
        """,
        "Hola, Ana\nBuenas, Luis",
        "El parámetro con valor por defecto se usa cuando no se pasa ese argumento.",
    ),
    choice(
        "fun-04",
        "funciones",
        "¿Qué ocurre al ejecutar este programa?",
        [
            ("NameError: total no existe fuera de la función", None),
            ("Muestra 10", "funciones.ambito"),
            ("Muestra None", "funciones.ambito"),
            ("Muestra 0", "funciones.ambito"),
        ],
        0,
        "`total` es una variable **local** de `calcular`: deja de existir al terminar la función. Para usar el valor fuera hay que devolverlo con `return`.",
        code="""
           def calcular():
               total = 10

           calcular()
           print(total)
           """,
        level=2,
    ),
    code(
        "fun-05",
        "funciones",
        "Escribe `es_primo(n)`: devuelve True si n es primo y False si no. (Los números menores que 2 no son primos.)",
        """
         def es_primo(n):
             ...
         """,
        """
         def es_primo(n):
             if n < 2:
                 return False
             for d in range(2, n):
                 if n % d == 0:
                     return False
             return True
         """,
        [
            case(
                'assert es_primo(7) is True and es_primo(13) is True, "7 y 13 son primos"',
                error="funciones.return-en-bucle",
            ),
            case(
                'assert es_primo(9) is False, "9 no es primo: es divisible entre 3"',
                error="funciones.return-en-bucle",
            ),
            case(
                'assert es_primo(1) is False and es_primo(0) is False, "0 y 1 no son primos"',
                error="algoritmos.sin-caso-limite",
            ),
            case('assert es_primo(2) is True, "2 es primo"', error="bucles.uno-de-mas"),
        ],
        "Búsqueda de un divisor: en cuanto aparece uno, ya sabemos que no es primo (`return False` dentro del bucle). Solo cuando se han probado todos sin encontrar ninguno se puede afirmar que es primo (`return True` **después** del bucle).",
        "Prueba los divisores desde 2 hasta n − 1. ¿Dónde va el `return True`?",
        wrong=[
            (
                """
                 def es_primo(n):
                     if n < 2:
                         return False
                     for d in range(2, n):
                         if n % d == 0:
                             return False
                         else:
                             return True
                     return True
                 """,
                2,
            ),
            (
                """
                 def es_primo(n):
                     for d in range(2, n):
                         if n % d == 0:
                             return False
                     return True
                 """,
                3,
            ),
        ],
        level=3,
    ),
    fill(
        "fun-06",
        "funciones",
        "Completa para que la función devuelva el mayor de dos números.",
        """
        def mayor(a, b):
            if a > b:
                ___ a
            return b
        print(mayor(3, 8), mayor(9, 2))
        """,
        ["return"],
        "`return` devuelve el valor y termina la función; así el `return b` final solo se alcanza si a no es mayor.",
        expect="8 9",
        traps={"print": "funciones.print-en-vez-de-return"},
    ),
]

# ================================================================== STRINGS
E += [
    output(
        "str-01",
        "strings",
        """
        s = "Python"
        print(s[1], s[-2], s[1:4])
        """,
        "y o yth",
        "Las posiciones empiezan en 0: s[1] es «y». s[-2] es el penúltimo, «o». s[1:4] toma las posiciones 1, 2 y 3.",
        traps={
            "P n Pyth": "strings.indice-uno",
            "y o ytho": "strings.slice-fin",
            "P o Pyt": "strings.indice-uno",
        },
    ),
    output(
        "str-02",
        "strings",
        """
        s = "hola"
        s.upper()
        print(s)
        """,
        "hola",
        "Los textos son inmutables: `upper()` devuelve un texto nuevo que aquí no se guarda. Para cambiar s: `s = s.upper()`.",
        traps={"HOLA": "strings.inmutable"},
    ),
    code(
        "str-03",
        "strings",
        "Escribe `contar_vocales(texto)` que devuelva cuántas vocales (a, e, i, o, u, en mayúscula o minúscula) tiene el texto.",
        """
         def contar_vocales(texto):
             ...
         """,
        """
         def contar_vocales(texto):
             total = 0
             for letra in texto.lower():
                 if letra in "aeiou":
                     total += 1
             return total
         """,
        [
            case(
                'assert contar_vocales("programa") == 3, "«programa» tiene 3 vocales"',
                error="acumuladores.cuenta-todo",
            ),
            case(
                'assert contar_vocales("ARBOL") == 2, "Cuenta también las mayúsculas: «ARBOL» tiene 2"',
                error="strings.inmutable",
            ),
            case(
                'assert contar_vocales("") == 0, "Un texto vacío tiene 0 vocales"',
                error="algoritmos.sin-caso-limite",
            ),
        ],
        "Recorrido del texto con un contador. Pasar el texto a minúsculas con `lower()` (guardando o recorriendo el resultado) evita comprobar las mayúsculas aparte.",
        'Recorre `texto.lower()` letra a letra y comprueba `letra in "aeiou"`.',
        wrong=[
            (
                """
                 def contar_vocales(texto):
                     total = 0
                     texto.lower()
                     for letra in texto:
                         if letra in "aeiou":
                             total += 1
                     return total
                 """,
                2,
            )
        ],
    ),
    output(
        "str-04",
        "strings",
        """
        palabra = "radar"
        print(palabra == palabra[::-1])
        print("ab" * 3)
        """,
        "True\nababab",
        "`[::-1]` invierte el texto: «radar» es un palíndromo. `*` repite un texto.",
    ),
    choice(
        "str-05",
        "strings",
        '¿Qué ocurre con `nombre = "ana"; nombre[0] = "A"`?',
        [
            ("TypeError: los str no admiten asignación por posición", None),
            ('nombre pasa a ser "Ana"', "strings.inmutable"),
            ('nombre pasa a ser "A"', "strings.inmutable"),
            ("IndexError", "strings.indice-uno"),
        ],
        0,
        'Los textos son inmutables. Para obtener "Ana": `nombre = nombre[0].upper() + nombre[1:]` o `nombre.capitalize()`.',
    ),
]

# ================================================================== LISTAS
E += [
    output(
        "lis-01",
        "listas",
        """
        a = [1, 2]
        b = a
        b.append(3)
        print(a)
        """,
        "[1, 2, 3]",
        "`b = a` no copia la lista: `a` y `b` son la misma lista. Por eso el `append` hecho a través de b se ve en a.",
        traps={"[1, 2]": "listas.alias"},
        level=2,
    ),
    output(
        "lis-02",
        "listas",
        """
        numeros = [3, 1, 2]
        resultado = numeros.sort()
        print(resultado, numeros)
        """,
        "None [1, 2, 3]",
        "`sort()` ordena la propia lista y devuelve None. Si quieres una copia ordenada, usa `sorted(numeros)`.",
        traps={
            "[1, 2, 3] [1, 2, 3]": "listas.sort-none",
            "[1, 2, 3] [3, 1, 2]": "listas.sort-none",
        },
        level=2,
    ),
    choice(
        "lis-03",
        "listas",
        "Con `lista = [10, 20, 30]`, ¿qué da `lista[3]`?",
        [
            ("IndexError", None),
            ("30", "listas.indice-fuera"),
            ("None", "listas.indice-fuera"),
            ("10", "listas.indice-fuera"),
        ],
        0,
        "Hay 3 elementos, en las posiciones 0, 1 y 2. La posición 3 no existe.",
        code_options=True,
    ),
    output(
        "lis-04",
        "listas",
        """
        l = [5, 8, 2]
        l.insert(1, 7)
        l.pop()
        print(l, len(l))
        """,
        "[5, 7, 8] 3",
        "`insert(1, 7)` mete el 7 en la posición 1: [5, 7, 8, 2]. `pop()` sin argumento quita el último: [5, 7, 8].",
    ),
    code(
        "lis-05",
        "listas",
        "Escribe `filtrar_aprobados(notas)` que devuelva una **lista nueva** con las notas mayores o iguales a 5, en el mismo orden.",
        """
         def filtrar_aprobados(notas):
             ...
         """,
        """
         def filtrar_aprobados(notas):
             resultado = []
             for nota in notas:
                 if nota >= 5:
                     resultado.append(nota)
             return resultado
         """,
        [
            case(
                'assert filtrar_aprobados([7, 3, 5, 9, 4]) == [7, 5, 9], "Con [7, 3, 5, 9, 4] se esperaba [7, 5, 9]"',
                error="condicionales.frontera",
            ),
            case(
                'original = [4, 6]\nfiltrar_aprobados(original)\nassert original == [4, 6], "La lista original no debe modificarse"',
                error="listas.modificar-recorriendo",
            ),
            case('assert filtrar_aprobados([]) == [], "Con la lista vacía debe devolver []"'),
        ],
        "Se construye una lista nueva con `append`, sin tocar la original. Eliminar de la lista mientras se recorre se salta elementos.",
        "Crea `resultado = []` antes del bucle y añade con `append` las que cumplan.",
        wrong=[
            (
                """
                 def filtrar_aprobados(notas):
                     for nota in notas:
                         if nota < 5:
                             notas.remove(nota)
                     return notas
                 """,
                2,
            )
        ],
    ),
    fill(
        "lis-06",
        "listas",
        "Completa para obtener una copia **independiente** de la lista.",
        """
        original = [1, 2, 3]
        copia = original.___()
        copia.append(4)
        print(original)
        """,
        ["copy"],
        "`copy()` crea una lista nueva con los mismos elementos; modificar la copia no afecta a la original.",
        expect="[1, 2, 3]",
    ),
]

# ================================================================== TUPLAS Y CONJUNTOS
E += [
    output(
        "tup-01",
        "tuplas-conjuntos",
        """
        punto = (3, 4)
        x, y = punto
        print(x + y)
        print(len({1, 2, 2, 3, 3, 3}))
        """,
        "7\n3",
        "El desempaquetado reparte la tupla en x e y. Un conjunto no guarda repetidos: {1, 2, 3}.",
        traps={"7\n6": "tuplas-conjuntos.set-orden"},
    ),
    choice(
        "tup-02",
        "tuplas-conjuntos",
        "¿Qué tipo tiene `vacio = {}`?",
        [
            ("dict", None),
            ("set", "tuplas-conjuntos.llaves-vacias"),
            ("tuple", "tuplas-conjuntos.llaves-vacias"),
            ("list", "tuplas-conjuntos.llaves-vacias"),
        ],
        0,
        "Las llaves vacías crean un diccionario. El conjunto vacío se crea con `set()`.",
        code_options=True,
    ),
    choice(
        "tup-03",
        "tuplas-conjuntos",
        "¿Qué ocurre con `fecha = (1, 10, 2026); fecha[0] = 2`?",
        [
            ("TypeError: las tuplas no se pueden modificar", None),
            ("fecha pasa a ser (2, 10, 2026)", "tuplas-conjuntos.tupla-mutable"),
            ("Se crea una tupla nueva automáticamente", "tuplas-conjuntos.tupla-mutable"),
            ("IndexError", "tuplas-conjuntos.tupla-mutable"),
        ],
        0,
        "Las tuplas son inmutables. Si los datos deben cambiar, usa una lista; si no, crea una tupla nueva.",
    ),
    code(
        "tup-04",
        "tuplas-conjuntos",
        "Escribe `comunes(a, b)` que devuelva una **lista ordenada** con los elementos que aparecen en las dos listas, sin repetidos.",
        """
         def comunes(a, b):
             ...
         """,
        """
         def comunes(a, b):
             return sorted(set(a) & set(b))
         """,
        [
            case(
                'assert comunes([1, 2, 3, 3], [3, 2, 5]) == [2, 3], "Con [1, 2, 3, 3] y [3, 2, 5] se esperaba [2, 3]"',
                error="tuplas-conjuntos.set-orden",
            ),
            case('assert comunes([1], [2]) == [], "Sin elementos comunes debe devolver []"'),
            case(
                'assert isinstance(comunes([2, 1], [1, 2]), list), "Debe devolver una lista, no un conjunto"',
                error="tuplas-conjuntos.set-orden",
            ),
        ],
        "Los conjuntos quitan repetidos y `&` da la intersección. Como el conjunto no tiene orden, se convierte con `sorted`, que devuelve una lista.",
        "Convierte las dos listas a `set`, intersécalas con `&` y ordena el resultado.",
        wrong=[
            (
                """
                 def comunes(a, b):
                     return set(a) & set(b)
                 """,
                1,
            )
        ],
    ),
]

# ================================================================== DICCIONARIOS
E += [
    output(
        "dic-01",
        "diccionarios",
        """
        edades = {"Ana": 20, "Luis": 22}
        edades["Ana"] = 21
        edades["Eva"] = 19
        print(len(edades), edades["Ana"])
        """,
        "3 21",
        "Asignar a una clave existente sustituye su valor (Ana pasa a 21); a una clave nueva, la añade (Eva).",
        traps={"4 21": "diccionarios.keyerror", "3 20": "variables.orden-asignacion"},
    ),
    output(
        "dic-02",
        "diccionarios",
        """
        d = {"a": 1, "b": 2}
        print("a" in d, 1 in d)
        """,
        "True False",
        '`in` busca entre las **claves**: "a" es clave, 1 no lo es (es un valor). Para los valores: `1 in d.values()`.',
        traps={"True True": "diccionarios.in-valores"},
    ),
    output(
        "dic-03",
        "diccionarios",
        """
        precios = {"pan": 1.2, "leche": 0.9}
        for x in precios:
            print(x)
        """,
        "pan\nleche",
        "Recorrer un diccionario da sus claves. Para los valores, `.values()`; para las dos cosas, `.items()`.",
        traps={
            "1.2\n0.9": "diccionarios.recorrido-claves",
            "pan 1.2\nleche 0.9": "diccionarios.recorrido-claves",
        },
    ),
    code(
        "dic-04",
        "diccionarios",
        "Escribe `frecuencias(palabras)` que reciba una lista de palabras y devuelva un diccionario con cuántas veces aparece cada una.",
        """
         def frecuencias(palabras):
             ...
         """,
        """
         def frecuencias(palabras):
             conteo = {}
             for p in palabras:
                 conteo[p] = conteo.get(p, 0) + 1
             return conteo
         """,
        [
            case(
                'assert frecuencias(["sol", "luna", "sol"]) == {"sol": 2, "luna": 1}, "Con [sol, luna, sol] se esperaba {\\"sol\\": 2, \\"luna\\": 1}"',
                error="diccionarios.keyerror",
            ),
            case('assert frecuencias([]) == {}, "Con la lista vacía debe devolver {}"'),
            case(
                'assert frecuencias(["a"] * 5) == {"a": 5}, "Cinco veces la misma palabra"',
                error="acumuladores.inicializa-dentro",
            ),
        ],
        "El patrón contador con diccionario: `get(p, 0)` da 0 la primera vez que aparece la palabra, así nunca hay KeyError.",
        "Empieza con `conteo = {}`. Para cada palabra: `conteo[p] = conteo.get(p, 0) + 1`.",
        wrong=[
            (
                """
                 def frecuencias(palabras):
                     conteo = {}
                     for p in palabras:
                         conteo[p] = 1
                     return conteo
                 """,
                1,
            )
        ],
    ),
    choice(
        "dic-05",
        "diccionarios",
        'Con `stock = {"pan": 3}`, ¿qué devuelve `stock.get("leche", 0)`?',
        [
            ("0", None),
            ("KeyError", "diccionarios.keyerror"),
            ("None", "diccionarios.keyerror"),
            ("3", "diccionarios.keyerror"),
        ],
        0,
        '`get` devuelve el valor por defecto (aquí 0) si la clave no existe, en lugar de lanzar KeyError como `stock["leche"]`.',
        code_options=True,
    ),
]

# ================================================================== RECORRIDOS Y BÚSQUEDA
E += [
    output(
        "rec-01",
        "recorridos",
        """
        valores = [-4, -2, -9]
        mayor = 0
        for v in valores:
            if v > mayor:
                mayor = v
        print(mayor)
        """,
        "0",
        "Como el máximo empieza en 0 y todos los valores son negativos, nunca se actualiza: el resultado es 0, que ni siquiera está en la lista. Hay que empezar con `valores[0]`.",
        traps={"-2": "recorridos.max-cero"},
        level=2,
    ),
    bug(
        "rec-02",
        "recorridos",
        "`buscar([4, 7, 9], 9)` debería devolver 2, pero devuelve -1. ¿Qué línea falla?",
        """
        def buscar(lista, objetivo):
            for i in range(len(lista)):
                if lista[i] == objetivo:
                    return i
                return -1
        print(buscar([4, 7, 9], 9))
        """,
        5,
        "    return -1",
        "2",
        "recorridos.no-encontrado-dentro",
        "El `return -1` dentro del bucle decide «no está» al mirar solo el primer elemento. El -1 se devuelve **después** del bucle, cuando se han revisado todos.",
        level=2,
    ),
    code(
        "rec-03",
        "recorridos",
        "Escribe `posicion_maximo(numeros)`: devuelve la **posición** del mayor número (la primera si se repite). La lista nunca está vacía.",
        """
         def posicion_maximo(numeros):
             ...
         """,
        """
         def posicion_maximo(numeros):
             mejor = 0
             for i in range(1, len(numeros)):
                 if numeros[i] > numeros[mejor]:
                     mejor = i
             return mejor
         """,
        [
            case(
                'assert posicion_maximo([3, 9, 2]) == 1, "En [3, 9, 2] el mayor (9) está en la posición 1"'
            ),
            case(
                'assert posicion_maximo([-5, -1, -3]) == 1, "Con todos negativos: en [-5, -1, -3] el mayor está en la posición 1"',
                error="recorridos.max-cero",
            ),
            case(
                'assert posicion_maximo([7, 7, 1]) == 0, "Si se repite, la primera posición: [7, 7, 1] → 0"',
                error="condicionales.frontera",
            ),
            case('assert posicion_maximo([4]) == 0, "Con un solo elemento, la posición 0"'),
        ],
        "Se guarda la posición del mejor candidato, empezando por el primer elemento. Con `>` (y no `>=`) se conserva la primera aparición en caso de empate.",
        "Guarda la posición del mejor, empezando en 0, y compara `numeros[i] > numeros[mejor]`.",
        wrong=[
            (
                """
                 def posicion_maximo(numeros):
                     mayor = 0
                     pos = 0
                     for i in range(len(numeros)):
                         if numeros[i] > mayor:
                             mayor = numeros[i]
                             pos = i
                     return pos
                 """,
                2,
            ),
            (
                """
                 def posicion_maximo(numeros):
                     mejor = 0
                     for i in range(len(numeros)):
                         if numeros[i] >= numeros[mejor]:
                             mejor = i
                     return mejor
                 """,
                3,
            ),
        ],
        level=2,
    ),
    choice(
        "rec-04",
        "recorridos",
        "Para comprobar si **todos** los números de una lista son pares, ¿con qué valor empieza la variable `todos_pares` y cuándo cambia?",
        [
            ("Empieza en True y pasa a False al encontrar un impar", None),
            ("Empieza en False y pasa a True al encontrar un par", "recorridos.todos-alguno"),
            ("Empieza en True y pasa a False al encontrar un par", "recorridos.todos-alguno"),
            ("Empieza en 0 y suma 1 por cada par", "recorridos.todos-alguno"),
        ],
        0,
        "«¿Todos cumplen?»: se supone que sí y basta un contraejemplo para desmentirlo. Empezar en False y cambiar con un par respondería a «¿alguno es par?».",
        level=2,
    ),
    code(
        "rec-05",
        "recorridos",
        "Escribe `todos_positivos(numeros)` que devuelva True si todos los números son mayores que 0 (una lista vacía cuenta como True). No uses `all()`.",
        """
         def todos_positivos(numeros):
             ...
         """,
        """
         def todos_positivos(numeros):
             for n in numeros:
                 if n <= 0:
                     return False
             return True
         """,
        [
            case(
                'assert todos_positivos([1, 5, 3]) is True, "[1, 5, 3] son todos positivos"',
                error="recorridos.no-encontrado-dentro",
            ),
            case(
                'assert todos_positivos([1, -5, 3]) is False, "[1, -5, 3] tiene un negativo"',
                error="recorridos.todos-alguno",
            ),
            case(
                'assert todos_positivos([4, 0]) is False, "0 no es mayor que 0"',
                error="condicionales.frontera",
            ),
            case(
                'assert todos_positivos([]) is True, "Una lista vacía cuenta como True"',
                error="recorridos.todos-alguno",
            ),
            case('assert "all(" not in __code__, "Resuélvelo con un bucle, sin all()"'),
        ],
        "Basta un contraejemplo (un número ≤ 0) para devolver False en cuanto aparece. Solo después de revisar todos se puede devolver True.",
        "Busca un contraejemplo: si lo encuentras, `return False`; si el bucle termina, `return True`.",
        wrong=[
            (
                """
                 def todos_positivos(numeros):
                     for n in numeros:
                         if n > 0:
                             return True
                     return False
                 """,
                2,
            )
        ],
        level=2,
    ),
    choice(
        "rec-06",
        "recorridos",
        "Una función compara cada elemento de una lista con todos los demás (dos bucles anidados). Si la lista pasa de 100 a 1.000 elementos, ¿cuántas comparaciones hará aproximadamente?",
        [
            ("Unas 100 veces más (de 10.000 a 1.000.000)", None),
            ("10 veces más", "recorridos.no-para"),
            ("Las mismas", "recorridos.no-para"),
            ("1.000 veces más", "recorridos.no-para"),
        ],
        0,
        "Con dos bucles anidados el trabajo crece con n²: (1.000)² / (100)² = 100. Un solo bucle crecería 10 veces.",
        level=3,
    ),
]

# ================================================================== EXCEPCIONES
E += [
    output(
        "exc-01",
        "excepciones",
        """
        try:
            n = int("doce")
            print("convertido")
        except ValueError:
            print("no es un número")
        print("sigue")
        """,
        "no es un número\nsigue",
        '`int("doce")` lanza ValueError: se salta el resto del `try`, se ejecuta el `except` y el programa continúa.',
        traps={
            "convertido\nno es un número\nsigue": "excepciones.try-gigante",
            "no es un número": "trazado.intencion",
        },
    ),
    choice(
        "exc-02",
        "excepciones",
        '¿Qué excepción lanza `int("3.5")`?',
        [
            ("ValueError", None),
            ("TypeError", "excepciones.tipo-equivocado"),
            ("ZeroDivisionError", "excepciones.tipo-equivocado"),
            ("Ninguna: devuelve 3", "tipos.texto-numero"),
        ],
        0,
        "El argumento es del tipo correcto (str) pero su **valor** no representa un entero: ValueError. TypeError sería, por ejemplo, `int([1])`.",
    ),
    choice(
        "exc-03",
        "excepciones",
        "¿Por qué es mala idea escribir `except:` sin indicar el tipo?",
        [
            (
                "Oculta también errores de programación, como NameError, y dificulta encontrarlos",
                None,
            ),
            ("Porque da error de sintaxis", "excepciones.except-generico"),
            ("Porque es más lento", "excepciones.except-generico"),
            ("No es mala idea: es la forma recomendada", "excepciones.except-generico"),
        ],
        0,
        "Un `except` sin tipo lo captura todo, incluso un nombre mal escrito. Captura solo la excepción que esperas.",
    ),
    code(
        "exc-04",
        "excepciones",
        "Escribe `a_entero(texto)` que devuelva el entero que representa el texto, o `None` si no es un número entero válido.",
        """
         def a_entero(texto):
             ...
         """,
        """
         def a_entero(texto):
             try:
                 return int(texto)
             except ValueError:
                 return None
         """,
        [
            case(
                'assert a_entero("42") == 42 and a_entero("-7") == -7, "\\"42\\" → 42 y \\"-7\\" → -7"'
            ),
            case(
                'assert a_entero("hola") is None and a_entero("3.5") is None, "Los textos que no son enteros devuelven None"',
                error="excepciones.tipo-equivocado",
            ),
            case(
                'assert "except:" not in __code__.replace(" ", ""), "Captura la excepción concreta (ValueError), no todas"',
                error="excepciones.except-generico",
            ),
        ],
        "Se intenta la conversión y se captura solo ValueError, que es lo que lanza `int()` con un texto no numérico.",
        "`try: return int(texto)` y `except ValueError: return None`.",
        wrong=[
            (
                """
                 def a_entero(texto):
                     try:
                         return int(texto)
                     except TypeError:
                         return None
                 """,
                2,
            )
        ],
    ),
]

# ================================================================== MÓDULOS
E += [
    choice(
        "mod-01",
        "modulos",
        "Tras `import math`, ¿cómo se calcula la raíz cuadrada de 9?",
        [
            ("math.sqrt(9)", None),
            ("sqrt(9)", "modulos.prefijo"),
            ("math(9).sqrt", "modulos.prefijo"),
            ("import sqrt(9)", "modulos.prefijo"),
        ],
        0,
        "Con `import math` las funciones se usan con el prefijo del módulo. `sqrt(9)` solo funcionaría con `from math import sqrt`.",
        code_options=True,
    ),
    output(
        "mod-02",
        "modulos",
        """
        from math import floor, ceil
        print(floor(2.7), ceil(2.1))
        """,
        "2 3",
        "`floor` redondea hacia abajo y `ceil` hacia arriba. Con `from ... import` se usan sin prefijo.",
    ),
    choice(
        "mod-03",
        "modulos",
        "Guardas tu programa como `random.py` y dentro escribes `import random`. ¿Qué pasa?",
        [
            ("Se importa tu propio fichero en vez del módulo estándar", None),
            ("Funciona normal", "modulos.nombre-fichero"),
            ("Python avisa del conflicto y elige el estándar", "modulos.nombre-fichero"),
            ("Da SyntaxError", "modulos.nombre-fichero"),
        ],
        0,
        "Python busca primero en la carpeta del programa: tu fichero tapa al módulo `random`. No nombres tus ficheros como módulos estándar.",
        level=2,
    ),
]

# ================================================================== ARCHIVOS
E += [
    choice(
        "arc-01",
        "archivos",
        "Quieres **añadir** una línea al final de `registro.txt` sin perder lo que ya tiene. ¿Qué modo usas?",
        [
            ('"a"', None),
            ('"w"', "archivos.modo-w"),
            ('"r"', "archivos.modo-w"),
            ('"x"', "archivos.modo-w"),
        ],
        0,
        '`"a"` (append) escribe al final. `"w"` vacía el fichero al abrirlo y `"r"` es solo lectura.',
        code_options=True,
    ),
    output(
        "arc-02",
        "archivos",
        """
        with open("datos.txt", "w", encoding="utf-8") as f:
            f.write("uno")
            f.write("dos")
        with open("datos.txt", encoding="utf-8") as f:
            print(len(f.readlines()))
        """,
        "1",
        "`write` no añade saltos de línea: el fichero contiene «unodos» en una sola línea.",
        traps={"2": "archivos.salto-linea"},
        level=2,
    ),
    code(
        "arc-03",
        "archivos",
        "Escribe `contar_lineas_no_vacias(ruta)` que devuelva cuántas líneas del fichero tienen algún carácter que no sea espacio.",
        """
         def contar_lineas_no_vacias(ruta):
             ...
         """,
        """
         def contar_lineas_no_vacias(ruta):
             total = 0
             with open(ruta, encoding="utf-8") as f:
                 for linea in f:
                     if linea.strip():
                         total += 1
             return total
         """,
        [
            case(
                'with open("p.txt", "w", encoding="utf-8") as f:\n    f.write("hola\\n\\n  \\nadios\\n")\nassert contar_lineas_no_vacias("p.txt") == 2, "El fichero tiene 2 líneas con texto (las otras están vacías o solo tienen espacios)"',
                error="archivos.salto-linea",
            ),
            case(
                'with open("q.txt", "w", encoding="utf-8") as f:\n    f.write("")\nassert contar_lineas_no_vacias("q.txt") == 0, "Un fichero vacío tiene 0 líneas"'
            ),
        ],
        "Cada línea leída termina en «\\n», así que nunca es un texto vacío: hay que limpiarla con `strip()` antes de comprobarla.",
        "Recorre el fichero con `for linea in f` y comprueba `linea.strip()`.",
        wrong=[
            (
                """
                 def contar_lineas_no_vacias(ruta):
                     total = 0
                     with open(ruta, encoding="utf-8") as f:
                         for linea in f:
                             if linea != "":
                                 total += 1
                     return total
                 """,
                1,
            )
        ],
        level=2,
    ),
]

# ================================================================== PSEUDOCÓDIGO
E += [
    choice(
        "pse-01",
        "pseudocodigo",
        "¿Cómo se traduce `PARA i DESDE 1 HASTA n HACER` a Python?",
        [
            ("for i in range(1, n + 1):", None),
            ("for i in range(1, n):", "pseudocodigo.hasta-incluye"),
            ("for i in range(n):", "pseudocodigo.hasta-incluye"),
            ("while i < n:", "pseudocodigo.hasta-incluye"),
        ],
        0,
        "HASTA n incluye n; `range` excluye el final, así que hay que poner n + 1.",
        code_options=True,
    ),
    choice(
        "pse-02",
        "pseudocodigo",
        "¿Qué estructura de Python equivale a `REPETIR … HASTA QUE x > 10`?",
        [
            ("while True: … if x > 10: break", None),
            ("while x > 10: …", "pseudocodigo.repetir-hasta"),
            ("for x in range(10): …", "pseudocodigo.repetir-hasta"),
            ("if x > 10: …", "pseudocodigo.repetir-hasta"),
        ],
        0,
        "REPETIR…HASTA QUE ejecuta el bloque al menos una vez y termina **cuando** la condición es verdadera. `while x > 10` haría lo contrario: repetir mientras sea verdadera.",
        level=2,
        code_options=True,
    ),
    order(
        "pse-03",
        "pseudocodigo",
        "Ordena el pseudocódigo que lee n números y escribe cuántos son negativos.",
        [
            "LEER n",
            "negativos ← 0",
            "PARA i DESDE 1 HASTA n HACER",
            "    LEER x",
            "    SI x < 0 ENTONCES negativos ← negativos + 1",
            "FIN PARA",
            "ESCRIBIR negativos",
        ],
        "Leer la cantidad, inicializar el contador **antes** del bucle, leer y comprobar cada número dentro del bucle y escribir el resultado al final.",
        pseudo=True,
        error="pseudocodigo.orden-pasos",
    ),
    code(
        "pse-04",
        "pseudocodigo",
        "Traduce a Python este pseudocódigo:\n\n```\nLEER n\nfactorial ← 1\nPARA i DESDE 1 HASTA n HACER\n    factorial ← factorial * i\nFIN PARA\nESCRIBIR factorial\n```",
        "",
        """
         n = int(input())
         factorial = 1
         for i in range(1, n + 1):
             factorial = factorial * i
         print(factorial)
         """,
        [
            case(
                'assert __output__.strip() == "120", f"Con n = 5 el factorial es 120 y tu programa muestra «{__output__.strip()}»"',
                "5\n",
                "pseudocodigo.hasta-incluye",
            ),
            case(
                'assert __output__.strip() == "1", "Con n = 0 el factorial es 1"',
                "0\n",
                "acumuladores.producto-cero",
            ),
            case('assert __output__.strip() == "1", "Con n = 1 el factorial es 1"', "1\n"),
        ],
        "Traducción línea a línea: LEER → `int(input())`, ← → `=`, PARA … HASTA n → `range(1, n + 1)`, ESCRIBIR → `print`.",
        "Cuidado con HASTA n: en `range` hay que poner n + 1.",
        wrong=[
            (
                """
                 n = int(input())
                 factorial = 1
                 for i in range(1, n):
                     factorial = factorial * i
                 print(factorial)
                 """,
                1,
            )
        ],
        level=2,
    ),
    order(
        "pse-05",
        "pseudocodigo",
        "Ordena las líneas de Python que traducen: «LEER n; MIENTRAS n > 0 HACER ESCRIBIR n; n ← n − 2; FIN MIENTRAS».",
        ["n = int(input())", "while n > 0:", "    print(n)", "    n = n - 2"],
        "Se lee antes del bucle; dentro, primero se escribe y después se actualiza la variable de la condición.",
        expect=None,
        error="pseudocodigo.orden-pasos",
        level=1,
    ),
    code(
        "pse-06",
        "pseudocodigo",
        'Traduce a Python:\n\n```\nintentos ← 0\nREPETIR\n    LEER clave\n    intentos ← intentos + 1\nHASTA QUE clave = "1234"\nESCRIBIR "Intentos: ", intentos\n```\n\nMuestra exactamente `Intentos: X`.',
        "",
        """
         intentos = 0
         while True:
             clave = input()
             intentos = intentos + 1
             if clave == "1234":
                 break
         print("Intentos:", intentos)
         """,
        [
            case(
                'assert __output__.strip() == "Intentos: 3", f"Con las entradas 0000, abcd y 1234 se esperaba «Intentos: 3» y tu programa muestra «{__output__.strip()}»"',
                "0000\nabcd\n1234\n",
                "pseudocodigo.repetir-hasta",
            ),
            case(
                'assert __output__.strip() == "Intentos: 1", "Si la primera clave ya es correcta, se pide una sola vez: «Intentos: 1»"',
                "1234\n",
                "pseudocodigo.repetir-hasta",
            ),
        ],
        "REPETIR…HASTA QUE se ejecuta al menos una vez y sale **cuando** la condición es verdadera: `while True` con `break` al cumplirse.",
        'Usa `while True:`, lee la clave, suma el intento y haz `break` si es "1234".',
        wrong=[
            (
                """
                 intentos = 0
                 clave = input()
                 while clave == "1234":
                     clave = input()
                     intentos = intentos + 1
                 print("Intentos:", intentos)
                 """,
                1,
            )
        ],
        level=2,
    ),
]

# ================================================================== TRAZADO
E += [
    output(
        "tra-01",
        "trazado",
        """
        a = 1
        b = 1
        for i in range(4):
            a, b = b, a + b
        print(a)
        """,
        "5",
        "Traza: (a, b) = (1, 1) → (1, 2) → (2, 3) → (3, 5) → (5, 8). Tras 4 vueltas, a = 5. Es la sucesión de Fibonacci.",
        traps={"8": "trazado.valor-antiguo", "3": "bucles.uno-de-mas"},
        level=3,
    ),
    output(
        "tra-02",
        "trazado",
        """
        total = 0
        for i in range(1, 4):
            total += i
            print(total)
        """,
        "1\n3\n6",
        "El `print` está dentro del bucle: muestra el total acumulado en cada vuelta (1, 1 + 2, 1 + 2 + 3).",
        traps={"6": "trazado.print-dentro-fuera"},
    ),
    output(
        "tra-03",
        "trazado",
        """
        x = 10
        while x > 1:
            if x % 2 == 0:
                x = x // 2
            else:
                x = x * 3 + 1
            print(x, end=" ")
        """,
        "5 16 8 4 2 1",
        "Traza: 10 es par → 5; 5 es impar → 16; 16 → 8 → 4 → 2 → 1. Con x = 1 la condición es falsa y el bucle termina.",
        traps={
            "5 16 8 4 2": "trazado.valor-antiguo",
            "10 5 16 8 4 2": "trazado.print-dentro-fuera",
        },
        level=3,
    ),
    output(
        "tra-04",
        "trazado",
        """
        def f(n):
            if n <= 1:
                return 1
            return n + f(n - 1)

        print(f(4))
        """,
        "10",
        "f(4) = 4 + f(3) = 4 + 3 + f(2) = 4 + 3 + 2 + f(1) = 4 + 3 + 2 + 1 = 10.",
        traps={"24": "trazado.intencion", "9": "trazado.valor-antiguo"},
        level=3,
    ),
    output(
        "tra-05",
        "trazado",
        """
        lista = [2, 4, 6]
        for i in range(len(lista)):
            lista[i] = lista[i] + i
        print(lista)
        """,
        "[2, 5, 8]",
        "A cada elemento se le suma su posición: 2 + 0, 4 + 1, 6 + 2.",
        traps={"[3, 5, 7]": "strings.indice-uno", "[2, 4, 6]": "trazado.intencion"},
        level=2,
    ),
    output(
        "tra-06",
        "trazado",
        """
        for i in range(3):
            for j in range(i):
                print(i, j)
        """,
        "1 0\n2 0\n2 1",
        "Con i = 0 el bucle interno no da ninguna vuelta (range(0) está vacío). Con i = 1, j vale 0. Con i = 2, j vale 0 y 1.",
        traps={"0 0\n1 0\n1 1\n2 0\n2 1\n2 2": "bucles.range-fin"},
        level=3,
    ),
]

# ================================================================== DEPURACIÓN
E += [
    choice(
        "dep-01",
        "depuracion",
        "En este traceback, ¿dónde está el error y de qué tipo es?",
        [
            ("En la línea 4, ZeroDivisionError", None),
            ("En la línea 1, Traceback", "depuracion.lee-primera-linea"),
            ("En la función media, SyntaxError", "depuracion.tipo-error"),
            ("No se puede saber", "depuracion.lee-primera-linea"),
        ],
        0,
        "Un traceback se lee de abajo arriba: la última línea da el tipo (ZeroDivisionError) y la de encima, el fichero y la línea (4).",
        code="""
           Traceback (most recent call last):
             File "notas.py", line 4, in <module>
               media = suma / cantidad
           ZeroDivisionError: division by zero
           """,
    ),
    choice(
        "dep-02",
        "depuracion",
        "Un programa termina sin mostrar ningún error, pero la media que calcula es incorrecta. ¿Qué tipo de error es?",
        [
            ("Un error lógico", None),
            ("Un error de sintaxis", "depuracion.tipo-error"),
            ("Una excepción", "depuracion.tipo-error"),
            ("No es un error", "depuracion.tipo-error"),
        ],
        0,
        "Si el programa termina pero el resultado está mal, es un error lógico. Se encuentra con trazas y pruebas, no leyendo un traceback.",
    ),
    choice(
        "dep-03",
        "depuracion",
        "Python señala un `SyntaxError` en la línea 3, que parece correcta. ¿Dónde conviene mirar?",
        [
            ("En la línea 2: puede faltar un paréntesis o unas comillas por cerrar", None),
            ("Solo en la línea 3", "depuracion.linea-anterior"),
            ("Al final del fichero", "depuracion.linea-anterior"),
            ("Es un fallo de Python", "depuracion.linea-anterior"),
        ],
        0,
        "Cuando algo se abre y no se cierra, Python se da cuenta al leer la línea siguiente.",
    ),
    bug(
        "dep-04",
        "depuracion",
        "Este programa da `TypeError`. ¿Qué línea hay que corregir?",
        """
        edad = input()
        siguiente = edad + 1
        print(siguiente)
        """,
        1,
        "edad = int(input())",
        "21",
        "entrada-salida.input-texto",
        "El error salta en la línea 2, pero la causa está en la 1: `input()` devuelve texto. La línea donde salta un error no siempre es la que hay que arreglar.",
        stdin="20\n",
        level=2,
    ),
    choice(
        "dep-05",
        "depuracion",
        "Tu función devuelve un resultado incorrecto con la lista [3, 0, 5]. ¿Qué es lo primero que deberías hacer?",
        [
            ("Formular una hipótesis y comprobarla con un print temporal o el depurador", None),
            ("Cambiar operadores hasta que funcione", "depuracion.cambios-a-ciegas"),
            ("Reescribir la función desde cero", "depuracion.cambios-a-ciegas"),
            ("Probar con otra lista para la que funcione", "depuracion.cambios-a-ciegas"),
        ],
        0,
        "Depurar con método: reproducir, formular una hipótesis («creo que el 0 rompe la condición»), comprobarla y corregir una sola cosa.",
        level=2,
    ),
    bug(
        "dep-06",
        "depuracion",
        "La función debería devolver la suma de los pares, pero devuelve un número demasiado alto. ¿Qué línea tiene el error?",
        """
        def suma_pares(numeros):
            total = 0
            for n in numeros:
                if n % 2 == 0:
                    total += n
                total += 0 if n % 2 == 0 else n
            return total
        print(suma_pares([1, 2, 3, 4]))
        """,
        6,
        "",
        "6",
        "depuracion.cambios-a-ciegas",
        "La línea 6 suma los impares. Es un error lógico típico de cambios hechos a ciegas: sobra la línea entera. La línea corregida está vacía (se elimina).",
        level=3,
    ),
]

# ================================================================== POO (más adelante)
E += [
    output(
        "poo-01",
        "poo",
        """
        class Contador:
            def __init__(self):
                self.valor = 0

            def incrementar(self):
                self.valor += 1

        a = Contador()
        b = Contador()
        a.incrementar()
        a.incrementar()
        b.incrementar()
        print(a.valor, b.valor)
        """,
        "2 1",
        "Cada objeto tiene sus propios atributos: a se incrementa dos veces y b una.",
        traps={"3 3": "poo.clase-objeto"},
        level=2,
        daw=False,
    ),
    choice(
        "poo-02",
        "poo",
        "¿Qué falla en este método?",
        [
            ("Falta self: debería ser self.saldo += cantidad", None),
            ("Falta return", "funciones.print-en-vez-de-return"),
            ("cantidad debería ser global", "poo.olvida-self"),
            ("Nada", "poo.olvida-self"),
        ],
        0,
        "`saldo` sin `self.` es una variable local del método que ni siquiera existe: da UnboundLocalError. El atributo del objeto es `self.saldo`.",
        code="""
           class Cuenta:
               def __init__(self):
                   self.saldo = 0

               def ingresar(self, cantidad):
                   saldo += cantidad
           """,
        level=2,
        daw=False,
    ),
    code(
        "poo-03",
        "poo",
        "Crea la clase `Rectangulo` con `__init__(self, base, altura)` y los métodos `area()` y `perimetro()`.",
        """
         class Rectangulo:
             ...
         """,
        """
         class Rectangulo:
             def __init__(self, base, altura):
                 self.base = base
                 self.altura = altura

             def area(self):
                 return self.base * self.altura

             def perimetro(self):
                 return 2 * (self.base + self.altura)
         """,
        [
            case(
                'r = Rectangulo(3, 4)\nassert r.area() == 12, "Un rectángulo de 3 × 4 tiene área 12"',
                error="poo.olvida-self",
            ),
            case(
                'r = Rectangulo(3, 4)\nassert r.perimetro() == 14, "Un rectángulo de 3 × 4 tiene perímetro 14"',
                error="poo.olvida-self",
            ),
            case(
                'a, b = Rectangulo(1, 1), Rectangulo(2, 5)\nassert (a.area(), b.area()) == (1, 10), "Cada objeto usa sus propios datos"',
                error="poo.clase-objeto",
            ),
        ],
        "Los datos se guardan en `self` en el constructor y los métodos los leen con `self.`.",
        "En `__init__`: `self.base = base`. En `area`: `return self.base * self.altura`.",
        level=2,
        daw=False,
    ),
]
