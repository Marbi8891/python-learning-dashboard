# ruff: noqa: E501
# (contenido didáctico: los textos largos van en una sola línea para poder leerlos y editarlos)
"""M05 · Agregación condicional (4 h): 2 unidades y 28 ejercicios.

Diseño en docs/excel-academy/CURRICULUM_M3_M5.md. Empresas y personas ficticias. Los criterios
con fechas del currículo original se dejan para M07 (fechas), que es donde se explican.
"""

from __future__ import annotations

from units import F, R, T, example, unit

# Registro de facturas de la Gestoría Albaida (ficticio)
REGISTRO = {
    "A1": "Cliente",
    "B1": "Zona",
    "C1": "Estado",
    "D1": "Importe",
    "A2": "Ferretería Sol",
    "B2": "Norte",
    "C2": "Pagada",
    "D2": 420,
    "A3": "Bar Lucía",
    "B3": "Sur",
    "C3": "Pendiente",
    "D3": 180,
    "A4": "Farmacia Río",
    "B4": "Norte",
    "C4": "Pendiente",
    "D4": 960,
    "A5": "Bar Lucía",
    "B5": "Sur",
    "C5": "Pagada",
    "D5": 75,
    "A6": "Frutas Ana",
    "B6": "Centro",
    "C6": "Pagada",
    "D6": 310,
    "A7": "Ferretería Sol",
    "B7": "Norte",
    "C7": "Pendiente",
    "D7": 1250,
}


def con(extra: dict) -> dict:
    """El registro con celdas de criterio añadidas."""
    return {**REGISTRO, **extra}


# ---------------------------------------------------------------- xl5-sumar-si

