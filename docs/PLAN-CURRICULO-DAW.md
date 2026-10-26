# Currículo oficial de DAW: diagnóstico y plan técnico

Fases 1 a 3 del encargo «integrar el currículo oficial de DAW». Fecha: 26 de octubre de 2026. Este documento **no cambia código**: describe lo que hay, lo que dice la normativa y cómo se podría implementar. El tutor con IA queda fuera por decisión del autor.

## 1. Diagnóstico del proyecto

### Lo que ya existe y sirve

| Necesidad del encargo | Lo que hay hoy | Dónde |
|---|---|---|
| Cursos de módulos de DAW | 5 cursos con teoría, ejercicios y banco de preguntas: Programación (163 preguntas), Bases de datos (110), Entornos (51), JavaScript (50) y Java (80) | `frontend/data/courses/<curso>/`, generados por `scripts/courses/` |
| Evaluación inicial | Prueba de nivel por concepto, no solo una nota global | `frontend/js/learn/exam.js`, `learn-app.js` |
| Dominio por concepto y errores frecuentes | Modelo de dominio, errores activos y repaso espaciado | `frontend/js/learn/mastery.js` |
| Itinerario y refuerzo | «¿Qué estudio ahora?»: repasos, errores recientes y «Necesitas reforzar X antes de Y» | `frontend/js/learn/recommend.js` |
| Simulacros | Simulacros cronometrados del PCAP y de la preparación DAW, corregidos al final | `frontend/js/learn/exam.js`, `pcap.js` |
| Seguimiento del progreso | Progreso por curso y por concepto, guardado en la cuenta; panel del alumno | `/api/v1/course-state/{curso}`, `#/panel` |
| Tipos de actividad | Test, ¿qué muestra?, completar, ordenar, encontrar el error y escribir código (Python con Pyodide; SQL, JS y Java comprobados al generar el temario) | `learning.json`, `courses/*/bank.json` |
| Privacidad | Exportar y borrar todos los datos de la cuenta | `/api/v1/users/me/export` y `/delete` |
| Control de acceso | Cada alumno solo ve y cambia sus datos; probado | `backend/tests/test_security_isolation.py` |

### Lo que falta

1. **No hay modelo curricular.** Los cursos no tienen resultados de aprendizaje (RA) ni criterios de evaluación (CE). Los códigos oficiales (0485, 0484, 0487) solo aparecen como texto en `frontend/js/course-store.js` y en los docstrings de los scripts.
2. **Faltan 12 de los 17 módulos del plan vigente** (ver 2.2).
3. **No hay rol de administrador.** `User` no tiene roles (`backend/app/models.py`), y el contenido se publica con los scripts y un pull request.
4. **Las preguntas no están etiquetadas por RA.** Tienen `block` y `lesson`, pero no la relación con el currículo.
5. **Origen de los materiales:** las UT y UD de Programación, Bases de datos y Entornos siguen los apuntes del centro («temario del centro» en los scripts). Son programación didáctica o material del centro, no normativa.

### Riesgos técnicos detectados

- Si el currículo va a la base de datos, habría que tocar el backend, las migraciones y la autorización. Si va en JSON generado por un script, encaja con lo que ya hay.
- Importar documentos subidos por un usuario (PDF y similares) abre problemas de seguridad: tipos de archivo, tamaño, almacenamiento en Render y contenido malicioso. Es demasiado para el alcance del proyecto.

## 2. Currículo oficial verificado

### 2.1 Normativa aplicable

