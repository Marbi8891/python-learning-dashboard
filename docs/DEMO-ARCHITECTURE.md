# Arquitectura de la Demo Edition

Diseño de la Fase 2. Nada de esto está implementado todavía. Contexto y decisiones pendientes en
[`DEMO-EDITION.md`](DEMO-EDITION.md).

## Principios

1. **La demo es la misma web**, no una copia. Mismos HTML, CSS, módulos ES, Pyodide y Web Worker. Sin
   frameworks ni dependencias nuevas.
2. **Aislamiento total del progreso real.** En modo demo no se lee ni se escribe ninguna clave `pld:*` de
   `localStorage` y no sale ninguna petición a la API.
3. **Datos ficticios, deterministas y a la vista.** Un solo archivo generado por script, con un aviso fijo en pantalla.
4. **Seguridad intacta.** La CSP, el Pyodide propio, el tiempo límite de ejecución y CORS no cambian.

## Cómo se entra y se sale

```
Portada ── «Probar la demo» ──▶ index.html?demo=1#/panel
                                     │
                     demo-mode.js (primer módulo que se evalúa)
                     ├─ ve ?demo=1 → sessionStorage["pld-demo:active"] = "1"
                     ├─ quita ?demo=1 de la barra de direcciones (replaceState)
                     ├─ carga data/demo/alex.json y lo siembra en sessionStorage["pld-demo:*"]
                     └─ exporta isDemo = true y storage = almacén con prefijo
```

- **Salir de la demo** borra las claves `pld-demo:*` y vuelve a `#/portada`, ya en modo normal.
- Cerrar la pestaña también lo borra todo (`sessionStorage` es por pestaña).
- Recargar dentro de la demo conserva lo que el visitante haya hecho en esa pestaña. «Reiniciar demo»
  vuelve a sembrar los datos de Alex.

## Módulo nuevo `frontend/js/demo-mode.js`

```js
export const isDemo;          // se decide una vez, al cargar
export const storage;         // localStorage en modo normal; sessionStorage con prefijo "pld-demo:" en la demo
export function exitDemo();   // borra pld-demo:* y recarga en modo normal
export function resetDemo();  // vuelve a sembrar a Alex
```

Los datos se siembran con un `await` de nivel superior **solo en modo demo**: los módulos que importan
`storage` esperan a que estén listos, así que leen ya los datos de Alex al evaluarse. En modo normal no se
descarga nada más.

### Cambios en los almacenes que ya existen

Es un cambio mecánico: `localStorage.getItem(KEY)` pasa a `storage.getItem(KEY)` en `store.js`, `game.js`,
`learn-store.js`, `pcap-store.js`, `course-store.js`, `planner-store.js`, `cybersecurity.js`,
`console.js`, `certificate.js`, `prefs.js` e `i18n.js`. `theme-init.js` se queda igual (se ejecuta antes
que los módulos y solo lee el tema).

- `api.js`: `apiEnabled` es falso en la demo y `request()` lanza un error claro si alguien la llama. Así
  ningún `uploader` ni `sync-gate` sube nada, y tampoco se despierta el servidor de Render.
- `store.clearLocalData()` sigue borrando solo `pld:*`; la demo tiene su propia limpieza.
- Una prueba unitaria y otra e2e comprueban que, tras usar la demo, `localStorage` está igual que antes
  y que no hubo ninguna petición a la API.

## Datos de Alex Developer

- Fuente: `scripts/demo/build_demo.py`. Salida: `frontend/data/demo/alex.json` (con `--check` en CI, como el
  resto de `data/`). El script valida cada id de lección, concepto, ejercicio y logro contra los JSON reales,
  para que la demo no se rompa cuando cambie el temario.
- Contenido: el mismo formato de cada documento (`completed`, `game`, `learn`, `pcap`, `planner`, curso de
  DAW), pasado por los `clean*` de siempre al cargarse.
