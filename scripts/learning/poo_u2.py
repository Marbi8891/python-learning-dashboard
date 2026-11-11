# ruff: noqa: E501
"""Unidad 2 del módulo de POO: creación de clases y objetos.

Es el concepto `poo` de concepts.py (su id no cambia, para conservar el progreso de los alumnos):
OVERRIDES sustituye su título y su resumen, y UNIT le añade los campos de unidad.
La salida de los ejemplos la obtiene build_learning.py ejecutándolos.
"""

from exercises import bug as bug_exercise
from exercises import case, choice, code, fill, output
from poo_common import practice, proposed, ref

CID = "poo"

OVERRIDES = {
    "title": "Creación de clases y objetos",
    "area": "poo",
    "summary": "Definir clases, crear objetos con `__init__`, usar `self` y trabajar con el estado de varios objetos.",
    # Desde el Sprint 2 la Unidad 2 se apoya en la Unidad 1 (que a su vez pide funciones y diccionarios)
    "requires": ["poo-fundamentos"],
}

UNIT = {
    "unit": {"module": "poo", "number": 2},
    "objectives": [
        "Definir una clase con `class` y crear varios objetos a partir de ella.",
        "Escribir un constructor `__init__` que dé a cada objeto sus datos iniciales.",
        "Explicar qué es `self` y por qué no se escribe al llamar a un método.",
        "Distinguir el estado (atributos) del comportamiento (métodos) de un objeto.",
        "Predecir qué ocurre al modificar un objeto y sus alias.",
        "Definir `__str__` para que un objeto se muestre como un texto útil.",
    ],
    "prior": "Funciones con parámetros y `return`, listas y diccionarios. Conviene haber leído la Unidad 1 (qué es una clase y qué es un objeto), aunque esta unidad lo vuelve a explicar desde cero.",
    "key": [
        [
            "Clase",
            "La plantilla que describe qué datos y qué acciones tendrán sus objetos. Se define con `class`.",
        ],
        [
            "Objeto o instancia",
            'Cada ejemplar concreto creado a partir de una clase: `ana = Alumno("Ana", 19)`.',
        ],
        ["Instanciar", "Crear un objeto llamando a la clase como si fuera una función."],
        [
            "Constructor `__init__`",
            "Método que Python ejecuta solo al crear el objeto para darle sus atributos iniciales.",
        ],
        [
            "`self`",
            "El propio objeto con el que se está trabajando. Es el primer parámetro de todo método de instancia.",
        ],
        ["Atributo", "Un dato guardado en el objeto (`self.nombre`)."],
        [
            "Método",
            "Una función definida dentro de la clase que trabaja con los datos del objeto.",
        ],
        ["Estado", "Los valores que tienen los atributos de un objeto en un momento dado."],
    ],
    "sections": [
        {
            "id": "poo.definir",
            "title": "Definir una clase y crear objetos",
            "theory": "Una **clase** se define con la palabra `class` seguida de su nombre. Por convenio, los nombres de clase van en *PascalCase*: `Alumno`, `CuentaBancaria`. Todo lo que va sangrado debajo pertenece a la clase.\n\nPara **instanciar** (crear un objeto) se *llama* a la clase como si fuera una función: `ana = Alumno()`. Cada llamada crea un objeto **nuevo e independiente**, aunque sea de la misma clase.\n\n- `type(objeto)` dice de qué clase es un objeto, e `isinstance(objeto, Clase)` lo comprueba.\n- `a is b` dice si dos variables apuntan **al mismo** objeto.\n- Sin paréntesis no se crea nada: `x = Alumno` guarda la clase en otra variable, no un objeto.",
            "examples": [
                {
                    "code": "class Alumno:\n    pass                      # clase vacía, de momento\n\n\nana = Alumno()                # instancia: un objeto nuevo\nluis = Alumno()               # otro objeto, distinto del anterior\n\nprint(type(ana).__name__)\nprint(ana is luis)\nprint(isinstance(ana, Alumno))",
                    "lines": [
                        [
                            1,
                            "`class Alumno:` define la clase. Todavía no existe ningún alumno.",
                        ],
                        [
                            2,
                            "`pass` deja la clase vacía: no hace nada, pero la sintaxis pide al menos una línea.",
                        ],
                        [
                            5,
                            "Con paréntesis se llama a la clase y se crea un objeto. `ana` apunta a él.",
                        ],
                        [6, "Otra llamada, otro objeto: `luis` no es el mismo que `ana`."],
                        [
                            8,
                            "`type(ana)` es la clase `Alumno`; su `__name__` es el texto `'Alumno'`.",
                        ],
                        [
                            9,
                            "`False`: son dos objetos distintos, aunque sean de la misma clase.",
                        ],
                    ],
                }
            ],
            "quiz": ["poo-04", "poo-05", "poo-06"],
        },
        {
            "id": "poo.init-self",
            "title": "El constructor `__init__` y `self`",
            "theory": 'Un objeto vacío sirve de poco. El método especial **`__init__`** (dos guiones bajos a cada lado) se ejecuta **automáticamente** cada vez que se crea un objeto y le da sus datos iniciales.\n\n- Su primer parámetro es **`self`**: el objeto que se acaba de crear. Con `self.nombre = nombre` se guarda el dato *dentro* del objeto (un **atributo**).\n- Al crear el objeto **no se escribe** `self`: `Alumno("Ana", 19)` hace que Python ejecute `Alumno.__init__(objeto_nuevo, "Ana", 19)`.\n- Se le pueden poner parámetros con valor por defecto, como a cualquier función.\n- `__init__` no devuelve nada: solo prepara el objeto.\n\nSi el nombre está mal escrito (`_init_`, `__int__`), Python no lo reconoce como constructor y falla al pasarle datos: `TypeError: Alumno() takes no arguments`.',
            "examples": [
                {
                    "code": 'class Alumno:\n    def __init__(self, nombre, edad, curso="1.º DAW"):\n        self.nombre = nombre      # atributo de instancia\n        self.edad = edad\n        self.curso = curso\n\n\nana = Alumno("Ana", 19)\neva = Alumno("Eva", 22, "2.º DAW")\nprint(ana.nombre, ana.curso)\nprint(eva.nombre, eva.curso)',
                    "lines": [
                        [
                            2,
                            "`__init__` recibe primero `self` y después los datos. `curso` es opcional.",
                        ],
                        [
                            3,
                            "`self.nombre = nombre`: el parámetro (local) se guarda como atributo del objeto.",
                        ],
                        [
                            8,
                            "No se pasa `self`: Python lo añade solo. `curso` toma el valor por defecto.",
                        ],
                        [9, "Otro objeto con sus propios datos: no pisa los de `ana`."],
                        [10, "Los atributos se leen con un punto: `objeto.atributo`."],
                    ],
                }
            ],
            "quiz": ["poo-02", "poo-07", "poo-08"],
        },
        {
            "id": "poo.estado",
            "title": "Estado y comportamiento de varios objetos",
            "theory": "Un objeto reúne **estado** (los valores de sus atributos) y **comportamiento** (sus **métodos**). Un método es una función definida dentro de la clase; recibe `self` y con él puede leer y cambiar el estado del objeto. Se llama con un punto: `ana.poner_nota(8)`.\n\nCada objeto tiene **su propio estado**: cambiar `ana` no cambia `luis`. Pero ojo con los **alias**: `b = a` no copia el objeto, hace que `b` apunte al **mismo** objeto que `a`. Cualquier cambio hecho por `b` se ve desde `a`.",
            "examples": [
                {
                    "code": 'class Alumno:\n    def __init__(self, nombre):\n        self.nombre = nombre\n        self.notas = []                 # cada alumno, su propia lista\n\n    def poner_nota(self, nota):\n        self.notas.append(nota)         # cambia el estado del objeto\n\n    def media(self):\n        if not self.notas:\n            return 0\n        return sum(self.notas) / len(self.notas)\n\n\nana = Alumno("Ana")\nluis = Alumno("Luis")\nana.poner_nota(8)\nana.poner_nota(6)\nluis.poner_nota(9)\nprint(ana.nombre, ana.media())\nprint(luis.nombre, luis.media())',
                    "lines": [
                        [4, "La lista se crea en `__init__`: cada objeto tiene la suya."],
                        [6, "Un método: recibe `self` (el alumno) y la nota."],
                        [7, "Modifica el estado del alumno con el que se ha llamado."],
                        [9, "Otro método que solo lee el estado y devuelve un resultado."],
                        [17, "`ana.poner_nota(8)` equivale a `Alumno.poner_nota(ana, 8)`."],
                        [20, "Las notas de `luis` no se mezclan con las de `ana`."],
                    ],
                },
                {
                    "code": "class Contador:\n    def __init__(self):\n        self.valor = 0\n\n\na = Contador()\nb = a            # b NO es una copia: es el mismo objeto\nb.valor = 5\nprint(a.valor)\nc = Contador()   # este sí es otro objeto\nprint(c.valor)",
                    "lines": [
                        [7, "Asignar un objeto a otra variable crea un alias, no una copia."],
                        [9, "Muestra 5: `a` y `b` son el mismo contador."],
                        [
                            10,
                            "Llamar a la clase de nuevo sí crea un objeto distinto, que empieza en 0.",
                        ],
                    ],
                },
            ],
            "quiz": ["poo-01", "poo-09", "poo-10"],
        },
        {
            "id": "poo.str",
            "title": "Mostrar un objeto como texto: `__str__`",
            "theory": "Si haces `print(objeto)` con una clase propia, Python muestra algo como `<__main__.Alumno object at 0x7f…>`: el nombre de la clase y una dirección de memoria, que no ayudan nada.\n\nPara elegir qué se muestra, la clase define el método especial **`__str__`** (dos guiones bajos a cada lado):\n\n- Recibe solo `self` y **devuelve** un texto con `return`. No lo imprime.\n- Python lo llama solo cada vez que necesita el objeto como texto: en `print(objeto)`, en `str(objeto)` y dentro de una *f-string*.\n- Tiene que devolver un `str`. Si devuelve otra cosa (o nada, porque se ha usado `print` dentro), Python termina con `TypeError: __str__ returned non-string`.\n\nEs uno de los **métodos especiales** de Python: no se llaman a mano, sino que Python los usa en momentos concretos, igual que `__init__` al crear el objeto. En la Unidad 8 verás otros, como `__repr__` o `__eq__`.",
            "examples": [
                {
                    "code": 'class Alumno:\n    def __init__(self, nombre, curso):\n        self.nombre = nombre\n        self.curso = curso\n\n    def __str__(self):\n        return f"{self.nombre} ({self.curso})"\n\n\nana = Alumno("Ana", "1.º DAW")\nprint(ana)\nprint("Alumna: " + str(ana))\nprint(f"Hoy expone {ana}")',
                    "lines": [
                        [6, "`__str__` solo recibe `self`: el alumno que hay que mostrar."],
                        [7, "Devuelve el texto con `return`. No usa `print`."],
                        [11, "`print(ana)` llama por dentro a `ana.__str__()`."],
                        [12, "`str(ana)` también lo usa, y así se puede unir con otro texto."],
                        [13, "Una f-string que incluye el objeto lo convierte con `__str__`."],
                    ],
                }
            ],
            "quiz": ["poo-16", "poo-17", "poo-18"],
        },
    ],
    "guided": ["poo-11"],
    "autonomous": ["poo-15"],
    "extras": ["poo-03", "poo-12"],
    "selfcheck": ["poo-13", "poo-14"],
    "recap": [
        "Una clase se define con `class Nombre:` y se instancia llamándola: `objeto = Nombre(...)`.",
        "`__init__` se ejecuta solo al crear cada objeto y guarda sus datos con `self.atributo = valor`.",
        "`self` es el propio objeto: es el primer parámetro de los métodos y no se escribe al llamarlos.",
        "Cada objeto tiene su propio estado; los métodos lo leen y lo cambian.",
        "`b = a` no copia un objeto: las dos variables apuntan al mismo.",
        "`__str__` devuelve el texto con el que se muestra el objeto en `print`, `str()` y las f-strings.",
    ],
    "pass": {
        "minScore": 0.7,
        "required": ["poo-11", "poo-15"],
        "text": [
            "Resolver el ejercicio guiado (`Alumno`) y el ejercicio principal `Vehiculo` con todos los tests superados.",
            "Dominar la unidad según el motor: al menos un 70 % de aciertos recientes en sus ejercicios, con varios tipos distintos.",
            "Completar las lecciones ayuda a organizarte, pero **no** demuestra la competencia: la demuestran los ejercicios.",
        ],
    },
    "practices": [
        practice(
            "Crea todos los atributos del objeto en `__init__`, aunque empiecen vacíos (`self.notas = []`).",
            "Así cualquier método puede contar con ellos y se ve de un vistazo qué datos tiene cada objeto.",
        ),
        practice(
            "Escribe `self.` delante de cada dato que tenga que durar más que el método.",
            "Sin `self.` es una variable local, que desaparece al terminar el método.",
        ),
        practice(
            "Define `__str__` para que `print(objeto)` muestre algo útil, y haz que devuelva el texto con `return`.",
            "Python usa `__str__` en `print`, `str()` y las f-strings, y exige que devuelva un texto.",
        ),
        practice(
            "Da valor por defecto solo a los parámetros que de verdad son opcionales.",
            "Obligar a dar los datos esenciales evita crear objetos a medias.",
        ),
        practice(
            "Si necesitas otro objeto, llama otra vez a la clase: `b = a` solo le pone otro nombre al mismo.",
            "Así no cambias por sorpresa dos «objetos» que en realidad son uno.",
        ),
    ],
    "references": [
        ref(
            "py-tutorial-classes",
            "9.3.2. Objetos clase",
            ["instanciar una clase", "el constructor `__init__` y sus argumentos"],
        ),
        ref(
            "py-tutorial-classes",
            "9.3.3. Objetos instancia y 9.3.4. Objetos método",
            ["atributos de instancia", "por qué `x.f()` equivale a `Clase.f(x)`"],
        ),
        ref(
            "py-faq-programming",
            "Objetos: ¿Qué es self?",
            ["`self` como primer argumento de un método y su nombre por convenio"],
        ),
    ],
    "bank": [
        "poo-02",
        "poo-04",
        "poo-10",
        "poo-13",
        "poo-16",
        "poo-17",
        "poo-18",
        "poo-19",
        "poo-20",
        "poo-21",
        "poo-22",
        "poo-23",
        "poo-24",
        "poo-25",
        "poo-26",
    ],
    "curriculum": [
        proposed("0485-RA2-h", "Se usan constructores (`__init__`) para inicializar objetos."),
        proposed("0485-RA4-b", "Se definen clases propias con `class`."),
        proposed("0485-RA4-d", "Se escriben constructores con parámetros y valores por defecto."),
        proposed(
            "0485-RA4-e",
            "Se escriben programas que crean y usan varios objetos de las clases definidas.",
        ),
    ],
}

