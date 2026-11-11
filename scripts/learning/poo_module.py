# ruff: noqa: E501
"""Módulo de Programación orientada a objetos (POO): 10 unidades del núcleo por conceptos.

Cada unidad es un concepto de `concepts.py` (área `poo`) con campos opcionales de unidad, que los
demás conceptos no tienen. Así el dominio, los errores típicos, el repaso espaciado y las
recomendaciones del motor adaptativo funcionan igual que en el resto del temario.

- `MODULE`: índice de las 10 unidades (la web lo enseña en `#/poo`). Una unidad aparece como
  disponible cuando existe su concepto.
- `UNITS`: campos de unidad de cada concepto (objetivos, lecciones con ejemplos y mini-quiz,
  ejercicios guiados y autónomos, autoevaluación, resumen, criterios de superación y currículo).
- `EXERCISES`: ejercicios nuevos de las unidades (se añaden a los de `exercises.py`).

La salida de cada ejemplo no se escribe a mano: build_learning.py la obtiene ejecutándolo.
Las correspondencias con el currículo (`curriculum`) son propuestas de la plataforma
(`proposed`) hasta que una persona las valide; nunca se muestran como oficiales.
"""

import poo_u1
import poo_u2
import poo_u3
import poo_u4
import poo_u5
import poo_u6
from exercises import E as BASE_EXERCISES
from poo_common import REVIEWED, SOURCE, proposed, tag_bank

__all__ = ["REVIEWED", "SOURCE", "proposed"]


MODULE = {
    "id": "poo",
    "title": "Programación orientada a objetos con Python",
    "summary": "De la primera clase a una aplicación completa: objetos, encapsulación, herencia, polimorfismo, composición y diseño.",
    "course": "0485",
    "units": [
        {
            "number": 1,
            "id": "poo-fundamentos",
            "title": "Fundamentos de la programación orientada a objetos",
        },
        {"number": 2, "id": "poo", "title": "Creación de clases y objetos"},
        {"number": 3, "id": "poo-atributos-metodos", "title": "Atributos y métodos"},
        {"number": 4, "id": "poo-encapsulacion", "title": "Encapsulación y propiedades"},
        {"number": 5, "id": "poo-herencia", "title": "Herencia"},
        {"number": 6, "id": "poo-polimorfismo", "title": "Polimorfismo"},
        {"number": 7, "id": "poo-composicion", "title": "Composición y relaciones entre objetos"},
        {"number": 8, "id": "poo-metodos-especiales", "title": "Métodos especiales de Python"},
        {"number": 9, "id": "poo-diseno", "title": "Diseño y buenas prácticas"},
        {"number": 10, "id": "poo-proyecto", "title": "Proyecto final: gestión de una biblioteca"},
    ],
}

# Apartados que debe tener cada unidad (los comprueba build_learning.py)
UNIT_FIELDS = (
    "objectives",
    "prior",
    "key",
    "sections",
    "guided",
    "autonomous",
    "selfcheck",
    "recap",
    "pass",
    "curriculum",
    "practices",
    "references",
    "bank",
)

UNITS = {
    "poo-fundamentos": poo_u1.UNIT,
    "poo": poo_u2.UNIT,
    "poo-atributos-metodos": poo_u3.UNIT,
    "poo-encapsulacion": poo_u4.UNIT,
    "poo-herencia": poo_u5.UNIT,
    "poo-polimorfismo": poo_u6.UNIT,
}

EXERCISES = [
    *poo_u1.EXERCISES,
    *poo_u3.EXERCISES,
    *poo_u4.EXERCISES,
    *poo_u5.EXERCISES,
    *poo_u6.EXERCISES,
    *poo_u2.EXERCISES,  # la Unidad 2 va al final: así no cambia el orden de learning.json
]

# Preguntas tipo test que ya existían y pasan al banco evaluable de su unidad (mismo id)
BANK_TAGS = {
    **poo_u1.BANK_TAGS,
    **poo_u2.BANK_TAGS,
    **poo_u3.BANK_TAGS,
    **poo_u4.BANK_TAGS,
    **poo_u5.BANK_TAGS,
    **poo_u6.BANK_TAGS,
}
tag_bank([*BASE_EXERCISES, *EXERCISES], BANK_TAGS)

# Errores típicos nuevos de cada unidad (la Unidad 2 los añade a los del concepto `poo`)
UNIT_ERRORS = {
    "poo-fundamentos": poo_u1.ERRORS,
    "poo": poo_u2.ERRORS,
    "poo-atributos-metodos": poo_u3.ERRORS,
    "poo-encapsulacion": poo_u4.ERRORS,
    "poo-herencia": poo_u5.ERRORS,
    "poo-polimorfismo": poo_u6.ERRORS,
}

# Teoría y presentación de la Unidad 2 (sustituyen a las del concepto `poo`; el id no cambia)
UNIT_OVERRIDES = {"poo": poo_u2.OVERRIDES}

# Conceptos nuevos de las unidades (concepts.py los coloca alrededor de `poo`, en el orden del módulo)
CONCEPTS_BEFORE_POO = [poo_u1.CONCEPT]
CONCEPTS_AFTER_POO = [poo_u3.CONCEPT, poo_u4.CONCEPT, poo_u5.CONCEPT, poo_u6.CONCEPT]
