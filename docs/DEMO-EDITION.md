# Demo Edition de PLD

Estado: **Fases 1 y 2 terminadas (auditoría y diseño). Las fases 3 a 9 esperan autorización.**
Rama: `feat/demo-edition`, sobre `main` en `86ffa7d` (18/11/2026). El diseño técnico está en
[`DEMO-ARCHITECTURE.md`](DEMO-ARCHITECTURE.md). `DEMO-DEPLOYMENT.md` y `DEMO-TESTING.md` se escriben en las fases 8 y 9.

## Objetivo

Una versión que cualquiera pueda abrir sin registrarse, como el alumno ficticio **Alex Developer**, para
ver el panel, el progreso, los cursos y ejecutar Python de verdad. Se enseña a empresas, reclutadores,
centros educativos y colaboradores. No se reconstruye nada: se reutiliza lo que ya hay.

## Fase 1. Auditoría del repositorio

### Estado de Git y pruebas (medido el 18/11/2026 en la nube)

| Comprobación | Resultado |
|---|---|
| `git status` en `main` | Limpio, al día con `origin/main` (`86ffa7d`, PR #173) |
| Lint (`ruff check`) | Sin errores |
| Backend (`pytest --cov-fail-under=100`) | 808 pasan, 2 saltadas (necesitan PostgreSQL), cobertura 100 % |
| Frontend (`npm run test:unit`) | 507 de 507 pasan |
| End-to-end y axe (`npm run test:e2e`, Chromium, con Pyodide propio) | 248 pasan, 1 falla: «Excel profesional… WCAG en tema light» (`e2e/excel.spec.js:241`) |
| `npm audit --audit-level=high` | 0 vulnerabilidades |
| `pip-audit -r backend/requirements.txt` | Sin vulnerabilidades conocidas |

**Prueba inestable que ya está en `main`.** La de WCAG de Excel en tema claro falla 1 de cada 5 veces
(`--repeat-each=5`): axe mide un contraste de 4,01:1 (`#767f8c` sobre `#fefefe`) en un texto de 19 px.
Sola suele pasar. Parece que axe mide mientras cambia un color (transición). No es de la demo, pero en CI
haría fallar cualquier PR (`failOnFlakyTests`), así que conviene arreglarla antes de la Fase 3.

### Qué existe ya y se reutiliza

| Lo que pide la Demo Edition | Qué hay en el repositorio | Hueco |
|---|---|---|
| XP, niveles, racha, logros | `frontend/js/game.js` y `game-data.js`: XP calculados a partir de hechos, 7 niveles, racha por días, 20 logros. Se guardan en `pld:game` y en la cuenta | Nada nuevo: solo hay que cargarle datos ficticios |
| Panel del alumno | `#/panel` (`dashboard.js`, `dashboard-data.js`) con 7 secciones | Solo funciona con sesión iniciada y pide `/api/v1/dashboard` al backend |
| Motor adaptativo | `frontend/js/learn/` (dominio, repaso espaciado, `todayPlan`, planificador). Documentado en `ADAPTIVE_ENGINE.md` | Nada: recomienda a partir del estado `pld:learn` |
| Ejecutar Python | `python-runner.js` y `pyodide-worker.js`: Pyodide 314.0.7 servido desde la propia web, en un Web Worker, con tiempo límite de 10 s y botón Detener | No hay una página de laboratorio suelta: la consola vive dentro de cada lección |
| Resaltado de sintaxis | highlight.js propio en `frontend/vendor/highlight/` (Python, JS, Java, SQL) | El editor es un `textarea` sin color |
| Ejercicios con corrección | 387 ejercicios en `learning.json`, 63 de escribir código con pruebas reales | Variables, tipos y bucles no tienen ejercicios de código propios (los bucles se practican en acumuladores y recorridos) |
| Cursos | Python (27 lecciones), PCAP, POO (10 unidades), DAW: Programación (12), JavaScript (10), Java (10), Bases de datos (SQL, 14), Entornos, Lenguajes de marcas; Ciberseguridad (16 semanas); Excel profesional | Ninguno falta. No hay una vista única con el progreso de todos |
| Tema claro y oscuro, móvil, navegación lateral | Rediseño premium (#78-#86), `site-nav`, `theme-init.js`, auditoría axe WCAG 2.2 AA en e2e | Se mantiene |
| Seguridad | CSP de producción sin `unsafe-inline` en scripts, Pyodide propio, cookie HttpOnly, CORS con lista cerrada de orígenes | Se mantiene |

### Riesgos encontrados

1. **El progreso se guarda en cuanto se carga cada módulo.** Hay 12 almacenes que leen y escriben claves
   `pld:*` de `localStorage` al importarse (`store.js`, `game.js`, `learn-store.js`, `pcap-store.js`,
   `course-store.js`, `planner-store.js`, `cybersecurity.js`, `console.js`, `certificate.js`…). Si la demo
   escribiera ahí, **pisaría el progreso real del visitante en ese navegador**. Es el riesgo principal.
2. **Varios almacenes suben a la cuenta** (`/api/course-state/*`) si hay sesión. La demo no puede llegar a llamar a la API.
3. **El panel depende del backend.** Sin sesión, `#/panel` muestra «inicia sesión».
4. **Tiempo de estudio.** La web no mide el tiempo, y la regla del proyecto es no inventar datos (ni rachas, ni tiempos).
5. **E2E en la nube.** Las pruebas que cargan Google o el backend real no se pueden comprobar desde aquí;
   la web publicada (github.io) tampoco se abre desde la nube.

### Choques entre el encargo y decisiones anteriores

| Encargo | Decisión anterior | Propuesta |
|---|---|---|
| XP e insignias | «Sin XP» en POO y «sin XP ni insignias en el piloto» de Excel | La demo usa el sistema de XP que ya existe (Python y PCAP). POO y Excel siguen sin XP |
| Tiempo de estudio | No inventar datos | Mostrar «tiempo estimado» calculado con los minutos que el motor ya asigna a cada tarea hecha (`ACTION_MINUTES`), con la palabra «estimado». Sirve también fuera de la demo |
| Recomendaciones del motor adaptativo | El tutor IA y A2A se retiraron (#62); nada de APIs de pago | Solo el motor adaptativo local, sin IA |
| Cursos JavaScript, Java, Ciberseguridad | Existen | Se enlazan los cursos reales; nada «en desarrollo» salvo lo que ya lo esté |

## Fase 2. Diseño

Resumen (el detalle está en [`DEMO-ARCHITECTURE.md`](DEMO-ARCHITECTURE.md)):

- **Entrada:** botón «Probar la demo» en la portada, que abre `?demo=1#/panel`. Sin registro.
- **Aislamiento:** en modo demo todos los almacenes usan `sessionStorage` con el prefijo `pld-demo:` y
  `request()` se niega a llamar a la API. Cerrar la pestaña o pulsar «Salir de la demo» borra todo.
  El progreso real (`pld:*` en `localStorage`) no se lee ni se escribe.
- **Datos:** un único archivo `frontend/data/demo/alex.json`, generado por `scripts/demo/build_demo.py`
  (regla del proyecto: los JSON de `data/` salen de un script). Fechas relativas al día de entrada, con
  la misma forma siempre: es reproducible y la racha nunca sale caducada.
- **Aviso permanente:** franja «Modo demostración · Alex Developer es un alumno ficticio · Salir».
- **Panel:** el `#/panel` de siempre, alimentado por un adaptador local en vez de `/api/v1/dashboard`.
- **Laboratorio** `#/laboratorio`: editor con color, ejecución real con el mismo `PythonRunner`,
  consola, errores, Ejecutar, Restablecer, ejemplos y ejercicios con corrección.
- **Centro de aprendizaje** `#/cursos`: una tarjeta por curso con su progreso y sus lecciones.

### Decisiones que necesito

- **D1. XP e insignias:** ¿vale el sistema actual (Python y PCAP), dejando POO y Excel sin XP?
- **D2. Tiempo de estudio:** ¿«tiempo estimado» calculado, también fuera de la demo, o solo en la demo como dato ficticio?
- **D3. Ejercicios nuevos:** faltan ejercicios de código de variables y tipos. ¿Añado 2 de cada uno al
  núcleo (`scripts/learning/`, también para alumnos reales) o los dejo solo en el laboratorio?
- **D4. Laboratorio y Centro de aprendizaje:** ¿visibles para todos o solo en la demo?

Recomiendo en las cuatro la opción que sirve también fuera de la demo, porque así lo que se enseña es lo que hay.
