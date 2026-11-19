# ruff: noqa: E501
# (contenido didáctico: los textos largos van en una sola línea para poder leerlos y editarlos)
"""M02 · Fórmulas y funciones básicas (8 h): 4 unidades y 55 ejercicios.

Diseño en docs/excel-academy/CURRICULUM_M1_M2.md §7. Empresas y personas ficticias.
"""

from __future__ import annotations

from units import F, R, T, example, unit

# ---------------------------------------------------------------- xl2-operadores

LINEAS = {
    "A1": "Cantidad",
    "B1": "Precio",
    "C1": "Descuento",
    "A2": 3,
    "B2": 12.5,
    "C2": 0.1,
    "A3": 10,
    "B3": 4,
    "C3": 0,
    "A4": 2,
    "B4": 99.9,
    "C4": 0.25,
}

OPERADORES = unit(
    "xl2-operadores",
    "Fórmulas y operadores",
    hours=2,
    level=2,
    requires=["xl1-referencias"],
    objectives=[
        "Escribir fórmulas con los operadores + - * / ^ % y &.",
        "Aplicar la prioridad de Excel y usar paréntesis para cambiarla.",
        "Explicar por qué `=-2^2` da 4 en Excel.",
    ],
    theory="""
## Una fórmula empieza por =

Todo lo que empieza por `=` es una fórmula: Excel la calcula y la celda muestra el resultado. Sin el `=`, Excel guarda un texto.

## Operadores

| Operador | Hace | Ejemplo | Resultado |
|---|---|---|---|
| `+` `-` | Suma y resta | `=10-4` | 6 |
| `*` `/` | Multiplica y divide | `=10/4` | 2,5 |
| `^` | Potencia | `=2^3` | 8 |
| `%` | Divide entre 100 | `=200*10%` | 20 |
| `&` | Une textos | `="Hola "&"Ana"` | Hola Ana |
| `=` `<>` `<` `>` `<=` `>=` | Compara | `=5>3` | VERDADERO |

## Prioridad: qué se calcula antes

Excel no calcula de izquierda a derecha sin más. Este es su orden, de primero a último:

1. Paréntesis.
2. Negación (el signo `-` delante de un valor).
3. Porcentaje `%`.
4. Potencia `^`.
5. Multiplicación y división, de izquierda a derecha.
6. Suma y resta, de izquierda a derecha.
7. Unir textos `&`.
8. Comparaciones.

Consecuencias que conviene recordar:

- `=2+3*4` da **14** (primero 3 × 4); `=(2+3)*4` da **20**.
- `=-2^2` da **4**: Excel aplica la negación antes que la potencia, así que calcula (−2)². En matemáticas, −2² sería −4. Si quieres −4, escribe `=-(2^2)`.
- `="Total: "&2+3` da **«Total: 5»**: la suma va antes que `&`.

## Una línea de factura, paso a paso

Cantidad en A2, precio en B2 y descuento en C2 (0,1 es un 10 %):

1. Importe sin descuento: `=A2*B2`.
2. La parte que se paga es `1-C2` (el 90 %).
3. Junta las dos con paréntesis: `=A2*B2*(1-C2)`.

Sin paréntesis, `=A2*B2*1-C2` resta el descuento (0,1) al final y da un importe casi entero: un error que no avisa.
""",
    examples=[
        example(
            "xl2-op-ej1",
            "Los paréntesis cambian el orden",
            "=(2+3)*4",
            20,
            "Primero el paréntesis (5) y después × 4. Sin paréntesis daría 14.",
        ),
        example(
            "xl2-op-ej2",
            "Importe de una línea con descuento",
            "=A2*B2*(1-C2)",
            33.75,
            "3 × 12,5 = 37,5; con un 10 % de descuento se paga el 90 %: 37,5 × 0,9 = 33,75.",
            grid=LINEAS,
            cell="D2",
        ),
    ],
    guided="xl2-op-12",
    guided_steps=[
        "Primero, cantidad por precio: A2*B2.",
        "La parte que se paga es 1 menos el descuento: (1-C2). Los paréntesis son obligatorios.",
        "Multiplica las dos partes y copia la fórmula hasta D4.",
    ],
    case=(
        "Caso: las líneas de factura del Taller Montesol",
        """
El Taller Montesol (empresa ficticia) factura piezas con cantidad, precio y un descuento por línea.

1. Escribe cuatro líneas con Cantidad, Precio y Descuento (como 0,1 o 10 %).
2. En la columna Importe calcula cantidad × precio con el descuento aplicado.
3. Añade una columna Concepto que una el nombre de la pieza y la cantidad con `&` («Filtro × 3»).
4. Comprueba una línea a mano con la calculadora.
""",
    ),
    mistakes=[
        (
            "Olvidar los paréntesis: `=A2*B2*1-C2`.",
            "Excel multiplica antes de restar: resta el descuento al final. Escribe `=A2*B2*(1-C2)`.",
        ),
        (
            "Esperar −4 de `=-2^2`.",
            "En Excel la negación va antes que la potencia: da 4. Para −4, `=-(2^2)`.",
        ),
        (
            'Unir textos con `+` (`=A2+" "+B2`).',
            "El `+` intenta sumar y da #¡VALOR!. Para unir textos se usa `&`.",
        ),
    ],
    summary=[
        "Toda fórmula empieza por =.",
        "Orden: paréntesis, negación, %, ^, * /, + -, &, comparaciones.",
        "`=-2^2` da 4 en Excel.",
        "& une textos; las comparaciones devuelven VERDADERO o FALSO.",
    ],
    faq=[
        (
            "¿Puedo poner espacios dentro de una fórmula?",
            "Sí, entre operadores y valores (`= A2 * B2`). Excel los ignora. No dentro de un nombre de celda ni de función.",
        ),
        (
            '¿Por qué ="Total: "&2,5 no muestra el formato de moneda?',
            "Al unir con &, el número se convierte en texto sin formato. Para darle formato al unir hace falta la función TEXTO, que llega en M06.",
        ),
    ],
    sources=[
        (
            "Operadores de cálculo y prioridad",
            "https://support.microsoft.com/es-es/office/operadores-de-c%C3%A1lculo-y-prioridad-36de9366-46fe-43a3-bfa8-cf6d8068eacc",
        ),
        (
            "Información general sobre fórmulas en Excel",
            "https://support.microsoft.com/es-es/office/informaci%C3%B3n-general-sobre-f%C3%B3rmulas-en-excel-ecfdc708-9162-49e8-b993-c311f47ca173",
        ),
    ],
    required=["xl2-op-12"],
    questions=[
        T(
            "xl2-op-01",
            "¿Con qué carácter empieza siempre una fórmula?",
            ["=", "+", "@", "#"],
            0,
            "Sin el =, Excel guarda lo que escribes como texto o como número.",
        ),
        T(
            "xl2-op-02",
            "¿En qué orden calcula Excel `=2+3*4`?",
            [
                "Primero 3*4 y después le suma 2",
                "De izquierda a derecha: 2+3 y luego *4",
                "Primero 2+3",
                "Depende del formato de la celda",
            ],
            0,
            "La multiplicación va antes que la suma: 2 + 12 = 14.",
        ),
        T(
            "xl2-op-03",
            "¿Por qué `=-2^2` da 4 en Excel?",
            [
                "Porque Excel aplica la negación antes que la potencia: (−2)²",
                "Porque Excel calcula mal las potencias",
                "Porque ^ multiplica",
                "Por el formato de la celda",
            ],
            0,
            "En Excel la negación tiene más prioridad que ^. Para −4, `=-(2^2)`.",
        ),
        T(
            "xl2-op-04",
            "¿Qué operador une dos textos?",
            ["&", "+", "*", ";"],
            0,
            '& concatena: `="Taller "&"Montesol"` da «Taller Montesol».',
        ),
        T(
            "xl2-op-05",
            "¿Qué devuelve `=5>3`?",
            ["VERDADERO", "FALSO", "5", "2"],
            0,
            "Una comparación devuelve un valor lógico: VERDADERO o FALSO.",
        ),
        T(
            "xl2-op-06",
            "Cantidad en A2, precio en B2 y descuento en C2 (0,1). ¿Qué fórmula calcula el importe con descuento?",
            ["=A2*B2*(1-C2)", "=A2*B2*1-C2", "=A2*B2-C2", "=A2*(B2-C2)"],
            0,
            "Se paga (1 − descuento) del importe; los paréntesis hacen que la resta vaya primero.",
        ),
        R(
            "xl2-op-07",
            "¿Qué devuelve la fórmula?",
            "=-2^2",
            4,
            "La negación va antes que la potencia: (−2)² = 4.",
        ),
        R(
            "xl2-op-08",
            "¿Qué devuelve la fórmula?",
            "=2+3*4",
            14,
            "Primero 3 × 4 = 12 y después 2 + 12.",
        ),
        R("xl2-op-09", "¿Qué devuelve la fórmula?", "=200*10%", 20, "10 % es 0,1: 200 × 0,1 = 20."),
        R(
            "xl2-op-10",
            "¿Qué devuelve la fórmula? Escribe el texto tal cual.",
            '="Total: "&2+3',
            "Total: 5",
            "La suma va antes que &: 2 + 3 = 5, y después se une con «Total: ».",
            answer_input="text",
        ),
        R(
            "xl2-op-11",
            "¿Qué devuelve la fórmula?",
            "=A2*B2-C2",
            32.5,
            "Primero 3 × 12,5 = 37,5 y después se resta C2 (5): 32,5. Aquí C2 es un importe, no un porcentaje.",
            grid={
                "A1": "Cantidad",
                "B1": "Precio",
                "C1": "Rebaja (€)",
                "A2": 3,
                "B2": 12.5,
                "C2": 5,
            },
        ),
        F(
            "xl2-op-12",
            "Escribe en `D2` el importe de la línea (cantidad × precio con el descuento aplicado), para copiarla hasta `D4`.",
            grid=LINEAS,
            cell="D2",
            expect=33.75,
            checks=[
                {"type": "value"},
                {"type": "fill", "to": "D4", "expect": [40, 149.85]},
                {"type": "variants", "count": 2},
                {"type": "noConstants", "except": [1]},
            ],
            solution="=A2*B2*(1-C2)",
            mistakes=[
                (
                    "=A2*B2*1-C2",
                    "Sin paréntesis, Excel resta el descuento al final: 37,4 en vez de 33,75.",
                ),
                ("=A2*B2", "Falta aplicar el descuento."),
            ],
            hints=[
                "Cantidad por precio: A2*B2.",
                "Se paga 1 menos el descuento: (1-C2). Los paréntesis son imprescindibles.",
            ],
            explain="`=A2*B2*(1-C2)`: 3 × 12,5 × 0,9 = 33,75. Al copiarla, cada línea usa sus celdas.",
            vary=["A2:C4"],
        ),
        R(
            "xl2-op-13",
            "¿Qué devuelve la fórmula?",
            "=10/4*2",
            5,
            "División y multiplicación tienen la misma prioridad y se hacen de izquierda a derecha: 10 / 4 = 2,5 y 2,5 × 2 = 5.",
        ),
        F(
            "xl2-op-14",
            "Escribe en `C2` el precio con IVA (precio × (1 + tipo de `E1`)), para copiarla hasta `C4`.",
            grid={
                "A1": "Pieza",
                "B1": "Precio",
                "A2": "Filtro",
                "B2": 100,
                "A3": "Bujía",
                "B3": 40,
                "A4": "Junta",
                "B4": 12.5,
                "D1": "IVA",
                "E1": 0.21,
            },
            cell="C2",
            expect=121,
            checks=[
                {"type": "value"},
                {"type": "fill", "to": "C4", "expect": [48.4, 15.125]},
                {"type": "references", "must": ["$E$1"]},
                {"type": "noConstants", "except": [1]},
            ],
            solution="=B2*(1+$E$1)",
            mistakes=[
                ("=B2*1+$E$1", "Sin paréntesis suma el tipo (0,21) al final: 100,21."),
                ("=B2*(1+E1)", "Al copiarla, E1 pasa a E2, vacía: el IVA desaparece."),
            ],
            hints=[
                "El precio con IVA es el precio por (1 + tipo).",
                "Pon paréntesis y fija E1 con $.",
            ],
            explain="`=B2*(1+$E$1)`: 100 × 1,21 = 121. El 1 es la única constante permitida.",
        ),
        F(
            "xl2-op-15",
            "Escribe en `C2` el nombre completo (nombre, un espacio y apellido), para copiarla hasta `C4`.",
            grid={
                "A1": "Nombre",
                "B1": "Apellido",
                "A2": "Ana",
                "B2": "Ruiz",
                "A3": "Luis",
                "B3": "Gil",
                "A4": "Marta",
                "B4": "Sanz",
            },
            cell="C2",
            expect="Ana Ruiz",
            checks=[
                {"type": "value"},
                {"type": "fill", "to": "C4", "expect": ["Luis Gil", "Marta Sanz"]},
            ],
            solution='=A2&" "&B2',
            mistakes=[
                ("=A2&B2", "Sin el espacio sale «AnaRuiz»."),
                ('=A2+" "+B2', "El + intenta sumar textos y da #¡VALOR!."),
            ],
            hints=["Para unir textos se usa &.", 'El espacio es un texto: " ".'],
            explain='`=A2&" "&B2`: une el nombre, un espacio y el apellido.',
        ),
    ],
)

