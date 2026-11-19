# ruff: noqa: E501
"""Unidad 9 del módulo de POO: diseño y buenas prácticas.

Concepto `poo-diseno` (área `poo`): responsabilidad única, cohesión y acoplamiento, composición frente a
herencia e introducción a SOLID, type hints, docstrings y `dataclasses`, y cómo organizar en módulos y
refactorizar. Los módulos se explican con ejemplos comentados, sin importar archivos propios (el
ejecutor del navegador trabaja con un solo archivo). La salida de los ejemplos la obtiene
build_learning.py ejecutándolos.
"""

from exercises import bug, c, case, choice, code, fill, output
from poo_common import practice, proposed, ref

CID = "poo-diseno"

CONCEPT = {
    "id": CID,
    "title": "Diseño y buenas prácticas",
    "area": "poo",
    "requires": ["poo-polimorfismo", "poo-composicion"],
    "daw": 2,
    "ut": "prog-ut6",
    "lessons": ["poo"],
    "summary": "Clases fáciles de entender y de cambiar: una responsabilidad por clase, poco acoplamiento, SOLID, type hints, docstrings y dataclasses.",
    "when": "Cuando un programa crece y cada cambio rompe algo: una función que lo hace todo, clases que dependen de los detalles de otras o datos sueltos en diccionarios.",
    "example": {
        "code": c(
            """
            from dataclasses import dataclass


            @dataclass
            class Producto:
                \"\"\"Un artículo de la tienda: solo sus datos.\"\"\"
                nombre: str
                precio: float


            class Carrito:
                \"\"\"Guarda lo que compra un cliente y calcula su importe.\"\"\"

                def __init__(self) -> None:
                    self.lineas: list[tuple[Producto, int]] = []

                def agregar(self, producto: Producto, cantidad: int = 1) -> None:
                    self.lineas.append((producto, cantidad))

                def total(self) -> float:
                    return sum(p.precio * n for p, n in self.lineas)


            class Ticket:
                \"\"\"Presenta un carrito al cliente: no calcula ni guarda nada.\"\"\"

                def __init__(self, carrito: Carrito) -> None:
                    self.carrito = carrito

                def texto(self) -> str:
                    return f"Total: {self.carrito.total():.2f} €"


            carrito = Carrito()
            carrito.agregar(Producto("Teclado", 25.0), 2)
            print(Ticket(carrito).texto())
            """
        ),
        "lines": [
            [
                4,
                "`@dataclass` escribe `__init__`, `__repr__` y `__eq__` a partir de los atributos.",
            ],
            [7, "Type hints: dicen de qué tipo es cada dato, para quien lee el código."],
            [12, "Cada clase tiene una docstring que dice de qué se ocupa."],
            [25, "`Ticket` solo presenta: si cambia el formato, no se toca el cálculo."],
        ],
    },
    "errors": [],
    "related": ["poo-composicion", "poo-polimorfismo", "funciones"],
}

