# ruff: noqa: E501
"""Unidad 4 del módulo de POO: encapsulación y propiedades.

Concepto `poo-encapsulacion` (área `poo`): convenios `_x` y `__x` (name mangling), propiedades con
`@property` y su `setter`, atributos de solo lectura y validación del estado (invariantes).
La salida de los ejemplos la obtiene build_learning.py ejecutándolos.
"""

from exercises import bug, case, choice, code, fill, output
from poo_common import practice, proposed, ref

CID = "poo-encapsulacion"

CONCEPT = {
    "id": CID,
    "title": "Encapsulación y propiedades",
    "area": "poo",
    "requires": ["poo-atributos-metodos"],
    "daw": 2,
    "ut": "prog-ut5",
    "lessons": ["atributos-clase"],
    "summary": "Proteger el estado de un objeto: atributos protegidos y privados, propiedades con `@property` y validación.",
    "when": "Cuando un dato de un objeto tiene reglas (un saldo que no puede ser negativo, una nota de 0 a 10) y no quieres que nadie las salte cambiando el atributo desde fuera.",
    "example": {
        "code": 'class Producto:\n    def __init__(self, nombre, precio):\n        self.nombre = nombre\n        self.precio = precio            # pasa por el setter: se valida\n\n    @property\n    def precio(self):                   # getter: se lee como un atributo\n        return self._precio\n\n    @precio.setter\n    def precio(self, valor):            # setter: se ejecuta al asignar\n        if valor < 0:\n            raise ValueError("El precio no puede ser negativo")\n        self._precio = valor\n\n\np = Producto("Teclado", 25)\np.precio = 30\nprint(p.nombre, p.precio)\ntry:\n    p.precio = -5\nexcept ValueError as e:\n    print("Error:", e)\nprint(p.precio)',
        "lines": [
            [4, "Incluso en `__init__` la asignación pasa por el setter y se valida."],
            [6, "`@property` convierte el método en un atributo que se lee sin paréntesis."],
            [8, "El dato real se guarda en `_precio` (protegido por convenio)."],
            [10, "`@precio.setter` define qué pasa al escribir `p.precio = …`."],
            [21, "Un precio negativo se rechaza y el objeto sigue con su valor válido."],
        ],
    },
    "errors": [],
    "related": ["poo-atributos-metodos", "excepciones"],
}

