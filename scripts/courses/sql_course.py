# ruff: noqa: E501
# (contenido didáctico: los textos largos van en una sola línea para poder leerlos y editarlos)
"""Curso de Bases de datos (módulo 0484 de DAW) para la app Android (ADR-0016, ADR-0019).

Sigue las UD1-UD3 del temario del centro; lo que va más allá está en el bloque de ampliación.

Las preguntas de código se ejecutan en SQLite con las claves ajenas activadas y su salida se compara con
la esperada. El SQL usado es estándar: funciona igual en MySQL salvo lo que la teoría avisa.

Formato de salida: una fila por línea, columnas separadas por « | », NULL como «NULL»,
«(sin filas)» si no hay resultado y «Error» si alguna sentencia falla.
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from course_builder import Block, Lesson, Q, main  # noqa: E402

# ---------------------------------------------------------------- ejecución


def run_sql(script: str) -> str:
    conn = sqlite3.connect(
        ":memory:", isolation_level=None
    )  # BEGIN/COMMIT explícitos, como en una consola
    conn.execute("PRAGMA foreign_keys = ON")
    rows: list[tuple] = []
    try:
        for statement in (s.strip() for s in script.split(";")):
            if statement and not all(
                line.strip().startswith("--") for line in statement.splitlines() if line.strip()
            ):
                rows = conn.execute(statement).fetchall()
    except sqlite3.Error:
        return "Error"
    finally:
        conn.close()
    if not rows:
        return "(sin filas)"
    return "\n".join(" | ".join("NULL" if v is None else str(v) for v in row) for row in rows)


def check_example(script: str) -> None:
    assert run_sql(script) != "Error", f"el ejemplo falla:\n{script}"


# ---------------------------------------------------------------- tablas de ejemplo


class T:
    def __init__(self, name: str, columns: list[tuple[str, str]], rows: list[tuple]):
        self.name, self.columns, self.rows = name, columns, rows

    def setup(self) -> str:
        cols = ", ".join(f"{n} {t}" for n, t in self.columns)
        values = ", ".join("(" + ", ".join(sql_value(v) for v in row) + ")" for row in self.rows)
        return f"CREATE TABLE {self.name} ({cols});\nINSERT INTO {self.name} VALUES {values};\n"

    def render(self) -> str:
        """La tabla como comentario SQL, para que el alumno vea los datos en el móvil."""
        header = [n for n, _ in self.columns]
        cells = [["NULL" if v is None else str(v) for v in row] for row in self.rows]
        widths = [max(len(r[i]) for r in [header, *cells]) for i in range(len(header))]

        def line(r: list[str]) -> str:
            return "-- " + " | ".join(c.ljust(w) for c, w in zip(r, widths, strict=True)).rstrip()

        return "\n".join([f"-- {self.name}", line(header), *(line(r) for r in cells)])


def sql_value(v) -> str:
    if v is None:
        return "NULL"
    return str(v) if isinstance(v, (int, float)) else "'" + str(v).replace("'", "''") + "'"


ALUMNOS = T(
    "alumnos",
    [("id", "INTEGER PRIMARY KEY"), ("nombre", "TEXT"), ("ciclo", "TEXT"), ("nota", "INTEGER")],
    [
        (1, "Ana", "DAW", 8),
        (2, "Luis", "DAM", 5),
        (3, "Eva", "DAW", None),
        (4, "Juan", "ASIR", 7),
        (5, "Sara", "DAM", 9),
    ],
)
PRODUCTOS = T(
    "productos",
    [
        ("id", "INTEGER PRIMARY KEY"),
        ("nombre", "TEXT"),
        ("precio", "INTEGER"),
        ("stock", "INTEGER"),
    ],
    [(1, "Teclado", 25, 10), (2, "Ratón", 15, 0), (3, "Monitor", 180, 4), (4, "Cable", 5, 50)],
)
CLIENTES = T(
    "clientes",
    [("id", "INTEGER PRIMARY KEY"), ("nombre", "TEXT"), ("ciudad", "TEXT")],
    [(1, "Ana", "Madrid"), (2, "Luis", "Leganés"), (3, "Eva", "Valladolid")],
)
PEDIDOS = T(
    "pedidos",
    [
        ("id", "INTEGER PRIMARY KEY"),
        ("cliente_id", "INTEGER REFERENCES clientes(id)"),
        ("total", "INTEGER"),
    ],
    [(1, 1, 30), (2, 1, 20), (3, 2, 50)],
)


def cq(
    id: str, q: str, tables: list[T], query: str, expect: str, wrong: list[str], explain: str
) -> Q:
    """Pregunta de código sobre tablas de ejemplo: el alumno ve los datos y la consulta."""
    query = query.strip()
    shown = "\n\n".join(t.render() for t in tables) + ("\n\n" if tables else "") + query
    run = "".join(t.setup() for t in tables) + query
    return Q(id=id, q=q, code=shown, run=run, expect=expect, wrong=wrong, explain=explain)


def sq(id: str, q: str, script: str, expect: str, wrong: list[str], explain: str) -> Q:
    """Pregunta sobre un script completo (DDL, DML o transacciones): se ve y se ejecuta tal cual."""
    script = script.strip()
    return Q(id=id, q=q, code=script, run=script, expect=expect, wrong=wrong, explain=explain)


def tq(id: str, q: str, options: list[str], answer: int, explain: str) -> Q:
    """Pregunta teórica."""
    return Q(id=id, q=q, options=options, answer=answer, explain=explain)


QUE = "¿Qué devuelve esta consulta?"
SCRIPT = "¿Qué devuelve la última sentencia de este script?"

MYSQL = ("MySQL 8.0 Reference Manual", "https://dev.mysql.com/doc/refman/8.0/en/")
SQLITE = ("SQLite — SQL As Understood By SQLite", "https://www.sqlite.org/lang.html")
PG = (
    "PostgreSQL Tutorial (documentación oficial)",
    "https://www.postgresql.org/docs/current/tutorial-sql.html",
)

# ---------------------------------------------------------------- bloque 1: consultas

L_SELECT = Lesson(
    slug="sql-select",
    title="SELECT: consultar datos",
    theory="""
SQL es un lenguaje **declarativo**: describes *qué* datos quieres y el sistema gestor (SGBD) decide *cómo* obtenerlos. La sentencia básica es `SELECT columnas FROM tabla`.

- `SELECT *` devuelve todas las columnas. En programas reales es mejor nombrarlas: la consulta no se rompe si la tabla cambia.
- Puedes calcular expresiones y ponerles un **alias** con `AS`: `SELECT nombre, precio * stock AS valor FROM productos`.
- `DISTINCT` elimina las **filas** repetidas del resultado. Con varias columnas, compara la combinación completa.

**Ordenar y limitar:**
- `ORDER BY columna` ordena de menor a mayor (`ASC`, por defecto); `DESC` invierte el orden. Con varias columnas, la segunda solo desempata.
- `LIMIT n` devuelve solo las n primeras filas (MySQL, SQLite y PostgreSQL). En Oracle se escribe `FETCH FIRST n ROWS ONLY`.

El SGBD evalúa las cláusulas en un **orden lógico** distinto al escrito: `FROM` → `WHERE` → `GROUP BY` → `HAVING` → `SELECT` → `ORDER BY` → `LIMIT`. Por eso un alias del `SELECT` se puede usar en `ORDER BY`, pero no en `WHERE`.

En esta app los ejemplos se ejecutan en **SQLite**. Usan SQL estándar, que funciona igual en MySQL; cuando haya diferencias, la teoría lo avisa.
""",
    example="""
CREATE TABLE productos (id INTEGER PRIMARY KEY, nombre TEXT, precio INTEGER, stock INTEGER);
INSERT INTO productos VALUES (1, 'Teclado', 25, 10), (2, 'Ratón', 15, 0), (3, 'Monitor', 180, 4);

SELECT nombre, precio * stock AS valor
FROM productos
ORDER BY valor DESC;
""",
    exercise="""
Con la tabla `productos(id, nombre, precio, stock)`, muestra el **nombre** y el **valor en almacén** (`precio * stock`) de cada producto.

- La columna calculada debe llamarse `valor`.
- Ordena de mayor a menor valor y muestra solo los **dos** primeros.
""",
    starter="SELECT nombre, ...\nFROM productos\n-- ORDER BY ...\n-- LIMIT ...;",
    hint="Primero FROM (de dónde), luego SELECT (qué columnas) y al final ORDER BY y LIMIT. El alias `valor` sí se puede usar en ORDER BY.",
    faq=[
        (
            "¿Importan las mayúsculas en SQL?",
            "Las palabras clave no: `select` y `SELECT` son iguales, aunque por costumbre se escriben en mayúsculas. Los **datos** pueden distinguirlas o no según la configuración de la base de datos (*collation*).",
        ),
        (
            "¿Hace falta el punto y coma?",
            "Separa sentencias. Con una sola sentencia suele ser opcional, pero en un script con varias es obligatorio. Acostúmbrate a ponerlo siempre.",
        ),
    ],
    challenge=(
        "Catálogo ordenado",
        1,
        "Muestra el nombre y el precio de todos los productos, ordenados por precio de menor a mayor y, a igual precio, por nombre alfabéticamente.",
        "SELECT nombre, precio\nFROM productos\n-- ORDER BY ...;",
        "ORDER BY admite varias columnas separadas por comas: la segunda solo se usa para desempatar.",
    ),
    questions=[
        cq(
            "sql-01",
            QUE,
            [ALUMNOS],
            "SELECT DISTINCT ciclo FROM alumnos ORDER BY ciclo;",
            "ASIR\nDAM\nDAW",
            ["DAW\nDAM\nASIR", "DAW\nDAM\nDAW\nASIR\nDAM", "ASIR\nDAM\nDAM\nDAW\nDAW"],
            "`DISTINCT` deja una fila por cada ciclo distinto (DAW, DAM y ASIR) y `ORDER BY ciclo` los ordena alfabéticamente de menor a mayor.",
        ),
        cq(
            "sql-02",
            QUE,
            [ALUMNOS],
            "SELECT nombre FROM alumnos ORDER BY nota DESC LIMIT 2;",
            "Sara\nAna",
            ["Ana\nSara", "Eva\nSara", "Luis\nAna"],
            "`DESC` ordena de mayor a menor nota (9, 8, 7, 5) y `LIMIT 2` se queda con las dos primeras: Sara y Ana. En SQLite y MySQL los NULL van al final al ordenar en descendente.",
        ),
        cq(
            "sql-03",
            QUE,
            [PRODUCTOS],
            "SELECT nombre, precio * stock AS valor\nFROM productos\nORDER BY valor DESC\nLIMIT 1;",
            "Monitor | 720",
            ["Teclado | 250", "Monitor | 180", "Cable | 250"],
            "El valor es precio × stock: Monitor 180 × 4 = 720, Teclado 250, Cable 250, Ratón 0. El alias `valor` se puede usar en ORDER BY porque este se evalúa después del SELECT.",
        ),
        tq(
            "sql-04",
            "¿En qué orden **lógico** evalúa el SGBD estas cláusulas?",
            [
                "FROM → WHERE → SELECT → ORDER BY",
                "SELECT → FROM → WHERE → ORDER BY",
                "SELECT → WHERE → FROM → ORDER BY",
                "FROM → SELECT → WHERE → ORDER BY",
            ],
            0,
            "Primero elige la tabla (`FROM`), filtra filas (`WHERE`), calcula las columnas (`SELECT`) y por último ordena (`ORDER BY`). Por eso un alias del SELECT no existe todavía dentro del WHERE.",
        ),
        tq(
            "sql-05",
            "¿Qué hace `SELECT DISTINCT ciclo, nota FROM alumnos`?",
            [
                "Elimina las filas en las que coinciden a la vez el ciclo y la nota",
                "Elimina los ciclos repetidos y se queda con la primera nota",
                "Aplica DISTINCT solo a la columna ciclo",
                "Da error: DISTINCT solo admite una columna",
            ],
            0,
            "`DISTINCT` afecta a la **fila completa** del resultado: dos filas solo se consideran repetidas si coinciden en todas las columnas seleccionadas.",
        ),
    ],
    quiz=[
        cq(
            "sql-q01",
            QUE,
            [ALUMNOS],
            "SELECT nombre AS alumno FROM alumnos ORDER BY nombre LIMIT 1;",
            "Ana",
            ["alumno", "Sara", "Juan"],
            "El alias solo cambia el nombre de la columna, no los datos. Ordenados alfabéticamente, el primero es Ana.",
        ),
        tq(
            "sql-q02",
            "¿Qué cláusula limita el número de filas del resultado en MySQL?",
            ["LIMIT", "TOP", "ROWNUM", "MAXROWS"],
            0,
            "MySQL, SQLite y PostgreSQL usan `LIMIT`. `TOP` es de SQL Server y `ROWNUM` de las versiones antiguas de Oracle.",
        ),
    ],
    sources=[MYSQL, SQLITE],
)

L_WHERE = Lesson(
    slug="sql-where",
    title="WHERE: filtrar filas",
    theory="""
`WHERE` se queda solo con las filas que cumplen una condición: `SELECT nombre FROM alumnos WHERE nota >= 5`.

**Operadores de comparación:** `=`, `<>` (distinto; `!=` también funciona), `<`, `>`, `<=`, `>=`. Los textos van entre comillas simples: `ciclo = 'DAW'`.

**Operadores lógicos:** `AND`, `OR` y `NOT`. Cuidado con la precedencia: `AND` se evalúa **antes** que `OR`. `a OR b AND c` significa `a OR (b AND c)`. Ante la duda, usa paréntesis.

**Atajos muy usados:**
- `BETWEEN 10 AND 20`: entre dos valores, **ambos incluidos**.
- `IN ('DAW', 'DAM')`: igual a alguno de la lista.
- `LIKE 'A%'`: patrones de texto. `%` equivale a cualquier secuencia de caracteres (también vacía) y `_` a exactamente uno.

**NULL** significa «valor desconocido». Cualquier comparación con NULL da *desconocido*, que no es verdadero: `nota = NULL` nunca se cumple, ni siquiera en las filas sin nota. Para eso existen `IS NULL` e `IS NOT NULL`.

Distinción de mayúsculas: en SQLite y en la configuración habitual de MySQL, `LIKE` no distingue mayúsculas en letras sin tilde.
""",
    example="""
CREATE TABLE productos (id INTEGER PRIMARY KEY, nombre TEXT, precio INTEGER, stock INTEGER);
INSERT INTO productos VALUES (1, 'Teclado', 25, 10), (2, 'Ratón', 15, 0), (3, 'Monitor', 180, 4), (4, 'Cable', 5, 50);

SELECT nombre, precio
FROM productos
WHERE stock > 0 AND precio < 100
ORDER BY precio;
""",
    exercise="""
Con la tabla `productos(id, nombre, precio, stock)`:

1. Lista los productos **con stock** que cuestan **menos de 30 €**.
2. Lista los productos cuyo nombre **empieza por M o por C**.
""",
    starter="SELECT nombre, precio\nFROM productos\nWHERE ...;",
    hint="Para el segundo apartado puedes combinar dos LIKE con OR: `nombre LIKE 'M%' OR nombre LIKE 'C%'`.",
    faq=[
        (
            "¿`<>` o `!=`?",
            "Los dos significan «distinto». `<>` es el del estándar SQL; `!=` lo aceptan MySQL, SQLite y PostgreSQL.",
        ),
        (
            "¿Por qué `nota = NULL` no devuelve nada?",
            "NULL significa «desconocido». Comparar algo con un desconocido da *desconocido*, que no es verdadero, así que la fila no pasa el filtro. Usa `IS NULL`.",
        ),
    ],
    challenge=(
        "Búsqueda por texto",
        2,
        "Muestra los alumnos cuyo nombre contiene la letra `u` y que **no** son de DAW.",
        "SELECT nombre, ciclo\nFROM alumnos\nWHERE ...;",
        "Combina `LIKE '%u%'` con `ciclo <> 'DAW'`. Si mezclas AND y OR, usa paréntesis.",
    ),
    questions=[
        cq(
            "sql-06",
            QUE,
            [ALUMNOS],
            "SELECT nombre FROM alumnos WHERE nota >= 7 AND ciclo = 'DAW';",
            "Ana",
            ["Ana\nEva", "Ana\nJuan\nSara", "(sin filas)"],
            "De DAW son Ana (8) y Eva (NULL). `NULL >= 7` da *desconocido*, no verdadero, así que Eva no pasa el filtro.",
        ),
        cq(
            "sql-07",
            QUE,
            [ALUMNOS],
            "SELECT nombre FROM alumnos WHERE nota = NULL;",
            "(sin filas)",
            ["Eva", "Error", "Ana\nLuis\nJuan\nSara"],
            "No da error, pero no devuelve nada: comparar con NULL usando `=` nunca es verdadero. Para encontrar a Eva hay que escribir `WHERE nota IS NULL`.",
        ),
        cq(
            "sql-08",
            QUE,
            [ALUMNOS],
            "SELECT nombre FROM alumnos\nWHERE ciclo = 'DAM' OR ciclo = 'DAW' AND nota > 7\nORDER BY id;",
            "Ana\nLuis\nSara",
            ["Ana\nSara", "Sara", "Ana\nLuis\nEva\nSara"],
            "`AND` va antes que `OR`: la condición es `ciclo = 'DAM' OR (ciclo = 'DAW' AND nota > 7)`. Entran todos los de DAM (Luis y Sara) y, de DAW, solo Ana.",
        ),
        cq(
            "sql-09",
            QUE,
            [PRODUCTOS],
            "SELECT nombre FROM productos\nWHERE precio BETWEEN 15 AND 25\nORDER BY precio;",
            "Ratón\nTeclado",
            ["Teclado", "Ratón", "Cable\nRatón\nTeclado"],
            "`BETWEEN` incluye los dos extremos: entran el Ratón (15) y el Teclado (25).",
        ),
        cq(
            "sql-10",
            QUE,
            [ALUMNOS],
            "SELECT nombre FROM alumnos WHERE nombre LIKE '_a%';",
            "Sara",
            ["Ana\nSara", "Ana\nJuan\nSara", "Juan\nSara"],
            "`_` es exactamente un carácter y `%` cualquier resto: el patrón pide que la **segunda** letra sea una a. Solo la cumple Sara.",
        ),
    ],
    quiz=[
        cq(
            "sql-q03",
            QUE,
            [ALUMNOS],
            "SELECT nombre FROM alumnos WHERE nota IS NULL;",
            "Eva",
            ["(sin filas)", "Luis", "Error"],
            "`IS NULL` es la forma correcta de buscar valores desconocidos.",
        ),
        cq(
            "sql-q04",
            QUE,
            [ALUMNOS],
            "SELECT nombre FROM alumnos WHERE ciclo IN ('ASIR', 'DAM') ORDER BY nombre;",
            "Juan\nLuis\nSara",
            ["Luis\nSara", "Juan", "Ana\nEva"],
            "`IN` equivale a varias igualdades unidas con OR: de ASIR o de DAM son Juan, Luis y Sara.",
        ),
    ],
    sources=[MYSQL, SQLITE],
)

# ---------------------------------------------------------------- bloque 2: agregación

L_AGG = Lesson(
    slug="sql-agregados",
    title="Funciones de agregado",
    theory="""
Las **funciones de agregado** resumen muchas filas en un solo valor:

- `COUNT(*)` cuenta filas. `COUNT(columna)` cuenta solo las filas donde esa columna **no es NULL**. `COUNT(DISTINCT columna)` cuenta valores distintos.
- `SUM`, `AVG`, `MIN` y `MAX` calculan suma, media, mínimo y máximo.

Todas, salvo `COUNT(*)`, **ignoran los NULL**. Por eso `AVG(nota)` es la media de las notas conocidas, no de todas las filas. Si quieres tratar el NULL como 0, sustitúyelo con `COALESCE(nota, 0)`.

Si ninguna fila tiene valor, `SUM`, `AVG`, `MIN` y `MAX` devuelven **NULL** (no 0); `COUNT` devuelve 0.

Admiten expresiones: `SUM(precio * stock)`. Para redondear, `ROUND(AVG(precio), 2)`.

Sin `GROUP BY`, una consulta con agregados devuelve **una sola fila**. No mezcles una columna normal con un agregado: MySQL da error y SQLite devuelve un valor de una fila cualquiera. Para eso existe `GROUP BY` (siguiente lección).
""",
    example="""
CREATE TABLE productos (id INTEGER PRIMARY KEY, nombre TEXT, precio INTEGER, stock INTEGER);
INSERT INTO productos VALUES (1, 'Teclado', 25, 10), (2, 'Ratón', 15, 0), (3, 'Monitor', 180, 4), (4, 'Cable', 5, 50);

SELECT COUNT(*) AS productos,
       SUM(stock) AS unidades,
       ROUND(AVG(precio), 2) AS precio_medio
FROM productos;
""",
    exercise="""
Con la tabla `productos(id, nombre, precio, stock)` calcula, en una sola consulta:

- cuántos productos hay **sin stock**;
- cuál es el **precio más alto** de los que sí tienen stock.

Pista: son dos consultas distintas o, si te atreves, una con dos subconsultas.
""",
    starter="SELECT COUNT(*)\nFROM productos\nWHERE ...;",
    hint="`COUNT(*)` con un `WHERE stock = 0` cuenta los agotados; `MAX(precio)` con `WHERE stock > 0`, el más caro disponible.",
    faq=[
        (
            "¿COUNT(*) o COUNT(1)?",
            "Son equivalentes en los motores modernos: cuentan filas. `COUNT(columna)` es distinto porque no cuenta los NULL de esa columna.",
        ),
        (
            "¿Por qué AVG no divide entre todas las filas?",
            "Porque ignora los NULL: calcula la media de los valores conocidos. Con `AVG(COALESCE(nota, 0))` los NULL cuentan como 0.",
        ),
    ],
    challenge=(
        "Valor del almacén",
        1,
        "Calcula el valor total del almacén: la suma de `precio * stock` de todos los productos.",
        "SELECT ...\nFROM productos;",
        "Las funciones de agregado admiten expresiones: `SUM(precio * stock)`.",
    ),
    questions=[
        cq(
            "sql-11",
            QUE,
            [ALUMNOS],
            "SELECT COUNT(*), COUNT(nota) FROM alumnos;",
            "5 | 4",
            ["5 | 5", "4 | 4", "4 | 5"],
            "`COUNT(*)` cuenta las 5 filas; `COUNT(nota)` ignora el NULL de Eva y da 4.",
        ),
        cq(
            "sql-12",
            QUE,
            [ALUMNOS],
            "SELECT AVG(nota) FROM alumnos;",
            "7.25",
            ["5.8", "7", "NULL"],
            "AVG ignora los NULL: (8 + 5 + 7 + 9) / 4 = 7,25. Si contara a Eva como 0 saldría 29 / 5 = 5,8.",
        ),
        cq(
            "sql-13",
            QUE,
            [ALUMNOS],
            "SELECT COUNT(DISTINCT ciclo) FROM alumnos;",
            "3",
            ["5", "2", "1"],
            "Hay tres ciclos distintos: DAW, DAM y ASIR.",
        ),
        cq(
            "sql-14",
            QUE,
            [PRODUCTOS],
            "SELECT MAX(precio) - MIN(precio) FROM productos;",
            "175",
            ["180", "5", "155"],
            "El más caro cuesta 180 y el más barato 5: la diferencia es 175. Se pueden operar agregados entre sí.",
        ),
        cq(
            "sql-15",
            QUE,
            [ALUMNOS],
            "SELECT SUM(nota) FROM alumnos WHERE nota IS NULL;",
            "NULL",
            ["0", "Error", "(sin filas)"],
            "Devuelve una fila con NULL: SUM ignora los NULL y, si no queda ningún valor, el resultado es NULL, no 0. Para obtener 0 se escribe `COALESCE(SUM(nota), 0)`.",
        ),
    ],
    quiz=[
        cq(
            "sql-q05",
            QUE,
            [PRODUCTOS],
            "SELECT SUM(stock) FROM productos WHERE precio > 20;",
            "14",
            ["64", "10", "2"],
            "Cuestan más de 20 el Teclado (10 unidades) y el Monitor (4): 14 unidades.",
        ),
        tq(
            "sql-q06",
            "¿Cuál de estas expresiones **no** ignora los NULL?",
            ["COUNT(*)", "COUNT(nota)", "AVG(nota)", "MAX(nota)"],
            0,
            "`COUNT(*)` cuenta filas, tengan lo que tengan. Las demás solo trabajan con valores no nulos.",
        ),
    ],
    sources=[MYSQL, SQLITE],
)

L_GROUP = Lesson(
    slug="sql-group-by",
    title="GROUP BY y HAVING",
    theory="""
`GROUP BY` reparte las filas en **grupos** con el mismo valor y calcula los agregados de cada grupo:

`SELECT ciclo, COUNT(*) FROM alumnos GROUP BY ciclo` devuelve una fila por ciclo con su número de alumnos.

**La regla de oro:** cada columna del SELECT debe estar en el `GROUP BY` o dentro de una función de agregado. MySQL (con su modo por defecto `ONLY_FULL_GROUP_BY`), PostgreSQL y Oracle dan error si no.

**WHERE frente a HAVING:**
- `WHERE` filtra **filas** antes de agrupar. No admite agregados.
- `HAVING` filtra **grupos** después de agrupar. Es donde van condiciones como `COUNT(*) > 1`.

Orden de escritura: `SELECT … FROM … WHERE … GROUP BY … HAVING … ORDER BY …`.

Todos los NULL de la columna agrupada forman **un único grupo**.
""",
    example="""
CREATE TABLE alumnos (id INTEGER PRIMARY KEY, nombre TEXT, ciclo TEXT, nota INTEGER);
INSERT INTO alumnos VALUES (1, 'Ana', 'DAW', 8), (2, 'Luis', 'DAM', 5), (3, 'Eva', 'DAW', NULL), (4, 'Juan', 'ASIR', 7), (5, 'Sara', 'DAM', 9);

SELECT ciclo, COUNT(*) AS alumnos, AVG(nota) AS media
FROM alumnos
GROUP BY ciclo
HAVING COUNT(*) > 1
ORDER BY media DESC;
""",
    exercise="""
Con la tabla `alumnos(id, nombre, ciclo, nota)`:

1. Cuenta cuántos alumnos hay en cada ciclo.
2. Muestra solo los ciclos cuya **nota media** es de 7 o más.
""",
    starter="SELECT ciclo, COUNT(*)\nFROM alumnos\nGROUP BY ...\n-- HAVING ...;",
    hint="La condición sobre la media es un filtro de grupos: va en HAVING, no en WHERE.",
    faq=[
        (
            "¿Puedo usar un alias del SELECT en HAVING?",
            "MySQL y SQLite lo permiten, pero no es estándar y PostgreSQL u Oracle fallan. Para que funcione en todas partes, repite la expresión: `HAVING COUNT(*) > 1`.",
        ),
        (
            "¿Qué pasa con los NULL en GROUP BY?",
            "Todos los NULL de la columna agrupada forman un grupo propio.",
        ),
    ],
    challenge=(
        "Ranking de ciclos",
        2,
        "Muestra cada ciclo con su nota máxima, ordenados de mayor a menor nota máxima.",
        "SELECT ciclo, ...\nFROM alumnos\nGROUP BY ciclo\n-- ORDER BY ...;",
        "Puedes ordenar por un agregado: `ORDER BY MAX(nota) DESC`.",
    ),
    questions=[
        cq(
            "sql-16",
            QUE,
            [ALUMNOS],
            "SELECT ciclo, COUNT(*) FROM alumnos\nGROUP BY ciclo\nORDER BY ciclo;",
            "ASIR | 1\nDAM | 2\nDAW | 2",
            ["ASIR | 1\nDAM | 2\nDAW | 1", "5", "DAW | 2\nDAM | 2\nASIR | 1"],
            "Una fila por ciclo. `COUNT(*)` cuenta filas, así que Eva cuenta en DAW aunque no tenga nota. `ORDER BY ciclo` ordena alfabéticamente.",
        ),
        cq(
            "sql-17",
            QUE,
            [ALUMNOS],
            "SELECT ciclo FROM alumnos\nGROUP BY ciclo\nHAVING COUNT(*) > 1\nORDER BY ciclo;",
            "DAM\nDAW",
            ["ASIR", "DAM", "ASIR\nDAM\nDAW"],
            "`HAVING` descarta los grupos con un solo alumno (ASIR).",
        ),
        cq(
            "sql-18",
            QUE,
            [ALUMNOS],
            "SELECT ciclo, MAX(nota) FROM alumnos\nWHERE nota < 9\nGROUP BY ciclo\nORDER BY ciclo;",
            "ASIR | 7\nDAM | 5\nDAW | 8",
            ["ASIR | 7\nDAM | 9\nDAW | 8", "DAM | 5\nDAW | 8", "ASIR | 7\nDAM | 5\nDAW | NULL"],
            "`WHERE` actúa **antes** de agrupar: quita a Sara (9) y a Eva (NULL no cumple `< 9`). En DAM solo queda Luis con 5.",
        ),
        tq(
            "sql-19",
            "¿Cuál es la diferencia entre WHERE y HAVING?",
            [
                "WHERE filtra filas antes de agrupar; HAVING filtra grupos después",
                "Son equivalentes; HAVING es más moderno",
                "HAVING filtra filas y WHERE filtra columnas",
                "WHERE solo funciona con GROUP BY",
            ],
            0,
            "Por eso las condiciones con agregados (`COUNT(*) > 1`, `AVG(nota) >= 5`) solo pueden ir en HAVING.",
        ),
        cq(
            "sql-20",
            QUE,
            [ALUMNOS],
            "SELECT ciclo, AVG(nota) FROM alumnos\nGROUP BY ciclo\nHAVING AVG(nota) >= 7\nORDER BY ciclo;",
            "ASIR | 7.0\nDAM | 7.0\nDAW | 8.0",
            ["DAW | 8.0", "ASIR | 7.0\nDAW | 8.0", "ASIR | 7.0\nDAM | 7.0\nDAW | 4.0"],
            "Medias: ASIR 7, DAM (5 + 9) / 2 = 7 y DAW 8 (el NULL de Eva no cuenta). Las tres cumplen `>= 7`. SQLite muestra los decimales como 7.0; MySQL, como 7.0000.",
        ),
    ],
    quiz=[
        tq(
            "sql-q07",
            "`SELECT ciclo, nombre, COUNT(*) FROM alumnos GROUP BY ciclo` da error en MySQL. ¿Por qué?",
            [
                "`nombre` no está en GROUP BY ni dentro de un agregado",
                "Falta un HAVING",
                "COUNT(*) no se puede combinar con GROUP BY",
                "Hay que agrupar por id",
            ],
            0,
            "Cada grupo tiene varios nombres: el SGBD no sabe cuál mostrar. O agrupas también por `nombre` o lo metes en un agregado.",
        ),
        cq(
            "sql-q08",
            QUE,
            [ALUMNOS],
            "SELECT COUNT(*) FROM alumnos\nGROUP BY ciclo\nHAVING ciclo = 'DAW';",
            "2",
            ["1", "5", "(sin filas)"],
            "Solo queda el grupo DAW, con Ana y Eva. (Filtrar por ciclo sería más eficiente en WHERE.)",
        ),
    ],
    sources=[MYSQL, PG],
)

# ---------------------------------------------------------------- bloque 3: combinaciones y subconsultas

L_JOIN = Lesson(
    slug="sql-inner-join",
    title="INNER JOIN: combinar tablas",
    theory="""
En una base de datos relacional la información se reparte en varias tablas unidas por **claves**: `pedidos.cliente_id` guarda el `id` del cliente. Un **JOIN** vuelve a juntarlas.

`SELECT c.nombre, p.total FROM clientes c INNER JOIN pedidos p ON p.cliente_id = c.id`

- `ON` indica cómo se relacionan las filas.
- `INNER JOIN` (o solo `JOIN`) devuelve **solo** las combinaciones que tienen pareja en las dos tablas. Un cliente sin pedidos no aparece.
- Los **alias de tabla** (`c`, `p`) acortan la consulta. Si dos tablas tienen una columna con el mismo nombre (como `id`), hay que **cualificarla** (`c.id`); si no, el SGBD da un error de columna ambigua.

**Producto cartesiano:** sin condición de unión (`FROM clientes, pedidos`) se combina cada fila con todas las de la otra tabla: 3 clientes × 3 pedidos = 9 filas. Casi nunca es lo que quieres.

Puedes encadenar varios JOIN: `pedidos` → `clientes` → `ciudades`.
""",
    example="""
