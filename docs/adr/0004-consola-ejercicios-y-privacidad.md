# ADR-0004: Consola en el navegador, corrección de ejercicios, asistente y privacidad del frontend

- **Estado:** Aceptada
- **Fecha:** 2026-09-25

## 1. Python en el navegador: Pyodide dentro de un Web Worker

| Opción | A favor | En contra |
|---|---|---|
| **A. Pyodide en un Web Worker** (elegida) | CPython real (3.14) en el navegador; no ejecuta nada en el servidor; funciona sin backend | Unos 10 MB en la primera carga (luego queda en caché) |
| B. Ejecutar en el backend | Sin descarga | Exige un sandbox seguro: justo el riesgo que se evita (ADR-0003) |
| C. Skulpt o Brython | Ligeros | No son CPython: comportamiento y errores distintos a los de PyCharm |

- **Worker de tipo módulo:** Pyodide 314 ya no admite workers clásicos. Se detectó porque la consola no cargaba en las pruebas.
- **Límite de 10 s por ejecución:** si se supera (por ejemplo, un bucle infinito), se destruye el Worker y se crea otro. La página nunca se congela.
- **`input()`:** se alimenta desde el cuadro «Entrada», una línea por llamada. Si faltan datos, se muestra `EOFError` con una pista.
- **Mismo motor en todas partes:** el runner (`frontend/py/runner.py`) es el mismo en el navegador y en los tests de CPython, así que la CI prueba el mismo código que ejecuta el alumno.
- **CDN:** Pyodide se carga desde jsDelivr por su tamaño. Se puede cambiar con `pyodideUrl` en `config.js`.

## 2. Corrección de ejercicios

- Cada lección tiene `checks`: una lista de casos con `stdin` y `test` (asserts con mensajes en español). Los tests ven las variables del alumno, su salida (`__output__`) y su código (`__code__`).
- El código se ejecuta con `__name__ = "solucion"`, así que lo que va dentro de `if __name__ == "__main__":` no se ejecuta al comprobar.
- El ejercicio de pytest comprueba **la calidad de los tests del alumno**: sustituye cada función por una versión con un fallo y exige que algún test lo detecte.
- **Las soluciones de referencia no están en el repositorio**, porque serían un spoiler para quien estudia. Se comprobaron fuera del repositorio: las 15 superan todos sus casos. En la CI se garantiza que:
  - todos los ejemplos se ejecutan sin errores con el mismo motor;
  - ninguna plantilla supera sus tests;
  - los tests son Python válido.
- El resultado se decide en el navegador: no sirve como certificación (ADR-0003).

## 3. Asistente

Respuestas **preparadas y revisadas** por lección (preguntas frecuentes, pista del ejercicio y siguiente tema). No se usa una IA generativa. Motivo: coste cero, sin riesgo de respuestas incorrectas y sin enviar datos a terceros. Se podrá reconsiderar si aporta valor real frente a su coste.

## 4. Privacidad y accesibilidad del frontend

- Las fuentes (Inter, JetBrains Mono) y highlight.js se alojan en el propio sitio: no hay peticiones a Google Fonts ni a otros CDN, que en la UE han generado sanciones por transferir la IP.
- Sin cookies. `localStorage` solo guarda progreso, borradores y la sesión, a petición del usuario.
- Auditoría WCAG 2.1 AA automática (axe-core) en los tests end-to-end. Corrigió contrastes y un bloque de código al que no se llegaba con el teclado.
- Menú móvil con `inert` cuando está cerrado, cierre con `Esc` y foco gestionado. El editor permite salir con `Esc` y después `Tab`, para no atrapar el foco del teclado.
