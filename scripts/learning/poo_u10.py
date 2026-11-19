# ruff: noqa: E501
"""Unidad 10 del módulo de POO: proyecto final, gestión de una biblioteca.

Concepto `poo-proyecto` (área `poo`). El proyecto se construye en 6 ejercicios encadenados
(`poo10-01` … `poo10-06`): cada uno añade una pieza con sus tests y parte del código resuelto del
anterior, así que nadie se queda bloqueado. Todo cabe en un solo archivo, que es lo que ejecuta el
navegador. La unidad añade tres campos propios: `diagram` (diagrama de clases que la web dibuja como
SVG accesible), `rubric` (rúbrica de 100 puntos) y `challenges` (retos de ampliación sin tests).
"""

from textwrap import dedent

from exercises import c, case, choice, code, output
from poo_common import practice, proposed, ref

CID = "poo-proyecto"

# ---------------------------------------------------------------- piezas del proyecto
# Cada fase añade una pieza; la solución de la fase N es la cabecera y las piezas 1…N.
HEAD = "from datetime import date\n"

LIBRO = '''
class Libro:
    """Un libro del catálogo, identificado por su ISBN."""

    def __init__(self, isbn: str, titulo: str, autor: str) -> None:
        if not isbn.strip() or not titulo.strip():
            raise ValueError("El ISBN y el título son obligatorios")
        self.isbn = isbn
        self.titulo = titulo
        self.autor = autor
        self.disponible = True

    def __str__(self) -> str:
        estado = "disponible" if self.disponible else "prestado"
        return f"{self.titulo} ({self.autor}) [{estado}]"

    def __eq__(self, otro: object) -> bool:
        if not isinstance(otro, Libro):
            return NotImplemented
        return self.isbn == otro.isbn
'''

USUARIO = '''
class Usuario:
    """Una persona socia de la biblioteca."""

    def __init__(self, id: int, nombre: str, max_prestamos: int = 3) -> None:
        if not nombre.strip():
            raise ValueError("El nombre es obligatorio")
        self.id = id
        self.nombre = nombre
        self.max_prestamos = max_prestamos

    def puede_prestar(self, activos: int) -> bool:
        return activos < self.max_prestamos

    def __str__(self) -> str:
        return f"{self.nombre} (#{self.id})"
'''

PRESTAMO = '''
class Prestamo:
    """Un libro prestado a un usuario desde una fecha hasta que se devuelve."""

    def __init__(self, libro: Libro, usuario: Usuario, inicio: date) -> None:
        self.libro = libro
        self.usuario = usuario
        self.inicio = inicio
        self.fin: date | None = None

    @property
    def activo(self) -> bool:
        return self.fin is None

    def cerrar(self, fecha: date) -> None:
        if not self.activo:
            raise ValueError("El préstamo ya está cerrado")
        if fecha < self.inicio:
            raise ValueError("La devolución no puede ser anterior al préstamo")
        self.fin = fecha
'''

ERRORES = '''
class ErrorBiblioteca(Exception):
    """Cualquier error de las operaciones de la biblioteca."""


class LibroNoEncontrado(ErrorBiblioteca):
    def __init__(self, isbn: str) -> None:
        super().__init__(f"No existe el libro con ISBN {isbn}")
        self.isbn = isbn


class UsuarioNoEncontrado(ErrorBiblioteca):
    def __init__(self, id: int) -> None:
        super().__init__(f"No existe el usuario {id}")
        self.id = id


class LibroNoDisponible(ErrorBiblioteca):
    def __init__(self, titulo: str) -> None:
        super().__init__(f"«{titulo}» está prestado")
        self.titulo = titulo


class PrestamoDuplicado(ErrorBiblioteca):
    def __init__(self, titulo: str) -> None:
        super().__init__(f"Ya tienes en préstamo «{titulo}»")
        self.titulo = titulo


class LimiteAlcanzado(ErrorBiblioteca):
    def __init__(self, nombre: str) -> None:
        super().__init__(f"{nombre} ha llegado a su límite de préstamos")
        self.nombre = nombre
'''

_REGISTRO = '''
class Biblioteca:
    """Guarda libros y usuarios, y gestiona los préstamos."""

    def __init__(self, nombre: str) -> None:
        self.nombre = nombre
        self._libros: dict[str, Libro] = {}
        self._usuarios: dict[int, Usuario] = {}
        self._prestamos: list[Prestamo] = []

    def registrar_libro(self, libro: Libro) -> None:
        if libro.isbn in self._libros:
            raise ValueError(f"Ya hay un libro con ISBN {libro.isbn}")
        self._libros[libro.isbn] = libro

    def registrar_usuario(self, usuario: Usuario) -> None:
        if usuario.id in self._usuarios:
            raise ValueError(f"Ya hay un usuario con id {usuario.id}")
        self._usuarios[usuario.id] = usuario

    def catalogo(self, solo_disponibles: bool = False) -> list[Libro]:
        libros = [l for l in self._libros.values() if l.disponible or not solo_disponibles]
        return sorted(libros, key=lambda l: l.titulo)
'''

_OPERACIONES = """
    def _libro(self, isbn: str) -> Libro:
        if isbn not in self._libros:
            raise LibroNoEncontrado(isbn)
        return self._libros[isbn]

    def _usuario(self, id: int) -> Usuario:
        if id not in self._usuarios:
            raise UsuarioNoEncontrado(id)
        return self._usuarios[id]

    def prestamos_activos(self, usuario_id: int | None = None) -> list[Prestamo]:
        return [
            p
            for p in self._prestamos
            if p.activo and (usuario_id is None or p.usuario.id == usuario_id)
        ]

    def prestar(self, isbn: str, usuario_id: int, fecha: date) -> Prestamo:
        libro = self._libro(isbn)
        usuario = self._usuario(usuario_id)
        activos = self.prestamos_activos(usuario_id)
        if any(p.libro == libro for p in activos):
            raise PrestamoDuplicado(libro.titulo)
        if not libro.disponible:
            raise LibroNoDisponible(libro.titulo)
        if not usuario.puede_prestar(len(activos)):
            raise LimiteAlcanzado(usuario.nombre)
        prestamo = Prestamo(libro, usuario, fecha)
        libro.disponible = False
        self._prestamos.append(prestamo)
        return prestamo

    def devolver(self, isbn: str, fecha: date) -> Prestamo:
        libro = self._libro(isbn)
        for prestamo in self.prestamos_activos():
            if prestamo.libro == libro:
                prestamo.cerrar(fecha)
                libro.disponible = True
                return prestamo
        raise ErrorBiblioteca(f"«{libro.titulo}» no está prestado")
"""

BIBLIOTECA = _REGISTRO
BIBLIOTECA_COMPLETA = _REGISTRO + _OPERACIONES

PIECES = [LIBRO, USUARIO, PRESTAMO, ERRORES, BIBLIOTECA]

DEMOS = [
    'print(Libro("978-1", "Dune", "Frank Herbert"))\nprint(Libro("978-1", "Dune", "F. H.") == Libro("978-1", "Otro", "X"))',
    'ana = Usuario(1, "Ana", max_prestamos=2)\nprint(ana, ana.puede_prestar(1), ana.puede_prestar(2))',
    'p = Prestamo(Libro("978-1", "Dune", "F. Herbert"), Usuario(1, "Ana"), date(2026, 1, 10))\nprint(p.activo)\np.cerrar(date(2026, 1, 20))\nprint(p.activo, p.fin)',
    'try:\n    raise LibroNoEncontrado("978-9")\nexcept ErrorBiblioteca as error:\n    print(type(error).__name__, "-", error)',
    'bib = Biblioteca("IES")\nbib.registrar_libro(Libro("2", "Neuromante", "W. Gibson"))\nbib.registrar_libro(Libro("1", "Dune", "F. Herbert"))\nprint([l.titulo for l in bib.catalogo()])',
    'bib = Biblioteca("IES")\nbib.registrar_libro(Libro("1", "Dune", "F. Herbert"))\nbib.registrar_usuario(Usuario(7, "Ana"))\nbib.prestar("1", 7, date(2026, 1, 10))\nprint([str(l) for l in bib.catalogo()])\ntry:\n    bib.prestar("1", 7, date(2026, 1, 11))\nexcept ErrorBiblioteca as error:\n    print(error)\nbib.devolver("1", date(2026, 1, 20))\nprint(len(bib.prestamos_activos()))',
]


def _program(n: int, *, full: bool = False, demo: bool = True) -> str:
    """Código de las fases 1…n (la 6 usa la Biblioteca completa) más la demostración de la fase n."""
    pieces = PIECES[:n] if n <= 5 else [*PIECES[:4], BIBLIOTECA_COMPLETA]
    body = HEAD + "\n" + "\n".join(p.strip("\n") + "\n\n" for p in pieces)
    return body + ("\n" + DEMOS[n - 1] + "\n" if demo else "")


def _starter(n: int, todo: str) -> str:
    """Código inicial de la fase n: lo resuelto en las fases anteriores y el hueco de la nueva."""
    previous = _program(n - 1, demo=False) if n > 1 else HEAD + "\n"
    return previous + f"\n# Fase {n}: {todo}\n"


def _broken(n: int, old: str, new: str) -> str:
    """Solución de la fase n con un fallo (para comprobar que los tests lo detectan)."""
    program = _program(n, demo=False)
    assert program.count(old) == 1, old
    return program.replace(old, new)