SUMAR = unit(
    "xl5-sumar-si",
    "SUMAR.SI y SUMAR.SI.CONJUNTO",
    hours=2,
    level=3,
    requires=["xl4-si", "xl2-estadisticas"],
    objectives=[
        "Sumar solo las filas que cumplen un criterio con SUMAR.SI.",
        "Sumar con varios criterios a la vez con SUMAR.SI.CONJUNTO y recordar su orden de argumentos.",
        'Escribir criterios con operadores (">500"), con una celda (">="&G1) y con comodines ("Bar*").',
        "Construir una tabla resumen que se actualiza sola al cambiar los datos.",
    ],
    theory="""
## SUMAR.SI: sumar lo que cumple una condición

```
=SUMAR.SI(rango; criterio; [rango_suma])
```

- **rango**: donde se mira el criterio (por ejemplo, la columna Zona, `B2:B7`).
- **criterio**: qué tiene que cumplir (`"Norte"`).
- **rango_suma**: qué se suma (la columna Importe, `D2:D7`). Si lo omites, se suma el propio rango (útil con números: `=SUMAR.SI(D2:D7;">500")`).

`=SUMAR.SI(B2:B7;"Norte";D2:D7)` suma los importes de las filas cuya zona es Norte.

## Cómo se escribe un criterio

| Criterio | Casa con | Ejemplo |
|---|---|---|
| `"Norte"` o `"=Norte"` | el texto Norte (sin distinguir mayúsculas) | `=SUMAR.SI(B2:B7;"Norte";D2:D7)` |
| `500` | el número 500 | |
| `">500"` `"<=100"` `"<>0"` | números que cumplen la comparación | `=SUMAR.SI(D2:D7;">500")` |
| `"<>Pagada"` | todo lo que no es Pagada (también las vacías) | |
| `G1` | lo que haya en la celda G1 | `=SUMAR.SI(B2:B7;G1;D2:D7)` |
| `">="&G2` | mayor o igual que el número de G2 | `=SUMAR.SI(D2:D7;">="&G2)` |
| `"Bar*"` | textos que empiezan por Bar | `*` = cualquier texto, `?` = un carácter |

El operador va **entre comillas**. Para combinarlo con una celda se une con `&`: `">="&G2`. Escribir `">=G2"` buscaría el texto «G2», no el valor de la celda.

## SUMAR.SI.CONJUNTO: varios criterios

```
=SUMAR.SI.CONJUNTO(rango_suma; rango1; criterio1; rango2; criterio2; …)
```

Suma las filas que cumplen **todos** los criterios. ¡Atención al orden! Aquí el **rango que se suma va primero**, al revés que en SUMAR.SI.

`=SUMAR.SI.CONJUNTO(D2:D7;B2:B7;"Norte";C2:C7;"Pendiente")` suma lo pendiente de la zona Norte.

Todos los rangos tienen que tener el mismo tamaño; si no, da #¡VALOR!.

## Una tabla resumen

Con los criterios en celdas (`G2` = Norte, `G3` = Sur…) y la fórmula con referencias absolutas a los datos:

```
=SUMAR.SI($B$2:$B$7;G2;$D$2:$D$7)
```

Al copiarla hacia abajo cambia solo el criterio. Si añades una factura dentro del rango, el resumen se actualiza.
""",
    examples=[
        example(
            "xl5-sum-ej1",
            "Total de una zona",
            '=SUMAR.SI(B2:B7;"Norte";D2:D7)',
            2630,
            "Las facturas de Norte son 420, 960 y 1.250: suman 2.630.",
            grid=REGISTRO,
            cell="F2",
        ),
        example(
            "xl5-sum-ej2",
            "Dos criterios a la vez",
            '=SUMAR.SI.CONJUNTO(D2:D7;B2:B7;"Norte";C2:C7;"Pendiente")',
            2210,
            "Norte y Pendiente a la vez: 960 + 1.250 = 2.210. El rango que se suma va primero.",
            grid=REGISTRO,
            cell="F3",
        ),
    ],
    guided="xl5-sum-11",
    guided_steps=[
        "El criterio se mira en la columna Zona (B2:B7) y se suma la columna Importe (D2:D7).",
        "El criterio está en la celda G2: escribe G2, sin comillas.",
        "Fija con $ los dos rangos para poder copiar la fórmula hacia abajo.",
    ],
    case=(
        "Caso: el resumen de facturación de la Gestoría Albaida",
        """
La Gestoría Albaida (empresa ficticia) lleva un registro de facturas con cliente, zona, estado e importe.

1. Escribe al menos doce facturas en tres zonas, con estados Pagada y Pendiente.
2. Haz una tabla resumen con una fila por zona y el total facturado de cada una con SUMAR.SI.
3. Añade una columna con lo pendiente de cobro por zona con SUMAR.SI.CONJUNTO.
4. Pon en una celda un importe mínimo y suma las facturas que lo superan.
5. Añade una factura nueva dentro del rango y comprueba que el resumen cambia solo.
""",
    ),
    mistakes=[
        (
            "Usar en SUMAR.SI.CONJUNTO el orden de SUMAR.SI.",
            "En SUMAR.SI.CONJUNTO el rango que se suma va primero: (suma; rango1; criterio1; …).",
        ),
        (
            'Escribir el criterio con una celda dentro de las comillas: `">=G2"`.',
            'Así busca el texto «G2». Une el operador y la celda con &: `">="&G2`.',
        ),
        (
            "Rangos de distinto tamaño en SUMAR.SI.CONJUNTO.",
            "Todos deben tener las mismas filas (B2:B7 y D2:D7). Si no, da #¡VALOR!.",
        ),
        (
            "Copiar la fórmula del resumen sin fijar los rangos de datos.",
            "Los datos se mueven al copiar. Fíjalos: $B$2:$B$7 y $D$2:$D$7; solo el criterio debe cambiar.",
        ),
    ],
    summary=[
        "SUMAR.SI(rango; criterio; rango_suma).",
        "SUMAR.SI.CONJUNTO(rango_suma; rango1; criterio1; …): la suma va primero.",
        'Operadores entre comillas; con una celda, `">="&G2`.',
        "* y ? son comodines en los criterios de texto.",
        "Con los criterios en celdas, una tabla resumen se copia y se actualiza sola.",
    ],
    faq=[
        (
            "¿SUMAR.SI distingue mayúsculas?",
            "No: «norte», «Norte» y «NORTE» cuentan igual.",
        ),
        (
            "¿Y si quiero sumar con «una condición u otra» (Norte o Sur)?",
            'SUMAR.SI.CONJUNTO exige todas. Para «o», suma dos SUMAR.SI: `=SUMAR.SI(B2:B7;"Norte";D2:D7)+SUMAR.SI(B2:B7;"Sur";D2:D7)`.',
        ),
    ],
    sources=[
        (
            "SUMAR.SI (función SUMAR.SI)",
            "https://support.microsoft.com/es-es/office/sumar-si-funci%C3%B3n-sumar-si-169b8c99-c05c-4483-a712-1697a653039b",
        ),
        (
            "Función SUMAR.SI.CONJUNTO",
            "https://support.microsoft.com/es-es/excel/functions/sumifs-function",
        ),
        (
            "Sumar valores basados en varias condiciones",
            "https://support.microsoft.com/es-es/excel/sum-values-based-on-multiple-conditions",
        ),
    ],
    required=["xl5-sum-11", "xl5-sum-12"],
    questions=[
        T(
            "xl5-sum-01",
            "¿Qué fórmula suma los importes (D2:D7) de las facturas de la zona Sur (B2:B7)?",
            [
                '=SUMAR.SI(B2:B7;"Sur";D2:D7)',
                '=SUMAR.SI(D2:D7;"Sur";B2:B7)',
                "=SUMAR.SI(B2:B7;Sur;D2:D7)",
                '=SUMA(B2:B7;"Sur";D2:D7)',
            ],
            0,
            "Primero dónde se mira el criterio, luego el criterio entre comillas y al final lo que se suma.",
        ),
        T(
            "xl5-sum-02",
            "En SUMAR.SI.CONJUNTO, ¿qué argumento va primero?",
            [
                "El rango que se suma",
                "El primer criterio",
                "El rango del primer criterio",
                "Da igual el orden",
            ],
            0,
            "SUMAR.SI.CONJUNTO(rango_suma; rango1; criterio1; …), al revés que SUMAR.SI.",
        ),
        T(
            "xl5-sum-03",
            "El importe mínimo está en G2. ¿Cómo escribes el criterio «mayor o igual que G2»?",
            ['">="&G2', '">=G2"', ">=G2", '"G2>="'],
            0,
            "El operador va entre comillas y se une con & a la celda.",
        ),
        T(
            "xl5-sum-04",
            '¿Con qué clientes casa el criterio `"Bar*"`?',
            [
                "Con los que empiezan por «Bar», como «Bar Lucía»",
                "Solo con el que se llama exactamente «Bar*»",
                "Con los que terminan en «Bar»",
                "Con todos",
            ],
            0,
            "El asterisco significa «cualquier texto». Para buscar un * de verdad se escribe ~*.",
        ),
        T(
            "xl5-sum-05",
            '¿Qué da `=SUMAR.SI.CONJUNTO(D2:D7;B2:B6;"Norte")`?',
            [
                "#¡VALOR!, porque los rangos no tienen el mismo tamaño",
                "La suma de Norte de las cinco primeras filas",
                "0",
                "La suma de toda la columna D",
            ],
            0,
            "En las funciones «.CONJUNTO» todos los rangos deben medir lo mismo.",
        ),
        T(
            "xl5-sum-06",
            "Vas a copiar `=SUMAR.SI(B2:B7;G2;D2:D7)` hacia abajo para cada zona de G2:G4. ¿Qué tienes que cambiar?",
            [
                "Fijar los rangos de datos: $B$2:$B$7 y $D$2:$D$7",
                "Fijar el criterio: $G$2",
                "Nada",
                "Poner G2 entre comillas",
            ],
            0,
            "Los datos tienen que quedarse quietos y el criterio tiene que bajar fila a fila.",
        ),
        R(
            "xl5-sum-07",
            "¿Qué devuelve la fórmula?",
            '=SUMAR.SI(C2:C7;"Pagada";D2:D7)',
            805,
            "Las pagadas son 420, 75 y 310: 805.",
            grid=REGISTRO,
            cell="F2",
        ),
        R(
            "xl5-sum-08",
            "¿Qué devuelve la fórmula?",
            '=SUMAR.SI(D2:D7;">500")',
            2210,
            "Sin rango de suma se suma el propio rango: 960 + 1.250 = 2.210.",
            grid=REGISTRO,
            cell="F2",
        ),
        R(
            "xl5-sum-09",
            "¿Qué devuelve la fórmula?",
            '=SUMAR.SI(A2:A7;"F*";D2:D7)',
            2940,
            "Los clientes que empiezan por F son Ferretería Sol (420 y 1.250), Farmacia Río (960) y Frutas Ana (310): 2.940.",
            grid=REGISTRO,
            cell="F2",
        ),
        R(
            "xl5-sum-10",
            "¿Qué devuelve la fórmula?",
            '=SUMAR.SI.CONJUNTO(D2:D7;A2:A7;"Bar Lucía";C2:C7;"Pendiente")',
            180,
            "Bar Lucía tiene dos facturas, pero solo la de 180 está pendiente.",
            grid=REGISTRO,
            cell="F2",
        ),
        F(
            "xl5-sum-11",
            "Escribe en `H2` el total facturado de la zona de `G2`, para copiarla hasta `H4` (una fila por zona).",
            grid=con({"G1": "Zona", "G2": "Norte", "G3": "Sur", "G4": "Centro", "H1": "Total"}),
            cell="H2",
            expect=2630,
            checks=[
                {"type": "value"},
                {"type": "fill", "to": "H4", "expect": [255, 310]},
                {"type": "references", "must": ["$B$2:$B$7", "$D$2:$D$7", "G2"]},
                {"type": "functions", "requires": ["SUMIF"]},
                {"type": "variants", "count": 2},
            ],
            solution="=SUMAR.SI($B$2:$B$7;G2;$D$2:$D$7)",
            mistakes=[
                (
                    "=SUMAR.SI(B2:B7;G2;D2:D7)",
                    "Sin $, al copiarla los rangos bajan una fila y se pierden facturas.",
                ),
                (
                    '=SUMAR.SI($B$2:$B$7;"Norte";$D$2:$D$7)',
                    "Con el texto escrito, todas las filas del resumen dan el total de Norte.",
                ),
                (
                    "=SUMAR.SI($D$2:$D$7;G2;$B$2:$B$7)",
                    "Los rangos están al revés: el criterio se mira en la zona y se suma el importe.",
                ),
            ],
            hints=[
                "SUMAR.SI(rango del criterio; criterio; rango que se suma).",
                "El criterio es G2 (sin $, para que baje); los rangos, fijos con $.",
            ],
            explain="`=SUMAR.SI($B$2:$B$7;G2;$D$2:$D$7)`: Norte 2.630, Sur 255 y Centro 310.",
            vary=["D2:D7"],
        ),
        F(
            "xl5-sum-12",
            "Escribe en `H2` lo pendiente de cobro de la zona de `G2` (estado «Pendiente»), para copiarla hasta `H4`.",
            grid=con({"G1": "Zona", "G2": "Norte", "G3": "Sur", "G4": "Centro", "H1": "Pendiente"}),
            cell="H2",
            expect=2210,
            checks=[
                {"type": "value"},
                {"type": "fill", "to": "H4", "expect": [180, 0]},
                {"type": "references", "must": ["$B$2:$B$7", "$C$2:$C$7", "$D$2:$D$7", "G2"]},
                {"type": "functions", "requires": ["SUMIFS"]},
            ],
            solution='=SUMAR.SI.CONJUNTO($D$2:$D$7;$B$2:$B$7;G2;$C$2:$C$7;"Pendiente")',
            mistakes=[
                (
                    "=SUMAR.SI($B$2:$B$7;G2;$D$2:$D$7)",
                    "Falta el criterio del estado: suma también lo pagado.",
                ),
                (
                    '=SUMAR.SI.CONJUNTO(D2:D7;B2:B7;G2;C2:C7;"Pendiente")',
                    "Sin $, al copiarla los rangos bajan y se pierden facturas.",
                ),
            ],
            hints=[
                "SUMAR.SI.CONJUNTO empieza por lo que se suma: $D$2:$D$7.",
                'Después, dos parejas: $B$2:$B$7;G2 y $C$2:$C$7;"Pendiente".',
            ],
            explain='`=SUMAR.SI.CONJUNTO($D$2:$D$7;$B$2:$B$7;G2;$C$2:$C$7;"Pendiente")`: Norte 2.210, Sur 180 y Centro 0.',
        ),
        F(
            "xl5-sum-13",
            "Escribe en `H1` la suma de los importes que llegan al mínimo de `G1` (mayor o igual). El mínimo puede cambiar: no lo escribas en la fórmula.",
            grid=con({"F1": "Mínimo", "G1": 420}),
            cell="H1",
            expect=2630,
            checks=[
                {"type": "value"},
                {"type": "variants", "count": 3},
                {"type": "references", "must": ["G1"]},
                {"type": "noConstants"},
            ],
            solution='=SUMAR.SI(D2:D7;">="&G1)',
            mistakes=[
                (
                    '=SUMAR.SI(D2:D7;">=G1")',
                    'Busca el texto «G1»: da 0. Une el operador y la celda con &: ">="&G1.',
                ),
                (
                    '=SUMAR.SI(D2:D7;">="&400)',
                    "El mínimo está escrito en la fórmula: si cambia G1, no se entera.",
                ),
                (
                    '=SUMAR.SI(D2:D7;">"&G1)',
                    "Con > se queda fuera la factura de 420, igual al mínimo.",
                ),
            ],
            hints=[
                "Aquí se suma el propio rango de importes: no hace falta tercer argumento.",
                'El criterio se construye con &: ">="&G1.',
            ],
            explain='`=SUMAR.SI(D2:D7;">="&G1)`: con 420, 420 + 960 + 1.250 = 2.630.',
            vary=["G1"],
        ),
        F(
            "xl5-sum-14",
            "Escribe en `F2` el total facturado a los clientes que empiezan por «Bar» (usa un comodín).",
            grid=REGISTRO,
            cell="F2",
            expect=255,
            checks=[
                {"type": "value"},
                {"type": "variants", "count": 2},
                {"type": "functions", "requires": ["SUMIF"]},
            ],
            solution='=SUMAR.SI(A2:A7;"Bar*";D2:D7)',
            mistakes=[
                (
                    '=SUMAR.SI(A2:A7;"Bar";D2:D7)',
                    "Sin comodín busca un cliente que se llame exactamente «Bar»: da 0.",
                ),
                ('=SUMAR.SI(A2:A7;"*Bar";D2:D7)', "Así buscaría los que terminan en «Bar»."),
            ],
            hints=[
                "El criterio se mira en la columna Cliente (A2:A7).",
                '"Bar*": Bar seguido de cualquier texto.',
            ],
            explain='`=SUMAR.SI(A2:A7;"Bar*";D2:D7)`: las dos facturas de Bar Lucía, 180 + 75 = 255.',
            vary=["D2:D7"],
        ),
    ],
)

