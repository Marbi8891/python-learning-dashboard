# ruff: noqa: E501
"""Unidad 1 del módulo de POO: fundamentos de la programación orientada a objetos.

Concepto `poo-fundamentos` (área `poo`): del programa procedural a las clases, qué es una clase y
qué es un objeto, cómo se modela un enunciado, cuándo conviene la POO y sus cuatro pilares.
La salida de los ejemplos la obtiene build_learning.py ejecutándolos.
"""

from exercises import case, choice, code, output
from poo_common import proposed

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
    "autonomous": ["poo1-11"],
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
        "required": ["poo1-10", "poo1-11"],
        "text": [
            "Resolver el ejercicio guiado (tres clases con `describir()`) y el autónomo `Libro` con todos los tests superados.",
            "Dominar la unidad según el motor: al menos un 70 % de aciertos recientes en sus ejercicios, con varios tipos distintos.",
            "Completar las lecciones ayuda a organizarte, pero **no** demuestra la competencia: la demuestran los ejercicios.",
        ],
    },
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
        "Al modelar `Alumno` para la secretaría guardas nombre, curso y notas, pero no su color favorito. ¿Qué pilar estás aplicando?",
        [
            ("Abstracción", None),
            ("Herencia", None),
            ("Polimorfismo", None),
            ("Encapsulación", None),
        ],
        0,
        "La **abstracción** consiste en quedarse con lo que importa para el problema y dejar fuera el resto.",
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
        "¿Cuál de estas afirmaciones es correcta?",
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
        "La clase se define una vez con `class` y de ella se crean todos los objetos que haga falta. Los datos son atributos; los métodos son acciones.",
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
]

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
