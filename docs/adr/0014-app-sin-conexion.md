# ADR-0014: La app Android funciona entera sin conexión

- **Estado:** Aceptada
- **Fecha:** 2026-09-27

## Contexto

Desde la versión 0.2.2 la app ya tiene dentro el banco de preguntas y la ruta, pero los botones "Teoría" (en la ruta, en la pestaña Examen y al fallar una pregunta) abrían la lección de la web en el navegador. El autor quiere que todo esté dentro de la app, sin necesitar internet.

## Opciones

| Opción | Pros | Contras |
|---|---|---|
| **A. Pantalla nativa de teoría con `lessons.json`**, que ya va dentro del APK | Sin conexión, sin copiar contenido, reutiliza el formato de la web | La lógica de párrafos y listas existe dos veces (JS y Kotlin) |
| B. WebView con el frontend empaquetado | Aspecto idéntico a la web | Duplica toda la web dentro del APK, pesa más y deja de ser una app nativa (va contra ADR-0011) |
| C. Seguir abriendo la web | Nada que hacer | No cumple el objetivo |

## Decisión

**A.** `TheoryScreen` muestra la lección completa: explicación, ejemplo, ejercicio con su código de partida y pista, mini-quiz corregido al momento, reto extra, dudas frecuentes y títulos de las fuentes.

- **Una sola fuente de datos:** `LessonLibrary` lee el mismo `frontend/data/lessons.json` que la web. `parseBlocks` sigue la misma regla que `markdown.js` (párrafos y listas con "- " o "1. "), y un test lo comprueba.
- **Sin permiso de internet:** el manifiesto no declara `INTERNET` y la app ya no abre enlaces. Se elimina `BuildConfig.WEB_URL`.
- Las fuentes se muestran solo como títulos, para ampliar cuando haya conexión.
- El mini-quiz de la teoría no cuenta para la preparación del PCAP (igual que en la web). Lo que cuenta es la ruta y la práctica.

## Consecuencias

- **Ejecutar Python todavía no es posible dentro de la app.** Los ejemplos y ejercicios se muestran como código. Esto llegará sin conexión en la entrega 5 (Chaquopy, ADR-0011).
- **La entrega 6 (cuenta y sincronización)** será la única función con red y será opcional: la app tiene que seguir funcionando entera sin ella. Añadirá el permiso `INTERNET` con su propio ADR.
- VERIFY: la interfaz solo se compila en la CI; la lectura de las 27 lecciones y la regla de párrafos y listas tienen tests.
