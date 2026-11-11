# ruff: noqa: E501
"""Unidad 4 del módulo de POO: encapsulación y propiedades.

Concepto `poo-encapsulacion` (área `poo`): convenios `_x` y `__x` (name mangling), propiedades con
`@property` y su `setter`, atributos de solo lectura y validación del estado (invariantes).
La salida de los ejemplos la obtiene build_learning.py ejecutándolos.
"""

from exercises import bug, case, choice, code, fill, output
from poo_common import proposed

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
            "theory": "La **encapsulación** consiste en que cada objeto cuide de sus propios datos: el resto del programa usa su **interfaz pública** (métodos y propiedades) y no toca los detalles internos. Así se pueden cambiar esos detalles sin romper el código que usa la clase.\n\nPython no tiene `private` como Java: usa **convenios** con guiones bajos.\n\n- `nombre`: **público**, se puede usar desde fuera.\n- `_saldo`: **protegido** por convenio. Significa «es interno»; Python lo deja usar, pero un buen programador no lo hace desde fuera.\n- `__pin`: **privado**. Python le cambia el nombre a `_Caja__pin` (*name mangling*), así que `objeto.__pin` desde fuera da `AttributeError`. No es una caja fuerte: sigue existiendo con el nombre cambiado, pero evita usos accidentales y choques con subclases.\n\nDesde dentro de la clase se usa siempre igual: `self._saldo`, `self.__pin`.",
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
    "autonomous": ["poo4-11", "poo4-12"],
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
        "required": ["poo4-10", "poo4-11"],
        "text": [
            "Resolver el ejercicio guiado (`CuentaSegura`) y el autónomo `Termostato` con todos los tests superados.",
            "Dominar la unidad según el motor: al menos un 70 % de aciertos recientes en sus ejercicios, con varios tipos distintos.",
            "Completar las lecciones ayuda a organizarte, pero **no** demuestra la competencia: la demuestran los ejercicios.",
        ],
    },
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