CREATE TABLE clientes (id INTEGER PRIMARY KEY, nombre TEXT, ciudad TEXT);
CREATE TABLE pedidos (id INTEGER PRIMARY KEY, cliente_id INTEGER REFERENCES clientes(id), total INTEGER);
INSERT INTO clientes VALUES (1, 'Ana', 'Madrid'), (2, 'Luis', 'Leganés'), (3, 'Eva', 'Valladolid');
INSERT INTO pedidos VALUES (1, 1, 30), (2, 1, 20), (3, 2, 50);

SELECT p.id, c.nombre, c.ciudad, p.total
FROM pedidos p
JOIN clientes c ON c.id = p.cliente_id
ORDER BY p.id;
""",
    exercise="""
Con `clientes(id, nombre, ciudad)` y `pedidos(id, cliente_id, total)`:

1. Muestra cada pedido con el **nombre** y la **ciudad** de su cliente.
2. Calcula el **total gastado** por cada cliente que tenga pedidos.
""",
    starter="SELECT c.nombre, p.total\nFROM pedidos p\nJOIN clientes c ON ...;",
    hint="La condición de unión compara la clave ajena con la primaria: `ON c.id = p.cliente_id`. Para el total, añade `GROUP BY c.nombre` y `SUM(p.total)`.",
    faq=[
        ("¿JOIN es lo mismo que INNER JOIN?", "Sí: la palabra `INNER` es opcional."),
        (
            "¿La condición va en ON o en WHERE?",
            "Con INNER JOIN el resultado es el mismo. Por claridad, pon en `ON` cómo se relacionan las tablas y en `WHERE` los filtros. En los LEFT JOIN la diferencia sí importa.",
        ),
    ],
    challenge=(
        "Tres tablas",
        3,
        "Añade la tabla `ciudades(nombre, provincia)` con Madrid, Leganés y Valladolid y muestra cada pedido con la **provincia** de su cliente.",
        "CREATE TABLE ciudades (nombre TEXT PRIMARY KEY, provincia TEXT);\nINSERT INTO ciudades VALUES ('Madrid', 'Madrid'), ('Leganés', 'Madrid'), ('Valladolid', 'Valladolid');\n\nSELECT ...\nFROM pedidos p\nJOIN clientes c ON ...\nJOIN ciudades ci ON ...;",
        "Encadena dos JOIN: pedidos → clientes (por `cliente_id`) y clientes → ciudades (por el nombre de la ciudad).",
    ),
    questions=[
        cq(
            "sql-21",
            QUE,
            [CLIENTES, PEDIDOS],
            "SELECT c.nombre, p.total\nFROM clientes c\nINNER JOIN pedidos p ON p.cliente_id = c.id\nORDER BY p.id;",
            "Ana | 30\nAna | 20\nLuis | 50",
            [
                "Ana | 30\nLuis | 50",
                "Ana | 30\nAna | 20\nLuis | 50\nEva | NULL",
                "Ana | 50\nLuis | 50",
            ],
            "Sale una fila por cada pareja cliente-pedido: Ana tiene dos pedidos y aparece dos veces. Eva no tiene pedidos y el INNER JOIN la descarta.",
        ),
        cq(
            "sql-22",
            QUE,
            [CLIENTES, PEDIDOS],
            "SELECT COUNT(*) FROM clientes, pedidos;",
            "9",
            ["3", "6", "Error"],
            "Sin condición de unión se hace el **producto cartesiano**: cada uno de los 3 clientes con cada uno de los 3 pedidos, 9 filas.",
        ),
        cq(
            "sql-23",
            QUE,
            [CLIENTES, PEDIDOS],
            "SELECT c.nombre, SUM(p.total)\nFROM clientes c\nJOIN pedidos p ON p.cliente_id = c.id\nGROUP BY c.nombre\nORDER BY c.nombre;",
            "Ana | 50\nLuis | 50",
            ["Ana | 50\nEva | NULL\nLuis | 50", "Ana | 30\nLuis | 50", "Ana | 100"],
            "JOIN y GROUP BY se combinan: Ana suma 30 + 20 = 50 y Luis 50. Eva no aparece porque no tiene pedidos.",
        ),
        cq(
            "sql-24",
            QUE,
            [CLIENTES, PEDIDOS],
            "SELECT nombre FROM clientes\nJOIN pedidos ON pedidos.cliente_id = clientes.id\nWHERE total > 25\nORDER BY total;",
            "Ana\nLuis",
            ["Luis", "Ana\nAna\nLuis", "Eva"],
            "Pedidos de más de 25: el 1 de Ana (30) y el 3 de Luis (50). `nombre` y `total` solo existen en una tabla cada una, así que no hace falta cualificarlas.",
        ),
        cq(
            "sql-25",
            "¿Qué ocurre al ejecutar esta consulta?",
            [CLIENTES, PEDIDOS],
            "SELECT id FROM clientes\nJOIN pedidos ON pedidos.cliente_id = clientes.id;",
            "Error",
            ["1\n1\n2", "1\n2\n3", "(sin filas)"],
            "Las dos tablas tienen una columna `id` y el SGBD no sabe cuál quieres: error de columna **ambigua**. Hay que escribir `clientes.id` o `pedidos.id`.",
        ),
    ],
    quiz=[
        tq(
            "sql-q09",
            "¿Qué devuelve un INNER JOIN?",
            [
                "Solo las combinaciones de filas que tienen pareja en las dos tablas",
                "Todas las filas de la tabla de la izquierda",
                "Todas las filas de las dos tablas",
                "Cada fila de una tabla con todas las de la otra",
            ],
            0,
            "Las filas sin pareja se descartan. Para conservarlas se usa LEFT JOIN (siguiente lección).",
        ),
        cq(
            "sql-q10",
            QUE,
            [CLIENTES, PEDIDOS],
            "SELECT COUNT(*) FROM clientes c\nJOIN pedidos p ON p.cliente_id = c.id\nWHERE c.ciudad = 'Madrid';",
            "2",
            ["1", "3", "9"],
            "La única clienta de Madrid es Ana, que tiene dos pedidos.",
        ),
    ],
    sources=[MYSQL, PG],
)

L_LEFT = Lesson(
    slug="sql-left-join-subconsultas",
    title="LEFT JOIN y subconsultas",
    theory="""
`LEFT JOIN` conserva **todas** las filas de la tabla de la izquierda. Si una fila no tiene pareja, las columnas de la derecha se rellenan con **NULL**.

`SELECT c.nombre, p.total FROM clientes c LEFT JOIN pedidos p ON p.cliente_id = c.id`

Así aparecen también los clientes sin pedidos. Para quedarte **solo** con ellos: `WHERE p.id IS NULL`.

`RIGHT JOIN` es lo mismo con la tabla de la derecha. Casi siempre se prefiere reescribirlo como LEFT JOIN cambiando el orden de las tablas.

**Cuidado al contar:** tras un LEFT JOIN, `COUNT(*)` cuenta también la fila rellenada con NULL. Usa `COUNT(p.id)` para que un cliente sin pedidos salga con 0.

**Subconsultas:** una consulta dentro de otra, entre paréntesis.
- Escalar, que devuelve un solo valor: `WHERE nota > (SELECT AVG(nota) FROM alumnos)`.
- De lista, con `IN`: `WHERE id IN (SELECT cliente_id FROM pedidos)`.
- Con `EXISTS`, que comprueba si la subconsulta devuelve alguna fila.

**Trampa de NOT IN:** si la subconsulta contiene algún NULL, `NOT IN` no devuelve nada. `NOT EXISTS` o el LEFT JOIN con `IS NULL` no tienen ese problema.
""",
    example="""
CREATE TABLE clientes (id INTEGER PRIMARY KEY, nombre TEXT, ciudad TEXT);
CREATE TABLE pedidos (id INTEGER PRIMARY KEY, cliente_id INTEGER REFERENCES clientes(id), total INTEGER);
INSERT INTO clientes VALUES (1, 'Ana', 'Madrid'), (2, 'Luis', 'Leganés'), (3, 'Eva', 'Valladolid');
INSERT INTO pedidos VALUES (1, 1, 30), (2, 1, 20), (3, 2, 50);

SELECT c.nombre, COUNT(p.id) AS pedidos
FROM clientes c
LEFT JOIN pedidos p ON p.cliente_id = c.id
GROUP BY c.id
ORDER BY pedidos DESC;
""",
    exercise="""
Con `clientes` y `pedidos`:

1. Lista **todos** los clientes con cuántos pedidos tienen, incluidos los que tienen 0.
2. Muestra los clientes que han hecho algún pedido de **más de 40 €**, usando una subconsulta con `IN`.
""",
    starter="SELECT c.nombre, COUNT(p.id)\nFROM clientes c\nLEFT JOIN pedidos p ON ...\nGROUP BY c.id;",
    hint="Para contar 0 en los clientes sin pedidos, cuenta una columna de la tabla de la derecha: `COUNT(p.id)`.",
    faq=[
        (
            "¿COUNT(*) o COUNT(p.id) tras un LEFT JOIN?",
            "`COUNT(*)` cuenta también la fila rellenada con NULL, así que un cliente sin pedidos saldría con 1. `COUNT(p.id)` ignora ese NULL y da 0.",
        ),
        (
            "¿Subconsulta o JOIN?",
            "Muchas veces son equivalentes. Usa JOIN cuando necesites columnas de las dos tablas, e `IN`/`EXISTS` cuando solo quieras filtrar.",
        ),
    ],
    challenge=(
        "Clientes sin compras",
        2,
        "Encuentra los clientes sin pedidos de **dos** formas: con `LEFT JOIN … WHERE … IS NULL` y con `NOT EXISTS`.",
        "SELECT c.nombre\nFROM clientes c\nLEFT JOIN pedidos p ON ...\nWHERE ...;",
        "Con NOT EXISTS: `WHERE NOT EXISTS (SELECT 1 FROM pedidos p WHERE p.cliente_id = c.id)`.",
    ),
    questions=[
        cq(
            "sql-26",
            QUE,
            [CLIENTES, PEDIDOS],
            "SELECT c.nombre, p.total\nFROM clientes c\nLEFT JOIN pedidos p ON p.cliente_id = c.id\nORDER BY c.id, p.id;",
            "Ana | 30\nAna | 20\nLuis | 50\nEva | NULL",
            [
                "Ana | 30\nAna | 20\nLuis | 50",
                "Ana | 30\nLuis | 50\nEva | NULL",
                "Ana | 50\nLuis | 50\nEva | 0",
            ],
            "LEFT JOIN conserva a Eva aunque no tenga pedidos y rellena `total` con NULL (no con 0).",
        ),
        cq(
            "sql-27",
            QUE,
            [CLIENTES, PEDIDOS],
            "SELECT c.nombre\nFROM clientes c\nLEFT JOIN pedidos p ON p.cliente_id = c.id\nWHERE p.id IS NULL;",
            "Eva",
            ["(sin filas)", "Ana\nLuis", "Ana\nLuis\nEva"],
            "Es el patrón para encontrar filas **sin pareja**: solo Eva tiene la parte de pedidos a NULL.",
        ),
        cq(
            "sql-28",
            QUE,
            [ALUMNOS],
            "SELECT nombre FROM alumnos\nWHERE nota > (SELECT AVG(nota) FROM alumnos)\nORDER BY nombre;",
            "Ana\nSara",
            ["Ana\nJuan\nSara", "Sara", "Error"],
            "La subconsulta calcula la media: 7,25. Superan esa nota Ana (8) y Sara (9); Juan tiene 7.",
        ),
        cq(
            "sql-29",
            QUE,
            [CLIENTES, PEDIDOS],
            "SELECT nombre FROM clientes\nWHERE id IN (SELECT cliente_id FROM pedidos WHERE total >= 30)\nORDER BY nombre;",
            "Ana\nLuis",
            ["Luis", "Ana\nAna\nLuis", "Eva"],
            "La subconsulta devuelve los clientes 1 (pedido de 30) y 2 (pedido de 50). Con IN cada cliente sale una sola vez, a diferencia de un JOIN.",
        ),
        cq(
            "sql-30",
            QUE,
            [CLIENTES, PEDIDOS],
            "SELECT COUNT(*)\nFROM clientes c\nLEFT JOIN pedidos p ON p.cliente_id = c.id;",
            "4",
            ["3", "9", "5"],
            "Tres filas de parejas (Ana ×2, Luis) más la fila de Eva rellenada con NULL: 4.",
        ),
    ],
    quiz=[
        cq(
            "sql-q11",
            QUE,
            [CLIENTES, PEDIDOS],
            "SELECT c.nombre, COUNT(p.id)\nFROM clientes c\nLEFT JOIN pedidos p ON p.cliente_id = c.id\nGROUP BY c.id\nORDER BY c.id;",
            "Ana | 2\nLuis | 1\nEva | 0",
            ["Ana | 2\nLuis | 1\nEva | 1", "Ana | 2\nLuis | 1", "Ana | 2\nLuis | 1\nEva | NULL"],
            "`COUNT(p.id)` no cuenta el NULL de Eva: 0. Con `COUNT(*)` habría salido 1.",
        ),
        tq(
            "sql-q12",
            "¿Por qué `WHERE id NOT IN (SELECT cliente_id FROM pedidos)` puede no devolver ninguna fila?",
            [
                "Si la subconsulta contiene algún NULL, la condición nunca es verdadera",
                "NOT IN no admite subconsultas",
                "Porque falta un GROUP BY",
                "Solo funciona con números",
            ],
            0,
            "`x NOT IN (1, NULL)` equivale a `x <> 1 AND x <> NULL`, y lo segundo es *desconocido*. Usa `NOT EXISTS` o filtra los NULL en la subconsulta.",
        ),
    ],
    sources=[MYSQL, PG],
)

# ---------------------------------------------------------------- bloque 4: DDL y DML

L_CREATE = Lesson(
    slug="sql-crear-tablas",
    title="CREATE TABLE y restricciones",
    theory="""
El **DDL** (lenguaje de definición de datos) crea y modifica la estructura: `CREATE`, `ALTER` y `DROP`.

`CREATE TABLE libros (id INT PRIMARY KEY, titulo VARCHAR(200) NOT NULL, precio DECIMAL(8,2))`

**Tipos habituales en MySQL:** `INT`, `DECIMAL(p,s)` para dinero (sin errores de redondeo), `VARCHAR(n)`, `CHAR(n)` de longitud fija, `DATE`, `DATETIME` y `BOOLEAN`. SQLite, el motor de la app, usa **tipado flexible**: acepta esas declaraciones, pero no siempre comprueba el tipo.

**Restricciones:**
- `PRIMARY KEY`: identifica cada fila; implica valores únicos y no nulos.
- `NOT NULL`: obligatorio.
- `UNIQUE`: sin repetidos (admite NULL).
- `DEFAULT valor`: valor si no se indica otro.
- `CHECK (condición)`: regla de negocio, como `CHECK (precio >= 0)`.
- `FOREIGN KEY … REFERENCES tabla(columna)`: **clave ajena**. El valor tiene que existir en la otra tabla (integridad referencial). `ON DELETE CASCADE` borra también las filas hijas; `ON DELETE SET NULL` las deja sin padre.

**Identificadores automáticos:** en MySQL, `AUTO_INCREMENT`; en SQLite, una columna `INTEGER PRIMARY KEY`; en PostgreSQL, `GENERATED … AS IDENTITY`.

Si una sentencia incumple una restricción, el SGBD la **rechaza con un error** y no guarda nada de esa sentencia.
""",
    example="""
CREATE TABLE ciclos (
  codigo CHAR(4) PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL
);
CREATE TABLE alumnos (
  id INTEGER PRIMARY KEY,
  nombre VARCHAR(80) NOT NULL,
  email VARCHAR(120) UNIQUE,
  ciclo CHAR(4) REFERENCES ciclos(codigo) ON DELETE CASCADE,
  nota INTEGER CHECK (nota BETWEEN 0 AND 10)
);
INSERT INTO ciclos VALUES ('DAW', 'Desarrollo de Aplicaciones Web');
INSERT INTO alumnos (nombre, email, ciclo, nota) VALUES ('Ana', 'ana@fp.es', 'DAW', 8);

SELECT a.nombre, c.nombre FROM alumnos a JOIN ciclos c ON c.codigo = a.ciclo;
""",
    exercise="""
Crea la tabla `libros` con:

- `id`: clave primaria;
- `titulo`: obligatorio;
- `isbn`: único;
- `precio`: con dos decimales y nunca negativo;
- `alta`: fecha, por defecto la de hoy (`CURRENT_DATE`).
""",
    starter="CREATE TABLE libros (\n  id INTEGER PRIMARY KEY,\n  -- ...\n);",
    hint="Precio: `DECIMAL(8,2) CHECK (precio >= 0)`. Fecha: `alta DATE DEFAULT CURRENT_DATE`.",
    faq=[
        (
            "¿VARCHAR o CHAR?",
            "`CHAR(n)` siempre ocupa n caracteres; va bien para códigos de longitud fija, como `CHAR(9)` para un DNI. `VARCHAR(n)` ocupa solo lo que guardas, hasta n.",
        ),
        (
            "¿Por qué SQLite no se queja si guardo texto en una columna INTEGER?",
            "Por su tipado flexible: el tipo declarado es una recomendación. MySQL y PostgreSQL sí lo comprueban. Las restricciones (PRIMARY KEY, NOT NULL, UNIQUE, CHECK y FOREIGN KEY) sí se cumplen en todos.",
        ),
    ],
    challenge=(
        "Biblioteca",
        3,
        "Crea `socios` y `prestamos` relacionadas: cada préstamo pertenece a un socio y, si se borra el socio, se borran sus préstamos. Inserta datos de prueba y comprueba el borrado en cascada.",
        "CREATE TABLE socios (\n  id INTEGER PRIMARY KEY,\n  nombre VARCHAR(80) NOT NULL\n);\n\nCREATE TABLE prestamos (\n  -- ...\n);",
        "La clave ajena lleva la opción: `socio_id INTEGER REFERENCES socios(id) ON DELETE CASCADE`.",
    ),
    questions=[
        sq(
            "sql-31",
            "¿Qué ocurre al ejecutar este script?",
            "CREATE TABLE socios (id INTEGER PRIMARY KEY, email TEXT UNIQUE);\nINSERT INTO socios VALUES (1, 'a@fp.es');\nINSERT INTO socios VALUES (2, 'a@fp.es');\nSELECT COUNT(*) FROM socios;",
            "Error",
            ["1", "2", "0"],
            "El segundo INSERT repite un email en una columna `UNIQUE`: el SGBD lo rechaza con un error y el script se detiene ahí.",
        ),
        sq(
            "sql-32",
            SCRIPT,
            "CREATE TABLE cuentas (\n  id INTEGER PRIMARY KEY,\n  estado TEXT DEFAULT 'activa',\n  edad INTEGER CHECK (edad >= 16)\n);\nINSERT INTO cuentas (id, edad) VALUES (1, 18);\nSELECT estado FROM cuentas;",
            "activa",
            ["NULL", "Error", "(sin filas)"],
            "El INSERT no da valor a `estado`, así que se usa el `DEFAULT`. La edad 18 cumple el CHECK.",
        ),
        sq(
            "sql-33",
            "¿Qué ocurre al ejecutar este script?",
            "CREATE TABLE cuentas (\n  id INTEGER PRIMARY KEY,\n  edad INTEGER CHECK (edad >= 16)\n);\nINSERT INTO cuentas VALUES (1, 15);\nSELECT edad FROM cuentas;",
            "Error",
            ["15", "NULL", "(sin filas)"],
            "15 no cumple `CHECK (edad >= 16)`: el INSERT se rechaza con un error. Así se protegen las reglas de negocio en la propia base de datos.",
        ),
        sq(
            "sql-34",
            "¿Qué ocurre al ejecutar este script?",
            "CREATE TABLE ciclos (codigo TEXT PRIMARY KEY);\nCREATE TABLE matriculas (\n  id INTEGER PRIMARY KEY,\n  ciclo TEXT REFERENCES ciclos(codigo)\n);\nINSERT INTO ciclos VALUES ('DAW');\nINSERT INTO matriculas VALUES (1, 'DAM');\nSELECT * FROM matriculas;",
            "Error",
            ["1 | DAM", "(sin filas)", "1 | NULL"],
            "'DAM' no existe en `ciclos`: la clave ajena lo impide (integridad referencial). MySQL con InnoDB también lo rechaza; en SQLite hay que activar `PRAGMA foreign_keys = ON`, que la app activa siempre.",
        ),
        tq(
            "sql-35",
            "¿Qué tipo usarías en MySQL para guardar precios sin errores de redondeo?",
            ["DECIMAL(10,2)", "FLOAT", "DOUBLE", "VARCHAR(10)"],
            0,
            "`DECIMAL` guarda el número exacto. `FLOAT` y `DOUBLE` son aproximados (0,1 + 0,2 no da exactamente 0,3) y en un texto no se puede calcular.",
        ),
    ],
    quiz=[
        tq(
            "sql-q13",
            "Una PRIMARY KEY implica que la columna…",
            [
                "no admite repetidos ni NULL",
                "solo admite números",
                "se rellena sola siempre",
                "no se puede consultar con WHERE",
            ],
            0,
            "Es UNIQUE + NOT NULL. Que se rellene sola depende de AUTO_INCREMENT (MySQL) o de INTEGER PRIMARY KEY (SQLite).",
        ),
        sq(
            "sql-q14",
            SCRIPT,
            "CREATE TABLE socios (id INTEGER PRIMARY KEY);\nCREATE TABLE prestamos (\n  id INTEGER PRIMARY KEY,\n  socio_id INTEGER REFERENCES socios(id) ON DELETE CASCADE\n);\nINSERT INTO socios VALUES (1);\nINSERT INTO prestamos VALUES (10, 1), (11, 1);\nDELETE FROM socios WHERE id = 1;\nSELECT COUNT(*) FROM prestamos;",
            "0",
            ["2", "Error", "1"],
            "`ON DELETE CASCADE` borra automáticamente los préstamos del socio borrado. Sin esa opción, el DELETE habría dado error.",
        ),
    ],
    sources=[MYSQL, SQLITE],
)

L_DML = Lesson(
    slug="sql-modificar-datos",
    title="INSERT, UPDATE y DELETE",
    theory="""
El **DML** (lenguaje de manipulación de datos) cambia el contenido de las tablas.

**Insertar:**
- `INSERT INTO productos (nombre, precio) VALUES ('Cable', 5)`. Las columnas que no indiques reciben su `DEFAULT` o NULL.
- Varias filas a la vez: `VALUES (...), (...)`.
- A partir de una consulta: `INSERT INTO historico SELECT * FROM pedidos WHERE ...`.

**Modificar:** `UPDATE productos SET precio = precio * 1.1 WHERE stock > 0`.

**Borrar:** `DELETE FROM productos WHERE stock = 0`.

**Sin WHERE**, UPDATE y DELETE afectan a **todas** las filas. Antes de lanzarlos, ejecuta un `SELECT` con el mismo WHERE para ver qué filas vas a tocar. Recuerda que los NULL no cumplen las comparaciones: `DELETE … WHERE nota < 5` no borra las filas sin nota.

**Cambios de estructura:**
- `ALTER TABLE t ADD COLUMN …`, `DROP COLUMN …` y `RENAME TO …`.
- `DROP TABLE t` elimina la tabla entera.
- `TRUNCATE TABLE t` la vacía muy rápido y reinicia el AUTO_INCREMENT. Es de MySQL; SQLite no lo tiene.
""",
    example="""
CREATE TABLE productos (id INTEGER PRIMARY KEY, nombre TEXT, precio INTEGER, stock INTEGER DEFAULT 0);
INSERT INTO productos (nombre, precio, stock) VALUES ('Teclado', 25, 10), ('Ratón', 15, 0), ('Cable', 5, 50);

UPDATE productos SET precio = precio + 2 WHERE precio < 20;
DELETE FROM productos WHERE stock = 0;
ALTER TABLE productos ADD COLUMN activo INTEGER DEFAULT 1;

SELECT * FROM productos;
""",
    exercise="""
Con la tabla `productos(id, nombre, precio, stock)`:

1. Sube un 10 % el precio de los productos que cuestan menos de 20 €.
2. Borra los que no tienen stock.
3. Comprueba el resultado con un SELECT.
""",
    starter="UPDATE productos\nSET precio = ...\nWHERE ...;\n\nDELETE FROM productos\nWHERE ...;\n\nSELECT * FROM productos;",
    hint="Subir un 10 % es multiplicar por 1.1: `SET precio = precio * 1.1`.",
    faq=[
        (
            "¿Se puede deshacer un DELETE?",
            "Solo si estás dentro de una transacción sin confirmar (con `ROLLBACK`). Tras `COMMIT`, o en modo autocommit, no: para eso están las copias de seguridad.",
        ),
        (
            "¿TRUNCATE o DELETE sin WHERE?",
            "Los dos vacían la tabla. `TRUNCATE` es más rápido y reinicia el AUTO_INCREMENT, pero no admite WHERE y en MySQL no se puede deshacer.",
        ),
    ],
    challenge=(
        "Reposición",
        2,
        "Pon stock 20 a los productos con menos de 5 unidades, añade un producto nuevo con precio y stock y muestra el catálogo ordenado por nombre.",
        "UPDATE productos\nSET stock = 20\nWHERE ...;\n\nINSERT INTO productos (nombre, precio, stock) VALUES (...);\n\nSELECT * FROM productos ORDER BY nombre;",
        "Condición del UPDATE: `stock < 5`. Recuerda que los NULL no cumplen la comparación.",
    ),
    questions=[
        cq(
            "sql-36",
            SCRIPT,
            [PRODUCTOS],
            "UPDATE productos SET precio = precio * 2 WHERE stock = 0;\nSELECT SUM(precio) FROM productos;",
            "240",
            ["225", "450", "255"],
            "Solo el Ratón tiene stock 0: su precio pasa de 15 a 30. Suma: 25 + 30 + 180 + 5 = 240.",
        ),
        cq(
            "sql-37",
            SCRIPT,
            [ALUMNOS],
            "DELETE FROM alumnos WHERE nota < 7;\nSELECT COUNT(*) FROM alumnos;",
            "4",
            ["3", "5", "2"],
            "Solo se borra Luis (5). Eva tiene la nota a NULL y `NULL < 7` no es verdadero, así que **no** se borra. Quedan 4 filas.",
        ),
        cq(
            "sql-38",
            SCRIPT,
            [ALUMNOS],
            "UPDATE alumnos SET nota = 10;\nSELECT COUNT(*) FROM alumnos WHERE nota = 10;",
            "5",
            ["0", "1", "4"],
            "Un UPDATE sin WHERE cambia **todas** las filas, incluida la de Eva, que tenía NULL.",
        ),
        cq(
            "sql-39",
            SCRIPT,
            [PRODUCTOS],
            "INSERT INTO productos (nombre, precio) VALUES ('Alfombrilla', 8);\nSELECT id, stock FROM productos WHERE nombre = 'Alfombrilla';",
            "5 | NULL",
            ["5 | 0", "1 | NULL", "Error"],
            "El id se genera solo (el mayor más uno: 5), como con AUTO_INCREMENT en MySQL. `stock` no tiene DEFAULT, así que queda NULL, no 0.",
        ),
        tq(
            "sql-40",
            "¿Qué diferencia hay entre `DELETE FROM t` y `DROP TABLE t`?",
            [
                "DELETE borra las filas y la tabla sigue existiendo; DROP elimina la tabla entera",
                "Ninguna, son sinónimos",
                "DROP borra solo las filas repetidas",
                "DELETE elimina también la estructura",
            ],
            0,
            "Después de un DELETE sin WHERE la tabla sigue ahí, vacía. Después de DROP TABLE ya no existe.",
        ),
    ],
    quiz=[
        cq(
            "sql-q15",
            SCRIPT,
            [ALUMNOS],
            "INSERT INTO alumnos (id, nombre, ciclo, nota)\n  SELECT 10, 'Copia', ciclo, nota FROM alumnos WHERE id = 1;\nSELECT nombre, nota FROM alumnos WHERE id = 10;",
            "Copia | 8",
            ["Ana | 8", "Copia | NULL", "Error"],
            "`INSERT … SELECT` inserta las filas que devuelve la consulta; aquí copia el ciclo y la nota de Ana.",
        ),
        tq(
            "sql-q16",
            "Antes de lanzar un UPDATE o DELETE en producción, ¿qué conviene hacer?",
            [
                "Ejecutar un SELECT con el mismo WHERE para ver qué filas afectará",
                "Desactivar las claves ajenas",
                "Hacer un DROP TABLE de prueba",
                "Nada: se puede deshacer siempre",
            ],
            0,
            "Así compruebas el filtro sin riesgo. Y, si puedes, trabaja dentro de una transacción.",
        ),
    ],
    sources=[MYSQL, SQLITE],
)

# ---------------------------------------------------------------- bloque 5: diseño y transacciones

L_MODEL = Lesson(
    slug="sql-modelo-relacional",
    title="Modelo relacional y normalización",
    theory="""
Antes de crear tablas se **diseña**. El modelo **entidad-relación (E/R)** describe entidades (alumno, módulo), sus atributos y cómo se relacionan.

**Cardinalidades y paso a tablas:**
- **1:N** (un ciclo tiene muchos alumnos): la clave ajena va en el lado N. `alumnos.ciclo` apunta a `ciclos.codigo`.
- **N:M** (un alumno cursa muchos módulos y un módulo tiene muchos alumnos): hace falta una **tabla intermedia** `matriculas(alumno_id, modulo_id)` con dos claves ajenas y clave primaria compuesta.
- **1:1**: la clave ajena va en cualquiera de las dos tablas, con UNIQUE.

**Claves:**
- **candidata**: identifica cada fila de forma única y mínima;
- **primaria**: la candidata elegida;
- **ajena** (o foránea): apunta a la primaria de otra tabla.

**Normalización:** evita datos repetidos y las anomalías al insertar, modificar o borrar.
- **1FN:** valores atómicos, sin listas en una celda ni grupos repetidos (`telefono1`, `telefono2`…).
- **2FN:** 1FN y cada atributo no clave depende de **toda** la clave primaria. Solo puede fallar con claves compuestas.
- **3FN:** 2FN y sin **dependencias transitivas**: ningún atributo no clave depende de otro atributo no clave.
""",
    example="""
CREATE TABLE alumnos (id INTEGER PRIMARY KEY, nombre TEXT NOT NULL);
CREATE TABLE modulos (codigo TEXT PRIMARY KEY, nombre TEXT NOT NULL);
CREATE TABLE matriculas (
  alumno_id INTEGER REFERENCES alumnos(id),
  modulo_codigo TEXT REFERENCES modulos(codigo),
  nota INTEGER,
  PRIMARY KEY (alumno_id, modulo_codigo)
);
INSERT INTO alumnos VALUES (1, 'Ana'), (2, 'Luis');
INSERT INTO modulos VALUES ('BD', 'Bases de datos'), ('PRO', 'Programación');
INSERT INTO matriculas VALUES (1, 'BD', 8), (1, 'PRO', 7), (2, 'BD', 6);

SELECT a.nombre, m.nombre, x.nota
FROM matriculas x
JOIN alumnos a ON a.id = x.alumno_id
JOIN modulos m ON m.codigo = x.modulo_codigo;
""",
    exercise="""
Diseña las tablas de una biblioteca:

- un **libro** puede tener varios **autores** y un autor, varios libros;
- los **socios** piden **préstamos** de libros, con fecha de salida y de devolución.