# ---------------------------------------------------------------- xl2-estadisticas

SEMESTRE = {
    "A1": "Mes",
    "B1": "Ventas",
    "A2": "Enero",
    "B2": 1200,
    "A3": "Febrero",
    "B3": 950,
    "A4": "Marzo",
    "B4": 1430,
    "A5": "Abril",
    "B5": 1100,
    "A6": "Mayo",
    "B6": 1850,
    "A7": "Junio",
    "B7": 1620,
}
CON_HUECOS = {
    "A1": "Mes",
    "B1": "Ventas",
    "A2": "Enero",
    "B2": 1200,
    "A3": "Febrero",
    "B3": 950,
    "A4": "Marzo",
    "B4": "sin datos",
    "A5": "Abril",
    "A6": "Mayo",
    "B6": 1850,
}

ESTADISTICAS = unit(
    "xl2-estadisticas",
    "SUMA, PROMEDIO, MIN y MAX",
    hours=2,
    level=2,
    requires=["xl2-operadores"],
    objectives=[
        "Usar SUMA, PROMEDIO, MIN y MAX con rangos.",
        "Predecir cómo tratan las celdas vacías y los textos.",
        "Elegir una función en vez de sumar celda a celda.",
    ],
    theory="""
## Cómo se escribe una función

`=NOMBRE(argumento1;argumento2;…)`. En Excel en español los argumentos se separan con **punto y coma**. Un argumento puede ser un número, una celda o un rango: `=SUMA(B2:B7)`, `=SUMA(B2;B5;100)`.

## Las cuatro funciones

| Función | Devuelve | Ejemplo |
|---|---|---|
| `SUMA` | La suma | `=SUMA(B2:B7)` |
| `PROMEDIO` | La media aritmética | `=PROMEDIO(B2:B7)` |
| `MIN` | El valor más pequeño | `=MIN(B2:B7)` |
| `MAX` | El valor más grande | `=MAX(B2:B7)` |

## Vacíos, textos y ceros

Dentro de un rango, las cuatro funciones **ignoran las celdas vacías y los textos**. Un **0 sí cuenta**.

Esto importa sobre todo en `PROMEDIO`: con 1200, 950, «sin datos», una celda vacía y 1850 en `B2:B6`, la media es 4000 / 3 = **1333,33**, no 4000 / 5. Si un mes sin ventas debe contar, escribe 0, no lo dejes vacío.

## Por qué usar SUMA

`=B2+B3+B4+B5+B6+B7` da lo mismo que `=SUMA(B2:B7)`, pero:

- es más larga y es fácil saltarse una celda;
- si insertas una fila dentro del rango, `SUMA` la incluye sola;
- `+` falla con un texto (#¡VALOR!) y `SUMA` lo ignora.

El botón **Autosuma** (Inicio > Edición) escribe `=SUMA(...)` con el rango que cree que quieres: revísalo siempre antes de aceptar.
""",
    examples=[
        example(
            "xl2-est-ej1",
            "PROMEDIO ignora textos y vacías",
            "=PROMEDIO(B2:B4)",
            400,
            "Solo hay dos números (300 y 500): (300 + 500) / 2 = 400. «pendiente» no cuenta.",
            grid={
                "A1": "Mes",
                "B1": "Ventas",
                "A2": "Julio",
                "B2": 300,
                "A3": "Agosto",
                "B3": "pendiente",
                "A4": "Septiembre",
                "B4": 500,
            },
        ),
        example(
            "xl2-est-ej2",
            "Total del trimestre",
            "=SUMA(B2:B4)",
            800,
            "SUMA suma los números del rango e ignora el texto: 300 + 500.",
            grid={
                "A1": "Mes",
                "B1": "Ventas",
                "A2": "Julio",
                "B2": 300,
                "A3": "Agosto",
                "B3": "pendiente",
                "A4": "Septiembre",
                "B4": 500,
            },
        ),
    ],
    guided="xl2-est-09",
    guided_steps=[
        "Busca el rango con las ventas de los seis meses: de B2 a B7.",
        "Escribe =SUMA( y selecciona el rango.",
        "Cierra el paréntesis y comprueba que el rango incluye junio.",
    ],
    case=(
        "Caso: las ventas del semestre de una tienda",
        """
Una tienda de bicicletas (ficticia) tiene sus ventas de enero a junio en `B2:B7`.

1. Escribe los seis meses con sus ventas.
2. Debajo calcula el total, la media, el peor mes y el mejor mes, cada uno con su función.
3. Borra las ventas de un mes: ¿qué cambia en la media? Escribe 0 en su lugar: ¿y ahora?
4. Inserta una fila en mitad del rango con un mes nuevo y comprueba que el total la incluye.
""",
    ),
    mistakes=[
        (
            "Dejar fuera del rango la última fila (`=SUMA(B2:B6)` en vez de `B2:B7`).",
            "Revisa siempre el rango, sobre todo el que propone Autosuma.",
        ),
        (
            "Creer que PROMEDIO divide entre el número de filas.",
            "Divide entre el número de celdas con números: las vacías y los textos no cuentan.",
        ),
        (
            "Separar los argumentos con coma (`=SUMA(B2,B5)`).",
            "En Excel en español el separador es el punto y coma: `=SUMA(B2;B5)`.",
        ),
    ],
    summary=[
        "Sintaxis: =FUNCIÓN(arg1;arg2), con punto y coma.",
        "SUMA, PROMEDIO, MIN y MAX ignoran vacías y textos de un rango; el 0 cuenta.",
        "PROMEDIO divide entre las celdas con números.",
        "Revisa siempre el rango de la función.",
    ],
    faq=[
        (
            "¿Qué devuelve MIN si el rango no tiene números?",
            "0. Y PROMEDIO de un rango sin números da #¡DIV/0!, porque no puede dividir entre 0.",
        ),
        (
            "¿Puedo mezclar rangos y celdas sueltas?",
            "Sí: `=SUMA(B2:B7;D2;100)` suma el rango, D2 y 100.",
        ),
    ],
    sources=[
        ("Función SUMA", "https://support.microsoft.com/es-es/excel/functions/sum-function"),
        (
            "Función PROMEDIO",
            "https://support.microsoft.com/es-es/office/promedio-funci%C3%B3n-promedio-047bac88-d466-426c-a32b-8f33eb960cf6",
        ),
        (
            "Función MIN",
            "https://support.microsoft.com/es-es/office/funci%C3%B3n-min-61635d12-920f-4ce2-a70f-96f202dcc152",
        ),
        (
            "Función MAX",
            "https://support.microsoft.com/es-es/office/funci%C3%B3n-max-e0012414-9ac8-4b34-9a47-73e662c08098",
        ),
    ],
    required=["xl2-est-09"],
    questions=[
        T(
            "xl2-est-01",
            "En Excel en español, ¿qué separa los argumentos de una función?",
            [
                "El punto y coma: =SUMA(B2;B5)",
                "La coma: =SUMA(B2,B5)",
                "El punto: =SUMA(B2.B5)",
                "Un espacio",
            ],
            0,
            "La coma es el separador decimal en español, así que los argumentos se separan con ;.",
        ),
        T(
            "xl2-est-02",
            "`B2:B5` tiene 10, 20, una celda vacía y 30. ¿Qué devuelve `=PROMEDIO(B2:B5)`?",
            ["20", "15", "30", "60"],
            0,
            "La vacía no cuenta: (10 + 20 + 30) / 3 = 20.",
        ),
        T(
            "xl2-est-03",
            "¿Qué hace SUMA con un texto que está dentro del rango?",
            ["Lo ignora", "Da #¡VALOR!", "Lo cuenta como 1", "Lo convierte siempre en número"],
            0,
            "Las funciones ignoran el texto de un rango; el operador + no.",
        ),
        T(
            "xl2-est-04",
            "¿Qué ventaja tiene `=SUMA(B2:B7)` frente a `=B2+B3+B4+B5+B6+B7`?",
            [
                "Es más corta y, si insertas una fila dentro del rango, la incluye sola",
                "Es más precisa con los decimales",
                "Redondea el resultado",
                "Permite sumar textos",
            ],
            0,
            "El resultado es el mismo, pero SUMA es más fácil de leer y de mantener.",
        ),
        T(
            "xl2-est-05",
            "`A1:A4` tiene 5, −2, una celda vacía y 8. ¿Qué devuelve `=MIN(A1:A4)`?",
            ["−2", "0", "5", "8"],
            0,
            "La vacía no cuenta como 0: el mínimo de 5, −2 y 8 es −2.",
        ),
        T(
            "xl2-est-06",
            "En un PROMEDIO, ¿qué diferencia hay entre una celda con 0 y una vacía?",
            [
                "El 0 cuenta y baja la media; la vacía no cuenta",
                "Ninguna de las dos cuenta",
                "Las dos cuentan igual",
                "La vacía cuenta como 0",
            ],
            0,
            "Si un mes sin ventas tiene que contar en la media, escribe 0.",
        ),
        R(
            "xl2-est-07",
            "B4 tiene el texto «sin datos» y B5 está vacía. ¿Qué devuelve la fórmula? (Dos decimales)",
            "=PROMEDIO(B2:B6)",
            1333.33,
            "Solo cuentan los tres números: (1200 + 950 + 1850) / 3 = 1333,33.",
            grid=CON_HUECOS,
        ),
        R(
            "xl2-est-08",
            "¿Qué devuelve la fórmula?",
            "=SUMA(B2:B6)",
            4000,
            "1200 + 950 + 1850; el texto y la vacía se ignoran.",
            grid=CON_HUECOS,
        ),
        F(
            "xl2-est-09",
            "Escribe en `B8` el total de ventas del semestre con la función SUMA.",
            grid=SEMESTRE,
            cell="B8",
            expect=8150,
            checks=[
                {"type": "value"},
                {"type": "variants", "count": 2},
                {"type": "functions", "requires": ["SUM"]},
            ],
            solution="=SUMA(B2:B7)",
            mistakes=[
                ("=SUMA(B2:B6)", "El rango deja fuera junio: 6530."),
                ("=B2+B3+B4+B5+B6+B7", "Da el total, pero el ejercicio pide usar SUMA."),
            ],
            hints=["Las ventas van de B2 a B7.", "=SUMA(rango)."],
            explain="`=SUMA(B2:B7)`: 8150. Comprueba siempre que el rango llega hasta el último mes.",
            vary=["B2:B7"],
        ),
        R(
            "xl2-est-10",
            "¿Qué devuelve la fórmula?",
            "=MIN(B2:B6)",
            950,
            "El texto y la vacía no cuentan: el mínimo de 1200, 950 y 1850 es 950.",
            grid=CON_HUECOS,
        ),
        R(
            "xl2-est-11",
            "¿Qué devuelve la fórmula?",
            "=MAX(B2:B6)",
            1850,
            "El valor más grande de los números del rango.",
            grid=CON_HUECOS,
        ),
        R(
            "xl2-est-12",
            "C3 tiene un 0 y C5 está vacía. ¿Qué devuelve la fórmula?",
            "=PROMEDIO(C2:C5)",
            10,
            "El 0 cuenta y la vacía no: (10 + 0 + 20) / 3 = 10.",
            grid={"C1": "Ventas", "C2": 10, "C3": 0, "C4": 20},
        ),
        F(
            "xl2-est-13",
            "Escribe en `B8` la media mensual de ventas del semestre con la función PROMEDIO.",
            grid=SEMESTRE,
            cell="B8",
            expect=1358.3333333333333,
            checks=[
                {"type": "value"},
                {"type": "variants", "count": 2},
                {"type": "functions", "requires": ["AVERAGE"]},
            ],
            solution="=PROMEDIO(B2:B7)",
            mistakes=[
                ("=PROMEDIO(B2:B6)", "El rango deja fuera junio."),
                ("=SUMA(B2:B7)/6", "Da la media, pero el ejercicio pide usar PROMEDIO."),
            ],
            hints=["Las ventas van de B2 a B7.", "=PROMEDIO(rango)."],
            explain="`=PROMEDIO(B2:B7)`: 8150 / 6 = 1358,33.",
            vary=["B2:B7"],
        ),
        F(
            "xl2-est-14",
            "Escribe en `E2` la mejor venta del semestre con la función MAX.",
            grid={**SEMESTRE, "B6": 1620, "B7": 1850, "D2": "Mejor mes"},
            cell="E2",
            expect=1850,
            checks=[
                {"type": "value"},
                {"type": "variants", "count": 2},
                {"type": "functions", "requires": ["MAX"]},
            ],
            solution="=MAX(B2:B7)",
            mistakes=[
                ("=MAX(B2:B6)", "El rango deja fuera junio, que es el mejor mes."),
                ("=MIN(B2:B7)", "MIN da la peor venta, no la mejor."),
            ],
            hints=["Las ventas van de B2 a B7.", "=MAX(rango)."],
            explain="`=MAX(B2:B7)`: 1850, la venta de junio.",
            vary=["B2:B7"],
        ),
    ],
)

