# ruff: noqa: E501
"""Unidad 8 del módulo de POO: métodos especiales de Python.

Concepto `poo-metodos-especiales` (área `poo`): los métodos con dos guiones bajos que Python llama por
su cuenta (`print`, `len`, `==`, `in`, `for`). Se separan los esenciales (`__str__`, `__repr__`,
`__eq__`, `__len__`) de los avanzados (`__contains__`, `__iter__`, `__next__`). La salida de los
ejemplos la obtiene build_learning.py ejecutándolos.
"""

from exercises import bug, c, case, choice, code, fill, output
from poo_common import practice, proposed, ref

CID = "poo-metodos-especiales"

CONCEPT = {
    "id": CID,
    "title": "Métodos especiales de Python",
    "area": "poo",
    "requires": ["poo", "poo-atributos-metodos"],
    "daw": 2,
    "ut": "prog-ut5",
    "lessons": ["poo"],
    "summary": "Que tus objetos funcionen con `print`, `len`, `==`, `in` y `for` como los de Python: los métodos especiales.",
    "when": "Cuando quieres que un objeto se imprima de forma legible, se compare por su contenido, diga cuántos elementos tiene o se pueda recorrer con `for`, igual que una lista.",
    "example": {
        "code": c(
            """
            class Carrito:
                def __init__(self):
                    self.productos = []

                def agregar(self, producto):
                    self.productos.append(producto)

                def __len__(self):                  # len(carrito)
                    return len(self.productos)

                def __contains__(self, producto):   # producto in carrito
                    return producto in self.productos

                def __str__(self):                  # print(carrito) y str(carrito)
                    return f"Carrito con {len(self)} productos"


            carrito = Carrito()
            carrito.agregar("pan")
            carrito.agregar("leche")
            print(carrito)
            print(len(carrito), "pan" in carrito)
            """
        ),
        "lines": [
            [8, "Python llama a `__len__` cuando escribes `len(carrito)`."],
            [11, "`in` usa `__contains__`."],
            [14, "`print` usa `__str__` para saber qué texto mostrar."],
            [21, "Nadie llama a los métodos especiales por su nombre: los llama Python."],
        ],
    },
    "errors": [],
    "related": ["poo", "poo-atributos-metodos", "listas"],
}

