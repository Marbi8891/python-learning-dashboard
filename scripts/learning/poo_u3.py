# ruff: noqa: E501
"""Unidad 3 del módulo de POO: atributos y métodos.

Concepto `poo-atributos-metodos` (área `poo`): atributos de instancia y de clase, métodos de
instancia, de clase (`@classmethod`) y estáticos (`@staticmethod`), y métodos que cambian y
protegen el estado del objeto. La salida de los ejemplos la obtiene build_learning.py ejecutándolos.
"""

from exercises import bug, case, choice, code, fill, output
from poo_common import proposed

CID = "poo-atributos-metodos"

CONCEPT = {
    "id": CID,
    "title": "Atributos y métodos",
    "area": "poo",
    "requires": ["poo"],
    "daw": 2,
    "ut": "prog-ut5",
    "lessons": ["atributos-clase"],
    "summary": "Atributos de instancia y de clase, y métodos de instancia, de clase y estáticos.",
    "when": "Cuando un dato debe ser común a todos los objetos (un contador, un tipo de IVA) o una acción no depende de un objeto concreto (una conversión, otra forma de crear objetos).",
    "example": {
        "code": 'class Ticket:\n    iva = 21                          # atributo de clase\n    emitidos = 0\n\n    def __init__(self, importe):\n        self.importe = importe        # atributo de instancia\n        Ticket.emitidos += 1\n\n    def con_iva(self):                # método de instancia\n        return round(self.importe * (1 + Ticket.iva / 100), 2)\n\n    @classmethod\n    def cuantos(cls):                 # método de clase\n        return cls.emitidos\n\n\nt1 = Ticket(25)\nprint(Ticket.cuantos(), end=" ")\nt2 = Ticket(10)\nprint(Ticket.cuantos(), t2.emitidos)\nprint(t1.con_iva())',
        "lines": [
            [2, "Un atributo de clase es común a todos los tickets."],
            [6, "Un atributo de instancia es propio de cada ticket."],
            [7, "El contador compartido se cambia a través de la clase, no de `self`."],
            [12, "`@classmethod` recibe la clase (`cls`) en vez del objeto."],
            [20, "El atributo de clase también se puede leer desde un objeto: `t2.emitidos`."],
        ],
    },
    "errors": [],
    "related": ["poo", "funciones"],
}

