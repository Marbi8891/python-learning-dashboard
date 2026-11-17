# Especificación maestra · Excel profesional (proyecto «Excel Academy»)

**Versión:** 1.2 · **Fecha:** 17/11/2026 · **Estado:** el 17/11/2026 el propietario autorizó P1, la fusión del PR #159, la incorporación de estos documentos al repositorio y las 16 resoluciones de §4; P1 se fusionó (PR #164) y después autorizó P2 y fijó las decisiones DA-22 a DA-27 (ver §6). El resto de las decisiones pendientes de §7 siguen abiertas.
**Base comprobada:** `main` en `3b2dd8b`; rama `claude/project-thread-tr7z7w` en `ebda151` (PR #159, borrador, CI 7/7 en verde). Esta fase no ha modificado el repositorio, ninguna rama ni el PR.
Leyenda: **[H]** hecho comprobado · **[R]** recomendación · **[Hip]** hipótesis · **[D]** decisión pendiente.

Este documento es el **índice y la fuente principal de decisiones**. Si un anexo o un documento original lo contradice, manda este documento, y la contradicción se corrige en el anexo.

## 0. Índice

| N.º | Documento | Contenido |
|---|---|---|
| 1 | **MASTER_SPECIFICATION.md** (este) | Inventario, auditoría, consolidación funcional, contradicciones, registros de decisiones, trazabilidad y control de calidad |
| 2 | [ARCHITECTURE.md](ARCHITECTURE.md) | Componentes, servicios, estado, seguridad, rendimiento, accesibilidad, PWA; reutilizado frente a nuevo |
| 3 | [FUNCTIONAL_REQUIREMENTS.md](FUNCTIONAL_REQUIREMENTS.md) | RF-01…RF-29 y RNF-01…RNF-11 con aceptación y fase |
| 4 | [FORMULA_ENGINE_SPEC.md](FORMULA_ENGINE_SPEC.md) | Motor: sintaxis, tipos, errores, funciones, recálculo, límites, API; capacidades obligatorias, previstas, futuras y descartadas |
| 5 | [DATA_MODEL.md](DATA_MODEL.md) | Catálogo, contenido generado, documento de progreso |
| 6 | [API_SPECIFICATION.md](API_SPECIFICATION.md) | Endpoints existentes que usa el curso (no hay nuevos) |
| 7 | [CURRICULUM_M1_M2.md](CURRICULUM_M1_M2.md) | Las 9 unidades del piloto con ejercicios verificables |
| 8 | [TESTING_STRATEGY.md](TESTING_STRATEGY.md) | Línea base, regresión de DAW, pruebas por fase, umbrales |
| 9 | [SECURITY_AND_RISK_ASSESSMENT.md](SECURITY_AND_RISK_ASSESSMENT.md) | Amenazas, riesgos R-01…R-21, análisis del PR #159 |
| 10 | [IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md) | P0-P5 con equivalencias, criterios y esfuerzo |

Desde el 17/11/2026 están en `docs/excel-academy/` del repositorio (DP-02). Los diez documentos originales del 16/11 se conservan fuera del repositorio, en la carpeta compartida del proyecto.

---

## 1. Fase A · Inventario documental

### 1.1 Los diez documentos originales

Ubicación: `/mnt/project-files/excel-academy/docs/excel-academy/`. Los diez tienen fecha de archivo 16/11/2026 08:34 y versión única (no hay versiones anteriores ni duplicados de ninguno). **No están en el repositorio.** Se localizaron los diez.

| N.º | Título | Objetivo | Alcance funcional | Requisitos y decisiones técnicas clave | Depende de | Estado de aprobación |
|---|---|---|---|---|---|---|
| 01 | Auditoría de la arquitectura | Describir cómo funcionan cursos, lecciones, ejercicios y progreso en PLD | Lectura del código en `3b2dd8b` | AUD-XL-01…12; registro de un curso en 4 sitios | — | Informe (no se aprueba). **Desactualizado** en dos datos (§1.3) |
| 02 | Especificación funcional | Qué hace el curso | Usuarios, RF-01…20, RNF-01…08, indicadores, pantallas | Corrección formativa; tiempo estimado | 03, 06, 07 | Propuesta; RF-09/10 contradicen DA-11 |
| 03 | Arquitectura técnica | Cómo encaja en PLD | 4 familias, contratos JSON, archivos, Node y navegador | Catálogo genérico; campos `xlsx` y `rubrics`; motor en el hilo principal | 01, 04, 05 | Propuesta. La parte de P0 está implementada |
| 04 | Especificación del motor | Semántica del motor | Gramática, tipos, errores, 45 funciones, límites, API | Sin `eval`; máquina de estados; registro de funciones | 03 | Preparación del diseño autorizada; contenido sin aprobar |
| 05 | Especificación del lector XLSX | Leer .xlsx en el navegador | ZIP, XML propio, límites, rechazos | DecompressionStream; sin DOMParser en Node | 03, 04 | Propuesta. **En pausa** (DA-11) |
| 06 | Modelo de evaluación | Cómo se corrige | 4 modalidades, rúbricas, criterios de unidad | Funcional frente a procedimiento; formativa | 04, 07 | Propuesta |
| 07 | Currículo de 120 horas | Qué se enseña | 25 módulos, 53 unidades, 4 proyectos, MOS | Niveles 1-5; datos ficticios; etiquetas de versión | 06 | Diseño; sustituye a los 12 módulos de la propuesta |
| 08 | Plan de implementación | En qué orden | 5 fases; decisiones D1-D10 del 16/11 | P1a motor, P1b M1-M2, lector en pausa | Todos | Recoge la autorización del 16/11 |
| 09 | Plan de pruebas | Cómo se comprueba | P-UNI, P-INT, P-E2E, P-SEG, P-REN, P-ACC; criterios del piloto | ≥ 150 casos; ≥ 30 con Excel 365 | 04, 06, 08 | Propuesta |
| 10 | Registro de riesgos | Qué puede salir mal | R-01…R-15 | R-07 cerrado | Todos | Vivo |

### 1.2 Documentos relacionados

| Documento | Ubicación | Fecha | Papel |
|---|---|---|---|
| Propuesta inicial (12 módulos) | `/mnt/project-files/excel-academy/PROPUESTA_EXCEL_ACADEMY.md` | 15/11 16:43 | **Versión antigua**: la superan los docs 02-08. Se conserva por las pruebas de bibliotecas (§3) y la tabla de versiones (**[Hip]**) |
| Revisión de P0 | `/mnt/project-files/excel-academy/P0_REVISION.md` | 16/11 09:10 | Vigente; incluye el CI en verde |
| Script de prueba con LibreOffice | `/mnt/project-files/excel-academy/prueba-motor/mk2.py` | 15/11 | Evidencia de R-09 |
| DEC-018 | `docs/DECISIONS.md` en la rama del PR #159 | 16/11 | Decisión técnica de P0, en el repo |

### 1.3 Duplicados, versiones antiguas y datos desactualizados

| Hallazgo | Dónde | Resolución |
|---|---|---|
| Decisiones del 16/11 repetidas | Doc 08 §0 y mensaje de autorización | Este documento (§6) es ahora el registro único |
| Esquema de ejercicio repetido | Doc 03 §3.5 y doc 06 §3 | Coinciden; manda doc 06 por detalle; resumen en DATA_MODEL §3.2 |
| 12 módulos frente a 25 | Propuesta frente a doc 07 | Manda doc 07 (C-05) |
| «Cobertura del backend sin medir» | Doc 01 §1 | **[H]** hoy es 100 % (794 pruebas en la rama) |
| «196 unitarias, 792 backend» | Docs 01 y 09 | **[H]** en la rama: 200 y 794 |
| «Un curso se registra en `course-store.js`» | Doc 01 §2.1 | **[H]** tras P0, en `catalog.js` |

---

## 2. Fase B · Auditoría del repositorio

### 2.1 Documentado frente a implementado

| Elemento | Documentado en | Implementado | Evidencia |
|---|---|---|---|
| Catálogo por familias (`catalog.js`) | Doc 03 §2, DEC-018 | **Sí** (PR #159, sin fusionar) | `frontend/js/catalog.js`, 64 líneas |
| `DAW_COURSES` idéntico | Doc 08 Fase 1 | **Sí** | `catalog.test.mjs` (deep-equal con `main`) |
| Sincronización de `excel` | Doc 03 §3.7 | **Sí** | `course-store.js:133` recorre `SYNCED_COURSES`; e2e de fusión |
| `"excel"` en `COURSES` | Doc 03 | **Sí** | `backend/app/schemas.py:192` |
| Coherencia catálogo ↔ backend | Doc 09 P-INT-05 | **Sí** | `backend/tests/test_course_catalog.py` |
| Precache con `catalog.js` | — | **Sí** | `frontend/precache.js` |
| CHANGELOG y DEC-018 | — | **Sí** | `CHANGELOG.md` «Sin publicar»; `docs/DECISIONS.md` |
| Familias certificación e independiente | Doc 03 §2.1 | No (solo diseño, DA-04) | — |
| Motor de fórmulas | Doc 04 | **Sí (P1)**: 8 funciones, 37 previstas | `frontend/js/excel/formula/`; 194 casos de referencia |
| Tipos `formula-result`, `formula`, `rubric` | Doc 06 | **Sí (P1)** los dos primeros; `rubric` en P3 | `frontend/js/excel/checks.js`, `course_builder.py` |
| `module` opcional en el generador | Doc 08 Fase 4 | **Sí (P1)** | `course_builder.py`; `scripts/courses/tests/` |
| Ruta `#/academia/excel` y alias `#/excel-academy` | Docs 02, 03; DA-25 | **Sí (P2)** | `app.js`, `frontend/js/excel/course.js`; `e2e/excel.spec.js` |
| Contenido M01-M02 | Doc 07 | **Sí (P2)**: 9 unidades, 111 ejercicios | `scripts/courses/excel/m01.py`, `m02.py`; `frontend/data/academia/excel/` (DT-06) |
| Campos `xlsx` y `rubrics` | Doc 03 §3.7 | **No** | `progress-guard.js` sin cambios |
| Lector XLSX | Doc 05 | **No** (en pausa) | — |
| Indicadores del panel | Doc 02 §5 | **Parcial (P2)**: unidades completadas y superadas, ejercicios resueltos | `frontend/js/excel/progress.js`; resto en P3 |

### 2.2 Archivos revisados (rama del PR #159)

| Archivo | Estado | Observación |
|---|---|---|
| `frontend/js/catalog.js` | Nuevo | `DAW_COURSES` copiado tal cual; `ACADEMY_COURSES` con `excel` en `planned`; `SYNCED_COURSES`; `COURSE_FAMILIES`; `familyOf()` |
| `frontend/js/course-store.js` | Cambiado | Reexporta `DAW_COURSES`; recorre `SYNCED_COURSES` |
| `frontend/precache.js` | Regenerado | +`js/catalog.js` |
| `backend/app/schemas.py` | Cambiado | `"excel"` en `COURSES`; `MAX_PCAP_STATE_BYTES = 200_000` sin cambios |
| `backend/app/routers/course_state.py` | Docstring | Endpoints sin cambios |
| `backend/tests/test_course_catalog.py` | Nuevo | Coherencia, versión, 409, exportación |
| `tests/unit/catalog.test.mjs` | Nuevo | 4 pruebas |
| `e2e/excel.spec.js` | Nuevo | Fusión en dos sentidos; DAW con 6 tarjetas |
| `docs/DECISIONS.md` | Cambiado | DEC-018 (DEC-011…015 reservados por el PR #101) |
| `CHANGELOG.md` | Cambiado | Entrada en «Sin publicar» |

**Comprobado en esta fase (16/11, tarde):** `git status` limpio; `main` sigue en `3b2dd8b`; unitarias 200/200; `test_course_catalog.py` y `test_course_state.py` 10/10; PR #159 abierto, en borrador, sin conflictos, 0 comentarios, 7/7 checks en verde.

**Hallazgos nuevos:** la descripción del PR #159 dice que CI aún tiene que confirmar la batería completa, y ya lo hizo (R-18); `cleanProgress` deja pasar campos desconocidos sin limpiar (R-20); al fusionar, puede haber un 404 transitorio de `excel` si la web se despliega antes que el backend (R-16).

---

## 3. Fase C · Consolidación funcional

| Concepto | Definición consolidada | En el piloto | Detalle |
|---|---|---|---|
| **Catálogo** | Lista de cursos por familia en `catalog.js`. Familias activas: DAW y academia | Excel en academia, `planned` hasta P2 | DATA_MODEL §2 |
| **Rutas de aprendizaje** | El itinerario M01 → M25 con dependencias **recomendadas** (no bloquean) | M01 → M02 | CURRICULUM §3; doc 07 §2 |
| **Módulos** | Agrupan unidades; tienen horas, nivel y requisitos | M01 (10 h) y M02 (8 h); M03-M25 «próximamente» | CURRICULUM §6-7 |
| **Unidades y lecciones** | Una **unidad** es lo que el JSON llama `lessons[]`; una **lección** o apartado es cada parte de la unidad (explicación, ejemplos, test…) | 9 unidades | C-12 |
| **Ejercicios** | `choice`, `formula-result`, `formula`; `rubric` en P3; `xlsx` en P4 | 111 (58 T, 36 R, 17 F) | CURRICULUM §8 |
| **Simulaciones** | Simulacro por bloques al final de cada módulo, con datos nuevos y sin pistas (reutiliza el simulacro de DAW) | P3 | RF-28; C-11 |
| **Evaluaciones** | Formativas, en el navegador. «Superada» = criterios de la unidad | P3 | CURRICULUM §5 |
| **Progreso** | Documento `excel` (local y cuenta), los mismos campos que DAW | **[H]** sincroniza desde P0 | DATA_MODEL §4 |
| **XP y niveles** | **Sin XP ni logros en el piloto** (DA-07). «Nivel» es el nivel pedagógico 1-5 de cada pregunta, no gamificación | Indicador «nivel alcanzado» en P3 | C-03; DP-07 |
| **Certificados** | No hay certificado. Una constancia formativa imprimible es posible después (RF-16); una verificada exige corrección en el servidor (DP-10) | No | — |
| **Recursos descargables** | Plantillas .xlsx, aplazadas con el lector (DA-11) | No | C-06 |
| **Seguimiento** | Indicadores calculados del documento `excel` | Básicos en P2, completos en P3 | FUNCTIONAL_REQUIREMENTS §5 |
| **Relación con DAW** | Comparte código y API; no comparte progreso, vistas de lista, panel por módulo ni simulacro | DAW intacto (RF-23, RF-24) | TESTING §2 |

---

## 4. Contradicciones detectadas y resolución

| Id | Contradicción | Fuentes | Resolución (aprobada el 17/11/2026) | Estado |
|---|---|---|---|---|
| C-01 | Nombre «Excel Academy» frente a «Excel profesional» | Prompts del 15/11 y 16/11 tarde; autorización del 16/11 | Visible: «Excel profesional» (DA-01). «Excel Academy» solo como nombre interno del proyecto en documentos | Resuelta por DA-01 |
| C-02 | Ruta `#/academias/excel` frente a `#/academia/excel` | Propuesta; autorización | `#/academia/excel` (DA-02); los diez docs ya están corregidos | Resuelta |
| C-03 | «XP y niveles cuando corresponda» frente a «sin XP ni logros en el piloto» | Prompt del 16/11 tarde; autorización | Manda DA-07 en el piloto. Los niveles pedagógicos se mantienen. XP después del piloto: DP-07 | Resuelta para el piloto |
| C-04 | Numeración de fases: doc 08 (P1a/P1b, lector en Fase 3) frente a P0-P5 del prompt; «P2» de la autorización significaba «lo siguiente al piloto» | Doc 08; prompt; autorización | Tabla de equivalencias (ROADMAP §1); adoptar P0-P5 (DP-06) | Resuelta (DP-06 aprobada) |
| C-05 | 12 módulos frente a 25 módulos / 53 unidades / 120 h | Propuesta; doc 07 | Manda doc 07 | Resuelta |
| C-06 | RF-09/RF-10 (descarga y comprobación de .xlsx en el piloto) y correcciones «X» en M01-M02 frente a DA-11 | Docs 02 y 07; autorización | Aplazados a P4.3; en el piloto se sustituyen por ejercicios de cuadrícula | Resuelta |
| C-07 | 4 familias (doc 03) frente a 2 aprobadas | Doc 03; DA-04 | Solo DAW y academia; las otras, diseño | Resuelta |
| C-08 | 45 funciones especificadas frente a 8 en v1 | Doc 04; doc 08 | 8 obligatorias v1, 37 previstas con estado `planned` (DA-16) | Resuelta |
| C-09 | Doc 07 exige «1 práctica .xlsx o 1 rúbrica» por unidad | Doc 07 §3 | En el piloto, el mínimo se cambia por «ejercicios F en las unidades de fórmulas» | Resuelta en CURRICULUM §2 |
| C-10 | «Completada» frente a «superada» | Docs 02 y 06 | Las dos en el panel de Excel; DAW sin cambios | Resuelta (DP-13 aprobada) |
| C-11 | «Simulaciones» pedido en el prompt pero sin definir en ningún doc | Prompt del 16/11 tarde | Simulacro por bloques al final del módulo (RF-28) | Resuelta (DP-12 aprobada) |
| C-12 | «Lección» usado como unidad y como apartado | Docs 03 y 07 | Unidad = `lessons[]`; lección = apartado | Resuelta |
| C-13 | Recálculo y dependencias pedidos, pero el motor v1 no tiene grafo | Prompt; doc 04 | v1 evalúa una fórmula sobre datos estáticos; grafo futuro | Resuelta (DP-14 aprobada) |
| C-14 | Doc 01 da datos de pruebas antiguos | Doc 01; rama | Datos actualizados en TESTING §1 | Resuelta |
| C-15 | «20 pruebas e2e fallan» frente a CI verde | Prompt; CI | Los 20 fallos son del contenedor (proxy bloquea el CDN de Pyodide). En CI, todo verde | Resuelta |
| C-16 | Tolerancia de 0,005 por defecto frente a ejercicios de redondeo | Doc 06 §3.B | Tolerancia por ejercicio | Resuelta en CURRICULUM §7.3 |

---

## 5. Fases D a H: dónde está cada una

| Fase del prompt | Anexo |
|---|---|
| D · Motor de fórmulas | [FORMULA_ENGINE_SPEC.md](FORMULA_ENGINE_SPEC.md) |
| E · M1 y M2 | [CURRICULUM_M1_M2.md](CURRICULUM_M1_M2.md) |
| F · Arquitectura | [ARCHITECTURE.md](ARCHITECTURE.md), [DATA_MODEL.md](DATA_MODEL.md), [API_SPECIFICATION.md](API_SPECIFICATION.md) |
| G · Riesgos y regresiones | [SECURITY_AND_RISK_ASSESSMENT.md](SECURITY_AND_RISK_ASSESSMENT.md), [TESTING_STRATEGY.md](TESTING_STRATEGY.md) §2 |
| H · Hoja de ruta | [IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md) |

---

## 6. Registro de decisiones aprobadas

Fuentes: DA-01…17, mensaje del propietario «Autorización condicionada: Excel profesional en PLD», 16/11/2026 08:31; DA-18…27, mensajes del propietario del 17/11/2026.

| Id | Decisión | Efecto |
|---|---|---|
| DA-01 | Nombre visible **«Excel profesional»** | Textos de la interfaz; R-07 cerrado |
| DA-02 | Ruta **`#/academia/excel`** | `catalog.js` (**[H]**); rutas en P2 |
| DA-03 | Integración en el sistema de cursos existente | Reutilizar generador, vistas y almacén |
| DA-04 | Catálogo separado por familias: **DAW y academia** | **[H]** P0 |
| DA-05 | P0 primero; revisión; esperar autorización antes de P1 | **[H]** cumplido |
| DA-06 | P1 limitado al motor de fórmulas y M1-M2 (9 unidades) | Fases P1 y P2 |
| DA-07 | **Sin XP ni logros** en el piloto | `game.js` no se toca |
| DA-08 | Duración estimada, sin medir tiempo real | Indicador «tiempo estimado» |
| DA-09 | **Sin tablas ni migraciones** | Solo `"excel"` en `COURSES` (**[H]**) |
| DA-10 | Sin tocar la autenticación ni duplicar la sincronización | **[H]** P0 reutiliza la existente |
| DA-11 | **No desarrollar todavía el lector XLSX** | P4.3 con autorización |
| DA-12 | No empezar M3 ni posteriores | P4 |
| DA-13 | No publicar cambios en producción | Ninguna fusión sin el propietario; R-17 |
| DA-14 | No presentar los ejercicios corregidos en el navegador como evaluaciones seguras | RF-22 |
| DA-15 | Motor sin `eval` ni `Function`, con especificación semántica y pruebas independientes | RNF-03, MF-VAL |
| DA-16 | Separar las funciones implementadas de las que aún no lo están | Registro con `status` |
| DA-17 | No migrar el frontend a otro framework ni añadir dependencias sin justificar | RNF-01 |
| DA-18 | Autorizar P1 (motor y base funcional), 17/11/2026 | DP-03 cerrada. M1-M2 (P2) sigue necesitando autorización |
| DA-19 | Fusionar el PR #159 con CI en verde, 17/11/2026 | DP-05 cerrada |
| DA-20 | Incorporar estos documentos a `docs/excel-academy/`, 17/11/2026 | DP-02 cerrada |
| DA-21 | Dar por buenas las 16 resoluciones de §4, 17/11/2026 | Cierra DP-06 (numeración P0-P5), DP-12 (simulacro por bloques), DP-13 (completada y superada) y DP-14 (motor v1 sin grafo) |
| DA-22 | Autorizar P2 (contenido M1-M2), 17/11/2026 | DP-04 cerrada. Lector XLSX y M3+ siguen fuera |
| DA-23 | Al fusionar P2, el curso es **visible para todos**: `status: "active"`, entrada en el menú y en la portada, 17/11/2026 | DP-09 cerrada (en lugar de esperar a P5) |
| DA-24 | Esta especificación consolidada **prevalece** sobre la «Especificación funcional y técnica de Excel Academy» v1.0 recibida el 17/11/2026; de esa propuesta solo se toma lo compatible, fase a fase | Ver DA-25 a DA-27 |
| DA-25 | Ruta principal `#/academia/excel` con el **alias** `#/excel-academy` (reescribe a la principal) | `app.js` (P2) |
| DA-26 | Se mantienen: sin XP ni insignias en el piloto (DA-07); **tutor de IA fuera** del alcance; sin tablas nuevas (DA-09); progreso con el documento de curso de la cuenta; contenido en archivos versionados y generados | Rechaza las tablas `Excel*`, la API `/api/excel-academy/*` y el tutor de Ollama de la propuesta del 17/11 |
| DA-27 | Se mantienen los **25 módulos** y las fases P0-P5; los **cuatro proyectos empresariales** de la propuesta (finanzas, personal, inventario y cuadro de mando) se añaden al final, en M24-M25 (P4.5); el **laboratorio interactivo** libre se aplaza | Antes de un cambio incompatible se actualiza esta documentación; las decisiones aprobadas no se reabren sin justificación técnica |

**Decisiones técnicas tomadas dentro de P0** (en DEC-018, implementadas en el PR #159, pendientes de la revisión del propietario junto con el PR): DT-01 las fichas de DAW no llevan `family`; DT-02 el PCAP no entra en el catálogo; DT-03 Excel se sincroniza desde P0 aunque no se vea; DT-04 el catálogo es una constante JS, no un JSON descargado.

**Decisiones técnicas tomadas dentro de P2** (en DEC-020, pendientes de la revisión del propietario junto con su PR). Concretan DA-03 («reutilizar generador, vistas y almacén») sin cambiar su intención:

- **DT-05 · Vista propia en `frontend/js/excel/course.js` en lugar de ampliar `daw.js`.** Se reutilizan el generador (`course_builder.py`), el almacén (`course-store.js`, `lesson-progress.js`, repaso de `srs.js`), el Markdown seguro, la página 404 y los estilos de DAW. Motivo técnico: `daw.js` está atado a DAW (migas, currículo oficial del BOE, `DAW_COURSES`, tandas de práctica) y ampliarlo era el riesgo R-05; con un módulo aparte, DAW no cambia ni un byte (RF-23) y el motor solo se descarga en las rutas de Excel.
- **DT-06 · Los JSON del curso van en `frontend/data/academia/excel/`, no en `frontend/data/courses/`.** Esa carpeta la recorren como «cursos de DAW» las pruebas de DAW, el currículo, los recursos y el registro de ids; meter Excel allí obligaba a cambiar todas. Los ids de Excel tienen su propio registro estable, `scripts/courses/academia.lock.json`, que comprueba `backend/tests/test_excel_course.py`.

## 7. Registro de decisiones pendientes

| Id | Decisión | Recomendación | Estado |
|---|---|---|---|
| DP-01 | Aprobar esta especificación maestra | Revisarla; aprobar o pedir cambios | Pendiente |
| DP-02 | Incorporar estos documentos a `docs/excel-academy/` del repositorio | Sí, en un PR solo de documentación, después de DP-01 | Aprobada (DA-20) |
| DP-03 | Autorizar P1 (motor y base funcional) | Sí, tras revisar P0: no cambia nada visible | Aprobada (DA-18) |
| DP-04 | Autorizar P2 (contenido M1-M2) | Después de revisar P1 | Aprobada (DA-22) |
| DP-05 | Fusionar el PR #159 | Apto: CI verde, nada visible; antes, actualizar su descripción | Aprobada (DA-19) |
| DP-06 | Adoptar la numeración P0-P5 | Sí, con la tabla de equivalencias | Aprobada (DA-21) |
| DP-07 | XP y logros después del piloto | No decidir hasta tener los datos de P3 | Pendiente |
| DP-08 | Lugar del lector XLSX | P4.3, con autorización propia | Pendiente |
| DP-09 | Cuándo se ve el curso en la web publicada | No fusionar P2 hasta P5, o fusionarlo con `status: "planned"` | Decidida: visible al fusionar P2 (DA-23) |
| DP-10 | Evaluación verificada en el servidor | Después del piloto | Pendiente |
| DP-11 | Mapa con MOS MO-210/211 | Antes de M23; el propietario descarga la guía oficial | Pendiente |
| DP-12 | Definición de «simulación» | Simulacro por bloques al final del módulo | Aprobada (DA-21) |
| DP-13 | «Completada» y «superada» por separado | Sí, solo en Excel | Aprobada (DA-21) |
| DP-14 | Motor v1 sin grafo de dependencias | Sí; grafo cuando lleguen los proyectos | Aprobada (DA-21) |
| DP-15 | Dónde van las ejecuciones largas de pruebas | CI de GitHub desde la rama | Pendiente |
| DP-16 | Dependencias entre unidades como recomendación, no bloqueo | Sí, como en DAW | Pendiente |

---

## 8. Matriz de trazabilidad

Documento original → Requisito → Componente → Prueba → Fase.

| Doc. original | Requisito | Componente | Prueba | Fase |
|---|---|---|---|---|
| 03 §2 | RF-25 Catálogo por familias | `catalog.js` | P-UNI-09, REG-01, REG-02 | P0 **[H]** |
| 03 §3.7 | RF-29 Fusión del progreso | `course-store.js`, `sync-gate.js` | P-E2E-10 | P0 **[H]** |
| 03 | RNF-02 Sin tablas | `schemas.py` | P-INT-05, P-INT-03, P-INT-04 | P0 **[H]** |
| 01, 08 | RF-23 DAW intacto | `catalog.js`, `daw.js`, generador | REG-01…07 | Siempre |
| 04 §2.1 | MF-02, MF-03 Operadores y precedencia | `parser.js` | P-UNI-02 | P1 |
| 04 §3 | MF-04, MF-05 Referencias y hojas | `references.js` | P-UNI-03 | P1 |
| 04 §8 | MF-06 Copia | `shiftFormula` | P-UNI-03 | P1 |
| 04 §5 | MF-07 Errores | `errors.js` | P-UNI-06 | P1 |
| 04 §7 | MF-08 Límites | `evaluator.js` | P-SEG-03 | P1 |
| 04 §6, 08 | MF-09, MF-10 Registro y 8 funciones | `functions/*` | P-UNI-04, P-UNI-05 | P1 |
| 04 §1 | RNF-03 Sin `eval` | Motor | P-SEG-01 | P1 |
| 02 RNF-04 | RNF-04 < 50 ms | Motor | P-REN-01 | P1 |
| 04 §9 | RNF-09 Node = navegador | Motor, `eval.mjs` | P-INT-06 | P1 |
| 06 §3.B | RF-07 Resultado de fórmula | `checks.js`, generador | P-INT-01 | P1-P2 |
| 06 §3.C | RF-27 Escribir fórmula | `checks.js`, `views.js` | P-UNI-07, P-E2E-02 | P1-P2 |
| 02 §6 | RF-04, RF-05 Cuadrícula y editor | `views.js` | P-ACC-02, P-ACC-03 | P1-P2 |
| 02 | RF-01, RF-02, RF-26 Página y rutas | `app.js`, `daw.js` | P-E2E-01 | P2 |
| 07 §4 | RF-03 Unidades M01-M02 | `scripts/courses/excel/*` | P-INT-07 | P2 |
| 02 | RF-18, RF-22 Avisos | `daw.js`/`views.js` | e2e | P2 |
| 02 | RF-20, RNF-08 Accesibilidad | Vistas | P-ACC-01…03 | P2 |
| 03 §3.7 | RF-12 Completar y sincronizar | `course-store.js` | P-E2E-03…07 | P2 |
| 02 §5 | RF-14 Indicadores | Panel del curso | P-UNI-08 | P3 |
| 06 §5 | RF-21 Superada | Panel del curso | P-UNI-10 | P3 |
| 06 §4 | RF-11 Rúbricas | `views.js`, `progress-guard.js` | P-SEG-04 | P3 |
| — | RF-28 Simulacro | Simulacro de DAW | e2e | P3 |
| 04 §9 | MF-VAL-04 Excel 365 | Casos de referencia | P-EXT-01 | P3 |
| 05 | RF-09, RF-10 .xlsx | `excel/xlsx/*` | Doc 05 | P4.3 |
| 07 §2 | M03-M25 | Generador | — | P4 |

## 9. Control de calidad

| Comprobación | Resultado |
|---|---|
| Sin contradicciones entre anexos | Revisadas las referencias cruzadas DA, DP, RF, MF y R; las contradicciones con los originales están en §4 con su resolución |
| Cada requisito con id y aceptación | RF-01…29, RNF-01…11, MF-01…32 con aceptación o clase; los MF previstos se detallarán al empezar su módulo |
| Dependencias de módulos | M01-M02 en CURRICULUM §3; M03-M25 en doc original 07 §2 (columna «Requiere») |
| Arquitectura coherente con el código | Lo marcado **[H]** se comprobó en `ebda151` (rutas de archivo y líneas citadas) |
| Nada descrito como implementado sin estarlo | §2.1: solo P0 está implementado |
| Decisiones pendientes identificadas | §7, DP-01…16 |
| Hoja de ruta viable | ROADMAP §3: piloto viable (**[Hip]** 55-86 h); curso completo, solo por bloques |
| Respuestas de los ejercicios de ejemplo | Calculadas a mano y con Python el 16/11; el generador las recalculará |

**Lo que no se ha podido comprobar:** el temario oficial de MO-210/211 (el proxy bloquea Microsoft Learn); los nombres de funciones en un Excel 365 real; el comportamiento de despliegue automático de Render; la e2e completa con Pyodide en el contenedor (sí en CI).
