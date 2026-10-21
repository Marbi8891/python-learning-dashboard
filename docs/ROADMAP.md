# Hoja de ruta

> Actualizada el **21 de octubre de 2026** a partir de [`AUDIT.md`](AUDIT.md). Cada punto es un PR
> pequeño y revisable; el *merge* (que publica la web) lo hace siempre el autor.
> Prioridad: **P1** urgente, **P2** importante, **P3** mejora. Esfuerzo: S (< 1 día), M (1-3 días), L (más).

## Hecho en la rama `claude/project-thread-xl5vtb`

| Fase | Cambio | Criterio de aceptación (cumplido) |
|---|---|---|
| 2 | Botón «Detener» en la consola | Corta un `while True` sin esperar al límite; la siguiente ejecución funciona (`e2e/console.spec.js`) |
| 2/9 | Exportar e importar el progreso local | Archivo versionado; rechaza JSON inválido, otro formato, versión futura y > 2 MB; limpia HTML e ids raros; importar fusiona sin borrar (`progress-file.test.mjs`, `progress-backup.spec.js`) |
| 4 | Buscador de lecciones + «Solo pendientes» | Sin tildes ni mayúsculas, anuncia resultados, Escape lo vacía (`lesson-filter.spec.js`) |
| 5 | Tipos de resultado del corrector | Respuesta incorrecta, error de ejecución, tiempo agotado y fallo del corrector se ven distintos; el fallo del corrector no cuenta como intento |
| 3/17 | Prueba de humo del sitio y comprobación tras publicar | `check_site.py` falla con rutas absolutas, archivos o imports que faltan, JS o JSON rotos (`test_check_site.py`); `pages.yml` no publica si falla |
| 1 | `AUDIT.md`, `ROADMAP.md`; `ARCHITECTURE.md`, `TESTING.md`, `DEPLOY.md` y README al día | Coinciden con el código de esta rama |

## Decisiones que te tocan (bloquean trabajo, pero no el resto)

| ID | Decisión | Opciones | Recomendación |
|---|---|---|---|
| D1 | Simulacro PCAP sin límite de tiempo (AUD-13) | a) dejarlo como está (WCAG 2.2.1 admite el límite «esencial» de un examen); b) casilla «sin límite» cuyo resultado **no** cuenta para el certificado ni el logro «Aprobado» | b) — más accesible sin falsear el «aprobado» |
| D2 | *Lock* de pip con *hashes* (PLD-SEC-005) | a) `pip-tools` (`requirements.lock` con `--require-hashes`); b) seguir con rangos | a) — gratis y la propuesta ya está verificada en `docs/security/` |
| D3 | Casos ocultos en los ejercicios (AUD-18) | En una web estática **no hay casos realmente ocultos**: todo lo que el navegador ejecuta se puede leer. a) casos «no mostrados» (no se enseñan, pero están en el JSON); b) corrección en el backend (requiere ejecutar código ajeno en un servidor aislado: coste y riesgo) | a) — y decirlo con honestidad en la interfaz |
| D4 | Fuente del temario PCAP (AUD-19) | Revisar la página oficial de Python Institute y fijar versión y fecha en `pcap.json` | Hazlo tú o autoriza la consulta web; no se puede comprobar desde este entorno |

## Pendiente, por prioridad

### P2

