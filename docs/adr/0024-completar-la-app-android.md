# ADR-0024: Completar la app Android, empezando por el simulacro de examen

- **Estado:** Aceptada. Fase 1 implementada; fases 2 y 3 propuestas
- **Fecha:** 2026-09-30

## Contexto

El autor quiere una app para su móvil a partir de este proyecto. La app Android nativa (ADR-0011) ya existe y funciona sin conexión (ADR-0014), pero le faltan cosas que la web sí tiene:

1. **Simulacro cronometrado.** Solo existe en la web y solo para el PCAP. El examen de Programación de 1.º de DAW, que es en Python, no tiene simulacro en ningún sitio.
2. **Cuenta y sincronización.** El progreso del móvil y el de la web no se juntan.
3. **Ejecutar Python** dentro de la app.

El autor eligió completar la app existente, no crear una nueva, para no duplicar código ni mantenimiento.

## Opciones de orden

| Opción | Valor para aprobar | Riesgo técnico | Coste |
|---|---|---|---|
| **A. Simulacro primero** | Alto: practicar en condiciones de examen es lo que más acerca al aprobado | Bajo: reutiliza el banco, los tipos de pregunta y el estado | Bajo |
| B. Cuenta y sincronización primero | Medio: comodidad, no aprendizaje | Medio: red, errores, tokens; cambia ADR-0014 (permiso `INTERNET`) | Medio |
| C. Python real (Chaquopy) primero | Medio-alto | Alto: plugin de Gradle de terceros, unos 20 MB más de APK, compatibilidad con AGP (VERIFY) | Alto |

## Decisión

**A, en tres fases:**

1. **Fase 1 (esta entrega, 0.12.0): simulacro de examen para todos los cursos.**
2. **Fase 2: cuenta y sincronización.** Es la entrega 6 prevista en ADR-0014. Tendrá su propio ADR, que revise ADR-0014 porque añade el permiso `INTERNET`, y seguirá siendo opcional.
3. **Fase 3: Python real con Chaquopy.** Antes, una prueba de concepto que mida el tamaño del APK y la compatibilidad con la versión del plugin de Android.

### Fase 1: reglas del simulacro

- **PCAP:** el reparto oficial del examen: 40 preguntas, 65 minutos y un 70 % para aprobar, con los mismos ítems por bloque que la web.
- **Cursos DAW (Programación, Bases de datos, Entornos, JavaScript, Java):**
  - 30 preguntas repartidas según el peso de cada bloque, con el método del mayor resto y sin pedir a un bloque más de las que tiene;
  - 90 segundos por pregunta (45 minutos);
  - un 50 % para aprobar.

  **ASSUMPTION:** estas cifras imitan un examen de FP (aprobado con un 5). Si el centro publica el formato real (número de preguntas y duración), se ajustan en `Mock.COURSE_*`.
- **Durante el examen:** se responde sin ver la corrección, se puede ir y volver entre preguntas, y todos los tipos de ejercicio valen (test, completar y ordenar).
- **Al entregar o acabarse el tiempo:**
  - se corrige todo y las no respondidas cuentan como falladas;
  - entregar con preguntas sin responder pide confirmación.
- **Resultado:**
  - nota, aprobado o no, y acierto por bloque;
  - revisión de cada fallo con la solución y la explicación.
- **Qué se guarda:**
  - cada respuesta, en el repaso espaciado;
  - el simulacro, en `exams`: el mismo campo y formato que la web. En el PCAP cuenta para «Listo para examinarte» y se sincroniza cuando llegue la fase 2;
  - +1 XP por acierto.
- **Si sales a mitad**, el tiempo sigue corriendo y lo retomas al volver.
- **Arquitectura:** la de la práctica (ADR-0018):
  - `Mock.kt`: plan, construcción, corrección y el *reducer* `MockUiState.reduce`, puros y con tests (`MockTest`);
  - `MockViewModel`: aplica los efectos;
  - `MockScreen`: solo pinta.
- **Accesibilidad:**
  - el reloj tiene una descripción legible por TalkBack;
  - se anuncia al quedar 10, 5 y 1 minutos, como en la web;
  - los botones de pregunta dicen si está respondida.

## Consecuencias

- La pestaña «Examen» (o «Práctica», en los cursos) empieza por el simulacro.
- **DONE:** el dominio (`Mock.kt`) se compila y sus tests pasan: 52 tests del dominio, 6 de ellos nuevos.
- **VERIFY:** la interfaz de Compose solo se compila en la CI (`android.yml`), y hay que probarla en el móvil: el reloj, la entrega automática y la revisión.
- **Riesgo:** un simulacro a medias vive en memoria. Si Android cierra la app, se pierde y no se guarda nada, igual que la mazmorra (ADR-0015).
