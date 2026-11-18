# Cambios

Los cambios importantes del proyecto, del más reciente al más antiguo. El formato sigue
[Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/).

El proyecto no publica versiones numeradas: cada merge a `main` se publica en la web. Por eso los
cambios se agrupan por fecha de merge, con el número de pull request entre paréntesis.

## [Sin publicar]

### Añadido
- Excel profesional, P4.1: módulos M03 (formato profesional y gestión de libros), M04 (funciones
  lógicas) y M05 (agregación condicional). 6 unidades y 79 ejercicios más (190 en total), comprobados con
  el motor. El motor calcula 16 funciones nuevas: SI, Y, O, NO, SI.CONJUNTO, SI.ERROR, REDONDEAR.MAS,
  ENTERO, RESIDUO, SUMAR.SI, SUMAR.SI.CONJUNTO, CONTAR.SI, CONTAR.SI.CONJUNTO, PROMEDIO.SI,
  MAX.SI.CONJUNTO y MIN.SI.CONJUNTO, con criterios y comodines (DEC-021); 58 casos de referencia nuevos
  contrastados con LibreOffice.

- Excel profesional, fase P2: el curso ya se ve en `#/academia/excel` (alias `#/excel-academy`), en
  el menú y en la portada. M01 y M02: 9 unidades con explicación, ejemplos resueltos, ejercicio guiado,
  caso, errores frecuentes, resumen y fuentes, y 111 ejercicios (58 de test, 36 de «¿qué devuelve?» y 17
  de «escribe la fórmula») comprobados con el motor al generar el curso. Práctica por unidad, repaso
  espaciado, unidades «completadas» y «superadas», y avisos de no afiliación y de corrección formativa
  (DEC-020). Sin XP, sin tablas nuevas: el progreso va en el documento del curso de la cuenta.
- Excel profesional, fase P1: motor de fórmulas propio (`frontend/js/excel/formula/`, DEC-019) con
  8 funciones, operadores, referencias y copia de fórmulas; corrección de ejercicios por lo que hace la
  fórmula (`frontend/js/excel/checks.js`); cuadrícula y editor accesibles (`frontend/js/excel/views.js`);
  194 casos de referencia (138 contrastados con LibreOffice). El generador de cursos acepta cursos sin
  módulo oficial y ejercicios de fórmulas. Sin cambios visibles: la ruta llega con el contenido (P2).
- Excel profesional, fase P0: catálogo de cursos por familias (`frontend/js/catalog.js`, DEC-018).
  El curso `excel` (familia academia) tiene ya documento de progreso en la cuenta y sincronización,
  sin contenido ni ruta visibles todavía. Los cursos de DAW no cambian.
- Especificación de Excel profesional en `docs/excel-academy/`: especificación maestra con los
  registros de decisiones y nueve anexos (arquitectura, requisitos, motor de fórmulas, datos, API,
  currículo M1-M2, pruebas, riesgos y hoja de ruta P0-P5).
- La POO entra en el simulacro de Preparación DAW como cuarta competencia (peso 20; Fundamentos y
  Programación pasan a 30 y Lógica a 20), solo con las 150 preguntas de su banco. La prueba de nivel no
  cambia.