Escribe los `CREATE TABLE` con sus claves primarias y ajenas.
""",
    starter="CREATE TABLE libros (\n  id INTEGER PRIMARY KEY,\n  titulo TEXT NOT NULL\n);\n\n-- autores, libros_autores, socios, prestamos...",
    hint="Libros-autores es N:M: necesitas una tabla intermedia `libros_autores(libro_id, autor_id)`. Un préstamo une un socio y un libro.",
    faq=[
        (
            "¿Siempre hay que llegar a 3FN?",
            "Es el objetivo por defecto en bases de datos de gestión. A veces se desnormaliza a propósito para leer más rápido (informes), aceptando el coste de mantener datos duplicados.",
        ),
        (
            "¿Clave natural o sustituta?",
            "Natural: un dato real, como el DNI o el ISBN. Sustituta: un id artificial autoincremental. La sustituta no cambia nunca y ocupa poco; la natural se protege con UNIQUE.",
        ),
    ],
    challenge=(
        "Normaliza",
        3,
        "Lleva hasta 3FN esta tabla: `pedidos(id, cliente, direccion_cliente, producto1, producto2, producto3)`. Escribe las tablas resultantes con sus claves.",
        "CREATE TABLE clientes (\n  -- ...\n);\n\nCREATE TABLE pedidos (\n  -- ...\n);\n\nCREATE TABLE lineas_pedido (\n  -- ...\n);",
        "Los productos repetidos rompen la 1FN (tabla de líneas). La dirección depende del cliente, no del pedido: rompe la 3FN (tabla de clientes).",
    ),
    questions=[
        tq(
            "sql-41",
            "Un alumno se matricula en muchos módulos y cada módulo tiene muchos alumnos. ¿Cómo se representa?",
            [
                "Con una tabla intermedia matriculas(alumno_id, modulo_id)",
                "Con una clave ajena modulo_id en alumnos",
                "Con una clave ajena alumno_id en modulos",
                "Guardando los módulos separados por comas en alumnos",
            ],
            0,
            "Una relación N:M necesita una tabla intermedia con una clave ajena hacia cada tabla. Una sola clave ajena solo permitiría un módulo por alumno (o un alumno por módulo).",
        ),
        tq(
            "sql-42",
            "En la relación 1:N «un ciclo tiene muchos alumnos», ¿dónde va la clave ajena?",
            [
                "En alumnos: cada alumno guarda el código de su ciclo",
                "En ciclos: cada ciclo guarda la lista de alumnos",
                "En una tabla intermedia obligatoria",
                "En las dos tablas",
            ],
            0,
            "La clave ajena va en el lado N: cada alumno apunta a **un** ciclo. Al revés habría que guardar una lista, lo que rompe la 1FN.",
        ),
        tq(
            "sql-43",
            "La tabla alumnos tiene una columna `telefonos` con el valor '600111222, 611333444'. ¿Qué incumple?",
            [
                "La 1FN: los valores no son atómicos",
                "La 2FN",
                "La 3FN",
                "Nada: es una forma válida de guardarlo",
            ],
            0,
            "Una celda debe tener un solo valor. Lo correcto es una tabla `telefonos(alumno_id, telefono)`.",
        ),
        tq(
            "sql-44",
            "matriculas(alumno_id, modulo_id, nombre_modulo, nota) tiene como clave (alumno_id, modulo_id). ¿Qué problema hay?",
            [
                "nombre_modulo depende solo de modulo_id: incumple la 2FN",
                "nota debería ser clave",
                "Incumple la 1FN",
                "Ninguno",
            ],
            0,
            "`nombre_modulo` depende de **parte** de la clave. Se repetiría en cada matrícula y habría que cambiarlo en muchas filas. Va en la tabla `modulos`.",
        ),
        tq(
            "sql-45",
            "empleados(id, departamento_id, nombre_departamento), con clave id. ¿Qué forma normal incumple?",
            [
                "La 3FN: nombre_departamento depende de departamento_id, no directamente de la clave",
                "La 1FN",
                "La 2FN",
                "Ninguna",
            ],
            0,
            "Es una **dependencia transitiva** (id → departamento_id → nombre_departamento). El nombre va en una tabla `departamentos`.",
        ),
    ],
    quiz=[
        tq(
            "sql-q17",
            "¿Qué es una clave candidata?",
            [
                "Un conjunto mínimo de atributos que identifica cada fila de forma única",
                "Una clave ajena todavía sin usar",
                "Cualquier columna con índice",
                "La columna id que se genera sola",
            ],
            0,
            "De las claves candidatas se elige una como primaria. Las demás se suelen proteger con UNIQUE.",
        ),
        tq(
            "sql-q18",
            "¿Qué garantiza la integridad referencial?",
            [
                "Que toda clave ajena apunte a una fila que existe",
                "Que no haya filas repetidas",
                "Que las consultas sean rápidas",
                "Que los datos estén cifrados",
            ],
            0,
            "Es lo que comprueban las FOREIGN KEY: no puedes matricular a nadie en un ciclo que no existe.",
        ),
    ],
    sources=[PG, MYSQL],
)

L_TX = Lesson(
    slug="sql-transacciones-vistas",
    title="Transacciones, vistas e índices",
    theory="""
Una **transacción** agrupa varias sentencias que deben aplicarse **todas o ninguna**. El ejemplo clásico es una transferencia: restar de una cuenta y sumar en otra.

- `BEGIN` (o `START TRANSACTION` en MySQL) la abre.
- `COMMIT` confirma los cambios.
- `ROLLBACK` deshace todo lo hecho desde el BEGIN.

Sin transacción explícita, cada sentencia se confirma sola (*autocommit*).

**ACID**, las garantías de una transacción:
- **Atomicidad:** todo o nada.
- **Consistencia:** se respetan las restricciones.
- **Aislamiento:** las transacciones simultáneas no se estorban.
- **Durabilidad:** lo confirmado sobrevive a un fallo.

**Vistas:** `CREATE VIEW aprobados AS SELECT …` guarda una **consulta** con nombre. Se usa como una tabla, pero no copia datos: cada vez que la consultas se ejecuta de nuevo y ves los datos actuales.

**Índices:** `CREATE INDEX idx_ciclo ON alumnos(ciclo)` acelera las búsquedas, los JOIN y los ORDER BY por esa columna. A cambio ocupa espacio y ralentiza un poco los INSERT y UPDATE. La PRIMARY KEY y los UNIQUE ya crean su índice. Un índice **no cambia nunca el resultado** de una consulta, solo su velocidad.
""",
    example="""
CREATE TABLE cuentas (id INTEGER PRIMARY KEY, titular TEXT, saldo INTEGER CHECK (saldo >= 0));
INSERT INTO cuentas VALUES (1, 'Ana', 100), (2, 'Luis', 20);

BEGIN;
UPDATE cuentas SET saldo = saldo - 50 WHERE id = 1;
UPDATE cuentas SET saldo = saldo + 50 WHERE id = 2;
COMMIT;

CREATE VIEW resumen AS SELECT titular, saldo FROM cuentas WHERE saldo > 0;
SELECT * FROM resumen;
""",
    exercise="""
Con la tabla `alumnos(id, nombre, ciclo, nota)`:

1. Crea una vista `resumen_ciclos` con cada ciclo, su número de alumnos y su nota media.
2. Consulta la vista, cambia una nota con UPDATE y vuelve a consultarla: ¿ha cambiado?
""",
    starter="CREATE VIEW resumen_ciclos AS\nSELECT ciclo, ...\nFROM alumnos\nGROUP BY ciclo;\n\nSELECT * FROM resumen_ciclos;",
    hint="Una vista es una consulta guardada: al volver a consultarla verás la nota nueva.",
    faq=[
        (
            "¿Qué pasa si se corta la luz a mitad de una transacción?",
            "Al reiniciar, el SGBD deshace lo no confirmado (atomicidad) y conserva lo confirmado (durabilidad).",
        ),
        (
            "¿Por qué no indexar todas las columnas?",
            "Cada índice ocupa espacio y hay que actualizarlo en cada INSERT, UPDATE y DELETE. Se indexan las columnas por las que filtras o unes a menudo.",
        ),
    ],
    challenge=(
        "Transferencia segura",
        2,
        "Con `cuentas(id, titular, saldo)`, pasa 50 € de la cuenta 1 a la 2 dentro de una transacción. Después, intenta pasar 1000 € y deshaz la operación con ROLLBACK.",
        "BEGIN;\nUPDATE cuentas SET saldo = saldo - 50 WHERE id = 1;\n-- ...\nCOMMIT;",
        "Si una de las dos sentencias falla (por ejemplo, por un CHECK de saldo >= 0), haz ROLLBACK para que no se aplique ninguna.",
    ),
    questions=[
        cq(
            "sql-46",
            SCRIPT,
            [PRODUCTOS],
            "BEGIN;\nUPDATE productos SET stock = 0;\nROLLBACK;\nSELECT SUM(stock) FROM productos;",
            "64",
            ["0", "Error", "NULL"],
            "`ROLLBACK` deshace el UPDATE: el stock vuelve a ser 10 + 0 + 4 + 50 = 64.",
        ),
        cq(
            "sql-47",
            SCRIPT,
            [ALUMNOS],
            "BEGIN;\nDELETE FROM alumnos WHERE ciclo = 'DAM';\nCOMMIT;\nSELECT COUNT(*) FROM alumnos;",
            "3",
            ["5", "2", "Error"],
            "`COMMIT` confirma el borrado de los dos alumnos de DAM: quedan 3.",
        ),
        cq(
            "sql-48",
            SCRIPT,
            [ALUMNOS],
            "CREATE VIEW aprobados AS\n  SELECT nombre FROM alumnos WHERE nota >= 5;\nUPDATE alumnos SET nota = 4 WHERE nombre = 'Luis';\nSELECT COUNT(*) FROM aprobados;",
            "3",
            ["4", "5", "Error"],
            "Una vista guarda la **consulta**, no los datos. Al consultarla después del UPDATE, Luis ya no tiene un 5: aprueban Ana, Juan y Sara.",
        ),
        tq(
            "sql-49",
            "¿Qué propiedad ACID garantiza que una transacción se aplica entera o no se aplica nada?",
            ["Atomicidad", "Consistencia", "Aislamiento", "Durabilidad"],
            0,
            "Atómico significa indivisible: o todas las sentencias o ninguna.",
        ),
        tq(
            "sql-50",
            "¿Cuándo **no** compensa crear un índice?",
            [
                "En una tabla pequeña o muy escrita, sobre una columna por la que casi nunca filtras",
                "En la columna de un JOIN frecuente",
                "En una columna de un WHERE muy habitual",
                "En una tabla grande de solo lectura",
            ],
            0,
            "El índice cuesta espacio y tiempo en cada escritura; solo compensa si acelera consultas frecuentes.",
        ),
    ],
    quiz=[
        tq(
            "sql-q19",
            "¿Qué hace ROLLBACK?",
            [
                "Deshace los cambios de la transacción en curso",
                "Confirma los cambios",
                "Borra la tabla",
                "Vuelve a la copia de seguridad de ayer",
            ],
            0,
            "Solo deshace lo no confirmado de la transacción abierta.",
        ),
        cq(
            "sql-q20",
            SCRIPT,
            [ALUMNOS],
            "CREATE INDEX idx_ciclo ON alumnos(ciclo);\nSELECT COUNT(*) FROM alumnos WHERE ciclo = 'DAW';",
            "2",
            ["1", "Error", "0"],
            "Un índice no cambia el resultado, solo lo rápido que se obtiene: sigue habiendo 2 alumnos de DAW.",
        ),
    ],
    sources=[MYSQL, PG],
)

# ---------------------------------------------------------------- temario del centro (ADR-0019)
# Lecciones nuevas que siguen las UD1-UD3 del módulo Bases de datos de tu centro. Las lecciones
# anteriores conservan sus slugs e ids para no perder el progreso; solo cambian de bloque.

PROVEEDORES = T(
    "proveedores",
    [("id", "INTEGER PRIMARY KEY"), ("nombre", "TEXT")],
    [(1, "Ana"), (2, "Tecnofp"), (3, "Luis")],
)


def fq(id: str, q: str, code: str, accept: list[str], expect: str, explain: str) -> Q:
    """Completar el hueco `___`: cada respuesta aceptada se ejecuta y tiene que dar `expect`."""
    return Q(
        id=id,
        q=q,
        code=code.strip("\n"),
        expect=expect,
        explain=explain,
        kind="fill",
        accept=accept,
    )


def oq(id: str, q: str, lines: list[str], expect: str, explain: str, context: str = "___") -> Q:
    """Ordenar líneas: en `context`, la línea `___` es donde van las líneas ordenadas."""
    return Q(
        id=id,
        q=q,
        code=context.strip("\n"),
        expect=expect,
        explain=explain,
        kind="order",
        lines=lines,
    )


def bq(id: str, code: str, bug: int, fix: str, target: str, explain: str) -> Q:
    """Encontrar el error: las opciones son las líneas; la corrección tiene que dar `target`."""
    q = f"Este script debería devolver `{target}`, pero da error o devuelve otra cosa. ¿Qué línea tiene el error?"
    return Q(
        id=id,
        q=q,
        code=code.strip("\n"),
        explain=explain,
        kind="bug",
        bug=bug,
        fix=fix,
        target=target,
    )


AEPD = ("Agencia Española de Protección de Datos", "https://www.aepd.es/")

L_UD1_TIPOS = Lesson(
    slug="bd-tipos-y-modelos",
    title="Tipos y modelos de bases de datos",
    theory="""
**Almacenar información** es organizar, guardar y recuperar datos de forma eficiente. Si una tienda online guarda mal sus pedidos, pierde datos o se retrasa.

**Según dónde está la información:**
- **Centralizada:** todo en un único servidor. Es fácil de administrar y de mantener coherente, pero si ese servidor cae, no hay acceso a nada (**punto único de fallo**) y se satura con muchos usuarios.
- **Distribuida:** los datos se reparten entre varios servidores conectados. Si uno falla, los demás siguen y la carga se reparte, pero es más difícil mantener los datos sincronizados y cuesta más administrarla.

**Fragmentación** (en las distribuidas):
- **Horizontal:** se reparten las **filas**. Los alumnos de cada provincia, en un servidor distinto.
- **Vertical:** se reparten las **columnas**. Los datos personales de un empleado en un servidor y la nómina en otro, unidos por la clave.
- **Mixta:** las dos a la vez.

**Modelos de bases de datos:**
- **Relacional:** tablas con filas y columnas, relacionadas por claves primarias y ajenas. Es el más usado.
- **Jerárquico:** un árbol; cada nodo tiene **un solo padre** (Empresa → Departamentos → Empleados).
- **En red:** como el jerárquico, pero un nodo puede tener **varios padres**. Más flexible y más difícil de gestionar.
- **Orientado a objetos:** los datos son objetos con **atributos y métodos** (un `Personaje` con `nivel` y `actualizarNivel()`).

**Según la ubicación:** **local** (en un solo equipo), **en la nube** (servidores remotos por internet, escalable) y **distribuida**. Para elegir se mira la **escalabilidad**, el **rendimiento** y la **seguridad**.

**Big Data:** volúmenes de datos que las herramientas tradicionales no procesan bien. Las **5 V**: **Volumen**, **Velocidad** (tiempo real), **Variedad** (estructurados y no estructurados), **Veracidad** (fiabilidad) y **Valor**. Herramientas: **Hadoop** (almacena y procesa datos repartidos en muchos servidores) y **Spark** (procesamiento muy rápido, en tiempo real).
""",
    example="""
-- Fragmentación horizontal: cada provincia en su tabla (en la realidad, en su servidor)
CREATE TABLE alumnos_madrid (id INTEGER PRIMARY KEY, nombre TEXT, provincia TEXT);
CREATE TABLE alumnos_valladolid (id INTEGER PRIMARY KEY, nombre TEXT, provincia TEXT);
INSERT INTO alumnos_madrid VALUES (1, 'Ana', 'Madrid'), (2, 'Luis', 'Madrid');
INSERT INTO alumnos_valladolid VALUES (3, 'Eva', 'Valladolid');

-- La tabla completa se reconstruye uniendo los fragmentos
SELECT * FROM alumnos_madrid
UNION ALL
SELECT * FROM alumnos_valladolid;
""",
    exercise="""
Una cadena de academias tiene sedes en Madrid y Valladolid y guarda de cada alumno: nombre, DNI, dirección, notas y pagos.

