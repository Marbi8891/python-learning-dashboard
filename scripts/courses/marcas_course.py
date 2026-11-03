# ruff: noqa: E501
# (contenido didáctico: los textos largos van en una sola línea para poder leerlos y editarlos)
"""Curso de Lenguajes de marcas y sistemas de gestión de información (módulo 0373 de DAW).

Sigue los resultados de aprendizaje del Real Decreto 405/2023 (anexo I): XML bien formado, HTML y
CSS, validación con DTD y XML Schema, XPath y XSLT, JSON e intercambio de datos, sindicación y
sistemas de gestión empresarial. Los scripts de cliente (RA3) se practican en el curso de
JavaScript.

Las respuestas no se escriben «a ojo»:
- las preguntas con salida se ejecutan con Python (ElementTree, json, html.parser, csv, sqlite3);
- las de «¿está bien formado?» se comprueban con el analizador XML o JSON de Python;
- las de modelos de contenido de una DTD se comprueban convirtiendo el modelo en una expresión
  regular sobre los hijos del elemento.
Las preguntas sobre fragmentos de HTML, CSS, XSD o XSLT que Python no procesa son teóricas.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from course_builder import Block, Lesson, Q, main  # noqa: E402

# ---------------------------------------------------------------- ejecución

# El programa escribe y se lee en UTF-8, sea cual sea la codificación del sistema
UTF8_ENV = {**os.environ, "PYTHONIOENCODING": "utf-8"}


def run_python(code: str) -> str:
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        encoding="utf-8",  # mismo resultado en Windows y en Linux (ver UTF8_ENV)
        env=UTF8_ENV,
        timeout=10,
        check=False,
    )
    if result.returncode != 0:
        return "Error"
    return result.stdout.rstrip("\n")


def check_example(code: str) -> None:
    assert run_python(code) != "Error", f"el ejemplo falla:\n{code}"


# ---------------------------------------------------------------- comprobaciones


def xml_ok(text: str) -> bool:
    try:
        ET.fromstring(text)
    except ET.ParseError:
        return False
    return True


def json_ok(text: str) -> bool:
    try:
        json.loads(text)
    except json.JSONDecodeError:
        return False
    return True


def dtd_matches(model: str, children: list[str]) -> bool:
    """¿Encajan los hijos de un elemento en el modelo de contenido de una DTD?

    `(titulo, autor+, anio?)` se convierte en la expresión regular `(?:titulo )(?:autor )+(?:anio )?`
    sobre «titulo autor autor ». Basta para secuencias, alternativas y cardinalidades.
    """
    pattern = re.sub(r"[A-Za-z_][\w.-]*", lambda m: f"(?:{m.group(0)}\\x20)", model)
    pattern = re.sub(r"[\s,]+", "", pattern)  # la secuencia es concatenar
    return re.fullmatch(pattern, "".join(f"{c} " for c in children)) is not None


# ---------------------------------------------------------------- ayudas


def tq(id: str, q: str, options: list[str], answer: int, explain: str) -> Q:
    """Pregunta teórica."""
    return Q(id=id, q=q, options=options, answer=answer, explain=explain)


def kq(id: str, q: str, code: str, options: list[str], answer: int, explain: str) -> Q:
    """Pregunta sobre un fragmento (HTML, CSS, XSD, XSLT) que no se ejecuta."""
    return Q(id=id, q=q, code=code.strip("\n"), options=options, answer=answer, explain=explain)


def pq(id: str, q: str, code: str, expect: str, wrong: list[str], explain: str) -> Q:
    """Pregunta de Python: se ejecuta y la salida real tiene que ser `expect`."""
    return Q(id=id, q=q, code=code.strip("\n"), expect=expect, wrong=wrong, explain=explain)


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


def oq(id: str, q: str, lines: list[str], expect: str, explain: str) -> Q:
    """Ordenar líneas de un programa de Python."""
    return Q(id=id, q=q, code="___", expect=expect, explain=explain, kind="order", lines=lines)


WF_OK = "Sí, está bien formado"
JSON_OK = "Sí, es JSON válido"


def wq(id: str, code: str, options: list[str], answer: int, explain: str) -> Q:
    """¿Está bien formado este XML? El analizador de Python tiene que darle la razón a `answer`."""
    code = code.strip("\n")
    assert WF_OK in options, f"{id}: falta la opción «{WF_OK}»"
    assert (options[answer] == WF_OK) == xml_ok(code), f"{id}: el analizador XML no está de acuerdo"
    return kq(id, "¿Está bien formado este documento XML?", code, options, answer, explain)


def jq(id: str, code: str, options: list[str], answer: int, explain: str) -> Q:
    """¿Es JSON válido? `json.loads` tiene que darle la razón a `answer`."""
    code = code.strip("\n")
    assert JSON_OK in options, f"{id}: falta la opción «{JSON_OK}»"
    assert (options[answer] == JSON_OK) == json_ok(code), f"{id}: json.loads no está de acuerdo"
    return kq(id, "¿Es válido este JSON?", code, options, answer, explain)


def dq(id: str, model: str, element: str, options: list[list[str]], explain: str) -> Q:
    """Modelo de contenido de una DTD: exactamente una de las opciones tiene que encajar."""
    valid = [i for i, children in enumerate(options) if dtd_matches(model, children)]
    assert len(valid) == 1, f"{id}: encajan {len(valid)} opciones, debe encajar una"
    shown = [" ".join(f"<{c}>" for c in children) or "(vacío)" for children in options]
    return kq(
        id,
        f"Con esta declaración, ¿qué hijos de `<{element}>` son válidos, en este orden?",
        f"<!ELEMENT {element} {model}>",
        shown,
        valid[0],
        explain,
    )


QUE = "¿Qué muestra este código de Python?"

W3C_XML = ("W3C — Extensible Markup Language (XML) 1.0", "https://www.w3.org/TR/xml/")
ETREE = (
    "Documentación de Python — xml.etree.ElementTree",
    "https://docs.python.org/es/3/library/xml.etree.elementtree.html",
)
MDN_HTML = ("MDN Web Docs — HTML", "https://developer.mozilla.org/es/docs/Web/HTML")
MDN_CSS = ("MDN Web Docs — CSS", "https://developer.mozilla.org/es/docs/Web/CSS")
VALIDATOR = ("Validador HTML del W3C", "https://validator.w3.org/")
XSD = ("W3C — XML Schema 1.1, parte 1: estructuras", "https://www.w3.org/TR/xmlschema11-1/")
XPATH = ("W3C — XPath 3.1", "https://www.w3.org/TR/xpath-31/")
XSLT = ("W3C — XSLT 3.0", "https://www.w3.org/TR/xslt-30/")
JSON_RFC = ("RFC 8259 — The JSON Data Interchange Format", "https://www.rfc-editor.org/rfc/rfc8259")
PY_JSON = ("Documentación de Python — json", "https://docs.python.org/es/3/library/json.html")
RSS = ("RSS 2.0 Specification (RSS Advisory Board)", "https://www.rssboard.org/rss-specification")
ATOM = ("RFC 4287 — The Atom Syndication Format", "https://www.rfc-editor.org/rfc/rfc4287")
ODOO = ("Documentación de Odoo", "https://www.odoo.com/documentation/")

BIBLIOTECA = """<biblioteca>
  <libro id="1" idioma="es"><titulo>Ficciones</titulo><precio>12</precio></libro>
  <libro id="2" idioma="en"><titulo>Dune</titulo><precio>25</precio></libro>
  <libro id="3" idioma="es"><titulo>Rayuela</titulo><precio>18</precio></libro>
</biblioteca>"""

# ---------------------------------------------------------------- soluciones de los ejercicios

AGENDA = """<?xml version="1.0" encoding="UTF-8"?>
<agenda>
  <contacto id="1"><nombre>Ana Gil</nombre><telefono>600111222</telefono></contacto>
  <contacto id="2"><nombre>Pérez &amp; Hijos</nombre><telefono>983000111</telefono></contacto>
  <contacto id="3"><nombre>Íker Sanz</nombre><telefono>611222333</telefono></contacto>
</agenda>"""

FICHA = """<!DOCTYPE html>
<html lang="es">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Ficha · Dune</title>
    <link rel="stylesheet" href="estilos.css">
  </head>
  <body>
    <header><h1>Dune</h1></header>
    <main>
      <article>
        <img src="dune.jpg" alt="Portada de Dune: un desierto bajo dos lunas">
        <p>Autor: <span class="destacado">Frank Herbert</span></p>
        <h2>Géneros</h2>
        <ul><li>Ciencia ficción</li><li>Aventuras</li></ul>
      </article>
    </main>
    <footer><p>Ficha de ejemplo</p></footer>
  </body>
</html>

