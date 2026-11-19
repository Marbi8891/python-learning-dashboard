"""Correspondencia de cada lección de los cursos de DAW con los RA y CE oficiales (#106).

Fuente de los RA y CE: RD 405/2023 y Orden EDU/1311/2024 de Castilla y León, ya convertidos en
`frontend/data/curriculum/daw-cyl.json`. Los ids son los de ese fichero: `0484-RA3-b`.

Estados (`status`):
- `verified`: un docente lo ha revisado. Exige `reviewed` (quién y cuándo). Hoy no hay ninguno.
- `proposed`: lo propone el proyecto y está pendiente de revisión docente. No es una evaluación.
- `unassigned`: la lección no tiene todavía correspondencia.

El mapa es por lección: cada pregunta hereda los CE de su lección, salvo que el curso le ponga los
suyos (`Q.ce`). Que un alumno practique un CE no quiere decir que lo haya superado: la evaluación de
un CE la hace el profesorado con sus propios instrumentos.

Para cambiar un estado a `verified`, el docente revisa la lección y se edita aquí `reviewed` y
`status`; después se regeneran los cursos con sus scripts.
"""

from __future__ import annotations

from dataclasses import dataclass

STATUSES = ("verified", "proposed", "unassigned")

# De dónde sale cada propuesta
FROM_OBJECTIVES = "Objetivos de la lección: su autor cita estos RA y CE"
FROM_CONTENT = "Propuesta por el contenido de la lección"


@dataclass(frozen=True)
class Mapping:
    ce: tuple[str, ...]
    source: str
    status: str = "proposed"
    reviewed: str | None = None  # «Nombre, AAAA-MM-DD» cuando un docente lo revisa


def ce(module: str, *parts: str) -> tuple[str, ...]:
    """`ce("0484", "RA3 ab", "RA4 e")` → ("0484-RA3-a", "0484-RA3-b", "0484-RA4-e")."""
    ids = []
    for part in parts:
        ra, letters = part.split()
        ids += [f"{module}-{ra}-{letter}" for letter in letters]
    return tuple(ids)


def _p(module: str, *parts: str, source: str = FROM_CONTENT) -> Mapping:
    return Mapping(ce(module, *parts), source)