| Nivel | Norma | Qué fija | Estado |
|---|---|---|---|
| Estatal (título) | Real Decreto 686/2010, de 20 de mayo (BOE-A-2010-9269) | Título de Técnico Superior en DAW y enseñanzas mínimas | Vigente, **modificado** |
| Estatal | Real Decreto 405/2023, de 29 de mayo (BOE-A-2023-13221), artículo tercero | Actualiza el título: reescribe el anexo I con los RA y CE de 0483, 0484, 0485, 0373, 0487, 0612, 0613, 0614 y 0615. Entra en vigor a los 20 días de su publicación (23/06/2023) | Verificado en el BOE |
| Estatal | Real Decreto 500/2024, de 21 de mayo (BOE-A-2024-10685), artículo séptimo | Para DAW (grupo a): suprime FOL, EIE y FCT; añade 0179, 1709, 1710, 1665 y 1708, cuyos RA están en los anexos X, V, VII y VIII del RD 659/2023; cambia «Proyecto» por «Proyecto intermodular». **No toca los RA de los módulos técnicos** | Verificado en el XML del BOE |
| Estatal (sistema) | Real Decreto 659/2023, de 18 de julio | Ordenación del sistema de FP (proyecto intermodular, optatividad, formación en empresa) | Citado por la orden; no leído en detalle |
| Castilla y León (común) | Decreto 24/2024, de 21 de noviembre (BOCYL 25/11/2024) | Currículo común de los ciclos de grado superior. **Deroga el Decreto 43/2011**, el antiguo currículo de DAW en Castilla y León | Verificado por referencia |
| Castilla y León (ciclo) | **Orden EDU/1311/2024, de 26 de noviembre** (BOCYL núm. 234, 2/12/2024, BOCYL-D-02122024-27) | Duración, curso y horas semanales de cada módulo (anexos I y II) y espacios (anexo III). Entra en vigor el 3/12/2024 | **Verificado en el PDF oficial** |

La orden autonómica **no recoge los RA ni los CE**: remite al real decreto del título. Los RA y CE vigentes son los del anexo I del RD 686/2010 en la redacción del RD 405/2023, con lo que haya cambiado el RD 500/2024.

### 2.2 Módulos, horas y curso en Castilla y León (Orden EDU/1311/2024, anexos I y II)

| Código | Módulo profesional | Horas | Curso | h/semana | ECTS (RD 405/2023) |
|---|---|---|---|---|---|
| 0373 | Lenguajes de marcas y sistemas de gestión de información | 102 | 1º | 3 | 7 |
| 0483 | Sistemas informáticos | 170 | 1º | 5 | 10 |
| 0484 | Bases de datos | 170 | 1º | 5 | 12 |
| 0485 | Programación | 272 | 1º | 8 | 14 |
| 0487 | Entornos de desarrollo | 68 | 1º | 2 | 6 |
| 0179 | Inglés profesional (GS) | 68 | 1º | 2 | Pendiente |
| 1709 | Itinerario personal para la empleabilidad I | 102 | 1º | 3 | Pendiente |
| — | Módulo optativo I | 34 | 1º | 2 | — |
| 1665 | Digitalización aplicada a los sectores productivos (GS) | 34 | 2º | 1 | Pendiente |
| 0612 | Desarrollo web en entorno cliente | 231 | 2º | 7 | 9 |
| 0613 | Desarrollo web en entorno servidor | 264 | 2º | 8 | 12 |
| 0614 | Despliegue de aplicaciones web | 99 | 2º | 3 | 5 |
| 0615 | Diseño de interfaces web | 165 | 2º | 5 | 9 |
| 1708 | Sostenibilidad aplicada al sistema productivo | 34 | 2º | 1 | Pendiente |
| 1710 | Itinerario personal para la empleabilidad II | 68 | 2º | 2 | Pendiente |
| — | Módulo optativo II | 54 | 2º | 3 | — |
| 0616 | Proyecto intermodular de desarrollo de aplicaciones web | 65 | No figura en el texto extraído | — | Pendiente |
| | **Total** | **2000** | | **30 y 30** | |

Comprobaciones: primer curso 986 h y segundo 1.014 h, que suman 2.000; 30 horas semanales en cada curso. Dos detalles para revisar en el PDF: el módulo optativo I tiene 34 h con 2 h semanales (no cuadra con 34 semanas), y el curso del 0616 no aparece en la extracción de texto.

En el texto original de 2010 el 0616 se llamaba «Proyecto de desarrollo de aplicaciones web» y había 0617 FOL, 0618 EIE y 0619 FCT. En el plan vigente ya no están.

### 2.3 Resultados de aprendizaje comprobados (RD 405/2023)

| Módulo | Nº de RA | Con CE |
|---|---|---|
| 0485 Programación | 9 | Sí |
| 0612 Desarrollo web en entorno cliente | 7 | Sí |
| 0613 Desarrollo web en entorno servidor | 9 | Sí |
| 0614 Despliegue de aplicaciones web | 6 | Sí |
| 0615 Diseño de interfaces web | 6 | Sí |
| 0483 Sistemas informáticos | 7 | Sí |
| 0484 Bases de datos | 7 | Sí |
| 0373 Lenguajes de marcas | 7 | Sí |
| 0487 Entornos de desarrollo | 6 | Sí |
| 0179, 1709, 1710, 1665, 1708 | En el RD 659/2023 (anexos X, V, VII y VIII) | Pendiente de extraer |
| 0616 Proyecto intermodular | Sin localizar | Pendiente |