1. Propón una **fragmentación horizontal** y una **vertical** de la tabla de alumnos.
2. Escribe los `CREATE TABLE` de la vertical y la consulta que reconstruye al alumno completo.
""",
    starter="-- Fragmento con los datos personales\nCREATE TABLE alumnos_personal (\n  id INTEGER PRIMARY KEY,\n  -- ...\n);\n\n-- Fragmento con los datos académicos\nCREATE TABLE alumnos_academico (\n  -- ...\n);",
    hint="En la vertical, los dos fragmentos repiten la clave primaria `id` para poder volver a unirlos con un JOIN.",
    faq=[
        (
            "¿La fragmentación es lo mismo que una copia de seguridad?",
            "No. Fragmentar reparte los datos: cada fila o columna está en un solo sitio. Replicar sí copia los mismos datos en varios servidores, para que sigan disponibles si uno falla.",
        ),
        (
            "¿Qué modelo se usa hoy?",
            "El relacional domina en aplicaciones de gestión (MySQL, PostgreSQL, Oracle). Los jerárquicos y en red son sobre todo históricos. Para Big Data y redes sociales se usan también bases NoSQL y de grafos.",
        ),
    ],
    challenge=(
        "Elige el modelo",
        2,
        "Para cada caso, di qué tipo de base de datos elegirías y por qué: (1) el inventario de una tienda de barrio; (2) una plataforma de cursos online con alumnos de todo el mundo; (3) una red de contactos donde importa quién conoce a quién.",
        "-- 1. Tienda de barrio: ...\n-- 2. Plataforma global: ...\n-- 3. Red de contactos: ...",
        "Piensa en escalabilidad y acceso remoto. Una relacional local basta para una tienda pequeña; lo global pide nube; las relaciones complejas, un modelo de grafos.",
    ),
    questions=[
        tq(
            "bd-01",
            "¿Cuál es el principal inconveniente de una base de datos centralizada?",
            [
                "Si el servidor central falla, no se puede acceder a ningún dato",
                "Es difícil mantener la coherencia de los datos",
                "Necesita varios servidores sincronizados",
                "No permite usar SQL",
            ],
            0,
            "Todo está en un único servidor: es un **punto único de fallo**. En cambio, la coherencia es justo lo más fácil de mantener en una centralizada.",
        ),
        tq(
            "bd-02",
            "¿Qué ventaja tiene una base de datos distribuida frente a una centralizada?",
            [
                "Si un servidor falla, los datos de los demás siguen accesibles",
                "Es más fácil de administrar",
                "Es más sencillo mantener los datos sincronizados",
                "Necesita menos recursos",
            ],
            0,
            "Reparte los datos y la carga entre servidores. A cambio, sincronizarlos y administrarla es más difícil y costoso.",
        ),
        tq(
            "bd-03",
            "Guardar a los alumnos de cada provincia en un servidor distinto es fragmentación…",
            ["horizontal", "vertical", "mixta", "jerárquica"],
            0,
            "Se reparten las **filas** según una condición (la provincia). Todas las filas conservan todas sus columnas.",
        ),
        tq(
            "bd-04",
            "Los datos personales de los empleados van a un servidor y los de nómina a otro. ¿Qué fragmentación es?",
            ["Vertical", "Horizontal", "Mixta", "Ninguna: es una réplica"],
            0,
            "Se reparten las **columnas**. Cada fragmento repite la clave para poder reconstruir al empleado con un JOIN.",
        ),
        tq(
            "bd-05",
            "Se separan los alumnos por provincia y, dentro de cada provincia, sus datos personales de los académicos. ¿Qué fragmentación es?",
            ["Mixta", "Horizontal", "Vertical", "Distribuida simple"],
            0,
            "Combina la horizontal (por provincia, filas) y la vertical (personal o académico, columnas).",
        ),
        tq(
            "bd-06",
            "¿En qué modelo cada nodo tiene un único padre, como un árbol?",
            ["Jerárquico", "En red", "Relacional", "Orientado a objetos"],
            0,
            "Empresa → Departamentos → Empleados. Si un nodo pudiera tener varios padres, sería el modelo **en red**.",
        ),
        tq(
            "bd-07",
            "Un empleado puede estar vinculado a varios proyectos, y cada proyecto a varios empleados, en un modelo que no usa tablas. ¿Cuál es?",
            ["En red", "Jerárquico", "Relacional", "Fichero plano"],
            0,
            "El modelo en red permite que un nodo tenga **varios padres**. Es más flexible que el jerárquico, pero más difícil de gestionar que el relacional.",
        ),
        tq(
            "bd-08",
            "¿Qué modelo guarda los datos como objetos con atributos y métodos?",
            ["Orientado a objetos", "Relacional", "Jerárquico", "En red"],
            0,
            "Combina bases de datos y POO. Va bien cuando los datos tienen comportamiento asociado, como en simulaciones o videojuegos.",
        ),
        tq(
            "bd-09",
            "¿Cuál de estas NO es una de las 5 V del Big Data?",
            ["Visibilidad", "Veracidad", "Variedad", "Velocidad"],
            0,
            "Las 5 V son Volumen, Velocidad, Variedad, Veracidad y Valor.",
        ),
        tq(
            "bd-10",
            "¿Para qué sirve Hadoop?",
            [
                "Para almacenar y procesar grandes volúmenes de datos repartidos en muchos servidores",
                "Para diseñar diagramas entidad-relación",
                "Para cifrar bases de datos personales",
                "Para dar permisos a los usuarios de MySQL",
            ],
            0,
            "Hadoop es una plataforma de código abierto para Big Data, con datos estructurados y no estructurados. Spark se usa cuando se necesita procesar muy rápido, en tiempo real.",
        ),
        sq(
            "bd-11",
            "La tabla de alumnos está fragmentada horizontalmente. ¿Qué devuelve la última consulta?",
            "CREATE TABLE alumnos_madrid (id INTEGER PRIMARY KEY, nombre TEXT);\nCREATE TABLE alumnos_valladolid (id INTEGER PRIMARY KEY, nombre TEXT);\nINSERT INTO alumnos_madrid VALUES (1, 'Ana'), (2, 'Luis');\nINSERT INTO alumnos_valladolid VALUES (3, 'Eva');\nSELECT COUNT(*) FROM (\n  SELECT nombre FROM alumnos_madrid\n  UNION ALL\n  SELECT nombre FROM alumnos_valladolid\n);",
            "3",
            ["2", "1", "Error"],
            "`UNION ALL` junta las filas de los dos fragmentos: 2 + 1 = 3 alumnos. Así se reconstruye la tabla completa.",
        ),
        sq(
            "bd-12",
            "Los empleados están fragmentados verticalmente. ¿Qué devuelve la última consulta?",
            "CREATE TABLE emp_personal (id INTEGER PRIMARY KEY, nombre TEXT);\nCREATE TABLE emp_nomina (id INTEGER PRIMARY KEY, salario INTEGER);\nINSERT INTO emp_personal VALUES (1, 'Ana'), (2, 'Luis');\nINSERT INTO emp_nomina VALUES (1, 2100), (2, 1800);\nSELECT p.nombre, n.salario\nFROM emp_personal p JOIN emp_nomina n ON n.id = p.id\nWHERE p.id = 2;",
            "Luis | 1800",
            ["Luis | 2100", "Luis", "Error"],
            "Los dos fragmentos comparten la clave `id`: con un JOIN por ella se reconstruye la fila completa del empleado 2.",
        ),
    ],
    quiz=[
        tq(
            "bd-q01",
            "Una app móvil de pedidos de comida con usuarios en todo el país necesita escalar rápido. ¿Qué tipo de base de datos encaja mejor?",
            [
                "En la nube",
                "Local, en el ordenador del restaurante",
                "Un fichero plano",
                "Jerárquica",
            ],
            0,
            "La nube da escalabilidad y acceso desde cualquier lugar sin montar infraestructura propia.",
        ),
        tq(
            "bd-q02",
            "En Big Data, ¿qué significa la «Veracidad»?",
            [
                "Que los datos sean fiables y estén libres de errores",
                "Que se procesen en tiempo real",
                "Que haya muchos formatos distintos",
                "Que generen beneficio",
            ],
            0,
            "Tiempo real es Velocidad; muchos formatos, Variedad; beneficio, Valor.",
        ),
    ],
    sources=[MYSQL, PG],
)

L_UD1_SGBD = Lesson(
    slug="bd-ficheros-rgpd-sgbd",
    title="Ficheros, protección de datos y SGBD",
    theory="""
**Ficheros:** la forma más básica de guardar datos.
- **Planos** (de texto): líneas seguidas sin estructura extra, como `Juan,25`. Fáciles de crear, pero lentos para buscar un dato concreto.
- **Indexados:** los datos van con un **índice** (por ejemplo, por número de cliente) para encontrarlos sin recorrer todo. A cambio, el índice ocupa espacio y hay que mantenerlo al día.
- **De acceso directo:** divididos en registros a los que se salta directamente (el producto `P123`). Rápidos, pero más complejos de diseñar.

**Métodos de acceso:**
- **Secuencial:** se lee del principio al final. Ideal para procesar **todo** (la media de todas las edades), lento para un dato concreto.
- **Aleatorio** (directo): se va a cualquier posición sin recorrer lo anterior. Ideal para **un registro concreto** (actualizar el precio de un producto).

**Protección de datos:**
- **RGPD:** reglamento **europeo**, aplicable desde 2018, para los datos personales de los ciudadanos de la UE.
- **LOPDGDD:** ley orgánica **española** que lo complementa y añade derechos digitales, como la **desconexión digital** en el trabajo.
- **Principios:** **consentimiento** claro, **transparencia** (qué datos, para qué y quién), **minimización** (solo los datos necesarios) y **seguridad** (cifrado, control de accesos).
- **Tus obligaciones como desarrollador:** informar a los usuarios, proteger los datos y facilitar sus derechos: **acceso, rectificación y supresión** (la app debe permitir borrar los datos).

**SGBD** (sistema gestor de bases de datos): el software intermediario entre los datos y quien los usa. Sus tres funciones:
- **Definición** de datos: crear tablas, índices y relaciones (**DDL**: `CREATE`, `ALTER`, `DROP`).
- **Manipulación**: insertar, modificar, borrar y consultar (**DML**: `INSERT`, `UPDATE`, `DELETE`, `SELECT`).
- **Control**: seguridad, integridad y permisos (**DCL**: `GRANT`, `REVOKE`).

**Componentes:** el **motor** (procesa el almacenamiento y la recuperación), el **lenguaje de consulta** (SQL) y las **herramientas de administración** (permisos, copias de seguridad).

**Tipos:** **relacionales** (MySQL, PostgreSQL, Oracle), **NoSQL** (MongoDB, Cassandra; datos no estructurados, gran volumen) y **de grafos** (Neo4j; relaciones complejas como redes de contactos o rutas).
""",
    example="""
-- Definición (DDL)
CREATE TABLE productos (codigo TEXT PRIMARY KEY, nombre TEXT NOT NULL, precio INTEGER);

-- Manipulación (DML)
INSERT INTO productos VALUES ('P123', 'Teclado', 25), ('P124', 'Ratón', 15);
UPDATE productos SET precio = 22 WHERE codigo = 'P123';

-- Control (DCL), en MySQL (SQLite no tiene usuarios):
-- GRANT SELECT ON tienda.productos TO 'vendedor'@'localhost';

SELECT * FROM productos WHERE codigo = 'P123';
""",
    exercise="""
Diseña el registro de usuarios de una web que permite descargar un PDF gratuito.

1. ¿Qué datos pedirías como **mínimo**? Justifícalo con el principio de minimización.
2. Escribe el `CREATE TABLE` y el `DELETE` que ejecutarías si un usuario ejerce su derecho de supresión.
""",
    starter="CREATE TABLE usuarios (\n  id INTEGER PRIMARY KEY,\n  -- ...\n);\n\n-- Derecho de supresión del usuario 7\n",
    hint="Para descargar un PDF basta con un email (y la fecha del consentimiento). Ni dirección ni teléfono. Supresión: `DELETE FROM usuarios WHERE id = 7;`.",
    faq=[
        (
            "¿Un SGBD y una base de datos son lo mismo?",
            "No. La base de datos son los datos organizados; el SGBD es el programa que los gestiona (MySQL, PostgreSQL…). Un mismo SGBD puede gestionar muchas bases de datos.",
        ),
        (
            "¿El RGPD se aplica a mis proyectos de clase?",
            "Si guardan datos personales de personas reales, sí. En clase y en pruebas, usa datos inventados.",
        ),
    ],
    challenge=(
        "Clasifica sentencias",
        1,
        "Clasifica como DDL, DML o DCL: `CREATE TABLE`, `SELECT`, `GRANT`, `ALTER TABLE`, `DELETE`, `REVOKE`, `UPDATE`, `DROP TABLE`.",
        "-- DDL: ...\n-- DML: ...\n-- DCL: ...",
        "DDL cambia la estructura; DML, los datos; DCL, los permisos.",
    ),
    questions=[
        tq(
            "bd-13",
            "Un fichero guarda «Juan,25» en cada línea, sin ninguna estructura más. ¿Qué tipo de fichero es?",
            ["Plano", "Indexado", "De acceso directo", "Una base de datos relacional"],
            0,
            "Es un fichero plano (de texto). Es fácil de manejar, pero con muchos datos cuesta encontrar uno concreto.",
        ),
        tq(
            "bd-14",
            "¿Qué inconveniente tiene un fichero indexado?",
            [
                "El índice ocupa espacio y hay que mantenerlo actualizado",
                "No permite buscar un registro concreto",
                "Solo se puede leer de principio a fin",
                "No puede guardar números",
            ],
            0,
            "El índice acelera las búsquedas, pero cuesta espacio y tiempo mantenerlo al día. Es el mismo equilibrio que con los índices de una base de datos.",
        ),
        tq(
            "bd-15",
            "Quieres calcular la media de edad de todas las personas de un fichero. ¿Qué acceso es el adecuado?",
            ["Secuencial", "Aleatorio", "Por índice único", "Ninguno: hace falta un SGBD"],
            0,
            "Hay que leer todos los registros en orden: el acceso secuencial es justo para eso.",
        ),
        tq(
            "bd-16",
            "Quieres actualizar el precio del producto P123 en un fichero de acceso directo. ¿Qué acceso usarás?",
            ["Aleatorio", "Secuencial", "Fragmentado", "Distribuido"],
            0,
            "El acceso aleatorio salta directamente al registro sin recorrer los anteriores.",
        ),
        tq(
            "bd-17",
            "¿Qué relación hay entre el RGPD y la LOPDGDD?",
            [
                "El RGPD es europeo y la LOPDGDD es la ley española que lo complementa",
                "La LOPDGDD es europea y el RGPD es español",
                "La LOPDGDD sustituyó al RGPD en 2018",
                "Son dos nombres de la misma ley",
            ],
            0,
            "El RGPD se aplica en toda la UE desde 2018. La LOPDGDD lo adapta a España y añade derechos digitales.",
        ),
        tq(
            "bd-18",
            "Una web te pide dirección y teléfono solo para descargar un archivo gratuito. ¿Qué principio incumple?",
            ["Minimización de datos", "Transparencia", "Seguridad", "Veracidad"],
            0,
            "Solo se deben recoger los datos estrictamente necesarios para la finalidad. Para descargar un archivo, la dirección y el teléfono sobran.",
        ),
        tq(
            "bd-19",
            "¿Qué norma recoge el derecho a la desconexión digital en el trabajo?",
            ["La LOPDGDD", "El RGPD", "El modelo relacional", "La norma SQL"],
            0,
            "Es uno de los derechos digitales que la LOPDGDD añade a lo que ya establece el RGPD.",
        ),
        tq(
            "bd-20",
            "Un usuario pide que borren todos sus datos de tu app. ¿Qué debes hacer?",
            [
                "Facilitarlo: es su derecho de supresión",
                "Negarte si los datos son útiles para la empresa",
                "Ocultarlos en la app pero conservarlos siempre",
                "Pedirle que lo haga él con SQL",
            ],
            0,
            "Los usuarios tienen derecho de acceso, rectificación y supresión, y la aplicación debe facilitarlos.",
        ),
        tq(
            "bd-21",
            "¿Qué función del SGBD cubre la sentencia GRANT?",
            [
                "Control de datos (DCL)",
                "Definición de datos (DDL)",
                "Manipulación de datos (DML)",
                "Ninguna: GRANT no es SQL",
            ],
            0,
            "Dar y quitar permisos (GRANT y REVOKE) es control de datos. CREATE, ALTER y DROP son definición; INSERT, UPDATE, DELETE y SELECT, manipulación.",
        ),
        tq(
            "bd-22",
            "¿Qué componente del SGBD procesa realmente el almacenamiento y la recuperación de los datos?",
            [
                "El motor de base de datos",
                "El lenguaje de consulta",
                "Las herramientas de administración",
                "El sistema operativo",
            ],
            0,
            "El motor es el núcleo. SQL es cómo se lo pides y las herramientas de administración sirven para permisos, copias o supervisión.",
        ),
        tq(
            "bd-23",
            "MongoDB y Neo4j son, respectivamente, SGBD…",
            [
                "NoSQL y de grafos",
                "relacional y NoSQL",
                "de grafos y relacional",
                "jerárquico y en red",
            ],
            0,
            "MongoDB es NoSQL (documentos, datos semiestructurados). Neo4j es de grafos (relaciones complejas). MySQL, PostgreSQL y Oracle son relacionales.",
        ),
        sq(
            "bd-24",
            "El SGBD garantiza la integridad de los datos. ¿Qué ocurre al ejecutar este script?",
            "CREATE TABLE productos (codigo TEXT PRIMARY KEY, precio INTEGER);\nINSERT INTO productos VALUES ('P123', 25);\nINSERT INTO productos VALUES ('P123', 30);\nSELECT precio FROM productos;",
            "Error",
            ["25", "30", "25\n30"],
            "El segundo INSERT repite la clave primaria: el SGBD lo rechaza. Evitar duplicados es parte de su función de control.",
        ),
    ],
    quiz=[
        tq(
            "bd-q03",
            "¿Qué método de acceso es más eficiente para leer un único registro concreto?",
            ["Aleatorio", "Secuencial", "Los dos igual", "Ninguno"],
            0,
            "El secuencial obliga a recorrer todo hasta encontrarlo; el aleatorio va directo.",
        ),
        tq(
            "bd-q04",
            "¿Cuál de estos es un principio de la protección de datos?",
            ["Transparencia", "Fragmentación", "Normalización", "Velocidad"],
            0,
            "Consentimiento, transparencia, minimización y seguridad. Los demás son conceptos de bases de datos o de Big Data.",
        ),
    ],
    sources=[AEPD, MYSQL],
)

L_UD2_MAS = Lesson(
    slug="bd-null-indices-dcl",
    title="NULL, ALTER, índices, usuarios y vistas",
    theory="""
