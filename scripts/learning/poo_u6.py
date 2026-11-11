# ruff: noqa: E501
"""Unidad 6 del módulo de POO: polimorfismo.

Concepto `poo-polimorfismo` (área `poo`): el mismo mensaje con comportamientos distintos, *duck
typing*, clases abstractas con `abc` (el equivalente a las interfaces) y código que no pregunta por el
tipo. La salida de los ejemplos la obtiene build_learning.py ejecutándolos.
"""

from exercises import bug, case, choice, code, fill, output
from poo_common import practice, proposed, ref

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
            "theory": "A veces quieres **obligar** a que todas las subclases tengan ciertos métodos. Para eso están las **clases abstractas** del módulo `abc`:\n\n```\nfrom abc import ABC, abstractmethod\n\nclass Forma(ABC):\n    @abstractmethod\n    def area(self): ...\n```\n\n- Una clase con métodos abstractos **no se puede instanciar**: `Forma()` da `TypeError`.\n- Una subclase solo se puede instanciar si **implementa todos** los métodos abstractos, con el mismo nombre. Si se le olvida uno (o lo escribe mal), crear el objeto da `TypeError`.\n- La clase abstracta puede tener también métodos normales que usen los abstractos.\n\nEs lo que en Java se consigue con `abstract` e `interface`: un **contrato** que dice qué deben saber hacer los objetos, y el error aparece al crearlos y no a mitad del programa.\n\n**¿Clase abstracta o duck typing?**\n\n| | Duck typing | Clase abstracta (`ABC`) |\n|---|---|---|\n| Qué pide | Que el objeto tenga el método | Heredar de la clase e implementar todos sus métodos abstractos |\n| Cuándo se nota un olvido | Al llamar al método (`AttributeError`) | Al crear el objeto (`TypeError`) |\n| Encaja con | Clases que no controlas o que no tienen nada en común | Una familia de clases tuyas que deben cumplir el mismo contrato |\n| Coste | Ninguno | Escribir la clase base y heredar de ella |\n\nLas dos formas son polimorfismo: el código que usa los objetos no pregunta su tipo, solo llama al método.",
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
    "autonomous": ["poo6-15"],
    "extras": ["poo6-11", "poo6-12"],
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
        "required": ["poo6-10", "poo6-15"],
        "text": [
            "Resolver el ejercicio guiado (notificaciones) y el ejercicio principal de notificaciones con validación con todos los tests superados.",
            "Dominar la unidad según el motor: al menos un 70 % de aciertos recientes en sus ejercicios, con varios tipos distintos.",
            "Completar las lecciones ayuda a organizarte, pero **no** demuestra la competencia: la demuestran los ejercicios.",
        ],
    },
    "practices": [
        practice(
            "Llama al método y deja que cada objeto responda a su manera, en vez de preguntar su tipo con `isinstance`.",
            "Así, añadir una clase nueva no obliga a cambiar el código que usa los objetos.",
        ),
        practice(
            "Da al método el mismo nombre y los mismos parámetros en todas las clases.",
            "Si cambia en alguna, el código común deja de funcionar con ella.",
        ),
        practice(
            "Usa una clase abstracta (`ABC` y `@abstractmethod`) cuando una familia de clases tuyas deba cumplir el mismo contrato.",
            "El olvido de un método se detecta al crear el objeto y no a mitad del programa.",
        ),
        practice(
            "Si usas duck typing, explica en la documentación de la función qué métodos necesita.",
            "Quien la use sabrá qué debe tener su objeto sin leer todo el código.",
        ),
        practice(
            "Pon en la clase base los métodos comunes que usan los abstractos.",
            "Cada subclase los hereda y solo escribe lo que la hace distinta.",
        ),
    ],
    "references": [
        ref(
            "py-abc",
            "abc.ABC y el decorador abc.abstractmethod",
            [
                "clases de base abstracta",
                "una clase con métodos abstractos sin implementar no se puede instanciar",
            ],
        ),
        ref(
            "py-faq-programming",
            "Objetos: ¿Cómo puedo comprobar si un objeto es una instancia de una clase dada o de una subclase de ella?",
            ["`isinstance()` y la alternativa de llamar a un método común"],
        ),
    ],
    "bank": [
        "poo6-02",
        "poo6-05",
        "poo6-13",
        "poo6-16",
        "poo6-17",
        "poo6-18",
        "poo6-19",
        "poo6-20",
        "poo6-21",
        "poo6-22",
        "poo6-23",
        "poo6-24",
        "poo6-25",
        "poo6-26",
        "poo6-27",
    ],
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
    # ---------- Ejercicio principal de la unidad
    code(
        "poo6-15",
        CID,
        '**Ejercicio principal: `Notificacion`, `NotificacionEmail` y `NotificacionSMS`.** Crea:\n\n- La clase abstracta `Notificacion(ABC)` con `__init__(self, destinatario)`, que guarda el destinatario y una lista `historial` vacía; el método **abstracto** `enviar(mensaje)`, y el método normal `registrar(mensaje)`, que llama a `self.enviar(mensaje)`, guarda el texto en el historial y lo devuelve.\n- `NotificacionEmail`: el destinatario debe contener `@` (si no, `ValueError`). `enviar` devuelve `"Email a ana@ies.es: Hola"`.\n- `NotificacionSMS`: el destinatario debe tener 9 cifras (si no, `ValueError`). `enviar` devuelve `"SMS a 600111222: …"` con como mucho 160 caracteres del mensaje.\n- La función `notificar(notificaciones, mensaje)`: registra el mensaje en todas y devuelve la lista de textos. **No** preguntes el tipo de cada notificación: tiene que funcionar también con clases que se creen más adelante.',
        """
        from abc import ABC, abstractmethod


        class Notificacion(ABC):
            ...
        """,
        """
        from abc import ABC, abstractmethod


        class Notificacion(ABC):
            def __init__(self, destinatario):
                self.destinatario = destinatario
                self.historial = []

            @abstractmethod
            def enviar(self, mensaje):
                ...

            def registrar(self, mensaje):
                texto = self.enviar(mensaje)
                self.historial.append(texto)
                return texto


        class NotificacionEmail(Notificacion):
            def __init__(self, destinatario):
                if "@" not in destinatario:
                    raise ValueError(f"Correo no válido: {destinatario}")
                super().__init__(destinatario)

            def enviar(self, mensaje):
                return f"Email a {self.destinatario}: {mensaje}"


        class NotificacionSMS(Notificacion):
            def __init__(self, destinatario):
                if not (len(destinatario) == 9 and destinatario.isdigit()):
                    raise ValueError(f"Teléfono no válido: {destinatario}")
                super().__init__(destinatario)

            def enviar(self, mensaje):
                return f"SMS a {self.destinatario}: {mensaje[:160]}"


        def notificar(notificaciones, mensaje):
            return [n.registrar(mensaje) for n in notificaciones]


        avisos = [NotificacionEmail("ana@ies.es"), NotificacionSMS("600111222")]
        for texto in notificar(avisos, "Mañana no hay clase"):
            print(texto)
        """,
        [
            case(
                'try:\n    Notificacion("x")\nexcept TypeError:\n    pass\nelse:\n    raise AssertionError("Notificacion debe ser abstracta: hereda de ABC y marca enviar con @abstractmethod")',
                error=f"{CID}.abstracta-instanciable",
            ),
            case(
                'e = NotificacionEmail("ana@ies.es")\nassert e.enviar("Hola") == "Email a ana@ies.es: Hola", f"Texto del email incorrecto: {e.enviar(\'Hola\')!r}"\ns = NotificacionSMS("600111222")\nassert s.enviar("x" * 200) == "SMS a 600111222: " + "x" * 160, "El SMS lleva como mucho 160 caracteres del mensaje"\nassert e.destinatario == "ana@ies.es" and e.historial == [], "Las subclases deben llamar a super().__init__(destinatario)"',
            ),
            case(
                'for clase, malo in ((NotificacionEmail, "ana.ies.es"), (NotificacionSMS, "600-111")):\n    try:\n        clase(malo)\n    except ValueError:\n        pass\n    else:\n        raise AssertionError(f"{clase.__name__}({malo!r}) debe lanzar ValueError")',
            ),
            case(
                'a = NotificacionEmail("ana@ies.es")\nb = NotificacionEmail("luis@ies.es")\nassert a.registrar("Uno") == "Email a ana@ies.es: Uno", "registrar devuelve el texto enviado"\na.registrar("Dos")\nassert a.historial == ["Email a ana@ies.es: Uno", "Email a ana@ies.es: Dos"], "registrar guarda cada texto en el historial"\nassert b.historial == [], "Cada notificación tiene su propio historial"',
            ),
            case(
                'class NotificacionPush(Notificacion):\n    def enviar(self, mensaje):\n        return f"Push a {self.destinatario}: {mensaje}"\n\navisos = [NotificacionPush("app-ana"), NotificacionSMS("600111222")]\nassert notificar(avisos, "Hola") == ["Push a app-ana: Hola", "SMS a 600111222: Hola"], "notificar debe funcionar con cualquier subclase, también con las que no conoce"\nassert avisos[0].historial == ["Push a app-ana: Hola"], "notificar usa registrar, que guarda el historial"',
                error=f"{CID}.isinstance-en-cadena",
            ),
        ],
        "La clase abstracta fija el contrato (`enviar`) y aporta lo común (`registrar` y el historial). Cada subclase valida su destinatario y envía a su manera. `notificar` solo llama a `registrar`, así que funciona con `NotificacionPush`, que no existía al escribirla: eso es el polimorfismo.",
        "Hereda de `ABC` y pon `@abstractmethod` encima de `enviar`. En cada subclase valida primero y después llama a `super().__init__(destinatario)`. En `notificar`, basta con `[n.registrar(mensaje) for n in notificaciones]`.",
        wrong=[
            (
                """
                class Notificacion:
                    def __init__(self, destinatario):
                        self.destinatario = destinatario
                        self.historial = []

                    def enviar(self, mensaje):
                        raise NotImplementedError

                    def registrar(self, mensaje):
                        texto = self.enviar(mensaje)
                        self.historial.append(texto)
                        return texto
                """,
                1,
            ),
            (
                """
                from abc import ABC, abstractmethod


                class Notificacion(ABC):
                    def __init__(self, destinatario):
                        self.destinatario = destinatario
                        self.historial = []

                    @abstractmethod
                    def enviar(self, mensaje):
                        ...

                    def registrar(self, mensaje):
                        texto = self.enviar(mensaje)
                        self.historial.append(texto)
                        return texto


                class NotificacionEmail(Notificacion):
                    def __init__(self, destinatario):
                        if "@" not in destinatario:
                            raise ValueError(destinatario)
                        super().__init__(destinatario)

                    def enviar(self, mensaje):
                        return f"Email a {self.destinatario}: {mensaje}"


                class NotificacionSMS(Notificacion):
                    def __init__(self, destinatario):
                        if not (len(destinatario) == 9 and destinatario.isdigit()):
                            raise ValueError(destinatario)
                        super().__init__(destinatario)

                    def enviar(self, mensaje):
                        return f"SMS a {self.destinatario}: {mensaje[:160]}"


                def notificar(notificaciones, mensaje):
                    textos = []
                    for n in notificaciones:
                        if isinstance(n, NotificacionEmail):
                            textos.append(n.registrar(mensaje))
                        elif isinstance(n, NotificacionSMS):
                            textos.append(n.registrar(mensaje))
                    return textos
                """,
                5,
            ),
        ],
        level=2,
        daw=False,
    ),
    # ---------- Banco de preguntas de la unidad (cuestionario)
    choice(
        "poo6-16",
        CID,
        "¿Qué es el *duck typing*?",
        [
            ("Usar un objeto por los métodos que tiene, sin comprobar de qué clase es", None),
            (
                "Comprobar con `isinstance` el tipo de cada objeto antes de usarlo",
                f"{CID}.isinstance-en-cadena",
                "Es lo contrario: con duck typing no se pregunta el tipo, se llama al método.",
            ),
            (
                "Obligar a que todas las clases hereden de una clase abstracta común",
                f"{CID}.necesita-herencia",
                "Eso es usar una clase abstracta. El duck typing no exige ninguna herencia.",
            ),
            (
                "Convertir un objeto en otro tipo con `str()` o `int()`",
                None,
                "Eso es convertir valores, no una forma de polimorfismo.",
            ),
        ],
        0,
        "«Si camina como un pato y hace cuac, es un pato»: a Python le basta con que el objeto tenga el método que se llama.",
        level=1,
        daw=False,
        bank=True,
        qtype="teoria",
    ),
    choice(
        "poo6-17",
        CID,
        "Una subclase de una clase abstracta olvida implementar un método abstracto. ¿Cuándo da error Python?",
        [
            ("Al crear un objeto de esa subclase: `TypeError`", None),
            (
                "Al escribir la clase: `SyntaxError`",
                None,
                "La clase está bien escrita; el contrato se comprueba al intentar crear objetos.",
            ),
            (
                "Al llamar al método que falta: `AttributeError`",
                f"{CID}.abstracta-sin-implementar",
                "Eso pasaría con duck typing. Con `ABC` el error llega antes, al crear el objeto.",
            ),
            (
                "Nunca: los métodos abstractos son solo un comentario",
                f"{CID}.abstracta-instanciable",
                "`@abstractmethod` sí tiene efecto: impide crear objetos hasta que se implementen todos.",
            ),
        ],
        0,
        "Es la ventaja de las clases abstractas: el olvido se descubre en cuanto se crea el objeto, no a mitad del programa.",
        level=2,
        daw=False,
        bank=True,
        qtype="teoria",
    ),
    choice(
        "poo6-18",
        CID,
        "Para que esta función funcione, ¿qué tiene que cumplir cada elemento de `figuras`?",
        [
            ("Tener un método `area()` que devuelva un número", None),
            (
                "Heredar de una clase `Figura`",
                f"{CID}.necesita-herencia",
                "La función no comprueba ninguna herencia: solo llama a `f.area()`.",
            ),
            (
                "Ser todos de la misma clase",
                None,
                "Pueden ser de clases distintas mientras todas tengan `area()`.",
            ),
            (
                "Haber pasado antes por `isinstance`",
                f"{CID}.isinstance-en-cadena",
                "No hace falta ninguna comprobación: si el objeto tiene `area()`, funciona.",
            ),
        ],
        0,
        "La función usa duck typing: le da igual la clase de cada figura, solo necesita que responda a `area()` con un número que se pueda sumar.",
        code="""
        def total(figuras):
            return sum(f.area() for f in figuras)
        """,
        level=2,
        daw=False,
        bank=True,
        qtype="codigo",
    ),
    choice(
        "poo6-19",
        CID,
        "En este código, ¿qué papel tiene el método `guardar` de `Exportador`?",
        [
            (
                "Es un método normal que usa el abstracto: cada subclase lo hereda y funciona con su propio `exportar`",
                None,
            ),
            (
                "Es abstracto también: cada subclase tiene que volver a escribirlo",
                f"{CID}.abstracta-sin-implementar",
                "No lleva `@abstractmethod`: las subclases lo heredan tal cual.",
            ),
            (
                "Impide crear objetos de `CSV`",
                f"{CID}.abstracta-instanciable",
                "`CSV` implementa `exportar`, que es el único método abstracto, así que se puede instanciar.",
            ),
            (
                "Solo funciona en `Exportador`, no en sus subclases",
                f"{CID}.version-base",
                "Al revés: en `Exportador` no se puede usar (es abstracta) y en `CSV` sí, con el `exportar` de `CSV`.",
            ),
        ],
        0,
        "Una clase abstracta puede tener métodos completos. `guardar` llama a `self.exportar`, así que cada subclase guarda en su formato sin reescribir `guardar`.",
        code="""
        from abc import ABC, abstractmethod

        class Exportador(ABC):
            @abstractmethod
            def exportar(self, datos):
                ...

            def guardar(self, datos):
                return f"Guardado: {self.exportar(datos)}"

        class CSV(Exportador):
            def exportar(self, datos):
                return ",".join(datos)
        """,
        level=3,
        daw=False,
        bank=True,
        qtype="codigo",
    ),
    choice(
        "poo6-20",
        CID,
        "¿Qué muestra este programa?",
        [
            ("Guau Bip", None),
            (
                "AttributeError",
                f"{CID}.necesita-herencia",
                "`Perro` y `Robot` no comparten superclase, pero los dos tienen `hablar()`: con eso basta.",
            ),
            (
                "Guau Guau",
                f"{CID}.version-base",
                "Cada objeto usa el `hablar` de su propia clase.",
            ),
            (
                "Bip Bip",
                None,
                "El primer objeto es un perro y responde con su propio método.",
            ),
        ],
        0,
        "Duck typing: el bucle llama a `hablar()` y cada objeto responde a su manera, aunque sus clases no tengan nada en común.",
        code="""
        class Perro:
            def hablar(self):
                return "Guau"

        class Robot:
            def hablar(self):
                return "Bip"

        for x in [Perro(), Robot()]:
            print(x.hablar(), end=" ")
        """,
        level=1,
        daw=False,
        bank=True,
        qtype="prediccion",
    ),
    choice(
        "poo6-21",
        CID,
        "¿Qué muestra este programa?",
        [
            ("abstracta 4", None),
            (
                "creada 4",
                f"{CID}.abstracta-instanciable",
                "`Forma` tiene un método abstracto, así que `Forma()` lanza `TypeError`.",
            ),
            (
                "abstracta TypeError",
                f"{CID}.abstracta-sin-implementar",
                "`Cuadrado` implementa `area`, así que sí se puede crear.",
            ),
            (
                "creada TypeError",
                None,
                "Es al revés: la clase abstracta es la que no se puede instanciar, y la subclase completa sí.",
            ),
        ],
        0,
        "La clase abstracta no se puede instanciar, pero su subclase implementa todos los métodos abstractos y funciona con normalidad.",
        code="""
        from abc import ABC, abstractmethod

        class Forma(ABC):
            @abstractmethod
            def area(self):
                ...

        class Cuadrado(Forma):
            def area(self):
                return 4

        try:
            Forma()
            resultado = "creada"
        except TypeError:
            resultado = "abstracta"
        print(resultado, Cuadrado().area())
        """,
        level=2,
        daw=False,
        bank=True,
        qtype="prediccion",
    ),
    choice(
        "poo6-22",
        CID,
        "¿Qué muestra este programa?",
        [
            ("Hola, base | Hola, Ana", None),
            (
                "Hola, base | Hola, base",
                f"{CID}.version-base",
                "`saludar` llama a `self.nombre()`, y para un objeto `Ana` se usa el `nombre` de `Ana`.",
            ),
            (
                "Hola, Ana | Hola, Ana",
                None,
                "El objeto `Base()` usa su propio `nombre`, que devuelve `base`.",
            ),
            (
                "AttributeError",
                None,
                "`Ana` hereda `saludar` de `Base` y las dos clases tienen `nombre`.",
            ),
        ],
        0,
        "Aunque `saludar` está escrito en `Base`, `self.nombre()` se busca en la clase del objeto. Así un método de la superclase usa las versiones de cada subclase.",
        code="""
        class Base:
            def saludar(self):
                return "Hola, " + self.nombre()

            def nombre(self):
                return "base"

        class Ana(Base):
            def nombre(self):
                return "Ana"

        print(Base().saludar(), "|", Ana().saludar())
        """,
        level=3,
        daw=False,
        bank=True,
        qtype="prediccion",
    ),
    choice(
        "poo6-23",
        CID,
        "Este programa termina con `TypeError: Can't instantiate abstract class Tarjeta…`. ¿Por qué?",
        [
            (
                "`Tarjeta` no implementa `cobrar`: su método se llama `cobro`, así que sigue siendo abstracta",
                None,
            ),
            (
                "Las subclases de una clase abstracta tampoco se pueden instanciar nunca",
                f"{CID}.abstracta-instanciable",
                "Se pueden instanciar cuando implementan todos los métodos abstractos con el mismo nombre.",
            ),
            (
                "Falta llamar a `super().__init__()` en `Tarjeta`",
                None,
                "Ninguna de las dos clases define `__init__`: no hay nada que llamar.",
            ),
            (
                "`@abstractmethod` solo funciona con métodos sin parámetros",
                None,
                "Funciona con cualquier método; el problema es el nombre distinto.",
            ),
        ],
        0,
        "El nombre tiene que coincidir: `cobro` es un método nuevo y `cobrar` sigue sin implementar.",
        code="""
        from abc import ABC, abstractmethod

        class Pago(ABC):
            @abstractmethod
            def cobrar(self, importe):
                ...

        class Tarjeta(Pago):
            def cobro(self, importe):
                return f"Cobrados {importe} €"

        t = Tarjeta()
        """,
        level=1,
        daw=False,
        bank=True,
        qtype="error",
    ),
    choice(
        "poo6-24",
        CID,
        "Debería mostrar `email` y `sms`, pero muestra `<bound method Email.enviar of …>` y algo parecido. ¿Por qué?",
        [
            ("Falta llamar al método: `canal.enviar()`, con paréntesis", None),
            (
                "Las dos clases deberían heredar de una clase común",
                f"{CID}.necesita-herencia",
                "No hace falta herencia: las dos tienen `enviar`. El fallo es que no se llama.",
            ),
            (
                "Hay que comprobar con `isinstance` qué tipo de canal es",
                f"{CID}.isinstance-en-cadena",
                "Preguntar el tipo no cambia nada: sin paréntesis el método sigue sin ejecutarse.",
            ),
            (
                "`enviar` debería usar `print` en vez de `return`",
                None,
                "Devolver el texto es correcto; lo que falta es ejecutar el método.",
            ),
        ],
        0,
        "`canal.enviar` es el método sin ejecutar, y `print` muestra su descripción. Con `canal.enviar()` cada objeto devuelve su texto.",
        code="""
        class Email:
            def enviar(self):
                return "email"

        class SMS:
            def enviar(self):
                return "sms"

        for canal in [Email(), SMS()]:
            print(canal.enviar)
        """,
        level=2,
        daw=False,
        bank=True,
        qtype="error",
    ),
    choice(
        "poo6-25",
        CID,
        "¿Qué versión de `area_total(figuras)` sigue funcionando sin cambios si mañana se añade la clase `Triangulo` con su `area()`?",
        [
            ("`return sum(f.area() for f in figuras)`", None),
            (
                "Un `if isinstance(f, Cuadrado)` y un `elif isinstance(f, Circulo)` con la fórmula de cada uno",
                f"{CID}.isinstance-en-cadena",
                "Habría que añadir otro `elif` para el triángulo: la función depende de cada clase.",
            ),
            (
                "`return sum(f.lado ** 2 for f in figuras)`",
                None,
                "Solo sirve para cuadrados: un triángulo no tiene `lado` ni esa fórmula.",
            ),
            (
                'Comparar `type(f).__name__` con `"Cuadrado"` y `"Circulo"`',
                f"{CID}.isinstance-en-cadena",
                "Es la misma cadena de comprobaciones, con texto en vez de `isinstance`.",
            ),
        ],
        0,
        "Si cada clase sabe calcular su área, la función solo tiene que pedírsela. Una clase nueva funciona sin tocar nada.",
        level=2,
        daw=False,
        bank=True,
        qtype="solucion",
    ),
    choice(
        "poo6-26",
        CID,
        "Toda subclase de `Exportador` debe tener obligatoriamente el método `exportar(datos)`. ¿Qué código lo garantiza?",
        [
            ("`class Exportador(ABC)` con `exportar` marcado con `@abstractmethod`", None),
            (
                "`class Exportador:` con `def exportar(self, datos): pass`",
                f"{CID}.version-base",
                "Una subclase podría olvidarlo y usaría la versión vacía sin ningún aviso.",
            ),
            (
                "Un comentario en `Exportador` que pida implementar `exportar`",
                None,
                "Python no lee comentarios: nada comprueba que se cumpla.",
            ),
            (
                "`class Exportador(ABC)` sin ningún `@abstractmethod`",
                f"{CID}.abstracta-instanciable",
                "Sin métodos abstractos, la clase y sus subclases se pueden instanciar aunque no tengan `exportar`.",
            ),
        ],
        0,
        "Heredar de `ABC` y marcar el método con `@abstractmethod` hace que Python no deje crear objetos de una subclase que no lo implemente.",
        level=3,
        daw=False,
        bank=True,
        qtype="solucion",
    ),
    choice(
        "poo6-27",
        CID,
        "Una tienda cobra con tarjeta, con Bizum y por transferencia, y añadirá más formas de pago. ¿Qué diseño encaja mejor?",
        [
            (
                "Una clase abstracta `Pago` con `cobrar(importe)` abstracto y una subclase por forma de pago; el programa solo llama a `pago.cobrar(...)`",
                None,
            ),
            (
                "Una función `cobrar(tipo, importe)` con un `if` por cada forma de pago",
                f"{CID}.isinstance-en-cadena",
                "Cada forma de pago nueva obliga a cambiar la función.",
            ),
            (
                "Una sola clase `Pago` con un atributo `tipo` y un `if` en `cobrar` según ese tipo",
                f"{CID}.isinstance-en-cadena",
                "Mete todas las formas de pago en un método lleno de condiciones: es el mismo problema dentro de una clase.",
            ),
            (
                "Una clase por forma de pago sin nada en común, y comprobar el tipo antes de llamar",
                f"{CID}.isinstance-en-cadena",
                "Si hay que comprobar el tipo, el código que cobra sigue dependiendo de cada clase.",
            ),
        ],
        0,
        "Con una clase abstracta, cada forma de pago cumple el mismo contrato y el resto del programa no cambia cuando llega una nueva.",
        level=3,
        daw=False,
        bank=True,
        qtype="diseno",
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

# Preguntas tipo test que ya existían y pasan al banco: (tipo, nivel, por qué falla cada distractor)
BANK_TAGS = {
    "poo6-02": (
        "teoria",
        1,
        [
            "Una clase tiene un solo `__init__`; el polimorfismo trata de objetos distintos que responden al mismo método.",
            "Eso es la herencia múltiple (Unidad 5).",
            "Es justo lo contrario: con polimorfismo no hace falta preguntar el tipo.",
        ],
    ),
    "poo6-05": (
        "codigo",
        1,
        [
            "En Python basta con que el objeto tenga el método: es el duck typing.",
            "Un `str` no tiene ningún método `texto()`: lo que hace falta es ese método.",
            "Python no comprueba tipos al llamar a una función: solo intenta ejecutar `x.texto()`.",
        ],
    ),
    "poo6-13": (
        "diseno",
        2,
        [
            "Cada figura nueva obliga a tocar la función: es justo lo que el polimorfismo evita.",
            "Es la misma cadena de comprobaciones, escrita de otra forma.",
            "Mete todos los cálculos en un sitio lleno de `if` y pierde lo que aporta cada clase.",
        ],
    ),
}
