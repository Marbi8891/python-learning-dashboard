# ruff: noqa: E501
# (contenido didáctico: los textos largos van en una sola línea para poder leerlos y editarlos)
"""M03 · Formato profesional y gestión de libros (4 h): 2 unidades y 21 ejercicios.

Diseño en docs/excel-academy/CURRICULUM_M3_M5.md. Empresas y personas ficticias. Las prácticas
.xlsx del currículo original («X») se sustituyen por ejercicios con cuadrícula, como en el piloto.
"""

from __future__ import annotations

from units import R, T, example, note, unit

# ---------------------------------------------------------------- xl3-formato-celdas

TARIFA = {
    "A1": "Servicio",
    "B1": "Precio",
    "A2": "Cambio de aceite",
    "B2": {"v": 45.5, "format": "currency"},
    "A3": "Revisión completa",
    "B3": {"v": 120, "format": "currency"},
    "A4": "Equilibrado",
    "B4": {"v": 18.75, "format": "currency"},
}

FORMATO = unit(
    "xl3-formato-celdas",
    "Estilos, bordes, alineación y paneles",
    hours=2,
    level=2,
    requires=["xl1-formatos"],
    objectives=[
        "Dar a una tabla un aspecto profesional con estilos de celda, bordes y alineación.",
        "Ajustar el ancho de columna y el alto de fila, y saber qué significa ####.",
        "Inmovilizar la fila de encabezados para que no desaparezca al desplazarte.",
        "Explicar por qué el formato no cambia el valor que usan las fórmulas.",
    ],
    theory="""
## Formato no es contenido

En xl1-formatos viste que el formato de número es una máscara. Con el resto del formato pasa igual: **negrita, colores, bordes y alineación cambian cómo se ve la hoja, nunca el valor de la celda.** Una fórmula que use una celda en rojo y negrita usa el mismo número que si no tuviera formato.

## Estilos de celda

En **Inicio > Estilos de celda** hay estilos ya preparados: *Título*, *Encabezado 1*, *Total*, *Entrada*, *Cálculo*… Usarlos tiene dos ventajas frente a ir cambiando fuente y color a mano:

- Todo el libro queda coherente.
- Si cambias el estilo, cambian a la vez todas las celdas que lo usan.

## Bordes

En **Inicio > Fuente > Bordes** eliges qué lados de la selección tienen línea. Una tabla legible suele tener:

- Un borde inferior grueso bajo la fila de encabezados.
- Un borde superior doble sobre la fila de totales.
- Pocas líneas más: las líneas de la cuadrícula de Excel **no se imprimen** por defecto, los bordes sí.

## Alineación

- Los **textos** se alinean a la izquierda y los **números** a la derecha: así las cifras quedan en columna y se comparan de un vistazo. Si un número aparece a la izquierda sin que lo hayas pedido, sospecha: puede ser un número guardado como texto (xl1-datos).
- **Ajustar texto** reparte un texto largo en varias líneas dentro de la celda.
- **Combinar y centrar** junta varias celdas en una. Úsalo solo en títulos: dentro de una tabla impide ordenar, filtrar y copiar bien. Para centrar un título sobre varias columnas sin combinar, usa *Centrar en la selección* (Formato de celdas > Alineación).

## Ancho de columna y alto de fila

Si una columna es demasiado estrecha para un número, Excel muestra **####**. El valor está bien guardado: solo no cabe. Haz doble clic en el borde derecho del encabezado de la columna para **autoajustar** el ancho al contenido. Un texto largo, en cambio, invade la celda de al lado si está vacía, o se corta si no lo está.

## Inmovilizar paneles

En **Vista > Inmovilizar** puedes dejar fija la **fila superior**, la **primera columna** o ambas (*Inmovilizar paneles*, con la celda activa justo debajo y a la derecha de lo que quieres fijar; por ejemplo, B2 fija la fila 1 y la columna A). Al bajar por una tabla de 500 filas, los encabezados siguen a la vista. Inmovilizar solo afecta a la pantalla: no cambia datos ni impresión.
""",
    examples=[
        example(
            "xl3-for-ej1",
            "El formato no cambia el valor",
            "=SUMA(B2:B4)",
            184.25,
            "Aunque los precios se vean en moneda, negrita o con bordes, SUMA usa los números guardados: 45,5 + 120 + 18,75 = 184,25.",
            grid=TARIFA,
            cell="B5",
        ),
        note(
            "Qué celda elegir para inmovilizar",
            "Para dejar fijas la fila 1 (encabezados) y la columna A (nombres), selecciona **B2** y elige Vista > Inmovilizar > Inmovilizar paneles: se fija todo lo que queda por encima y a la izquierda de la celda activa.",
        ),
    ],
    guided="xl3-for-09",
    guided_steps=[
        "Mira qué celdas usa la fórmula, no cómo están pintadas.",
        "Recuerda que la moneda y la negrita no cambian el número guardado.",
        "Calcula con los valores y escribe el resultado.",
    ],
    case=(
        "Caso: la tarifa del Taller Montesol, lista para imprimir",
        """
El Taller Montesol (empresa ficticia) tiene la tarifa de servicios en una hoja sin formato y quiere dársela a los clientes.

1. Escribe un título, una fila de encabezados (Servicio, Precio sin IVA, Precio con IVA) y ocho servicios.
2. Aplica el estilo *Título* al título y *Encabezado 1* a los encabezados; pon los precios en formato Moneda.
3. Centra el título sobre las tres columnas con *Centrar en la selección*, sin combinar celdas.
4. Añade un borde inferior grueso a los encabezados y autoajusta el ancho de las columnas.
5. Inmoviliza la fila de encabezados y comprueba que sigue a la vista al bajar.
""",
    ),
    mistakes=[
        (
            "Combinar celdas dentro de una tabla de datos.",
            "Impide ordenar, filtrar y copiar rangos. Combina solo títulos, o mejor usa *Centrar en la selección*.",
        ),
        (
            "Pensar que #### es un error del cálculo.",
            "Es que la columna es estrecha para el número. Ensánchala (doble clic en el borde del encabezado) y verás el valor.",
        ),
        (
            "Alinear los números a la izquierda «para que quede bonito».",
            "Los números van a la derecha para que las cifras queden en columna. Un número a la izquierda suele indicar un número guardado como texto.",
        ),
        (
            "Inmovilizar con la celda activa equivocada.",
            "Se fija lo que hay por encima y a la izquierda de la celda activa. Para la fila 1 y la columna A, selecciona B2.",
        ),
    ],
    summary=[
        "El formato cambia cómo se ve, no el valor que usan las fórmulas.",
        "Usa estilos de celda para que el libro sea coherente.",
        "#### = columna estrecha; el valor está bien.",
        "Combinar celdas solo en títulos; en tablas, nunca.",
        "Inmovilizar paneles fija lo que hay encima y a la izquierda de la celda activa.",
    ],
    faq=[
        (
            "¿Las líneas grises de la hoja se imprimen?",
            "No por defecto. Son la cuadrícula de la pantalla. Si quieres líneas en papel, pon bordes o activa Diseño de página > Líneas de la cuadrícula > Imprimir.",
        ),
        (
            "¿Cómo copio solo el formato de una celda a otra?",
            "Con **Copiar formato** (la brocha de Inicio > Portapapeles): un clic lo aplica una vez y doble clic lo deja activo para varias celdas.",
        ),
    ],
    sources=[
        (
            "Cambiar el ancho de las columnas y el alto de las filas",
            "https://support.microsoft.com/es-es/office/cambiar-el-ancho-de-las-columnas-y-el-alto-de-las-filas-72f5e3cc-994d-43e8-ae58-9774a0905f46",
        ),
        (
            "Aplicar o quitar bordes de celda en una hoja de cálculo",
            "https://support.microsoft.com/es-es/office/aplicar-o-quitar-bordes-de-celda-en-una-hoja-de-c%C3%A1lculo-dc8a310b-92e3-46a7-9f17-2ab745810f4a",
        ),
        (
            "Inmovilizar paneles para bloquear filas y columnas",
            "https://support.microsoft.com/es-es/excel/get-started/freeze-panes-to-lock-rows-and-columns",
        ),
    ],
    questions=[
        T(
            "xl3-for-01",
            "Pones en negrita y en rojo la celda B2, que vale 50. ¿Qué devuelve `=B2*2`?",
            ["100", "Un error, porque la celda tiene formato", "50", "Depende del color"],
            0,
            "El formato no cambia el valor: B2 sigue valiendo 50.",
        ),
        T(
            "xl3-for-02",
            "Una celda con un importe muestra `####`. ¿Qué pasa?",
            [
                "La columna es demasiado estrecha para mostrar el número",
                "La fórmula tiene un error",
                "El número es negativo",
                "La celda está protegida",
            ],
            0,
            "Al ensanchar la columna se ve el valor, que estaba bien guardado.",
        ),
        T(
            "xl3-for-03",
            "¿Cuál es la forma más rápida de ajustar el ancho de una columna a su contenido?",
            [
                "Doble clic en el borde derecho del encabezado de la columna",
                "Escribir espacios en la celda",
                "Combinar la celda con la de al lado",
                "Reducir el tamaño de la fuente de toda la hoja",
            ],
            0,
            "El doble clic autoajusta el ancho a la celda más larga de la columna.",
        ),
        T(
            "xl3-for-04",
            "Quieres centrar el título de un informe sobre las columnas A a D sin perder la posibilidad de ordenar la tabla. ¿Qué usas?",
            [
                "Centrar en la selección (Formato de celdas > Alineación)",
                "Combinar y centrar en todas las filas de la tabla",
                "Escribir espacios delante del título",
                "Ajustar texto",
            ],
            0,
            "Centrar en la selección da el mismo aspecto que combinar, pero las celdas siguen siendo independientes.",
        ),
        T(
            "xl3-for-05",
            "En una columna de importes, uno aparece alineado a la izquierda y los demás a la derecha, sin que nadie lo haya cambiado. ¿Qué sospechas?",
            [
                "Que es un número guardado como texto",
                "Que es un número negativo",
                "Que tiene más decimales",
                "Que la columna está inmovilizada",
            ],
            0,
            "Por defecto Excel alinea los números a la derecha y los textos a la izquierda.",
        ),
        T(
            "xl3-for-06",
            "Quieres que la fila 1 (encabezados) y la columna A (nombres) se queden fijas al desplazarte. ¿Qué celda seleccionas antes de Vista > Inmovilizar paneles?",
            ["B2", "A1", "A2", "B1"],
            0,
            "Se inmoviliza lo que queda por encima y a la izquierda de la celda activa: la fila 1 y la columna A.",
        ),
        T(
            "xl3-for-07",
            "¿Qué ventaja tiene aplicar un estilo de celda (por ejemplo, *Encabezado 1*) frente a cambiar fuente y color a mano?",
            [
                "Si cambias el estilo, cambian a la vez todas las celdas que lo usan",
                "Hace que las fórmulas calculen más rápido",
                "Protege las celdas contra cambios",
                "Convierte el rango en una tabla",
            ],
            0,
            "Los estilos mantienen el libro coherente y se modifican en un solo sitio.",
        ),
        T(
            "xl3-for-08",
            "¿Qué se imprime por defecto en una hoja de Excel?",
            [
                "Los bordes que hayas puesto, pero no las líneas grises de la cuadrícula",
                "Las líneas grises de la cuadrícula y los bordes",
                "Solo las líneas de la cuadrícula",
                "Nada de líneas, ni bordes ni cuadrícula",
            ],
            0,
            "La cuadrícula es una ayuda de pantalla; para líneas en papel, usa bordes.",
        ),
        R(
            "xl3-for-09",
            "Los precios se ven en formato moneda. ¿Qué devuelve la fórmula?",
            "=B2+B4",
            64.25,
            "El formato no cambia los valores: 45,5 + 18,75 = 64,25.",
            grid=TARIFA,
            cell="C5",
        ),
        R(
            "xl3-for-10",
            "B2 se ve «1.235 €» porque tiene formato moneda sin decimales, pero guarda 1234,6. ¿Qué devuelve la fórmula?",
            "=B2*2",
            2469.2,
            "La fórmula usa el valor guardado (1234,6), no el que se ve: 1234,6 × 2 = 2469,2.",
            grid={"A2": "Importe", "B2": {"v": 1234.6, "format": 0}},
            cell="C2",
        ),
        R(
            "xl3-for-11",
            "La columna B es tan estrecha que B3 se ve `####`. ¿Qué devuelve la fórmula?",
            "=B3/4",
            2500,
            "#### solo indica que el número no cabe: B3 guarda 10.000 y 10.000 / 4 = 2.500.",
            grid={"A3": "Ventas", "B3": 10000},
            cell="C3",
        ),
    ],
)