# ---------------------------------------------------------------- xl2-contar

FACTURAS = {"A1": "Factura", "A2": "F-001", "A3": 120, "A5": "pendiente", "A6": 80}

CONTAR = unit(
    "xl2-contar",
    "CONTAR, CONTARA, PRODUCTO y REDONDEAR",
    hours=2,
    level=2,
    requires=["xl2-estadisticas"],
    objectives=[
        "Distinguir CONTAR (cuenta números) de CONTARA (cuenta celdas no vacías).",
        "Multiplicar un rango con PRODUCTO.",
        "Redondear el valor con REDONDEAR, frente a solo cambiar los decimales que se ven.",
    ],
    theory="""
## Contar

| Función | Cuenta | `A2:A6` = «F-001», 120, vacía, «pendiente», 80 |
|---|---|---|
| `CONTAR` | Celdas con **números** (y fechas) | **2** |
| `CONTARA` | Celdas **no vacías** (números, textos, errores…) | **4** |

Úsalas así: `CONTAR` para saber cuántos importes hay; `CONTARA` para saber cuántas filas tienen algo escrito.

## PRODUCTO

`=PRODUCTO(A2:C2)` multiplica los números del rango (ignora textos y vacías). Con 3, 12,5 y 0,9 da **33,75**. Es lo mismo que `=A2*B2*C2`, pero más corto cuando hay muchos factores.

## REDONDEAR

`=REDONDEAR(número;núm_decimales)` **cambia el valor**, no solo cómo se ve:

| Fórmula | Resultado | Por qué |
|---|---|---|
| `=REDONDEAR(4,1979;2)` | 4,2 | A céntimos |
| `=REDONDEAR(2,5;0)` | 3 | A entero; el 5 sube |
| `=REDONDEAR(-2,5;0)` | −3 | El 5 se aleja del cero |
| `=REDONDEAR(1234,567;-2)` | 1200 | A centenas |

Con decimales negativos redondea a la izquierda de la coma: −1 a decenas, −2 a centenas.

## Formato frente a REDONDEAR

Si el IVA de una línea es 4,1979 y solo reduces decimales, se **ve** 4,20 pero se **suma** 4,1979. En una factura con muchas líneas, el total que se ve puede no coincidir con la suma de lo que se ve. Por eso es habitual redondear el IVA de cada línea a céntimos: `=REDONDEAR(B2*$E$1;2)`.
""",
    examples=[
        example(
            "xl2-con-ej1",
            "CONTAR solo cuenta números",
            "=CONTAR(A2:A4)",
            2,
            "101 y 102 son números; «anulada» es texto y no cuenta.",
            grid={"A1": "Factura", "A2": 101, "A3": "anulada", "A4": 102},
        ),
        example(
            "xl2-con-ej2",
            "IVA redondeado a céntimos",
            "=REDONDEAR(19,99*0,21;2)",
            4.2,
            "19,99 × 0,21 = 4,1979, que redondeado a dos decimales es 4,20.",
        ),
    ],
    guided="xl2-con-11",
    guided_steps=[
        "Primero el IVA sin redondear: B2*$E$1 (con E1 fijo).",
        "Mételo dentro de REDONDEAR con 2 decimales: REDONDEAR(…;2).",
        "Copia la fórmula hasta C4 y comprueba los céntimos.",
    ],
    case=(
        "Caso: recuento de facturas y redondeo del IVA",
        """
La gestoría revisa el libro de facturas de un cliente: hay números de factura, importes, celdas con «anulada» y filas en blanco.

1. Cuenta cuántas facturas tienen importe (CONTAR) y cuántas filas tienen algo escrito (CONTARA).
2. Calcula el IVA de cada línea redondeado a céntimos con REDONDEAR.
3. Suma el IVA con y sin redondear: ¿coinciden?
4. Aplica formato de 2 decimales a la columna sin redondear y compara lo que se ve con lo que se suma.
""",
    ),
    mistakes=[
        (
            "Usar CONTARA para contar importes.",
            "CONTARA cuenta también los textos («anulada»). Para números, CONTAR.",
        ),
        (
            "Creer que reducir decimales redondea.",
            "Solo cambia lo que se ve. Para cambiar el valor, REDONDEAR.",
        ),
        (
            "Olvidar fijar la tasa dentro de REDONDEAR (`=REDONDEAR(B2*E1;2)`).",
            "Al copiarla, E1 se desplaza. Escribe `=REDONDEAR(B2*$E$1;2)`.",
        ),
    ],
    summary=[
        "CONTAR: números. CONTARA: no vacías.",
        "PRODUCTO multiplica los números de un rango.",
        "REDONDEAR(número;decimales) cambia el valor; el 5 se aleja del cero.",
        "Redondea el IVA por línea para que lo que se ve cuadre con lo que se suma.",
    ],
    faq=[
        (
            "¿Hay funciones para redondear siempre hacia arriba o hacia abajo?",
            "Sí: REDONDEAR.MAS y REDONDEAR.MENOS. Llegan en un módulo posterior; en este solo se usa REDONDEAR.",
        ),
        (
            "¿CONTARA cuenta una celda con un espacio?",
            "Sí: un espacio es un texto y la celda no está vacía. Es un error frecuente en datos copiados.",
        ),
    ],
    sources=[
        ("Función CONTAR", "https://support.microsoft.com/es-es/excel/functions/count-function"),
        (
            "Función CONTARA",
            "https://support.microsoft.com/es-es/office/funci%C3%B3n-contara-7dc98875-d5c1-46f1-9a82-53f3219e2509",
        ),
        ("Función PRODUCTO", "https://support.microsoft.com/es-ES/Excel/product-function"),
        (
            "Función REDONDEAR",
            "https://support.microsoft.com/es-es/office/redondear-funci%C3%B3n-redondear-c018c5d8-40fb-4053-90b1-b3e7f61a213c",
        ),
    ],
    required=["xl2-con-11"],
    questions=[
        T(
            "xl2-con-01",
            "¿Qué diferencia hay entre CONTAR y CONTARA?",
            [
                "CONTAR cuenta celdas con números; CONTARA, celdas que no están vacías",
                "Son iguales",
                "CONTAR cuenta textos y CONTARA números",
                "CONTARA solo cuenta celdas vacías",
            ],
            0,
            "CONTARA cuenta todo lo que no esté vacío: números, textos y errores.",
        ),
        T(
            "xl2-con-02",
            "`A1:A5` tiene «Ana», 3, una celda vacía, 0 y «No». ¿Qué devuelve `=CONTARA(A1:A5)`?",
            ["4", "2", "5", "3"],
            0,
            "Cuatro celdas no están vacías. El 0 es un valor y cuenta.",
        ),
        T(
            "xl2-con-03",
            "¿Qué hace REDONDEAR con `núm_decimales` igual a 0?",
            [
                "Redondea a un número entero",
                "Quita los decimales sin redondear",
                "Da un error",
                "Devuelve 0",
            ],
            0,
            "`=REDONDEAR(2,5;0)` da 3 y `=REDONDEAR(2,4;0)` da 2.",
        ),
        T(
            "xl2-con-04",
            "¿En qué se diferencia «Disminuir decimales» de REDONDEAR?",
            [
                "Disminuir decimales solo cambia lo que se ve; REDONDEAR cambia el valor guardado",
                "Son lo mismo",
                "REDONDEAR solo cambia lo que se ve",
                "Disminuir decimales es más exacto",
            ],
            0,
            "Los cálculos usan el valor guardado: solo REDONDEAR lo cambia.",
        ),
        T(
            "xl2-con-05",
            "`A1:A3` tiene 2, una celda vacía y 5. ¿Qué devuelve `=PRODUCTO(A1:A3)`?",
            ["10", "0", "7", "2"],
            0,
            "PRODUCTO ignora la celda vacía: 2 × 5 = 10. En cambio, `=A1*A2*A3` daría 0.",
        ),
        T(
            "xl2-con-06",
            "¿Qué devuelve `=REDONDEAR(-2,5;0)`?",
            ["−3", "−2", "2", "3"],
            0,
            "REDONDEAR aleja el 5 del cero: −2,5 pasa a −3.",
        ),
        R(
            "xl2-con-07",
            "¿Qué devuelve la fórmula?",
            "=CONTAR(A2:A6)",
            2,
            "Solo 120 y 80 son números.",
            grid=FACTURAS,
        ),
        R(
            "xl2-con-08",
            "¿Qué devuelve la fórmula?",
            "=CONTARA(A2:A6)",
            4,
            "Cuatro celdas no están vacías: «F-001», 120, «pendiente» y 80.",
            grid=FACTURAS,
        ),
        R(
            "xl2-con-09",
            "¿Qué devuelve la fórmula?",
            "=PRODUCTO(A2:C2)",
            33.75,
            "3 × 12,5 × 0,9 = 33,75.",
            grid={"A1": "Cantidad", "B1": "Precio", "C1": "Pagas", "A2": 3, "B2": 12.5, "C2": 0.9},
        ),
        R(
            "xl2-con-10",
            "¿Qué devuelve la fórmula?",
            "=REDONDEAR(1234,567;-2)",
            1200,
            "Con −2 decimales redondea a centenas: 1234,567 queda en 1200.",
        ),
        F(
            "xl2-con-11",
            "Escribe en `C2` el IVA de la línea (precio × tipo de `E1`) **redondeado a céntimos**, para copiarla hasta `C4`.",
            grid={
                "A1": "Concepto",
                "B1": "Precio",
                "A2": "Cable",
                "B2": 19.99,
                "A3": "Clavija",
                "B3": 7.4,
                "A4": "Router",
                "B4": 133.33,
                "D1": "IVA",
                "E1": 0.21,
            },
            cell="C2",
            expect=4.2,
            tolerance=0.0001,
            checks=[
                {"type": "value"},
                {"type": "fill", "to": "C4", "expect": [1.55, 28]},
                {"type": "functions", "requires": ["ROUND"]},
                {"type": "references", "must": ["$E$1"]},
            ],
            solution="=REDONDEAR(B2*$E$1;2)",
            mistakes=[
                (
                    "=B2*$E$1",
                    "Sin redondear da 4,1979: se ve 4,20 con formato, pero el valor no está redondeado.",
                ),
                ("=REDONDEAR(B2*E1;2)", "Al copiarla, E1 pasa a E2, vacía."),
            ],
            hints=[
                "Primero el IVA: B2*$E$1.",
                "Mételo en REDONDEAR con 2 decimales: =REDONDEAR(…;2).",
            ],
            explain="`=REDONDEAR(B2*$E$1;2)`: 4,1979 pasa a 4,20; 1,554 a 1,55; 27,9993 a 28,00.",
        ),
        R(
            "xl2-con-12",
            "¿Qué devuelve la fórmula?",
            "=REDONDEAR(4,1979;2)",
            4.2,
            "A dos decimales: el tercer decimal es 7, así que el 9 sube y queda 4,20.",
            tolerance=0.0001,
        ),
        F(
            "xl2-con-13",
            "Escribe en `B8` cuántas facturas tienen **importe** (número) con la función CONTAR.",
            grid={
                "A1": "Factura",
                "B1": "Importe",
                "A2": "F-001",
                "B2": 120,
                "A3": "F-002",
                "B3": "pendiente",
                "A4": "F-003",
                "B4": 95,
                "A6": "F-005",
                "B6": 300,
                "A7": "F-006",
                "B7": "anulada",
            },
            cell="B8",
            expect=3,
            checks=[{"type": "value"}, {"type": "functions", "requires": ["COUNT"]}],
            solution="=CONTAR(B2:B7)",
            mistakes=[
                ("=CONTARA(B2:B7)", "CONTARA cuenta también «pendiente» y «anulada»: 5."),
                ("=CONTAR(B2:B5)", "El rango deja fuera las dos últimas filas."),
            ],
            hints=["Los importes están en B2:B7.", "CONTAR cuenta solo los números."],
            explain="`=CONTAR(B2:B7)`: 120, 95 y 300 son números; los textos y la vacía no cuentan.",
        ),
        F(
            "xl2-con-14",
            "Escribe en `D2` el importe de la línea multiplicando cantidad, precio y factor de IVA con la función PRODUCTO, para copiarla hasta `D4`.",
            grid={
                "A1": "Cantidad",
                "B1": "Precio",
                "C1": "Con IVA",
                "A2": 4,
                "B2": 2.5,
                "C2": 1.21,
                "A3": 2,
                "B3": 19.9,
                "C3": 1.21,
                "A4": 10,
                "B4": 0.75,
                "C4": 1.21,
            },
            cell="D2",
            expect=12.1,
            checks=[
                {"type": "value"},
                {"type": "fill", "to": "D4", "expect": [48.158, 9.075]},
                {"type": "functions", "requires": ["PRODUCT"]},
            ],
            solution="=PRODUCTO(A2:C2)",
            mistakes=[
                ("=SUMA(A2:C2)", "SUMA suma, no multiplica."),
                ("=PRODUCTO(A2:B2)", "Falta el factor de IVA de la columna C."),
            ],
            hints=["Los tres factores están en A2:C2.", "=PRODUCTO(rango)."],
            explain="`=PRODUCTO(A2:C2)`: 4 × 2,5 × 1,21 = 12,1.",
        ),
    ],
)

