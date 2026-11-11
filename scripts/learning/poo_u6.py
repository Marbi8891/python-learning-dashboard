# ruff: noqa: E501
"""Unidad 6 del módulo de POO: polimorfismo.

Concepto `poo-polimorfismo` (área `poo`): el mismo mensaje con comportamientos distintos, *duck
typing*, clases abstractas con `abc` (el equivalente a las interfaces) y código que no pregunta por el
tipo. La salida de los ejemplos la obtiene build_learning.py ejecutándolos.
"""

from exercises import bug, case, choice, code, fill, output
from poo_common import proposed

CID = "poo-polimorfismo"

CONCEPT = {
    "id": CID,
    "title": "Polimorfismo",
    "area": "poo",
    "requires": ["poo-herencia"],
    "daw": 2,
    "ut": "prog-ut6",
    "lessons": ["herencia"],
    "summary": "Tratar igual a objetos distintos: el mismo método con distinto comportamiento, duck typing y clases abstractas.",
    "when": "Cuando un programa trabaja con objetos de varias clases que hacen «lo mismo» de forma distinta (pagos, notificaciones, figuras) y no quieres llenar el código de `if` por cada tipo.",
    "example": {
        "code": 'from abc import ABC, abstractmethod\n\n\nclass Pago(ABC):                      # clase abstracta: el contrato\n    @abstractmethod\n    def cobrar(self, importe):\n        ...\n\n\nclass Tarjeta(Pago):\n    def cobrar(self, importe):\n        return f"{importe} € con tarjeta"\n\n\nclass Bizum(Pago):\n    def cobrar(self, importe):\n        return f"{importe} € por Bizum"\n\n\ndef pagar_todo(pagos, importe):\n    for pago in pagos:                # no pregunta de qué tipo es\n        print(pago.cobrar(importe))\n\n\npagar_todo([Tarjeta(), Bizum()], 20)',
        "lines": [
            [4, "`Pago` dice qué deben saber hacer todos los pagos, pero no cómo."],
            [5, "`@abstractmethod`: cada subclase está obligada a implementarlo."],
            [11, "Cada forma de pago cobra a su manera."],
            [
                21,
                "La función solo envía el mismo mensaje, `cobrar`; cada objeto responde a su modo.",
            ],
        ],
    },
    "errors": [],
    "related": ["poo-herencia", "funciones"],
}

