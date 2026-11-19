# Estrategia de pruebas · Excel profesional

**Anexo 8 de la [especificación maestra](MASTER_SPECIFICATION.md)** · Versión 1.0 · 16/11/2026.
Fuente: doc original 09, actualizado con el estado real tras P0 y con los identificadores de requisitos de los anexos.

## 1. Línea base comprobada

| Batería | `main` (3b2dd8b, 16/11) | Rama del PR #159 (ebda151, 16/11) |
|---|---|---|
| `npm run test:unit` | 196/196 | **200/200** (4 nuevas en `catalog.test.mjs`); repetido en esta fase |
| Backend `pytest` | 792 superadas, 2 omitidas | **794 superadas, 2 omitidas, cobertura 100 %** |
| `ruff check` y `ruff format --check` | Limpio | Limpio |
| `--check` de los seis cursos de DAW | Al día | **JSON idéntico** |
| `build_precache.mjs --check` | Al día | Al día (añade `js/catalog.js`) |
| e2e en CI (Chromium completo, con Pyodide) | Verde | **Verde** (7 de 7 checks de CI en `ebda151`) |
| e2e local en el contenedor | 20 fallos por bloqueo de `cdn.jsdelivr.net` | Los mismos 20 (ajenos al cambio) |

**Corrección del dato «20 e2e fallan»:** esos fallos solo ocurren en el contenedor de trabajo, porque su proxy bloquea el CDN de Pyodide. En CI de GitHub, la batería completa está en verde. No hay ninguna prueba e2e fallando en el PR #159.

## 2. Regresión obligatoria de DAW (todas las fases)

| Id | Prueba | Dónde | Estado |
|---|---|---|---|
| REG-01 | `DAW_COURSES` igual al de `main` (ids, orden, campos) y sin `family` | `tests/unit/catalog.test.mjs` | **[H]** existe |
| REG-02 | `course-store.js` reexporta `DAW_COURSES` del catálogo | `catalog.test.mjs` | **[H]** existe |
| REG-03 | `#/daw/cursos` muestra 6 tarjetas y ninguna de Excel | `e2e/excel.spec.js` | **[H]** existe |
| REG-04 | Los seis `--check` de DAW sin un byte de diferencia | CI, job «cursos» | **[H]** existe |
| REG-05 | e2e de DAW, sincronización, panel, portada y currículo | `daw.spec.js`, `sync.spec.js`, panel, portada | **[H]** existen, verdes |
| REG-06 | Backend completo con cobertura 100 % | CI, job backend | **[H]** existe |
| REG-07 | El panel por módulo de DAW no cuenta Excel | e2e de panel | **[R]** añadir en P2, cuando Excel tenga progreso real |

Ninguna fase se da por terminada sin REG-01 a REG-06 en verde (CLAUDE.md: «Prohibido saltar o debilitar un test para que pase»).

## 3. Pruebas por fase

### P0 (hecho)

| Id | Qué | Archivo | Estado |
|---|---|---|---|
| P-UNI-09 | Catálogo y familias | `catalog.test.mjs` | **[H]** |
| P-INT-05 | Catálogo ↔ `COURSES` del backend | `backend/tests/test_course_catalog.py` | **[H]** |
| P-INT-03 | `GET/PUT /course-state/excel` con versión y 409 | `test_course_catalog.py` | **[H]** |
| P-INT-04 | La exportación incluye `courses.excel` | `test_course_catalog.py` | **[H]** |
| P-E2E-10 | Fusión de `done` de Excel en los dos sentidos al iniciar sesión | `e2e/excel.spec.js` | **[H]** |

### P1 (motor y base funcional)

