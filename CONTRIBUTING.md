# Cómo contribuir

## Flujo de trabajo

1. Crea una rama desde `main`: `feat/panel-contenido`, `fix/progreso-circular`, etc.
2. Haz commits pequeños con [Conventional Commits](https://www.conventionalcommits.org/es/v1.0.0/):
   `feat: ...`, `fix: ...`, `docs: ...`, `refactor: ...`, `test: ...`, `chore: ...`
3. Abre un pull request. La CI (lint + tests) debe estar en verde antes de fusionar.

## Antes de subir cambios del backend

```bash
cd backend
ruff check . && ruff format --check . && python -m pytest -q
```

## Criterios de calidad

- Python: PEP 8 (comprobado con ruff), nombres descriptivos, sin configuración escrita en el código.
- Base de datos: sin consultas N+1.
- Frontend: accesible con teclado, contraste WCAG AA, usable a 360 px de ancho.
- Decisiones de arquitectura: se documentan como ADR en `docs/adr/`.