CONCEPT = {
    "id": CID,
    "title": "Proyecto final: gestión de una biblioteca",
    "area": "poo",
    "requires": ["poo-metodos-especiales", "poo-diseno"],
    "daw": 2,
    "ut": "prog-ut7",
    "lessons": ["poo"],
    "summary": "Una aplicación completa con todo lo del módulo: libros, usuarios y préstamos, con errores propios, pruebas y una rúbrica.",
    "when": "Cuando quieras demostrar que sabes diseñar varias clases que colaboran: es el tipo de proyecto que se pide al final de la POO en Programación.",
    "example": {
        "code": c(
            """
            from datetime import date


            class Libro:
                def __init__(self, isbn, titulo):
                    self.isbn = isbn
                    self.titulo = titulo
                    self.disponible = True


            class Prestamo:
                def __init__(self, libro, inicio):
                    self.libro = libro
                    self.inicio = inicio


            class Biblioteca:
                def __init__(self):
                    self.libros = {}            # agregación: los libros vienen de fuera
                    self.prestamos = []         # composición: los crea la biblioteca

                def prestar(self, isbn, fecha):
                    libro = self.libros[isbn]
                    if not libro.disponible:
                        raise ValueError(f"{libro.titulo} está prestado")
                    libro.disponible = False
                    self.prestamos.append(Prestamo(libro, fecha))


            bib = Biblioteca()
            bib.libros["1"] = Libro("1", "Dune")
            bib.prestar("1", date(2026, 1, 10))
            try:
                bib.prestar("1", date(2026, 1, 11))
            except ValueError as error:
                print(error)
            """
        ),
        "lines": [
            [19, "La biblioteca guarda libros que existen por su cuenta."],
            [20, "Los préstamos los crea la propia biblioteca."],
            [24, "Primero se comprueba; solo si todo está bien se cambia el estado."],
            [34, "El segundo préstamo del mismo libro da un error claro."],
        ],
    },
    "errors": [],
    "related": ["poo-diseno", "poo-composicion", "excepciones"],
}