| Id | Qué | Archivo | Umbral |
|---|---|---|---|
| P-UNI-01 | Tokenizer: números con coma, textos con `""`, booleanos, errores, `$`, hojas con comillas, posiciones | `tests/unit/excel-tokenizer.test.mjs` | Todos los tokens de MF-01 |
| P-UNI-02 | Parser: precedencia (`-2^2=4`, `2+3*4=14`, `2^3^2=64`, `"a"&1+1="a2"`), paréntesis, aridad, profundidad | `excel-parser.test.mjs` | |
| P-UNI-03 | Referencias y `shiftFormula` en filas y columnas; salida de la hoja → `#¡REF!` | `excel-references.test.mjs` | |
| P-UNI-04 | Las 8 funciones: normal, límite, inválido, anidado, error propagado, vacío | `excel-functions.test.mjs` | ≥ 6 casos por función |
| P-UNI-05 | Registro: toda `planned` da `#¿NOMBRE?` con «todavía no disponible»; ninguna sin firma | `excel-registry.test.mjs` | 37 `planned`, 8 `implemented` |
| P-UNI-06 | Errores y propagación; ciclo | `excel-errors.test.mjs` | |
| P-UNI-07 | Comprobaciones `value`, `fill`, `variants`, `references`, `noConstants`, `functions` | `excel-checks.test.mjs` | |
| P-INT-01 | El generador evalúa con `eval.mjs` y se para si una respuesta no cuadra o un error frecuente no falla | prueba Python del generador | |
| P-INT-02 | Con `module` opcional y tipos nuevos, los seis cursos de DAW generan el mismo JSON | CI | Byte a byte |
| P-INT-06 | Mismos casos de referencia en Node y en el navegador (la e2e importa el motor con `import()` en una página existente; no hace falta una página de prueba publicada) | `e2e/excel.spec.js` | 0 diferencias |
| P-SEG-01 | Sin `eval(`, `new Function`, `Function(`, `setTimeout("` en `frontend/js/excel/` | `excel-security.test.mjs` | |
| P-SEG-03 | Límites: 2 001 caracteres, 33 niveles, rango de 10 001 celdas, ciclo, presupuesto de pasos | `excel-limits.test.mjs` | |
| P-REN-01 | 500 celdas con copia hacia abajo | `excel-perf.test.mjs` | < 50 ms p95 en CI |
| P-REN-02 | Tamaño del motor | `excel-size.test.mjs` | < 60 KB |
| — | Casos de referencia del piloto | `tests/fixtures/excel/reference-cases.json` | **≥ 150, 100 % verde** |

### P2 (M1-M2)

| Id | Caso |
|---|---|
| P-INT-07 | `excel_course.py --check` en CI |
| P-E2E-01 | Enlace directo y recarga en `#/academia/excel`, una unidad y su práctica |
| P-E2E-02 | Fórmula correcta, con error de sintaxis y sin `$` que falla al copiar; mensajes en `role="status"` |
| P-E2E-03 | Anónimo: el progreso se guarda y sobrevive a recargar |
| P-E2E-04 | Con cuenta: completar en un contexto y verlo en otro |
| P-E2E-05 | 409: dos pestañas guardan a la vez y ninguna pierde lo suyo |
| P-E2E-06 | Sin conexión: se estudia, queda pendiente y se sube al volver |
| P-E2E-07 | Cerrar sesión borra `pld:course:excel`; otra cuenta no recibe el progreso (AUTH-02) |
| P-E2E-08 | = REG-03, más portada y panel de DAW sin cambios |
| P-E2E-09 | WebKit: prueba de humo del editor |
| P-SEG-02 | Una fórmula con `<script>` en un texto se muestra como texto |
| P-ACC-01 | axe 0 infracciones en curso, unidad y práctica, claro y oscuro |
| P-ACC-02 | Todo con teclado |
| P-ACC-03 | Cuadrícula como `<table>`; 320 px sin desplazamiento horizontal |

### P3 (evaluación y seguimiento)

| Id | Caso |
|---|---|
| P-UNI-08 | Indicadores (§5 de requisitos) con un documento sintético |
| P-UNI-10 | «Superada» frente a «completada» |
| P-SEG-04 | `localStorage` con `rubrics` manipulado: se limpia |
| P-REN-03 | Documento sintético máximo ≤ 60 KB (RNF-06) |
| P-EXT-01 | ≥ 30 casos contrastados con el Excel 365 del propietario |

## 4. Dónde se ejecutan

| Batería | Local (contenedor) | CI de GitHub |
|---|---|---|
| Unitarias, backend, ruff, `--check` | Sí | Sí |
| e2e sin Pyodide (DAW, sincronización, Excel) | Sí | Sí |
| e2e completa con Pyodide | No (proxy) | **Sí: es la fuente de verdad** |
| WebKit | No | Sí |

**[D]** DP-15: dónde van las ejecuciones largas (la memoria del proyecto no lo tiene registrado). Recomendación: CI de GitHub desde la rama.

## 5. Criterios cuantificables para aprobar el piloto

| Criterio | Umbral |
|---|---|
| Baterías existentes | 100 % verde; cobertura del backend 100 % |
| JSON de los cursos de DAW | 0 bytes de diferencia |
| Casos de referencia del motor | ≥ 150, 100 % verde, en Node y navegador |
| Casos contrastados con Excel 365 | ≥ 30, 0 diferencias no declaradas |
| Unidades | 9, con los mínimos |
| Ejercicios | ≥ 100 (previstos 111); cada F con un error frecuente rechazado |
| e2e de Excel | P-E2E-01 a 10 verdes |
| Accesibilidad | 0 infracciones de axe |
| Revisión del propietario | ≤ 3 fallos del corrector, todos corregidos |