UNIT = {
    "unit": {"module": "poo", "number": 4},
    "objectives": [
        "Explicar qué es la encapsulación y por qué protege el estado de un objeto.",
        "Usar los convenios de Python: `_atributo` (protegido) y `__atributo` (privado, con *name mangling*).",
        "Crear propiedades con `@property` y validar las asignaciones con su `setter`.",
        "Definir atributos de solo lectura y atributos calculados.",
        "Mantener las reglas del objeto (invariantes) desde que se crea hasta que se modifica.",
    ],
    "prior": "La Unidad 3 (atributos de instancia y métodos que validan con `raise ValueError`) y la captura de excepciones con `try`/`except`.",
    "key": [
        [
            "Encapsulación",
            "Ocultar los detalles internos de un objeto y dejar usarlo a través de su interfaz (métodos y propiedades).",
        ],
        [
            "Interfaz pública",
            "Lo que el resto del programa puede usar de un objeto: sus métodos y atributos sin guion bajo.",
        ],
        [
            "Atributo protegido `_x`",
            "Un convenio: «es interno, no lo uses desde fuera». Python no lo impide.",
        ],
        [
            "Atributo privado `__x`",
            "Python le cambia el nombre a `_Clase__x` (*name mangling*) para evitar choques y usos accidentales.",
        ],
        ["Propiedad", "Un método con `@property` que se usa como un atributo, sin paréntesis."],
        ["Getter y setter", "El código que se ejecuta al leer y al asignar una propiedad."],
        [
            "Solo lectura",
            "Una propiedad sin setter: se puede leer pero asignarla da `AttributeError`.",
        ],
        [
            "Invariante",
            "Una regla que el objeto cumple siempre, por ejemplo «el saldo nunca es negativo».",
        ],
    ],
    "sections": [
        {
            "id": f"{CID}.convenio",
            "title": "Público, protegido y privado",
            "theory": "La **encapsulación** consiste en que cada objeto cuide de sus propios datos: el resto del programa usa su **interfaz pública** (métodos y propiedades) y no toca los detalles internos. Así se pueden cambiar esos detalles sin romper el código que usa la clase.\n\nPython no tiene `private` como Java: usa **convenios** con guiones bajos.\n\n- `nombre`: **público**, se puede usar desde fuera.\n- `_saldo`: **protegido** por convenio. Significa «es interno»; Python lo deja usar, pero un buen programador no lo hace desde fuera.\n- `__pin`: **privado**. Python le cambia el nombre a `_Caja__pin` (*name mangling*), así que `objeto.__pin` desde fuera da `AttributeError`. No es una caja fuerte: sigue existiendo con el nombre cambiado, pero evita usos accidentales y choques con subclases.\n\n**Importante:** ni `_x` ni `__x` son una medida de seguridad. Cualquier código del mismo programa puede leer `objeto._Caja__pin`. Sirven para organizar el código y avisar de lo que es interno, no para guardar secretos como contraseñas.\n\nDesde dentro de la clase se usa siempre igual: `self._saldo`, `self.__pin`.",
            "examples": [
                {
                    "code": 'class Caja:\n    def __init__(self, dueno, pin):\n        self.dueno = dueno          # público\n        self._intentos = 0          # protegido (convenio)\n        self.__pin = pin            # privado (name mangling)\n\n    def abrir(self, intento):\n        self._intentos += 1\n        return intento == self.__pin\n\n\nc = Caja("Ana", 1234)\nprint(c.dueno, c.abrir(1111), c.abrir(1234))\nprint(c._intentos)\nprint(hasattr(c, "__pin"), hasattr(c, "_Caja__pin"))',
                    "lines": [
                        [3, "Público: forma parte de la interfaz de la caja."],
                        [4, "Protegido: un guion bajo avisa de que es un detalle interno."],
                        [5, "Privado: dos guiones bajos; Python lo guarda como `_Caja__pin`."],
                        [9, "Dentro de la clase se usa con su nombre normal."],
                        [
                            14,
                            "Se puede leer `_intentos`, pero el guion bajo dice que no se debería.",
                        ],
                        [
                            15,
                            "`__pin` no existe con ese nombre fuera de la clase: está como `_Caja__pin`.",
                        ],
                    ],
                }
            ],
            "quiz": ["poo4-01", "poo4-02", "poo4-03"],
        },
        {
            "id": f"{CID}.property",
            "title": "Propiedades con `@property`",
            "theory": "Una **propiedad** es un método que se usa como si fuera un atributo. Se crea con el decorador `@property` encima del método que **lee** el valor (el *getter*) y se usa **sin paréntesis**: `p.precio`, no `p.precio()`.\n\nPara permitir asignarla se añade un **setter** con `@nombre.setter`, un método con el **mismo nombre** que recibe el valor nuevo. Ahí se valida antes de guardar.\n\n- El dato real se guarda en otro atributo, normalmente con guion bajo (`self._precio`). Si el setter hiciera `self.precio = valor`, se llamaría a sí mismo sin fin (`RecursionError`).\n- Una propiedad **sin setter** es de **solo lectura**: asignarla da `AttributeError`.\n- Una propiedad puede ser **calculada**: no guarda nada, devuelve un valor a partir de otros atributos (el área de un rectángulo).\n\nVentaja: el código que usa la clase escribe `p.precio` tanto si es un atributo simple como si hay validación detrás; se puede añadir la regla después sin cambiar nada fuera.",
            "examples": [
                {
                    "code": 'class Rectangulo:\n    def __init__(self, base, altura):\n        self.base = base\n        self.altura = altura\n\n    @property\n    def area(self):                 # propiedad calculada y de solo lectura\n        return self.base * self.altura\n\n\nr = Rectangulo(3, 4)\nprint(r.area)\nr.base = 5\nprint(r.area)\ntry:\n    r.area = 100\nexcept AttributeError:\n    print("area es de solo lectura")',
                    "lines": [
                        [6, "`@property`: `area` se usará como un atributo."],
                        [8, "No guarda nada: se calcula cada vez a partir de base y altura."],
                        [12, "Se lee sin paréntesis: `r.area`."],
                        [14, "Al cambiar la base, el área calculada cambia sola."],
                        [16, "No hay setter, así que asignarla da `AttributeError`."],
                    ],
                }
            ],
            "quiz": ["poo4-04", "poo4-05", "poo4-06"],
        },
        {
            "id": f"{CID}.invariantes",
            "title": "Validar y proteger el estado",
            "theory": "Una **invariante** es una regla que el objeto debe cumplir **siempre**: una nota entre 0 y 10, un saldo que no baja de 0, un nombre que no está vacío. La encapsulación sirve para que nadie pueda romperla.\n\n- Pon la validación en el **setter** y, en `__init__`, asigna **a través de la propiedad** (`self.nota = nota`, no `self._nota = nota`). Así el objeto ya nace válido.\n- Si un dato no debe cambiar desde fuera (el saldo), hazlo **de solo lectura** y ofrece métodos (`ingresar`, `retirar`) que apliquen las reglas.\n- Si una operación no es válida, lanza una excepción **antes** de cambiar nada, para no dejar el objeto a medias.",
            "examples": [
                {
                    "code": 'class Temperatura:\n    def __init__(self, celsius):\n        self.celsius = celsius           # se valida desde el principio\n\n    @property\n    def celsius(self):\n        return self._celsius\n\n    @celsius.setter\n    def celsius(self, valor):\n        if valor < -273.15:\n            raise ValueError("Por debajo del cero absoluto")\n        self._celsius = valor\n\n    @property\n    def fahrenheit(self):                # calculada y de solo lectura\n        return self.celsius * 9 / 5 + 32\n\n\nt = Temperatura(25)\nprint(t.fahrenheit)\nfor valor in (100, -300):\n    try:\n        t.celsius = valor\n    except ValueError as e:\n        print("Rechazado:", e)\nprint(t.celsius)',
                    "lines": [
                        [
                            3,
                            "La asignación de `__init__` pasa por el setter: un valor imposible ni se crea.",
                        ],
                        [11, "La regla (invariante) está en un único sitio."],
                        [16, "`fahrenheit` se calcula siempre a partir del dato validado."],
                        [
                            24,
                            "100 se acepta; -300 se rechaza y el objeto conserva su último valor válido.",
                        ],
                    ],
                }
            ],
            "quiz": ["poo4-07", "poo4-08", "poo4-09"],
        },
    ],
    "guided": ["poo4-10"],
    "autonomous": ["poo4-15"],
    "extras": ["poo4-11", "poo4-12"],
    "selfcheck": ["poo4-13", "poo4-14"],
    "recap": [
        "Encapsular es dejar usar un objeto por su interfaz pública y esconder los detalles internos.",
        "`_x` es protegido por convenio (Python no lo impide); `__x` es privado y Python lo renombra a `_Clase__x`.",
        "`@property` crea un atributo que se lee sin paréntesis; `@nombre.setter` valida al asignarlo.",
        "Una propiedad sin setter es de solo lectura; el dato real va en otro atributo (`self._x`) para no caer en recursión.",
        "Valida en el setter y asigna por la propiedad en `__init__`: el objeto cumple sus reglas desde que nace.",
    ],
    "pass": {
        "minScore": 0.7,
        "required": ["poo4-10", "poo4-15"],
        "text": [
            "Resolver el ejercicio guiado (`CuentaSegura`) y el ejercicio principal `CuentaBancaria` con todos los tests superados.",
            "Dominar la unidad según el motor: al menos un 70 % de aciertos recientes en sus ejercicios, con varios tipos distintos.",
            "Completar las lecciones ayuda a organizarte, pero **no** demuestra la competencia: la demuestran los ejercicios.",
        ],
    },
    "practices": [
        practice(
            "Marca con un guion bajo (`_saldo`) lo que es interno y deja públicos solo los métodos y propiedades que otros deben usar.",
            "Así queda claro qué se puede usar desde fuera y qué puede cambiar sin avisar.",
        ),
        practice(
            "No uses `__x` como medida de seguridad: sirve para evitar choques de nombres con las subclases.",
            "Python lo renombra a `_Clase__x`, pero cualquier código puede seguir leyéndolo con ese nombre.",
        ),
        practice(
            "Cuando escribas una propiedad, guarda el dato real en otro atributo (`self._edad`).",
            "Si el setter asignara `self.edad`, se llamaría a sí mismo sin fin (`RecursionError`).",
        ),
        practice(
            "Valida en el setter y, en `__init__`, asigna a través de la propiedad.",
            "Así el objeto cumple sus reglas desde el momento en que se crea.",
        ),
        practice(
            "Si un valor no es válido, lanza `ValueError` en vez de corregirlo en silencio o de imprimir un aviso.",
            "Quien llama se entera del problema y el objeto no se queda en un estado incorrecto.",
        ),
        practice(
            "Si un método devuelve una lista interna, devuelve una copia o una tupla.",
            "Si no, desde fuera se podría cambiar el estado del objeto sin pasar por sus métodos.",
        ),
    ],
    "references": [
        ref(
            "py-tutorial-classes",
            "9.6. Variables privadas",
            [
                "convenio del guion bajo para lo que es interno",
                "renombrado de `__x` (name mangling) y que no impide el acceso",
            ],
        ),
    ],
    "bank": [
        "poo4-01",
        "poo4-08",
        "poo4-09",
        "poo4-13",
        "poo4-16",
        "poo4-17",
        "poo4-18",
        "poo4-19",
        "poo4-20",
        "poo4-21",
        "poo4-22",
        "poo4-23",
        "poo4-24",
        "poo4-25",
        "poo4-26",
    ],
    "curriculum": [
        proposed(
            "0485-RA4-f",
            "Se controla la visibilidad de los miembros con `_x`, `__x` y propiedades.",
        ),
        proposed("0485-RA2-d", "Se usan propiedades (`@property`) de los objetos."),
        proposed(
            "0485-RA4-c", "Se definen propiedades con getter y setter, y métodos que las usan."
        ),
    ],
}

