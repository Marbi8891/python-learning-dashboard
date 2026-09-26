# Changelog

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/). Versionado [SemVer](https://semver.org/lang/es/).

## [Unreleased]

## [0.6.0] - 2026-09-26

### Añadido
- Portada con «Continuar donde lo dejaste», resumen del progreso y tarjetas por módulo.
- Guía en cada lección (Aprende → Practica → Comprueba) con un botón «Siguiente paso».
- Errores de Python explicados en español, con botón «Ir a la línea» (22 casos probados).
- Tema claro, oscuro o automático y tres tamaños de letra, recordados en el navegador.
- Tests: explicación de errores (backend); portada, guía, errores, apariencia, consola al lado y auditoría WCAG en los dos temas (e2e).

### Cambiado
- En pantallas de 1280 px o más, la consola queda fija al lado de la lección.
- La barra lateral agrupa el progreso y los XP en una sola tarjeta.
- Los colores salen de variables de tema (ADR-0006).

## [0.5.0] - 2026-09-26

### Añadido
- Mini-quiz por lección (45 preguntas), con explicación de cada respuesta y mejor nota guardada.
- Reto extra por lección (★ a ★★★), con plantilla, pista y tests automáticos.
- XP calculados a partir del progreso, 7 niveles, racha de días, 13 logros con vitrina y confeti (respeta la reducción de movimiento).
- API: las lecciones incluyen `quiz` y `challenge` (migración 3, probada en PostgreSQL con datos existentes).
- Tests: estructura de los quizzes y plantillas de reto que no pasan (backend); flujo completo del juego y accesibilidad (e2e).

### Corregido
- El atributo `hidden` no ocultaba los botones con clase `.btn`.

## [0.4.0] - 2026-09-26

### Añadido
- Versión de escritorio: `Iniciar-Dashboard.bat` (doble clic en Windows) y `scripts/run_local.py`. Un solo proceso sirve la web y la API en `127.0.0.1`, con puerto libre automático, base de datos y clave propias persistentes, y apertura del navegador.
- Modo `SERVE_FRONTEND` en el backend: sirve el frontend con `config.js` de mismo origen y tipos MIME fijados (evita el fallo del registro de Windows que marca `.js` como `text/plain`).
- Guía `docs/EJECUTAR-EN-WINDOWS.md` con solución de problemas (SmartScreen y Control de aplicaciones).

## [0.3.0] - 2026-09-26

### Añadido
- Consola interactiva con Python 3.14 (Pyodide) en un Web Worker de tipo módulo: `input()` desde «Entrada», errores con la línea del alumno y corte de bucles infinitos a los 10 s.
- Ejercicios corregibles en las 15 lecciones: plantilla, casos de test y resultado en español. Superarlos completa la lección.
- Asistente por lección: preguntas frecuentes, pista y «Siguiente tema».
- Cuenta en el frontend: registro, login, sesión persistente, sincronización del progreso, recuperación de contraseña, descarga de datos y borrado de cuenta.
- Backend: recuperación de contraseña (token de un solo uso, 30 min, email por SMTP en segundo plano), invalidación de sesiones al cambiar la contraseña, exportación y borrado de datos (RGPD), consentimiento de privacidad registrado.
- Política de privacidad (con campos pendientes de completar).
- Menú lateral deslizante en móvil y orden recomendado de lecciones.
- Tests end-to-end con Playwright contra el backend real, con auditoría WCAG 2.1 AA (axe-core).
- Cobertura del 100 % en el backend, obligatoria en CI. Migraciones probadas en PostgreSQL con datos existentes.
- Despliegue: `render.yaml` (Render Blueprint), `docker-compose.yml` y `docs/DEPLOY.md`.

### Cambiado
- Fuentes y highlight.js alojados en el propio sitio (sin Google Fonts ni CDN de terceros).
- Contrastes corregidos para cumplir WCAG AA (texto tenue, botones azules y comentarios de código).

### Corregido
- Anillo de progreso descolocado por un selector CSS roto.
- La migración 2 fallaba en PostgreSQL con datos existentes (valor por defecto booleano).

## [0.2.0] - 2026-09-25

### Añadido (backend)
- Usuarios: registro, login (OAuth2 + JWT) y `/api/users/me`. Contraseñas con Argon2 y límite de intentos por IP (ADR-0003).
- Progreso por usuario: `GET/PUT/DELETE /api/progress` e importación del progreso del navegador.
- Intentos de ejercicios: `POST/GET /api/lessons/{slug}/attempts`; un intento superado completa la lección.
- Migraciones con Alembic y comprobación en CI contra PostgreSQL 16.
- Dockerfile del backend (usuario sin privilegios, migración y carga de lecciones al arrancar).

### Añadido (contenido)
- Contenido de las 15 lecciones (teoría propia, ejemplo ejecutable, ejercicio y fuentes enlazadas) en `frontend/data/lessons.json`, fuente única compartida por frontend y backend (ADR-0002).
- Frontend: la barra lateral se genera a partir de los datos; navegación por URL (`#/leccion/<slug>`); pestañas accesibles; resaltado de sintaxis; botones "Copiar al portapapeles" y "Abrir en PyCharm" (copia + guía + descarga del `.py`); progreso guardado en el navegador.
- Backend: campo `sources` en las lecciones y test que exige contenido y fuentes en todas.

### Eliminado
- `backend/data/lessons.json` (sustituido por el archivo compartido).

## [0.1.0] - 2026-09-25

### Añadido
- Frontend: estructura HTML base y barra lateral "Ruta de Aprendizaje" con progreso circular y estados de lección.
- Backend: API FastAPI con `/api/health`, `/api/modules` y `/api/lessons/{slug}`; carga de lecciones idempotente.
- CI: lint, formato y tests del backend; despliegue del frontend en GitHub Pages.