UNIT = {
    "unit": {"module": "poo", "number": 9},
    "objectives": [
        "Reconocer una clase con demasiadas responsabilidades y repartirlas.",
        "Explicar la cohesión y el acoplamiento y por qué conviene alta cohesión y bajo acoplamiento.",
        "Conocer a nivel introductorio los cinco principios SOLID y aplicar los más sencillos.",
        "Documentar clases con type hints y docstrings, y crear clases de datos con `@dataclass`.",
        "Refactorizar código procedural en clases sin cambiar lo que hace el programa.",
    ],
    "prior": "Las Unidades 1 a 8, en especial el polimorfismo (Unidad 6) y la composición (Unidad 7).",
    "key": [
        [
            "Responsabilidad única",
            "Cada clase se ocupa de una sola cosa y solo tiene un motivo para cambiar.",
        ],
        [
            "Cohesión",
            "Cuánto tienen que ver entre sí los métodos y atributos de una clase. Se busca que sea alta.",
        ],
        [
            "Acoplamiento",
            "Cuánto depende una clase de los detalles de otras. Se busca que sea bajo.",
        ],
        [
            "SOLID",
            "Cinco principios de diseño: responsabilidad única, abierto/cerrado, sustitución de Liskov, segregación de interfaces e inversión de dependencias.",
        ],
        [
            "Type hints",
            "Anotaciones como `precio: float` o `-> str` que documentan los tipos. Python no las comprueba al ejecutar.",
        ],
        [
            "`@dataclass`",
            "Decorador que escribe `__init__`, `__repr__` y `__eq__` de una clase a partir de sus atributos anotados.",
        ],
        [
            "Refactorizar",
            "Cambiar cómo está organizado el código sin cambiar lo que hace.",
        ],
    ],
    "sections": [
        {
            "id": f"{CID}.responsabilidad",
            "title": "Responsabilidad única, cohesión y acoplamiento",
            "theory": "Un programa no se escribe una vez: se lee y se cambia muchas veces. Un buen diseño hace que cada cambio toque **pocas** partes.\n\n**Responsabilidad única.** Cada clase se ocupa de **una sola cosa**. Pregúntate: «¿por qué motivos podría tener que cambiar esta clase?». Si hay varios (el cálculo de precios, el formato del ticket y cómo se guarda en un archivo), son varias responsabilidades y conviene separarlas.\n\n**Cohesión.** Los métodos y atributos de una clase deben tener que ver entre sí. Una clase `Alumno` con `media()` y `enviar_email_al_director()` tiene **baja cohesión**: el email no es cosa del alumno.\n\n**Acoplamiento.** Es cuánto depende una clase de **cómo está hecha por dentro** otra. Si `Ticket` lee `carrito.lineas[i][0].precio`, cualquier cambio en `Carrito` rompe `Ticket`. Si solo llama a `carrito.total()`, el acoplamiento es **bajo**.\n\nLa regla práctica: **alta cohesión y bajo acoplamiento**. Una señal de alarma es una clase o una función enorme que «lo hace todo» y que nadie se atreve a tocar.",
            "examples": [
                {
                    "code": c(
                        """
                        # Antes: una sola función calcula, decide y presenta
                        def informe(notas):
                            media = sum(notas) / len(notas)
                            estado = "aprobado" if media >= 5 else "suspenso"
                            return f"Media {media:.1f}: {estado}"


                        # Después: cada clase tiene una responsabilidad
                        class Calificaciones:
                            def __init__(self, notas):
                                self.notas = list(notas)

                            def media(self):
                                return sum(self.notas) / len(self.notas)

                            def aprobado(self):
                                return self.media() >= 5


                        class Informe:
                            def __init__(self, calificaciones):
                                self.calificaciones = calificaciones

                            def texto(self):
                                c = self.calificaciones
                                estado = "aprobado" if c.aprobado() else "suspenso"
                                return f"Media {c.media():.1f}: {estado}"


                        print(informe([6, 4, 7]))
                        print(Informe(Calificaciones([6, 4, 7])).texto())
                        """
                    ),
                    "lines": [
                        [2, "Una función que hace tres cosas: calcular, decidir y dar formato."],
                        [9, "`Calificaciones` solo se ocupa de los números."],
                        [20, "`Informe` solo presenta; pide los datos, no los calcula."],
                        [
                            31,
                            "El resultado es el mismo: refactorizar no cambia lo que hace el programa.",
                        ],
                    ],
                }
            ],
            "quiz": ["poo9-01", "poo9-02", "poo9-03"],
        },
        {
            "id": f"{CID}.solid",
            "title": "Composición frente a herencia e introducción a SOLID",
            "theory": "En la Unidad 7 viste la regla «es un» → herencia, «tiene un» → composición. **SOLID** reúne cinco principios clásicos del diseño orientado a objetos. Aquí basta con conocerlos y aplicar los más sencillos:\n\n| Letra | Principio | Idea en una frase |\n|---|---|---|\n| **S** | Responsabilidad única | Una clase, un motivo para cambiar. |\n| **O** | Abierto/cerrado | Añade comportamiento con clases nuevas, sin modificar el código que ya funciona (polimorfismo en vez de `if` por tipos). |\n| **L** | Sustitución de Liskov | Un objeto de la subclase debe poder usarse donde se espera uno de la superclase sin sorpresas. |\n| **I** | Segregación de interfaces | No obligues a una clase a tener métodos que no necesita: mejor contratos pequeños. |\n| **D** | Inversión de dependencias | Una clase recibe los objetos de los que depende (por el constructor) en vez de crearlos ella; así se pueden cambiar o simular en las pruebas. |\n\nEl principio de Liskov explica por qué la herencia a veces engaña: un `Cuadrado` «es un» rectángulo en matemáticas, pero si `Rectangulo` deja cambiar el ancho sin el alto, un `Cuadrado` que hereda de él deja de ser cuadrado o se comporta distinto de lo que espera quien usa rectángulos. Cuando una subclase tiene que «romper» lo que promete la superclase, la herencia no es la relación adecuada.",
            "examples": [
                {
                    "code": c(
                        """
                        class AvisoPorEmail:
                            def enviar(self, texto):
                                return f"email: {texto}"


                        class AvisoFalso:                        # para las pruebas: no envía nada
                            def __init__(self):
                                self.enviados = []

                            def enviar(self, texto):
                                self.enviados.append(texto)
                                return "guardado"


                        class Pedido:
                            def __init__(self, numero, aviso):   # D: recibe su dependencia
                                self.numero = numero
                                self.aviso = aviso

                            def confirmar(self):
                                return self.aviso.enviar(f"Pedido {self.numero} confirmado")


                        print(Pedido(1, AvisoPorEmail()).confirmar())
                        falso = AvisoFalso()
                        Pedido(2, falso).confirmar()
                        print(falso.enviados)
                        """
                    ),
                    "lines": [
                        [6, "Otra clase con el mismo método: el pedido no nota la diferencia."],
                        [
                            16,
                            "El pedido no crea su aviso: se lo dan. Es la inversión de dependencias.",
                        ],
                        [21, "Solo usa `enviar`: no depende de cómo se envía."],
                        [
                            25,
                            "En una prueba se le pasa un aviso falso y se comprueba qué habría enviado.",
                        ],
                    ],
                }
            ],
            "quiz": ["poo9-04", "poo9-05", "poo9-06"],
        },
        {
            "id": f"{CID}.tipos-docs",
            "title": "Type hints, docstrings y dataclasses",
            "theory": "Tres herramientas de Python que hacen las clases más fáciles de leer y de usar.\n\n**Type hints.** Anotan el tipo esperado: `def total(self) -> float:` o `nombre: str`. Sirven a quien lee y a herramientas como el editor o `mypy`, pero **Python no las comprueba** al ejecutar: `doble(\"ab\")` funciona aunque diga `x: int`. Algunas formas útiles: `list[str]`, `dict[str, int]`, `str | None`.\n\n**Docstrings.** Un texto entre triples comillas **justo debajo** de `class` o `def` que explica qué hace (no cómo). Python lo guarda en `__doc__` y `help()` lo muestra. Un comentario con `#` no es una docstring.\n\n**`@dataclass`** (módulo `dataclasses`). Para clases que sobre todo guardan datos:\n\n```\nfrom dataclasses import dataclass, field\n\n@dataclass\nclass Libro:\n    titulo: str\n    paginas: int = 0\n    etiquetas: list[str] = field(default_factory=list)\n```\n\n- Escribe por ti `__init__`, `__repr__` (`Libro(titulo='Dune', paginas=0, etiquetas=[])`) y `__eq__` (compara los atributos).\n- Puedes añadir tus propios métodos como en cualquier clase.\n- Un valor por defecto mutable (`= []`) da `ValueError`: usa `field(default_factory=list)`, que crea una lista nueva para cada objeto.\n- `@dataclass(order=True)` añade `<`, `>`… comparando los atributos **en el orden en que están escritos**.",
            "examples": [
                {
                    "code": c(
                        """
                        from dataclasses import dataclass, field


                        @dataclass
                        class Libro:
                            \"\"\"Un libro de la estantería.\"\"\"
                            titulo: str
                            paginas: int = 0
                            etiquetas: list[str] = field(default_factory=list)

                            def es_largo(self) -> bool:
                                return self.paginas > 400


                        dune = Libro("Dune", 600)
                        dune.etiquetas.append("ciencia ficción")
                        print(dune)
                        print(dune == Libro("Dune", 600, ["ciencia ficción"]), dune.es_largo())
                        print(Libro("Otro").etiquetas)
                        print(Libro.__doc__)
                        """
                    ),
                    "lines": [
                        [4, "`@dataclass` genera el constructor, la representación y la igualdad."],
                        [9, "`default_factory=list`: cada libro estrena su propia lista."],
                        [12, "Una dataclass admite métodos propios."],
                        [17, "El `__repr__` generado muestra todos los atributos."],
                        [20, "La docstring queda guardada en `__doc__`."],
                    ],
                }
            ],
            "quiz": ["poo9-07", "poo9-08", "poo9-09"],
        },
        {
            "id": f"{CID}.modulos-refactor",
            "title": "Organización en módulos y refactorización",
            "theory": '**Módulos.** En un proyecto real cada grupo de clases va en su archivo y se importa: `modelo.py` con `Producto` e `Inventario`, `ventas.py` con `Carrito` y `Ticket`, y `main.py`, que solo pone el programa en marcha (`from modelo import Producto`). Un **paquete** es una carpeta de módulos. Agrupa lo que cambia junto y evita importaciones en círculo (A importa B y B importa A). En esta web todo se ejecuta en **un solo archivo**, así que verás la separación marcada con comentarios.\n\n**Refactorizar** es cambiar la organización del código **sin cambiar lo que hace**. Pasos seguros:\n\n1. Ten antes **pruebas** que comprueben el comportamiento (aunque sean unos `assert`).\n2. Cambia **poco cada vez**: extrae una función, pon un nombre claro, mueve un dato a una clase.\n3. Ejecuta las pruebas después de cada paso. Si fallan, sabes qué paso lo rompió.\n\nSeñales de que toca refactorizar: código repetido, funciones muy largas, cadenas de `if` por tipos, diccionarios que viajan por todo el programa con claves «mágicas» (`p["precio"]`) y nombres como `datos2` o `aux`.',
            "examples": [
                {
                    "code": c(
                        """
                        # ---- modelo.py ----------------------------------------
                        class Producto:
                            def __init__(self, nombre, precio):
                                self.nombre = nombre
                                self.precio = precio


                        # ---- ventas.py (haría: from modelo import Producto) ----
                        class Carrito:
                            def __init__(self):
                                self.lineas = []

                            def agregar(self, producto, cantidad):
                                self.lineas.append((producto, cantidad))

                            def total(self):
                                return sum(p.precio * n for p, n in self.lineas)


                        # ---- main.py: solo pone el programa en marcha ----------
                        def main():
                            carrito = Carrito()
                            carrito.agregar(Producto("Pan", 1.5), 2)
                            assert carrito.total() == 3.0      # prueba: el comportamiento no cambia
                            print(f"Total: {carrito.total():.2f} €")


                        main()
                        """
                    ),
                    "lines": [
                        [1, "En un proyecto real, esto sería el archivo `modelo.py`."],
                        [8, "`ventas.py` importaría `Producto` del módulo `modelo`."],
                        [21, "`main` solo coordina: crea los objetos y los usa."],
                        [24, "Un `assert` protege el comportamiento mientras refactorizas."],
                    ],
                }
            ],
            "quiz": ["poo9-10", "poo9-11", "poo9-12"],
        },
    ],
    "guided": ["poo9-14"],
    "autonomous": ["poo9-27"],
    "extras": ["poo9-15", "poo9-25"],
    "selfcheck": ["poo9-13", "poo9-26"],
    "recap": [
        "Una clase, una responsabilidad: si tiene varios motivos para cambiar, sepárala.",
        "Alta cohesión (todo lo de la clase tiene que ver) y bajo acoplamiento (pide a los demás, no mires sus tripas).",
        "SOLID: responsabilidad única, abierto/cerrado, Liskov, segregación de interfaces e inversión de dependencias.",
        "Los type hints documentan tipos, pero Python no los comprueba al ejecutar.",
        "Las docstrings explican qué hace una clase o función y quedan en `__doc__`.",
        "`@dataclass` genera `__init__`, `__repr__` y `__eq__`; para listas, `field(default_factory=list)`.",
        "Refactoriza con pruebas y en pasos pequeños: el comportamiento no debe cambiar.",
    ],
    "pass": {
        "minScore": 0.7,
        "required": ["poo9-14", "poo9-27"],
        "text": [
            "Resolver el ejercicio guiado (boletín de notas) y el ejercicio principal (refactorizar la tienda) con todos los tests superados.",
            "Al menos un 70 % en el cuestionario de la unidad y dominar la unidad según el motor, con varios tipos de ejercicio distintos.",
            "Completar las lecciones ayuda a organizarte, pero **no** demuestra la competencia: la demuestran los ejercicios.",
        ],
    },
    "practices": [
        practice(
            "Antes de añadir un método, pregúntate si es responsabilidad de esa clase.",
            "Si no lo es, acabarás con una clase que hay que tocar por motivos que no tienen nada que ver.",
        ),
        practice(
            "Pide resultados a los objetos (`carrito.total()`) en vez de leer sus atributos internos.",
            "Así puedes cambiar cómo está hecha una clase sin romper las que la usan.",
        ),
        practice(
            "Pasa por el constructor los objetos de los que depende una clase.",
            "Puedes cambiarlos sin tocar la clase y usar objetos falsos en las pruebas.",
        ),
        practice(
            "Pon type hints y una docstring corta en las clases y métodos públicos.",
            "Quien use tu clase sabe qué pasarle y qué devuelve sin leer todo el código.",
        ),
        practice(
            "Usa `@dataclass` para las clases que sobre todo guardan datos.",
            "Te ahorra escribir a mano `__init__`, `__repr__` y `__eq__`, que es donde más fallos se cometen.",
        ),
        practice(
            "Refactoriza en pasos pequeños y ejecuta las pruebas después de cada uno.",
            "Si algo se rompe, sabes exactamente qué cambio lo ha causado.",
        ),
    ],
    "references": [
        ref(
            "py-dataclasses",
            "Contenido del módulo: el decorador dataclass, sus parámetros (order) y field con default_factory",
            [
                "`@dataclass` genera `__init__`, `__repr__` y `__eq__`",
                "valores por defecto mutables y `default_factory`",
                "`order=True` compara los campos en orden",
            ],
        ),
        ref(
            "py-tutorial-classes",
            "9.7. Cajón de sastre",
            ["clases sencillas para agrupar datos con nombre (como un registro)"],
        ),
        ref(
            "py-faq-programming",
            "Objetos: ¿Qué es la delegación?",
            ["pasar trabajo a otro objeto en vez de heredar de él"],
        ),
    ],
    "bank": [
        "poo9-01",
        "poo9-03",
        "poo9-04",
        "poo9-08",
        "poo9-10",
        "poo9-13",
        "poo9-16",
        "poo9-17",
        "poo9-18",
        "poo9-19",
        "poo9-20",
        "poo9-21",
        "poo9-22",
        "poo9-23",
        "poo9-24",
    ],
    "curriculum": [
        proposed(
            "0485-RA3-g",
            "Se documenta el código con docstrings y type hints.",
        ),
        proposed(
            "0485-RA7-h",
            "Se comentan y documentan las clases de una jerarquía y sus métodos.",
        ),
        proposed(
            "0485-RA4-i",
            "Se organizan las clases en módulos que forman una librería propia (presentado con ejemplos comentados).",
        ),
    ],
}