EXERCISES = [
    # ---------- Lección «Definir una clase y crear objetos»
    choice(
        "poo-04",
        "poo",
        "Con la clase `Producto` ya definida, ¿qué hace la línea `p = Producto()`?",
        [
            ("Crea un objeto nuevo de la clase `Producto` y lo guarda en `p`", None),
            ("Define una clase nueva llamada `p`", "poo.clase-objeto"),
            ("Guarda en `p` la propia clase `Producto`, sin crear nada", "poo.clase-objeto"),
            ("Ejecuta todos los métodos de `Producto` uno tras otro", None),
        ],
        0,
        "Llamar a la clase (con paréntesis) la **instancia**: crea un objeto nuevo. Sin paréntesis (`p = Producto`) solo se copiaría la referencia a la clase. Los métodos no se ejecutan solos: hay que llamarlos.",
        level=1,
        daw=False,
    ),
    output(
        "poo-05",
        "poo",
        """
        class Perro:
            pass

        a = Perro()
        b = Perro()
        c = a
        print(a is b, a is c)
        """,
        "False True",
        "`a` y `b` son dos objetos distintos (dos llamadas a la clase). `c = a` no crea un objeto: `c` es otro nombre para el mismo objeto que `a`.",
        traps={"True True": "poo.clase-objeto", "False False": "poo.alias-copia"},
        level=1,
        daw=False,
    ),
    bug_exercise(
        "poo-06",
        "poo",
        "Debería mostrar `Ana`. ¿Qué línea falla?",
        """
        class Saludo:
            def __init__(self, nombre):
                self.nombre = nombre

        s = Saludo
        print(s.nombre)
        """,
        5,
        's = Saludo("Ana")',
        "Ana",
        "poo.clase-objeto",
        'Sin paréntesis, `s` es la clase y no un objeto: la clase no tiene el atributo `nombre` y salta `AttributeError`. Hay que crear el objeto con sus datos: `Saludo("Ana")`.',
        level=1,
        daw=False,
    ),
    # ---------- Lección «El constructor __init__ y self»
    fill(
        "poo-07",
        "poo",
        "Completa el nombre del método para que cada libro se cree con su título.",
        """
        class Libro:
            def ___(self, titulo):
                self.titulo = titulo

        libro = Libro("Rayuela")
        print(libro.titulo)
        """,
        ["__init__"],
        'El constructor se llama exactamente `__init__`, con dos guiones bajos a cada lado. Con otro nombre, `Libro("Rayuela")` daría `TypeError: Libro() takes no arguments`.',
        expect="Rayuela",
        traps={
            "_init_": "poo.init-mal-escrito",
            "__int__": "poo.init-mal-escrito",
            "init": "poo.init-mal-escrito",
        },
        level=1,
        daw=False,
    ),
    bug_exercise(
        "poo-08",
        "poo",
        "Debería mostrar `Luis 20`. ¿Qué línea falla?",
        """
        class Alumno:
            def __init__(nombre, edad):
                self.nombre = nombre
                self.edad = edad

        luis = Alumno("Luis", 20)
        print(luis.nombre, luis.edad)
        """,
        2,
        "    def __init__(self, nombre, edad):",
        "Luis 20",
        "poo.olvida-self",
        "El primer parámetro de `__init__` debe ser `self`. Sin él, Python mete el objeto nuevo en `nombre`, sobran argumentos (`TypeError`) y además `self` no existe dentro del método.",
        level=2,
        daw=False,
    ),
    # ---------- Lección «Estado y comportamiento de varios objetos»
    output(
        "poo-09",
        "poo",
        """
        class Lampara:
            def __init__(self):
                self.encendida = False

            def pulsar(self):
                self.encendida = not self.encendida

        luz = Lampara()
        luz.pulsar()
        luz.pulsar()
        luz.pulsar()
        print(luz.encendida)
        """,
        "True",
        "Empieza apagada (`False`) y cada `pulsar()` invierte el estado: tras tres pulsaciones queda encendida (`True`). El método cambia el estado del propio objeto a través de `self`.",
        traps={"False": None},
        level=2,
        daw=False,
    ),
    choice(
        "poo-10",
        "poo",
        "`a` es un objeto con el atributo `x = 1`. Se ejecuta `b = a` y después `b.x = 9`. ¿Cuánto vale `a.x`?",
        [
            ("9, porque `a` y `b` son el mismo objeto", None),
            ("1, porque `b` es una copia de `a`", "poo.alias-copia"),
            ("Da un error: no se puede asignar un objeto a otra variable", None),
            ("1, porque cada variable tiene su propio objeto desde que se crea", "poo.alias-copia"),
        ],
        0,
        "`b = a` no crea un objeto nuevo: `b` es un alias. Lo que se cambie por un nombre se ve por el otro. Para tener otro objeto hay que llamar de nuevo a la clase (o copiarlo explícitamente).",
        level=2,
        daw=False,
    ),
    # ---------- Ejercicio guiado
    code(
        "poo-11",
        "poo",
        '**Ejercicio guiado: la clase `Alumno`.** Sigue los pasos:\n\n1. Escribe `__init__(self, nombre, edad, curso)` y guarda los tres datos como atributos.\n2. Añade el método `presentarse()`, que **devuelva** (no que imprima) el texto `"Soy Ana, tengo 19 años y estudio 1.º DAW"` con los datos del alumno.\n3. Añade el método `cumplir_anios()`, que sume 1 a la edad del alumno.\n4. Pulsa **▶ Ejecutar** para ver el resultado y después **Comprobar con los tests**.',
        """
        class Alumno:
            def __init__(self, nombre, edad, curso):
                # Paso 1: guarda los datos con self.
                ...

            # Paso 2: presentarse()

            # Paso 3: cumplir_anios()


        ana = Alumno("Ana", 19, "1.º DAW")
        print(ana.presentarse())
        ana.cumplir_anios()
        print(ana.edad)
        """,
        """
        class Alumno:
            def __init__(self, nombre, edad, curso):
                self.nombre = nombre
                self.edad = edad
                self.curso = curso

            def presentarse(self):
                return f"Soy {self.nombre}, tengo {self.edad} años y estudio {self.curso}"

            def cumplir_anios(self):
                self.edad += 1


        ana = Alumno("Ana", 19, "1.º DAW")
        print(ana.presentarse())
        ana.cumplir_anios()
        print(ana.edad)
        """,
        [
            case(
                'a = Alumno("Eva", 22, "2.º DAW")\nassert (a.nombre, a.edad, a.curso) == ("Eva", 22, "2.º DAW"), "Guarda nombre, edad y curso como atributos con self (self.nombre = nombre…)"',
                error="poo.olvida-self",
            ),
            case(
                'a = Alumno("Eva", 22, "2.º DAW")\nassert a.presentarse() == "Soy Eva, tengo 22 años y estudio 2.º DAW", f"presentarse() debe devolver el texto con los datos del alumno; devuelve {a.presentarse()!r}"',
            ),
            case(
                'a = Alumno("Eva", 22, "2.º DAW")\nb = Alumno("Leo", 30, "1.º DAW")\na.cumplir_anios()\nassert a.edad == 23, "cumplir_anios() debe sumar 1 a self.edad"\nassert b.edad == 30, "cumplir_anios() solo cambia el alumno con el que se llama"',
                error="poo.clase-objeto",
            ),
        ],
        "Cada dato se guarda en `self` dentro de `__init__`; los métodos lo leen o lo cambian con `self.`. `presentarse` devuelve el texto con `return` para que quien la llame decida si lo imprime.",
        "En `__init__`: `self.nombre = nombre` (igual con edad y curso). `presentarse` devuelve una f-string con `self.nombre`, `self.edad` y `self.curso`. `cumplir_anios` hace `self.edad += 1`.",
        wrong=[
            (
                """
                class Alumno:
                    def __init__(self, nombre, edad, curso):
                        nombre = nombre
                        edad = edad
                        curso = curso

                    def presentarse(self):
                        return ""

                    def cumplir_anios(self):
                        pass
                """,
                1,
            ),
            (
                """
                class Alumno:
                    def __init__(self, nombre, edad, curso):
                        self.nombre = nombre
                        self.edad = edad
                        self.curso = curso

                    def presentarse(self):
                        print(f"Soy {self.nombre}, tengo {self.edad} años y estudio {self.curso}")

                    def cumplir_anios(self):
                        self.edad += 1
                """,
                2,
            ),
        ],
        level=2,
        daw=False,
    ),
    # ---------- Ejercicio autónomo
    code(
        "poo-12",
        "poo",
        '**Ejercicio autónomo: el marcador de un partido.** Crea la clase `Marcador` con:\n\n- `__init__(self, local, visitante)`: los nombres de los equipos; los dos empiezan con 0 goles.\n- `gol_local()` y `gol_visitante()`: suman un gol al equipo correspondiente.\n- `resultado()`: devuelve un texto como `"Betis 2 - 1 Sevilla"`.\n\nCrea un partido, marca algunos goles y muestra el resultado.',
        """
        class Marcador:
            ...
        """,
        """
        class Marcador:
            def __init__(self, local, visitante):
                self.local = local
                self.visitante = visitante
                self.goles_local = 0
                self.goles_visitante = 0

            def gol_local(self):
                self.goles_local += 1

            def gol_visitante(self):
                self.goles_visitante += 1

            def resultado(self):
                return f"{self.local} {self.goles_local} - {self.goles_visitante} {self.visitante}"


        partido = Marcador("Betis", "Sevilla")
        partido.gol_local()
        partido.gol_local()
        partido.gol_visitante()
        print(partido.resultado())
        """,
        [
            case(
                'm = Marcador("A", "B")\nassert m.resultado() == "A 0 - 0 B", f"Un partido nuevo debe empezar 0 - 0; resultado() devuelve {m.resultado()!r}"',
            ),
            case(
                'm = Marcador("A", "B")\nm.gol_local()\nm.gol_local()\nm.gol_visitante()\nassert m.resultado() == "A 2 - 1 B", f"Tras dos goles locales y uno visitante debe ser \'A 2 - 1 B\'; es {m.resultado()!r}"',
                error="poo.olvida-self",
            ),
            case(
                'm1 = Marcador("A", "B")\nm2 = Marcador("C", "D")\nm1.gol_local()\nassert m2.resultado() == "C 0 - 0 D", "Los goles de un partido no deben cambiar otro partido"',
                error="poo.clase-objeto",
            ),
        ],
        "Los goles son el **estado** del marcador y empiezan en 0 en `__init__`; los métodos `gol_*` lo cambian y `resultado` lo lee para construir el texto.",
        "Guarda cuatro atributos en `__init__`: los dos nombres y dos contadores a 0. Cada método `gol_*` suma 1 a su contador con `self.`.",
        wrong=[
            (
                """
                class Marcador:
                    goles_local = 0
                    goles_visitante = 0

                    def __init__(self, local, visitante):
                        self.local = local
                        self.visitante = visitante

                    def gol_local(self):
                        Marcador.goles_local += 1

                    def gol_visitante(self):
                        Marcador.goles_visitante += 1

                    def resultado(self):
                        return f"{self.local} {Marcador.goles_local} - {Marcador.goles_visitante} {self.visitante}"
                """,
                3,
            ),
        ],
        level=2,
        daw=False,
    ),
    # ---------- Autoevaluación
    choice(
        "poo-13",
        "poo",
        "¿Cuál de estas afirmaciones sobre `__init__` es correcta?",
        [
            ("Python lo ejecuta automáticamente cada vez que se crea un objeto de la clase", None),
            (
                "Hay que llamarlo a mano después de crear el objeto: `a.__init__()`",
                "poo.init-mal-escrito",
            ),
            ("Debe terminar con `return self` para que el objeto exista", None),
            ("Solo se ejecuta la primera vez que se usa la clase", "poo.clase-objeto"),
        ],
        0,
        "`__init__` se ejecuta solo en cada instanciación (`Clase(...)`) y no devuelve nada: el objeto ya existe y `__init__` solo le pone sus datos iniciales. Si devolviera algo distinto de `None`, Python lanzaría `TypeError`.",
        level=1,
        daw=False,
    ),
    output(
        "poo-14",
        "poo",
        """
        class Caja:
            def __init__(self, contenido):
                self.contenido = contenido

            def cambiar(self, nuevo):
                contenido = nuevo

        caja = Caja("libros")
        caja.cambiar("ropa")
        print(caja.contenido)
        """,
        "libros",
        'En `cambiar` falta `self.`: `contenido = nuevo` crea una variable **local** del método que desaparece al terminar. El atributo del objeto sigue valiendo `"libros"`.',
        traps={"ropa": "poo.olvida-self"},
        level=2,
        daw=False,
    ),
    # ---------- Ejercicio principal de la unidad
    code(
        "poo-15",
        "poo",
        '**Ejercicio principal: la clase `Vehiculo`.** Crea la clase con:\n\n- `__init__(self, marca, modelo, anio)`: guarda los tres datos como atributos.\n- `__str__()`: devuelve un texto como `"Seat Ibiza (2020)"`, para que `print(coche)` lo muestre así.\n- `antiguedad(anio_actual)`: devuelve los años que tiene el vehículo.\n- `es_clasico(anio_actual)`: devuelve `True` si tiene 25 años o más.\n\nCrea dos vehículos y muéstralos con `print`.',
        """
        class Vehiculo:
            ...
        """,
        """
        class Vehiculo:
            def __init__(self, marca, modelo, anio):
                self.marca = marca
                self.modelo = modelo
                self.anio = anio

            def __str__(self):
                return f"{self.marca} {self.modelo} ({self.anio})"

            def antiguedad(self, anio_actual):
                return anio_actual - self.anio

            def es_clasico(self, anio_actual):
                return self.antiguedad(anio_actual) >= 25


        coche = Vehiculo("Seat", "Ibiza", 2020)
        moto = Vehiculo("Vespa", "Primavera", 1990)
        print(coche)
        print(moto, "es un clásico:", moto.es_clasico(2026))
        """,
        [
            case(
                'v = Vehiculo("Seat", "Ibiza", 2020)\nassert (v.marca, v.modelo, v.anio) == ("Seat", "Ibiza", 2020), "Guarda marca, modelo y anio como atributos con self"',
                error="poo.olvida-self",
            ),
            case(
                'v = Vehiculo("Seat", "Ibiza", 2020)\nassert str(v) == "Seat Ibiza (2020)", f"str(v) debe ser \'Seat Ibiza (2020)\'; es {str(v)!r}"\nassert f"{v}" == "Seat Ibiza (2020)", "Las f-strings también usan __str__"',
            ),
            case(
                'v = Vehiculo("Seat", "Ibiza", 2020)\nassert v.antiguedad(2026) == 6, "antiguedad(2026) de un coche de 2020 es 6"\nassert Vehiculo("Vespa", "PX", 2001).es_clasico(2026) is True, "Con 25 años ya es un clásico"\nassert v.es_clasico(2026) is False, "Con 6 años no es un clásico"',
            ),
            case(
                'a = Vehiculo("Seat", "Ibiza", 2020)\nb = Vehiculo("Renault", "Clio", 2015)\nassert str(a) != str(b), "Cada vehículo se muestra con sus propios datos"',
                error="poo.alias-copia",
            ),
        ],
        "`__str__` devuelve el texto que representa al objeto y Python lo usa en `print`, `str()` y las f-strings. Los demás métodos trabajan con los datos del propio vehículo a través de `self`, y `es_clasico` reutiliza `antiguedad` en vez de repetir la resta.",
        "Escribe `def __str__(self):` con dos guiones bajos a cada lado y **devuelve** la f-string con `return`. `es_clasico` puede llamar a `self.antiguedad(anio_actual)`.",
        wrong=[
            (
                """
                class Vehiculo:
                    def __init__(self, marca, modelo, anio):
                        self.marca = marca
                        self.modelo = modelo
                        self.anio = anio

                    def __str__(self):
                        print(f"{self.marca} {self.modelo} ({self.anio})")

                    def antiguedad(self, anio_actual):
                        return anio_actual - self.anio

                    def es_clasico(self, anio_actual):
                        return self.antiguedad(anio_actual) >= 25
                """,
                2,
            ),
            (
                """
                class Vehiculo:
                    def __init__(self, marca, modelo, anio):
                        self.marca = marca
                        self.modelo = modelo
                        self.anio = anio

                    def __str__(self):
                        return f"{self.marca} {self.modelo} ({self.anio})"

                    def antiguedad(self, anio_actual):
                        return anio_actual - self.anio

                    def es_clasico(self, anio_actual):
                        return self.antiguedad(anio_actual) > 25
                """,
                3,
            ),
        ],
        level=2,
        daw=False,
    ),
    # ---------- Banco de preguntas de la unidad (cuestionario)
    choice(
        "poo-16",
        "poo",
        "¿Qué muestra este programa?",
        [
            ("Seat Ibiza", None),
            (
                "<__main__.Vehiculo object>",
                None,
                "Eso es lo que se vería **sin** `__str__`. Como la clase lo define, `print` usa el texto que devuelve.",
            ),
            (
                "Vehiculo",
                "poo.clase-objeto",
                "`print` no muestra el nombre de la clase: muestra lo que devuelve `__str__` del objeto.",
            ),
            (
                "marca modelo",
                None,
                "La f-string sustituye `self.marca` y `self.modelo` por sus valores, no por sus nombres.",
            ),
        ],
        0,
        "`print(coche)` llama a `coche.__str__()`, que devuelve el texto con la marca y el modelo de ese objeto.",
        code="""
        class Vehiculo:
            def __init__(self, marca, modelo):
                self.marca = marca
                self.modelo = modelo

            def __str__(self):
                return f"{self.marca} {self.modelo}"

        coche = Vehiculo("Seat", "Ibiza")
        print(coche)
        """,
        level=1,
        daw=False,
        bank=True,
        qtype="prediccion",
    ),
    choice(
        "poo-17",
        "poo",
        "Este programa muestra `Ana (1.º DAW)` y después termina con `TypeError`. ¿Por qué?",
        [
            (
                "`__str__` imprime el texto en vez de devolverlo, así que devuelve `None` y no un `str`",
                None,
            ),
            (
                "`__str__` tiene que recibir el texto como parámetro",
                None,
                "`__str__` solo recibe `self`: el texto lo construye a partir de los atributos del objeto.",
            ),
            (
                "No se puede usar `print` con objetos de clases propias",
                None,
                "Sí se puede: `print` llama a `__str__`. El fallo está en lo que devuelve ese método.",
            ),
            (
                "Falta llamar a mano a `ana.__str__()` antes del `print`",
                None,
                "Python llama a `__str__` solo; llamarlo a mano no arregla que devuelva `None`.",
            ),
        ],
        0,
        "`print(ana)` ejecuta `__str__`, que imprime el texto (por eso aparece) pero no tiene `return`. Python recibe `None` y protesta: `__str__` debe **devolver** un texto.",
        code="""
        class Alumno:
            def __init__(self, nombre, curso):
                self.nombre = nombre
                self.curso = curso

            def __str__(self):
                print(f"{self.nombre} ({self.curso})")

        ana = Alumno("Ana", "1.º DAW")
        print(ana)
        """,
        level=2,
        daw=False,
        bank=True,
        qtype="error",
    ),
    choice(
        "poo-18",
        "poo",
        "¿Cuándo usa Python el método `__str__` de un objeto?",
        [
            (
                "Cuando necesita el objeto como texto: en `print(objeto)`, `str(objeto)` y las f-strings",
                None,
            ),
            (
                "Al crear el objeto, justo después de `__init__`",
                "poo.init-mal-escrito",
                "Al crear el objeto solo se ejecuta `__init__`; `__str__` espera a que se pida el objeto como texto.",
            ),
            (
                "Solo cuando se llama a mano: `objeto.__str__()`",
                None,
                "Se puede llamar a mano, pero lo normal es que Python lo llame solo al convertir el objeto en texto.",
            ),
            (
                "Cada vez que cambia uno de sus atributos",
                None,
                "Cambiar un atributo no muestra nada: `__str__` solo se ejecuta cuando se pide el texto.",
            ),
        ],
        0,
        "`__str__` es un método especial: no se suele llamar a mano. Python lo usa cada vez que tiene que convertir el objeto en texto.",
        level=1,
        daw=False,
        bank=True,
        qtype="teoria",
    ),
    choice(
        "poo-19",
        "poo",
        "¿Qué muestra este programa?",
        [
            ("3 15", None),
            (
                "3 3",
                "poo.clase-objeto",
                "`a` y `b` son dos contadores distintos: lo que se suma a uno no se suma al otro.",
            ),
            (
                "2 15",
                None,
                "`a` suma 1 (valor por defecto de `n`) y luego 2: en total 3.",
            ),
            (
                "1 15",
                None,
                "La segunda llamada `a.sumar(2)` también cambia `a`: 1 + 2 = 3.",
            ),
        ],
        0,
        "`a` empieza en 0 y suma 1 y 2 (queda en 3); `b` empieza en 10 y suma 5 (queda en 15). Cada objeto guarda su propio `valor`.",
        code="""
        class Contador:
            def __init__(self, inicio=0):
                self.valor = inicio

            def sumar(self, n=1):
                self.valor += n

        a = Contador()
        b = Contador(10)
        a.sumar()
        b.sumar(5)
        a.sumar(2)
        print(a.valor, b.valor)
        """,
        level=2,
        daw=False,
        bank=True,
        qtype="prediccion",
    ),
    choice(
        "poo-20",
        "poo",
        "¿Qué muestra este programa?",
        [
            ("ropa libros False", None),
            (
                "libros libros False",
                "poo.alias-copia",
                "`b = a` no copia la caja: `a` y `b` son el mismo objeto, así que el cambio se ve desde `a`.",
            ),
            (
                "ropa ropa True",
                "poo.alias-copia",
                "`c` es otra caja creada con `Caja(...)`: el cambio hecho por `b` no le llega.",
            ),
            (
                "ropa libros True",
                None,
                "`is` dice si son el mismo objeto; `a` y `c` tienen el mismo contenido inicial, pero son dos cajas distintas.",
            ),
        ],
        0,
        "`b` es otro nombre de `a`, así que cambiar `b.contenido` cambia `a`. `c` es un objeto distinto y conserva `libros`; por eso `a is c` es `False`.",
        code="""
        class Caja:
            def __init__(self, contenido):
                self.contenido = contenido

        a = Caja("libros")
        b = a
        c = Caja("libros")
        b.contenido = "ropa"
        print(a.contenido, c.contenido, a is c)
        """,
        level=3,
        daw=False,
        bank=True,
        qtype="prediccion",
    ),
    choice(
        "poo-21",
        "poo",
        "Dentro de un método, ¿qué es `self`?",
        [
            ("El objeto con el que se ha llamado al método", None),
            (
                "La clase en la que está definido el método",
                "poo.clase-objeto",
                "En `ana.presentarse()`, `self` es `ana`, no la clase `Alumno`.",
            ),
            (
                "Una palabra reservada: el primer parámetro tiene que llamarse así o Python da error",
                None,
                "Es un convenio muy extendido, pero Python pasa el objeto como primer argumento se llame como se llame.",
            ),
            (
                "Una copia del objeto, así que los cambios no se guardan",
                "poo.olvida-self",
                "No es una copia: lo que se cambia en `self.atributo` se queda en el objeto.",
            ),
        ],
        0,
        "Al escribir `ana.presentarse()`, Python ejecuta `Alumno.presentarse(ana)`: el objeto llega como primer parámetro, que por convenio se llama `self`.",
        level=2,
        daw=False,
        bank=True,
        qtype="teoria",
    ),
    choice(
        "poo-22",
        "poo",
        "Con esta clase, ¿qué hace la línea `ana.poner_nota(8)`?",
        [
            ("Añade 8 a la lista de notas de `ana`: equivale a `Alumno.poner_nota(ana, 8)`", None),
            (
                "Añade 8 a las notas de todos los alumnos",
                "poo.clase-objeto",
                "La lista se crea en `__init__`: cada alumno tiene la suya y solo cambia la de `ana`.",
            ),
            (
                "Crea en `ana` un atributo nuevo llamado `nota` que vale 8",
                None,
                "`nota` es un parámetro del método: el 8 se añade a `self.notas` con `append`.",
            ),
            (
                "Da error, porque falta pasar `self`",
                None,
                "`self` no se escribe al llamar: Python pasa `ana` como primer argumento.",
            ),
        ],
        0,
        "Un método se llama desde un objeto y recibe ese objeto en `self`. Así `self.notas.append(nota)` cambia solo las notas de `ana`.",
        code="""
        class Alumno:
            def __init__(self, nombre):
                self.nombre = nombre
                self.notas = []

            def poner_nota(self, nota):
                self.notas.append(nota)
        """,
        level=1,
        daw=False,
        bank=True,
        qtype="codigo",
    ),
    choice(
        "poo-23",
        "poo",
        "Cada cuenta debe guardar su titular y empezar con saldo 0. ¿Qué constructor es correcto?",
        [
            ("def __init__(self, titular): self.titular = titular; self.saldo = 0", None),
            (
                "def __init__(titular): self.titular = titular; self.saldo = 0",
                "poo.olvida-self",
                "Falta `self` como primer parámetro: Python pasaría la cuenta en `titular` y `self` no existiría.",
            ),
            (
                "def __init__(self, titular): titular = titular; saldo = 0",
                "poo.olvida-self",
                "Sin `self.` son variables locales que desaparecen al terminar `__init__`: la cuenta se queda sin datos.",
            ),
            (
                "def _init_(self, titular): self.titular = titular; self.saldo = 0",
                "poo.init-mal-escrito",
                "Con un solo guion bajo a cada lado no es el constructor: Python no lo ejecuta al crear la cuenta.",
            ),
        ],
        0,
        "El constructor se llama exactamente `__init__`, recibe `self` primero y guarda cada dato con `self.`.",
        level=3,
        daw=False,
        code_options=True,
        bank=True,
        qtype="solucion",
    ),
    choice(
        "poo-24",
        "poo",
        "Queremos que `print(v)` muestre `Seat Ibiza (2020)`. ¿Qué método lo consigue?",
        [
            ('def __str__(self): return f"{self.marca} {self.modelo} ({self.anio})"', None),
            (
                'def __str__(self): print(f"{self.marca} {self.modelo} ({self.anio})")',
                None,
                "Imprime el texto pero devuelve `None`, y `print(v)` termina con `TypeError`.",
            ),
            (
                'def str(self): return f"{self.marca} {self.modelo} ({self.anio})"',
                None,
                "`print` busca `__str__`, con dos guiones bajos a cada lado; un método `str` normal no lo usa.",
            ),
            (
                'def __str__(): return f"{marca} {modelo} ({anio})"',
                "poo.olvida-self",
                "Sin `self` el método no recibe el vehículo y `marca` no existe como variable.",
            ),
        ],
        0,
        "`__str__` recibe `self` y **devuelve** el texto construido con los atributos del objeto.",
        level=3,
        daw=False,
        code_options=True,
        bank=True,
        qtype="solucion",
    ),
    choice(
        "poo-25",
        "poo",
        "Una aplicación de gimnasio guarda los socios con su nombre y su cuota, y tiene que poder cambiar la cuota de un socio. ¿Qué diseño encaja?",
        [
            (
                "Una clase `Socio` con los atributos `nombre` y `cuota` y un método `cambiar_cuota(nueva)`",
                None,
            ),
            (
                "Una clase por cada socio: `Ana`, `Luis`, `Eva`…",
                "poo.clase-objeto",
                "Los socios concretos son objetos de una misma clase; crear una clase por persona repite el mismo código.",
            ),
            (
                "Una variable global `cuota` que comparten todos los socios",
                None,
                "Cada socio puede pagar una cuota distinta: el dato tiene que ser de cada objeto.",
            ),
            (
                "Una clase `Cuota` con un método `nombre()`",
                None,
                "El nombre es un dato del socio, no una acción de la cuota: el diseño confunde qué es cada cosa.",
            ),
        ],
        0,
        "Cada socio es un objeto con sus propios datos y la acción que los cambia va en la misma clase.",
        level=2,
        daw=False,
        bank=True,
        qtype="diseno",
    ),
    choice(
        "poo-26",
        "poo",
        "Cada `Pista` de pádel tiene su propia lista de reservas. ¿Dónde conviene crear esa lista?",
        [
            ("En `__init__`, con `self.reservas = []`, para que cada pista tenga la suya", None),
            (
                "Debajo de `class Pista:`, con `reservas = []`",
                "poo.clase-objeto",
                "Así sería una sola lista de la clase, compartida por todas las pistas (lo verás en la Unidad 3).",
            ),
            (
                "Fuera de la clase, como variable global",
                None,
                "Una lista global no sabe a qué pista pertenece cada reserva.",
            ),
            (
                "Dentro del método `reservar`, con `reservas = []` cada vez",
                "poo.olvida-self",
                "Se crearía una lista nueva y local en cada llamada: las reservas anteriores se perderían.",
            ),
        ],
        0,
        "Lo que es de cada objeto se crea en `__init__` con `self.`: así cada pista empieza con su lista vacía.",
        level=3,
        daw=False,
        bank=True,
        qtype="diseno",
    ),
]

