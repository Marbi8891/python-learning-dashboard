# ruff: noqa: E501
"""Unidad 7 del módulo de POO: composición y relaciones entre objetos.

Concepto `poo-composicion` (área `poo`): asociación, agregación y composición, delegación y cuándo
usar composición en vez de herencia. Son ideas de **diseño**: Python no tiene palabras clave para
ellas; en el código solo hay objetos que guardan referencias a otros objetos. La salida de los
ejemplos la obtiene build_learning.py ejecutándolos.
"""

from exercises import bug, c, case, choice, code, fill, output
from poo_common import practice, proposed, ref

CID = "poo-composicion"

CONCEPT = {
    "id": CID,
    "title": "Composición y relaciones entre objetos",
    "area": "poo",
    "requires": ["poo-encapsulacion", "poo-herencia"],
    "daw": 2,
    "ut": "prog-ut6",
    "lessons": ["herencia"],
    "summary": "Objetos que trabajan juntos: asociación, agregación y composición, delegación y cuándo componer en vez de heredar.",
    "when": "Cuando un objeto necesita a otros para hacer su trabajo (un pedido con su cliente y sus líneas, un coche con su motor) y tienes que decidir quién crea a quién y quién hace cada cosa.",
    "example": {
        "code": c(
            """
            class Linea:
                def __init__(self, producto, precio, cantidad):
                    self.producto = producto
                    self.precio = precio
                    self.cantidad = cantidad

                def subtotal(self):
                    return self.precio * self.cantidad


            class Pedido:
                def __init__(self, cliente):
                    self.cliente = cliente          # asociación: el cliente existe fuera
                    self.lineas = []                # composición: las líneas son del pedido

                def agregar(self, producto, precio, cantidad):
                    self.lineas.append(Linea(producto, precio, cantidad))

                def total(self):                    # delegación: cada línea calcula lo suyo
                    return sum(linea.subtotal() for linea in self.lineas)


            pedido = Pedido("Ana")
            pedido.agregar("Teclado", 25, 2)
            pedido.agregar("Ratón", 10, 1)
            print(pedido.cliente, pedido.total())
            """
        ),
        "lines": [
            [13, "El pedido guarda una referencia al cliente: los dos existen por separado."],
            [14, "Las líneas solo tienen sentido dentro de su pedido."],
            [17, "El propio pedido crea sus líneas: eso es la composición."],
            [19, "`total` no calcula precios: se lo pide a cada línea."],
        ],
    },
    "errors": [],
    "related": ["poo-herencia", "poo-encapsulacion", "listas"],
}

