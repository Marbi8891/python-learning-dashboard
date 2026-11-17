# ruff: noqa: E501
# (contenido didáctico: los textos largos van en una sola línea para poder leerlos y editarlos)
"""M01 · Fundamentos de Excel (10 h): 5 unidades y 56 ejercicios.

Diseño en docs/excel-academy/CURRICULUM_M1_M2.md §6. Empresas y personas ficticias.
"""

from __future__ import annotations

from units import F, R, T, example, note, unit

# ---------------------------------------------------------------- xl1-interfaz

CLIENTES = {
    "A1": "Cliente",
    "B1": "Cuota",
    "A2": "Ana Ruiz",
    "B2": 45,
    "A3": "Talleres Sol",
    "B3": 120,
    "A4": "Luis Gil",
    "B4": 60,
}

INTERFAZ = unit(
    "xl1-interfaz",
    "Interfaz, libros y hojas",
    hours=1.5,
    level=1,
    requires=[],
    objectives=[
        "Reconocer la cinta de opciones, la barra de fórmulas y el cuadro de nombres.",
        "Distinguir libro, hoja, celda y rango.",
        "Nombrar una celda (C4) y un rango (B2:D5) y saber cuántas celdas tiene un rango.",
    ],
    theory="""
## Libro, hoja, celda y rango

- Un **libro** es el archivo de Excel (por ejemplo, `clientes.xlsx`). Dentro tiene una o varias **hojas**, que se ven como pestañas en la parte de abajo.
- Cada hoja es una cuadrícula. Las **columnas** se nombran con letras (A, B… Z, AA, AB… hasta XFD: 16 384 columnas) y las **filas**, con números (de 1 a 1 048 576).
- Una **celda** es el cruce de una columna y una fila. Su nombre es la letra y después el número: `C4` es la columna C y la fila 4.
- Un **rango** es un rectángulo de celdas. Se escribe con la celda de arriba a la izquierda, dos puntos y la de abajo a la derecha: `B2:D5`.

Para contar las celdas de un rango, multiplica columnas por filas. `B2:D5` va de la columna B a la D (3 columnas) y de la fila 2 a la 5 (4 filas): 3 × 4 = **12 celdas**.

## La ventana de Excel

- **Cinta de opciones:** la franja de arriba, con pestañas (Inicio, Insertar, Disposición de página, Fórmulas, Datos, Revisar, Vista). Cada pestaña agrupa botones por tareas.
- **Cuadro de nombres:** a la izquierda de la barra de fórmulas. Dice qué celda está activa. Si escribes `K250` y pulsas Intro, Excel salta a esa celda.
- **Barra de fórmulas:** enseña lo que **guarda** la celda activa. Si la celda tiene una fórmula, en la barra ves la fórmula y en la celda ves su resultado.
- **Celda activa:** la que tiene el borde grueso. Cuando seleccionas un rango, la celda activa es la que se queda en blanco dentro de la selección.

## Moverse y organizar hojas

- Flechas, Tab e Intro mueven la celda activa. **Ctrl+Inicio** vuelve a `A1`; **Ctrl+flecha** salta al borde de los datos.
- El botón **+** junto a las pestañas añade una hoja. Con doble clic en la pestaña se cambia su nombre, y arrastrándola se cambia de sitio.
- **Ctrl+AvPág** y **Ctrl+RePág** pasan a la hoja siguiente o a la anterior.

## Una fórmula que solo lee una celda

Una fórmula empieza siempre por `=`. La más sencilla es una referencia: `=B3` devuelve lo que hay en `B3`. Si la celda está vacía, la fórmula muestra **0**. En la cuadrícula de los ejercicios verás las letras de columna arriba y los números de fila a la izquierda, como en Excel.
""",
    examples=[
        note(
            "¿Cuántas celdas tiene B2:D5?",
            "Columnas B, C y D: 3. Filas 2, 3, 4 y 5: 4. Total: 3 × 4 = **12 celdas**.",
        ),
        example(
            "xl1-int-ej1",
            "Leer una celda por su nombre",
            "=B3",
            120,
            "`=B3` devuelve lo que guarda la celda B3: la cuota de Talleres Sol, 120.",
            grid=CLIENTES,
        ),
    ],
    guided="xl1-int-09",
    guided_steps=[
        "Busca la letra de la columna en la fila de arriba de la cuadrícula.",
        "Baja por esa columna hasta el número de fila que dice la fórmula.",
        "Lo que hay en esa celda es lo que devuelve la fórmula.",
    ],
    case=(
        "Caso: el libro de clientes de la Gestoría Albaida",
        """
La Gestoría Albaida (empresa ficticia) tiene todo en una sola hoja: clientes, facturas y notas mezclados. Te piden ordenarlo **sin crear archivos nuevos**.

1. Crea un libro y cambia el nombre de la primera hoja a «Clientes» (doble clic en la pestaña).
2. Añade dos hojas con el botón **+** y llámalas «Facturas» y «Notas».
3. En «Clientes», escribe en `A1` «Cliente» y en `B1` «Cuota», y debajo tres clientes inventados.
4. Usa el cuadro de nombres para ir a `B4` y comprueba en la barra de fórmulas qué guarda.

Hazlo en Excel o en Excel para la web (gratis con una cuenta de Microsoft). PLD no comprueba este caso: los ejercicios de abajo sí se corrigen.
""",
    ),
    mistakes=[
        (
            "Confundir la celda activa con el rango seleccionado.",
            "En un rango seleccionado solo hay una celda activa: la que se ve en blanco. Lo que escribas va a esa celda.",
        ),
        (
            "Creer que la celda guarda lo que muestra.",
            "Mira la barra de fórmulas: ahí está lo que guarda (una fórmula, un número con todos sus decimales…).",
        ),
        (
            "Llamar «libro» a una hoja.",
            "El libro es el archivo entero; las hojas son las pestañas que hay dentro.",
        ),
    ],
    summary=[
        "Libro = archivo; hoja = pestaña; celda = columna + fila (C4); rango = rectángulo (B2:D5).",
        "Celdas de un rango = columnas × filas.",
        "La barra de fórmulas enseña lo que guarda la celda; la celda enseña el resultado.",
        "El cuadro de nombres dice la celda activa y sirve para ir a cualquier celda.",
    ],
    faq=[
        (
            "¿Necesito tener Excel instalado?",
            "No para este curso: los ejercicios se hacen aquí. Para practicar fuera, Excel para la web es gratuito con una cuenta de Microsoft.",
        ),
        (
            "¿Por qué una celda vacía da 0 en una fórmula?",
            "Porque Excel trata la celda vacía como 0 al calcular. Lo verás en `=C2` cuando C2 no tiene nada.",
        ),
    ],
    sources=[
        ("¿Qué es Excel?", "https://support.microsoft.com/es-es/excel/get-started/what-is-excel"),
        (
            "Tareas básicas en Excel",
            "https://support.microsoft.com/es-es/office/tareas-b%C3%A1sicas-en-excel-dc775dd1-fa52-430f-9c3c-d998d1735fca",
        ),
        ("Glosario de Excel", "https://support.microsoft.com/es-es/excel/excel-glossary"),
    ],
    questions=[
        T(
            "xl1-int-01",
            "¿Qué es un **libro** de Excel?",
            [
                "El archivo de Excel, que contiene una o varias hojas",
                "Una sola hoja de cálculo",
                "Una fila de datos",
                "La cinta de opciones",
            ],
            0,
            "El libro es el archivo (.xlsx). Las hojas son las pestañas que tiene dentro.",
        ),
        T(
            "xl1-int-02",
            "¿Cuántas celdas tiene el rango `B2:D5`?",
            ["12", "9", "16", "20"],
            0,
            "B, C y D son 3 columnas; de la fila 2 a la 5 hay 4 filas: 3 × 4 = 12.",
        ),
        T(
            "xl1-int-03",
            "¿Dónde ves la fórmula que guarda la celda activa?",
            [
                "En la barra de fórmulas",
                "En el cuadro de nombres",
                "En la pestaña Inicio",
                "En la propia celda, siempre",
            ],
            0,
            "La celda muestra el resultado; la barra de fórmulas muestra lo que guarda.",
        ),
        T(
            "xl1-int-04",
            "¿Cuál es la forma más rápida de ir a la celda `K250`?",
            [
                "Escribir K250 en el cuadro de nombres y pulsar Intro",
                "Escribir K250 en la barra de fórmulas",
                "Pulsar Ctrl+Inicio",
                "Hacer doble clic en la pestaña de la hoja",
            ],
            0,
            "El cuadro de nombres, a la izquierda de la barra de fórmulas, lleva a la celda que escribas. Ctrl+Inicio va a A1.",
        ),
        T(
            "xl1-int-05",
            "Seleccionas el rango `A1:C3` empezando a arrastrar desde `A1`. ¿Cuál es la celda activa?",
            [
                "A1, la que se ve en blanco dentro de la selección",
                "C3",
                "Todas las del rango",
                "B2, la del centro",
            ],
            0,
            "En una selección solo hay una celda activa: aquella desde la que empezaste. Se ve sin sombrear.",
        ),
        T(
            "xl1-int-06",
            "La celda `D2` muestra **150** y en la barra de fórmulas pone `=B2*C2`. ¿Qué guarda `D2`?",
            [
                "La fórmula =B2*C2; 150 es su resultado",
                "El número 150",
                "El texto «=B2*C2»",
                "Nada: el valor está en B2",
            ],
            0,
            "La celda guarda la fórmula y muestra el resultado. Si cambias B2 o C2, el 150 cambia solo.",
        ),
        T(
            "xl1-int-07",
            "¿Cómo se llama la celda de la **columna C** y la **fila 4**?",
            ["C4", "4C", "C-4", "D3"],
            0,
            "Primero la letra de la columna y después el número de la fila.",
        ),
        T(
            "xl1-int-08",
            "La Gestoría Albaida quiere separar clientes, facturas y notas **en el mismo archivo**. ¿Qué hace?",
            [
                "Crea tres hojas en el mismo libro y les cambia el nombre",
                "Crea tres libros distintos",
                "Lo escribe todo en la misma columna",
                "Crea tres cintas de opciones",
            ],
            0,
            "Un libro puede tener muchas hojas. Cada hoja con un nombre claro mantiene el archivo ordenado.",
        ),
        R(
            "xl1-int-09",
            "¿Qué devuelve la fórmula con estos datos?",
            "=B3",
            120,
            "`=B3` lee la celda B3: columna B (Cuota), fila 3 (Talleres Sol).",
            grid=CLIENTES,
        ),
        R(
            "xl1-int-10",
            "¿Qué devuelve la fórmula con estos datos? Escribe el texto tal cual.",
            "=A4",
            "Luis Gil",
            "`=A4` lee la celda A4: columna A (Cliente), fila 4.",
            grid=CLIENTES,
            answer_input="text",
        ),
        R(
            "xl1-int-11",
            "La celda `C2` está vacía. ¿Qué devuelve la fórmula?",
            "=C2",
            0,
            "Una fórmula que lee una celda vacía muestra 0: al calcular, Excel trata la celda vacía como 0.",
            grid=CLIENTES,
            options=[0, 45, "Ana Ruiz"],
        ),
    ],
)

