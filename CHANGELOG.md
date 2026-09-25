# Changelog

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/). Versionado [SemVer](https://semver.org/lang/es/).

## [Unreleased]

## [0.1.0] - 2026-09-25

### Añadido
- Frontend: estructura HTML base y barra lateral "Ruta de Aprendizaje" con progreso circular y estados de lección.
- Backend: API FastAPI con `/api/health`, `/api/modules` y `/api/lessons/{slug}`; carga de lecciones idempotente.
- CI: lint, formato y tests del backend; despliegue del frontend en GitHub Pages.
