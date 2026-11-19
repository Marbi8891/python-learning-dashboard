# ruff: noqa: E501
"""Unidad 1 del módulo de POO: fundamentos de la programación orientada a objetos.

Concepto `poo-fundamentos` (área `poo`): del programa procedural a las clases, qué es una clase y
qué es un objeto, cómo se modela un enunciado, cuándo conviene la POO y sus cuatro pilares.
La salida de los ejemplos la obtiene build_learning.py ejecutándolos.
"""

from exercises import case, choice, code, output
from poo_common import practice, proposed, ref

CID = "poo-fundamentos"

CONCEPT = {
    "id": CID,
    "title": "Fundamentos de la programación orientada a objetos",
    "area": "poo",
    "requires": ["funciones", "diccionarios"],
    "daw": 2,
    "ut": "prog-ut4",
    "lessons": ["poo"],
    "summary": "Qué es la programación orientada a objetos, en qué se diferencia de la procedural y cuándo conviene usarla.",
    "when": "Antes de escribir tu primera clase: te ayuda a leer un enunciado y decidir qué serán clases, atributos y métodos, y cuándo basta con una función.",
    "example": {
        "code": 'class Producto:\n    def __init__(self, nombre, precio):\n        self.nombre = nombre                # atributo: una característica\n        self.precio = precio\n\n    def con_descuento(self, porcentaje):    # método: una acción\n        return self.precio * (1 - porcentaje / 100)\n\n\nteclado = Producto("Teclado", 40)          # dos instancias\nraton = Producto("Ratón", 20)              # de la misma clase\nprint(teclado.nombre, teclado.con_descuento(25))\nprint(raton.nombre, raton.con_descuento(25))',
        "lines": [
            [
                1,
                "`Producto` es la clase: el molde que dice qué tiene y qué sabe hacer un producto.",
            ],
            [3, "`nombre` y `precio` son atributos: los datos que guarda cada producto."],
            [6, "`con_descuento` es un método: una acción que usa los datos del propio objeto."],
            [10, "`teclado` y `raton` son objetos (instancias) distintos de la misma clase."],
            [12, "Cada objeto responde con sus propios datos: 40 € y 20 € con un 25 % menos."],
        ],
    },
    "errors": [],
    "related": ["funciones", "diccionarios"],
}