# ---------------------------------------------------------------- xl1-datos

DATOS = unit(
    "xl1-datos",
    "Introducir datos",
    hours=2,
    level=1,
    requires=["xl1-interfaz"],
    objectives=[
        "Introducir texto, números, fechas y horas sabiendo cómo los interpreta Excel.",
        "Reconocer un «número almacenado como texto» y lo que provoca en los cálculos.",
        "Usar el autorrelleno para crear series y deshacer un error con Ctrl+Z.",
    ],
    theory="""
## Cómo decide Excel el tipo de dato

Cuando escribes en una celda y pulsas Intro, Excel decide qué es:

| Escribes | Excel guarda | Pista visual (formato General) |
|---|---|---|
| `Ana Ruiz` | Texto | Alineado a la izquierda |
| `12,5` | Número 12,5 | Alineado a la derecha |
| `1.200` | Número 1200 | Alineado a la derecha |
| `17/11/2026` | Una fecha (un número de serie con formato de fecha) | Alineado a la derecha |
| `9:30` | Una hora (una fracción de día) | Alineado a la derecha |

En Excel en español de España **la coma es el separador decimal** y el punto separa los miles. Si escribes `1,200` creyendo que es mil doscientos, Excel guarda **1,2**.

## Números almacenados como texto

A veces un número llega como texto: copiado de una web, de un CSV o escrito con un apóstrofo delante (`'120`). Se nota porque se alinea a la izquierda y Excel pone un **triángulo verde** en la esquina con el aviso «Número almacenado como texto».

- Las funciones como `SUMA` **ignoran el texto** de un rango: `=SUMA(A2:A3)` con «120» (texto) y 80 da **80**.
- Los operadores como `+` **sí convierten** el texto que parece un número: `=A2+A3` da **200**.

Por eso un número como texto es peligroso: unas fórmulas lo cuentan y otras no. La solución es convertirlo en número (el menú del triángulo verde ofrece «Convertir en número»).

## Autorrelleno y deshacer

- El **controlador de relleno** es el cuadradito de la esquina inferior derecha de la celda activa. Si escribes `5` y `10` en dos celdas, las seleccionas y arrastras, Excel sigue la serie: 15, 20, 25…
- Con textos conocidos también funciona: «enero» → «febrero», «marzo»…
- **Ctrl+Z** deshace el último cambio y **Ctrl+Y** lo rehace.
""",
    examples=[
        example(
            "xl1-dat-ej1",
            "SUMA ignora el número escrito como texto",
            "=SUMA(A2:A3)",
            80,
            "A2 guarda el texto «120», no el número. SUMA ignora el texto de un rango y solo suma el 80.",
            grid={"A1": "Importe", "A2": "120", "A3": 80},
        ),
        example(
            "xl1-dat-ej2",
            "El operador + sí lo convierte",
            "=A2+A3",
            200,
            "El operador `+` convierte el texto «120» en el número 120 y suma 120 + 80.",
            grid={"A1": "Importe", "A2": "120", "A3": 80},
        ),
    ],
    guided="xl1-dat-07",
    guided_steps=[
        "Mira cada celda del rango: ¿cuál es un número y cuál un texto (está entre comillas en el enunciado o alineada a la izquierda)?",
        "SUMA solo suma los números del rango.",
        "Suma solo las celdas que son números.",
    ],
    case=(
        "Caso: alta de clientes de la gestoría",
        """
La Gestoría Albaida da de alta 10 clientes con su **fecha de alta** y su **cuota mensual**. Un compañero copió las cuotas desde un correo y algunas llegaron como texto.

1. Escribe en una hoja las columnas Cliente, Fecha de alta y Cuota con 10 clientes inventados.
2. Escribe las fechas como `dd/mm/aaaa` y comprueba que se alinean a la derecha.
3. Escribe una cuota con un apóstrofo delante (`'60`) y observa el triángulo verde.
4. Pon un total con `=SUMA(...)` debajo: ¿cuenta esa cuota? Conviértela en número y vuelve a mirar el total.
""",
    ),
    mistakes=[
        (
            "Escribir `1,200` creyendo que es mil doscientos.",
            "En es-ES la coma es decimal: queda 1,2. Para mil doscientos escribe `1200` o `1.200`.",
        ),
        (
            "Dejar números con espacios o copiados como texto.",
            "Si un número se alinea a la izquierda o tiene el triángulo verde, conviértelo en número antes de sumar.",
        ),
        (
            "Escribir las fechas como texto (`17-nov`, `17.11.2026`).",
            "Usa el formato que Excel reconoce en es-ES, `17/11/2026`, y comprueba que se alinea a la derecha.",
        ),
    ],
    summary=[
        "Texto a la izquierda, números y fechas a la derecha (con formato General).",
        "En es-ES, coma decimal y punto de miles.",
        "SUMA ignora el texto de un rango; `+` convierte el texto numérico.",
        "El controlador de relleno continúa series; Ctrl+Z deshace.",
    ],
    faq=[
        (
            "¿Por qué Excel guarda las fechas como números?",
            "Para poder calcular con ellas: restar dos fechas da los días que hay entre ellas. El formato de fecha solo cambia cómo se ve. Las funciones de fechas llegan en M07.",
        ),
        (
            "¿Y si quiero que un código como 00123 no pierda los ceros?",
            "Escríbelo como texto (con formato Texto o con un apóstrofo delante). Es un código, no un número para sumar.",
        ),
    ],
    sources=[
        (
            "Introducir datos manualmente en celdas de hojas de cálculo",
            "https://support.microsoft.com/es-es/office/introducir-datos-manualmente-en-celdas-de-hojas-de-c%C3%A1lculo-c798181d-d75a-41b1-92ad-6c0800f80038",
        ),
        (
            "Escribir una serie de números, fechas u otros elementos",
            "https://support.microsoft.com/es-es/excel/enter-a-series-of-numbers-dates-or-other-items",
        ),
        (
            "Corregir números con formato de texto aplicando un formato de número",
            "https://support.microsoft.com/es-es/office/corregir-n%C3%BAmeros-con-formato-de-texto-aplicando-un-formato-de-n%C3%BAmero-6599c03a-954d-4d83-b78a-23af2c8845d0",
        ),
    ],
    questions=[
        T(
            "xl1-dat-01",
            "Con Excel en español de España escribes `1,200` en una celda. ¿Qué guarda?",
            ["El número 1,2", "El número mil doscientos", "El texto «1,200»", "Un error"],
            0,
            "En es-ES la coma es el separador decimal: 1,200 es 1,2.",
        ),
        T(
            "xl1-dat-02",
            "Con el formato General, ¿cómo distingues a simple vista un número de un texto?",
            [
                "El número se alinea a la derecha y el texto a la izquierda",
                "Los números salen en negrita",
                "El texto sale en rojo",
                "No se pueden distinguir",
            ],
            0,
            "Es una pista útil: un «número» alineado a la izquierda probablemente es texto.",
        ),
        T(
            "xl1-dat-03",
            "Una celda con 250 tiene un triángulo verde en la esquina superior izquierda. ¿Qué significa?",
            [
                "Excel avisa de un posible problema, como un número almacenado como texto",
                "La celda está protegida",
                "La celda tiene una nota",
                "La celda está vinculada a otro libro",
            ],
            0,
            "El triángulo verde es un aviso de comprobación de errores. Al seleccionar la celda aparece un menú con la explicación.",
        ),
        T(
            "xl1-dat-04",
            "Escribes `17/11/2026`. ¿Qué guarda Excel?",
            [
                "Una fecha: un número de serie que se muestra con formato de fecha",
                "El texto «17/11/2026»",
                "La división 17 entre 11 entre 2026",
                "Tres números en tres celdas",
            ],
            0,
            "Excel reconoce la fecha y guarda un número de serie; así puede calcular con fechas.",
        ),
        T(
            "xl1-dat-05",
            "Escribes 5 en `A1` y 10 en `A2`, seleccionas las dos y arrastras el controlador de relleno hasta `A5`. ¿Qué aparece en `A3:A5`?",
            ["15, 20 y 25", "5, 10 y 5", "10, 10 y 10", "15, 15 y 15"],
            0,
            "Con dos valores seleccionados, Excel calcula el paso (5) y continúa la serie.",
        ),
        T(
            "xl1-dat-06",
            "Acabas de borrar sin querer una columna llena de datos. ¿Qué haces primero?",
            [
                "Pulsar Ctrl+Z para deshacer",
                "Volver a escribirlo todo",
                "Pulsar Ctrl+Y",
                "Cerrar el libro sin guardar, siempre",
            ],
            0,
            "Ctrl+Z deshace el último cambio. Ctrl+Y rehace lo que acabas de deshacer.",
        ),
        R(
            "xl1-dat-07",
            "B3 guarda la cuota «60» como **texto**. ¿Qué devuelve la fórmula?",
            "=SUMA(B2:B4)",
            75,
            "SUMA ignora el texto de un rango: suma solo 45 + 30.",
            grid={
                "A1": "Cliente",
                "B1": "Cuota",
                "A2": "Ana Ruiz",
                "B2": 45,
                "A3": "Luis Gil",
                "B3": "60",
                "A4": "Marta Sanz",
                "B4": 30,
            },
        ),
        R(
            "xl1-dat-08",
            "B3 guarda la cuota «60» como **texto**. ¿Qué devuelve la fórmula?",
            "=B2+B3+B4",
            135,
            "El operador `+` convierte el texto «60» en número: 45 + 60 + 30.",
            grid={
                "A1": "Cliente",
                "B1": "Cuota",
                "A2": "Ana Ruiz",
                "B2": 45,
                "A3": "Luis Gil",
                "B3": "60",
                "A4": "Marta Sanz",
                "B4": 30,
            },
        ),
        R(
            "xl1-dat-09",
            "Alguien escribió `1,200` en A1 queriendo decir mil doscientos. ¿Qué devuelve la fórmula?",
            "=A1*1000",
            1200,
            "A1 guarda 1,2 (la coma es decimal), así que 1,2 × 1000 = 1200. El error de A1 se arrastra a todo lo que la use.",
            grid={"A1": 1.2},
        ),
        R(
            "xl1-dat-10",
            "A3 tiene 30 y A4 está vacía. ¿Qué devuelve la fórmula?",
            "=A3+A4",
            30,
            "Una celda vacía vale 0 al operar: 30 + 0.",
            grid={"A1": "Cuota", "A2": 15, "A3": 30},
        ),
        R(
            "xl1-dat-11",
            "A2 guarda «9» como **texto** y A3 el número 9. ¿Qué devuelve la fórmula?",
            "=SUMA(A2:A3)+A2",
            18,
            "SUMA(A2:A3) ignora el texto y da 9; después `+A2` convierte el texto «9» y suma 9 más: 18.",
            grid={"A1": "Unidades", "A2": "9", "A3": 9},
        ),
    ],
)

