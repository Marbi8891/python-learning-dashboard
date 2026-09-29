# ADR-0020: Curso de Programación (módulo 0485) en Python por unidades de trabajo

- **Estado:** Aceptada e implementada
- **Fecha:** 2026-09-29
- **Revisa:** ADR-0016 (cursos de DAW)

## Contexto

Hasta ahora se daba por hecho que el examen de Programación sería en Java: por eso existe el curso de Java (ADR-0016). El autor ha confirmado que **su examen es en Python**. Como referencia del temario ha aportado el curso abierto «DAW-Programacion», de César San Juan Pastor (IES Arcipreste de Hita). Tiene 9 unidades de trabajo:

1. Introducción y algoritmos.
2. Elementos de un programa.
3. Estructuras de control.
4. POO.
5. POO en Python (I).
6. POO en Python (II).
7. Proyecto.
8. Gestión de datos.
9. Interfaces gráficas.

Su licencia es **Creative Commons no comercial**: el `LICENSE` del repositorio dice BY-NC 4.0 y el pie de las unidades, BY-SA. Permite adaptarlo citando al autor y sin fines comerciales.

Además, el autor quiere aprender Java **más adelante**.

## Opciones

| Opción | Resumen | Veredicto |
|---|---|---|
| A. Reutilizar el curso del PCAP | Ya es Python | Descartada: sigue el temario de una certificación, no las UT. Faltan algoritmos y pseudocódigo, teoría de la POO, ficheros, bases de datos e interfaces gráficas |
| **B. Curso nuevo `programacion` por UT** | Un bloque por unidad, con teoría y preguntas propias y respuestas ejecutadas | **Elegida** |
| C. Copiar los apuntes dentro de la app | El texto original | Descartada: más riesgo con la licencia, y los apuntes tienen errores (ver abajo) |

## Decisión

- **Estructura:**
  - Curso `programacion`, «Programación», con 9 bloques (`prog-ut1` … `prog-ut9`), 12 lecciones, 163 preguntas y 23 del mini-quiz.
  - Incluye ejercicios de escribir código: completar el hueco, ordenar líneas y encontrar el error.
- **Pesos:**

  | Bloque | Peso |
  |---|---|
  | UT1 | 8 % |
  | UT2 | 12 % |
  | UT3 | 20 % |
  | UT4 | 8 % |
  | UT5 | 15 % |
  | UT6 | 17 % |
  | UT7 | 5 % |
  | UT8 | 10 % |
  | UT9 | 5 % |

  Se da más peso a lo que más se programa. **ASSUMPTION:** no conocemos cómo se reparte la nota del examen real.
- **Comprobación de las respuestas:**
  - Cada respuesta de código se comprueba **ejecutando Python** en la CI, en una carpeta temporal, porque las preguntas de ficheros escriben en disco.
  - Las de bases de datos usan `sqlite3`.
  - Las de interfaces gráficas (PySide6) no se ejecutan: preguntan qué hace el código.
- **Texto propio:** la teoría y las preguntas están redactadas de nuevo. Siguen el orden y los contenidos de las UT, sin copiar el texto de los apuntes. Cada lección cita la fuente con el autor, la licencia y el enlace.
- **Orden del selector:** PCAP, Programación, Bases de datos, Entornos, JavaScript y Java.
- **Java se conserva** tal cual, con el subtítulo «Para más adelante». El progreso que ya tenga no se toca.
- El backend añade `programacion` a `COURSES`, para que la sincronización (B2) lo cubra.

## Correcciones sobre los apuntes

Se enseña lo correcto y, cuando hace falta, se explica en qué simplifican los apuntes:

- **Tipado:** Python es de tipado **fuerte y dinámico**, no «débilmente tipado».
- **Parámetros:** los apuntes dicen que los simples se pasan «por valor» y los compuestos «por referencia». En realidad, todo se pasa como referencia al objeto. Reasignar un parámetro no afecta fuera, pero modificar un objeto mutable sí.
- **Sobrecarga y polimorfismo:**
  - La sobrecarga se resuelve al compilar, en Java y C++.
  - El polimorfismo viene de la **sobrescritura**, que se resuelve en ejecución.
  - Python no tiene sobrecarga: el segundo `def` sustituye al primero.
- **Herencia múltiple:** `super()` sí funciona con herencia múltiple (MRO).
- **Atributos con `__`:** se heredan con el nombre cambiado; no es que no se hereden.
- **`@final`:** lo comprueban los analizadores de código, como mypy; el intérprete no.
- **`with`:** cierra el fichero, pero no captura las excepciones.
- **Codificación:** ASCII es de 7 bits; UTF-8 tiene longitud variable, de 1 a 4 bytes.
- **Widgets:** en PySide6 están en `QtWidgets`, no en `QtGui`, y el bucle de eventos se lanza con `exec()` en lugar de `exec_()`.
- **SQL:** se usan parámetros (`?` o `%s`), nunca concatenación, para evitar la inyección SQL. Hay una pregunta que lo demuestra.
- **Valores por defecto mutables:** se enseña el error de `def f(lista=[])`.

## Consecuencias

- Hay 5 cursos de DAW además del PCAP. `CoursesTest` comprueba que el curso de Programación tiene las 9 UT y que cada bloque llena una planta de la mazmorra.
- **VERIFY:**
  - Que el temario del centro del autor, Alcazarén, coincida con estas UT. El curso de referencia es de otro instituto.
  - Qué bibliotecas y versiones pide el examen: por ejemplo, si GUI con PySide6 o con Tkinter.
- **Siguiente paso posible:** un simulacro de examen de Programación con tiempo, mezclando las UT según sus pesos.
