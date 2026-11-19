"""Piezas comunes de las unidades del módulo de POO (poo_module.py y poo_u*.py)."""

REVIEWED = "2026-11-11"
SOURCE = "rd-405-2023#anexo-I"  # texto oficial ya extraído en frontend/data/curriculum/daw-cyl.json

# Catálogo cerrado de fuentes de la bibliografía. build_learning.py rechaza cualquier otra.
# `kind`: "python" (documentación oficial de Python, respalda conceptos) o "norma" (normativa de
# FP: solo sirve para el currículo y nunca respalda un concepto de Python).
SOURCES = {
    "py-tutorial-classes": {
        "title": "Tutorial de Python: Clases",
        "url": "https://docs.python.org/es/3/tutorial/classes.html",
        "kind": "python",
    },
    "py-faq-programming": {
        "title": "Preguntas frecuentes de programación de Python",
        "url": "https://docs.python.org/es/3/faq/programming.html",
        "kind": "python",
    },
    "py-abc": {
        "title": "abc: clases de base abstracta (biblioteca estándar de Python)",
        "url": "https://docs.python.org/es/3/library/abc.html",
        "kind": "python",
    },
    "py-dataclasses": {
        "title": "dataclasses: clases de datos (biblioteca estándar de Python)",
        "url": "https://docs.python.org/es/3/library/dataclasses.html",
        "kind": "python",
    },
    "rd-405-2023": {
        "title": "Real Decreto 405/2023, de 29 de mayo",
        "url": "https://www.boe.es/eli/es/rd/2023/05/29/405",
        "kind": "norma",
    },
    "rd-659-2023": {
        "title": "Real Decreto 659/2023, de 18 de julio",
        "url": "https://www.boe.es/eli/es/rd/2023/07/18/659",
        "kind": "norma",
    },
}

REFERENCE_STATUS = {"pending", "verified"}

# Banco de preguntas evaluables: 15 por unidad, con este reparto por tipo y por nivel
BANK_SIZE = 15
BANK_QTYPES = {"teoria": 3, "codigo": 3, "prediccion": 3, "error": 2, "solucion": 2, "diseno": 2}
BANK_LEVELS = {1: 5, 2: 6, 3: 4}  # básico, intermedio, avanzado


def proposed(ce: str, note: str) -> dict:
    """Correspondencia propuesta por la plataforma: falta que la valide una persona."""
    return {
        "ce": ce,
        "status": "proposed",
        "source": SOURCE,
        "reviewed": REVIEWED,
        "by": "plataforma",
        "note": note,
    }


def ref(source: str, section: str, supports: list[str], status="pending", by=None, date=None):
    """Referencia bibliográfica de una unidad.

    Nace `pending` («pendiente de comprobación»): solo pasa a `verified` cuando una persona abre la
    fuente, comprueba el apartado y anota quién (`by`) y cuándo (`date`).
    """
    reference = {"source": source, "section": section, "supports": supports, "status": status}
    if by or date:
        reference.update(by=by, date=date)
    return reference


def practice(text: str, why: str) -> dict:
    """Una buena práctica de la unidad y su porqué."""
    return {"text": text, "why": why}


def tag_bank(exercises: list[dict], tags: dict) -> None:
    """Pasa al banco preguntas tipo test que ya existían, sin cambiar su id ni su enunciado.

    `tags`: {id: (qtype, level, [por qué es incorrecta cada opción no correcta, en orden])}.
    """
    found = {e["id"]: e for e in exercises if e["id"] in tags}
    missing = set(tags) - set(found)
    if missing:
        raise KeyError(f"preguntas del banco que no existen: {sorted(missing)}")
    for eid, (qtype, level, whys) in tags.items():
        exercise = found[eid]
        wrong = [o for i, o in enumerate(exercise["options"]) if i != exercise["answer"]]
        if len(whys) != len(wrong):
            raise ValueError(f"{eid}: hace falta un porqué por cada opción incorrecta")
        for option, why in zip(wrong, whys, strict=True):
            option["why"] = why
        exercise.update(level=level, bank=True, qtype=qtype)
