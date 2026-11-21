# Progreso local y hitos verificados (#109)

La web calcula casi todo el progreso en el navegador: así funciona sin cuenta y sin conexión. Ese
progreso es **orientativo**: cualquiera puede cambiarlo con las herramientas del navegador, y el
servidor solo lo guarda. Para lo que tenga valor fuera de la web (un certificado o el seguimiento
del piloto) hay **hitos verificados**: el servidor los comprueba y el navegador no los puede inventar.

## 1. Qué llega del navegador y qué depende de ello [verificado en el código]

| Dato | Ruta | Quién lo calcula | Qué comprueba el servidor | Lo usa |
|---|---|---|---|---|
| Lección completada | `PUT /api/v1/progress/{slug}`, `POST /progress/import` | El navegador | Que la lección exista; idempotente (una fila por usuario y lección) | Panel, certificado del PCAP |
| Intento de ejercicio (`passed`) | `POST /lessons/{slug}/attempts` | El navegador (Pyodide ejecuta los tests) | Que la lección exista; guarda los 50 últimos | Panel, marca la lección completada |
| Documento del PCAP (aciertos, simulacros locales, fichas) | `PUT /api/v1/pcap-state` | El navegador | Tamaño máximo y versión (409 si otra pestaña guardó antes) | Panel del PCAP, certificado del PCAP |
| Documentos de los cursos de DAW, motor adaptativo, XP y logros | `PUT /api/v1/course-state/{course}` | El navegador | Lista cerrada de cursos, tamaño y versión | Panel, certificados de los cursos de DAW |
| Derechos de los planes (Free, Pro, Academy) | Solo lectura: `GET /users/me/entitlements` | El servidor | Los concede el servidor; el navegador no los puede escribir | Acceso a funciones de pago |
| **Simulacro verificado del PCAP** | `POST /api/v1/verified/pcap-exams…` | **El servidor** | Todo: ver la sección 2 | Panel del PCAP y certificado del PCAP |

No hay rankings. Los certificados se generan en el navegador; desde #109 dicen si el simulacro
está verificado por el servidor o no.

## 2. Simulacro verificado

Con la sesión iniciada, el simulacro del PCAP pasa por el servidor:

1. `POST /api/v1/verified/pcap-exams` → el servidor elige 40 preguntas de `frontend/data/pcap.json` con
   el reparto por bloques del examen y apunta la hora de inicio. Responde los ids y la hora límite.
2. El navegador pinta esas preguntas (ya tiene su texto) y controla el reloj.
3. `POST /api/v1/verified/pcap-exams/{id}/answers` con `{"answers": {"id": [opciones]}}` → el servidor
   corrige con las respuestas correctas y guarda la nota.
4. `GET /api/v1/verified` → simulacros corregidos, mejor nota y si hay alguno aprobado.

Reglas que hace cumplir el servidor (todas con prueba en `backend/tests/test_verified_exams.py`):

| Regla | Respuesta |
|---|---|
| Pregunta que no es de ese simulacro, id inventado, opción fuera de rango o repetida, más opciones de las que pide la pregunta | 422, y el simulacro sigue en curso |
| La nota la pone el servidor; un campo `score` en la entrega se ignora | — |
| Repetir la misma entrega | 200 con la misma nota, sin volver a corregir |
| Entregar otras respuestas a un simulacro ya corregido | 409 |
| Entregar después de la hora límite (más 2 minutos de margen) | 409, y queda `expired` sin nota |
| Empezar otro sin entregar el anterior | El anterior queda `abandoned` sin nota |
| Dos entregas a la vez | Solo una pasa de `open` a `finished` (UPDATE condicionado) |
| Simulacro de otra cuenta | 404, igual que uno que no existe |
| Más de `VERIFIED_EXAMS_PER_DAY` (5) en 24 horas | 429 |
| Varios inicios a la vez de la misma cuenta | Van de uno en uno (bloqueo de la fila del usuario, PLD-001): nunca pasan del límite y solo queda uno `open`. Los de cuentas distintas no se esperan. Prueba con PostgreSQL en `backend/tests/test_verified_concurrency.py` |

Sin cuenta, o si el servidor no responde, el simulacro es local, como antes de #109, y la web lo dice.

### Qué no garantiza

No es un examen vigilado. El banco de preguntas es público (la web lo descarga entero) y nadie mira
la pantalla. «Verificado» quiere decir que el servidor eligió las preguntas, controló el tiempo y
puso la nota, no que la persona lo hiciera sin ayuda. Un certificado oficial necesitaría un examen
supervisado, y eso queda fuera del proyecto.

Las lecciones completadas tampoco se pueden verificar: los ejercicios de Python se ejecutan en el
navegador (Pyodide), y comprobarlos en el servidor exigiría ejecutar código de los alumnos allí, que
es un cambio de arquitectura y de seguridad que no se hace.

## 3. En la interfaz

- **Intro del simulacro:** explica si se va a verificar (con cuenta) o si será local.
- **Resultado:** distintivo «Verificado: el servidor eligió las preguntas, controló el tiempo y puso la
  nota» o «Simulacro local: corregido en este navegador. Es orientativo». Si el servidor falla, lo dice.
- **Panel del PCAP:** una línea con lo que dice el servidor (mejor nota verificada) y el aviso de que el
  historial de la tabla está en este navegador y es orientativo.
- **Certificado del PCAP:** dice si el simulacro aprobado está verificado por el servidor.
- **Certificados de los cursos de DAW:** dicen que el progreso se comprobó en el navegador.

Lo verificado solo sale de `GET /api/v1/verified`. El campo `verified` que el navegador guarda en su
historial es solo para pintar el resultado, y no cuenta como verificación.

## 4. Datos personales

La tabla `verified_exams` guarda, por cuenta: ids de las preguntas, opciones marcadas, aciertos, nota y
horas. Sale en la exportación (`/users/me/export`, campo `verified_exams`) y se borra con la cuenta.
