# Demo Edition de PLD

Versión de Python Learning Dashboard que cualquiera puede abrir **sin registrarse**, como el alumno
ficticio **Alex Developer**, para ver el panel, el progreso, los cursos y ejecutar Python de verdad. Está
pensada para enseñarla a empresas, reclutadores, centros educativos y colaboradores.

No es otra aplicación: es la misma web, con la misma arquitectura (HTML, CSS, módulos ES, Pyodide en un
Web Worker, FastAPI, SQLAlchemy y PostgreSQL), con un modo demostración que no toca nada real.

| Documento | Qué cuenta |
|---|---|
| Este | Qué es, qué incluye, cómo se usa, decisiones y limitaciones |
| [DEMO-ARCHITECTURE.md](DEMO-ARCHITECTURE.md) | Cómo está hecho el aislamiento, los datos, el laboratorio y los cursos |
| [DEMO-DEPLOYMENT.md](DEMO-DEPLOYMENT.md) | Ejecutarla en local y publicarla |
| [DEMO-TESTING.md](DEMO-TESTING.md) | Pruebas, seguridad y resultados |

## Cómo se entra

- Desde la portada: **«Probar la demo sin registrarte»**.
- Con un enlace directo: `https://marbi8891.github.io/python-learning-dashboard/?demo=1#/panel`
  (en local, `http://localhost:5500/?demo=1#/panel`).

Una franja fija en todas las pantallas dice «Modo demostración. Alex Developer es un alumno ficticio…»
con los botones **Reiniciar** (vuelve a los datos de Alex) y **Salir de la demo** (borra todo lo de la
demo y vuelve a la portada). Cerrar la pestaña también lo borra.

## Qué incluye

| Lo pedido | Dónde está | Notas |
|---|---|---|
| Perfil de demostración, sin registro | `?demo=1` → `#/panel` | Alex Developer, sin correo ni datos personales |
| Nivel y XP | Panel, «Resumen» | Nivel 3, «Programador/a en prácticas», 590 XP. Los XP se calculan como siempre (`game.js`) |
| Progreso, lecciones hechas y ejercicios pendientes | Panel, `#/cursos`, `#/aprender` | 6 de 27 lecciones del curso PCAP; el ejercicio de «Funciones» empezado sin superar; «Colecciones» pendiente |
| Insignias | Panel, «Logros» | 7 de 20 (¡Hola, mundo!, Primer ejercicio, A la primera, Cazador/a de bugs, Quiz perfecto, Constancia, Primer simulacro) |
| Racha y actividad | Panel, «Resumen» y «Actividad» | Racha de 6 días que termina hoy, historial de 30 días y gráfica |
| Tiempo de estudio | Panel, «Resumen» | **Estimado**: 15 min por tarea del plan diario hecha (la web no mide el tiempo real). También fuera de la demo |
| Objetivos diarios y recomendaciones | Panel, «Planificación»; `#/aprender` | El motor adaptativo de siempre (`docs/ADAPTIVE_ENGINE.md`), sin IA |
| Laboratorio Python | `#/laboratorio` | Editor con color, Ejecutar, Comprobar, Detener, Restablecer, ejemplos y 14 ejercicios con pruebas reales |
| Centro de aprendizaje | `#/cursos` | Python, PCAP, Programación (DAW), JavaScript, Java, Bases de datos y Ciberseguridad, con su progreso y sus lecciones |
| Tema claro y oscuro, móvil, teclado | Todas | Mismo sistema de diseño; axe WCAG 2.2 AA en las páginas nuevas |

El laboratorio y el centro de cursos **también los usan los alumnos reales** (D4): enseñan lo mismo que la demo.

## Decisiones (aprobadas el 22/11/2026)

| | Decisión | Por qué |
|---|---|---|
| D1 | XP e insignias con el sistema que ya existía (Python y PCAP). POO y Excel siguen sin XP | Respeta las decisiones anteriores del proyecto |
| D2 | «Tiempo estimado» calculado, no inventado, y visible también fuera de la demo | Regla del proyecto: no inventar datos |
| D3 | Sin ejercicios nuevos | Variables y tipos ya tenían ejercicio con pruebas en sus lecciones (`lessons.json`); el laboratorio los reutiliza |
| D4 | Laboratorio y Cursos visibles para todos | Lo que se enseña en la demo es lo que hay |

## Seguridad y datos

- Los datos de Alex son ficticios y están en [`frontend/data/demo/alex.json`](../frontend/data/demo/alex.json),
  generado por `scripts/demo/build_demo.py`.
- En la demo nada se escribe en `localStorage` (donde está el progreso real) y **no sale ninguna petición
  al servidor**: ni sesión, ni sincronización, ni tutor IA. Lo comprueba `e2e/demo.spec.js`.
- El backend no cambia. No hay cuentas de demostración en la base de datos.
- La CSP, el Pyodide propio, el tiempo límite de ejecución y CORS siguen igual.

## Archivos

| Fase | Archivos nuevos | Archivos cambiados |
|---|---|---|
| 3. Datos ficticios | `frontend/js/demo/demo-mode.js`, `demo-data.js`, `scripts/demo/build_demo.py`, `frontend/data/demo/alex.json`, `tests/unit/demo-data.test.mjs` | `api.js`, `store.js`, `game.js`, `pcap-store.js`, `course-store.js`, `cybersecurity-store.js`, `console.js`, `certificate.js`, `career/career-store.js`, `career/finance-store.js`, `learn/learn-store.js`, `learn/planner-store.js`, `.github/workflows/ci.yml` |
| 4. Panel | `frontend/js/demo/demo-banner.js`, `frontend/css/demo.css` | `dashboard.js`, `dashboard-data.js`, `app.js`, `landing.js`, `index.html`, `i18n/en.json` |
| 5. Laboratorio | `frontend/js/lab/lab.js`, `lab-data.js`, `tests/unit/lab-data.test.mjs` | `console.js`, `app.js`, `index.html` |
| 6. Cursos y diseño | `frontend/js/hub/hub.js`, `hub-data.js`, `tests/unit/hub-data.test.mjs`, `e2e/demo.spec.js` | `app.js`, `index.html`, `css/demo.css` |
| 7. Pruebas | — | `e2e/excel.spec.js` (espera a la animación antes de axe: era inestable en `main`) |
| 8-9. Entrega | `docs/DEMO-*.md` | `precache.js`, `docs/TESTING.md`, `README.md`, `CHANGELOG.md` |

## Limitaciones conocidas

- **La actividad del panel es fija.** La lista «Actividad» y los intentos del curso PCAP son los de Alex;
  lo que haga el visitante en la demo cambia lecciones, XP, logros y dominio, pero no añade filas a esa lista
  (en una cuenta real la escribe el servidor).
- **El tema y el idioma** se guardan en las preferencias del navegador también en la demo (no son progreso).
- **La primera ejecución de Python** descarga unos 10 MB; con mala conexión tarda.
- **Solo en esta pestaña.** Abrir el enlace de la demo en otra pestaña empieza otra demo desde cero.
- **El tiempo estimado** es una aproximación (15 min por tarea del plan hecha), no un tiempo medido.
- Desde la nube no se ha podido abrir la web publicada en github.io: la comprobación final en producción la
  tiene que hacer una persona (ver [DEMO-DEPLOYMENT.md](DEMO-DEPLOYMENT.md)).
