# ruff: noqa: E501
"""Módulo de Programación orientada a objetos (POO): 10 unidades del núcleo por conceptos.

Cada unidad es un concepto de `concepts.py` (área `poo`) con campos opcionales de unidad, que los
demás conceptos no tienen. Así el dominio, los errores típicos, el repaso espaciado y las
recomendaciones del motor adaptativo funcionan igual que en el resto del temario.

- `MODULE`: índice de las 10 unidades (la web lo enseña en `#/poo`). Una unidad aparece como
  disponible cuando existe su concepto.
- `UNITS`: campos de unidad de cada concepto (objetivos, lecciones con ejemplos y mini-quiz,
  ejercicios guiados y autónomos, autoevaluación, resumen, criterios de superación y currículo).
- `EXERCISES`: ejercicios nuevos de las unidades (se añaden a los de `exercises.py`).

La salida de cada ejemplo no se escribe a mano: build_learning.py la obtiene ejecutándolo.
Las correspondencias con el currículo (`curriculum`) son propuestas de la plataforma
(`proposed`) hasta que una persona las valide; nunca se muestran como oficiales.
"""

from exercises import bug as bug_exercise
from exercises import case, choice, code, fill, output

REVIEWED = "2026-11-11"
SOURCE = "rd-405-2023#anexo-I"  # texto oficial ya extraído en frontend/data/curriculum/daw-cyl.json


def proposed(ce: str, note: str) -> dict:
    """Correspondencia propuesta por la plataforma: falta que la valide una persona."""
    return {
        "ce": ce,
        "status": "proposed",
        "source": SOURCE,
        "reviewed": REVIEWED,
        "by": "plataforma",
        "note": note,
    }


MODULE = {
    "id": "poo",
    "title": "Programación orientada a objetos con Python",
    "summary": "De la primera clase a una aplicación completa: objetos, encapsulación, herencia, polimorfismo, composición y diseño.",
    "course": "0485",
    "units": [
        {
            "number": 1,
            "id": "poo-fundamentos",
            "title": "Fundamentos de la programación orientada a objetos",
        },
        {"number": 2, "id": "poo", "title": "Creación de clases y objetos"},
        {"number": 3, "id": "poo-atributos-metodos", "title": "Atributos y métodos"},
        {"number": 4, "id": "poo-encapsulacion", "title": "Encapsulación y propiedades"},
        {"number": 5, "id": "poo-herencia", "title": "Herencia"},
        {"number": 6, "id": "poo-polimorfismo", "title": "Polimorfismo"},
        {"number": 7, "id": "poo-composicion", "title": "Composición y relaciones entre objetos"},
        {"number": 8, "id": "poo-metodos-especiales", "title": "Métodos especiales de Python"},
        {"number": 9, "id": "poo-diseno", "title": "Diseño y buenas prácticas"},
        {"number": 10, "id": "poo-proyecto", "title": "Proyecto final: gestión de una biblioteca"},
    ],
}

# Apartados que debe tener cada unidad (los comprueba build_learning.py)
UNIT_FIELDS = (
    "objectives",
    "prior",
    "key",
    "sections",
    "guided",
    "autonomous",
    "selfcheck",
    "recap",
    "pass",
    "curriculum",
)

UNITS = {
    # ------------------------------------------------------------------ UNIDAD 2
    "poo": {
        "unit": {"module": "poo", "number": 2},
        "objectives": [
            "Definir una clase con `class` y crear varios objetos a partir de ella.",
            "Escribir un constructor `__init__` que dé a cada objeto sus datos iniciales.",
            "Explicar qué es `self` y por qué no se escribe al llamar a un método.",
            "Distinguir el estado (atributos) del comportamiento (métodos) de un objeto.",
            "Predecir qué ocurre al modificar un objeto y sus alias.",
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
        ],
        "guided": ["poo-11"],
        "autonomous": ["poo-03", "poo-12"],
        "selfcheck": ["poo-13", "poo-14"],
        "recap": [
            "Una clase se define con `class Nombre:` y se instancia llamándola: `objeto = Nombre(...)`.",
            "`__init__` se ejecuta solo al crear cada objeto y guarda sus datos con `self.atributo = valor`.",
            "`self` es el propio objeto: es el primer parámetro de los métodos y no se escribe al llamarlos.",
            "Cada objeto tiene su propio estado; los métodos lo leen y lo cambian.",
            "`b = a` no copia un objeto: las dos variables apuntan al mismo.",
        ],
        "pass": {
            "minScore": 0.7,
            "required": ["poo-11", "poo-12"],
            "text": [
                "Resolver el ejercicio guiado (`Alumno`) y el autónomo `Marcador` con todos los tests superados.",
                "Dominar la unidad según el motor: al menos un 70 % de aciertos recientes en sus ejercicios, con varios tipos distintos.",
                "Completar las lecciones ayuda a organizarte, pero **no** demuestra la competencia: la demuestran los ejercicios.",
            ],
        },
        "curriculum": [
            proposed("0485-RA2-h", "Se usan constructores (`__init__`) para inicializar objetos."),
            proposed("0485-RA4-b", "Se definen clases propias con `class`."),
            proposed(
                "0485-RA4-d", "Se escriben constructores con parámetros y valores por defecto."
            ),
            proposed(
                "0485-RA4-e",
                "Se escriben programas que crean y usan varios objetos de las clases definidas.",
            ),
        ],
    },
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
]

# Errores típicos nuevos de la Unidad 2 (se añaden a los del concepto `poo`)
UNIT_ERRORS = {
    "poo": [
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
    ],
}

# Teoría y presentación de la Unidad 2 (sustituyen a las del concepto `poo`; el id no cambia)
UNIT_OVERRIDES = {
    "poo": {
        "title": "Creación de clases y objetos",
        "area": "poo",
        "summary": "Definir clases, crear objetos con `__init__`, usar `self` y trabajar con el estado de varios objetos.",
    },
}
