# Python Learning Dashboard

[![CI](https://github.com/Marbi8891/python-learning-dashboard/actions/workflows/ci.yml/badge.svg)](https://github.com/Marbi8891/python-learning-dashboard/actions/workflows/ci.yml)
[![Deploy frontend](https://github.com/Marbi8891/python-learning-dashboard/actions/workflows/pages.yml/badge.svg)](https://github.com/Marbi8891/python-learning-dashboard/actions/workflows/pages.yml)
![Cobertura backend](https://img.shields.io/badge/cobertura%20backend-100%25-brightgreen)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Herramienta para **aprender Python entendiendo lo que haces** y **preparar la parte de programación de DAW**. Funciona por conceptos: teoría con ejemplos, ejercicios corregidos al momento, explicación de cada error, repaso espaciado y simulacros. Incluye además el curso del examen PCAP y los demás módulos de DAW.

**Demo:** https://marbi8891.github.io/python-learning-dashboard/

## Núcleo educativo (ADR-0031)

El ciclo es: concepto → explicación → ejemplo → intento → error o acierto → explicación → nuevo intento → repaso → dominio.

- **Aprender:** responde a «¿qué estudio ahora?» con un plan corto en este orden: repasos pendientes, errores recientes, conceptos importantes para DAW sin dominar y contenido nuevo (solo si la base está firme; si no, dice «Necesitas reforzar X antes de pasar a Y»). Incluye la prueba de nivel y la ruta personal.
- **Teoría:** 22 conceptos en orden (fundamentos, programación, lógica). Cada uno tiene explicación, ejemplo línea a línea con su salida real, cuándo usarlo, errores habituales, relación con otros conceptos y ejercicios.
- **Practicar:**
  - seis tipos de ejercicio: pregunta, ¿qué muestra?, completar, ordenar líneas o pseudocódigo, encontrar el error y escribir el programa (corregido con tests en Pyodide);
  - **cada fallo explica el error típico** (qué falla, por qué, cómo pensarlo y cómo evitarlo) y vuelve al final con un ejercicio parecido;
  - «Mis errores» permite practicar un error concreto.
- **DAW:** competencias (Fundamentos, Programación, Lógica) con su dominio, actividades de examen (cronometrados, problemas completos, lectura de código, detectar errores, del enunciado al algoritmo) y **simulacros** sin corrección hasta el final. Enlaza el temario por UT y los demás módulos.
- **Progreso:** dominio, estado y próximo repaso de cada concepto, errores frecuentes (pendientes o corregidos), actividad y simulacros.
- **Contenido verificado:** 128 ejercicios en `frontend/data/learning.json`, generados por `scripts/learning/`. El script ejecuta cada salida, cada corrección y cada solución, y comprueba que las soluciones equivocadas típicas fallan en el test que delata su error.
- **Mismo progreso en la web y en la app:** `/api/course-state/learn`.

## Curso PCAP y demás funcionalidades

- **Temario del PCAP:** un módulo de bases (nivel PCEP) y uno por cada bloque oficial del examen (Módulos y paquetes, Excepciones, Strings, POO, Miscelánea), más un extra «Después del PCAP». 27 lecciones.
- **Zona de examen:** simulacro de 40 preguntas en 65 minutos con el reparto oficial del temario, práctica por bloque con corrección al momento, 48 fichas de repaso y panel de preparación por bloque. 126 preguntas originales, en español o en inglés (como el examen), cada una con una comprobación en Python que demuestra su respuesta.
- **Teoría y ejemplos:** explicaciones propias, código con resaltado de sintaxis y botones «Copiar», «Probar en la consola» y «Abrir en PyCharm» (copia el código, guía los pasos y permite descargar el `.py`).
- **Consola interactiva:** Python 3.14 real ([Pyodide](https://pyodide.org)) en un Web Worker. Admite `input()`, muestra los errores con la línea exacta y corta los bucles infinitos a los 10 s.
- **Ejercicios corregidos:** cada lección tiene plantilla y tests. Superarlos completa la lección.
- **Asistente:** preguntas frecuentes, pista del ejercicio y «Siguiente tema», adaptados a cada lección.
- **Mini-quiz:** 3 preguntas por lección (81 en total) que explican por qué cada respuesta es correcta o no.
- **Retos extra:** uno por lección, de ★ a ★★★ (FizzBuzz, carrito de la compra, renombrador de fotos…), con tests automáticos.
- **XP, niveles y racha:** 7 niveles de «Novato/a» a «Leyenda de Python», bonus por acertar a la primera, XP por la preparación del examen, 20 logros (7 de ellos del PCAP) con su vitrina y confeti (desactivado si el sistema pide reducir el movimiento).
- **Estudio guiado:** repaso espaciado de preguntas y fichas, plan semanal a partir de la fecha del examen y, en cada fallo, enlace a la lección que lo explica.
- **Cuenta (opcional):** registro, login, progreso y preparación del examen sincronizados entre dispositivos, recuperación de contraseña y RGPD (descargar los datos y borrar la cuenta).
- **Certificado de finalización** imprimible (no oficial) y **app instalable** que funciona sin conexión.
- **Estética de academia:** diseño editorial (tinta, marfil y dorado, titulares en serif), portada con la ficha del curso y temario, y página «Mi aprendizaje» con cifras, actividad, logros e historial.
- **Pensado para el alumno:** portada con «Continuar donde lo dejaste», guía Aprende → Practica → Comprueba en cada lección, consola al lado en pantallas anchas y errores de Python explicados en español.
- **Tema y letra:** claro, oscuro o automático, y tres tamaños de letra.
- **Accesible y adaptable:** WCAG 2.1 AA verificado automáticamente en los dos temas, navegable con teclado y con menú móvil.

## Usarlo en tu PC (Windows)

Doble clic en **`Iniciar-Dashboard.bat`**. La primera vez instala lo necesario y después abre la app en el navegador, solo accesible desde tu ordenador. Requiere Python 3.11 o superior. Guía y solución de problemas: [docs/EJECUTAR-EN-WINDOWS.md](docs/EJECUTAR-EN-WINDOWS.md).

En Linux o macOS: `pip install -r backend/requirements.txt && python scripts/run_local.py`.

## Arquitectura

| Parte | Tecnología | Despliegue |
|---|---|---|
| `frontend/` | HTML, CSS y JavaScript (módulos ES, sin framework), Pyodide | GitHub Pages |
| `backend/` | FastAPI, SQLAlchemy 2, Alembic, PostgreSQL/SQLite, JWT + Argon2 | Docker: Render, Oracle Cloud… |
| `backend/app/a2a/` | Agentes A2A 1.0 con el SDK oficial `a2a-sdk` (Python Tutor), en la misma app FastAPI | Con el backend (desactivado por defecto) |

Decisiones documentadas:
- [ADR-0001 Arquitectura](docs/adr/0001-arquitectura.md)
- [ADR-0002 Contenido](docs/adr/0002-contenido-de-lecciones.md)
- [ADR-0003 Autenticación y ejercicios](docs/adr/0003-autenticacion-y-ejercicios.md)
- [ADR-0004 Consola, corrección y privacidad](docs/adr/0004-consola-ejercicios-y-privacidad.md)
- [ADR-0005 Gamificación](docs/adr/0005-gamificacion.md)
- [ADR-0006 Experiencia del alumno](docs/adr/0006-experiencia-del-alumno.md)
- [ADR-0007 Estética editorial](docs/adr/0007-estetica-editorial.md)
- [ADR-0008 Backend en Render y base de datos en Neon](docs/adr/0008-backend-render-neon.md)
- [ADR-0009 Enfoque en el examen PCAP](docs/adr/0009-enfoque-pcap.md)
- [ADR-0010 Estudio guiado, sincronización y PWA](docs/adr/0010-estudio-guiado-y-pwa.md)
- [ADR-0031 Núcleo educativo por conceptos](docs/adr/0031-nucleo-educativo-por-conceptos.md) (las ADR-0011 a 0030 están en `docs/adr/`)
- [ADR-0034 Agentes A2A junto a la API REST](docs/adr/0034-agentes-a2a.md) · guía: [docs/a2a.md](docs/a2a.md)

```
├── frontend/
│   ├── data/learning.json  Núcleo educativo: conceptos, errores típicos y ejercicios (generado por scripts/learning)
│   ├── data/lessons.json   Contenido: teoría, ejemplos, ejercicios, quiz, retos y asistente (fuente única)
│   ├── data/pcap.json      Banco de preguntas del examen, fichas y formato oficial del PCAP
│   ├── py/runner.py        Motor que ejecuta y corrige el código (navegador y CI)
│   ├── js/learn/           núcleo educativo: lógica pura (dominio, repaso, recomendación, sesiones) y vistas
│   ├── js/                 app, consola, Worker de Pyodide, quiz, juego, asistente, cuenta, API
│   ├── css/  fonts/  vendor/
│   ├── config.js           URL de la API (vacía = modo sin cuenta)
│   └── privacidad.html
├── backend/
│   ├── app/                API: config, seguridad, modelos, routers, email
│   ├── app/services/       lógica reutilizable fuera de los routers (contexto del alumno)
│   ├── app/a2a/            agentes A2A: cards, agents, executors, providers y server.py
│   ├── migrations/         Alembic
│   ├── tests/              pytest (100 % de cobertura)
│   └── Dockerfile
├── e2e/                    Playwright: app completa + auditoría WCAG
├── docs/                   ADR y guía de despliegue
├── render.yaml             Blueprint de Render (backend + PostgreSQL)
├── docker-compose.yml      Todo en local con PostgreSQL
├── deploy.ps1              Publicación en GitHub Pages (Windows)
├── scripts/run_local.py    Versión de escritorio: web + API en 127.0.0.1
├── scripts/a2a/            Cliente A2A de ejemplo para el Python Tutor
└── Iniciar-Dashboard.bat   Lanzador para Windows (doble clic)
```

## Desarrollo local

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate            # Linux/Mac: source .venv/bin/activate
pip install -r requirements-dev.txt
copy .env.example .env            # Linux/Mac: cp .env.example .env
python -c "import secrets; print(secrets.token_urlsafe(48))"   # pégalo en JWT_SECRET del .env
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload     # http://127.0.0.1:8000/docs
```

### Frontend

```bash
cd frontend
python -m http.server 5500        # http://localhost:5500 (usa la API local automáticamente)
```

### Todo con Docker

```bash
JWT_SECRET=<valor> docker compose up --build
```

## Tests

| Suite | Comando | Qué cubre |
|---|---|---|
| Backend | `cd backend && python -m pytest --cov=app` | API, seguridad, RGPD, migraciones, contenido y banco del PCAP (cada respuesta se comprueba ejecutando Python; 100 % de cobertura) |
| Unitarios del frontend | `npm run test:unit` | Dominio por concepto, errores activos, repaso espaciado, plan de hoy, selección de ejercicios, sesiones, simulacros, prueba de nivel y Markdown seguro (`node --test`, sin dependencias) |
| Núcleo educativo | `python scripts/learning/build_learning.py --check` | Cada respuesta de los 128 ejercicios se comprueba ejecutando Python con el mismo `runner.py` del navegador |
| End-to-end | `npm ci && npx playwright install chromium && npm run test:e2e` | La app completa con el backend real, la consola Python y la auditoría WCAG |
| Calidad | `cd backend && ruff check . ../e2e && ruff format --check . ../e2e` | Estilo PEP 8 y formato |
| Cursos de la app | `python scripts/courses/sql_course.py --check` (y `js_course.py`, `java_course.py`, `entornos_course.py`, `programacion_course.py`) | Cada respuesta de código se comprueba ejecutándola (SQLite, Node, Java y Python) |
| App Android | `cd android && ./gradlew testDebugUnitTest lintDebug` | Dominio del PCAP y del núcleo educativo en Kotlin (banco, repaso espaciado, plan de hoy, sesiones, fusión con la cuenta) y lint de Android |

La CI ejecuta todo en cada push, incluidas las migraciones contra PostgreSQL 16.

## App Android nativa

En `android/` hay una app en **Kotlin + Jetpack Compose**. Su pestaña principal es **«Hoy»** (ADR-0031): el mismo plan de estudio, la teoría por concepto y las sesiones con explicación de errores que la web, con el mismo progreso. Los ejercicios de escribir programas se hacen en la web, porque necesitan Python. Además, tiene la experiencia tipo Duolingo (ADR-0011 y ADR-0012):

- una **ruta** de 12 unidades y 25 lecciones cortas generada a partir del banco del PCAP;
- **XP, racha y meta diaria**;
- **vidas**, que solo se gastan en la ruta y se recuperan con el tiempo o practicando;
- práctica libre por bloque y la preparación estimada.
- pestaña **Jugar** (ADR-0015): la **Mazmorra del Intérprete**, un roguelite de 5 plantas con jefes, monedas y comodines, y el minijuego **Bug Rush** de 90 segundos;
- **teoría completa de las 27 lecciones dentro de la app** (explicación, ejemplo, ejercicio, mini-quiz, reto y dudas frecuentes).

**Más cursos de DAW** (ADR-0016): ya están **Programación** (Python, UT1-UT9, ADR-0020), **Bases de datos** (SQL, organizado por las UD1-UD3 del centro, ADR-0019), **Entornos de desarrollo** (UD1 del centro), **JavaScript** (Entorno cliente) y **Java** (para más adelante). Todas las respuestas de código se comprueban ejecutando el código. HTML/CSS irá después. El del PCAP no cambia.

**Funciona entera sin conexión:** la app no pide permiso de internet (ADR-0014).

Usa los mismos datos que la web (`frontend/data/*.json`) y guarda el progreso en el mismo formato, para poder sincronizarlo con la cuenta.

| Entrega | Contenido | Estado |
|---|---|---|
| 1 | Proyecto, CI con APK, panel y práctica por bloque | ✔ |
| 2 | Ruta, lecciones cortas, XP, racha, meta diaria, vidas, celebración y perfil | ✔ |
| 3 | Modo «Jugar»: Mazmorra del Intérprete y Bug Rush | Por probar en el móvil |
| 4 | Escribir código: completar el hueco, ordenar líneas y encontrar el error (ADR-0017, Java) | Por probar en el móvil |
| 4b | Bases de datos por UD1-UD3 del centro y curso de Entornos de desarrollo (ADR-0019) | Por probar en el móvil |
| 4c | Programación en Python por UT1-UT9 (ADR-0020) | Por probar en el móvil |
| Web | Cursos de DAW en la web, con el progreso compartido con la app (ADR-0021) | ✔ (e2e) |
| 5 | Simulacro cronometrado, fichas y repaso de hoy | Pendiente |
| 6 | Python real en el móvil (Chaquopy) | Pendiente |
| 7 | Cuenta y sincronización (ADR-0018): B1 en el backend y la web | B1 ✔ · B2 pendiente |

**Instalarla:** en GitHub → *Actions* → *Android* → la última ejecución → *Artifacts*:

- `python-pcap-release`: `app-release.apk`, firmado con la clave del proyecto (ADR-0013). Es la versión para usar: las actualizaciones se instalan encima sin perder el progreso.
- `python-pcap-apk`: `app-debug.apk`, solo en los pull requests. Se instala aparte como "Python PCAP (debug)", con su propio progreso, así que **no es para el móvil de uso diario** (ADR-0030).

La firma de release necesita tres secretos en *Settings → Secrets and variables → Actions*: `PLD_KEYSTORE_BASE64`, `PLD_KEYSTORE_PASSWORD` y `PLD_KEY_ALIAS`. La clave (`.jks`) nunca va al repositorio.

## API

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| GET | `/api/health` | | Estado del servicio |
| GET | `/api/modules` | | Módulos con sus lecciones |
| GET | `/api/lessons/{slug}` | | Lección completa (teoría, ejemplo, ejercicio, tests y asistente) |
| POST | `/api/auth/register` | | Crear cuenta (requiere `accept_privacy: true`) |
| POST | `/api/auth/login` | | Formulario OAuth2 (`username` = email) → token |
| POST | `/api/auth/password-reset/request` | | Enviar enlace de recuperación |
| POST | `/api/auth/password-reset/confirm` | | Nueva contraseña (cierra todas las sesiones) |
| GET | `/api/users/me` | ✔ | Usuario actual |
| GET | `/api/users/me/export` | ✔ | Todos mis datos en JSON (RGPD) |
| POST | `/api/users/me/delete` | ✔ | Borrar la cuenta y sus datos (pide la contraseña) |
| GET | `/api/progress` | ✔ | Lecciones completadas |
| PUT / DELETE | `/api/progress/{slug}` | ✔ | Marcar o desmarcar |
| POST | `/api/progress/import` | ✔ | Fusionar el progreso del navegador |
| POST / GET | `/api/lessons/{slug}/attempts` | ✔ | Registrar un intento o ver los últimos 20 |
| GET / PUT | `/api/pcap-state` | ✔ | Preparación del PCAP (simulacros, aciertos, fichas, repaso y plan) |
| GET / PUT | `/api/course-state/{curso}` | ✔ | Estado de los cursos de la app Android: `sql`, `js`, `java`, `entornos` o `programacion` (ADR-0018), y `learn`: progreso por conceptos del núcleo educativo (ADR-0031) |

### A2A (agentes)

Con `A2A_ENABLED=true` el backend añade agentes [A2A 1.0](https://a2a-protocol.org/) junto a la API REST, que no cambia. El tutor usa por defecto un **modelo local y gratuito con [Ollama](https://ollama.com)** (`A2A_MODEL_PROVIDER=ollama`, modelo recomendado `qwen2.5-coder:7b`); Anthropic está disponible pero desactivado (de pago, solo si se elige). Para tests, `A2A_MOCK_MODEL=true`, sin modelo ni claves. Detalle, ejemplos, privacidad, límites de coste y cómo añadir agentes o cambiar de proveedor: **[docs/a2a.md](docs/a2a.md)**.

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| GET | `/a2a/python-tutor/.well-known/agent-card.json` | | Agent Card del Python Tutor (también en `/.well-known/agent-card.json`) |
| POST | `/a2a/python-tutor` | ✔ | JSON-RPC de A2A 1.0 (`SendMessage`, `GetTask`, `ListTasks`, `CancelTask`), cabecera `A2A-Version: 1.0` |

En la web es la sección **Tutor Python** (`#/tutor`), que solo aparece si el servidor ofrece el agente.

## Publicar

Guía completa en **[docs/DEPLOY.md](docs/DEPLOY.md)**: GitHub Pages, backend en Render, conexión entre ambos, SMTP y la lista de comprobación del RGPD.

## Contribuir y licencia

Consulta [CONTRIBUTING.md](CONTRIBUTING.md) y [SECURITY.md](SECURITY.md). Licencia [MIT](LICENSE). Las fuentes tipográficas (Inter, JetBrains Mono y Fraunces, OFL) y highlight.js incluyen sus propias licencias en `frontend/fonts/` y `frontend/vendor/`.