# ---------------------------------------------------------------- xl3-libros

TRIMESTRE = {
    "Enero!A2": "Ventas",
    "Enero!B2": 1200,
    "Febrero!A2": "Ventas",
    "Febrero!B2": 950,
    "Marzo!A2": "Ventas",
    "Marzo!B2": 1430,
}

LIBROS = unit(
    "xl3-libros",
    "Hojas, grupos, impresión y vistas",
    hours=2,
    level=2,
    requires=["xl3-formato-celdas", "xl2-hojas"],
    objectives=[
        "Organizar un libro: insertar, mover, copiar, renombrar y colorear hojas.",
        "Editar varias hojas a la vez agrupándolas, sin cambiar las que no querías.",
        "Preparar una hoja para imprimir: área de impresión, orientación, ajustar a una página y títulos en cada página.",
        "Elegir la vista adecuada: Normal, Diseño de página o Ver salto de página.",
    ],
    theory="""
## Las hojas de un libro

Con clic derecho en la pestaña de una hoja puedes **insertar**, **eliminar**, **cambiar el nombre**, **mover o copiar** y darle **color**. Un libro bien organizado tiene hojas con nombres cortos y claros (*Enero*, *Clientes*, *Resumen*), sin espacios si puedes evitarlo: así las referencias entre hojas son más fáciles de escribir (`Enero!B2` en vez de `'Ventas de enero'!B2`, xl2-hojas).

## Agrupar hojas

Si seleccionas varias pestañas (Ctrl+clic, o Mayús+clic para un intervalo), las hojas quedan **agrupadas**: la barra de título muestra **[Grupo]** y todo lo que escribas o el formato que apliques **se hace en todas a la vez**, en las mismas celdas. Es muy útil para preparar doce hojas mensuales iguales.

El peligro: si se te olvida desagrupar, lo que escribas después machaca las otras hojas. Para desagrupar, haz clic en una pestaña que no esté en el grupo, o clic derecho > *Desagrupar hojas*.

## Preparar la impresión

En **Diseño de página**:

- **Área de impresión** > *Establecer*: solo se imprime el rango seleccionado.
- **Orientación**: vertical u horizontal. Una tabla ancha suele ir en horizontal.
- **Ajustar área de impresión** (o *Ajustar hoja en una página* al imprimir): reduce la escala para que quepa.
- **Imprimir títulos** > *Repetir filas en extremo superior*: por ejemplo `$1:$1`, para que la fila de encabezados salga en todas las páginas.
- **Encabezado y pie de página**: número de página («Página 1 de 3»), nombre del archivo o fecha.

Antes de imprimir, mira siempre la **vista previa** (Archivo > Imprimir).

## Vistas

En la pestaña **Vista**:

| Vista | Para qué |
|---|---|
| Normal | Trabajar con los datos |
| Diseño de página | Ver márgenes, encabezado y pie como en el papel |
| Ver salto de página | Ver y mover con el ratón dónde empieza cada página |

Ninguna vista cambia los datos ni las fórmulas: solo cómo ves la hoja.
""",
    examples=[
        example(
            "xl3-lib-ej1",
            "Un resumen de tres hojas con la misma estructura",
            "=Enero!B2+Febrero!B2+Marzo!B2",
            3580,
            "Las tres hojas se prepararon agrupadas, así que las ventas están en la misma celda (B2) de cada una: 1.200 + 950 + 1.430 = 3.580.",
            grid=TRIMESTRE,
            sheet="Resumen",
            cell="B2",
        ),
        note(
            "Repetir los encabezados en cada página",
            "En Diseño de página > Imprimir títulos, escribe `$1:$1` en *Repetir filas en extremo superior*. Si la tabla ocupa tres páginas, las tres empiezan con la fila de encabezados.",
        ),
    ],
    guided="xl3-lib-09",
    guided_steps=[
        "Las hojas se rellenaron agrupadas: el dato está en la misma celda de cada hoja.",
        "La fórmula del resumen toma esa celda de cada hoja.",
        "Suma los tres valores y escribe el resultado.",
    ],
    case=(
        "Caso: el libro trimestral de la Gestoría Albaida",
        """
La Gestoría Albaida (empresa ficticia) quiere un libro con una hoja por mes y un resumen.

1. Crea las hojas Enero, Febrero, Marzo y Resumen, y dales un color distinto.
2. Agrupa Enero, Febrero y Marzo y escribe a la vez los encabezados y el formato de la tabla. Desagrupa.
3. Rellena cada mes con sus datos y calcula el total del trimestre en Resumen con referencias entre hojas.
4. Prepara Resumen para imprimir: orientación horizontal, ajustada a una página, con la fila 1 repetida y «Página X de Y» en el pie.
5. Comprueba el resultado en la vista previa y en Ver salto de página.
""",
    ),
    mistakes=[
        (
            "Olvidar desagrupar las hojas y seguir escribiendo.",
            "Lo que escribes se copia en todas las hojas del grupo. Fíjate en «[Grupo]» en la barra de título y desagrupa al terminar.",
        ),
        (
            "Imprimir una tabla larga sin repetir los encabezados.",
            "Desde la segunda página no se sabe qué es cada columna. Usa Imprimir títulos > Repetir filas en extremo superior.",
        ),
        (
            "Reducir la fuente para que la tabla quepa en una página.",
            "Usa Ajustar a una página o cambia la orientación: el archivo sigue legible en pantalla.",
        ),
        (
            "Nombres de hoja largos y con espacios.",
            "Obligan a escribir comillas en las referencias ('Ventas de enero'!B2). Usa nombres cortos: Enero!B2.",
        ),
    ],
    summary=[
        "Clic derecho en una pestaña: insertar, mover, copiar, renombrar, color.",
        "Hojas agrupadas: lo que haces se aplica a todas. Desagrupa al terminar.",
        "Diseño de página: área de impresión, orientación, ajustar e imprimir títulos.",
        "Las vistas no cambian los datos.",
    ],
    faq=[
        (
            "¿Cómo copio una hoja a otro libro?",
            "Clic derecho en la pestaña > Mover o copiar, elige el libro de destino y marca *Crear una copia*.",
        ),
        (
            "¿Se puede imprimir solo una parte de la hoja sin cambiar el área de impresión?",
            "Sí: selecciona el rango y en Archivo > Imprimir elige *Imprimir selección*.",
        ),
    ],
    sources=[
        (
            "Agrupar hojas de cálculo",
            "https://support.microsoft.com/es-es/office/agrupar-hojas-de-c%C3%A1lculo-4e1f7747-3d63-4fd7-8a36-838b05adc0f0",
        ),
        (
            "Establecer o eliminar un área de impresión en una hoja de cálculo",
            "https://support.microsoft.com/es-es/office/establecer-o-eliminar-un-%C3%A1rea-de-impresi%C3%B3n-en-una-hoja-de-c%C3%A1lculo-27048af8-a321-416d-ba1b-e99ae2182a7e",
        ),
        (
            "Imprimir las filas con los encabezados de columna en la parte superior de todas las páginas",
            "https://support.microsoft.com/es-es/office/imprimir-las-filas-con-los-encabezados-de-columna-en-la-parte-superior-de-todas-las-p%C3%A1ginas-d3550133-f6a1-4c72-ad70-5309a2e8fe8c",
        ),
        ("Ver saltos de página", "https://support.microsoft.com/es-es/excel/view-page-breaks"),
    ],
    questions=[
        T(
            "xl3-lib-01",
            "Seleccionas las pestañas Enero, Febrero y Marzo con Ctrl+clic y escribes «Ventas» en A1. ¿Qué pasa?",
            [
                "Se escribe «Ventas» en A1 de las tres hojas",
                "Solo se escribe en Enero",
                "Excel da un error",
                "Se crea una hoja nueva",
            ],
            0,
            "Las hojas agrupadas reciben a la vez lo que escribes y el formato.",
        ),
        T(
            "xl3-lib-02",
            "¿Cómo sabes que tienes hojas agrupadas?",
            [
                "La barra de título muestra «[Grupo]» y las pestañas seleccionadas se ven resaltadas",
                "Las hojas cambian de color",
                "Aparece un candado en las pestañas",
                "No hay forma de saberlo",
            ],
            0,
            "Compruébalo siempre antes de escribir para no cambiar hojas sin querer.",
        ),
        T(
            "xl3-lib-03",
            "Tu tabla ocupa tres páginas y quieres que la fila de encabezados salga en todas. ¿Qué haces?",
            [
                "Diseño de página > Imprimir títulos > Repetir filas en extremo superior: $1:$1",
                "Copiar la fila 1 cada 40 filas",
                "Inmovilizar la fila superior",
                "Combinar la fila 1",
            ],
            0,
            "Inmovilizar solo afecta a la pantalla; para el papel se usan los títulos de impresión.",
        ),
        T(
            "xl3-lib-04",
            "Solo quieres imprimir el rango A1:F30 de una hoja con más datos, siempre. ¿Qué usas?",
            [
                "Diseño de página > Área de impresión > Establecer área de impresión",
                "Ocultar el resto de filas cada vez",
                "Copiar el rango a un documento de texto",
                "Ver salto de página",
            ],
            0,
            "El área de impresión se guarda con el libro.",
        ),
        T(
            "xl3-lib-05",
            "¿Qué vista te deja mover con el ratón dónde empieza cada página impresa?",
            ["Ver salto de página", "Normal", "Pantalla completa", "Inmovilizar paneles"],
            0,
            "En Ver salto de página las líneas azules marcan los saltos y se pueden arrastrar.",
        ),
        T(
            "xl3-lib-06",
            "Una tabla de 12 columnas no cabe a lo ancho en una página vertical. ¿Qué es lo más adecuado?",
            [
                "Orientación horizontal y, si hace falta, ajustar todas las columnas en una página",
                "Bajar la fuente a tamaño 6",
                "Borrar columnas",
                "Imprimirla en dos hojas y pegarlas",
            ],
            0,
            "Orientación y escala cambian la impresión sin estropear la hoja.",
        ),
        T(
            "xl3-lib-07",
            "¿Por qué conviene llamar a una hoja «Enero» y no «Ventas de enero 2026»?",
            [
                "Porque en las referencias no hacen falta comillas: Enero!B2",
                "Porque Excel no admite nombres largos",
                "Porque los nombres largos ocupan más memoria",
                "Porque así se imprime mejor",
            ],
            0,
            "Con espacios hay que escribir 'Ventas de enero 2026'!B2.",
        ),
        T(
            "xl3-lib-08",
            "¿Cambia algún dato al pasar de la vista Normal a Diseño de página?",
            [
                "No: las vistas solo cambian cómo ves la hoja",
                "Sí: se recalculan las fórmulas",
                "Sí: se borran las celdas fuera del área de impresión",
                "Sí: se quita el formato",
            ],
            0,
            "Ninguna vista modifica datos ni fórmulas.",
        ),
        R(
            "xl3-lib-09",
            "Las hojas Enero, Febrero y Marzo se prepararon agrupadas. ¿Qué devuelve la fórmula de Resumen?",
            "=Enero!B2+Febrero!B2+Marzo!B2",
            3580,
            "1.200 + 950 + 1.430 = 3.580.",
            grid=TRIMESTRE,
            sheet="Resumen",
            cell="B2",
        ),
        R(
            "xl3-lib-10",
            "Al rellenar Febrero se te olvidó desagrupar y escribiste 0 en B2 con Enero y Marzo en el grupo. ¿Qué devuelve ahora la fórmula de Resumen?",
            "=Enero!B2+Febrero!B2+Marzo!B2",
            0,
            "El 0 se escribió en B2 de las tres hojas agrupadas, así que el total es 0. Por eso hay que desagrupar al terminar.",
            grid={
                "Enero!A2": "Ventas",
                "Enero!B2": 0,
                "Febrero!A2": "Ventas",
                "Febrero!B2": 0,
                "Marzo!A2": "Ventas",
                "Marzo!B2": 0,
            },
            sheet="Resumen",
            cell="B2",
        ),
    ],
)

UNITS = [FORMATO, LIBROS]