UNIT = {
    "unit": {"module": "poo", "number": 10},
    "objectives": [
        "Diseñar una aplicación de varias clases a partir de un enunciado y su diagrama de clases.",
        "Programar `Libro`, `Usuario`, `Prestamo` y `Biblioteca` con sus responsabilidades y relaciones.",
        "Crear una jerarquía de excepciones propias y lanzarlas en cada caso de error sin dejar el estado a medias.",
        "Comprobar el proyecto con tests y añadir pruebas propias.",
        "Valorar tu trabajo con una rúbrica y ampliarlo con retos opcionales.",
    ],
    "prior": "Todo el módulo: en especial la composición (Unidad 7), los métodos especiales (Unidad 8) y el diseño (Unidad 9), además de las excepciones.",
    "key": [
        [
            "Diagrama de clases",
            "Dibujo de las clases, sus atributos y métodos, y las relaciones entre ellas. Se hace antes de programar.",
        ],
        [
            "Excepción propia",
            "Una clase que hereda de `Exception` (o de otra excepción propia) para nombrar un error del programa: `class LibroNoDisponible(ErrorBiblioteca)`.",
        ],
        [
            "Jerarquía de excepciones",
            "Excepciones propias que heredan de una base común; `except ErrorBiblioteca` las captura todas.",
        ],
        [
            "Estado consistente",
            "Tras un error, ningún dato queda a medias: se comprueba todo antes de cambiar nada.",
        ],
        [
            "Integración",
            "Juntar las piezas que ya funcionan por separado y comprobar que funcionan juntas.",
        ],
        [
            "Rúbrica",
            "Tabla con los criterios y los puntos con que se valora el proyecto.",
        ],
    ],
    "sections": [
        {
            "id": f"{CID}.arquitectura",
            "title": "Arquitectura y diagrama de clases",
            "theory": "El proyecto es la gestión de una biblioteca: se registran libros y usuarios, se prestan libros y se devuelven. Antes de escribir código se decide **qué clases hay**, **de qué se ocupa cada una** y **cómo se relacionan** (lo verás dibujado en el diagrama de esta página).\n\n| Clase | Responsabilidad |\n|---|---|\n| `Libro` | Sus datos (ISBN, título, autor) y si está disponible. Dos libros son el mismo si tienen el mismo ISBN. |\n| `Usuario` | Sus datos y cuántos préstamos puede tener a la vez. |\n| `Prestamo` | Un libro prestado a un usuario: la fecha de inicio, la de devolución y si sigue activo. |\n| `Biblioteca` | Registra libros y usuarios, crea y cierra préstamos y comprueba las reglas. |\n| `ErrorBiblioteca` y sus subclases | Nombran cada error de las operaciones. |\n\nRelaciones:\n\n- La biblioteca **agrega** libros y usuarios: se crean fuera y existen por su cuenta.\n- La biblioteca **compone** los préstamos: los crea ella al prestar.\n- Cada préstamo está **asociado** a un libro y a un usuario.\n\nEl proyecto se construye **por fases**: cada ejercicio añade una pieza con sus propios tests y parte del código resuelto del anterior. La última fase lo integra todo.",
            "examples": [
                {
                    "code": c(
                        """
                        # Fase   Pieza                      Depende de
                        fases = [
                            (1, "Libro", []),
                            (2, "Usuario", []),
                            (3, "Prestamo", ["Libro", "Usuario"]),
                            (4, "Excepciones", []),
                            (5, "Biblioteca: registro", ["Libro", "Usuario"]),
                            (6, "Biblioteca: préstamos", ["Prestamo", "Excepciones"]),
                        ]
                        hechas = set()
                        for numero, pieza, necesita in fases:
                            assert all(n in hechas or n.split(":")[0] in hechas for n in necesita)
                            hechas.add(pieza.split(":")[0])
                            print(numero, pieza)
                        """
                    ),
                    "lines": [
                        [3, "Las clases sin dependencias van primero."],
                        [5, "`Prestamo` necesita que existan `Libro` y `Usuario`."],
                        [12, "Comprueba que cada fase solo usa piezas ya hechas."],
                    ],
                }
            ],
            "quiz": ["poo10-07", "poo10-08", "poo10-09"],
        },
        {
            "id": f"{CID}.libro-usuario",
            "title": "Libro y Usuario",
            "theory": 'Son las dos clases más sencillas: guardan datos, los validan y saben presentarse.\n\n- **Validar en el constructor**: un libro sin ISBN o sin título, o un usuario sin nombre, no tiene sentido. Lanza `ValueError` y el objeto no llega a crearse. `"  ".strip()` es `""`, así que `if not isbn.strip()` detecta también los textos con solo espacios.\n- **`__str__`** para mostrarlos: `Dune (Frank Herbert) [disponible]`.\n- **`__eq__` por ISBN**: el ISBN identifica el libro aunque otro objeto tenga el título mal escrito. Devuelve `NotImplemented` si el otro no es un `Libro`.\n- **`puede_prestar(activos)`**: el usuario sabe su límite (`max_prestamos`, 3 por defecto), pero no cuenta sus préstamos: eso lo sabe la biblioteca, que se lo pasa. Así cada dato está en un solo sitio.',
            "examples": [
                {
                    "code": c(
                        """
                        class Usuario:
                            def __init__(self, id, nombre, max_prestamos=3):
                                if not nombre.strip():
                                    raise ValueError("El nombre es obligatorio")
                                self.id = id
                                self.nombre = nombre
                                self.max_prestamos = max_prestamos

                            def puede_prestar(self, activos):
                                return activos < self.max_prestamos


                        eva = Usuario(2, "Eva", max_prestamos=1)
                        print(eva.puede_prestar(0), eva.puede_prestar(1))
                        try:
                            Usuario(3, "   ")
                        except ValueError as error:
                            print(error)
                        """
                    ),
                    "lines": [
                        [
                            3,
                            "`strip()` quita los espacios: un nombre de solo espacios también es vacío.",
                        ],
                        [9, "El usuario recibe cuántos préstamos tiene; no los cuenta él."],
                        [16, "El objeto no llega a crearse si los datos no son válidos."],
                    ],
                }
            ],
            "quiz": ["poo10-10", "poo10-11", "poo10-12"],
        },
        {
            "id": f"{CID}.prestamo",
            "title": "Prestamo: fechas y estado",
            "theory": "Un préstamo une un libro y un usuario durante un tiempo. Usa el módulo `datetime` de la biblioteca estándar: `date(2026, 1, 10)` es una fecha y dos fechas se comparan con `<`.\n\n- Guarda `inicio` y `fin`, que empieza en `None` mientras el libro no se devuelve.\n- **`activo`** es una **propiedad** (Unidad 4): no se guarda, se calcula (`self.fin is None`). Así nunca se contradice con `fin`.\n- **`cerrar(fecha)`** valida antes de cambiar nada: si ya estaba cerrado o la fecha es anterior al inicio, lanza `ValueError` y el préstamo sigue como estaba.\n\nEl préstamo no cambia la disponibilidad del libro: de eso se encarga la biblioteca, que es quien sabe que ha prestado o recibido el libro.",
            "examples": [
                {
                    "code": c(
                        """
                        from datetime import date


                        class Prestamo:
                            def __init__(self, libro, inicio):
                                self.libro = libro
                                self.inicio = inicio
                                self.fin = None

                            @property
                            def activo(self):
                                return self.fin is None

                            def cerrar(self, fecha):
                                if not self.activo:
                                    raise ValueError("El préstamo ya está cerrado")
                                if fecha < self.inicio:
                                    raise ValueError("La devolución no puede ser anterior al préstamo")
                                self.fin = fecha


                        p = Prestamo("Dune", date(2026, 1, 10))
                        try:
                            p.cerrar(date(2026, 1, 5))
                        except ValueError as error:
                            print(error, "- activo:", p.activo)
                        p.cerrar(date(2026, 1, 20))
                        print(p.activo, (p.fin - p.inicio).days, "días")
                        """
                    ),
                    "lines": [
                        [8, "Sin devolver todavía: `fin` es `None`."],
                        [11, "`activo` se calcula a partir de `fin`, no se guarda aparte."],
                        [17, "Se valida antes de tocar `fin`."],
                        [28, "Restar dos fechas da los días que ha durado el préstamo."],
                    ],
                }
            ],
            "quiz": ["poo10-13", "poo10-14", "poo10-15"],
        },
        {
            "id": f"{CID}.biblioteca-errores",
            "title": "Biblioteca y excepciones propias",
            "theory": "La `Biblioteca` coordina: guarda los libros (por ISBN) y los usuarios (por id) en diccionarios, y crea los préstamos.\n\nCada caso de error tiene **su excepción**. Todas heredan de `ErrorBiblioteca`, que hereda de `Exception`:\n\n| Excepción | Cuándo |\n|---|---|\n| `LibroNoEncontrado` | El ISBN no está registrado. |\n| `UsuarioNoEncontrado` | El id no está registrado. |\n| `PrestamoDuplicado` | El usuario ya tiene ese mismo libro. |\n| `LibroNoDisponible` | El libro lo tiene otra persona. |\n| `LimiteAlcanzado` | El usuario ya tiene su máximo de préstamos. |\n\nLos datos vacíos y los ISBN o id repetidos al registrar dan `ValueError`, y devolver un libro que no está prestado da `ErrorBiblioteca`.\n\n- Quien usa la biblioteca puede capturar un error concreto (`except LibroNoDisponible`) o todos a la vez (`except ErrorBiblioteca`).\n- En un `try` con varios `except`, Python usa el **primero** que encaja: pon los concretos antes que el general.\n- **Comprueba todo antes de cambiar nada**: si `prestar` marcara el libro como prestado y luego fallara la comprobación del límite, el libro quedaría «prestado» sin préstamo. Es el error que la rúbrica llama dejar el estado a medias.",
            "examples": [
                {
                    "code": c(
                        """
                        class ErrorBiblioteca(Exception):
                            \"\"\"Cualquier error de la biblioteca.\"\"\"


                        class LibroNoEncontrado(ErrorBiblioteca):
                            def __init__(self, isbn):
                                super().__init__(f"No existe el libro con ISBN {isbn}")
                                self.isbn = isbn


                        def buscar(libros, isbn):
                            if isbn not in libros:
                                raise LibroNoEncontrado(isbn)
                            return libros[isbn]


                        libros = {"1": "Dune"}
                        for isbn in ("1", "9"):
                            try:
                                print(buscar(libros, isbn))
                            except LibroNoEncontrado as error:
                                print("Concreto:", error, error.isbn)
                            except ErrorBiblioteca:
                                print("Cualquier otro error de la biblioteca")
                        print(issubclass(LibroNoEncontrado, Exception))
                        """
                    ),
                    "lines": [
                        [1, "La base de todas las excepciones del proyecto."],
                        [7, "`super().__init__` guarda el mensaje que se ve al imprimir el error."],
                        [8, "La excepción guarda además el dato que falló."],
                        [21, "El `except` concreto va antes que el general."],
                    ],
                }
            ],
            "quiz": ["poo10-16", "poo10-17", "poo10-18"],
        },
        {
            "id": f"{CID}.pruebas-retos",
            "title": "Pruebas, retos y rúbrica",
            "theory": 'Cada fase se corrige con tests en tu navegador. Además, la rúbrica pide que añadas **al menos 3 pruebas tuyas** con `assert`. Una buena prueba:\n\n- comprueba **una sola cosa** y su mensaje dice qué falla: `assert len(bib.prestamos_activos()) == 1, "Debe haber un préstamo activo"`;\n- prueba también los **casos de error**: que se lanza la excepción correcta **y** que el estado no ha cambiado;\n- parte de datos nuevos, para no depender de lo que hizo otra prueba.\n\nPara comprobar que algo lanza un error sin una librería de pruebas:\n\n```\ntry:\n    bib.prestar("1", 7, date(2026, 1, 11))\nexcept LibroNoDisponible:\n    pass\nelse:\n    raise AssertionError("Debía lanzar LibroNoDisponible")\n```\n\nCuando termines, valora tu proyecto con la **rúbrica** de esta página y, si quieres más, elige uno de los **retos de ampliación**: no tienen tests obligatorios.',
            "examples": [
                {
                    "code": c(
                        """
                        def lanza(error, funcion, *args):
                            \"\"\"True si funcion(*args) lanza ese error.\"\"\"
                            try:
                                funcion(*args)
                            except error:
                                return True
                            return False


                        stock = {"Dune": 1}


                        def prestar(titulo):
                            if stock.get(titulo, 0) == 0:
                                raise ValueError(f"No queda {titulo}")
                            stock[titulo] -= 1


                        prestar("Dune")
                        assert stock["Dune"] == 0, "Prestar descuenta uno"
                        assert lanza(ValueError, prestar, "Dune"), "Sin stock debe dar ValueError"
                        assert stock["Dune"] == 0, "Un error no cambia el stock"
                        print("3 pruebas superadas")
                        """
                    ),
                    "lines": [
                        [1, "Una función de ayuda para probar errores sin repetir el `try`."],
                        [20, "Primera prueba: el caso normal."],
                        [21, "Segunda: el caso de error lanza la excepción correcta."],
                        [22, "Tercera: el error no deja el estado a medias."],
                    ],
                }
            ],
            "quiz": ["poo10-19", "poo10-20", "poo10-21"],
        },
    ],
    "guided": ["poo10-01"],
    "autonomous": ["poo10-06"],
    "extras": ["poo10-02", "poo10-03", "poo10-04", "poo10-05"],
    "selfcheck": ["poo10-22", "poo10-23"],
    "recap": [
        "Diseña antes de programar: clases, responsabilidades y relaciones en un diagrama.",
        "La biblioteca agrega libros y usuarios y compone los préstamos; cada préstamo se asocia a un libro y a un usuario.",
        "Valida los datos en el constructor y lanza `ValueError` si no sirven.",
        "Una jerarquía de excepciones propias permite capturar un error concreto o todos a la vez.",
        "Comprueba todas las reglas antes de cambiar el estado.",
        "Construye por fases, con tests en cada una, e integra al final.",
    ],
    "pass": {
        "minScore": 0.7,
        "required": ["poo10-01", "poo10-06"],
        "text": [
            "Superar los tests de las 6 fases del proyecto; la fase 6 (la biblioteca completa) es el ejercicio principal.",
            "Al menos un 70 % en el cuestionario de la unidad y dominar la unidad según el motor, con varios tipos de ejercicio distintos.",
            "Valorar tu proyecto con la rúbrica: la funcionalidad son 40 de los 100 puntos; el diseño, los errores, tus pruebas y el estilo, el resto.",
        ],
    },
    "practices": [
        practice(
            "Dibuja el diagrama de clases antes de escribir la primera línea.",
            "Decidir las responsabilidades después de programar obliga a rehacer clases enteras.",
        ),
        practice(
            "Termina y prueba una clase antes de empezar la siguiente.",
            "Si algo falla al integrar, sabes que las piezas por separado funcionaban.",
        ),
        practice(
            "Comprueba todas las reglas antes de cambiar el estado.",
            "Un error a mitad de operación no puede dejar un libro «prestado» sin préstamo.",
        ),
        practice(
            "Crea una excepción propia para cada caso de error que quien use la clase quiera distinguir.",
            "`except LibroNoDisponible` es más claro y seguro que comparar el texto del mensaje.",
        ),
        practice(
            "Guarda cada dato en un solo sitio: la disponibilidad en el libro, los préstamos en la biblioteca.",
            "Dos copias del mismo dato acaban contradiciéndose.",
        ),
    ],
    "references": [
        ref(
            "py-tutorial-classes",
            "9.5. Herencia",
            ["excepciones propias como subclases de `Exception`"],
        ),
        ref(
            "py-faq-programming",
            "Objetos: ¿Cómo puedo llamar a un método definido en una clase base desde una clase derivada que la extiende?",
            ["`super().__init__(mensaje)` en una excepción propia"],
        ),
        ref(
            "py-dataclasses",
            "El decorador dataclass",
            ["reto de ampliación: informes con clases de datos"],
        ),
    ],
    "diagram": {
        "title": "Diagrama de clases del proyecto biblioteca",
        "summary": "La biblioteca guarda libros y usuarios que existen por su cuenta (agregación) y crea los préstamos (composición). Cada préstamo apunta a un libro y a un usuario (asociación). Las excepciones del proyecto heredan de ErrorBiblioteca.",
        "classes": [
            {
                "id": "biblioteca",
                "name": "Biblioteca",
                "col": 1,
                "row": 0,
                "members": [
                    "registrar_libro()",
                    "registrar_usuario()",
                    "catalogo()",
                    "prestar() · devolver()",
                ],
            },
            {
                "id": "libro",
                "name": "Libro",
                "col": 0,
                "row": 1,
                "members": ["isbn · titulo · autor", "disponible", "__str__ · __eq__"],
            },
            {
                "id": "usuario",
                "name": "Usuario",
                "col": 2,
                "row": 1,
                "members": ["id · nombre", "max_prestamos", "puede_prestar()"],
            },
            {
                "id": "prestamo",
                "name": "Prestamo",
                "col": 1,
                "row": 2,
                "members": ["libro · usuario", "inicio · fin", "activo · cerrar()"],
            },
            {
                "id": "error",
                "name": "ErrorBiblioteca",
                "col": 0,
                "row": 2,
                "members": ["LibroNoEncontrado", "UsuarioNoEncontrado", "PrestamoDuplicado · …"],
            },
        ],
        "relations": [
            {
                "from": "biblioteca",
                "to": "libro",
                "kind": "agregacion",
                "text": "La biblioteca agrega libros: se crean fuera y existen por su cuenta.",
            },
            {
                "from": "biblioteca",
                "to": "usuario",
                "kind": "agregacion",
                "text": "La biblioteca agrega usuarios: se crean fuera y existen por su cuenta.",
            },
            {
                "from": "biblioteca",
                "to": "prestamo",
                "kind": "composicion",
                "text": "La biblioteca compone los préstamos: los crea al prestar.",
            },
            {
                "from": "prestamo",
                "to": "libro",
                "kind": "asociacion",
                "text": "Cada préstamo está asociado a un libro.",
            },
            {
                "from": "prestamo",
                "to": "usuario",
                "kind": "asociacion",
                "text": "Cada préstamo está asociado a un usuario.",
            },
        ],
    },
    "rubric": [
        {"criterion": "Funcionalidad", "points": 40, "text": "Pasan los tests de las 6 fases."},
        {
            "criterion": "Diseño de clases",
            "points": 25,
            "text": "Cada clase tiene una sola responsabilidad y las relaciones son las del diagrama.",
        },
        {
            "criterion": "Control de errores",
            "points": 15,
            "text": "Cada caso de error lanza su excepción y no deja el estado a medias.",
        },
        {"criterion": "Pruebas propias", "points": 10, "text": "Añades al menos 3 `assert` tuyos."},
        {
            "criterion": "Estilo y documentación",
            "points": 10,
            "text": "Type hints, docstrings y nombres claros.",
        },
    ],
    "challenges": [
        "Multas por retraso: cada préstamo vence a los 14 días y `devolver` calcula una multa por día de retraso.",
        "Reservas: un usuario puede reservar un libro prestado y es el primero en recibirlo al devolverse.",
        "Búsqueda por autor: `buscar(autor)` devuelve los libros de ese autor, sin distinguir mayúsculas.",
        "Informes con `dataclasses`: un `Informe` con los libros más prestados y los usuarios con más préstamos.",
        "Guardar el estado en JSON: `guardar(ruta)` y `cargar(ruta)` con el módulo `json` (en tu ordenador, no en el navegador).",
    ],
    "bank": [
        "poo10-07",
        "poo10-08",
        "poo10-09",
        "poo10-11",
        "poo10-12",
        "poo10-14",
        "poo10-15",
        "poo10-17",
        "poo10-18",
        "poo10-19",
        "poo10-20",
        "poo10-21",
        "poo10-22",
        "poo10-24",
        "poo10-25",
    ],
    "curriculum": [
        proposed(
            "0485-RA4-e",
            "Se desarrolla una aplicación que instancia y usa objetos de varias clases propias.",
        ),
        proposed(
            "0485-RA3-h",
            "Se crean excepciones propias en una jerarquía (`ErrorBiblioteca` y sus subclases).",
        ),
        proposed(
            "0485-RA3-f",
            "Se prueba y depura el proyecto por fases con tests y pruebas propias.",
        ),
    ],
}