UNIT = {
    "unit": {"module": "poo", "number": 6},
    "objectives": [
        "Explicar el polimorfismo: el mismo método produce comportamientos distintos según el objeto.",
        "Recorrer colecciones de objetos de clases distintas llamando al mismo método.",
        "Aplicar el *duck typing* de Python: lo que importa es qué sabe hacer un objeto, no su clase.",
        "Definir clases abstractas con `abc.ABC` y `@abstractmethod` como contrato (interfaz).",
        "Sustituir cadenas de `if isinstance(...)` por métodos polimórficos.",
    ],
    "prior": "La Unidad 5 (herencia, sobrescribir métodos y `super()`) y recorrer listas con `for`.",
    "key": [
        [
            "Polimorfismo",
            "«Muchas formas»: un mismo mensaje (`objeto.metodo()`) se ejecuta de forma distinta según la clase del objeto.",
        ],
        ["Mensaje", "Llamar a un método sobre un objeto: `figura.area()`."],
        [
            "Duck typing",
            "«Si camina como un pato y hace cuac, es un pato»: basta con que el objeto tenga el método.",
        ],
        [
            "Clase abstracta",
            "Una clase que no se puede instanciar y sirve de modelo para sus subclases (`class Forma(ABC)`).",
        ],
        [
            "Método abstracto",
            "Un método marcado con `@abstractmethod` que toda subclase concreta debe implementar.",
        ],
        [
            "Interfaz",
            "El conjunto de métodos que un objeto promete tener. En Python se expresa con clases abstractas o por convenio.",
        ],
    ],
    "sections": [
        {
            "id": f"{CID}.mismo-mensaje",
            "title": "Mismo método, distinto comportamiento",
            "theory": '**Polimorfismo** significa «muchas formas». Cuando varias clases tienen un método con el **mismo nombre**, el programa puede llamarlo sin saber de qué clase es cada objeto: cada uno responde **a su manera**. Es la consecuencia natural de sobrescribir métodos (Unidad 5).\n\nAsí, en vez de escribir\n\n```\nif tipo == "perro": ...\nelif tipo == "gato": ...\n```\n\nse escribe `animal.hablar()` y punto. Añadir un animal nuevo es crear una clase con su `hablar()`, sin tocar el código que los recorre.\n\n- El método se llama **con paréntesis**: `animal.hablar` sin ellos es el propio método, no su resultado.\n- Un método de la superclase que llama a `self.otro()` usará la versión de la subclase: también es polimorfismo.',
            "examples": [
                {
                    "code": 'class Animal:\n    def __init__(self, nombre):\n        self.nombre = nombre\n\n    def hablar(self):\n        return "..."\n\n    def presentarse(self):\n        return f"{self.nombre} dice {self.hablar()}"   # usa la versión de cada uno\n\n\nclass Perro(Animal):\n    def hablar(self):\n        return "guau"\n\n\nclass Gato(Animal):\n    def hablar(self):\n        return "miau"\n\n\nfor animal in [Perro("Toby"), Gato("Misi"), Animal("Bicho")]:\n    print(animal.presentarse())',
                    "lines": [
                        [
                            9,
                            "`presentarse` llama a `self.hablar()`: el resultado depende del objeto.",
                        ],
                        [13, "Cada subclase sobrescribe `hablar`."],
                        [22, "El bucle no pregunta por la clase: envía el mismo mensaje a todos."],
                    ],
                }
            ],
            "quiz": ["poo6-01", "poo6-02", "poo6-03"],
        },
        {
            "id": f"{CID}.duck",
            "title": "Duck typing: lo que importa es lo que sabe hacer",
            "theory": 'En Python el polimorfismo **no exige herencia**. Una función que llama a `x.texto()` funciona con **cualquier** objeto que tenga ese método, sea de la clase que sea. Es el *duck typing*: «si camina como un pato y hace cuac, es un pato».\n\nYa lo usas sin saberlo: `len()` funciona con textos, listas y diccionarios; `for` recorre cualquier cosa iterable.\n\n- Si el objeto **no** tiene el método, salta `AttributeError` al llamarlo.\n- Para aceptar objetos opcionales se puede comprobar con `hasattr(objeto, "metodo")` o capturar el `AttributeError`.\n- Evita preguntar el tipo con `isinstance` para decidir qué hacer: si cada clase tiene su método, el código queda abierto a clases nuevas.',
            "examples": [
                {
                    "code": 'class Pato:\n    def sonido(self):\n        return "cuac"\n\n\nclass Robot:                     # no hereda de Pato\n    def sonido(self):\n        return "bip"\n\n\nclass Piedra:\n    pass\n\n\ndef hacer_ruido(cosa):\n    if hasattr(cosa, "sonido"):\n        return cosa.sonido()\n    return "(silencio)"\n\n\nfor cosa in [Pato(), Robot(), Piedra()]:\n    print(hacer_ruido(cosa))\nprint(len("hola"), len([1, 2]), len({"a": 1}))',
                    "lines": [
                        [
                            6,
                            "`Robot` no tiene nada que ver con `Pato`, pero también tiene `sonido`.",
                        ],
                        [
                            16,
                            "`hasattr` comprueba si el objeto sabe hacer algo, sin mirar su clase.",
                        ],
                        [22, "`Piedra` no tiene `sonido`: se trata sin error."],
                        [
                            23,
                            "`len` es polimórfico: funciona con cualquier objeto que tenga longitud.",
                        ],
                    ],
                }
            ],
            "quiz": ["poo6-04", "poo6-05", "poo6-06"],
        },
        {
            "id": f"{CID}.abstractas",
            "title": "Clases abstractas e interfaces",
            "theory": "A veces quieres **obligar** a que todas las subclases tengan ciertos métodos. Para eso están las **clases abstractas** del módulo `abc`:\n\n```\nfrom abc import ABC, abstractmethod\n\nclass Forma(ABC):\n    @abstractmethod\n    def area(self): ...\n```\n\n- Una clase con métodos abstractos **no se puede instanciar**: `Forma()` da `TypeError`.\n- Una subclase solo se puede instanciar si **implementa todos** los métodos abstractos, con el mismo nombre. Si se le olvida uno (o lo escribe mal), crear el objeto da `TypeError`.\n- La clase abstracta puede tener también métodos normales que usen los abstractos.\n\nEs lo que en Java se consigue con `abstract` e `interface`: un **contrato** que dice qué deben saber hacer los objetos, y el error aparece al crearlos y no a mitad del programa.",
            "examples": [
                {
                    "code": 'from abc import ABC, abstractmethod\n\n\nclass Forma(ABC):\n    @abstractmethod\n    def area(self):\n        ...\n\n    def informe(self):                       # método normal que usa el abstracto\n        return f"{type(self).__name__}: {self.area():.1f}"\n\n\nclass Cuadrado(Forma):\n    def __init__(self, lado):\n        self.lado = lado\n\n    def area(self):\n        return self.lado**2\n\n\nprint(Cuadrado(3).informe())\ntry:\n    Forma()\nexcept TypeError:\n    print("Forma es abstracta: no se puede instanciar")',
                    "lines": [
                        [4, "Heredar de `ABC` la convierte en clase abstracta."],
                        [5, "`@abstractmethod`: las subclases deben implementarlo."],
                        [9, "Un método normal puede apoyarse en el abstracto."],
                        [17, "`Cuadrado` cumple el contrato, así que se puede crear."],
                        [23, "La clase abstracta no se puede instanciar."],
                    ],
                }
            ],
            "quiz": ["poo6-07", "poo6-08", "poo6-09"],
        },
    ],
    "guided": ["poo6-10"],
    "autonomous": ["poo6-11", "poo6-12"],
    "selfcheck": ["poo6-13", "poo6-14"],
    "recap": [
        "Polimorfismo: el mismo mensaje (`objeto.metodo()`) se comporta distinto según la clase del objeto.",
        "Recorre colecciones llamando al mismo método en vez de preguntar el tipo con `if`.",
        "Duck typing: en Python basta con que el objeto tenga el método; no hace falta una superclase común.",
        "`ABC` y `@abstractmethod` definen un contrato: la clase abstracta no se instancia y las subclases deben implementarlo todo.",
        "Un método de la superclase que llama a `self.metodo()` usa la versión de la subclase.",
    ],
    "pass": {
        "minScore": 0.7,
        "required": ["poo6-10", "poo6-11"],
        "text": [
            "Resolver el ejercicio guiado (notificaciones) y el autónomo de nóminas con todos los tests superados.",
            "Dominar la unidad según el motor: al menos un 70 % de aciertos recientes en sus ejercicios, con varios tipos distintos.",
            "Completar las lecciones ayuda a organizarte, pero **no** demuestra la competencia: la demuestran los ejercicios.",
        ],
    },
    "curriculum": [
        proposed(
            "0485-RA7-i",
            "Se identifican escenarios de uso de interfaces (clases abstractas con `abc`).",
        ),
        proposed(
            "0485-RA7-g",
            "Se escriben programas que usan jerarquías de clases de forma polimórfica.",
        ),
        proposed(
            "0485-RA7-f",
            "Se prueban y depuran jerarquías de clases (métodos abstractos sin implementar).",
        ),
    ],
}

