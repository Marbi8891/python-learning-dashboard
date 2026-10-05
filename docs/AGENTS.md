# Agentes de desarrollo (propuesta)

> Documento de la **Fase 1**. Es una **propuesta**: todavía no existe ningún archivo en `.claude/`.
> Los agentes se crearán en la Fase 2 cuando se autorice. La arquitectura real del proyecto está en
> [`ARCHITECTURE.md`](ARCHITECTURE.md).

## 1. Dos mundos que no se mezclan

| | A) Agentes de desarrollo | B) IA dentro de la aplicación |
|---|---|---|
| Quién lo usa | El autor, desde Claude Code | El alumno, en la web o la app |
| Dónde vive | `.claude/`, `CLAUDE.md`, `.mcp.json` | `frontend/`, `backend/` (hoy **no existe**) |
| Qué puede tocar | El repositorio, con permisos por área | Nada del repositorio |
| Este documento | **Sí** | No (ver sección 8) |

Ningún archivo de `.claude/` se publica en GitHub Pages: `pages.yml` solo sube `frontend/`.

## 2. Cómo funcionan los agentes en Claude Code (comprobado)

Comprobado con Claude Code **2.1.289** y la documentación oficial (`code.claude.com/docs`) el 5/10/2026.
Antes de la Fase 2 hay que repetir `claude --version` **en el PC del autor**, que puede tener otra versión.

- Un agente es un archivo `.claude/agents/<nombre>.md` con cabecera YAML (`name`, `description`,
  `tools`, `disallowedTools`, `model`, `permissionMode`, `mcpServers`, `hooks`, `maxTurns`…) y las
  instrucciones debajo.
- **El orquestador es la conversación principal**, no un subagente: es la sesión de Claude Code que
  recibe la petición y delega con la herramienta `Agent`. Sus reglas van en `CLAUDE.md`, que la sesión
  principal lee siempre. Opcionalmente, `claude --agent orchestrator` arranca la sesión con ese agente.
- `tools:` limita **qué herramientas** usa un agente (por ejemplo, sin `Edit` ni `Write`), pero
  **no limita rutas**. Para limitar rutas hay dos mecanismos reales:
  1. reglas de permisos en `.claude/settings.json` (`Edit(frontend/**)`, `Read(.env)`…), que valen para
     **todas** las sesiones y agentes;
  2. un *hook* `PreToolUse` en la cabecera de cada agente que ejecuta un script y bloquea (código de
     salida 2) si la ruta no es de su área.
- Un *hook* sobre `Bash` solo ve el comando, no lo que hace un script por dentro: un `python algo.py`
  podría escribir fuera del área. Por eso la última barrera es **Git**: rama por tarea, `git diff`
  revisado, CI y *merge* hecho por una persona.

## 3. Los 12 agentes

Áreas por ruta (lo que el *hook* de cada agente dejará editar):

| Agente | Responsabilidad | Puede editar | Herramientas |
|---|---|---|---|
| **orchestrator** (sesión principal) | Analiza, decide agentes, divide, detecta conflictos entre capas, revisa el resultado | Nada de código; plan en la conversación | Todas en lectura, `Agent`, `git status/diff/branch` |
| **architecture** | Módulos, interfaces, dependencias, refactorizaciones, ADR | `docs/adr/**`, `docs/ARCHITECTURE.md`; código solo con tarea aprobada | Read, Grep, Glob, Edit (docs) |
| **frontend** | HTML, CSS, JS de vistas, navegación, *responsive*, UX | `frontend/*.html`, `frontend/css/**`, `frontend/js/**` **excepto** los de autenticación (`api.js`, `account.js`, `private.js`) | Read, Grep, Glob, Edit, Write, Bash (tests) |
| **python-education** | Teoría, ejemplos, ejercicios, errores típicos y progresión del núcleo educativo | `scripts/learning/**` y, regenerado, `frontend/data/learning.json` | Read, Grep, Glob, Edit, Bash (`build_learning.py`) |
| **daw** | Cursos de DAW (Programación, BD, Entornos, JS, Java) y su alineación con el temario | `scripts/courses/**` y, regenerado, `frontend/data/courses/**` | Read, Grep, Glob, Edit, Bash (`*_course.py --check`) |
| **pcap** | Curso y zona de examen PCAP | `frontend/data/lessons.json`, `frontend/data/pcap.json` | Read, Grep, Glob, Edit, Bash (pytest de contenido) |
| **security** | Revisión de seguridad de todo (lista de la petición original) | `backend/tests/**`, `e2e/security.spec.js`, `docs/security/**`, `SECURITY.md`, `docs/SECURITY.md`; parches solo con tarea aprobada | Read, Grep, Glob, Edit, Bash (auditorías) |
| **test** | Unitarios, integración, e2e, validación de contenido y API | `tests/unit/**`, `e2e/**`, `backend/tests/**`, `android/app/src/test/**` | Read, Grep, Glob, Edit, Write, Bash (tests) |
| **accessibility** | WCAG 2.1 AA, HTML semántico, teclado, foco, contraste | `frontend/*.html`, `frontend/css/**`, `frontend/js/**` (vistas), `e2e/a11y.spec.js` | Read, Grep, Glob, Edit, Bash (e2e) |
| **performance** | Carga inicial, Pyodide, Worker, caché, PWA, fuentes | Solo optimizaciones autorizadas en `frontend/**` (incluido `sw.js`) | Read, Grep, Glob, Edit, Bash |
| **content-qa** | Errores técnicos, ambigüedades, respuestas incorrectas, duplicados, ortografía | **Nada**: informa y el agente dueño corrige | Read, Grep, Glob, Bash (solo `--check`) |
| **release** | Tests, revisión de cambios, rutas, PWA, *changelog* | `CHANGELOG.md`, `docs/RELEASE-*.md`, `VERSION` de `frontend/sw.js` | Read, Grep, Glob, Edit, Bash (tests, `git`) |