EXERCISES = [
    # ---------- Lección «Público, protegido y privado»
    choice(
        "poo4-01",
        CID,
        "En una clase aparece el atributo `self._saldo`. ¿Qué significa el guion bajo?",
        [
            ("Es un convenio: avisa de que es interno y no debería usarse desde fuera", None),
            ("Python impide leerlo o cambiarlo desde fuera de la clase", f"{CID}.privado-absoluto"),
            ("Hace que el atributo sea de solo lectura", f"{CID}.sin-setter"),
            ("Lo convierte en un atributo de clase compartido", None),
        ],
        0,
        "Un guion bajo es solo un aviso entre programadores: «esto es un detalle interno». Python no bloquea nada; la protección real se consigue con propiedades y métodos.",
        level=1,
        daw=False,
    ),
    output(
        "poo4-02",
        CID,
        """
        class Clave:
            def __init__(self, valor):
                self.__valor = valor

        k = Clave("abc")
        print(hasattr(k, "__valor"), hasattr(k, "_Clave__valor"))
        """,
        "False True",
        "Con dos guiones bajos Python renombra el atributo a `_Clave__valor` (*name mangling*). Por eso no se encuentra como `__valor` desde fuera, aunque sigue existiendo.",
        traps={"True False": f"{CID}.privado-absoluto", "False False": f"{CID}.privado-absoluto"},
        level=2,
        daw=False,
    ),
    bug(
        "poo4-03",
        CID,
        "Debería mostrar `True` comprobando el PIN. ¿Qué línea falla?",
        """
        class Caja:
            def __init__(self, pin):
                self.__pin = pin

            def abrir(self, intento):
                return intento == self.__pin

        c = Caja(1234)
        print(c.__pin == 1234)
        """,
        9,
        "print(c.abrir(1234))",
        "True",
        f"{CID}.privado-desde-fuera",
        "Fuera de la clase `c.__pin` no existe (se llama `_Caja__pin`) y salta `AttributeError`. Lo correcto es usar la interfaz pública de la caja: el método `abrir`.",
        level=2,
        daw=False,
    ),
    # ---------- Lección «Propiedades con @property»
    output(
        "poo4-04",
        CID,
        """
        class Circulo:
            def __init__(self, radio):
                self.radio = radio

            @property
            def diametro(self):
                return self.radio * 2

        c = Circulo(3)
        c.radio = 5
        print(c.diametro)
        """,
        "10",
        "`diametro` es una propiedad calculada: no guarda nada y se calcula cada vez que se lee, con el radio actual (5).",
        traps={"6": None},
        level=1,
        daw=False,
    ),
    bug(
        "poo4-05",
        CID,
        "Debería mostrar `12`. ¿Qué línea falla?",
        """
        class Rectangulo:
            def __init__(self, base, altura):
                self.base = base
                self.altura = altura

            @property
            def area(self):
                return self.base * self.altura

        r = Rectangulo(3, 4)
        print(r.area())
        """,
        11,
        "print(r.area)",
        "12",
        f"{CID}.property-con-parentesis",
        "Una propiedad se lee **sin paréntesis**. `r.area` ya vale 12; `r.area()` intenta llamar al número 12 y da `TypeError: 'int' object is not callable`.",
        level=2,
        daw=False,
    ),
    fill(
        "poo4-06",
        CID,
        "Completa el decorador del setter para que la edad se valide al asignarla.",
        """
        class Persona:
            def __init__(self, edad):
                self.edad = edad

            @property
            def edad(self):
                return self._edad

            @___.setter
            def edad(self, valor):
                if valor < 0:
                    raise ValueError("Edad negativa")
                self._edad = valor

        p = Persona(20)
        p.edad = 21
        print(p.edad)
        """,
        ["edad"],
        "El setter se declara con `@nombre_de_la_propiedad.setter` y el método se llama igual que la propiedad: `@edad.setter` y `def edad(self, valor)`.",
        expect="21",
        traps={"property": None, "_edad": None, "self.edad": None},
        level=2,
        daw=False,
    ),
    # ---------- Lección «Validar y proteger el estado»
    output(
        "poo4-07",
        CID,
        """
        class Nota:
            def __init__(self, valor):
                self.valor = valor

            @property
            def valor(self):
                return self._valor

            @valor.setter
            def valor(self, nuevo):
                if not 0 <= nuevo <= 10:
                    raise ValueError("Fuera de rango")
                self._valor = nuevo

        try:
            n = Nota(12)
            print("creada")
        except ValueError as e:
            print(e)
        """,
        "Fuera de rango",
        "En `__init__`, `self.valor = valor` pasa por el setter, así que una nota de 12 se rechaza al crearla: el objeto nunca llega a existir con un valor no válido.",
        traps={"creada": f"{CID}.validacion-fuera"},
        level=2,
        daw=False,
    ),
    choice(
        "poo4-08",
        CID,
        "Dentro del setter de la propiedad `edad` se escribe `self.edad = valor` en vez de `self._edad = valor`. ¿Qué pasa al asignar una edad?",
        [
            ("`RecursionError`: el setter se vuelve a llamar a sí mismo sin parar", None),
            ("Se guarda el valor con normalidad", f"{CID}.setter-recursivo"),
            ("Python crea solo un atributo `_edad`", f"{CID}.setter-recursivo"),
            ("Da `SyntaxError` al definir la clase", None),
        ],
        0,
        "`self.edad = …` dentro del setter vuelve a llamar al setter, que vuelve a asignar… hasta agotar la pila. El dato real debe ir en otro atributo: `self._edad`.",
        level=2,
        daw=False,
    ),
    choice(
        "poo4-09",
        CID,
        "¿Qué ventaja tiene una propiedad `precio` frente a un método `get_precio()`?",
        [
            (
                "Se usa como un atributo (`p.precio`) y se puede añadir validación después sin cambiar el código que la usa",
                None,
            ),
            (
                "Hace que el precio sea imposible de cambiar de ninguna forma",
                f"{CID}.privado-absoluto",
            ),
            ("Es obligatoria: Python no permite métodos `get_`", None),
            ("Guarda el valor en un atributo de clase compartido", None),
        ],
        0,
        "Con una propiedad, el código de fuera sigue escribiendo `p.precio` y `p.precio = 30`; la clase decide por dentro cómo se calcula o se valida. Los métodos `get_`/`set_` funcionan, pero son menos naturales en Python.",
        level=1,
        daw=False,
    ),
    # ---------- Ejercicio guiado
    code(
        "poo4-10",
        CID,
        "**Ejercicio guiado: `CuentaSegura`.** Sigue los pasos:\n\n1. En `__init__(self, titular, saldo=0)` asigna `self.titular = titular` (pasará por su setter) y guarda el saldo en `self._saldo`.\n2. Crea la propiedad `titular` con un setter que lance `ValueError` si el texto está vacío.\n3. Crea la propiedad `saldo` **de solo lectura** (sin setter).\n4. Escribe `ingresar(cantidad)` y `retirar(cantidad)`: lanzan `ValueError` si la cantidad no es positiva o si no hay saldo suficiente, y devuelven el saldo nuevo.",
        """
        class CuentaSegura:
            def __init__(self, titular, saldo=0):
                # Paso 1
                ...

            # Paso 2: propiedad titular con su setter

            # Paso 3: propiedad saldo (solo lectura)

            # Paso 4: ingresar(cantidad) y retirar(cantidad)


        c = CuentaSegura("Ana", 50)
        print(c.ingresar(25))
        print(c.saldo)
        """,
        """
        class CuentaSegura:
            def __init__(self, titular, saldo=0):
                self.titular = titular
                self._saldo = saldo

            @property
            def titular(self):
                return self._titular

            @titular.setter
            def titular(self, valor):
                if not valor:
                    raise ValueError("El titular no puede estar vacío")
                self._titular = valor

            @property
            def saldo(self):
                return self._saldo

            def ingresar(self, cantidad):
                if cantidad <= 0:
                    raise ValueError("La cantidad debe ser positiva")
                self._saldo += cantidad
                return self._saldo

            def retirar(self, cantidad):
                if cantidad <= 0:
                    raise ValueError("La cantidad debe ser positiva")
                if cantidad > self._saldo:
                    raise ValueError("Saldo insuficiente")
                self._saldo -= cantidad
                return self._saldo


        c = CuentaSegura("Ana", 50)
        print(c.ingresar(25))
        print(c.saldo)
        """,
        [
            case(
                'c = CuentaSegura("Eva", 50)\nassert c.titular == "Eva" and c.saldo == 50, "Guarda titular y saldo"\nassert c.ingresar(25) == 75, "ingresar() debe devolver el saldo nuevo"\nassert c.retirar(70) == 5, "retirar() debe devolver el saldo nuevo"',
            ),
            case(
                'c = CuentaSegura("Eva", 50)\nassert isinstance(CuentaSegura.__dict__.get("saldo"), property), "saldo debe ser una propiedad (@property)"\ntry:\n    c.saldo = 1000\nexcept AttributeError:\n    pass\nelse:\n    raise AssertionError("saldo debe ser de solo lectura: c.saldo = 1000 tiene que dar AttributeError")',
                error=f"{CID}.sin-setter",
            ),
            case(
                'c = CuentaSegura("Eva", 10)\nfor mal in (lambda: c.retirar(20), lambda: c.ingresar(-1), lambda: setattr(c, "titular", ""), lambda: CuentaSegura("", 5)):\n    try:\n        mal()\n    except ValueError:\n        pass\n    else:\n        raise AssertionError("Sin saldo, con cantidades no positivas o con un titular vacío debe lanzarse ValueError (también al crear la cuenta)")\nassert c.saldo == 10 and c.titular == "Eva", "Una operación rechazada no debe cambiar nada"',
                error=f"{CID}.validacion-fuera",
            ),
        ],
        "El saldo solo cambia a través de `ingresar` y `retirar`, que aplican las reglas: por eso la propiedad `saldo` no tiene setter. El titular sí se puede cambiar, pero su setter impide dejarlo vacío, también al crear la cuenta.",
        "Para la propiedad: `@property` y `def saldo(self): return self._saldo`. Para el setter: `@titular.setter` y `def titular(self, valor):`, que guarda en `self._titular`.",
        wrong=[
            (
                """
                class CuentaSegura:
                    def __init__(self, titular, saldo=0):
                        self.titular = titular
                        self.saldo = saldo

                    def ingresar(self, cantidad):
                        if cantidad <= 0:
                            raise ValueError("La cantidad debe ser positiva")
                        self.saldo += cantidad
                        return self.saldo

                    def retirar(self, cantidad):
                        if cantidad <= 0:
                            raise ValueError("La cantidad debe ser positiva")
                        if cantidad > self.saldo:
                            raise ValueError("Saldo insuficiente")
                        self.saldo -= cantidad
                        return self.saldo
                """,
                2,
            ),
        ],
        level=2,
        daw=False,
    ),
    # ---------- Ejercicios autónomos
    code(
        "poo4-11",
        CID,
        '**Ejercicio autónomo: `Termostato`.** Crea la clase con:\n\n- La propiedad `temperatura`, con un setter que solo acepte valores de 10 a 30 (ambos incluidos) y lance `ValueError` con cualquier otro. También debe validarse al crear el termostato.\n- El método `subir(grados=1)`, que sube la temperatura usando la propiedad (así se valida).\n- La propiedad de solo lectura `modo`: `"confort"` si la temperatura está entre 19 y 24 (incluidos) y `"ajustar"` en otro caso.',
        """
        class Termostato:
            ...
        """,
        """
        class Termostato:
            def __init__(self, temperatura):
                self.temperatura = temperatura

            @property
            def temperatura(self):
                return self._temperatura

            @temperatura.setter
            def temperatura(self, valor):
                if not 10 <= valor <= 30:
                    raise ValueError("Temperatura fuera de rango (10-30)")
                self._temperatura = valor

            def subir(self, grados=1):
                self.temperatura = self.temperatura + grados

            @property
            def modo(self):
                return "confort" if 19 <= self.temperatura <= 24 else "ajustar"


        t = Termostato(20)
        t.subir(3)
        print(t.temperatura, t.modo)
        """,
        [
            case(
                't = Termostato(20)\nassert t.temperatura == 20, "Guarda la temperatura inicial"\nassert t.modo == "confort", f"Con 20 grados el modo es \'confort\'; es {t.modo!r}"\nassert Termostato(25).modo == "ajustar", "Con 25 grados el modo es \'ajustar\'"',
            ),
            case(
                'for mal in (lambda: Termostato(31), lambda: setattr(Termostato(20), "temperatura", 5)):\n    try:\n        mal()\n    except ValueError:\n        pass\n    else:\n        raise AssertionError("Fuera de 10-30 debe lanzarse ValueError, también al crear el termostato")\nassert isinstance(Termostato.__dict__.get("temperatura"), property), "temperatura debe ser una propiedad"',
                error=f"{CID}.validacion-fuera",
            ),
            case(
                't = Termostato(29)\nt.subir()\nassert t.temperatura == 30, "subir() sin argumentos sube 1 grado"\ntry:\n    t.subir()\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError("subir() por encima de 30 debe lanzar ValueError")\nassert t.temperatura == 30, "Si no se puede subir, la temperatura no cambia"\ntry:\n    t.modo = "x"\nexcept AttributeError:\n    pass\nelse:\n    raise AssertionError("modo debe ser de solo lectura")',
                error=f"{CID}.sin-setter",
            ),
        ],
        "Toda escritura de la temperatura pasa por el setter: la de `__init__`, la de `subir` y la de fuera. Así la regla de 10 a 30 está en un único sitio. `modo` se calcula, así que no necesita setter.",
        "En `__init__` y en `subir` asigna `self.temperatura = …` (con la propiedad), nunca `self._temperatura` directamente.",
        wrong=[
            (
                """
                class Termostato:
                    def __init__(self, temperatura):
                        self._temperatura = temperatura

                    @property
                    def temperatura(self):
                        return self._temperatura

                    @temperatura.setter
                    def temperatura(self, valor):
                        if not 10 <= valor <= 30:
                            raise ValueError("Temperatura fuera de rango (10-30)")
                        self._temperatura = valor

                    def subir(self, grados=1):
                        self.temperatura = self.temperatura + grados

                    @property
                    def modo(self):
                        return "confort" if 19 <= self.temperatura <= 24 else "ajustar"
                """,
                2,
            ),
        ],
        level=2,
        daw=False,
    ),
    code(
        "poo4-12",
        CID,
        "**Ejercicio autónomo: `Usuario` con contraseña privada.** Crea la clase con:\n\n- `__init__(self, nombre, clave)`: guarda el nombre y la contraseña en un atributo **privado** `__clave`.\n- La propiedad de solo lectura `nombre`.\n- `comprobar(clave)`: devuelve `True` si coincide.\n- `cambiar_clave(actual, nueva)`: si `actual` es correcta y `nueva` tiene al menos 8 caracteres, cambia la contraseña y devuelve `True`; si no, devuelve `False` sin cambiar nada.",
        """
        class Usuario:
            ...
        """,
        """
        class Usuario:
            def __init__(self, nombre, clave):
                self._nombre = nombre
                self.__clave = clave

            @property
            def nombre(self):
                return self._nombre

            def comprobar(self, clave):
                return clave == self.__clave

            def cambiar_clave(self, actual, nueva):
                if not self.comprobar(actual) or len(nueva) < 8:
                    return False
                self.__clave = nueva
                return True


        u = Usuario("ana", "secreto123")
        print(u.comprobar("secreto123"))
        print(u.cambiar_clave("secreto123", "corta"))
        """,
        [
            case(
                'u = Usuario("ana", "secreto123")\nassert u.nombre == "ana", "La propiedad nombre devuelve el nombre"\nassert u.comprobar("secreto123") is True and u.comprobar("otra") is False, "comprobar() devuelve True solo con la contraseña correcta"',
            ),
            case(
                'u = Usuario("ana", "secreto123")\nassert u.cambiar_clave("mal", "nuevaclave1") is False, "Con la contraseña actual incorrecta no se cambia"\nassert u.cambiar_clave("secreto123", "corta") is False, "Una contraseña nueva de menos de 8 caracteres no se acepta"\nassert u.comprobar("secreto123"), "Si el cambio se rechaza, la contraseña sigue siendo la misma"\nassert u.cambiar_clave("secreto123", "nuevaclave1") is True and u.comprobar("nuevaclave1"), "Con datos correctos se cambia y devuelve True"',
            ),
            case(
                'u = Usuario("ana", "secreto123")\nassert "_Usuario__clave" in vars(u), "Guarda la contraseña en el atributo privado self.__clave"\nassert not any(k in vars(u) for k in ("clave", "_clave")), "La contraseña no debe estar en un atributo público ni protegido"\ntry:\n    u.nombre = "otro"\nexcept AttributeError:\n    pass\nelse:\n    raise AssertionError("nombre debe ser de solo lectura")',
                error=f"{CID}.privado-absoluto",
            ),
        ],
        "La contraseña no se puede leer desde fuera: solo se puede **comprobar** o **cambiar** con reglas. Ese es el sentido de la encapsulación: el objeto decide qué se puede hacer con sus datos.",
        "Guarda con `self.__clave = clave` y usa `self.__clave` dentro de los métodos. Para `nombre`, guarda `self._nombre` y crea una propiedad sin setter.",
        wrong=[
            (
                """
                class Usuario:
                    def __init__(self, nombre, clave):
                        self._nombre = nombre
                        self.clave = clave

                    @property
                    def nombre(self):
                        return self._nombre

                    def comprobar(self, clave):
                        return clave == self.clave

                    def cambiar_clave(self, actual, nueva):
                        if not self.comprobar(actual) or len(nueva) < 8:
                            return False
                        self.clave = nueva
                        return True
                """,
                3,
            ),
        ],
        level=2,
        daw=False,
    ),
    # ---------- Autoevaluación
    choice(
        "poo4-13",
        CID,
        "¿Qué hace Python con un atributo `self.__pin` definido dentro de la clase `Caja`?",
        [
            (
                "Le cambia el nombre a `_Caja__pin`, así que desde fuera no se encuentra como `__pin`",
                None,
            ),
            ("Lo hace imposible de leer de ninguna manera", f"{CID}.privado-absoluto"),
            ("Lo borra cuando termina `__init__`", None),
            (
                "Nada: los dos guiones bajos son solo estilo, igual que uno",
                f"{CID}.privado-absoluto",
            ),
        ],
        0,
        "Es el *name mangling*: el atributo existe, pero renombrado. Evita usos accidentales y choques con subclases, aunque no es una protección absoluta.",
        level=1,
        daw=False,
    ),
    output(
        "poo4-14",
        CID,
        """
        class Termo:
            def __init__(self):
                self._grados = 20

            @property
            def grados(self):
                return self._grados

        t = Termo()
        try:
            t.grados = 50
        except AttributeError:
            print("solo lectura")
        print(t.grados)
        """,
        "solo lectura\n20",
        "`grados` es una propiedad sin setter, así que asignarla da `AttributeError` y el valor sigue siendo 20.",
        traps={"50": f"{CID}.sin-setter", "solo lectura\n50": f"{CID}.sin-setter"},
        level=2,
        daw=False,
    ),
    # ---------- Ejercicio principal de la unidad
    code(
        "poo4-15",
        CID,
        "**Ejercicio principal: la clase `CuentaBancaria`.** Crea la clase con:\n\n- `__init__(self, titular, saldo=0)`: guarda el titular y el saldo en el atributo **privado** `__saldo`, y una lista **privada** `__movimientos` vacía. Lanza `ValueError` si el saldo inicial es negativo.\n- La propiedad de **solo lectura** `saldo`.\n- `ingresar(cantidad)` y `retirar(cantidad)`: lanzan `ValueError` si la cantidad no es mayor que 0 o (al retirar) si no hay saldo suficiente. Si todo va bien, cambian el saldo y apuntan el movimiento en la lista: `+50` o `-20`.\n- La propiedad `movimientos`: devuelve los movimientos como **tupla**, para que nadie pueda cambiarlos desde fuera.\n- `transferir(destino, cantidad)`: retira de esta cuenta e ingresa en la otra usando sus métodos.\n\nRecuerda: `__saldo` evita usos accidentales, pero no es una medida de seguridad.",
        """
        class CuentaBancaria:
            ...
        """,
        """
        class CuentaBancaria:
            def __init__(self, titular, saldo=0):
                if saldo < 0:
                    raise ValueError("El saldo inicial no puede ser negativo")
                self.titular = titular
                self.__saldo = saldo
                self.__movimientos = []

            @property
            def saldo(self):
                return self.__saldo

            @property
            def movimientos(self):
                return tuple(self.__movimientos)

            def ingresar(self, cantidad):
                if cantidad <= 0:
                    raise ValueError("La cantidad debe ser mayor que 0")
                self.__saldo += cantidad
                self.__movimientos.append(cantidad)

            def retirar(self, cantidad):
                if cantidad <= 0:
                    raise ValueError("La cantidad debe ser mayor que 0")
                if cantidad > self.__saldo:
                    raise ValueError("Saldo insuficiente")
                self.__saldo -= cantidad
                self.__movimientos.append(-cantidad)

            def transferir(self, destino, cantidad):
                self.retirar(cantidad)
                destino.ingresar(cantidad)


        ana = CuentaBancaria("Ana", 100)
        luis = CuentaBancaria("Luis")
        ana.transferir(luis, 30)
        print(ana.saldo, luis.saldo, ana.movimientos)
        """,
        [
            case(
                'c = CuentaBancaria("Ana", 100)\nassert c.saldo == 100, "La propiedad saldo devuelve el saldo"\nassert "_CuentaBancaria__saldo" in vars(c), "Guarda el saldo en el atributo privado self.__saldo"\ntry:\n    c.saldo = 1000\nexcept AttributeError:\n    pass\nelse:\n    raise AssertionError("saldo debe ser de solo lectura (una propiedad sin setter)")',
                error=f"{CID}.sin-setter",
            ),
            case(
                'c = CuentaBancaria("Ana", 100)\nc.ingresar(50)\nc.retirar(20)\nassert c.saldo == 130, "ingresar suma y retirar resta"\nfor mala in (0, -5):\n    try:\n        c.ingresar(mala)\n    except ValueError:\n        pass\n    else:\n        raise AssertionError(f"ingresar({mala}) debe lanzar ValueError")\ntry:\n    c.retirar(1000)\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError("Retirar más del saldo debe lanzar ValueError")\nassert c.saldo == 130, "Una operación rechazada no cambia el saldo"',
                error=f"{CID}.validacion-fuera",
            ),
            case(
                'try:\n    CuentaBancaria("Ana", -1)\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError("Un saldo inicial negativo debe lanzar ValueError")',
            ),
            case(
                'c = CuentaBancaria("Ana", 100)\nc.ingresar(50)\nc.retirar(20)\nassert c.movimientos == (50, -20), f"movimientos debe ser (50, -20); es {c.movimientos!r}"\nassert isinstance(c.movimientos, tuple), "movimientos se devuelve como tupla, que no se puede cambiar"',
            ),
            case(
                'a = CuentaBancaria("Ana", 100)\nb = CuentaBancaria("Luis")\na.transferir(b, 30)\nassert (a.saldo, b.saldo) == (70, 30), "transferir pasa el dinero de una cuenta a otra"\ntry:\n    a.transferir(b, 500)\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError("Sin saldo suficiente, transferir debe lanzar ValueError")\nassert (a.saldo, b.saldo) == (70, 30), "Si la transferencia falla, ninguna de las dos cuentas cambia"',
            ),
        ],
        "El saldo solo cambia a través de `ingresar` y `retirar`, que aplican las reglas antes de tocar nada. `transferir` reutiliza esos métodos, así que también valida. Y `movimientos` devuelve una tupla: desde fuera se puede leer el historial, pero no cambiarlo. Aun así, `__saldo` no es secreto: `c._CuentaBancaria__saldo` lo sigue mostrando.",
        "Crea `self.__saldo` y `self.__movimientos` en `__init__`. Para la solo lectura, usa `@property` sin setter. En `retirar`, comprueba primero y cambia después.",
        wrong=[
            (
                """
                class CuentaBancaria:
                    def __init__(self, titular, saldo=0):
                        self.titular = titular
                        self.saldo = saldo
                        self.movimientos = []

                    def ingresar(self, cantidad):
                        self.saldo += cantidad
                        self.movimientos.append(cantidad)

                    def retirar(self, cantidad):
                        self.saldo -= cantidad
                        self.movimientos.append(-cantidad)
                """,
                1,
            ),
            (
                """
                class CuentaBancaria:
                    def __init__(self, titular, saldo=0):
                        if saldo < 0:
                            raise ValueError("negativo")
                        self.titular = titular
                        self.__saldo = saldo
                        self.__movimientos = []

                    @property
                    def saldo(self):
                        return self.__saldo

                    @property
                    def movimientos(self):
                        return self.__movimientos

                    def ingresar(self, cantidad):
                        if cantidad <= 0:
                            raise ValueError("cantidad")
                        self.__saldo += cantidad
                        self.__movimientos.append(cantidad)

                    def retirar(self, cantidad):
                        if cantidad <= 0 or cantidad > self.__saldo:
                            raise ValueError("cantidad")
                        self.__saldo -= cantidad
                        self.__movimientos.append(-cantidad)

                    def transferir(self, destino, cantidad):
                        self.retirar(cantidad)
                        destino.ingresar(cantidad)
                """,
                4,
            ),
            (
                """
                class CuentaBancaria:
                    def __init__(self, titular, saldo=0):
                        if saldo < 0:
                            raise ValueError("negativo")
                        self.titular = titular
                        self.__saldo = saldo
                        self.__movimientos = []

                    @property
                    def saldo(self):
                        return self.__saldo

                    @property
                    def movimientos(self):
                        return tuple(self.__movimientos)

                    def ingresar(self, cantidad):
                        if cantidad <= 0:
                            raise ValueError("cantidad")
                        self.__saldo += cantidad
                        self.__movimientos.append(cantidad)

                    def retirar(self, cantidad):
                        if cantidad <= 0 or cantidad > self.__saldo:
                            raise ValueError("cantidad")
                        self.__saldo -= cantidad
                        self.__movimientos.append(-cantidad)

                    def transferir(self, destino, cantidad):
                        destino.ingresar(cantidad)
                        self.retirar(cantidad)
                """,
                5,
            ),
        ],
        level=2,
        daw=False,
    ),
    # ---------- Banco de preguntas de la unidad (cuestionario)
    choice(
        "poo4-16",
        CID,
        "Con esta clase y `p = Producto(10)`, ¿cómo se lee el precio?",
        [
            ("`p.precio`, sin paréntesis", None),
            (
                "`p.precio()`",
                f"{CID}.property-con-parentesis",
                "Una propiedad se usa como un atributo: con paréntesis se intentaría llamar al número y daría `TypeError`.",
            ),
            (
                "`p.get_precio()`",
                None,
                "La clase no define ningún método `get_precio`: la propiedad ya hace ese papel.",
            ),
            (
                "`p._precio()`",
                f"{CID}.privado-desde-fuera",
                "`_precio` es el dato interno (y es un número, no se llama). Desde fuera se usa la propiedad.",
            ),
        ],
        0,
        "`@property` convierte el método en algo que se lee como un atributo: `p.precio` ejecuta el método y devuelve `self._precio`.",
        code="""
        class Producto:
            def __init__(self, precio):
                self._precio = precio

            @property
            def precio(self):
                return self._precio
        """,
        level=1,
        daw=False,
        bank=True,
        qtype="codigo",
    ),
    choice(
        "poo4-17",
        CID,
        "Con `t = Termometro(20)`, ¿qué ocurre al ejecutar `t.temperatura = 80`?",
        [
            ("Se lanza `ValueError` y la temperatura sigue siendo 20", None),
            (
                "Se guarda 80, porque un atributo acepta cualquier valor",
                f"{CID}.validacion-fuera",
                "La asignación pasa por el setter, que comprueba el rango antes de guardar.",
            ),
            (
                "Se guarda 50, el máximo permitido",
                None,
                "El setter no corrige el valor: lanza una excepción y no guarda nada.",
            ),
            (
                "Se lanza `AttributeError`, porque la propiedad es de solo lectura",
                f"{CID}.sin-setter",
                "La propiedad tiene setter (`@temperatura.setter`), así que se puede asignar si el valor es válido.",
            ),
        ],
        0,
        "El setter valida antes de guardar en `self._temperatura`. Como 80 está fuera de rango, lanza la excepción y el dato anterior no cambia.",
        code="""
        class Termometro:
            def __init__(self, grados):
                self.temperatura = grados

            @property
            def temperatura(self):
                return self._temperatura

            @temperatura.setter
            def temperatura(self, valor):
                if not -50 <= valor <= 50:
                    raise ValueError("Temperatura fuera de rango")
                self._temperatura = valor
        """,
        level=2,
        daw=False,
        bank=True,
        qtype="codigo",
    ),
    choice(
        "poo4-18",
        CID,
        "En esta clase, ¿por qué `__init__` escribe `self.temperatura = grados` y no `self._temperatura = grados`?",
        [
            ("Para que el valor inicial también pase por el setter y se valide", None),
            (
                "Porque `self._temperatura` no se puede usar dentro de `__init__`",
                None,
                "Se puede usar en cualquier método; el motivo es que así se valida.",
            ),
            (
                "Da igual: las dos formas validan el valor",
                f"{CID}.validacion-fuera",
                "Asignar `self._temperatura` directamente se salta el setter: `Termometro(80)` se crearía sin error.",
            ),
            (
                "Para que la temperatura sea de solo lectura",
                f"{CID}.sin-setter",
                "La propiedad tiene setter: se puede cambiar después. Lo que se busca es validar desde el principio.",
            ),
        ],
        0,
        "Si `__init__` asigna por la propiedad, la regla se aplica también al crear el objeto: un termómetro no puede nacer con 80 grados.",
        code="""
        class Termometro:
            def __init__(self, grados):
                self.temperatura = grados

            @property
            def temperatura(self):
                return self._temperatura

            @temperatura.setter
            def temperatura(self, valor):
                if not -50 <= valor <= 50:
                    raise ValueError("Temperatura fuera de rango")
                self._temperatura = valor
        """,
        level=3,
        daw=False,
        bank=True,
        qtype="codigo",
    ),
    choice(
        "poo4-19",
        CID,
        "¿Qué muestra este programa?",
        [
            ("5", None),
            (
                "3",
                f"{CID}.privado-absoluto",
                "Un guion bajo no impide cambiar el atributo desde fuera: es solo un aviso.",
            ),
            (
                "AttributeError",
                f"{CID}.privado-absoluto",
                "Python no bloquea los atributos con un guion bajo; solo renombra los que llevan dos.",
            ),
            (
                "None",
                None,
                "El atributo existe y se le acaba de asignar 5.",
            ),
        ],
        0,
        "`_items` es interno solo por convenio. Python deja leerlo y cambiarlo desde fuera, aunque no se debería hacer.",
        code="""
        class Caja:
            def __init__(self):
                self._items = 3

        c = Caja()
        c._items = 5
        print(c._items)
        """,
        level=1,
        daw=False,
        bank=True,
        qtype="prediccion",
    ),
    choice(
        "poo4-20",
        CID,
        "¿Qué muestra este programa?",
        [
            ("100 0", None),
            (
                "0 0",
                f"{CID}.privado-desde-fuera",
                "Desde fuera `c.__saldo` no se renombra: crea un atributo nuevo y el saldo real (`_Cuenta__saldo`) sigue en 100.",
            ),
            (
                "100 100",
                None,
                "`c.__saldo = 0` sí crea un atributo con ese nombre exacto, y vale 0.",
            ),
            (
                "AttributeError",
                f"{CID}.privado-absoluto",
                "Los dos nombres existen: `_Cuenta__saldo` (creado en `__init__`) y `__saldo` (creado fuera).",
            ),
        ],
        0,
        "Dentro de la clase, `self.__saldo` se guarda como `_Cuenta__saldo`. Fuera de la clase no hay renombrado, así que `c.__saldo = 0` crea otro atributo distinto.",
        code="""
        class Cuenta:
            def __init__(self, saldo):
                self.__saldo = saldo

        c = Cuenta(100)
        c.__saldo = 0
        print(c._Cuenta__saldo, c.__saldo)
        """,
        level=2,
        daw=False,
        bank=True,
        qtype="prediccion",
    ),
    choice(
        "poo4-21",
        CID,
        "¿Qué muestra este programa?",
        [
            ("3", None),
            (
                "-2",
                f"{CID}.validacion-fuera",
                "`__init__` asigna por la propiedad, así que el -5 ya se convirtió en 0 al crear el producto.",
            ),
            (
                "0",
                None,
                "Después de crear el producto se le suman 3 al precio, que pasa por el setter: 0 + 3 = 3.",
            ),
            (
                "-5",
                None,
                "El setter guarda `max(valor, 0)`: nunca guarda un número negativo.",
            ),
        ],
        0,
        "Al crear el producto, el setter convierte -5 en 0. Después `p.precio + 3` vale 3 y el setter lo guarda tal cual.",
        code="""
        class Producto:
            def __init__(self, precio):
                self.precio = precio

            @property
            def precio(self):
                return self._precio

            @precio.setter
            def precio(self, valor):
                self._precio = max(valor, 0)

        p = Producto(-5)
        p.precio = p.precio + 3
        print(p.precio)
        """,
        level=3,
        daw=False,
        bank=True,
        qtype="prediccion",
    ),
    choice(
        "poo4-22",
        CID,
        "Este programa termina con `TypeError: 'float' object is not callable`. ¿Qué lo arregla?",
        [
            ("Leer la propiedad sin paréntesis: `print(c.area)`", None),
            (
                "Cambiar `self.radio ** 2` por `self.radio * 2`",
                None,
                "Eso cambia la fórmula (y la estropea), pero el error sigue: el problema son los paréntesis al usar `area`.",
            ),
            (
                "Escribir `return` con paréntesis: `return (3.14 * self.radio ** 2)`",
                None,
                "Los paréntesis del `return` no cambian nada: el fallo está en cómo se usa `area`.",
            ),
            (
                "Añadir un setter para `area`",
                f"{CID}.sin-setter",
                "Un setter sirve para asignar. Aquí solo se lee el área.",
            ),
        ],
        0,
        "`c.area` ya ejecuta el método y devuelve un número. Con `c.area()` se intenta llamar a ese número como si fuera una función.",
        code="""
        class Circulo:
            def __init__(self, radio):
                self.radio = radio

            @property
            def area(self):
                return 3.14 * self.radio ** 2

        c = Circulo(2)
        print(c.area())
        """,
        level=2,
        daw=False,
        bank=True,
        qtype="error",
    ),
    choice(
        "poo4-23",
        CID,
        "Queremos que el `saldo` de una cuenta se pueda leer desde fuera (`c.saldo`) pero no asignar. ¿Qué lo consigue?",
        [
            ("Una propiedad `saldo` con `@property` que devuelve `self._saldo`, sin setter", None),
            (
                "Guardarlo en `self.__saldo` y nada más",
                f"{CID}.privado-absoluto",
                "No se podría leer como `c.saldo`, y el renombrado tampoco impide cambiarlo con `c._Cuenta__saldo`.",
            ),
            (
                "Una propiedad con un setter que hace `self.saldo = valor`",
                f"{CID}.setter-recursivo",
                "Con setter se podría asignar, y además ese setter se llamaría a sí mismo sin fin.",
            ),
            (
                "Un método `saldo()` que devuelve `self._saldo`",
                f"{CID}.property-con-parentesis",
                "Habría que leerlo con paréntesis, y `c.saldo = 5` taparía el método sin dar ningún error.",
            ),
        ],
        0,
        "Una propiedad sin setter es de solo lectura: `c.saldo` funciona y `c.saldo = 5` lanza `AttributeError`.",
        level=1,
        daw=False,
        bank=True,
        qtype="solucion",
    ),
    choice(
        "poo4-24",
        CID,
        "El setter de la propiedad `edad` debe rechazar las edades negativas. ¿Qué versión es correcta?",
        [
            ("Si `valor < 0` lanza `ValueError`; si no, guarda el valor en `self._edad`", None),
            (
                "Comprueba el valor y lo guarda en `self.edad`",
                f"{CID}.setter-recursivo",
                "`self.edad = …` dentro del setter vuelve a llamar al setter, sin fin (`RecursionError`).",
            ),
            (
                'Si `valor < 0` hace `print("Edad no válida")` y después lo guarda igualmente',
                None,
                "El aviso no impide que el objeto se quede con una edad negativa.",
            ),
            (
                "No comprueba nada: el programa principal comprueba la edad antes de asignarla",
                f"{CID}.validacion-fuera",
                "Si la regla está fuera, cualquier parte del programa puede olvidarla. La clase debe protegerse sola.",
            ),
        ],
        0,
        "El setter es el sitio de la regla: valida primero y guarda en el atributo interno solo si el valor es correcto.",
        level=3,
        daw=False,
        bank=True,
        qtype="solucion",
    ),
    choice(
        "poo4-25",
        CID,
        "La clase `Usuario` guarda una contraseña. ¿Qué interfaz pública es la más adecuada?",
        [
            (
                "Los métodos `comprobar(clave)` y `cambiar_clave(actual, nueva)`, sin forma de leer la contraseña",
                None,
            ),
            (
                "Una propiedad `clave` con getter y setter, sin ninguna comprobación",
                f"{CID}.validacion-fuera",
                "Cualquiera podría leerla y cambiarla sin conocer la actual: la propiedad no protege nada.",
            ),
            (
                "Un atributo público `clave`",
                None,
                "Deja leer y cambiar la contraseña desde cualquier parte del programa.",
            ),
            (
                "Guardar la contraseña en un atributo de clase",
                None,
                "Un atributo de clase es el mismo para todos los usuarios.",
            ),
        ],
        0,
        "Encapsular no es solo ocultar: es decidir qué operaciones tienen sentido. Con una contraseña basta con poder comprobarla y cambiarla con reglas.",
        level=2,
        daw=False,
        bank=True,
        qtype="diseno",
    ),
    choice(
        "poo4-26",
        CID,
        "El `estado` de un `Pedido` solo puede pasar de `nuevo` a `enviado` y de `enviado` a `entregado`. ¿Qué diseño lo garantiza mejor?",
        [
            (
                "Un dato interno `_estado`, una propiedad `estado` de solo lectura y los métodos `enviar()` y `entregar()`, que comprueban el estado actual",
                None,
            ),
            (
                "Un atributo público `estado` y un comentario que explique el orden correcto",
                f"{CID}.validacion-fuera",
                'Un comentario no impide asignar `estado = "entregado"` a un pedido nuevo.',
            ),
            (
                "Una propiedad `estado` con un setter que acepta cualquier texto",
                None,
                "Si el setter no comprueba nada, la propiedad no añade ninguna protección.",
            ),
            (
                "Guardar el estado en un atributo de clase de `Pedido`",
                None,
                "Sería el mismo estado para todos los pedidos.",
            ),
        ],
        0,
        "La regla vive dentro del objeto: desde fuera solo se puede leer el estado y pedir los cambios permitidos, y cada método comprueba que el paso es válido.",
        level=3,
        daw=False,
        bank=True,
        qtype="diseno",
    ),
]

