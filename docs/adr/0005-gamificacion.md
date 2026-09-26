# ADR-0005: Gamificación (quiz, retos, XP, niveles, racha y logros)

- **Estado:** Aceptada
- **Fecha:** 2026-09-26

## Contexto

Se quiere que la app sea más instructiva y divertida sin convertirla en un juego que distraiga del aprendizaje.

## Decisiones

1. **Primero lo instructivo:**
   - **Mini-quiz** de 3 preguntas por lección. Cada respuesta **explica el porqué**, e incluye preguntas de "¿qué imprime este código?".
   - **Reto extra** opcional por lección, de ★ a ★★★, con tests automáticos.
   - Ambos se verificaron fuera del repositorio: las respuestas de los quizzes se contrastaron ejecutando el código, y cada reto tiene una solución de referencia que supera sus tests. Las soluciones no se publican (ADR-0004).
2. **XP calculados, no acumulados:** los XP se derivan de hechos (lecciones completadas, mejor nota de cada quiz, retos superados, ejercicios acertados a la primera). Repetir una acción no da puntos dobles y el total siempre es coherente.

   | Acción | XP |
   |---|---|
   | Lección completada | 50 |
   | Quiz | 10 por acierto (mejor intento) + 10 si es pleno |
   | Ejercicio superado al primer intento | +20 |
   | Reto | 30 por estrella |

3. **Niveles:** 7, de «Novato/a» (0 XP) a «Leyenda de Python» (2200 XP). Con todo completado se consiguen 2520 XP.
4. **Racha:** días seguidos con actividad, en hora local. No se pierde hasta que acaba el día siguiente.
5. **13 logros**, que premian hábitos útiles: arreglar un error, acertar a la primera, la constancia…
6. **Celebraciones:** confeti al superar ejercicios, retos, logros y niveles. Respeta `prefers-reduced-motion`.
7. **Almacenamiento:** el estado del juego se guarda en el navegador (`localStorage`, clave `pld:game`). Las lecciones completadas, que son la mayor parte de los XP, sí se sincronizan con la cuenta. Sincronizar también el resto (quizzes, retos, logros) queda como mejora futura: exige su propia tabla y migración, y hoy no aporta lo suficiente para justificarlo.

## Consecuencias

- Todo funciona sin cuenta y sin conexión con el backend.
- En otro navegador, las lecciones completadas aparecen (si hay sesión), pero la racha, los logros y las notas de los quizzes empiezan de cero.
- Los tests del backend verifican la estructura de los quizzes y que ninguna plantilla de reto supera sus tests. Los tests end-to-end verifican el flujo completo del juego y su accesibilidad (WCAG).