Reglas comunes a todos:
- Nadie edita a mano un JSON generado: se cambia el script y se regenera.
- Nadie toca `android/` sin tarea aprobada. La lógica de `frontend/js/learn/` está duplicada en
  `android/.../learn/Learning.kt`: si cambia una, el orquestador debe avisar de la otra.
- Nadie edita `.github/**`, `render.yaml`, `backend/Dockerfile`, `docker-compose.yml`, `deploy.ps1`,
  `.claude/**`, `.mcp.json` ni `CLAUDE.md` sin autorización explícita (regla `ask` en `settings.json`).
- Nadie ejecuta `deploy.ps1`, `git push --force`, `git reset --hard` ni `git clean`.
- Ningún agente lee `.env`, `*.jks`, `*.keystore`, `backend/.local-secret`.

Instrucciones específicas que irán en cada archivo de agente:
- **python-education**: cada ejercicio debe pedir razonar, leer código, depurar o escribir código; nada
  que se resuelva copiando una respuesta de IA sin entenderla (por ejemplo, «¿qué muestra?» con
  trazas, «encuentra el error», programas con tests que delatan las soluciones típicas equivocadas,
  que ya comprueba `build_learning.py`).
- **daw** y **pcap**: separar siempre **contenido propio** de **requisitos oficiales externos**; nunca
  inventar temarios, porcentajes ni preguntas oficiales; citar la fuente (ya hay `sources` en las
  lecciones) o marcar «pendiente de verificar».
- **frontend**: mantener módulos ES sin framework ni *build*; escapar siempre con `markdown.js`.
- **security**: todo dato del usuario, de `localStorage`, de la cuenta o del Worker es hostil; no
  añadir complejidad que no reduzca un riesgo concreto.
- **accessibility**: HTML semántico antes que ARIA.
- **performance**: medir antes de optimizar.

## 4. Matriz de permisos

`R` = leer · `W` = editar · `A` = solo con tarea aprobada · `—` = sin acceso.

| Área (rutas) | orch. | arch. | front. | py-edu | daw | pcap | sec. | test | a11y | perf. | qa | release |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `frontend/js`, `css`, `*.html` (vistas) | R | R·A | **W** | R | R | R | R·A | R | **W** | A | R | R |
| `frontend/js/{api,account,private}.js` (auth) | R | R·A | R·A* | — | — | — | R·A | R | R | R | — | R |
| `frontend/sw.js`, `manifest` | R | R | R·A | — | — | — | R | R | R | A | — | W (`VERSION`) |
| `frontend/index.html` (CSP) | R | R | W* | — | — | — | R·A | R | W | A | — | R |
| `scripts/learning/**`, `data/learning.json` | R | R | — | **W** | R | R | R | R | — | — | R | R |
| `scripts/courses/**`, `data/courses/**` | R | R | — | R | **W** | — | R | R | — | — | R | R |
| `data/lessons.json`, `data/pcap.json` | R | R | — | R | — | **W** | R | R | — | — | R | R |
| `backend/app/**` | R | R·A | — | — | — | — | R·A | R | — | — | — | R |
| `backend/tests/**`, `tests/unit/**`, `e2e/**` | R | R | R | R | R | R | W | **W** | W (`a11y`) | R | R | R |
| `android/**` | R | R·A | — | — | — | — | R | R·A (tests) | — | — | — | R |
| `docs/adr/**`, `docs/ARCHITECTURE.md` | R | **W** | R | R | R | R | R | R | R | R | R | R |
| `docs/security/**`, `SECURITY.md` | R | R | R | — | — | — | **W** | R | — | — | — | R |
| `CHANGELOG.md`, `docs/RELEASE-*.md` | R | R | — | — | — | — | — | — | — | — | — | **W** |
| `.github/**`, `render.yaml`, Docker, `deploy.ps1` | R | R | — | — | — | — | R | R | — | — | — | R (cambios: A) |
| `.env`, claves, *keystores* | — | — | — | — | — | — | — | — | — | — | — | — |
| **Publicar** (`push` a `main`, *merge*, APK) | — | — | — | — | — | — | — | — | — | — | — | **solo con autorización explícita** |