# ---------------------------------------------------------------- tests de cada fase
D = "from datetime import date\n"

T_LIBRO = [
    case(
        'l = Libro("978-1", "Dune", "Frank Herbert")\nassert (l.isbn, l.titulo, l.autor, l.disponible) == ("978-1", "Dune", "Frank Herbert", True), "Libro guarda isbn, titulo y autor, y empieza disponible"\nassert str(l) == "Dune (Frank Herbert) [disponible]", f"str() devuelve {str(l)!r}"\nl.disponible = False\nassert str(l) == "Dune (Frank Herbert) [prestado]", f"Prestado, str() devuelve {str(l)!r}"',
    ),
    case(
        'assert Libro("978-1", "Dune", "F. H.") == Libro("978-1", "Duna", "X"), "Dos libros con el mismo ISBN son el mismo"\nassert Libro("978-1", "Dune", "F. H.") != Libro("978-2", "Dune", "F. H."), "Con otro ISBN no son el mismo"\nassert (Libro("1", "A", "B") == "1") is False, "Con otro tipo, __eq__ devuelve NotImplemented y == da False"',
        error="poo-metodos-especiales.eq-identidad",
    ),
    case(
        'for args in (("", "Dune", "X"), ("   ", "Dune", "X"), ("978-1", " ", "X")):\n    try:\n        Libro(*args)\n    except ValueError:\n        pass\n    else:\n        raise AssertionError(f"Libro{args} debe lanzar ValueError: el ISBN y el título son obligatorios")',
        error=f"{CID}.valida-tarde",
    ),
]

T_USUARIO = [
    case(
        'u = Usuario(1, "Ana")\nassert (u.id, u.nombre, u.max_prestamos) == (1, "Ana", 3), "Usuario(id, nombre) con max_prestamos=3 por defecto"\nassert str(u) == "Ana (#1)", f"str() devuelve {str(u)!r}"',
    ),
    case(
        'u = Usuario(2, "Eva", max_prestamos=2)\nassert u.puede_prestar(0) and u.puede_prestar(1), "Con menos préstamos que el máximo, puede"\nassert not u.puede_prestar(2) and not u.puede_prestar(5), "Con el máximo o más, no puede"',
    ),
    case(
        'for nombre in ("", "   "):\n    try:\n        Usuario(3, nombre)\n    except ValueError:\n        pass\n    else:\n        raise AssertionError(f"Usuario(3, {nombre!r}) debe lanzar ValueError")',
        error=f"{CID}.valida-tarde",
    ),
]

T_PRESTAMO = [
    case(
        D
        + 'l, u = Libro("1", "Dune", "X"), Usuario(1, "Ana")\np = Prestamo(l, u, date(2026, 1, 10))\nassert p.libro is l and p.usuario is u, "El préstamo guarda el mismo libro y el mismo usuario"\nassert p.inicio == date(2026, 1, 10) and p.fin is None, "Empieza con su fecha de inicio y sin fin"\nassert p.activo is True, "Un préstamo nuevo está activo"',
    ),
    case(
        D
        + 'p = Prestamo(Libro("1", "Dune", "X"), Usuario(1, "Ana"), date(2026, 1, 10))\np.cerrar(date(2026, 1, 10))\nassert p.fin == date(2026, 1, 10) and p.activo is False, "cerrar(fecha) guarda el fin y el préstamo deja de estar activo"\ntry:\n    p.cerrar(date(2026, 1, 12))\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError("Cerrar dos veces debe lanzar ValueError")\nassert p.fin == date(2026, 1, 10), "El segundo cierre no cambia la fecha"',
        error=f"{CID}.estado-a-medias",
    ),
    case(
        D
        + 'p = Prestamo(Libro("1", "Dune", "X"), Usuario(1, "Ana"), date(2026, 1, 10))\ntry:\n    p.cerrar(date(2026, 1, 9))\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError("Una devolución anterior al inicio debe lanzar ValueError")\nassert p.activo and p.fin is None, "Si la fecha no vale, el préstamo sigue activo"\np.fin = date(2026, 2, 1)\nassert p.activo is False, "activo debe calcularse a partir de fin (una propiedad), no guardarse aparte"',
        error=f"{CID}.dato-duplicado",
    ),
]

T_ERRORES = [
    case(
        'for clase in (LibroNoEncontrado, UsuarioNoEncontrado, LibroNoDisponible, PrestamoDuplicado, LimiteAlcanzado):\n    assert issubclass(clase, ErrorBiblioteca), f"{clase.__name__} debe heredar de ErrorBiblioteca"\nassert issubclass(ErrorBiblioteca, Exception) and ErrorBiblioteca is not Exception, "ErrorBiblioteca hereda de Exception"',
        error=f"{CID}.excepcion-sin-jerarquia",
    ),
    case(
        'e = LibroNoEncontrado("978-9")\nassert str(e) == "No existe el libro con ISBN 978-9" and e.isbn == "978-9", f"Mensaje: {e}"\ne = UsuarioNoEncontrado(7)\nassert str(e) == "No existe el usuario 7" and e.id == 7, f"Mensaje: {e}"',
    ),
    case(
        'e = LibroNoDisponible("Dune")\nassert str(e) == "«Dune» está prestado" and e.titulo == "Dune", f"Mensaje: {e}"\ne = PrestamoDuplicado("Dune")\nassert str(e) == "Ya tienes en préstamo «Dune»", f"Mensaje: {e}"\ne = LimiteAlcanzado("Ana")\nassert str(e) == "Ana ha llegado a su límite de préstamos" and e.nombre == "Ana", f"Mensaje: {e}"\ntry:\n    raise LimiteAlcanzado("Ana")\nexcept ErrorBiblioteca:\n    pass',
    ),
]

T_REGISTRO = [
    case(
        'b = Biblioteca("IES")\nassert b.nombre == "IES" and b.catalogo() == [], "Una biblioteca nueva no tiene libros"\nl = Libro("1", "Dune", "X")\nb.registrar_libro(l)\nassert b.catalogo() == [l] and b.catalogo()[0] is l, "registrar_libro guarda el mismo libro"',
    ),
    case(
        'b = Biblioteca("IES")\nb.registrar_libro(Libro("1", "Dune", "X"))\nb.registrar_usuario(Usuario(1, "Ana"))\nfor accion in (lambda: b.registrar_libro(Libro("1", "Otro", "Y")), lambda: b.registrar_usuario(Usuario(1, "Eva"))):\n    try:\n        accion()\n    except ValueError:\n        pass\n    else:\n        raise AssertionError("Un ISBN o un id ya registrado debe lanzar ValueError")\nassert [l.titulo for l in b.catalogo()] == ["Dune"], "El libro repetido no se registra"',
    ),
    case(
        'b = Biblioteca("IES")\nfor isbn, titulo in (("3", "Neuromante"), ("1", "Dune"), ("2", "Fundación")):\n    b.registrar_libro(Libro(isbn, titulo, "X"))\nassert [l.titulo for l in b.catalogo()] == ["Dune", "Fundación", "Neuromante"], "El catálogo sale ordenado por título"\nb.catalogo()[0].disponible = False\nassert [l.titulo for l in b.catalogo(solo_disponibles=True)] == ["Fundación", "Neuromante"], "catalogo(solo_disponibles=True) quita los prestados"\nassert len(b.catalogo()) == 3, "Sin el parámetro, salen todos"',
    ),
]