# Errores típicos nuevos de la Unidad 2 (se añaden a los del concepto `poo`)
ERRORS = [
    (
        "init-mal-escrito",
        "Escribe mal `__init__` o cree que hay que llamarlo a mano",
        "El constructor solo funciona si se llama exactamente `__init__` (dos guiones bajos a cada lado). Python lo llama solo al crear el objeto.",
        "¿He escrito `__init__` letra a letra? ¿Estoy creando el objeto con `Clase(...)`?",
        "Copia el nombre `__init__` tal cual y crea los objetos llamando a la clase.",
    ),
    (
        "alias-copia",
        "Cree que `b = a` copia el objeto",
        "Asignar un objeto a otra variable no lo copia: las dos variables apuntan al mismo objeto y los cambios se ven por las dos.",
        "¿He llamado a la clase otra vez o solo he puesto otro nombre al mismo objeto?",
        "Para tener otro objeto, créalo con `Clase(...)`; `is` te dice si dos variables son el mismo objeto.",
    ),
]

# Preguntas tipo test que ya existían y pasan al banco: (tipo, nivel, por qué falla cada distractor)
BANK_TAGS = {
    "poo-02": (
        "error",
        2,
        [
            "El método solo tiene que sumar al saldo: no necesita devolver nada para funcionar.",
            "`cantidad` es un parámetro y llega bien; lo que no existe es la variable `saldo` dentro del método.",
            "`saldo += cantidad` usa una variable local que no existe y termina con `UnboundLocalError`.",
        ],
    ),
    "poo-04": (
        "codigo",
        1,
        [
            "Las clases se definen con `class`; `p = Producto()` llama a una clase que ya existe.",
            "Con paréntesis se llama a la clase y se crea un objeto; sin ellos sí sería la propia clase.",
            "Al crear el objeto solo se ejecuta `__init__`; los demás métodos hay que llamarlos.",
        ],
    ),
    "poo-10": (
        "codigo",
        2,
        [
            "`b = a` no copia el objeto: las dos variables apuntan al mismo.",
            "Asignar un objeto a otra variable es válido: solo le da otro nombre.",
            "Solo hay un objeto: se creó una vez y `b` es otro nombre para él.",
        ],
    ),
    "poo-13": (
        "teoria",
        1,
        [
            "Python lo llama solo al hacer `Clase(...)`: llamarlo a mano no hace falta.",
            "`__init__` no devuelve nada; si devolviera algo distinto de `None`, Python daría `TypeError`.",
            "Se ejecuta con cada objeto nuevo, no solo con el primero.",
        ],
    ),
}