UNIT = {
    "unit": {"module": "poo", "number": 8},
    "objectives": [
        "Explicar qué es un método especial y qué instrucción hace que Python lo llame.",
        "Dar a una clase `__str__` para el usuario y `__repr__` para el programador.",
        "Comparar objetos por su contenido con `__eq__` y distinguir `==` de `is`.",
        "Usar `__len__` y `__contains__` para que un objeto contenedor funcione con `len()` e `in`.",
        "(Avanzado) Hacer un objeto recorrible con `__iter__` y entender qué hace `__next__`.",
    ],
    "prior": "La Unidad 2 (clases, `__init__` y `__str__`) y la Unidad 3 (atributos y métodos).",
    "key": [
        [
            "Método especial",
            "Un método con dos guiones bajos delante y detrás (`__len__`) que Python llama por su cuenta en ciertas operaciones.",
        ],
        ["`__str__`", "El texto legible para el usuario: lo usan `print()` y `str()`."],
        [
            "`__repr__`",
            "El texto para el programador: lo usan la consola, las listas al imprimirse y `repr()`.",
        ],
        ["`__eq__`", "Decide si dos objetos son iguales con `==`. Sin él, `==` compara identidad."],
        ["`__len__` y `__contains__`", "Hacen funcionar `len(objeto)` y `x in objeto`."],
        [
            "Iterador",
            "Un objeto que va dando elementos con `__next__` hasta lanzar `StopIteration`; `for` lo pide con `__iter__`.",
        ],
    ],
    "sections": [
        {
            "id": f"{CID}.que-son",
            "title": "Qué son y cuándo los llama Python",
            "theory": "Ya conoces dos métodos especiales: `__init__` y `__str__`. Tienen **dos guiones bajos** delante y detrás y una particularidad: **no los llamas tú**, los llama Python cuando usas ciertas instrucciones.\n\n| Escribes | Python llama a |\n|---|---|\n| `print(x)` o `str(x)` | `x.__str__()` |\n| `repr(x)` o la consola | `x.__repr__()` |\n| `a == b` | `a.__eq__(b)` |\n| `len(x)` | `x.__len__()` |\n| `y in x` | `x.__contains__(y)` |\n| `for y in x:` | `x.__iter__()` |\n\n- Escribe tú `len(carrito)`, no `carrito.__len__()`: el resultado es el mismo, pero es más claro y es lo que espera cualquier programador de Python.\n- El nombre tiene que ser **exacto**. Si escribes `_str_` o `__str`, Python no lo reconoce y sigue usando el comportamiento por defecto.\n- No inventes métodos con dos guiones bajos (`__total__`): ese tipo de nombres está reservado para Python.",
            "examples": [
                {
                    "code": c(
                        """
                        class Lista:
                            def __init__(self, *elementos):
                                self.elementos = list(elementos)

                            def __len__(self):
                                return len(self.elementos)


                        class SinLen:
                            pass


                        compra = Lista("pan", "leche", "huevos")
                        print(len(compra))
                        try:
                            len(SinLen())
                        except TypeError:
                            print("SinLen no tiene __len__: len() no sabe qué hacer")
                        """
                    ),
                    "lines": [
                        [5, "Al definir `__len__`, la clase acepta `len()`."],
                        [14, "`len(compra)` hace que Python llame a `compra.__len__()`."],
                        [16, "Sin `__len__`, `len()` da `TypeError`."],
                    ],
                }
            ],
            "quiz": ["poo8-01", "poo8-02", "poo8-03"],
        },
        {
            "id": f"{CID}.esenciales",
            "title": "Los esenciales: __str__, __repr__, __eq__ y __len__",
            "theory": "Son los que más vas a usar.\n\n**`__str__` y `__repr__`.** Los dos devuelven un **texto** (con `return`, no con `print`), pero para públicos distintos:\n\n- `__str__` es para el **usuario**: `Pan (1.20 €)`. Lo usan `print()`, `str()` y los f-strings.\n- `__repr__` es para el **programador**: `Producto('Pan', 1.2)`, a ser posible con el aspecto del código que crea el objeto. Lo usan la consola, `repr()` y **las listas** al imprimirse.\n- Si solo defines `__repr__`, `print` también lo usa. Si no defines ninguno, verás algo como `<__main__.Producto object at 0x…>`.\n\n**`__eq__`.** Sin él, `a == b` solo es `True` si `a` y `b` son **el mismo objeto** (como `is`). Con él decides qué hace iguales a dos objetos:\n\n```\ndef __eq__(self, otro):\n    if not isinstance(otro, Producto):\n        return NotImplemented\n    return self.nombre == otro.nombre and self.precio == otro.precio\n```\n\n`NotImplemented` le dice a Python «no sé compararme con eso», y entonces `Producto(...) == 3` da `False` en vez de un error. Ojo: una clase que define `__eq__` y no define `__hash__` ya no puede usarse en un `set` ni como clave de diccionario.\n\n**`__len__`.** Devuelve un **entero mayor o igual que 0**: el número de elementos del objeto. Tiene sentido en objetos que son colecciones (un carrito, una lista de reproducción), no en cualquier clase.",
            "examples": [
                {
                    "code": c(
                        """
                        class Producto:
                            def __init__(self, nombre, precio):
                                self.nombre = nombre
                                self.precio = precio

                            def __str__(self):
                                return f"{self.nombre} ({self.precio:.2f} €)"

                            def __repr__(self):
                                return f"Producto({self.nombre!r}, {self.precio!r})"

                            def __eq__(self, otro):
                                if not isinstance(otro, Producto):
                                    return NotImplemented
                                return self.nombre == otro.nombre and self.precio == otro.precio


                        pan = Producto("Pan", 1.2)
                        print(pan)
                        print([pan, Producto("Leche", 0.9)])
                        print(pan == Producto("Pan", 1.2), pan is Producto("Pan", 1.2))
                        print(pan == "Pan")
                        """
                    ),
                    "lines": [
                        [7, "`__str__` devuelve el texto para el usuario."],
                        [
                            10,
                            "`!r` pone las comillas: el texto parece el código que crea el objeto.",
                        ],
                        [14, "Con otro tipo de objeto, deja que Python responda `False`."],
                        [20, "Una lista muestra sus elementos con `__repr__`, no con `__str__`."],
                        [
                            21,
                            "Iguales por contenido (`==`), pero son dos objetos distintos (`is`).",
                        ],
                    ],
                }
            ],
            "quiz": ["poo8-04", "poo8-05", "poo8-06"],
        },
        {
            "id": f"{CID}.avanzados",
            "title": "Avanzados: __contains__, __iter__ y __next__",
            "theory": "Estos métodos convierten tu objeto en un **contenedor** que se usa como una lista. Son de nivel avanzado: primero domina los esenciales.\n\n**`__contains__(self, elemento)`** responde a `elemento in objeto` y devuelve `True` o `False`.\n\n**`__iter__(self)`** hace que el objeto se pueda recorrer con `for`. Debe devolver un **iterador**. La forma más sencilla es delegar en la lista que guardas dentro:\n\n```\ndef __iter__(self):\n    return iter(self.canciones)\n```\n\n**`__next__(self)`** es lo que tiene un iterador: cada llamada devuelve el siguiente elemento y, cuando no quedan, lanza `StopIteration`. Así funciona `for` por dentro: pide un iterador con `__iter__` y llama a `__next__` hasta que llega `StopIteration`.\n\n- `__iter__` debe devolver un iterador, no una lista: `return self.canciones` da `TypeError`.\n- Un iterador escrito a mano (con `__iter__` que devuelve `self` y su `__next__`) **se gasta**: después de recorrerlo una vez ya no da más elementos.",
            "examples": [
                {
                    "code": c(
                        """
                        class Playlist:
                            def __init__(self, nombre):
                                self.nombre = nombre
                                self.canciones = []

                            def agregar(self, cancion):
                                self.canciones.append(cancion)

                            def __contains__(self, cancion):
                                return cancion in self.canciones

                            def __iter__(self):
                                return iter(self.canciones)     # delega en la lista


                        class CuentaAtras:                      # un iterador escrito a mano
                            def __init__(self, desde):
                                self.actual = desde

                            def __iter__(self):
                                return self

                            def __next__(self):
                                if self.actual == 0:
                                    raise StopIteration
                                self.actual -= 1
                                return self.actual + 1


                        lista = Playlist("Estudio")
                        lista.agregar("Lo-fi 1")
                        lista.agregar("Lo-fi 2")
                        print("Lo-fi 2" in lista)
                        for cancion in lista:
                            print(cancion)
                        print(list(CuentaAtras(3)))
                        """
                    ),
                    "lines": [
                        [9, "`in` llama a `__contains__`."],
                        [13, "`iter()` sobre la lista interna devuelve un iterador ya hecho."],
                        [24, "Cuando no quedan elementos, el iterador avisa con `StopIteration`."],
                        [34, "`for` usa `__iter__` y después `__next__` hasta `StopIteration`."],
                    ],
                }
            ],
            "quiz": ["poo8-07", "poo8-08", "poo8-09"],
        },
    ],
    "guided": ["poo8-10"],
    "autonomous": ["poo8-15"],
    "extras": ["poo8-11", "poo8-12"],
    "selfcheck": ["poo8-13", "poo8-14"],
    "recap": [
        "Los métodos especiales llevan dos guiones bajos delante y detrás y los llama Python, no tú.",
        "`__str__` es el texto para el usuario y `__repr__` el del programador; los dos devuelven un `str`.",
        "Una lista de objetos se imprime con el `__repr__` de cada uno.",
        "Sin `__eq__`, `==` compara identidad; con él, compara lo que tú decidas. Devuelve `NotImplemented` con otros tipos.",
        "`__len__` devuelve un entero y `__contains__` un booleano.",
        "(Avanzado) `__iter__` devuelve un iterador; el iterador da elementos con `__next__` hasta `StopIteration`.",
    ],
    "pass": {
        "minScore": 0.7,
        "required": ["poo8-10", "poo8-15"],
        "text": [
            "Resolver el ejercicio guiado (puntos) y el ejercicio principal (el carrito de la compra) con todos los tests superados.",
            "Dominar la unidad según el motor: al menos un 70 % de aciertos recientes en sus ejercicios, con varios tipos distintos.",
            "Completar las lecciones ayuda a organizarte, pero **no** demuestra la competencia: la demuestran los ejercicios.",
        ],
    },
    "practices": [
        practice(
            "Da a tus clases al menos un `__repr__` que diga qué objeto es y con qué datos.",
            "Al depurar o imprimir una lista verás `Producto('Pan', 1.2)` en vez de una dirección de memoria.",
        ),
        practice(
            "Haz que `__str__` y `__repr__` devuelvan el texto con `return`; nunca uses `print` dentro.",
            "Python necesita recibir un `str`; si el método no devuelve nada, da `TypeError`.",
        ),
        practice(
            "En `__eq__`, devuelve `NotImplemented` si el otro objeto no es de tu clase.",
            "Así comparar con otro tipo da `False` en vez de un error por un atributo que no existe.",
        ),
        practice(
            "Usa `len(x)`, `str(x)` e `in` en tu código, no `x.__len__()` ni `x.__str__()`.",
            "Es más legible y es la forma que espera cualquier programador de Python.",
        ),
        practice(
            "Define solo los métodos especiales que tienen sentido para la clase.",
            "`len()` en una persona o `in` en una fecha confunden más que ayudan.",
        ),
    ],
    "references": [
        ref(
            "py-tutorial-classes",
            "9.8. Iteradores",
            [
                "`for` llama a `iter()` y después a `__next__()` hasta `StopIteration`",
                "una clase con `__iter__` que devuelve `self` y su `__next__`",
            ],
        ),
        ref(
            "py-dataclasses",
            "El decorador dataclass y los métodos que genera",
            [
                "`@dataclass` puede generar `__init__`, `__repr__` y `__eq__` a partir de los atributos"
            ],
        ),
        ref(
            "py-faq-programming",
            "¿Cuándo puedo fiarme de las comparaciones de identidad con el operador *is*?",
            ["diferencia entre comparar identidad (`is`) e igualdad (`==`)"],
        ),
    ],
    "bank": [
        "poo8-02",
        "poo8-05",
        "poo8-08",
        "poo8-13",
        "poo8-16",
        "poo8-17",
        "poo8-18",
        "poo8-19",
        "poo8-20",
        "poo8-21",
        "poo8-22",
        "poo8-23",
        "poo8-24",
        "poo8-25",
        "poo8-26",
    ],
    "curriculum": [
        proposed(
            "0485-RA4-c",
            "Se definen métodos especiales (`__str__`, `__eq__`, `__len__`…) en las clases.",
        ),
        proposed(
            "0485-RA6-d",
            "Se recorren objetos propios con iteradores (`__iter__` y `__next__`).",
        ),
        proposed(
            "0485-RA4-e",
            "Se escriben programas que usan objetos propios con `print`, `len`, `==` e `in`.",
        ),
    ],
}