En total, los 9 módulos técnicos suman 64 RA y 516 CE (extraídos y comprobados en la fase A).

Los textos legales no tienen derechos de autor (art. 13 de la Ley de Propiedad Intelectual), así que los RA y CE se pueden copiar literalmente indicando la norma y el artículo.

### 2.4 Pendiente de verificar

1. ~~Tu plan de estudios real~~. **Resuelto:** el autor está en el plan de la Orden EDU/1311/2024.
2. **Calendario de implantación** del nuevo currículo en Castilla y León: no he encontrado el curso exacto.
3. **Modalidad y oferta del centro.** La orden fija la distribución horaria para los centros **públicos presenciales**. Escuela de Profesionales Alcazarén es un centro privado autorizado y tú estudias online, así que la distribución puede ser otra. Hacen falta las programaciones didácticas del centro.
4. **Módulos optativos** que ofrece el centro.
5. **Lenguaje de Programación (0485)** que usa el centro. El curso del proyecto está en Python; el de Java está marcado como «para más adelante».
6. RA de los módulos transversales (RD 659/2023) y del 0616. El RD 500/2024 ya está verificado.

## 3. Relación entre lo que hay y el currículo

| Curso del proyecto | Módulo oficial | Cobertura | Tipo de material |
|---|---|---|---|
| Programación (UT1-UT9) y núcleo por conceptos | 0485 Programación | Amplia en Python | Material de la plataforma basado en los apuntes del centro |
| Bases de datos (UD1-UD3 y ampliación) | 0484 Bases de datos | Parcial (falta diseño ER, normalización, programación en BD...) | Ídem |
| Entornos de desarrollo (UD1) | 0487 Entornos de desarrollo | Solo la primera unidad | Ídem |
| JavaScript | 0612 Desarrollo web en entorno cliente | Fundamentos, DOM y asincronía | Material de la plataforma |
| Java | 0485 (si el centro usa Java) | Básico | Material de la plataforma |
| PCAP | Ninguno | — | Certificación externa, complementaria |
| — | 0373, 0483, 0613, 0614, 0615, 0616 y transversales | Sin contenido | — |

Ninguna actividad se asociará a un CE concreto hasta que alguien revise esa relación (el autor o un profesor). Mientras tanto, las actividades se relacionan solo con el **módulo**, y la relación con el RA queda como «propuesta sin verificar».

## 4. Plan técnico

### 4.1 Principios

- **Misma arquitectura:** JSON estático generado por un script de Python con `--check`, como el resto del temario. Sin tablas nuevas en la base de datos y sin framework.
- **Cada dato con su origen.** Los campos tienen `source` (norma, artículo o anexo, URL) y `status`: `oficial`, `centro`, `plataforma` o `pendiente`. Ningún campo se rellena sin fuente.
- **Las prácticas son prácticas:** la interfaz dice siempre que las evaluaciones de la plataforma no son calificaciones del centro.
- **Gestión con Git en vez de panel de administración.** El catálogo se edita en `scripts/curriculum/`, el script lo valida y el cambio entra por pull request. El historial de Git hace de versionado, y la revisión del PR evita publicar datos sin revisar. Es sencillo, seguro y defendible. Un panel con subida de archivos queda fuera de alcance (ver 4.4).

### 4.2 Modelo de datos (propuesta)

`frontend/data/curriculum/daw-cyl.json`, generado por `scripts/curriculum/build_curriculum.py`:

```json
{
  "cycle": { "id": "daw", "name": "Técnico Superior en Desarrollo de Aplicaciones Web", "region": "Castilla y León", "hours": 2000 },
  "sources": [
    { "id": "orden-edu-1311-2024", "title": "Orden EDU/1311/2024", "url": "https://bocyl.jcyl.es/boletines/2024/12/02/pdf/BOCYL-D-02122024-27.pdf", "kind": "oficial" },
    { "id": "rd-405-2023", "title": "Real Decreto 405/2023", "url": "https://www.boe.es/diario_boe/txt.php?id=BOE-A-2023-13221", "kind": "oficial" }
  ],
  "modules": [
    {
      "code": "0485",
      "name": "Programación",
      "course": 1, "hours": 272, "weeklyHours": 8, "ects": 14,
      "source": "orden-edu-1311-2024#anexo-I",
      "learningOutcomes": [
        { "id": "0485-RA1", "text": "Reconoce la estructura de un programa informático…", "criteria": [{ "id": "0485-RA1-a", "text": "…" }], "source": "rd-405-2023#anexo-I" }
      ],
      "platformCourses": ["programacion", "java"],
      "status": "oficial"
    }
  ]
}
```

