# ADR-0019: Cursos según el temario del centro (Bases de datos y Entornos de desarrollo)

- **Estado:** Aceptada e implementada
- **Fecha:** 2026-09-27
- **Revisa:** ADR-0016 (cursos de DAW)

## Contexto

El autor subió los apuntes oficiales de su centro (Escuela Alcazarén, FP Aspasia, DAW virtual):

- **Bases de datos** (módulo 3): UD1 «Almacenamiento de la información», UD2 «Bases de datos relacionales» y UD3 «Realización de consultas».
- **Entornos de desarrollo** (módulo 5): UD1 «Desarrollo de software».

Cada PDF venía repetido, y con ellos llegaron el carnet y la matrícula, que tienen datos personales y no se usan.

El curso de SQL (ADR-0016) seguía un orden propio: consultas, agregados, JOIN, DDL/DML y diseño. **No cubría** la UD1 completa (tipos y modelos de bases de datos, fragmentación, Big Data, ficheros, RGPD/LOPDGDD y SGBD) ni partes de la UD2 y la UD3: NULL, ALTER/DROP, índices únicos y compuestos, DCL (usuarios, GRANT, REVOKE y roles), UNION/INTERSECT/EXCEPT, RIGHT/FULL JOIN, COALESCE, EXPLAIN y optimización.

Los exámenes finales son presenciales y siguen ese temario.

## Opciones

| Opción | Resumen | Veredicto |
|---|---|---|
| A. Curso nuevo «Bases de datos» junto al de SQL | Dos cursos que se solapan | Descartada: duplica preguntas y reparte el progreso |
| **B. Reorganizar el curso de SQL por UD** | Mismo id `sql`, bloques = UD del centro, lecciones nuevas para lo que faltaba | **Elegida** |
| C. Rehacer el curso desde cero | Preguntas nuevas con ids nuevos | Descartada: se pierde el progreso |

Para Entornos de desarrollo no había nada, así que se crea un curso nuevo, `entornos`.

## Decisión

### Bases de datos (curso `sql`, ahora «Bases de datos»)

- Bloques = unidades del centro:
  - `bd-ud1` (15 %): 2 lecciones nuevas.
  - `bd-ud2` (30 %): modelo relacional, CREATE TABLE y una lección nueva sobre NULL, ALTER, índices, DCL y vistas.
  - `bd-ud3` (45 %): las 6 lecciones de consultas y una nueva sobre conjuntos, subconsultas y optimización.
  - `bd-ampliacion` (10 %): DML y transacciones, que van más allá de la UD3.
- **El progreso se conserva:**
  - el id del curso, los slugs de las lecciones antiguas y los ids de sus preguntas (`sql-01`… `sql-50`) no cambian;
  - no se añaden preguntas a las lecciones antiguas, así que sus nodos de la ruta tampoco cambian;
  - los aciertos por bloque se calculan a partir de las respuestas por id, así que cambiar los slugs de los bloques no pierde nada.
- 60 preguntas nuevas (`bd-01`… `bd-60`), 8 del mini-quiz y 6 ejercicios de escribir SQL (hueco, ordenar y encontrar el error). Las de código se ejecutan en SQLite, como las demás.
- **MySQL frente a SQLite:** los apuntes usan sintaxis de MySQL, como `ALTER TABLE … MODIFY`, `CREATE USER 'x'@'host'`, GRANT y REVOKE. Como SQLite no la ejecuta, esas preguntas son teóricas y la teoría indica siempre qué sintaxis es de MySQL.

### Entornos de desarrollo (curso nuevo `entornos`)

- 4 bloques de la UD1, uno por lección:
  - lenguajes y programas;
  - del código fuente al ejecutable;
  - paradigmas;
  - fases y metodologías ágiles.
- 51 preguntas y 8 del mini-quiz.
- Las preguntas con salida y los ejemplos son de Python y se ejecutan en la CI.
- Los fragmentos de Java, C y C++ no se ejecutan: se pregunta qué son (qué lenguaje, qué paradigma, qué fase), no qué muestran.
- `COURSES` del backend incluye `entornos` para que la sincronización (B2) lo cubra.

## Correcciones sobre los apuntes

Se enseña lo correcto sin contradecir los apuntes:

- `<>` es el operador estándar de «distinto»; `!=` lo aceptan MySQL y SQLite.
- MySQL no tiene FULL OUTER JOIN: se simula con LEFT JOIN UNION RIGHT JOIN.
- INTERSECT y EXCEPT existen en MySQL desde la versión 8.0.31.
- `NOT IN` con una subconsulta que devuelve NULL no devuelve ninguna fila.
- Python también genera bytecode internamente, pero en la unidad se considera un lenguaje interpretado.

## Consecuencias

- Los jefes de la mazmorra del curso de SQL cambian, porque dependen de los bloques. Cada curso tiene los suyos.
- `CoursesTest` ya no supone 5 bloques ni 10 unidades por curso. Comprueba que cada lección es una unidad y que Bases de datos conserva los ids antiguos.
- **VERIFY:**
  - el orden de las UD siguientes (UD4 en adelante) no se conoce;
  - cuando lleguen los apuntes, `bd-ampliacion` se sustituirá por las UD reales, conservando los ids.
- Programación sigue siendo prioritaria: falta su temario (RA 4-9) para alinear el curso de Java igual.
