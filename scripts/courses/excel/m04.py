# ruff: noqa: E501
# (contenido didáctico: los textos largos van en una sola línea para poder leerlos y editarlos)
"""M04 · Funciones lógicas (4 h): 2 unidades y 30 ejercicios.

Diseño en docs/excel-academy/CURRICULUM_M3_M5.md. Empresas y personas ficticias.
"""

from __future__ import annotations

from units import F, R, T, example, unit

# ---------------------------------------------------------------- xl4-si

FACTURAS = {
    "A1": "Factura",
    "B1": "Importe",
    "C1": "Cobrado",
    "A2": "F-101",
    "B2": 250,
    "C2": 250,
    "A3": "F-102",
    "B3": 480,
    "C3": 200,
    "A4": "F-103",
    "B4": 90,
    "C4": 120,
    "A5": "F-104",
    "B5": 310,
    "C5": 0,
}

VENTAS = {
    "A1": "Comercial",
    "B1": "Ventas",
    "A2": "Ana",
    "B2": 12000,
    "A3": "Luis",
    "B3": 8000,
    "A4": "Marta",
    "B4": 10000,
    "D1": "Objetivo",
    "E1": 10000,
    "D2": "Comisión",
    "E2": 0.05,
}

SI = unit(
    "xl4-si",
    "SI y comparaciones",
    hours=2,
    level=2,
    requires=["xl2-operadores", "xl1-referencias"],
    objectives=[
        "Escribir comparaciones con = <> < > <= >= y saber que devuelven VERDADERO o FALSO.",
        "Usar SI para devolver un valor u otro según una condición.",
        "Poner los umbrales en celdas de datos y fijarlos con $ al copiar.",
        "Evitar #¡DIV/0! comprobando el divisor con SI.",
    ],
    theory="""
## Una comparación devuelve VERDADERO o FALSO

| Operador | Significa | `=B2>=100` con B2 = 100 |
|---|---|---|
| `=` | igual | |
| `<>` | distinto | |
| `<` `>` | menor, mayor | |
| `<=` `>=` | menor o igual, mayor o igual | VERDADERO |

Los textos se comparan **sin distinguir mayúsculas**: `="pagada"="PAGADA"` da VERDADERO. Un texto siempre va entre comillas: `=C2="Pagada"`.

## La función SI

```
=SI(prueba_lógica; valor_si_verdadero; valor_si_falso)
```

- **prueba_lógica**: una comparación, como `C2>=B2`.
- **valor_si_verdadero**: lo que devuelve si se cumple. Puede ser un número, un texto entre comillas o un cálculo.
- **valor_si_falso**: lo que devuelve si no se cumple.

`=SI(C2>=B2;"Cobrada";"Pendiente")` escribe «Cobrada» si lo cobrado llega al importe y «Pendiente» si no.

Si omites el tercer argumento (`=SI(C2>=B2;"Cobrada")`) y la condición no se cumple, SI devuelve **FALSO**: casi nunca es lo que quieres. Escribe siempre los tres.

## Umbrales en celdas, no dentro de la fórmula

Una comisión del 5 % para quien llegue a 10.000 € se puede escribir `=SI(B2>=10000;B2*0,05;0)`, pero si mañana el objetivo cambia hay que tocar todas las fórmulas. Mejor pon el objetivo en E1 y el porcentaje en E2:

```
=SI(B2>=$E$1;B2*$E$2;0)
```

Los `$` mantienen E1 y E2 fijas al copiar la fórmula hacia abajo (xl1-referencias).

## SI solo calcula la parte que toca

Si B2 vale 0, `=A2/B2` da #¡DIV/0!. Con SI puedes evitarlo:

```
=SI(B2=0;0;A2/B2)
```

Cuando B2 es 0, SI devuelve 0 y **ni siquiera calcula** `A2/B2`, así que no hay error.
""",
    examples=[
        example(
            "xl4-si-ej1",
            "Estado de una factura",
            '=SI(C2>=B2;"Cobrada";"Pendiente")',
            "Cobrada",
            "Lo cobrado (250) llega al importe (250): la condición se cumple y devuelve «Cobrada».",
            grid=FACTURAS,
            cell="D2",
        ),
        example(
            "xl4-si-ej2",
            "Comisión con el objetivo en una celda",
            "=SI(B2>=$E$1;B2*$E$2;0)",
            600,
            "Ana vende 12.000, que llega al objetivo de 10.000: cobra 12.000 × 5 % = 600.",
            grid=VENTAS,
            cell="C2",
        ),
    ],
    guided="xl4-si-12",
    guided_steps=[
        "La condición compara lo cobrado (C2) con el importe (B2): C2>=B2.",
        "Si se cumple, el texto «Cobrada»; si no, «Pendiente». Los textos van entre comillas.",
        "Escribe los tres argumentos separados por punto y coma y copia la fórmula hasta D5.",
    ],
    case=(
        "Caso: el control de cobros del Taller Montesol",
        """
El Taller Montesol (empresa ficticia) quiere saber de un vistazo qué facturas están cobradas.

1. Escribe diez facturas con número, importe y cantidad cobrada.
2. En la columna Estado, «Cobrada» si lo cobrado llega al importe y «Pendiente» si no.
3. En otra columna, lo que falta por cobrar: el importe menos lo cobrado, o 0 si ya está cobrada.
4. Pon en una celda un importe mínimo para reclamar (por ejemplo, 100 €) y marca «Reclamar» en las pendientes que lo superen.
""",
    ),
    mistakes=[
        (
            "Escribir los textos sin comillas: `=SI(C2>=B2;Cobrada;Pendiente)`.",
            "Sin comillas Excel busca un nombre «Cobrada» y da #¿NOMBRE?. Los textos van entre comillas.",
        ),
        (
            "Usar `>` cuando la regla dice «llega a» o «al menos».",
            "«Al menos 100» es `>=100`. Con `>` se quedan fuera los que valen justo 100.",
        ),
        (
            "Escribir el umbral dentro de la fórmula (`B2>=10000`).",
            "Ponlo en una celda y fíjala con $: `B2>=$E$1`. Si cambia, solo tocas una celda.",
        ),
        (
            "Omitir el valor si falso.",
            'SI devuelve FALSO cuando no se cumple. Escribe siempre el tercer argumento (por ejemplo, 0 o "").',
        ),
    ],
    summary=[
        "Las comparaciones devuelven VERDADERO o FALSO.",
        "=SI(prueba; si verdadero; si falso). Escribe siempre los tres.",
        "Los textos entre comillas; las mayúsculas no cuentan al comparar.",
        "Umbrales en celdas fijadas con $.",
        "=SI(B2=0;0;A2/B2) evita #¡DIV/0!: SI solo calcula la rama que toca.",
    ],
    faq=[
        (
            "¿Cómo dejo la celda vacía si no se cumple?",
            'Con dos comillas seguidas: `=SI(C2>=B2;"Cobrada";"")`. La celda parece vacía, aunque contiene un texto vacío.',
        ),
        (
            "¿Puedo poner un SI dentro de otro?",
            "Sí (SI anidados), pero se leen mal a partir de dos. Para varios tramos, la unidad siguiente enseña SI.CONJUNTO.",
        ),
    ],
    sources=[
        ("SI (función SI)", "https://support.microsoft.com/es-es/excel/functions/if-function"),
        (
            "Función SI: fórmulas anidadas y cómo evitar problemas",
            "https://support.microsoft.com/es-es/excel/if-function-nested-formulas-and-avoiding-pitfalls",
        ),
        (
            "Operadores de cálculo y prioridad",
            "https://support.microsoft.com/es-es/office/operadores-de-c%C3%A1lculo-y-prioridad-36de9366-46fe-43a3-bfa8-cf6d8068eacc",
        ),
    ],
    required=["xl4-si-12", "xl4-si-13"],
    questions=[
        T(
            "xl4-si-01",
            "¿Qué devuelve `=B2>=100` si B2 vale 100?",
            ["VERDADERO", "FALSO", "100", "#¡VALOR!"],
            0,
            "100 es mayor o igual que 100.",
        ),
        T(
            "xl4-si-02",
            "¿Qué fórmula escribe «Aprobado» si la nota de B2 es al menos 5 y «Suspenso» si no?",
            [
                '=SI(B2>=5;"Aprobado";"Suspenso")',
                '=SI(B2>5;"Aprobado";"Suspenso")',
                "=SI(B2>=5;Aprobado;Suspenso)",
                '=SI("Aprobado";B2>=5;"Suspenso")',
            ],
            0,
            "«Al menos 5» es >=5, los textos van entre comillas y la condición es el primer argumento.",
        ),
        T(
            "xl4-si-03",
            '¿Qué devuelve `=SI(B2>100;"Alto")` si B2 vale 50?',
            ["FALSO", "Una celda vacía", '"Alto"', "#N/D"],
            0,
            "Sin tercer argumento, SI devuelve FALSO cuando la condición no se cumple.",
        ),
        T(
            "xl4-si-04",
            '¿Qué devuelve `="pagada"="PAGADA"`?',
            ["VERDADERO", "FALSO", "#¡VALOR!", "0"],
            0,
            "Las comparaciones de texto no distinguen mayúsculas.",
        ),
        T(
            "xl4-si-05",
            "El objetivo de ventas está en E1 y vas a copiar la fórmula hacia abajo. ¿Cómo escribes la condición?",
            ["B2>=$E$1", "B2>=E1", "B2>=10000", "$B$2>=E1"],
            0,
            "E1 tiene que quedarse fija al copiar ($E$1); B2 tiene que cambiar en cada fila.",
        ),
        T(
            "xl4-si-06",
            "¿Por qué `=SI(B2=0;0;A2/B2)` no da #¡DIV/0! cuando B2 vale 0?",
            [
                "Porque SI solo calcula la rama que toca y no llega a dividir",
                "Porque Excel ignora los errores dentro de SI",
                "Porque 0 entre 0 da 0 en Excel",
                "Sí da #¡DIV/0!",
            ],
            0,
            "Cuando la condición se cumple, SI devuelve 0 sin calcular A2/B2.",
        ),
        R(
            "xl4-si-07",
            "¿Qué devuelve la fórmula? Escribe el texto tal cual.",
            '=SI(C3>=B3;"Cobrada";"Pendiente")',
            "Pendiente",
            "Se han cobrado 200 de 480: no llega, así que devuelve «Pendiente».",
            grid=FACTURAS,
            cell="D3",
            answer_input="text",
        ),
        R(
            "xl4-si-08",
            "¿Qué devuelve la fórmula?",
            "=SI(B3>=$E$1;B3*$E$2;0)",
            0,
            "Luis vende 8.000, que no llega al objetivo de 10.000: la comisión es 0.",
            grid=VENTAS,
            cell="C3",
        ),
        R(
            "xl4-si-09",
            "¿Qué devuelve la fórmula?",
            "=SI(B4>=$E$1;B4*$E$2;0)",
            500,
            "Marta vende justo 10.000: con >= llega al objetivo y cobra 10.000 × 5 % = 500.",
            grid=VENTAS,
            cell="C4",
        ),
        R(
            "xl4-si-10",
            "¿Qué devuelve la fórmula?",
            "=SI(B5-C5>0;B5-C5;0)",
            310,
            "Falta por cobrar 310 − 0 = 310, que es mayor que 0.",
            grid=FACTURAS,
            cell="E5",
        ),
        R(
            "xl4-si-11",
            "Elige lo que devuelve la fórmula.",
            "=SI(B2=0;0;A2/B2)",
            0,
            "B2 vale 0: SI devuelve 0 y no llega a dividir.",
            grid={"A1": "Total", "B1": "Unidades", "A2": 150, "B2": 0},
            cell="C2",
            options=[0, {"error": "#¡DIV/0!"}, 150, False],
        ),
        F(
            "xl4-si-12",
            "Escribe en `D2` el estado de la factura: «Cobrada» si lo cobrado (C) llega al importe (B) y «Pendiente» si no. Cópiala hasta `D5`.",
            grid=FACTURAS,
            cell="D2",
            expect="Cobrada",
            checks=[
                {"type": "value"},
                {"type": "fill", "to": "D5", "expect": ["Pendiente", "Cobrada", "Pendiente"]},
                {"type": "functions", "requires": ["IF"]},
            ],
            solution='=SI(C2>=B2;"Cobrada";"Pendiente")',
            mistakes=[
                (
                    '=SI(C2>B2;"Cobrada";"Pendiente")',
                    "Con > la factura F-101, cobrada justo por su importe, sale «Pendiente».",
                ),
                ('=SI(C2>=B2;"Pendiente";"Cobrada")', "Los dos textos están al revés."),
            ],
            hints=[
                "La condición es C2>=B2.",
                'Después, "Cobrada" y "Pendiente", entre comillas y separados por punto y coma.',
            ],
            explain='`=SI(C2>=B2;"Cobrada";"Pendiente")`: F-101 (250 de 250) está cobrada; F-102 y F-104 no; F-103 sí (120 de 90).',
        ),
        F(
            "xl4-si-13",
            "Escribe en `C2` la comisión: si las ventas llegan al objetivo de `E1`, ventas × el porcentaje de `E2`; si no, 0. Cópiala hasta `C4`.",
            grid=VENTAS,
            cell="C2",
            expect=600,
            checks=[
                {"type": "value"},
                {"type": "fill", "to": "C4", "expect": [0, 500]},
                {"type": "references", "must": ["$E$1", "$E$2"]},
                {"type": "noConstants", "except": [0]},
                {"type": "variants", "count": 2},
            ],
            solution="=SI(B2>=$E$1;B2*$E$2;0)",
            mistakes=[
                (
                    "=SI(B2>=E1;B2*E2;0)",
                    "Sin $, al copiarla E1 y E2 pasan a E2 y E3 y las comisiones salen mal.",
                ),
                (
                    "=SI(B2>=10000;B2*0,05;0)",
                    "Los datos están en E1 y E2: si cambian, esta fórmula se queda vieja.",
                ),
                (
                    "=SI(B2>$E$1;B2*$E$2;0)",
                    "Con > Marta, que vende justo el objetivo, se queda sin comisión.",
                ),
            ],
            hints=[
                "La condición es B2>=$E$1.",
                "Si se cumple, B2*$E$2; si no, 0.",
            ],
            explain="`=SI(B2>=$E$1;B2*$E$2;0)`: Ana 600, Luis 0 y Marta 500.",
            vary=["B2:B4"],
        ),
        F(
            "xl4-si-14",
            "Escribe en `C2` el precio medio por unidad (total entre unidades), pero 0 si no hay unidades, para que no salga #¡DIV/0!. Cópiala hasta `C4`.",
            grid={
                "A1": "Total",
                "B1": "Unidades",
                "A2": 150,
                "B2": 6,
                "A3": 80,
                "B3": 0,
                "A4": 99,
                "B4": 4,
            },
            cell="C2",
            expect=25,
            checks=[
                {"type": "value"},
                {"type": "fill", "to": "C4", "expect": [0, 24.75]},
                {"type": "functions", "requires": ["IF"]},
            ],
            solution="=SI(B2=0;0;A2/B2)",
            mistakes=[
                ("=A2/B2", "Cuando no hay unidades (fila 3) da #¡DIV/0!."),
                ("=SI(B2=0;A2/B2;0)", "Las ramas están al revés: divide justo cuando B2 es 0."),
            ],
            hints=[
                "Primero comprueba si B2 es 0.",
                "Si lo es, 0; si no, A2/B2.",
            ],
            explain="`=SI(B2=0;0;A2/B2)`: 150/6 = 25, la fila sin unidades da 0 y 99/4 = 24,75.",
        ),
        F(
            "xl4-si-15",
            "Escribe en `D2` lo que falta por cobrar: el importe (B) menos lo cobrado (C), o 0 si ya se ha cobrado todo o más. Cópiala hasta `D5`.",
            grid=FACTURAS,
            cell="D2",
            expect=0,
            checks=[
                {"type": "value"},
                {"type": "fill", "to": "D5", "expect": [280, 0, 310]},
                {"type": "noConstants", "except": [0]},
            ],
            solution="=SI(C2>=B2;0;B2-C2)",
            mistakes=[
                (
                    "=B2-C2",
                    "En F-103 se cobró de más y saldría −30: lo pendiente no puede ser negativo.",
                ),
                ("=SI(C2>=B2;0;C2-B2)", "La resta está al revés: da negativos."),
            ],
            hints=[
                "Si lo cobrado llega al importe, no falta nada: 0.",
                "Si no, el importe menos lo cobrado.",
            ],
            explain="`=SI(C2>=B2;0;B2-C2)` (o `=SI(B2-C2>0;B2-C2;0)`): F-101 0, F-102 280, F-103 0 y F-104 310.",
        ),
    ],
)