El script comprueba: códigos únicos, suma de horas igual a 2.000, que cada `source` exista, que cada `platformCourses` exista en `frontend/data/courses/` y que ningún RA ni CE esté vacío.

### 4.3 Fases de implementación

| Fase | Qué | Archivos | Esfuerzo | Pruebas |
|---|---|---|---|---|
| A | Catálogo: 17 módulos con horas, curso y fuente; RA y CE de los 9 módulos técnicos copiados del BOE | `scripts/curriculum/`, `frontend/data/curriculum/daw-cyl.json` | Medio (sobre todo copiar y revisar los RA y CE) | pytest: esquema, totales y fuentes; `--check` en CI |
| B | Vista «Currículo DAW» en `#/daw`: módulos por curso, RA y CE, fuente enlazada y qué cursos de la plataforma lo trabajan. Los módulos sin contenido aparecen como «sin material todavía» | `frontend/js/daw.js` (o un módulo nuevo `curriculum.js`), CSS | Medio | e2e de navegación y axe |
| C | Etiquetar las preguntas existentes con el módulo (campo nuevo `module` en los scripts de cursos, **sin cambiar ids ni textos**) | `scripts/courses/*.py` y los JSON regenerados | Bajo | `--check` y recuento de preguntas igual |
| D | Progreso por módulo en el panel, calculado con el estado de los cursos que ya existe; separar «completado» de «dominado» | `dashboard-data.js`, `dashboard.js` | Medio | unitarias de `dashboard-data` |
| E | Simulacro y prueba de nivel por módulo, reutilizando `exam.js` con un filtro por módulo y tipo de pregunta, y sin repetir preguntas recientes | `learn/exam.js` y la vista del curso | Medio | unitarias de selección |
| F | Relación de actividades con RA, solo cuando esté revisada (`status: "revisado"` y quién la revisó) | Scripts de cursos | Según el contenido | Validación en el script |

Orden recomendado: A → B → C → D → E. La fase F depende de que alguien revise las relaciones.

### 4.4 Fuera de alcance (y por qué)

- **Tutor con IA:** descartado por el autor. Además necesitaría un proveedor de pago o Ollama, y `CLAUDE.md` prohíbe los servicios de pago.
- **Panel de administración con subida de documentos y roles:** exigiría roles, almacenamiento de archivos, análisis de PDF, un flujo de revisión y nuevas superficies de ataque. Con Git y pull requests se consiguen el versionado, la revisión y el origen de los datos sin nada de eso.
- **Generar preguntas nuevas automáticamente:** sin IA, las preguntas nuevas se escriben en los scripts y se comprueban al generar el temario, como hasta ahora.
- **Contenido de los 12 módulos sin material:** es trabajo de contenido, no técnico. El catálogo los muestra con sus RA aunque todavía no tengan ejercicios.

### 4.5 Criterios de aceptación revisados

1. El catálogo representa los 17 módulos de la Orden EDU/1311/2024, cada uno con su fuente.
2. Los RA y CE de los módulos técnicos coinciden literalmente con el BOE.
3. Ningún dato sin fuente: lo que falta se muestra como «pendiente de verificar».
4. El temario existente no pierde nada: mismos ids, mismos recuentos y `--check` en verde.
5. El alumno ve su progreso por módulo, separando completado de dominado.
6. Las prácticas se identifican como no oficiales.

## 5. Estado de la fase A (hecha)

Confirmado por el autor: está en el plan de la Orden EDU/1311/2024.