\* Con revisión del agente **security** antes del *merge*. Importante: **hacer *merge* a `main` publica la
web** (`pages.yml`), así que *merge* = despliegue.

## 5. Flujo de trabajo

1. **orchestrator** lee la petición, `git status`, `git branch`, `git diff`.
2. Elige los agentes mínimos y dice qué capas toca. **Si toca más de una capa, lo avisa antes.**
3. Cada agente inspecciona solo su área y propone.
4. **orchestrator** junta un plan corto y detecta conflictos (por ejemplo, dos agentes en el mismo archivo).
5. Se trabaja en una rama `tipo/descripcion`, con cambios pequeños.
6. **test** ejecuta las pruebas de lo tocado (y añade o actualiza tests).
7. **security** revisa si se toca entrada de usuario, autenticación, almacenamiento, CSP, Worker o dependencias.
8. **accessibility** revisa si se toca HTML/CSS/vistas.
9. **orchestrator** revisa `git diff` completo.
10. **release** prepara el *changelog* y el PR.
11. **Nada se publica sin autorización explícita** del autor.

## 6. Comandos propuestos

| Comando | Agentes (en orden) |
|---|---|
| `/audit` | architecture → security → accessibility → performance → content-qa → orchestrator (solo lectura) |
| `/test` | test → orchestrator |
| `/security` | security → test → orchestrator |
| `/accessibility` | accessibility → test → orchestrator |
| `/python <tema>` | python-education → content-qa → test |
| `/daw <módulo>` | daw → content-qa → test |
| `/pcap <tema>` | pcap → content-qa → test |
| `/frontend <tarea>` | frontend → accessibility → test → orchestrator |
| `/performance` | performance → test → orchestrator |
| `/content-review [área]` | content-qa (solo lectura) |
| `/release` | test → security → release (prepara, **no publica**) |

En Claude Code 2.1.289 los archivos `.claude/commands/<nombre>.md` siguen funcionando, aunque la
documentación oficial recomienda `.claude/skills/<nombre>/SKILL.md` para lo nuevo. Ver [`MCP.md`](MCP.md#5-capacidades-detectadas).

## 7. Ejemplos rápidos

- «Quiero crear 20 ejercicios de listas» → `/python ejercicios de listas`: python-education edita
  `scripts/learning/exercises.py`, regenera `learning.json` con `--check`; content-qa revisa; test pasa
  `build_learning.py --check` y `npm run test:unit`.
- «Quiero revisar la autenticación» → `/security`: solo lectura de `backend/app/` y `frontend/js/api.js`;
  informe con riesgos; cualquier parche pasa a ser una tarea aprobada aparte.

(Los ejemplos completos irán en `docs/AGENT_WORKFLOW.md`, Fase 12.)

## 8. IA dentro de la aplicación (futuro, separado)

Hoy **no hay IA** en la app. Si se añade un tutor:
- será un componente independiente (por ejemplo, `frontend/js/tutor/` y un router propio en el backend);
- la clave de la API de IA solo en el backend (nunca en `frontend/`), con límite de uso por cuenta;
- dará explicaciones, pistas graduadas y detección de errores, **no la solución completa** cuando el
  objetivo es aprender;
- no enviará datos personales; el código del alumno se trata como entrada no fiable (inyección de
  *prompts*) y la respuesta del modelo se escapa como cualquier otro texto;
- tendrá su propio ADR, su revisión de seguridad y sus tests.
Los agentes de desarrollo **no** forman parte de ese tutor.