# Errores típicos (slug, etiqueta, por qué, qué pensar, cómo evitarlo)
ERRORS = [
    (
        "privado-absoluto",
        "Cree que `_x` o `__x` bloquean del todo el acceso",
        "En Python `_x` es solo un convenio y `__x` se renombra a `_Clase__x`. La protección real la dan las propiedades y los métodos que aplican las reglas.",
        "¿Qué impide de verdad que se rompa la regla: un guion bajo o un setter que valida?",
        "Usa `_x` para avisar y una propiedad o un método para proteger.",
    ),
    (
        "privado-desde-fuera",
        "Usa desde fuera un atributo privado en vez de la interfaz pública",
        "Desde fuera `objeto.__x` no existe (está renombrado) y los atributos internos pueden cambiar en cualquier versión de la clase.",
        "¿La clase me ofrece un método o una propiedad para esto?",
        "Fuera de la clase usa solo métodos y atributos sin guion bajo.",
    ),
    (
        "property-con-parentesis",
        "Llama a una propiedad con paréntesis",
        "Una propiedad ya devuelve su valor al leerla: `r.area()` intenta llamar al resultado y da `TypeError`.",
        "¿Tiene `@property` encima? Entonces se lee como un atributo.",
        "Escribe `objeto.propiedad`, sin paréntesis.",
    ),
    (
        "setter-recursivo",
        "Guarda el valor en la propia propiedad dentro del setter",
        "`self.edad = valor` dentro del setter de `edad` vuelve a llamar al setter sin fin (`RecursionError`).",
        "¿Dónde está guardado de verdad el dato?",
        "Guarda el valor en otro atributo con guion bajo: `self._edad = valor`.",
    ),
    (
        "validacion-fuera",
        "Se salta la validación al crear o al modificar el objeto",
        "Si `__init__` o un método escriben directamente `self._x`, el setter no se ejecuta y el objeto puede quedar con un valor no válido.",
        "¿Todas las asignaciones pasan por la propiedad que valida?",
        "En `__init__` y en los métodos asigna `self.x = …` (la propiedad), no `self._x`.",
    ),
    (
        "sin-setter",
        "Cree que una propiedad sin setter se puede asignar (o que un atributo normal es de solo lectura)",
        "Solo una propiedad sin setter es de solo lectura: asignarla da `AttributeError`. Un atributo normal se puede cambiar desde fuera.",
        "¿Este dato tiene `@property`? ¿Tiene `@x.setter`?",
        "Para que nadie cambie un dato desde fuera, guárdalo en `self._x` y exponlo con una propiedad sin setter.",
    ),
]