# ---------------------------------------------------------------- xl4-logicas

PLANTILLA = {
    "A1": "Empleado",
    "B1": "Ventas",
    "C1": "Años",
    "A2": "Ana",
    "B2": 12000,
    "C2": 3,
    "A3": "Luis",
    "B3": 15000,
    "C3": 1,
    "A4": "Marta",
    "B4": 9000,
    "C4": 5,
    "A5": "Pablo",
    "B5": 10000,
    "C5": 2,
    "E1": "Objetivo",
    "F1": 10000,
    "E2": "Años mínimos",
    "F2": 2,
}

PEDIDOS = {
    "A1": "Pedido",
    "B1": "Importe",
    "C1": "Cliente",
    "A2": "P-1",
    "B2": 65,
    "C2": "Normal",
    "A3": "P-2",
    "B3": 30,
    "C3": "Premium",
    "A4": "P-3",
    "B4": 20,
    "C4": "Normal",
    "A5": "P-4",
    "B5": 50,
    "C5": "Normal",
    "E1": "Envío gratis desde",
    "F1": 50,
    "E2": "Precio del envío",
    "F2": 4.95,
}

NOTAS = {
    "A1": "Alumno",
    "B1": "Nota",
    "A2": "Irene",
    "B2": 9.5,
    "A3": "Hugo",
    "B3": 7,
    "A4": "Sara",
    "B4": 4.9,
    "A5": "Tomás",
    "B5": 5,
}