UNIT = {
    "unit": {"module": "poo", "number": 1},
    "objectives": [
        "Explicar qué es la programación orientada a objetos y en qué se diferencia de la procedural.",
        "Distinguir una clase (el molde) de un objeto o instancia (cada ejemplar concreto).",
        "Leer un enunciado y decidir qué serán clases, atributos y métodos.",
        "Reconocer que los tipos de Python (`str`, `list`…) ya son clases con métodos.",
        "Nombrar los cuatro pilares de la POO y decidir cuándo merece la pena usarla.",
    ],
    "prior": "Funciones con parámetros y `return`, y diccionarios. No hace falta saber nada de clases: esta unidad empieza desde cero.",
    "key": [
        [
            "Programación procedural",
            "Organiza el programa en datos por un lado y funciones por otro, que reciben esos datos como parámetros.",
        ],
        [
            "Programación orientada a objetos (POO)",
            "Organiza el programa en objetos que reúnen sus datos y las acciones que trabajan con ellos.",
        ],
        [
            "Clase",
            "El molde o plantilla que describe qué datos y qué acciones tendrán sus objetos.",
        ],
        [
            "Objeto o instancia",
            "Cada ejemplar concreto creado a partir de una clase, con sus propios valores.",
        ],
        ["Atributo", "Una característica o dato del objeto: el nombre, el precio, la matrícula."],
        ["Método", "Una acción que sabe hacer el objeto: una función que pertenece a la clase."],
        [
            "Abstracción",
            "Quedarse solo con los datos y acciones que importan para el problema.",
        ],
        [
            "Encapsulación",
            "Ocultar los detalles internos y dejar usar el objeto a través de sus métodos.",
        ],
        [
            "Herencia y polimorfismo",
            "Crear clases a partir de otras y tratar igual a objetos distintos (Unidades 5 y 6).",
        ],
    ],
    "sections": [
        {
            "id": f"{CID}.procedural",
            "title": "Del programa procedural a los objetos",
            "theory": "Hasta ahora has programado de forma **procedural**: los datos van en variables, listas o diccionarios y las **funciones** van aparte y los reciben como parámetros. Funciona bien, pero cuando el programa crece nada impide pasar a una función un diccionario que no es el suyo, y los datos y lo que se puede hacer con ellos quedan separados.\n\nLa **programación orientada a objetos (POO)** junta las dos cosas: un **objeto** guarda sus datos (**atributos**) y sabe hacer acciones con ellos (**métodos**). En vez de `ingresar(cuenta, 50)` se escribe `cuenta.ingresar(50)`: se le pide a la cuenta que haga algo consigo misma.\n\n- La POO no sustituye a las funciones, las condiciones ni los bucles: los métodos se escriben con ellos.\n- No hace que el programa vaya más rápido: lo que mejora es la **organización** del código.",
            "examples": [
                {
                    "code": '# Procedural: los datos en un diccionario y las funciones aparte\ncuenta = {"titular": "Ana", "saldo": 100}\n\n\ndef ingresar(c, cantidad):\n    c["saldo"] += cantidad\n\n\ningresar(cuenta, 50)\nprint(cuenta["saldo"])\n\n\n# Orientado a objetos: los datos y sus acciones juntos\nclass Cuenta:\n    def __init__(self, titular, saldo):\n        self.titular = titular\n        self.saldo = saldo\n\n    def ingresar(self, cantidad):\n        self.saldo += cantidad\n\n\nmi_cuenta = Cuenta("Ana", 100)\nmi_cuenta.ingresar(50)\nprint(mi_cuenta.saldo)',
                    "lines": [
                        [2, "Enfoque procedural: los datos de la cuenta viven en un diccionario."],
                        [5, "La función está separada y recibe la cuenta como parámetro."],
                        [9, "Se llama a la función pasándole los datos."],
                        [14, "Enfoque POO: la clase `Cuenta` reúne los datos y la acción."],
                        [
                            19,
                            "El método `ingresar` trabaja con los datos del propio objeto (`self`).",
                        ],
                        [24, "Se le pide al objeto que haga la acción: `mi_cuenta.ingresar(50)`."],
                    ],
                }
            ],
            "quiz": ["poo1-01", "poo1-02", "poo1-03"],
        },
        {
            "id": f"{CID}.clase-instancia",
            "title": "Clases, objetos y cómo modelar un problema",
            "theory": "Una **clase** es un molde: describe qué datos y qué acciones tendrá algo, como el plano de una casa. Un **objeto** (o **instancia**) es cada ejemplar concreto hecho con ese molde: «Alumno» es una clase; «Ana, de 1.º DAW» es un objeto. De una clase se pueden crear tantos objetos como haga falta y cada uno guarda **sus propios valores**.\n\nPara **modelar** un enunciado, una técnica sencilla es fijarse en las palabras:\n\n- Los **sustantivos** importantes suelen ser **clases**: alumno, coche, pedido.\n- Sus **características** son **atributos**: nombre, matrícula, importe.\n- Los **verbos** (lo que hace o lo que se le hace) son **métodos**: matricularse, arrancar, pagar.\n\nEn Python **todo es un objeto**: un texto es un objeto de la clase `str` y una lista, de la clase `list`. Por eso escribes `texto.upper()` o `lista.sort()`: estás llamando a métodos de esos objetos.",
            "examples": [
                {
                    "code": 'texto = "hola"\nnumeros = [3, 1, 2]\n\nprint(type(texto).__name__)      # texto es un objeto de la clase str\nprint(texto.upper())             # upper() es un método de str\nnumeros.sort()                   # sort() cambia el estado de la lista\nprint(numeros)\nprint(isinstance(numeros, list))',
                    "lines": [
                        [1, "Un texto ya es un objeto: una instancia de la clase `str`."],
                        [4, "`type()` dice de qué clase es un objeto; `__name__` da su nombre."],
                        [5, "`upper()` es un método: devuelve el texto en mayúsculas."],
                        [6, "`sort()` es un método que cambia el estado de la propia lista."],
                        [8, "`isinstance` comprueba si un objeto es de una clase."],
                    ],
                }
            ],
            "quiz": ["poo1-04", "poo1-05", "poo1-06"],
        },
        {
            "id": f"{CID}.cuando",
            "title": "Cuándo usar la POO y sus cuatro pilares",
            "theory": "La POO **ayuda** cuando el programa maneja muchas entidades parecidas con datos y acciones propias (alumnos, productos, cuentas): el código queda ordenado por responsabilidades, se reutiliza y es más fácil de mantener y probar. **No compensa** para un cálculo suelto o un script corto: ahí una función es más clara. Una clase que no guarda datos propios suele ser una función disfrazada.\n\nLa POO se apoya en **cuatro pilares**, que verás a lo largo del módulo:\n\n1. **Abstracción**: modelar solo lo que importa para el problema (de un alumno, a secretaría le importan las notas, no su color favorito).\n2. **Encapsulación**: ocultar los detalles internos y dejar usar el objeto a través de sus métodos (Unidad 4).\n3. **Herencia**: crear clases nuevas a partir de otras (Unidad 5).\n4. **Polimorfismo**: tratar igual a objetos de clases distintas que responden al mismo método (Unidad 6).",
            "examples": [
                {
                    "code": "import math\n\n\n# Para un cálculo suelto basta una función\ndef area_circulo(radio):\n    return round(math.pi * radio**2, 2)\n\n\nprint(area_circulo(2))\n\n\n# Una clase sin datos propios no aporta nada aquí\nclass CalculadoraArea:\n    def circulo(self, radio):\n        return round(math.pi * radio**2, 2)\n\n\nprint(CalculadoraArea().circulo(2))",
                    "lines": [
                        [5, "Una función resuelve el cálculo sin más ceremonia."],
                        [13, "Esta clase no guarda ningún dato: el objeto no aporta nada."],
                        [18, "Mismo resultado, más código: aquí la POO no compensa."],
                    ],
                }
            ],
            "quiz": ["poo1-07", "poo1-08", "poo1-09"],
        },
    ],
    "guided": ["poo1-10"],
    "autonomous": ["poo1-14"],
    "extras": ["poo1-11"],
    "selfcheck": ["poo1-12", "poo1-13"],
    "recap": [
        "La programación procedural separa datos y funciones; la POO los junta en objetos.",
        "Una clase es el molde; cada objeto (instancia) es un ejemplar concreto con sus propios valores.",
        "Al modelar: sustantivos → clases, características → atributos, verbos → métodos.",
        "En Python todo es un objeto: `str`, `list` o `dict` son clases con sus métodos.",
        "Los cuatro pilares son abstracción, encapsulación, herencia y polimorfismo; la POO compensa cuando hay entidades con datos y acciones propias.",
    ],
    "pass": {
        "minScore": 0.7,
        "required": ["poo1-10", "poo1-14"],
        "text": [
            "Resolver el ejercicio guiado (tres clases con `describir()`) y el ejercicio principal `Producto` con todos los tests superados.",
            "Dominar la unidad según el motor: al menos un 70 % de aciertos recientes en sus ejercicios, con varios tipos distintos.",
            "Completar las lecciones ayuda a organizarte, pero **no** demuestra la competencia: la demuestran los ejercicios.",
        ],
    },
    "practices": [
        practice(
            "Antes de programar, subraya en el enunciado los sustantivos (posibles clases), sus características (atributos) y los verbos (métodos).",
            "Así el diseño sale del problema y no de la intuición del momento, y es más fácil explicar por qué existe cada clase.",
        ),
        practice(
            "Nombra las clases en singular y con mayúscula inicial en cada palabra: `Producto`, `CuentaBancaria`.",
            "Cada clase describe un solo ejemplar, y el nombre la distingue a simple vista de una variable o una función (`producto`, `mostrar`).",
        ),
        practice(
            "Crea una clase cuando haya datos y acciones que vayan juntos; para un cálculo suelto, deja una función.",
            "Una clase sin datos propios solo añade código y no aporta organización.",
        ),
        practice(
            "Haz que los métodos que calculan algo lo devuelvan con `return` y deja `print` para el programa principal.",
            "Un valor devuelto se puede comprobar, reutilizar en otro cálculo y probar con tests.",
        ),
        practice(
            "Guarda los datos de cada ejemplar en el propio objeto (`self.precio`) y no en variables sueltas del programa.",
            "Así cada objeto lleva sus valores consigo y dos productos no se pisan los datos.",
        ),
    ],
    "references": [
        ref(
            "py-tutorial-classes",
            "9.3. Un primer vistazo a las clases",
            ["qué es una clase y cómo se crea un objeto", "atributos y métodos de una instancia"],
        ),
        ref(
            "py-tutorial-classes",
            "9.1. Unas palabras sobre nombres y objetos",
            ["en Python los valores son objetos y varios nombres pueden apuntar al mismo"],
        ),
        ref(
            "py-faq-programming",
            "Objetos: ¿Qué es una clase? y ¿Qué es un método?",
            ["definición de clase y de método"],
        ),
    ],
    "bank": [
        "poo1-01",
        "poo1-03",
        "poo1-04",
        "poo1-06",
        "poo1-07",
        "poo1-08",
        "poo1-09",
        "poo1-12",
        "poo1-15",
        "poo1-16",
        "poo1-17",
        "poo1-18",
        "poo1-19",
        "poo1-20",
        "poo1-21",
    ],
    "curriculum": [
        proposed(
            "0485-RA2-a",
            "Se explican los fundamentos de la POO: clase, objeto, atributo, método y sus pilares.",
        ),
        proposed(
            "0485-RA2-c",
            "Se usan objetos de clases predefinidas de Python (`str`, `list`) y sus métodos.",
        ),
        proposed(
            "0485-RA4-a",
            "Se reconocen la sintaxis y los componentes típicos de una clase (atributos y métodos).",
        ),
    ],
}