EXERCISES = [
    # ---------- Lección «Mismo método, distinto comportamiento»
    output(
        "poo6-01",
        CID,
        """
        class Forma:
            def lados(self):
                return 0

        class Triangulo(Forma):
            def lados(self):
                return 3

        class Cuadrado(Forma):
            def lados(self):
                return 4

        print(sum(f.lados() for f in [Triangulo(), Cuadrado(), Forma()]))
        """,
        "7",
        "Cada objeto responde con su propia versión de `lados()`: 3 + 4 + 0 = 7. El código que suma no necesita saber de qué clase es cada uno.",
        traps={"0": f"{CID}.version-base", "8": None},
        level=1,
        daw=False,
    ),
    choice(
        "poo6-02",
        CID,
        "¿Qué es el polimorfismo?",
        [
            (
                "Que el mismo método se comporte de forma distinta según la clase del objeto que lo recibe",
                None,
            ),
            ("Que una clase tenga varios constructores `__init__`", None),
            ("Que una clase herede de varias a la vez", None),
            (
                "Comprobar con `isinstance` el tipo de cada objeto antes de usarlo",
                f"{CID}.isinstance-en-cadena",
            ),
        ],
        0,
        "Polimorfismo es enviar el mismo mensaje (`objeto.metodo()`) a objetos distintos y que cada uno responda a su manera. Preguntar el tipo con `isinstance` es justo lo que el polimorfismo evita.",
        level=1,
        daw=False,
    ),
    bug(
        "poo6-03",
        CID,
        "Debería mostrar `miau` y `guau`. ¿Qué línea falla?",
        """
        class Gato:
            def hablar(self):
                return "miau"

        class Perro:
            def hablar(self):
                return "guau"

        for animal in [Gato(), Perro()]:
            print(animal.hablar)
        """,
        10,
        "    print(animal.hablar())",
        "miau\nguau",
        f"{CID}.metodo-sin-llamar",
        "Sin paréntesis `animal.hablar` es el propio método (se imprime algo como `<bound method …>`), no lo que devuelve. Para ejecutarlo hay que llamarlo: `animal.hablar()`.",
        level=1,
        daw=False,
    ),
    # ---------- Lección «Duck typing»
    output(
        "poo6-04",
        CID,
        """
        class Libro:
            def resumen(self):
                return "libro"

        class Cancion:
            def resumen(self):
                return "canción"

        def mostrar(cosa):
            return cosa.resumen()

        print(mostrar(Libro()), mostrar(Cancion()))
        """,
        "libro canción",
        "`Libro` y `Cancion` no comparten superclase (salvo `object`), pero las dos tienen `resumen()`. A `mostrar` solo le importa eso: es *duck typing*.",
        traps={"libro libro": None},
        level=1,
        daw=False,
    ),
    choice(
        "poo6-05",
        CID,
        "¿Qué necesita un objeto para poder pasarlo a `def imprimir(x): print(x.texto())`?",
        [
            ("Tener un método `texto()`", None),
            ("Heredar de una clase común con las demás", f"{CID}.necesita-herencia"),
            ("Ser una instancia de `str`", None),
            ("Estar declarado con un tipo en la función", f"{CID}.necesita-herencia"),
        ],
        0,
        "En Python no se comprueba la clase: si el objeto tiene `texto()`, funciona. Si no lo tiene, saltará `AttributeError` al llamarlo.",
        level=1,
        daw=False,
    ),
    output(
        "poo6-06",
        CID,
        """
        class Coche:
            def arrancar(self):
                return "brum"

        class Bici:
            pass

        for v in [Coche(), Bici()]:
            try:
                print(v.arrancar())
            except AttributeError:
                print("no sabe arrancar")
        """,
        "brum\nno sabe arrancar",
        "`Bici` no tiene `arrancar`, así que llamarlo da `AttributeError`, que aquí se captura. Con *duck typing* el error aparece al usar el método que falta.",
        traps={"brum\nNone": None, "brum": f"{CID}.necesita-herencia"},
        level=2,
        daw=False,
    ),
    # ---------- Lección «Clases abstractas e interfaces»
    output(
        "poo6-07",
        CID,
        """
        from abc import ABC, abstractmethod

        class Forma(ABC):
            @abstractmethod
            def area(self):
                ...

        try:
            Forma()
            print("creada")
        except TypeError:
            print("no se puede instanciar")
        """,
        "no se puede instanciar",
        "Una clase con métodos abstractos no se puede instanciar: `Forma()` lanza `TypeError`. Solo sirve como modelo para sus subclases.",
        traps={"creada": f"{CID}.abstracta-instanciable"},
        level=1,
        daw=False,
    ),
    bug(
        "poo6-08",
        CID,
        "Debería mostrar `Cobrados 20 € en efectivo`. ¿Qué línea falla?",
        """
        from abc import ABC, abstractmethod

        class Pago(ABC):
            @abstractmethod
            def cobrar(self, importe):
                ...

        class Efectivo(Pago):
            def cobra(self, importe):
                return f"Cobrados {importe} € en efectivo"

        print(Efectivo().cobrar(20))
        """,
        9,
        "    def cobrar(self, importe):",
        "Cobrados 20 € en efectivo",
        f"{CID}.abstracta-sin-implementar",
        "El método se llama `cobra` y no `cobrar`, así que `Efectivo` no implementa el método abstracto y `Efectivo()` da `TypeError`. Es la ventaja de las clases abstractas: el error aparece al crear el objeto.",
        level=2,
        daw=False,
    ),
    fill(
        "poo6-09",
        CID,
        "Completa el decorador para que toda forma esté obligada a tener `perimetro()`.",
        """
        from abc import ABC, abstractmethod

        class Forma(ABC):
            @___
            def perimetro(self):
                ...

        class Cuadrado(Forma):
            def __init__(self, lado):
                self.lado = lado

            def perimetro(self):
                return 4 * self.lado

        print(Cuadrado(5).perimetro())
        """,
        ["abstractmethod"],
        "`@abstractmethod` marca el método como obligatorio: `Forma` no se podrá instanciar y sus subclases tendrán que implementarlo.",
        expect="20",
        traps={"staticmethod": None, "abstract": f"{CID}.abstracta-instanciable", "ABC": None},
        level=2,
        daw=False,
    ),
    # ---------- Ejercicio guiado
    code(
        "poo6-10",
        CID,
        '**Ejercicio guiado: notificaciones.** La clase abstracta `Notificacion` ya está. Sigue los pasos:\n\n1. Crea `Email(Notificacion)` con `enviar(mensaje)`, que devuelva `"Email a ana@ies.es: Hola"`.\n2. Crea `SMS(Notificacion)` con `enviar(mensaje)`, que devuelva `"SMS a 600111222: …"` con solo los **20 primeros** caracteres del mensaje.\n3. Escribe la función `enviar_todas(notificaciones, mensaje)`, que devuelva una lista con lo que devuelve cada `enviar`. **Sin** `if` ni `isinstance`: debe funcionar con cualquier objeto que tenga `enviar`.',
        """
        from abc import ABC, abstractmethod


        class Notificacion(ABC):
            def __init__(self, destinatario):
                self.destinatario = destinatario

            @abstractmethod
            def enviar(self, mensaje):
                ...


        # Paso 1: Email

        # Paso 2: SMS

        # Paso 3: enviar_todas(notificaciones, mensaje)


        avisos = [Email("ana@ies.es"), SMS("600111222")]
        for texto in enviar_todas(avisos, "Mañana no hay clase de Programación"):
            print(texto)
        """,
        """
        from abc import ABC, abstractmethod


        class Notificacion(ABC):
            def __init__(self, destinatario):
                self.destinatario = destinatario

            @abstractmethod
            def enviar(self, mensaje):
                ...


        class Email(Notificacion):
            def enviar(self, mensaje):
                return f"Email a {self.destinatario}: {mensaje}"


        class SMS(Notificacion):
            def enviar(self, mensaje):
                return f"SMS a {self.destinatario}: {mensaje[:20]}"


        def enviar_todas(notificaciones, mensaje):
            return [n.enviar(mensaje) for n in notificaciones]


        avisos = [Email("ana@ies.es"), SMS("600111222")]
        for texto in enviar_todas(avisos, "Mañana no hay clase de Programación"):
            print(texto)
        """,
        [
            case(
                'assert Email("ana@ies.es").enviar("Hola") == "Email a ana@ies.es: Hola", "Email.enviar() debe devolver \'Email a <destinatario>: <mensaje>\'"\nassert isinstance(Email("x"), Notificacion), "Email debe heredar de Notificacion"\ntry:\n    Notificacion("x")\nexcept TypeError:\n    pass\nelse:\n    raise AssertionError("No cambies Notificacion: debe seguir siendo abstracta")',
            ),
            case(
                's = SMS("600111222")\nassert isinstance(s, Notificacion), "SMS debe heredar de Notificacion"\nassert s.enviar("0123456789ABCDEFGHIJKLMN") == "SMS a 600111222: 0123456789ABCDEFGHIJ", "SMS.enviar() solo debe incluir los 20 primeros caracteres"',
                error=f"{CID}.abstracta-sin-implementar",
            ),
            case(
                'class Paloma:\n    def enviar(self, mensaje):\n        return "paloma: " + mensaje\n\nres = enviar_todas([Email("a@b.es"), Paloma(), SMS("1")], "Hola")\nassert res == ["Email a a@b.es: Hola", "paloma: Hola", "SMS a 1: Hola"], f"enviar_todas() debe llamar a enviar() de cada objeto, sea de la clase que sea; devuelve {res!r}"',
                error=f"{CID}.isinstance-en-cadena",
            ),
        ],
        "Cada tipo de notificación sabe enviarse a su manera y `enviar_todas` solo envía el mismo mensaje a todas. Para añadir un tipo nuevo (WhatsApp, push) basta con crear su clase: la función no cambia.",
        "`enviar_todas` cabe en una línea: `return [n.enviar(mensaje) for n in notificaciones]`. En `SMS`, recorta con `mensaje[:20]`.",
        wrong=[
            (
                """
                from abc import ABC, abstractmethod


                class Notificacion(ABC):
                    def __init__(self, destinatario):
                        self.destinatario = destinatario

                    @abstractmethod
                    def enviar(self, mensaje):
                        ...


                class Email(Notificacion):
                    def enviar(self, mensaje):
                        return f"Email a {self.destinatario}: {mensaje}"


                class SMS(Notificacion):
                    def enviar(self, mensaje):
                        return f"SMS a {self.destinatario}: {mensaje[:20]}"


                def enviar_todas(notificaciones, mensaje):
                    resultado = []
                    for n in notificaciones:
                        if isinstance(n, Email):
                            resultado.append(f"Email a {n.destinatario}: {mensaje}")
                        elif isinstance(n, SMS):
                            resultado.append(f"SMS a {n.destinatario}: {mensaje[:20]}")
                    return resultado
                """,
                3,
            ),
        ],
        level=2,
        daw=False,
    ),
    # ---------- Ejercicios autónomos
    code(
        "poo6-11",
        CID,
        "**Ejercicio autónomo: nóminas.** Crea:\n\n- La clase abstracta `Empleado(ABC)` con `__init__(self, nombre)` y el método abstracto `salario()`.\n- `Fijo(nombre, sueldo)`: su salario es el sueldo.\n- `PorHoras(nombre, horas, precio_hora)`: horas por precio.\n- `Becario(nombre)`: siempre 300.\n- La función `total_nominas(empleados)`, que devuelva la suma de los salarios de una lista de empleados de cualquier tipo, también de tipos que se creen más adelante.",
        """
        from abc import ABC, abstractmethod
        """,
        """
        from abc import ABC, abstractmethod


        class Empleado(ABC):
            def __init__(self, nombre):
                self.nombre = nombre

            @abstractmethod
            def salario(self):
                ...


        class Fijo(Empleado):
            def __init__(self, nombre, sueldo):
                super().__init__(nombre)
                self.sueldo = sueldo

            def salario(self):
                return self.sueldo


        class PorHoras(Empleado):
            def __init__(self, nombre, horas, precio_hora):
                super().__init__(nombre)
                self.horas = horas
                self.precio_hora = precio_hora

            def salario(self):
                return self.horas * self.precio_hora


        class Becario(Empleado):
            def salario(self):
                return 300


        def total_nominas(empleados):
            return sum(e.salario() for e in empleados)


        plantilla = [Fijo("Ana", 1500), PorHoras("Leo", 80, 12), Becario("Eva")]
        print(total_nominas(plantilla))
        """,
        [
            case(
                'assert Fijo("A", 1500).salario() == 1500, "El salario de Fijo es su sueldo"\nassert PorHoras("B", 10, 12).salario() == 120, "El salario por horas es horas * precio_hora"\nassert Becario("C").salario() == 300 and Becario("C").nombre == "C", "Becario cobra 300 y guarda su nombre"',
            ),
            case(
                'try:\n    Empleado("x")\nexcept TypeError:\n    pass\nelse:\n    raise AssertionError("Empleado debe ser abstracta: hereda de ABC y marca salario() con @abstractmethod")\nassert all(isinstance(e, Empleado) for e in (Fijo("A", 1), PorHoras("B", 1, 1), Becario("C"))), "Las tres clases deben heredar de Empleado"',
                error=f"{CID}.abstracta-instanciable",
            ),
            case(
                'class Autonomo(Empleado):\n    def salario(self):\n        return 1000\n\ntotal = total_nominas([Fijo("A", 1500), Becario("B"), Autonomo("C")])\nassert total == 2800, f"total_nominas() debe sumar salario() de cualquier empleado, también de clases nuevas; devuelve {total!r}"\nassert total_nominas([]) == 0, "Sin empleados el total es 0"',
                error=f"{CID}.isinstance-en-cadena",
            ),
        ],
        "La clase abstracta asegura que todo empleado tiene `salario()`; `total_nominas` solo envía ese mensaje. Por eso una clase nueva como `Autonomo` funciona sin tocar la función.",
        "`total_nominas` puede ser `return sum(e.salario() for e in empleados)`. `Becario` no necesita `__init__`: hereda el de `Empleado`.",
        wrong=[
            (
                """
                from abc import ABC, abstractmethod


                class Empleado(ABC):
                    def __init__(self, nombre):
                        self.nombre = nombre

                    @abstractmethod
                    def salario(self):
                        ...


                class Fijo(Empleado):
                    def __init__(self, nombre, sueldo):
                        super().__init__(nombre)
                        self.sueldo = sueldo

                    def salario(self):
                        return self.sueldo


                class PorHoras(Empleado):
                    def __init__(self, nombre, horas, precio_hora):
                        super().__init__(nombre)
                        self.horas = horas
                        self.precio_hora = precio_hora

                    def salario(self):
                        return self.horas * self.precio_hora


                class Becario(Empleado):
                    def salario(self):
                        return 300


                def total_nominas(empleados):
                    total = 0
                    for e in empleados:
                        if isinstance(e, Fijo):
                            total += e.sueldo
                        elif isinstance(e, PorHoras):
                            total += e.horas * e.precio_hora
                        elif isinstance(e, Becario):
                            total += 300
                    return total
                """,
                3,
            ),
        ],
        level=2,
        daw=False,
    ),
    code(
        "poo6-12",
        CID,
        '**Ejercicio autónomo: exportar un catálogo.** Crea:\n\n- `Libro(titulo, autor)` con `a_texto()`, que devuelva `"Libro: Rayuela, de Julio Cortázar"`.\n- `Pelicula(titulo, minutos)` con `a_texto()`, que devuelva `"Película: Coco (105 min)"`.\n- La función `exportar(elementos)`, que devuelva la lista de textos de los elementos que **tengan** el método `a_texto` y se salte los demás (números, textos sueltos…) sin dar error.',
        """
        class Libro:
            ...
        """,
        """
        class Libro:
            def __init__(self, titulo, autor):
                self.titulo = titulo
                self.autor = autor

            def a_texto(self):
                return f"Libro: {self.titulo}, de {self.autor}"


        class Pelicula:
            def __init__(self, titulo, minutos):
                self.titulo = titulo
                self.minutos = minutos

            def a_texto(self):
                return f"Película: {self.titulo} ({self.minutos} min)"


        def exportar(elementos):
            return [e.a_texto() for e in elementos if hasattr(e, "a_texto")]


        catalogo = [Libro("Rayuela", "Julio Cortázar"), Pelicula("Coco", 105), 42]
        for linea in exportar(catalogo):
            print(linea)
        """,
        [
            case(
                'assert Libro("Rayuela", "Julio Cortázar").a_texto() == "Libro: Rayuela, de Julio Cortázar", "Formato del libro: \'Libro: <título>, de <autor>\'"\nassert Pelicula("Coco", 105).a_texto() == "Película: Coco (105 min)", "Formato de la película: \'Película: <título> (<minutos> min)\'"',
            ),
            case(
                'res = exportar([Pelicula("A", 90), Libro("B", "C")])\nassert res == ["Película: A (90 min)", "Libro: B, de C"], f"exportar() debe devolver los textos en el mismo orden; devuelve {res!r}"',
            ),
            case(
                'class Disco:\n    def a_texto(self):\n        return "Disco"\n\nres = exportar([42, Libro("B", "C"), "hola", Disco(), None])\nassert res == ["Libro: B, de C", "Disco"], f"exportar() debe saltarse lo que no tiene a_texto() y aceptar cualquier objeto que lo tenga; devuelve {res!r}"',
                error=f"{CID}.necesita-herencia",
            ),
        ],
        "Es *duck typing*: `exportar` no mira la clase, sino si el objeto sabe convertirse a texto. Por eso acepta también un `Disco` que nadie había previsto.",
        'Filtra con `hasattr(e, "a_texto")` dentro de una comprensión de listas o un bucle.',
        wrong=[
            (
                """
                class Libro:
                    def __init__(self, titulo, autor):
                        self.titulo = titulo
                        self.autor = autor

                    def a_texto(self):
                        return f"Libro: {self.titulo}, de {self.autor}"


                class Pelicula:
                    def __init__(self, titulo, minutos):
                        self.titulo = titulo
                        self.minutos = minutos

                    def a_texto(self):
                        return f"Película: {self.titulo} ({self.minutos} min)"


                def exportar(elementos):
                    return [e.a_texto() for e in elementos]
                """,
                3,
            ),
        ],
        level=2,
        daw=False,
    ),
    # ---------- Autoevaluación
    choice(
        "poo6-13",
        CID,
        "Una función tiene diez `elif isinstance(figura, …)` para calcular el área de cada tipo de figura. ¿Cuál es la mejora orientada a objetos?",
        [
            ("Dar a cada clase su propio método `area()` y llamar a `figura.area()`", None),
            (
                "Añadir un `elif` más cada vez que aparezca una figura nueva",
                f"{CID}.isinstance-en-cadena",
            ),
            (
                "Guardar el tipo de figura en un texto y comparar con `==`",
                f"{CID}.isinstance-en-cadena",
            ),
            ("Juntar todas las figuras en una sola clase con un atributo `tipo`", None),
        ],
        0,
        "Con polimorfismo cada clase sabe calcular su área y la función solo llama a `area()`. Una figura nueva no obliga a tocar la función.",
        level=2,
        daw=False,
    ),
    output(
        "poo6-14",
        CID,
        """
        class Informe:
            def generar(self):
                return "[" + self.cuerpo() + "]"

            def cuerpo(self):
                return "vacío"

        class Ventas(Informe):
            def cuerpo(self):
                return "ventas: 3"

        print(Ventas().generar())
        """,
        "[ventas: 3]",
        "`generar` se hereda de `Informe`, pero llama a `self.cuerpo()` y `self` es un objeto `Ventas`: se usa la versión de la subclase.",
        traps={"[vacío]": f"{CID}.version-base"},
        level=2,
        daw=False,
    ),
]