LOGICAS = unit(
    "xl4-logicas",
    "Y, O, NO, SI.CONJUNTO y SI.ERROR",
    hours=2,
    level=3,
    requires=["xl4-si"],
    objectives=[
        "Combinar condiciones con Y (todas), O (al menos una) y NO.",
        "Clasificar en varios tramos con SI.CONJUNTO, con un «en otro caso» final.",
        "Capturar un error esperado con SI.ERROR sin esconder errores de verdad.",
        "Elegir entre SI anidados y SI.CONJUNTO pensando en quién leerá la fórmula.",
    ],
    theory="""
## Y, O y NO

| Función | Devuelve VERDADERO si… | Ejemplo |
|---|---|---|
| `Y(c1; c2; …)` | **todas** las condiciones se cumplen | `=Y(B2>=$F$1;C2>=$F$2)` |
| `O(c1; c2; …)` | **al menos una** se cumple | `=O(B2>=$F$1;C2="Premium")` |
| `NO(c)` | la condición **no** se cumple | `=NO(C2="Baja")` |

Solas devuelven VERDADERO o FALSO, así que casi siempre van dentro de un SI:

```
=SI(Y(B2>=$F$1;C2>=$F$2);"Sí";"No")
```

Un error frecuente es escribir `=SI(B2>=10000 Y C2>=2;…)`: en Excel, Y es una función y las condiciones van dentro de sus paréntesis.

## SI.CONJUNTO: varios tramos sin anidar [2019+]

Para clasificar una nota en Sobresaliente, Notable, Aprobado o Suspenso, con SI anidados:

```
=SI(B2>=9;"Sobresaliente";SI(B2>=7;"Notable";SI(B2>=5;"Aprobado";"Suspenso")))
```

Con **SI.CONJUNTO** se escriben parejas *condición; valor*, y se devuelve el valor de la **primera** condición que se cumple:

```
=SI.CONJUNTO(B2>=9;"Sobresaliente";B2>=7;"Notable";B2>=5;"Aprobado";VERDADERO;"Suspenso")
```

- El orden importa: de mayor a menor. Si empiezas por `B2>=5`, un 9,5 se queda en «Aprobado».
- Si ninguna condición se cumple, da **#N/D**. Por eso la última pareja suele ser `VERDADERO;"…"`: el «en otro caso».
- SI.CONJUNTO existe desde Excel 2019. En versiones anteriores la fórmula da #¿NOMBRE?.

## SI.ERROR

```
=SI.ERROR(valor; valor_si_error)
```

Devuelve el valor normal o, si es un error (#¡DIV/0!, #N/D, #¡VALOR!…), lo que pongas como segundo argumento. `=SI.ERROR(A2/B2;0)` da 0 cuando B2 vale 0.

**Cuidado:** SI.ERROR esconde **cualquier** error, también los que indican un fallo de verdad (un texto donde debería haber un número, una referencia rota). Úsalo solo cuando sepas qué error esperas y por qué; si no, el error te está avisando de algo. Cuando puedas, prefiere una comprobación concreta: `=SI(B2=0;0;A2/B2)` solo evita la división entre cero.
""",
    examples=[
        example(
            "xl4-log-ej1",
            "Dos condiciones a la vez",
            '=SI(Y(B2>=$F$1;C2>=$F$2);"Sí";"No")',
            "Sí",
            "Ana vende 12.000 (llega al objetivo) y lleva 3 años (al menos 2): se cumplen las dos.",
            grid=PLANTILLA,
            cell="D2",
        ),
        example(
            "xl4-log-ej2",
            "Tramos con SI.CONJUNTO",
            '=SI.CONJUNTO(B3>=9;"Sobresaliente";B3>=7;"Notable";B3>=5;"Aprobado";VERDADERO;"Suspenso")',
            "Notable",
            "Un 7 no llega a 9, pero sí a 7: la primera condición que se cumple es la segunda.",
            grid=NOTAS,
            cell="C3",
        ),
    ],
    guided="xl4-log-12",
    guided_steps=[
        "Las dos condiciones son: ventas >= objetivo ($F$1) y años >= años mínimos ($F$2).",
        "Tienen que cumplirse las dos: van dentro de Y(…; …).",
        'Mete el Y en un SI que devuelva "Sí" o "No" y cópiala hasta D5.',
    ],
    case=(
        "Caso: incentivos y envíos en la Clínica Dental Ribera",
        """
La Clínica Dental Ribera (empresa ficticia) vende productos de higiene en su web y reparte incentivos a la plantilla.

1. Con una tabla de empleados (ventas y años en la empresa), marca con «Sí» a quien cumpla el objetivo de ventas **y** lleve al menos dos años.
2. Con una tabla de pedidos, calcula el envío: gratis si el pedido llega a 50 € **o** el cliente es Premium; si no, 4,95 €. Pon 50 y 4,95 en celdas.
3. Clasifica la valoración de cada cliente (de 0 a 10) en Excelente, Buena, Regular o Mala con SI.CONJUNTO.
4. Calcula el precio por unidad de cada pedido y usa SI.ERROR solo donde un pedido sin unidades sea normal. Escribe al lado por qué.
""",
    ),
    mistakes=[
        (
            "Escribir Y como una palabra entre condiciones: `B2>=10000 Y C2>=2`.",
            "Y es una función: `Y(B2>=10000;C2>=2)`.",
        ),
        (
            "Confundir Y con O.",
            "Y exige que se cumplan todas; O, que se cumpla al menos una. Léelo en voz alta: «ventas suficientes y antigüedad» es Y.",
        ),
        (
            "Ordenar los tramos de SI.CONJUNTO de menor a mayor.",
            "Gana la primera condición que se cumple: con `B2>=5` primero, un 9,5 sale «Aprobado». Ordena de mayor a menor.",
        ),
        (
            "Olvidar el «en otro caso» de SI.CONJUNTO.",
            'Si no se cumple ninguna condición da #N/D. Termina con `VERDADERO;"…"`.',
        ),
        (
            "Poner SI.ERROR en todas las fórmulas «por si acaso».",
            "Esconde errores que te avisan de datos mal escritos. Úsalo solo para un error que esperas, y mejor con una comprobación concreta.",
        ),
    ],
    summary=[
        "Y: todas; O: al menos una; NO: lo contrario.",
        "Y, O y NO suelen ir dentro de un SI.",
        "SI.CONJUNTO: parejas condición; valor, de mayor a menor, con VERDADERO al final.",
        "SI.ERROR captura cualquier error: úsalo con cabeza.",
    ],
    faq=[
        (
            "Mi Excel no tiene SI.CONJUNTO. ¿Qué hago?",
            "Existe desde Excel 2019. En versiones anteriores usa SI anidados: el resultado es el mismo.",
        ),
        (
            "¿Cuántas condiciones admite Y?",
            "Hasta 255. Pero si necesitas más de tres o cuatro, seguramente te conviene una columna auxiliar o una tabla de criterios.",
        ),
    ],
    sources=[
        (
            "Usar SI con las funciones Y, O y NO en Excel",
            "https://support.microsoft.com/es-es/excel/using-if-with-and-or-and-not-functions-in-excel",
        ),
        ("Función SI.CONJUNTO", "https://support.microsoft.com/es-es/excel/functions/ifs-function"),
        (
            "SI.ERROR (función SI.ERROR)",
            "https://support.microsoft.com/es-ES/Excel/iferror-function",
        ),
    ],
    required=["xl4-log-12", "xl4-log-14"],
    questions=[
        T(
            "xl4-log-01",
            "¿Qué devuelve `=Y(5>3;2>4)`?",
            ["FALSO", "VERDADERO", "#¡VALOR!", "1"],
            0,
            "Y necesita que se cumplan todas; 2>4 no se cumple.",
        ),
        T(
            "xl4-log-02",
            "¿Qué devuelve `=O(5>3;2>4)`?",
            ["VERDADERO", "FALSO", "#¡VALOR!", "2"],
            0,
            "O necesita que se cumpla al menos una; 5>3 se cumple.",
        ),
        T(
            "xl4-log-03",
            "El envío es gratis si el pedido llega a 50 € **o** el cliente es Premium. ¿Qué condición usas?",
            [
                'O(B2>=50;C2="Premium")',
                'Y(B2>=50;C2="Premium")',
                'B2>=50 O C2="Premium"',
                'NO(B2>=50;C2="Premium")',
            ],
            0,
            "Basta con una de las dos: O. Y es una función, no una palabra entre condiciones.",
        ),
        T(
            "xl4-log-04",
            '¿Qué devuelve `=SI.CONJUNTO(B2>=9;"A";B2>=5;"B")` si B2 vale 3?',
            ["#N/D", '"B"', "FALSO", "Una celda vacía"],
            0,
            'Ninguna condición se cumple. Para evitarlo, añade VERDADERO;"…" al final.',
        ),
        T(
            "xl4-log-05",
            '¿Por qué está mal `=SI.CONJUNTO(B2>=5;"Aprobado";B2>=7;"Notable";B2>=9;"Sobresaliente";VERDADERO;"Suspenso")`?',
            [
                "Porque gana la primera condición que se cumple: un 9,5 sale «Aprobado»",
                "Porque SI.CONJUNTO no admite VERDADERO",
                "Porque faltan comillas en las condiciones",
                "No está mal",
            ],
            0,
            "Con tramos «mayor o igual», ordena de mayor a menor.",
        ),
        T(
            "xl4-log-06",
            "¿Cuándo está justificado usar SI.ERROR?",
            [
                "Cuando esperas un error concreto, sabes por qué ocurre y quieres mostrar otra cosa",
                "Siempre, para que la hoja no muestre errores",
                "Nunca: Excel no tiene esa función",
                "Solo con textos",
            ],
            0,
            "SI.ERROR esconde cualquier error, también los que te avisan de un fallo.",
        ),
        R(
            "xl4-log-07",
            "¿Qué devuelve la fórmula? Escribe el texto tal cual.",
            '=SI(Y(B3>=$F$1;C3>=$F$2);"Sí";"No")',
            "No",
            "Luis vende 15.000 (sí llega), pero lleva 1 año (no llega a 2): con Y hace falta todo.",
            grid=PLANTILLA,
            cell="D3",
            answer_input="text",
        ),
        R(
            "xl4-log-08",
            "¿Qué devuelve la fórmula?",
            '=SI(O(B3>=$F$1;C3="Premium");0;$F$2)',
            0,
            "El pedido P-2 es de 30 € (no llega a 50), pero el cliente es Premium: con O basta, el envío es gratis.",
            grid=PEDIDOS,
            cell="D3",
        ),
        R(
            "xl4-log-09",
            "¿Qué devuelve la fórmula?",
            '=SI(O(B4>=$F$1;C4="Premium");0;$F$2)',
            4.95,
            "P-3 es de 20 € y el cliente es Normal: no se cumple ninguna, así que paga 4,95.",
            grid=PEDIDOS,
            cell="D4",
        ),
        R(
            "xl4-log-10",
            "¿Qué devuelve la fórmula? Escribe el texto tal cual.",
            '=SI.CONJUNTO(B4>=9;"Sobresaliente";B4>=7;"Notable";B4>=5;"Aprobado";VERDADERO;"Suspenso")',
            "Suspenso",
            "Un 4,9 no llega a 5: ninguna de las tres primeras se cumple y gana VERDADERO.",
            grid=NOTAS,
            cell="C4",
            answer_input="text",
        ),
        R(
            "xl4-log-11",
            "Elige lo que devuelve la fórmula.",
            '=SI.ERROR(B2*C2;"Revisar")',
            0,
            "C2 contiene el texto «seis», así que B2*C2 da #¡VALOR! y SI.ERROR lo cambia por «Revisar». Fíjate en que aquí el error avisaba de un dato mal escrito.",
            grid={
                "A1": "Producto",
                "B1": "Precio",
                "C1": "Unidades",
                "A2": "Cepillo",
                "B2": 3.5,
                "C2": "seis",
            },
            cell="D2",
            options=["Revisar", {"error": "#¡VALOR!"}, 21, 0],
        ),
        F(
            "xl4-log-12",
            "Escribe en `D2` «Sí» si el empleado llega al objetivo de ventas de `F1` **y** lleva al menos los años de `F2`; si no, «No». Cópiala hasta `D5`.",
            grid=PLANTILLA,
            cell="D2",
            expect="Sí",
            checks=[
                {"type": "value"},
                {"type": "fill", "to": "D5", "expect": ["No", "No", "Sí"]},
                {"type": "references", "must": ["$F$1", "$F$2"]},
                {"type": "functions", "requires": ["IF", "AND"]},
            ],
            solution='=SI(Y(B2>=$F$1;C2>=$F$2);"Sí";"No")',
            mistakes=[
                (
                    '=SI(O(B2>=$F$1;C2>=$F$2);"Sí";"No")',
                    "Con O, Luis (1 año) y Marta (9.000 €) también tendrían incentivo.",
                ),
                (
                    '=SI(Y(B2>$F$1;C2>$F$2);"Sí";"No")',
                    "Con > Pablo, que llega justo a las dos cifras, se queda fuera.",
                ),
                (
                    '=SI(Y(B2>=F1;C2>=F2);"Sí";"No")',
                    "Sin $, al copiarla F1 y F2 se mueven y las condiciones dejan de tener sentido.",
                ),
            ],
            hints=[
                "Las dos condiciones: B2>=$F$1 y C2>=$F$2.",
                'Van dentro de Y(…;…), y el Y dentro de un SI con "Sí" y "No".',
            ],
            explain='`=SI(Y(B2>=$F$1;C2>=$F$2);"Sí";"No")`: Ana y Pablo sí; Luis no llega en años y Marta no llega en ventas.',
        ),
        F(
            "xl4-log-13",
            "Escribe en `D2` el precio del envío: 0 si el pedido llega al importe de `F1` **o** el cliente es «Premium»; si no, el precio de `F2`. Cópiala hasta `D5`.",
            grid=PEDIDOS,
            cell="D2",
            expect=0,
            checks=[
                {"type": "value"},
                {"type": "fill", "to": "D5", "expect": [0, 4.95, 0]},
                {"type": "references", "must": ["$F$1", "$F$2"]},
                {"type": "functions", "requires": ["IF", "OR"]},
                {"type": "noConstants", "except": [0]},
            ],
            solution='=SI(O(B2>=$F$1;C2="Premium");0;$F$2)',
            mistakes=[
                (
                    '=SI(Y(B2>=$F$1;C2="Premium");0;$F$2)',
                    "Con Y solo sería gratis para pedidos grandes de clientes Premium.",
                ),
                (
                    '=SI(O(B2>$F$1;C2="Premium");0;$F$2)',
                    "Con > el pedido P-4, de 50 € justos, pagaría envío.",
                ),
            ],
            hints=[
                'Basta con una de las dos condiciones: O(B2>=$F$1;C2="Premium").',
                "Si se cumple, 0; si no, $F$2.",
            ],
            explain='`=SI(O(B2>=$F$1;C2="Premium");0;$F$2)`: P-1 y P-4 llegan al importe, P-2 es Premium y solo P-3 paga 4,95.',
        ),
        F(
            "xl4-log-14",
            "Escribe en `C2` la calificación con SI.CONJUNTO: «Sobresaliente» desde 9, «Notable» desde 7, «Aprobado» desde 5 y «Suspenso» en otro caso. Cópiala hasta `C5`.",
            grid=NOTAS,
            cell="C2",
            expect="Sobresaliente",
            checks=[
                {"type": "value"},
                {"type": "fill", "to": "C5", "expect": ["Notable", "Suspenso", "Aprobado"]},
                {"type": "functions", "requires": ["IFS"]},
            ],
            solution='=SI.CONJUNTO(B2>=9;"Sobresaliente";B2>=7;"Notable";B2>=5;"Aprobado";VERDADERO;"Suspenso")',
            mistakes=[
                (
                    '=SI.CONJUNTO(B2>=5;"Aprobado";B2>=7;"Notable";B2>=9;"Sobresaliente";VERDADERO;"Suspenso")',
                    "Los tramos van de menor a mayor: el 9,5 y el 7 salen «Aprobado».",
                ),
                (
                    '=SI.CONJUNTO(B2>=9;"Sobresaliente";B2>=7;"Notable";B2>=5;"Aprobado")',
                    "Falta el «en otro caso»: el 4,9 da #N/D.",
                ),
                (
                    '=SI.CONJUNTO(B2>9;"Sobresaliente";B2>7;"Notable";B2>5;"Aprobado";VERDADERO;"Suspenso")',
                    "Con > el 7 y el 5 bajan un tramo.",
                ),
            ],
            hints=[
                'Empieza por el tramo más alto: B2>=9;"Sobresaliente".',
                'Sigue con B2>=7 y B2>=5, y termina con VERDADERO;"Suspenso".',
            ],
            explain="De mayor a menor y con VERDADERO al final: 9,5 Sobresaliente, 7 Notable, 4,9 Suspenso y 5 Aprobado.",
        ),
        F(
            "xl4-log-15",
            "Escribe en `C2` el coste por paciente (gasto entre pacientes). Si no hubo pacientes, la división da error: con SI.ERROR muestra el texto «Sin pacientes». Cópiala hasta `C4`.",
            grid={
                "A1": "Gasto",
                "B1": "Pacientes",
                "A2": 900,
                "B2": 30,
                "A3": 450,
                "B3": 0,
                "A4": 1200,
                "B4": 48,
            },
            cell="C2",
            expect=30,
            checks=[
                {"type": "value"},
                {"type": "fill", "to": "C4", "expect": ["Sin pacientes", 25]},
                {"type": "functions", "requires": ["IFERROR"]},
            ],
            solution='=SI.ERROR(A2/B2;"Sin pacientes")',
            mistakes=[
                ("=A2/B2", "La fila sin pacientes da #¡DIV/0!."),
                (
                    "=SI.ERROR(A2/B2;0)",
                    "El enunciado pide el texto «Sin pacientes»: un 0 parecería un coste real.",
                ),
            ],
            hints=[
                "El cálculo normal es A2/B2.",
                'Envuélvelo: SI.ERROR(A2/B2;"Sin pacientes").',
            ],
            explain='`=SI.ERROR(A2/B2;"Sin pacientes")`: 900/30 = 30, la fila sin pacientes muestra el texto y 1200/48 = 25.',
        ),
    ],
)

UNITS = [SI, LOGICAS]
