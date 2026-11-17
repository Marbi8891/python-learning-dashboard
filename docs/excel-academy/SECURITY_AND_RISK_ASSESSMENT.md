# Seguridad y riesgos · Excel profesional

**Anexo 9 de la [especificación maestra](MASTER_SPECIFICATION.md)** · Versión 1.0 · 16/11/2026.
Fuente: docs originales 05 (límites del lector), 06 §1 (límite de la corrección) y 10 (riesgos R-01 a R-15), revisados tras P0. Probabilidad e impacto: B baja · M media · A alta.

## 1. Modelo de amenazas del piloto

| Activo | Amenaza | Control | Estado |
|---|---|---|---|
| Navegador del alumno | Una fórmula o un texto del banco ejecuta código | Motor sin `eval`/`Function` (P-SEG-01); salida con `textContent` o escapado (P-SEG-02); CSP `script-src 'self'` sin cambios | Diseño (P1-P2) |
| Navegador del alumno | Fórmula que cuelga la pestaña (rango enorme, anidamiento, ciclo) | Límites del motor (P-SEG-03) | Diseño (P1) |
| Progreso del alumno | `localStorage` manipulado llega a la vista | `progress-guard.js`; añadir `rubrics`/`xlsx` cuando existan (P-SEG-04) | **[H]** para los campos actuales |
| Progreso en la cuenta | Otro usuario lo lee o escribe | Filas por `user.id` de la sesión; JWT/cookie con cabecera CSRF; sin cambios (DA-10) | **[H]** |
| Progreso en la cuenta | Documento enorme | 200 000 bytes en el validador; `BodySizeLimit` | **[H]** |
| Servidor | Abuso de escritura | `WritingUser` (límite de escritura) | **[H]** |
| Integridad de la nota | El alumno lee la solución del JSON público | **No se protege**: la corrección es formativa y se dice así (RF-22) | Aceptado (R-06) |
| Privacidad | Guardar fórmulas o tiempos del alumno | No se guardan (DATA_MODEL §4.2) | Diseño |
| Exportación y borrado (RGPD) | El progreso de Excel queda fuera | `courses.excel` en la exportación (**[H]** probado); el borrado elimina todas las filas | **[H]** |
| Lector XLSX (P4) | ZIP bomb, XXE, macros, archivos cifrados | Límites del doc original 05: 2 MB, 300 entradas, 10 MB por entrada, 40 MB total, ratio 200, 50 000 celdas; rechazo de `DOCTYPE`, macros y OLE; Worker con `terminate()` | En pausa (DA-11) |

## 2. Lo que la corrección no es

**[H]** En PLD los bancos de preguntas son JSON públicos y el navegador corrige. Solo los simulacros verificados del PCAP se corrigen en el servidor (`verified_exams.py`). Por eso, en Excel profesional:

- Ningún resultado se presenta como «verificado», «oficial» o «certificado».
- Las «variantes» de datos sirven para detectar fórmulas que solo funcionan con un ejemplo, no para impedir trampas.
- Una evaluación con valor externo exige corregir en el servidor (DP-10) y no entra en el piloto.

## 3. Registro de riesgos

