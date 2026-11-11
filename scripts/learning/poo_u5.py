# ruff: noqa: E501
"""Unidad 5 del módulo de POO: herencia.

Concepto `poo-herencia` (área `poo`): superclase y subclase, relación «es un», constructores con
`super().__init__`, sobrescribir y ampliar métodos, jerarquías e `isinstance`/`issubclass`.
La salida de los ejemplos la obtiene build_learning.py ejecutándolos.
"""

from exercises import bug, case, choice, code, fill, output
from poo_common import proposed

CID = "poo-herencia"

CONCEPT = {
    "id": CID,
    "title": "Herencia",
    "area": "poo",
    "requires": ["poo-atributos-metodos"],
    "daw": 2,
    "ut": "prog-ut6",
    "lessons": ["herencia"],
    "summary": "Crear clases a partir de otras: superclase y subclase, `super()`, sobrescribir métodos y jerarquías.",
    "when": "Cuando varias clases comparten datos y comportamiento y entre ellas hay una relación «es un» (un gerente es un empleado), para escribir lo común una sola vez.",
    "example": {
        "code": 'class Empleado:\n    def __init__(self, nombre, sueldo):\n        self.nombre = nombre\n        self.sueldo = sueldo\n\n    def salario(self):\n        return self.sueldo\n\n\nclass Gerente(Empleado):                 # Gerente hereda de Empleado\n    def __init__(self, nombre, sueldo, plus):\n        super().__init__(nombre, sueldo)  # inicializa la parte de Empleado\n        self.plus = plus\n\n    def salario(self):                    # sobrescribe y amplía\n        return super().salario() + self.plus\n\n\nana = Empleado("Ana", 1500)\nluis = Gerente("Luis", 2000, 500)\nprint(ana.nombre, ana.salario())\nprint(luis.nombre, luis.salario())\nprint(isinstance(luis, Empleado))',
        "lines": [
            [10, "`class Gerente(Empleado)`: la subclase recibe todo lo de la superclase."],
            [
                12,
                "`super().__init__` ejecuta el constructor de `Empleado` para guardar nombre y sueldo.",
            ],
            [15, "El gerente tiene su propia versión de `salario`."],
            [16, "`super().salario()` reutiliza el cálculo de la superclase y le suma el plus."],
            [23, "Un gerente **es un** empleado: `isinstance` lo confirma."],
        ],
    },
    "errors": [],
    "related": ["poo-atributos-metodos", "poo-encapsulacion"],
}

