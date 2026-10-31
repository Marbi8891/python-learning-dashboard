# CLAUDE.md

Instrucciones para Claude Code en este repositorio. La descripción del proyecto está en
[`docs/memoria/memoria.md`](docs/memoria/memoria.md) y las pruebas en [`docs/TESTING.md`](docs/TESTING.md).

## Reglas del proyecto

- **Hacer merge a `main` publica la web** (`.github/workflows/pages.yml`). El merge lo hace siempre la
  persona. Nunca `git push` a `main`, `gh pr merge` ni `deploy.ps1`.
- Trabaja en una rama `tipo/descripcion` con cambios pequeños, y revisa `git diff` antes de cada commit.
- No leas ni muestres `.env`, claves ni `backend/.local-secret`. No toques secretos de GitHub
  ni variables de Render.
- No uses servicios ni APIs de pago: solo herramientas gratuitas.
- Nadie edita a mano un JSON generado de `frontend/data/`: se cambia su script y se regenera.
- Una tarea no está terminada hasta que pasan las pruebas de `docs/TESTING.md` que le tocan.
  Prohibido saltar o debilitar un test para que pase.

## Agentes

- `revisor-daw`: revisa el código o unos cambios y devuelve fallos con evidencia.
- `buscador-mejoras`: propone mejoras priorizadas por impacto y esfuerzo. Se lanza con `/mejoras`
  (o `/mejoras accesibilidad` para un área) y guarda el informe en `.claude/informes/`.
- `red-teamer`: auditoría de seguridad con evidencias (estática y, si se autoriza, en un laboratorio local).
- `python-reviewer`: revisión de estilo y buenas prácticas de Python, copiado de Everything Claude Code
  (versión de oct 2026). Sus comprobaciones de `mypy`, `black` y `bandit` no se ejecutan: no están en el proyecto.
- Todos son de solo lectura: lo que propongan se implementa después, en otra rama, si el autor lo elige.