EXERCISES = [
    # ---------- Lección «Qué son y cuándo los llama Python»
    output(
        "poo8-01",
        CID,
        """
        class Equipo:
            def __init__(self, *jugadores):
                self.jugadores = list(jugadores)

            def __len__(self):
                return len(self.jugadores)

        e = Equipo("Ana", "Eva", "Luis")
        print(len(e) * 2)
        """,
        "6",
        "`len(e)` hace que Python llame a `e.__len__()`, que devuelve 3. Por 2, 6.",
        traps={"3": None, "TypeError": f"{CID}.llamada-directa"},
        level=1,
        daw=False,
    ),
    choice(
        "poo8-02",
        CID,
        "¿Quién llama normalmente a un método especial como `__len__`?",
        [
            ("Python, cuando el programa usa `len(objeto)`", None),
            (
                "El programador, escribiendo siempre `objeto.__len__()`",
                f"{CID}.llamada-directa",
                "Funciona, pero no es lo habitual: se escribe `len(objeto)` y Python llama al método.",
            ),
            (
                "El constructor `__init__`, al crear el objeto",
                None,
                "`__init__` solo prepara el objeto; no llama a los demás métodos especiales.",
            ),
            (
                "Nadie: los métodos con guiones bajos son privados y no se ejecutan",
                None,
                "Los dos guiones bajos delante **y detrás** marcan un método especial, no uno privado.",
            ),
        ],
        0,
        "Los métodos especiales son la forma en que Python conecta sus instrucciones (`len`, `print`, `==`, `in`, `for`) con tus clases. Tú usas la instrucción y Python llama al método.",
        level=1,
        daw=False,
        bank=True,
        qtype="teoria",
    ),
    bug(
        "poo8-03",
        CID,
        "Debería mostrar `Libro: Dune`, pero muestra algo como `<__main__.Libro object at 0x…>`. ¿Qué línea falla?",
        """
        class Libro:
            def __init__(self, titulo):
                self.titulo = titulo

            def _str_(self):
                return f"Libro: {self.titulo}"

        print(Libro("Dune"))
        """,
        5,
        "    def __str__(self):",
        "Libro: Dune",
        f"{CID}.nombre-especial-mal",
        "El método se llama `__str__`, con **dos** guiones bajos a cada lado. Con otro nombre, Python no lo reconoce y `print` usa el texto por defecto.",
        level=1,
        daw=False,
    ),
    # ---------- Lección «Los esenciales»
    output(
        "poo8-04",
        CID,
        """
        class Nota:
            def __init__(self, valor):
                self.valor = valor

            def __str__(self):
                return f"{self.valor} puntos"

            def __repr__(self):
                return f"Nota({self.valor})"

        notas = [Nota(7), Nota(9)]
        print(notas[0])
        print(notas)
        """,
        "7 puntos\n[Nota(7), Nota(9)]",
        "`print(notas[0])` usa `__str__`. Al imprimir la **lista**, cada elemento se muestra con su `__repr__`.",
        traps={
            "7 puntos\n[7 puntos, 9 puntos]": f"{CID}.lista-usa-str",
            "Nota(7)\n[Nota(7), Nota(9)]": None,
        },
        level=2,
        daw=False,
    ),
    choice(
        "poo8-05",
        CID,
        "¿Cuál es un `__eq__` correcto para que dos `Punto` sean iguales si tienen las mismas coordenadas?",
        [
            (
                "`if not isinstance(otro, Punto): return NotImplemented` y después `return self.x == otro.x and self.y == otro.y`",
                None,
            ),
            (
                "`return self is otro`",
                f"{CID}.eq-identidad",
                "Eso es lo que ya hace `==` sin `__eq__`: compara si son el mismo objeto, no sus coordenadas.",
            ),
            (
                "`print(self.x == otro.x and self.y == otro.y)`",
                f"{CID}.imprime-en-vez-de-devolver",
                "`__eq__` tiene que devolver el resultado; con `print` devuelve `None` y la comparación falla.",
            ),
            (
                "`return self.x == otro.x and self.y == otro.y`, sin más",
                None,
                "Funciona entre puntos, pero `Punto(1, 2) == 5` da `AttributeError` porque un número no tiene `x`.",
            ),
        ],
        0,
        "`__eq__` compara el contenido y devuelve un booleano. Con `NotImplemented` para otros tipos, `Punto(1, 2) == 5` da `False` sin error.",
        level=2,
        daw=False,
        bank=True,
        qtype="codigo",
    ),
    fill(
        "poo8-06",
        CID,
        "Completa `__len__` para que `len(carrito)` devuelva cuántos productos hay.",
        """
        class Carrito:
            def __init__(self):
                self.productos = ["pan", "leche"]

            def __len__(self):
                return ___

        print(len(Carrito()))
        """,
        ["len(self.productos)"],
        "`__len__` delega en la lista interna: `return len(self.productos)`. Devuelve un entero, como exige `len()`.",
        expect="2",
        traps={"self.productos": f"{CID}.len-no-entero", "len(self)": None, "len(productos)": None},
        level=1,
        daw=False,
    ),
    # ---------- Lección «Avanzados»
    output(
        "poo8-07",
        CID,
        """
        class Rango:
            def __init__(self, minimo, maximo):
                self.minimo = minimo
                self.maximo = maximo

            def __contains__(self, valor):
                return self.minimo <= valor <= self.maximo

        aprobado = Rango(5, 10)
        print(7 in aprobado, 4 in aprobado)
        """,
        "True False",
        "`7 in aprobado` llama a `aprobado.__contains__(7)`, que comprueba si está entre 5 y 10. El 4 no lo está.",
        traps={"True True": None, "False False": None, "TypeError": None},
        level=2,
        daw=False,
    ),
    choice(
        "poo8-08",
        CID,
        "¿Qué hace cada método en un objeto que se recorre con `for`?",
        [
            (
                "`__iter__` devuelve un iterador y el iterador da cada elemento con `__next__` hasta lanzar `StopIteration`",
                None,
            ),
            (
                "`__next__` devuelve una lista con todos los elementos de una vez",
                None,
                "`__next__` da **un** elemento cada vez que se le llama.",
            ),
            (
                "`__iter__` imprime los elementos uno a uno",
                f"{CID}.imprime-en-vez-de-devolver",
                "`__iter__` no imprime nada: devuelve el iterador que usará el `for`.",
            ),
            (
                "`for` llama a `__len__` y después accede a cada posición",
                None,
                "`for` no necesita saber cuántos elementos hay: pide un iterador y espera a `StopIteration`.",
            ),
        ],
        0,
        "Así funciona `for` por dentro: llama a `__iter__` para tener un iterador y le pide elementos con `__next__` hasta que este lanza `StopIteration`.",
        level=2,
        daw=False,
        bank=True,
        qtype="teoria",
    ),
    output(
        "poo8-09",
        CID,
        """
        class Clase:
            def __init__(self, *alumnos):
                self._alumnos = list(alumnos)

            def __iter__(self):
                return iter(self._alumnos)

        for nombre in Clase("Ana", "Luis"):
            print(nombre.upper())
        """,
        "ANA\nLUIS",
        "`for` llama a `__iter__`, que devuelve el iterador de la lista interna. Así el objeto se recorre igual que una lista.",
        traps={"Ana\nLuis": None, "TypeError": f"{CID}.iter-no-iterador"},
        level=2,
        daw=False,
    ),
    # ---------- Ejercicio guiado
    code(
        "poo8-10",
        CID,
        '**Ejercicio guiado: puntos.** La clase `Punto(x, y)` ya está. Sigue los pasos:\n\n1. Añade `__str__`, que devuelva `"(1, 2)"`.\n2. Añade `__repr__`, que devuelva `"Punto(1, 2)"`.\n3. Añade `__eq__`: dos puntos son iguales si tienen las mismas coordenadas; si el otro objeto no es un `Punto`, devuelve `NotImplemented`.',
        """
        class Punto:
            def __init__(self, x, y):
                self.x = x
                self.y = y

            # Paso 1: __str__

            # Paso 2: __repr__

            # Paso 3: __eq__


        a = Punto(1, 2)
        print(a)
        print([a, Punto(3, 4)])
        print(a == Punto(1, 2), a == (1, 2))
        """,
        """
        class Punto:
            def __init__(self, x, y):
                self.x = x
                self.y = y

            def __str__(self):
                return f"({self.x}, {self.y})"

            def __repr__(self):
                return f"Punto({self.x}, {self.y})"

            def __eq__(self, otro):
                if not isinstance(otro, Punto):
                    return NotImplemented
                return self.x == otro.x and self.y == otro.y


        a = Punto(1, 2)
        print(a)
        print([a, Punto(3, 4)])
        print(a == Punto(1, 2), a == (1, 2))
        """,
        [
            case(
                'p = Punto(1, 2)\nassert str(p) == "(1, 2)", f"str(Punto(1, 2)) debe ser \'(1, 2)\'; es {str(p)!r}"',
                error=f"{CID}.nombre-especial-mal",
            ),
            case(
                'p = Punto(3, -4)\nassert repr(p) == "Punto(3, -4)", f"repr(Punto(3, -4)) debe ser \'Punto(3, -4)\'; es {repr(p)!r}"\nassert str([p]) == "[Punto(3, -4)]", "Una lista muestra sus puntos con __repr__"',
                error=f"{CID}.lista-usa-str",
            ),
            case(
                'assert Punto(1, 2) == Punto(1, 2), "Dos puntos con las mismas coordenadas deben ser iguales con =="\nassert Punto(1, 2) != Punto(2, 1), "Puntos con coordenadas distintas no son iguales"\nassert (Punto(1, 2) == (1, 2)) is False, "Comparar con algo que no es un Punto debe dar False (devuelve NotImplemented)"',
                error=f"{CID}.eq-identidad",
            ),
        ],
        "`__str__` da el texto para el usuario, `__repr__` el del programador (por eso la lista lo usa) y `__eq__` compara el contenido. `NotImplemented` hace que comparar con una tupla dé `False` en vez de un error.",
        'Usa f-strings: `return f"Punto({self.x}, {self.y})"`. En `__eq__`, empieza por `if not isinstance(otro, Punto): return NotImplemented`.',
        wrong=[
            (
                """
                class Punto:
                    def __init__(self, x, y):
                        self.x = x
                        self.y = y

                    def __str__(self):
                        return f"({self.x}, {self.y})"

                    def __eq__(self, otro):
                        if not isinstance(otro, Punto):
                            return NotImplemented
                        return self.x == otro.x and self.y == otro.y
                """,
                2,
            ),
            (
                """
                class Punto:
                    def __init__(self, x, y):
                        self.x = x
                        self.y = y

                    def __str__(self):
                        return f"({self.x}, {self.y})"

                    def __repr__(self):
                        return f"Punto({self.x}, {self.y})"

                    def __eq__(self, otro):
                        return self.x == otro.x and self.y == otro.y
                """,
                3,
            ),
        ],
        level=2,
        daw=False,
    ),
    # ---------- Prácticas adicionales
    code(
        "poo8-11",
        CID,
        '**Práctica: lista de reproducción.** Crea `Playlist(nombre)` con una lista interna de canciones y:\n\n- `agregar(cancion)`.\n- `__len__`: cuántas canciones tiene.\n- `__contains__`: si una canción está en la lista.\n- `__iter__`: para recorrerla con `for` (delega en la lista interna).\n- `__str__`: `"Estudio (2 canciones)"`.',
        """
        class Playlist:
            ...
        """,
        """
        class Playlist:
            def __init__(self, nombre):
                self.nombre = nombre
                self._canciones = []

            def agregar(self, cancion):
                self._canciones.append(cancion)

            def __len__(self):
                return len(self._canciones)

            def __contains__(self, cancion):
                return cancion in self._canciones

            def __iter__(self):
                return iter(self._canciones)

            def __str__(self):
                return f"{self.nombre} ({len(self)} canciones)"


        lista = Playlist("Estudio")
        lista.agregar("Lo-fi 1")
        lista.agregar("Lo-fi 2")
        print(lista, "Lo-fi 1" in lista)
        for cancion in lista:
            print("-", cancion)
        """,
        [
            case(
                'p = Playlist("Estudio")\nassert len(p) == 0, "Una playlist nueva tiene 0 canciones"\np.agregar("A")\np.agregar("B")\nassert len(p) == 2, f"len() debe dar 2; da {len(p)}"\nassert str(p) == "Estudio (2 canciones)", f"str() devuelve {str(p)!r}"',
            ),
            case(
                'p = Playlist("X")\np.agregar("A")\nassert "A" in p and "Z" not in p, "in debe comprobar si la canción está en la lista"',
            ),
            case(
                'p = Playlist("X")\nfor c in ("A", "B", "C"):\n    p.agregar(c)\nassert list(p) == ["A", "B", "C"], "for debe recorrer las canciones en orden"\nassert list(p) == ["A", "B", "C"], "La playlist se debe poder recorrer más de una vez: devuelve iter(lista) en __iter__"',
                error=f"{CID}.iter-no-iterador",
            ),
        ],
        "Cada método especial delega en la lista interna. La playlist se usa como una lista (`len`, `in`, `for`), pero solo ofrece lo que tú decides.",
        "En `__iter__`, `return iter(self._canciones)`. En `__str__` puedes usar `len(self)`, que llama a tu propio `__len__`.",
        wrong=[
            (
                """
                class Playlist:
                    def __init__(self, nombre):
                        self.nombre = nombre
                        self._canciones = []

                    def agregar(self, cancion):
                        self._canciones.append(cancion)

                    def __len__(self):
                        return len(self._canciones)

                    def __contains__(self, cancion):
                        return cancion in self._canciones

                    def __iter__(self):
                        return self._canciones

                    def __str__(self):
                        return f"{self.nombre} ({len(self)} canciones)"
                """,
                3,
            ),
        ],
        level=2,
        daw=False,
    ),
    code(
        "poo8-12",
        CID,
        "**Práctica avanzada: un iterador a mano.** Crea `Pares(limite)`, un iterador que da los números pares desde 0 hasta `limite` (incluido si es par):\n\n- `__iter__` devuelve `self`.\n- `__next__` devuelve el siguiente par y, cuando se pasa del límite, lanza `StopIteration`.\n\nAsí, `list(Pares(7))` da `[0, 2, 4, 6]`.",
        """
        class Pares:
            def __init__(self, limite):
                self.limite = limite
                self.actual = 0

            def __iter__(self):
                return self

            def __next__(self):
                ...
        """,
        """
        class Pares:
            def __init__(self, limite):
                self.limite = limite
                self.actual = 0

            def __iter__(self):
                return self

            def __next__(self):
                if self.actual > self.limite:
                    raise StopIteration
                valor = self.actual
                self.actual += 2
                return valor


        print(list(Pares(7)))
        for n in Pares(4):
            print(n)
        """,
        [
            case(
                'assert list(Pares(7)) == [0, 2, 4, 6], f"list(Pares(7)) da {list(Pares(7))}"\nassert list(Pares(4)) == [0, 2, 4], "Si el límite es par, se incluye"',
            ),
            case(
                'assert list(Pares(-1)) == [], "Si el límite es negativo, no hay pares"\nit = Pares(2)\nassert next(it) == 0 and next(it) == 2, "next() da los pares uno a uno"\ntry:\n    next(it)\nexcept StopIteration:\n    pass\nelse:\n    raise AssertionError("Al pasarse del límite, __next__ debe lanzar StopIteration")',
            ),
        ],
        "`__next__` recuerda por dónde va (`self.actual`) y avisa con `StopIteration` cuando acaba. Es lo que hace `for` con cualquier iterador. Como `__iter__` devuelve `self`, el iterador se gasta tras recorrerlo una vez.",
        "Comprueba primero si `self.actual > self.limite`; si no, guarda el valor, suma 2 y devuélvelo.",
        wrong=[
            (
                """
                class Pares:
                    def __init__(self, limite):
                        self.limite = limite
                        self.actual = 0

                    def __iter__(self):
                        return self

                    def __next__(self):
                        if self.actual >= self.limite:
                            raise StopIteration
                        valor = self.actual
                        self.actual += 2
                        return valor
                """,
                1,
            ),
        ],
        level=3,
        daw=False,
    ),
    # ---------- Autoevaluación
    choice(
        "poo8-13",
        CID,
        "`print(alumno)` muestra `<__main__.Alumno object at 0x7f…>`. ¿Cuál es la solución?",
        [
            ("Añadir a `Alumno` un `__str__` que devuelva el texto que quieres ver", None),
            (
                "Escribir `print(alumno.__str__)`",
                f"{CID}.llamada-directa",
                "Sin paréntesis se imprime el propio método; y aunque se llamara, sigue sin haber un `__str__` propio.",
            ),
            (
                "Añadir un `__str__` que haga `print(self.nombre)`",
                f"{CID}.imprime-en-vez-de-devolver",
                "`__str__` debe devolver el texto; si imprime y no devuelve nada, `print` da `TypeError`.",
            ),
            (
                "Añadir un método `str(self)` sin guiones bajos",
                f"{CID}.nombre-especial-mal",
                "Python solo reconoce el nombre exacto `__str__`.",
            ),
        ],
        0,
        "`print` busca `__str__` (o, si no hay, `__repr__`). Sin ninguno de los dos, muestra la clase y la dirección de memoria.",
        level=2,
        daw=False,
        bank=True,
        qtype="solucion",
    ),
    output(
        "poo8-14",
        CID,
        """
        class Moneda:
            def __init__(self, valor):
                self.valor = valor

        a = Moneda(2)
        b = Moneda(2)
        print(a == b, a == a)
        """,
        "False True",
        "`Moneda` no define `__eq__`, así que `==` compara identidad: `a` y `b` son objetos distintos aunque valgan lo mismo. `a == a` sí es `True`.",
        traps={"True True": f"{CID}.eq-identidad", "False False": None},
        level=2,
        daw=False,
    ),
    # ---------- Ejercicio principal de la unidad
    code(
        "poo8-15",
        CID,
        '**Ejercicio principal: `CarritoCompra`.** Crea:\n\n- `Producto(nombre, precio)` con `__repr__` → `Producto(\'Pan\', 1.2)` y `__eq__`: dos productos son iguales si tienen el mismo nombre y precio (con otro tipo, `NotImplemented`).\n- `CarritoCompra()` con:\n  - `agregar(producto, cantidad=1)`: si la cantidad no es mayor que 0, `ValueError`; si ya hay un producto **igual** en el carrito, suma la cantidad.\n  - `total()`: el importe total.\n  - `__len__`: el número total de **unidades**.\n  - `__contains__`: si un producto está en el carrito (vale uno igual creado aparte).\n  - `__str__` → `"Carrito: 3 unidades, 4.50 €"`.\n  - `__repr__` → `"CarritoCompra(productos=2, unidades=3)"`.',
        """
        class Producto:
            ...


        class CarritoCompra:
            ...
        """,
        """
        class Producto:
            def __init__(self, nombre, precio):
                self.nombre = nombre
                self.precio = precio

            def __repr__(self):
                return f"Producto({self.nombre!r}, {self.precio!r})"

            def __eq__(self, otro):
                if not isinstance(otro, Producto):
                    return NotImplemented
                return self.nombre == otro.nombre and self.precio == otro.precio


        class CarritoCompra:
            def __init__(self):
                self._lineas = []  # pares [producto, cantidad]

            def agregar(self, producto, cantidad=1):
                if cantidad <= 0:
                    raise ValueError("La cantidad debe ser mayor que 0")
                for linea in self._lineas:
                    if linea[0] == producto:
                        linea[1] += cantidad
                        return
                self._lineas.append([producto, cantidad])

            def total(self):
                return sum(producto.precio * cantidad for producto, cantidad in self._lineas)

            def __len__(self):
                return sum(cantidad for _, cantidad in self._lineas)

            def __contains__(self, producto):
                return any(p == producto for p, _ in self._lineas)

            def __str__(self):
                return f"Carrito: {len(self)} unidades, {self.total():.2f} €"

            def __repr__(self):
                return f"CarritoCompra(productos={len(self._lineas)}, unidades={len(self)})"


        carrito = CarritoCompra()
        carrito.agregar(Producto("Pan", 1.2), 2)
        carrito.agregar(Producto("Leche", 2.1))
        print(carrito)
        print(repr(carrito))
        print(Producto("Pan", 1.2) in carrito, len(carrito))
        """,
        [
            case(
                'p = Producto("Pan", 1.2)\nassert repr(p) == "Producto(\'Pan\', 1.2)", f"repr() devuelve {repr(p)!r}"\nassert p == Producto("Pan", 1.2), "Productos con el mismo nombre y precio son iguales"\nassert p != Producto("Pan", 1.5), "Si cambia el precio, no son iguales"\nassert (p == "Pan") is False, "Comparar con otro tipo debe dar False (NotImplemented)"',
                error=f"{CID}.eq-identidad",
            ),
            case(
                'c = CarritoCompra()\nassert len(c) == 0, "Un carrito nuevo tiene 0 unidades"\nc.agregar(Producto("Pan", 1.2), 2)\nc.agregar(Producto("Leche", 2.1))\nassert len(c) == 3, f"len() cuenta unidades: debe dar 3; da {len(c)}"\nassert abs(c.total() - 4.5) < 1e-9, f"total() debe dar 4.5; da {c.total()}"',
                error=f"{CID}.len-no-entero",
            ),
            case(
                'c = CarritoCompra()\nc.agregar(Producto("Pan", 1.2), 2)\nc.agregar(Producto("Pan", 1.2), 3)\nassert len(c) == 5 and repr(c) == "CarritoCompra(productos=1, unidades=5)", f"Un producto igual suma su cantidad; repr() devuelve {repr(c)!r}"\nfor mala in (0, -2):\n    try:\n        c.agregar(Producto("Pan", 1.2), mala)\n    except ValueError:\n        pass\n    else:\n        raise AssertionError(f"agregar(producto, {mala}) debe lanzar ValueError")',
            ),
            case(
                'c = CarritoCompra()\nc.agregar(Producto("Pan", 1.2))\nassert Producto("Pan", 1.2) in c, "in debe encontrar un producto igual, aunque sea otro objeto"\nassert Producto("Leche", 2.1) not in c, "Un producto que no está no debe aparecer"',
            ),
            case(
                'c = CarritoCompra()\nc.agregar(Producto("Pan", 1.2), 2)\nc.agregar(Producto("Leche", 2.1))\nassert str(c) == "Carrito: 3 unidades, 4.50 €", f"str() devuelve {str(c)!r}"\nassert repr(c) == "CarritoCompra(productos=2, unidades=3)", f"repr() devuelve {repr(c)!r}"',
                error=f"{CID}.imprime-en-vez-de-devolver",
            ),
        ],
        "Gracias a los métodos especiales el carrito se usa con las mismas instrucciones que una colección de Python: `len`, `in`, `print` y `repr`. `__eq__` en `Producto` es lo que permite encontrar un producto igual creado aparte, tanto en `agregar` como en `in`.",
        "Guarda pares `[producto, cantidad]` en una lista. `__len__` suma las cantidades y `__contains__` puede usar `any(p == producto for p, _ in self._lineas)`.",
        wrong=[
            (
                """
                class Producto:
                    def __init__(self, nombre, precio):
                        self.nombre = nombre
                        self.precio = precio

                    def __repr__(self):
                        return f"Producto({self.nombre!r}, {self.precio!r})"
                """,
                1,
            ),
            (
                """
                class Producto:
                    def __init__(self, nombre, precio):
                        self.nombre = nombre
                        self.precio = precio

                    def __repr__(self):
                        return f"Producto({self.nombre!r}, {self.precio!r})"

                    def __eq__(self, otro):
                        if not isinstance(otro, Producto):
                            return NotImplemented
                        return self.nombre == otro.nombre and self.precio == otro.precio


                class CarritoCompra:
                    def __init__(self):
                        self._lineas = []

                    def agregar(self, producto, cantidad=1):
                        if cantidad <= 0:
                            raise ValueError("La cantidad debe ser mayor que 0")
                        for linea in self._lineas:
                            if linea[0] == producto:
                                linea[1] += cantidad
                                return
                        self._lineas.append([producto, cantidad])

                    def total(self):
                        return sum(producto.precio * cantidad for producto, cantidad in self._lineas)

                    def __len__(self):
                        return len(self._lineas)

                    def __contains__(self, producto):
                        return any(p == producto for p, _ in self._lineas)
                """,
                2,
            ),
            (
                """
                class Producto:
                    def __init__(self, nombre, precio):
                        self.nombre = nombre
                        self.precio = precio

                    def __repr__(self):
                        return f"Producto({self.nombre!r}, {self.precio!r})"

                    def __eq__(self, otro):
                        if not isinstance(otro, Producto):
                            return NotImplemented
                        return self.nombre == otro.nombre and self.precio == otro.precio


                class CarritoCompra:
                    def __init__(self):
                        self._lineas = []

                    def agregar(self, producto, cantidad=1):
                        if cantidad <= 0:
                            raise ValueError("La cantidad debe ser mayor que 0")
                        for linea in self._lineas:
                            if linea[0] == producto:
                                linea[1] += cantidad
                                return
                        self._lineas.append([producto, cantidad])

                    def total(self):
                        return sum(producto.precio * cantidad for producto, cantidad in self._lineas)

                    def __len__(self):
                        return sum(cantidad for _, cantidad in self._lineas)

                    def __contains__(self, producto):
                        return any(p == producto for p, _ in self._lineas)

                    def __str__(self):
                        print(f"Carrito: {len(self)} unidades, {self.total():.2f} €")
                        return ""

                    def __repr__(self):
                        return f"CarritoCompra(productos={len(self._lineas)}, unidades={len(self)})"
                """,
                5,
            ),
        ],
        level=3,
        daw=False,
    ),
    # ---------- Banco de preguntas de la unidad (cuestionario)
    choice(
        "poo8-16",
        CID,
        "¿Para qué sirve cada uno, `__str__` y `__repr__`?",
        [
            (
                "`__str__` da el texto para el usuario y `__repr__` el texto para el programador",
                None,
            ),
            (
                "`__str__` convierte el objeto en número y `__repr__` en texto",
                None,
                "Los dos devuelven texto; para convertir en número se usarían otros métodos especiales.",
            ),
            (
                "Son lo mismo: Python usa siempre `__str__`",
                f"{CID}.lista-usa-str",
                "No son lo mismo: la consola y las listas usan `__repr__`.",
            ),
            (
                "`__repr__` imprime el objeto y `__str__` lo guarda",
                f"{CID}.imprime-en-vez-de-devolver",
                "Ninguno imprime: los dos devuelven un texto y es `print` quien lo muestra.",
            ),
        ],
        0,
        "`__str__` es la versión legible (`Pan (1.20 €)`) y `__repr__` la versión técnica, que dice qué objeto es (`Producto('Pan', 1.2)`).",
        level=1,
        daw=False,
        bank=True,
        qtype="teoria",
    ),
    choice(
        "poo8-17",
        CID,
        "¿Qué método especial llama Python al ejecutar `len(carrito)`?",
        [
            ("`carrito.__len__()`", None),
            (
                "`carrito.__size__()`",
                f"{CID}.nombre-especial-mal",
                "Ese método no existe en Python: `len()` solo busca `__len__`.",
            ),
            (
                "`carrito.len()`",
                f"{CID}.nombre-especial-mal",
                "Un método normal llamado `len` no se usa con `len(carrito)`.",
            ),
            (
                "`carrito.__iter__()`, para contar los elementos uno a uno",
                None,
                "`len()` no recorre el objeto: pide directamente el número a `__len__`.",
            ),
        ],
        0,
        "Cada función o instrucción de Python tiene su método especial: `len()` → `__len__`, `str()` → `__str__`, `in` → `__contains__`.",
        code_options=True,
        level=1,
        daw=False,
        bank=True,
        qtype="codigo",
    ),
    choice(
        "poo8-18",
        CID,
        "La clase guarda sus alumnos en `self._alumnos`, una lista. ¿Qué `__iter__` es correcto?",
        [
            ("`return iter(self._alumnos)`", None),
            (
                "`return self._alumnos`",
                f"{CID}.iter-no-iterador",
                "Una lista es recorrible, pero no es un iterador: `for` da `TypeError: iter() returned non-iterator`.",
            ),
            (
                "`for a in self._alumnos: print(a)`",
                f"{CID}.imprime-en-vez-de-devolver",
                "`__iter__` no recorre ni imprime: devuelve el iterador que usará el `for`.",
            ),
            (
                "`return len(self._alumnos)`",
                None,
                "Eso es lo que haría `__len__`; un número no se puede recorrer.",
            ),
        ],
        0,
        "`iter(lista)` devuelve un iterador nuevo de la lista cada vez, así que el objeto se puede recorrer tantas veces como quieras.",
        code_options=True,
        level=3,
        daw=False,
        bank=True,
        qtype="codigo",
    ),
    choice(
        "poo8-19",
        CID,
        "¿Qué muestra este programa?",
        [
            ("Ciudad: Soria", None),
            (
                "Soria",
                None,
                "`print` usa el texto que devuelve `__str__`, que añade «Ciudad: ».",
            ),
            (
                "<__main__.Ciudad object>",
                f"{CID}.nombre-especial-mal",
                "La clase sí define `__str__` con el nombre correcto, así que `print` lo usa.",
            ),
            (
                "Ciudad('Soria')",
                f"{CID}.lista-usa-str",
                "Ese sería el texto de `__repr__`; `print` de un objeto suelto usa `__str__`.",
            ),
        ],
        0,
        "`print(objeto)` llama a `__str__` y muestra lo que devuelve.",
        code="""
        class Ciudad:
            def __init__(self, nombre):
                self.nombre = nombre

            def __str__(self):
                return f"Ciudad: {self.nombre}"

            def __repr__(self):
                return f"Ciudad({self.nombre!r})"

        print(Ciudad("Soria"))
        """,
        level=1,
        daw=False,
        bank=True,
        qtype="prediccion",
    ),
    choice(
        "poo8-20",
        CID,
        "¿Qué muestra este programa?",
        [
            ("[Ciudad('Soria'), Ciudad('Ávila')]", None),
            (
                "[Ciudad: Soria, Ciudad: Ávila]",
                f"{CID}.lista-usa-str",
                "Una lista muestra sus elementos con `__repr__`, no con `__str__`.",
            ),
            (
                "Ciudad: Soria Ciudad: Ávila",
                None,
                "Se imprime la lista entera, con sus corchetes y comas.",
            ),
            (
                "['Soria', 'Ávila']",
                None,
                "La lista guarda objetos `Ciudad`, no los textos con sus nombres.",
            ),
        ],
        0,
        "Al imprimir una lista, Python usa el `__repr__` de cada elemento. Por eso conviene que `__repr__` diga claramente qué objeto es.",
        code="""
        class Ciudad:
            def __init__(self, nombre):
                self.nombre = nombre

            def __str__(self):
                return f"Ciudad: {self.nombre}"

            def __repr__(self):
                return f"Ciudad({self.nombre!r})"

        print([Ciudad("Soria"), Ciudad("Ávila")])
        """,
        level=2,
        daw=False,
        bank=True,
        qtype="prediccion",
    ),
    choice(
        "poo8-21",
        CID,
        "¿Qué muestra este programa?",
        [
            ("[3, 2, 1] []", None),
            (
                "[3, 2, 1] [3, 2, 1]",
                None,
                "`__iter__` devuelve `self` y `actual` ya llegó a 0: el iterador se gastó en el primer `list`.",
            ),
            (
                "[1, 2, 3] []",
                None,
                "`__next__` devuelve primero el valor más alto y va bajando.",
            ),
            (
                "StopIteration",
                None,
                "`list()` recoge la `StopIteration` como señal de fin: no llega a verse como error.",
            ),
        ],
        0,
        "Un iterador que se devuelve a sí mismo en `__iter__` se **gasta**: el primer `list(c)` lo recorre entero y el segundo ya no recibe ningún elemento.",
        code="""
        class CuentaAtras:
            def __init__(self, desde):
                self.actual = desde

            def __iter__(self):
                return self

            def __next__(self):
                if self.actual == 0:
                    raise StopIteration
                self.actual -= 1
                return self.actual + 1

        c = CuentaAtras(3)
        print(list(c), list(c))
        """,
        level=3,
        daw=False,
        bank=True,
        qtype="prediccion",
    ),
    choice(
        "poo8-22",
        CID,
        "`print(libro)` da `TypeError: __str__ returned non-string (type NoneType)`. ¿Cuál es el fallo?",
        [
            ("`__str__` imprime el texto con `print` en vez de devolverlo con `return`", None),
            (
                "Falta llamar a `__str__` con paréntesis en `print(libro)`",
                f"{CID}.llamada-directa",
                "`print(libro)` es correcto: Python ya llama a `__str__` por su cuenta.",
            ),
            (
                "El título es un número y no se puede imprimir",
                None,
                "El error dice que `__str__` devolvió `None`, no que falle el título.",
            ),
            (
                "Hay que definir `__repr__` además de `__str__`",
                None,
                "`__repr__` no es obligatorio; el problema es lo que devuelve `__str__`.",
            ),
        ],
        0,
        "`__str__` tiene que **devolver** un `str`. Un método sin `return` devuelve `None`, y Python avisa con `TypeError`.",
        code="""
        class Libro:
            def __init__(self, titulo):
                self.titulo = titulo

            def __str__(self):
                print(f"Libro: {self.titulo}")
        """,
        level=2,
        daw=False,
        bank=True,
        qtype="error",
    ),
    choice(
        "poo8-23",
        CID,
        "`for alumno in clase:` da `TypeError: iter() returned non-iterator of type 'list'`. ¿Qué falla?",
        [
            (
                "`__iter__` devuelve la lista; debe devolver un iterador, por ejemplo `iter(self._alumnos)`",
                None,
            ),
            (
                "Las clases propias no se pueden recorrer con `for`",
                None,
                "Sí se pueden, si `__iter__` devuelve un iterador.",
            ),
            (
                "Falta definir `__len__`",
                None,
                "`for` no usa `__len__`: le basta con un iterador.",
            ),
            (
                "Hay que escribir `for alumno in clase.__iter__:`",
                f"{CID}.llamada-directa",
                "Sin paréntesis se intenta recorrer el propio método; lo correcto es `for alumno in clase:`.",
            ),
        ],
        0,
        "Una lista es recorrible, pero no es un iterador (no tiene `__next__`). `iter(lista)` sí lo es.",
        code="""
        class Clase:
            def __init__(self, alumnos):
                self._alumnos = list(alumnos)

            def __iter__(self):
                return self._alumnos
        """,
        level=3,
        daw=False,
        bank=True,
        qtype="error",
    ),
    choice(
        "poo8-24",
        CID,
        "`Producto` define `__eq__`, y ahora `{Producto('Pan', 1.2)}` da `TypeError: unhashable type`. Quieres seguir comparando por contenido y poder meterlos en un `set`. ¿Qué haces?",
        [
            (
                "Definir también `__hash__` con los mismos datos que compara `__eq__`: `return hash((self.nombre, self.precio))`",
                None,
            ),
            (
                "Borrar `__eq__`",
                f"{CID}.eq-identidad",
                "Volverías a comparar identidad: dos productos iguales creados aparte ya no serían iguales.",
            ),
            (
                "Usar una lista en vez de un `set` en todo el programa",
                None,
                "Evita el error, pero no lo que se pide: los productos seguirían sin poder ir en un `set`.",
            ),
            (
                "Hacer que `__eq__` devuelva siempre `True`",
                None,
                "Todos los productos serían iguales entre sí: el `set` solo guardaría uno.",
            ),
        ],
        0,
        "Al definir `__eq__`, Python quita el `__hash__` por defecto para que objetos iguales no tengan hashes distintos. Si defines `__hash__` con los mismos datos que compara `__eq__`, se pueden usar en `set` y como claves. Esos datos no deberían cambiar después.",
        level=3,
        daw=False,
        bank=True,
        qtype="solucion",
    ),
    choice(
        "poo8-25",
        CID,
        "¿En qué clase tiene sentido definir `__len__`?",
        [
            ("En `Carrito`, que agrupa productos y tiene un tamaño claro", None),
            (
                "En `Persona`, para devolver su edad",
                None,
                "`len(persona)` no se entendería: la edad no es un número de elementos.",
            ),
            (
                "En todas las clases, por si acaso",
                None,
                "Un método especial sin sentido para la clase confunde a quien la usa.",
            ),
            (
                "En `Fecha`, para devolver el día del mes",
                None,
                "Una fecha no es una colección; para el día, mejor un atributo `dia`.",
            ),
        ],
        0,
        "`__len__` es para objetos que son colecciones: el número de elementos que contienen.",
        level=1,
        daw=False,
        bank=True,
        qtype="diseno",
    ),
    choice(
        "poo8-26",
        CID,
        "Un alumno puede cambiar de nota o de correo, pero su DNI no cambia y no hay dos alumnos con el mismo. ¿Qué debe comparar `Alumno.__eq__`?",
        [
            ("El DNI, que es lo que identifica al alumno", None),
            (
                "Todos los atributos: nombre, correo, nota y DNI",
                None,
                "Si el alumno cambia de nota dejaría de ser «igual» a sí mismo en otra parte del programa.",
            ),
            (
                "Nada: es mejor no definir `__eq__` y usar `is`",
                f"{CID}.eq-identidad",
                "Dos objetos cargados por separado del mismo alumno no serían iguales.",
            ),
            (
                "La nota, porque es lo que más se consulta",
                None,
                "Dos alumnos distintos pueden tener la misma nota: no los identifica.",
            ),
        ],
        0,
        "Decidir qué hace iguales a dos objetos es una decisión de diseño. Si un dato identifica al objeto y no cambia (DNI, ISBN, número de pedido), compara ese dato.",
        level=2,
        daw=False,
        bank=True,
        qtype="diseno",
    ),
]