EXERCISES = [
    # ---------- Lección «Del programa procedural a los objetos»
    choice(
        "poo1-01",
        CID,
        "¿Cuál es la diferencia principal entre la programación procedural y la orientada a objetos?",
        [
            (
                "En la POO los datos y las funciones que trabajan con ellos se agrupan en una misma unidad, la clase",
                None,
            ),
            ("La POO no usa funciones, condiciones ni bucles", f"{CID}.poo-siempre"),
            ("La POO hace que el programa se ejecute más rápido", f"{CID}.poo-siempre"),
            ("En la programación procedural no se pueden usar diccionarios", None),
        ],
        0,
        "La POO cambia la **organización**: junta los datos (atributos) con las acciones que los usan (métodos). Dentro de los métodos sigue habiendo funciones, condiciones y bucles, y la velocidad no cambia por usar clases.",
        level=1,
        daw=False,
    ),
    output(
        "poo1-02",
        CID,
        """
        def ingresar(cuenta, cantidad):
            cuenta["saldo"] += cantidad

        cuenta = {"titular": "Ana", "saldo": 10}
        ingresar(cuenta, 5)
        ingresar(cuenta, 5)
        print(cuenta["saldo"])
        """,
        "20",
        "Versión procedural: la función recibe el diccionario y lo modifica, así que los dos ingresos se acumulan (10 + 5 + 5). Un método hace lo mismo con `self`, pero los datos y la acción quedan juntos en el objeto.",
        traps={"10": None, "15": None},
        level=1,
        daw=False,
    ),
    choice(
        "poo1-03",
        CID,
        "En la línea `teclado.con_descuento(25)`, ¿qué es `con_descuento`?",
        [
            ("Un método: una acción del objeto `teclado` que trabaja con sus datos", None),
            ("Un atributo: un dato guardado en `teclado`", f"{CID}.atributo-metodo"),
            ("La clase de la que se ha creado `teclado`", f"{CID}.clase-instancia"),
            ("Una variable global del programa", None),
        ],
        0,
        "Los paréntesis lo delatan: se está **llamando** a algo del objeto, así que es un método. Un atributo se lee sin paréntesis (`teclado.precio`).",
        level=1,
        daw=False,
    ),
    # ---------- Lección «Clases, objetos y cómo modelar un problema»
    choice(
        "poo1-04",
        CID,
        "Enunciado: «Un coche tiene matrícula y color, y puede arrancar y frenar». Si `Coche` es una clase, ¿qué son «matrícula» y «arrancar»?",
        [
            ("«matrícula» es un atributo y «arrancar» es un método", None),
            ("«matrícula» es un método y «arrancar» es un atributo", f"{CID}.atributo-metodo"),
            ("Las dos son clases nuevas", f"{CID}.clase-instancia"),
            ("Las dos son atributos", f"{CID}.atributo-metodo"),
        ],
        0,
        "Las características (lo que el coche **tiene**) son atributos; las acciones (lo que el coche **hace**) son métodos.",
        level=1,
        daw=False,
    ),
    output(
        "poo1-05",
        CID,
        """
        print(type([1]).__name__, type("a").__name__)
        """,
        "list str",
        "Una lista es un objeto de la clase `list` y un texto, de la clase `str`: en Python todo valor es una instancia de alguna clase.",
        traps={"[1] a": f"{CID}.clase-instancia", "lista texto": None},
        level=1,
        daw=False,
    ),
    choice(
        "poo1-06",
        CID,
        "¿Cuál de estas frases describe una **instancia** y no una clase?",
        [
            ("El coche de matrícula 1234-ABC aparcado en la puerta del instituto", None),
            ("Coche: todo vehículo con matrícula, color y motor", f"{CID}.clase-instancia"),
            ("Alumno: cualquier persona matriculada en el ciclo", f"{CID}.clase-instancia"),
            ("Producto: lo que vende una tienda, con nombre y precio", f"{CID}.clase-instancia"),
        ],
        0,
        "Una instancia es **un ejemplar concreto** con sus propios valores (esa matrícula). Las otras frases describen un tipo general de cosa: son clases.",
        level=1,
        daw=False,
    ),
    # ---------- Lección «Cuándo usar la POO y sus cuatro pilares»
    choice(
        "poo1-07",
        CID,
        "¿En cuál de estos casos **no** merece la pena crear una clase?",
        [
            (
                "Un script de diez líneas que convierte una temperatura de °C a °F y la muestra",
                None,
            ),
            ("Una aplicación que gestiona cientos de alumnos, cada uno con sus notas", None),
            ("Un juego con varios personajes que se mueven y tienen vidas", None),
            ("Una tienda con productos, clientes y pedidos", None),
        ],
        0,
        "Un cálculo suelto se resuelve mejor con una función: una clase solo añadiría código. La POO compensa cuando hay muchas entidades con datos y acciones propias, como en los otros tres casos.",
        level=1,
        daw=False,
    ),
    choice(
        "poo1-08",
        CID,
        "¿Qué pilar de la POO consiste en ocultar los detalles internos de un objeto y dejar usarlo solo a través de sus métodos?",
        [
            ("Encapsulación", None),
            ("Herencia", None),
            ("Polimorfismo", None),
            ("Abstracción", None),
        ],
        0,
        "Eso es la **encapsulación** (Unidad 4). La herencia crea clases a partir de otras, el polimorfismo trata igual a objetos distintos y la abstracción elige qué datos importan.",
        level=1,
        daw=False,
    ),
    choice(
        "poo1-09",
        CID,
        "Esta clase `Alumno` es para la secretaría: guarda nombre, curso y notas, pero no el color favorito del alumno. ¿Qué pilar de la POO se está aplicando?",
        [
            ("Abstracción", None),
            ("Herencia", None),
            ("Polimorfismo", None),
            ("Encapsulación", None),
        ],
        0,
        "La **abstracción** consiste en quedarse con lo que importa para el problema y dejar fuera el resto.",
        code="""
        class Alumno:
            def __init__(self, nombre, curso, notas):
                self.nombre = nombre
                self.curso = curso
                self.notas = notas
        """,
        level=1,
        daw=False,
    ),
    # ---------- Ejercicio guiado
    code(
        "poo1-10",
        CID,
        '**Ejercicio guiado: tres clases sencillas.** La clase `Persona` ya está hecha como modelo. Sigue los pasos:\n\n1. Crea la clase `Vehiculo` con `__init__(self, marca, matricula)` y un método `describir()` que **devuelva** `"Seat (1234-ABC)"`.\n2. Crea la clase `Producto` con `__init__(self, nombre, precio)` y un método `describir()` que devuelva `"Teclado: 25.00 €"` (el precio con dos decimales).\n3. Pulsa **▶ Ejecutar** y después **Comprobar con los tests**.',
        """
        class Persona:
            def __init__(self, nombre, edad):
                self.nombre = nombre
                self.edad = edad

            def describir(self):
                return f"{self.nombre}, {self.edad} años"


        # Paso 1: clase Vehiculo(marca, matricula) con describir()

        # Paso 2: clase Producto(nombre, precio) con describir()


        print(Persona("Ana", 19).describir())
        """,
        """
        class Persona:
            def __init__(self, nombre, edad):
                self.nombre = nombre
                self.edad = edad

            def describir(self):
                return f"{self.nombre}, {self.edad} años"


        class Vehiculo:
            def __init__(self, marca, matricula):
                self.marca = marca
                self.matricula = matricula

            def describir(self):
                return f"{self.marca} ({self.matricula})"


        class Producto:
            def __init__(self, nombre, precio):
                self.nombre = nombre
                self.precio = precio

            def describir(self):
                return f"{self.nombre}: {self.precio:.2f} €"


        print(Persona("Ana", 19).describir())
        print(Vehiculo("Seat", "1234-ABC").describir())
        print(Producto("Teclado", 25).describir())
        """,
        [
            case(
                'assert Persona("Leo", 30).describir() == "Leo, 30 años", "No cambies la clase Persona: es el modelo"',
            ),
            case(
                'v = Vehiculo("Seat", "1234-ABC")\nassert (v.marca, v.matricula) == ("Seat", "1234-ABC"), "Guarda marca y matrícula como atributos con self"\nassert v.describir() == "Seat (1234-ABC)", f"describir() debe devolver \'Seat (1234-ABC)\'; devuelve {v.describir()!r}"',
                error=f"{CID}.atributo-metodo",
            ),
            case(
                'p = Producto("Ratón", 9.5)\nassert p.describir() == "Ratón: 9.50 €", f"describir() debe devolver \'Ratón: 9.50 €\' (dos decimales); devuelve {p.describir()!r}"',
            ),
        ],
        "Cada clase guarda sus datos en `__init__` con `self.` y tiene su propio `describir()`. Que las tres clases tengan un método con el mismo nombre es normal: cada objeto responde a su manera (es la idea del polimorfismo, Unidad 6).",
        'Copia la estructura de `Persona`. Para los dos decimales usa `f"{self.precio:.2f}"`.',
        wrong=[
            (
                """
                class Persona:
                    def __init__(self, nombre, edad):
                        self.nombre = nombre
                        self.edad = edad

                    def describir(self):
                        return f"{self.nombre}, {self.edad} años"


                class Vehiculo:
                    def __init__(self, marca, matricula):
                        self.marca = marca
                        self.matricula = matricula

                    def describir(self):
                        return f"{self.marca} ({self.matricula})"


                class Producto:
                    def __init__(self, nombre, precio):
                        self.nombre = nombre
                        self.precio = precio

                    def describir(self):
                        return f"{self.nombre}: {self.precio} €"
                """,
                3,
            ),
        ],
        level=1,
        daw=False,
    ),
    # ---------- Ejercicio autónomo
    code(
        "poo1-11",
        CID,
        '**Ejercicio autónomo: de procedural a objetos.** Este programa guarda libros en diccionarios y usa funciones sueltas:\n\n```\ndef crear_libro(titulo, autor, paginas):\n    return {"titulo": titulo, "autor": autor, "paginas": paginas}\n\ndef es_largo(libro):\n    return libro["paginas"] > 300\n\ndef ficha(libro):\n    return f\'{libro["titulo"]} ({libro["autor"]}), {libro["paginas"]} páginas\'\n```\n\nReescríbelo como una clase `Libro` con `__init__(self, titulo, autor, paginas)` y los métodos `es_largo()` (más de 300 páginas) y `ficha()`, que devuelva un texto como `"Rayuela (Julio Cortázar), 600 páginas"`.',
        """
        class Libro:
            ...
        """,
        """
        class Libro:
            def __init__(self, titulo, autor, paginas):
                self.titulo = titulo
                self.autor = autor
                self.paginas = paginas

            def es_largo(self):
                return self.paginas > 300

            def ficha(self):
                return f"{self.titulo} ({self.autor}), {self.paginas} páginas"


        libro = Libro("Rayuela", "Julio Cortázar", 600)
        print(libro.ficha())
        print(libro.es_largo())
        """,
        [
            case(
                'l = Libro("A", "B", 100)\nassert l.ficha() == "A (B), 100 páginas", f"ficha() debe devolver \'A (B), 100 páginas\'; devuelve {l.ficha()!r}"',
            ),
            case(
                'assert Libro("A", "B", 301).es_largo() is True, "Un libro de 301 páginas es largo"\nassert Libro("A", "B", 300).es_largo() is False, "Un libro de 300 páginas justas NO es largo: más de 300"',
            ),
            case(
                'l1 = Libro("A", "B", 100)\nl2 = Libro("C", "D", 500)\nassert l1.titulo == "A" and l2.titulo == "C", "Cada libro debe guardar su propio título"\nassert l2.es_largo() and not l1.es_largo(), "Cada libro responde con sus propios datos"',
                error=f"{CID}.clase-instancia",
            ),
        ],
        "El diccionario se convierte en atributos guardados en `__init__` y cada función pasa a ser un método que, en vez de recibir el libro, usa `self`.",
        'Cambia `libro["paginas"]` por `self.paginas` y quita el parámetro `libro` de las funciones: ahora lo es `self`.',
        wrong=[
            (
                """
                class Libro:
                    def __init__(self, titulo, autor, paginas):
                        self.titulo = titulo
                        self.autor = autor
                        self.paginas = paginas

                    def es_largo(self):
                        return self.paginas >= 300

                    def ficha(self):
                        return f"{self.titulo} ({self.autor}), {self.paginas} páginas"
                """,
                2,
            ),
        ],
        level=2,
        daw=False,
    ),
    # ---------- Autoevaluación
    choice(
        "poo1-12",
        CID,
        "Con este código, ¿cuál de estas afirmaciones es correcta?",
        [
            (
                "De una clase se pueden crear muchos objetos, y cada uno guarda sus propios valores",
                None,
            ),
            ("Cada clase solo puede tener un objeto", f"{CID}.clase-instancia"),
            ("Los objetos se definen con la palabra `class`", f"{CID}.clase-instancia"),
            ("Los métodos son los datos que guarda un objeto", f"{CID}.atributo-metodo"),
        ],
        0,
        "La clase se define una vez con `class` y de ella se crean todos los objetos que haga falta: aquí `a` y `b` son dos productos, cada uno con su nombre. Los datos son atributos; los métodos son acciones.",
        code="""
        class Producto:
            def __init__(self, nombre):
                self.nombre = nombre

        a = Producto("Teclado")
        b = Producto("Ratón")
        """,
        level=1,
        daw=False,
    ),
    output(
        "poo1-13",
        CID,
        """
        class Punto:
            def __init__(self, x, y):
                self.x = x
                self.y = y

        p1 = Punto(1, 2)
        p2 = Punto(1, 2)
        print(type(p1) == type(p2), p1 == p2)
        """,
        "True False",
        "Los dos son de la misma clase (`True`), pero son **dos objetos distintos**: sin más instrucciones, `==` entre objetos compara si son el mismo objeto, no sus valores. En la Unidad 8 verás cómo cambiarlo con `__eq__`.",
        traps={"True True": f"{CID}.clase-instancia", "False False": None},
        level=2,
        daw=False,
    ),
    # ---------- Ejercicio principal de la unidad
    code(
        "poo1-14",
        CID,
        '**Ejercicio principal: la clase `Producto`.** Una tienda quiere dejar de guardar sus productos en diccionarios. Crea la clase `Producto` con:\n\n- `__init__(self, nombre, precio, unidades=0)`: guarda los tres datos como atributos.\n- `mostrar()`: **devuelve** un texto como `"Teclado · 25.00 € · 3 uds."` (el precio con dos decimales).\n- `valor_stock()`: devuelve el precio por las unidades.\n- `reponer(cantidad)`: suma la cantidad a las unidades.\n\nCrea dos productos, repón uno y muestra los dos.',
        """
        class Producto:
            ...
        """,
        """
        class Producto:
            def __init__(self, nombre, precio, unidades=0):
                self.nombre = nombre
                self.precio = precio
                self.unidades = unidades

            def mostrar(self):
                return f"{self.nombre} · {self.precio:.2f} € · {self.unidades} uds."

            def valor_stock(self):
                return self.precio * self.unidades

            def reponer(self, cantidad):
                self.unidades += cantidad


        teclado = Producto("Teclado", 25, 3)
        raton = Producto("Ratón", 9.5)
        raton.reponer(4)
        print(teclado.mostrar())
        print(raton.mostrar())
        """,
        [
            case(
                'p = Producto("Monitor", 120, 2)\nassert (p.nombre, p.precio, p.unidades) == ("Monitor", 120, 2), "Guarda nombre, precio y unidades como atributos con self"\nassert Producto("Cable", 3).unidades == 0, "Las unidades empiezan en 0 si no se indican"',
                error=f"{CID}.atributo-metodo",
            ),
            case(
                'p = Producto("Teclado", 25, 3)\nassert p.mostrar() == "Teclado · 25.00 € · 3 uds.", f"mostrar() debe devolver \'Teclado · 25.00 € · 3 uds.\'; devuelve {p.mostrar()!r}"',
            ),
            case(
                'p = Producto("Teclado", 25, 3)\nassert p.valor_stock() == 75, "valor_stock() devuelve precio × unidades"\np.reponer(2)\nassert p.unidades == 5 and p.valor_stock() == 125, "reponer() suma la cantidad a las unidades del producto"',
            ),
            case(
                'a = Producto("A", 1, 1)\nb = Producto("B", 2, 1)\na.reponer(10)\nassert b.unidades == 1, "Reponer un producto no debe cambiar las unidades de otro"\nassert a.mostrar() != b.mostrar(), "Cada producto muestra sus propios datos"',
                error=f"{CID}.clase-instancia",
            ),
        ],
        "Los datos (`nombre`, `precio`, `unidades`) viven en cada objeto y los métodos trabajan con ellos a través de `self`. Por eso reponer el ratón no cambia el teclado: cada producto es una instancia con su propio estado.",
        "Copia la estructura de `__init__` de la lección. Para el texto usa una f-string con `{self.precio:.2f}` y recuerda **devolverlo** con `return`, no imprimirlo.",
        wrong=[
            (
                """
                class Producto:
                    def __init__(self, nombre, precio, unidades=0):
                        self.nombre = nombre
                        self.precio = precio
                        self.unidades = unidades

                    def mostrar(self):
                        print(f"{self.nombre} · {self.precio:.2f} € · {self.unidades} uds.")

                    def valor_stock(self):
                        return self.precio * self.unidades

                    def reponer(self, cantidad):
                        self.unidades += cantidad
                """,
                2,
            ),
            (
                """
                class Producto:
                    unidades = 0

                    def __init__(self, nombre, precio, unidades=0):
                        self.nombre = nombre
                        self.precio = precio
                        Producto.unidades = unidades

                    def mostrar(self):
                        return f"{self.nombre} · {self.precio:.2f} € · {Producto.unidades} uds."

                    def valor_stock(self):
                        return self.precio * Producto.unidades

                    def reponer(self, cantidad):
                        Producto.unidades += cantidad
                """,
                4,
            ),
        ],
        level=2,
        daw=False,
    ),
    # ---------- Banco de preguntas de la unidad (cuestionario)
    choice(
        "poo1-15",
        CID,
        "¿Qué muestra este programa?",
        [
            ("35 20", None),
            (
                "35 35",
                f"{CID}.clase-instancia",
                "Cambiar `a.precio` solo cambia el objeto `a`: `b` es otra instancia con su propio precio.",
            ),
            (
                "40 20",
                None,
                "Los atributos de un objeto se pueden cambiar después de crearlo: `a.precio = 35` sustituye el 40.",
            ),
            (
                "AttributeError",
                None,
                "`precio` existe en los dos objetos porque lo crea `__init__`; asignarle otro valor no da error.",
            ),
        ],
        0,
        "Cada objeto guarda sus propios valores. `a.precio = 35` cambia el precio del teclado y el ratón conserva sus 20.",
        code="""
        class Producto:
            def __init__(self, nombre, precio):
                self.nombre = nombre
                self.precio = precio

        a = Producto("Teclado", 40)
        b = Producto("Ratón", 20)
        a.precio = 35
        print(a.precio, b.precio)
        """,
        level=2,
        daw=False,
        bank=True,
        qtype="prediccion",
    ),
    choice(
        "poo1-16",
        CID,
        "¿Qué muestra este programa?",
        [
            ("str HOLA", None),
            (
                "hola HOLA",
                f"{CID}.clase-instancia",
                "`type()` no devuelve el valor sino su clase; el nombre de la clase de un texto es `str`.",
            ),
            (
                "str hola",
                None,
                "`upper()` es un método de los textos que devuelve otro texto en mayúsculas.",
            ),
            (
                "texto HOLA",
                None,
                "Las clases de Python tienen nombre en inglés: la de los textos se llama `str`.",
            ),
        ],
        0,
        "Un texto es un objeto de la clase `str` y `upper()` es uno de sus métodos: en Python los tipos predefinidos también son clases.",
        code="""
        saludo = "hola"
        print(type(saludo).__name__, saludo.upper())
        """,
        level=2,
        daw=False,
        bank=True,
        qtype="prediccion",
    ),
    choice(
        "poo1-17",
        CID,
        "¿Qué muestra este programa?",
        [
            ("2 1", None),
            (
                "3 3",
                f"{CID}.clase-instancia",
                "La lista se crea en `__init__`, así que cada carrito tiene la suya: no comparten productos.",
            ),
            (
                "1 1",
                None,
                "`a` recibe dos llamadas a `meter` (pan y sal), y cada una añade un elemento.",
            ),
            (
                "3 0",
                None,
                "Lo que se mete en `b` va a la lista de `b`, no a la de `a`.",
            ),
        ],
        0,
        "`self.items = []` se ejecuta al crear **cada** carrito, así que hay dos listas. `a` acaba con pan y sal (2) y `b` con leche (1).",
        code="""
        class Carrito:
            def __init__(self):
                self.items = []

            def meter(self, producto):
                self.items.append(producto)

        a = Carrito()
        b = Carrito()
        a.meter("pan")
        b.meter("leche")
        a.meter("sal")
        print(len(a.items), len(b.items))
        """,
        level=3,
        daw=False,
        bank=True,
        qtype="prediccion",
    ),
    choice(
        "poo1-18",
        CID,
        "Este programa termina con `TypeError`. ¿Cuál es la causa?",
        [
            ("Falta el precio: `__init__` pide nombre y precio y solo se le pasa el nombre", None),
            (
                'Hay que pasar `self` al crear el objeto: `Producto(self, "Teclado")`',
                None,
                "Python pasa `self` solo; al crear el objeto solo se escriben los datos.",
            ),
            (
                "Falta `return self` al final de `__init__`",
                None,
                "`__init__` no devuelve nada: solo prepara el objeto que Python ya ha creado.",
            ),
            (
                "Una clase no puede recibir textos como datos",
                None,
                "Un atributo puede guardar cualquier valor: textos, números, listas u otros objetos.",
            ),
        ],
        0,
        'Al crear un objeto hay que dar un valor a cada parámetro de `__init__` (menos `self`). Aquí falta `precio`: `Producto("Teclado", 40)`.',
        code="""
        class Producto:
            def __init__(self, nombre, precio):
                self.nombre = nombre
                self.precio = precio

        p = Producto("Teclado")
        """,
        level=2,
        daw=False,
        bank=True,
        qtype="error",
    ),
    choice(
        "poo1-19",
        CID,
        "Debería mostrar `True`, pero muestra `False`. ¿Por qué?",
        [
            ("En la línea 8 falta llamar al método: `l.encender()`, con paréntesis", None),
            (
                "`encendida` es un atributo compartido por todas las lámparas",
                None,
                "`self.encendida` se crea en `__init__`: es de cada lámpara, no de la clase.",
            ),
            (
                "El método `encender` necesita `return True`",
                None,
                "El método cambia el estado del objeto; no hace falta que devuelva nada. El problema es que nunca se ejecuta.",
            ),
            (
                "Hay que llamarlo desde la clase: `Lampara.encender()`",
                f"{CID}.clase-instancia",
                "Sin objeto, `encender` no sabría qué lámpara encender y daría `TypeError`.",
            ),
        ],
        0,
        "Sin paréntesis, `l.encender` solo nombra el método y no lo ejecuta. Un atributo se lee sin paréntesis; un método se **llama** con ellos.",
        code="""
        class Lampara:
            def __init__(self):
                self.encendida = False

            def encender(self):
                self.encendida = True

        l = Lampara()
        l.encender
        print(l.encendida)
        """,
        level=3,
        daw=False,
        bank=True,
        qtype="error",
    ),
    choice(
        "poo1-20",
        CID,
        "Hay que guardar varios libros con su título y sus páginas, y saber si cada uno es largo (más de 300 páginas). ¿Qué diseño lo resuelve con POO?",
        [
            (
                "`class Libro` con `__init__(self, titulo, paginas)` y un método `es_largo(self)` que devuelve `self.paginas > 300`",
                None,
            ),
            (
                "`class Libro` con un método `es_largo(paginas)`, sin `self`, que devuelve `paginas > 300`",
                f"{CID}.atributo-metodo",
                "Sin `self` el método no recibe el libro: al llamar `libro.es_largo()` Python pasa el objeto y no cuadran los parámetros.",
            ),
            (
                "Un diccionario por libro y una función suelta `es_largo(libro)`",
                f"{CID}.poo-siempre",
                "Funciona, pero es la versión procedural: los datos y la acción siguen separados.",
            ),
            (
                "Una sola clase `Libros` con un atributo `titulo` común a todos los libros",
                f"{CID}.clase-instancia",
                "Cada libro necesita su propio título y sus páginas: un dato común no distingue un libro de otro.",
            ),
        ],
        0,
        "En la POO cada libro es un objeto con sus datos y el método `es_largo` usa los datos del propio libro a través de `self`.",
        level=3,
        daw=False,
        bank=True,
        qtype="solucion",
    ),
    choice(
        "poo1-21",
        CID,
        "Con la clase `Producto(nombre, precio)`, ¿qué código muestra `Teclado Ratón`?",
        [
            (
                'a = Producto("Teclado", 40); b = Producto("Ratón", 20); print(a.nombre, b.nombre)',
                None,
            ),
            (
                "a = Producto; b = Producto; print(a.nombre, b.nombre)",
                f"{CID}.clase-instancia",
                "Sin paréntesis no se crea ningún objeto: `a` y `b` son la clase, que no tiene `nombre`.",
            ),
            (
                'a = b = Producto("Teclado", 40); b.nombre = "Ratón"; print(a.nombre, b.nombre)',
                f"{CID}.clase-instancia",
                "`a = b = …` crea un solo objeto con dos nombres: los dos mostrarían `Ratón`.",
            ),
            (
                'Producto("Teclado", 40); Producto("Ratón", 20); print(Producto.nombre)',
                None,
                "Los objetos se crean pero no se guardan en ninguna variable, y la clase no tiene el atributo `nombre`.",
            ),
        ],
        0,
        "Cada llamada a la clase crea un objeto nuevo; guardándolo en una variable se puede usar después.",
        level=3,
        daw=False,
        code_options=True,
        bank=True,
        qtype="solucion",
    ),
]