# ---------------------------------------------------------------- xl2-hojas

TRIMESTRE = {
    "Enero!A5": "Ventas",
    "Enero!B5": 4200,
    "Febrero!A5": "Ventas",
    "Febrero!B5": 3900,
    "Marzo!A5": "Ventas",
    "Marzo!B5": 4650,
    "A2": "Total del trimestre",
}

HOJAS = unit(
    "xl2-hojas",
    "Referencias entre hojas",
    hours=2,
    level=3,
    requires=["xl2-operadores", "xl1-referencias"],
    objectives=[
        "Escribir referencias a otra hoja, como `Enero!B5` y `'Primer trimestre'!B5`.",
        "Construir un resumen con datos de varias hojas.",
        "Saber qué son las referencias 3D, aunque PLD no las corrija.",
    ],
    theory="""
## Hoja!Celda

Para usar una celda de otra hoja se escribe el nombre de la hoja, un signo de exclamación y la celda: `=Enero!B5`. Sin nombre de hoja, la referencia es de la hoja donde está la fórmula: en la hoja Resumen, `=B5` es `Resumen!B5`.

Si el nombre de la hoja tiene **espacios** u otros caracteres especiales, va entre **comillas simples**: `='Primer trimestre'!B5`.

No hace falta escribirlo a mano: escribe `=`, haz clic en la pestaña de la otra hoja, haz clic en la celda y pulsa Intro. Excel escribe la referencia, con comillas si hacen falta.

## Un resumen trimestral, paso a paso

Las hojas Enero, Febrero y Marzo tienen las ventas del mes en `B5`. En la hoja Resumen:

1. Escribe `=` en `B2`.
2. Clic en la pestaña Enero, clic en `B5`, escribe `+`.
3. Lo mismo con Febrero y Marzo. Intro: `=Enero!B5+Febrero!B5+Marzo!B5`.

También vale `=SUMA(Enero!B5;Febrero!B5;Marzo!B5)`. Y un rango de otra hoja: `=SUMA(Enero!B2:B4)`.

## Si cambias o borras hojas

- Si **renombras** una hoja, Excel actualiza solo todas las fórmulas que la usan.
- Si **borras** una hoja que usaba una fórmula, la fórmula da `#¡REF!`.

## Referencias 3D (información)

Excel permite `=SUMA(Enero:Marzo!B5)`: suma `B5` de Enero, de Marzo y de todas las hojas que estén **entre** ellas en el orden de las pestañas. Es cómodo, pero mover una hoja de sitio cambia el resultado sin avisar. **El corrector de PLD no las admite todavía**: si la escribes en un ejercicio, te dirá que no está soportada.
""",
    examples=[
        example(
            "xl2-hoj-ej1",
            "Sumar dos hojas desde Resumen",
            "=Enero!B5+Febrero!B5",
            8100,
            "Enero!B5 (4200) + Febrero!B5 (3900).",
            grid=TRIMESTRE,
            sheet="Resumen",
            cell="B3",
        ),
        example(
            "xl2-hoj-ej2",
            "Una hoja con espacios en el nombre",
            "='Primer trimestre'!B5*2",
            25500,
            "Las comillas simples son obligatorias porque el nombre tiene un espacio: 12 750 × 2.",
            grid={"'Primer trimestre'!B5": 12750},
            sheet="Resumen",
        ),
    ],
    guided="xl2-hoj-08",
    guided_steps=[
        "Cada mes está en su hoja, en la celda B5.",
        "Escribe el nombre de la hoja, ! y la celda: Enero!B5.",
        "Suma los tres meses.",
    ],
    case=(
        "Caso: el resumen trimestral del Taller Montesol",
        """
El taller lleva una hoja por mes (Enero, Febrero, Marzo) con la misma estructura: las ventas en `B5` y los gastos en `B6`.

1. Crea las tres hojas con sus ventas y gastos y una hoja Resumen.
2. En Resumen calcula el total de ventas, el de gastos y el resultado (ventas − gastos) del trimestre.
3. Cambia el nombre de la hoja Enero por «Ene»: ¿qué les pasa a las fórmulas?
4. Haz una copia del libro y borra la hoja Febrero en la copia: ¿qué aparece en Resumen?
""",
    ),
    mistakes=[
        (
            "Escribir `=B5+B5+B5` en Resumen.",
            "Sin nombre de hoja, las tres son Resumen!B5. Escribe `=Enero!B5+Febrero!B5+Marzo!B5`.",
        ),
        (
            "Olvidar las comillas en una hoja con espacios (`=Primer trimestre!B5`).",
            "Escribe `='Primer trimestre'!B5`, o haz clic en la celda y deja que Excel la escriba.",
        ),
        (
            "Borrar una hoja que otras fórmulas usan.",
            "Las fórmulas pasan a #¡REF!. Antes de borrar, busca qué la usa (Fórmulas > Rastrear dependientes).",
        ),
    ],
    summary=[
        "Otra hoja: Hoja!Celda (Enero!B5).",
        "Con espacios, entre comillas simples: 'Primer trimestre'!B5.",
        "Renombrar una hoja actualiza las fórmulas; borrarla da #¡REF!.",
        "Las referencias 3D existen, pero PLD aún no las corrige.",
    ],
    faq=[
        (
            "¿Puedo referenciar otro libro?",
            "Sí, con un vínculo de libro (`=[Ventas.xlsx]Enero!B5`). Se ve en módulos posteriores; aquí todo está en el mismo libro.",
        ),
        (
            "¿Por qué PLD no corrige las referencias 3D?",
            "El motor de PLD es propio y de momento solo admite referencias de una hoja. Está previsto para más adelante.",
        ),
    ],
    sources=[
        (
            "Crear o modificar una referencia de celda",
            "https://support.microsoft.com/es-es/office/crear-o-modificar-una-referencia-de-celda-c7b8b95d-c594-4488-947e-c835903cebaa",
        ),
        (
            "Crear una referencia al mismo rango de celdas en varias hojas de cálculo",
            "https://support.microsoft.com/es-es/office/crear-una-referencia-al-mismo-rango-de-celdas-en-varias-hojas-de-c%C3%A1lculo-c906f8b4-c648-4aa0-8063-65d38d03370f",
        ),
    ],
    required=["xl2-hoj-08"],
    questions=[
        T(
            "xl2-hoj-01",
            "¿Cómo se escribe la celda `B5` de la hoja **Enero**?",
            ["Enero!B5", "B5!Enero", "Enero.B5", "[Enero]B5"],
            0,
            "Primero la hoja, después ! y la celda.",
        ),
        T(
            "xl2-hoj-02",
            "¿Cómo se escribe la celda `B5` de la hoja **Primer trimestre**?",
            [
                "'Primer trimestre'!B5",
                "Primer trimestre!B5",
                '"Primer trimestre"!B5',
                "(Primer trimestre)!B5",
            ],
            0,
            "Con espacios en el nombre, la hoja va entre comillas simples.",
        ),
        T(
            "xl2-hoj-03",
            "En la hoja Resumen escribes `=B5`. ¿A qué celda se refiere?",
            [
                "A Resumen!B5",
                "A la B5 de la primera hoja del libro",
                "A la B5 de todas las hojas",
                "A ninguna: da error",
            ],
            0,
            "Sin nombre de hoja, la referencia es de la hoja donde está la fórmula.",
        ),
        T(
            "xl2-hoj-04",
            "Borras la hoja Febrero, que usaba la fórmula `=Enero!B5+Febrero!B5`. ¿Qué pasa?",
            [
                "La fórmula da #¡REF!",
                "Excel suma solo Enero",
                "La fórmula se borra",
                "No pasa nada",
            ],
            0,
            "La referencia apunta a una hoja que ya no existe: #¡REF!.",
        ),
        T(
            "xl2-hoj-05",
            "Cambias el nombre de la hoja Enero a «Ene». ¿Qué pasa con `=Enero!B5`?",
            [
                "Excel la cambia sola a =Ene!B5",
                "Da #¡REF!",
                "Da #¿NOMBRE?",
                "Sigue poniendo Enero y da 0",
            ],
            0,
            "Excel actualiza las referencias cuando se renombra una hoja.",
        ),
        T(
            "xl2-hoj-06",
            "¿Qué hace `=SUMA(Enero:Marzo!B5)` en Excel?",
            [
                "Suma B5 de Enero, de Marzo y de todas las hojas que hay entre ellas",
                "Suma solo B5 de Enero y de Marzo",
                "Da error siempre",
                "Suma B5 de la hoja activa",
            ],
            0,
            "Es una referencia 3D: incluye las hojas que estén entre las dos en el orden de las pestañas. PLD aún no la corrige.",
        ),
        R(
            "xl2-hoj-07",
            "¿Qué devuelve la fórmula?",
            "='Hoja 2'!A1*2",
            30,
            "'Hoja 2'!A1 vale 15: 15 × 2 = 30. Las comillas son por el espacio del nombre.",
            grid={"'Hoja 2'!A1": 15},
        ),
        F(
            "xl2-hoj-08",
            "En la hoja **Resumen**, escribe en `B2` el total de ventas del trimestre (la celda `B5` de las hojas Enero, Febrero y Marzo).",
            grid=TRIMESTRE,
            sheet="Resumen",
            cell="B2",
            expect=12750,
            checks=[
                {"type": "value"},
                {"type": "variants", "count": 2},
                {"type": "references", "must": ["Enero!B5", "Febrero!B5", "Marzo!B5"]},
            ],
            solution="=Enero!B5+Febrero!B5+Marzo!B5",
            mistakes=[
                ("=B5+B5+B5", "Sin nombre de hoja las tres son Resumen!B5, que está vacía: 0."),
                ("=Enero!B5+Febrero!B5", "Falta marzo."),
            ],
            hints=[
                "Cada mes está en la celda B5 de su hoja.",
                "Escribe la hoja, ! y la celda: Enero!B5.",
                "También vale SUMA con las tres referencias separadas por ;.",
            ],
            explain="`=Enero!B5+Febrero!B5+Marzo!B5` o `=SUMA(Enero!B5;Febrero!B5;Marzo!B5)`: 12 750.",
            vary=["Enero!B5", "Febrero!B5", "Marzo!B5"],
        ),
        R(
            "xl2-hoj-09",
            "¿Qué devuelve la fórmula?",
            "=SUMA(Enero!B2:B4)",
            600,
            "Un rango de otra hoja se escribe igual: la hoja y el rango. 100 + 200 + 300.",
            grid={"Enero!B2": 100, "Enero!B3": 200, "Enero!B4": 300},
            sheet="Resumen",
        ),
        R(
            "xl2-hoj-10",
            "¿Qué devuelve la fórmula?",
            "=Ventas!B2-Gastos!B2",
            1100,
            "4200 de Ventas menos 3100 de Gastos.",
            grid={"Ventas!B2": 4200, "Gastos!B2": 3100},
            sheet="Resumen",
        ),
        F(
            "xl2-hoj-11",
            "En la hoja **Resumen**, escribe en `B3` los gastos del semestre: la celda `C10` de las hojas «Primer trimestre» y «Segundo trimestre».",
            grid={
                "'Primer trimestre'!C10": 2300,
                "'Segundo trimestre'!C10": 2750,
                "A3": "Gastos del semestre",
            },
            sheet="Resumen",
            cell="B3",
            expect=5050,
            checks=[{"type": "value"}, {"type": "variants", "count": 2}],
            solution="='Primer trimestre'!C10+'Segundo trimestre'!C10",
            mistakes=[
                (
                    "=Primer trimestre!C10+Segundo trimestre!C10",
                    "Sin comillas simples Excel no entiende un nombre de hoja con espacios.",
                ),
                ("=C10+C10", "Sin nombre de hoja son Resumen!C10, vacía."),
            ],
            hints=[
                "Los nombres tienen espacios: van entre comillas simples.",
                "'Primer trimestre'!C10.",
            ],
            explain="`='Primer trimestre'!C10+'Segundo trimestre'!C10`: 2300 + 2750 = 5050.",
            vary=["'Primer trimestre'!C10", "'Segundo trimestre'!C10"],
        ),
        F(
            "xl2-hoj-12",
            "En la hoja **Resumen**, escribe en `B4` la venta media diaria de la hoja Enero (rango `B2:B6`) con PROMEDIO.",
            grid={
                "Enero!A1": "Día",
                "Enero!B1": "Ventas",
                "Enero!B2": 310,
                "Enero!B3": 285,
                "Enero!B4": 402,
                "Enero!B5": 198,
                "Enero!B6": 355,
                "A4": "Media de enero",
            },
            sheet="Resumen",
            cell="B4",
            expect=310,
            checks=[
                {"type": "value"},
                {"type": "variants", "count": 2},
                {"type": "functions", "requires": ["AVERAGE"]},
            ],
            solution="=PROMEDIO(Enero!B2:B6)",
            mistakes=[
                ("=PROMEDIO(B2:B6)", "Sin la hoja es el rango de Resumen, vacío: #¡DIV/0!."),
                ("=SUMA(Enero!B2:B6)", "SUMA da el total, no la media."),
            ],
            hints=["El rango está en otra hoja: Enero!B2:B6.", "=PROMEDIO(…)."],
            explain="`=PROMEDIO(Enero!B2:B6)`: 1550 / 5 = 310.",
            vary=["Enero!B2:B6"],
        ),
    ],
)

UNITS = [OPERADORES, ESTADISTICAS, CONTAR, HOJAS]