| Archivo | Qué hace |
|---|---|
| `scripts/curriculum/extract_boe.py` | Lee el XML oficial del RD 405/2023 y extrae literalmente los RA, los CE, los contenidos básicos, los ECTS y la duración mínima estatal de los 9 módulos técnicos. Normaliza el texto a NFC porque algunos párrafos del BOE usan tildes combinadas |
| `scripts/curriculum/rd_405_2023_daw.json` | Resultado de la extracción, guardado en el repositorio para que la CI no necesite red |
| `scripts/curriculum/build_curriculum.py` | Junta la tabla de la orden, los RA del BOE y la relación con los cursos de la plataforma. Valida códigos, horas (2.000 en total y 30 semanales por curso), fuentes y cursos. Tiene `--check` |
| `frontend/data/curriculum/daw-cyl.json` | Catálogo generado: 17 módulos, 9 con RA oficiales, 64 RA y 516 CE |
| `backend/tests/test_curriculum.py` | 15 pruebas: módulos de la orden, horas, número de RA por módulo, ids únicos, que no haya datos inventados en los pendientes y referencias válidas |
| `.github/workflows/ci.yml` | Paso nuevo: `build_curriculum.py --check` |

Comprobaciones de la extracción: hay 64 RA y 64 encabezados «Criterios de evaluación:» en el texto; los 580 textos (RA y CE) aparecen literalmente en el BOE; las letras de los criterios son consecutivas; y los ECTS coinciden con el BOE.

Para actualizar el catálogo cuando cambie la normativa: descargar el XML (`https://www.boe.es/diario_boe/xml.php?id=BOE-A-2023-13221`), ejecutar `extract_boe.py` con su ruta y después `build_curriculum.py`.

Siguen pendientes: los RA de los módulos transversales, el curso del 0616, la incoherencia de horas del optativo I y qué optativos ofrece el centro.

### Fase B (hecha): vista del currículo en la web

| Archivo | Qué hace |
|---|---|
| `frontend/js/curriculum.js` | Carga `daw-cyl.json` solo al entrar en la vista y pinta dos pantallas. `#/daw/curriculo`: tabla de módulos por curso con horas, horas semanales, estado («N RA oficiales» o «RA pendientes») y cursos de la plataforma. `#/daw/curriculo/<código>`: datos del módulo, RA desplegables con sus criterios, contenidos básicos y fuentes enlazadas. Todo el texto pasa por `escapeHtml` y las URL por `safeUrl` |
| `frontend/js/daw.js` | Enruta `#/daw/curriculo` hacia `curriculum.js` y enlaza el currículo desde el catálogo de cursos |
| `frontend/js/learn/daw-prep.js` | Enlace «Currículo oficial del ciclo» en la Preparación DAW |
| `frontend/css/daw.css` | Estilos `curr-*`. Reutiliza `.table-wrap`, `.history`, `.daw-faq` y `.course-hero`. El estado se indica con texto, no solo con color |
| `e2e/curriculum.spec.js` | 6 pruebas: navegación, contenido de un módulo, módulo pendiente sin datos inventados, módulo inexistente y axe (WCAG 2.1 AA) en claro y oscuro con un RA abierto |

Un módulo pendiente explica dónde están sus RA (por ejemplo, el RD 659/2023) y no muestra ninguno. El aviso «las actividades de la plataforma son prácticas» aparece en el índice y en cada módulo.

### Fase C (hecha): preguntas etiquetadas por módulo

Cada pregunta de los bancos de DAW lleva ahora `"module"` con el código oficial del módulo que trabaja: Programación y Java con 0485, Bases de datos con 0484, Entornos con 0487 y JavaScript con 0612. En total son 454 preguntas.

| Archivo | Cambio |
|---|---|
| `scripts/courses/course_builder.py` | `main(..., module="0485")` pone el módulo del curso a cada pregunta. `Q` admite `module` por si una pregunta concreta trabaja otro módulo |
| `scripts/courses/<curso>_course.py` | Cada curso indica su módulo en la llamada a `main` |
| `frontend/data/courses/*/bank.json` | Regenerados: solo se añade `"module"` |
| `scripts/curriculum/build_curriculum.py` | Ya no hay tabla «módulo → cursos» escrita a mano: se calcula con las etiquetas de las preguntas, junto con el número de preguntas por módulo (`platformQuestions`). Falla si una pregunta no tiene módulo o usa un código que no está en la orden |
| `frontend/js/curriculum.js` | Muestra «Programación, Java (243 preguntas)» |
| `backend/tests/test_curriculum.py` | Prueba nueva: toda pregunta tiene un módulo del catálogo y los recuentos cuadran |