# ---------------------------------------------------------------- xl1-formatos

FORMATOS = unit(
    "xl1-formatos",
    "Formatos de número",
    hours=2,
    level=2,
    requires=["xl1-datos"],
    objectives=[
        "Aplicar los formatos General, Número, Moneda, Contabilidad, Porcentaje y Fecha.",
        "Explicar que el formato cambia cómo se ve un valor, no el valor guardado.",
        "Predecir el resultado de una fórmula que usa celdas con formato.",
    ],
    theory="""
## El formato cambia cómo se ve, no lo que vale

Un formato de número es una «máscara» sobre el valor. La celda puede mostrar `2,68 €` mientras guarda `2,675`: lo ves en la barra de fórmulas. **Las fórmulas siempre usan el valor guardado.**

| Formato | El valor 1234,5 se ve | Para qué |
|---|---|---|
| General | 1234,5 | Lo que Excel decide |
| Número (2 decimales, miles) | 1.234,50 | Cantidades |
| Moneda | 1.234,50 € | Importes sueltos |
| Contabilidad | 1.234,50 € (símbolo y decimales alineados en la columna; el 0 se ve como un guion) | Columnas de importes |
| Porcentaje | 123450,00 % | Tasas: 0,21 se ve 21 % |
| Fecha | Un día del calendario | Fechas |

Se cambian en **Inicio > Número** o con **Ctrl+1** (Formato de celdas).

## Decimales que se ven y decimales que se guardan

Los botones «Aumentar decimales» y «Disminuir decimales» solo cambian lo que se ve. Si tres celdas guardan 1,004 y se ven «1,00», su suma da **3,012**, no 3. Para cambiar el valor de verdad se usa la función `REDONDEAR` (unidad xl2-contar).

## Porcentajes

El formato porcentaje **multiplica por 100 solo al mostrar**: la celda guarda 0,21 y se ve «21 %». Por eso:

- `=100*C1` con C1 = 0,21 da **21**.
- Si una celda ya contiene **21** y le aplicas formato porcentaje, verás **2100 %**: el valor sigue siendo 21. Escribe 0,21 (o escribe 21 % directamente).

## Formato personalizado (idea básica)

En Formato de celdas > Personalizada, el código `0,00` fija dos decimales y `#.##0` añade el separador de miles. Más adelante (M03) se ven con detalle.
""",
    examples=[
        example(
            "xl1-for-ej1",
            "La fórmula usa el valor guardado",
            "=B2*100",
            267.5,
            "B2 se ve «2,68 €» pero guarda 2,675: 2,675 × 100 = 267,5.",
            grid={"A2": "Precio", "B2": {"v": 2.675, "format": "currency"}},
        ),
        example(
            "xl1-for-ej2",
            "Un porcentaje es un número entre 0 y 1",
            "=100*C1",
            21,
            "C1 se ve «21 %» y guarda 0,21: 100 × 0,21 = 21.",
            grid={"B1": "IVA", "C1": {"v": 0.21, "format": "percent"}},
        ),
    ],
    guided="xl1-for-07",
    guided_steps=[
        "Fíjate en el valor guardado, no en el que se ve (el enunciado lo dice).",
        "Haz la operación con el valor guardado.",
        "Escribe el resultado con todos sus decimales.",
    ],
    case=(
        "Caso: la tarifa de precios del Taller Montesol",
        """
El Taller Montesol (empresa ficticia) publica una tarifa con los precios con IVA y quiere que todos se vean con **dos decimales y el símbolo €**.

1. Escribe cinco servicios con su precio sin IVA y en otra celda el tipo de IVA, 0,21, con formato porcentaje.
2. Calcula el precio con IVA de cada servicio (en M01 ya sabes multiplicar celdas; en xl1-referencias aprenderás a copiar la fórmula).
3. Aplica formato Moneda a los precios y compara con Contabilidad: ¿qué cambia en la columna?
4. Mira en la barra de fórmulas un precio que se vea redondeado: ¿cuántos decimales guarda?
""",
    ),
    mistakes=[
        (
            "Creer que reducir decimales redondea el valor.",
            "Solo cambia lo que se ve. Los cálculos siguen usando todos los decimales; para redondear el valor usa REDONDEAR.",
        ),
        (
            "Escribir 21 en una celda y aplicarle después formato porcentaje (se ve 2100 %).",
            "Escribe 0,21, o escribe directamente 21 %, que Excel guarda como 0,21.",
        ),
        (
            "Confundir Moneda y Contabilidad.",
            "Las dos muestran el símbolo; Contabilidad además alinea símbolo y decimales en la columna y muestra el 0 como un guion.",
        ),
    ],
    summary=[
        "El formato es una máscara: la barra de fórmulas enseña el valor de verdad.",
        "Las fórmulas usan el valor guardado, con todos sus decimales.",
        "Porcentaje: 0,21 se ve 21 %.",
        "Para cambiar el valor, REDONDEAR; para cambiar cómo se ve, el formato.",
    ],
    faq=[
        (
            "¿Dónde están todos los formatos?",
            "En Inicio > Número, en la lista desplegable, o con Ctrl+1 (Formato de celdas), que tiene todas las opciones.",
        ),
        (
            "¿El formato se copia con la celda?",
            "Sí. Copiar y pegar lleva el valor y el formato; Pegado especial permite pegar solo uno de los dos.",
        ),
    ],
    sources=[
        (
            "Formatos de número disponibles en Excel",
            "https://support.microsoft.com/es-es/excel/get-started/available-number-formats-in-excel",
        ),
        (
            "Dar formato a números como moneda en Excel",
            "https://support.microsoft.com/es-es/excel/format-numbers-as-currency-in-excel",
        ),
    ],
    questions=[
        T(
            "xl1-for-01",
            "Una celda muestra **2,68 €** y en la barra de fórmulas pone **2,675**. ¿Qué valor usa una fórmula que la lea?",
            ["2,675", "2,68", "2,7", "3"],
            0,
            "El formato solo cambia lo que se ve; las fórmulas usan el valor guardado.",
        ),
        T(
            "xl1-for-02",
            "¿Qué hace el formato Porcentaje con una celda que guarda 0,15?",
            [
                "La muestra como 15 % sin cambiar el valor 0,15",
                "Cambia el valor a 15",
                "Cambia el valor a 0,0015",
                "La convierte en texto",
            ],
            0,
            "El porcentaje multiplica por 100 solo al mostrar.",
        ),
        T(
            "xl1-for-03",
            "¿En qué se diferencia el formato Contabilidad del formato Moneda?",
            [
                "Contabilidad alinea el símbolo y los decimales en la columna y muestra el 0 como un guion",
                "Moneda solo sirve para dólares",
                "Contabilidad redondea los importes",
                "No hay ninguna diferencia",
            ],
            0,
            "Los dos muestran el símbolo de moneda; Contabilidad está pensado para columnas de importes.",
        ),
        T(
            "xl1-for-04",
            "Una celda contiene **21** y le aplicas el formato Porcentaje. ¿Qué se ve?",
            ["2100 %", "21 %", "0,21 %", "0,21"],
            0,
            "El valor es 21 y el porcentaje lo multiplica por 100 al mostrarlo: 2100 %. Había que escribir 0,21.",
        ),
        T(
            "xl1-for-05",
            "Quieres que los precios se vean siempre con dos decimales **sin cambiar su valor**. ¿Qué haces?",
            [
                "Aplicar formato Número o Moneda con 2 decimales",
                "Escribir los precios como texto",
                "Borrar a mano los decimales que sobran",
                "Multiplicarlos por 100",
            ],
            0,
            "El formato cambia solo la presentación, que es lo que se pide.",
        ),
        T(
            "xl1-for-06",
            "¿Qué formato pondrías a una columna con las fechas de las facturas?",
            ["Fecha", "Porcentaje", "Contabilidad", "Texto"],
            0,
            "Con formato Fecha se ven como días del calendario y siguen siendo números con los que calcular.",
        ),
        R(
            "xl1-for-07",
            "B2 se ve **20,00** pero guarda 19,999. ¿Qué devuelve la fórmula? Escribe todos los decimales.",
            "=B2*10",
            199.99,
            "La fórmula usa el valor guardado: 19,999 × 10 = 199,99 (no 200).",
            grid={"A2": "Precio", "B2": {"v": 19.999, "format": 2}},
            tolerance=0.0001,
        ),
        R(
            "xl1-for-08",
            "C1 se ve **7 %**. ¿Qué devuelve la fórmula?",
            "=A2*C1",
            105,
            "C1 guarda 0,07: 1500 × 0,07 = 105.",
            grid={"A1": "Base", "A2": 1500, "B1": "Tipo", "C1": {"v": 0.07, "format": "percent"}},
        ),
        R(
            "xl1-for-09",
            "B2 se ve **50 %**. ¿Qué devuelve la fórmula?",
            "=B2+1",
            1.5,
            "B2 guarda 0,5: 0,5 + 1 = 1,5.",
            grid={"A2": "Descuento", "B2": {"v": 0.5, "format": "percent"}},
        ),
        R(
            "xl1-for-10",
            "Las tres celdas se ven **1,00** pero cada una guarda 1,004. ¿Qué devuelve la fórmula? Escribe todos los decimales.",
            "=B2+B3+B4",
            3.012,
            "Se suman los valores guardados: 1,004 × 3 = 3,012. Por eso a veces un total «no cuadra» con lo que se ve.",
            grid={
                "B1": "Importe",
                "B2": {"v": 1.004, "format": 2},
                "B3": {"v": 1.004, "format": 2},
                "B4": {"v": 1.004, "format": 2},
            },
            tolerance=0.0001,
        ),
        R(
            "xl1-for-11",
            "A1 se ve **1.234,50 €**. ¿Qué devuelve la fórmula?",
            "=A1/2",
            617.25,
            "A1 guarda 1234,5: 1234,5 / 2 = 617,25. El símbolo € es solo formato.",
            grid={"A1": {"v": 1234.5, "format": "currency"}},
        ),
    ],
)