# ---------------------------------------------------------------- xl5-contar-si

CONTAR = unit(
    "xl5-contar-si",
    "CONTAR.SI, PROMEDIO.SI y MAX/MIN.SI.CONJUNTO",
    hours=2,
    level=3,
    requires=["xl5-sumar-si"],
    objectives=[
        "Contar filas que cumplen uno o varios criterios con CONTAR.SI y CONTAR.SI.CONJUNTO.",
        "Calcular la media de las filas que cumplen un criterio con PROMEDIO.SI.",
        "Obtener el máximo y el mínimo con condiciones con MAX.SI.CONJUNTO y MIN.SI.CONJUNTO.",
        'Contar celdas vacías y no vacías con los criterios "" y "<>".',
    ],
    theory="""
## CONTAR.SI y CONTAR.SI.CONJUNTO

```
=CONTAR.SI(rango; criterio)
=CONTAR.SI.CONJUNTO(rango1; criterio1; rango2; criterio2; …)
```

Cuentan cuántas celdas (o filas) cumplen el criterio. Los criterios se escriben igual que en SUMAR.SI: `"Pendiente"`, `">500"`, `">="&G1`, `"F*"`.

- `=CONTAR.SI(C2:C7;"Pendiente")` cuenta las facturas pendientes.
- `=CONTAR.SI.CONJUNTO(B2:B7;"Norte";C2:C7;"Pendiente")` cuenta las de Norte **y** pendientes.

Dos criterios especiales:

| Criterio | Cuenta |
|---|---|
| `"<>"` | celdas que **no** están vacías |
| `""` | celdas vacías |

Por ejemplo, `=CONTAR.SI(E2:E7;"")` dice cuántas facturas no tienen fecha de cobro.

## PROMEDIO.SI

```
=PROMEDIO.SI(rango; criterio; [rango_promedio])
```

La misma idea que SUMAR.SI, pero hace la media. Si ninguna fila cumple el criterio da **#¡DIV/0!** (no hay nada que promediar). Existe también PROMEDIO.SI.CONJUNTO, con varios criterios.

## MAX.SI.CONJUNTO y MIN.SI.CONJUNTO [2019+]

```
=MAX.SI.CONJUNTO(rango_max; rango1; criterio1; …)
```

Devuelven el mayor o el menor valor de las filas que cumplen los criterios. Como SUMAR.SI.CONJUNTO, **el rango del resultado va primero**. Si ninguna fila cumple, devuelven **0**: cuidado, un 0 puede confundirse con un importe real.

## Porcentajes a partir de recuentos

El porcentaje de facturas pendientes es el recuento entre el total:

```
=CONTAR.SI(C2:C7;"Pendiente")/CONTARA(C2:C7)
```

con formato porcentaje (xl1-formatos).
""",
    examples=[
        example(
            "xl5-con-ej1",
            "Cuántas facturas están pendientes",
            '=CONTAR.SI(C2:C7;"Pendiente")',
            3,
            "Bar Lucía (180), Farmacia Río y la segunda de Ferretería Sol: 3.",
            grid=REGISTRO,
            cell="F2",
        ),
        example(
            "xl5-con-ej2",
            "La factura más alta de una zona",
            '=MAX.SI.CONJUNTO(D2:D7;B2:B7;"Norte")',
            1250,
            "En Norte hay 420, 960 y 1.250: la mayor es 1.250.",
            grid=REGISTRO,
            cell="F3",
        ),
    ],
    guided="xl5-con-11",
    guided_steps=[
        "CONTAR.SI.CONJUNTO va por parejas de rango y criterio.",
        "Primera pareja: la zona ($B$2:$B$7) con el criterio de G2; segunda: el estado con «Pendiente».",
        "Fija los rangos con $ y copia la fórmula hasta H4.",
    ],
    case=(
        "Caso: el informe de cobros de la Gestoría Albaida",
        """
Con el registro de facturas del caso anterior, la Gestoría Albaida (empresa ficticia) quiere un informe de cobros.

1. Por zona: número de facturas, número de pendientes y porcentaje de pendientes.
2. El importe medio de las facturas pagadas y el de las pendientes con PROMEDIO.SI.
3. La factura pendiente más alta de cada zona con MAX.SI.CONJUNTO. ¿Qué pasa en una zona sin pendientes?
4. Añade una columna «Fecha de cobro» vacía en las pendientes y cuenta cuántas faltan por fechar con el criterio "".
""",
    ),
    mistakes=[
        (
            "Usar CONTAR para contar textos que cumplen algo.",
            "CONTAR solo cuenta números y no admite criterios. Para contar con una condición, CONTAR.SI.",
        ),
        (
            "Poner en MAX.SI.CONJUNTO el rango del criterio primero.",
            "Como en SUMAR.SI.CONJUNTO, primero va el rango del que se saca el máximo.",
        ),
        (
            "Fiarse de un 0 de MAX.SI.CONJUNTO.",
            "Si ninguna fila cumple, da 0. Comprueba con CONTAR.SI.CONJUNTO si había filas.",
        ),
        (
            "Esperar 0 de PROMEDIO.SI sin coincidencias.",
            "Da #¡DIV/0!: no hay nada que promediar. Si es un caso normal, trátalo con SI.ERROR o comprobando el recuento.",
        ),
    ],
    summary=[
        "CONTAR.SI(rango; criterio) y CONTAR.SI.CONJUNTO(rango1; criterio1; …).",
        '"<>" cuenta no vacías; "" cuenta vacías.',
        "PROMEDIO.SI da #¡DIV/0! si nada cumple.",
        "MAX.SI.CONJUNTO y MIN.SI.CONJUNTO: el resultado primero; 0 si nada cumple.",
    ],
    faq=[
        (
            "¿CONTAR.SI cuenta el texto «5» si busco el número 5?",
            "En PLD no: un criterio numérico solo casa con celdas numéricas. En Excel hay casos en que sí lo hace, así que evita mezclar números y números guardados como texto (xl1-datos).",
        ),
        (
            "Mi Excel no tiene MAX.SI.CONJUNTO. ¿Qué hago?",
            "Existe desde Excel 2019. En versiones anteriores se resuelve con fórmulas matriciales o con una columna auxiliar con SI.",
        ),
    ],
    sources=[
        (
            "Función CONTAR.SI.CONJUNTO",
            "https://support.microsoft.com/es-es/excel/functions/countifs-function",
        ),
        (
            "Función PROMEDIO.SI",
            "https://support.microsoft.com/es-es/office/promedio-si-funci%C3%B3n-promedio-si-faec8e2e-0dec-4308-af69-f5576d8ac642",
        ),
        (
            "MAX.SI.CONJUNTO (función MAX.SI.CONJUNTO)",
            "https://support.microsoft.com/es-es/office/max-si-conjunto-funci%C3%B3n-max-si-conjunto-dfd611e6-da2c-488a-919b-9b6376b28883",
        ),
        (
            "Formas de contar valores en una hoja de cálculo",
            "https://support.microsoft.com/es-es/excel/ways-to-count-values-in-a-worksheet",
        ),
    ],
    required=["xl5-con-11", "xl5-con-13"],
    questions=[
        T(
            "xl5-con-01",
            "¿Qué fórmula cuenta las facturas pendientes del rango de estados C2:C7?",
            [
                '=CONTAR.SI(C2:C7;"Pendiente")',
                '=CONTAR(C2:C7;"Pendiente")',
                '=SUMAR.SI(C2:C7;"Pendiente")',
                "=CONTARA(C2:C7)",
            ],
            0,
            "CONTAR.SI cuenta las celdas que cumplen el criterio.",
        ),
        T(
            "xl5-con-02",
            '¿Qué cuenta `=CONTAR.SI(E2:E7;"<>")`?',
            [
                "Las celdas de E2:E7 que no están vacías",
                "Las celdas vacías",
                "Las celdas que contienen «<>»",
                "Nada: da error",
            ],
            0,
            "«<>» sin nada detrás significa «distinto de vacío».",
        ),
        T(
            "xl5-con-03",
            "Ninguna factura cumple el criterio. ¿Qué devuelve PROMEDIO.SI?",
            ["#¡DIV/0!", "0", "#N/D", "Una celda vacía"],
            0,
            "Sin valores no hay media: sería dividir entre 0.",
        ),
        T(
            "xl5-con-04",
            "Ninguna factura cumple los criterios. ¿Qué devuelve MAX.SI.CONJUNTO?",
            ["0", "#¡DIV/0!", "#N/D", "El máximo de todo el rango"],
            0,
            "Devuelve 0, que puede confundirse con un importe real.",
        ),
        T(
            "xl5-con-05",
            "¿Cuál es el orden de los argumentos de MIN.SI.CONJUNTO?",
            [
                "Rango del mínimo; rango1; criterio1; …",
                "Rango1; criterio1; rango del mínimo",
                "Criterio1; rango1; rango del mínimo",
                "Rango1; rango del mínimo; criterio1",
            ],
            0,
            "Igual que SUMAR.SI.CONJUNTO y MAX.SI.CONJUNTO: el resultado primero.",
        ),
        T(
            "xl5-con-06",
            "¿Qué fórmula da el porcentaje de facturas pagadas (con formato porcentaje)?",
            [
                '=CONTAR.SI(C2:C7;"Pagada")/CONTARA(C2:C7)',
                '=CONTAR.SI(C2:C7;"Pagada")*100',
                '=SUMAR.SI(C2:C7;"Pagada";D2:D7)/SUMA(D2:D7)',
                '=CONTARA(C2:C7)/CONTAR.SI(C2:C7;"Pagada")',
            ],
            0,
            "El recuento de pagadas entre el total de facturas. La opción con SUMAR.SI da el porcentaje del importe, que es otra cosa.",
        ),
        R(
            "xl5-con-07",
            "¿Qué devuelve la fórmula?",
            '=CONTAR.SI.CONJUNTO(B2:B7;"Norte";C2:C7;"Pendiente")',
            2,
            "En Norte hay tres facturas; pendientes, dos (960 y 1.250).",
            grid=REGISTRO,
            cell="F2",
        ),
        R(
            "xl5-con-08",
            "¿Qué devuelve la fórmula?",
            '=PROMEDIO.SI(C2:C7;"Pagada";D2:D7)',
            268.3333,
            "Las pagadas son 420, 75 y 310: 805 / 3 = 268,33.",
            grid=REGISTRO,
            cell="F2",
            tolerance=0.01,
        ),
        R(
            "xl5-con-09",
            "¿Qué devuelve la fórmula?",
            '=MIN.SI.CONJUNTO(D2:D7;C2:C7;"Pendiente")',
            180,
            "Los importes pendientes son 180, 960 y 1.250: el menor es 180.",
            grid=REGISTRO,
            cell="F2",
        ),
        R(
            "xl5-con-10",
            "La columna E guarda la fecha de cobro; las pendientes la tienen vacía. ¿Qué devuelve la fórmula?",
            '=CONTAR.SI(E2:E7;"")',
            3,
            "Tres facturas no tienen fecha de cobro.",
            grid=con({"E1": "Cobro", "E2": "05/11", "E5": "12/11", "E6": "14/11"}),
            cell="F2",
        ),
        F(
            "xl5-con-11",
            "Escribe en `H2` cuántas facturas pendientes hay en la zona de `G2`, para copiarla hasta `H4`.",
            grid=con(
                {"G1": "Zona", "G2": "Norte", "G3": "Sur", "G4": "Centro", "H1": "Pendientes"}
            ),
            cell="H2",
            expect=2,
            checks=[
                {"type": "value"},
                {"type": "fill", "to": "H4", "expect": [1, 0]},
                {"type": "references", "must": ["$B$2:$B$7", "$C$2:$C$7", "G2"]},
                {"type": "functions", "requires": ["COUNTIFS"]},
            ],
            solution='=CONTAR.SI.CONJUNTO($B$2:$B$7;G2;$C$2:$C$7;"Pendiente")',
            mistakes=[
                (
                    "=CONTAR.SI($B$2:$B$7;G2)",
                    "Cuenta todas las facturas de la zona, no solo las pendientes.",
                ),
                (
                    '=CONTAR.SI.CONJUNTO(B2:B7;G2;C2:C7;"Pendiente")',
                    "Sin $, al copiarla los rangos bajan y se pierden facturas.",
                ),
            ],
            hints=[
                "Dos parejas de rango y criterio.",
                '$B$2:$B$7;G2 y $C$2:$C$7;"Pendiente".',
            ],
            explain='`=CONTAR.SI.CONJUNTO($B$2:$B$7;G2;$C$2:$C$7;"Pendiente")`: Norte 2, Sur 1 y Centro 0.',
        ),
        F(
            "xl5-con-12",
            "Escribe en `F2` el importe medio de las facturas de la zona Norte.",
            grid=REGISTRO,
            cell="F2",
            expect=876.6667,
            tolerance=0.01,
            checks=[
                {"type": "value"},
                {"type": "variants", "count": 2},
                {"type": "functions", "requires": ["AVERAGEIF"]},
            ],
            solution='=PROMEDIO.SI(B2:B7;"Norte";D2:D7)',
            mistakes=[
                ('=SUMAR.SI(B2:B7;"Norte";D2:D7)', "Eso es el total de Norte, no la media."),
                ("=PROMEDIO(D2:D7)", "Es la media de todas las zonas."),
            ],
            hints=[
                "PROMEDIO.SI tiene los mismos argumentos que SUMAR.SI.",
                'PROMEDIO.SI(B2:B7;"Norte";D2:D7).',
            ],
            explain='`=PROMEDIO.SI(B2:B7;"Norte";D2:D7)`: (420 + 960 + 1.250) / 3 = 876,67.',
            vary=["D2:D7"],
        ),
        F(
            "xl5-con-13",
            "Escribe en `H2` la factura **pendiente** más alta de la zona de `G2`, para copiarla hasta `H4`. Si una zona no tiene pendientes, dará 0.",
            grid=con(
                {"G1": "Zona", "G2": "Norte", "G3": "Sur", "G4": "Centro", "H1": "Mayor pendiente"}
            ),
            cell="H2",
            expect=1250,
            checks=[
                {"type": "value"},
                {"type": "fill", "to": "H4", "expect": [180, 0]},
                {"type": "references", "must": ["$D$2:$D$7", "G2"]},
                {"type": "functions", "requires": ["MAXIFS"]},
                {"type": "variants", "count": 2},
            ],
            solution='=MAX.SI.CONJUNTO($D$2:$D$7;$B$2:$B$7;G2;$C$2:$C$7;"Pendiente")',
            mistakes=[
                (
                    "=MAX.SI.CONJUNTO($D$2:$D$7;$B$2:$B$7;G2)",
                    "Falta el estado: en Centro sale 310, una factura ya pagada.",
                ),
                (
                    '=MAX.SI.CONJUNTO($B$2:$B$7;G2;$D$2:$D$7;$C$2:$C$7;"Pendiente")',
                    "El rango del máximo va primero.",
                ),
            ],
            hints=[
                "MAX.SI.CONJUNTO(rango del máximo; rango1; criterio1; rango2; criterio2).",
                'El máximo sale de $D$2:$D$7; los criterios: zona G2 y estado "Pendiente".',
            ],
            explain='`=MAX.SI.CONJUNTO($D$2:$D$7;$B$2:$B$7;G2;$C$2:$C$7;"Pendiente")`: Norte 1.250, Sur 180 y Centro 0 (no tiene pendientes).',
            vary=["D2:D7"],
        ),
        F(
            "xl5-con-14",
            "Escribe en `F2` cuántas facturas llegan al importe mínimo de `G1` (mayor o igual). El mínimo puede cambiar.",
            grid=con({"E1": "Mínimo", "G1": 310}),
            cell="F2",
            expect=4,
            checks=[
                {"type": "value"},
                {"type": "variants", "count": 3},
                {"type": "references", "must": ["G1"]},
                {"type": "noConstants"},
            ],
            solution='=CONTAR.SI(D2:D7;">="&G1)',
            mistakes=[
                (
                    '=CONTAR.SI(D2:D7;">=G1")',
                    'Busca el texto «G1»: da 0. Une el operador con la celda: ">="&G1.',
                ),
                (
                    '=CONTAR.SI(D2:D7;">="&300)',
                    "El mínimo está escrito en la fórmula y no sigue a G1.",
                ),
                ("=CONTAR(D2:D7)", "Cuenta todas las facturas, sin criterio."),
            ],
            hints=[
                "CONTAR.SI(rango; criterio).",
                'El criterio se construye con &: ">="&G1.',
            ],
            explain='`=CONTAR.SI(D2:D7;">="&G1)`: con 310 cuentan 420, 960, 310 y 1.250 (la de 310 entra por el «o igual»).',
            vary=["G1"],
        ),
    ],
)

UNITS = [SUMAR, CONTAR]