# Preguntas tipo test que ya existían y pasan al banco: (tipo, nivel, por qué falla cada distractor)
BANK_TAGS = {
    "poo4-01": (
        "teoria",
        1,
        [
            "Python no bloquea nada con un guion bajo: es solo un aviso entre programadores.",
            "La solo lectura se consigue con una propiedad sin setter; el guion bajo no cambia nada.",
            "Sigue siendo un dato de cada objeto, porque se crea con `self.`.",
        ],
    ),
    "poo4-08": (
        "error",
        2,
        [
            "`self.edad = valor` vuelve a llamar al setter, que vuelve a asignar, sin fin.",
            "Python no añade guiones bajos por su cuenta: hay que escribir `self._edad`.",
            "La sintaxis es correcta: el fallo aparece al ejecutar el setter.",
        ],
    ),
    "poo4-09": (
        "teoria",
        1,
        [
            "Con setter se puede cambiar; sin setter es de solo lectura, pero esa no es la ventaja frente a un método.",
            "Los métodos `get_` son válidos: la propiedad solo es más cómoda y deja añadir reglas después.",
            "El valor se sigue guardando en cada objeto, normalmente en `self._precio`.",
        ],
    ),
    "poo4-13": (
        "teoria",
        2,
        [
            "Sigue existiendo como `_Caja__pin` y se puede leer con ese nombre: no es una barrera de seguridad.",
            "El atributo existe mientras exista el objeto: Python no lo borra.",
            "Con dos guiones bajos Python sí cambia el nombre; con uno solo no hace nada.",
        ],
    ),
}