- Fechas: se guardan como «hace N días» y se convierten al entrar. La forma es siempre la misma (por
  ejemplo, 6 días seguidos de actividad hasta hoy), así que la racha y el historial son reproducibles.
  Las pruebas fijan la fecha.
- Perfil propuesto: nivel «Programador/a en prácticas» (unos 450 XP), 9 de 27 lecciones de Python, 6
  logros, 40 preguntas del PCAP y 1 simulacro aprobado, 3 lecciones de JavaScript y 2 de SQL, y conceptos
  con distinto dominio para que el motor recomiende repasos y tareas nuevas.
- Todo dato es inventado. No hay email ni datos personales.

## Panel `#/panel` en la demo

`dashboard.js` pide hoy `/api/v1/dashboard` y `/dashboard/activity`. En la demo usa un adaptador
`demoDashboard()` que construye **la misma forma de respuesta** a partir de los almacenes locales, con
las funciones puras de `dashboard-data.js`. La sección «Mi perfil» muestra «Cuenta de demostración» y
oculta lo que solo tiene sentido con cuenta (cambiar contraseña, borrar cuenta, descargar datos).

Añadidos al resumen (también fuera de la demo, si se aprueba D4): saludo, objetivo diario (tareas de hoy
del planificador), tiempo estimado (D2) y las recomendaciones de `todayPlan`, cada una con su motivo.

## Laboratorio `#/laboratorio`

- **Editor:** `textarea` con una capa `pre > code` detrás, coloreada con el highlight.js que ya está en
  `vendor/`. El texto sigue siendo un `textarea`, así que el teclado, el lector de pantalla y deshacer
  funcionan como hasta ahora.
- **Ejecución:** el `PythonRunner` actual (Pyodide en Web Worker, límite de 10 s, Detener). No se simula nada.
- **Consola:** salida, errores con la línea y una explicación en español (la que ya da la consola de lecciones).
- **Botones:** Ejecutar (también `Ctrl/⌘ + Enter`), Detener, Restablecer y un selector de ejemplos.
- **Ejercicios:** los de código de `learning.json` de variables, tipos, condicionales, bucles
  (acumuladores y recorridos), funciones, listas, diccionarios y POO, corregidos con sus `checks` reales.
  Faltan los de variables y tipos (D3).
- En la demo, superar un ejercicio actualiza el progreso de Alex; fuera de ella, el del alumno.

## Centro de aprendizaje `#/cursos`

Una tarjeta por curso: Python, PCAP, Programación (DAW), JavaScript, Java, Bases de datos y
Ciberseguridad, con el progreso que ya guarda cada almacén y el enlace a sus lecciones. Si un curso no
tiene contenido, la tarjeta dice «En desarrollo» en lugar de inventarlo. Hoy los siete tienen lecciones.

## Archivos previstos

| Fase | Archivos |
|---|---|
| 3 | `frontend/js/demo-mode.js`, `scripts/demo/build_demo.py`, `frontend/data/demo/alex.json`, almacenes, `api.js`, `tests/unit/demo-mode.test.mjs`, `backend/tests/test_demo_data.py` |
| 4 | `dashboard.js`, `dashboard-data.js`, `landing.js`, `index.html`, CSS, `e2e/demo.spec.js` |
| 5 | `frontend/js/lab.js`, `index.html`, CSS, `e2e/lab.spec.js`, y según D3 `scripts/learning/` |
| 6 | CSS, `e2e/a11y.spec.js` (rutas nuevas), navegación |
| 7-9 | `precache.js`, `DEMO-TESTING.md`, `DEMO-DEPLOYMENT.md`, README, CHANGELOG |

El backend no cambia: la demo no necesita servidor.

## Lo que no se hace

- Ninguna cuenta demo en el backend ni datos en PostgreSQL.
- Ni tutor IA ni APIs de pago.
- Ningún cambio en la CSP, el worker de Pyodide ni CORS.
- Nada de XP en POO ni en Excel.
