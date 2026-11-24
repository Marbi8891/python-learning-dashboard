# Pruebas de la Demo Edition

Qué se prueba de la Demo Edition ([DEMO-EDITION.md](DEMO-EDITION.md)), cómo se ejecuta y qué salió. No se
ha quitado ni debilitado ninguna prueba: todas las de antes siguen y pasan. La guía general está en
[TESTING.md](TESTING.md).

## Cómo se ejecutan

```bash
npm ci && python scripts/web/vendor_pyodide.py        # una vez

npm run test:unit                                     # unitarias de JS (node --test)
python scripts/demo/build_demo.py --check             # datos de Alex al día y válidos
cd backend && python -m pytest -q --cov=app --cov-fail-under=100 && cd ..
cd backend && ruff check . ../e2e ../scripts && ruff format --check . ../e2e ../scripts && cd ..
npx playwright test e2e/demo.spec.js --trace off      # e2e de la demo, el laboratorio y los cursos
npx playwright test --trace off                       # e2e completas
```

## Qué cubre cada prueba

| Prueba | Archivo | Comprueba |
|---|---|---|
| Datos de Alex | `scripts/demo/build_demo.py --check` (CI) | El JSON generado coincide con el script y cada lección, concepto, ejercicio, pregunta y semana existe en el temario real |
| Unitarias de la demo | `tests/unit/demo-data.test.mjs` | Fechas llevadas a hoy (también con cambio de hora), siembra, `PrefixedStorage` (nunca escribe una clave real), cada documento de Alex pasa intacto por la limpieza de su almacén, `demoDashboard` con la forma de `DashboardOut`, tiempo estimado |
| Unitarias del laboratorio | `tests/unit/lab-data.test.mjs` | 14 ejercicios, todos existen en `lessons.json` o `learning.json` y tienen pruebas; ejemplos; rutas |
| Unitarias de los cursos | `tests/unit/hub-data.test.mjs` | Siete cursos, lecciones y enlaces, cuenta de lo hecho, siguiente lección |
| Privacidad | `backend/tests/test_privacy_policy.py` | Toda clave del navegador empieza por `pld:` y la explica `privacidad.html` (la demo usa `pld:demo:` en `sessionStorage`) |
| E2E de la demo | `e2e/demo.spec.js` (9 pruebas) | Ver abajo |

`e2e/demo.spec.js`:

1. Entrar desde la portada sin registro: «Hola, Alex Developer», franja de aviso, la marca `?demo=1` se quita
   de la dirección, resumen determinista (6/27, «Programador/a en prácticas», 6 días, 7/20, tiempo
   estimado), ningún aviso de «Logro desbloqueado», las seis secciones del panel, perfil sin cuenta.
   **Cero peticiones al servidor** y **`localStorage` idéntico** antes y después. «Salir» vuelve a la portada,
   borra lo de la demo y deja intacto el progreso propio.
2. Reiniciar deshace lo que hizo el visitante.
3. Fuera de la demo no aparece nada de Alex ni la franja.
4. Laboratorio: ejecuta Python de verdad en Pyodide (`[1, 2, 3] 36`), color en el editor, error
   `ZeroDivisionError` con explicación, Detener un `while True`, ejercicio de diccionarios que falla y
   después pasa con sus pruebas reales, Restablecer y ejemplos.
5. El editor no atrapa el teclado: `Tab` sangra, `Esc` y `Tab` salen.
6. Cursos: siete tarjetas con su progreso real (PCAP 6/27, JavaScript 3/10, Ciberseguridad 1/16), lista de
   lecciones y «Continuar».
7. y 8. axe-core WCAG 2.2 AA sin infracciones en panel, laboratorio y cursos, en tema claro y oscuro.
9. A 320 px de ancho ninguna página nueva se desplaza en horizontal.

## Seguridad

| Punto pedido | Cómo se ha comprobado |
|---|---|
| Sin secretos en JavaScript | La demo no añade claves, tokens ni URLs nuevas; `alex.json` solo tiene datos ficticios |
| Sin cuentas reales ni datos de producción | `api.js` desactiva la API en la demo y la prueba e2e cuenta cero peticiones a `localhost:8000` u `onrender.com` |
| Datos de la demo separados | `sessionStorage` con prefijo `pld:demo:`; la e2e compara `localStorage` antes y después |
| Protecciones de Pyodide | Mismo Worker, mismo tiempo límite y mismo Pyodide propio (`frontend/pyodide/`); la e2e detiene un bucle infinito |
| Medidas existentes | CSP sin cambios (`scripts/security/production_csp.py`), sin `unsafe-inline`, sin scripts externos nuevos |
| CORS | El backend no cambia y la demo no hace peticiones; la configuración de `backend/app/config.py` sigue igual |
| Dependencias | Ninguna nueva. `npm audit`: 0 vulnerabilidades; `pip-audit`: sin avisos |

## Resultados (22/11/2026, en la nube)

| Comando | Resultado |
|---|---|
| `npm run test:unit` | 593 pasan, 0 fallan |
| `build_demo.py --check` | al día |
| `pytest` del backend | 951 pasan, 2 omitidas (ya lo estaban), cobertura 100 % |
| `ruff check` y `ruff format --check` | sin avisos |
| `e2e/demo.spec.js` | 9 de 9 pasan |
| `npx playwright test` (todas las e2e) | 293 de 293 pasan |
| `e2e/excel.spec.js` | la prueba WCAG que fallaba a veces en `main` (axe durante la animación) pasa 20 de 20 veces tras esperar a la animación |
| Comprobación del despliegue (`scripts/qa/verify_pages_artifact.py`, `scripts/qa/frontend_static.mjs`) | correcta |

La prueba `learn.spec.js` «en la lección se ve el índice del curso sin desplazar el menú lateral» falló en
CI con dos entradas nuevas en el menú (a 1440×900 empujaban el índice fuera de la pantalla). Se arregló sin
tocar la prueba: el menú tiene una sola entrada nueva, compacta («Todos los cursos»), y el laboratorio se
abre desde Practicar y desde Cursos.

## Lo que no se ha podido probar aquí

- La web publicada en github.io (no se puede abrir desde la nube): los pasos están en
  [DEMO-DEPLOYMENT.md](DEMO-DEPLOYMENT.md#después-de-fusionar).
- Lectores de pantalla reales (VoiceOver, NVDA): axe cubre lo automático, no sustituye una prueba con personas.