UNIT = {
    "unit": {"module": "poo", "number": 7},
    "objectives": [
        "Reconocer en un enunciado las relaciones entre objetos: asociación, agregación y composición.",
        "Construir objetos que guardan referencias a otros objetos y entender que no se copian.",
        "Decidir quién crea las partes y quién vive más tiempo, el todo o sus partes.",
        "Delegar: que cada objeto haga su parte del trabajo en vez de hacerlo todo desde fuera.",
        "Elegir entre herencia («es un») y composición («tiene un») con argumentos.",
    ],
    "prior": "La Unidad 4 (encapsulación y propiedades), la Unidad 5 (herencia) y trabajar con listas de objetos.",
    "key": [
        [
            "Asociación",
            "Un objeto conoce a otro y lo usa, pero los dos existen por separado (un pedido y su cliente).",
        ],
        [
            "Agregación",
            "Un todo agrupa partes que se crean fuera y pueden seguir existiendo sin él (un equipo y sus jugadores).",
        ],
        [
            "Composición",
            "Un todo crea sus partes y estas no tienen sentido sin él (un pedido y sus líneas).",
        ],
        [
            "Delegación",
            "Un objeto pasa una tarea a otro objeto que sabe hacerla, en vez de hacerla él.",
        ],
        [
            "«Es un» / «tiene un»",
            "La prueba para elegir: si «A es un B», herencia; si «A tiene un B», composición.",
        ],
        [
            "Referencia",
            "Lo que guarda un atributo cuando le asignas un objeto: el mismo objeto, no una copia.",
        ],
    ],
    "sections": [
        {
            "id": f"{CID}.asociacion",
            "title": "Asociación: objetos que se conocen",
            "theory": "Hasta ahora cada objeto trabajaba solo. En un programa real los objetos **se relacionan**: un pedido es de un cliente, un alumno está matriculado en un curso. La relación más sencilla es la **asociación**: un objeto guarda en un atributo a otro objeto y lo usa cuando lo necesita.\n\n```\nclass Pedido:\n    def __init__(self, cliente):\n        self.cliente = cliente\n```\n\n- El atributo guarda una **referencia** al mismo objeto, **no una copia**. Si el cliente cambia su correo, el pedido ve el cambio.\n- Los dos objetos **viven por separado**: el cliente existía antes del pedido y seguirá existiendo si el pedido se borra.\n- Asociación, agregación y composición son **ideas de diseño** (se dibujan en los diagramas de clases). Python no tiene palabras clave para ellas: en el código siempre verás lo mismo, un atributo que apunta a otro objeto. Lo que cambia es **quién crea** el objeto y **cuánto vive**.",
            "examples": [
                {
                    "code": c(
                        """
                        class Cliente:
                            def __init__(self, nombre, email):
                                self.nombre = nombre
                                self.email = email


                        class Pedido:
                            def __init__(self, numero, cliente):
                                self.numero = numero
                                self.cliente = cliente      # guarda el mismo objeto, no una copia

                            def destinatario(self):
                                return f"Pedido {self.numero} para {self.cliente.email}"


                        ana = Cliente("Ana", "ana@ies.es")
                        pedido = Pedido(1, ana)
                        ana.email = "ana.garcia@ies.es"     # el cliente cambia su correo
                        print(pedido.destinatario())
                        print(pedido.cliente is ana)
                        """
                    ),
                    "lines": [
                        [10, "El pedido guarda una referencia al cliente que recibe."],
                        [13, "Usa los datos del cliente en el momento de llamarlo."],
                        [18, "Cambiar el cliente se nota desde el pedido: es el mismo objeto."],
                        [
                            20,
                            "`is` confirma que no hay copia: los dos nombres apuntan al mismo objeto.",
                        ],
                    ],
                }
            ],
            "quiz": ["poo7-01", "poo7-02", "poo7-03"],
        },
        {
            "id": f"{CID}.agregacion-composicion",
            "title": "Agregación y composición",
            "theory": "Cuando un objeto es un **todo** formado por **partes**, hay dos casos:\n\n| | Agregación | Composición |\n|---|---|---|\n| Quién crea las partes | Se crean **fuera** y se le pasan al todo | Las crea **el propio todo** |\n| Quién vive más | Las partes pueden seguir sin el todo | Las partes desaparecen con el todo |\n| Ejemplo | Un equipo y sus jugadores | Un pedido y sus líneas |\n\nLa pregunta clave es: **¿esta parte tiene sentido sin el todo?** Un jugador sigue existiendo si el equipo desaparece; una línea de pedido («2 teclados a 25 €») no significa nada fuera de su pedido.\n\nDos trampas al guardar partes en una lista:\n\n- **Nunca** uses una lista como valor por defecto de un parámetro (`def __init__(self, jugadores=[])`). Esa lista se crea **una sola vez** y la comparten todos los objetos. Usa `None` y crea la lista dentro.\n- Si recibes una lista de fuera, guarda una **copia** (`list(jugadores)`) si no quieres que los cambios de fuera se cuelen en tu objeto.",
            "examples": [
                {
                    "code": c(
                        """
                        class Jugador:
                            def __init__(self, nombre):
                                self.nombre = nombre


                        class Equipo:                       # agregación: recibe jugadores creados fuera
                            def __init__(self, nombre, jugadores=None):
                                self.nombre = nombre
                                self.jugadores = list(jugadores) if jugadores else []

                            def fichar(self, jugador):
                                self.jugadores.append(jugador)


                        class Linea:
                            def __init__(self, producto, cantidad):
                                self.producto = producto
                                self.cantidad = cantidad


                        class Pedido:                       # composición: crea sus propias líneas
                            def __init__(self):
                                self.lineas = []

                            def agregar(self, producto, cantidad):
                                self.lineas.append(Linea(producto, cantidad))


                        lucia = Jugador("Lucía")
                        equipo = Equipo("IES", [lucia])
                        otro = Equipo("Club")
                        otro.fichar(Jugador("Marta"))
                        print(len(equipo.jugadores), len(otro.jugadores))

                        pedido = Pedido()
                        pedido.agregar("Teclado", 2)
                        print(pedido.lineas[0].producto, pedido.lineas[0].cantidad)
                        """
                    ),
                    "lines": [
                        [7, "`None` como valor por defecto: cada equipo tendrá su propia lista."],
                        [9, "`list(...)` guarda una copia de la lista recibida."],
                        [26, "El pedido crea la línea: nadie de fuera la ve nacer."],
                        [
                            29,
                            "La jugadora existe antes que el equipo y seguiría existiendo sin él.",
                        ],
                        [33, "Cada equipo tiene su lista: fichar en uno no cambia el otro."],
                    ],
                }
            ],
            "quiz": ["poo7-04", "poo7-05", "poo7-06"],
        },
        {
            "id": f"{CID}.delegacion",
            "title": "Delegación: cada objeto hace su parte",
            "theory": "**Delegar** es que un objeto pase una tarea al objeto que sabe hacerla. El pedido no sabe calcular el precio de una línea: se lo pide a la línea.\n\n```\ndef total(self):\n    return sum(linea.subtotal() for linea in self.lineas)\n```\n\n- Cada clase se ocupa de **sus propios datos**: la línea sabe su subtotal, el pedido suma las líneas.\n- Si cambia cómo se calcula un subtotal (un descuento por cantidad), solo se toca `Linea`.\n- Desde fuera, pide las cosas al objeto que tienes, en vez de recorrer sus tripas: mejor `pedido.total()` que `pedido.lineas[0].producto.precio * …`. Encadenar atributos de objetos ajenos hace que tu código dependa de cómo están hechos por dentro.",
            "examples": [
                {
                    "code": c(
                        """
                        class Motor:
                            def __init__(self, potencia):
                                self.potencia = potencia
                                self.encendido = False

                            def encender(self):
                                self.encendido = True
                                return f"Motor de {self.potencia} CV en marcha"


                        class Coche:
                            def __init__(self, modelo, potencia):
                                self.modelo = modelo
                                self.motor = Motor(potencia)    # el coche crea su motor

                            def arrancar(self):
                                return self.motor.encender()    # delega en el motor

                            def en_marcha(self):
                                return self.motor.encendido


                        coche = Coche("Ibiza", 95)
                        print(coche.en_marcha())
                        print(coche.arrancar())
                        print(coche.en_marcha())
                        """
                    ),
                    "lines": [
                        [14, "Composición: el motor nace con el coche."],
                        [17, "`arrancar` no sabe encender motores: se lo pide al motor."],
                        [20, "Quien usa el coche no necesita saber que hay un motor dentro."],
                    ],
                }
            ],
            "quiz": ["poo7-07", "poo7-08", "poo7-09"],
        },
        {
            "id": f"{CID}.herencia-o-composicion",
            "title": "Herencia frente a composición",
            "theory": "Herencia y composición sirven para reutilizar código, pero dicen cosas distintas:\n\n- **Herencia** («es un»): un `Perro` **es un** `Animal`. La subclase recibe **todos** los métodos de la superclase y se puede usar en su lugar.\n- **Composición** («tiene un»): un `Coche` **tiene un** `Motor`. La clase usa otro objeto y solo enseña lo que ella decide.\n\nLa prueba es decir la frase en voz alta. «Un coche es un motor» suena mal: no heredes, compón.\n\nUn caso típico es una `Pila`. Si haces `class Pila(list)`, la pila hereda `insert`, `sort` o `pop(0)`, y cualquiera puede romper la regla «solo se saca el último». Si la pila **tiene** una lista dentro, solo ofrece `apilar`, `desapilar` y `cima`.\n\nUn consejo clásico del diseño orientado a objetos es **preferir la composición** cuando dudes: cambiar la pieza interna (otra lista, otro motor) no afecta a quien usa la clase, y no arrastras métodos que no quieres.",
            "examples": [
                {
                    "code": c(
                        """
                        class Pila:
                            def __init__(self):
                                self._elementos = []        # la pila TIENE una lista

                            def apilar(self, valor):
                                self._elementos.append(valor)

                            def desapilar(self):
                                return self._elementos.pop()

                            def cima(self):
                                return self._elementos[-1]

                            def esta_vacia(self):
                                return not self._elementos


                        pila = Pila()
                        for plato in ["azul", "rojo", "verde"]:
                            pila.apilar(plato)
                        print(pila.desapilar(), pila.cima())
                        print(hasattr(pila, "insert"))
                        """
                    ),
                    "lines": [
                        [
                            3,
                            "Composición: la lista es una pieza interna, con `_` porque no es pública.",
                        ],
                        [
                            9,
                            "Cada método delega en la lista, pero solo los que tienen sentido en una pila.",
                        ],
                        [22, "La pila no tiene `insert`: nadie puede meter un plato por debajo."],
                    ],
                }
            ],
            "quiz": ["poo7-10", "poo7-11", "poo7-12"],
        },
    ],
    "guided": ["poo7-13"],
    "autonomous": ["poo7-18"],
    "extras": ["poo7-14", "poo7-15"],
    "selfcheck": ["poo7-16", "poo7-17"],
    "recap": [
        "Asociación, agregación y composición son ideas de diseño: en Python siempre es un atributo que apunta a otro objeto.",
        "Guardar un objeto en un atributo guarda una referencia, no una copia.",
        "Agregación: las partes se crean fuera y sobreviven al todo. Composición: el todo crea sus partes.",
        "Nunca uses una lista como valor por defecto de un parámetro: usa `None` y crea la lista dentro.",
        "Delega: cada objeto hace lo que sabe hacer con sus datos.",
        "«Es un» → herencia; «tiene un» → composición. Si dudas, compón.",
    ],
    "pass": {
        "minScore": 0.7,
        "required": ["poo7-13", "poo7-18"],
        "text": [
            "Resolver el ejercicio guiado (coche y motor) y el ejercicio principal (clientes, pedidos y productos) con todos los tests superados.",
            "Dominar la unidad según el motor: al menos un 70 % de aciertos recientes en sus ejercicios, con varios tipos distintos.",
            "Completar las lecciones ayuda a organizarte, pero **no** demuestra la competencia: la demuestran los ejercicios.",
        ],
    },
    "practices": [
        practice(
            "Antes de escribir código, di la relación en voz alta: «A es un B» o «A tiene un B».",
            "Evita heredar de una clase solo para aprovechar sus métodos cuando en realidad la usas.",
        ),
        practice(
            "Decide quién crea cada objeto: si la parte no tiene sentido sin el todo, que la cree el todo.",
            "Así nadie de fuera puede dejar el todo con partes a medias o compartidas por error.",
        ),
        practice(
            "No uses listas ni diccionarios como valor por defecto de un parámetro: usa `None`.",
            "El valor por defecto se crea una sola vez y lo compartirían todos los objetos.",
        ),
        practice(
            "Pide las cosas al objeto que tienes (`pedido.total()`) en vez de encadenar atributos de otros (`pedido.lineas[0].producto.precio`).",
            "Si cambia cómo está hecha una clase por dentro, tu código no se rompe.",
        ),
        practice(
            "Guarda las piezas internas con `_` y ofrece solo los métodos que tienen sentido.",
            "La clase decide qué se puede hacer con ella y protege sus reglas.",
        ),
    ],
    "references": [
        ref(
            "py-faq-programming",
            "Objetos: ¿Qué es la delegación?",
            ["delegar en otro objeto las operaciones que no hace el propio objeto"],
        ),
        ref(
            "py-tutorial-classes",
            "9.3.5. Variables de clase y de instancia",
            ["una lista compartida por todos los objetos cuando no se crea en `__init__`"],
        ),
        ref(
            "py-faq-programming",
            "¿Por qué se comparten los valores por defecto entre objetos?",
            [
                "el valor por defecto de un parámetro se crea una sola vez",
                "usar `None` como valor por defecto",
            ],
        ),
    ],
    "bank": [
        "poo7-02",
        "poo7-05",
        "poo7-08",
        "poo7-10",
        "poo7-12",
        "poo7-16",
        "poo7-19",
        "poo7-20",
        "poo7-21",
        "poo7-22",
        "poo7-23",
        "poo7-24",
        "poo7-25",
        "poo7-26",
        "poo7-27",
    ],
    "curriculum": [
        proposed(
            "0485-RA7-j",
            "Se comparan herencia («es un») y composición («tiene un») y se elige entre ellas.",
        ),
        proposed(
            "0485-RA4-e",
            "Se escriben programas con objetos que usan otros objetos (cliente, pedido y líneas).",
        ),
        proposed(
            "0485-RA6-c",
            "Se guardan y procesan listas de objetos dentro de otro objeto.",
        ),
    ],
}