**NULL** significa que el dato **no se conoce, no aplica o aún no se ha registrado**. No es 0 ni una cadena vacía.
- `NULL` no es igual a nada, ni siquiera a otro NULL: `WHERE telefono = NULL` **no devuelve nunca filas**. Se usa `IS NULL` o `IS NOT NULL`.
- `COUNT(*)` cuenta filas; `COUNT(columna)` no cuenta los NULL. `SUM`, `AVG`, `MAX` y `MIN` también los ignoran.
- Si un dato es obligatorio, declara la columna `NOT NULL`; si tiene un valor habitual, usa `DEFAULT`.

**Tipos de datos:** `INT`/`INTEGER` (enteros), `VARCHAR(n)` y `TEXT` (texto), `DATE`, `TIME` y `DATETIME` (fechas y horas), `BOOLEAN` (verdadero o falso) y `DECIMAL(p,s)` (dinero). El tipo correcto ahorra espacio, acelera las consultas e impide guardar datos inválidos.

**DDL para cambiar la estructura:**
- `ALTER TABLE clientes ADD email VARCHAR(100);` añade una columna, que queda a NULL en las filas que ya existían (o con su `DEFAULT`).
- `ALTER TABLE clientes MODIFY email VARCHAR(75);` cambia el tipo en **MySQL** (en PostgreSQL es `ALTER COLUMN … TYPE`).
- `DROP TABLE clientes;` borra la tabla **y todos sus datos**. Úsalo con cuidado.

**Índices:** como el índice de un libro. `CREATE INDEX idx_cat ON productos(categoria);`
- **Únicos** (`CREATE UNIQUE INDEX`): además impiden repetidos.
- **Compuestos:** sobre varias columnas, como `(cliente_id, fecha)`, para consultas que filtran por las dos.
- Aceleran las lecturas, pero **ralentizan las escrituras** (INSERT, UPDATE y DELETE deben actualizar el índice). No se indexan todas las columnas: solo las que se consultan a menudo.

**DCL (MySQL):** usuarios, permisos y roles.
- `CREATE USER 'juan'@'localhost' IDENTIFIED BY '…';`
- `GRANT SELECT, INSERT ON tienda.productos TO 'juan'@'localhost';` da permisos (`tienda.*` es toda la base de datos; `ALL PRIVILEGES`, todos los permisos).
- `REVOKE INSERT ON tienda.productos FROM 'juan'@'localhost';` los quita. Ojo: GRANT va con **TO** y REVOKE con **FROM**.
- **Roles:** un conjunto de permisos con nombre que se asigna a varios usuarios: `CREATE ROLE 'gestor_tienda'; GRANT SELECT, INSERT, UPDATE ON tienda.* TO 'gestor_tienda'; GRANT 'gestor_tienda' TO 'juan'@'localhost';`

**Vistas:** `CREATE VIEW nombre AS SELECT …` es una **tabla virtual**: guarda la consulta, no los datos. Sirven para reutilizar consultas complejas, **ocultar columnas sensibles** (el salario) y dar a cada usuario los datos que necesita. Siempre muestran los datos actuales de las tablas; no todas permiten INSERT o UPDATE.
""",
    example="""
CREATE TABLE clientes (
  id INTEGER PRIMARY KEY,
  nombre VARCHAR(50) NOT NULL,
  telefono VARCHAR(15) NULL
);
INSERT INTO clientes VALUES (1, 'Ana', '600111222'), (2, 'Carlos', NULL), (3, 'Marta', '611333444');

ALTER TABLE clientes ADD email VARCHAR(100);
CREATE INDEX idx_nombre ON clientes(nombre);
CREATE VIEW sin_telefono AS SELECT id, nombre FROM clientes WHERE telefono IS NULL;

SELECT * FROM sin_telefono;
""",
    exercise="""
Sobre una tabla `empleados(id, nombre, puesto, salario, telefono)`:

1. Crea una vista `empleados_publico` sin el salario.
2. Añade la columna `fecha_baja` (vacía mientras el empleado siga activo).
3. Escribe, en MySQL, el GRANT para que `rrhh`@`localhost` solo pueda consultar esa vista.
""",
    starter="CREATE VIEW empleados_publico AS\nSELECT ...;\n\nALTER TABLE empleados ...;\n\n-- GRANT ...",
    hint="`GRANT SELECT ON empresa.empleados_publico TO 'rrhh'@'localhost';`. La fecha de baja admite NULL: es un dato que no aplica mientras el empleado sigue activo.",
    faq=[
        (
            "¿Por qué `= NULL` no da error pero tampoco devuelve nada?",
            "Comparar con NULL da «desconocido», ni verdadero ni falso, y el WHERE solo deja pasar lo verdadero. Por eso existe `IS NULL`.",
        ),
        (
            "¿Un índice cambia el resultado de una consulta?",
            "Nunca. Solo cambia lo rápido que se obtiene. El plan de ejecución (`EXPLAIN`) te dice si se usa.",
        ),
    ],
    challenge=(
        "Permisos de una tienda",
        2,
        "Escribe en MySQL: un rol `vendedor` que pueda consultar e insertar en `tienda.pedidos` y solo consultar `tienda.productos`; asígnalo a `lucia`@`localhost`; después quítale a ese rol el permiso de insertar.",
        "CREATE ROLE 'vendedor';\n-- ...",
        "Cada GRANT va con ON base.tabla TO rol. Para quitarlo: `REVOKE INSERT ON tienda.pedidos FROM 'vendedor';`.",
    ),
    questions=[
        cq(
            "bd-25",
            QUE,
            [ALUMNOS],
            "SELECT nombre FROM alumnos WHERE nota = NULL;",
            "(sin filas)",
            ["Eva", "Error", "NULL"],
            "Comparar con `= NULL` nunca es verdadero, ni siquiera con otro NULL. Para encontrar a Eva hay que escribir `WHERE nota IS NULL`.",
        ),
        cq(
            "bd-26",
            QUE,
            [ALUMNOS],
            "SELECT nombre FROM alumnos WHERE nota IS NULL;",
            "Eva",
            ["(sin filas)", "Error", "Ana\nLuis\nJuan\nSara"],
            "`IS NULL` es la forma correcta de preguntar por un dato que falta.",
        ),
        cq(
            "bd-27",
            QUE,
            [ALUMNOS],
            "SELECT COUNT(nota), COUNT(*) FROM alumnos;",
            "4 | 5",
            ["5 | 5", "4 | 4", "5 | 4"],
            "`COUNT(*)` cuenta las 5 filas; `COUNT(nota)` no cuenta la nota NULL de Eva.",
        ),
        cq(
            "bd-28",
            QUE,
            [ALUMNOS],
            "SELECT AVG(nota) FROM alumnos;",
            "7.25",
            ["5.8", "7", "Error"],
            "AVG ignora los NULL: (8 + 5 + 7 + 9) / 4 = 7,25. Si contara a Eva como 0, saldría 29 / 5 = 5,8.",
        ),
        sq(
            "bd-29",
            SCRIPT,
            "CREATE TABLE clientes (id INTEGER PRIMARY KEY, nombre TEXT);\nINSERT INTO clientes VALUES (1, 'Ana');\nALTER TABLE clientes ADD email TEXT;\nSELECT nombre, email FROM clientes;",
            "Ana | NULL",
            ["Ana", "Error", "Ana | "],
            "La columna nueva existe en todas las filas, pero las que ya había no tienen valor: queda a NULL.",
        ),
        sq(
            "bd-30",
            SCRIPT,
            "CREATE TABLE productos (id INTEGER PRIMARY KEY, nombre TEXT);\nINSERT INTO productos VALUES (1, 'Teclado');\nALTER TABLE productos ADD stock INTEGER DEFAULT 0;\nSELECT stock FROM productos;",
            "0",
            ["NULL", "Error", "(sin filas)"],
            "Con `DEFAULT 0`, las filas que ya existían toman ese valor en la columna nueva.",
        ),
        sq(
            "bd-31",
            "¿Qué ocurre al ejecutar este script?",
            "CREATE TABLE clientes (id INTEGER PRIMARY KEY, nombre TEXT);\nINSERT INTO clientes VALUES (1, 'Ana');\nDROP TABLE clientes;\nSELECT * FROM clientes;",
            "Error",
            ["(sin filas)", "1 | Ana", "NULL"],
            "`DROP TABLE` elimina la tabla entera, estructura y datos. Después ya no existe y el SELECT falla. Para vaciarla conservando la estructura se usa `DELETE FROM`.",
        ),
        tq(
            "bd-32",
            "En MySQL, ¿cómo cambias la columna Email de la tabla Clientes a VARCHAR(75)?",
            [
                "ALTER TABLE Clientes MODIFY Email VARCHAR(75);",
                "UPDATE Clientes SET Email = VARCHAR(75);",
                "CHANGE TABLE Clientes Email VARCHAR(75);",
                "ALTER Clientes Email TO VARCHAR(75);",
            ],
            0,
            "`ALTER TABLE … MODIFY` es la sintaxis de MySQL. UPDATE cambia datos, no la estructura.",
        ),
        tq(
            "bd-33",
            "¿Qué efecto tiene crear un índice sobre una columna?",
            [
                "Las búsquedas por esa columna van más rápido, pero los INSERT y UPDATE algo más lentos",
                "Todo va más rápido, sin ningún inconveniente",
                "Cambia el orden de los resultados de las consultas",
                "Impide que la columna tenga valores repetidos",
            ],
            0,
            "Cada escritura tiene que actualizar también el índice. Solo un índice **único** impide repetidos, y ninguno cambia el resultado.",
        ),
        tq(
            "bd-34",
            "Las consultas buscan a menudo los pedidos de un cliente en una fecha. ¿Qué índice conviene?",
            [
                "Un índice compuesto sobre (cliente_id, fecha)",
                "Un índice único sobre fecha",
                "Un índice sobre cada columna de la tabla",
                "Ninguno: los índices solo sirven para la clave primaria",
            ],
            0,
            "Un índice compuesto cubre consultas que filtran por varias columnas a la vez. Indexarlo todo ralentizaría las escrituras sin necesidad.",
        ),
        sq(
            "bd-35",
            "¿Qué ocurre al ejecutar este script?",
            "CREATE TABLE usuarios (id INTEGER PRIMARY KEY, email TEXT);\nCREATE UNIQUE INDEX idx_email ON usuarios(email);\nINSERT INTO usuarios VALUES (1, 'a@fp.es');\nINSERT INTO usuarios VALUES (2, 'a@fp.es');\nSELECT COUNT(*) FROM usuarios;",
            "Error",
            ["2", "1", "0"],
            "Un índice **único** acelera las búsquedas y además impide repetir el email: el segundo INSERT se rechaza.",
        ),
        tq(
            "bd-36",
            "¿Qué sentencia de MySQL deja a juan consultar y añadir datos en la tabla productos de la base tienda?",
            [
                "GRANT SELECT, INSERT ON tienda.productos TO 'juan'@'localhost';",
                "GRANT SELECT, INSERT ON tienda.productos FROM 'juan'@'localhost';",
                "REVOKE SELECT, INSERT ON tienda.productos TO 'juan'@'localhost';",
                "ALLOW SELECT, INSERT FOR juan IN tienda.productos;",
            ],
            0,
            "GRANT privilegios ON base.tabla TO usuario. REVOKE es para quitarlos, y va con FROM.",
        ),
        tq(
            "bd-37",
            "¿Cómo le quitas a juan el permiso de insertar en tienda.productos?",
            [
                "REVOKE INSERT ON tienda.productos FROM 'juan'@'localhost';",
                "REVOKE INSERT ON tienda.productos TO 'juan'@'localhost';",
                "DELETE INSERT FROM juan;",
                "DROP GRANT INSERT ON tienda.productos;",
            ],
            0,
            "REVOKE tiene la misma estructura que GRANT, pero con **FROM** en lugar de TO.",
        ),
        tq(
            "bd-38",
            "¿Qué ventaja tiene usar roles?",
            [
                "Agrupan permisos y se asignan de una vez a muchos usuarios con la misma función",
                "Hacen que las consultas sean más rápidas",
                "Sustituyen a las contraseñas",
                "Permiten saltarse las claves ajenas",
            ],
            0,
            "Si cambian los permisos de los gestores, se cambia el rol una vez y afecta a todos los que lo tienen.",
        ),
        sq(
            "bd-39",
            "La vista se crea antes de insertar los pedidos. ¿Qué devuelve la última consulta?",
            "CREATE TABLE pedidos (id INTEGER PRIMARY KEY, total INTEGER, estado TEXT);\nCREATE VIEW completados AS\n  SELECT id, total FROM pedidos WHERE estado = 'Completado';\nINSERT INTO pedidos VALUES\n  (1, 30, 'Completado'), (2, 20, 'Pendiente'), (3, 50, 'Completado');\nSELECT COUNT(*) FROM completados;",
            "2",
            ["0", "3", "Error"],
            "Una vista no guarda datos: guarda la consulta y la ejecuta cada vez. Por eso ve los pedidos insertados después de crearla.",
        ),
        tq(
            "bd-40",
            "Algunos usuarios no deben ver el salario de los empleados. ¿Qué solución usa lo visto en la unidad?",
            [
                "Una vista con todas las columnas menos el salario, y dar permiso solo sobre la vista",
                "Borrar la columna salario",
                "Guardar el salario como NULL",
                "Crear un índice sobre salario",
            ],
            0,
            "Proteger datos sensibles es uno de los usos principales de las vistas. Combinada con GRANT, cada usuario solo ve lo que necesita.",
        ),
        fq(
            "bd-41",
            "Completa la consulta para obtener los alumnos sin nota.",
            ALUMNOS.setup() + "SELECT nombre FROM alumnos WHERE nota IS ___;",
            ["NULL", "null"],
            "Eva",
            "Con `= NULL` no saldría nadie: hay que usar `IS NULL`.",
        ),
        bq(
            "bd-42",
            "CREATE TABLE clientes (id INTEGER PRIMARY KEY, telefono TEXT);\nINSERT INTO clientes VALUES (1, '600111222'), (2, NULL);\nSELECT id FROM clientes WHERE telefono = NULL;",
            2,
            "SELECT id FROM clientes WHERE telefono IS NULL;",
            "2",
            "`telefono = NULL` nunca es verdadero, así que no sale ninguna fila. La corrección es `WHERE telefono IS NULL`.",
        ),
        oq(
            "bd-43",
            "Ordena el script para que el SELECT devuelva `1 | Ana | NULL`.",
            [
                "CREATE TABLE clientes (id INTEGER PRIMARY KEY, nombre TEXT);",
                "INSERT INTO clientes VALUES (1, 'Ana');",
                "ALTER TABLE clientes ADD email TEXT;",
                "SELECT * FROM clientes;",
            ],
            "1 | Ana | NULL",
            "Primero la estructura, luego los datos, después el cambio de estructura y por último la consulta. Si el ALTER fuera antes del INSERT, faltaría un valor para `email` y el INSERT fallaría.",
        ),
    ],
    quiz=[
        tq(
            "bd-q05",
            "¿Qué significa que una columna tenga el valor NULL?",
            [
                "Que el dato se desconoce, no aplica o no se ha registrado",
                "Que vale 0",
                "Que es una cadena vacía",
                "Que la fila está borrada",
            ],
            0,
            "NULL es ausencia de dato. No es 0 ni una cadena vacía.",
        ),
        tq(
            "bd-q06",
            "¿Qué es una vista?",
            [
                "Una consulta guardada que se usa como una tabla virtual",
                "Una copia de seguridad de una tabla",
                "Un índice sobre varias columnas",
                "Un usuario con permisos de solo lectura",
            ],
            0,
            "No almacena datos propios: los lee de las tablas cada vez que se consulta.",
        ),
    ],
    sources=[MYSQL, SQLITE],
)

L_UD3_MAS = Lesson(
    slug="bd-conjuntos-y-optimizacion",
    title="UNION, INTERSECT, EXCEPT, subconsultas y optimización",
    theory="""
