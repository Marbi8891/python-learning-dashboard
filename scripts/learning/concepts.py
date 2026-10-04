# ruff: noqa: E501
"""Mapa de conceptos del núcleo educativo (ADR-0031).

Cada concepto es la unidad de aprendizaje: tiene prerrequisitos, importancia para DAW,
teoría, un ejemplo explicado línea a línea, cuándo usarlo y sus errores típicos.

- `lessons`: lecciones de `frontend/data/lessons.json` cuya teoría se reutiliza tal cual
  (no se duplica). Si el concepto no tiene lección, lleva su propia `theory`.
- `theory`: explicación propia, solo cuando no hay lección que la cubra o cuando el concepto
  es una parte de una lección más amplia (p. ej. listas dentro de «colecciones»).
- `ut`: unidad de trabajo del curso de Programación de DAW (data/courses/programacion).
- `daw`: importancia para el módulo de Programación (3 = imprescindible, 1 = complementario).
- `errors`: malentendidos frecuentes. Los ejercicios los referencian (`error`) para que
  cada fallo quede registrado con su causa y la app pueda recomendar ejercicios para él.

La salida de cada ejemplo no se escribe a mano: build_learning.py la obtiene ejecutándolo.
"""

AREAS = [
    {
        "id": "fundamentos",
        "title": "Fundamentos",
        "summary": "Lo imprescindible para escribir cualquier programa.",
    },
    {
        "id": "programacion",
        "title": "Programación",
        "summary": "Funciones, colecciones y programas que trabajan con datos.",
    },
    {
        "id": "logica",
        "title": "Lógica",
        "summary": "Pensar antes de programar: algoritmos, pseudocódigo, trazas y depuración.",
    },
    {"id": "avanzado", "title": "Más adelante", "summary": "Cuando la base esté firme."},
]

# Orden recomendado de la ruta «Aprender»: intercala la lógica (pseudocódigo, trazas, depuración)
# con el lenguaje en el momento en que se puede practicar, en vez de dejarla para el final.
PATH = [
    "algoritmos",
    "variables",
    "tipos",
    "operadores",
    "entrada-salida",
    "condicionales",
    "pseudocodigo",
    "bucles",
    "trazado",
    "acumuladores",
    "validacion",
    "funciones",
    "depuracion",
    "strings",
    "listas",
    "recorridos",
    "tuplas-conjuntos",
    "diccionarios",
    "excepciones",
    "modulos",
    "archivos",
    "poo",
]


def err(cid: str, slug: str, label: str, why: str, think: str, avoid: str) -> dict:
    return {"id": f"{cid}.{slug}", "label": label, "why": why, "think": think, "avoid": avoid}