_SETUP = (
    D
    + 'b = Biblioteca("IES")\nfor isbn, titulo in (("1", "Dune"), ("2", "Fundación"), ("3", "Neuromante")):\n    b.registrar_libro(Libro(isbn, titulo, "X"))\nb.registrar_usuario(Usuario(7, "Ana", max_prestamos=2))\nb.registrar_usuario(Usuario(8, "Luis"))\nhoy = date(2026, 1, 10)\n'
)


def _raises(call: str, error: str, why: str) -> str:
    return (
        f'try:\n    {call}\nexcept {error}:\n    pass\nelse:\n    raise AssertionError("{why}")\n'
    )


T_BIBLIOTECA = [
    case(
        _SETUP
        + 'p = b.prestar("1", 7, hoy)\nassert isinstance(p, Prestamo) and p.libro.isbn == "1" and p.usuario.id == 7 and p.inicio == hoy, "prestar() crea y devuelve el Prestamo"\nassert p.libro.disponible is False, "El libro prestado deja de estar disponible"\nassert b.prestamos_activos() == [p] and b.prestamos_activos(7) == [p] and b.prestamos_activos(8) == [], "prestamos_activos() con y sin usuario"',
    ),
    case(
        _SETUP
        + _raises(
            'b.prestar("9", 7, hoy)',
            "LibroNoEncontrado",
            "Un ISBN que no existe debe lanzar LibroNoEncontrado",
        )
        + _raises(
            'b.prestar("1", 99, hoy)',
            "UsuarioNoEncontrado",
            "Un usuario que no existe debe lanzar UsuarioNoEncontrado",
        )
        + _raises(
            'b.devolver("9", hoy)',
            "LibroNoEncontrado",
            "Devolver un ISBN que no existe debe lanzar LibroNoEncontrado",
        )
        + 'assert b.prestamos_activos() == [], "Los errores no crean préstamos"',
        error=f"{CID}.excepcion-generica",
    ),
    case(
        _SETUP
        + 'b.prestar("1", 7, hoy)\n'
        + _raises(
            'b.prestar("1", 7, hoy)',
            "PrestamoDuplicado",
            "Pedir otra vez un libro que ya tienes debe lanzar PrestamoDuplicado",
        )
        + _raises(
            'b.prestar("1", 8, hoy)',
            "LibroNoDisponible",
            "Un libro prestado a otra persona debe lanzar LibroNoDisponible",
        )
        + 'assert len(b.prestamos_activos()) == 1, "Un libro no se puede prestar dos veces"',
    ),
    case(
        _SETUP
        + 'b.prestar("1", 7, hoy)\nb.prestar("2", 7, hoy)\n'
        + _raises(
            'b.prestar("3", 7, hoy)',
            "LimiteAlcanzado",
            "Con su máximo de préstamos, el usuario no puede pedir más: LimiteAlcanzado",
        )
        + 'tercero = [l for l in b.catalogo() if l.isbn == "3"][0]\nassert tercero.disponible, "Si se supera el límite, el libro sigue disponible (sin estado a medias)"\nassert len(b.prestamos_activos(7)) == 2, "No se crea el tercer préstamo"',
        error=f"{CID}.estado-a-medias",
    ),
    case(
        _SETUP
        + 'p = b.prestar("1", 7, hoy)\ndevuelto = b.devolver("1", date(2026, 1, 20))\nassert devuelto is p and p.fin == date(2026, 1, 20) and not p.activo, "devolver() cierra y devuelve el préstamo"\nassert p.libro.disponible and b.prestamos_activos() == [], "El libro vuelve a estar disponible"\n'
        + _raises(
            'b.devolver("1", date(2026, 1, 21))',
            "ErrorBiblioteca",
            "Devolver un libro que no está prestado debe lanzar ErrorBiblioteca",
        )
        + 'b.prestar("1", 8, date(2026, 1, 21))\n'
        + _raises(
            'b.devolver("1", date(2026, 1, 1))',
            "ValueError",
            "Una devolución anterior al préstamo debe lanzar ValueError",
        )
        + 'assert not [l for l in b.catalogo() if l.isbn == "1"][0].disponible and len(b.prestamos_activos()) == 1, "Si la fecha no vale, el libro sigue prestado"\nassert [l.titulo for l in b.catalogo(solo_disponibles=True)] == ["Fundación", "Neuromante"], "El catálogo de disponibles quita el prestado"',
        error=f"{CID}.estado-a-medias",
    ),
]