EXERCISES = [
    # ---------- Lección «Asociación»
    output(
        "poo7-01",
        CID,
        """
        class Cliente:
            def __init__(self, nombre):
                self.nombre = nombre

        class Pedido:
            def __init__(self, cliente):
                self.cliente = cliente

        luis = Cliente("Luis")
        p1 = Pedido(luis)
        p2 = Pedido(luis)
        p1.cliente.nombre = "Luis Pérez"
        print(p2.cliente.nombre)
        """,
        "Luis Pérez",
        "Los dos pedidos guardan una referencia al **mismo** cliente. Cambiar su nombre a través de `p1` se ve desde `p2` y desde `luis`: no hay copias.",
        traps={"Luis": f"{CID}.copia-al-guardar"},
        level=1,
        daw=False,
    ),
    choice(
        "poo7-02",
        CID,
        "Un `Pedido` guarda en `self.cliente` un objeto `Cliente` que ya existía y que sigue existiendo cuando el pedido se borra. ¿Qué relación es?",
        [
            ("Asociación: el pedido conoce al cliente, pero los dos viven por separado", None),
            (
                "Herencia: `Pedido` es un tipo de `Cliente`",
                f"{CID}.herencia-por-tiene",
                "Un pedido no «es un» cliente: solo lo conoce. No hay ninguna subclase.",
            ),
            (
                "Composición: el pedido crea al cliente",
                None,
                "El cliente ya existía antes y no lo crea el pedido: no es una parte suya.",
            ),
            (
                "Ninguna: un objeto no puede guardar otro objeto en un atributo",
                None,
                "Un atributo puede guardar cualquier valor, también otros objetos.",
            ),
        ],
        0,
        "Es una **asociación**: un objeto guarda una referencia a otro y lo usa, sin crearlo ni ser su dueño.",
        level=1,
        daw=False,
        bank=True,
        qtype="teoria",
    ),
    fill(
        "poo7-03",
        CID,
        "Completa el constructor para que cada curso **conozca** a su tutor (el mismo objeto, sin copiarlo).",
        """
        class Profesor:
            def __init__(self, nombre):
                self.nombre = nombre

        class Curso:
            def __init__(self, nombre, tutor):
                self.nombre = nombre
                self.tutor = ___

        rosa = Profesor("Rosa")
        daw1 = Curso("1.º DAW", rosa)
        print(daw1.tutor.nombre, daw1.tutor is rosa)
        """,
        ["tutor"],
        "Basta con guardar el parámetro: `self.tutor = tutor`. El curso apunta al mismo profesor, por eso `is` da `True`.",
        expect="Rosa True",
        traps={"Profesor(tutor)": f"{CID}.copia-al-guardar", "rosa": None, "nombre": None},
        level=1,
        daw=False,
    ),
    # ---------- Lección «Agregación y composición»
    output(
        "poo7-04",
        CID,
        """
        class Equipo:
            def __init__(self, nombre, jugadores=[]):
                self.nombre = nombre
                self.jugadores = jugadores

            def fichar(self, jugador):
                self.jugadores.append(jugador)

        a = Equipo("A")
        b = Equipo("B")
        a.fichar("Lucía")
        print(len(b.jugadores))
        """,
        "1",
        "La lista `[]` del valor por defecto se crea **una sola vez**, al definir la función, y la comparten todos los equipos creados sin lista. Fichar en `a` también «ficha» en `b`.",
        traps={"0": f"{CID}.lista-por-defecto"},
        level=2,
        daw=False,
    ),
    choice(
        "poo7-05",
        CID,
        "¿Qué distingue la **composición** de la **agregación**?",
        [
            ("En la composición el todo crea sus partes y estas no tienen sentido sin él", None),
            (
                "En la composición las partes se crean fuera y se pasan al constructor",
                None,
                "Eso describe la agregación: las partes vienen de fuera y pueden vivir sin el todo.",
            ),
            (
                "La composición usa la palabra clave `compose` de Python",
                f"{CID}.relacion-es-sintaxis",
                "Python no tiene palabras clave para estas relaciones: son ideas de diseño.",
            ),
            (
                "La composición solo se puede hacer con herencia",
                f"{CID}.herencia-por-tiene",
                "Es al revés: la composición es una alternativa a la herencia («tiene un» frente a «es un»).",
            ),
        ],
        0,
        "La pregunta es quién crea la parte y si tiene sentido sola. Una línea de pedido la crea el pedido y no significa nada fuera de él: composición.",
        level=1,
        daw=False,
        bank=True,
        qtype="teoria",
    ),
    bug(
        "poo7-06",
        CID,
        "Cada carrito debería empezar vacío, pero el segundo ya trae el producto del primero. Sin tocar la cabecera de `__init__`, ¿qué línea hay que cambiar?",
        """
        class Carrito:
            def __init__(self, productos=[]):
                self.productos = productos

            def meter(self, producto):
                self.productos.append(producto)

        c1 = Carrito()
        c1.meter("pan")
        c2 = Carrito()
        print(c2.productos)
        """,
        3,
        "        self.productos = list(productos)",
        "[]",
        f"{CID}.lista-por-defecto",
        "La lista `[]` del valor por defecto se crea una sola vez y la comparten todos los carritos que se crean sin lista. `list(productos)` hace que cada carrito guarde una lista nueva. Lo más limpio, además, es cambiar el valor por defecto a `None`.",
        level=2,
        daw=False,
    ),
    # ---------- Lección «Delegación»
    output(
        "poo7-07",
        CID,
        """
        class Linea:
            def __init__(self, precio, cantidad):
                self.precio = precio
                self.cantidad = cantidad

            def subtotal(self):
                return self.precio * self.cantidad

        class Pedido:
            def __init__(self):
                self.lineas = []

            def agregar(self, precio, cantidad):
                self.lineas.append(Linea(precio, cantidad))

            def total(self):
                return sum(l.subtotal() for l in self.lineas)

        p = Pedido()
        p.agregar(10, 3)
        p.agregar(5, 2)
        print(p.total())
        """,
        "40",
        "El pedido delega en cada línea: 10 × 3 = 30 y 5 × 2 = 10, en total 40.",
        traps={"15": None, "5": None},
        level=1,
        daw=False,
    ),
    choice(
        "poo7-08",
        CID,
        "Cada `Linea` tiene el método `subtotal()`. ¿Qué versión de `Pedido.total()` **delega** en las líneas?",
        [
            ("`return sum(linea.subtotal() for linea in self.lineas)`", None),
            (
                "`return sum(linea.precio * linea.cantidad for linea in self.lineas)`",
                f"{CID}.no-delega",
                "Repite fuera de la línea un cálculo que la línea ya sabe hacer.",
            ),
            (
                "`return sum(self.lineas)`",
                None,
                "No se pueden sumar objetos `Linea` directamente: hay que pedirle a cada una su subtotal.",
            ),
            (
                "`return Linea.subtotal()`",
                None,
                "Así se llama al método sin ninguna línea concreta: falta el objeto sobre el que trabajar.",
            ),
        ],
        0,
        "Delegar es pedirle a cada línea lo que sabe hacer. Si mañana `subtotal` aplica un descuento, `total` sigue siendo correcto sin tocarlo.",
        code_options=True,
        level=2,
        daw=False,
        bank=True,
        qtype="codigo",
    ),
    fill(
        "poo7-09",
        CID,
        "Completa `arrancar` para que el coche **delegue** en su motor.",
        """
        class Motor:
            def encender(self):
                return "brrrum"

        class Coche:
            def __init__(self):
                self.motor = Motor()

            def arrancar(self):
                return ___

        print(Coche().arrancar())
        """,
        ["self.motor.encender()"],
        "El coche no sabe encender motores: se lo pide a su motor con `self.motor.encender()`.",
        expect="brrrum",
        traps={
            "Motor.encender()": None,
            "self.motor.encender": f"{CID}.no-delega",
            "motor.encender()": None,
        },
        level=2,
        daw=False,
    ),
    # ---------- Lección «Herencia frente a composición»
    choice(
        "poo7-10",
        CID,
        "Un coche necesita un motor con `encender()` y `apagar()`. ¿Qué diseño es mejor?",
        [
            ("`Coche` guarda un objeto `Motor` en un atributo y le delega esas tareas", None),
            (
                "`class Coche(Motor)`, para heredar `encender()` y `apagar()`",
                f"{CID}.herencia-por-tiene",
                "«Un coche es un motor» no es cierto: el coche heredaría todo lo del motor y se podría usar como si fuera uno.",
            ),
            (
                "`class Motor(Coche)`, porque el motor forma parte del coche",
                f"{CID}.herencia-por-tiene",
                "Formar parte de algo es «tiene un», no «es un»: tampoco es herencia.",
            ),
            (
                "Copiar los métodos del motor dentro de `Coche`",
                None,
                "Duplicaría el código: un cambio en el motor habría que hacerlo en dos sitios.",
            ),
        ],
        0,
        "«Un coche **tiene un** motor»: composición. El coche usa el motor y solo enseña lo que le interesa (`arrancar`).",
        level=2,
        daw=False,
        bank=True,
        qtype="diseno",
    ),
    output(
        "poo7-11",
        CID,
        """
        class Pila:
            def __init__(self):
                self._datos = []

            def apilar(self, x):
                self._datos.append(x)

            def desapilar(self):
                return self._datos.pop()

        p = Pila()
        p.apilar(1)
        p.apilar(2)
        p.apilar(3)
        print(p.desapilar() + p.desapilar())
        """,
        "5",
        "La pila delega en su lista interna y saca siempre el último: primero 3 y después 2, que suman 5.",
        traps={"3": None, "6": None, "1": None},
        level=1,
        daw=False,
    ),
    choice(
        "poo7-12",
        CID,
        "¿Qué es cierto sobre la asociación, la agregación y la composición en Python?",
        [
            (
                "Son ideas de diseño: en el código siempre es un atributo que apunta a otro objeto",
                None,
            ),
            (
                "Cada una se declara con una palabra clave distinta",
                f"{CID}.relacion-es-sintaxis",
                "Python no tiene palabras clave para ellas; se reconocen por quién crea los objetos y cuánto viven.",
            ),
            (
                "Solo existen si se usa herencia",
                f"{CID}.herencia-por-tiene",
                "Son relaciones entre objetos distintos; la herencia es una relación entre clases.",
            ),
            (
                "Python copia el objeto al guardarlo en un atributo",
                f"{CID}.copia-al-guardar",
                "Python guarda una referencia al mismo objeto, nunca una copia automática.",
            ),
        ],
        0,
        "En los diagramas de clases se dibujan de forma distinta, pero en Python el código es el mismo: `self.parte = objeto`. Lo que cambia es el diseño: quién crea la parte y si sobrevive al todo.",
        level=2,
        daw=False,
        bank=True,
        qtype="teoria",
    ),
    # ---------- Ejercicio guiado
    code(
        "poo7-13",
        CID,
        '**Ejercicio guiado: coche y motor.** Sigue los pasos:\n\n1. Crea `Motor(potencia)` con el atributo `encendido` a `False` y los métodos `encender()` y `apagar()`, que cambian `encendido`.\n2. Crea `Coche(modelo, potencia)`: el propio coche crea su `Motor` y lo guarda en `self.motor` (composición).\n3. Añade a `Coche` los métodos `arrancar()` y `parar()`, que **delegan** en el motor, y `estado()`, que devuelve `"Ibiza: en marcha"` o `"Ibiza: parado"`.',
        """
        # Paso 1: Motor

        # Paso 2: Coche crea su motor

        # Paso 3: arrancar, parar y estado


        coche = Coche("Ibiza", 95)
        coche.arrancar()
        print(coche.estado())
        coche.parar()
        print(coche.estado())
        """,
        """
        class Motor:
            def __init__(self, potencia):
                self.potencia = potencia
                self.encendido = False

            def encender(self):
                self.encendido = True

            def apagar(self):
                self.encendido = False


        class Coche:
            def __init__(self, modelo, potencia):
                self.modelo = modelo
                self.motor = Motor(potencia)

            def arrancar(self):
                self.motor.encender()

            def parar(self):
                self.motor.apagar()

            def estado(self):
                situacion = "en marcha" if self.motor.encendido else "parado"
                return f"{self.modelo}: {situacion}"


        coche = Coche("Ibiza", 95)
        coche.arrancar()
        print(coche.estado())
        coche.parar()
        print(coche.estado())
        """,
        [
            case(
                'm = Motor(90)\nassert m.potencia == 90 and m.encendido is False, "Un motor nuevo guarda su potencia y empieza apagado"\nm.encender()\nassert m.encendido is True, "encender() pone encendido a True"\nm.apagar()\nassert m.encendido is False, "apagar() pone encendido a False"',
            ),
            case(
                'a = Coche("Ibiza", 95)\nb = Coche("León", 150)\nassert isinstance(a.motor, Motor), "El coche debe crear su Motor y guardarlo en self.motor"\nassert a.motor.potencia == 95 and b.motor.potencia == 150, "Cada coche crea su motor con su potencia"\nassert a.motor is not b.motor, "Cada coche tiene su propio motor"\nassert not isinstance(a, Motor), "Un coche no es un motor: no heredes de Motor, guárdalo en un atributo"',
                error=f"{CID}.herencia-por-tiene",
            ),
            case(
                'c = Coche("Ibiza", 95)\nassert c.estado() == "Ibiza: parado", f"Un coche nuevo está parado; estado() devuelve {c.estado()!r}"\nc.arrancar()\nassert c.motor.encendido, "arrancar() debe encender el motor del coche"\nassert c.estado() == "Ibiza: en marcha", f"Tras arrancar, estado() devuelve {c.estado()!r}"\nc.parar()\nassert not c.motor.encendido and c.estado() == "Ibiza: parado", "parar() debe apagar el motor"',
                error=f"{CID}.no-delega",
            ),
        ],
        "El coche crea su motor (composición) y le pasa el trabajo de encenderse y apagarse (delegación). `estado()` consulta al motor en vez de llevar su propia copia del dato, así nunca se contradicen.",
        "En `Coche.__init__` escribe `self.motor = Motor(potencia)`. `arrancar` es una línea: `self.motor.encender()`.",
        wrong=[
            (
                """
                class Motor:
                    def __init__(self, potencia):
                        self.potencia = potencia
                        self.encendido = False

                    def encender(self):
                        self.encendido = True

                    def apagar(self):
                        self.encendido = False


                class Coche(Motor):
                    def __init__(self, modelo, potencia):
                        super().__init__(potencia)
                        self.modelo = modelo
                        self.motor = self

                    def arrancar(self):
                        self.encender()

                    def parar(self):
                        self.apagar()

                    def estado(self):
                        return f"{self.modelo}: {'en marcha' if self.encendido else 'parado'}"
                """,
                2,
            ),
            (
                """
                class Motor:
                    def __init__(self, potencia):
                        self.potencia = potencia
                        self.encendido = False

                    def encender(self):
                        self.encendido = True

                    def apagar(self):
                        self.encendido = False


                class Coche:
                    def __init__(self, modelo, potencia):
                        self.modelo = modelo
                        self.motor = Motor(potencia)
                        self.en_marcha = False

                    def arrancar(self):
                        self.en_marcha = True

                    def parar(self):
                        self.en_marcha = False

                    def estado(self):
                        return f"{self.modelo}: {'en marcha' if self.en_marcha else 'parado'}"
                """,
                3,
            ),
        ],
        level=2,
        daw=False,
    ),
    # ---------- Prácticas adicionales
    code(
        "poo7-14",
        CID,
        "**Práctica: agenda de contactos (agregación).** Crea:\n\n- `Contacto(nombre, telefono)`.\n- `Agenda(contactos=None)`: guarda una **copia** de la lista de contactos que recibe (o una lista vacía). Así, si quien la creó cambia su lista, la agenda no cambia.\n- `agregar(contacto)`, que añade un contacto creado fuera.\n- `buscar(nombre)`, que devuelve el teléfono del contacto con ese nombre o `None` si no está.\n- `cuantos()`, que devuelve el número de contactos.",
        """
        class Contacto:
            ...


        class Agenda:
            ...
        """,
        """
        class Contacto:
            def __init__(self, nombre, telefono):
                self.nombre = nombre
                self.telefono = telefono


        class Agenda:
            def __init__(self, contactos=None):
                self.contactos = list(contactos) if contactos else []

            def agregar(self, contacto):
                self.contactos.append(contacto)

            def buscar(self, nombre):
                for contacto in self.contactos:
                    if contacto.nombre == nombre:
                        return contacto.telefono
                return None

            def cuantos(self):
                return len(self.contactos)


        ana = Contacto("Ana", "600111222")
        agenda = Agenda([ana])
        agenda.agregar(Contacto("Luis", "600333444"))
        print(agenda.buscar("Luis"), agenda.cuantos())
        """,
        [
            case(
                'ana = Contacto("Ana", "600111222")\nag = Agenda([ana])\nag.agregar(Contacto("Luis", "600333444"))\nassert ag.buscar("Luis") == "600333444", "buscar() devuelve el teléfono del contacto"\nassert ag.buscar("Eva") is None, "buscar() devuelve None si no encuentra el nombre"\nassert ag.cuantos() == 2, "cuantos() devuelve cuántos contactos hay"\nassert ag.contactos[0] is ana, "La agenda guarda los mismos contactos que recibe, no copias de cada uno"',
            ),
            case(
                'a = Agenda()\nb = Agenda()\na.agregar(Contacto("Ana", "1"))\nassert b.cuantos() == 0, "Cada agenda nueva debe tener su propia lista vacía (no uses [] como valor por defecto)"',
                error=f"{CID}.lista-por-defecto",
            ),
            case(
                'mis = [Contacto("Ana", "1")]\nag = Agenda(mis)\nmis.append(Contacto("Intruso", "0"))\nassert ag.cuantos() == 1, "La agenda debe guardar una copia de la lista recibida: list(contactos)"',
                error=f"{CID}.copia-al-guardar",
            ),
        ],
        "Los contactos se crean fuera y la agenda solo los agrupa: es una agregación. Copiar la lista (no los contactos) protege a la agenda de cambios en la lista de quien la creó, y `None` como valor por defecto evita que todas las agendas compartan la misma lista.",
        "En `__init__`: `self.contactos = list(contactos) if contactos else []`.",
        wrong=[
            (
                """
                class Contacto:
                    def __init__(self, nombre, telefono):
                        self.nombre = nombre
                        self.telefono = telefono


                class Agenda:
                    def __init__(self, contactos=[]):
                        self.contactos = contactos

                    def agregar(self, contacto):
                        self.contactos.append(contacto)

                    def buscar(self, nombre):
                        for contacto in self.contactos:
                            if contacto.nombre == nombre:
                                return contacto.telefono
                        return None

                    def cuantos(self):
                        return len(self.contactos)
                """,
                2,
            ),
            (
                """
                class Contacto:
                    def __init__(self, nombre, telefono):
                        self.nombre = nombre
                        self.telefono = telefono


                class Agenda:
                    def __init__(self, contactos=None):
                        self.contactos = contactos if contactos is not None else []

                    def agregar(self, contacto):
                        self.contactos.append(contacto)

                    def buscar(self, nombre):
                        for contacto in self.contactos:
                            if contacto.nombre == nombre:
                                return contacto.telefono
                        return None

                    def cuantos(self):
                        return len(self.contactos)
                """,
                3,
            ),
        ],
        level=2,
        daw=False,
    ),
    code(
        "poo7-15",
        CID,
        '**Práctica: una cola por composición.** Crea la clase `Cola` (el primero que entra es el primero que sale) **sin heredar de `list`**: guarda una lista interna `_elementos` y ofrece solo:\n\n- `encolar(valor)`, que añade al final.\n- `desencolar()`, que saca y devuelve el **primero**; si la cola está vacía, lanza `IndexError("La cola está vacía")`.\n- `primero()`, que devuelve el primero sin sacarlo.\n- `tamano()`, que devuelve cuántos hay.',
        """
        class Cola:
            ...
        """,
        """
        class Cola:
            def __init__(self):
                self._elementos = []

            def encolar(self, valor):
                self._elementos.append(valor)

            def desencolar(self):
                if not self._elementos:
                    raise IndexError("La cola está vacía")
                return self._elementos.pop(0)

            def primero(self):
                return self._elementos[0]

            def tamano(self):
                return len(self._elementos)


        cola = Cola()
        for persona in ["Ana", "Luis", "Eva"]:
            cola.encolar(persona)
        print(cola.desencolar(), cola.primero(), cola.tamano())
        """,
        [
            case(
                'c = Cola()\nfor x in "abc":\n    c.encolar(x)\nassert c.tamano() == 3, "tamano() devuelve cuántos elementos hay"\nassert c.desencolar() == "a", "desencolar() saca el primero que entró"\nassert c.primero() == "b" and c.tamano() == 2, "primero() mira el siguiente sin sacarlo"',
            ),
            case(
                'try:\n    Cola().desencolar()\nexcept IndexError as e:\n    assert str(e) == "La cola está vacía", f"Mensaje del error: {e}"\nelse:\n    raise AssertionError("desencolar() en una cola vacía debe lanzar IndexError")',
            ),
            case(
                'c = Cola()\nassert not isinstance(c, list), "Una cola no es una lista: guarda la lista dentro (composición), no heredes de list"\nassert not hasattr(c, "insert") and not hasattr(c, "sort"), "La cola no debe ofrecer los métodos de una lista"\na, b = Cola(), Cola()\na.encolar(1)\nassert b.tamano() == 0, "Cada cola tiene su propia lista"',
                error=f"{CID}.herencia-por-tiene",
            ),
        ],
        "La cola **tiene** una lista y delega en ella, pero solo enseña las operaciones de una cola. Si heredara de `list`, cualquiera podría usar `insert` o `sort` y colarse en la fila.",
        "Crea la lista en `__init__` con `self._elementos = []`. Para sacar el primero, `self._elementos.pop(0)`.",
        wrong=[
            (
                """
                class Cola:
                    def __init__(self):
                        self._elementos = []

                    def encolar(self, valor):
                        self._elementos.append(valor)

                    def desencolar(self):
                        return self._elementos.pop()

                    def primero(self):
                        return self._elementos[0]

                    def tamano(self):
                        return len(self._elementos)
                """,
                1,
            ),
            (
                """
                class Cola(list):
                    def encolar(self, valor):
                        self.append(valor)

                    def desencolar(self):
                        if not self:
                            raise IndexError("La cola está vacía")
                        return self.pop(0)

                    def primero(self):
                        return self[0]

                    def tamano(self):
                        return len(self)
                """,
                3,
            ),
        ],
        level=2,
        daw=False,
    ),
    # ---------- Autoevaluación
    choice(
        "poo7-16",
        CID,
        "En el programa principal aparece `print(pedido.lineas[0].producto.precio * pedido.lineas[0].cantidad)`. ¿Cuál es la mejor corrección?",
        [
            ("Dar a `Linea` un método `subtotal()` y escribir `pedido.lineas[0].subtotal()`", None),
            (
                "Guardar el precio también en el pedido para no tener que buscarlo",
                None,
                "Duplicaría el dato: si cambia el precio, el pedido y el producto se contradirían.",
            ),
            (
                "Hacer que `Pedido` herede de `Producto` para tener el precio a mano",
                f"{CID}.herencia-por-tiene",
                "Un pedido no es un producto: heredar mezclaría dos clases que no tienen nada que ver.",
            ),
            (
                "Nada: encadenar atributos es la forma normal de usar objetos",
                f"{CID}.no-delega",
                "Así el programa depende de cómo están hechas por dentro tres clases distintas.",
            ),
        ],
        0,
        "Quien tiene los datos hace el cálculo: la línea conoce su producto y su cantidad, así que ella calcula su subtotal. El resto del programa solo se lo pide.",
        level=2,
        daw=False,
        bank=True,
        qtype="solucion",
    ),
    output(
        "poo7-17",
        CID,
        """
        class Jugador:
            def __init__(self, nombre):
                self.nombre = nombre

        class Equipo:
            def __init__(self, jugadores):
                self.jugadores = list(jugadores)

        plantilla = [Jugador("Ana"), Jugador("Eva")]
        equipo = Equipo(plantilla)
        plantilla.append(Jugador("Luis"))
        plantilla[0].nombre = "Ana G."
        print(len(equipo.jugadores), equipo.jugadores[0].nombre)
        """,
        "2 Ana G.",
        "`list(jugadores)` copia la **lista**, así que añadir a `plantilla` no afecta al equipo (sigue con 2). Pero los jugadores son los **mismos objetos**: cambiar el nombre de Ana se ve en los dos sitios.",
        traps={
            "3 Ana G.": f"{CID}.copia-al-guardar",
            "2 Ana": f"{CID}.copia-al-guardar",
            "3 Ana": None,
        },
        level=3,
        daw=False,
    ),
    # ---------- Ejercicio principal de la unidad
    code(
        "poo7-18",
        CID,
        '**Ejercicio principal: `Cliente`, `Pedido` y `Producto`.** Crea:\n\n- `Producto(nombre, precio)`.\n- `LineaPedido(producto, cantidad)` con `subtotal()`.\n- `Pedido(numero, cliente)`: guarda el cliente (asociación) y una lista `lineas` vacía. Su método `agregar(producto, cantidad)` **crea** la línea (composición); si la cantidad no es mayor que 0, lanza `ValueError`, y si el producto ya está en el pedido, suma la cantidad a su línea en vez de crear otra. `total()` delega en las líneas y `resumen()` devuelve `"Pedido 1 de Ana: 3 líneas, 70.00 €"`.\n- `Cliente(nombre, email)` con una lista `pedidos`. `nuevo_pedido(numero)` crea un `Pedido` de ese cliente, lo guarda y lo devuelve. `total_gastado()` suma el total de todos sus pedidos.',
        """
        class Producto:
            ...


        class LineaPedido:
            ...


        class Pedido:
            ...


        class Cliente:
            ...
        """,
        """
        class Producto:
            def __init__(self, nombre, precio):
                self.nombre = nombre
                self.precio = precio


        class LineaPedido:
            def __init__(self, producto, cantidad):
                self.producto = producto
                self.cantidad = cantidad

            def subtotal(self):
                return self.producto.precio * self.cantidad


        class Pedido:
            def __init__(self, numero, cliente):
                self.numero = numero
                self.cliente = cliente
                self.lineas = []

            def agregar(self, producto, cantidad):
                if cantidad <= 0:
                    raise ValueError("La cantidad debe ser mayor que 0")
                for linea in self.lineas:
                    if linea.producto is producto:
                        linea.cantidad += cantidad
                        return
                self.lineas.append(LineaPedido(producto, cantidad))

            def total(self):
                return sum(linea.subtotal() for linea in self.lineas)

            def resumen(self):
                return f"Pedido {self.numero} de {self.cliente.nombre}: {len(self.lineas)} líneas, {self.total():.2f} €"


        class Cliente:
            def __init__(self, nombre, email):
                self.nombre = nombre
                self.email = email
                self.pedidos = []

            def nuevo_pedido(self, numero):
                pedido = Pedido(numero, self)
                self.pedidos.append(pedido)
                return pedido

            def total_gastado(self):
                return sum(pedido.total() for pedido in self.pedidos)


        ana = Cliente("Ana", "ana@ies.es")
        teclado = Producto("Teclado", 25)
        raton = Producto("Ratón", 10)
        pedido = ana.nuevo_pedido(1)
        pedido.agregar(teclado, 2)
        pedido.agregar(raton, 1)
        pedido.agregar(Producto("Alfombrilla", 10), 1)
        print(pedido.resumen())
        print(ana.total_gastado())
        """,
        [
            case(
                'p = Producto("Teclado", 25)\nl = LineaPedido(p, 3)\nassert l.subtotal() == 75, f"subtotal() es precio por cantidad; devuelve {l.subtotal()!r}"\nassert l.producto is p, "La línea guarda el mismo producto que recibe"',
            ),
            case(
                'ana = Cliente("Ana", "a@b.es")\nped = Pedido(7, ana)\nassert ped.cliente is ana and ped.lineas == [], "El pedido guarda su cliente (el mismo objeto) y empieza sin líneas"\nt = Producto("Teclado", 25)\nped.agregar(t, 2)\nassert len(ped.lineas) == 1 and isinstance(ped.lineas[0], LineaPedido), "agregar() debe crear una LineaPedido dentro del pedido"\nassert ped.lineas[0].producto is t and ped.lineas[0].cantidad == 2, "La línea creada lleva el producto y la cantidad"',
            ),
            case(
                'ped = Pedido(1, Cliente("Ana", "a@b.es"))\nt = Producto("Teclado", 25)\nped.agregar(t, 2)\nped.agregar(t, 3)\nassert len(ped.lineas) == 1 and ped.lineas[0].cantidad == 5, "Si el producto ya está en el pedido, suma la cantidad en su línea"\nfor mala in (0, -1):\n    try:\n        ped.agregar(t, mala)\n    except ValueError:\n        pass\n    else:\n        raise AssertionError(f"agregar(producto, {mala}) debe lanzar ValueError")',
            ),
            case(
                'ped = Pedido(1, Cliente("Ana", "a@b.es"))\nped.agregar(Producto("Teclado", 25), 2)\nped.agregar(Producto("Ratón", 10), 1)\nped.agregar(Producto("Alfombrilla", 10), 1)\nassert ped.total() == 70, f"total() suma los subtotales; devuelve {ped.total()!r}"\nassert ped.resumen() == "Pedido 1 de Ana: 3 líneas, 70.00 €", f"resumen() devuelve {ped.resumen()!r}"\nped.lineas[0].producto.precio = 30\nassert ped.total() == 80, "total() debe delegar en las líneas cada vez, sin guardar un total calculado antes"',
                error=f"{CID}.no-delega",
            ),
            case(
                'ana = Cliente("Ana", "a@b.es")\nluis = Cliente("Luis", "l@b.es")\np1 = ana.nuevo_pedido(1)\np2 = ana.nuevo_pedido(2)\nassert isinstance(p1, Pedido) and p1.cliente is ana, "nuevo_pedido() crea un Pedido de este cliente y lo devuelve"\nassert ana.pedidos == [p1, p2] and luis.pedidos == [], "Cada cliente guarda solo sus pedidos"\np1.agregar(Producto("Teclado", 25), 2)\np2.agregar(Producto("Ratón", 10), 3)\nassert ana.total_gastado() == 80 and luis.total_gastado() == 0, f"total_gastado() suma el total de sus pedidos; devuelve {ana.total_gastado()!r}"',
                error=f"{CID}.lista-por-defecto",
            ),
        ],
        "El pedido **conoce** a su cliente (asociación) y **crea** sus líneas (composición). Cada objeto calcula con sus datos: la línea su subtotal, el pedido su total y el cliente lo que lleva gastado (delegación). Por eso un cambio de precio se nota en todos los cálculos sin tocar nada más.",
        "En `agregar`, recorre `self.lineas` buscando `linea.producto is producto`; si no la encuentras, crea `LineaPedido(producto, cantidad)`. En `nuevo_pedido`, `Pedido(numero, self)`.",
        wrong=[
            (
                """
                class Producto:
                    def __init__(self, nombre, precio):
                        self.nombre = nombre
                        self.precio = precio


                class LineaPedido:
                    def __init__(self, producto, cantidad):
                        self.producto = producto
                        self.cantidad = cantidad

                    def subtotal(self):
                        return self.producto.precio * self.cantidad


                class Pedido:
                    def __init__(self, numero, cliente):
                        self.numero = numero
                        self.cliente = cliente
                        self.lineas = []

                    def agregar(self, producto, cantidad):
                        if cantidad <= 0:
                            raise ValueError("La cantidad debe ser mayor que 0")
                        self.lineas.append(LineaPedido(producto, cantidad))

                    def total(self):
                        return sum(linea.subtotal() for linea in self.lineas)

                    def resumen(self):
                        return f"Pedido {self.numero} de {self.cliente.nombre}: {len(self.lineas)} líneas, {self.total():.2f} €"


                class Cliente:
                    def __init__(self, nombre, email):
                        self.nombre = nombre
                        self.email = email
                        self.pedidos = []

                    def nuevo_pedido(self, numero):
                        pedido = Pedido(numero, self)
                        self.pedidos.append(pedido)
                        return pedido

                    def total_gastado(self):
                        return sum(pedido.total() for pedido in self.pedidos)
                """,
                3,
            ),
            (
                """
                class Producto:
                    def __init__(self, nombre, precio):
                        self.nombre = nombre
                        self.precio = precio


                class LineaPedido:
                    def __init__(self, producto, cantidad):
                        self.producto = producto
                        self.cantidad = cantidad

                    def subtotal(self):
                        return self.producto.precio * self.cantidad


                class Pedido:
                    def __init__(self, numero, cliente):
                        self.numero = numero
                        self.cliente = cliente
                        self.lineas = []
                        self._total = 0

                    def agregar(self, producto, cantidad):
                        if cantidad <= 0:
                            raise ValueError("La cantidad debe ser mayor que 0")
                        self._total += producto.precio * cantidad
                        for linea in self.lineas:
                            if linea.producto is producto:
                                linea.cantidad += cantidad
                                return
                        self.lineas.append(LineaPedido(producto, cantidad))

                    def total(self):
                        return self._total

                    def resumen(self):
                        return f"Pedido {self.numero} de {self.cliente.nombre}: {len(self.lineas)} líneas, {self.total():.2f} €"


                class Cliente:
                    def __init__(self, nombre, email):
                        self.nombre = nombre
                        self.email = email
                        self.pedidos = []

                    def nuevo_pedido(self, numero):
                        pedido = Pedido(numero, self)
                        self.pedidos.append(pedido)
                        return pedido

                    def total_gastado(self):
                        return sum(pedido.total() for pedido in self.pedidos)
                """,
                4,
            ),
            (
                """
                class Producto:
                    def __init__(self, nombre, precio):
                        self.nombre = nombre
                        self.precio = precio


                class LineaPedido:
                    def __init__(self, producto, cantidad):
                        self.producto = producto
                        self.cantidad = cantidad

                    def subtotal(self):
                        return self.producto.precio * self.cantidad


                class Pedido:
                    def __init__(self, numero, cliente):
                        self.numero = numero
                        self.cliente = cliente
                        self.lineas = []

                    def agregar(self, producto, cantidad):
                        if cantidad <= 0:
                            raise ValueError("La cantidad debe ser mayor que 0")
                        for linea in self.lineas:
                            if linea.producto is producto:
                                linea.cantidad += cantidad
                                return
                        self.lineas.append(LineaPedido(producto, cantidad))

                    def total(self):
                        return sum(linea.subtotal() for linea in self.lineas)

                    def resumen(self):
                        return f"Pedido {self.numero} de {self.cliente.nombre}: {len(self.lineas)} líneas, {self.total():.2f} €"


                class Cliente:
                    def __init__(self, nombre, email, pedidos=[]):
                        self.nombre = nombre
                        self.email = email
                        self.pedidos = pedidos

                    def nuevo_pedido(self, numero):
                        pedido = Pedido(numero, self)
                        self.pedidos.append(pedido)
                        return pedido

                    def total_gastado(self):
                        return sum(pedido.total() for pedido in self.pedidos)
                """,
                5,
            ),
        ],
        level=3,
        daw=False,
    ),
    # ---------- Banco de preguntas de la unidad (cuestionario)
    choice(
        "poo7-19",
        CID,
        "Tras ejecutar `p = Pedido(ana)`, cuyo constructor hace `self.cliente = cliente`, ¿qué guarda `p.cliente`?",
        [
            ("Una referencia al mismo objeto que `ana`", None),
            (
                "Una copia independiente de `ana`",
                f"{CID}.copia-al-guardar",
                "Python nunca copia un objeto al asignarlo: `p.cliente is ana` da `True`.",
            ),
            (
                "El texto con el nombre de `ana`",
                None,
                "Se guarda el objeto entero, no uno de sus atributos.",
            ),
            (
                "Nada hasta que se llame a un método del pedido",
                None,
                "La asignación se hace al ejecutar el constructor, al crear el pedido.",
            ),
        ],
        0,
        "Asignar un objeto a un atributo guarda una referencia: `p.cliente` y `ana` son dos nombres para el mismo cliente.",
        level=1,
        daw=False,
        bank=True,
        qtype="codigo",
    ),
    choice(
        "poo7-20",
        CID,
        "¿Qué línea hace que la relación entre `Factura` y sus `Linea` sea una **composición**?",
        [
            ("La línea 7: la factura crea cada `Linea` dentro de su propio método", None),
            (
                "La línea 3: `self.cliente = cliente`",
                f"{CID}.relacion-es-sintaxis",
                "Esa línea relaciona la factura con su cliente, que viene de fuera: es una asociación.",
            ),
            (
                "La línea 4: `self.lineas = []`",
                f"{CID}.relacion-es-sintaxis",
                "Crear una lista vacía no dice nada aún: lo que cuenta es quién crea las líneas que se meten en ella.",
            ),
            (
                "Ninguna: para que haya composición `Linea` tendría que heredar de `Factura`",
                f"{CID}.herencia-por-tiene",
                "La composición no usa herencia: es una relación «tiene un» entre objetos.",
            ),
        ],
        0,
        "Lo que convierte la relación en composición es que el todo **crea** sus partes: nadie de fuera crea una `Linea` y se la pasa. Así las líneas nacen y viven con su factura.",
        code="""
        class Factura:
            def __init__(self, cliente):
                self.cliente = cliente
                self.lineas = []

            def agregar(self, concepto, importe):
                self.lineas.append(Linea(concepto, importe))
        """,
        level=3,
        daw=False,
        bank=True,
        qtype="codigo",
    ),
    choice(
        "poo7-21",
        CID,
        "¿Qué muestra este programa?",
        [
            ("Pepa Pepa", None),
            (
                "Pepa Pep",
                f"{CID}.copia-al-guardar",
                "`a.duena` y `b.duena` son la misma persona: el cambio se ve desde los dos.",
            ),
            (
                "Pep Pep",
                None,
                "El nombre cambia antes del `print`, y los dos perros apuntan a esa misma persona.",
            ),
            (
                "AttributeError",
                None,
                "Los dos perros tienen el atributo `duena`, que guarda un objeto `Persona`.",
            ),
        ],
        0,
        "Los dos perros guardan una referencia a la **misma** persona. Al cambiar su nombre a través de `a`, `b` también lo ve.",
        code="""
        class Persona:
            def __init__(self, nombre):
                self.nombre = nombre

        class Perro:
            def __init__(self, duena):
                self.duena = duena

        pepa = Persona("Pep")
        a = Perro(pepa)
        b = Perro(pepa)
        a.duena.nombre = "Pepa"
        print(a.duena.nombre, b.duena.nombre)
        """,
        level=1,
        daw=False,
        bank=True,
        qtype="prediccion",
    ),
    choice(
        "poo7-22",
        CID,
        "¿Qué muestra este programa?",
        [
            ("2 2", None),
            (
                "1 1",
                f"{CID}.lista-por-defecto",
                "Las dos clases usan la misma lista por defecto, así que cada `apuntar` se suma a la misma.",
            ),
            (
                "2 0",
                f"{CID}.lista-por-defecto",
                "`b` se creó sin lista y recibe la lista por defecto, la misma que `a`.",
            ),
            (
                "1 0",
                f"{CID}.lista-por-defecto",
                "La lista `[]` del valor por defecto se crea una sola vez y la comparten `a` y `b`.",
            ),
        ],
        0,
        "`alumnos=[]` crea la lista **una vez**, al definir el método. `a` y `b` comparten esa lista: después de dos `apuntar`, los dos ven 2 alumnos.",
        code="""
        class Clase:
            def __init__(self, alumnos=[]):
                self.alumnos = alumnos

            def apuntar(self, nombre):
                self.alumnos.append(nombre)

        a = Clase()
        b = Clase()
        a.apuntar("Ana")
        b.apuntar("Luis")
        print(len(a.alumnos), len(b.alumnos))
        """,
        level=2,
        daw=False,
        bank=True,
        qtype="prediccion",
    ),
    choice(
        "poo7-23",
        CID,
        "¿Qué muestra este programa?",
        [
            ("90 2", None),
            (
                "75 2",
                f"{CID}.no-delega",
                "`total()` se calcula al llamarlo y pregunta a cada línea por el precio actual del producto: ya es 40.",
            ),
            (
                "90 3",
                None,
                "Se han agregado dos productos, así que el pedido tiene 2 líneas.",
            ),
            (
                "50 2",
                None,
                "Cada línea multiplica por su cantidad: 40 × 2 + 10 × 1.",
            ),
        ],
        0,
        "Las líneas guardan una referencia al producto, no su precio copiado. Cuando el teclado pasa a 40 €, `total()` ya lo usa: 40 × 2 + 10 × 1 = 90, en 2 líneas.",
        code="""
        class Producto:
            def __init__(self, precio):
                self.precio = precio

        class Linea:
            def __init__(self, producto, cantidad):
                self.producto = producto
                self.cantidad = cantidad

            def subtotal(self):
                return self.producto.precio * self.cantidad

        class Pedido:
            def __init__(self):
                self.lineas = []

            def agregar(self, producto, cantidad):
                self.lineas.append(Linea(producto, cantidad))

            def total(self):
                return sum(l.subtotal() for l in self.lineas)

        teclado = Producto(25)
        raton = Producto(10)
        p = Pedido()
        p.agregar(teclado, 2)
        p.agregar(raton, 1)
        teclado.precio = 40
        print(p.total(), len(p.lineas))
        """,
        level=3,
        daw=False,
        bank=True,
        qtype="prediccion",
    ),
    choice(
        "poo7-24",
        CID,
        "Cada biblioteca nueva debería empezar sin libros, pero la segunda ya tiene los de la primera. ¿Cuál es el fallo?",
        [
            (
                "El valor por defecto `libros=[]` se crea una vez y lo comparten todas las bibliotecas",
                None,
            ),
            (
                "Falta llamar a `super().__init__()`",
                None,
                "`Biblioteca` no hereda de nadie más que `object`; no es la causa.",
            ),
            (
                "`append` copia la lista en vez de añadir",
                None,
                "`append` añade a la lista que hay; el problema es que esa lista es la misma para todas.",
            ),
            (
                "Hay que guardar los libros como atributo de clase",
                None,
                "Un atributo de clase también lo compartirían todas: es justo el problema que hay que evitar.",
            ),
        ],
        0,
        "Los valores por defecto se evalúan una sola vez, al definir el método. Usa `libros=None` y, dentro, `self.libros = list(libros) if libros else []`.",
        code="""
        class Biblioteca:
            def __init__(self, libros=[]):
                self.libros = libros

            def donar(self, libro):
                self.libros.append(libro)
        """,
        level=2,
        daw=False,
        bank=True,
        qtype="error",
    ),
    choice(
        "poo7-25",
        CID,
        "`Pila` hereda de `list` para aprovechar `append` y `pop`. ¿Qué problema de diseño tiene?",
        [
            (
                "La pila hereda todos los métodos de una lista, como `insert(0, x)`, y se puede saltar su regla «solo se saca el último»",
                None,
            ),
            (
                "No funciona: no se puede heredar de `list`",
                None,
                "Sí se puede heredar de `list`; el problema no es técnico, es de diseño.",
            ),
            (
                "Ninguno: si funciona, el diseño es correcto",
                f"{CID}.herencia-por-tiene",
                "Funcionar no basta: una pila no «es una» lista con todas sus operaciones.",
            ),
            (
                "`pop` saca el primer elemento en vez del último",
                None,
                "`pop()` sin argumentos saca el último, así que eso sí es correcto.",
            ),
        ],
        0,
        "Con herencia la pila **es una** lista y ofrece todo lo de una lista. Con composición (`self._elementos = []`) solo enseña `apilar`, `desapilar` y `cima`, y su regla no se puede romper.",
        code="""
        class Pila(list):
            def apilar(self, x):
                self.append(x)

            def desapilar(self):
                return self.pop()

        p = Pila()
        p.apilar("abajo")
        p.insert(0, "colado")
        """,
        level=3,
        daw=False,
        bank=True,
        qtype="error",
    ),
    choice(
        "poo7-26",
        CID,
        "Un `Equipo` guarda directamente la lista que recibe. Quien la creó la sigue usando y los cambios se cuelan en el equipo. ¿Qué cambio lo evita?",
        [
            ("`self.jugadores = list(jugadores)`", None),
            (
                "`self.jugadores = jugadores`",
                f"{CID}.copia-al-guardar",
                "Es lo que ya hace: guarda la misma lista y comparte los cambios.",
            ),
            (
                "`self.jugadores = jugadores.copy` (sin paréntesis)",
                None,
                "Sin paréntesis se guarda el método `copy`, no una lista copiada.",
            ),
            (
                "`self.jugadores = []` y no usar el parámetro",
                None,
                "Así se pierden los jugadores que se le pasan al crear el equipo.",
            ),
        ],
        0,
        "`list(jugadores)` crea una lista nueva con los mismos jugadores. El equipo controla su lista, aunque los jugadores sigan siendo los mismos objetos (agregación).",
        code_options=True,
        level=3,
        daw=False,
        bank=True,
        qtype="solucion",
    ),
    choice(
        "poo7-27",
        CID,
        "¿En qué pareja la relación es una **composición**?",
        [
            ("Una casa y sus habitaciones: las crea la casa y no existen sin ella", None),
            (
                "Un equipo y sus jugadores",
                None,
                "Los jugadores existen antes y pueden cambiar de equipo: es una agregación.",
            ),
            (
                "Un pedido y su cliente",
                None,
                "El cliente existe por su cuenta y tiene muchos pedidos: es una asociación.",
            ),
            (
                "Un perro y un animal",
                f"{CID}.herencia-por-tiene",
                "«Un perro es un animal» es herencia, no una relación entre objetos.",
            ),
        ],
        0,
        "En la composición las partes nacen y mueren con el todo. Una habitación no tiene sentido fuera de su casa.",
        level=1,
        daw=False,
        bank=True,
        qtype="diseno",
    ),
]