LESSONS: dict[str, Mapping] = {
    # 0485 Programación (curso en Python)
    "prog-ut1-algoritmos": _p("0485", "RA1 a"),
    "prog-ut2-elementos": _p("0485", "RA1 defghi", "RA5 ab"),
    "prog-ut3-control": _p("0485", "RA3 abcef"),
    "prog-ut3-funciones": _p("0485", "RA2 bf"),
    "prog-ut4-poo": _p("0485", "RA2 acdh", "RA4 a"),
    "prog-ut5-clases": _p("0485", "RA4 abcdefh", "RA2 e"),
    "prog-ut5-modulos-cadenas": _p("0485", "RA2 g", "RA4 i", "RA6 g"),
    "prog-ut6-colecciones": _p("0485", "RA6 acdej"),
    "prog-ut6-herencia-excepciones": _p("0485", "RA7 acdeg", "RA3 dh"),
    "prog-ut7-proyecto": _p("0485", "RA3 e", "RA5 a"),
    "prog-ut8-ficheros-bd": _p("0485", "RA5 cde", "RA6 hi", "RA9 abcd"),
    "prog-ut9-interfaces": _p("0485", "RA5 fgh"),
    # 0485 Programación (curso en Java)
    "java-tipos": _p("0485", "RA1 defgh"),
    "java-strings": _p("0485", "RA2 cd"),
    "java-condicionales": _p("0485", "RA3 a"),
    "java-bucles-arrays": _p("0485", "RA3 b", "RA6 a"),
    "java-clases": _p("0485", "RA4 abcde", "RA2 h"),
    "java-encapsulacion": _p("0485", "RA4 fh", "RA2 e"),
    "java-herencia": _p("0485", "RA7 acdeg"),
    "java-abstractas-interfaces": _p("0485", "RA7 bi"),
    "java-colecciones": _p("0485", "RA6 bcde"),
    "java-excepciones": _p("0485", "RA3 dh"),
    # 0612 Desarrollo web en entorno cliente
    "js-variables": _p("0612", "RA2 b"),
    "js-coercion": _p("0612", "RA2 de"),
    "js-funciones": _p("0612", "RA4 ab"),
    "js-ambito": _p("0612", "RA2 c"),
    "js-arrays": _p("0612", "RA4 cde"),
    "js-objetos": _p("0612", "RA4 fghi"),
    "js-dom": _p("0612", "RA6 abcd", "RA3 d"),
    "js-eventos": _p("0612", "RA5 bcd", "RA6 e"),
    "js-asincronia": _p("0612", "RA7 ab"),
    "js-fetch-json": _p("0612", "RA7 cef"),
    # 0484 Bases de datos
    "bd-tipos-y-modelos": _p("0484", "RA1 bcghj", source=FROM_OBJECTIVES),
    "bd-ficheros-rgpd-sgbd": _p("0484", "RA1 adefi", source=FROM_OBJECTIVES),
    "sql-modelo-relacional": _p("0484", "RA6 bcdefg", source=FROM_OBJECTIVES),
    "sql-crear-tablas": _p("0484", "RA2 bcde", source=FROM_OBJECTIVES),
    "bd-null-indices-dcl": _p("0484", "RA2 cfgh", source=FROM_OBJECTIVES),
    "sql-select": _p("0484", "RA3 ab", source=FROM_OBJECTIVES),
    "sql-where": _p("0484", "RA3 b", source=FROM_OBJECTIVES),
    "sql-agregados": _p("0484", "RA3 ef", source=FROM_OBJECTIVES),
    "sql-group-by": _p("0484", "RA3 e", source=FROM_OBJECTIVES),
    "sql-inner-join": _p("0484", "RA3 ce", source=FROM_OBJECTIVES),
    "sql-left-join-subconsultas": _p("0484", "RA3 df", source=FROM_OBJECTIVES),
    "bd-conjuntos-y-optimizacion": _p("0484", "RA3 dfgh", source=FROM_OBJECTIVES),
    "sql-modificar-datos": _p("0484", "RA4 abch", source=FROM_OBJECTIVES),
    "sql-transacciones-vistas": _p("0484", "RA4 ef", "RA2 f", "RA3 h", source=FROM_OBJECTIVES),
    # 0373 Lenguajes de marcas y sistemas de gestión de información
    "mar-xml-bien-formado": _p("0373", "RA1 abcdefghi", source=FROM_OBJECTIVES),
    "mar-html-css": _p("0373", "RA2 abcdefgh", source=FROM_OBJECTIVES),
    "mar-dtd-xsd": _p("0373", "RA4 abcdefg", source=FROM_OBJECTIVES),
    "mar-xpath-xslt": _p("0373", "RA6 ehi", "RA5 cdefg", source=FROM_OBJECTIVES),
    "mar-json-intercambio": _p("0373", "RA6 abcdfg", "RA5 g", source=FROM_OBJECTIVES),
    "mar-sindicacion-erp": _p("0373", "RA2 ij", "RA7 abcdefghi", source=FROM_OBJECTIVES),
    # 0487 Entornos de desarrollo
    "ent-lenguajes-y-programas": _p("0487", "RA1 ef", source=FROM_OBJECTIVES),
    "ent-compilar-e-interpretar": _p("0487", "RA1 cde", source=FROM_OBJECTIVES),
    "ent-paradigmas": _p("0487", "RA1 e", "RA5 a", source=FROM_OBJECTIVES),
    "ent-fases-y-agiles": _p("0487", "RA1 bg", source=FROM_OBJECTIVES),
}

UNASSIGNED = Mapping((), "Sin correspondencia todavía", status="unassigned")


def ra_of(ce_id: str) -> str:
    """`0484-RA3-b` → `0484-RA3`."""
    return ce_id.rsplit("-", 1)[0]


def for_lesson(slug: str) -> Mapping:
    return LESSONS.get(slug, UNASSIGNED)


def check(mapping: Mapping, module: str, known: set[str], where: str) -> None:
    """Falla si el mapa no es coherente: estado válido, CE que existen y del módulo del curso."""
    assert mapping.status in STATUSES, f"{where}: estado desconocido {mapping.status!r}"
    if mapping.status == "verified":
        assert mapping.reviewed, f"{where}: «verified» necesita quién y cuándo lo revisó"
    else:
        assert mapping.reviewed is None, f"{where}: solo «verified» lleva revisión"
    assert (mapping.status == "unassigned") == (not mapping.ce), (
        f"{where}: «unassigned» va sin CE y los demás estados con al menos uno"
    )
    assert len(set(mapping.ce)) == len(mapping.ce), f"{where}: CE repetido"
    for ce_id in mapping.ce:
        assert ce_id in known, f"{where}: {ce_id} no existe en el currículo oficial"
        assert ce_id.startswith(f"{module}-"), f"{where}: {ce_id} no es del módulo {module}"
