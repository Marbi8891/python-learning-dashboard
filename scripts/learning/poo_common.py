"""Piezas comunes de las unidades del módulo de POO (poo_module.py y poo_u*.py)."""

REVIEWED = "2026-11-11"
SOURCE = "rd-405-2023#anexo-I"  # texto oficial ya extraído en frontend/data/curriculum/daw-cyl.json


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