**Proyección, selección y ordenación:**
- **Proyección:** elegir **columnas**, en el `SELECT`.
- **Selección:** elegir **filas**, en el `WHERE`.
- **Ordenación:** `ORDER BY columna ASC` (por defecto) o `DESC`.

**Operadores:** de comparación `=`, `<>` (o `!=`, que aceptan MySQL y SQLite), `<`, `>`, `<=` y `>=`; lógicos `AND`, `OR` y `NOT`. Usa paréntesis al mezclar AND y OR: `precio > 50 AND (categoria = 'Hogar' OR categoria = 'Electrónica')`.

**Combinar selecciones** (las dos consultas deben tener **el mismo número de columnas y tipos compatibles**):
- `UNION`: junta los resultados y **quita los duplicados**. `UNION ALL` los conserva.
- `INTERSECT`: solo lo que está **en las dos**.
- `EXCEPT`: lo que está en la **primera y no en la segunda**. (MySQL los admite desde la versión 8.0.31; Oracle llama `MINUS` a EXCEPT).
- No garantizan orden: añade `ORDER BY` **al final**.

**Composiciones externas:**
- `LEFT JOIN`: todas las filas de la izquierda; donde no hay pareja, NULL.
- `RIGHT JOIN`: todas las de la derecha. `A RIGHT JOIN B` equivale a `B LEFT JOIN A`.
- `FULL OUTER JOIN`: todas las de las dos (MySQL no la tiene: se simula con LEFT JOIN UNION RIGHT JOIN).
- `COALESCE(valor, alternativa)` sustituye los NULL: `COALESCE(p.total, 0)`.

**Subconsultas:** una consulta entre paréntesis dentro de otra; se ejecuta primero.
- **Escalar** (un solo valor): `WHERE precio > (SELECT AVG(precio) FROM productos)`.
- **De varias filas**: con `IN`, `ANY` o `ALL`: `WHERE id IN (SELECT cliente_id FROM pedidos)`.
- Un JOIN suele ser más eficiente que una subconsulta equivalente.

**Optimización:**
- **Índices** en las columnas que se filtran o se unen a menudo.
- Evita `SELECT *`: pide solo las columnas que necesitas.
- **Estadísticas** al día: el SGBD las usa para decidir cómo ejecutar la consulta.
- **Plan de ejecución:** `EXPLAIN SELECT …` muestra los pasos y si se usa un índice. Sirve para encontrar **cuellos de botella** (falta de índices, consultas mal diseñadas, tablas enormes sin particionar).
""",
    example=CLIENTES.setup()
    + PROVEEDORES.setup()
    + PEDIDOS.setup()
    + """
-- Nombres que son a la vez clientes y proveedores
SELECT nombre FROM clientes INTERSECT SELECT nombre FROM proveedores;

-- Todos los clientes con su gasto (0 si no han comprado)
SELECT c.nombre, COALESCE(SUM(p.total), 0) AS gasto
FROM clientes c LEFT JOIN pedidos p ON p.cliente_id = c.id
GROUP BY c.id, c.nombre
ORDER BY gasto DESC;
""",
    exercise="""
Con las tablas `clientes`, `proveedores` y `pedidos`:

1. Lista sin repetidos todos los nombres de clientes y proveedores, en orden alfabético.
2. Muestra los clientes que no han hecho ningún pedido de dos formas: con `NOT IN` y con `LEFT JOIN … IS NULL`.
3. Escribe un `EXPLAIN` de la segunda y crea el índice que ayudaría.
""",
    starter="SELECT nombre FROM clientes\nUNION\nSELECT nombre FROM proveedores\nORDER BY nombre;\n\n-- 2. ...",
    hint="`WHERE id NOT IN (SELECT cliente_id FROM pedidos)`. Con LEFT JOIN: `WHERE p.id IS NULL`. El índice iría en `pedidos(cliente_id)`.",
    faq=[
        (
            "¿UNION o JOIN?",
            "UNION pone filas **debajo** de otras (mismas columnas). JOIN pone columnas **al lado** (relaciona filas por una clave).",
        ),
        (
            "¿Cuidado con NOT IN?",
            "Si la subconsulta devuelve algún NULL, `NOT IN` no devuelve ninguna fila. Con claves ajenas que admiten NULL, es más seguro `NOT EXISTS` o el `LEFT JOIN … IS NULL`.",
        ),
    ],
    challenge=(
        "Informe de ventas",
        3,
        "Con `ventas(producto, categoria, cantidad, precio)`: el ingreso total por categoría, solo de las categorías que superen los 1000 €, de mayor a menor, y los productos cuyo ingreso supere la media de ingresos por producto.",
        "SELECT categoria, SUM(cantidad * precio) AS ingresos\nFROM ventas\n-- ...",
        "Lo primero es GROUP BY + HAVING + ORDER BY DESC. Lo segundo necesita una subconsulta que calcule la media.",
    ),
    questions=[
        cq(
            "bd-44",
            QUE,
            [CLIENTES, PROVEEDORES],
            "SELECT nombre FROM clientes\nUNION\nSELECT nombre FROM proveedores\nORDER BY nombre;",
            "Ana\nEva\nLuis\nTecnofp",
            ["Ana\nAna\nEva\nLuis\nLuis\nTecnofp", "Ana\nLuis", "Eva"],
            "UNION junta los dos resultados y quita los duplicados: Ana y Luis aparecen una sola vez.",
        ),
        cq(
            "bd-45",
            QUE,
            [CLIENTES, PROVEEDORES],
            "SELECT COUNT(*) FROM (\n  SELECT nombre FROM clientes\n  UNION ALL\n  SELECT nombre FROM proveedores\n);",
            "6",
            ["4", "2", "Error"],
            "`UNION ALL` conserva los duplicados: 3 clientes + 3 proveedores = 6 filas. Con UNION serían 4.",
        ),
        cq(
            "bd-46",
            QUE,
            [CLIENTES, PROVEEDORES],
            "SELECT nombre FROM clientes\nINTERSECT\nSELECT nombre FROM proveedores\nORDER BY nombre;",
            "Ana\nLuis",
            ["Eva", "Ana\nEva\nLuis\nTecnofp", "Tecnofp"],
            "INTERSECT devuelve solo los nombres que aparecen en las dos consultas.",
        ),
        cq(
            "bd-47",
            QUE,
            [CLIENTES, PROVEEDORES],
            "SELECT nombre FROM clientes\nEXCEPT\nSELECT nombre FROM proveedores;",
            "Eva",
            ["Tecnofp", "Ana\nLuis", "Eva\nTecnofp"],
            "EXCEPT devuelve lo que está en la primera consulta y no en la segunda. Al revés (proveedores EXCEPT clientes) saldría Tecnofp.",
        ),
        cq(
            "bd-48",
            "¿Qué ocurre al ejecutar esta consulta?",
            [CLIENTES, PROVEEDORES],
            "SELECT id, nombre FROM clientes\nUNION\nSELECT nombre FROM proveedores;",
            "Error",
            ["Ana\nEva\nLuis\nTecnofp", "1 | Ana\n2 | Luis\n3 | Eva", "(sin filas)"],
            "Para combinar selecciones, las dos consultas deben tener el mismo número de columnas. Aquí una tiene 2 y la otra 1.",
        ),
        cq(
            "bd-49",
            QUE,
            [CLIENTES, PEDIDOS],
            "SELECT c.nombre, COALESCE(p.total, 0)\nFROM clientes c LEFT JOIN pedidos p ON p.cliente_id = c.id\nWHERE c.id = 3;",
            "Eva | 0",
            ["Eva | NULL", "(sin filas)", "Error"],
            "Eva no tiene pedidos: el LEFT JOIN la mantiene con `p.total` a NULL, y COALESCE lo sustituye por 0.",
        ),
        cq(
            "bd-50",
            QUE,
            [PRODUCTOS],
            "SELECT nombre FROM productos\nWHERE precio > (SELECT AVG(precio) FROM productos);",
            "Monitor",
            ["Teclado\nMonitor", "Cable\nRatón", "Error"],
            "La subconsulta escalar calcula la media: (25 + 15 + 180 + 5) / 4 = 56,25. Solo el monitor la supera.",
        ),
        cq(
            "bd-51",
            QUE,
            [CLIENTES, PEDIDOS],
            "SELECT nombre FROM clientes\nWHERE id IN (SELECT cliente_id FROM pedidos)\nORDER BY nombre;",
            "Ana\nLuis",
            ["Ana\nAna\nLuis", "Eva", "Ana\nEva\nLuis"],
            "La subconsulta devuelve varias filas (1, 1, 2) e IN comprueba si el id está entre ellas. Cada cliente sale una vez, aunque tenga varios pedidos.",
        ),
        cq(
            "bd-52",
            QUE,
            [CLIENTES, PEDIDOS],
            "SELECT nombre FROM clientes\nWHERE id NOT IN (SELECT cliente_id FROM pedidos);",
            "Eva",
            ["Ana\nLuis", "(sin filas)", "Error"],
            "Los clientes cuyo id no aparece en ningún pedido. Es lo mismo que un LEFT JOIN con `WHERE p.id IS NULL`.",
        ),
        tq(
            "bd-53",
            "¿Qué composición incluye todas las filas de las dos tablas, con NULL donde no hay coincidencia?",
            ["FULL OUTER JOIN", "INNER JOIN", "LEFT JOIN", "RIGHT JOIN"],
            0,
            "LEFT conserva la izquierda; RIGHT, la derecha; FULL OUTER, las dos. INNER solo lo que coincide.",
        ),
        tq(
            "bd-54",
            "`clientes RIGHT JOIN pedidos ON …` da el mismo resultado que…",
            [
                "pedidos LEFT JOIN clientes ON …",
                "clientes LEFT JOIN pedidos ON …",
                "clientes INNER JOIN pedidos ON …",
                "clientes FULL OUTER JOIN pedidos ON …",
            ],
            0,
            "RIGHT JOIN conserva todas las filas de la tabla de la derecha. Cambiando el orden de las tablas se escribe como LEFT JOIN.",
        ),
        tq(
            "bd-55",
            "¿Para qué sirve `EXPLAIN SELECT …`?",
            [
                "Para ver el plan de ejecución: cómo va a hacer el SGBD la consulta y si usa índices",
                "Para que la consulta explique sus resultados en texto",
                "Para ejecutar la consulta sin permisos",
                "Para crear un índice automáticamente",
            ],
            0,
            "El plan de ejecución ayuda a encontrar cuellos de botella, como una búsqueda que recorre toda la tabla porque falta un índice.",
        ),
        tq(
            "bd-56",
            "¿Cuál de estas es una buena práctica para optimizar consultas?",
            [
                "Pedir solo las columnas necesarias en lugar de SELECT *",
                "Crear un índice en todas las columnas",
                "No actualizar nunca las estadísticas",
                "Usar siempre subconsultas en lugar de JOIN",
            ],
            0,
            "Menos columnas, menos datos que procesar. Indexar todo ralentiza las escrituras, las estadísticas deben estar al día y un JOIN suele ser más eficiente.",
        ),
        tq(
            "bd-57",
            "En `SELECT nombre, departamento FROM empleados WHERE departamento = 'Ventas'`, ¿qué parte es la proyección y cuál la selección?",
            [
                "Proyección: nombre, departamento. Selección: el WHERE",
                "Proyección: el WHERE. Selección: nombre, departamento",
                "Las dos son el FROM",
                "Proyección: FROM empleados. Selección: el SELECT",
            ],
            0,
            "Proyectar es elegir columnas; seleccionar es filtrar filas.",
        ),
        fq(
            "bd-58",
            "Completa la consulta para obtener los clientes que no son proveedores.",
            CLIENTES.setup()
            + PROVEEDORES.setup()
            + "SELECT nombre FROM clientes\n___\nSELECT nombre FROM proveedores;",
            ["EXCEPT", "except"],
            "Eva",
            "EXCEPT deja lo que está en la primera consulta y no en la segunda.",
        ),
        oq(
            "bd-59",
            "Ordena las cláusulas para obtener las unidades vendidas por región, en orden alfabético.",
            [
                "SELECT region, SUM(cantidad)",
                "FROM ventas",
                "GROUP BY region",
                "ORDER BY region;",
            ],
            "Norte | 7\nSur | 3",
            "El orden de las cláusulas es fijo: SELECT, FROM, WHERE, GROUP BY, HAVING y ORDER BY.",
            context="CREATE TABLE ventas (region TEXT, cantidad INTEGER);\nINSERT INTO ventas VALUES ('Norte', 5), ('Sur', 3), ('Norte', 2);\n___",
        ),
        bq(
            "bd-60",
            "CREATE TABLE ventas (region TEXT, cantidad INTEGER);\nINSERT INTO ventas VALUES ('Norte', 5), ('Sur', 3), ('Norte', 2);\nSELECT region, SUM(cantidad) FROM ventas\nWHERE SUM(cantidad) > 4 GROUP BY region;",
            3,
            "GROUP BY region HAVING SUM(cantidad) > 4;",
            "Norte | 7",
            "WHERE filtra filas antes de agrupar y no puede usar funciones de agregado. Las condiciones sobre grupos van en HAVING, después del GROUP BY.",
        ),
    ],
    quiz=[
        tq(
            "bd-q07",
            "¿Qué diferencia hay entre UNION y UNION ALL?",
            [
                "UNION quita los duplicados y UNION ALL los conserva",
                "UNION ALL quita los duplicados y UNION los conserva",
                "UNION ALL une todas las tablas de la base de datos",
                "Ninguna",
            ],
            0,
            "UNION ALL es además más rápido, porque no tiene que buscar duplicados.",
        ),
        tq(
            "bd-q08",
            "¿Cuándo se ejecuta una subconsulta escalar dentro de un WHERE?",
            [
                "Primero, y su resultado se usa en la consulta principal",
                "Después de la consulta principal",
                "Solo si la consulta principal no devuelve filas",
                "Nunca: las subconsultas no van en el WHERE",
            ],
            0,
            "La consulta interna calcula el valor (por ejemplo, la media) y la externa lo usa para filtrar.",
        ),
    ],
    sources=[MYSQL, PG],
)


BLOCKS = [
    Block(
        "bd-ud1",
        "UD1 · Almacenamiento de la información",
        "Tipos y modelos de bases de datos, fragmentación, Big Data, ficheros, RGPD y SGBD.",
        15,
        [L_UD1_TIPOS, L_UD1_SGBD],
    ),
    Block(
        "bd-ud2",
        "UD2 · Bases de datos relacionales",
        "Claves, relaciones, NULL, tipos, restricciones, índices, DDL, DCL y vistas.",
        30,
        [L_MODEL, L_CREATE, L_UD2_MAS],
    ),
    Block(
        "bd-ud3",
        "UD3 · Realización de consultas",
        "SELECT, operadores, agrupación, composiciones, UNION/INTERSECT/EXCEPT, subconsultas y optimización.",
        45,
        [L_SELECT, L_WHERE, L_AGG, L_GROUP, L_JOIN, L_LEFT, L_UD3_MAS],
    ),
    Block(
        "bd-ampliacion",
        "Ampliación · Modificar datos y transacciones",
        "INSERT, UPDATE, DELETE y transacciones: lo que viene después de la UD3.",
        10,
        [L_DML, L_TX],
    ),
]

if __name__ == "__main__":
    main("sql", BLOCKS, run_sql, check_example)
