# ADR-0001 — Arquitectura: frontend en GitHub Pages + API aparte

- **Estado:** Aceptada
- **Fecha:** 2026-09-25

## Contexto

La web necesita backend para guardar progreso, gestionar usuarios, servir lecciones y corregir ejercicios. GitHub Pages solo sirve archivos estáticos.

## Opciones

| Opción | A favor | En contra |
|---|---|---|
| A. Pages (frontend) + API aparte | Frontend gratis y siempre disponible; separación clara | CORS; dos despliegues |
| B. Todo en un servidor | Un despliegue, sin CORS | Si el servidor duerme o cae, cae todo |
| C. Solo frontend | Mínima complejidad | No cumple los requisitos de usuarios y progreso |

## Decisión

**A.** Un solo repositorio (monorepo):

- `frontend/`: HTML, CSS y JS sin framework. Se publica en Pages con `.github/workflows/pages.yml`.
- `backend/`: FastAPI + SQLAlchemy 2. SQLite en local; PostgreSQL en producción (`DATABASE_URL`).

## Consecuencias y fases

1. **Fase 1 (hecha):** esqueleto de la API y lecciones servidas por API (`/api/modules`, `/api/lessons/{slug}`), con tests y CI.
2. **Fase 2:** usuarios y login (hash de contraseñas con Argon2 o bcrypt, JWT de corta duración, rate limiting en el login).
3. **Fase 3:** progreso por usuario (`/api/progress`).
4. **Fase 4 — corrección de ejercicios:**
   - Primero: los tests se ejecutan en el navegador con Pyodide y el backend solo registra el resultado.
   - Ejecutar código de usuarios en el servidor exige un sandbox aislado (contenedor sin red, límites de CPU, memoria y tiempo). Solo se hará si hace falta de verdad.

**Pendiente de decidir (VERIFY):** dónde alojar el backend (Render u Oracle Cloud Free Tier). El disco de muchos planes gratuitos es efímero, así que SQLite no sirve en producción: hará falta PostgreSQL.