UNIT = {
    "unit": {"module": "poo", "number": 3},
    "objectives": [
        "Distinguir los atributos de instancia (propios de cada objeto) de los de clase (compartidos).",
        "Modificar un atributo de clase sin crear por error uno de instancia que lo tape.",
        "Escribir métodos de instancia, de clase (`@classmethod`) y estáticos (`@staticmethod`), y elegir el adecuado.",
        "Llamar a métodos con parámetros y usar lo que devuelven.",
        "Escribir métodos que cambian el estado del objeto y rechazan valores no válidos.",
    ],
    "prior": "La Unidad 2: definir una clase, `__init__`, `self` y llamar a métodos. También conviene repasar `raise ValueError` de la unidad de excepciones.",
    "key": [
        [
            "Atributo de instancia",
            "Dato propio de cada objeto; se crea con `self.dato = valor`, normalmente en `__init__`.",
        ],
        [
            "Atributo de clase",
            "Dato definido en el cuerpo de la clase, compartido por todos sus objetos: `Clase.dato`.",
        ],
        [
            "Sombreado",
            "Asignar `objeto.dato = valor` crea un atributo de instancia que tapa al de clase solo para ese objeto.",
        ],
        ["Método de instancia", "Recibe `self`: trabaja con los datos de un objeto concreto."],
        [
            "Método de clase",
            "Lleva `@classmethod` y recibe `cls`, la clase. Sirve para datos compartidos y para crear objetos de otra forma.",
        ],
        [
            "Método estático",
            "Lleva `@staticmethod` y no recibe ni `self` ni `cls`: una utilidad relacionada con la clase.",
        ],
        [
            "Decorador",
            "La línea `@algo` encima de un `def` que cambia cómo se comporta ese método.",
        ],
    ],
    "sections": [
        {
            "id": f"{CID}.instancia-clase",
            "title": "Atributos de instancia y de clase",
            "theory": 'Los **atributos de instancia** se crean con `self.dato = valor` (normalmente en `__init__`) y cada objeto tiene los suyos. Los **atributos de clase** se escriben en el cuerpo de la clase, fuera de los métodos, y son **compartidos** por todos los objetos: sirven para constantes comunes (el centro, el IVA) o contadores.\n\n- Un atributo de clase se puede **leer** desde la clase (`Alumno.centro`) o desde cualquier objeto (`ana.centro`).\n- Para **cambiarlo** hay que hacerlo a través de la clase: `Alumno.total += 1`.\n- Si escribes `ana.centro = "Otro"` o `self.total += 1`, Python crea un atributo **de instancia** con ese nombre que tapa al de clase **solo para ese objeto** (se llama *sombreado*). El de clase no cambia.\n- Cuidado con las listas y diccionarios como atributo de clase: todos los objetos comparten **la misma** lista. Si cada objeto necesita la suya, créala en `__init__`.',
            "examples": [
                {
                    "code": 'class Alumno:\n    centro = "IES Python"       # atributo de clase: compartido\n    total = 0\n\n    def __init__(self, nombre):\n        self.nombre = nombre    # atributo de instancia: propio\n        Alumno.total += 1       # cambia el dato compartido\n\n\nana = Alumno("Ana")\nluis = Alumno("Luis")\nprint(ana.centro, luis.centro)\nprint(Alumno.total)\nluis.centro = "IES Java"        # crea un atributo de instancia que tapa el de clase\nprint(ana.centro, luis.centro, Alumno.centro)',
                    "lines": [
                        [2, "Definido en el cuerpo de la clase: lo comparten todos los alumnos."],
                        [6, "Cada alumno guarda su propio nombre."],
                        [
                            7,
                            "El contador se cambia a través de la clase, así que cuenta todos los objetos.",
                        ],
                        [12, "Los dos objetos leen el mismo atributo de clase."],
                        [
                            14,
                            "Asignar desde un objeto no cambia la clase: crea un atributo solo para `luis`.",
                        ],
                        [
                            15,
                            "`ana` y la clase siguen con «IES Python»; solo `luis` ve «IES Java».",
                        ],
                    ],
                }
            ],
            "quiz": ["poo3-01", "poo3-02", "poo3-03"],
        },
        {
            "id": f"{CID}.metodos",
            "title": "Métodos de instancia, de clase y estáticos",
            "theory": 'Hay tres tipos de métodos según lo que necesitan:\n\n- **De instancia** (los de siempre): reciben `self` y trabajan con los datos de **un objeto**. Se llaman sobre un objeto: `fecha.texto()`.\n- **De clase**: llevan el decorador `@classmethod` y reciben **`cls`**, la propia clase. Se usan para trabajar con atributos de clase o como **constructores alternativos**: `cls(...)` crea un objeto nuevo de esa clase. Se llaman sobre la clase: `Fecha.desde_texto("5-3-2024")`.\n- **Estáticos**: llevan `@staticmethod` y **no reciben ni `self` ni `cls`**. Son funciones de utilidad que tienen que ver con la clase pero no necesitan sus datos (validar, convertir). Se llaman `Fecha.es_bisiesto(2024)`.\n\nRegla rápida: ¿usa datos del objeto? → instancia. ¿Usa la clase o crea objetos? → de clase. ¿No usa ninguno de los dos? → estático.',
            "examples": [
                {
                    "code": 'class Fecha:\n    def __init__(self, dia, mes, anio):\n        self.dia = dia\n        self.mes = mes\n        self.anio = anio\n\n    def texto(self):                      # método de instancia\n        return f"{self.dia:02d}/{self.mes:02d}/{self.anio}"\n\n    @classmethod\n    def desde_texto(cls, cadena):         # método de clase: otro constructor\n        dia, mes, anio = cadena.split("-")\n        return cls(int(dia), int(mes), int(anio))\n\n    @staticmethod\n    def es_bisiesto(anio):                # método estático: una utilidad\n        return anio % 4 == 0 and (anio % 100 != 0 or anio % 400 == 0)\n\n\nf = Fecha.desde_texto("5-3-2024")\nprint(f.texto())\nprint(Fecha.es_bisiesto(2024), Fecha.es_bisiesto(1900))',
                    "lines": [
                        [7, "Método de instancia: usa los datos de esta fecha a través de `self`."],
                        [10, "`@classmethod` hace que el primer parámetro sea la clase (`cls`)."],
                        [13, "`cls(...)` crea y devuelve un objeto `Fecha` nuevo."],
                        [15, "`@staticmethod`: no recibe `self` ni `cls`, solo sus parámetros."],
                        [20, "El método de clase se llama sobre la clase y devuelve un objeto."],
                        [
                            22,
                            "El estático también se llama sobre la clase, sin crear ningún objeto.",
                        ],
                    ],
                }
            ],
            "quiz": ["poo3-04", "poo3-05", "poo3-06"],
        },
        {
            "id": f"{CID}.estado",
            "title": "Métodos que cambian y protegen el estado",
            "theory": "Los métodos de instancia son el sitio natural para **cambiar el estado** del objeto, y también para **protegerlo**: si un valor no tiene sentido (una cantidad negativa, más litros de los que caben), el método lo rechaza con `raise ValueError(...)` antes de tocar nada.\n\n- Valida **dentro** del método, no en cada sitio donde se use el objeto: así la regla está en un solo lugar.\n- Un método puede cambiar el estado y además **devolver** un resultado útil (el saldo nuevo, los litros actuales).\n- Una operación rechazada no debe dejar el objeto a medias: comprueba primero y cambia después.\n\nEn la Unidad 4 verás cómo ocultar los atributos para que nadie se salte estas reglas.",
            "examples": [
                {
                    "code": 'class Deposito:\n    def __init__(self, capacidad):\n        self.capacidad = capacidad\n        self.litros = 0\n\n    def llenar(self, litros):\n        if litros <= 0:\n            raise ValueError("La cantidad debe ser positiva")\n        self.litros = min(self.capacidad, self.litros + litros)\n        return self.litros\n\n    def vaciar(self):\n        self.litros = 0\n\n\nd = Deposito(50)\nprint(d.llenar(30))\nprint(d.llenar(30))\ntry:\n    d.llenar(-5)\nexcept ValueError as e:\n    print("Error:", e)',
                    "lines": [
                        [
                            7,
                            "Primero se comprueba: un valor no válido se rechaza sin cambiar nada.",
                        ],
                        [9, "Después se cambia el estado, sin pasar de la capacidad."],
                        [10, "Además devuelve el estado nuevo, útil para quien llama."],
                        [18, "El segundo llenado se queda en 50: el método protege el límite."],
                        [20, "Una cantidad negativa lanza `ValueError` y el depósito no cambia."],
                    ],
                }
            ],
            "quiz": ["poo3-07", "poo3-08", "poo3-09"],
        },
    ],
    "guided": ["poo3-10"],
    "autonomous": ["poo3-11", "poo3-12"],
    "selfcheck": ["poo3-13", "poo3-14"],
    "recap": [
        "Los atributos de instancia (`self.x`) son propios de cada objeto; los de clase se escriben en el cuerpo de la clase y se comparten.",
        "Un atributo de clase se cambia a través de la clase (`Clase.x += 1`); asignarlo desde un objeto crea uno de instancia que lo tapa.",
        "Una lista como atributo de clase la comparten todos los objetos: si cada uno necesita la suya, créala en `__init__`.",
        "`@classmethod` recibe `cls` (para datos de clase y constructores alternativos); `@staticmethod` no recibe ni `self` ni `cls`.",
        "Los métodos que cambian el estado deben validar antes y pueden devolver el resultado.",
    ],
    "pass": {
        "minScore": 0.7,
        "required": ["poo3-10", "poo3-11"],
        "text": [
            "Resolver el ejercicio guiado (`CuentaBancaria`) y el autónomo `Temperatura` con todos los tests superados.",
            "Dominar la unidad según el motor: al menos un 70 % de aciertos recientes en sus ejercicios, con varios tipos distintos.",
            "Completar las lecciones ayuda a organizarte, pero **no** demuestra la competencia: la demuestran los ejercicios.",
        ],
    },
    "curriculum": [
        proposed("0485-RA2-d", "Se usan métodos y atributos (propiedades) de los objetos."),
        proposed("0485-RA2-e", "Se llaman métodos estáticos (`Clase.metodo(...)`)."),
        proposed("0485-RA2-f", "Se pasan parámetros en la llamada a los métodos."),
        proposed("0485-RA4-c", "Se definen atributos de instancia y de clase, y métodos."),
        proposed("0485-RA4-h", "Se crean y usan métodos estáticos (`@staticmethod`) y de clase."),
    ],
}

