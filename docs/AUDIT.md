# Auditoría técnica integral

> Fecha: **21 de octubre de 2026**. Línea base: `main` en `936f641` (tras #55, #56, #57 y #60).
> Rama de trabajo: `claude/project-thread-xl5vtb`. Entorno: contenedor Linux, Python 3.13, Node 22,
> Chromium 1194 de Playwright.
>
> Sustituye a la auditoría de la Fase 1 del 5/10/2026 (resumida en `ARCHITECTURE.md` §8) y reutiliza
> los informes de seguridad (`security/SECURITY_FINDINGS.md`), del cierre del MVP y del tutor híbrido.
> **Producción no se ha podido comprobar**: el proxy de este entorno bloquea `marbi8891.github.io` y
> `pld-api.onrender.com`. Nada de producción se declara verificado aquí.

Leyenda de estados: **Verificado** = comprobado con una prueba que se ha ejecutado de verdad en esta
auditoría. **Revisado** = leído en el código, sin prueba propia. **No verificable aquí** = necesita
credenciales, producción, Java o el SDK de Android.

## 1. Resumen

El proyecto está en buen estado técnico y es bastante más maduro de lo que sugiere un «dashboard»: SPA
sin *build* con módulos ES, Python real en el navegador (Pyodide en un Worker), API FastAPI con 100 %
de cobertura, app Android, 38 ADR y un equipo de agentes de seguridad. **Todas las suites que se pueden
ejecutar aquí estaban en verde antes de tocar nada** (§5).

Los huecos reales frente al prompt maestro no eran de estabilidad sino de funciones concretas:

| Hueco encontrado | Estado en esta rama |
|---|---|
| La consola no se podía detener: un programa largo solo paraba al llegar a los 10 s | **Corregido**: botón «Detener» |
| Sin cuenta no había forma de guardar o mover el progreso (solo la exportación RGPD de la cuenta) | **Corregido**: exportar e importar en «Mi aprendizaje», con validación y fusión |
| Sin búsqueda ni filtro de lecciones | **Corregido**: buscador y «Solo pendientes» en la barra lateral |
| El corrector no distinguía respuesta incorrecta, error de ejecución, tiempo agotado y fallo del corrector | **Corregido** |
| Nada comprobaba el sitio estático antes de publicarlo (rutas, imports, sintaxis) ni la web después | **Corregido**: `scripts/check_site.py` en CI y en `pages.yml`, más comprobación tras publicar |
| `aviso-legal.html` cargaba sus estilos con la ruta absoluta de Pages (sin estilos en local) | **Corregido** (encontrado por la prueba nueva) |
| Manifiesto de la PWA desfasado («Prepara el PCAP», abría `#/inicio`) | **Corregido** |

Lo que queda pendiente está en [`ROADMAP.md`](ROADMAP.md), ordenado por prioridad.

## 2. Arquitectura detectada

Detalle en [`ARCHITECTURE.md`](ARCHITECTURE.md). En una línea por pieza:

| Pieza | Tecnología real | Despliegue |
|---|---|---|
| `frontend/` | HTML + CSS + JavaScript con módulos ES, **sin framework, sin *build*, sin `node_modules` en producción**. Rutas `#/…` | GitHub Pages (`pages.yml`, al fusionar en `main`) |
| Python en el navegador | Pyodide 314.0.7 (Python 3.14) desde jsDelivr, en un Web Worker; motor común `frontend/py/runner.py` | Con la web |
| `backend/` | FastAPI, SQLAlchemy 2, Alembic, Pydantic Settings, PyJWT, Argon2id; tutor A2A (Ollama/mock, Anthropic/OpenAI desactivados) | Render (Docker) + PostgreSQL en Neon |
| `android/` | Kotlin + Jetpack Compose, mismo contenido y misma cuenta | APK desde `android.yml` |
| `scripts/` | Python (biblioteca estándar) que **genera y comprueba** `frontend/data/learning.json` y los cursos de DAW | PC del autor y CI |

**GitHub Pages solo sirve archivos estáticos.** Nada de Python de servidor se ejecuta allí: el Python de
la consola corre en el navegador del alumno, y la API (cuentas, sincronización, tutor) vive en Render.
Sin backend, la web funciona entera en modo local (progreso en `localStorage`), sin cuentas ni tutor.

## 3. Funcionalidades verificadas

| Funcionalidad | Evidencia | Estado |
|---|---|---|
| Portada pública (`#/portada`) y núcleo educativo (`#/aprender`, `#/teoria`, `#/practicar`, `#/progreso`) | `e2e/landing.spec.js`, `learn.spec.js`, `study.spec.js` | Verificado |
| 22 conceptos y 131 ejercicios de seis tipos (salida, elección, código, bug, rellenar, ordenar) cuyas respuestas se ejecutan | `build_learning.py --check` | Verificado |
| Curso PCAP: 27 lecciones con teoría, ejemplo, ejercicio con tests, quiz de 3 preguntas y reto | `test_content.py` (cada ejemplo y cada plantilla se ejecutan), `e2e/academy.spec.js` | Verificado |
| Zona de examen PCAP: 126 preguntas originales, simulacro 40/65 min, práctica por bloque, 48 fichas | `test_pcap.py`, `e2e/pcap.spec.js` | Verificado |
| Cursos de DAW (Programación, SQL, Entornos, JavaScript, Java) | `e2e/daw.spec.js`; `--check` de cada curso | Web verificada; `--check` de Java y Android **no verificable aquí** (los pasa la CI) |
| Consola Python: `input()`, errores con línea y explicación, corte por tiempo, **detener**, borrador persistente | `e2e/console.spec.js`, `tests/unit/python-runner.test.mjs` | Verificado |
| Corrección automática con tests que comprueban comportamiento (asserts sobre variables, salida y código) | `runner.py` `check_exercise`, `test_content.py` | Verificado |
| Progreso local por concepto, repaso espaciado (cajas de Leitner 0-1-3-7-14-30 días), errores activos, plan de hoy | `tests/unit/*.test.mjs` (lógica pura), `e2e/study.spec.js` | Verificado |
| XP, niveles, racha y 20 logros calculados a partir de hechos | `tests/unit/game-data.test.mjs`, `e2e/game.spec.js` | Verificado |
| Cuentas: registro, login, cookie HttpOnly, sesiones, borrado, exportación RGPD, aislamiento entre cuentas | `test_auth.py`, `test_security_isolation.py`, `e2e/account.spec.js` | Verificado (con el backend local) |
| Login con Google y recuperación por email (Brevo) | `test_google_auth.py`, `test_password_reset.py` con servicios simulados | Código verificado; **real no verificable aquí** (falta `GOOGLE_CLIENT_ID`/`BREVO_API_KEY` en Render) |
| Panel del alumno (`#/panel`) | `test_dashboard.py`, `e2e/dashboard.spec.js` | Verificado |
| Tutor híbrido (gratuito + IA avanzada apagada) y tutor A2A con Ollama/mock | `test_tutor_*.py`, `test_a2a*.py`, `e2e/tutor*.spec.js` | Verificado con el modelo simulado; Ollama real **no verificable aquí** |
| Accesibilidad automática (axe-core, WCAG 2.1 AA) en tema claro y oscuro, móvil y teclado | `e2e/a11y.spec.js`, `ux.spec.js`, `widgets.spec.js` | Verificado (automático) |
| Exportar/importar progreso, buscador de lecciones, tipos de resultado del corrector | `e2e/progress-backup.spec.js`, `lesson-filter.spec.js`, `console.spec.js`, `tests/unit/progress-file.test.mjs` | **Nuevo**, verificado |
| PWA sin conexión | `sw.js` revisado; `e2e/study.spec.js` comprueba el manifiesto | Revisado (sin prueba del modo sin conexión) |

## 4. Hallazgos

Prioridad: **P1** afecta a usuarios o seguridad ahora; **P2** importante; **P3** mejora.

### 4.1 Corregidos en esta rama

| ID | Hallazgo | Evidencia | Corrección |
|---|---|---|---|
| AUD-01 | La consola no se podía detener; solo el límite de 10 s cortaba un programa | `python-runner.js` no tenía forma de cancelar | `PythonRunner.stop()` + botón «Detener» (P2) |
| AUD-02 | Sin cuenta, el progreso no se podía guardar ni llevar a otro navegador | Solo existía `GET /api/users/me/export` (con cuenta) | `progress-file.js` + `progress-transfer.js`: JSON versionado, 2 MB máx., limpiadores existentes, fusión (P2) |
| AUD-03 | Sin búsqueda ni filtro de lecciones | `app.js` `renderSidebar` | `lesson-filter.js` (P3) |
| AUD-04 | El corrector no distinguía los cuatro tipos de fallo; un fallo del Worker contaba como intento | `runner.py` `check_exercise`, `console.js` `checkCode` | Campo `kind`, textos propios, un fallo del corrector no cuenta (P2) |
| AUD-05 | Nada comprobaba el artefacto de Pages antes ni después de publicar | `pages.yml` | `scripts/check_site.py` en `ci.yml` y `pages.yml`; comprobación HTTP tras publicar; reversión en `DEPLOY.md` (P2) |
| AUD-06 | `aviso-legal.html` enlazaba sus estilos con `/python-learning-dashboard/…` | `aviso-legal.html:13-15` (antes) | Rutas relativas, como `privacidad.html` (P3) |
| AUD-07 | Manifiesto desfasado | `manifest.webmanifest` | Nombre, descripción y `start_url ./#/aprender` (P3) |
| AUD-08 | La plantilla de PR no pedía `test:unit`, `build_learning --check` ni e2e | `.github/pull_request_template.md` | Añadidos (P3) |

### 4.2 Pendientes (pasan al roadmap)

| ID | Hallazgo | Evidencia | Prioridad |
|---|---|---|---|
| AUD-10 | `docs/security/SECURITY_FINDINGS.md` dice «PR #55 sin fusionar» para PLD-SEC-003/007/008/009, pero #55 está fusionado | Tabla del documento; `git log` (`4a8d37b`) | P3 (documental; lo actualiza `security-lead`) |
| AUD-11 | Dependencias de pip con rangos y sin *hashes* (PLD-SEC-005) | `backend/requirements.txt` | P2 (decisión pendiente del autor) |
| AUD-12 | Pyodide se carga de jsDelivr sin SRI | `python-runner.js` | P3 (riesgo aceptado en PLD-SEC-006; alternativa: autoalojar) |
| AUD-13 | El simulacro PCAP tiene límite de tiempo fijo, sin opción de practicar sin él | `pcap.js` `startExam` | P2 (WCAG 2.2.1 tiene la excepción «esencial» para un examen; decisión pedagógica, ver roadmap) |
| AUD-14 | Desplazamiento de diseño (CLS) ≈ 0,10-0,11 al abrir una lección, en el límite de «bueno» (0,1) | Medida local con `PerformanceObserver` (§6) | P3 |
| AUD-15 | Carga inicial: 50 módulos JS (≈ 150 KB gzip) y 16 hojas CSS (≈ 25 KB gzip) se piden al arrancar; `lessons.json` y `learning.json` (≈ 100 KB gzip) también | §6 | P3 |
| AUD-16 | Capas CSS de varios rediseños que se pisan (`base`, `academy`, `pro`, `learn`) y 177 `font-size` en `px` | `frontend/css/` | P3 |
| AUD-17 | Lógica del núcleo educativo duplicada en JavaScript y Kotlin, sin prueba de paridad | `frontend/js/learn/`, `android/` | P2 |
| AUD-18 | Los ejercicios del núcleo educativo no tienen pistas progresivas ni casos ocultos; los de lección tienen tests pero todos visibles en `lessons.json` | `learning.json`, `lessons.json` | P2 (ver roadmap, Fase 5) |
| AUD-19 | El temario PCAP es `PCAP-31-03`, sin fecha de última revisión contra la web de Python Institute; la portada del curso dice «simulacros como el examen real» | `pcap.json` `exam.code`, `lessons.json` `course.tagline` | P2 (verificar fuente oficial y matizar la frase) |
| AUD-20 | Itinerario «Python desde cero»: faltan iteradores/generadores, comprensiones, entornos virtuales y pruebas automatizadas como conceptos del núcleo (sí están en el curso PCAP) | `learning.json` `concepts` | P3 |
| AUD-21 | No hay pruebas manuales de accesibilidad documentadas (lector de pantalla, zoom 200 %, solo teclado completo) | `docs/TESTING.md` §5 | P2 |
| AUD-22 | El buscador nuevo no se vuelve a aplicar si cambia el estado de una lección con el filtro «Solo pendientes» activo | `lesson-filter.js` | P3 |
| AUD-23 | Sin prueba automática del modo sin conexión del service worker | `sw.js` | P3 |
| AUD-24 | Archivos grandes: `programacion_course.py` (3 199 líneas), `exercises.py` (2 926), `dashboard.js` (784), `pcap.js` (774), `app.js` (824) | `wc -l` | P3 |

## 5. Pruebas: línea base y resultado final

Comandos ejecutados de verdad en este contenedor. Los e2e usan Pyodide de npm servido en local
(`frontend/pyodide-local`, sin commitear) porque `cdn.jsdelivr.net` está bloqueado aquí.

| Suite | Comando | Línea base (`936f641`) | Final (esta rama) |
|---|---|---|---|
| Lint y formato | `cd backend && ruff check . ../e2e ../scripts && ruff format --check . ../e2e ../scripts` | PASS | PASS |
| Backend + cobertura | `cd backend && python -m pytest -q --cov=app --cov-fail-under=100` | 785 passed, 1 skipped, 100 % | 791 passed, 1 skipped, 100 % |
| Núcleo educativo | `python scripts/learning/build_learning.py --check` | 22 conceptos, 131 ejercicios | igual |
| Unitarios JS | `npm run test:unit` | 87 | 94 |
| End-to-end + axe | `PYODIDE_URL=… npx playwright test` | 148 passed | 153 passed |
| Sitio estático | `python scripts/check_site.py` | (no existía) | PASS |
| Dependencias | `npm audit --audit-level=high`, `pip-audit -r backend/requirements.txt` | 0 vulnerabilidades | igual |
| Cursos DAW con Java, Android, migraciones en PostgreSQL, Gitleaks, Semgrep | — | No ejecutados aquí; los pasa la CI | — |

## 6. Rendimiento (medido, no estimado)

Medido con Chromium de Playwright contra `python -m http.server` local (sin compresión ni red real),
abriendo `#/leccion/variables`. Sirve para comparar versiones, no como dato de producción.

| Métrica | Valor |
|---|---|
| Peticiones al abrir una lección | 80 |
| Bytes transferidos (sin gzip) | ≈ 1,06 MB |
| JS importado al arrancar | 50 módulos, 498 KB (≈ 151 KB gzip) |
| CSS | 16 hojas, 144 KB (≈ 25 KB gzip) |
| Datos al arrancar | `lessons.json` 225 KB + `learning.json` 160 KB (≈ 101 KB gzip) |
| `DOMContentLoaded` | ≈ 250-290 ms (local) |
| Primera ejecución de Python (descarga e inicio de Pyodide, ≈ 14 MB en local) | ≈ 2,9 s |
| Ejecuciones siguientes | ≈ 80-90 ms |
| CLS | ≈ 0,10-0,11 |
| Errores de JavaScript en la carga | 0 |

GitHub Pages sirve con gzip y CDN, así que en producción el peso real es menor; el tiempo de Pyodide
depende de la red del alumno (≈ 10 MB desde jsDelivr la primera vez, después desde la caché del SW).

## 7. Seguridad

Resumen; el registro completo con evidencias está en [`security/SECURITY_FINDINGS.md`](security/SECURITY_FINDINGS.md).

- **Secretos**: ninguno en el frontend (`config.js` solo tiene datos públicos: la URL de la API, el email de
  contacto y el Client ID público de Google). Gitleaks se ejecuta en `security.yml`. Revisado.
- **Sesión**: cookie HttpOnly + token en memoria (ADR-0033), Argon2id, `token_version`, bloqueos por IP y
  cuenta. Verificado por `test_auth.py`, `test_session_cookie.py`, `test_attack_detection.py`.
- **Aislamiento entre cuentas**: verificado en todas las rutas privadas (`test_security_isolation.py`).
- **XSS**: todo el HTML pasa por `escapeHtml`/`renderMarkdown` seguro; la salida del Worker se trata como
  no fiable. Los datos importados nuevos pasan por los mismos limpiadores (`cleanLearning`, `cleanProgress`,
  `cleanGame`) y se prueban con cargas maliciosas (`tests/unit/progress-file.test.mjs`).
- **Ejecución de código**: el código del alumno **nunca llega al servidor**; corre en un Worker de Pyodide
  en su navegador, que tras cargar cierra el acceso a la red (PLD-SEC-004, mitigado con riesgo residual
  documentado). Límite de tiempo (10 s) y ahora detención manual; sin límite de memoria propio (el del
  navegador). No hay sandbox de servidor porque no hace falta: no se ejecuta código ajeno en el backend.
- **CSP**: en `<meta>` (Pages no permite cabeceras); la copia publicada quita los orígenes de desarrollo
  (PLD-SEC-003, en `pages.yml`).
- **Dependencias**: `pip-audit` y `npm audit` sin vulnerabilidades conocidas; falta el *lock* con *hashes*.

## 8. Limitaciones de GitHub Pages y de otros servicios

- Pages no ejecuta código de servidor ni permite cabeceras HTTP propias (de ahí la CSP en `<meta>`, sin
  `frame-ancestors`; la defensa anti-marcos está en `theme-init.js`).
- `404.html` se sirve en cualquier ruta, por eso es la única página con rutas absolutas.
- Render gratuito «duerme» el backend: la primera petición tras un rato tarda ≈ 1 minuto.
- Pyodide depende de jsDelivr la primera vez; sin red y sin caché, la consola no arranca (la web sí).
- Google Login y la recuperación por email necesitan configuración en Render que solo puede hacer el autor.

## 9. Accesibilidad

Automático y verificado: axe-core sin infracciones WCAG 2.1 AA en las vistas principales, en los dos
temas y en móvil; foco visible; menú móvil con `inert`; tablas con región desplazable; confeti desactivado
con `prefers-reduced-motion`; estados de lecciones con texto (no solo color). Novedades de esta rama:
«Detener» devuelve el foco a «Ejecutar», el buscador anuncia resultados con `role="status"` y Escape lo
vacía, y los errores de importación se anuncian.

**No declarado**: conformidad completa. Faltan las comprobaciones manuales de AUD-21 y la decisión sobre
el temporizador del simulacro (AUD-13). axe-core comprueba WCAG 2.1; los criterios nuevos de 2.2
(p. ej. 2.4.11 foco no oculto, 2.5.8 tamaño del objetivo) necesitan revisión manual.
