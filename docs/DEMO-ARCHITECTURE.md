# Arquitectura de la Demo Edition

Cómo está hecha la Demo Edition ([DEMO-EDITION.md](DEMO-EDITION.md)). Todo es frontend: el backend no cambia.

## Principios

1. **La demo es la misma web**, no una copia: mismos HTML, CSS, módulos ES, Pyodide y Web Worker. Sin
   frameworks ni dependencias nuevas.
2. **Aislamiento total del progreso real.** En la demo no se lee ni se escribe ninguna clave `pld:*` de
   `localStorage` y no sale ninguna petición a la API.
3. **Datos ficticios, deterministas y a la vista.** Un solo archivo generado por script y una franja fija en pantalla.
4. **Seguridad intacta.** La CSP, el Pyodide propio, el tiempo límite de ejecución y CORS no cambian.

## Entrada y salida

```
Portada ── «Probar la demo» ──▶ index.html?demo=1#/panel
                                     │
                    demo/demo-mode.js (lo importan api.js y todos los almacenes)
                    ├─ ve ?demo=1 → la quita de la dirección (replaceState)
                    ├─ descarga data/demo/alex.json
                    ├─ siembra sessionStorage["pld:demo:<clave>"] con las fechas llevadas a hoy
                    └─ export isDemo = true; export storage = almacén con prefijo
```

- `isDemo` se decide **una vez**, con un `await` de nivel superior. Como los almacenes importan
  `demo-mode.js`, el navegador espera a que termine antes de evaluarlos: cuando leen, ya están los datos de Alex.
  Fuera de la demo no se descarga nada y `storage` es el `localStorage` de siempre.
- Recargar dentro de la demo conserva lo que el visitante haya hecho en esa pestaña.
- **Reiniciar** vuelve a sembrar y recarga. **Salir** borra `pld:demo:*`, la marca de la pestaña y recarga en `#/portada`.
- Si `alex.json` no carga, la web sigue en modo normal (sin demo) y lo dice en la consola.

## Aislamiento

| Pieza | Cambio | Efecto en la demo |
|---|---|---|
| `demo/demo-data.js` | `PrefixedStorage`: la interfaz de `localStorage` sobre `sessionStorage` con el prefijo `pld:demo:` | Nada se mezcla con `pld:*` |
| Almacenes (`store.js`, `game.js`, `pcap-store.js`, `course-store.js`, `cybersecurity-store.js`, `learn/learn-store.js`, `learn/planner-store.js`, `career/*-store.js`, `console.js`, `certificate.js`) | `localStorage.getItem/setItem/removeItem` → `storage.…` | Leen y guardan en la pestaña |
| `api.js` | `apiEnabled` es falso y `request()` lanza un error claro | No hay sesión, ni subidas, ni tutor IA, ni se despierta Render |
| `store.js` | `state.demo` | El menú enseña «Mi panel» y el panel tiene alumno |

Se quedan en `localStorage` las preferencias (tema, letra, idioma: `prefs.js`, `i18n.js`, `theme-init.js`),
que no son progreso y que `theme-init.js` necesita leer antes de que carguen los módulos.

## Datos de Alex Developer

- **Fuente:** `scripts/demo/build_demo.py` → `frontend/data/demo/alex.json` (con `--check` en CI). Nadie
  edita el JSON a mano.
- **Validación:** el script comprueba que cada lección, concepto, ejercicio, pregunta y semana existe en los
  JSON reales; `tests/unit/demo-data.test.mjs` comprueba que cada documento pasa intacto por la limpieza de
  su almacén (`cleanGame`, `cleanLearning`, `cleanPlanner`, `cleanProgress`, `cleanCyber`).
- **Fechas:** absolutas alrededor de `anchor` (20/11/2026). Al entrar, `shiftDates` desplaza todas (valores y
  claves con forma de día) para que `anchor` sea hoy. Las horas son de tarde en UTC, lejos de medianoche, para
  que el día local no cambie en Europa ni en América. Mismo día, mismos datos: es reproducible.
- **Logros:** vienen ya ganados en el documento, así que entrar no lanza el aviso de «Logro desbloqueado».

## Panel `#/panel`

`dashboard.js` pedía `/api/v1/dashboard` y `/dashboard/activity`. En la demo, `loadDemo()` construye **la
misma forma de respuesta** (`DashboardOut` de `backend/app/schemas.py`) con `demoDashboard()`: lecciones del
progreso de la pestaña e intentos de la actividad ficticia. La cabecera cambia «Cerrar sesión» por
«Reiniciar la demo» y «Salir de la demo», y «Mi perfil» explica que no hay cuenta (sin contraseña, borrado
ni descarga de datos).

El resumen añade **Tiempo estimado** (`estimatedStudyMinutes` en `dashboard-data.js`): tareas del plan
diario marcadas como hechas en 30 días × 15 min. Sin tareas hechas muestra «—», no un cero inventado.

## Laboratorio `#/laboratorio`

```
lab/lab-data.js   temas, ejercicios y ejemplos (puro, probado con node --test)
lab/lab.js        vista: lista, enunciado, editor, consola y comprobación
       │
       └─ console.js → pythonRunner (el mismo Worker de Pyodide de las lecciones)
```

- **Editor:** un `textarea` real con el texto transparente encima de una capa `pre > code` coloreada con el
  highlight.js de `vendor/`. El teclado, el lector de pantalla, seleccionar y deshacer funcionan como en
  cualquier campo. `Tab` inserta 4 espacios; `Esc` y después `Tab` salen del editor (sin trampa de teclado).
- **Ejecución:** `runner.run()` y `runner.check()` en el Web Worker, con el tiempo límite y «Detener».
  Los errores muestran la explicación en español que ya genera `py/runner.py`.
- **Ejercicios:** 14, todos del temario y con sus pruebas: el ejercicio de las lecciones Variables, Tipos,
  Condicionales, Bucles, Funciones, Colecciones y POO (`lessons.json`) y 7 ejercicios de código del núcleo
  (`learning.json`). Superar uno cuenta como en su sitio de origen: XP y lección (`recordExercise`,
  `recordAttempt`) o dominio del concepto (`mastery.recordAttempt`).
- **Ejemplos:** el código de ejemplo de 7 lecciones.
- Los borradores se guardan por ejercicio (`pld:lab-draft:<id>`, en la demo con el prefijo).

## Centro de aprendizaje `#/cursos`

`hub/hub-data.js` define los siete cursos y cómo se cuenta lo hecho en cada uno; `hub/hub.js` los pinta.

| Curso | Lecciones | Hecho |
|---|---|---|
| Python | conceptos de `learning.json` | concepto dominado (motor adaptativo) |
| PCAP | `lessons.json` (+ enlace a la zona de examen) | lección completada |
| Programación, JavaScript, Java, Bases de datos | `data/courses/<id>/lessons.json` | lección completada (`done` del curso) |
| Ciberseguridad | semanas de `cybersecurity/course.json` | semana completada |

Un curso que no carga se queda en su tarjeta con un aviso, sin romper los demás; uno sin lecciones dice
«En desarrollo». Los siete tienen contenido.

## Carga diferida y sin conexión

El laboratorio y el centro de cursos son zonas de carga diferida en `app.js`, como el resto de secciones
grandes. Sus archivos y `data/demo/alex.json` están en `precache.js`, así que funcionan sin conexión
después de la primera visita.

## Lo que no se hace

- Ninguna cuenta de demostración en el backend ni datos en PostgreSQL.
- Ni tutor IA ni APIs de pago.
- Ningún cambio en la CSP, el worker de Pyodide ni CORS.
- Nada de XP en POO ni en Excel.