EXERCISES = [
    # ---------- Lección «Responsabilidad única, cohesión y acoplamiento»
    choice(
        "poo9-01",
        CID,
        "¿Qué dice el principio de responsabilidad única?",
        [
            ("Que cada clase se ocupe de una sola cosa y tenga un solo motivo para cambiar", None),
            (
                "Que cada clase tenga un solo método",
                f"{CID}.responsabilidad-es-un-metodo",
                "Una responsabilidad puede necesitar varios métodos: `media()` y `aprobado()` son de la misma.",
            ),
            (
                "Que solo una persona del equipo pueda modificar cada clase",
                None,
                "Habla del diseño del código, no de quién lo escribe.",
            ),
            (
                "Que un programa tenga una sola clase",
                None,
                "Al revés: suele llevar a más clases, cada una con su tarea.",
            ),
        ],
        0,
        "Si una clase cambia por motivos distintos (el cálculo, el formato, cómo se guarda), tiene varias responsabilidades y conviene separarlas.",
        level=1,
        daw=False,
        bank=True,
        qtype="teoria",
    ),
    output(
        "poo9-02",
        CID,
        """
        class Calificaciones:
            def __init__(self, notas):
                self.notas = notas

            def media(self):
                return sum(self.notas) / len(self.notas)

        class Informe:
            def __init__(self, calificaciones):
                self.calificaciones = calificaciones

            def texto(self):
                return f"Media: {self.calificaciones.media():.1f}"

        c = Calificaciones([8, 6])
        c.notas.append(10)
        print(Informe(c).texto())
        """,
        "Media: 8.0",
        "`Informe` no guarda una copia de la media: se la pide a `Calificaciones` cuando la necesita. Con la nota nueva, (8 + 6 + 10) / 3 = 8.0.",
        traps={"Media: 7.0": f"{CID}.copia-de-datos", "Media: 8": None},
        level=1,
        daw=False,
    ),
    choice(
        "poo9-03",
        CID,
        "¿Qué clase tiene **baja cohesión**?",
        [
            (
                "`Alumno` con `media()`, `aprobado()`, `imprimir_factura_de_la_cafeteria()` y `reservar_aula()`",
                None,
            ),
            (
                "`Alumno` con `media()` y `aprobado()`",
                None,
                "Los dos métodos trabajan con las notas del alumno: tienen que ver entre sí.",
            ),
            (
                "`Termometro` con `celsius` y `a_fahrenheit()`",
                None,
                "La conversión usa el dato de la propia clase: es cohesiva.",
            ),
            (
                "`Carrito` con `agregar()`, `quitar()` y `total()`",
                None,
                "Todo trata de los productos del carrito.",
            ),
        ],
        0,
        "Facturas de la cafetería y reservas de aulas no tienen nada que ver con las notas: esa clase mezcla responsabilidades.",
        level=1,
        daw=False,
        bank=True,
        qtype="diseno",
    ),
    # ---------- Lección «SOLID»
    choice(
        "poo9-04",
        CID,
        "¿Qué pide el principio **abierto/cerrado** (la O de SOLID)?",
        [
            (
                "Poder añadir comportamiento con clases nuevas sin modificar el código que ya funciona",
                None,
            ),
            (
                "Que todos los atributos sean públicos (abiertos) y los métodos privados (cerrados)",
                None,
                "No trata de la visibilidad de los miembros, sino de cómo crece el programa.",
            ),
            (
                "Añadir un `elif` a la función cada vez que aparece un tipo nuevo",
                f"{CID}.if-por-tipos",
                "Eso obliga a modificar código que ya funcionaba: es lo que el principio quiere evitar.",
            ),
            (
                "Cerrar los archivos después de abrirlos",
                None,
                "El nombre se parece, pero el principio habla del diseño de clases.",
            ),
        ],
        0,
        "Con polimorfismo, un tipo nuevo es una clase nueva con su método: el código que recorre los objetos no se toca.",
        level=2,
        daw=False,
        bank=True,
        qtype="teoria",
    ),
    output(
        "poo9-05",
        CID,
        """
        class Rectangulo:
            def __init__(self, ancho, alto):
                self.ancho = ancho
                self.alto = alto

            def area(self):
                return self.ancho * self.alto

        class Cuadrado(Rectangulo):
            def __init__(self, lado):
                super().__init__(lado, lado)

        def estirar(figura):
            figura.ancho = figura.ancho * 2
            return figura.area()

        print(estirar(Rectangulo(2, 3)), estirar(Cuadrado(2)))
        """,
        "12 8",
        "`estirar` duplica el ancho de cualquier rectángulo. El cuadrado acaba con ancho 4 y alto 2: ya no es un cuadrado. Es el problema que señala el principio de sustitución de Liskov.",
        traps={"12 16": f"{CID}.herencia-que-rompe", "12 4": None},
        level=2,
        daw=False,
    ),
    fill(
        "poo9-06",
        CID,
        "Completa el constructor para que el pedido **reciba** su aviso (inversión de dependencias) en vez de crearlo.",
        """
        class AvisoFalso:
            def enviar(self, texto):
                return "simulado: " + texto

        class Pedido:
            def __init__(self, numero, aviso):
                self.numero = numero
                self.aviso = ___

            def confirmar(self):
                return self.aviso.enviar(f"pedido {self.numero}")

        print(Pedido(3, AvisoFalso()).confirmar())
        """,
        ["aviso"],
        "Guardar el parámetro (`self.aviso = aviso`) permite pasarle cualquier objeto con `enviar`, también uno falso para las pruebas.",
        expect="simulado: pedido 3",
        traps={
            "AvisoFalso()": f"{CID}.crea-su-dependencia",
            "AvisoPorEmail()": f"{CID}.crea-su-dependencia",
        },
        level=2,
        daw=False,
    ),
    # ---------- Lección «Type hints, docstrings y dataclasses»
    output(
        "poo9-07",
        CID,
        """
        def doble(x: int) -> int:
            return x * 2

        print(doble("ab"))
        """,
        "abab",
        'Los type hints no se comprueban al ejecutar: `"ab" * 2` es `"abab"`. Sirven para documentar y para herramientas como `mypy`.',
        traps={"TypeError": f"{CID}.hints-obligan", "4": None},
        level=1,
        daw=False,
    ),
    choice(
        "poo9-08",
        CID,
        "¿Qué métodos escribe por ti `@dataclass` en una clase con atributos anotados?",
        [
            ("`__init__`, `__repr__` y `__eq__`", None),
            (
                "Solo `__init__`",
                None,
                "También genera `__repr__` y `__eq__`.",
            ),
            (
                "`__str__` y `__len__`",
                None,
                "No genera `__len__`, y `print` usa el `__repr__` generado porque no hay `__str__`.",
            ),
            (
                "Ninguno: solo comprueba los tipos de los atributos",
                f"{CID}.hints-obligan",
                "`@dataclass` no comprueba tipos; escribe métodos a partir de los atributos.",
            ),
        ],
        0,
        "`@dataclass` lee los atributos anotados y genera el constructor, la representación (`Libro(titulo='Dune', paginas=600)`) y la comparación con `==`.",
        level=1,
        daw=False,
        bank=True,
        qtype="codigo",
    ),
    bug(
        "poo9-09",
        CID,
        "Python da `ValueError: mutable default <class 'list'> for field etiquetas is not allowed`. ¿Qué línea hay que cambiar?",
        """
        from dataclasses import dataclass, field

        @dataclass
        class Libro:
            titulo: str
            etiquetas: list = []

        a = Libro("Dune")
        a.etiquetas.append("sf")
        print(Libro("Otro").etiquetas)
        """,
        6,
        "    etiquetas: list = field(default_factory=list)",
        "[]",
        f"{CID}.dataclass-lista-por-defecto",
        "Una lista como valor por defecto la compartirían todos los libros, y `@dataclass` lo prohíbe. `field(default_factory=list)` crea una lista nueva para cada objeto.",
        level=2,
        daw=False,
    ),
    # ---------- Lección «Organización en módulos y refactorización»
    choice(
        "poo9-10",
        CID,
        "`Pinguino` hereda de `Ave`, que tiene `volar()`. Como los pingüinos no vuelan, `Pinguino.volar()` lanza un error. ¿Qué dice esto del diseño?",
        [
            (
                "Que se rompe la sustitución de Liskov: un pingüino no se puede usar donde se espera un `Ave` que vuela",
                None,
            ),
            (
                "Nada: sobrescribir un método para que lance un error es la forma correcta",
                f"{CID}.herencia-que-rompe",
                "El código que recorre aves y llama a `volar()` fallaría por sorpresa con un pingüino.",
            ),
            (
                "Que `Ave` debería heredar de `Pinguino`",
                None,
                "Invertir la jerarquía no tiene sentido: no todas las aves son pingüinos.",
            ),
            (
                "Que hay que añadir un `if isinstance(ave, Pinguino)` en cada sitio donde se llama a `volar()`",
                f"{CID}.if-por-tipos",
                "Llenaría el programa de comprobaciones de tipo: es justo lo que se quiere evitar.",
            ),
        ],
        0,
        "Si una subclase no puede cumplir lo que promete la superclase, la jerarquía está mal: por ejemplo, saca `volar()` a una clase `AveVoladora` solo para las que vuelan.",
        level=2,
        daw=False,
        bank=True,
        qtype="diseno",
    ),
    output(
        "poo9-11",
        CID,
        """
        # Antes
        def total(lineas):
            t = 0
            for precio, cantidad in lineas:
                t += precio * cantidad
            return t

        # Después de refactorizar
        class Linea:
            def __init__(self, precio, cantidad):
                self.precio = precio
                self.cantidad = cantidad

            def subtotal(self):
                return self.precio * self.cantidad

        datos = [(2, 3), (5, 1)]
        nuevo = sum(Linea(p, n).subtotal() for p, n in datos)
        print(total(datos) == nuevo, nuevo)
        """,
        "True 11",
        "Refactorizar cambia la organización, no el resultado: los dos cálculos dan 2 × 3 + 5 × 1 = 11.",
        traps={"False 11": None, "True 6": None},
        level=1,
        daw=False,
    ),
    choice(
        "poo9-12",
        CID,
        "Vas a refactorizar una función larga que funciona. ¿Qué haces **primero**?",
        [
            ("Escribir pruebas que comprueben lo que hace ahora", None),
            ("Reescribirla entera de una vez con clases", None),
            ("Cambiar todos los nombres de variables", None),
            ("Borrar los comentarios", None),
        ],
        0,
        "Sin pruebas no sabes si el código refactorizado sigue haciendo lo mismo. Con ellas, cada paso pequeño se comprueba al momento.",
        level=1,
        daw=False,
    ),
    # ---------- Autoevaluación
    choice(
        "poo9-13",
        CID,
        "`procesar_venta()` comprueba el stock, calcula el total con IVA, imprime el ticket y guarda la venta en un archivo. ¿Cuál es la mejor reorganización?",
        [
            (
                "Repartirlo: el inventario comprueba el stock, el carrito calcula, el ticket presenta y otra clase guarda",
                None,
            ),
            (
                "Dejarla igual pero con más comentarios",
                None,
                "Los comentarios ayudan a leer, pero la función sigue teniendo cuatro motivos para cambiar.",
            ),
            (
                "Convertirla en un método de una clase `Tienda` sin cambiar nada más",
                f"{CID}.clase-que-lo-hace-todo",
                "Seguiría haciendo cuatro cosas: solo cambia de sitio.",
            ),
            (
                "Partirla en cuatro funciones que se llaman `paso1()`, `paso2()`, `paso3()` y `paso4()`",
                None,
                "Separa, pero los nombres no dicen nada y el reparto no sigue las responsabilidades.",
            ),
        ],
        0,
        "Cada parte tiene su motivo para cambiar (el stock, el IVA, el formato, el almacenamiento): cada una va a la clase que se ocupa de ello.",
        level=2,
        daw=False,
        bank=True,
        qtype="solucion",
    ),
    # ---------- Ejercicio guiado
    code(
        "poo9-14",
        CID,
        '**Ejercicio guiado: boletín de notas.** La función `boletin(nombre, notas)` calcula, decide y presenta a la vez. Repártelo en dos clases:\n\n1. `Calificaciones(notas)`: guarda una **copia** de la lista y tiene `media()` (0 si no hay notas) y `aprobado()` (media ≥ 5).\n2. `Boletin(nombre, calificaciones)`: recibe un objeto `Calificaciones` y tiene `texto()`, que devuelve lo mismo que la función: `"Ana: 6.5 (aprobado)"`.\n3. Pon una docstring en cada clase. La función antigua se queda para comparar.',
        """
        def boletin(nombre, notas):
            media = sum(notas) / len(notas) if notas else 0
            estado = "aprobado" if media >= 5 else "suspenso"
            return f"{nombre}: {media:.1f} ({estado})"


        # Paso 1: Calificaciones

        # Paso 2: Boletin

        # Paso 3: docstrings


        print(boletin("Ana", [6, 7]))
        print(Boletin("Ana", Calificaciones([6, 7])).texto())
        """,
        """
        def boletin(nombre, notas):
            media = sum(notas) / len(notas) if notas else 0
            estado = "aprobado" if media >= 5 else "suspenso"
            return f"{nombre}: {media:.1f} ({estado})"


        class Calificaciones:
            \"\"\"Las notas de un alumno y los cálculos con ellas.\"\"\"

            def __init__(self, notas: list[float]) -> None:
                self.notas = list(notas)

            def media(self) -> float:
                return sum(self.notas) / len(self.notas) if self.notas else 0

            def aprobado(self) -> bool:
                return self.media() >= 5


        class Boletin:
            \"\"\"Presenta las calificaciones de un alumno.\"\"\"

            def __init__(self, nombre: str, calificaciones: Calificaciones) -> None:
                self.nombre = nombre
                self.calificaciones = calificaciones

            def texto(self) -> str:
                estado = "aprobado" if self.calificaciones.aprobado() else "suspenso"
                return f"{self.nombre}: {self.calificaciones.media():.1f} ({estado})"


        print(boletin("Ana", [6, 7]))
        print(Boletin("Ana", Calificaciones([6, 7])).texto())
        """,
        [
            case(
                'c = Calificaciones([6, 7])\nassert c.media() == 6.5, f"media() debe dar 6.5; da {c.media()!r}"\nassert c.aprobado() is True and Calificaciones([3, 4]).aprobado() is False, "aprobado() es media >= 5"\nassert Calificaciones([]).media() == 0, "Sin notas, la media es 0"\nmis = [5]\nc = Calificaciones(mis)\nmis.append(0)\nassert c.notas == [5], "Calificaciones debe guardar una copia de la lista"',
            ),
            case(
                'for nombre, notas in (("Ana", [6, 7]), ("Luis", [2, 4]), ("Eva", [])):\n    nuevo = Boletin(nombre, Calificaciones(notas)).texto()\n    assert nuevo == boletin(nombre, notas), f"Boletin debe dar lo mismo que la función: {nuevo!r} frente a {boletin(nombre, notas)!r}"',
            ),
            case(
                'class Fijas:\n    def media(self):\n        return 9.0\n    def aprobado(self):\n        return True\nassert Boletin("Zoe", Fijas()).texto() == "Zoe: 9.0 (aprobado)", "Boletin debe pedir media() y aprobado() al objeto que recibe, sin calcular por su cuenta"\nassert Calificaciones.__doc__ and Boletin.__doc__, "Pon una docstring en cada clase"',
                error=f"{CID}.acoplado-a-detalles",
            ),
        ],
        "`Calificaciones` hace los cálculos y `Boletin` solo presenta. Como `Boletin` pide los resultados en vez de leer `notas`, funciona con cualquier objeto que tenga `media()` y `aprobado()`: bajo acoplamiento.",
        "En `Boletin.texto()` usa `self.calificaciones.media()` y `self.calificaciones.aprobado()`, no `self.calificaciones.notas`.",
        wrong=[
            (
                """
                def boletin(nombre, notas):
                    media = sum(notas) / len(notas) if notas else 0
                    estado = "aprobado" if media >= 5 else "suspenso"
                    return f"{nombre}: {media:.1f} ({estado})"


                class Calificaciones:
                    \"\"\"Notas.\"\"\"

                    def __init__(self, notas):
                        self.notas = notas

                    def media(self):
                        return sum(self.notas) / len(self.notas) if self.notas else 0

                    def aprobado(self):
                        return self.media() >= 5


                class Boletin:
                    \"\"\"Boletín.\"\"\"

                    def __init__(self, nombre, calificaciones):
                        self.nombre = nombre
                        self.calificaciones = calificaciones

                    def texto(self):
                        estado = "aprobado" if self.calificaciones.aprobado() else "suspenso"
                        return f"{self.nombre}: {self.calificaciones.media():.1f} ({estado})"
                """,
                1,
            ),
            (
                """
                def boletin(nombre, notas):
                    media = sum(notas) / len(notas) if notas else 0
                    estado = "aprobado" if media >= 5 else "suspenso"
                    return f"{nombre}: {media:.1f} ({estado})"


                class Calificaciones:
                    \"\"\"Notas.\"\"\"

                    def __init__(self, notas):
                        self.notas = list(notas)

                    def media(self):
                        return sum(self.notas) / len(self.notas) if self.notas else 0

                    def aprobado(self):
                        return self.media() >= 5


                class Boletin:
                    \"\"\"Boletín.\"\"\"

                    def __init__(self, nombre, calificaciones):
                        self.nombre = nombre
                        self.calificaciones = calificaciones

                    def texto(self):
                        return boletin(self.nombre, self.calificaciones.notas)
                """,
                3,
            ),
        ],
        level=2,
        daw=False,
    ),
    # ---------- Prácticas adicionales
    code(
        "poo9-15",
        CID,
        "**Práctica: una dataclass.** Crea con `@dataclass` la clase `Tarea` con `titulo: str`, `horas: float = 1.0`, `hecha: bool = False` y `etiquetas: list[str]` (lista nueva para cada tarea). Añade:\n\n- `marcar()`, que pone `hecha` a `True`.\n- `es_larga()`, que devuelve si dura más de 4 horas.\n\nY una función `pendientes(tareas)` que devuelva los títulos de las tareas no hechas, en el mismo orden.",
        """
        from dataclasses import dataclass, field


        class Tarea:
            ...
        """,
        """
        from dataclasses import dataclass, field


        @dataclass
        class Tarea:
            \"\"\"Una tarea de la lista de pendientes.\"\"\"
            titulo: str
            horas: float = 1.0
            hecha: bool = False
            etiquetas: list[str] = field(default_factory=list)

            def marcar(self) -> None:
                self.hecha = True

            def es_larga(self) -> bool:
                return self.horas > 4


        def pendientes(tareas: list[Tarea]) -> list[str]:
            return [t.titulo for t in tareas if not t.hecha]


        lista = [Tarea("Práctica 1", 3), Tarea("Proyecto", 10)]
        lista[0].marcar()
        print(lista[1], pendientes(lista))
        """,
        [
            case(
                'import dataclasses\nassert dataclasses.is_dataclass(Tarea), "Tarea debe llevar @dataclass"\nt = Tarea("Leer")\nassert (t.horas, t.hecha, t.etiquetas) == (1.0, False, []), "Valores por defecto: horas 1.0, hecha False y etiquetas vacía"\nassert Tarea("A", 2) == Tarea("A", 2), "Dos tareas con los mismos datos son iguales (__eq__ generado)"\nassert repr(Tarea("A", 2)) == "Tarea(titulo=\'A\', horas=2, hecha=False, etiquetas=[])", f"repr generado: {Tarea(\'A\', 2)!r}"',
            ),
            case(
                'a, b = Tarea("A"), Tarea("B")\na.etiquetas.append("dam")\nassert b.etiquetas == [], "Cada tarea debe tener su propia lista: field(default_factory=list)"',
                error=f"{CID}.dataclass-lista-por-defecto",
            ),
            case(
                't = Tarea("A", 5)\nassert t.es_larga() and not Tarea("B", 4).es_larga(), "es_larga() es más de 4 horas"\nt.marcar()\nassert t.hecha, "marcar() pone hecha a True"\nlista = [Tarea("x"), t, Tarea("y")]\nassert pendientes(lista) == ["x", "y"], f"pendientes() devuelve {pendientes(lista)!r}"',
            ),
        ],
        "`@dataclass` escribe el constructor, el `repr` y la igualdad; tú solo añades lo que es propio de una tarea. `field(default_factory=list)` evita que todas las tareas compartan la misma lista de etiquetas.",
        "Las anotaciones van como `titulo: str` dentro de la clase. Para la lista: `etiquetas: list[str] = field(default_factory=list)`.",
        wrong=[
            (
                """
                from dataclasses import dataclass, field


                class Tarea:
                    def __init__(self, titulo, horas=1.0, hecha=False, etiquetas=None):
                        self.titulo = titulo
                        self.horas = horas
                        self.hecha = hecha
                        self.etiquetas = etiquetas or []

                    def marcar(self):
                        self.hecha = True

                    def es_larga(self):
                        return self.horas > 4


                def pendientes(tareas):
                    return [t.titulo for t in tareas if not t.hecha]
                """,
                1,
            ),
            (
                """
                from dataclasses import dataclass, field


                @dataclass
                class Tarea:
                    titulo: str
                    horas: float = 1.0
                    hecha: bool = False
                    etiquetas: list[str] = field(default_factory=list)

                    def marcar(self):
                        self.hecha = True

                    def es_larga(self):
                        return self.horas >= 4


                def pendientes(tareas):
                    return [t.titulo for t in tareas if not t.hecha]
                """,
                3,
            ),
        ],
        level=2,
        daw=False,
    ),
    # ---------- Banco de preguntas de la unidad (cuestionario)
    choice(
        "poo9-16",
        CID,
        "¿Qué es una docstring?",
        [
            (
                "Un texto entre triples comillas justo debajo de `class` o `def` que explica qué hace; Python lo guarda en `__doc__`",
                None,
            ),
            (
                "Cualquier comentario que empieza por `#`",
                None,
                "Los comentarios con `#` los ignora Python; la docstring es una cadena que queda en `__doc__`.",
            ),
            (
                "Un type hint que indica que el resultado es un `str`",
                f"{CID}.hints-obligan",
                "Eso sería `-> str`, una anotación de tipo, no una docstring.",
            ),
            (
                "Un método especial que convierte el objeto en texto",
                None,
                "Ese es `__str__` (Unidad 8).",
            ),
        ],
        0,
        "La docstring documenta el **qué**; `help(Clase)` la muestra. Un comentario `#` explica detalles del código y no se guarda.",
        level=1,
        daw=False,
        bank=True,
        qtype="teoria",
    ),
    choice(
        "poo9-17",
        CID,
        "¿Qué indica `def buscar(self, nombre: str) -> Producto | None:`?",
        [
            ("Que recibe un texto y devuelve un `Producto` o `None` si no lo encuentra", None),
            (
                "Que Python lanzará `TypeError` si `nombre` no es un `str`",
                f"{CID}.hints-obligan",
                "Los type hints no se comprueban al ejecutar; solo documentan.",
            ),
            (
                "Que devuelve a la vez un `Producto` y `None`",
                None,
                "`|` significa «o»: devuelve una cosa u otra.",
            ),
            (
                "Que `nombre` es opcional y vale `None` por defecto",
                None,
                "El `None` está en el tipo de lo que devuelve, no en el parámetro; `nombre` no tiene valor por defecto.",
            ),
        ],
        0,
        "`nombre: str` anota el parámetro y `-> Producto | None` lo que devuelve. Quien lo use sabe que debe comprobar si recibe `None`.",
        level=2,
        daw=False,
        bank=True,
        qtype="codigo",
    ),
    choice(
        "poo9-18",
        CID,
        "En una dataclass, ¿qué diferencia hay entre `etiquetas: list = field(default_factory=list)` y escribir en `__init__` `self.etiquetas = []`?",
        [
            ("Ninguna en el resultado: las dos crean una lista nueva para cada objeto", None),
            (
                "`default_factory` crea una sola lista que comparten todos los objetos",
                f"{CID}.dataclass-lista-por-defecto",
                "Es al revés: llama a `list()` cada vez que se crea un objeto.",
            ),
            (
                "Con `default_factory` la lista no se puede modificar",
                None,
                "Es una lista normal: se puede añadir y quitar.",
            ),
            (
                "`self.etiquetas = []` en `__init__` también comparte la lista entre objetos",
                None,
                "Esa línea se ejecuta en cada `__init__`, así que cada objeto estrena su lista.",
            ),
        ],
        0,
        "`default_factory=list` es la forma de pedirle a `@dataclass` lo mismo que harías en un `__init__` escrito a mano: una lista nueva por objeto.",
        level=3,
        daw=False,
        bank=True,
        qtype="codigo",
    ),
    choice(
        "poo9-19",
        CID,
        "¿Qué muestra este programa?",
        [
            ("Punto(x=1, y=2)", None),
            (
                "<__main__.Punto object>",
                None,
                "`@dataclass` genera un `__repr__` que muestra los atributos.",
            ),
            (
                "(1, 2)",
                None,
                "El `__repr__` generado incluye el nombre de la clase y de cada atributo.",
            ),
            (
                "Punto(1, 2)",
                None,
                "El `__repr__` generado pone el nombre de cada atributo: `x=1`.",
            ),
        ],
        0,
        "El `__repr__` que escribe `@dataclass` muestra la clase y cada atributo con su nombre y su valor.",
        code="""
        from dataclasses import dataclass

        @dataclass
        class Punto:
            x: int
            y: int

        print(Punto(1, 2))
        """,
        level=1,
        daw=False,
        bank=True,
        qtype="prediccion",
    ),
    choice(
        "poo9-20",
        CID,
        "¿Qué muestra este programa?",
        [
            ("True False", None),
            (
                "False False",
                None,
                "`@dataclass` genera `__eq__`, que compara los atributos: los dos libros tienen los mismos.",
            ),
            (
                "True True",
                None,
                "Son dos objetos distintos con los mismos datos: `is` da `False`.",
            ),
            (
                "False True",
                None,
                "`is` solo es `True` si es el mismo objeto, y aquí se crean dos.",
            ),
        ],
        0,
        "`==` usa el `__eq__` generado y compara `titulo` y `paginas`. `is` mira si son el mismo objeto, y no lo son.",
        code="""
        from dataclasses import dataclass

        @dataclass
        class Libro:
            titulo: str
            paginas: int

        a = Libro("Dune", 600)
        b = Libro("Dune", 600)
        print(a == b, a is b)
        """,
        level=2,
        daw=False,
        bank=True,
        qtype="prediccion",
    ),
    choice(
        "poo9-21",
        CID,
        "¿Qué muestra este programa?",
        [
            ("['Luis', 'Ana', 'Eva']", None),
            (
                "['Eva', 'Luis', 'Ana']",
                None,
                "`sorted` ordena: no deja la lista en el orden en que se escribió.",
            ),
            (
                "['Ana', 'Eva', 'Luis']",
                None,
                "`order=True` compara primero `valor` (el primer atributo), no el nombre.",
            ),
            (
                "['Luis', 'Eva', 'Ana']",
                None,
                "Con el mismo `valor`, se compara el siguiente atributo, `alumno`: «Ana» va antes que «Eva».",
            ),
        ],
        0,
        "`order=True` compara los atributos en el orden en que están escritos: primero `valor` (5 antes que 7) y, si empatan, `alumno` (Ana antes que Eva).",
        code="""
        from dataclasses import dataclass

        @dataclass(order=True)
        class Nota:
            valor: int
            alumno: str

        notas = [Nota(7, "Eva"), Nota(5, "Luis"), Nota(7, "Ana")]
        print([n.alumno for n in sorted(notas)])
        """,
        level=3,
        daw=False,
        bank=True,
        qtype="prediccion",
    ),
    choice(
        "poo9-22",
        CID,
        "¿Cuál es el problema de diseño de esta clase?",
        [
            (
                "Mezcla responsabilidades: cálculo, formato y guardado en un archivo tienen motivos distintos para cambiar",
                None,
            ),
            (
                "Tiene demasiados atributos",
                None,
                "Solo tiene uno; el problema está en lo que hacen sus métodos.",
            ),
            (
                "Le faltan type hints",
                None,
                "Los type hints ayudarían a leerla, pero el problema de diseño seguiría ahí.",
            ),
            (
                "Debería heredar de `list` para guardar las notas",
                f"{CID}.herencia-que-rompe",
                "Un expediente no es una lista; además, eso no arregla la mezcla de tareas.",
            ),
        ],
        0,
        "Si cambia el formato del informe o el archivo donde se guarda, hay que tocar la clase de las notas. Lo propio es separar: `Expediente` calcula, `Informe` presenta y otra clase guarda.",
        code="""
        class Expediente:
            def __init__(self, notas):
                self.notas = notas

            def media(self):
                return sum(self.notas) / len(self.notas)

            def informe_html(self):
                return f"<p>Media: {self.media():.1f}</p>"

            def guardar(self, ruta):
                with open(ruta, "w") as f:
                    f.write(self.informe_html())
        """,
        level=2,
        daw=False,
        bank=True,
        qtype="error",
    ),
    choice(
        "poo9-23",
        CID,
        "Al ejecutar este código Python da `ValueError` antes de crear ningún objeto. ¿Por qué?",
        [
            (
                "`@dataclass` no admite una lista como valor por defecto: hay que usar `field(default_factory=list)`",
                None,
            ),
            (
                "Falta escribir el `__init__`",
                None,
                "Con `@dataclass` no hace falta: lo genera el decorador.",
            ),
            (
                "Los type hints `list` y `str` no se pueden mezclar",
                None,
                "Cada atributo puede tener su propio tipo.",
            ),
            (
                "Hay que poner `alumnos` antes que `nombre`",
                None,
                "El orden es correcto: el atributo con valor por defecto va después del que no lo tiene.",
            ),
        ],
        0,
        "Una lista por defecto la compartirían todos los objetos, así que `@dataclass` la rechaza al definir la clase. `field(default_factory=list)` crea una por objeto.",
        code="""
        from dataclasses import dataclass

        @dataclass
        class Grupo:
            nombre: str
            alumnos: list = []
        """,
        level=3,
        daw=False,
        bank=True,
        qtype="error",
    ),
    choice(
        "poo9-24",
        CID,
        "`precio_envio(pedido)` tiene un `if`/`elif` por cada transportista y hay que añadir uno nuevo cada mes. ¿Qué cambio sigue el principio abierto/cerrado?",
        [
            (
                "Una clase por transportista con su método `precio(pedido)`, y que el pedido reciba el transportista y le pida el precio",
                None,
            ),
            (
                "Añadir otro `elif` para el transportista nuevo",
                f"{CID}.if-por-tipos",
                "Cada transportista nuevo obliga a modificar la función que ya funcionaba.",
            ),
            (
                "Guardar en un diccionario el nombre del transportista y una tarifa fija",
                None,
                "Sirve si todos cobran igual, pero no si cada uno calcula el precio a su manera.",
            ),
            (
                "Copiar la función y llamarla `precio_envio2`",
                None,
                "Duplica el código y los cambios habría que hacerlos en dos sitios.",
            ),
        ],
        0,
        "Con una clase por transportista (polimorfismo, Unidad 6) y el transportista pasado al pedido (inversión de dependencias), uno nuevo es una clase nueva: no se modifica nada de lo que ya funciona.",
        level=3,
        daw=False,
        bank=True,
        qtype="solucion",
    ),
    code(
        "poo9-25",
        CID,
        '**Práctica: inversión de dependencias.** Crea `Pedido(numero, aviso)`, que **recibe** el objeto que envía los avisos, y:\n\n- `confirmar()`: si el pedido ya estaba confirmado lanza `ValueError`; si no, lo marca como confirmado (atributo `confirmado`) y devuelve lo que devuelve `aviso.enviar("Pedido 7 confirmado")`.\n\nCrea también `AvisoFalso`, con una lista `enviados` y un `enviar(texto)` que guarda el texto y devuelve `"ok"`, para probar el pedido sin enviar nada de verdad.',
        """
        class AvisoFalso:
            ...


        class Pedido:
            ...
        """,
        """
        class AvisoFalso:
            \"\"\"Aviso de mentira para las pruebas: guarda lo que se habría enviado.\"\"\"

            def __init__(self) -> None:
                self.enviados: list[str] = []

            def enviar(self, texto: str) -> str:
                self.enviados.append(texto)
                return "ok"


        class Pedido:
            \"\"\"Un pedido que avisa al confirmarse con el aviso que recibe.\"\"\"

            def __init__(self, numero: int, aviso) -> None:
                self.numero = numero
                self.aviso = aviso
                self.confirmado = False

            def confirmar(self) -> str:
                if self.confirmado:
                    raise ValueError("El pedido ya está confirmado")
                self.confirmado = True
                return self.aviso.enviar(f"Pedido {self.numero} confirmado")


        falso = AvisoFalso()
        print(Pedido(7, falso).confirmar(), falso.enviados)
        """,
        [
            case(
                'f = AvisoFalso()\nassert f.enviados == [] and f.enviar("x") == "ok" and f.enviados == ["x"], "AvisoFalso guarda cada texto y devuelve \'ok\'"',
            ),
            case(
                'class Eco:\n    def enviar(self, texto):\n        return "eco: " + texto\np = Pedido(7, Eco())\nassert p.confirmado is False, "Un pedido nuevo no está confirmado"\nassert p.confirmar() == "eco: Pedido 7 confirmado", "confirmar() debe usar el aviso que recibe el pedido y devolver su resultado"\nassert p.confirmado is True, "confirmar() marca el pedido"',
                error=f"{CID}.crea-su-dependencia",
            ),
            case(
                'f = AvisoFalso()\np = Pedido(1, f)\np.confirmar()\ntry:\n    p.confirmar()\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError("Confirmar dos veces debe lanzar ValueError")\nassert f.enviados == ["Pedido 1 confirmado"], "El segundo intento no debe enviar otro aviso"',
            ),
        ],
        "El pedido no sabe cómo se envían los avisos: solo llama a `enviar`. Por eso en las pruebas se le pasa un `AvisoFalso` y se comprueba qué habría enviado, sin mandar nada.",
        "Guarda el parámetro en `self.aviso` y en `confirmar` llama a `self.aviso.enviar(...)`. Comprueba `self.confirmado` antes de enviar.",
        wrong=[
            (
                """
                class AvisoFalso:
                    def __init__(self):
                        self.enviados = []

                    def enviar(self, texto):
                        self.enviados.append(texto)
                        return "ok"


                class Pedido:
                    def __init__(self, numero, aviso):
                        self.numero = numero
                        self.aviso = AvisoFalso()
                        self.confirmado = False

                    def confirmar(self):
                        if self.confirmado:
                            raise ValueError("El pedido ya está confirmado")
                        self.confirmado = True
                        return self.aviso.enviar(f"Pedido {self.numero} confirmado")
                """,
                2,
            ),
            (
                """
                class AvisoFalso:
                    def __init__(self):
                        self.enviados = []

                    def enviar(self, texto):
                        self.enviados.append(texto)
                        return "ok"


                class Pedido:
                    def __init__(self, numero, aviso):
                        self.numero = numero
                        self.aviso = aviso
                        self.confirmado = False

                    def confirmar(self):
                        resultado = self.aviso.enviar(f"Pedido {self.numero} confirmado")
                        if self.confirmado:
                            raise ValueError("El pedido ya está confirmado")
                        self.confirmado = True
                        return resultado
                """,
                3,
            ),
        ],
        level=2,
        daw=False,
    ),
    output(
        "poo9-26",
        CID,
        """
        from dataclasses import dataclass, field

        @dataclass
        class Grupo:
            nombre: str
            alumnos: list = field(default_factory=list)

        a = Grupo("1A")
        b = Grupo("1B")
        a.alumnos.append("Ana")
        print(len(a.alumnos), len(b.alumnos), a == Grupo("1A", ["Ana"]))
        """,
        "1 0 True",
        "Cada grupo estrena su lista gracias a `default_factory`, y el `__eq__` generado compara nombre y alumnos.",
        traps={"1 1 True": f"{CID}.dataclass-lista-por-defecto", "1 0 False": None},
        level=2,
        daw=False,
    ),
    # ---------- Ejercicio principal de la unidad
    code(
        "poo9-27",
        CID,
        '**Ejercicio principal: refactorizar la tienda.** El código inicial es una tienda procedural con diccionarios. Reorganízala en cuatro clases, cada una con su responsabilidad, docstring y type hints:\n\n- `Producto`: una **dataclass** con `nombre: str`, `precio: float` y `stock: int = 0`.\n- `Inventario`: `agregar(producto)` (un nombre repetido da `ValueError`), `buscar(nombre)` (devuelve el producto; si no existe, `KeyError`) y `retirar(nombre, cantidad)` (si no hay stock suficiente, `ValueError` y no cambia nada).\n- `Carrito(inventario)`: `agregar(nombre, cantidad)` retira del inventario y guarda la línea; `subtotal()` suma precio × cantidad.\n- `Ticket(carrito, iva=0.21)`: `total()` (subtotal con IVA, redondeado a 2 decimales) y `texto()`, que devuelve las líneas `"2 x Teclado = 50.00 €"` y al final `"Total con IVA: 60.50 €"`, separadas por saltos de línea. El ticket **no** toca el stock.',
        """
        # Tienda procedural: funciona, pero todo está mezclado
        inventario = {"Teclado": {"precio": 25.0, "stock": 5}}
        carrito = []


        def comprar(nombre, cantidad):
            producto = inventario[nombre]
            if producto["stock"] < cantidad:
                raise ValueError("No hay stock")
            producto["stock"] -= cantidad
            carrito.append((nombre, cantidad))


        def ticket():
            lineas = []
            subtotal = 0
            for nombre, cantidad in carrito:
                importe = inventario[nombre]["precio"] * cantidad
                subtotal += importe
                lineas.append(f"{cantidad} x {nombre} = {importe:.2f} €")
            lineas.append(f"Total con IVA: {round(subtotal * 1.21, 2):.2f} €")
            return "\\n".join(lineas)


        comprar("Teclado", 2)
        print(ticket())
        """,
        """
        from dataclasses import dataclass


        @dataclass
        class Producto:
            \"\"\"Un artículo de la tienda.\"\"\"
            nombre: str
            precio: float
            stock: int = 0


        class Inventario:
            \"\"\"Los productos de la tienda y su stock.\"\"\"

            def __init__(self) -> None:
                self._productos: dict[str, Producto] = {}

            def agregar(self, producto: Producto) -> None:
                if producto.nombre in self._productos:
                    raise ValueError(f"Ya existe {producto.nombre}")
                self._productos[producto.nombre] = producto

            def buscar(self, nombre: str) -> Producto:
                if nombre not in self._productos:
                    raise KeyError(nombre)
                return self._productos[nombre]

            def retirar(self, nombre: str, cantidad: int) -> Producto:
                producto = self.buscar(nombre)
                if cantidad > producto.stock:
                    raise ValueError(f"No hay stock suficiente de {nombre}")
                producto.stock -= cantidad
                return producto


        class Carrito:
            \"\"\"Lo que compra un cliente.\"\"\"

            def __init__(self, inventario: Inventario) -> None:
                self.inventario = inventario
                self.lineas: list[tuple[Producto, int]] = []

            def agregar(self, nombre: str, cantidad: int) -> None:
                producto = self.inventario.retirar(nombre, cantidad)
                self.lineas.append((producto, cantidad))

            def subtotal(self) -> float:
                return sum(producto.precio * cantidad for producto, cantidad in self.lineas)


        class Ticket:
            \"\"\"Presenta un carrito con su IVA: no calcula precios ni toca el stock.\"\"\"

            def __init__(self, carrito: Carrito, iva: float = 0.21) -> None:
                self.carrito = carrito
                self.iva = iva

            def total(self) -> float:
                return round(self.carrito.subtotal() * (1 + self.iva), 2)

            def texto(self) -> str:
                lineas = [
                    f"{cantidad} x {producto.nombre} = {producto.precio * cantidad:.2f} €"
                    for producto, cantidad in self.carrito.lineas
                ]
                lineas.append(f"Total con IVA: {self.total():.2f} €")
                return "\\n".join(lineas)


        inventario = Inventario()
        inventario.agregar(Producto("Teclado", 25.0, 5))
        carrito = Carrito(inventario)
        carrito.agregar("Teclado", 2)
        print(Ticket(carrito).texto())
        """,
        [
            case(
                'import dataclasses\nassert dataclasses.is_dataclass(Producto), "Producto debe ser una dataclass"\np = Producto("Pan", 1.5)\nassert p.stock == 0 and p == Producto("Pan", 1.5, 0), "Producto(nombre, precio, stock=0) con __eq__ generado"',
            ),
            case(
                'inv = Inventario()\npan = Producto("Pan", 1.5, 10)\ninv.agregar(pan)\nassert inv.buscar("Pan") is pan, "buscar() devuelve el producto guardado"\nfor accion in (lambda: inv.agregar(Producto("Pan", 2.0)), lambda: inv.retirar("Pan", 11)):\n    try:\n        accion()\n    except ValueError:\n        pass\n    else:\n        raise AssertionError("Un nombre repetido o retirar más del stock debe lanzar ValueError")\nassert pan.stock == 10, "Si no hay stock suficiente, no debe cambiar nada"\ntry:\n    inv.buscar("Leche")\nexcept KeyError:\n    pass\nelse:\n    raise AssertionError("buscar() de un producto que no existe debe lanzar KeyError")\ninv.retirar("Pan", 4)\nassert pan.stock == 6, "retirar() descuenta del stock"',
            ),
            case(
                'inv = Inventario()\ninv.agregar(Producto("Teclado", 25.0, 5))\ninv.agregar(Producto("Ratón", 10.0, 1))\ncar = Carrito(inv)\ncar.agregar("Teclado", 2)\ncar.agregar("Ratón", 1)\nassert car.subtotal() == 60.0, f"subtotal() debe dar 60.0; da {car.subtotal()!r}"\nassert inv.buscar("Teclado").stock == 3, "El carrito retira del inventario"\ntry:\n    car.agregar("Ratón", 1)\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError("Sin stock, Carrito.agregar() debe lanzar el ValueError del inventario")\nassert len(car.lineas) == 2, "Si no hay stock no se añade la línea"',
            ),
            case(
                'inv = Inventario()\ninv.agregar(Producto("Teclado", 25.0, 5))\ncar = Carrito(inv)\ncar.agregar("Teclado", 2)\nt = Ticket(car)\nassert t.total() == 60.5, f"total() con IVA del 21 %: debe dar 60.5; da {t.total()!r}"\nassert t.texto() == "2 x Teclado = 50.00 €\\nTotal con IVA: 60.50 €", f"texto() devuelve {t.texto()!r}"\nassert Ticket(car, iva=0.1).total() == 55.0, "El IVA se puede cambiar"\nt.texto()\nassert inv.buscar("Teclado").stock == 3, "El ticket no debe tocar el stock"',
                error=f"{CID}.clase-que-lo-hace-todo",
            ),
            case(
                'for clase in (Producto, Inventario, Carrito, Ticket):\n    assert clase.__doc__ and not clase.__doc__.startswith(clase.__name__ + "("), f"Pon una docstring en {clase.__name__}"\nassert Ticket.texto.__annotations__.get("return") in (str, "str"), "Anota que Ticket.texto() devuelve str"',
                error=f"{CID}.sin-documentar",
            ),
        ],
        "Cada clase tiene un solo motivo para cambiar: `Producto` los datos, `Inventario` el stock, `Carrito` lo que se compra y `Ticket` cómo se presenta. El ticket solo pide `subtotal()` y las líneas: si mañana cambia el IVA o el formato, no se toca nada más.",
        "Empieza por la dataclass y el inventario (guarda los productos en un diccionario por nombre). `Carrito.agregar` llama a `self.inventario.retirar(...)` y guarda lo que devuelve.",
        wrong=[
            (
                """
                class Producto:
                    def __init__(self, nombre, precio, stock=0):
                        self.nombre = nombre
                        self.precio = precio
                        self.stock = stock
                """,
                1,
            ),
            (
                """
                from dataclasses import dataclass


                @dataclass
                class Producto:
                    \"\"\"Un artículo.\"\"\"
                    nombre: str
                    precio: float
                    stock: int = 0


                class Inventario:
                    \"\"\"Stock.\"\"\"

                    def __init__(self):
                        self._productos = {}

                    def agregar(self, producto):
                        self._productos[producto.nombre] = producto

                    def buscar(self, nombre):
                        return self._productos[nombre]

                    def retirar(self, nombre, cantidad):
                        producto = self.buscar(nombre)
                        producto.stock -= cantidad
                        if producto.stock < 0:
                            raise ValueError(nombre)
                        return producto
                """,
                2,
            ),
            (
                """
                from dataclasses import dataclass


                @dataclass
                class Producto:
                    \"\"\"Un artículo.\"\"\"
                    nombre: str
                    precio: float
                    stock: int = 0


                class Inventario:
                    \"\"\"Stock.\"\"\"

                    def __init__(self):
                        self._productos = {}

                    def agregar(self, producto):
                        if producto.nombre in self._productos:
                            raise ValueError(producto.nombre)
                        self._productos[producto.nombre] = producto

                    def buscar(self, nombre):
                        return self._productos[nombre]

                    def retirar(self, nombre, cantidad):
                        producto = self.buscar(nombre)
                        if cantidad > producto.stock:
                            raise ValueError(nombre)
                        producto.stock -= cantidad
                        return producto


                class Carrito:
                    \"\"\"Compra.\"\"\"

                    def __init__(self, inventario):
                        self.inventario = inventario
                        self.lineas = []

                    def agregar(self, nombre, cantidad):
                        self.lineas.append((self.inventario.buscar(nombre), cantidad))

                    def subtotal(self):
                        return sum(p.precio * n for p, n in self.lineas)
                """,
                3,
            ),
            (
                """
                from dataclasses import dataclass


                @dataclass
                class Producto:
                    \"\"\"Un artículo.\"\"\"
                    nombre: str
                    precio: float
                    stock: int = 0


                class Inventario:
                    \"\"\"Stock.\"\"\"

                    def __init__(self):
                        self._productos = {}

                    def agregar(self, producto):
                        if producto.nombre in self._productos:
                            raise ValueError(producto.nombre)
                        self._productos[producto.nombre] = producto

                    def buscar(self, nombre):
                        return self._productos[nombre]

                    def retirar(self, nombre, cantidad):
                        producto = self.buscar(nombre)
                        if cantidad > producto.stock:
                            raise ValueError(nombre)
                        producto.stock -= cantidad
                        return producto


                class Carrito:
                    \"\"\"Compra.\"\"\"

                    def __init__(self, inventario):
                        self.inventario = inventario
                        self.lineas = []

                    def agregar(self, nombre, cantidad):
                        self.lineas.append((self.inventario.retirar(nombre, cantidad), cantidad))

                    def subtotal(self):
                        return sum(p.precio * n for p, n in self.lineas)


                class Ticket:
                    \"\"\"Ticket.\"\"\"

                    def __init__(self, carrito, iva=0.21):
                        self.carrito = carrito
                        self.iva = iva

                    def total(self):
                        return round(self.carrito.subtotal() * (1 + self.iva), 2)

                    def texto(self):
                        lineas = []
                        for producto, cantidad in self.carrito.lineas:
                            producto.stock -= cantidad
                            lineas.append(f"{cantidad} x {producto.nombre} = {producto.precio * cantidad:.2f} €")
                        lineas.append(f"Total con IVA: {self.total():.2f} €")
                        return "\\n".join(lineas)
                """,
                4,
            ),
        ],
        level=3,
        daw=False,
    ),
]