# Errores típicos (slug, etiqueta, por qué, qué pensar, cómo evitarlo)
ERRORS = [
    (
        "nombre-especial-mal",
        "Escribe mal el nombre del método especial",
        "Python solo llama al método si el nombre es exacto, con dos guiones bajos delante y detrás (`__str__`). Con otro nombre se usa el comportamiento por defecto.",
        "¿He puesto dos guiones bajos a cada lado y el nombre que espera Python?",
        "Consulta la tabla de la lección: `len()` → `__len__`, `in` → `__contains__`, `for` → `__iter__`.",
    ),
    (
        "llamada-directa",
        "Llama al método especial por su nombre en vez de usar la instrucción de Python",
        "Los métodos especiales están para que Python los llame. `x.__len__()` funciona, pero se escribe `len(x)`; y sin paréntesis no se llama a nada.",
        "¿Qué instrucción de Python usa este método?",
        "Escribe `len(x)`, `str(x)`, `a == b` o `y in x`, y deja que Python llame al método.",
    ),
    (
        "imprime-en-vez-de-devolver",
        "Imprime dentro del método especial en vez de devolver el resultado",
        "`__str__`, `__repr__` y `__eq__` deben devolver su resultado. Si imprimen y no devuelven nada, devuelven `None` y Python da error o una comparación falsa.",
        "¿Este método tiene un `return` con el valor que se espera?",
        "Usa `return` con un `str` (en `__str__` y `__repr__`) o un `bool` (en `__eq__` y `__contains__`).",
    ),
    (
        "lista-usa-str",
        "Cree que una lista de objetos se imprime con `__str__`",
        "Las listas, las tuplas y los diccionarios muestran sus elementos con `__repr__`. Si solo hay `__str__`, verás `<__main__.X object at …>` dentro de la lista.",
        "¿Estoy imprimiendo el objeto suelto o un contenedor con objetos?",
        "Define `__repr__` en tus clases; si quieres el texto de usuario, recorre la lista e imprime cada `str`.",
    ),
    (
        "eq-identidad",
        "Cree que `==` compara los atributos sin definir `__eq__`",
        "Sin `__eq__`, `==` hace lo mismo que `is`: solo da `True` si es el mismo objeto.",
        "¿Esta clase define `__eq__`? ¿Qué debería hacer iguales a dos objetos?",
        "Define `__eq__` comparando los datos que identifican al objeto y devuelve `NotImplemented` con otros tipos.",
    ),
    (
        "len-no-entero",
        "`__len__` no devuelve un número entero",
        "`len()` exige que `__len__` devuelva un entero mayor o igual que 0; si devuelve una lista, un texto o un decimal, da `TypeError`.",
        "¿Qué devuelve mi `__len__`: un número o la colección entera?",
        "Devuelve `len(self.elementos)` o una suma de cantidades enteras.",
    ),
    (
        "iter-no-iterador",
        "`__iter__` devuelve algo que no es un iterador",
        "`for` necesita un iterador (algo con `__next__`). Una lista es recorrible pero no es un iterador, así que `return self.lista` da `TypeError`.",
        "¿Lo que devuelve `__iter__` tiene `__next__`?",
        "Devuelve `iter(self.lista)`, o `self` si la clase tiene su propio `__next__`.",
    ),
]

# Las preguntas del banco de esta unidad ya nacen con su tipo y su nivel: no hay que etiquetar ninguna antigua
BANK_TAGS: dict = {}