UNIT = {
    "unit": {"module": "poo", "number": 5},
    "objectives": [
        "Definir una subclase que hereda atributos y métodos de una superclase.",
        "Reconocer cuándo hay una relación «es un» (herencia) y cuándo «tiene un» (composición).",
        "Escribir constructores de subclase que llamen a `super().__init__`.",
        "Sobrescribir métodos y ampliarlos con `super()`.",
        "Comprobar jerarquías con `isinstance` e `issubclass`.",
    ],
    "prior": "Las Unidades 2 y 3: clases, `__init__`, `self`, atributos y métodos. Conviene haber hecho la Unidad 4, aunque no es imprescindible.",
    "key": [
        [
            "Herencia",
            "Mecanismo para crear una clase nueva a partir de otra y reutilizar su código.",
        ],
        ["Superclase (clase base o padre)", "La clase de la que se hereda: `Empleado`."],
        ["Subclase (clase derivada o hija)", "La clase que hereda: `class Gerente(Empleado):`."],
        ["Relación «es un»", "La prueba de la herencia: un gerente *es un* empleado."],
        ["`super()`", "Da acceso a los métodos de la superclase desde la subclase."],
        [
            "Sobrescribir",
            "Definir en la subclase un método con el mismo nombre que en la superclase.",
        ],
        [
            "Jerarquía",
            "El árbol de clases que heredan unas de otras; en Python todas heredan de `object`.",
        ],
    ],
    "sections": [
        {
            "id": f"{CID}.subclases",
            "title": "Superclase y subclase",
            "theory": "Con la **herencia** una clase nueva (la **subclase**) se crea a partir de otra (la **superclase**) y recibe **todos** sus atributos y métodos. Se escribe poniendo la superclase entre paréntesis: `class Perro(Animal):`. Después la subclase puede **añadir** cosas nuevas.\n\nLa herencia expresa una relación **«es un»**: un perro *es un* animal, un gerente *es un* empleado. Si la frase natural es «**tiene un**» (un coche *tiene un* motor), no es herencia sino **composición** (Unidad 7).\n\n- `isinstance(objeto, Clase)` es `True` también con las superclases: un perro es un `Animal`.\n- `issubclass(Perro, Animal)` comprueba la relación entre clases.\n- En Python todas las clases heredan, al final, de `object`.",
            "examples": [
                {
                    "code": 'class Animal:\n    def __init__(self, nombre):\n        self.nombre = nombre\n\n    def presentarse(self):\n        return f"Soy {self.nombre}"\n\n\nclass Perro(Animal):            # Perro hereda de Animal\n    def ladrar(self):           # y añade un método nuevo\n        return "¡Guau!"\n\n\ntoby = Perro("Toby")\nprint(toby.presentarse())       # método heredado\nprint(toby.ladrar())            # método propio\nprint(isinstance(toby, Animal), issubclass(Perro, Animal))\nprint(issubclass(Animal, Perro))',
                    "lines": [
                        [
                            9,
                            "`Perro` recibe `__init__` y `presentarse` de `Animal` sin escribirlos.",
                        ],
                        [10, "Además tiene un método que `Animal` no tiene."],
                        [15, "El método heredado funciona con los datos del perro."],
                        [17, "Un perro es un animal (`True`) y `Perro` es subclase de `Animal`."],
                        [18, "Al revés no: no todo animal es un perro."],
                    ],
                }
            ],
            "quiz": ["poo5-01", "poo5-02", "poo5-03"],
        },
        {
            "id": f"{CID}.super",
            "title": "Constructores y `super()`",
            "theory": "Si la subclase **no** define `__init__`, usa el de la superclase. Si define el suyo, **lo sustituye**: el `__init__` de la superclase ya no se ejecuta solo y sus atributos no se crean.\n\nPor eso el constructor de la subclase suele empezar llamando a **`super().__init__(...)`** con los datos que necesita la superclase, y después guarda los suyos.\n\n- `super()` da acceso a la superclase sin escribir su nombre; no se pasa `self`.\n- Si se olvida, los atributos de la superclase no existen y aparece `AttributeError` más tarde.\n- También funciona `Superclase.__init__(self, ...)`, pero `super()` es más claro y se adapta mejor a jerarquías grandes.",
            "examples": [
                {
                    "code": 'class Persona:\n    def __init__(self, nombre):\n        self.nombre = nombre\n\n\nclass Alumno(Persona):\n    def __init__(self, nombre, curso):\n        super().__init__(nombre)      # crea self.nombre\n        self.curso = curso            # y después lo propio\n\n\nclass Profesor(Persona):\n    def __init__(self, nombre, modulo):\n        self.modulo = modulo          # ¡olvida super().__init__!\n\n\na = Alumno("Ana", "1.º DAW")\nprint(a.nombre, a.curso)\np = Profesor("Luis", "Programación")\nprint(hasattr(p, "nombre"), p.modulo)',
                    "lines": [
                        [8, "Primero se inicializa la parte heredada con los datos de `Persona`."],
                        [9, "Después, los atributos que solo tiene el alumno."],
                        [14, "Este constructor sustituye al de `Persona` y no lo llama."],
                        [20, "Resultado: el profesor no tiene `nombre`."],
                    ],
                }
            ],
            "quiz": ["poo5-04", "poo5-05", "poo5-06"],
        },
        {
            "id": f"{CID}.sobrescribir",
            "title": "Sobrescribir y ampliar métodos",
            "theory": "Una subclase puede **sobrescribir** un método: definir otro con el **mismo nombre**. Cuando se llama sobre un objeto de la subclase, Python usa **su** versión y no la de la superclase.\n\nSi no quieres sustituir el método sino **ampliarlo**, llama dentro a la versión de la superclase con `super().metodo(...)` y añade lo nuevo.\n\nPython busca un método primero en la clase del objeto y, si no está, va subiendo por la jerarquía (el orden se ve en `Clase.__mro__`). Un consejo: usa la herencia solo si de verdad hay una relación «es un». Heredar únicamente para reutilizar un par de métodos suele dar jerarquías difíciles de mantener; para eso está la composición (Unidad 7).",
            "examples": [
                {
                    "code": 'class Producto:\n    def __init__(self, nombre, precio):\n        self.nombre = nombre\n        self.precio = precio\n\n    def etiqueta(self):\n        return f"{self.nombre}: {self.precio:.2f} €"\n\n\nclass Oferta(Producto):\n    def __init__(self, nombre, precio, descuento):\n        super().__init__(nombre, precio)\n        self.descuento = descuento\n\n    def etiqueta(self):                          # sobrescribe\n        base = super().etiqueta()                # reutiliza la de Producto\n        return f"{base} (-{self.descuento} %)"   # y la amplía\n\n\nfor p in [Producto("Libro", 20), Oferta("Ratón", 15, 10)]:\n    print(p.etiqueta())\nprint([c.__name__ for c in Oferta.__mro__])',
                    "lines": [
                        [
                            15,
                            "Mismo nombre que en `Producto`: para una oferta se usa esta versión.",
                        ],
                        [16, "`super().etiqueta()` devuelve la etiqueta normal del producto."],
                        [20, "Cada objeto usa la versión de su clase."],
                        [
                            22,
                            "El orden de búsqueda: primero `Oferta`, luego `Producto` y al final `object`.",
                        ],
                    ],
                }
            ],
            "quiz": ["poo5-07", "poo5-08", "poo5-09"],
        },
    ],
    "guided": ["poo5-10"],
    "autonomous": ["poo5-11", "poo5-12"],
    "selfcheck": ["poo5-13", "poo5-14"],
    "recap": [
        "`class Hija(Padre):` crea una subclase que recibe todos los atributos y métodos de la superclase.",
        "La herencia expresa «es un»; si la relación es «tiene un», usa composición.",
        "Si la subclase define `__init__`, debe llamar a `super().__init__(...)` para crear la parte heredada.",
        "Sobrescribir es definir un método con el mismo nombre; `super().metodo()` permite ampliarlo en vez de sustituirlo.",
        "`isinstance` acepta las superclases e `issubclass` compara clases.",
    ],
    "pass": {
        "minScore": 0.7,
        "required": ["poo5-10", "poo5-11"],
        "text": [
            "Resolver el ejercicio guiado (empleados) y el autónomo de figuras con todos los tests superados.",
            "Dominar la unidad según el motor: al menos un 70 % de aciertos recientes en sus ejercicios, con varios tipos distintos.",
            "Completar las lecciones ayuda a organizarte, pero **no** demuestra la competencia: la demuestran los ejercicios.",
        ],
    },
    "curriculum": [
        proposed("0485-RA4-g", "Se definen y usan clases heredadas."),
        proposed("0485-RA7-a", "Se identifican la herencia, la superclase y la subclase."),
        proposed(
            "0485-RA7-c",
            "Se reconoce el efecto de los constructores en la herencia (`super().__init__`).",
        ),
        proposed("0485-RA7-d", "Se crean subclases que sobrescriben métodos de la superclase."),
        proposed("0485-RA7-e", "Se diseñan jerarquías de clases sencillas."),
    ],
}