# Errores típicos (slug, etiqueta, por qué, qué pensar, cómo evitarlo)
ERRORS = [
    (
        "clase-que-lo-hace-todo",
        "Pone en una sola clase o función varias responsabilidades",
        "Cuando una clase calcula, presenta y guarda, cualquier cambio en una de esas cosas obliga a tocarla y puede romper las otras.",
        "¿Por cuántos motivos distintos podría tener que cambiar esta clase?",
        "Separa cada responsabilidad en su clase y haz que colaboren pidiéndose resultados.",
    ),
    (
        "responsabilidad-es-un-metodo",
        "Cree que «una responsabilidad» significa «un solo método»",
        "Una responsabilidad (por ejemplo, las cuentas de las notas) puede necesitar varios métodos; lo que importa es que todos traten de lo mismo.",
        "¿Todos estos métodos cambian por el mismo motivo?",
        "Agrupa por motivo de cambio, no por número de métodos.",
    ),
    (
        "acoplado-a-detalles",
        "Usa los atributos internos de otra clase en vez de pedirle el resultado",
        "Si una clase lee `otra.lista[0].precio`, cualquier cambio en cómo se guarda la otra la rompe: acoplamiento alto.",
        "¿Tiene la otra clase un método que me dé lo que necesito?",
        "Llama a sus métodos (`carrito.total()`) y deja que cada clase decida cómo guarda sus datos.",
    ),
    (
        "copia-de-datos",
        "Copia un resultado de otro objeto en vez de pedírselo cuando lo necesita",
        "La copia se queda vieja en cuanto el otro objeto cambia y los dos dejan de coincidir.",
        "¿Este dato puede cambiar en el objeto que lo tiene?",
        "Pide el dato o el cálculo en el momento: `self.calificaciones.media()`.",
    ),
    (
        "if-por-tipos",
        "Añade un `if` por cada tipo nuevo en vez de una clase nueva",
        "Cada tipo nuevo obliga a modificar código que ya funcionaba, que es lo que el principio abierto/cerrado quiere evitar.",
        "¿Podría cada caso ser una clase con el mismo método?",
        "Usa polimorfismo: una clase por caso con el mismo método, y llama al método.",
    ),
    (
        "herencia-que-rompe",
        "Hereda aunque la subclase no pueda cumplir lo que promete la superclase",
        "Si un objeto de la subclase no se comporta como se espera de la superclase (un cuadrado que deja de serlo, un pingüino que no vuela), rompe la sustitución de Liskov.",
        "¿Puedo usar un objeto de la subclase en cualquier sitio donde se use la superclase?",
        "Cambia la jerarquía o usa composición.",
    ),
    (
        "crea-su-dependencia",
        "La clase crea dentro los objetos de los que depende",
        "Si un pedido crea su propio aviso por email, no se puede cambiar por otro ni probar sin enviar emails de verdad.",
        "¿Podría recibir este objeto por el constructor?",
        "Pásale la dependencia al crearlo (`Pedido(numero, aviso)`) y guárdala.",
    ),
    (
        "hints-obligan",
        "Cree que Python comprueba los type hints al ejecutar",
        'Los type hints documentan y los usan el editor o `mypy`, pero Python no los comprueba: `doble("ab")` funciona aunque diga `x: int`.',
        "¿Quién comprobaría este tipo: Python o una herramienta aparte?",
        "Valida tú los datos importantes (con `if` y `raise`) y usa los hints para documentar.",
    ),
    (
        "dataclass-lista-por-defecto",
        "Pone una lista como valor por defecto en una dataclass",
        "`@dataclass` lo rechaza con `ValueError`, porque todos los objetos compartirían la misma lista.",
        "¿Este valor por defecto es mutable (lista, diccionario, conjunto)?",
        "Usa `field(default_factory=list)` (o `dict`, `set`).",
    ),
    (
        "sin-documentar",
        "Deja las clases sin docstring ni type hints",
        "Quien usa la clase tiene que leer todo su código para saber qué hace y qué recibe.",
        "¿Sabría alguien usar esta clase leyendo solo su cabecera?",
        "Añade una docstring corta y anota los parámetros y lo que devuelve.",
    ),
]

# Las preguntas del banco de esta unidad ya nacen con su tipo y su nivel: no hay que etiquetar ninguna antigua
BANK_TAGS: dict = {}
