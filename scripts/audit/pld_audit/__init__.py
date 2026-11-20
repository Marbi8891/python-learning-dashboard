"""Project Auditor de Python Learning Dashboard (docs/AUDITOR.md).

Solo librería estándar. Los módulos son independientes entre sí salvo por `config`:

- `config`: lee y valida project-auditor.toml.
- `checks`: ejecuta las pruebas configuradas y guarda qué pasó (nunca inventa un resultado).
- `findings`: esquema, validación y huella de los hallazgos que devuelven los agentes.
- `registry`: registro de hallazgos entre auditorías (nuevos, cambiados, regresiones, resueltos).
- `report`: informe Markdown y puntuación heurística.
- `plan`: plan de corrección ordenado por prioridad.
- `fix`: clasificación SAFE FIX / APPROVAL REQUIRED y comprobaciones previas a corregir.
"""

SEVERITIES = ("CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO")
PRIORITIES = ("P0", "P1", "P2", "P3")


def severity_rank(severity: str) -> int:
    """0 es la más grave."""
    return SEVERITIES.index(severity)