EXERCISES = [
    # ---------- Fases del proyecto (guiado, prácticas adicionales y principal)
    code(
        "poo10-01",
        CID,
        '**Fase 1 del proyecto: `Libro`.** Crea `Libro(isbn, titulo, autor)`:\n\n1. Si el ISBN o el título están vacíos (o solo tienen espacios), lanza `ValueError`.\n2. Guarda los tres datos y `disponible = True`.\n3. `__str__` devuelve `"Dune (Frank Herbert) [disponible]"` o `[prestado]`.\n4. `__eq__`: dos libros son iguales si tienen el mismo ISBN; con otro tipo, `NotImplemented`.',
        _starter(1, "la clase Libro"),
        _program(1),
        T_LIBRO,
        "El libro valida sus datos al crearse y se compara por lo que lo identifica, el ISBN. Así la biblioteca podrá encontrar «el mismo libro» aunque sea otro objeto.",
        "Valida con `if not isbn.strip() or not titulo.strip(): raise ValueError(...)` antes de guardar nada.",
        wrong=[
            (
                _broken(
                    1,
                    '        return f"{self.titulo} ({self.autor}) [{estado}]"',
                    '        return f"{self.titulo} [{estado}]"',
                ),
                1,
            ),
            (_broken(1, "        return self.isbn == otro.isbn", "        return self is otro"), 2),
            (
                _broken(
                    1,
                    "        if not isbn.strip() or not titulo.strip():",
                    "        if not isbn or not titulo:",
                ),
                3,
            ),
        ],
        level=2,
        daw=False,
    ),
    code(
        "poo10-02",
        CID,
        '**Fase 2 del proyecto: `Usuario`.** El `Libro` de la fase 1 ya está. Añade `Usuario(id, nombre, max_prestamos=3)`:\n\n- Un nombre vacío (o solo espacios) da `ValueError`.\n- `puede_prestar(activos)`: `True` si `activos` es menor que `max_prestamos`.\n- `__str__` → `"Ana (#1)"`.',
        _starter(2, "la clase Usuario"),
        _program(2),
        T_USUARIO,
        "El usuario conoce su límite, pero no cuenta sus préstamos: esa información la tiene la biblioteca y se la pasa. Cada dato está en un solo sitio.",
        "`puede_prestar` es una sola línea: `return activos < self.max_prestamos`.",
        wrong=[
            (
                _broken(
                    2,
                    "    def __init__(self, id: int, nombre: str, max_prestamos: int = 3) -> None:",
                    "    def __init__(self, id: int, nombre: str, max_prestamos: int = 1) -> None:",
                ),
                1,
            ),
            (
                _broken(
                    2,
                    "        return activos < self.max_prestamos",
                    "        return activos <= self.max_prestamos",
                ),
                2,
            ),
            (_broken(2, "        if not nombre.strip():", '        if nombre == "":'), 3),
        ],
        level=2,
        daw=False,
    ),
    code(
        "poo10-03",
        CID,
        "**Fase 3 del proyecto: `Prestamo`.** `Libro` y `Usuario` ya están. Añade `Prestamo(libro, usuario, inicio)`, con `from datetime import date`:\n\n- Guarda el libro, el usuario, la fecha `inicio` y `fin = None`.\n- `activo` es una **propiedad**: `True` mientras `fin` sea `None`.\n- `cerrar(fecha)`: si ya está cerrado o la fecha es anterior al inicio, `ValueError` sin cambiar nada; si no, guarda `fin`.",
        _starter(3, "la clase Prestamo"),
        _program(3),
        T_PRESTAMO,
        "`activo` se calcula a partir de `fin`, así nunca se contradicen. `cerrar` valida antes de tocar `fin`, de modo que un error no deja el préstamo a medias.",
        "Pon `@property` encima de `def activo(self): return self.fin is None`. En `cerrar`, las dos comprobaciones van antes de `self.fin = fecha`.",
        wrong=[
            (
                _broken(
                    3,
                    "        self.fin: date | None = None",
                    "        self.fin: date | None = inicio",
                ),
                1,
            ),
            (
                _broken(
                    3,
                    '        if not self.activo:\n            raise ValueError("El préstamo ya está cerrado")\n',
                    "",
                ),
                2,
            ),
            (
                _broken(
                    3,
                    "        self.fin: date | None = None\n\n    @property\n    def activo(self) -> bool:\n        return self.fin is None\n",
                    "        self.fin: date | None = None\n        self.activo = True\n",
                ).replace(
                    "        self.fin = fecha\n",
                    "        self.fin = fecha\n        self.activo = False\n",
                ),
                3,
            ),
        ],
        level=2,
        daw=False,
    ),
    code(
        "poo10-04",
        CID,
        "**Fase 4 del proyecto: excepciones propias.** Añade `ErrorBiblioteca(Exception)` y cinco subclases suyas, cada una con su dato y su mensaje (pásalo a `super().__init__`):\n\n| Clase | Dato | Mensaje |\n|---|---|---|\n| `LibroNoEncontrado(isbn)` | `isbn` | `No existe el libro con ISBN 978-9` |\n| `UsuarioNoEncontrado(id)` | `id` | `No existe el usuario 7` |\n| `LibroNoDisponible(titulo)` | `titulo` | `«Dune» está prestado` |\n| `PrestamoDuplicado(titulo)` | `titulo` | `Ya tienes en préstamo «Dune»` |\n| `LimiteAlcanzado(nombre)` | `nombre` | `Ana ha llegado a su límite de préstamos` |",
        _starter(4, "ErrorBiblioteca y sus subclases"),
        _program(4),
        T_ERRORES,
        "Con una base común, quien use la biblioteca puede capturar un error concreto o todos con `except ErrorBiblioteca`. Cada excepción guarda el dato que falló, además del mensaje.",
        'Cada subclase: `def __init__(self, isbn): super().__init__(f"No existe el libro con ISBN {isbn}"); self.isbn = isbn`.',
        wrong=[
            (
                _broken(
                    4,
                    "class LimiteAlcanzado(ErrorBiblioteca):",
                    "class LimiteAlcanzado(Exception):",
                ),
                1,
            ),
            (
                _broken(
                    4,
                    '        super().__init__(f"No existe el usuario {id}")',
                    '        super().__init__(f"Usuario {id} no encontrado")',
                ),
                2,
            ),
            (
                _broken(
                    4,
                    '        super().__init__(f"«{titulo}» está prestado")',
                    '        super().__init__(f"{titulo} está prestado")',
                ),
                3,
            ),
        ],
        level=2,
        daw=False,
    ),
    code(
        "poo10-05",
        CID,
        "**Fase 5 del proyecto: registro y catálogo.** Las piezas anteriores ya están. Crea `Biblioteca(nombre)`, que guarda los libros por ISBN y los usuarios por id en diccionarios, y una lista vacía de préstamos:\n\n- `registrar_libro(libro)` y `registrar_usuario(usuario)`: un ISBN o un id ya registrado da `ValueError`.\n- `catalogo(solo_disponibles=False)`: la lista de libros **ordenada por título**; con `solo_disponibles=True`, sin los prestados.",
        _starter(5, "la clase Biblioteca con el registro y el catálogo"),
        _program(5),
        T_REGISTRO,
        "La biblioteca agrega libros y usuarios creados fuera. Guardarlos en diccionarios por su ISBN o id hace que encontrarlos y detectar repetidos sea inmediato.",
        "Ordena con `sorted(libros, key=lambda l: l.titulo)`.",
        wrong=[
            (
                _broken(
                    5,
                    "        self._libros[libro.isbn] = libro",
                    "        self._libros[libro.titulo] = libro",
                ),
                2,
            ),
            (
                _broken(
                    5,
                    '        if usuario.id in self._usuarios:\n            raise ValueError(f"Ya hay un usuario con id {usuario.id}")\n',
                    "",
                ),
                2,
            ),
            (
                _broken(
                    5,
                    "        return sorted(libros, key=lambda l: l.titulo)",
                    "        return libros",
                ),
                3,
            ),
        ],
        level=2,
        daw=False,
    ),
    code(
        "poo10-06",
        CID,
        "**Fase 6 del proyecto (ejercicio principal): préstamos.** Completa la `Biblioteca` de la fase 5 con:\n\n- `prestamos_activos(usuario_id=None)`: los préstamos activos, todos o solo los de ese usuario.\n- `prestar(isbn, usuario_id, fecha)`: crea, guarda y devuelve el `Prestamo` y marca el libro como no disponible. Errores, en este orden: `LibroNoEncontrado`, `UsuarioNoEncontrado`, `PrestamoDuplicado` (ya lo tiene ese usuario), `LibroNoDisponible` (lo tiene otra persona) y `LimiteAlcanzado`.\n- `devolver(isbn, fecha)`: cierra el préstamo activo de ese libro, lo vuelve a poner disponible y devuelve el préstamo. Si no está prestado, `ErrorBiblioteca`.\n\nNingún error puede dejar el estado a medias.",
        _starter(6, "añade a Biblioteca prestamos_activos, prestar y devolver"),
        _program(6),
        T_BIBLIOTECA,
        "`prestar` comprueba todas las reglas antes de cambiar nada: si una falla, ni se crea el préstamo ni cambia el libro. `devolver` deja que `Prestamo.cerrar` valide la fecha antes de devolver el libro a la estantería. Cada caso de error tiene su excepción, que quien use la biblioteca puede capturar por separado.",
        "Escribe dos métodos de ayuda, `_libro(isbn)` y `_usuario(id)`, que lanzan `LibroNoEncontrado` y `UsuarioNoEncontrado`. En `devolver`, cierra el préstamo **antes** de poner `disponible = True`.",
        wrong=[
            (
                _broken(
                    6,
                    "        libro.disponible = False\n        self._prestamos.append(prestamo)",
                    "        self._prestamos.append(prestamo)",
                ),
                1,
            ),
            (
                _broken(
                    6,
                    "        if isbn not in self._libros:\n            raise LibroNoEncontrado(isbn)\n        return self._libros[isbn]",
                    "        return self._libros[isbn]",
                ),
                2,
            ),
            (
                _broken(
                    6,
                    "        if any(p.libro == libro for p in activos):\n            raise PrestamoDuplicado(libro.titulo)\n",
                    "",
                ),
                3,
            ),
            (
                _broken(
                    6,
                    "        if not libro.disponible:\n            raise LibroNoDisponible(libro.titulo)\n        if not usuario.puede_prestar(len(activos)):\n            raise LimiteAlcanzado(usuario.nombre)\n        prestamo = Prestamo(libro, usuario, fecha)\n        libro.disponible = False\n",
                    "        if not libro.disponible:\n            raise LibroNoDisponible(libro.titulo)\n        libro.disponible = False\n        if not usuario.puede_prestar(len(activos)):\n            raise LimiteAlcanzado(usuario.nombre)\n        prestamo = Prestamo(libro, usuario, fecha)\n",
                ),
                4,
            ),
            (
                _broken(
                    6,
                    "                prestamo.cerrar(fecha)\n                libro.disponible = True\n",
                    "                libro.disponible = True\n                prestamo.cerrar(fecha)\n",
                ),
                5,
            ),
        ],
        level=3,
        daw=False,
    ),
    # ---------- Lección «Arquitectura y diagrama de clases»
    choice(
        "poo10-07",
        CID,
        "En el proyecto, los libros se crean fuera y se registran en la biblioteca; si la biblioteca desapareciera, los libros seguirían existiendo. ¿Qué relación hay entre `Biblioteca` y `Libro`?",
        [
            ("Agregación", None),
            (
                "Composición",
                "poo-composicion.relacion-es-sintaxis",
                "En la composición el todo crea sus partes; los libros se crean fuera.",
            ),
            (
                "Herencia",
                "poo-composicion.herencia-por-tiene",
                "Una biblioteca no «es un» libro: lo guarda.",
            ),
            (
                "Ninguna: no están relacionadas",
                None,
                "La biblioteca guarda los libros en un atributo: sí hay relación.",
            ),
        ],
        0,
        "Las partes existen por su cuenta y el todo solo las agrupa: es una agregación. Los préstamos, en cambio, los crea la biblioteca (composición).",
        level=1,
        daw=False,
        bank=True,
        qtype="diseno",
    ),
    choice(
        "poo10-08",
        CID,
        "¿Por qué `Prestamo` es una clase propia en vez de guardar en cada libro el nombre de quien lo tiene?",
        [
            (
                "Porque un préstamo tiene sus propios datos y reglas (fechas, si sigue activo, cerrar) y relaciona un libro con un usuario",
                None,
            ),
            (
                "Porque Python obliga a tener al menos cuatro clases en un programa",
                None,
                "Python no obliga a ningún número de clases: es una decisión de diseño.",
            ),
            (
                "Para que el programa vaya más rápido",
                None,
                "No cambia la velocidad: organiza los datos y las reglas.",
            ),
            (
                "Porque así `Libro` puede heredar de `Prestamo`",
                "poo-composicion.herencia-por-tiene",
                "Un libro no «es un» préstamo; el préstamo apunta al libro.",
            ),
        ],
        0,
        "Si el libro guardara quién lo tiene, se perderían las fechas y el historial, y el libro tendría una responsabilidad que no es suya.",
        level=1,
        daw=False,
        bank=True,
        qtype="teoria",
    ),
    choice(
        "poo10-09",
        CID,
        "¿Quién debería crear los objetos `Prestamo`?",
        [
            ("La `Biblioteca`, en su método `prestar`, después de comprobar las reglas", None),
            (
                "El programa principal, que luego se los pasa a la biblioteca",
                None,
                "Así cualquiera podría crear préstamos sin pasar por las comprobaciones de la biblioteca.",
            ),
            (
                "El `Libro`, al crearse",
                None,
                "Un libro recién registrado no está prestado a nadie.",
            ),
            (
                "El `Usuario`, en `puede_prestar`",
                None,
                "`puede_prestar` solo responde sí o no; no sabe si el libro está disponible.",
            ),
        ],
        0,
        "La biblioteca compone los préstamos: los crea ella cuando todo está en regla, así ningún préstamo existe sin haber pasado por sus comprobaciones.",
        level=2,
        daw=False,
        bank=True,
        qtype="diseno",
    ),
    # ---------- Lección «Libro y Usuario»
    output(
        "poo10-10",
        CID,
        """
        class Libro:
            def __init__(self, isbn, titulo):
                self.isbn = isbn
                self.titulo = titulo

            def __eq__(self, otro):
                if not isinstance(otro, Libro):
                    return NotImplemented
                return self.isbn == otro.isbn

        a = Libro("978-1", "Dune")
        b = Libro("978-1", "Duna")
        print(a == b, a is b, a in [Libro("978-2", "Dune")])
        """,
        "True False False",
        "`==` compara el ISBN, que coincide. Pero son dos objetos (`is` da `False`), y `in` también usa `__eq__`: en la lista solo hay un libro con otro ISBN.",
        traps={"False False False": "poo-metodos-especiales.eq-identidad", "True False True": None},
        level=2,
        daw=False,
    ),
    choice(
        "poo10-11",
        CID,
        'Con el `Libro` del proyecto, ¿qué devuelve `str(Libro("978-1", "Dune", "Frank Herbert"))`?',
        [
            ("`Dune (Frank Herbert) [disponible]`", None),
            (
                "`Libro('978-1', 'Dune', 'Frank Herbert')`",
                "poo-metodos-especiales.lista-usa-str",
                "Ese sería el estilo de un `__repr__`; el proyecto define `__str__` para el usuario.",
            ),
            (
                "`Dune (Frank Herbert) [prestado]`",
                None,
                "Un libro nuevo empieza con `disponible = True`.",
            ),
            (
                "`<__main__.Libro object at …>`",
                "poo-metodos-especiales.nombre-especial-mal",
                "La clase define `__str__`, así que `str()` lo usa.",
            ),
        ],
        0,
        "`__str__` junta título, autor y el estado, que en un libro recién creado es «disponible».",
        code_options=True,
        level=1,
        daw=False,
        bank=True,
        qtype="codigo",
    ),
    choice(
        "poo10-12",
        CID,
        "¿Qué muestra este programa?",
        [
            ("True False False", None),
            (
                "True True False",
                None,
                "Con 2 préstamos y un máximo de 2, `2 < 2` es `False`.",
            ),
            (
                "False False False",
                None,
                "Con 1 préstamo y un máximo de 2 todavía puede: `1 < 2`.",
            ),
            (
                "True False True",
                None,
                "Con 3 préstamos tampoco puede: `3 < 2` es `False`.",
            ),
        ],
        0,
        "`puede_prestar` compara con `<`: con 1 puede, con 2 (su máximo) ya no, y con 3 tampoco.",
        code="""
        class Usuario:
            def __init__(self, nombre, max_prestamos=3):
                self.nombre = nombre
                self.max_prestamos = max_prestamos

            def puede_prestar(self, activos):
                return activos < self.max_prestamos

        eva = Usuario("Eva", max_prestamos=2)
        print(eva.puede_prestar(1), eva.puede_prestar(2), eva.puede_prestar(3))
        """,
        level=2,
        daw=False,
        bank=True,
        qtype="prediccion",
    ),
    # ---------- Lección «Prestamo: fechas y estado»
    output(
        "poo10-13",
        CID,
        """
        from datetime import date

        class Prestamo:
            def __init__(self, inicio):
                self.inicio = inicio
                self.fin = None

            @property
            def activo(self):
                return self.fin is None

        p = Prestamo(date(2026, 3, 1))
        antes = p.activo
        p.fin = date(2026, 3, 15)
        print(antes, p.activo, (p.fin - p.inicio).days)
        """,
        "True False 14",
        "`activo` se calcula cada vez que se consulta: antes de poner `fin` es `True` y después `False`. Restar dos fechas da un intervalo cuyos `.days` son 14.",
        traps={"True True 14": f"{CID}.dato-duplicado", "True False 15": None},
        level=2,
        daw=False,
    ),
    choice(
        "poo10-14",
        CID,
        "En `Prestamo`, ¿qué ventaja tiene que `activo` sea una propiedad (`@property` que devuelve `self.fin is None`) en vez de un atributo que se pone a `False` al cerrar?",
        [
            ("Que no puede contradecirse con `fin`: siempre se calcula a partir de él", None),
            (
                "Que se puede asignar con `p.activo = False`",
                "poo-encapsulacion.sin-setter",
                "Sin setter, una propiedad no se puede asignar; y no hace falta, porque se calcula.",
            ),
            (
                "Que ocupa menos memoria y por eso va más rápido",
                None,
                "La diferencia de memoria es despreciable; la ventaja es que el dato no se duplica.",
            ),
            (
                "Ninguna: es lo mismo escrito de otra forma",
                f"{CID}.dato-duplicado",
                "Con un atributo aparte, alguien puede cambiar `fin` y olvidar `activo`, y los dos se contradicen.",
            ),
        ],
        0,
        "Un dato que se puede calcular a partir de otro no se guarda dos veces. Así nunca hay un préstamo «activo» con fecha de devolución.",
        level=2,
        daw=False,
        bank=True,
        qtype="codigo",
    ),
    choice(
        "poo10-15",
        CID,
        "Este `cerrar` tiene un fallo. ¿Cuál?",
        [
            (
                "Guarda `fin` antes de validar: con una fecha anterior al inicio lanza el error, pero el préstamo ya queda cerrado",
                None,
            ),
            (
                "Falta `return True` al final",
                None,
                "`cerrar` no necesita devolver nada; el fallo está en el orden de las líneas.",
            ),
            (
                "Las fechas no se pueden comparar con `<`",
                None,
                "Los objetos `date` sí se comparan con `<`.",
            ),
            (
                "Debería lanzar `TypeError` en vez de `ValueError`",
                None,
                "El tipo es correcto: es una fecha; lo que falla es su valor, y para eso es `ValueError`.",
            ),
        ],
        0,
        "Primero se comprueba y después se cambia. Si no, un error deja el objeto a medias: el préstamo aparece cerrado con una fecha imposible.",
        code="""
        def cerrar(self, fecha):
            self.fin = fecha
            if fecha < self.inicio:
                raise ValueError("La devolución no puede ser anterior al préstamo")
        """,
        level=2,
        daw=False,
        bank=True,
        qtype="error",
    ),
    # ---------- Lección «Biblioteca y excepciones propias»
    output(
        "poo10-16",
        CID,
        """
        class ErrorBiblioteca(Exception):
            pass

        class LibroNoDisponible(ErrorBiblioteca):
            pass

        def prestar(disponible):
            if not disponible:
                raise LibroNoDisponible("Dune está prestado")
            return "prestado"

        for d in (True, False):
            try:
                print(prestar(d))
            except ErrorBiblioteca as error:
                print("Error:", error)
        """,
        "prestado\nError: Dune está prestado",
        "`except ErrorBiblioteca` captura también sus subclases, como `LibroNoDisponible`. El mensaje es el que se pasó al lanzarla.",
        traps={
            "prestado": f"{CID}.excepcion-sin-jerarquia",
            "prestado\nError: LibroNoDisponible": None,
        },
        level=2,
        daw=False,
    ),
    choice(
        "poo10-17",
        CID,
        "¿Para qué sirve que todas las excepciones del proyecto hereden de `ErrorBiblioteca`?",
        [
            (
                "Para poder capturar cualquier error de la biblioteca con un solo `except ErrorBiblioteca`, o uno concreto si hace falta",
                None,
            ),
            (
                "Para que Python no muestre el mensaje de error",
                None,
                "Heredar no cambia el mensaje: se sigue viendo si no se captura.",
            ),
            (
                "Porque una excepción propia no puede heredar directamente de `Exception`",
                None,
                "Sí puede; `ErrorBiblioteca` hereda directamente de `Exception`.",
            ),
            (
                "Para que todas tengan el mismo mensaje",
                None,
                "Cada subclase tiene su mensaje y su dato; lo que comparten es la base.",
            ),
        ],
        0,
        "Es el mismo polimorfismo de la Unidad 6 aplicado a los errores: quien usa la biblioteca decide si trata cada caso por separado o todos a la vez.",
        level=2,
        daw=False,
        bank=True,
        qtype="teoria",
    ),
    choice(
        "poo10-18",
        CID,
        "¿Qué muestra este programa?",
        [
            ("general", None),
            (
                "concreto",
                f"{CID}.except-en-mal-orden",
                "Python usa el primer `except` que encaja, y `ErrorBiblioteca` ya encaja con la subclase.",
            ),
            (
                "general concreto",
                None,
                "Solo se ejecuta un `except`: el primero que encaja.",
            ),
            (
                "LibroNoEncontrado",
                None,
                "Se captura la excepción y se imprime el texto del bloque `except`, no su nombre.",
            ),
        ],
        0,
        "El `except` general va primero y encaja con cualquier subclase, así que el concreto nunca se usa. Los concretos deben ir antes.",
        code="""
        class ErrorBiblioteca(Exception):
            pass

        class LibroNoEncontrado(ErrorBiblioteca):
            pass

        try:
            raise LibroNoEncontrado("978-9")
        except ErrorBiblioteca:
            print("general")
        except LibroNoEncontrado:
            print("concreto")
        """,
        level=3,
        daw=False,
        bank=True,
        qtype="prediccion",
    ),
    # ---------- Lección «Pruebas, retos y rúbrica»
    choice(
        "poo10-19",
        CID,
        "¿Qué prueba comprueba bien que un libro **no se puede prestar dos veces**?",
        [
            (
                "Prestarlo a Ana, intentar prestarlo a Luis comprobando que lanza `LibroNoDisponible` y que solo hay un préstamo activo",
                None,
            ),
            (
                "Prestarlo a Ana y comprobar que `prestar` devuelve un `Prestamo`",
                None,
                "Solo prueba el caso normal: no intenta el segundo préstamo.",
            ),
            (
                "Prestarlo dos veces seguidas sin `try` y ver si el programa termina",
                None,
                "Si lanza el error, el programa se para y la prueba no dice qué excepción fue ni comprueba el estado.",
            ),
            (
                "Comprobar que `LibroNoDisponible` hereda de `ErrorBiblioteca`",
                None,
                "Eso prueba la jerarquía, no la regla de los préstamos.",
            ),
        ],
        0,
        "Una buena prueba de error comprueba dos cosas: que se lanza la excepción correcta y que el estado no ha cambiado.",
        level=3,
        daw=False,
        bank=True,
        qtype="solucion",
    ),
    choice(
        "poo10-20",
        CID,
        "Este `prestar` marca el libro como prestado antes de comprobar el límite del usuario. ¿Qué pasa si el usuario ya está en su límite?",
        [
            (
                "Lanza `LimiteAlcanzado`, pero el libro queda como no disponible sin ningún préstamo: estado a medias",
                None,
            ),
            (
                "Nada: el error impide que se cambie nada",
                f"{CID}.estado-a-medias",
                "Lo que ya se ejecutó antes del `raise` no se deshace: `disponible` ya es `False`.",
            ),
            (
                "Se crea el préstamo y después se lanza el error",
                None,
                "El `raise` está antes de crear el préstamo: el préstamo no llega a existir.",
            ),
            (
                "Python da `SyntaxError` por el orden de las líneas",
                None,
                "El código es válido; el fallo es de lógica.",
            ),
        ],
        0,
        "Primero todas las comprobaciones y después los cambios. Si no, nadie podrá prestar ese libro aunque nunca se prestó.",
        code="""
        def prestar(self, isbn, usuario_id, fecha):
            libro = self._libro(isbn)
            usuario = self._usuario(usuario_id)
            activos = self.prestamos_activos(usuario_id)
            libro.disponible = False
            if not usuario.puede_prestar(len(activos)):
                raise LimiteAlcanzado(usuario.nombre)
            prestamo = Prestamo(libro, usuario, fecha)
            self._prestamos.append(prestamo)
            return prestamo
        """,
        level=3,
        daw=False,
        bank=True,
        qtype="error",
    ),
    choice(
        "poo10-21",
        CID,
        "¿Qué es la **integración** en un proyecto construido por fases?",
        [
            (
                "Juntar las piezas que ya funcionan por separado y comprobar que funcionan juntas",
                None,
            ),
            (
                "Escribir todo el programa de una vez al final",
                None,
                "Al revés: las piezas ya existen y probadas; la integración las une.",
            ),
            (
                "Borrar los tests de las fases anteriores",
                None,
                "Los tests de cada fase se mantienen: siguen protegiendo cada pieza.",
            ),
            (
                "Convertir todas las clases en una sola",
                None,
                "Las clases siguen separadas; la integración las hace colaborar.",
            ),
        ],
        0,
        "En la fase 6, la biblioteca usa libros, usuarios, préstamos y excepciones a la vez. Si algo falla, ya sabes que cada pieza funcionaba sola.",
        level=1,
        daw=False,
        bank=True,
        qtype="teoria",
    ),
    # ---------- Autoevaluación
    choice(
        "poo10-22",
        CID,
        "Quieres saber si `devolver` lanza `ErrorBiblioteca` con un libro que no está prestado. ¿Qué prueba es correcta?",
        [
            (
                '`try: bib.devolver("1", hoy)` / `except ErrorBiblioteca: pass` / `else: raise AssertionError("Debía fallar")`',
                None,
            ),
            (
                '`assert bib.devolver("1", hoy) == ErrorBiblioteca`',
                None,
                "Una excepción no se devuelve: se lanza, y el `assert` ni llega a comparar.",
            ),
            (
                '`try: bib.devolver("1", hoy)` / `except: pass`',
                None,
                "Pasa aunque no se lance nada y aunque el error sea otro: no comprueba nada.",
            ),
            (
                "`assert isinstance(ErrorBiblioteca, Exception)`",
                None,
                "Comprueba la jerarquía (y mal: es una clase, no una instancia), no lo que hace `devolver`.",
            ),
        ],
        0,
        "El `else` del `try` solo se ejecuta si no hubo excepción: es justo el caso en que la prueba debe fallar.",
        code_options=True,
        level=2,
        daw=False,
        bank=True,
        qtype="solucion",
    ),
    output(
        "poo10-23",
        CID,
        """
        libros = {"1": {"titulo": "Dune", "disponible": True}}
        prestamos = []

        def prestar(isbn, quien, limite_de_quien):
            libro = libros[isbn]
            if not libro["disponible"]:
                return "no disponible"
            if limite_de_quien == 0:
                return "límite"
            libro["disponible"] = False
            prestamos.append((isbn, quien))
            return "ok"

        print(prestar("1", "Ana", 0), prestar("1", "Luis", 3), prestar("1", "Eva", 3))
        """,
        "límite ok no disponible",
        "Como las comprobaciones van antes de los cambios, el intento de Ana no deja el libro bloqueado: Luis lo consigue y Eva ya lo encuentra prestado.",
        traps={
            "límite no disponible no disponible": f"{CID}.estado-a-medias",
            "ok no disponible no disponible": None,
        },
        level=2,
        daw=False,
    ),
    # ---------- Banco de preguntas de la unidad (cuestionario)
    choice(
        "poo10-24",
        CID,
        "En la `Biblioteca`, ¿qué hace `prestamos_activos(7)`?",
        [
            ("Devuelve los préstamos no cerrados del usuario con id 7", None),
            (
                "Devuelve cuántos préstamos ha tenido el usuario 7 en total",
                None,
                "Devuelve una lista, y solo de los activos: los cerrados no cuentan.",
            ),
            (
                "Presta 7 libros",
                None,
                "El 7 es el id del usuario, no una cantidad.",
            ),
            (
                "Devuelve todos los préstamos activos de la biblioteca",
                None,
                "Eso es `prestamos_activos()` sin argumento; con el id filtra por usuario.",
            ),
        ],
        0,
        "Filtra por `p.activo` y, si se le pasa un id, por `p.usuario.id`. `prestar` lo usa con `len(...)` para comprobar el límite del usuario.",
        code="""
        def prestamos_activos(self, usuario_id=None):
            return [
                p
                for p in self._prestamos
                if p.activo and (usuario_id is None or p.usuario.id == usuario_id)
            ]
        """,
        level=3,
        daw=False,
        bank=True,
        qtype="codigo",
    ),
    choice(
        "poo10-25",
        CID,
        "¿Qué muestra este programa?",
        [
            ("['Dune', 'Fundación', 'Neuromante']", None),
            (
                "['Neuromante', 'Dune', 'Fundación']",
                None,
                "`sorted` ordena; ese es el orden en que se registraron.",
            ),
            (
                "['Fundación', 'Neuromante', 'Dune']",
                None,
                "Se ordena por título, no por ISBN.",
            ),
            (
                "['Neuromante', 'Fundación', 'Dune']",
                None,
                "Es orden alfabético ascendente: de la A a la Z.",
            ),
        ],
        0,
        "`key=lambda l: l[1]` ordena por el título, que es el segundo elemento de cada tupla.",
        code="""
        registrados = [("3", "Neuromante"), ("1", "Dune"), ("2", "Fundación")]
        print([titulo for _, titulo in sorted(registrados, key=lambda l: l[1])])
        """,
        level=1,
        daw=False,
        bank=True,
        qtype="prediccion",
    ),
]