# Errores típicos (slug, etiqueta, por qué, qué pensar, cómo evitarlo)
ERRORS = [
    (
        "copia-al-guardar",
        "Cree que guardar un objeto en un atributo lo copia",
        "Un atributo guarda una referencia: el mismo objeto se ve desde todos los sitios que lo guardan, y sus cambios también.",
        "¿Hay aquí uno o dos objetos? ¿Dónde se creó cada uno?",
        "Comprueba con `is` si dos nombres apuntan al mismo objeto; copia la lista con `list(...)` cuando necesites una propia.",
    ),
    (
        "lista-por-defecto",
        "Usa una lista como valor por defecto de un parámetro",
        "El valor por defecto se crea una sola vez, al definir la función, y todos los objetos creados sin ese argumento comparten la misma lista.",
        "¿Qué pasará al crear un segundo objeto sin pasarle la lista?",
        "Pon `None` como valor por defecto y crea la lista dentro: `self.x = list(x) if x else []`.",
    ),
    (
        "herencia-por-tiene",
        "Usa herencia cuando la relación es «tiene un»",
        "Heredar dice «es un»: la subclase recibe todos los métodos de la otra y se puede usar en su lugar, aunque no tenga sentido.",
        "¿Suena bien la frase «A es un B»? ¿O es «A tiene un B»?",
        "Si es «tiene un», guarda el otro objeto en un atributo y delega en él.",
    ),
    (
        "no-delega",
        "Hace desde fuera lo que el objeto ya sabe hacer",
        "Repetir un cálculo con los atributos de otro objeto (o guardar una copia del resultado) hace que dos sitios tengan que estar de acuerdo, y tarde o temprano se contradicen.",
        "¿Qué objeto tiene estos datos? ¿Tiene ya un método para esto?",
        "Pídeselo al objeto que tiene los datos: `linea.subtotal()`, `motor.encender()`.",
    ),
    (
        "relacion-es-sintaxis",
        "Cree que asociación, agregación y composición son instrucciones de Python",
        "Son ideas de diseño. En el código siempre hay un atributo que apunta a otro objeto; lo que cambia es quién crea ese objeto y cuánto vive.",
        "¿Quién crea esta parte? ¿Existiría sin el todo?",
        "Para clasificar una relación, mira dónde se crea el objeto y qué pasa con él cuando el todo desaparece.",
    ),
]

# Las preguntas del banco de esta unidad ya nacen con su tipo y su nivel: no hay que etiquetar ninguna antigua
BANK_TAGS: dict = {}