# Errores típicos (slug, etiqueta, por qué, qué pensar, cómo evitarlo)
ERRORS = [
    (
        "isinstance-en-cadena",
        "Pregunta el tipo con `if isinstance` en vez de usar métodos polimórficos",
        "Una cadena de `if` por cada clase hay que tocarla cada vez que aparece una clase nueva, y repite lo que cada clase ya debería saber hacer.",
        "¿Podría cada clase tener su propio método con el mismo nombre?",
        "Pon el comportamiento en un método de cada clase y llama a `objeto.metodo()`.",
    ),
    (
        "necesita-herencia",
        "Cree que solo funcionan juntos los objetos que heredan de la misma clase",
        "En Python basta con que el objeto tenga el método (*duck typing*). La herencia es útil, pero no es obligatoria para el polimorfismo.",
        "¿Qué método uso de este objeto? ¿Lo tiene?",
        "Piensa en lo que sabe hacer el objeto, no en su clase; usa `hasattr` si puede faltar.",
    ),
    (
        "abstracta-instanciable",
        "Cree que se puede crear un objeto de una clase abstracta",
        "Una clase que hereda de `ABC` y tiene métodos `@abstractmethod` sin implementar no se puede instanciar: da `TypeError`.",
        "¿Esta clase tiene métodos abstractos pendientes?",
        "Crea objetos de las subclases concretas, que implementan todos los métodos abstractos.",
    ),
    (
        "abstracta-sin-implementar",
        "Deja sin implementar (o con otro nombre) un método abstracto",
        "Si la subclase no implementa todos los métodos abstractos con el mismo nombre, sigue siendo abstracta y no se puede instanciar.",
        "¿He escrito todos los métodos del contrato, con el nombre exacto?",
        "Copia la firma del método abstracto (`def cobrar(self, importe):`) en cada subclase.",
    ),
    (
        "version-base",
        "Cree que se ejecuta la versión de la superclase",
        "Python usa el método de la clase del objeto, aunque la llamada esté escrita en un método heredado (`self.cuerpo()`).",
        "¿De qué clase es `self` en este momento?",
        "Sigue la llamada desde el objeto real, no desde la clase donde está escrito el código.",
    ),
    (
        "metodo-sin-llamar",
        "Usa el método sin paréntesis",
        "`objeto.metodo` es el método en sí; para ejecutarlo y obtener su resultado hay que escribir `objeto.metodo()`.",
        "¿Quiero el método o lo que devuelve?",
        "Pon siempre los paréntesis al llamar a un método.",
    ),
]