EXERCISES = [
    # ---------- Lección «Superclase y subclase»
    output(
        "poo5-01",
        CID,
        """
        class Vehiculo:
            pass

        class Coche(Vehiculo):
            pass

        c = Coche()
        print(isinstance(c, Vehiculo), issubclass(Vehiculo, Coche))
        """,
        "True False",
        "Un coche es un vehículo, así que `isinstance(c, Vehiculo)` es `True`. Pero `Vehiculo` no es subclase de `Coche`: la herencia va de la superclase hacia abajo, no al revés.",
        traps={
            "True True": f"{CID}.jerarquia-al-reves",
            "False False": f"{CID}.jerarquia-al-reves",
        },
        level=1,
        daw=False,
    ),
    choice(
        "poo5-02",
        CID,
        "¿En cuál de estos casos encaja la herencia?",
        [
            ("Un `Gato` es un `Animal`", None),
            ("Un `Coche` tiene un `Motor`", f"{CID}.es-un-tiene-un"),
            ("Una `Biblioteca` tiene muchos `Libro`", f"{CID}.es-un-tiene-un"),
            ("Un `Pedido` tiene una lista de `Producto`", f"{CID}.es-un-tiene-un"),
        ],
        0,
        "La herencia es para relaciones «es un». Cuando un objeto **tiene** otros dentro (motor, libros, productos), se usa composición: un atributo que guarda esos objetos.",
        level=1,
        daw=False,
    ),
    output(
        "poo5-03",
        CID,
        """
        class Vehiculo:
            def __init__(self, ruedas):
                self.ruedas = ruedas

            def describir(self):
                return f"{self.ruedas} ruedas"

        class Moto(Vehiculo):
            pass

        print(Moto(2).describir())
        """,
        "2 ruedas",
        "`Moto` no define nada, así que hereda `__init__` y `describir` de `Vehiculo`. Por eso `Moto(2)` funciona y usa el mismo método.",
        traps={"None": None, "ruedas": None},
        level=1,
        daw=False,
    ),
    # ---------- Lección «Constructores y super()»
    bug(
        "poo5-04",
        CID,
        "Debería mostrar `Ana 1.º DAW`. ¿Qué línea falla?",
        """
        class Persona:
            def __init__(self, nombre):
                self.nombre = nombre

        class Alumno(Persona):
            def __init__(self, nombre, curso):
                super().__init__()
                self.curso = curso

        a = Alumno("Ana", "1.º DAW")
        print(a.nombre, a.curso)
        """,
        7,
        "        super().__init__(nombre)",
        "Ana 1.º DAW",
        f"{CID}.olvida-super",
        "`super().__init__()` llama al constructor de `Persona`, que necesita el nombre: sin él da `TypeError: missing 1 required positional argument`. Hay que pasarle los datos de la superclase (sin `self`).",
        level=2,
        daw=False,
    ),
    output(
        "poo5-05",
        CID,
        """
        class A:
            def __init__(self):
                print("A")

        class B(A):
            def __init__(self):
                print("B")
                super().__init__()

        B()
        """,
        "B\nA",
        "Se ejecuta el `__init__` de `B`: primero imprime `B` y después, con `super().__init__()`, el de `A`. El constructor de la superclase solo se ejecuta porque se le llama.",
        traps={"A\nB": None, "B": f"{CID}.olvida-super"},
        level=2,
        daw=False,
    ),
    fill(
        "poo5-06",
        CID,
        "Completa la llamada para que el gerente también tenga nombre.",
        """
        class Empleado:
            def __init__(self, nombre):
                self.nombre = nombre

        class Gerente(Empleado):
            def __init__(self, nombre, equipo):
                super().___(nombre)
                self.equipo = equipo

        g = Gerente("Eva", 5)
        print(g.nombre, g.equipo)
        """,
        ["__init__"],
        "`super().__init__(nombre)` ejecuta el constructor de `Empleado`, que guarda el nombre. Después el gerente guarda su propio dato.",
        expect="Eva 5",
        traps={"init": f"{CID}.olvida-super", "Empleado": None},
        level=2,
        daw=False,
    ),
    # ---------- Lección «Sobrescribir y ampliar métodos»
    output(
        "poo5-07",
        CID,
        """
        class Ave:
            def mover(self):
                return "vuela"

        class Pinguino(Ave):
            def mover(self):
                return "nada"

        for ave in [Ave(), Pinguino()]:
            print(ave.mover())
        """,
        "vuela\nnada",
        "`Pinguino` sobrescribe `mover`: para un pingüino se usa su versión. El ave normal sigue con la de `Ave`.",
        traps={"vuela\nvuela": f"{CID}.sobrescribir", "nada\nnada": None},
        level=1,
        daw=False,
    ),
    output(
        "poo5-08",
        CID,
        """
        class Mensaje:
            def texto(self):
                return "Hola"

        class Urgente(Mensaje):
            def texto(self):
                return super().texto() + " (urgente)"

        print(Urgente().texto())
        """,
        "Hola (urgente)",
        '`Urgente` amplía el método: `super().texto()` devuelve `"Hola"` y le añade el aviso.',
        traps={" (urgente)": f"{CID}.sobrescribir", "Hola": f"{CID}.sobrescribir"},
        level=2,
        daw=False,
    ),
    choice(
        "poo5-09",
        CID,
        "`Gerente` hereda de `Empleado` y `Empleado` hereda de `Persona`. Con `g = Gerente(...)`, ¿qué es verdadero?",
        [
            ("`isinstance(g, Persona)` es `True`", None),
            ("Solo `isinstance(g, Gerente)` es `True`", f"{CID}.jerarquia-al-reves"),
            ("`issubclass(Persona, Gerente)` es `True`", f"{CID}.jerarquia-al-reves"),
            ("`g` no tiene los métodos de `Persona`", None),
        ],
        0,
        "La herencia se encadena: un gerente es un empleado y un empleado es una persona, así que el gerente también es una `Persona` y tiene sus métodos.",
        level=2,
        daw=False,
    ),
    # ---------- Ejercicio guiado
    code(
        "poo5-10",
        CID,
        "**Ejercicio guiado: empleados de una empresa.** La clase `Empleado` ya está. Sigue los pasos:\n\n1. Crea `Comercial(Empleado)` con `__init__(self, nombre, sueldo, ventas)`: llama a `super().__init__(nombre, sueldo)` y guarda las ventas.\n2. Sobrescribe `salario()` en `Comercial`: el salario de la superclase más el 10 % de las ventas.\n3. Crea `Gerente(Empleado)` con un `plus` y un `salario()` que sume el plus al de la superclase.\n4. No sobrescribas `descripcion()`: la heredada ya usa el `salario()` de cada uno.",
        """
        class Empleado:
            def __init__(self, nombre, sueldo):
                self.nombre = nombre
                self.sueldo = sueldo

            def salario(self):
                return self.sueldo

            def descripcion(self):
                return f"{self.nombre}: {self.salario():.2f} €"


        # Paso 1 y 2: Comercial

        # Paso 3: Gerente


        print(Empleado("Ana", 1500).descripcion())
        """,
        """
        class Empleado:
            def __init__(self, nombre, sueldo):
                self.nombre = nombre
                self.sueldo = sueldo

            def salario(self):
                return self.sueldo

            def descripcion(self):
                return f"{self.nombre}: {self.salario():.2f} €"


        class Comercial(Empleado):
            def __init__(self, nombre, sueldo, ventas):
                super().__init__(nombre, sueldo)
                self.ventas = ventas

            def salario(self):
                return super().salario() + self.ventas * 0.10


        class Gerente(Empleado):
            def __init__(self, nombre, sueldo, plus):
                super().__init__(nombre, sueldo)
                self.plus = plus

            def salario(self):
                return super().salario() + self.plus


        print(Empleado("Ana", 1500).descripcion())
        print(Comercial("Leo", 1200, 3000).descripcion())
        print(Gerente("Eva", 2000, 500).descripcion())
        """,
        [
            case(
                'assert Empleado("Ana", 1500).descripcion() == "Ana: 1500.00 €", "No cambies la clase Empleado"',
            ),
            case(
                'c = Comercial("Leo", 1200, 3000)\nassert issubclass(Comercial, Empleado), "Comercial debe heredar de Empleado: class Comercial(Empleado)"\nassert c.nombre == "Leo" and c.ventas == 3000, "Llama a super().__init__(nombre, sueldo) y guarda las ventas"\nassert c.salario() == 1500, f"1200 + 10 % de 3000 = 1500; salario() devuelve {c.salario()!r}"\nassert c.descripcion() == "Leo: 1500.00 €", "descripcion() heredada debe usar el salario del comercial"',
                error=f"{CID}.olvida-super",
            ),
            case(
                'g = Gerente("Eva", 2000, 500)\nassert issubclass(Gerente, Empleado), "Gerente debe heredar de Empleado"\nassert g.salario() == 2500, f"2000 + 500 = 2500; salario() devuelve {g.salario()!r}"\nassert "descripcion" not in Comercial.__dict__ and "descripcion" not in Gerente.__dict__, "No sobrescribas descripcion(): reutiliza la de Empleado"',
                error=f"{CID}.sobrescribir",
            ),
        ],
        "Lo común (nombre, sueldo, `descripcion`) se escribe una vez en `Empleado`. Cada subclase solo añade lo suyo y cambia `salario`. Como `descripcion` llama a `self.salario()`, cada objeto usa su propia versión.",
        "En `salario` de la subclase usa `super().salario()` para obtener el sueldo base y súmale lo que corresponda.",
        wrong=[
            (
                """
                class Empleado:
                    def __init__(self, nombre, sueldo):
                        self.nombre = nombre
                        self.sueldo = sueldo

                    def salario(self):
                        return self.sueldo

                    def descripcion(self):
                        return f"{self.nombre}: {self.salario():.2f} €"


                class Comercial(Empleado):
                    def __init__(self, nombre, sueldo, ventas):
                        self.ventas = ventas

                    def salario(self):
                        return super().salario() + self.ventas * 0.10


                class Gerente(Empleado):
                    def __init__(self, nombre, sueldo, plus):
                        super().__init__(nombre, sueldo)
                        self.plus = plus

                    def salario(self):
                        return super().salario() + self.plus
                """,
                2,
            ),
        ],
        level=2,
        daw=False,
    ),
    # ---------- Ejercicios autónomos
    code(
        "poo5-11",
        CID,
        '**Ejercicio autónomo: figuras geométricas.** Crea:\n\n- `Figura` con `__init__(self, nombre)`, un método `area()` que lance `NotImplementedError` y `describir()`, que devuelva `"Rectángulo: 6.00"` (nombre y área con dos decimales).\n- `Rectangulo(Figura)` con `__init__(self, base, altura)`; su nombre es `"Rectángulo"`.\n- `Circulo(Figura)` con `__init__(self, radio)`; su nombre es `"Círculo"` y su área `math.pi * radio ** 2`.\n\nLas subclases solo sobrescriben `area()`: `describir()` se hereda.',
        """
        import math

        class Figura:
            ...
        """,
        """
        import math


        class Figura:
            def __init__(self, nombre):
                self.nombre = nombre

            def area(self):
                raise NotImplementedError("Cada figura calcula su área")

            def describir(self):
                return f"{self.nombre}: {self.area():.2f}"


        class Rectangulo(Figura):
            def __init__(self, base, altura):
                super().__init__("Rectángulo")
                self.base = base
                self.altura = altura

            def area(self):
                return self.base * self.altura


        class Circulo(Figura):
            def __init__(self, radio):
                super().__init__("Círculo")
                self.radio = radio

            def area(self):
                return math.pi * self.radio**2


        for figura in [Rectangulo(2, 3), Circulo(1)]:
            print(figura.describir())
        """,
        [
            case(
                'r = Rectangulo(2, 3)\nassert r.area() == 6, "El área del rectángulo es base * altura"\nassert r.describir() == "Rectángulo: 6.00", f"describir() debe devolver \'Rectángulo: 6.00\'; devuelve {r.describir()!r}"',
            ),
            case(
                'c = Circulo(1)\nassert isinstance(c, Figura) and isinstance(Rectangulo(1, 1), Figura), "Rectangulo y Circulo deben heredar de Figura"\nassert c.describir() == "Círculo: 3.14", f"describir() debe devolver \'Círculo: 3.14\'; devuelve {c.describir()!r}"\nassert "describir" not in Circulo.__dict__ and "describir" not in Rectangulo.__dict__, "describir() se hereda de Figura: no la repitas"',
                error=f"{CID}.sobrescribir",
            ),
            case(
                'try:\n    Figura("x").area()\nexcept NotImplementedError:\n    pass\nelse:\n    raise AssertionError("Figura.area() debe lanzar NotImplementedError")',
            ),
        ],
        "`Figura` guarda lo común y deja `area` sin implementar; cada subclase la sobrescribe. `describir` llama a `self.area()`, así que funciona para cualquier figura sin repetir código.",
        'En el `__init__` de cada subclase llama a `super().__init__("Rectángulo")` (o `"Círculo"`) y guarda sus medidas.',
        wrong=[
            (
                """
                import math


                class Figura:
                    def __init__(self, nombre):
                        self.nombre = nombre

                    def area(self):
                        raise NotImplementedError("Cada figura calcula su área")

                    def describir(self):
                        return f"{self.nombre}: {self.area():.2f}"


                class Rectangulo(Figura):
                    def __init__(self, base, altura):
                        super().__init__("Rectángulo")
                        self.base = base
                        self.altura = altura

                    def area(self):
                        return self.base * self.altura


                class Circulo:
                    def __init__(self, radio):
                        self.nombre = "Círculo"
                        self.radio = radio

                    def area(self):
                        return math.pi * self.radio**2

                    def describir(self):
                        return f"{self.nombre}: {self.area():.2f}"
                """,
                2,
            ),
        ],
        level=2,
        daw=False,
    ),
    code(
        "poo5-12",
        CID,
        "**Ejercicio autónomo: tipos de cuenta.** Crea:\n\n- `Cuenta` con `__init__(self, titular, saldo=0)` y `retirar(cantidad)`, que lanza `ValueError` si no hay saldo suficiente y, si lo hay, resta y devuelve el saldo.\n- `CuentaAhorro(Cuenta)` con un `interes` (en %) y el método `aplicar_interes()`, que suma el interés al saldo y lo devuelve.\n- `CuentaCredito(Cuenta)` con un `limite`: sobrescribe `retirar` para permitir quedarse en negativo hasta `-limite`.",
        """
        class Cuenta:
            ...
        """,
        """
        class Cuenta:
            def __init__(self, titular, saldo=0):
                self.titular = titular
                self.saldo = saldo

            def retirar(self, cantidad):
                if cantidad > self.saldo:
                    raise ValueError("Saldo insuficiente")
                self.saldo -= cantidad
                return self.saldo


        class CuentaAhorro(Cuenta):
            def __init__(self, titular, saldo=0, interes=2):
                super().__init__(titular, saldo)
                self.interes = interes

            def aplicar_interes(self):
                self.saldo += self.saldo * self.interes / 100
                return self.saldo


        class CuentaCredito(Cuenta):
            def __init__(self, titular, saldo=0, limite=100):
                super().__init__(titular, saldo)
                self.limite = limite

            def retirar(self, cantidad):
                if self.saldo - cantidad < -self.limite:
                    raise ValueError("Límite de crédito superado")
                self.saldo -= cantidad
                return self.saldo


        ahorro = CuentaAhorro("Ana", 100, interes=5)
        print(ahorro.aplicar_interes())
        credito = CuentaCredito("Leo", 0, limite=100)
        print(credito.retirar(80))
        """,
        [
            case(
                'c = Cuenta("A", 50)\nassert c.retirar(20) == 30, "retirar() resta y devuelve el saldo"\ntry:\n    c.retirar(100)\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError("Cuenta.retirar() sin saldo suficiente debe lanzar ValueError")',
            ),
            case(
                'a = CuentaAhorro("A", 100, interes=5)\nassert isinstance(a, Cuenta), "CuentaAhorro debe heredar de Cuenta"\nassert a.titular == "A", "Llama a super().__init__ para guardar el titular"\nassert a.aplicar_interes() == 105, "100 € con un 5 % de interés son 105"\nassert a.retirar(5) == 100, "La cuenta de ahorro hereda retirar()"',
                error=f"{CID}.olvida-super",
            ),
            case(
                'k = CuentaCredito("A", 0, limite=100)\nassert isinstance(k, Cuenta), "CuentaCredito debe heredar de Cuenta"\nassert k.retirar(80) == -80, "Con crédito se puede quedar en negativo hasta el límite"\ntry:\n    k.retirar(30)\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError("Pasar de -limite debe lanzar ValueError")\nassert k.saldo == -80, "Una retirada rechazada no cambia el saldo"',
                error=f"{CID}.sobrescribir",
            ),
        ],
        "Las tres cuentas comparten titular, saldo y la idea de retirar. `CuentaAhorro` añade un método y hereda `retirar`; `CuentaCredito` lo sobrescribe porque su regla es distinta.",
        "En `CuentaCredito.retirar` la condición es `self.saldo - cantidad < -self.limite`.",
        wrong=[
            (
                """
                class Cuenta:
                    def __init__(self, titular, saldo=0):
                        self.titular = titular
                        self.saldo = saldo

                    def retirar(self, cantidad):
                        if cantidad > self.saldo:
                            raise ValueError("Saldo insuficiente")
                        self.saldo -= cantidad
                        return self.saldo


                class CuentaAhorro(Cuenta):
                    def __init__(self, titular, saldo=0, interes=2):
                        super().__init__(titular, saldo)
                        self.interes = interes

                    def aplicar_interes(self):
                        self.saldo += self.saldo * self.interes / 100
                        return self.saldo


                class CuentaCredito(Cuenta):
                    def __init__(self, titular, saldo=0, limite=100):
                        super().__init__(titular, saldo)
                        self.limite = limite
                """,
                3,
            ),
        ],
        level=2,
        daw=False,
    ),
    # ---------- Autoevaluación
    choice(
        "poo5-13",
        CID,
        "Quieres reutilizar el código de la clase `Motor` en la clase `Coche`. ¿Debe `Coche` heredar de `Motor`?",
        [
            (
                "No: un coche *tiene* un motor, así que `Coche` debe guardar un objeto `Motor` (composición)",
                None,
            ),
            ("Sí: heredar es la forma de reutilizar código de otra clase", f"{CID}.es-un-tiene-un"),
            ("Sí, porque `Motor` es más pequeño que `Coche`", f"{CID}.es-un-tiene-un"),
            ("No se puede saber sin ejecutar el programa", None),
        ],
        0,
        "La prueba es la frase «es un»: «un coche es un motor» es falso. La herencia no es solo para reutilizar código: modela una relación. Aquí lo correcto es un atributo `self.motor = Motor(...)` (Unidad 7).",
        level=2,
        daw=False,
    ),
    output(
        "poo5-14",
        CID,
        """
        class Base:
            def __init__(self):
                self.x = 1

        class Hija(Base):
            def __init__(self):
                self.y = 2

        h = Hija()
        print(hasattr(h, "x"), hasattr(h, "y"))
        """,
        "False True",
        "`Hija` define su propio `__init__` y no llama a `super().__init__()`, así que el de `Base` no se ejecuta y `x` no existe.",
        traps={"True True": f"{CID}.olvida-super"},
        level=2,
        daw=False,
    ),
]

