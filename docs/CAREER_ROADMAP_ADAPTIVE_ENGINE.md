# Career Roadmap · Dominio y estados

El Career Roadmap **no tiene un motor propio**: agrega lo que ya mide el motor adaptativo 2.0
([`ADAPTIVE_ENGINE.md`](ADAPTIVE_ENGINE.md)) y los cursos de DAW. Todo está en
`frontend/js/career/career-data.js`: funciones puras y deterministas (los mismos datos y la misma fecha
dan el mismo resultado), probadas en `tests/unit/career-data.test.mjs`.

> Las cifras son estimaciones para orientar el estudio. No son una calificación ni garantizan un empleo.

## Dominio de una competencia (0-100)

Cada competencia tiene fuentes (`sources` en el catálogo). Cada fuente da un valor `v` y una evidencia `e`, entre 0 y 1:

| Fuente | v | e |
|---|---|---|
| Concepto | dominio del motor 2.0 (ya incluye la retención) | confianza del motor 2.0 |
| Bloque de un curso | acierto con el último intento de cada pregunta | cobertura: entera a partir de la mitad del bloque respondida (`blockCoverage`, la misma regla que la preparación del PCAP) |
| Proyecto | criterios marcados / criterios | 1 si hay enlace válido y algún criterio marcado; si no, 0 |

```
score      = Σ v·e / n        (n = número de fuentes; 0-1, se muestra 0-100)
confidence = Σ e / n
enough     = confidence ≥ 0,5                         (MIN_CONFIDENCE del motor)
ready      = enough y score ≥ 0,6 y ningún concepto «se está olvidando»   (READY_SCORE del motor)
level      = 0 sin evidencias; 1 si score < 0,4; 2 si < 0,8; 3 a partir de 0,8   (se compara con `target`)
```

- **Lo que no se ha practicado cuenta como 0.** Acertar una fuente de cuatro da como mucho un 25 %.
- **Contenido estudiado ≠ dominio.** Marcar unidades no sube el dominio; solo cambia el porcentaje de contenido.
- **Olvido:** si algún concepto de la competencia «se está olvidando» (motor 2.0), deja de estar firme.

## Estado de una fase

El bloqueo depende de `requires`, nunca de la posición de la fase. Un prerrequisito se cumple con `completed` o `needs_review`.

| Estado | Cuándo |
|---|---|
| `locked` | Algún prerrequisito no se ha cumplido (`missing` dice cuáles) |
| `completed` | Todas las unidades estudiadas, el proyecto entregado (enlace + todos los criterios) y todas sus competencias `ready` |
| `needs_review` | Unidades y proyecto hechos, pero alguna competencia no está firme o se está olvidando (`weak`) |
| `in_progress` | Alguna unidad estudiada, algún criterio marcado o alguna evidencia en sus competencias |
| `available` | Lo demás |

`needs_review` no bloquea las fases siguientes: olvidar algo no debe quitar el acceso a lo que ya se abrió.

## Siguiente actividad (`overview`)

Fase activa: la primera en curso o a revisar; si no hay, la primera disponible. Dentro de ella, por este
orden: la primera unidad sin estudiar, el proyecto y la competencia más débil (empate: orden alfabético).
Cada propuesta lleva su motivo (`next-unit`, `project-pending`, `skill-weak`, `skill-forgotten`).
En el Sprint 6 esta elección pasará a `recommend.js` con la prioridad explicable del motor 2.0.

## Limitaciones conocidas

- **Proyectos autoevaluados:** la plataforma no comprueba el repositorio; los criterios los marca el
  alumno. Se indica en cada fuente (`selfAssessed`).
- 10 de las 24 competencias (FastAPI, Docker, ORM, testing automatizado…) solo tienen proyectos como fuente hasta
  que haya contenido propio (Sprint 3) o evaluaciones (Sprint 5).
- Las fuentes pesan lo mismo dentro de una competencia; no hay datos de uso para ponderarlas (como DEC-009).
- Una unidad nueva en el catálogo puede devolver una fase completada a «en curso».
