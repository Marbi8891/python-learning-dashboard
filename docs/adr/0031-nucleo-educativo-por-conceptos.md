# ADR-0031: Núcleo educativo por conceptos (aprender Python y aprobar Programación de DAW)

- **Estado:** Aceptada e implementada en la web (fases 1-3). La app Android, en la fase 4.
- **Fecha:** 2026-10-04
- **Revisa:** ADR-0009 (enfoque PCAP), ADR-0005 (gamificación), ADR-0021 (cursos DAW en la web)

## Contexto

El autor redefine el objetivo de la plataforma. Tiene dos objetivos, los dos prioritarios:

1. **Aprender Python** entendiendo lo que hace, no solo marcando respuestas.
2. **Aprobar la parte de programación de DAW.**

Pide un ciclo concepto → explicación → ejemplo → intento → error/acierto → explicación → nuevo intento → repaso → dominio. También quiere una teoría visible y un «¿qué estudio ahora?». El PCAP y la gamificación pasan a ser secundarios (fase 5).

Lo que había al empezar se auditó antes de tocar nada:

| Pieza | Estado | Decisión |
|---|---|---|
| `lessons.json`: 27 lecciones con teoría, ejemplo, ejercicio corregido por Pyodide, quiz y reto | Funciona | **Se reutiliza.** Su teoría es la de la sección Teoría, y la lección completa se enlaza para practicar con consola |
| Consola, `runner.py` y Worker con límite de tiempo | Funciona | **Se reutiliza** para los ejercicios de escribir código, con el mismo Worker (`pythonRunner`) |
| Curso `programacion`, UT1-UT9 | Funciona, sincronizado con la app | **Se conserva** como «temario del centro» dentro de DAW |
| `/api/course-state/{curso}` | Guarda un JSON por curso | **Se reutiliza** con el id `learn`. No hacen falta tablas ni migraciones |
| Progreso por lección o por pregunta | No dice qué **concepto** se domina | **Falta.** Es la causa de que no se pudiera recomendar nada |
| Fallos guardados como `true`/`false` | No dicen **por qué** se falla | **Falta** |
| Navegación y portada centradas en el PCAP | Contradicen el nuevo objetivo | **Se reorganizan.** El PCAP pasa a «Más» y no se borra nada |
| Tests del frontend | Solo e2e | **Faltan** tests unitarios de la lógica |

## Opciones

| Opción | Veredicto |
|---|---|
| A. Etiquetar a mano por concepto las 126 preguntas del PCAP y las 163 del curso de Programación | Descartada. Esas preguntas siguen otros temarios (una certificación y otro instituto) y no tienen errores típicos por opción. Habría que reescribirlas igualmente, y cambiaría el progreso que ya está sincronizado con la app |
| **B. Mapa de conceptos con errores típicos y ejercicios propios, generado y comprobado por un script, que reutiliza la teoría existente** | **Elegida** |
| C. Reescribir la web en un framework | Descartada: el autor no lo quiere y no aporta nada al aprendizaje |

## Decisión

### Datos: `frontend/data/learning.json`

Se genera con `scripts/learning/build_learning.py` a partir de `concepts.py` y `exercises.py`, siguiendo el mismo patrón que `scripts/courses/`.

- **22 conceptos** en 4 áreas (Fundamentos, Programación, Lógica y Más adelante). Cada uno tiene:
  - prerrequisitos;
  - importancia para DAW, de 1 a 3;
  - su unidad de trabajo del curso de Programación;
  - teoría propia **solo** si no hay una lección que ya la cubra; si la hay, se reutiliza la de `lessons.json`;
  - un ejemplo explicado **línea a línea**;
  - «cuándo usarlo»;
  - sus **errores típicos**: qué falla, por qué está mal, cómo pensarlo y cómo evitarlo.
- **Ruta recomendada (`PATH`):** intercala la lógica (pseudocódigo, trazado, depuración) con el lenguaje en cuanto se puede practicar, en lugar de dejarla para el final.
- **111 ejercicios de 6 tipos:**
  - elegir opción;
  - predecir la salida (trazado);
  - completar el hueco;
  - ordenar líneas de código o de pseudocódigo;
  - encontrar la línea con el error;
  - escribir el programa, corregido con tests.
- **Cada respuesta incorrecta frecuente lleva el error que delata:**
  - la opción elegida;
  - la salida típica equivocada (`traps`);
  - el test que falla (`checks[].error`).

  Así, un fallo queda registrado con su causa.
- **Nada se escribe «a ojo».** El script ejecuta con el mismo `runner.py` del navegador:
  - cada salida esperada;
  - cada hueco completado;
  - cada línea corregida (y comprueba que la versión con el error **no** da la salida correcta);
  - cada solución.

  Además, comprueba que las **soluciones equivocadas típicas fallan justo en el test que delata ese error**. La CI ejecuta `--check`.

### Lógica: `frontend/js/learn/`

Son funciones puras, probadas con `node --test`, sin dependencias nuevas.