EXERCISES = [
    # ---------- Lección «Atributos de instancia y de clase»
    output(
        "poo3-01",
        CID,
        """
        class Visita:
            total = 0

            def __init__(self):
                Visita.total += 1

        Visita()
        Visita()
        v = Visita()
        print(Visita.total, v.total)
        """,
        "3 3",
        "`total` es un atributo de clase y cada objeto nuevo lo aumenta a través de la clase. Desde el objeto `v` se lee el mismo valor compartido.",
        traps={"1 1": f"{CID}.self-en-atributo-clase", "3 0": None},
        level=1,
        daw=False,
    ),
    output(
        "poo3-02",
        CID,
        """
        class Config:
            idioma = "es"

        a = Config()
        b = Config()
        a.idioma = "en"
        print(a.idioma, b.idioma, Config.idioma)
        """,
        "en es es",
        '`a.idioma = "en"` no cambia el atributo de clase: crea un atributo de instancia solo en `a` que lo tapa. `b` y la clase siguen viendo `"es"`.',
        traps={"en en en": f"{CID}.self-en-atributo-clase"},
        level=2,
        daw=False,
    ),
    bug(
        "poo3-03",
        CID,
        "Debería mostrar `2` (los pedidos creados). ¿Qué línea falla?",
        """
        class Pedido:
            total = 0

            def __init__(self, producto):
                self.producto = producto
                self.total += 1

        Pedido("pan")
        Pedido("leche")
        print(Pedido.total)
        """,
        6,
        "        Pedido.total += 1",
        "2",
        f"{CID}.self-en-atributo-clase",
        "`self.total += 1` lee el atributo de clase (0) y guarda el 1 en un atributo **nuevo** del objeto: el contador de la clase nunca cambia y se muestra 0. Hay que cambiarlo a través de la clase: `Pedido.total += 1`.",
        level=2,
        daw=False,
    ),
    # ---------- Lección «Métodos de instancia, de clase y estáticos»
    choice(
        "poo3-04",
        CID,
        "En un método con `@classmethod`, ¿qué recibe el primer parámetro `cls`?",
        [
            ("La propia clase, por eso `cls(...)` crea un objeto nuevo", None),
            ("El objeto con el que se ha llamado, igual que `self`", f"{CID}.tipo-metodo"),
            ("Nada: los métodos de clase no tienen parámetros", f"{CID}.tipo-metodo"),
            ("Una copia del último objeto creado", None),
        ],
        0,
        "`cls` es la clase. Con ella se leen o cambian los atributos de clase y se pueden crear objetos (`return cls(...)`), lo que permite escribir constructores alternativos.",
        level=1,
        daw=False,
    ),
    output(
        "poo3-05",
        CID,
        """
        class Conversor:
            @staticmethod
            def a_fahrenheit(celsius):
                return celsius * 9 / 5 + 32

        print(Conversor.a_fahrenheit(100))
        print(Conversor().a_fahrenheit(0))
        """,
        "212.0\n32.0",
        "Un método estático no recibe `self`: se puede llamar sobre la clase o sobre un objeto y solo usa sus parámetros. La división `/` siempre da `float`, por eso sale `212.0`.",
        traps={"212\n32": None},
        level=2,
        daw=False,
    ),
    bug(
        "poo3-06",
        CID,
        "Debería mostrar `8`. ¿Qué línea falla?",
        """
        class Calculo:
            @staticmethod
            def doble(self, x):
                return x * 2

        print(Calculo.doble(4))
        """,
        3,
        "    def doble(x):",
        "8",
        f"{CID}.static-con-self",
        "Un método estático **no** recibe `self`: el 4 se queda en `self` y falta `x` (`TypeError: missing 1 required positional argument`). Solo lleva sus propios parámetros.",
        level=2,
        daw=False,
    ),
    # ---------- Lección «Métodos que cambian y protegen el estado»
    output(
        "poo3-07",
        CID,
        """
        class Hucha:
            def __init__(self):
                self.dinero = 0

            def meter(self, euros):
                self.dinero += euros
                return self.dinero

        h = Hucha()
        h.meter(5)
        total = h.meter(10)
        print(total, h.dinero)
        """,
        "15 15",
        "`meter` cambia el estado y además devuelve el dinero acumulado. El primer resultado no se guarda, pero el estado sí cambió: 5 + 10 = 15.",
        traps={"10 15": None, "10 10": f"{CID}.tipo-metodo"},
        level=1,
        daw=False,
    ),
    choice(
        "poo3-08",
        CID,
        "Una `Cuenta` no debe quedarse nunca con saldo negativo. ¿Dónde es mejor comprobarlo?",
        [
            (
                "Dentro del método `retirar`, que lanza `ValueError` si no hay saldo suficiente",
                None,
            ),
            ("En cada parte del programa que use la cuenta, antes de llamar a `retirar`", None),
            ("En ningún sitio: Python no deja guardar números negativos en un atributo", None),
            ("En un atributo de clase que todas las cuentas comparten", f"{CID}.tipo-metodo"),
        ],
        0,
        "La regla pertenece a la cuenta: si se comprueba dentro de `retirar` está en un solo lugar y nadie la olvida. Python no impide valores negativos por sí solo.",
        level=1,
        daw=False,
    ),
    fill(
        "poo3-09",
        CID,
        "Completa el decorador para que `cuantas()` reciba la clase en `cls`.",
        """
        class Pieza:
            creadas = 0

            def __init__(self):
                Pieza.creadas += 1

            ___
            def cuantas(cls):
                return cls.creadas

        Pieza()
        Pieza()
        print(Pieza.cuantas())
        """,
        ["@classmethod"],
        "`@classmethod` hace que el primer parámetro sea la clase. Con `@staticmethod` no recibiría nada y faltaría el argumento `cls`.",
        expect="2",
        traps={"@staticmethod": f"{CID}.tipo-metodo", "classmethod": None},
        level=2,
        daw=False,
    ),
    # ---------- Ejercicio guiado
    code(
        "poo3-10",
        CID,
        "**Ejercicio guiado: `CuentaBancaria`.** Los atributos de clase ya están. Sigue los pasos:\n\n1. En `__init__(self, titular, saldo=0)` guarda los dos datos y suma 1 a `CuentaBancaria.abiertas` (a través de la clase).\n2. Añade el método estático `importe_valido(cantidad)`, que devuelva `True` si la cantidad es mayor que 0.\n3. Añade `ingresar(cantidad)` y `retirar(cantidad)`: si el importe no es válido, o si no hay saldo suficiente para retirar, lanza `ValueError`; si todo va bien, cambian el saldo y **devuelven** el saldo nuevo.\n4. Añade el método de clase `total_abiertas(cls)`, que devuelva el número de cuentas abiertas.",
        """
        class CuentaBancaria:
            banco = "PyBank"
            abiertas = 0

            def __init__(self, titular, saldo=0):
                # Paso 1: guarda titular y saldo, y suma 1 a las cuentas abiertas
                ...

            # Paso 2: @staticmethod importe_valido(cantidad)

            # Paso 3: ingresar(cantidad) y retirar(cantidad)

            # Paso 4: @classmethod total_abiertas(cls)


        c = CuentaBancaria("Ana", 100)
        print(c.ingresar(50))
        print(c.retirar(30))
        print(CuentaBancaria.total_abiertas())
        """,
        """
        class CuentaBancaria:
            banco = "PyBank"
            abiertas = 0

            def __init__(self, titular, saldo=0):
                self.titular = titular
                self.saldo = saldo
                CuentaBancaria.abiertas += 1

            @staticmethod
            def importe_valido(cantidad):
                return cantidad > 0

            def ingresar(self, cantidad):
                if not CuentaBancaria.importe_valido(cantidad):
                    raise ValueError("El importe debe ser positivo")
                self.saldo += cantidad
                return self.saldo

            def retirar(self, cantidad):
                if not CuentaBancaria.importe_valido(cantidad):
                    raise ValueError("El importe debe ser positivo")
                if cantidad > self.saldo:
                    raise ValueError("Saldo insuficiente")
                self.saldo -= cantidad
                return self.saldo

            @classmethod
            def total_abiertas(cls):
                return cls.abiertas


        c = CuentaBancaria("Ana", 100)
        print(c.ingresar(50))
        print(c.retirar(30))
        print(CuentaBancaria.total_abiertas())
        """,
        [
            case(
                'a = CuentaBancaria("Eva", 10)\nassert (a.titular, a.saldo) == ("Eva", 10), "Guarda titular y saldo como atributos con self"\nassert CuentaBancaria("Leo").saldo == 0, "Si no se indica, el saldo empieza en 0"',
            ),
            case(
                'a = CuentaBancaria("Eva", 10)\nassert a.ingresar(5) == 15, "ingresar() debe sumar y devolver el saldo nuevo"\nassert a.retirar(15) == 0, "retirar() debe restar y devolver el saldo nuevo"\nfor mal in (lambda: a.retirar(1), lambda: a.ingresar(-3), lambda: a.ingresar(0)):\n    try:\n        mal()\n    except ValueError:\n        pass\n    else:\n        raise AssertionError("Sin saldo suficiente o con un importe no positivo debe lanzarse ValueError")\nassert a.saldo == 0, "Una operación rechazada no debe cambiar el saldo"',
            ),
            case(
                'antes = CuentaBancaria.total_abiertas()\nx = CuentaBancaria("X")\nCuentaBancaria("Y")\nassert CuentaBancaria.total_abiertas() == antes + 2, "Cada cuenta nueva debe sumar 1 a CuentaBancaria.abiertas (a través de la clase)"\nassert "abiertas" not in vars(x), "El contador es de la clase: usa CuentaBancaria.abiertas, no self.abiertas"\nassert isinstance(CuentaBancaria.__dict__.get("importe_valido"), staticmethod), "importe_valido debe llevar @staticmethod"\nassert isinstance(CuentaBancaria.__dict__.get("total_abiertas"), classmethod), "total_abiertas debe llevar @classmethod"\nassert CuentaBancaria.importe_valido(5) and not CuentaBancaria.importe_valido(0), "importe_valido: True solo si la cantidad es mayor que 0"',
                error=f"{CID}.self-en-atributo-clase",
            ),
        ],
        "El saldo es de cada cuenta (atributo de instancia) y el contador, de todas (atributo de clase, que se cambia con `CuentaBancaria.abiertas`). Validar es una utilidad sin datos propios (estático) y contar las cuentas trabaja con la clase (de clase).",
        "Escribe `@staticmethod` encima de `def importe_valido(cantidad):` y `@classmethod` encima de `def total_abiertas(cls):`. En `ingresar` y `retirar`, comprueba primero y cambia el saldo después.",
        wrong=[
            (
                """
                class CuentaBancaria:
                    banco = "PyBank"
                    abiertas = 0

                    def __init__(self, titular, saldo=0):
                        self.titular = titular
                        self.saldo = saldo
                        self.abiertas += 1

                    @staticmethod
                    def importe_valido(cantidad):
                        return cantidad > 0

                    def ingresar(self, cantidad):
                        if not CuentaBancaria.importe_valido(cantidad):
                            raise ValueError("El importe debe ser positivo")
                        self.saldo += cantidad
                        return self.saldo

                    def retirar(self, cantidad):
                        if not CuentaBancaria.importe_valido(cantidad):
                            raise ValueError("El importe debe ser positivo")
                        if cantidad > self.saldo:
                            raise ValueError("Saldo insuficiente")
                        self.saldo -= cantidad
                        return self.saldo

                    @classmethod
                    def total_abiertas(cls):
                        return cls.abiertas
                """,
                3,
            ),
            (
                """
                class CuentaBancaria:
                    banco = "PyBank"
                    abiertas = 0

                    def __init__(self, titular, saldo=0):
                        self.titular = titular
                        self.saldo = saldo
                        CuentaBancaria.abiertas += 1

                    def ingresar(self, cantidad):
                        self.saldo += cantidad
                        return self.saldo

                    def retirar(self, cantidad):
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
        "poo3-11",
        CID,
        "**Ejercicio autónomo: `Temperatura`.** Crea la clase con:\n\n- El atributo de clase `CERO_ABSOLUTO = -273.15`.\n- El método estático `es_valida(celsius)`: `True` si la temperatura no está por debajo del cero absoluto.\n- `__init__(self, celsius)`: lanza `ValueError` si la temperatura no es válida; si lo es, la guarda en `self.celsius`.\n- El método `a_fahrenheit()`: devuelve `celsius * 9 / 5 + 32`.\n- El método de clase `desde_fahrenheit(cls, grados)`: crea y **devuelve un objeto** `Temperatura` a partir de grados Fahrenheit (`(grados - 32) * 5 / 9`).",
        """
        class Temperatura:
            CERO_ABSOLUTO = -273.15
            ...
        """,
        """
        class Temperatura:
            CERO_ABSOLUTO = -273.15

            def __init__(self, celsius):
                if not Temperatura.es_valida(celsius):
                    raise ValueError("Por debajo del cero absoluto")
                self.celsius = celsius

            @staticmethod
            def es_valida(celsius):
                return celsius >= Temperatura.CERO_ABSOLUTO

            def a_fahrenheit(self):
                return self.celsius * 9 / 5 + 32

            @classmethod
            def desde_fahrenheit(cls, grados):
                return cls((grados - 32) * 5 / 9)


        t = Temperatura(25)
        print(t.a_fahrenheit())
        print(Temperatura.desde_fahrenheit(212).celsius)
        print(Temperatura.es_valida(-300))
        """,
        [
            case(
                't = Temperatura(100)\nassert t.celsius == 100, "Guarda la temperatura en self.celsius"\nassert t.a_fahrenheit() == 212, f"100 °C son 212 °F; a_fahrenheit() devuelve {t.a_fahrenheit()!r}"',
            ),
            case(
                't = Temperatura.desde_fahrenheit(212)\nassert isinstance(t, Temperatura), "desde_fahrenheit debe devolver un objeto Temperatura (return cls(...)), no un número"\nassert round(t.celsius, 2) == 100, "212 °F son 100 °C"\nassert isinstance(Temperatura.__dict__.get("desde_fahrenheit"), classmethod), "desde_fahrenheit debe llevar @classmethod"',
                error=f"{CID}.tipo-metodo",
            ),
            case(
                'assert Temperatura.es_valida(-273.15) is True, "El cero absoluto justo es válido"\nassert Temperatura.es_valida(-300) is False, "-300 °C está por debajo del cero absoluto"\ntry:\n    Temperatura(-300)\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError("Temperatura(-300) debe lanzar ValueError")',
            ),
        ],
        "La constante es común a todas las temperaturas (atributo de clase); validar no necesita ningún objeto (estático); convertir usa los datos de una temperatura (instancia), y crear una temperatura desde °F es un constructor alternativo (de clase).",
        "En `desde_fahrenheit` calcula los grados Celsius y termina con `return cls(celsius)`. En `__init__`, llama a `Temperatura.es_valida(celsius)` antes de guardar nada.",
        wrong=[
            (
                """
                class Temperatura:
                    CERO_ABSOLUTO = -273.15

                    def __init__(self, celsius):
                        if not Temperatura.es_valida(celsius):
                            raise ValueError("Por debajo del cero absoluto")
                        self.celsius = celsius

                    @staticmethod
                    def es_valida(celsius):
                        return celsius >= Temperatura.CERO_ABSOLUTO

                    def a_fahrenheit(self):
                        return self.celsius * 9 / 5 + 32

                    @staticmethod
                    def desde_fahrenheit(grados):
                        return (grados - 32) * 5 / 9
                """,
                2,
            ),
        ],
        level=2,
        daw=False,
    ),
    code(
        "poo3-12",
        CID,
        "**Ejercicio autónomo: el IVA de una tienda.** Crea la clase `Producto` con:\n\n- El atributo de clase `iva = 21` (el mismo para todos los productos).\n- `__init__(self, nombre, precio)`.\n- `precio_final()`: devuelve el precio con IVA redondeado a 2 decimales (`round(..., 2)`).\n- El método de clase `cambiar_iva(cls, nuevo)`: cambia el IVA de **todos** los productos.\n\nPor ejemplo, un producto de 10 € cuesta 12.1 con el 21 % y 11.0 después de `Producto.cambiar_iva(10)`.",
        """
        class Producto:
            ...
        """,
        """
        class Producto:
            iva = 21

            def __init__(self, nombre, precio):
                self.nombre = nombre
                self.precio = precio

            def precio_final(self):
                return round(self.precio * (1 + Producto.iva / 100), 2)

            @classmethod
            def cambiar_iva(cls, nuevo):
                cls.iva = nuevo


        libro = Producto("Libro", 20)
        print(libro.precio_final())
        Producto.cambiar_iva(4)
        print(libro.precio_final())
        """,
        [
            case(
                'assert "iva" in vars(Producto), "iva debe ser un atributo de clase: escríbelo en el cuerpo de la clase"\nProducto.iva = 21\np = Producto("A", 10)\nassert p.precio_final() == 12.1, f"10 € con un 21 % son 12.1; precio_final() devuelve {p.precio_final()!r}"',
            ),
            case(
                'Producto.iva = 21\np = Producto("A", 10)\nq = Producto("B", 20)\ntry:\n    Producto.cambiar_iva(10)\n    assert p.precio_final() == 11.0 and q.precio_final() == 22.0, "cambiar_iva debe cambiar el IVA de TODOS los productos"\n    assert isinstance(Producto.__dict__.get("cambiar_iva"), classmethod), "cambiar_iva debe llevar @classmethod y cambiar cls.iva"\nfinally:\n    Producto.iva = 21',
                error=f"{CID}.tipo-metodo",
            ),
            case(
                'Producto.iva = 21\np = Producto("A", 9.99)\nassert p.precio_final() == 12.09, f"Redondea a 2 decimales: 9.99 € con IVA son 12.09; devuelve {p.precio_final()!r}"\nassert "iva" not in vars(p), "El IVA es de la clase: no lo guardes en cada producto"',
                error=f"{CID}.self-en-atributo-clase",
            ),
        ],
        "El IVA es común a todos los productos, así que es un atributo de clase y se cambia con un método de clase (`cls.iva = nuevo`). El precio final depende de cada producto: método de instancia.",
        "Pon `iva = 21` en el cuerpo de la clase y escribe `@classmethod` encima de `def cambiar_iva(cls, nuevo):`.",
        wrong=[
            (
                """
                class Producto:
                    iva = 21

                    def __init__(self, nombre, precio):
                        self.nombre = nombre
                        self.precio = precio

                    def precio_final(self):
                        return round(self.precio * (1 + self.iva / 100), 2)

                    def cambiar_iva(self, nuevo):
                        self.iva = nuevo
                """,
                2,
            ),
        ],
        level=2,
        daw=False,
    ),
    # ---------- Autoevaluación
    choice(
        "poo3-13",
        CID,
        "Quieres añadir a la clase `Cliente` una función `es_dni_valido(texto)` que no usa ningún dato del objeto ni de la clase. ¿Qué tipo de método encaja mejor?",
        [
            ("Un método estático, con `@staticmethod`", None),
            ("Un método de instancia, con `self`", f"{CID}.tipo-metodo"),
            ("Un método de clase, con `@classmethod`", f"{CID}.tipo-metodo"),
            ("Un atributo de clase", None),
        ],
        0,
        'Si no necesita ni el objeto ni la clase, es una utilidad: método estático. Se llama sin crear ningún cliente: `Cliente.es_dni_valido("12345678Z")`.',
        level=1,
        daw=False,
    ),
    output(
        "poo3-14",
        CID,
        """
        class Grupo:
            miembros = []

            def __init__(self, nombre):
                self.nombre = nombre

            def unir(self, persona):
                self.miembros.append(persona)

        a = Grupo("A")
        b = Grupo("B")
        a.unir("Ana")
        print(len(b.miembros))
        """,
        "1",
        "`miembros` es una lista de **clase**: `append` no crea un atributo nuevo, cambia la lista compartida, así que `b` también ve a Ana. Si cada grupo necesita la suya, se crea en `__init__` con `self.miembros = []`.",
        traps={"0": f"{CID}.lista-de-clase"},
        level=2,
        daw=False,
    ),
]

# Errores típicos (slug, etiqueta, por qué, qué pensar, cómo evitarlo)
ERRORS = [
    (
        "self-en-atributo-clase",
        "Cambia un atributo de clase a través de `self` o de un objeto",
        "`self.total += 1` u `objeto.dato = valor` crean un atributo de instancia que tapa al de clase: el valor compartido no cambia.",
        "¿Este dato es de cada objeto o de todos? Si es de todos, ¿lo estoy cambiando a través de la clase?",
        "Para cambiar un atributo de clase escribe `Clase.dato = …` (o `cls.dato` en un método de clase).",
    ),
    (
        "static-con-self",
        "Pone `self` en un método estático",
        "Un método con `@staticmethod` no recibe el objeto: si se declara `self`, el primer argumento cae ahí y falta otro.",
        "¿Este método lleva `@staticmethod`? Entonces sus parámetros son solo los datos que necesita.",
        "En un estático no escribas `self` ni `cls`; si necesitas el objeto, hazlo método de instancia.",
    ),
    (
        "tipo-metodo",
        "Elige mal entre método de instancia, de clase y estático",
        "Cada tipo recibe algo distinto: `self` (el objeto), `cls` (la clase) o nada. Si el tipo no encaja, falta un argumento o no se puede hacer lo que se quiere (por ejemplo, crear un objeto sin `cls`).",
        "¿Uso datos del objeto, de la clase o de ninguno de los dos?",
        "Datos del objeto → instancia; datos de la clase o crear objetos → `@classmethod`; ninguno → `@staticmethod`.",
    ),
    (
        "lista-de-clase",
        "Usa una lista o diccionario como atributo de clase pensando que cada objeto tiene el suyo",
        "Un atributo de clase mutable es uno solo para todos: `append` lo cambia para todos los objetos.",
        "¿Cada objeto necesita su propia lista?",
        "Crea las listas y diccionarios propios de cada objeto dentro de `__init__` con `self.`.",
    ),
]
