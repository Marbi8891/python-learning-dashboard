# Currículo de M03-M05 · Excel profesional (P4.1)

**Estado:** hecho el 17/11/2026 (DA-28 de `MASTER_SPECIFICATION.md`). Sigue la plantilla de unidad y
las reglas de corrección de [`CURRICULUM_M1_M2.md`](CURRICULUM_M1_M2.md); aquí solo se anota lo que
cambia. El contenido está en `scripts/courses/excel/m03.py`, `m04.py` y `m05.py`, y lo genera
`scripts/courses/excel_course.py`, que comprueba con el motor cada ejemplo y cada ejercicio de fórmula.

## 1. Módulos y unidades

| Módulo | Unidad | h | Nivel | Requiere | Caso (empresa ficticia) |
|---|---|---|---|---|---|
| M03 · Formato profesional y gestión de libros | `xl3-formato-celdas` Estilos, bordes, alineación y paneles | 2 | 2 | xl1-formatos | Tarifa del Taller Montesol, lista para imprimir |
| | `xl3-libros` Hojas, grupos, impresión y vistas | 2 | 2 | xl3-formato-celdas, xl2-hojas | Libro trimestral de la Gestoría Albaida |
| M04 · Funciones lógicas | `xl4-si` SI y comparaciones | 2 | 2 | xl2-operadores, xl1-referencias | Control de cobros del Taller Montesol |
| | `xl4-logicas` Y, O, NO, SI.CONJUNTO y SI.ERROR | 2 | 3 | xl4-si | Incentivos y envíos de la Clínica Dental Ribera |
| M05 · Agregación condicional | `xl5-sumar-si` SUMAR.SI y SUMAR.SI.CONJUNTO | 2 | 3 | xl4-si, xl2-estadisticas | Resumen de facturación de la Gestoría Albaida |
| | `xl5-contar-si` CONTAR.SI, PROMEDIO.SI y MAX/MIN.SI.CONJUNTO | 2 | 3 | xl5-sumar-si | Informe de cobros de la Gestoría Albaida |

Pesos del banco, proporcionales a las horas (M01 10 h, M02 8 h y 4 h cada uno de M03-M05): 33, 27, 13,
13 y 14.

## 2. Cambios respecto al currículo original (doc 07 §4)

- **Prácticas «X» y rúbrica «Rb» de M03**: como en el piloto (C-06), se sustituyen por preguntas de
  test y de «¿qué devuelve?» con cuadrícula. M03 es de interfaz (estilos, paneles, impresión) y no se
  puede corregir calculando; la rúbrica llegará con P3 si se aprueba.
- **Criterios con fechas de M05**: se dejan para M07, donde se explican las fechas como número de serie
  (MF-24). M05 usa criterios de texto, de número, de celda (`">="&G1`) y comodines.
- **REDONDEAR.MAS, ENTERO y RESIDUO** estaban previstas para M04 en el registro del motor. Se
  implementan ya (son pequeñas), pero las unidades de M04 no las usan todavía.

## 3. Ejercicios obligatorios

| Unidad | Obligatorios (fórmula) | Qué comprueban |
|---|---|---|
| xl4-si | xl4-si-12, xl4-si-13 | `>=` frente a `>` en el límite; umbral en celda fijada con $ |
| xl4-logicas | xl4-log-12, xl4-log-14 | Y frente a O; orden de los tramos y «en otro caso» de SI.CONJUNTO |
| xl5-sumar-si | xl5-sum-11, xl5-sum-12 | Rangos fijos y criterio en celda; orden de argumentos de SUMAR.SI.CONJUNTO |
| xl5-contar-si | xl5-con-11, xl5-con-13 | Dos criterios; MAX.SI.CONJUNTO con 0 cuando nada cumple |

Las unidades de M03 no tienen ejercicios de fórmula: se superan con el 80 % del test.

## 4. Volumen

| Unidad | Test | ¿Qué devuelve? | Fórmula | Total |
|---|---|---|---|---|
| xl3-formato-celdas | 8 | 3 | 0 | 11 |
| xl3-libros | 8 | 2 | 0 | 10 |
| xl4-si | 6 | 5 | 4 | 15 |
| xl4-logicas | 6 | 5 | 4 | 15 |
| xl5-sumar-si | 6 | 4 | 4 | 14 |
| xl5-contar-si | 6 | 4 | 4 | 14 |
| **M03-M05** | **40** | **23** | **16** | **79** |
| Con M01-M02 | 98 | 59 | 33 | **190** |

## 5. Fuentes

Páginas del soporte de Microsoft en español, consultadas el 17/11/2026: función SI; SI con Y, O y NO;
SI.CONJUNTO; SI.ERROR; SUMAR.SI; SUMAR.SI.CONJUNTO; CONTAR.SI.CONJUNTO; PROMEDIO.SI; MAX.SI.CONJUNTO;
inmovilizar paneles; ancho de columnas; bordes; agrupar hojas; área de impresión; imprimir títulos; ver
saltos de página. Las URL están en cada unidad (`sources`).