Comprobación de que no se ha perdido nada: cada banco regenerado, quitando `"module"`, es idéntico al anterior (mismas preguntas, ids, textos y orden), y los `lessons.json` no cambian. En el diff de Git solo aparecen las 454 líneas `"module"` y la coma de la línea anterior.

Dos arreglos que salieron por el camino, sin cambiar ningún contenido:

- Los generadores (`course_builder.py`, `build_learning.py`, `build_curriculum.py` y `extract_boe.py`) escribían CRLF en Windows. Ahora escriben siempre LF, como pide `.gitattributes`.
- `run_python` de `entornos_course.py` y `programacion_course.py` dependía de la codificación de Windows: con `PYTHONIOENCODING=utf-8` el `--check` fallaba al leer «Diseño». Ahora el proceso hijo escribe y se lee siempre en UTF-8.

### Fase D (hecha): progreso por módulo en el panel

En «Mi panel › Mi progreso» hay una sección nueva, «Módulos de DAW». Muestra cada módulo que tiene preguntas en la plataforma con dos barras:

- **Practicadas:** preguntas respondidas al menos una vez («completado»).
- **Dominadas:** preguntas cuyas **dos últimas** respuestas son correctas (`MASTERY_STREAK = 2`). Un acierto suelto en un test puede ser suerte.

Debajo indica cuántos módulos del ciclo aún no tienen preguntas en la plataforma (ahora mismo, 13) y enlaza al currículo. La sección aclara que es una orientación de la plataforma, no una calificación del centro.

| Archivo | Cambio |
|---|---|
| `scripts/curriculum/build_curriculum.py` | Cada módulo guarda `platformQuestionIds` (ids de sus preguntas por curso), así el panel no descarga los cinco bancos. El catálogo crece unos 4 KB |
| `frontend/js/dashboard-data.js` | `moduleProgress(modules, answersOf)`: función pura que cuenta practicadas y dominadas por módulo con el progreso guardado. Ignora historiales dañados |
| `frontend/js/dashboard.js` | Sección «Módulos de DAW» en «Mi progreso». Se rellena al pintar, con el mismo patrón que la tarjeta de los cursos |
| `tests/unit/dashboard.test.mjs` | Prueba de `moduleProgress`: dominada frente a acierto suelto o fallo final, historial dañado y módulos sin preguntas |
| `e2e/dashboard.spec.js` | Prueba con progreso sembrado: 3 practicadas y 1 dominada de 110 en Bases de datos, auditoría axe y enlace a la ficha del módulo |

No hacen falta cambios en el backend: el progreso de cada curso ya se guarda en la cuenta (`/api/v1/course-state/{curso}`) y el cálculo se hace con esos datos.

Siguiente fase: E (simulacro y prueba de nivel por módulo, reutilizando `learn/exam.js`).

## 6. Información que sigue haciendo falta

1. Qué módulos optativos ofrece tu centro.
2. Si puedes compartir las programaciones didácticas de tus módulos (sin datos personales), para marcar las UT del centro como `centro` y no como `oficial`.

## Fuentes consultadas

- Orden EDU/1311/2024 (PDF oficial): https://bocyl.jcyl.es/boletines/2024/12/02/pdf/BOCYL-D-02122024-27.pdf y versión HTML: https://bocyl.jcyl.es/html/2024/12/02/html/BOCYL-D-02122024-27.do
- Real Decreto 405/2023: https://www.boe.es/diario_boe/txt.php?id=BOE-A-2023-13221 (XML: https://www.boe.es/diario_boe/xml.php?id=BOE-A-2023-13221)
- Real Decreto 500/2024: https://www.boe.es/diario_boe/txt.php?id=BOE-A-2024-10685
- Real Decreto 659/2023: https://www.boe.es/buscar/act.php?id=BOE-A-2023-16889
- Real Decreto 686/2010 (texto original): https://www.boe.es/buscar/act.php?id=BOE-A-2010-9269
- Decreto 43/2011 (derogado): https://www.educa.jcyl.es/es/resumenbocyl/decreto-43-2011-14-julio-establece-curriculo-correspondient
- Ficha del título en el portal de FP de Castilla y León: https://www.educa.jcyl.es/fp/es/catalogo-titulos-fp-castilla-leon/catalogo-titulos-grado-superior/desarrollo-aplicaciones-web