CONCEPTS = [
    # ------------------------------------------------------------------ FUNDAMENTOS
    {
        "id": "algoritmos",
        "title": "Comprender el problema y diseñar el algoritmo",
        "area": "fundamentos",
        "requires": [],
        "daw": 3,
        "ut": "prog-ut1",
        "summary": "Antes de escribir código: datos de entrada, proceso y salida.",
        "theory": (
            "Un **algoritmo** es una secuencia **ordenada, finita y precisa** de pasos que resuelve un problema. "
            "Programar no empieza en el teclado: empieza entendiendo el problema.\n\n"
            "**Método en tres preguntas** (úsalo en cada ejercicio de clase y del examen):\n"
            "1. **Entrada:** ¿qué datos tengo o me da el usuario? ¿De qué tipo son?\n"
            "2. **Salida:** ¿qué tengo que mostrar o devolver exactamente?\n"
            "3. **Proceso:** ¿qué pasos transforman la entrada en la salida?\n\n"
            "Después, **prueba el algoritmo a mano** con un caso normal y con un caso límite "
            "(0, lista vacía, número negativo…). Si a mano no funciona, en Python tampoco.\n\n"
            "Un algoritmo usa solo tres estructuras (**programación estructurada**): "
            "**secuencia** (un paso tras otro), **selección** (`if`) e **iteración** (bucles)."
        ),
        "when": "Siempre, antes de escribir la primera línea. En el examen, dedica un minuto a escribir entrada, salida y proceso en un comentario.",
        "example": {
            "code": (
                "# Entrada: precio (float) y si el cliente es socio (bool)\n"
                "# Salida: precio final con un 10 % de descuento para socios\n"
                "precio = 80.0\n"
                "socio = True\n"
                "if socio:\n"
                "    precio = precio * 0.9\n"
                "print(precio)"
            ),
            "lines": [
                [1, "Primero se escribe la entrada: qué datos hay y de qué tipo."],
                [2, "Después la salida exacta que se pide."],
                [5, "Proceso: una selección, porque el descuento depende de una condición."],
                [6, "Se aplica el 10 %: multiplicar por 0.9 es restar la décima parte."],
            ],
        },
        "errors": [
            err(
                "algoritmos",
                "sin-entrada-salida",
                "Empieza a programar sin saber qué entra y qué sale",
                "Sin entrada y salida claras, el código resuelve otro problema o se queda a medias.",
                "Lee el enunciado buscando sustantivos (datos) y verbos (acciones). Los datos son la entrada; lo que se pide mostrar, la salida.",
                "Escribe siempre las tres líneas «Entrada / Proceso / Salida» como comentario antes de programar.",
            ),
            err(
                "algoritmos",
                "sin-caso-limite",
                "No prueba los casos límite",
                "El algoritmo funciona con el ejemplo del enunciado pero falla con 0, vacío o negativos.",
                "Pregúntate: ¿qué pasa si no hay datos? ¿Y si el número es 0 o negativo?",
                "Antes de dar por bueno un algoritmo, trázalo a mano con un caso normal y uno límite.",
            ),
            err(
                "algoritmos",
                "pasos-ambiguos",
                "Escribe pasos ambiguos o en desorden",
                "El ordenador no interpreta: necesita cada paso preciso y en el orden correcto.",
                "Un paso es correcto si otra persona puede ejecutarlo sin preguntarte nada.",
                "Numera los pasos y comprueba que cada uno usa solo datos calculados en pasos anteriores.",
            ),
        ],
        "related": ["pseudocodigo", "trazado"],
    },
    {
        "id": "variables",
        "title": "Variables y asignación",
        "area": "fundamentos",
        "requires": [],
        "daw": 3,
        "ut": "prog-ut2",
        "lessons": ["variables"],
        "summary": "Nombres que apuntan a valores; `=` asigna, no compara.",
        "when": "Para guardar cualquier dato que vayas a usar más de una vez o que cambie durante el programa.",
        "example": {
            "code": 'contador = 0\ncontador = contador + 1\nnombre = "Ana"\nprint(nombre, contador)',
            "lines": [
                [1, "Se crea `contador` con el valor 0."],
                [
                    2,
                    "Python evalúa primero la derecha (0 + 1) y guarda el resultado en `contador`.",
                ],
                [3, "Los textos van entre comillas."],
                [4, "`print` con comas separa los valores con un espacio."],
            ],
        },
        "errors": [
            err(
                "variables",
                "asigna-compara",
                "Confunde `=` (asignar) con `==` (comparar)",
                "`=` guarda un valor; `==` pregunta si dos valores son iguales y devuelve True o False.",
                "Lee `x = 5` como «x pasa a valer 5» y `x == 5` como «¿x vale 5?».",
                "En un `if` o un `while` casi siempre va `==`; en una línea suelta, `=`.",
            ),
            err(
                "variables",
                "orden-asignacion",
                "Cree que la asignación funciona de izquierda a derecha",
                "En `a = b` el valor de `b` se copia en `a`, nunca al revés. En `x = x + 1` primero se calcula la derecha.",
                "Evalúa siempre la parte derecha completa y después escribe el resultado en la variable de la izquierda.",
                "Haz una traza: apunta en una tabla el valor de cada variable después de cada línea.",
            ),
            err(
                "variables",
                "nombre-texto",
                "Confunde el nombre de una variable con un texto",
                '`nombre` es una variable; `"nombre"` es el texto literal «nombre».',
                "Las comillas convierten cualquier cosa en texto literal.",
                "Si quieres el valor, escribe el nombre sin comillas; si quieres esas letras, con comillas.",
            ),
        ],
        "related": ["tipos", "trazado"],
    },
    {
        "id": "tipos",
        "title": "Tipos de datos y conversiones",
        "area": "fundamentos",
        "requires": ["variables"],
        "daw": 3,
        "ut": "prog-ut2",
        "lessons": ["tipos"],
        "summary": "int, float, str y bool; cómo y cuándo convertir entre ellos.",
        "when": "Siempre que leas datos del usuario (llegan como texto) o mezcles números y textos.",
        "example": {
            "code": 'edad = "20"\nprint(edad + "1")\nprint(int(edad) + 1)\nprint(type(3 / 2), type(3 // 2))',
            "lines": [
                [1, "`edad` es un texto, aunque parezca un número."],
                [2, "Con textos, `+` concatena: «20» + «1» = «201»."],
                [3, "`int()` lo convierte a entero y ahora `+` suma: 21."],
                [4, "`/` siempre da float; `//` entre enteros da int."],
            ],
        },
        "errors": [
            err(
                "tipos",
                "texto-numero",
                "Trata un texto que parece número como si fuera un número",
                '`"5"` es un str: `"5" + "5"` da `"55"` y `"5" + 5` da TypeError.',
                "Pregúntate de dónde viene el dato. Si viene de `input()` o va entre comillas, es texto.",
                "Convierte con `int()` o `float()` justo al leer el dato.",
            ),
            err(
                "tipos",
                "division-float",
                "Espera un entero de la división `/`",
                "En Python 3, `/` devuelve siempre float (`6 / 2` es `3.0`).",
                "¿Necesito decimales o un número de grupos completos? Para grupos completos, `//`.",
                "Usa `//` para cociente entero y `%` para el resto.",
            ),
            err(
                "tipos",
                "bool-texto",
                "Escribe los booleanos como texto o en minúscula",
                'Los booleanos son `True` y `False` (con mayúscula y sin comillas). `"False"` es un texto no vacío y cuenta como verdadero.',
                "Un booleano responde a una pregunta de sí o no; no es una palabra.",
                "Nunca pongas comillas a True/False.",
            ),
        ],
        "related": ["operadores", "entrada-salida"],
    },
    {
        "id": "operadores",
        "title": "Operadores y expresiones",
        "area": "fundamentos",
        "requires": ["tipos"],
        "daw": 3,
        "ut": "prog-ut2",
        "lessons": ["operadores"],
        "summary": "Aritméticos, de comparación y lógicos; prioridad y resto (`%`).",
        "when": "En cálculos, en las condiciones de `if` y `while`, y para saber si un número es par o múltiplo de otro.",
        "example": {
            "code": "n = 17\nprint(n // 5, n % 5)\nprint(n % 2 == 0)\nprint(2 + 3 * 4, (2 + 3) * 4)\nprint(n > 10 and n < 20)",
            "lines": [
                [2, "`//` da el cociente (3) y `%` el resto (2)."],
                [3, "Un número es par si el resto entre 2 es 0."],
                [4, "La multiplicación va antes que la suma; los paréntesis cambian el orden."],
                [5, "`and` es verdadero solo si las dos partes lo son."],
            ],
        },
        "errors": [
            err(
                "operadores",
                "prioridad",
                "Ignora la prioridad de los operadores",
                "`*`, `/`, `//` y `%` se evalúan antes que `+` y `-`; `not` antes que `and`, y `and` antes que `or`.",
                "Evalúa por niveles: primero paréntesis, luego potencias, luego `* / // %`, luego `+ -`, luego comparaciones y por último `not`, `and`, `or`.",
                "Si dudas, pon paréntesis: hacen el código más claro.",
            ),
            err(
                "operadores",
                "and-or",
                "Confunde `and` con `or`",
                "`and` exige que se cumplan las dos condiciones; `or`, al menos una.",
                "Di la condición en voz alta: «mayor de edad Y con entrada» frente a «sábado O domingo».",
                "Comprueba la condición con un caso que deba dar True y otro que deba dar False.",
            ),
            err(
                "operadores",
                "modulo",
                "No sabe usar el resto `%`",
                "`a % b` es el resto de dividir a entre b. Es 0 cuando a es múltiplo de b.",
                "Divide a mano: 17 entre 5 cabe 3 veces y sobran 2. Ese 2 es `17 % 5`.",
                "Recuerda los usos típicos: par (`n % 2 == 0`), múltiplo (`n % k == 0`) y última cifra (`n % 10`).",
            ),
            err(
                "operadores",
                "rango-encadenado",
                "Escribe mal un rango de valores",
                "`0 < n < 10` es válido en Python; `n > 0 and < 10` no, porque cada lado de `and` tiene que ser una comparación completa.",
                "Cada condición se evalúa sola: ¿n > 0? ¿n < 10?",
                "Usa `0 < n < 10` o `n > 0 and n < 10`.",
            ),
        ],
        "related": ["condicionales", "tipos"],
    },
    {
        "id": "entrada-salida",
        "title": "Entrada y salida",
        "area": "fundamentos",
        "requires": ["tipos"],
        "daw": 3,
        "ut": "prog-ut2",
        "lessons": ["input"],
        "summary": "`input()` siempre devuelve texto; `print()` y f-strings para mostrar resultados.",
        "when": "En casi todos los ejercicios de clase: leer datos del usuario y mostrar el resultado con el formato pedido.",
        "example": {
            "code": 'nombre = input("Nombre: ")\nedad = int(input("Edad: "))\nprint(f"{nombre} cumplirá {edad + 1} años")\nprint(f"Media: {7 / 3:.2f}")',
            "stdin": "Ana\n20\n",
            "lines": [
                [1, "`input` muestra el mensaje y devuelve lo escrito, siempre como texto."],
                [2, "Para operar con un número hay que convertir la entrada con `int()`."],
                [3, "En una f-string, lo que va entre llaves se evalúa."],
                [4, "`:.2f` muestra el número con 2 decimales."],
            ],
        },
        "errors": [
            err(
                "entrada-salida",
                "input-texto",
                "Olvida que `input()` devuelve texto",
                'Aunque el usuario escriba 5, `input()` devuelve `"5"`. Sumarlo a un número da TypeError y compararlo con un número no funciona.',
                "Pregunta: ¿voy a hacer cuentas o comparaciones numéricas con este dato?",
                'Convierte en la misma línea: `n = int(input("n: "))`.',
            ),
            err(
                "entrada-salida",
                "formato-salida",
                "No respeta el formato de salida pedido",
                "En los ejercicios corregidos, «Total: 5» y «total=5» son salidas distintas.",
                "Copia del enunciado el texto exacto que hay que mostrar.",
                "Usa f-strings y compara tu salida carácter a carácter con la del enunciado.",
            ),
            err(
                "entrada-salida",
                "print-return",
                "Confunde mostrar (`print`) con devolver (`return`)",
                "`print` solo escribe en pantalla; el valor no se puede usar después. `return` devuelve el valor a quien llamó a la función.",
                "¿El resultado lo va a leer una persona (print) o lo va a usar otra parte del programa (return)?",
                "Dentro de las funciones de cálculo usa `return`; muestra con `print` fuera de ellas.",
            ),
        ],
        "related": ["tipos", "validacion"],
    },
    {
        "id": "condicionales",
        "title": "Condicionales: if, elif y else",
        "area": "fundamentos",
        "requires": ["operadores"],
        "daw": 3,
        "ut": "prog-ut3",
        "lessons": ["condicionales"],
        "summary": "Elegir qué código se ejecuta según una condición.",
        "when": "Cuando el programa tiene que tomar una decisión: clasificar, validar, elegir un caso.",
        "example": {
            "code": 'nota = 6.5\nif nota >= 9:\n    print("Sobresaliente")\nelif nota >= 5:\n    print("Aprobado")\nelse:\n    print("Suspenso")',
            "lines": [
                [2, "Se comprueba la condición más exigente primero."],
                [
                    4,
                    "`elif` solo se evalúa si las anteriores fueron falsas: aquí ya sabemos que nota < 9.",
                ],
                [5, "Se ejecuta un único bloque: el primero cuya condición sea verdadera."],
                [6, "`else` recoge todos los casos restantes y no lleva condición."],
            ],
        },
        "errors": [
            err(
                "condicionales",
                "orden-elif",
                "Ordena mal las condiciones de una cadena if/elif",
                "Solo se ejecuta la primera rama verdadera. Si `nota >= 5` va antes que `nota >= 9`, un 10 sale «Aprobado».",
                "Ordena de la condición más restrictiva a la más general.",
                "Prueba la cadena con un valor de cada tramo y con los valores frontera (5, 9…).",
            ),
            err(
                "condicionales",
                "if-separados",
                "Usa varios `if` cuando necesita `elif`",
                "Con `if` separados se evalúan todos y pueden ejecutarse varias ramas.",
                "¿Los casos se excluyen entre sí? Entonces es una sola cadena if/elif/else.",
                "Usa `elif` cuando solo debe ejecutarse una opción.",
            ),
            err(
                "condicionales",
                "sangria",
                "Sangra mal el bloque del `if`",
                "Python decide qué va dentro del `if` por la sangría. Una línea sin sangrar se ejecuta siempre.",
                "Todo lo que depende de la condición va 4 espacios a la derecha del `if`.",
                "Revisa la sangría después de cada `:`.",
            ),
            err(
                "condicionales",
                "frontera",
                "Se equivoca en los valores frontera (`>` frente a `>=`)",
                "«Aprobado desde 5» es `nota >= 5`; con `nota > 5` el 5 queda suspenso.",
                "Lee el enunciado buscando «desde», «a partir de», «más de», «menos de».",
                "Prueba siempre el valor exacto de la frontera.",
            ),
        ],
        "related": ["operadores", "bucles"],
    },
    {
        "id": "bucles",
        "title": "Bucles: while y for",
        "area": "fundamentos",
        "requires": ["condicionales"],
        "daw": 3,
        "ut": "prog-ut3",
        "lessons": ["bucles"],
        "summary": "Repetir: `for` cuando sabes sobre qué iteras, `while` mientras se cumpla una condición.",
        "when": "`for` para recorrer una secuencia o repetir N veces; `while` cuando no sabes cuántas vueltas habrá (menús, validar datos).",
        "example": {
            "code": 'for i in range(1, 4):\n    print("vuelta", i)\n\nn = 10\nwhile n > 0:\n    n = n - 4\nprint("n final:", n)',
            "lines": [
                [1, "`range(1, 4)` produce 1, 2 y 3: el final no se incluye."],
                [
                    5,
                    "La condición se comprueba antes de cada vuelta: es la condición para **seguir**, no para salir.",
                ],
                [6, "Algo dentro del bucle tiene que cambiar la condición; si no, sería infinito."],
                [7, "Al salir, n vale -2: la última resta se hizo cuando n era 2."],
            ],
        },
        "errors": [
            err(
                "bucles",
                "condicion-salida",
                "Confunde la condición del bucle con la condición de salida",
                "`while` repite **mientras** la condición sea verdadera. Si quieres parar cuando `n == 0`, la condición es `n != 0`.",
                "Formula la frase «sigue repitiendo mientras…» y escribe eso como condición.",
                "Antes de escribir el `while`, escribe en un comentario cuándo debe terminar y niega esa condición.",
            ),
            err(
                "bucles",
                "range-fin",
                "Cree que `range` incluye el valor final",
                "`range(1, 5)` da 1, 2, 3 y 4. Para llegar a n hay que escribir `range(1, n + 1)`.",
                "Cuenta: `range(a, b)` da `b - a` números.",
                "Comprueba el primer y el último valor con `print(list(range(...)))`.",
            ),
            err(
                "bucles",
                "bucle-infinito",
                "Escribe un bucle infinito por no actualizar la variable",
                "Si nada dentro del `while` cambia la condición, el bucle no termina nunca.",
                "Identifica la variable de la condición y busca la línea que la modifica dentro del bucle.",
                "Cada `while` necesita: inicialización antes, condición y actualización dentro.",
            ),
            err(
                "bucles",
                "uno-de-mas",
                "Da una vuelta de más o de menos",
                "Los errores «por uno» aparecen al elegir mal el inicio, el final o el operador (`<` o `<=`).",
                "Traza la primera y la última vuelta a mano.",
                "Prueba con n = 1 y n = 0: si esos casos salen bien, el resto suele salir bien.",
            ),
        ],
        "related": ["acumuladores", "recorridos", "trazado"],
    },
    {
        "id": "acumuladores",
        "title": "Contadores y acumuladores",
        "area": "fundamentos",
        "requires": ["bucles"],
        "daw": 3,
        "ut": "prog-ut3",
        "lessons": ["bucles"],
        "summary": "Contar cuántas veces pasa algo y sumar (o multiplicar) valores dentro de un bucle.",
        "theory": (
            "Son los dos patrones más usados en los ejercicios de bucles.\n\n"
            "**Contador:** cuenta cuántas veces ocurre algo. Empieza en `0` y suma `1` cada vez que se cumple la condición.\n\n"
            "```\ncontador = 0\nfor n in numeros:\n    if n > 0:\n        contador += 1\n```\n\n"
            "**Acumulador:** va guardando un resultado parcial. Para sumas empieza en `0`; para productos, en `1` "
            "(empezar en 0 haría que todo el producto diera 0).\n\n"
            "```\nsuma = 0\nfor n in numeros:\n    suma += n\n```\n\n"
            "**Las tres reglas:**\n"
            "1. Se **inicializa antes** del bucle (si lo inicializas dentro, se reinicia en cada vuelta).\n"
            "2. Se **actualiza dentro** del bucle.\n"
            "3. Se **usa después** del bucle: la media se calcula al final, `suma / contador`, y comprobando que `contador` no sea 0."
        ),
        "when": "Contar aprobados, sumar precios, calcular medias, el máximo de una serie… Cualquier enunciado con «cuántos», «total» o «media».",
        "example": {
            "code": "notas = [7, 4, 9, 5]\naprobados = 0\nsuma = 0\nfor nota in notas:\n    suma += nota\n    if nota >= 5:\n        aprobados += 1\nprint(aprobados, suma / len(notas))",
            "lines": [
                [2, "Contador inicializado a 0, **antes** del bucle."],
                [3, "Acumulador de la suma, también antes del bucle."],
                [5, "`suma += nota` equivale a `suma = suma + nota`."],
                [7, "El contador solo aumenta cuando se cumple la condición."],
                [8, "La media se calcula **después** del bucle."],
            ],
        },
        "errors": [
            err(
                "acumuladores",
                "inicializa-dentro",
                "Inicializa el contador o acumulador dentro del bucle",
                "Si `suma = 0` va dentro del bucle, se pone a cero en cada vuelta y solo queda el último valor.",
                "¿Cuántas veces debe ejecutarse la inicialización? Una sola: antes del bucle.",
                "Escribe siempre el patrón completo: inicializar (fuera), actualizar (dentro), usar (después).",
            ),
            err(
                "acumuladores",
                "producto-cero",
                "Inicializa un producto a 0",
                "Cualquier número multiplicado por 0 es 0: el producto acumulado debe empezar en 1.",
                "El valor inicial es el elemento neutro de la operación: 0 para sumar, 1 para multiplicar.",
                "Para factoriales y potencias, empieza en 1.",
            ),
            err(
                "acumuladores",
                "media-dentro",
                "Calcula la media dentro del bucle o sin proteger la división",
                "La media solo es correcta cuando ya se han sumado todos los valores. Además, si no hay datos, dividir entre 0 da error.",
                "La media es un resultado final: va después del bucle.",
                "Calcula `suma / contador` tras el bucle y solo si `contador > 0`.",
            ),
            err(
                "acumuladores",
                "cuenta-todo",
                "Incrementa el contador fuera de la condición",
                "Si `contador += 1` no está dentro del `if`, cuenta todos los elementos, no solo los que cumplen la condición.",
                "¿El contador responde a «cuántos hay» o a «cuántos cumplen X»?",
                "Revisa la sangría: el incremento va dentro del `if`.",
            ),
        ],
        "related": ["bucles", "recorridos"],
    },
    {
        "id": "validacion",
        "title": "Validación de datos",
        "area": "fundamentos",
        "requires": ["bucles", "entrada-salida"],
        "daw": 3,
        "ut": "prog-ut3",
        "summary": "Pedir un dato hasta que sea válido, sin que el programa se rompa.",
        "theory": (
            "Un programa robusto **no se fía de la entrada**. Validar es comprobar que el dato cumple lo esperado "
            "(tipo, rango, formato) y, si no, volver a pedirlo.\n\n"
            "**Patrón «pedir hasta que sea válido»** con `while`:\n\n"
            '```\nedad = int(input("Edad: "))\nwhile edad < 0 or edad > 120:\n    print("Edad no válida")\n    edad = int(input("Edad: "))\n```\n\n'
            "La condición del `while` describe el dato **inválido**: se repite **mientras** el dato sea incorrecto.\n\n"
            "**Si el usuario escribe letras**, `int()` lanza `ValueError`. Se captura con `try/except` "
            "(ver Excepciones):\n\n"
            '```\nwhile True:\n    try:\n        edad = int(input("Edad: "))\n        if 0 <= edad <= 120:\n            break\n        print("Fuera de rango")\n    except ValueError:\n        print("Escribe un número")\n```\n\n'
            'Otras comprobaciones útiles: `texto.strip() == ""` (vacío), `texto.isdigit()` (solo cifras), '
            '`opcion in ("s", "n")` (valor de una lista).'
        ),
        "when": "Siempre que el dato venga del usuario o de un fichero: menús, edades, notas, opciones sí/no.",
        "example": {
            "code": 'nota = int(input("Nota (0-10): "))\nwhile nota < 0 or nota > 10:\n    print("Nota no válida")\n    nota = int(input("Nota (0-10): "))\nprint("Nota guardada:", nota)',
            "stdin": "12\n-1\n8\n",
            "lines": [
                [1, "Se pide el dato una primera vez antes del bucle."],
                [2, "La condición describe el dato **incorrecto**: fuera de 0-10."],
                [4, "Dentro del bucle se vuelve a pedir; sin esta línea, el bucle sería infinito."],
                [5, "Al salir del bucle, el dato es válido seguro."],
            ],
        },
        "errors": [
            err(
                "validacion",
                "condicion-invertida",
                "Escribe la condición del dato válido en el `while`",
                "El bucle de validación repite mientras el dato es **incorrecto**. Con la condición del dato válido, pide de nuevo justo los datos buenos.",
                "Completa la frase «vuelve a pedirlo mientras el dato sea…».",
                "Escribe primero la condición de validez y niégala con `not (...)` si te resulta más fácil.",
            ),
            err(
                "validacion",
                "no-repide",
                "No vuelve a pedir el dato dentro del bucle",
                "Si el `input()` no se repite dentro del `while`, la variable no cambia y el bucle es infinito.",
                "¿Qué línea cambia la variable de la condición dentro del bucle?",
                "Dentro del bucle de validación siempre hay un nuevo `input()`.",
            ),
            err(
                "validacion",
                "or-and",
                "Usa `and` para un rango inválido",
                "Un número no puede ser a la vez menor que 0 y mayor que 10: `nota < 0 and nota > 10` nunca es verdadero.",
                "Fuera de rango significa «por debajo O por encima».",
                "Rango válido: `0 <= n <= 10`. Inválido: `n < 0 or n > 10`.",
            ),
        ],
        "related": ["excepciones", "bucles"],
    },
    # ------------------------------------------------------------------ PROGRAMACIÓN
    {
        "id": "funciones",
        "title": "Funciones: parámetros y return",
        "area": "programacion",
        "requires": ["condicionales"],
        "daw": 3,
        "ut": "prog-ut3",
        "lessons": ["funciones"],
        "summary": "Encapsular un cálculo con un nombre, recibir datos por parámetros y devolver un resultado.",
        "when": "Cuando un cálculo se repite, cuando el programa crece o cuando el enunciado dice «implementa una función que…».",
        "example": {
            "code": "def area_rectangulo(base, altura):\n    return base * altura\n\nresultado = area_rectangulo(4, 3)\nprint(resultado)\nprint(area_rectangulo(altura=2, base=5))",
            "lines": [
                [1, "`base` y `altura` son **parámetros**: nombres que recibirán los valores."],
                [2, "`return` devuelve el resultado y termina la función."],
                [4, "4 y 3 son los **argumentos**: los valores concretos de esta llamada."],
                [6, "Con argumentos por nombre, el orden da igual."],
            ],
        },
        "errors": [
            err(
                "funciones",
                "print-en-vez-de-return",
                "Usa `print` en lugar de `return` dentro de la función",
                "Si la función solo hace `print`, devuelve `None`: `total = calcular(3)` guarda None.",
                "¿Quién usa el resultado? Si es otra parte del programa, la función tiene que devolverlo.",
                "Las funciones de cálculo terminan en `return`; el `print` va donde se llama.",
            ),
            err(
                "funciones",
                "return-en-bucle",
                "Pone el `return` dentro del bucle antes de tiempo",
                "`return` termina la función en ese momento: dentro de un bucle, se sale en la primera vuelta.",
                "¿Tengo ya la respuesta definitiva en esta vuelta? Si no, el `return` va después del bucle.",
                "Comprueba la sangría del `return`.",
            ),
            err(
                "funciones",
                "definir-no-llamar",
                "Define la función pero no la llama (o la llama sin paréntesis)",
                "`def` solo crea la función; no se ejecuta hasta que se llama con paréntesis: `saludar()`.",
                "Definir es escribir la receta; llamar es cocinarla.",
                "Después de cada `def`, busca dónde se llama.",
            ),
            err(
                "funciones",
                "ambito",
                "Intenta usar fuera una variable local de la función",
                "Las variables creadas dentro de una función solo existen dentro de ella.",
                "Si necesitas el valor fuera, la función tiene que devolverlo.",
                "Comunica funciones con parámetros (entrada) y `return` (salida), no con variables globales.",
            ),
        ],
        "related": ["modulos", "depuracion"],
    },
    {
        "id": "strings",
        "title": "Cadenas de texto",
        "area": "programacion",
        "requires": ["bucles"],
        "daw": 3,
        "ut": "prog-ut2",
        "lessons": ["cadenas", "metodos-string"],
        "summary": "Índices, slicing, recorrido y métodos de str; los textos son inmutables.",
        "when": "Contar letras, validar formatos, invertir palabras, limpiar entradas del usuario.",
        "example": {
            "code": 'texto = "Programar"\nprint(texto[0], texto[-1], len(texto))\nprint(texto[0:3], texto[::-1])\nvocales = 0\nfor letra in texto.lower():\n    if letra in "aeiou":\n        vocales += 1\nprint(vocales)',
            "lines": [
                [2, "El primer carácter está en la posición 0; `-1` es el último."],
                [
                    3,
                    "`[0:3]` va de la posición 0 a la 2 (el final no se incluye); `[::-1]` invierte.",
                ],
                [
                    5,
                    "Un `for` recorre el texto letra a letra; `lower()` devuelve una copia en minúsculas.",
                ],
                [6, "`in` comprueba si la letra está dentro de otro texto."],
            ],
        },
        "errors": [
            err(
                "strings",
                "indice-uno",
                "Cuenta las posiciones desde 1",
                "Las posiciones empiezan en 0: en un texto de longitud n, la última es `n - 1`.",
                "El índice indica cuántos caracteres hay antes de ese.",
                "Usa `texto[-1]` para el último y `range(len(texto))` para las posiciones.",
            ),
            err(
                "strings",
                "inmutable",
                "Intenta modificar un texto en su sitio",
                'Los str son inmutables: `texto[0] = "X"` da TypeError y `texto.upper()` no cambia `texto`, devuelve otro.',
                "Los métodos de str crean un texto nuevo: hay que guardarlo.",
                "Escribe `texto = texto.upper()` o construye un texto nuevo.",
            ),
            err(
                "strings",
                "slice-fin",
                "Cree que el slicing incluye la posición final",
                "`texto[1:4]` incluye las posiciones 1, 2 y 3, no la 4.",
                "Igual que `range`: el inicio entra y el final no.",
                "La longitud del trozo es `fin - inicio`.",
            ),
        ],
        "related": ["listas", "recorridos"],
    },
    {
        "id": "listas",
        "title": "Listas",
        "area": "programacion",
        "requires": ["bucles"],
        "daw": 3,
        "ut": "prog-ut6",
        "lessons": ["colecciones"],
        "summary": "Secuencias ordenadas y modificables: crear, acceder, añadir, quitar y recorrer.",
        "theory": (
            "Una **lista** guarda varios valores en orden: `notas = [7, 4, 9]`. Es **mutable**: se puede cambiar después de crearla.\n\n"
            "- **Acceso:** `notas[0]` (primero), `notas[-1]` (último), `notas[1:3]` (trozo).\n"
            "- **Añadir:** `append(x)` al final, `insert(i, x)` en una posición.\n"
            "- **Quitar:** `remove(x)` (por valor, el primero que encuentra), `pop()` (el último) o `pop(i)` (por posición).\n"
            "- **Consultar:** `len(lista)`, `x in lista`, `lista.index(x)`, `lista.count(x)`.\n"
            "- **Ordenar:** `lista.sort()` ordena la propia lista y devuelve `None`; `sorted(lista)` devuelve una lista nueva.\n\n"
            "**Recorrer:** `for nota in notas:` cuando solo necesitas los valores; "
            "`for i in range(len(notas)):` o `for i, nota in enumerate(notas):` cuando también necesitas la posición.\n\n"
            "**Cuidado con los alias:** `b = a` no copia la lista; los dos nombres apuntan a la misma. Para copiarla: `b = a.copy()` o `b = a[:]`."
        ),
        "when": "Cuando tienes una colección de datos del mismo tipo en un orden: notas, productos, palabras.",
        "example": {
            "code": 'compra = ["pan", "leche"]\ncompra.append("huevos")\ncompra.remove("pan")\nprint(compra, len(compra))\nordenada = sorted([3, 1, 2])\nprint(ordenada)',
            "lines": [
                [2, "`append` modifica la propia lista: no hace falta reasignar."],
                [3, "`remove` busca el valor y quita la primera aparición."],
                [5, "`sorted` devuelve una lista nueva ordenada; la original no cambia."],
            ],
        },
        "errors": [
            err(
                "listas",
                "sort-none",
                "Guarda el resultado de `lista.sort()`",
                "`sort()` ordena la lista en su sitio y devuelve `None`: `x = lista.sort()` deja x en None.",
                "¿El método modifica la lista o devuelve una nueva? `sort`, `append`, `remove` modifican y devuelven None.",
                "Usa `lista.sort()` sola en su línea, o `nueva = sorted(lista)`.",
            ),
            err(
                "listas",
                "alias",
                "Cree que `b = a` copia la lista",
                "Asignar una lista no la copia: `a` y `b` son la misma lista y un cambio en una se ve en la otra.",
                "Una variable es una etiqueta: `b = a` pega una segunda etiqueta en la misma lista.",
                "Copia con `a.copy()` o `a[:]` cuando necesites una lista independiente.",
            ),
            err(
                "listas",
                "indice-fuera",
                "Accede a una posición que no existe",
                "En una lista de n elementos, las posiciones válidas van de 0 a n - 1. `lista[n]` da IndexError.",
                "¿Cuántos elementos hay? La última posición es uno menos.",
                "Recorre con `for x in lista` o `range(len(lista))`, nunca con `range(len(lista) + 1)`.",
            ),
            err(
                "listas",
                "modificar-recorriendo",
                "Elimina elementos mientras recorre la misma lista",
                "Al quitar un elemento, los siguientes se desplazan y el `for` se salta alguno.",
                "No cambies el tamaño de lo que estás recorriendo.",
                "Construye una lista nueva con los elementos que quieres conservar.",
            ),
        ],
        "related": ["recorridos", "tuplas-conjuntos", "diccionarios"],
    },
    {
        "id": "tuplas-conjuntos",
        "title": "Tuplas y conjuntos",
        "area": "programacion",
        "requires": ["listas"],
        "daw": 2,
        "ut": "prog-ut6",
        "lessons": ["colecciones"],
        "summary": "Tuplas: secuencias inmutables. Conjuntos: sin orden y sin repetidos.",
        "theory": (
            "**Tupla:** como una lista, pero **inmutable**. Se escribe con paréntesis: `punto = (3, 4)`. "
            "Sirve para datos que van juntos y no deben cambiar (coordenadas, una fecha, varios valores devueltos por una función).\n\n"
            "- Se accede igual que a una lista: `punto[0]`.\n"
            "- **Desempaquetado:** `x, y = punto`.\n"
            "- Una tupla de un elemento lleva coma: `(5,)`. Sin la coma, `(5)` es solo el número 5.\n\n"
            "**Conjunto (`set`):** colección **sin orden y sin elementos repetidos**: `{1, 2, 3}`. "
            "El conjunto vacío es `set()`; `{}` es un diccionario vacío.\n\n"
            "- Quitar repetidos: `set(lista)`.\n"
            "- Comprobar si un elemento está (`in`) es muy rápido.\n"
            "- Operaciones: unión `|`, intersección `&`, diferencia `-`.\n"
            "- No tienen posiciones: `conjunto[0]` da error."
        ),
        "when": "Tupla: datos fijos que van juntos. Conjunto: quitar repetidos o comprobar pertenencia rápidamente.",
        "example": {
            "code": "def min_max(numeros):\n    return min(numeros), max(numeros)\n\nmenor, mayor = min_max([4, 9, 1])\nprint(menor, mayor)\nprint(sorted(set([3, 1, 3, 2, 1])))\nprint({1, 2, 3} & {2, 3, 4})",
            "lines": [
                [2, "Devolver dos valores separados por coma devuelve una tupla."],
                [4, "Desempaquetado: cada variable recibe un elemento de la tupla."],
                [6, "`set` quita los repetidos; `sorted` lo convierte en una lista ordenada."],
                [7, "`&` es la intersección: los elementos que están en los dos conjuntos."],
            ],
        },
        "errors": [
            err(
                "tuplas-conjuntos",
                "tupla-mutable",
                "Intenta modificar una tupla",
                "Las tuplas no se pueden modificar: `t[0] = 1` da TypeError y no tienen `append`.",
                "¿Estos datos deben cambiar? Si sí, usa una lista.",
                "Para «cambiar» una tupla, crea otra nueva.",
            ),
            err(
                "tuplas-conjuntos",
                "set-orden",
                "Espera que un conjunto mantenga el orden o tenga posiciones",
                "Un set no tiene orden ni índices: `s[0]` da TypeError y el orden al imprimirlo no está garantizado.",
                "Un conjunto responde a «¿está o no está?», no a «¿qué posición ocupa?».",
                "Si necesitas orden, conviértelo con `sorted(conjunto)`.",
            ),
            err(
                "tuplas-conjuntos",
                "llaves-vacias",
                "Cree que `{}` es un conjunto vacío",
                "`{}` crea un diccionario vacío. El conjunto vacío es `set()`.",
                "Las llaves vacías se reservaron para los diccionarios, que existían antes.",
                "Escribe siempre `set()` para un conjunto vacío.",
            ),
        ],
        "related": ["listas", "diccionarios"],
    },
    {
        "id": "diccionarios",
        "title": "Diccionarios",
        "area": "programacion",
        "requires": ["listas"],
        "daw": 3,
        "ut": "prog-ut6",
        "lessons": ["colecciones"],
        "summary": "Pares clave → valor: buscar, contar y agrupar datos por nombre.",
        "theory": (
            'Un **diccionario** asocia **claves** con **valores**: `edades = {"Ana": 20, "Luis": 22}`.\n\n'
            '- **Leer:** `edades["Ana"]` (KeyError si no existe) o `edades.get("Ana", 0)` (devuelve 0 si no existe).\n'
            '- **Añadir o cambiar:** `edades["Eva"] = 19`.\n'
            '- **Borrar:** `del edades["Luis"]` o `edades.pop("Luis")`.\n'
            '- **Comprobar:** `"Ana" in edades` busca entre las **claves**.\n'
            "- **Recorrer:** `for clave in d`, `for valor in d.values()`, `for clave, valor in d.items()`.\n\n"
            "Las claves son **únicas** y deben ser inmutables (str, int, tuplas). Asignar a una clave que ya existe sustituye su valor.\n\n"
            "**Patrón contador con diccionario** (muy habitual en clase):\n\n"
            "```\nfrecuencia = {}\nfor letra in texto:\n    frecuencia[letra] = frecuencia.get(letra, 0) + 1\n```"
        ),
        "when": "Cuando buscas datos por un nombre o código (agenda, stock, notas por alumno) o cuentas apariciones.",
        "example": {
            "code": 'stock = {"manzana": 5, "pera": 0}\nstock["kiwi"] = 3\nstock["manzana"] -= 1\nfor fruta, cantidad in stock.items():\n    if cantidad > 0:\n        print(fruta, cantidad)\nprint(stock.get("uva", 0))',
            "lines": [
                [2, "Asignar a una clave nueva la añade."],
                [3, "Con una clave existente, se modifica su valor."],
                [4, "`items()` da cada pareja (clave, valor) para desempaquetarla."],
                [7, "`get` con valor por defecto evita el KeyError."],
            ],
        },
        "errors": [
            err(
                "diccionarios",
                "keyerror",
                "Lee una clave que puede no existir con `d[clave]`",
                "`d[clave]` lanza KeyError si la clave no está. Pasa mucho al contar la primera aparición.",
                "¿Es posible que la clave todavía no esté? Entonces necesitas `get` o comprobar con `in`.",
                "Usa `d.get(clave, 0)` o `if clave in d:`.",
            ),
            err(
                "diccionarios",
                "in-valores",
                "Cree que `in` busca entre los valores",
                "`x in d` busca entre las claves. Para los valores: `x in d.values()`.",
                "Un diccionario se indexa por claves: todo lo que no dice lo contrario trabaja con claves.",
                "Escribe `d.values()` o `d.items()` cuando quieras otra cosa.",
            ),
            err(
                "diccionarios",
                "recorrido-claves",
                "Recorre el diccionario esperando valores o parejas",
                "`for x in d` da solo las claves.",
                "¿Necesito la clave, el valor o los dos?",
                "Para los dos: `for clave, valor in d.items()`.",
            ),
        ],
        "related": ["listas", "recorridos"],
    },
    {
        "id": "recorridos",
        "title": "Recorridos, búsqueda, máximo y mínimo",
        "area": "programacion",
        "requires": ["listas", "acumuladores"],
        "daw": 3,
        "ut": "prog-ut6",
        "summary": "Los algoritmos clásicos sobre colecciones: buscar, contar, filtrar y quedarse con el mejor.",
        "theory": (
            "Casi todos los problemas sobre listas son una variación de cuatro algoritmos:\n\n"
            "**1. Recorrido con acumulador:** sumar, contar, construir una lista nueva (filtrar).\n\n"
            "**2. Búsqueda lineal:** ¿está el elemento? Se recorre hasta encontrarlo y se para.\n\n"
            "```\ndef buscar(lista, objetivo):\n    for i in range(len(lista)):\n        if lista[i] == objetivo:\n            return i\n    return -1\n```\n\n"
            "El `return -1` va **después** del bucle: solo sabemos que no está cuando lo hemos mirado todo.\n\n"
            "**3. Máximo / mínimo:** se toma el **primer elemento** como candidato y se compara con el resto. "
            "Empezar en 0 falla si todos los números son negativos.\n\n"
            "```\nmayor = lista[0]\nfor x in lista[1:]:\n    if x > mayor:\n        mayor = x\n```\n\n"
            "**4. Comprobación universal / existencial:** «¿todos cumplen?» empieza suponiendo `True` y cambia a `False` al encontrar uno que no cumple; "
            "«¿alguno cumple?» empieza en `False`.\n\n"
            "**Complejidad básica:** una búsqueda lineal mira, en el peor caso, los n elementos (O(n)). "
            "Dos bucles anidados sobre la misma lista hacen unas n² comparaciones (O(n²)): con 1.000 elementos, un millón."
        ),
        "when": "En los ejercicios de «busca», «el mayor», «cuántos cumplen», «¿todos son…?» o «filtra los que…».",
        "example": {
            "code": "temperaturas = [-3, -8, -1, -5]\nminima = temperaturas[0]\nfor t in temperaturas:\n    if t < minima:\n        minima = t\nprint(minima)\n\ntodas_negativas = True\nfor t in temperaturas:\n    if t >= 0:\n        todas_negativas = False\nprint(todas_negativas)",
            "lines": [
                [2, "El candidato inicial es el primer elemento, no 0."],
                [4, "Si aparece uno menor, pasa a ser el nuevo candidato."],
                [8, "«¿Todas cumplen?»: se supone que sí hasta encontrar un contraejemplo."],
                [10, "Un solo contraejemplo basta para que sea False."],
            ],
        },
        "errors": [
            err(
                "recorridos",
                "max-cero",
                "Inicializa el máximo (o el mínimo) con 0",
                "Si todos los valores son negativos, el máximo inicializado a 0 nunca cambia y el resultado es 0, que no está en la lista.",
                "El candidato inicial debe ser un valor real de la lista.",
                "Inicializa con `lista[0]` (comprobando antes que la lista no esté vacía).",
            ),
            err(
                "recorridos",
                "no-encontrado-dentro",
                "Decide «no encontrado» dentro del bucle",
                "Un `else: return -1` dentro del bucle termina en el primer elemento que no coincide.",
                "Solo puedo afirmar que no está cuando he revisado todos los elementos.",
                "El «no encontrado» va después del bucle, sin sangría extra.",
            ),
            err(
                "recorridos",
                "todos-alguno",
                "Confunde «todos cumplen» con «alguno cumple»",
                "Para «todos» se empieza en True y basta un contraejemplo; para «alguno», en False y basta un ejemplo.",
                "¿Qué valor tiene la respuesta si la lista está vacía? Para «todos», True; para «alguno», False.",
                "Escribe el valor inicial pensando en el caso de la lista vacía.",
            ),
            err(
                "recorridos",
                "no-para",
                "Sigue recorriendo cuando ya ha encontrado el elemento",
                "Sin `break` ni `return`, el bucle sigue y puede sobrescribir el resultado o hacer trabajo innecesario.",
                "¿Necesito mirar el resto una vez encontrado?",
                "Usa `return` dentro de una función, o `break` si estás en el programa principal.",
            ),
        ],
        "related": ["listas", "acumuladores", "trazado"],
    },
    {
        "id": "excepciones",
        "title": "Excepciones: try, except y raise",
        "area": "programacion",
        "requires": ["funciones"],
        "daw": 3,
        "ut": "prog-ut3",
        "lessons": ["excepciones"],
        "summary": "Controlar los errores en ejecución sin que el programa termine de golpe.",
        "when": "Al convertir entradas del usuario, abrir ficheros o dividir: operaciones que pueden fallar por causas externas.",
        "example": {
            "code": 'def dividir(a, b):\n    try:\n        return a / b\n    except ZeroDivisionError:\n        print("No se puede dividir entre 0")\n        return None\n\nprint(dividir(10, 4))\nprint(dividir(1, 0))',
            "lines": [
                [2, "Dentro de `try` va el código que puede fallar."],
                [4, "Se captura solo la excepción esperada, no todas."],
                [5, "El programa continúa en vez de terminar con un traceback."],
            ],
        },
        "errors": [
            err(
                "excepciones",
                "except-generico",
                "Captura todas las excepciones con un `except:` vacío",
                "Un `except:` sin tipo oculta también los errores de programación (NameError, TypeError) y dificulta depurar.",
                "¿Qué error concreto espero que ocurra aquí?",
                "Captura la excepción concreta: `except ValueError:`.",
            ),
            err(
                "excepciones",
                "try-gigante",
                "Mete demasiado código dentro del `try`",
                "Si el `try` es muy grande, no sabes qué línea falló y puedes capturar errores que no esperabas.",
                "¿Qué línea exacta puede lanzar la excepción?",
                "Deja en el `try` solo la operación arriesgada.",
            ),
            err(
                "excepciones",
                "tipo-equivocado",
                "Captura un tipo de excepción que no corresponde",
                '`int("hola")` lanza ValueError, no TypeError; dividir entre 0 lanza ZeroDivisionError.',
                "Provoca el error a propósito en la consola y lee su nombre en la última línea del traceback.",
                "Aprende los cinco habituales: ValueError, TypeError, ZeroDivisionError, IndexError y KeyError.",
            ),
        ],
        "related": ["validacion", "archivos", "depuracion"],
    },
    {
        "id": "modulos",
        "title": "Módulos e importación",
        "area": "programacion",
        "requires": ["funciones"],
        "daw": 2,
        "ut": "prog-ut3",
        "lessons": ["modulos"],
        "summary": "Organizar el código en ficheros y reutilizar la biblioteca estándar.",
        "when": "Cuando el programa crece (separar funciones en otro fichero) o necesitas math, random, datetime…",
        "example": {
            "code": "import math\nfrom random import seed, randint\n\nprint(math.sqrt(16), math.pi > 3)\nseed(1)\nprint(1 <= randint(1, 6) <= 6)",
            "lines": [
                [1, "`import math` obliga a escribir el prefijo: `math.sqrt`."],
                [2, "`from ... import` trae nombres concretos y se usan sin prefijo."],
                [5, "`seed` fija la semilla para que los aleatorios se repitan (útil en pruebas)."],
            ],
        },
        "errors": [
            err(
                "modulos",
                "prefijo",
                "Usa una función del módulo sin el prefijo (o con él cuando no toca)",
                "Con `import math` se escribe `math.sqrt`; con `from math import sqrt`, solo `sqrt`.",
                "Mira la línea del import: ¿importa el módulo o el nombre concreto?",
                "Usa `import modulo` y el prefijo: deja claro de dónde viene cada función.",
            ),
            err(
                "modulos",
                "nombre-fichero",
                "Llama a su fichero igual que un módulo estándar",
                "Un fichero propio llamado `random.py` tapa al módulo `random` y los imports dejan de funcionar.",
                "Python busca primero en la carpeta del programa.",
                "No nombres tus ficheros como módulos de la biblioteca estándar.",
            ),
        ],
        "related": ["funciones"],
    },
    {
        "id": "archivos",
        "title": "Ficheros de texto",
        "area": "programacion",
        "requires": ["excepciones", "strings"],
        "daw": 2,
        "ut": "prog-ut8",
        "lessons": ["archivos"],
        "summary": "Leer y escribir ficheros con `with open(...)`, línea a línea.",
        "when": "Para guardar datos entre ejecuciones o procesar ficheros (CSV, registros, listados).",
        "example": {
            "code": 'with open("notas.txt", "w", encoding="utf-8") as f:\n    f.write("Ana;7\\nLuis;4\\n")\n\nwith open("notas.txt", encoding="utf-8") as f:\n    for linea in f:\n        nombre, nota = linea.strip().split(";")\n        print(nombre, int(nota) >= 5)',
            "lines": [
                [1, 'Modo `"w"`: crea el fichero o **borra** su contenido si ya existía.'],
                [2, "`write` no añade el salto de línea: hay que escribir `\\n`."],
                [5, "Recorrer el fichero da una línea en cada vuelta, con su `\\n` al final."],
                [6, "`strip` quita el salto de línea y `split` separa los campos."],
            ],
        },
        "errors": [
            err(
                "archivos",
                "modo-w",
                'Abre con `"w"` un fichero que quería ampliar',
                'El modo `"w"` vacía el fichero al abrirlo. Para añadir al final se usa `"a"`.',
                "¿Quiero empezar de cero o añadir a lo que hay?",
                '`"r"` leer, `"w"` escribir desde cero, `"a"` añadir.',
            ),
            err(
                "archivos",
                "salto-linea",
                "Olvida el salto de línea al leer o escribir",
                "Cada línea leída termina en `\\n`, y `write` no lo añade solo.",
                "Imprime `repr(linea)` para ver los caracteres ocultos.",
                "Usa `linea.strip()` al leer y añade `\\n` al escribir.",
            ),
            err(
                "archivos",
                "sin-with",
                "Abre el fichero sin cerrarlo",
                "Sin cerrar, los datos pueden no guardarse y el fichero queda bloqueado.",
                "¿Quién cierra el fichero si ocurre un error a mitad?",
                "Usa siempre `with open(...) as f:`: lo cierra solo.",
            ),
        ],
        "related": ["excepciones", "strings"],
    },
    # ------------------------------------------------------------------ LÓGICA
    {
        "id": "pseudocodigo",
        "title": "Del enunciado al pseudocódigo y del pseudocódigo al código",
        "area": "logica",
        "requires": ["algoritmos", "condicionales"],
        "daw": 3,
        "ut": "prog-ut1",
        "summary": "Escribir el algoritmo en lenguaje estructurado y traducirlo a Python paso a paso.",
        "theory": (
            "El **pseudocódigo** describe un algoritmo con palabras estructuradas, sin preocuparse de la sintaxis de un lenguaje. "
            "En clase y en los exámenes se usa para comprobar que sabes **resolver** el problema, no solo escribir Python.\n\n"
            "**Correspondencias con Python:**\n\n"
            "| Pseudocódigo | Python |\n|---|---|\n"
            "| `LEER n` | `n = int(input())` |\n"
            "| `ESCRIBIR x` | `print(x)` |\n"
            "| `x ← x + 1` | `x = x + 1` |\n"
            "| `SI cond ENTONCES … SINO … FIN SI` | `if cond: … else: …` |\n"
            "| `MIENTRAS cond HACER … FIN MIENTRAS` | `while cond: …` |\n"
            "| `PARA i DESDE 1 HASTA n HACER` | `for i in range(1, n + 1):` |\n"
            "| `REPETIR … HASTA QUE cond` | `while True: … if cond: break` |\n\n"
            "**Método:**\n"
            "1. Del enunciado, saca entrada, salida y proceso (ver «Comprender el problema»).\n"
            "2. Escribe el pseudocódigo con una estructura por línea y sangría.\n"
            "3. Trázalo a mano con un ejemplo.\n"
            "4. Tradúcelo línea a línea. Fíjate en dos trampas: `HASTA n` **incluye** n (en `range` hay que poner `n + 1`), y "
            "`REPETIR … HASTA QUE` termina **cuando** la condición es verdadera (al revés que `while`)."
        ),
        "when": "En los ejercicios que piden el algoritmo, y siempre que un problema no te salga directamente en Python.",
        "example": {
            "code": "# ALGORITMO suma_pares\n#   LEER n\n#   suma ← 0\n#   PARA i DESDE 1 HASTA n HACER\n#     SI i MOD 2 = 0 ENTONCES suma ← suma + i\n#   ESCRIBIR suma\nn = int(input())\nsuma = 0\nfor i in range(1, n + 1):\n    if i % 2 == 0:\n        suma = suma + i\nprint(suma)",
            "stdin": "6\n",
            "lines": [
                [7, "`LEER n` se traduce como `input` convertido a entero."],
                [9, "`HASTA n` incluye n: en Python, `range(1, n + 1)`."],
                [10, "`MOD` es el operador `%`, y `=` en una comparación es `==`."],
                [12, "`ESCRIBIR` es `print`."],
            ],
        },
        "errors": [
            err(
                "pseudocodigo",
                "hasta-incluye",
                "Traduce `PARA i DESDE 1 HASTA n` como `range(1, n)`",
                "En pseudocódigo, HASTA n incluye n; `range(1, n)` se detiene en n - 1.",
                "Pregunta: ¿el último valor del pseudocódigo aparece en mi range?",
                "Traduce siempre `HASTA n` como `range(inicio, n + 1)`.",
            ),
            err(
                "pseudocodigo",
                "repetir-hasta",
                "Traduce `REPETIR … HASTA QUE cond` como `while cond`",
                "REPETIR…HASTA QUE se ejecuta al menos una vez y para **cuando** la condición es verdadera; `while cond` repite **mientras** es verdadera.",
                "HASTA QUE = condición de salida; MIENTRAS = condición de permanencia.",
                "Usa `while True:` con `if cond: break` al final del bloque, o `while not cond:` con una primera ejecución antes.",
            ),
            err(
                "pseudocodigo",
                "orden-pasos",
                "Ordena mal los pasos del algoritmo",
                "Un paso no puede usar un dato que aún no se ha leído o calculado.",
                "Para cada paso, ¿de dónde salen los datos que usa?",
                "Leer → inicializar → procesar (bucles y decisiones) → escribir.",
            ),
        ],
        "related": ["algoritmos", "trazado"],
    },
    {
        "id": "trazado",
        "title": "Lectura y trazado de código",
        "area": "logica",
        "requires": ["bucles"],
        "daw": 3,
        "ut": "prog-ut3",
        "summary": "Ejecutar un programa a mano, línea a línea, apuntando el valor de cada variable.",
        "theory": (
            "**Trazar** es ejecutar un programa a mano, como lo haría el intérprete. Es la habilidad que más se pregunta en los exámenes "
            "(«¿qué muestra este programa?») y la mejor herramienta para encontrar errores.\n\n"
            "**Tabla de traza:** una columna por variable, una fila por cada vez que algo cambia, y una columna para lo que se muestra.\n\n"
            "```\nsuma = 0\nfor i in range(1, 4):\n    suma += i\nprint(suma)\n```\n\n"
            "| paso | i | suma | salida |\n|---|---|---|---|\n| inicio | – | 0 | |\n| vuelta 1 | 1 | 1 | |\n| vuelta 2 | 2 | 3 | |\n| vuelta 3 | 3 | 6 | |\n| final | 3 | 6 | 6 |\n\n"
            "**Reglas para no equivocarte:**\n"
            "- Ejecuta **exactamente** lo que pone, no lo que crees que el programa pretende hacer.\n"
            "- En cada `if` y `while`, evalúa la condición con los valores **actuales**.\n"
            "- `print` dentro del bucle escribe una línea por vuelta; fuera, una sola vez.\n"
            "- Fíjate en la sangría: decide qué está dentro de cada bloque."
        ),
        "when": "Para responder «¿qué muestra?», para comprobar tu algoritmo antes de programarlo y para encontrar errores lógicos.",
        "example": {
            "code": "x = 5\ny = 2\nwhile x > y:\n    x = x - 1\n    y = y + 1\nprint(x, y)",
            "lines": [
                [3, "Vuelta 1: 5 > 2 es verdadero → x = 4, y = 3."],
                [3, "Vuelta 2: 4 > 3 es verdadero → x = 3, y = 4."],
                [3, "Vuelta 3: 3 > 4 es falso → se sale del bucle."],
                [6, "Se muestra «3 4»."],
            ],
        },
        "errors": [
            err(
                "trazado",
                "intencion",
                "Responde lo que el programa «debería» hacer, no lo que hace",
                "El intérprete no adivina intenciones: si el código tiene un error, la salida refleja ese error.",
                "Olvida el propósito y ejecuta cada línea literalmente.",
                "Haz la tabla de traza aunque el programa parezca fácil.",
            ),
            err(
                "trazado",
                "print-dentro-fuera",
                "Confunde un `print` dentro del bucle con uno fuera",
                "Un `print` sangrado dentro del bucle se ejecuta en cada vuelta; uno sin sangrar, una vez al final.",
                "Mira la columna en la que empieza el `print`.",
                "Cuenta cuántas líneas de salida tendrá el programa antes de calcularlas.",
            ),
            err(
                "trazado",
                "valor-antiguo",
                "Usa un valor antiguo de la variable",
                "Tras `x = x + 1`, las líneas siguientes ven el valor nuevo de x.",
                "Actualiza la tabla después de cada asignación, no al final de la vuelta.",
                "Tacha el valor anterior en tu tabla cada vez que una variable cambie.",
            ),
        ],
        "related": ["bucles", "depuracion"],
    },
    {
        "id": "depuracion",
        "title": "Depuración y análisis de errores",
        "area": "logica",
        "requires": ["funciones"],
        "daw": 3,
        "ut": "prog-ut3",
        "summary": "Leer un traceback, distinguir errores de sintaxis, de ejecución y lógicos, y localizarlos.",
        "theory": (
            "Hay tres tipos de errores:\n\n"
            "1. **De sintaxis** (`SyntaxError`, `IndentationError`): el programa ni siquiera empieza. Faltan `:`, paréntesis, comillas o la sangría es incorrecta.\n"
            "2. **De ejecución** (excepciones): el programa empieza y se detiene en una línea concreta (`NameError`, `TypeError`, `ZeroDivisionError`, `IndexError`…).\n"
            "3. **Lógicos:** el programa termina sin errores, pero el resultado es incorrecto. Son los más difíciles: solo los detectan las pruebas y las trazas.\n\n"
            "**Cómo leer un traceback:** empieza por la **última línea**: dice el tipo de error y el motivo. "
            "La línea de encima indica el fichero y el **número de línea** donde ocurrió.\n\n"
            '```\nTraceback (most recent call last):\n  File "notas.py", line 3, in <module>\n    media = suma / total\nZeroDivisionError: division by zero\n```\n\n'
            "**Depurar con método (no a ciegas):**\n"
            "1. **Reproduce** el error con una entrada concreta.\n"
            "2. **Formula una hipótesis:** «creo que `total` vale 0 porque…».\n"
            "3. **Compruébala:** un `print` temporal o el depurador de PyCharm (punto de ruptura y ejecución paso a paso).\n"
            "4. **Corrige** una sola cosa y vuelve a probar, también con los casos que ya funcionaban."
        ),
        "when": "Cada vez que algo falla. Y en el examen, en los ejercicios de «encuentra el error».",
        "example": {
            "code": "def media(numeros):\n    if not numeros:\n        return 0\n    return sum(numeros) / len(numeros)\n\nprint(media([4, 6]))\nprint(media([]))",
            "lines": [
                [
                    2,
                    "Corrección de un error de ejecución: con una lista vacía, `len` es 0 y la división fallaría.",
                ],
                [
                    3,
                    "Se decide qué devolver en el caso límite en vez de dejar que el programa se rompa.",
                ],
                [7, "Se prueba también el caso que antes fallaba."],
            ],
        },
        "errors": [
            err(
                "depuracion",
                "lee-primera-linea",
                "Lee el traceback por arriba y se pierde",
                "La información importante está abajo: tipo de error, mensaje y línea donde ocurrió.",
                "Lee de abajo arriba: ¿qué error?, ¿en qué línea?, ¿qué valores tenían las variables ahí?",
                "Copia la última línea del traceback y busca su significado si no lo conoces.",
            ),
            err(
                "depuracion",
                "linea-anterior",
                "Busca un error de sintaxis solo en la línea señalada",
                "Si falta un paréntesis o unas comillas, Python suele quejarse en la línea siguiente.",
                "Si la línea señalada parece correcta, mira la anterior.",
                "Revisa que cada paréntesis, corchete y comilla abierto se cierre.",
            ),
            err(
                "depuracion",
                "tipo-error",
                "No distingue errores de sintaxis, de ejecución y lógicos",
                "Cada tipo se busca de forma distinta: la sintaxis en la escritura, la ejecución en la línea del traceback y los lógicos con trazas y pruebas.",
                "¿El programa no arranca, se detiene a mitad o termina con un resultado incorrecto?",
                "Clasifica el error antes de intentar arreglarlo.",
            ),
            err(
                "depuracion",
                "cambios-a-ciegas",
                "Cambia cosas al azar hasta que funciona",
                "Los cambios sin hipótesis pueden ocultar el error con otro o romper lo que funcionaba.",
                "¿Qué creo que está pasando y cómo puedo comprobarlo?",
                "Una hipótesis, una comprobación, un cambio.",
            ),
        ],
        "related": ["trazado", "excepciones"],
    },
    # ------------------------------------------------------------------ MÁS ADELANTE
    {
        "id": "poo",
        "title": "Clases y objetos (introducción a la POO)",
        "area": "avanzado",
        "requires": ["funciones", "diccionarios"],
        "daw": 2,
        "ut": "prog-ut5",
        "lessons": ["poo"],
        "summary": "Agrupar datos y comportamiento: clases, objetos, atributos y métodos.",
        "when": "Cuando un programa maneja entidades con datos y acciones propias (cuenta bancaria, alumno, producto). Llega después de dominar funciones y colecciones.",
        "example": {
            "code": 'class Cuenta:\n    def __init__(self, titular, saldo=0):\n        self.titular = titular\n        self.saldo = saldo\n\n    def ingresar(self, cantidad):\n        self.saldo += cantidad\n\nc = Cuenta("Ana")\nc.ingresar(50)\nprint(c.titular, c.saldo)',
            "lines": [
                [1, "La clase es el molde; cada objeto creado con ella es una instancia."],
                [2, "`__init__` se ejecuta al crear el objeto; `self` es el propio objeto."],
                [3, "`self.titular` es un atributo: un dato que guarda cada objeto."],
                [9, "Al crear el objeto no se pasa `self`: Python lo añade solo."],
            ],
        },
        "errors": [
            err(
                "poo",
                "olvida-self",
                "Olvida `self` en los métodos o en los atributos",
                "Sin `self.` la variable es local del método y se pierde; sin `self` como primer parámetro, la llamada falla.",
                "¿Este dato pertenece al objeto? Entonces es `self.dato`.",
                "Todo método de instancia recibe `self` y guarda los atributos como `self.x`.",
            ),
            err(
                "poo",
                "clase-objeto",
                "Confunde la clase con el objeto",
                'La clase es la plantilla; los objetos se crean llamándola: `c = Cuenta("Ana")`.',
                "Una clase es «Perro»; un objeto es «mi perro Toby».",
                "Llama a los métodos sobre un objeto, no sobre la clase.",
            ),
        ],
        "related": ["funciones", "diccionarios"],
    },
]