# Errores típicos (slug, etiqueta, por qué, qué pensar, cómo evitarlo)
ERRORS = [
    (
        "estado-a-medias",
        "Cambia el estado antes de comprobar todas las reglas",
        "Si una comprobación falla después de un cambio, la excepción no deshace lo hecho: un libro puede quedar «prestado» sin préstamo.",
        "¿Qué pasa con los datos si la siguiente comprobación falla?",
        "Haz todas las comprobaciones primero y los cambios al final.",
    ),
    (
        "valida-tarde",
        "No valida los datos al crear el objeto",
        "Un libro sin ISBN o un usuario sin nombre se cuelan en el programa y fallan mucho después, lejos de donde se crearon.",
        "¿Qué datos hacen que este objeto no tenga sentido?",
        "Valida en `__init__` y lanza `ValueError` antes de guardar nada; usa `strip()` para los textos de solo espacios.",
    ),
    (
        "dato-duplicado",
        "Guarda un dato que se puede calcular a partir de otro",
        "Dos copias del mismo dato (`activo` y `fin`) se contradicen en cuanto alguien cambia una y no la otra.",
        "¿Puedo calcular este dato a partir de los que ya tengo?",
        "Calcúlalo con una propiedad (`@property`) en vez de guardarlo aparte.",
    ),
    (
        "excepcion-sin-jerarquia",
        "Crea excepciones propias sin una base común",
        "Sin una base como `ErrorBiblioteca`, quien usa la biblioteca no puede capturar todos sus errores a la vez sin capturar también errores de Python que no tienen nada que ver.",
        "¿De qué clase heredan mis excepciones?",
        "Crea una excepción base del proyecto y haz que las demás hereden de ella.",
    ),
    (
        "excepcion-generica",
        "Deja que salte un error genérico de Python en vez de la excepción del proyecto",
        "Un `KeyError` al buscar un ISBN no dice qué pasó y obliga a quien usa la clase a conocer cómo guarda los datos por dentro.",
        "¿Qué error verá quien llame a este método si el dato no existe?",
        "Comprueba antes y lanza tu excepción (`LibroNoEncontrado(isbn)`) con un mensaje claro.",
    ),
    (
        "except-en-mal-orden",
        "Pone un `except` general antes de uno concreto",
        "Python usa el primer `except` que encaja; si el general va primero, el concreto nunca se ejecuta.",
        "¿Alguno de los `except` de arriba captura ya esta excepción?",
        "Ordena los `except` de lo más concreto a lo más general.",
    ),
]

# Las preguntas del banco de esta unidad ya nacen con su tipo y su nivel: no hay que etiquetar ninguna antigua
BANK_TAGS: dict = {}

# Comprobación interna: el reparto de la rúbrica suma 100 (la valida también build_learning.py)
assert sum(r["points"] for r in UNIT["rubric"]) == 100
_ = dedent  # dedent se importa para quien quiera escribir piezas nuevas con sangría