# Preguntas tipo test que ya existían y pasan al banco: (tipo, nivel, por qué falla cada distractor)
BANK_TAGS = {
    "poo1-01": (
        "teoria",
        1,
        [
            "Dentro de los métodos se siguen usando funciones, condiciones y bucles: la POO cambia cómo se organiza el código.",
            "Usar clases no hace el programa más rápido; organiza el código.",
            "Los diccionarios se usan en cualquier estilo de programación.",
        ],
    ),
    "poo1-03": (
        "codigo",
        1,
        [
            "Un atributo se lee sin paréntesis; aquí se está llamando a algo, así que es un método.",
            "La clase es `Producto`; `teclado` es un objeto y `con_descuento` una acción suya.",
            "Va detrás de `teclado.`: pertenece al objeto, no es una variable suelta del programa.",
        ],
    ),
    "poo1-04": (
        "diseno",
        1,
        [
            "Es al revés: lo que el coche tiene es un atributo y lo que hace es un método.",
            "Son partes del coche (un dato y una acción), no tipos de cosa nuevos.",
            "«Arrancar» es una acción, y las acciones son métodos.",
        ],
    ),
    "poo1-06": (
        "teoria",
        1,
        [
            "Describe a todos los coches en general: es una clase.",
            "Habla de cualquier alumno, no de uno concreto: es una clase.",
            "Es la descripción general de lo que vende la tienda: una clase.",
        ],
    ),
    "poo1-07": (
        "diseno",
        2,
        [
            "Cientos de alumnos con sus notas son entidades con datos y acciones propias: ahí la POO compensa.",
            "Cada personaje tiene su estado (posición, vidas) y sus acciones: es un caso típico de objetos.",
            "Productos, clientes y pedidos son entidades distintas con datos y acciones: encajan como clases.",
        ],
    ),
    "poo1-08": (
        "teoria",
        1,
        [
            "La herencia sirve para crear una clase a partir de otra, no para ocultar detalles.",
            "El polimorfismo es tratar igual a objetos distintos que responden al mismo método.",
            "La abstracción elige qué datos importan; ocultarlos tras métodos es la encapsulación.",
        ],
    ),
    "poo1-09": (
        "codigo",
        2,
        [
            "No hay ninguna clase que herede de otra en este código.",
            "No hay varios objetos distintos respondiendo al mismo método.",
            "Los atributos son públicos: no se está ocultando nada, se está eligiendo qué guardar.",
        ],
    ),
    "poo1-12": (
        "codigo",
        2,
        [
            "En el código se crean dos objetos de `Producto`: una clase admite todos los que hagan falta.",
            'Con `class` se define la clase; los objetos se crean llamándola: `Producto("Teclado")`.',
            "Los datos que guarda un objeto son atributos, como `nombre`; los métodos son acciones.",
        ],
    ),
}

