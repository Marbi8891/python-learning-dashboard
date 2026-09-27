# ADR-0016: Más cursos de DAW en la app, sin tocar el del PCAP

- **Estado:** Aceptada
- **Fecha:** 2026-09-27

## Contexto

El autor quiere estudiar con la app otros lenguajes de DAW además de Python: SQL, JavaScript, Java y HTML/CSS, en ese orden. Condición: **todo lo del PCAP se queda igual**, incluidos sus datos (compartidos con la web), su examen y su preparación.

## Opciones

| Opción | Pros | Contras |
|---|---|---|
| **A. Varios cursos en la misma app, con un selector** | Una sola app; la ruta, el juego, la teoría y el repaso sirven para todos | Hay que separar el estado por curso |
| B. Una app por lenguaje | Arranque rápido | Cada mejora se repite en todas las copias |
| C. Meter los lenguajes como bloques del banco del PCAP | Casi sin código | Mezcla la preparación del PCAP con otros temarios y la vuelve inútil |

## Decisión

**A.**

- **El PCAP no cambia.** Sus datos siguen en `frontend/data/`, su estado en la misma clave (`pcap`) y con el mismo formato que la web.
- **Los demás cursos** viven en `assets/courses/<id>/bank.json` y `lessons.json`, con **el mismo formato** que el PCAP. La app los lee con los mismos lectores (`Bank`, `LessonIndex` y `LessonLibrary`) y les aplica la misma ruta, práctica, teoría y juego.
- **Estado:**
  - cada curso guarda sus respuestas y su repaso en `course:<id>`;
  - la XP, la racha, la meta, las vidas y los récords del juego son **comunes**. Se guardan con el PCAP (`PcapState.shareApp`) para que la racha no dependa de qué curso estudies;
  - los identificadores de preguntas y nodos llevan el curso delante (`sql-…`) y un test comprueba que no chocan con los del PCAP.
- **Contenido comprobado.** Cada curso se escribe en `scripts/courses/<id>_course.py`, que genera los JSON. En las preguntas de código, el script **ejecuta el código de verdad** y falla si la salida real no es la que dice la respuesta. La CI lo ejecuta con `--check`, que además falla si los JSON no están al día.
- **Interfaz:**
  - un selector de curso encima de las pestañas;
  - fuera del PCAP, la pestaña "Examen" se llama "Práctica" y muestra el **dominio** por bloque (acierto ponderado por la importancia del bloque) en lugar de la preparación para el examen;
  - el selector de idioma solo aparece en el PCAP.

## Primer curso: SQL (módulo Bases de datos)

- 5 bloques (consultas, agregación, combinaciones, DDL/DML y diseño), 10 lecciones, 50 preguntas y 20 del mini-quiz.
- Las preguntas de código se ejecutan en **SQLite**, con las claves ajenas activadas. El SQL es estándar y funciona igual en MySQL; donde hay diferencias, la teoría lo avisa (tipado flexible, `AUTO_INCREMENT`, formato de los decimales).
- Cada pregunta muestra las tablas de ejemplo como comentarios SQL, para verlas en el móvil sin conexión.

## Segundo curso: Java (módulo Programación)

- Se adelanta a JavaScript porque el autor lo echó en falta al probar la 0.5.0.
- 5 bloques: fundamentos, control de flujo, clases y objetos, herencia e interfaces, y colecciones y excepciones. 10 lecciones, 50 preguntas y 20 del mini-quiz.
- Cada pregunta de código se **compila y ejecuta con `java`** (Java 17 en la CI, en modo «archivo fuente»). La salida esperada distingue tres casos: lo que imprime, «Error de compilación» y «Excepción: Nombre». Así las preguntas sobre errores también quedan comprobadas.
- Los textos que imprimen los programas no llevan tildes, para que la salida sea idéntica con cualquier configuración regional.

## Consecuencias

- **Cursos siguientes:** JavaScript, que se comprobará con Node en la CI, y HTML/CSS, con sobre todo preguntas teóricas y de lectura de código.
- **Pendiente:** ejecutar SQL dentro de la app (Android trae SQLite, así que es viable sin conexión). Irá en una entrega propia.
- **ASSUMPTION:** la sincronización con la cuenta (entrega 7) necesitará guardar en el backend el estado de cada curso, no solo `pcap-state`.
- **VERIFY:** la interfaz del selector solo se compila en la CI.