| Id | Riesgo | P | I | Mitigación | Dueño | Estado |
|---|---|---|---|---|---|---|
| R-01 | El motor da un resultado distinto de Excel en casos raros | A | M | Subconjunto cerrado de 8 funciones; diferencias declaradas; casos de referencia con fuente; contraste con Excel 365 | Desarrollo | Abierto |
| R-02 | Volumen de contenido de 53 unidades | A | A | Piloto de 9 unidades; decidir la ampliación con datos (P3) | Propietario | Mitigado por DA-06 |
| R-03 | Excel no es un módulo de DAW y el tribunal puede preguntar por qué está | M | A | Defender la parte técnica (catálogo por familias, motor, sincronización) | Propietario | Abierto |
| R-04 | Romper DAW al generalizar el catálogo | B | A | REG-01 a REG-06 | Desarrollo | **Controlado en P0** (CI verde) |
| R-05 | `daw.js` (756 líneas) crece y se vuelve difícil de mantener | M | M | Tipos nuevos en `excel/views.js`; `daw.js` solo delega | Desarrollo | Abierto (P2) |
| R-06 | Corrección manipulable | Cierta | B | Formativa y dicha en la interfaz | Desarrollo | Aceptado |
| R-07 | Nombre «Academy» choca con el plan y con `academy.css` | — | — | Nombre visible «Excel profesional» (DA-01) | — | **Cerrado** |
| R-08 | Lector XLSX frágil o inseguro | M | M | Especificación con límites; en pausa | — | En pausa |
| R-09 | LibreOffice 24.2 no calcula funciones dinámicas | Cierta | M | Para v1 no importa (8 funciones clásicas); para P4, versión nueva o Excel 365 | Propietario | Abierto (P4) |
| R-10 | Contenido fiscal desactualizado | M | M | Tipos como datos, aviso, fecha de revisión | Propietario | No aplica al piloto (M15-M16) |
| R-11 | Nombres de funciones en español sin contrastar en un Excel real | M | M | P-EXT-01 | Propietario | Abierto (P3) |
| R-12 | El documento de progreso crece demasiado | B | B | 200 KB en el backend; mapas acotados; P-REN-03 | Desarrollo | Abierto |
| R-13 | Bajar la cobertura del backend | B | B | Toda línea de backend con su prueba | Desarrollo | **Controlado en P0** (100 %) |
| R-14 | Afirmar cobertura de MO-210/MO-211 sin haber leído la guía oficial | M | M | «Preparación complementaria» | Propietario | Abierto (M23) |
| R-15 | Uso de la marca Microsoft | B | M | Uso nominativo, sin logotipos, aviso de no afiliación (RF-18) | Desarrollo | Abierto (P2) |
| R-16 | **Nuevo.** Al fusionar el PR #159, la web llega antes que el backend y `GET /course-state/excel` da 404 unos minutos | M | B | La puerta de Excel reintenta 4 veces y no bloquea los demás cursos; el progreso de Excel está vacío hasta P2 | Desarrollo | Abierto, aceptable |
| R-17 | **Nuevo.** Fusionar P2 publica el curso, y la autorización del 16/11 dice «No publiques cambios en producción» | A | M | Decisión DP-09: no fusionar P2 sin autorización expresa de publicación, o fusionar con el curso oculto | Propietario | Abierto |
| R-18 | **Nuevo.** La descripción del PR #159 dice que CI tiene que confirmar la batería completa, y ya la confirmó | Cierta | B | Actualizar la descripción si el propietario lo pide (esta fase no toca el PR) | Desarrollo | Abierto |
| R-19 | **Nuevo.** Las dos numeraciones de fases (doc 08 y prompt del 16/11 tarde) llevan a autorizar lo que no se quería | M | M | Tabla de equivalencias en [IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md) §1 y DP-06 | Propietario | Abierto |
| R-20 | **Nuevo.** `cleanProgress` no limpia los campos que no conoce; un campo nuevo sin su limpieza llegaría a la vista sin validar | M | M | Añadir la limpieza en la misma fase que el campo; P-SEG-04 | Desarrollo | Abierto (P3) |
| R-21 | **Nuevo.** Tolerancia por defecto de 0,005 deja pasar fórmulas sin redondear en ejercicios de REDONDEAR | A | B | Tolerancia por ejercicio y aviso del generador (CURRICULUM §7.3) | Desarrollo | Mitigado en diseño |

## 4. Análisis del PR #159 (P0)

| Aspecto | Hallazgo | Evidencia |
|---|---|---|
| Estado | Abierto, en borrador, sin conflictos, 0 comentarios | GitHub, consultado el 16/11 |
| CI | **7 de 7 checks en verde** en `ebda151`: imagen Docker, artefacto de Pages, workflows y Render, e2e, cursos, backend y WebKit | GitHub Actions |
| Alcance | 12 archivos (286 líneas añadidas y 42 quitadas); ningún cambio de autenticación, base de datos, migraciones, vistas ni contenido | `git diff --stat 3b2dd8b ebda151` |
| Comportamiento visible | Ninguno en pantalla. Al iniciar sesión hay un GET y un PUT más (los de `excel`) | `e2e/excel.spec.js` |
| Contratos | `DAW_COURSES` idéntico; los importadores siguen funcionando por la reexportación | REG-01, REG-02 |
| Riesgos al fusionar | R-16 (404 transitorio, aceptable) | `sync-gate.js` |
| Pendiente | Descripción del PR desactualizada (R-18); pasar de borrador a listo y la fusión los hace el propietario | — |
| Recomendación | Apto para fusionar cuando el propietario lo revise. Fusionarlo publica la web, pero no cambia nada visible | — |

## 5. Normas del proyecto que se respetan

Sin secretos ni `.env` leídos; sin servicios de pago; sin dependencias nuevas; ningún JSON generado editado a mano; sin pruebas saltadas o debilitadas; ningún push a `main` ni fusión por parte de Claude; esta fase no modifica el repositorio.
