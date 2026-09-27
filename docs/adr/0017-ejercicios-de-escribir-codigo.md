# ADR-0017: Ejercicios de escribir código

- **Estado:** Aceptada
- **Fecha:** 2026-09-27
- **Retoma:** la entrega 4 de ADR-0015 ("ordenar código y completar el hueco")

## Contexto

El objetivo del autor es **aprobar Programación de 1.º DAW**, cuyo examen exige **escribir código**. Hasta ahora la app solo tenía preguntas de test, es decir, de **reconocer** la respuesta. El propio autor identifica su bloqueo en pasar de reconocer a producir: la hoja en blanco.

## Opciones

| Opción | Pros | Contras |
|---|---|---|
| **A. Tres ejercicios intermedios: completar el hueco, ordenar líneas y encontrar el error** | Entrenan la producción paso a paso; se corrigen sin ejecutar nada en el móvil; se comprueban en la CI | No sustituyen a escribir un programa entero |
| B. Escribir programas completos y ejecutarlos en el móvil | Lo más parecido al examen | Android no compila Java al vuelo; necesitaría un servidor (red) o un intérprete enorme |
| C. Escribir el programa y comparar con una solución modelo | Sin ejecución | La corrección sería poco fiable: hay muchas soluciones válidas |

## Decisión

**A.**

- **Completar el hueco (`fill`):** el código lleva `___` y el alumno teclea lo que falta. Se aceptan varias respuestas; al comparar no cuentan los espacios ni un `;` final.
- **Ordenar líneas (`order`, problema de Parsons):** el alumno toca las líneas disponibles en el orden correcto y toca las ya puestas para quitarlas. **No se arrastra**, para que funcione igual con TalkBack. Puede haber código fijo antes y después (la línea `___` del contexto marca dónde van).
- **Encontrar el error (`bug`):** se guarda como una pregunta de test cuyas opciones son las líneas del programa. No necesita pantalla nueva.
- **Comprobación en la CI** (`scripts/courses/course_builder.py`):
  - **fill:** cada respuesta aceptada se inserta en el código, se compila y se ejecuta, y tiene que dar la salida esperada;
  - **order:** la solución tiene que dar la salida esperada y **ningún intercambio de dos líneas vecinas** puede darla también, para que la solución sea única;
  - **bug:** el código original **no** da la salida objetivo y el código con la línea corregida **sí** la da.
- En la app, `Question.kind` y `Answer` (lo seleccionado, lo escrito y el orden) sustituyen al conjunto de opciones elegidas. Las tres pantallas (lección, práctica y mazmorra) usan el mismo componente `QuestionInput`. Bug Rush sigue siendo solo de test.

## Primera tanda

30 ejercicios en el curso de **Java**: uno de cada tipo por lección.

## Consecuencias

- Las lecciones de Java pasan de 5 a 8 preguntas, así que cada unidad de la ruta tiene ahora dos lecciones cortas.
- Generar el curso de Java tarda más (unos 90 s), porque compila cada variante.
- **Pendiente:** ampliar a más ejercicios por lección, y a SQL y JavaScript, cuando se valide con el uso.
- **VERIFY:** la usabilidad de teclear código en el móvil (teclado sin autocorrector) y de ordenar líneas largas en pantalla estrecha.