| ID | Tarea | Depende de | Esfuerzo | Criterio de aceptación |
|---|---|---|---|---|
| R1 | Pistas progresivas en los ejercicios del núcleo educativo (`hints: [..]` en `scripts/learning/`, se muestran de una en una; la solución solo tras agotar pistas o pedirla) | — | M | `build_learning.py --check` valida que cada ejercicio de código tiene ≥ 1 pista; e2e muestra pista 1, luego 2, luego solución |
| R2 | Casos de prueba «no mostrados» (según D3) | D3 | M | Un ejercicio con dos casos visibles y uno no mostrado falla si la solución solo cubre los visibles |
| R3 | Prueba de paridad JS ↔ Kotlin del núcleo educativo (mismos datos de entrada → mismo dominio, repaso y plan) | — | M | Un JSON de casos compartido que leen `node --test` y JUnit |
| R4 | Pruebas manuales de accesibilidad documentadas (NVDA o VoiceOver, zoom 200 %, solo teclado en todas las rutas) y revisión de WCAG 2.2 (2.4.11, 2.5.8) | — | S | Lista en `docs/TESTING.md` con fecha, navegador y resultado de cada ruta |
| R5 | Simulacro sin límite (según D1) | D1 | S | e2e: el simulacro sin límite no muestra temporizador y no cuenta para el certificado |
| R6 | Temario PCAP con versión y fecha de revisión visibles; matizar «simulacros como el examen real» → «con el formato del examen» | D4 | S | `pcap.json` tiene `syllabusVersion` y `reviewed`; la portada del curso lo muestra |
| R7 | Lock de dependencias (según D2) | D2 | S | `pip install --require-hashes -r requirements.lock` en CI y Dockerfile |

### P3

| ID | Tarea | Esfuerzo | Criterio de aceptación |
|---|---|---|---|
| R8 | Conceptos nuevos del núcleo educativo: comprensiones, iteradores y generadores, entornos virtuales, pruebas con `unittest`/`assert` (AUD-20) | L | `build_learning.py --check` con los ejercicios nuevos ejecutados; mapa de conceptos actualizado |
| R9 | Itinerarios explícitos («Python desde cero», «DAM/DAW», «PCAP») con objetivos, prerrequisitos y criterio de finalización en `learning.json` | M | Cada itinerario se ve en `#/aprender` y su criterio de finalización se calcula con datos verificables |
| R10 | Reducir el CLS (≈ 0,10) reservando espacio para la barra lateral y el contenido de la lección | S | CLS < 0,05 en la medida de `AUDIT.md` §6 |
| R11 | Carga diferida: importar con `import()` las vistas que no se usan al arrancar (PCAP, DAW, panel, tutor) y pedir `lessons.json` solo cuando haga falta | M | Menos de 30 módulos al abrir `#/aprender`; e2e sin cambios |
| R12 | Consolidar las capas CSS de los rediseños y pasar `font-size` a `rem` | L | Mismas capturas en e2e; axe sin infracciones |
| R13 | Volver a aplicar el filtro de lecciones cuando cambie el progreso (AUD-22) | S | e2e: completar una lección con «Solo pendientes» la oculta |
| R14 | Prueba del modo sin conexión del service worker | S | e2e con `context.setOffline(true)` tras la primera visita |
| R15 | Proyectos de portfolio (calculadora, gestor de tareas, CSV/JSON, cliente de API pública, API con FastAPI) con enunciado, plantilla, criterios y tests | L | Cada proyecto tiene tests que se ejecutan en Pyodide o, si necesitan red o FastAPI, instrucciones para PyCharm |
| R16 | Partir archivos grandes (`programacion_course.py`, `exercises.py`, `dashboard.js`, `pcap.js`) | M | Mismas salidas `--check` y e2e |
| R17 | Actualizar `security/SECURITY_FINDINGS.md`: #55 ya está fusionado (AUD-10) | S | Lo hace `security-lead` tras comprobar la web publicada |

## Fuera de alcance por ahora (y por qué)

- **Ejecutar código de alumnos en el servidor**: no hace falta (Pyodide lo hace en el navegador) y
  exigiría un sandbox aislado con coste y riesgo. Solo se reconsidera con D3 b).
- **Tutor de IA de pago**: el autor no quiere APIs de pago. El tutor gratuito y el A2A con Ollama/mock ya
  están; OpenAI y Anthropic siguen desactivados (ADR-0038).
- **Cambiar de framework o de alojamiento**: no hay motivo técnico; GitHub Pages + Render cubren el uso actual.
- **Telemetría**: GoatCounter sigue desactivado; no se añade seguimiento externo.
