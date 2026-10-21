## Qué cambia

<!-- Resumen en 1-3 líneas -->

## Por qué

<!-- Problema o issue que resuelve (Closes #...) -->

## Cómo se ha verificado

- [ ] `ruff check .` y `ruff format --check .` sin errores
- [ ] `python -m pytest -q` en verde
- [ ] `npm run test:unit` y `python scripts/check_site.py` en verde (si toca el frontend)
- [ ] `python scripts/learning/build_learning.py --check` (si toca `scripts/learning/` o `frontend/py/runner.py`)
- [ ] `npm run test:e2e` (si toca vistas, HTML o CSS); ver `docs/TESTING.md` §3
- [ ] Probado en el navegador (si toca el frontend), también a ancho de móvil
- [ ] Navegable con teclado y contraste correcto (WCAG)