<!-- estilos.css
body { font-family: system-ui, sans-serif; line-height: 1.5; }
.destacado { color: #b91c1c; }
article { margin: 1rem 0; }
-->"""

PEDIDO = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE pedido [
  <!ELEMENT pedido (cliente, linea+, nota?)>
  <!ELEMENT cliente (#PCDATA)>
  <!ELEMENT linea (producto, cantidad)>
  <!ATTLIST linea ref CDATA #REQUIRED>
  <!ELEMENT producto (#PCDATA)>
  <!ELEMENT cantidad (#PCDATA)>
  <!ELEMENT nota (#PCDATA)>
]>
<pedido>
  <cliente>Ana Gil</cliente>
  <linea ref="T-01"><producto>Teclado</producto><cantidad>2</cantidad></linea>
  <linea ref="R-07"><producto>Ratón</producto><cantidad>1</cantidad></linea>
  <nota>Entregar por la mañana</nota>
</pedido>"""

TABLA_XSL = """<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="html" encoding="UTF-8"/>
  <xsl:template match="/">
    <table>
      <tr><th>Título</th><th>Precio</th></tr>
      <xsl:for-each select="biblioteca/libro">
        <xsl:sort select="precio" data-type="number"/>
        <tr><td><xsl:value-of select="titulo"/></td><td><xsl:value-of select="precio"/> €</td></tr>
      </xsl:for-each>
    </table>
  </xsl:template>
</xsl:stylesheet>"""

CATALOGO_PY = """import json
import xml.etree.ElementTree as ET

texto = '''[
  {"id": 1, "nombre": "Teclado", "precio": 25.5, "etiquetas": ["usb"], "oferta": true},
  {"id": 2, "nombre": "Ratón", "precio": 12, "etiquetas": [], "oferta": false},
  {"id": 3, "nombre": "Monitor", "precio": 149.9, "etiquetas": ["hdmi", "24 pulgadas"], "oferta": true}
]'''
catalogo = json.loads(texto)  # con un archivo: json.load(open("catalogo.json", encoding="utf-8"))

for producto in catalogo:
    if producto["oferta"]:
        print(producto["nombre"], producto["precio"])

raiz = ET.Element("catalogo")
for p in catalogo:
    nodo = ET.SubElement(raiz, "producto", id=str(p["id"]), oferta=str(p["oferta"]).lower())
    ET.SubElement(nodo, "nombre").text = p["nombre"]
    ET.SubElement(nodo, "precio").text = str(p["precio"])
print(ET.tostring(raiz, encoding="unicode"))"""

CANAL_RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Mi semana en DAW</title>
    <link>https://ejemplo.org/</link>
    <description>Lo que estudio</description>
    <item>
      <title>XML bien formado</title>
      <link>https://ejemplo.org/xml</link>
      <guid>https://ejemplo.org/xml</guid>
      <pubDate>Mon, 02 Nov 2026 10:00:00 GMT</pubDate>
    </item>
    <item>
      <title>Validar con una DTD</title>
      <link>https://ejemplo.org/dtd</link>
      <guid>https://ejemplo.org/dtd</guid>
      <pubDate>Wed, 04 Nov 2026 10:00:00 GMT</pubDate>
    </item>
    <item>
      <title>De XML a JSON</title>
      <link>https://ejemplo.org/json</link>
      <guid>https://ejemplo.org/json</guid>
      <pubDate>Fri, 06 Nov 2026 10:00:00 GMT</pubDate>
    </item>
  </channel>
</rss>"""


# ---------------------------------------------------------------- lecciones

L_XML = Lesson(
    slug="mar-xml-bien-formado",
    title="Lenguajes de marcas y XML bien formado",
    theory="""
Un **lenguaje de marcas** mezcla en un documento de **texto plano** el contenido y unas **marcas** (etiquetas) que dicen qué es cada parte o cómo se presenta. Al ser texto, se lee con cualquier editor, no depende del sistema operativo y lo procesan muchos programas.

**Clasificación:**
- **De presentación:** dicen cómo se ve el texto (el formato RTF de los procesadores de textos).
- **De procedimiento:** instrucciones para componer el documento (TeX, LaTeX).
- **Descriptivos o semánticos:** dicen **qué es** cada parte, no cómo se ve. **XML** y **HTML** son de este tipo.

**Los más relevantes:** SGML (el antecesor), **HTML** (páginas web), **XML** (metalenguaje para crear otros lenguajes), y lenguajes creados con XML como **SVG** (gráficos), **MathML** (fórmulas), **RSS** y **Atom** (sindicación), **XHTML** u **Office Open XML** (los `.docx`). **Markdown** es un lenguaje de marcas ligero.

**XML** es de **propósito general**: no tiene etiquetas fijas, cada aplicación define las suyas. Sirve para intercambiar datos entre programas, configuraciones (el `pom.xml` de Maven) o documentos.

**Estructura de un documento XML:**
- **Prólogo** (opcional): `<?xml version="1.0" encoding="UTF-8"?>`.
- **Un único elemento raíz** que contiene a todos los demás.
- **Elementos:** `<titulo>Dune</titulo>`. Los vacíos se pueden cerrar así: `<br/>`.
- **Atributos** dentro de la etiqueta de apertura, **siempre entre comillas**: `<libro id="2">`.
- **Comentarios** `<!-- ... -->` y secciones `<![CDATA[ ... ]]>` para texto que no se analiza.
- **Entidades** para los caracteres reservados: `&lt;` (<), `&gt;` (>), `&amp;` (&), `&quot;` (") y `&apos;` (').

**Reglas para que esté bien formado:** toda etiqueta se cierra, se anidan sin cruzarse (`<a><b></b></a>`), XML **distingue mayúsculas** (`<Nombre>` no cierra con `</nombre>`), un atributo no se repite en el mismo elemento y los nombres no empiezan por número.

**Bien formado** significa que cumple la sintaxis de XML: si no lo está, el analizador **se detiene con un error** y no se puede procesar. **Válido** es más: además cumple las reglas de una DTD o un XML Schema (lo verás en el bloque de validación).

**Espacios de nombres:** si mezclas vocabularios con el mismo nombre de etiqueta (un `<titulo>` de libro y otro de persona), se distinguen con un prefijo asociado a una URI: `<lib:titulo xmlns:lib="https://ejemplo.org/libros">`. La URI es solo un identificador único, no hace falta que exista.
""",
    example="""
import xml.etree.ElementTree as ET

documento = '''<?xml version="1.0" encoding="UTF-8"?>
<biblioteca>
  <libro id="1"><titulo>Ficciones</titulo></libro>
  <libro id="2"><titulo>Dune</titulo></libro>
</biblioteca>'''

raiz = ET.fromstring(documento)          # falla si no está bien formado
print("Raíz:", raiz.tag)
for libro in raiz:
    print(libro.get("id"), libro.find("titulo").text)

try:
    ET.fromstring("<a><b></a></b>")      # etiquetas cruzadas
except ET.ParseError as error:
    print("Mal formado:", error)
""",
    exercise="""
Escribe a mano un documento XML `agenda.xml` con:

1. el prólogo con la versión y la codificación;
2. un elemento raíz `<agenda>`;
3. tres `<contacto>` con un atributo `id` y los hijos `<nombre>` y `<telefono>`;
4. un contacto cuyo nombre lleve el carácter `&` (por ejemplo «Pérez & Hijos»).

Después compruébalo con el programa de partida: si está bien formado, mostrará los nombres.
""",
    starter='import xml.etree.ElementTree as ET\n\nraiz = ET.parse("agenda.xml").getroot()\nfor contacto in raiz:\n    print(contacto.get("id"), contacto.find("nombre").text)\n',
    hint="El `&` del nombre se escribe `&amp;`. Revisa que cada `<contacto>` se cierre y que los `id` vayan entre comillas.",
    faq=[
        (
            "¿HTML es XML?",
            "No. HTML viene de SGML y el navegador perdona errores (etiquetas sin cerrar, atributos sin comillas). XHTML es HTML escrito con las reglas estrictas de XML.",
        ),
        (
            "¿Es seguro abrir cualquier XML con Python?",
            "La documentación de Python avisa de que los módulos XML no están protegidos frente a datos maliciosos (por ejemplo, entidades que se expanden sin fin). Para XML de origen no fiable se recomienda `defusedxml`.",
        ),
    ],
    challenge=(
        "Arregla el documento",
        2,
        "Este XML tiene cuatro errores. Encuéntralos y corrígelos: `<Pedido><cliente id=7>Ana</Cliente><total>20 & 5</total></pedido><pedido/>`.",
        "<Pedido><cliente id=7>Ana</Cliente><total>20 & 5</total></pedido><pedido/>",
        "Comillas en `id`, mayúsculas iguales al abrir y cerrar, `&amp;` en lugar de `&` y un solo elemento raíz.",
    ),
    questions=[
        tq(
            "mar-01",
            "¿Qué tipo de lenguaje de marcas son XML y HTML?",
            [
                "Descriptivos: dicen qué es cada parte del documento",
                "De procedimiento, como LaTeX",
                "De presentación, como RTF",
                "Lenguajes de programación compilados",
            ],
            0,
            "Las marcas de XML y HTML describen la estructura y el significado. Cómo se ve lo decide otra capa (CSS, XSLT).",
        ),
        tq(
            "mar-02",
            "¿Por qué se dice que XML es un metalenguaje?",
            [
                "Porque sirve para definir otros lenguajes de marcas, como SVG o RSS",
                "Porque solo se usa para metadatos",
                "Porque lo ejecuta una máquina virtual",
                "Porque tiene un conjunto fijo de etiquetas",
            ],
            0,
            "XML no tiene etiquetas predefinidas: cada vocabulario (SVG, MathML, RSS…) define las suyas con sus reglas.",
        ),
        wq(
            "mar-03",
            "<libro><titulo>Dune</libro></titulo>",
            [
                WF_OK,
                "No: las etiquetas se cruzan",
                "No: falta el prólogo",
                "No: hay más de un elemento raíz",
            ],
            1,
            "`<titulo>` se abre dentro de `<libro>`, así que tiene que cerrarse antes. El prólogo es opcional.",
        ),
        wq(
            "mar-04",
            "<libro>Dune</libro>\n<libro>Ficciones</libro>",
            [
                "No: hay más de un elemento raíz",
                "No: las etiquetas se cruzan",
                WF_OK,
                "No: un atributo no lleva comillas",
            ],
            0,
            "Un documento XML tiene un único elemento raíz. Habría que envolverlos en, por ejemplo, `<libros>`.",
        ),
        wq(
            "mar-05",
            "<libro id=2><titulo>Dune</titulo></libro>",
            [
                WF_OK,
                "No: falta el prólogo",
                "No: un atributo no lleva comillas",
                "No: hay más de un elemento raíz",
            ],
            2,
            "En XML el valor de un atributo va siempre entre comillas: `id=\"2\"` o `id='2'`.",
        ),
        wq(
            "mar-06",
            "<Nombre>Ana</nombre>",
            [
                "No: XML distingue mayúsculas y minúsculas",
                WF_OK,
                "No: falta el prólogo",
                "No: los nombres no pueden empezar por mayúscula",
            ],
            0,
            "`<Nombre>` y `</nombre>` son etiquetas distintas. Los nombres sí pueden empezar por mayúscula.",
        ),
        wq(
            "mar-07",
            '<tienda>\n  <!-- productos -->\n  <producto stock="0"/>\n  <nota>Precio &lt; 10 &amp; envío gratis</nota>\n</tienda>',
            [
                "No: el elemento vacío debe cerrarse con </producto>",
                "No: los comentarios no se permiten dentro del raíz",
                WF_OK,
                "No: & no se puede usar nunca",
            ],
            2,
            "`<producto/>` es un elemento vacío correcto, el comentario es válido y `&lt;` y `&amp;` son las entidades de < y &.",
        ),
        wq(
            "mar-08",
            "<nota>Tom & Jerry</nota>",
            [
                WF_OK,
                "No: & tiene que escribirse &amp;",
                "No: falta un atributo",
                "No: las etiquetas se cruzan",
            ],
            1,
            "El `&` inicia una entidad. Suelto, el analizador da error: se escribe `&amp;` o se mete en una sección CDATA.",
        ),
        tq(
            "mar-09",
            "¿Qué diferencia hay entre un XML bien formado y uno válido?",
            [
                "Bien formado cumple la sintaxis de XML; válido además cumple una DTD o un XML Schema",
                "Son lo mismo",
                "Válido cumple la sintaxis; bien formado además tiene una DTD",
                "Bien formado significa que tiene prólogo",
            ],
            0,
            "Todo XML válido está bien formado, pero no al revés.",
        ),
        tq(
            "mar-10",
            "¿Para qué sirven los espacios de nombres (xmlns)?",
            [
                "Para distinguir elementos con el mismo nombre que vienen de vocabularios distintos",
                "Para cifrar el documento",
                "Para indicar la codificación de caracteres",
                "Para enlazar la hoja de estilos",
            ],
            0,
            "Cada vocabulario se asocia a una URI y sus elementos llevan un prefijo, como `lib:titulo` y `per:titulo`.",
        ),
        pq(
            "mar-11",
            QUE,
            "import xml.etree.ElementTree as ET\nraiz = ET.fromstring('<biblioteca><libro/><libro/><revista/></biblioteca>')\nprint(raiz.tag, len(raiz))",
            "biblioteca 3",
            ["biblioteca 2", "libro 3", "Error"],
            "`len(raiz)` cuenta los hijos directos del elemento raíz: dos libros y una revista.",
        ),
        pq(
            "mar-12",
            QUE,
            'import xml.etree.ElementTree as ET\nlibro = ET.fromstring(\'<libro id="2" idioma="en"><titulo>Dune</titulo></libro>\')\nprint(libro.get("idioma"), libro.find("titulo").text)',
            "en Dune",
            ["idioma titulo", "2 Dune", "Error"],
            "`get` lee un atributo y `find(...).text` el texto del primer hijo con ese nombre.",
        ),
        fq(
            "mar-13",
            "Completa el hueco para mostrar el texto del título.",
            'import xml.etree.ElementTree as ET\nlibro = ET.fromstring("<libro><titulo>Rayuela</titulo></libro>")\nprint(libro.find("titulo").___)',
            ["text"],
            "Rayuela",
            "El contenido de texto de un elemento está en su atributo `.text`.",
        ),
    ],
    quiz=[
        tq(
            "mar-q01",
            "¿Cuántos elementos raíz puede tener un documento XML?",
            ["Uno", "Dos como máximo", "Los que se quiera", "Ninguno si tiene prólogo"],
            0,
            "Un único elemento raíz contiene a todos los demás.",
        ),
        tq(
            "mar-q02",
            "¿Cómo se escribe el carácter < dentro del texto de un elemento XML?",
            ["&lt;", "&gt;", "\\<", "<<"],
            0,
            "`&lt;` (less than). `&gt;` es >.",
        ),
    ],
    objectives=[
        "Clasificar los lenguajes de marcas y reconocer los más usados y sus ámbitos (RA1 a-f).",
        "Identificar la estructura de un documento XML y sus reglas sintácticas (RA1 g).",
        "Explicar por qué un documento tiene que estar bien formado para poder procesarse (RA1 h).",
        "Usar espacios de nombres para mezclar vocabularios sin choques de nombres (RA1 i).",
    ],
    mistakes=[
        (
            "Dejar un `&` suelto en el texto.",
            "Escribe `&amp;` o mete el texto en una sección `<![CDATA[ ... ]]>`.",
        ),
        (
            "Cerrar con otras mayúsculas: `<Nombre>…</nombre>`.",
            "XML distingue mayúsculas y minúsculas: copia el nombre exacto.",
        ),
        ("Poner dos elementos en el nivel superior.", "Envuelve todo en un único elemento raíz."),
        (
            "Escribir atributos sin comillas, como en HTML.",
            'En XML van siempre entre comillas: `id="2"`.',
        ),
        (
            "Confundir «bien formado» con «válido».",
            "Bien formado es la sintaxis de XML; válido es, además, cumplir una DTD o un XML Schema.",
        ),
    ],
    summary=[
        "Un lenguaje de marcas mezcla contenido y etiquetas en texto plano; XML y HTML son descriptivos.",
        "XML es un metalenguaje: SVG, RSS o MathML están hechos con XML.",
        "Un XML bien formado tiene un solo raíz, etiquetas cerradas y bien anidadas, atributos entre comillas y entidades para `<` y `&`.",
        "Si no está bien formado, el analizador se detiene: no se puede procesar.",
        "Los espacios de nombres distinguen elementos con el mismo nombre que vienen de vocabularios distintos.",
    ],
    solution=(
        AGENDA,
        "Un único elemento raíz (`<agenda>`), los `id` entre comillas y el `&` escrito como `&amp;`. Con el programa de partida se ve `2 Pérez & Hijos`: el analizador vuelve a convertir la entidad en `&`.",
    ),
    sources=[W3C_XML, ETREE],
)

L_HTML = Lesson(
    slug="mar-html-css",
    title="HTML y hojas de estilo CSS",
    theory="""
**HTML** es el lenguaje de marcas de las páginas web. Sus versiones: HTML 4.01 (1999), **XHTML** (HTML con las reglas de XML) y **HTML5**, que hoy mantiene el WHATWG como un estándar vivo (*HTML Living Standard*). HTML5 añadió etiquetas semánticas, audio y vídeo sin complementos, nuevos tipos de `input` y un `<!DOCTYPE html>` mucho más corto.

**Estructura de un documento:**
```
<!DOCTYPE html>
<html lang="es">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Mi página</title>
    <link rel="stylesheet" href="estilos.css">
  </head>
  <body>...</body>
</html>
```
`<head>` tiene la información **sobre** la página (no se ve en ella); `<body>`, el contenido visible.

**Etiquetas principales:** títulos `<h1>`…`<h6>`, párrafos `<p>`, enlaces `<a href="...">`, imágenes `<img src="..." alt="...">` (el `alt` describe la imagen a quien no la ve), listas `<ul>`/`<ol>` con `<li>`, tablas `<table>` con `<tr>`, `<th>` y `<td>`, y formularios `<form>` con `<label>` e `<input>`.

**Etiquetas semánticas de HTML5:** `<header>`, `<nav>`, `<main>` (una por página), `<article>`, `<section>`, `<aside>` y `<footer>`. Ayudan a los lectores de pantalla y a los buscadores; un `<div>` no dice nada de su contenido.

**CSS** separa la presentación del contenido: el mismo HTML puede verse de muchas formas y una sola hoja cambia todo el sitio. Una regla es `selector { propiedad: valor; }`. Se puede escribir en un atributo `style` (en línea), en un `<style>` del `<head>` o en un archivo externo con `<link>`, que es lo recomendable.

**Selectores:** de etiqueta (`p`), de clase (`.aviso`), de id (`#cabecera`), descendiente (`nav a`), hijo (`ul > li`) y pseudoclases (`a:hover`, `li:first-child`).

**Cascada y especificidad:** si dos reglas chocan, gana la más **específica**: estilo en línea > id > clase, atributo o pseudoclase > etiqueta. Con la misma especificidad, gana **la última** que aparece. `!important` se salta este orden y conviene evitarlo.

**Modelo de caja:** cada elemento es una caja con contenido, `padding` (relleno), `border` y `margin` (margen exterior). Con `box-sizing: border-box`, el `width` incluye el relleno y el borde.

**Validación:** el validador del W3C (validator.w3.org) revisa el HTML y el de CSS (jigsaw.w3.org/css-validator) las hojas de estilo. Los navegadores toleran errores, pero cada uno los «arregla» a su manera.

Para acceder a la página y cambiarla desde un script (el DOM), mira el curso de JavaScript.
""",
    example="""
from html.parser import HTMLParser

pagina = '''<main>
  <h1>Catálogo</h1>
  <img src="dune.jpg" alt="Portada de Dune">
  <img src="logo.png">
  <a href="https://www.w3.org/">W3C</a>
</main>'''

class Revisor(HTMLParser):
    def handle_starttag(self, tag, attrs):
        datos = dict(attrs)
        if tag == "img" and not datos.get("alt"):
            print("Imagen sin alt:", datos["src"])
        if tag == "a":
            print("Enlace a", datos["href"])

Revisor().feed(pagina)
""",
    exercise="""
Crea `index.html` y `estilos.css` para una ficha de un libro:

1. estructura completa con `<!DOCTYPE html>`, `lang="es"`, `meta charset` y `<title>`;
2. `<header>` con el título, `<main>` con un `<article>` (portada con `alt`, autor y una lista de géneros) y `<footer>`;
3. en el CSS: una fuente para `body`, la clase `.destacado` en rojo y un margen para `article`;
4. pásalo por el validador del W3C hasta que no dé errores.
""",
    starter='<!DOCTYPE html>\n<html lang="es">\n  <head>\n    <meta charset="UTF-8">\n    <title>Ficha</title>\n    <link rel="stylesheet" href="estilos.css">\n  </head>\n  <body>\n  </body>\n</html>\n',
    hint="Primero el HTML sin estilos; luego enlaza el CSS. El validador te dirá la línea exacta de cada error.",
    faq=[
        (
            "¿Uso `<b>` o `<strong>`?",
            "`<strong>` indica importancia y lo anuncian los lectores de pantalla; `<b>` solo resalta. Para el aspecto, mejor CSS.",
        ),
        (
            "¿Clase o id?",
            "Un id es único en la página; una clase se repite. Para dar estilos se usan casi siempre clases.",
        ),
    ],
    challenge=(
        "Gana la regla",
        2,
        'Un `<p id="intro" class="aviso">` tiene estas reglas: `p { color: black; }`, `.aviso { color: orange; }`, `#intro { color: blue; }` y `p.aviso { color: green; }`. ¿De qué color se ve? Explica por qué y qué pasaría si quitaras la regla del id.',
        "/* color final: ... */",
        "El id es lo más específico. Sin él, `p.aviso` (clase + etiqueta) gana a `.aviso`.",
    ),
    questions=[
        tq(
            "mar-14",
            "¿Qué contiene la sección `<head>` de un documento HTML?",
            [
                "Información sobre la página: título, codificación, hojas de estilo",
                "El contenido visible de la página",
                "Solo el menú de navegación",
                "Los scripts que se ejecutan al final",
            ],
            0,
            "El contenido visible va en `<body>`. `<head>` describe la página.",
        ),
        tq(
            "mar-15",
            "¿Para qué sirve el atributo `alt` de `<img>`?",
            [
                "Para describir la imagen a quien no puede verla o si no carga",
                "Para indicar la altura",
                "Para poner un título que aparece al pasar el ratón",
                "Para enlazar la imagen a otra página",
            ],
            0,
            "Lo leen los lectores de pantalla y se muestra si la imagen falla. Es obligatorio para la accesibilidad.",
        ),
        tq(
            "mar-16",
            "¿Qué etiqueta de HTML5 marca el contenido principal de la página?",
            ["<main>", "<section>", "<div>", "<body>"],
            0,
            "`<main>` aparece una vez y deja fuera la cabecera, la navegación y el pie.",
        ),
        tq(
            "mar-17",
            "¿Cuál es la declaración de tipo de documento de HTML5?",
            [
                "<!DOCTYPE html>",
                '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN">',
                '<?xml version="1.0"?>',
                "<html5>",
            ],
            0,
            "HTML5 simplificó el DOCTYPE. La segunda es la de HTML 4.01.",
        ),
        kq(
            "mar-18",
            'Un elemento `<p class="aviso">` recibe estas dos reglas. ¿De qué color se ve?',
            ".aviso { color: orange; }\np { color: black; }",
            ["Naranja", "Negro", "Del color por defecto", "Depende del navegador"],
            0,
            "Una clase es más específica que una etiqueta, aunque la regla de `p` vaya después.",
        ),
        kq(
            "mar-19",
            'Las dos reglas tienen la misma especificidad. ¿De qué color se ve un `<p class="nota">`?',
            ".nota { color: green; }\n.nota { color: purple; }",
            ["Morado", "Verde", "Mezcla de los dos", "Negro"],
            0,
            "Con la misma especificidad gana la última regla de la cascada.",
        ),
        kq(
            "mar-20",
            "¿Qué selecciona este selector?",
            "nav a { text-decoration: none; }",
            [
                "Los enlaces que están dentro de un <nav>",
                "Los <nav> que están dentro de un enlace",
                "Los <nav> y todos los enlaces",
                "Solo el primer enlace del <nav>",
            ],
            0,
            "El espacio es el combinador descendiente: elementos `a` en cualquier nivel dentro de `nav`.",
        ),
        tq(
            "mar-21",
            "¿Cuál es la forma recomendada de aplicar CSS a todo un sitio?",
            [
                "Una hoja externa enlazada con <link>",
                "Un atributo style en cada etiqueta",
                "Un <style> repetido en cada página",
                "Etiquetas <font>",
            ],
            0,
            "Una hoja externa se reutiliza en todas las páginas, se guarda en caché y separa contenido y presentación.",
        ),
        tq(
            "mar-22",
            "En el modelo de caja, ¿qué es el `padding`?",
            [
                "El espacio entre el contenido y el borde",
                "El espacio fuera del borde",
                "El grosor del borde",
                "El ancho total del elemento",
            ],
            0,
            "El margen (`margin`) es el espacio exterior; el relleno (`padding`), el interior.",
        ),
        tq(
            "mar-23",
            "¿Qué herramienta comprueba que un HTML cumple el estándar?",
            [
                "El validador del W3C (validator.w3.org)",
                "Un compilador de Java",
                "El inspector de red del navegador",
                "Un gestor de bases de datos",
            ],
            0,
            "Para CSS está el validador de hojas de estilo del W3C (jigsaw).",
        ),
        pq(
            "mar-24",
            QUE,
            'from html.parser import HTMLParser\n\nclass Contador(HTMLParser):\n    enlaces = 0\n    def handle_starttag(self, tag, attrs):\n        if tag == "a":\n            self.enlaces += 1\n\nc = Contador()\nc.feed(\'<nav><a href="/">Inicio</a> <a href="/blog">Blog</a></nav><p>Sin enlace</p>\')\nprint(c.enlaces)',
            "2",
            ["1", "3", "Error"],
            "`handle_starttag` se llama con cada etiqueta de apertura; solo hay dos `<a>`.",
        ),
        oq(
            "mar-25",
            "Ordena las líneas para mostrar la etiqueta de cada elemento de apertura.",
            [
                "from html.parser import HTMLParser",
                "class Etiquetas(HTMLParser):",
                "    def handle_starttag(self, tag, attrs):",
                "        print(tag)",
                'Etiquetas().feed("<ul><li>Uno</li></ul>")',
            ],
            "ul\nli",
            "Primero el import, después la clase con su método y al final se usa.",
        ),
    ],
    quiz=[
        tq(
            "mar-q03",
            "¿Qué gana en la cascada de CSS entre un selector de id y uno de clase?",
            ["El de id", "El de clase", "El que va primero", "Ninguno"],
            0,
            "Estilo en línea > id > clase > etiqueta.",
        ),
        tq(
            "mar-q04",
            "¿Qué ventaja tiene usar hojas de estilo?",
            [
                "Separar presentación y contenido, y cambiar el aspecto de todo el sitio desde un archivo",
                "Que la página cargue sin HTML",
                "Que el servidor ejecute la página",
                "Que no haga falta el navegador",
            ],
            0,
            "El mismo HTML puede tener varias presentaciones (pantalla, impresión, móvil).",
        ),
    ],
    objectives=[
        "Reconocer las versiones de HTML y las diferencias de HTML5 (RA2 a, d).",
        "Analizar la estructura de un documento HTML y la función de sus etiquetas y atributos principales (RA2 b, c).",
        "Aplicar hojas de estilo y explicar la cascada y la especificidad (RA2 f, g).",
        "Validar documentos HTML y CSS con las herramientas del W3C (RA2 e, h).",
    ],
    mistakes=[
        (
            "Olvidar el `alt` de las imágenes.",
            'Describe la imagen; si es decorativa, `alt=""` para que el lector de pantalla la ignore.',
        ),
        (
            "Usar `<div>` para todo.",
            "Elige la etiqueta semántica: `<nav>`, `<main>`, `<article>`, `<button>`…",
        ),
        (
            "Usar títulos por su tamaño (`<h4>` porque es pequeño).",
            "Los títulos van en orden (`h1`, `h2`, `h3`); el tamaño se cambia con CSS.",
        ),
        (
            "Abusar de `!important` para «ganar» la cascada.",
            "Sube la especificidad del selector o reordena las reglas.",
        ),
        (
            "Repetir un mismo `id` en la página.",
            "Un id es único; para repetir un estilo usa una clase.",
        ),
    ],
    summary=[
        "Un documento HTML5 empieza por `<!DOCTYPE html>` y tiene `<head>` (información sobre la página) y `<body>` (contenido).",
        "Las etiquetas semánticas (`header`, `nav`, `main`, `article`, `footer`) describen cada parte.",
        "CSS separa presentación y contenido; lo recomendable es una hoja externa enlazada con `<link>`.",
        "En la cascada gana lo más específico (en línea > id > clase > etiqueta) y, a igualdad, la última regla.",
        "El validador del W3C comprueba el HTML y el de jigsaw, las hojas de estilo.",
    ],
    solution=(
        FICHA,
        "La estructura completa pasa el validador: `lang`, `meta charset`, un solo `<main>` y la imagen con `alt`. Los estilos van en `estilos.css` (aquí, al final, como comentario) y la clase `.destacado` se reutiliza donde haga falta.",
    ),
    sources=[MDN_HTML, MDN_CSS, VALIDATOR],
)

L_VALIDACION = Lesson(
    slug="mar-dtd-xsd",
    title="Validación con DTD y XML Schema",
    theory="""
Dos programas que se intercambian XML tienen que ponerse de acuerdo: qué elementos hay, en qué orden, cuáles son obligatorios y qué tipo de dato lleva cada uno. Esa **descripción** se escribe en una **DTD** o en un **XML Schema (XSD)**, y un documento que la cumple es **válido**.

**DTD (Document Type Definition)** — la forma clásica, con sintaxis propia (no es XML).

Se asocia al documento con `<!DOCTYPE raiz SYSTEM "biblioteca.dtd">` (externa) o escribiendo las reglas entre corchetes dentro del `<!DOCTYPE raiz [ ... ]>` (interna).

`<!ELEMENT libro (titulo, autor+, anio?)>` define el **modelo de contenido**:
- `,` secuencia (en ese orden) y `|` alternativa (uno u otro);
- cardinalidad: sin símbolo, **exactamente uno**; `?` cero o uno; `*` cero o más; `+` uno o más;
- `(#PCDATA)` texto, `EMPTY` elemento vacío, `ANY` cualquier contenido.

`<!ATTLIST libro id ID #REQUIRED idioma CDATA "es">` define atributos: tipo (`CDATA` texto, `ID` identificador único, `IDREF` referencia a un ID, una lista `(si|no)`) y valor por defecto (`#REQUIRED` obligatorio, `#IMPLIED` opcional, `#FIXED "valor"` o un valor por defecto).

**XML Schema (XSD)** — más potente y escrito en XML:
```
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <xs:element name="libro">
    <xs:complexType>
      <xs:sequence>
        <xs:element name="titulo" type="xs:string"/>
        <xs:element name="autor" type="xs:string" maxOccurs="unbounded"/>
        <xs:element name="anio" type="xs:gYear" minOccurs="0"/>
      </xs:sequence>
      <xs:attribute name="id" type="xs:positiveInteger" use="required"/>
    </xs:complexType>
  </xs:element>
</xs:schema>
```
- **Tipos de datos**: `xs:string`, `xs:integer`, `xs:decimal`, `xs:date`, `xs:boolean`… (la DTD solo conoce texto).
- `minOccurs` y `maxOccurs` (por defecto, 1) sustituyen a `?`, `*` y `+`.
- `xs:sequence` (en orden), `xs:choice` (uno de ellos), `xs:all` (en cualquier orden).
- **Restricciones** con `xs:simpleType` y `xs:restriction`: `xs:minInclusive`, `xs:maxLength`, `xs:pattern` (expresión regular) o `xs:enumeration` (lista de valores).
- Se asocia con `xsi:noNamespaceSchemaLocation="libro.xsd"` en el elemento raíz.

**Herramientas:** `xmllint --dtdvalid biblioteca.dtd doc.xml` o `xmllint --schema libro.xsd doc.xml` (libxml2), editores como XML Copy Editor o la extensión XML de Red Hat para VS Code, y en Python la biblioteca `lxml`.
""",
    example="""
import re

# Cómo «piensa» un validador: el modelo (titulo, autor+, anio?) es casi una expresión regular
modelo = re.compile(r"(titulo )(autor )+(anio )?")

for hijos in (["titulo", "autor"], ["titulo", "autor", "autor", "anio"], ["autor", "titulo"]):
    texto = "".join(h + " " for h in hijos)
    print(hijos, "válido" if modelo.fullmatch(texto) else "no válido")
""",
    exercise="""
Escribe una DTD interna para un `<pedido>` que tenga:

1. un `<cliente>` (texto) y uno o más `<linea>`;
2. cada `<linea>` con `<producto>` y `<cantidad>`, y un atributo `ref` obligatorio;
3. un `<nota>` opcional al final.

Escribe después un pedido válido y otro no válido, y compruébalos con `xmllint --valid --noout pedido.xml`.
""",
    starter='<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE pedido [\n  <!ELEMENT pedido (cliente, linea+, nota?)>\n  <!-- completa el resto -->\n]>\n<pedido>\n</pedido>\n',
    hint="`<!ELEMENT linea (producto, cantidad)>`, `<!ATTLIST linea ref CDATA #REQUIRED>` y cada hoja con `(#PCDATA)`.",
    faq=[
        (
            "¿DTD o XSD?",
            "XSD si necesitas tipos de datos (números, fechas) o restricciones. La DTD es más sencilla y aún aparece en documentos antiguos y en el `<!DOCTYPE>`.",
        ),
        (
            "¿Python valida contra una DTD?",
            "La biblioteca estándar no. Con `lxml` se puede: `etree.DTD(...)` y `etree.XMLSchema(...)` tienen un método `validate`.",
        ),
    ],
    challenge=(
        "De DTD a XSD",
        3,
        "Traduce a XML Schema esta DTD: `<!ELEMENT alumno (nombre, nota*)>`, `<!ELEMENT nombre (#PCDATA)>`, `<!ELEMENT nota (#PCDATA)>`. Añade que cada nota sea un decimal entre 0 y 10.",
        '<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">\n  <!-- ... -->\n</xs:schema>',
        '`nota*` es `minOccurs="0" maxOccurs="unbounded"`. El rango, con `xs:restriction base="xs:decimal"`, `xs:minInclusive` y `xs:maxInclusive`.',
    ),
    questions=[
        dq(
            "mar-26",
            "(titulo, autor+, anio?)",
            "libro",
            [
                ["titulo", "autor", "autor"],
                ["titulo", "anio"],
                ["autor", "titulo"],
                ["titulo", "anio", "autor"],
            ],
            "`autor+` exige al menos un autor y el orden de la secuencia es obligatorio; `anio?` puede faltar.",
        ),
        dq(
            "mar-27",
            "(nombre, (telefono | email)*)",
            "contacto",
            [
                ["nombre", "telefono", "telefono"],
                ["email", "nombre"],
                ["telefono"],
                ["nombre", "nombre", "email"],
            ],
            "Un nombre al principio y después cualquier número de teléfonos o emails, en cualquier orden entre ellos.",
        ),
        dq(
            "mar-28",
            "(cabecera?, cuerpo)",
            "mensaje",
            [["cabecera"], ["cuerpo", "cabecera"], ["cuerpo"], ["cabecera", "cuerpo", "cuerpo"]],
            "`cuerpo` sin símbolo aparece exactamente una vez; la cabecera es opcional y va antes.",
        ),
        tq(
            "mar-29",
            "En una DTD, ¿qué significa `*` detrás de un elemento?",
            ["Cero o más veces", "Una o más veces", "Cero o una vez", "Exactamente una vez"],
            0,
            "`?` es cero o una, `+` una o más y sin símbolo, exactamente una.",
        ),
        kq(
            "mar-30",
            "¿Qué indica esta declaración?",
            '<!ATTLIST libro isbn ID #REQUIRED formato (papel|digital) "papel">',
            [
                "isbn es obligatorio y único; formato vale papel o digital, y papel por defecto",
                "isbn es opcional; formato puede tener cualquier texto",
                "isbn y formato son elementos hijos de libro",
                "formato es obligatorio y no tiene valor por defecto",
            ],
            0,
            "`ID` exige un valor único en el documento y `#REQUIRED` lo hace obligatorio. La lista entre paréntesis limita los valores.",
        ),
        kq(
            "mar-31",
            "¿Cómo se asocia esta DTD al documento?",
            '<?xml version="1.0"?>\n<!DOCTYPE biblioteca SYSTEM "biblioteca.dtd">\n<biblioteca>...</biblioteca>',
            [
                "Es una DTD externa, en el archivo biblioteca.dtd",
                "Es una DTD interna",
                "Es un XML Schema",
                "Es una hoja de estilos",
            ],
            0,
            "Con `SYSTEM` y una ruta, las reglas están en otro archivo. Una DTD interna va entre corchetes.",
        ),
        tq(
            "mar-32",
            "¿Qué ventaja tiene XML Schema frente a una DTD?",
            [
                "Tiene tipos de datos y restricciones, y está escrito en XML",
                "Es más corto y no usa XML",
                "No necesita que el documento esté bien formado",
                "Lo entienden los navegadores sin descargarlo",
            ],
            0,
            "Con XSD puedes exigir que `<precio>` sea un decimal positivo; con una DTD, solo que tenga texto.",
        ),
        kq(
            "mar-33",
            "¿Cuántas veces puede aparecer `<telefono>`?",
            '<xs:element name="telefono" type="xs:string" minOccurs="0" maxOccurs="3"/>',
            ["Entre 0 y 3", "Exactamente 3", "Entre 1 y 3", "Las que se quiera"],
            0,
            "`minOccurs` y `maxOccurs` fijan el mínimo y el máximo. Por defecto valen 1.",
        ),
        kq(
            "mar-34",
            "¿Qué valores acepta este tipo?",
            '<xs:simpleType name="talla">\n  <xs:restriction base="xs:string">\n    <xs:enumeration value="S"/>\n    <xs:enumeration value="M"/>\n    <xs:enumeration value="L"/>\n  </xs:restriction>\n</xs:simpleType>',
            ["Solo S, M o L", "Cualquier texto", "Cualquier letra mayúscula", "Números del 1 al 3"],
            0,
            "`xs:enumeration` restringe el tipo base a una lista cerrada de valores.",
        ),
        tq(
            "mar-35",
            "¿Qué atributo enlaza un documento sin espacio de nombres con su XML Schema?",
            [
                "xsi:noNamespaceSchemaLocation",
                "xmlns:xs",
                "xml:lang",
                "<!DOCTYPE>",
            ],
            0,
            'Se pone en el elemento raíz, junto a `xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"`.',
        ),
    ],
    quiz=[
        tq(
            "mar-q05",
            "¿Qué es un documento XML válido?",
            [
                "Uno bien formado que además cumple su DTD o su XML Schema",
                "Uno que tiene prólogo",
                "Uno que se ve bien en el navegador",
                "Uno sin atributos",
            ],
            0,
            "La validez se comprueba contra una descripción del documento.",
        ),
        tq(
            "mar-q06",
            "En XSD, ¿qué grupo obliga a que los hijos aparezcan en un orden concreto?",
            ["xs:sequence", "xs:choice", "xs:all", "xs:any"],
            0,
            "`xs:choice` es uno de ellos y `xs:all`, todos en cualquier orden.",
        ),
    ],
    objectives=[
        "Explicar por qué hay que describir los documentos que se intercambian (RA4 a, b).",
        "Leer y escribir modelos de contenido y atributos en una DTD (RA4 c, d).",
        "Escribir un XML Schema con tipos de datos, cardinalidades y restricciones (RA4 c, d).",
        "Asociar la descripción a un documento y validarlo con herramientas (RA4 e, f, g).",
    ],
    mistakes=[
        (
            "Olvidar declarar un elemento hoja.",
            "Cada elemento necesita su `<!ELEMENT … (#PCDATA)>`, también los que solo tienen texto.",
        ),
        ("Confundir `+` con `*`.", "`+` exige al menos uno; `*` admite ninguno."),
        (
            "Pensar que una DTD comprueba que `<precio>` es un número.",
            "La DTD solo conoce texto; para tipos de datos hace falta XML Schema.",
        ),
        (
            "Cambiar el orden de los hijos en una secuencia.",
            "Con `,` (o `xs:sequence`) el orden es obligatorio; si no importa, usa `xs:all`.",
        ),
    ],
    summary=[
        "Un XML válido está bien formado y cumple su DTD o su XML Schema.",
        "DTD: `<!ELEMENT>` con `,` (secuencia), `|` (alternativa) y `?`, `*`, `+`; `<!ATTLIST>` con `CDATA`, `ID`, `#REQUIRED`, `#IMPLIED`.",
        "XSD está escrito en XML y añade tipos (`xs:integer`, `xs:date`), `minOccurs`/`maxOccurs` y restricciones.",
        "Se valida con `xmllint` (`--valid`, `--dtdvalid`, `--schema`) o con `lxml` en Python.",
    ],
    solution=(
        PEDIDO,
        "`linea+` exige al menos una línea y `nota?` la deja opcional al final. Cada hoja se declara con `(#PCDATA)` y `ref` es obligatorio con `#REQUIRED`. Si quitas todas las `<linea>`, `xmllint --valid` da error.",
    ),
    sources=[W3C_XML, XSD],
)

L_XPATH = Lesson(
    slug="mar-xpath-xslt",
    title="Consultas y conversiones: XPath, XSLT y XQuery",
    theory="""
**XPath** es el lenguaje para **seleccionar partes** de un documento XML, que se ve como un árbol de nodos (elementos, atributos, texto). Lo usan XSLT, XQuery, XML Schema y muchas bibliotecas.

**Rutas:**
- `/biblioteca/libro`: ruta absoluta desde la raíz.
- `//titulo`: todos los `titulo`, estén donde estén.
- `.` el nodo actual, `..` el padre, `*` cualquier elemento.
- `@id`: el atributo `id`.

**Predicados**, entre corchetes, filtran: `libro[1]` (el primero: en XPath se cuenta desde 1), `libro[last()]`, `libro[@idioma='es']`, `libro[precio > 15]`.

**Funciones:** `count(//libro)`, `text()`, `contains(titulo, 'Du')`, `sum(//precio)`, `string-length()`.

ElementTree de Python entiende un **subconjunto** de XPath en `find` y `findall`: rutas, `//`, `*`, `..`, `[@atr]`, `[@atr='v']`, `[hijo]`, `[n]` y `[last()]`. No tiene funciones como `count()` ni comparaciones numéricas: para eso hace falta `lxml` o una herramienta XPath completa.

**XSLT** convierte un XML en otro XML, en HTML o en texto. Es una hoja de estilos **escrita en XML** que procesa un **procesador XSLT** (xsltproc, Saxon o el propio navegador):
```
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:template match="/">
    <ul>
      <xsl:for-each select="biblioteca/libro">
        <xsl:sort select="titulo"/>
        <li><xsl:value-of select="titulo"/></li>
      </xsl:for-each>
    </ul>
  </xsl:template>
</xsl:stylesheet>
```
- `xsl:template match="..."`: qué hacer con los nodos que encajan.
- `xsl:value-of select="..."`: escribe el texto del nodo.
- `xsl:for-each`, `xsl:sort`, `xsl:if test="..."` y `xsl:choose` / `xsl:when` / `xsl:otherwise`.
- Se asocia a un XML con `<?xml-stylesheet type="text/xsl" href="libros.xsl"?>`.

**¿Por qué convertir?** Un mismo dato se publica en una web (HTML), se envía a otro programa con otro vocabulario (XML) o se exporta a CSV o a texto.

**XQuery** consulta colecciones de XML como SQL consulta tablas. Sus expresiones **FLWOR** (`for`, `let`, `where`, `order by`, `return`) recorren, filtran y devuelven resultados. Lo usan las **bases de datos XML nativas**, como BaseX o eXist-db.
""",
    example="""
import xml.etree.ElementTree as ET

raiz = ET.fromstring('''<biblioteca>
  <libro id="1" idioma="es"><titulo>Ficciones</titulo><precio>12</precio></libro>
  <libro id="2" idioma="en"><titulo>Dune</titulo><precio>25</precio></libro>
</biblioteca>''')

print([t.text for t in raiz.findall(".//titulo")])         # //titulo
print(raiz.find("libro[@idioma='en']/titulo").text)        # predicado de atributo

# Una «conversión» a HTML como la de XSLT, escrita en Python
filas = [f"<li>{l.find('titulo').text}: {l.find('precio').text} €</li>" for l in raiz]
print("<ul>" + "".join(filas) + "</ul>")
""",
    exercise="""
Con el documento de la biblioteca del ejemplo (añade un tercer libro):

1. escribe las expresiones XPath para: todos los títulos, el título del libro con `id="2"`, los libros en español y el número de libros;
2. pruébalas en una herramienta XPath (por ejemplo `xmllint --xpath "count(//libro)" biblioteca.xml`);
3. escribe una hoja XSLT que genere una tabla HTML con título y precio, ordenada por precio.
""",
    starter='<?xml version="1.0" encoding="UTF-8"?>\n<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">\n  <xsl:template match="/">\n    <table>\n      <!-- xsl:for-each + xsl:sort + xsl:value-of -->\n    </table>\n  </xsl:template>\n</xsl:stylesheet>\n',
    hint='Para ordenar por número: `<xsl:sort select="precio" data-type="number"/>`.',
    faq=[
        (
            "¿Por qué `libro[1]` y no `libro[0]`?",
            "En XPath las posiciones empiezan en 1. En las listas de Python, en 0: no los mezcles.",
        ),
        (
            "¿XSLT sigue usándose?",
            "Sí, en integraciones entre sistemas, facturación electrónica, publicación de documentos y en sistemas que intercambian XML. Los navegadores aún entienden XSLT 1.0.",
        ),
    ],
    challenge=(
        "La consulta FLWOR",
        3,
        "Escribe una consulta XQuery que devuelva el título de los libros de más de 15 €, ordenados por precio de mayor a menor. Pruébala en BaseX.",
        'for $l in doc("biblioteca.xml")//libro\n(: where ... order by ... return ... :)',
        "`where $l/precio > 15`, `order by number($l/precio) descending`, `return $l/titulo/text()`.",
    ),
    questions=[
        pq(
            "mar-36",
            QUE,
            f'import xml.etree.ElementTree as ET\nraiz = ET.fromstring("""{BIBLIOTECA}""")\nprint(len(raiz.findall("libro[@idioma=\'es\']")))',
            "2",
            ["1", "3", "Error"],
            "El predicado `[@idioma='es']` deja los libros 1 y 3.",
        ),
        pq(
            "mar-37",
            QUE,
            f'import xml.etree.ElementTree as ET\nraiz = ET.fromstring("""{BIBLIOTECA}""")\nprint(raiz.find("libro[last()]/titulo").text)',
            "Rayuela",
            ["Ficciones", "Dune", "Error"],
            "`last()` es la posición del último libro.",
        ),
        pq(
            "mar-38",
            QUE,
            f'import xml.etree.ElementTree as ET\nraiz = ET.fromstring("""{BIBLIOTECA}""")\nprint(raiz.find("libro[2]").get("id"))',
            "2",
            ["1", "3", "Error"],
            "Como en XPath, la posición `[2]` cuenta desde 1: es el segundo libro.",
        ),
        pq(
            "mar-39",
            QUE,
            f'import xml.etree.ElementTree as ET\nraiz = ET.fromstring("""{BIBLIOTECA}""")\nprint(sum(int(p.text) for p in raiz.iter("precio")))',
            "55",
            ["12", "3", "Error"],
            "`iter` recorre todos los descendientes con ese nombre: 12 + 25 + 18. En XPath sería `sum(//precio)`.",
        ),
        fq(
            "mar-40",
            "Completa el hueco para seleccionar todos los títulos, estén donde estén.",
            f'import xml.etree.ElementTree as ET\nraiz = ET.fromstring("""{BIBLIOTECA}""")\nprint(len(raiz.findall("___")))',
            [".//titulo"],
            "3",
            "`.//titulo` busca a cualquier profundidad desde el nodo actual.",
        ),
        tq(
            "mar-41",
            "¿Qué selecciona la expresión XPath `//libro[precio > 20]/titulo`?",
            [
                "Los títulos de los libros que cuestan más de 20",
                "Los precios mayores que 20",
                "El libro número 20",
                "Todos los títulos, ordenados por precio",
            ],
            0,
            "El predicado filtra los libros y la ruta sigue hasta su `titulo`.",
        ),
        tq(
            "mar-42",
            "¿Qué devuelve `count(//libro)`?",
            [
                "El número de elementos libro del documento",
                "El primer libro",
                "La suma de los precios",
                "El número de atributos",
            ],
            0,
            "`count()` cuenta los nodos de una secuencia.",
        ),
        kq(
            "mar-43",
            "¿Qué hace esta instrucción de una hoja XSLT?",
            '<xsl:value-of select="titulo"/>',
            [
                "Escribe en la salida el texto del elemento titulo",
                "Crea un elemento titulo vacío",
                "Recorre todos los títulos",
                "Ordena por título",
            ],
            0,
            "Para recorrer se usa `xsl:for-each` y para ordenar, `xsl:sort`.",
        ),
        tq(
            "mar-44",
            "¿Para qué sirve XSLT?",
            [
                "Para transformar un XML en otro XML, en HTML o en texto",
                "Para validar un XML contra una DTD",
                "Para dar estilos a una página HTML como CSS",
                "Para guardar XML en una base de datos relacional",
            ],
            0,
            "XSLT transforma; la validación es cosa de la DTD o el XSD.",
        ),
        tq(
            "mar-45",
            "¿Qué significan las letras de FLWOR en XQuery?",
            [
                "for, let, where, order by, return",
                "find, load, write, open, read",
                "from, list, with, or, run",
                "for, loop, while, or, return",
            ],
            0,
            "Recorre (`for`), asigna (`let`), filtra (`where`), ordena (`order by`) y devuelve (`return`).",
        ),
        tq(
            "mar-46",
            "¿Qué es una base de datos XML nativa?",
            [
                "Una que guarda y consulta documentos XML directamente, como BaseX o eXist-db",
                "Una base de datos relacional con una columna de texto",
                "Un archivo XML muy grande",
                "Una hoja de cálculo exportada a XML",
            ],
            0,
            "Se consultan con XPath y XQuery, sin pasar los datos a tablas.",
        ),
    ],
    quiz=[
        tq(
            "mar-q07",
            "En XPath, ¿qué selecciona `@id`?",
            ["El atributo id", "El elemento id", "El primer hijo", "El texto del nodo"],
            0,
            "La arroba indica un atributo.",
        ),
        tq(
            "mar-q08",
            "¿Qué programa aplica una hoja XSLT a un XML?",
            [
                "Un procesador XSLT, como xsltproc o Saxon",
                "Un validador de DTD",
                "Un compilador de C",
                "Un servidor DNS",
            ],
            0,
            "Los navegadores también traen un procesador de XSLT 1.0.",
        ),
    ],
    objectives=[
        "Seleccionar nodos de un documento XML con expresiones XPath (RA6 e).",
        "Escribir una hoja XSLT que convierta un XML en HTML (RA5 c-g).",
        "Reconocer XQuery y las bases de datos XML nativas (RA6 h, i).",
    ],
    mistakes=[
        ("Contar las posiciones desde 0: `libro[0]`.", "En XPath la primera posición es `[1]`."),
        (
            "Olvidar la `@` de los atributos: `libro[idioma='es']`.",
            "Eso busca un hijo `<idioma>`; el atributo es `@idioma`.",
        ),
        (
            "Esperar en ElementTree todo XPath (`count()`, `precio > 20`).",
            "ElementTree admite un subconjunto; para el resto usa `lxml` o `xmllint --xpath`.",
        ),
        (
            "Olvidar el espacio de nombres `xsl:` en la hoja.",
            'Declara `xmlns:xsl="http://www.w3.org/1999/XSL/Transform"` en `xsl:stylesheet`.',
        ),
    ],
    summary=[
        "XPath recorre el árbol: `/` desde la raíz, `//` a cualquier profundidad, `@` para atributos y `[…]` para filtrar.",
        "XSLT transforma XML en XML, HTML o texto con plantillas (`xsl:template`), bucles (`xsl:for-each`) y `xsl:value-of`.",
        "XQuery consulta colecciones de XML con expresiones FLWOR; lo usan BaseX y eXist-db.",
    ],
    solution=(
        TABLA_XSL,
        "La plantilla de `/` crea la tabla y `xsl:for-each` genera una fila por libro, ordenada por precio como número. `xsl:value-of` escribe el texto de cada hijo.",
    ),
    sources=[XPATH, XSLT, ETREE],
)

L_JSON = Lesson(
    slug="mar-json-intercambio",
    title="JSON e intercambio de datos",
    theory="""
**JSON** (JavaScript Object Notation) es hoy el formato de intercambio más usado en la web: lo devuelven casi todas las API REST. Es texto, ligero y fácil de leer para personas y programas.

**Sintaxis:**
- **Objeto**: pares clave-valor entre llaves, `{"nombre": "Ana", "edad": 20}`. Las claves van **siempre entre comillas dobles**.
- **Array**: lista ordenada entre corchetes, `[1, 2, 3]`.
- **Valores**: cadena (comillas dobles), número, `true`, `false`, `null`, objeto o array.
- **No admite** comentarios, comas al final (`[1, 2,]`) ni comillas simples.

**XML, JSON, CSV o YAML:**
- **XML**: atributos, espacios de nombres, validación madura (XSD) y transformaciones (XSLT). Más verboso.
- **JSON**: más compacto y nativo en JavaScript; se valida con JSON Schema.
- **CSV**: tablas planas, ideal para hojas de cálculo; sin jerarquía ni tipos.
- **YAML**: muy legible, usado en configuraciones (Docker Compose, GitHub Actions).

**Guardar datos en formatos de intercambio** tiene ventajas (portables, legibles, independientes del programa) e inconvenientes: no hay índices, consultas eficientes, transacciones ni control de acceso como en un gestor de bases de datos. Por eso lo habitual es **guardar en una base de datos y exportar** a JSON o XML para enviar.

**De una base de datos relacional a JSON o XML:** se consulta con SQL y se convierte cada fila en un objeto o un elemento. Muchos gestores lo hacen ellos mismos: `JSON_OBJECT` en MySQL, `json_agg` en PostgreSQL o las funciones SQL/XML (`XMLELEMENT`). Los gestores también pueden **guardar** JSON en columnas de tipo JSON y consultarlo.

En Python, el módulo `json` convierte: `json.loads` (texto → diccionarios y listas) y `json.dumps` (al revés). `json.dumps(datos, ensure_ascii=False, indent=2)` deja las tildes tal cual y sangra el resultado.
""",
    example="""
import json
import sqlite3

# De una base de datos relacional a JSON
bd = sqlite3.connect(":memory:")
bd.execute("CREATE TABLE alumno (id INTEGER, nombre TEXT, nota REAL)")
bd.executemany("INSERT INTO alumno VALUES (?, ?, ?)", [(1, "Ana", 8.5), (2, "Íker", 6.0)])

filas = bd.execute("SELECT id, nombre, nota FROM alumno ORDER BY id").fetchall()
alumnos = [{"id": i, "nombre": n, "nota": nota} for i, n, nota in filas]
texto = json.dumps({"alumnos": alumnos}, ensure_ascii=False, indent=2)
print(texto)

# Y de vuelta: de JSON a objetos de Python
print(json.loads(texto)["alumnos"][1]["nombre"])
""",
    exercise="""
1. Escribe a mano un `catalogo.json` con un array de tres productos (`id`, `nombre`, `precio`, `etiquetas` como array y `oferta` como booleano).
2. Léelo con Python y muestra los productos que están en oferta.
3. Convierte el mismo catálogo a XML con `xml.etree.ElementTree` y guárdalo en `catalogo.xml`.
4. Compara el tamaño de los dos archivos.
""",
    starter='import json\n\nwith open("catalogo.json", encoding="utf-8") as archivo:\n    catalogo = json.load(archivo)\n\nfor producto in catalogo:\n    pass  # muestra los que estén en oferta\n',
    hint='`if producto["oferta"]:`. Para el XML: `ET.SubElement(raiz, "producto", id=str(p["id"]))`.',
    faq=[
        (
            "¿JSON ha sustituido a XML?",
            "En las API web, casi. XML sigue en documentos (ofimática), configuración, facturación electrónica y en muchos sistemas empresariales.",
        ),
        (
            "¿Por qué `True` de Python sale como `true`?",
            "`json.dumps` traduce a la sintaxis de JSON: `True` → `true`, `None` → `null`, tuplas → arrays.",
        ),
    ],
    challenge=(
        "Exporta una consulta",
        2,
        "Crea con `sqlite3` una tabla de pedidos (cliente, total) con cinco filas. Exporta a JSON un objeto por cliente con su número de pedidos y la suma total, usando `GROUP BY`.",
        'import json\nimport sqlite3\n\nbd = sqlite3.connect(":memory:")\n',
        "`SELECT cliente, COUNT(*), SUM(total) FROM pedido GROUP BY cliente` y un diccionario por fila.",
    ),
    questions=[
        jq(
            "mar-47",
            "{'nombre': 'Ana'}",
            [
                JSON_OK,
                "No: las cadenas van entre comillas dobles",
                "No: falta un array",
                "No: un objeto no puede tener una sola clave",
            ],
            1,
            "JSON solo admite comillas dobles en claves y cadenas.",
        ),
        jq(
            "mar-48",
            '{"notas": [7, 8, 9,]}',
            [
                "No: sobra la coma final",
                JSON_OK,
                "No: los números van entre comillas",
                "No: los arrays no pueden ir dentro de objetos",
            ],
            0,
            "Las comas finales son válidas en JavaScript, pero no en JSON.",
        ),
        jq(
            "mar-49",
            '{"activo": true, "padre": null, "etiquetas": [], "precio": 9.5}',
            [
                "No: null no existe en JSON",
                "No: un array no puede estar vacío",
                JSON_OK,
                "No: true va entre comillas",
            ],
            2,
            "`true`, `null`, los arrays vacíos y los decimales son JSON válido.",
        ),
        jq(
            "mar-50",
            '{"nombre": "Ana" // alumna\n}',
            [
                JSON_OK,
                "No: JSON no admite comentarios",
                "No: falta una coma",
                "No: las claves no llevan comillas",
            ],
            1,
            'JSON no tiene comentarios. Si se necesitan, se usa otro formato (YAML) o una clave como `"_nota"`.',
        ),
        pq(
            "mar-51",
            QUE,
            'import json\ndatos = json.loads(\'{"alumnos": [{"nombre": "Ana"}, {"nombre": "Íker"}]}\')\nprint(len(datos["alumnos"]), datos["alumnos"][1]["nombre"])',
            "2 Íker",
            ["2 Ana", "1 Íker", "Error"],
            "Un array de JSON es una lista de Python y un objeto, un diccionario.",
        ),
        pq(
            "mar-52",
            QUE,
            'import json\nprint(json.dumps({"ok": True, "valor": None, "lista": (1, 2)}))',
            '{"ok": true, "valor": null, "lista": [1, 2]}',
            [
                '{"ok": True, "valor": None, "lista": (1, 2)}',
                "{'ok': true, 'valor': null, 'lista': [1, 2]}",
                "Error",
            ],
            "`dumps` traduce `True` a `true`, `None` a `null` y las tuplas a arrays.",
        ),
        pq(
            "mar-53",
            QUE,
            'import json\nprint(json.dumps({"ciudad": "Málaga"}))',
            '{"ciudad": "M\\u00e1laga"}',
            ['{"ciudad": "Málaga"}', "{'ciudad': 'Málaga'}", "Error"],
            "Por defecto `dumps` escapa lo que no es ASCII. Con `ensure_ascii=False` sale «Málaga».",
        ),
        pq(
            "mar-54",
            QUE,
            'import json\nimport xml.etree.ElementTree as ET\nraiz = ET.fromstring(\'<alumnos><alumno nota="8">Ana</alumno><alumno nota="6">Íker</alumno></alumnos>\')\nlista = [{"nombre": a.text, "nota": int(a.get("nota"))} for a in raiz]\nprint(json.dumps(lista, ensure_ascii=False))',
            '[{"nombre": "Ana", "nota": 8}, {"nombre": "Íker", "nota": 6}]',
            [
                '[{"nombre": "Ana", "nota": "8"}, {"nombre": "Íker", "nota": "6"}]',
                '{"alumnos": ["Ana", "Íker"]}',
                "Error",
            ],
            "Una conversión de XML a JSON: cada elemento pasa a ser un objeto. `int()` convierte el atributo, que en XML siempre es texto.",
        ),
        pq(
            "mar-55",
            QUE,
            'import json\nimport sqlite3\nbd = sqlite3.connect(":memory:")\nbd.execute("CREATE TABLE ciudad (nombre TEXT, habitantes INTEGER)")\nbd.executemany("INSERT INTO ciudad VALUES (?, ?)", [("Soria", 40), ("León", 120), ("Ávila", 58)])\nfilas = bd.execute("SELECT nombre FROM ciudad WHERE habitantes > 50 ORDER BY nombre").fetchall()\nprint(json.dumps([n for (n,) in filas], ensure_ascii=False))',
            '["León", "Ávila"]',
            ['["Ávila", "León"]', '["León", "Ávila", "Soria"]', "Error"],
            "SQLite ordena el texto por su código: «L» va antes que «Á», que no es una letra ASCII. Para ordenar como un diccionario hace falta una intercalación (COLLATE).",
        ),
        fq(
            "mar-56",
            "Completa el hueco para convertir el texto JSON en un diccionario.",
            'import json\ntexto = \'{"curso": "DAW", "anio": 1}\'\ndatos = json.___(texto)\nprint(datos["curso"])',
            ["loads"],
            "DAW",
            "`loads` (load string) lee un texto; `load`, un archivo abierto.",
        ),
        tq(
            "mar-57",
            "¿Qué inconveniente tiene guardar los datos de una aplicación solo en archivos JSON o XML?",
            [
                "No tienen índices, transacciones ni control de acceso como un gestor de bases de datos",
                "No se pueden leer con un editor de texto",
                "Dependen del sistema operativo",
                "Solo admiten números",
            ],
            0,
            "Por eso se guardan en un gestor y se exportan a JSON o XML para intercambiarlos.",
        ),
    ],
    quiz=[
        tq(
            "mar-q09",
            "¿Qué formato devuelve hoy la mayoría de las API REST?",
            ["JSON", "CSV", "RTF", "SGML"],
            0,
            "Algunas también ofrecen XML, pero JSON es el más común.",
        ),
        tq(
            "mar-q10",
            "¿Qué función de Python convierte un diccionario en texto JSON?",
            ["json.dumps", "json.loads", "json.parse", "json.read"],
            0,
            "`dumps` escribe; `loads` lee.",
        ),
    ],
    objectives=[
        "Escribir JSON válido y distinguirlo de un objeto de JavaScript o de Python (RA6 a, d).",
        "Comparar XML, JSON, CSV y YAML y elegir el adecuado (RA6 b, c).",
        "Exportar a JSON los datos de una base de datos relacional y convertir entre XML y JSON (RA5 g, RA6 f, g).",
    ],
    mistakes=[
        (
            "Escribir las claves o las cadenas con comillas simples.",
            "JSON solo admite comillas dobles.",
        ),
        ("Dejar una coma después del último elemento.", "JSON no admite comas finales."),
        ("Añadir comentarios con `//`.", "JSON no tiene comentarios."),
        (
            "Confundir `json.load` con `json.loads`.",
            "`load` lee un archivo abierto; `loads`, un texto.",
        ),
    ],
    summary=[
        "JSON tiene objetos, arrays, cadenas, números, `true`, `false` y `null`.",
        "Es el formato de casi todas las API REST; XML sigue en documentos y sistemas empresariales.",
        "Los formatos de intercambio sirven para mover datos; para guardarlos con índices y transacciones está la base de datos.",
        "En Python, `json.loads` lee, `json.dumps` escribe y `ensure_ascii=False` conserva las tildes.",
    ],
    solution=(
        CATALOGO_PY,
        '`json.loads` convierte el texto en una lista de diccionarios. Después se filtra por `oferta` y se construye el XML con `ET.SubElement`: los atributos de XML siempre son texto, por eso `str(p["id"])`.',
    ),
    sources=[JSON_RFC, PY_JSON],
)

RSS_DOC = """<rss version="2.0"><channel>
  <title>Blog de DAW</title><link>https://ejemplo.org/</link><description>Apuntes</description>
  <item><title>XPath en 5 minutos</title><link>https://ejemplo.org/xpath</link></item>
  <item><title>JSON frente a XML</title><link>https://ejemplo.org/json</link></item>
</channel></rss>"""

L_GESTION = Lesson(
    slug="mar-sindicacion-erp",
    title="Sindicación y sistemas de gestión empresarial",
    theory="""
**Sindicación de contenidos:** un sitio publica un archivo XML (un **canal** o *feed*) con sus últimas novedades y los programas lo consultan cada cierto tiempo. Así puedes seguir muchos blogs o medios desde un **lector de noticias** (Feedly, Thunderbird, NetNewsWire) sin visitarlos uno a uno. Los **pódcast** se distribuyen así: cada episodio es una entrada con el audio adjunto.

- **RSS 2.0**: `<rss version="2.0">` con un `<channel>` (con `title`, `link` y `description` obligatorios) y un `<item>` por noticia (`title`, `link`, `description`, `pubDate`, `guid`).
- **Atom** (RFC 4287): `<feed xmlns="http://www.w3.org/2005/Atom">` con varias `<entry>`, cada una con `id`, `title` y `updated` obligatorios. Más estricto y con espacio de nombres propio.
- La página anuncia su canal en el `<head>`: `<link rel="alternate" type="application/rss+xml" href="/feed.xml">`.

**Sistemas de gestión empresarial:**
- **ERP** (planificación de recursos empresariales): integra en una sola aplicación y una sola base de datos la contabilidad, las compras, las ventas, el inventario, la facturación y los recursos humanos. Cada área es un **módulo** que se activa según la empresa.
- **CRM** (gestión de la relación con clientes): contactos, oportunidades de venta, campañas y atención al cliente.
- **Ventajas**: los datos se introducen una vez y los comparten todos los departamentos, se evitan errores al copiar, hay informes en tiempo real y procesos comunes.
- **Ejemplos de software libre**: **Odoo** (edición Community), **Dolibarr** y **ERPNext**. Comerciales: SAP, Microsoft Dynamics.
- **Instalación**: en un servidor propio (*on-premise*), en un contenedor Docker o como servicio en la nube (SaaS). Se configura la empresa, los módulos, los usuarios y sus **roles y permisos** (cada usuario ve solo lo que necesita).
- **Seguridad**: contraseñas robustas y doble factor, permisos mínimos, HTTPS, **copias de seguridad** de la base de datos probadas y registro de accesos.
- **Explotación**: generar **informes**, **importar** datos (clientes o productos desde CSV o Excel) y **exportarlos** o conectarlos con otros sistemas mediante su **API** (Odoo ofrece XML-RPC y JSON-RPC). Se documenta todo en un manual de usuario y uno de administración.
""",
    example="""
import csv
import io
import xml.etree.ElementTree as ET

canal = ET.fromstring('''<rss version="2.0"><channel>
  <title>Blog de DAW</title><link>https://ejemplo.org/</link><description>Apuntes</description>
  <item><title>XPath en 5 minutos</title><link>https://ejemplo.org/xpath</link></item>
  <item><title>JSON frente a XML</title><link>https://ejemplo.org/json</link></item>
</channel></rss>''')

print("Canal:", canal.find("channel/title").text)

# Exportar las entradas a CSV, como se importarían en otra aplicación
salida = io.StringIO()
escritor = csv.writer(salida)
escritor.writerow(["titulo", "enlace"])
for item in canal.iter("item"):
    escritor.writerow([item.find("title").text, item.find("link").text])
print(salida.getvalue())
""",
    exercise="""
1. Escribe a mano un canal RSS 2.0 con tres entradas sobre lo que estudias esta semana y valídalo en validator.w3.org/feed.
2. Ábrelo en un lector de noticias.
3. Instala Odoo Community o Dolibarr en un contenedor Docker, crea una empresa, activa los módulos de ventas e inventario y dos usuarios con permisos distintos.
4. Importa diez productos desde un CSV y genera un informe de ventas.
""",
    starter='<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0">\n  <channel>\n    <title>Mi semana en DAW</title>\n    <link>https://ejemplo.org/</link>\n    <description>Lo que estudio</description>\n    <!-- tres <item> -->\n  </channel>\n</rss>\n',
    hint="Cada `<item>` necesita al menos `title` o `description`. Añade `pubDate` en formato RFC 822: `Mon, 02 Nov 2026 10:00:00 GMT`.",
    faq=[
        (
            "¿Siguen usándose los RSS?",
            "Sí: los pódcast, muchos medios, blogs y repositorios (GitHub publica un Atom de los lanzamientos de cada proyecto).",
        ),
        (
            "¿Odoo es gratis?",
            "La edición Community es software libre (LGPL). La Enterprise y el alojamiento en la nube de Odoo son de pago.",
        ),
    ],
    challenge=(
        "Lector de noticias mínimo",
        2,
        "Escribe un programa que lea un canal RSS guardado en un archivo, muestre el título del canal y, de cada entrada, el título y el enlace. Después haz que también lea un canal Atom (recuerda el espacio de nombres).",
        'import xml.etree.ElementTree as ET\n\ncanal = ET.parse("feed.xml").getroot()\n',
        'En Atom, busca con el espacio de nombres: `raiz.findall("{http://www.w3.org/2005/Atom}entry")`.',
    ),
    questions=[
        tq(
            "mar-58",
            "¿Qué es la sindicación de contenidos?",
            [
                "Publicar un canal XML con las novedades para que otros programas las lean",
                "Copiar una web entera en otro servidor",
                "Enviar un boletín por correo",
                "Enlazar una hoja de estilos",
            ],
            0,
            "Los lectores de noticias y las aplicaciones de pódcast consultan esos canales.",
        ),
        tq(
            "mar-59",
            "¿Qué elemento de RSS 2.0 representa cada noticia?",
            ["<item>", "<entry>", "<channel>", "<article>"],
            0,
            "`<entry>` es el equivalente en Atom; `<channel>` contiene a todos los `<item>`.",
        ),
        pq(
            "mar-60",
            QUE,
            f'import xml.etree.ElementTree as ET\ncanal = ET.fromstring("""{RSS_DOC}""")\nprint(len(canal.findall("channel/item")), canal.find("channel/item/title").text)',
            "2 XPath en 5 minutos",
            ["2 Blog de DAW", "3 XPath en 5 minutos", "Error"],
            "Hay dos `<item>`; `find` devuelve el primero que encaja con la ruta.",
        ),
        pq(
            "mar-61",
            QUE,
            'import xml.etree.ElementTree as ET\nfeed = ET.fromstring(\'<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>Hola</title></entry></feed>\')\nprint(feed.find("entry"), feed.find("{http://www.w3.org/2005/Atom}entry/{http://www.w3.org/2005/Atom}title").text)',
            "None Hola",
            ["entry Hola", "None None", "Error"],
            "Con el espacio de nombres por defecto, el nombre real es `{URI}entry`: sin la URI, `find` no lo encuentra.",
        ),
        tq(
            "mar-62",
            "¿Qué es un ERP?",
            [
                "Una aplicación que integra la gestión de contabilidad, compras, ventas, inventario y personal",
                "Un lenguaje de marcas para facturas",
                "Un lector de canales RSS",
                "Un tipo de servidor web",
            ],
            0,
            "Todas las áreas comparten una base de datos y se activan como módulos.",
        ),
        tq(
            "mar-63",
            "¿Qué gestiona principalmente un CRM?",
            [
                "La relación con los clientes: contactos, oportunidades y campañas",
                "Las nóminas",
                "Los servidores de la empresa",
                "El código fuente",
            ],
            0,
            "Muchos ERP incluyen un módulo de CRM.",
        ),
        tq(
            "mar-64",
            "¿Cuál de estos es un ERP de software libre?",
            ["Dolibarr", "SAP S/4HANA", "Microsoft Dynamics 365", "Salesforce"],
            0,
            "Odoo Community y ERPNext también lo son. Los otros tres son comerciales.",
        ),
        tq(
            "mar-65",
            "Al configurar un ERP, ¿qué permisos debe tener cada usuario?",
            [
                "Solo los que necesita para su trabajo",
                "Todos, para que nadie se quede bloqueado",
                "Los mismos que el administrador",
                "Ninguno hasta que lo pida",
            ],
            0,
            "Es el principio de mínimo privilegio: limita el daño de un error o de una cuenta robada.",
        ),
        oq(
            "mar-66",
            "Ordena las líneas para exportar los productos a CSV.",
            [
                "import csv, io",
                "salida = io.StringIO()",
                "escritor = csv.writer(salida, lineterminator='\\n')",
                "escritor.writerow(['id', 'nombre'])",
                "escritor.writerow([1, 'Teclado'])",
                "print(salida.getvalue().strip())",
            ],
            "id,nombre\n1,Teclado",
            "Se importa, se crea el destino, el escritor, la cabecera, las filas y al final se muestra.",
        ),
    ],
    quiz=[
        tq(
            "mar-q11",
            "¿Qué ventaja principal tiene un ERP frente a una aplicación distinta por departamento?",
            [
                "Los datos se introducen una vez y los comparten todos los departamentos",
                "Es siempre gratuito",
                "No necesita base de datos",
                "No hace falta configurarlo",
            ],
            0,
            "Se evitan duplicados y errores al copiar datos de un programa a otro.",
        ),
        tq(
            "mar-q12",
            "¿Qué formato de sindicación usa el espacio de nombres http://www.w3.org/2005/Atom?",
            ["Atom", "RSS 2.0", "JSON", "SVG"],
            0,
            "RSS 2.0 no usa espacio de nombres en sus elementos básicos.",
        ),
    ],
    objectives=[
        "Reconocer las tecnologías de sindicación (RSS y Atom) y sus usos (RA2 i, j).",
        "Identificar los sistemas de gestión empresarial y sus ventajas (RA7 a-c).",
        "Describir la instalación, la configuración de usuarios y permisos, los informes y la importación de datos de un ERP (RA7 d-i).",
    ],
    mistakes=[
        (
            "Buscar `entry` en un canal Atom sin el espacio de nombres.",
            "En ElementTree el nombre real es `{http://www.w3.org/2005/Atom}entry`.",
        ),
        (
            "Olvidar `title`, `link` o `description` en el `<channel>`.",
            "Son obligatorios en RSS 2.0: el validador de canales lo avisa.",
        ),
        (
            "Dar a todos los usuarios del ERP permisos de administrador.",
            "Aplica el mínimo privilegio: cada rol ve solo lo que necesita.",
        ),
        (
            "No probar las copias de seguridad.",
            "Restaura de vez en cuando una copia en otro entorno para comprobar que sirve.",
        ),
    ],
    summary=[
        "Un canal RSS o Atom es un XML con las últimas novedades que leen los lectores de noticias y las aplicaciones de pódcast.",
        "Un ERP integra contabilidad, compras, ventas, inventario y personal en una base de datos; un CRM, la relación con los clientes.",
        "Odoo Community, Dolibarr y ERPNext son ERP de software libre.",
        "Explotar un ERP es configurar roles, generar informes, importar y exportar datos y conectarlo por su API.",
    ],
    solution=(
        CANAL_RSS,
        "Un `<channel>` con sus tres campos obligatorios y un `<item>` por entrada, con `guid` único y `pubDate` en formato RFC 822. Pásalo por validator.w3.org/feed antes de publicarlo.",
    ),
    sources=[RSS, ATOM, ODOO],
)

BLOCKS = [
    Block(
        "mar-xml",
        "XML bien formado",
        "Lenguajes de marcas, estructura de XML, reglas sintácticas y espacios de nombres.",
        20,
        [L_XML],
    ),
    Block(
        "mar-html",
        "HTML y CSS",
        "Estructura de HTML5, etiquetas semánticas, selectores, cascada y validación.",
        20,
        [L_HTML],
    ),
    Block(
        "mar-validacion",
        "Validación: DTD y XML Schema",
        "Modelos de contenido, atributos, tipos de datos y restricciones.",
        15,
        [L_VALIDACION],
    ),
    Block(
        "mar-consultas",
        "XPath, XSLT y XQuery",
        "Seleccionar nodos, transformar documentos y consultar bases de datos XML.",
        15,
        [L_XPATH],
    ),
    Block(
        "mar-json",
        "JSON e intercambio de datos",
        "Sintaxis de JSON, comparación de formatos y exportar desde una base de datos.",
        15,
        [L_JSON],
    ),
    Block(
        "mar-gestion",
        "Sindicación y gestión empresarial",
        "RSS y Atom; ERP y CRM: instalación, permisos, informes e importación.",
        15,
        [L_GESTION],
    ),
]


def check_solutions() -> None:
    """Las soluciones también se comprueban: XML bien formado, DTD cumplida y Python que funciona."""
    for xml in (AGENDA, PEDIDO, TABLA_XSL, CANAL_RSS):
        assert xml_ok(xml), f"una solución XML no está bien formada:\n{xml[:80]}"
    pedido = ET.fromstring(PEDIDO)
    assert dtd_matches("(cliente, linea+, nota?)", [hijo.tag for hijo in pedido])
    assert all(linea.get("ref") for linea in pedido.iter("linea"))
    assert ET.fromstring(CANAL_RSS).find("channel/title") is not None
    assert FICHA.startswith("<!DOCTYPE html>") and 'alt="' in FICHA and FICHA.count("<main>") == 1
    check_example(CATALOGO_PY)
    assert run_python(CATALOGO_PY).splitlines()[:2] == ["Teclado 25.5", "Monitor 149.9"]


if __name__ == "__main__":
    check_solutions()
    main("marcas", BLOCKS, run_python, check_example, module="0373")
