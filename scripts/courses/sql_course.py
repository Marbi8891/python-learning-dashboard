# ruff: noqa: E501
# (contenido didáctico: los textos largos van en una sola línea para poder leerlos y editarlos)
"""Curso de SQL (módulo Bases de datos de DAW) para la app Android (ADR-0016).

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

BLOCKS = [
    Block(
        "consultas",
        "Consultas básicas",
        "SELECT, filtros, orden y límites.",
        30,
        [L_SELECT, L_WHERE],
    ),
    Block(
        "agregacion",
        "Agregados y agrupación",
        "COUNT, SUM, AVG, GROUP BY y HAVING.",
        20,
        [L_AGG, L_GROUP],
    ),
    Block(
        "joins",
        "Combinaciones y subconsultas",
        "INNER JOIN, LEFT JOIN y consultas anidadas.",
        25,
        [L_JOIN, L_LEFT],
    ),
    Block(
        "ddl-dml",
        "Crear y modificar datos",
        "CREATE TABLE, restricciones, INSERT, UPDATE y DELETE.",
        15,
        [L_CREATE, L_DML],
    ),
    Block(
        "diseno",
        "Diseño y transacciones",
        "Modelo relacional, normalización, transacciones, vistas e índices.",
        10,
        [L_MODEL, L_TX],
    ),
]

if __name__ == "__main__":
    main("sql", BLOCKS, run_sql, check_example)