# ---------------------------------------------------------------- xl1-referencias

IVA_GRID = {
    "A1": "Factura",
    "B1": "Base",
    "A2": "F-101",
    "B2": 100,
    "A3": "F-102",
    "B3": 250,
    "A4": "F-103",
    "B4": 80,
    "A5": "F-104",
    "B5": 40,
    "A6": "F-105",
    "B6": 1000,
    "D1": "IVA",
    "E1": 0.21,
}
TABLA_GRID = {"A2": 1, "A3": 2, "A4": 3, "B1": 1, "C1": 2, "D1": 3}

REFERENCIAS = unit(
    "xl1-referencias",
    "Referencias relativas, absolutas y mixtas",
    hours=3,
    level=2,
    requires=["xl1-formatos"],
    objectives=[
        "Explicar qué le pasa a `A1`, `$A$1`, `A$1` y `$A1` al copiar una fórmula.",
        "Elegir el tipo de referencia correcto para que una fórmula se pueda copiar.",
        "Cambiar el tipo de referencia con F4 y guardar las tasas en una celda, nunca dentro de la fórmula.",
    ],
    theory="""
## Copiar una fórmula mueve sus referencias

Si `D2` tiene `=B2*C2` y la copias a `D3`, Excel escribe `=B3*C3`: las referencias se desplazan lo mismo que la fórmula. Son **referencias relativas** y son lo que quieres casi siempre (cada fila calcula con sus datos).

Para copiar, arrastra el **controlador de relleno** o haz doble clic en él: rellena hasta el final de los datos de la columna de al lado.

## Fijar con $

A veces una celda tiene que quedarse quieta: el tipo de IVA en `E1` vale para todas las facturas. El símbolo `$` fija lo que va detrás:

| Referencia | Al copiar hacia abajo | Al copiar hacia la derecha | Nombre |
|---|---|---|---|
| `E1` | `E2`, `E3`… | `F1`, `G1`… | Relativa |
| `$E$1` | `$E$1` | `$E$1` | Absoluta |
| `E$1` | `E$1` | `F$1`, `G$1`… | Mixta: fila fija |
| `$E1` | `$E2`, `$E3`… | `$E1` | Mixta: columna fija |

Con el cursor sobre una referencia de la fórmula, **F4** la va cambiando: `E1` → `$E$1` → `E$1` → `$E1` → `E1`.

## El IVA, paso a paso

1. En `D2` escribe `=B2*` y haz clic en `E1`.
2. Pulsa **F4**: queda `=B2*$E$1`. Intro.
3. Copia `D2` hasta `D6`. En `D3` verás `=B3*$E$1`: la base cambia y el tipo no.

Si hubieras escrito `=B2*E1`, en `D3` quedaría `=B3*E2`, que está vacía: el IVA saldría 0. Y si escribes `=B2*0,21`, funciona hoy, pero el día que cambie el tipo tendrás que cambiar todas las fórmulas. **Las tasas van en una celda de datos.**

## Tablas de doble entrada

Para una tabla que se copia en horizontal y en vertical hacen falta referencias mixtas. En una tabla de multiplicar, `=$A2*B$1` fija la columna A (los números de la izquierda) y la fila 1 (los de arriba).
""",
    examples=[
        example(
            "xl1-ref-ej1",
            "IVA con la tasa fija",
            "=B2*$E$1",
            21,
            "100 × 0,21 = 21. Al copiarla, B2 pasa a B3, B4… y $E$1 se queda fija.",
            grid=IVA_GRID,
            cell="D2",
        ),
        example(
            "xl1-ref-ej2",
            "La copia de una fórmula mixta",
            "=$A3*C$1",
            4,
            "Es `=$A2*B$1` copiada de B2 a C3: la columna A y la fila 1 no se mueven. 2 × 2 = 4.",
            grid=TABLA_GRID,
            cell="C3",
        ),
    ],
    guided="xl1-ref-07",
    guided_steps=[
        "Escribe la fórmula para la primera factura: base por tipo de IVA.",
        "Piensa qué pasa al copiarla hacia abajo: la base tiene que cambiar y el tipo no.",
        "Fija el tipo con $ (tecla F4): $E$1.",
    ],
    case=(
        "Caso: el IVA de las facturas del mes",
        """
La Gestoría Albaida prepara el IVA de las facturas de un cliente. El tipo general está en la celda `E1` para poder cambiarlo si cambia la ley.

1. Escribe cinco facturas con su base imponible en `B2:B6` y 0,21 en `E1`.
2. En `D2` calcula el IVA con una sola fórmula y cópiala hasta `D6`.
3. Cambia `E1` a 0,10: ¿se actualizan todas las cuotas?
4. Añade en `F2` el total de la factura (base + IVA) y cópialo hacia abajo.
""",
    ),
    mistakes=[
        (
            "Copiar `=B2*E1` hacia abajo.",
            "E1 se desplaza a E2, E3… que están vacías, y el IVA sale 0. Fija la tasa: `=B2*$E$1`.",
        ),
        (
            "Escribir la tasa dentro de la fórmula (`=B2*0,21`).",
            "Funciona hasta que cambia el tipo. Pon la tasa en una celda y referénciala con $.",
        ),
        (
            "Fijarlo todo con $ «por si acaso» (`=$B$2*$E$1`).",
            "Entonces todas las filas calculan con B2. Fija solo lo que no debe moverse.",
        ),
    ],
    summary=[
        "Relativa (A1): se mueve al copiar. Absoluta ($A$1): no se mueve.",
        "Mixtas: A$1 fija la fila; $A1 fija la columna.",
        "F4 cambia el tipo de referencia.",
        "Las tasas y constantes van en celdas de datos, no dentro de la fórmula.",
    ],
    faq=[
        (
            "¿Y si muevo una fórmula en vez de copiarla?",
            "Al cortar y pegar, Excel no cambia las referencias: la fórmula sigue apuntando a las mismas celdas.",
        ),
        (
            "¿F4 funciona en un portátil?",
            "En muchos portátiles hay que pulsar Fn+F4. También puedes escribir el $ a mano.",
        ),
    ],
    sources=[
        (
            "Cambiar entre referencias relativas, absolutas y mixtas",
            "https://support.microsoft.com/es-es/excel/switch-between-relative-absolute-and-mixed-references",
        ),
        (
            "Mover o copiar una fórmula",
            "https://support.microsoft.com/es-es/excel/move-or-copy-a-formula-in-excel",
        ),
    ],
    required=["xl1-ref-07", "xl1-ref-10"],
    questions=[
        T(
            "xl1-ref-01",
            "Copias `=A1+B1` de `C1` a `C2`. ¿Qué fórmula queda en `C2`?",
            ["=A2+B2", "=A1+B1", "=A2+B1", "=B2+C2"],
            0,
            "Las referencias relativas bajan una fila, igual que la fórmula.",
        ),
        T(
            "xl1-ref-02",
            "¿Qué referencia **no cambia** ni al copiar hacia abajo ni hacia la derecha?",
            ["$E$1", "E$1", "$E1", "E1"],
            0,
            "Con $ delante de la columna y de la fila, la referencia queda totalmente fija.",
        ),
        T(
            "xl1-ref-03",
            "Copias `=B$1` una fila hacia abajo y una columna hacia la derecha. ¿Qué queda?",
            ["=C$1", "=B$1", "=C$2", "=B$2"],
            0,
            "La fila está fija ($1); la columna es relativa y pasa de B a C.",
        ),
        T(
            "xl1-ref-04",
            "Con el cursor sobre `E1` dentro de una fórmula pulsas **F4** una vez. ¿Qué queda?",
            ["$E$1", "E$1", "$E1", "E1 entre comillas"],
            0,
            "La primera pulsación fija columna y fila; las siguientes pasan por E$1, $E1 y vuelven a E1.",
        ),
        T(
            "xl1-ref-05",
            "¿Por qué es mejor `=B2*$E$1` (con 0,21 en E1) que `=B2*0,21`?",
            [
                "Si el tipo cambia, se cambia en una sola celda y todas las fórmulas se actualizan",
                "Porque 0,21 da error en una fórmula",
                "Porque las fórmulas no admiten decimales",
                "Porque ocupa menos memoria",
            ],
            0,
            "Los datos que pueden cambiar van en celdas; las fórmulas solo los referencian.",
        ),
        T(
            "xl1-ref-06",
            "Copias `=$A2` tres columnas a la derecha. ¿Qué queda?",
            ["=$A2", "=D2", "=$D2", "=$A5"],
            0,
            "La columna está fija ($A) y la fila no cambia porque no te has movido en vertical.",
        ),
        F(
            "xl1-ref-07",
            "Escribe en `D2` el IVA de la factura (base × tipo de `E1`) de forma que funcione al copiarla hasta `D6`.",
            grid=IVA_GRID,
            cell="D2",
            expect=21,
            checks=[
                {"type": "value"},
                {"type": "fill", "to": "D6", "expect": [52.5, 16.8, 8.4, 210]},
                {"type": "variants", "count": 2},
                {"type": "references", "must": ["B2", "$E$1"]},
                {"type": "noConstants"},
            ],
            solution="=B2*$E$1",
            mistakes=[
                ("=B2*E1", "Al copiarla, E1 pasa a E2, E3…, que están vacías, y el IVA sale 0."),
                (
                    "=B2*0,21",
                    "Funciona, pero el tipo está escrito a mano: si cambia, hay que cambiar todas las fórmulas.",
                ),
            ],
            hints=[
                "La base cambia en cada fila; el tipo de IVA es siempre el de E1.",
                "Fija E1 con $ (tecla F4): $E$1.",
            ],
            explain="`=B2*$E$1`: B2 se mueve al copiar (cada factura su base) y $E$1 se queda fija.",
            vary=["B2:B6", "E1"],
        ),
        R(
            "xl1-ref-08",
            "Alguien copió `=B2*E1` de `D2` a `D3`, y en `D3` quedó esta fórmula. ¿Qué devuelve?",
            "=B3*E2",
            0,
            "E2 está vacía (vale 0): 250 × 0 = 0. Es el error típico de no fijar la tasa.",
            grid=IVA_GRID,
            cell="D3",
        ),
        R(
            "xl1-ref-09",
            "Esta es la copia en `D3` de `=$A2*B$1`. ¿Qué devuelve?",
            "=$A3*D$1",
            6,
            "Fila 3 de la columna A (2) por la columna D de la fila 1 (3): 6.",
            grid=TABLA_GRID,
            cell="D3",
        ),
        F(
            "xl1-ref-10",
            "Escribe en `B2` una fórmula que, copiada hasta `D4`, dé la tabla de multiplicar de los números de la columna A por los de la fila 1.",
            grid=TABLA_GRID,
            cell="B2",
            expect=1,
            checks=[
                {"type": "value"},
                {"type": "fill", "to": "D4", "expect": [2, 3, 2, 4, 6, 3, 6, 9]},
            ],
            solution="=$A2*B$1",
            mistakes=[
                (
                    "=A2*B1",
                    "Al copiarla a la derecha, A2 pasa a B2; y hacia abajo, B1 pasa a B2: la tabla sale mal.",
                ),
                ("=$A$2*$B$1", "Todo fijo: todas las celdas dan 1 × 1."),
            ],
            hints=[
                "Al copiar a la derecha, la columna A no se puede mover.",
                "Al copiar hacia abajo, la fila 1 no se puede mover.",
                "Necesitas dos referencias mixtas: $A2 y B$1.",
            ],
            explain="`=$A2*B$1`: $A fija la columna de los números de la izquierda y $1 la fila de los de arriba.",
        ),
        R(
            "xl1-ref-11",
            "¿Qué devuelve la fórmula?",
            "=$B$1*A3",
            70,
            "$B$1 vale 10 y A3 vale 7: 70.",
            grid={"A1": "Tarifa", "B1": 10, "A2": 5, "A3": 7},
            cell="C3",
        ),
        R(
            "xl1-ref-12",
            "Esta es la copia en `C4` de `=B2/$B$6`. ¿Qué devuelve?",
            "=B4/$B$6",
            0.1,
            "B4 (100) entre el total fijo $B$6 (1000): 0,1, es decir, un 10 %.",
            grid={
                "A1": "Zona",
                "B1": "Ventas",
                "B2": 200,
                "B3": 300,
                "B4": 100,
                "B5": 400,
                "A6": "Total",
                "B6": 1000,
            },
            cell="C4",
        ),
        F(
            "xl1-ref-13",
            "Escribe en `C2` la comisión del vendedor (ventas × porcentaje de `F1`) y que funcione al copiarla hasta `C5`.",
            grid={
                "A1": "Vendedor",
                "B1": "Ventas",
                "A2": "Ana",
                "B2": 1200,
                "A3": "Luis",
                "B3": 800,
                "A4": "Marta",
                "B4": 1500,
                "A5": "Raúl",
                "B5": 600,
                "E1": "Comisión",
                "F1": 0.05,
            },
            cell="C2",
            expect=60,
            checks=[
                {"type": "value"},
                {"type": "fill", "to": "C5", "expect": [40, 75, 30]},
                {"type": "references", "must": ["B2", "$F$1"]},
                {"type": "noConstants"},
            ],
            solution="=B2*$F$1",
            mistakes=[
                ("=B2*F1", "Al copiarla, F1 pasa a F2, F3…, vacías: la comisión sale 0."),
                ("=B2*0,05", "El porcentaje está escrito a mano en vez de usar F1."),
            ],
            hints=[
                "Cada fila usa sus ventas; el porcentaje es siempre el de F1.",
                "Fija F1 con $.",
            ],
            explain="`=B2*$F$1`: las ventas son relativas y el porcentaje, absoluto.",
        ),
        F(
            "xl1-ref-14",
            "Escribe en `B2` el precio con el descuento de cada tarifa (precio de la columna A × (1 − descuento de la fila 1)) para copiarla hasta `D4`.",
            grid={
                "A1": "Precio",
                "B1": 0.05,
                "C1": 0.1,
                "D1": 0.15,
                "A2": 100,
                "A3": 250,
                "A4": 40,
            },
            cell="B2",
            expect=95,
            checks=[
                {"type": "value"},
                {"type": "fill", "to": "D4", "expect": [90, 85, 237.5, 225, 212.5, 38, 36, 34]},
                {"type": "noConstants", "except": [1]},
            ],
            solution="=$A2*(1-B$1)",
            mistakes=[
                (
                    "=A2*(1-B1)",
                    "Sin $, al copiarla a la derecha el precio deja de ser el de la columna A.",
                ),
                (
                    "=$A$2*(1-$B$1)",
                    "Todo fijo: todas las celdas dan el precio de A2 con el descuento de B1.",
                ),
            ],
            hints=[
                "El precio siempre está en la columna A; el descuento, siempre en la fila 1.",
                "Usa referencias mixtas: $A2 y B$1.",
            ],
            explain="`=$A2*(1-B$1)`: $A fija la columna del precio y $1 la fila del descuento. El 1 de «1 − descuento» es la única constante permitida.",
        ),
        F(
            "xl1-ref-15",
            "Escribe en `C2` qué parte del total (`B6`) es cada zona, para copiarla hasta `C5`.",
            grid={
                "A1": "Zona",
                "B1": "Ventas",
                "A2": "Norte",
                "B2": 200,
                "A3": "Sur",
                "B3": 300,
                "A4": "Este",
                "B4": 100,
                "A5": "Oeste",
                "B5": 400,
                "A6": "Total",
                "B6": 1000,
            },
            cell="C2",
            expect=0.2,
            checks=[
                {"type": "value"},
                {"type": "fill", "to": "C5", "expect": [0.3, 0.1, 0.4]},
                {"type": "references", "must": ["$B$6"]},
                {"type": "noConstants"},
            ],
            solution="=B2/$B$6",
            mistakes=[
                ("=B2/B6", "Al copiarla, B6 pasa a B7, que está vacía: #¡DIV/0!."),
                (
                    "=B2/1000",
                    "El total está escrito a mano: si cambian las ventas, la fórmula no se entera.",
                ),
            ],
            hints=[
                "Ventas de la zona entre el total.",
                "El total siempre es el de B6: fíjalo con $.",
            ],
            explain="`=B2/$B$6`: cada zona entre el total fijo. Con formato porcentaje se ve 20 %, 30 %…",
        ),
    ],
)

