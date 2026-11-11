# Cambios

Los cambios importantes del proyecto, del más reciente al más antiguo. El formato sigue
[Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/).

El proyecto no publica versiones numeradas: cada merge a `main` se publica en la web. Por eso los
cambios se agrupan por fecha de merge, con el número de pull request entre paréntesis.

## [Sin publicar]

### Añadido
- Módulo de POO, Sprint 1: índice `#/poo` con las 10 unidades, página de unidad con objetivos,
  lecciones con ejemplos ejecutables y mini-quiz, ejercicios guiados y autónomos, autoevaluación,
  resumen, criterios de superación y currículo (propuesto); la Unidad 2 (`#/teoria/poo`) ya tiene el
  formato nuevo; lecciones completadas en el progreso; validadores en `build_learning.py`
  (`docs/MODULO_POO.md`).
- Módulo de POO, Sprint 2: Unidad 1 (fundamentos: procedural frente a objetos, modelado, pilares) y
  Unidad 3 (atributos de clase, `@classmethod`, `@staticmethod` y métodos que protegen el estado),
  con 27 ejercicios nuevos y 7 errores típicos; la Unidad 2 pasa a pedir la Unidad 1.
- Módulo de POO, Sprint 3: Unidades 4 (encapsulación, `_x`/`__x`, `@property`), 5 (herencia,
  `super()`, sobrescribir) y 6 (polimorfismo, duck typing, clases abstractas con `abc`), con 42
  ejercicios nuevos y 16 errores típicos.
- Módulo de POO, PR A: formato nuevo de unidad con buenas prácticas, referencias bibliográficas de
  un catálogo cerrado (pendientes de comprobación), prácticas adicionales y cuestionario de 15
  preguntas por unidad (90 en las Unidades 1 a 6, con el porqué de cada opción incorrecta); un
  ejercicio principal por unidad; lecciones nuevas de `__str__` y de herencia múltiple y MRO.
- Monitor de CI: `ci-monitor.yml` diagnostica cada ejecución de CI y avisa con una incidencia
  `ci-monitor` (nuevo, recurrente, corregido, cancelado u obsoleto); `scripts/ci-monitor/` y
  `docs/CI_CD_MONITORING.md` (#103).
- Documentación de proyecto: `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, este `CHANGELOG.md`, índice
  de `docs/` y plantillas de issues y de pull request.
- Lista de comprobación para activar Brevo en Render, con plantilla, errores, abuso y remitente
  (`docs/DEPLOY.md` §5).

### Cambiado
- Todas las auditorías de axe de las e2e usan las reglas de WCAG 2.2 A/AA; el README y las guías dicen
  WCAG 2.2 AA y que falta la revisión manual con lector de pantalla.

### Corregido
- La auditoría de accesibilidad del PCAP fallaba a veces con `color-contrast` en `#toast`: axe empezaba
  en el hueco de 250 ms entre dos avisos en cola y medía el segundo a media transición. Ahora espera a
  que la cola se vacíe; dos pruebas nuevas lo vigilan, y también el contraste del aviso visible.
- Las casillas del diálogo de cuenta miden 24 × 24 px (WCAG 2.5.8): la de privacidad del bloque de
  Google medía 13 px y le faltaba separación. Lo detectó axe al pasar a las reglas de WCAG 2.2.

### Corregido
- Cerrar sesión justo después de entrar ya no se queda con la sesión abierta: las subidas del
  progreso van de una en una (#103).
- Si la API no puede cerrar la sesión, se avisa en vez de fingir que se ha cerrado (#103).
- «Mi perfil» ya no borra lo que se está escribiendo cuando la vista se repinta (#103).
- La prueba del portapapeles usa el portapapeles real en Chromium y WebKit (#103).

## 2026-11-04

### Añadido
- Motor adaptativo 2.0 en «Aprender»: dominio por evidencias, confianza, olvido, repaso espaciado
  común y plan de «Hoy» con el motivo de cada recomendación (#97).
- Planificador diario sincronizado con la cuenta: tiempo disponible, exámenes y entregas (#97).
- `docs/ADAPTIVE_ENGINE.md`, `docs/DECISIONS.md` y la auditoría de evolución (Fase 0) (#97).

### Cambiado
- README con enlace a «Aprender» y al motor adaptativo (#98).

## 2026-11-03

### Añadido
- Interfaz en inglés y código protegido del traductor del navegador (#90).
- Opciones de lectura, contraste alto y pruebas de teclado y reflujo (#89).
- Aviso de la descarga de Python en conexiones lentas (#88).
- Lenguajes de marcas como asignatura piloto, progreso por lección y recursos con licencias (#87).
- Entornos de desarrollo con la unidad completa en las 4 lecciones (#94).
- Auditoría del temario de DAW, ids estables y pruebas de coherencia de los cursos (#93).
- Política de privacidad real, registro de tratamientos y procedimiento de incidentes (#79).

### Corregido
- El progreso ya no se pierde al cerrar sesión; las sesiones se renuevan y la consola no se rompe (#91).
- Accesibilidad con WCAG 2.2, corrección de ejercicios más clara y errores de formulario (#92).

## 2026-11-02

### Añadido
- Rediseño con la identidad ámbar sobre grafito y tokens en un solo archivo (#76, #78).
- Portada con rutas reales y «Continúa donde lo dejaste» (#80).
- Lección en tres áreas y catálogo de DAW en lista (#81).
- Editor de la consola con barra de estado y errores aparte (#82) y botón «Detener» (#85).
- Página «no encontrada» (#74).
- Agente `mejorador-web` y script de inspección de la web (#69).
- Auditoría técnica (Fase 1) (#70).

### Corregido
- Dos pestañas o dispositivos ya no se pisan el progreso: versión del documento y respuesta 409 (#72, #77).
- Practicar y Progreso en el móvil (#73, #75, #83).
- Títulos de pestaña propios, Progreso sin lecturas dobles y atajos ⌘ en Mac (#86).

## 2026-10-29

### Añadido
- Agentes `buscador-mejoras` (#64) y `red-teamer` (#67).
- Memoria y guía de defensa completadas con datos del código (#66).

## 2026-10-26

### Cambiado
- Proyecto simplificado e integración del currículo oficial de DAW de Castilla y León (#62).

### Eliminado
- Tutor con IA, A2A, app Android y agentes AppSec y LegalDocs (#62).

## 2026-10-20

### Añadido
- Portada pública en `#/portada` (#57).
- CSP de producción y cuentas de Google seguras (#55, #58).

## 2026-10-19

### Añadido
- Inicio de sesión con Google (#46, #47, #48).
- Panel integral del alumno en `#/panel` (#49).

## 2026-10-08

### Añadido
- Emails de recuperación de contraseña por la API HTTPS de Brevo (#44).
