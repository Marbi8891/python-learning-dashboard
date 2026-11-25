# ruff: noqa: E501
# (fichas de recursos: los textos largos van en una sola línea para poder leerlos y editarlos)
"""Genera frontend/data/resources.json: el catálogo de recursos complementarios del ciclo DAW.

Cada recurso se ha revisado a mano en la fecha de `checked`: quién lo publica, la licencia que
declara y si se puede acceder sin registro ni pago. Lo que no se ha podido comprobar se dice
(`license: "No identificada"`, `access: "no-verificado"`). No se inventa ninguna licencia.

La plataforma solo **enlaza** estos recursos: no copia su contenido. Las explicaciones de los
cursos son propias y los recursos son material complementario.

El script valida el catálogo: ids únicos y estables, módulos que existen en el currículo,
lecciones que existen en los cursos, URL https, campos obligatorios y valores permitidos.

Uso:  python scripts/resources/build_resources.py           (genera)
      python scripts/resources/build_resources.py --check   (CI: falla si no está al día o no es válido)
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "frontend" / "data"
OUT = DATA / "resources.json"

CHECKED = "2026-11-02"

TYPES = {
    "documentacion": "Documentación oficial",
    "especificacion": "Especificación o estándar",
    "libro": "Libro",
    "apuntes": "Apuntes",
    "repositorio": "Repositorio de código",
    "herramienta": "Herramienta en línea",
    "indice": "Índice de recursos",
    "normativa": "Normativa oficial",
    "curso": "Curso universitario o plataforma educativa estructurada",
}

ACCESS = {
    "accesible": "Accesible sin registro",
    "descargable": "Descargable",
    "registro": "Necesita registro",
    "pago": "De pago",
    "licencia-no-identificada": "Licencia no identificada: solo enlazar",
    "obsoleto": "Obsoleto",
    "no-disponible": "No disponible",
    "no-verificado": "No se pudo verificar",
}

QUALITY = {"alta", "media", "baja"}

# id, título, módulos (códigos del currículo), lecciones (curso/lección), autor, URL, descarga,
# idioma, tipo, licencia, reutilización, acceso, calidad, descripción
RESOURCES: list[dict] = [
    {
        "id": "res-mdn-html",
        "title": "MDN Web Docs: HTML",
        "modules": ["0373", "0615"],
        "lessons": ["marcas/mar-html-css"],
        "author": "Colaboradores de Mozilla",
        "url": "https://developer.mozilla.org/es/docs/Web/HTML",
        "lang": "es",
        "type": "documentacion",
        "license": "CC BY-SA 2.5 (textos); CC0 1.0 o MIT (ejemplos de código)",
        "reuse": "Se puede reutilizar citando a «Colaboradores de Mozilla» y con la misma licencia.",
        "access": "accesible",
        "quality": "alta",
        "description": "Referencia de todas las etiquetas y atributos de HTML, con guías para empezar.",
    },
    {
        "id": "res-mdn-css",
        "title": "MDN Web Docs: CSS",
        "modules": ["0373", "0615"],
        "lessons": ["marcas/mar-html-css"],
        "author": "Colaboradores de Mozilla",
        "url": "https://developer.mozilla.org/es/docs/Web/CSS",
        "lang": "es",
        "type": "documentacion",
        "license": "CC BY-SA 2.5 (textos); CC0 1.0 o MIT (ejemplos de código)",
        "reuse": "Se puede reutilizar citando a «Colaboradores de Mozilla» y con la misma licencia.",
        "access": "accesible",
        "quality": "alta",
        "description": "Selectores, cascada, modelo de caja, Flexbox, Grid y diseño adaptable.",
    },
    {
        "id": "res-mdn-js",
        "title": "MDN Web Docs: JavaScript",
        "modules": ["0612"],
        "lessons": [],
        "author": "Colaboradores de Mozilla",
        "url": "https://developer.mozilla.org/es/docs/Web/JavaScript",
        "lang": "es",
        "type": "documentacion",
        "license": "CC BY-SA 2.5 (textos); CC0 1.0 o MIT (ejemplos de código)",
        "reuse": "Se puede reutilizar citando a «Colaboradores de Mozilla» y con la misma licencia.",
        "access": "accesible",
        "quality": "alta",
        "description": "Guía y referencia del lenguaje, el DOM y las API del navegador.",
    },
    {
        "id": "res-php-manual",
        "title": "Manual de PHP",
        "modules": ["0613"],
        "lessons": [],
        "author": "The PHP Documentation Group",
        "url": "https://www.php.net/manual/es/",
        "lang": "es",
        "type": "documentacion",
        "license": "CC BY 3.0 o posterior",
        "reuse": "Se puede reutilizar citando al PHP Documentation Group.",
        "access": "accesible",
        "quality": "alta",
        "description": "Referencia oficial del lenguaje, sus funciones, sesiones, formularios y acceso a bases de datos.",
    },
    {
        "id": "res-docker-docs",
        "title": "Documentación de Docker",
        "modules": ["0614"],
        "lessons": [],
        "author": "Docker, Inc. y colaboradores",
        "url": "https://docs.docker.com/",
        "lang": "en",
        "type": "documentacion",
        "license": "Apache-2.0 (repositorio docker/docs)",
        "reuse": "Se puede reutilizar conservando el aviso de la licencia Apache 2.0.",
        "access": "accesible",
        "quality": "alta",
        "description": "Contenedores, imágenes, Docker Compose y despliegue.",
    },
    {
        "id": "res-pro-git",
        "title": "Pro Git (2.ª edición, en español)",
        "modules": ["0487", "0614"],
        "lessons": [],
        "author": "Scott Chacon y Ben Straub",
        "url": "https://git-scm.com/book/es/v2",
        "download": "https://github.com/progit/progit2-es/releases/download/2.1.23/progit.pdf",
        "lang": "es",
        "type": "libro",
        "license": "CC BY-NC-SA 3.0",
        "reuse": "Uso no comercial, citando a los autores y con la misma licencia.",
        "access": "descargable",
        "quality": "alta",
        "description": "El libro de referencia de Git: ramas, repositorios remotos, flujos de trabajo y GitHub.",
    },
    {
        "id": "res-python-tutorial",
        "title": "Tutorial oficial de Python",
        "modules": ["0485"],
        "lessons": [],
        "author": "Python Software Foundation",
        "url": "https://docs.python.org/es/3/tutorial/",
        "lang": "es",
        "type": "documentacion",
        "license": "PSF License v2 (textos); PSF v2 y 0BSD (código de ejemplo)",
        "reuse": "Se puede reutilizar conservando el aviso de la licencia de la PSF.",
        "access": "accesible",
        "quality": "alta",
        "description": "Introducción oficial al lenguaje, de los tipos de datos a las clases y los módulos.",
    },
    {
        "id": "res-python-etree",
        "title": "Python: xml.etree.ElementTree",
        "modules": ["0373"],
        "lessons": ["marcas/mar-xml-bien-formado", "marcas/mar-xpath-xslt"],
        "author": "Python Software Foundation",
        "url": "https://docs.python.org/es/3/library/xml.etree.elementtree.html",
        "lang": "es",
        "type": "documentacion",
        "license": "PSF License v2 (textos); PSF v2 y 0BSD (código de ejemplo)",
        "reuse": "Se puede reutilizar conservando el aviso de la licencia de la PSF.",
        "access": "accesible",
        "quality": "alta",
        "description": "Leer, recorrer y crear XML desde Python, con el subconjunto de XPath que admite.",
    },
    {
        "id": "res-w3c-xml",
        "title": "Extensible Markup Language (XML) 1.0",
        "modules": ["0373"],
        "lessons": ["marcas/mar-xml-bien-formado", "marcas/mar-dtd-xsd"],
        "author": "W3C",
        "url": "https://www.w3.org/TR/xml/",
        "lang": "en",
        "type": "especificacion",
        "license": "W3C Document License",
        "reuse": "Se puede copiar y distribuir sin cambios con el aviso del W3C; no permite obras derivadas.",
        "access": "accesible",
        "quality": "alta",
        "description": "La especificación de XML: documentos bien formados, DTD y entidades.",
    },
    {
        "id": "res-w3c-xsd",
        "title": "XML Schema 1.1, parte 1: estructuras",
        "modules": ["0373"],
        "lessons": ["marcas/mar-dtd-xsd"],
        "author": "W3C",
        "url": "https://www.w3.org/TR/xmlschema11-1/",
        "lang": "en",
        "type": "especificacion",
        "license": "W3C Document License",
        "reuse": "Se puede copiar y distribuir sin cambios con el aviso del W3C; no permite obras derivadas.",
        "access": "accesible",
        "quality": "alta",
        "description": "Elementos, tipos complejos, cardinalidades y restricciones de XML Schema.",
    },
    {
        "id": "res-w3c-xpath",
        "title": "XPath 3.1",
        "modules": ["0373"],
        "lessons": ["marcas/mar-xpath-xslt"],
        "author": "W3C",
        "url": "https://www.w3.org/TR/xpath-31/",
        "lang": "en",
        "type": "especificacion",
        "license": "W3C Document License",
        "reuse": "Se puede copiar y distribuir sin cambios con el aviso del W3C; no permite obras derivadas.",
        "access": "accesible",
        "quality": "alta",
        "description": "Rutas, predicados y funciones del lenguaje de consulta de XML.",
    },
    {
        "id": "res-w3c-xslt",
        "title": "XSLT 3.0",
        "modules": ["0373"],
        "lessons": ["marcas/mar-xpath-xslt"],
        "author": "W3C",
        "url": "https://www.w3.org/TR/xslt-30/",
        "lang": "en",
        "type": "especificacion",
        "license": "W3C Document License",
        "reuse": "Se puede copiar y distribuir sin cambios con el aviso del W3C; no permite obras derivadas.",
        "access": "accesible",
        "quality": "alta",
        "description": "Plantillas y transformaciones de XML a XML, HTML o texto.",
    },
    {
        "id": "res-w3c-validator",
        "title": "Validador HTML del W3C",
        "modules": ["0373", "0615"],
        "lessons": ["marcas/mar-html-css"],
        "author": "W3C",
        "url": "https://validator.w3.org/",
        "lang": "en",
        "type": "herramienta",
        "license": "No aplica (herramienta en línea)",
        "reuse": "Se usa en línea; no hay contenido que reutilizar.",
        "access": "accesible",
        "quality": "alta",
        "description": "Comprueba que un documento HTML cumple el estándar y señala cada error con su línea.",
    },
    {
        "id": "res-rss-spec",
        "title": "RSS 2.0 Specification",
        "modules": ["0373"],
        "lessons": ["marcas/mar-sindicacion-erp"],
        "author": "RSS Advisory Board",
        "url": "https://www.rssboard.org/rss-specification",
        "lang": "en",
        "type": "especificacion",
        "license": "Creative Commons Attribution/Share Alike (la página no indica la versión)",
        "reuse": "Se puede reutilizar citando al RSS Advisory Board y con la misma licencia.",
        "access": "accesible",
        "quality": "alta",
        "description": "Elementos obligatorios y opcionales de un canal RSS 2.0.",
    },
    {
        "id": "res-odoo-docs",
        "title": "Documentación de Odoo",
        "modules": ["0373"],
        "lessons": ["marcas/mar-sindicacion-erp"],
        "author": "Odoo S.A. y colaboradores",
        "url": "https://www.odoo.com/documentation/",
        "lang": "en",
        "type": "documentacion",
        "license": "CC BY-SA 4.0 (repositorio odoo/documentation)",
        "reuse": "Se puede reutilizar citando la fuente y con la misma licencia.",
        "access": "accesible",
        "quality": "alta",
        "description": "Instalación, módulos, usuarios y permisos, importación de datos y API de un ERP de software libre.",
    },
    {
        "id": "res-boe-rd-405-2023",
        "title": "Real Decreto 405/2023 (título de Técnico Superior en DAW actualizado)",
        "modules": ["0373", "0483", "0484", "0485", "0487", "0612", "0613", "0614", "0615"],
        "lessons": [],
        "author": "Boletín Oficial del Estado",
        "url": "https://www.boe.es/diario_boe/txt.php?id=BOE-A-2023-13221",
        "lang": "es",
        "type": "normativa",
        "license": "Texto legal (art. 13 de la Ley de Propiedad Intelectual: sin derechos de autor)",
        "reuse": "Las disposiciones legales no son objeto de propiedad intelectual; se citan como fuente.",
        "access": "accesible",
        "quality": "alta",
        "description": "Resultados de aprendizaje, criterios de evaluación y contenidos básicos de cada módulo técnico.",
    },
    {
        "id": "res-bocyl-edu-1311-2024",
        "title": "Orden EDU/1311/2024 (currículo de DAW en Castilla y León)",
        "modules": ["0373", "0483", "0484", "0485", "0487", "0612", "0613", "0614", "0615"],
        "lessons": [],
        "author": "Junta de Castilla y León (BOCYL)",
        "url": "https://bocyl.jcyl.es/boletines/2024/12/02/pdf/BOCYL-D-02122024-27.pdf",
        "lang": "es",
        "type": "normativa",
        "license": "Texto legal (art. 13 de la Ley de Propiedad Intelectual: sin derechos de autor)",
        "reuse": "Las disposiciones legales no son objeto de propiedad intelectual; se citan como fuente.",
        "access": "descargable",
        "quality": "alta",
        "description": "Horas, curso y horas semanales de cada módulo en Castilla y León. Otras comunidades tienen su propia norma.",
    },
    {
        "id": "res-sitiolibre",
        "title": "SitioLibre: temario y apuntes de DAW",
        "modules": ["0373", "0483", "0484", "0485", "0487", "0612", "0613", "0614", "0615"],
        "lessons": [],
        "author": "José Luis Comesaña",
        "url": "https://www.sitiolibre.com/",
        "lang": "es",
        "type": "apuntes",
        "license": "CC BY-NC-SA 3.0 ES (insignia de la portada; no indica qué materiales cubre)",
        "reuse": "Uso no comercial, citando al autor y con la misma licencia. Confirmar la licencia de cada documento antes de reutilizarlo.",
        "access": "accesible",
        "quality": "media",
        "description": "Temarios y apuntes de los módulos del plan anterior (LOE). Útil como consulta; revisa que el tema siga en el currículo vigente.",
    },
    {
        "id": "res-temario-daw-statickidz",
        "title": "TemarioDAW (statickidz)",
        "modules": ["0373", "0483", "0484", "0485", "0487", "0612", "0613", "0614", "0615"],
        "lessons": [],
        "author": "statickidz (recopila material de José Luis Comesaña)",
        "url": "https://github.com/statickidz/TemarioDAW",
        "lang": "es",
        "type": "repositorio",
        "license": "No identificada",
        "reuse": "El repositorio no declara licencia: solo se enlaza. El material original está en SitioLibre.",
        "access": "licencia-no-identificada",
        "quality": "media",
        "description": "Carpetas por módulo del plan anterior (incluye FOL y EIE, ya suprimidos por el RD 500/2024).",
    },
    {
        "id": "res-2-daw-publico",
        "title": "2-DAW-PUBLICO (proyectos de 2.º de DAW)",
        "modules": ["0612", "0613", "0614", "0615"],
        "lessons": [],
        "author": "Daniel Godoy Medina",
        "url": "https://github.com/DanielGodoyDAW/2-DAW-PUBLICO",
        "lang": "es",
        "type": "repositorio",
        "license": "No identificada",
        "reuse": "El repositorio no declara licencia: solo se enlaza como inspiración.",
        "access": "licencia-no-identificada",
        "quality": "media",
        "description": "Prácticas de un alumno: Apache y Tomcat, JavaScript, PHP con sesiones y bases de datos, Flexbox, Grid y Sass.",
    },
    {
        "id": "res-cibered-daw",
        "title": "CIBERED: hoja de ruta y recursos de DAW",
        "modules": ["0373", "0483", "0484", "0485", "0487", "0612", "0613", "0614", "0615"],
        "lessons": [],
        "author": "Pablo Álvarez Corredera (CIBERED)",
        "url": "https://cibered.com/recursos-daw/",
        "lang": "es",
        "type": "indice",
        "license": "Todos los derechos reservados",
        "reuse": "No se reutiliza: solo se enlaza. Muchos libros que cita son de pago (tiendas externas).",
        "access": "accesible",
        "quality": "media",
        "description": "Índice de libros y apuntes por módulo del plan anterior. Cada enlace tiene sus propias condiciones.",
    },
    {
        "id": "res-apuntes-fp-informatica",
        "title": "Apuntes FP Informática",
        "modules": [],
        "lessons": [],
        "author": "Profesorado (proyecto mejoratudocencia.es)",
        "url": "https://apuntesfpinformatica.es/",
        "lang": "es",
        "type": "apuntes",
        "license": "No identificada (© 2026 Apuntes FP Informática)",
        "reuse": "No declara licencia: solo se enlaza.",
        "access": "licencia-no-identificada",
        "quality": "media",
        "description": "Recursos para profesorado y alumnado de informática con filtro por módulo. No se ha podido comprobar qué módulos de DAW cubre.",
    },
    {
        "id": "res-apuntesdam",
        "title": "apuntesdam.com",
        "modules": [],
        "lessons": [],
        "author": "No identificado",
        "url": "https://apuntesdam.com/",
        "lang": "es",
        "type": "apuntes",
        "license": "No identificada",
        "reuse": "Sin verificar: solo se enlaza.",
        "access": "no-verificado",
        "quality": "media",
        "description": "Apuntes de DAM. La web no permite la consulta automática (robots.txt), así que no se ha podido revisar.",
    },
    {
        "id": "res-fp-informatica-daw",
        "title": "fp-informatica.es: ciclo DAW",
        "modules": [],
        "lessons": [],
        "author": "fp-informatica.es",
        "url": "https://www.fp-informatica.es/daw/",
        "lang": "es",
        "type": "indice",
        "license": "No identificada",
        "reuse": "Solo se enlaza.",
        "access": "obsoleto",
        "quality": "baja",
        "description": "Ficha del ciclo con el plan antiguo (RD 686/2010: FOL, EIE y FCT), centros por provincia, calendario y foro. No sirve como currículo vigente.",
    },
    {
        "id": "res-harvard-cs50x",
        "title": "Harvard CS50x: Introduction to Computer Science",
        "modules": [],
        "lessons": [],
        "author": "Harvard University · CS50",
        "url": "https://cs50.harvard.edu/x/",
        "lang": "en",
        "type": "curso",
        "license": "Solo enlazar; consultar licencia del contenido original antes de reutilizar.",
        "reuse": "PLD enlaza al recurso original; no copia contenido ni ejercicios sin comprobar sus condiciones.",
        "access": "accesible",
        "quality": "alta",
        "description": "Curso universitario abierto de fundamentos de informática, pensamiento computacional, algoritmos, C, Python, SQL, HTML, CSS y JavaScript.",
        "checked": "2026-11-25"
    },
    {
        "id": "res-harvard-cs50p",
        "title": "Harvard CS50P: Introduction to Programming with Python",
        "modules": [],
        "lessons": ["programacion/prog-ut2-elementos","programacion/prog-ut3-control","programacion/prog-ut3-funciones","programacion/prog-ut5-clases","programacion/prog-ut5-modulos-cadenas","programacion/prog-ut6-colecciones","programacion/prog-ut6-herencia-excepciones","programacion/prog-ut8-ficheros-bd"],
        "author": "Harvard University · CS50",
        "url": "https://cs50.harvard.edu/python/",
        "lang": "en",
        "type": "curso",
        "license": "Solo enlazar; consultar licencia del contenido original antes de reutilizar.",
        "reuse": "PLD enlaza al recurso original; no copia contenido ni ejercicios sin comprobar sus condiciones.",
        "access": "accesible",
        "quality": "alta",
        "description": "Curso práctico de Python: funciones, variables, tipos, condiciones, bucles, excepciones, debugging, pruebas, expresiones regulares, clases, objetos y ficheros.",
        "checked": "2026-11-25"
    },
    {
        "id": "res-harvard-cs50sql",
        "title": "Harvard CS50 SQL: Introduction to Databases with SQL",
        "modules": [],
        "lessons": ["sql/bd-tipos-y-modelos","sql/sql-modelo-relacional","sql/sql-crear-tablas","sql/bd-null-indices-dcl","sql/sql-select","sql/sql-where","sql/sql-agregados","sql/sql-group-by","sql/sql-inner-join","sql/sql-left-join-subconsultas","sql/bd-conjuntos-y-optimizacion","sql/sql-modificar-datos","sql/sql-transacciones-vistas"],
        "author": "Harvard University · CS50",
        "url": "https://cs50.harvard.edu/sql/",
        "lang": "en",
        "type": "curso",
        "license": "Solo enlazar; consultar licencia del contenido original antes de reutilizar.",
        "reuse": "PLD enlaza al recurso original; no copia contenido ni ejercicios sin comprobar sus condiciones.",
        "access": "accesible",
        "quality": "alta",
        "description": "Curso de bases de datos relacionales: modelado, tablas, tipos, restricciones, normalización, joins, vistas, índices y conexión desde otros lenguajes.",
        "checked": "2026-11-25"
    },
    {
        "id": "res-harvard-cs50web",
        "title": "Harvard CS50 Web: Programming with Python and JavaScript",
        "modules": [],
        "lessons": ["js/js-variables","js/js-coercion","js/js-funciones","js/js-ambito","js/js-arrays","js/js-objetos","js/js-dom","js/js-eventos","js/js-asincronia","js/js-fetch-json","marcas/mar-html-css","marcas/mar-json-intercambio"],
        "author": "Harvard University · CS50",
        "url": "https://cs50.harvard.edu/web/",
        "lang": "en",
        "type": "curso",
        "license": "Solo enlazar; consultar licencia del contenido original antes de reutilizar.",
        "reuse": "PLD enlaza al recurso original; no copia contenido ni ejercicios sin comprobar sus condiciones.",
        "access": "accesible",
        "quality": "alta",
        "description": "Curso de desarrollo web con Python, JavaScript, SQL y frameworks: bases de datos, APIs, interfaces, testing, CI/CD, escalabilidad y seguridad.",
        "checked": "2026-11-25"
    },
    {
        "id": "res-mit-missing-semester",
        "title": "MIT Missing Semester of Your CS Education",
        "modules": [],
        "lessons": [],
        "author": "MIT CSAIL / MIT Student Information Processing Board",
        "url": "https://missing.csail.mit.edu/",
        "lang": "en",
        "type": "curso",
        "license": "Solo enlazar; consultar licencia del contenido original antes de reutilizar.",
        "reuse": "PLD enlaza al recurso original; no copia contenido ni ejercicios sin comprobar sus condiciones.",
        "access": "accesible",
        "quality": "alta",
        "description": "Curso sobre herramientas de desarrollo: shell, terminal, entorno, debugging, profiling, Git, empaquetado y workflows.",
        "checked": "2026-11-25"
    },
    {
        "id": "res-typescript-handbook",
        "title": "TypeScript Handbook",
        "modules": [],
        "lessons": [],
        "author": "Microsoft / TypeScript",
        "url": "https://www.typescriptlang.org/docs/",
        "lang": "en",
        "type": "curso",
        "license": "Solo enlazar; consultar licencia del contenido original antes de reutilizar.",
        "reuse": "PLD enlaza al recurso original; no copia contenido ni ejercicios sin comprobar sus condiciones.",
        "access": "accesible",
        "quality": "alta",
        "description": "Manual oficial de TypeScript: tipos, narrowing, generics, módulos y configuración.",
        "checked": "2026-11-25"
    },
    {
        "id": "res-react-learn",
        "title": "React Learn",
        "modules": [],
        "lessons": [],
        "author": "React team",
        "url": "https://react.dev/learn",
        "lang": "en",
        "type": "curso",
        "license": "Solo enlazar; consultar licencia del contenido original antes de reutilizar.",
        "reuse": "PLD enlaza al recurso original; no copia contenido ni ejercicios sin comprobar sus condiciones.",
        "access": "accesible",
        "quality": "alta",
        "description": "Guía oficial de React: componentes, estado, eventos, efectos y composición.",
        "checked": "2026-11-25"
    },
    {
        "id": "res-fastapi-tutorial",
        "title": "FastAPI Tutorial",
        "modules": [],
        "lessons": [],
        "author": "FastAPI",
        "url": "https://fastapi.tiangolo.com/tutorial/",
        "lang": "en",
        "type": "curso",
        "license": "Solo enlazar; consultar licencia del contenido original antes de reutilizar.",
        "reuse": "PLD enlaza al recurso original; no copia contenido ni ejercicios sin comprobar sus condiciones.",
        "access": "accesible",
        "quality": "alta",
        "description": "Tutorial oficial para APIs, validación, dependencias, seguridad y testing.",
        "checked": "2026-11-25"
    },
    {
        "id": "res-postgresql-docs",
        "title": "PostgreSQL Documentation",
        "modules": [],
        "lessons": [],
        "author": "PostgreSQL Global Development Group",
        "url": "https://www.postgresql.org/docs/",
        "lang": "en",
        "type": "curso",
        "license": "Solo enlazar; consultar licencia del contenido original antes de reutilizar.",
        "reuse": "PLD enlaza al recurso original; no copia contenido ni ejercicios sin comprobar sus condiciones.",
        "access": "accesible",
        "quality": "alta",
        "description": "Documentación oficial de PostgreSQL: SQL, diseño, índices, transacciones y administración.",
        "checked": "2026-11-25"
    },
    {
        "id": "res-pytest-docs",
        "title": "pytest Documentation",
        "modules": [],
        "lessons": [],
        "author": "pytest contributors",
        "url": "https://docs.pytest.org/",
        "lang": "en",
        "type": "curso",
        "license": "Solo enlazar; consultar licencia del contenido original antes de reutilizar.",
        "reuse": "PLD enlaza al recurso original; no copia contenido ni ejercicios sin comprobar sus condiciones.",
        "access": "accesible",
        "quality": "alta",
        "description": "Documentación oficial de pytest para pruebas, fixtures, parametrización y plugins.",
        "checked": "2026-11-25"
    },
    {
        "id": "res-owasp-top10",
        "title": "OWASP Top 10",
        "modules": [],
        "lessons": [],
        "author": "OWASP",
        "url": "https://owasp.org/www-project-top-ten/",
        "lang": "en",
        "type": "curso",
        "license": "Solo enlazar; consultar licencia del contenido original antes de reutilizar.",
        "reuse": "PLD enlaza al recurso original; no copia contenido ni ejercicios sin comprobar sus condiciones.",
        "access": "accesible",
        "quality": "alta",
        "description": "Lista de riesgos principales de seguridad en aplicaciones web.",
        "checked": "2026-11-25"
    },
    {
        "id": "res-owasp-cheatsheets",
        "title": "OWASP Cheat Sheet Series",
        "modules": [],
        "lessons": [],
        "author": "OWASP",
        "url": "https://cheatsheetseries.owasp.org/",
        "lang": "en",
        "type": "curso",
        "license": "Solo enlazar; consultar licencia del contenido original antes de reutilizar.",
        "reuse": "PLD enlaza al recurso original; no copia contenido ni ejercicios sin comprobar sus condiciones.",
        "access": "accesible",
        "quality": "alta",
        "description": "Guías prácticas de controles de seguridad de aplicaciones.",
        "checked": "2026-11-25"
    },
    {
        "id": "res-pytorch-tutorials",
        "title": "PyTorch Tutorials",
        "modules": [],
        "lessons": [],
        "author": "PyTorch",
        "url": "https://pytorch.org/tutorials/",
        "lang": "en",
        "type": "curso",
        "license": "Solo enlazar; consultar licencia del contenido original antes de reutilizar.",
        "reuse": "PLD enlaza al recurso original; no copia contenido ni ejercicios sin comprobar sus condiciones.",
        "access": "accesible",
        "quality": "alta",
        "description": "Tutoriales oficiales de PyTorch para ML, deep learning y workflows.",
        "checked": "2026-11-25"
    },
    {
        "id": "res-huggingface-learn",
        "title": "Hugging Face Learn",
        "modules": [],
        "lessons": [],
        "author": "Hugging Face",
        "url": "https://huggingface.co/learn",
        "lang": "en",
        "type": "curso",
        "license": "Solo enlazar; consultar licencia del contenido original antes de reutilizar.",
        "reuse": "PLD enlaza al recurso original; no copia contenido ni ejercicios sin comprobar sus condiciones.",
        "access": "accesible",
        "quality": "alta",
        "description": "Cursos sobre Transformers, datasets, NLP y aplicaciones de modelos.",
        "checked": "2026-11-25"
    },
    {
        "id": "res-linux-manpages",
        "title": "Linux man-pages",
        "modules": [],
        "lessons": [],
        "author": "Linux man-pages project",
        "url": "https://man7.org/linux/man-pages/",
        "lang": "en",
        "type": "curso",
        "license": "Solo enlazar; consultar licencia del contenido original antes de reutilizar.",
        "reuse": "PLD enlaza al recurso original; no copia contenido ni ejercicios sin comprobar sus condiciones.",
        "access": "accesible",
        "quality": "alta",
        "description": "Referencia de interfaces de sistema y comandos Linux.",
        "checked": "2026-11-25"
    },
    {
        "id": "res-kubernetes-docs",
        "title": "Kubernetes Documentation",
        "modules": [],
        "lessons": [],
        "author": "Kubernetes project",
        "url": "https://kubernetes.io/docs/",
        "lang": "en",
        "type": "curso",
        "license": "Solo enlazar; consultar licencia del contenido original antes de reutilizar.",
        "reuse": "PLD enlaza al recurso original; no copia contenido ni ejercicios sin comprobar sus condiciones.",
        "access": "accesible",
        "quality": "alta",
        "description": "Documentación oficial de Kubernetes y tutoriales interactivos.",
        "checked": "2026-11-25"
    },
    {
        "id": "res-dev-java",
        "title": "Dev.java Learn",
        "modules": [],
        "lessons": [],
        "author": "Oracle / Java community",
        "url": "https://dev.java/learn/",
        "lang": "en",
        "type": "curso",
        "license": "Solo enlazar; consultar licencia del contenido original antes de reutilizar.",
        "reuse": "PLD enlaza al recurso original; no copia contenido ni ejercicios sin comprobar sus condiciones.",
        "access": "accesible",
        "quality": "alta",
        "description": "Material oficial para aprender Java y sus herramientas.",
        "checked": "2026-11-25"
    },
    {
        "id": "res-spring-guides",
        "title": "Spring Guides",
        "modules": [],
        "lessons": [],
        "author": "Spring",
        "url": "https://spring.io/guides",
        "lang": "en",
        "type": "curso",
        "license": "Solo enlazar; consultar licencia del contenido original antes de reutilizar.",
        "reuse": "PLD enlaza al recurso original; no copia contenido ni ejercicios sin comprobar sus condiciones.",
        "access": "accesible",
        "quality": "alta",
        "description": "Guías oficiales de Spring para aplicaciones Java.",
        "checked": "2026-11-25"
    },
    {
        "id": "res-mdn-http",
        "title": "MDN HTTP",
        "modules": [],
        "lessons": [],
        "author": "Mozilla contributors",
        "url": "https://developer.mozilla.org/en-US/docs/Web/HTTP",
        "lang": "en",
        "type": "curso",
        "license": "Solo enlazar; consultar licencia del contenido original antes de reutilizar.",
        "reuse": "PLD enlaza al recurso original; no copia contenido ni ejercicios sin comprobar sus condiciones.",
        "access": "accesible",
        "quality": "alta",
        "description": "Referencia didáctica de HTTP, métodos, códigos, headers, caching y seguridad.",
        "checked": "2026-11-25"
    },
    {
        "id": "res-mit-algorithms",
        "title": "MIT Introduction to Algorithms",
        "modules": [],
        "lessons": [],
        "author": "MIT OpenCourseWare",
        "url": "https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/",
        "lang": "en",
        "type": "curso",
        "license": "Solo enlazar; consultar licencia del contenido original antes de reutilizar.",
        "reuse": "PLD enlaza al recurso original; no copia contenido ni ejercicios sin comprobar sus condiciones.",
        "access": "accesible",
        "quality": "alta",
        "description": "Curso universitario de algoritmos, estructuras de datos, análisis y resolución de problemas.",
        "checked": "2026-11-25"
    },
    {
        "id": "res-cmu-db",
        "title": "CMU Database Systems",
        "modules": [],
        "lessons": [],
        "author": "Carnegie Mellon University",
        "url": "https://15445.courses.cs.cmu.edu/",
        "lang": "en",
        "type": "curso",
        "license": "Solo enlazar; consultar licencia del contenido original antes de reutilizar.",
        "reuse": "PLD enlaza al recurso original; no copia contenido ni ejercicios sin comprobar sus condiciones.",
        "access": "accesible",
        "quality": "alta",
        "description": "Curso de sistemas de bases de datos: almacenamiento, consultas, índices y arquitectura.",
        "checked": "2026-11-25"
    },
    {
        "id": "res-webdev-roadmap",
        "title": "The Odin Project",
        "modules": [],
        "lessons": [],
        "author": "The Odin Project",
        "url": "https://www.theodinproject.com/",
        "lang": "en",
        "type": "curso",
        "license": "Solo enlazar; consultar licencia del contenido original antes de reutilizar.",
        "reuse": "PLD enlaza al recurso original; no copia contenido ni ejercicios sin comprobar sus condiciones.",
        "access": "accesible",
        "quality": "alta",
        "description": "Currículo práctico de desarrollo web por proyectos; complemento, no autoridad primaria.",
        "checked": "2026-11-25"
    },
    {
        "id": "res-freecodecamp",
        "title": "freeCodeCamp",
        "modules": [],
        "lessons": [],
        "author": "freeCodeCamp",
        "url": "https://www.freecodecamp.org/learn/",
        "lang": "en",
        "type": "curso",
        "license": "Solo enlazar; consultar licencia del contenido original antes de reutilizar.",
        "reuse": "PLD enlaza al recurso original; no copia contenido ni ejercicios sin comprobar sus condiciones.",
        "access": "accesible",
        "quality": "alta",
        "description": "Ejercicios prácticos y proyectos para desarrollo web y programación.",
        "checked": "2026-11-25"
    },
    {
        "id": "res-fullstackopen",
        "title": "Full Stack Open",
        "modules": [],
        "lessons": [],
        "author": "University of Helsinki",
        "url": "https://fullstackopen.com/en/",
        "lang": "en",
        "type": "curso",
        "license": "Solo enlazar; consultar licencia del contenido original antes de reutilizar.",
        "reuse": "PLD enlaza al recurso original; no copia contenido ni ejercicios sin comprobar sus condiciones.",
        "access": "accesible",
        "quality": "alta",
        "description": "Curso de desarrollo full-stack moderno, APIs, React, testing, CI/CD y contenedores.",
        "checked": "2026-11-25"
    }
]

ID = re.compile(r"^res-[a-z0-9-]+$")
REQUIRED = (
    "id",
    "title",
    "author",
    "url",
    "lang",
    "type",
    "license",
    "reuse",
    "access",
    "quality",
    "description",
)


def known_modules() -> set[str]:
    curriculum = json.loads((DATA / "curriculum" / "daw-cyl.json").read_text("utf-8"))
    return {m["code"] for m in curriculum["modules"] if m.get("code")}


def known_lessons() -> set[str]:
    found = set()
    for path in (DATA / "courses").glob("*/lessons.json"):
        for module in json.loads(path.read_text("utf-8"))["modules"]:
            found.update(f"{path.parent.name}/{lesson['slug']}" for lesson in module["lessons"])
    return found


def validate(resources: list[dict]) -> list[str]:
    """Problemas del catálogo; vacío si todo está bien."""
    problems = []
    modules, lessons = known_modules(), known_lessons()
    seen: set[str] = set()
    for r in resources:
        rid = r.get("id", "?")
        for field in REQUIRED:
            if not str(r.get(field, "")).strip():
                problems.append(f"{rid}: falta «{field}»")
        if not ID.match(rid):
            problems.append(f"{rid}: id no válido (res-…)")
        if rid in seen:
            problems.append(f"{rid}: id repetido")
        seen.add(rid)
        for field in ("url", "download"):
            if field in r and not str(r[field]).startswith("https://"):
                problems.append(f"{rid}: «{field}» debe ser una URL https")
        if r.get("type") not in TYPES:
            problems.append(f"{rid}: tipo desconocido {r.get('type')}")
        if r.get("access") not in ACCESS:
            problems.append(f"{rid}: acceso desconocido {r.get('access')}")
        if r.get("quality") not in QUALITY:
            problems.append(f"{rid}: calidad desconocida {r.get('quality')}")
        if (
            r.get("access") == "descargable"
            and not r.get("download")
            and r.get("type") != "normativa"
        ):
            problems.append(f"{rid}: descargable sin URL de descarga")
        for code in r.get("modules", []):
            if code not in modules:
                problems.append(f"{rid}: el módulo {code} no está en el currículo")
        for lesson in r.get("lessons", []):
            if lesson not in lessons:
                problems.append(f"{rid}: la lección {lesson} no existe")
    return problems


def build() -> dict:
    problems = validate(RESOURCES)
    if problems:
        sys.exit("Catálogo de recursos no válido:\n" + "\n".join(f"- {p}" for p in problems))
    return {
        "version": 1,
        "checked": CHECKED,
        "notice": "La plataforma solo enlaza estos recursos. Cada uno tiene su autor y su licencia; compruébala antes de reutilizar nada.",
        "types": TYPES,
        "access": ACCESS,
        "resources": [{**r, "checked": r.get("checked", CHECKED)} for r in RESOURCES],
    }


def main() -> None:
    text = json.dumps(build(), ensure_ascii=False, indent=1) + "\n"
    summary = f"{len(RESOURCES)} recursos"
    if "--check" in sys.argv:
        if not OUT.exists() or OUT.read_text("utf-8") != text:
            sys.exit("resources.json no está al día: python scripts/resources/build_resources.py")
        print(f"resources.json al día y válido: {summary}")
        return
    OUT.write_text(text, "utf-8", newline="\n")  # LF también en Windows
    print(f"Escrito {OUT.relative_to(ROOT)}: {summary}")


if __name__ == "__main__":
    main()