# ---------------------------------------------------------------- xl1-archivos

ARCHIVOS = unit(
    "xl1-archivos",
    "Guardar, exportar y compatibilidad",
    hours=1.5,
    level=1,
    requires=["xl1-datos"],
    objectives=[
        "Elegir entre .xlsx, .xlsm, .csv y PDF según para qué sea el archivo.",
        "Abrir un CSV con separador «;» y tildes sin que se estropee.",
        "Saber que hay funciones que no existen en versiones antiguas y qué indican las etiquetas [2019+], [2021+] y [365].",
    ],
    theory="""
## Formatos de archivo

| Formato | Qué guarda | Cuándo |
|---|---|---|
| `.xlsx` | Todo: hojas, fórmulas, formatos, gráficos. **Sin macros** | El formato normal de trabajo |
| `.xlsm` | Lo mismo **y macros** (código VBA) | Solo si el libro necesita macros |
| `.xls` | Formato antiguo (Excel 97-2003) | Para versiones muy antiguas |
| `.csv` | Texto con los **valores** de **una** hoja, sin fórmulas ni formato | Para pasar datos a otro programa |
| PDF | Una «foto» para leer e imprimir | Para enviar sin que se modifique |

Guardar como CSV un libro con varias hojas y fórmulas guarda **solo la hoja activa y solo los valores**. Excel avisa: lee el aviso antes de aceptar.

## CSV en español

En España la coma es el separador decimal, así que los CSV suelen separar las columnas con **punto y coma** (`;`). Además, las tildes y la ñ necesitan la codificación **UTF-8**. Si al abrir un CSV ves `MÃ¡laga` en vez de `Málaga`, se ha leído con otra codificación.

Para abrirlo bien: **Datos > Obtener datos > De texto/CSV**, elige el origen **65001: Unicode (UTF-8)** y el delimitador **punto y coma**. Para crearlo: **Archivo > Guardar como** y el tipo **CSV UTF-8 (delimitado por comas)**; con la configuración regional de España, Excel separa con `;`.

## Exportar a PDF

**Archivo > Exportar > Crear documento PDF/XPS** (o Guardar como, tipo PDF). Revisa antes la vista previa de impresión: lo que no cabe en la página se corta.

## Macros: seguridad

Un `.xlsm` puede llevar código que se ejecuta en tu equipo. **No habilites las macros de un archivo de origen desconocido.** Microsoft 365 bloquea por defecto las macros de los archivos descargados de internet; si un correo te insiste en que las actives para «ver el contenido», desconfía y confirma con el remitente por otra vía.

## Versiones de Excel

Algunas funciones solo existen en versiones recientes. En este curso las marcamos así: **[2019+]** (Excel 2019 y posteriores), **[2021+]** (Excel 2021 y posteriores) y **[365]** (solo Microsoft 365 y Excel para la web). En una versión que no la tiene, la fórmula da `#¿NOMBRE?`. En M01 y M02 todas las funciones existen en cualquier versión.
""",
    examples=[
        note(
            "Un CSV de clientes, por dentro",
            "`Cliente;Ciudad;Cuota` en la primera línea y `Ana Ruiz;Málaga;45,50` en la segunda: columnas separadas por `;`, decimales con coma y la tilde guardada en UTF-8.",
        ),
    ],
    guided="xl1-arc-03",
    guided_steps=[
        "Piensa qué guarda un CSV: texto, valores y una sola hoja.",
        "Las fórmulas y los formatos no son «valores».",
        "Elige la opción que lo dice.",
    ],
    case=(
        "Caso: exportar el listado de clientes",
        """
La gestoría tiene que pasar su listado de clientes a un programa de facturación que solo lee CSV.

1. Crea una hoja con Cliente, Ciudad (con tildes: Málaga, Cádiz) y Cuota con decimales.
2. Guárdala como **CSV UTF-8** y lee el aviso de Excel.
3. Ábrela con el Bloc de notas: ¿qué separa las columnas? ¿Se ven bien las tildes?
4. Vuelve a abrirla en Excel con Datos > De texto/CSV, eligiendo UTF-8 y punto y coma.
""",
    ),
    mistakes=[
        (
            "Guardar como CSV y perder las fórmulas y el formato sin darte cuenta.",
            "Trabaja en .xlsx y exporta una copia a CSV solo cuando la necesites.",
        ),
        (
            "Abrir un CSV en UTF-8 como si fuera ANSI (tildes estropeadas).",
            "Impórtalo con Datos > De texto/CSV y elige 65001: Unicode (UTF-8).",
        ),
        (
            "Habilitar las macros por costumbre.",
            "Solo en archivos de confianza. Si no sabes de dónde viene un .xlsm, no las actives.",
        ),
    ],
    summary=[
        ".xlsx para trabajar, .xlsm solo con macros, CSV para pasar datos, PDF para enviar.",
        "CSV = valores de una hoja, sin fórmulas ni formato.",
        "En es-ES, CSV con «;» y en UTF-8.",
        "No habilites macros de origen desconocido.",
    ],
    faq=[
        (
            "¿Pierdo algo al abrir un .xlsx en Excel para la web?",
            "Casi nada en lo básico. Las macros no se ejecutan en la web y algunas funciones avanzadas cambian: el curso lo indica cuando importa.",
        ),
        (
            "¿Por qué el CSV no guarda las otras hojas?",
            "Porque un CSV es un archivo de texto con una sola tabla. Si necesitas varias, guarda un CSV por hoja.",
        ),
    ],
    sources=[
        (
            "Formatos de archivo que admite Excel",
            "https://support.microsoft.com/es-es/excel/file-formats-that-are-supported-in-excel",
        ),
        (
            "Importar o exportar archivos de texto (.txt o .csv)",
            "https://support.microsoft.com/es-es/excel/get-started/import-or-export-text-txt-or-csv-files",
        ),
        (
            "Habilitar o deshabilitar macros en archivos de Microsoft 365",
            "https://support.microsoft.com/es-es/office/habilitar-o-deshabilitar-macros-en-archivos-de-microsoft-365-12b036fd-d140-4e74-b45e-16fed1a7e5c6",
        ),
    ],
    warning="Un archivo .xlsm puede contener macros, que son código que se ejecuta en tu equipo. No habilites las macros de archivos de origen desconocido.",
    questions=[
        T(
            "xl1-arc-01",
            "Tienes que enviar un presupuesto a un cliente para que lo lea e imprima, **sin que pueda modificarlo**. ¿Qué formato eliges?",
            ["PDF", ".xlsx", ".csv", ".xlsm"],
            0,
            "El PDF conserva el aspecto y no se edita como una hoja de cálculo.",
        ),
        T(
            "xl1-arc-02",
            "Tu libro tiene macros que quieres conservar. ¿Con qué formato lo guardas?",
            [".xlsm", ".xlsx", ".csv", "PDF"],
            0,
            "El .xlsx no guarda macros; el .xlsm sí.",
        ),
        T(
            "xl1-arc-03",
            "Guardas como CSV un libro con tres hojas, fórmulas y formatos. ¿Qué se guarda?",
            [
                "Solo la hoja activa, con los valores, sin fórmulas ni formato",
                "Las tres hojas",
                "Las fórmulas de la hoja activa",
                "Todo, igual que en .xlsx",
            ],
            0,
            "Un CSV es texto: una tabla de valores. Excel avisa de lo que se pierde.",
        ),
        T(
            "xl1-arc-04",
            "Abres un CSV y donde ponía «Málaga» ves «MÃ¡laga». ¿Qué ha pasado?",
            [
                "El archivo está en UTF-8 y se ha leído con otra codificación: vuelve a importarlo eligiendo UTF-8",
                "El archivo está roto sin remedio",
                "Hay que cambiar la fuente de la celda",
                "Hay que guardarlo como PDF",
            ],
            0,
            "Es un problema de codificación. Datos > De texto/CSV permite elegir 65001: Unicode (UTF-8).",
        ),
        T(
            "xl1-arc-05",
            "¿Por qué en España los CSV suelen separar las columnas con «;»?",
            [
                "Porque la coma es el separador decimal",
                "Porque lo exige la ley",
                "Porque Excel no admite comas",
                "Porque ocupa menos espacio",
            ],
            0,
            "Si las columnas se separasen con comas, «45,50» se partiría en dos columnas.",
        ),
        T(
            "xl1-arc-06",
            "Recibes `factura.xlsm` de un remitente que no conoces y Excel te pide habilitar las macros. ¿Qué haces?",
            [
                "No las habilito y confirmo con el remitente por otra vía",
                "Las habilito para ver la factura",
                "Desactivo el antivirus para abrirlo",
                "Lo reenvío a mis compañeros",
            ],
            0,
            "Las macros son código. Pedir que las actives para ver el contenido es un truco habitual de los ataques.",
        ),
        T(
            "xl1-arc-07",
            "En el curso, una función lleva la etiqueta **[2021+]**. ¿Qué significa?",
            [
                "Existe en Excel 2021 y posteriores (y en Microsoft 365); en versiones anteriores da #¿NOMBRE?",
                "Es obligatoria desde 2021",
                "Solo funciona en Excel para la web",
                "Es de pago",
            ],
            0,
            "Las etiquetas avisan de la versión mínima. Una función desconocida para tu versión da #¿NOMBRE?.",
        ),
        T(
            "xl1-arc-08",
            "¿En qué formato guardas normalmente un libro de trabajo sin macros?",
            [".xlsx", ".csv", ".xls", "PDF"],
            0,
            ".xlsx es el formato actual y guarda fórmulas, formatos y varias hojas.",
        ),
    ],
)

UNITS = [INTERFAZ, DATOS, FORMATOS, REFERENCIAS, ARCHIVOS]