# Errores típicos (slug, etiqueta, por qué, qué pensar, cómo evitarlo)
ERRORS = [
    (
        "clase-instancia",
        "Confunde la clase (el molde) con sus objetos",
        "La clase describe un tipo de cosa; cada objeto es un ejemplar concreto con sus propios valores. Dos objetos de la misma clase son distintos.",
        "¿Hablo de «los coches» en general (clase) o de «este coche» en concreto (objeto)?",
        "Piensa en la clase como el plano y en los objetos como las casas construidas con él.",
    ),
    (
        "poo-siempre",
        "Cree que la POO sustituye a todo o que siempre hay que usarla",
        "La POO organiza el código, pero los métodos se siguen escribiendo con funciones, condiciones y bucles, y para un cálculo suelto una función es más clara.",
        "¿Tengo entidades con datos y acciones propias, o solo un cálculo?",
        "Usa una clase cuando haya datos que viajen con sus acciones; si no, una función.",
    ),
    (
        "atributo-metodo",
        "Confunde atributos (datos) con métodos (acciones)",
        "Un atributo es algo que el objeto tiene (se lee sin paréntesis); un método es algo que el objeto hace (se llama con paréntesis).",
        "¿Es una característica o una acción? ¿Lleva paréntesis?",
        "Sustantivos y adjetivos → atributos; verbos → métodos.",
    ),
]
