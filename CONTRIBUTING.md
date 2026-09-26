# Cómo contribuir

## Flujo de trabajo

1. Crea una rama desde `main`: `feat/panel-contenido`, `fix/progreso-circular`, etc.
2. Haz commits pequeños con [Conventional Commits](https://www.conventionalcommits.org/es/v1.0.0/):
   `feat: ...`, `fix: ...`, `docs: ...`, `refactor: ...`, `test: ...`, `chore: ...`
3. Abre un pull request. La CI (lint + tests) debe estar en verde antes de fusionar.

## Antes de subir cambios

```bash
cd backend
ruff check . ../e2e ../scripts && ruff format --check . ../e2e ../scripts
python -m pytest -q --cov=app --cov-fail-under=100
cd ..
npm run test:e2e        # la primera vez: npm ci && npx playwright install chromium
```

## Añadir o cambiar una lección

Edita `frontend/data/lessons.json`. El bloque `course` es la ficha del curso y cada módulo lleva un `summary`. Cada lección necesita `theory`, `example_code`, `exercise`, `starter`, `checks`, `assistant`, `sources`, `quiz` (3 preguntas de 4 opciones, con `explain`) y `challenge`. `tests/test_content.py` comprueba que el ejemplo se ejecuta y que la plantilla **no** supera los tests. Comprueba tú mismo que tu solución los supera, pero **no la subas al repositorio** (ver ADR-0004).

## Criterios de calidad

- Python: PEP 8 (comprobado con ruff), nombres descriptivos, sin configuración escrita en el código.
- Base de datos: sin consultas N+1.
- Frontend: accesible con teclado y contraste WCAG AA (la auditoría con axe-core está en los tests e2e), usable a 360 px de ancho.
- Decisiones de arquitectura: se documentan como ADR en `docs/adr/`.