- **`mastery.js`: dominio de un concepto.**
  - Se cuentan los ejercicios cuyo **último** intento fue correcto, ponderados por nivel, sobre el **total** de ejercicios del concepto. No basta con acertar uno.
  - **Dominado:** 80 % o más, al menos un ejercicio de aplicación acertado y ningún error activo.
  - **Un error está activo** hasta que se aciertan 2 ejercicios que lo detectan, o hasta que pasan 21 días sin repetirlo.
  - **Repaso espaciado por concepto** (cajas de Leitner a 1, 3, 7, 14 y 30 días, como el PCAP), al cerrar cada sesión.
  - **Limpieza (`cleanLearning`)** de lo que llega de `localStorage` o de la cuenta, con la misma idea que `progress-guard.js` (ADR-0022), y **fusión** con la copia de la cuenta.
- **`recommend.js`: plan de «Hoy»** con la prioridad que pidió el autor:
  1. repasos pendientes;
  2. errores recientes;
  3. conceptos importantes para DAW sin dominar;
  4. contenido nuevo, solo si sus prerrequisitos llegan al 60 %; si no, «Necesitas reforzar X antes de pasar a Y»;
  5. repaso general.
- **`recommend.js`: selección de ejercicios.** Por orden, se eligen los que detectan errores activos, los fallados y los nuevos. Se evitan los ya dominados y los que están muy por encima del nivel actual, y se ordenan de fácil a difícil.
- **`session.js`: el ciclo completo.**
  - Un fallo programa un **nuevo intento** al final, con un ejercicio **parecido** que detecte el mismo error, como máximo 3 por sesión.
  - Si se repite el mismo ejercicio, ese intento no cuenta para el dominio, porque la explicación ya enseñó la respuesta.
  - La nota de la sesión cuenta **solo los primeros intentos**.
  - En los simulacros no hay corrección hasta el final y hay tiempo límite.

### Web

**Menú principal:** Aprender · Teoría · Practicar · DAW · Progreso. En «Más» quedan el curso PCAP, el examen PCAP y Mi cuenta.

- **Barra lateral:** la tarjeta de XP y las lecciones del PCAP solo aparecen en la zona del PCAP. El asistente de cada lección, también.
- **`#/aprender`:** el plan de hoy con su motivo, los puntos débiles, los repasos pendientes, el progreso y la última actividad. No hay un panel de estadísticas.
- **`#/teoria`:** índice por áreas y, para cada concepto:
  - explicación;
  - ejemplo línea a línea con su salida real;
  - cuándo usarlo;
  - errores habituales;
  - relación con otros conceptos;
  - ejercicio corto;
  - enlace a la lección con consola.
- **`#/practicar`:** repaso de hoy, **mis errores** (con «Practicar este error»), práctica por tipo de actividad (lectura de código, detectar errores, completar, escribir programas) y por concepto.
- **`#/progreso`:** dominio, estado y próximo repaso de cada concepto, errores más frecuentes (pendientes o corregidos), actividad reciente y simulacros. «Mi aprendizaje» (XP y logros) se enlaza como secundario.
- **`#/sesion`:**
  - en un concepto nuevo, se empieza por el concepto y su ejemplo;
  - tras cada respuesta: veredicto, «cómo pensarlo» y, si se reconoce, el error típico con su explicación;
  - al final: resumen con los errores explicados y la siguiente recomendación.
- **Markdown:** admite bloques de código y tablas, siempre escapados.
- **Diseño:** se quitan los degradados y el efecto cristal de `pro.css`. Se corrigen los contrastes que el rediseño anterior había roto: la auditoría WCAG de la CI fallaba en `main`.

### Cuenta

- El documento se guarda en `pld:learn` y en `/api/course-state/learn`.
- El backend solo añade `learn` a la lista cerrada `COURSES`.
- La app Android leerá y fusionará el mismo documento (fase 4).

## Trade-offs y consecuencias

- **Hay más contenido que mantener** (111 ejercicios). A cambio, cada uno está comprobado por la CI, y un ejercicio con la respuesta mal no puede llegar a producción.
- **Tres zonas de Python conviven:** núcleo, curso PCAP y curso de Programación por UT. No se borran porque tienen progreso real sincronizado con la app.
  - El núcleo enlaza las otras dos.
  - **Deuda:** cuando el núcleo cubra todo, decidir si el curso por UT se mantiene o se integra.
- **Los umbrales son ASSUMPTION** razonables, no medidos: 80 % para «dominado», 60 % para avanzar, 2 aciertos para corregir un error y 21 días. Están en constantes con nombre para poder ajustarlos.
- **No se borra ninguna funcionalidad.** Los e2e del PCAP y de la cuenta se han adaptado solo donde cambiaban la navegación (el menú «Menú», «Curso PCAP») o la portada.
- **VERIFY:** que la ruta de conceptos coincide con el orden real de las UT de Alcazarén (ver ADR-0020).
