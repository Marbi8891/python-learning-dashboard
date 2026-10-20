# Python Learning Dashboard

[![CI](https://github.com/Marbi8891/python-learning-dashboard/actions/workflows/ci.yml/badge.svg)](https://github.com/Marbi8891/python-learning-dashboard/actions/workflows/ci.yml)
[![Security](https://github.com/Marbi8891/python-learning-dashboard/actions/workflows/security.yml/badge.svg)](https://github.com/Marbi8891/python-learning-dashboard/actions/workflows/security.yml)
[![Deploy frontend](https://github.com/Marbi8891/python-learning-dashboard/actions/workflows/pages.yml/badge.svg)](https://github.com/Marbi8891/python-learning-dashboard/actions/workflows/pages.yml)
![Cobertura backend](https://img.shields.io/badge/cobertura%20backend-100%25-brightgreen)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Herramienta para **aprender Python entendiendo lo que haces** y **preparar la parte de programación de DAW**. Funciona por conceptos: teoría con ejemplos, ejercicios corregidos al momento, explicación de cada error, repaso espaciado y simulacros. Incluye además el curso del examen PCAP, los demás módulos de DAW, una portada pública, un tutor de Python, un panel personal para el alumno y una app Android.

**Demo:** https://marbi8891.github.io/python-learning-dashboard/

## Índice

- [Qué incluye hoy](#qué-incluye-hoy)
- [Portada](#portada-adr-0037)
- [Núcleo educativo](#núcleo-educativo-adr-0031)
- [Curso PCAP y demás funcionalidades](#curso-pcap-y-demás-funcionalidades)
- [Mi panel](#mi-panel-adr-0035)
- [Cuenta, acceso y privacidad](#cuenta-acceso-y-privacidad)
- [Python Tutor (A2A)](#python-tutor-a2a)
- [App Android nativa](#app-android-nativa)
- [Agentes de Claude Code para el desarrollo](#agentes-de-claude-code-para-el-desarrollo)
- [Usarlo en tu PC](#usarlo-en-tu-pc-windows) · [Desarrollo local](#desarrollo-local) · [Tests](#tests)
- [Arquitectura](#arquitectura) · [API](#api) · [Documentación](#documentación) · [Publicar](#publicar)

## Qué incluye hoy

Todo lo de esta tabla está en `main`.

| Área | Qué hace | Dónde | Decisión |
|---|---|---|---|
| Núcleo educativo | 22 conceptos y 131 ejercicios comprobados ejecutando Python | Aprender, Teoría, Practicar, DAW, Progreso | [ADR-0031](docs/adr/0031-nucleo-educativo-por-conceptos.md) |
| Curso PCAP | 27 lecciones, 126 preguntas y simulacro oficial de 40 preguntas | Menú «Más» | [ADR-0009](docs/adr/0009-enfoque-pcap.md) |
| Portada | Presentación pública con una demostración real del temario; la raíz de la web lleva aquí | `#/portada` (PR #57, #55) | [ADR-0037](docs/adr/0037-portada-publica.md) |
| Bienvenida | Mapa de 5 paradas y recorrido guiado por el menú | `#/bienvenida` | — |
| Mi panel | Resumen, cursos, progreso, actividad, planificación, logros y perfil | `#/panel` (PR #49) | [ADR-0035](docs/adr/0035-panel-del-alumno.md) |
| Login con Google | Crear cuenta, entrar y borrar la cuenta con Google; el script de Google solo se carga al abrir el acceso | Pantalla de acceso (PR #46, #48, #55) | [docs/auth.md](docs/auth.md) |
| Sesión segura | Token en cookie `HttpOnly` con protección CSRF | Web (PR #39) | [ADR-0033](docs/adr/0033-sesion-en-cookie-httponly.md) |
| Recuperación de contraseña | Enlace por email, enviado por la API HTTPS de Brevo o por SMTP | `#/restablecer` (PR #36, #42, #44) | [docs/auth.md](docs/auth.md) |
| Python Tutor | Tutor de Python por A2A 1.0, con Ollama local, modo sin IA o Anthropic opcional | `#/tutor` (PR #40, #41) | [ADR-0034](docs/adr/0034-agentes-a2a.md) |
| Tutor adaptativo | Plan pedagógico propio, nivel por evidencias, pistas graduadas y origen visible de cada respuesta | `#/tutor` (PR #51, #54) | [ADR-0036](docs/adr/0036-tutor-adaptativo.md) |
| Tutor híbrido | Modo gratuito siempre disponible e «IA avanzada» con OpenAI opcional, desactivada por defecto y con cuotas | `#/tutor` (PR #60) | [ADR-0038](docs/adr/0038-tutor-hibrido.md) |
| App Android | Kotlin + Compose, sin conexión, con el mismo progreso que la web | `android/` | [ADR-0011](docs/adr/0011-app-android-nativa.md) |
| Equipo AppSec | 8 agentes de seguridad, guardián de rutas y análisis automático en cada PR | `.claude/agents/`, `security.yml` (PR #50, #52) | [AGENT_WORKFLOW](docs/security/AGENT_WORKFLOW.md) |
| LegalDocs AI | Agente que mantiene el expediente legal (privacidad, LSSI, licencias, IA) | `docs/legal/` (PR #53) | [docs/legal](docs/legal/README.md) |

## Portada (ADR-0037)

`#/portada` presenta la web a quien llega desde un enlace, con su propia cabecera y menú móvil accesible. Incluye una demostración con un concepto y un ejercicio reales del temario (corrige y explica el error de cada respuesta trampa, y el ejemplo se puede ejecutar en el navegador), las funciones disponibles, el recorrido en cuatro pasos, el temario, la tecnología, preguntas frecuentes y CodeFeed como propuesta en desarrollo. La raíz de la web y el logo llevan a la portada; «Empezar a aprender» lleva a «¿Qué estudio ahora?». Cada sección tiene su ruta (`#/portada/<sección>`).

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
- **Plan según el tiempo disponible:** el plan del día y las indicaciones del tutor se adaptan a los minutos que tengas (PR #45).
- **Contenido verificado:** 131 ejercicios en `frontend/data/learning.json`, generados por `scripts/learning/`. El script ejecuta cada salida, cada corrección y cada solución, y comprueba que las soluciones equivocadas típicas fallan en el test que delata su error.
- **Mismo progreso en la web y en la app:** `/api/v1/course-state/learn`.

## Curso PCAP y demás funcionalidades

- **Temario del PCAP:** un módulo de bases (nivel PCEP) y uno por cada bloque oficial del examen (Módulos y paquetes, Excepciones, Strings, POO, Miscelánea), más un extra «Después del PCAP». 27 lecciones.
- **Zona de examen:** simulacro de 40 preguntas en 65 minutos con el reparto oficial del temario, práctica por bloque con corrección al momento, 48 fichas de repaso y panel de preparación por bloque. 126 preguntas originales, en español o en inglés (como el examen), cada una con una comprobación en Python que demuestra su respuesta.
- **Teoría y ejemplos:** explicaciones propias, código con resaltado de sintaxis, números de línea y botones «Copiar», «Probar en la consola» y «Abrir en PyCharm» (copia el código, guía los pasos y permite descargar el `.py`).
- **Consola interactiva:** Python 3.14 real ([Pyodide](https://pyodide.org)) en un Web Worker. Admite `input()`, muestra los errores con la línea exacta y corta los bucles infinitos a los 10 s. Después de cargar Python, el Worker cierra el acceso a la red, así que un programa pegado en la consola no puede enviar datos a otros servidores.
- **Ejercicios corregidos:** cada lección tiene plantilla y tests. Superarlos completa la lección.
- **Asistente:** preguntas frecuentes, pista del ejercicio y «Siguiente tema», adaptados a cada lección.
- **Mini-quiz:** 3 preguntas por lección (81 en total) que explican por qué cada respuesta es correcta o no.
- **Retos extra:** uno por lección, de ★ a ★★★ (FizzBuzz, carrito de la compra, renombrador de fotos…), con tests automáticos.
- **XP, niveles y racha:** 7 niveles de «Novato/a» a «Leyenda de Python», bonus por acertar a la primera, XP por la preparación del examen, 20 logros (7 de ellos del PCAP) con su vitrina y confeti (desactivado si el sistema pide reducir el movimiento). Con la sesión iniciada se guardan en la cuenta.
- **Estudio guiado:** repaso espaciado de preguntas y fichas, plan semanal a partir de la fecha del examen y, en cada fallo, enlace a la lección que lo explica.
- **Certificado de finalización** imprimible (no oficial) y **app instalable** (PWA) que funciona sin conexión.
- **Estética de academia:** diseño editorial (tinta, marfil y dorado, titulares en serif) y portada con «Continuar donde lo dejaste».
- **Tema y letra:** claro, oscuro o automático, y tres tamaños de letra.
- **Accesible y adaptable:** WCAG 2.1 AA verificado automáticamente en los dos temas, navegable con teclado y con menú móvil.

## Mi panel (ADR-0035)

Con la sesión iniciada, `#/panel` reúne todo lo del alumno en siete secciones:

| Sección | Contenido |
|---|---|
| Resumen | Indicadores con datos reales y «Continuar aprendiendo» con la última actividad y el siguiente paso del plan |
| Mis cursos | Avance en cada curso |
| Mi progreso | Evolución de 30 días (gráfica accesible con su tabla), temas dominados, refuerzo, errores recurrentes y resultados |
| Actividad | Historial de aprendizaje paginado |
| Planificación | Plan de estudio |
| Logros | XP, nivel y logros, guardados en la cuenta |
| Mi perfil | Cuenta, método de acceso (contraseña o Google), aspecto, seguridad y datos |

Los indicadores solo muestran lo que se puede calcular de verdad: si no hay datos, el panel lo dice en lugar de inventar cifras. Sustituye a «Mi cuenta» (`#/cuenta` redirige a `#/panel/perfil`). Usa `GET /api/v1/dashboard` y `GET /api/v1/dashboard/activity`, sin migraciones nuevas.

## Cuenta, acceso y privacidad

La cuenta es **opcional**: sin ella todo funciona y el progreso se guarda en el navegador.

- **Registro con email y contraseña** (Argon2) o **con Google**. El ID token de Google se verifica en el servidor (firma, audiencia, caducidad y email verificado) y la cuenta nueva también exige aceptar la política de privacidad. El script de Google solo se descarga al abrir el inicio de sesión o el borrado de la cuenta, no en cada visita, y el botón solo aparece si el servidor tiene `GOOGLE_CLIENT_ID`. Si alguien entra con Google en una cuenta creada con contraseña cuyo email nunca se verificó, la contraseña se anula y se cierran las demás sesiones, para evitar que otra persona la haya registrado antes.
- **Sesión en una cookie `HttpOnly`** (ADR-0033): JavaScript no puede leer el token y la sesión sobrevive a recargar. Protección CSRF con la cabecera `X-PLD-Session`. La app Android sigue usando `Authorization: Bearer`. Sesiones de 30 minutos.
- **Cerrar sesión** en este dispositivo o en todos.
- **Protección contra fuerza bruta:** límite de intentos por minuto y bloqueo temporal de la cuenta tras varios fallos.
- **Recuperación de contraseña** ([docs/auth.md](docs/auth.md)): «¿Has olvidado tu contraseña?» envía un enlace de un solo uso que caduca a los 30 minutos y, al usarlo, cierra todas las sesiones. La respuesta es la misma exista o no la cuenta. El email sale por la **API HTTPS de Brevo** (`BREVO_API_KEY`), porque el plan gratuito de Render bloquea SMTP, o por SMTP (`SMTP_HOST`, puertos 587 o 465). Sin ninguno de los dos, no se envía.
- **Sincronización** del progreso, la preparación del PCAP, los cursos, el XP y los logros entre la web y la app.
- **RGPD:** descargar todos tus datos en JSON y borrar la cuenta, confirmando con la contraseña o eligiendo la misma cuenta de Google.
- Páginas públicas: [`privacidad.html`](frontend/privacidad.html) y [`aviso-legal.html`](frontend/aviso-legal.html).

## Python Tutor (A2A)

Con `A2A_ENABLED=true` el backend añade agentes [A2A 1.0](https://a2a-protocol.org/) (SDK oficial `a2a-sdk`) junto a la API REST, que no cambia. En la web es la sección **Tutor Python** (`#/tutor`), que solo aparece si el servidor ofrece el agente.

- **Qué hace:** explica conceptos y errores, revisa tu código **sin ejecutarlo** (lo analiza con `ast`), propone ejercicios según tu nivel y no da la solución de un ejercicio que tengas pendiente.
- **Adaptativo** (ADR-0036): antes de llamar a ningún modelo prepara un plan pedagógico (tipo de consulta, concepto, nivel, pista que toca y pregunta de comprobación). El nivel sale de las evidencias (conceptos demostrados y ejercicios superados), no del % global. Las pistas van de 1 a 3, recuerda la conversación (solo en memoria) y reutiliza el contenido revisado del curso.
- **Cada respuesta dice su origen:** de IA, del tutor sin IA o preparada. Si el modelo falla, explica el motivo y responde igualmente con la guía sin IA.
- **En la web:** Cancelar, Reintentar, «Pedir una pista», «Explícamelo paso a paso», la lección abierta preseleccionada y ejemplos que se ejecutan en el navegador.
- **Dos modalidades** (ADR-0038, [docs/tutor-hibrido.md](docs/tutor-hibrido.md)):
  - **Gratuita**, siempre disponible. Su modelo se elige con `A2A_MODEL_PROVIDER`:

    | `A2A_MODEL_PROVIDER` | Qué es | Coste |
    |---|---|---|
    | `ollama` (por defecto) | Modelo local con [Ollama](https://ollama.com), recomendado `qwen2.5-coder:7b` | Gratis |
    | `mock` | Tutor sin IA: responde con el plan pedagógico y el contenido del curso | Gratis |
    | `anthropic` | API de Anthropic, solo con `ANTHROPIC_API_KEY` | De pago, desactivado salvo que se elija |

  - **IA avanzada**, opcional y **desactivada por defecto** (`A2A_ADVANCED_PROVIDER=none`). Con `openai` y `OPENAI_API_KEY` usa OpenAI (de pago). La modalidad la decide el backend, no el navegador, y tiene cuotas guardadas en la base de datos: 10 consultas por alumno y día, 200 en total al día, 6000 caracteres de entrada, 600 tokens de salida y 30 s por llamada, sin reintentos. Al llegar a un límite o si falla, se explica y se responde en modo gratuito; un fallo nunca pasa una consulta gratuita a la de pago. Antes de activarla en producción hay que revisar la privacidad (borrador en `docs/legal/expediente/borradores/`).
- **Comprobaciones:** «Explícamelo de otra forma», «Otro ejercicio» y una escalera de comprobaciones que sube de dificultad si aciertas. Las corrige el backend con la salida verificada en CI, nunca la IA, y una respuesta de la IA no marca nada como completado.

- **Límites:** mensajes por usuario y minuto, consultas al modelo por usuario y día y en total por minuto, tokens de salida y tiempo máximo por llamada.
- **Evaluación:** 20 casos en español que se ejecutan en CI (`backend/tests/tutor_eval/`) y `scripts/a2a/eval_tutor.py` para evaluar con un modelo real.

Detalle, ejemplos, privacidad y cómo añadir agentes: **[docs/a2a.md](docs/a2a.md)** y **[docs/tutor-hibrido.md](docs/tutor-hibrido.md)**.

## App Android nativa

En `android/` hay una app en **Kotlin + Jetpack Compose**. Su pestaña principal es **«Hoy»** (ADR-0031): el mismo plan de estudio, la teoría por concepto y las sesiones con explicación de errores que la web, con el mismo progreso. Los ejercicios de escribir programas se hacen en la web, porque necesitan Python. Además, tiene la experiencia tipo Duolingo (ADR-0011 y ADR-0012):

- una **ruta** de 12 unidades y 25 lecciones cortas generada a partir del banco del PCAP;
- **XP, racha y meta diaria**;
- **vidas**, que solo se gastan en la ruta y se recuperan con el tiempo o practicando;
- práctica libre por bloque y la preparación estimada;
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

## Agentes de Claude Code para el desarrollo

El proyecto se desarrolla también con agentes de [Claude Code](https://claude.com/claude-code). No forman parte de la web: ayudan al autor a revisar y documentar. Las reglas comunes están en [`CLAUDE.md`](CLAUDE.md) y el plan general por fases en [`docs/AGENTS.md`](docs/AGENTS.md).

**Equipo AppSec** ([docs/security/AGENT_WORKFLOW.md](docs/security/AGENT_WORKFLOW.md)): ocho agentes en `.claude/agents/`.

| Agente | Para qué |
|---|---|
| `security-lead` | Coordina la auditoría y mantiene [SECURITY_FINDINGS.md](docs/security/SECURITY_FINDINGS.md) |
| `security-auditor` | Revisión OWASP Top 10 y API Top 10, solo lectura |
| `auth-security` | Google, JWT, cookies, sesiones, recuperación y aislamiento entre cuentas |
| `api-security` | FastAPI, Pydantic, SQLAlchemy, CORS/CSRF, límites y Alembic |
| `frontend-security` | XSS, CSP, Pyodide, almacenamiento local y recursos externos |
| `dependency-security` | Dependencias y secretos |
| `security-qa` | Pruebas de regresión de seguridad |
| `security-devsecops` | GitHub Actions y comprobaciones automáticas |

- Un guardián (`.claude/hooks/appsec-guard.mjs`, necesita Node) limita qué archivos edita cada agente y bloquea secretos, comandos destructivos y escaneos externos.
- En cada PR, en `main` y cada lunes, [`security.yml`](.github/workflows/security.yml) ejecuta Bandit, Semgrep (con reglas propias en `.semgrep/`) y Gitleaks. `pip-audit` y `npm audit` van en `ci.yml`. Todo es gratuito.
- Uso: `claude --agent security-lead "Auditoría completa de seguridad desde la línea base"`, o `@agent-auth-security revisa el login con Google` en una sesión normal.

**LegalDocs AI** ([docs/legal/README.md](docs/legal/README.md)): agente de documentación legal (privacidad RGPD/LOPDGDD, LSSI y cookies, licencias y Reglamento de IA). Mantiene el expediente en `docs/legal/expediente/` (diagnóstico, matriz de trazabilidad, borradores e historial) y solo escribe en `docs/legal/`. Nunca cambia las páginas publicadas: propone borradores que el autor aprueba. Uso: `claude --agent legaldocs-ai "Actualiza el expediente legal"`. No es asesoramiento jurídico.

## Usarlo en tu PC (Windows)

Doble clic en **`Iniciar-Dashboard.bat`**. La primera vez instala lo necesario y después abre la app en el navegador, solo accesible desde tu ordenador. Requiere Python 3.11 o superior. Guía y solución de problemas: [docs/EJECUTAR-EN-WINDOWS.md](docs/EJECUTAR-EN-WINDOWS.md).

En Linux o macOS: `pip install -r backend/requirements.txt && python scripts/run_local.py`.

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
uvicorn app.main:app --reload     # http://127.0.0.1:8000
```

La documentación interactiva de la API (`/docs`) solo se sirve con `ENABLE_DOCS=true`.

### Frontend

```bash
cd frontend
python -m http.server 5500        # http://localhost:5500 (usa la API local automáticamente)
```

### Tutor con un modelo local (opcional)

```bash
ollama pull qwen2.5-coder:7b
python scripts/a2a/validate_tutor.py   # 5 consultas reales al tutor con un servidor temporal
```

Para usarlo desde la web local, pon `A2A_ENABLED=true` en `backend/.env` (`A2A_MODEL_PROVIDER=ollama` es el valor por defecto). Sin Ollama, `A2A_MODEL_PROVIDER=mock` activa el tutor sin IA. Más opciones en [docs/a2a.md](docs/a2a.md).

### Todo con Docker

```bash
JWT_SECRET=<valor> docker compose up --build
```

## Tests

Qué ejecutar según lo que cambies: [docs/TESTING.md](docs/TESTING.md) §3.

| Suite | Comando | Qué cubre |
|---|---|---|
| Backend | `cd backend && python -m pytest --cov=app` | API, seguridad, aislamiento entre cuentas, RGPD, migraciones, tutor (incluidos los casos de evaluación), contenido y banco del PCAP (cada respuesta se comprueba ejecutando Python; 100 % de cobertura) |
| Unitarios del frontend | `npm run test:unit` | Dominio por concepto, errores activos, repaso espaciado, plan de hoy, selección de ejercicios, sesiones, simulacros, prueba de nivel, Markdown seguro, cálculos del panel y fusión de logros (`node --test`, sin dependencias) |
| Núcleo educativo | `python scripts/learning/build_learning.py --check` | Cada respuesta de los 131 ejercicios se comprueba ejecutando Python con el mismo `runner.py` del navegador |
| End-to-end | `npm ci && npx playwright install chromium && npm run test:e2e` | La app completa con el backend real, la consola Python y la auditoría WCAG |
| Calidad | `cd backend && ruff check . ../e2e && ruff format --check . ../e2e` | Estilo PEP 8 y formato |
| Seguridad | `python scripts/security/run_checks.py` | Bandit, Semgrep con las reglas del proyecto, Gitleaks y auditoría de dependencias, si están instalados |
| Cursos de la app | `python scripts/courses/sql_course.py --check` (y `js_course.py`, `java_course.py`, `entornos_course.py`, `programacion_course.py`) | Cada respuesta de código se comprueba ejecutándola (SQLite, Node, Java y Python) |
| App Android | `cd android && ./gradlew testDebugUnitTest lintDebug` | Dominio del PCAP y del núcleo educativo en Kotlin (banco, repaso espaciado, plan de hoy, sesiones, fusión con la cuenta) y lint de Android |

La CI ejecuta todo en cada push, incluidas las migraciones contra PostgreSQL 16, y `security.yml` añade el análisis de seguridad.

## Arquitectura

| Parte | Tecnología | Despliegue |
|---|---|---|
| `frontend/` | HTML, CSS y JavaScript (módulos ES, sin framework), Pyodide | GitHub Pages |
| `backend/` | FastAPI, SQLAlchemy 2, Alembic, PostgreSQL/SQLite, JWT + Argon2, Google Sign-In | Docker: Render, Oracle Cloud… |
| `backend/app/a2a/` | Agentes A2A 1.0 con el SDK oficial `a2a-sdk` (Python Tutor), en la misma app FastAPI | Con el backend (desactivado por defecto) |
| `android/` | Kotlin + Jetpack Compose | APK desde GitHub Actions |
| `.claude/` | Agentes de Claude Code (AppSec y LegalDocs AI) y su guardián | Solo para el desarrollo |

```
├── frontend/
│   ├── data/learning.json  Núcleo educativo: conceptos, errores típicos y ejercicios (generado por scripts/learning)
│   ├── data/lessons.json   Contenido: teoría, ejemplos, ejercicios, quiz, retos y asistente (fuente única)
│   ├── data/pcap.json      Banco de preguntas del examen, fichas y formato oficial del PCAP
│   ├── py/runner.py        Motor que ejecuta y corrige el código (navegador y CI)
│   ├── js/learn/           Núcleo educativo: lógica pura (dominio, repaso, recomendación, sesiones) y vistas
│   ├── js/                 App, consola, Worker de Pyodide, quiz, juego, asistente, cuenta, panel, tutor, API
│   ├── css/  fonts/  vendor/
│   ├── config.js           URL de la API (vacía = modo sin cuenta) e ID público de Google
│   └── privacidad.html  aviso-legal.html
├── backend/
│   ├── app/                API: config, seguridad, sesión en cookie, modelos, routers, email (Brevo/SMTP)
│   ├── app/routers/        auth, cuenta, lecciones, progreso, intentos, PCAP, cursos y panel
│   ├── app/services/       Lógica fuera de los routers (contexto del alumno y temario del tutor)
│   ├── app/a2a/            Agentes A2A: cards, agents, executors, providers y server.py
│   ├── migrations/         Alembic
│   ├── tests/              pytest (100 % de cobertura)
│   └── Dockerfile
├── android/                App nativa (Kotlin + Compose)
├── e2e/                    Playwright: app completa + auditoría WCAG
├── docs/                   ADR, guías, seguridad (docs/security) y expediente legal (docs/legal)
├── .claude/                Agentes de Claude Code y guardián appsec-guard.mjs
├── .semgrep/               Reglas de Semgrep propias del proyecto
├── render.yaml             Blueprint de Render (backend + PostgreSQL)
├── docker-compose.yml      Todo en local con PostgreSQL
├── deploy.ps1              Publicación en GitHub Pages (Windows)
├── scripts/run_local.py    Versión de escritorio: web + API en 127.0.0.1
├── scripts/a2a/            Cliente, validación y evaluación del Python Tutor
├── scripts/security/       Comprobaciones de seguridad en local
└── Iniciar-Dashboard.bat   Lanzador para Windows (doble clic)
```

Decisiones documentadas (todas en [`docs/adr/`](docs/adr/)):
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
- ADR-0011 a 0030: app Android, cursos de DAW, seguridad integral y MITRE ATT&CK, Mi cuenta…
- [ADR-0031 Núcleo educativo por conceptos](docs/adr/0031-nucleo-educativo-por-conceptos.md)
- [ADR-0032 Sesión en memoria y API v1](docs/adr/0032-sesion-en-memoria-y-api-v1.md)
- [ADR-0033 Sesión en cookie HttpOnly](docs/adr/0033-sesion-en-cookie-httponly.md)
- [ADR-0034 Agentes A2A junto a la API REST](docs/adr/0034-agentes-a2a.md)
- [ADR-0035 Panel del alumno](docs/adr/0035-panel-del-alumno.md)
- [ADR-0036 Tutor de Python adaptativo](docs/adr/0036-tutor-adaptativo.md)
- [ADR-0037 Portada pública](docs/adr/0037-portada-publica.md)
- [ADR-0038 Tutor híbrido](docs/adr/0038-tutor-hibrido.md)

## API

La API pública está en `/api/v1`. Las rutas antiguas sin versión (`/api/...`) siguen funcionando para la app Android, marcadas como obsoletas. Referencia completa en [docs/API.md](docs/API.md).

| Método | Ruta (`/api/v1` +) | Auth | Descripción |
|---|---|---|---|
| GET | `/health` | | Estado del servicio |
| GET | `/modules` | | Módulos con sus lecciones |
| GET | `/lessons/{slug}` | | Lección completa (teoría, ejemplo, ejercicio, tests y asistente) |
| POST | `/auth/register` | | Crear cuenta (requiere `accept_privacy: true`) |
| POST | `/auth/login` | | Formulario OAuth2 (`username` = email) → sesión |
| POST | `/auth/google` | | Crear cuenta o entrar con un ID token de Google |
| POST | `/auth/logout` · `/auth/logout-all` | | Cerrar la sesión actual o todas |
| POST | `/auth/forgot-password` (o `/auth/password-reset/request`) | | Enviar enlace de recuperación |
| POST | `/auth/reset-password` (o `/auth/password-reset/confirm`) | | Nueva contraseña (cierra todas las sesiones) |
| GET / PATCH | `/users/me` | ✔ | Ver o editar el usuario actual |
| POST | `/users/me/password` | ✔ | Cambiar la contraseña |
| GET | `/users/me/activity` | ✔ | Actividad de la cuenta (accesos y cambios) |
| GET | `/users/me/export` | ✔ | Todos mis datos en JSON (RGPD) |
| POST | `/users/me/delete` | ✔ | Borrar la cuenta y sus datos (pide `password` o `google_credential`) |
| GET | `/progress` | ✔ | Lecciones completadas |
| PUT / DELETE | `/progress/{slug}` | ✔ | Marcar o desmarcar |
| POST | `/progress/import` | ✔ | Fusionar el progreso del navegador |
| POST / GET | `/lessons/{slug}/attempts` | ✔ | Registrar un intento o ver los últimos 20 |
| GET / PUT | `/pcap-state` | ✔ | Preparación del PCAP (simulacros, aciertos, fichas, repaso y plan) |
| GET | `/dashboard` | ✔ | Panel del alumno: lecciones, intentos, actividad diaria, documentos sincronizados y método del último acceso (ADR-0035) |
| GET | `/dashboard/activity` | ✔ | Historial de aprendizaje paginado (`limit`, `offset`) |
| GET | `/tutor/modes` | ✔ | Modalidades del tutor y cuota avanzada que le queda al alumno (solo con A2A activo, ADR-0038) |
| GET / PUT | `/course-state/{curso}` | ✔ | Cursos de la app (`sql`, `js`, `java`, `entornos`, `programacion`), `learn` (núcleo educativo) y `game` (XP, racha y logros) |

«Auth» es la sesión: la cookie `HttpOnly` en la web o `Authorization: Bearer` en la app y los scripts.

### A2A

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| GET | `/a2a/python-tutor/.well-known/agent-card.json` | | Agent Card del Python Tutor (también en `/.well-known/agent-card.json`) |
| POST | `/a2a/python-tutor` | ✔ | JSON-RPC de A2A 1.0 (`SendMessage`, `GetTask`, `ListTasks`, `CancelTask`), cabecera `A2A-Version: 1.0` |

## Documentación

- [Documentación del proyecto](docs/DOCUMENTACION-DEL-PROYECTO.md): objetivos, arquitectura, tecnologías, instalación, configuración, API, seguridad, pruebas y despliegue
- [Arquitectura detallada](docs/ARCHITECTURE.md) · [Referencia de la API](docs/API.md) · [Pruebas](docs/TESTING.md)
- [Guía de despliegue](docs/DEPLOY.md) · [Ejecutar en Windows](docs/EJECUTAR-EN-WINDOWS.md)
- [Cuenta y recuperación de contraseña](docs/auth.md) · [Python Tutor y A2A](docs/a2a.md) · [Tutor híbrido](docs/tutor-hibrido.md)
- [Seguridad](docs/SECURITY.md) · [Hallazgos de seguridad](docs/security/SECURITY_FINDINGS.md) · [Flujo del equipo AppSec](docs/security/AGENT_WORKFLOW.md)
- [Expediente legal](docs/legal/README.md)
- [Agentes de desarrollo](docs/AGENTS.md) · [MCP](docs/MCP.md)
- [Demo y defensa del proyecto](docs/DEMO-Y-DEFENSA.md) · [Memoria](docs/memoria/memoria.md)
- [Changelog](CHANGELOG.md)

## Publicar

Hacer merge a `main` publica la web en GitHub Pages ([`pages.yml`](.github/workflows/pages.yml)), que antes quita de la CSP los orígenes de desarrollo (`localhost:8000`). Guía completa en **[docs/DEPLOY.md](docs/DEPLOY.md)**: GitHub Pages, backend en Render, conexión entre ambos, Google Sign-In, email con Brevo o SMTP y la lista de comprobación del RGPD. La configuración del tutor en el servidor está en [docs/a2a.md](docs/a2a.md).

## Contribuir y licencia

Consulta [CONTRIBUTING.md](CONTRIBUTING.md) y [SECURITY.md](SECURITY.md). Licencia [MIT](LICENSE). Las fuentes tipográficas (Inter, JetBrains Mono y Fraunces, OFL) y highlight.js incluyen sus propias licencias en `frontend/fonts/` y `frontend/vendor/`.