# Errores típicos (slug, etiqueta, por qué, qué pensar, cómo evitarlo)
ERRORS = [
    (
        "es-un-tiene-un",
        "Usa herencia donde la relación es «tiene un»",
        "La herencia modela «es un». Si un objeto contiene otro (un coche tiene un motor), la subclase hereda cosas que no tienen sentido y la jerarquía se vuelve rara.",
        "¿Es natural decir «un X es un Y»?",
        "Si es «tiene un», guarda el otro objeto en un atributo (composición).",
    ),
    (
        "olvida-super",
        "Olvida llamar a `super().__init__` (o no le pasa los datos)",
        "Si la subclase define su `__init__`, el de la superclase no se ejecuta solo: sus atributos no se crean.",
        "¿Mi constructor crea también los atributos de la superclase?",
        "Empieza el `__init__` de la subclase con `super().__init__(datos_de_la_superclase)`.",
    ),
    (
        "sobrescribir",
        "No entiende qué versión de un método se ejecuta al sobrescribirlo",
        "Python usa el método de la clase del objeto; solo si no existe sube a la superclase. `super().metodo()` llama explícitamente a la de arriba.",
        "¿De qué clase es el objeto? ¿Esa clase define el método?",
        "Sigue el orden de búsqueda (`Clase.__mro__`): primero la clase del objeto, luego sus superclases.",
    ),
    (
        "jerarquia-al-reves",
        "Interpreta la jerarquía al revés",
        "Un objeto de la subclase también es de la superclase, pero no al revés: todo perro es un animal, no todo animal es un perro.",
        "¿Cuál es la clase general y cuál la concreta?",
        "Lee `class Hija(Padre)` como «Hija es un tipo de Padre».",
    ),
]