- Hitos verificados (#109): con cuenta, el simulacro del PCAP lo elige, cronometra y corrige el
  servidor (`/api/v1/verified`), que rechaza respuestas imposibles, entregas fuera de tiempo y
  entregas repetidas con otras respuestas, y no deja ver los de otra cuenta. La web distingue lo
  verificado de lo local (orientativo) en el resultado, el panel del PCAP y los certificados
  (`docs/HITOS_VERIFICADOS.md`).
- Límites de intentos compartidos (#110): por IP, por cuenta y por email de recuperación se guardan
  en PostgreSQL (tabla `rate_limits`, con seudónimos HMAC), con una sola sentencia atómica por
  intento y ventana deslizante. Valen con varias instancias de la API; si la base de datos falla,
  cada instancia vuelve a limitar en memoria. Prueba de concurrencia en PostgreSQL en cada CI.
- `GET /api/v1/ready`: comprueba la base de datos y que el esquema está en la última migración (503
  sin detalles si no); `/api/health` sigue sin tocar la base de datos para que Render no reinicie en
  bucle. Script de copia y restauración (`scripts/ops/copia_bd.py`) con salvaguardas, ensayo en cada
  CI y guía de operación: monitor, copias, restauración y vuelta atrás (`docs/OPERACION.md`, #111).
- `deployment-check.yml`: comprueba el artefacto de Pages, la imagen Docker del backend y los workflows
  sin desplegar nada, y `dependabot.yml` vuelve (hacia `main`). Lo útil del PR #104, sin la rama `develop`.
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
- Módulo de POO, PR B: Unidad 7 (asociación, agregación y composición, delegación, herencia frente a
  composición; ejercicio principal Cliente, Pedido y Producto) y Unidad 8 (métodos especiales:
  `__str__`, `__repr__`, `__eq__`, `__len__` y, como avanzados, `__contains__`, `__iter__` y
  `__next__`; ejercicio principal CarritoCompra), con 53 ejercicios, 30 preguntas de banco y 12
  errores típicos nuevos.
- Módulo de POO, PR C: Unidad 9 (responsabilidad única, cohesión y acoplamiento, composición frente a
  herencia, SOLID, type hints, docstrings y `dataclasses`, módulos y refactorización; ejercicio
  principal: refactorizar una tienda) y Unidad 10 (proyecto biblioteca en 6 fases con excepciones
  propias, diagrama de clases accesible, rúbrica de 100 puntos y retos de ampliación), con 52
  ejercicios, 30 preguntas de banco (150 en total) y 16 errores típicos nuevos (#134).
- Módulo de POO, PR D: el cuestionario de cada unidad tiene nota (se supera con 11 de 15, el 70 %, y se
  guarda la mejor), evaluación final de 30 preguntas en `#/poo` (3 por unidad, una de cada nivel,
  corregida al terminar; se supera con 21) y «Repasar las preguntas falladas» en cada unidad. Las notas
  se sincronizan con la cuenta (`quizzes`) (#139).
- Módulo de POO, PR E: el índice `#/poo` muestra el progreso por unidad (prerrequisitos, lecciones,
  ejercicios obligatorios, cuestionario, dominio y si está superada), los CE del currículo que trabaja
  el módulo, siempre como propuesta, y la bibliografía general. Pruebas del grafo de prerrequisitos y de
  que la normativa de FP no respalda conceptos de Python.
- Correspondencia con los RA y CE oficiales en los cursos de DAW: cada lección y cada pregunta (520)
  dice qué CE trabaja y con qué estado (`verified`, `proposed` o `unassigned`). Hoy todo es
  `proposed`, pendiente de revisión docente. Mapa en `scripts/courses/curriculum_map.py`, validado al
  generar los cursos y en las pruebas (#106).
- «Mi progreso» muestra, por módulo de DAW, los criterios de evaluación agrupados por RA y si se han
  practicado, sin practicar o no tienen preguntas, con el aviso de que practicar no es superar (#106).
- Monitor de CI: `ci-monitor.yml` diagnostica cada ejecución de CI y avisa con una incidencia
  `ci-monitor` (nuevo, recurrente, corregido, cancelado u obsoleto); `scripts/ci-monitor/` y
  `docs/CI_CD_MONITORING.md` (#103).
- Documentación de proyecto: `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, este `CHANGELOG.md`, índice
  de `docs/` y plantillas de issues y de pull request.
- Lista de comprobación para activar Brevo en Render, con plantilla, errores, abuso y remitente
  (`docs/DEPLOY.md` §5).

### Corregido
- Excel profesional: en las preguntas de test la respuesta correcta era siempre la primera opción.
  Ahora las opciones se barajan con una semilla fija por pregunta.
- Excel profesional: «elige el resultado» muestra bien los errores (#¡DIV/0!) y los valores lógicos.
- Excel profesional: contraste insuficiente del texto de los módulos «Próximamente» en tema claro.

### Cambiado
- Seguridad (RT-004): la web ya no usa estilos en línea propios. Las barras de progreso pintan
  `data-meter="NN"` y `frontend/js/meters.js` lo pasa a `--value` con el CSSOM; los pocos `style="…"`
  fijos de `index.html` pasan a clases. La CSP publicada mantiene `'unsafe-inline'` en `style-src`
  porque el botón de Google (GSI) inyecta `<style>` y `style="…"` y sin él dejaba de funcionar; una e2e
  sirve la página con la CSP estricta y comprueba que ningún código propio los usa.
- Seguridad (RT-002): Python (Pyodide 314.0.7) se sirve desde la propia web, en `pyodide/v314.0.7/`, y
  no desde cdn.jsdelivr.net. `scripts/web/vendor_pyodide.py` lo toma del paquete npm de versión exacta,
  comprueba la huella sha512 de `package-lock.json` y la sha256 de cada archivo, y lo copian Pages, la
  comprobación de despliegue, las e2e y el lanzador local. La CSP ya no permite el CDN, el service
  worker guarda Python primero en caché y borra las copias antiguas del CDN, y la política de
  privacidad deja de citar a jsDelivr como tercero.
- Diálogos (MWG-08): Aspecto y Logros se cierran al pulsar fuera (`closedby="any"`, con respaldo para
  Safari); el de la cuenta no, para no perder lo escrito. Desplazarse sobre un diálogo ya no mueve la
  página de fondo (`overscroll-behavior`).
- Manifest de la app (MWG-09): nombre actual, `id`, categoría, accesos directos a Aprender, Practicar y
  DAW, y la app instalada empieza en Aprender en vez del curso PCAP.
- Fuentes (MWG-10): respaldos con las medidas de Inter y Fraunces (`size-adjust`, `ascent-override`):
  mientras llegan, el salto de la portada pasa de 138 px a 34 px.
- Código (MWG-11): `toSorted()`, `toReversed()` y `replaceChildren()` donde el `legacy-scan` lo indicaba.
- Rendimiento (MWG-03): Aprender, Teoría, Practicar y el panel piden el contenido (`learning.json`,
  172 KB comprimido) a la vez que el módulo de su zona, no después. En un móvil con 4G lenta el
  contenido principal de Practicar y Teoría aparece unos 0,25 s antes (5,8 s → 5,6 s).
- Rendimiento (AUD-024): Aprender, PCAP, DAW, Ciberseguridad, Planes, el panel y el certificado se
  descargan la primera vez que se abren, no al cargar la web. La portada pasa de 68 a 50 scripts y de
  ~2 MB a ~1,7 MB; en un móvil con 4G lenta su LCP baja de 6,3 s a 4,6 s y el de una lección de 7,9 s
  a 6,3 s. Si una zona no se puede descargar se dice, y al volver a abrirla se reintenta. Si el menú del
  móvil se abre mientras llega una zona, se queda abierto.
- Todas las auditorías de axe de las e2e usan las reglas de WCAG 2.2 A/AA; el README y las guías dicen
  WCAG 2.2 AA y que falta la revisión manual con lector de pantalla.

### Corregido
- Sin conexión fiable la web ya no se queda esperando: el service worker usa la copia guardada si la
  red tarda más de 4 s (y la red la actualiza después), se registra al terminar de cargar para no
  competir con la primera visita y avisa cuando hay una versión nueva. Las llamadas a la API tienen
  tiempo límite (90 s, por el arranque en frío de Render) con un mensaje para reintentar.
  Diagnóstico Modern Web Guidance MWG-05, MWG-06 y MWG-07.
- La portada ya no enseña «Cargando lección…» con la consola vacía mientras carga: la cabecera y el
  hero se pintan sin esperar a `learning.json` y `lessons.json`, y el resto de secciones se añade debajo
  al llegar los datos (LCP móvil medido en local con 4G lenta: 11,7 s → 6,2 s). El aviso para cambiar a
  inglés flota abajo y ya no empuja la página (CLS 0,16 → 0). Diagnóstico Modern Web Guidance MWG-01 y MWG-04.
- Al entrar directo a una lección (enlace compartido o recarga) la página ya no salta: hasta que llega
  `lessons.json` solo se ve «Cargando…» y lo demás aparece de una vez (CLS medido en local: móvil 0,81 →
  0,01; escritorio 0,16 → 0,03). Diagnóstico Modern Web Guidance MWG-02.
- En el panel, las secciones («Cursos», «Logros»…) ya no pierden el foco de teclado al repintarse la vista
  cuando llega el progreso de la cuenta: sus enlaces no tenían con qué volver a encontrarlos (#106).
- Las pruebas e2e del panel y de la cuenta fallaban a veces porque seguían antes de que se cerrara el
  diálogo de cuenta, que es modal y deja el resto de la página sin foco. Ahora esperan a que se cierre.
- La auditoría de accesibilidad del PCAP fallaba a veces con `color-contrast` en `#toast`: axe empezaba
  en el hueco de 250 ms entre dos avisos en cola y medía el segundo a media transición. Ahora espera a
  que la cola se vacíe; dos pruebas nuevas lo vigilan, y también el contraste del aviso visible.
- Las casillas del diálogo de cuenta miden 24 × 24 px (WCAG 2.5.8): la de privacidad del bloque de
  Google medía 13 px y le faltaba separación. Lo detectó axe al pasar a las reglas de WCAG 2.2.
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
