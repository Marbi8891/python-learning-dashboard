# Changelog

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/). Versionado [SemVer](https://semver.org/lang/es/).

## [Unreleased]

### Seguridad
- **Recuperación de contraseña revisada** ([docs/auth.md](docs/auth.md)):
  - nuevas rutas `POST /api/v1/auth/forgot-password` y `/reset-password`, alias de las actuales, que siguen funcionando para Android;
  - evento `auth.password_reset_failed` (T1110) por cada enlace no válido;
  - el enlace deja de valer justo en `expires_at`;
  - un enlace de un usuario que ya no existe responde 400 en lugar de 500;
  - en la web: campo «Repite la nueva contraseña», requisitos visibles, «Pedir un enlace nuevo» y un enlace incompleto lleva a pedir otro.
- Las migraciones de Alembic ya no desactivan los loggers creados antes, como `pld.security`, cuando se ejecutan en el mismo proceso que la app (modo local y tests).
- **Sesión de la web en una cookie `HttpOnly`** (ADR-0033): JavaScript ya no puede leer el token y la sesión sigue al recargar la página. Protección CSRF con la cabecera `X-PLD-Session`. Si el navegador bloquea la cookie, se entra igual con el token solo en memoria. La app Android no cambia. Nuevo `POST /api/v1/auth/logout`.

### Añadido
- **Agentes A2A y Python Tutor** (ADR-0034, [docs/a2a.md](docs/a2a.md)): el backend puede servir agentes [A2A 1.0](https://a2a-protocol.org/) con el SDK oficial `a2a-sdk`, en la misma app FastAPI y junto a la API REST, que no cambia.
  - **Python Tutor** (`/a2a/python-tutor`): explica conceptos y errores, revisa el código **sin ejecutarlo**, propone ejercicios según el nivel y no da la solución de un ejercicio pendiente. Usa solo el progreso necesario de la sesión del alumno.
  - **Agent Card** pública en `/.well-known/agent-card.json`; el JSON-RPC exige la sesión de la API (Bearer o cookie), con tareas aisladas por usuario y 20 mensajes por minuto.
  - **Modelo intercambiable** (`AgentModelProvider`); de momento solo el simulado para desarrollo (`A2A_MOCK_MODEL`). A2A está desactivado por defecto.
  - **Web:** sección **Tutor Python** (`#/tutor`), visible solo si el servidor ofrece el agente.
  - Cliente de ejemplo con el SDK: `scripts/a2a/tutor_client.py`.
- **Núcleo educativo por conceptos** (ADR-0031): la plataforma se centra en aprender Python y aprobar Programación de DAW. El PCAP pasa a «Más».
  - **Menú:** Aprender · Teoría · Practicar · DAW · Progreso.
  - **Aprender:** «¿Qué estudio ahora?», con un plan corto en este orden: repasos, errores recientes, conceptos de DAW sin dominar y contenido nuevo si la base está firme. También muestra los puntos débiles, la ruta personal y la prueba de nivel.
  - **Teoría:** 22 conceptos con explicación (reutiliza la de las lecciones), un ejemplo línea a línea con su salida real, cuándo usarlo, los errores habituales y ejercicios.
  - **Practicar:** «Mis errores» con «Practicar este error», práctica por tipo de actividad y por concepto. Cada fallo se explica (qué falla, por qué, cómo pensarlo y cómo evitarlo) y vuelve al final con un ejercicio parecido.
  - **Preparación DAW:** competencias con «Necesitas reforzar X antes de pasar a Y», actividades de examen y simulacros cronometrados con corrección al final.
  - **Progreso:** dominio, estado y próximo repaso de cada concepto, errores frecuentes, actividad y simulacros.
  - **128 ejercicios de 6 tipos**, generados y **comprobados ejecutando Python** (`scripts/learning/build_learning.py --check`).
  - **Tests unitarios del frontend** con `node --test`: dominio, repaso, recomendación, selección, sesiones y simulacros.
  - **App Android 0.16.0:** pestaña «Hoy» con la misma lógica y el mismo progreso que la web.
  - Revisión de seguridad con los riesgos que siguen abiertos (`docs/security/revision-2026-10.md`).
- **Pantalla de bienvenida** (`#/bienvenida`), que se muestra en la primera visita. Es un **mapa con 5 paradas** (Aprender → Teoría → Practicar → Repasar → DAW) que se recorre con «Anterior / Siguiente», pulsando una parada o con las flechas; cada parada explica la sección con un ejemplo real. Al final: empezar de cero, prueba de nivel o el **recorrido por el menú**, que resalta cada opción real de la barra lateral con un globo explicativo (también en el móvil, donde abre el menú; se cierra con Escape). Las siguientes visitas van directas a «¿Qué estudio ahora?», y la presentación sigue enlazada desde Aprender y el pie del menú.

### Corregido
- **Contraste WCAG** que había roto el rediseño visual: la auditoría de accesibilidad fallaba en `main`. Se quitan también los degradados y el efecto cristal.
- **Test e2e de la cuenta:** tenía una carrera con la sincronización.
- **Móvil:** el rediseño reservaba la columna de la barra lateral (272 px vacíos) y estrechaba todas las páginas. También se quita la sombra que proyectaba el menú cerrado.

### Cambiado
- **Una sola app en el móvil** (ADR-0030): la CI ya no publica el APK de depuración en `main`, solo el de release firmado. El de depuración queda para los pull requests. Pasos para llevar el progreso de «Python PCAP (debug)» a «Python PCAP» con la sincronización.

### Añadido
- **App Android 0.15.0: la Ruta como un libro** (ADR-0029), que sustituye al camino de la 0.14.0:
  - cada tema es una página que se pasa deslizando;
  - arriba, el nombre del tema, con un desplegable de sus lecciones y otro con el índice de todos los temas;
  - cada página abre con una entradilla de la teoría y un único botón para continuar.
- **App Android 0.14.0: Ruta rediseñada, fluida y sin ruido visual** (ADR-0028):
  - un solo color de acento para la lección que toca;
  - una línea fina que une las lecciones y se colorea hasta donde has llegado;
  - cabeceras de unidad finas que se quedan fijas arriba;
  - barra de estado en texto, sin emojis;
  - pulso suave en la lección actual y botón «Ir a mi lección» cuando no está en pantalla.
- **App Android 0.13.0: cuenta y sincronización** (ADR-0026):
  - inicio de sesión con la cuenta de la web en la pestaña Perfil;
  - el progreso de todos los cursos se junta con el de la web sin perder nada, al abrir la app, al salir y con «Sincronizar ahora»;
  - la contraseña no se guarda y la sesión no va en las copias de seguridad del móvil;
  - la app sigue funcionando entera sin conexión y sin cuenta.
- **App Android 0.13.0: «Mi cuenta» como en la web** (ADR-0027). En la pestaña Perfil:
  - plan de estudio con la fecha de cada examen (sincronizada con la web) y el repaso de hoy;
  - progreso de todos los cursos con el tema más flojo y un botón para practicarlo;
  - historial de simulacros, certificados (se abren en la web) y 8 logros;
  - cambiar el nombre y la contraseña sin cerrar la sesión del móvil, y ver la actividad reciente de la cuenta.
- **«Mi cuenta» ampliada** (ADR-0025):
  - **plan de estudio:** fecha de examen de cada curso con los días que faltan, repaso pendiente de hoy y meta diaria de preguntas;
  - **progreso de todos los cursos** (web y app): dominio, tema más flojo con un enlace para practicarlo e historial de simulacros;
  - **logros y certificados**, con un certificado nuevo para cada curso de DAW (#/certificado/<curso>);
  - **perfil y seguridad:** cambiar el nombre y la contraseña (cierra las demás sesiones y mantiene esta) y ver la actividad reciente de la cuenta con el dispositivo aproximado, sin guardar la IP.
- **App Android 0.12.0: simulacro de examen** (ADR-0024):
  - PCAP con el reparto oficial (40 preguntas, 65 minutos);
  - cursos DAW con 30 preguntas según el peso de cada bloque (45 minutos, aprobado con un 50 %), incluido el de Programación en Python;
  - se corrige al entregar o al acabarse el tiempo;
  - nota por bloques y revisión de los fallos con su explicación;
  - el resultado se guarda con el mismo formato que la web.

### Seguridad
- **Protección con MITRE ATT&CK** (ADR-0023):
  - modelo de amenazas por táctica con mitigaciones, evidencias y estado, y capa para ATT&CK Navigator;
  - registro de eventos de seguridad con el ID de técnica y la IP y el email seudonimizados (detecta fuerza bruta, tokens falsificados o robados, abusos de recuperación y ataques de tamaño);
  - se rechazan las contraseñas comunes o que contienen el email o el nombre;
  - restablecer la contraseña levanta el bloqueo de la cuenta;
  - la consola avisa al pegar código que toca el navegador o la red;
  - política de privacidad actualizada.
- **Auditoría y endurecimiento integral** (ADR-0022):
  - el límite de intentos ya no se puede saltar falsificando `X-Forwarded-For`;
  - bloqueo por cuenta tras 10 fallos y límite de emails de recuperación;
  - Argon2id con menos memoria para que no se pueda tumbar el servidor;
  - cierre de sesión en todos los dispositivos;
  - cuerpos de las peticiones limitados a 300 KB;
  - `Cache-Control: no-store`, `/docs` desactivado en producción y TLS obligatorio hacia la base de datos;
  - STARTTLS con el certificado verificado, y los enlaces de recuperación nunca se escriben en el log.
- **Web:**
  - Content-Security-Policy;
  - protección contra la inserción en marcos (*clickjacking*);
  - se corrige una XSS a partir de la salida del código Python del alumno;
  - se valida el progreso guardado en el navegador o en la cuenta;
  - al cerrar sesión o borrar la cuenta se borran los datos personales del navegador;
  - la analítica respeta Global Privacy Control y no envía el token de recuperación.
- **Cadena de suministro:**
  - las GitHub Actions tienen permisos de solo lectura;
  - `pip-audit` y `npm audit` en la CI;
  - se valida el wrapper de Gradle;
  - Dependabot vigila también npm, Gradle y Docker;
  - se retiran el SDK de AWS y `dotenv`, que no se usaban.
- **Documentación:** política de privacidad y `SECURITY.md` actualizados.

### Añadido
- **Cursos de DAW en la web** (ADR-0021): nueva sección «Cursos DAW» (`#/daw`) con Programación, Bases de datos, Entornos, JavaScript y Java. Incluye teoría, mini-quiz, práctica por bloque con test, completar el hueco y ordenar líneas, y repaso espaciado. Con sesión iniciada, el progreso se comparte con la app Android. Los JSON de los cursos pasan a `frontend/data/courses/`, que la app ya incluye como assets.
- **Curso de Programación en Python** en la app Android (ADR-0020): 9 unidades de trabajo, de algoritmos y pseudocódigo a interfaces gráficas con PySide6, siguiendo el curso abierto DAW-Programacion de César San Juan Pastor (CC no comercial). Tiene 12 lecciones, 163 preguntas y 23 del mini-quiz, con ejercicios de escribir código. Cada respuesta de código se comprueba ejecutando Python en la CI, incluidos los ficheros y SQLite. El curso de Java se queda para más adelante.
- **«Mi cuenta» (área privada):** pantalla `#/cuenta` con el nombre, el email, la fecha de alta, el resumen de progreso y del examen PCAP, un botón para continuar y el acceso a la gestión de datos. Solo aparece en el menú con la sesión iniciada; sin sesión muestra la invitación a entrar.

## [1.0.0] - 2026-09-29

Primera versión estable. Resumen en `docs/RELEASE-1.0.0.md`.

### Añadido
- **Cabeceras de seguridad en la API** (`X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Strict-Transport-Security` y `Permissions-Policy`) con sus pruebas; el backend mantiene el 100 % de cobertura (412 pruebas).
- **Memoria del proyecto** (`docs/memoria/`) con diagramas de casos de uso, arquitectura y modelo de datos, y guion de demo y defensa (`docs/DEMO-Y-DEFENSA.md`).

### Cambios anteriores incluidos en 1.0.0

### Añadido
- **Preparación para publicar:** aviso legal, página 404 propia, vista previa al compartir (Open Graph y Twitter con imagen 1200×630), `robots.txt`, `sitemap.xml`, aviso si JavaScript está desactivado y analítica opcional sin cookies (GoatCounter, apagada hasta definir `goatcounter` en `config.js`; la política de privacidad la menciona solo cuando está activa).
- **Bases de datos según el temario del centro** (ADR-0019): el curso de SQL pasa a llamarse «Bases de datos» y se organiza por las UD1-UD3 del centro. Tiene 60 preguntas nuevas: tipos y modelos, fragmentación, Big Data, ficheros, RGPD y LOPDGDD, SGBD, NULL, ALTER y DROP, índices, usuarios, GRANT, REVOKE y roles, vistas, UNION, INTERSECT y EXCEPT, subconsultas y EXPLAIN. Incluye 6 ejercicios de escribir SQL. Las preguntas y el progreso anteriores se conservan.
- **Curso de Entornos de desarrollo** (ADR-0019), según la UD1 del centro: lenguajes y tipos de software, compilación y enlace, compiladores e intérpretes, máquinas virtuales y contenedores, paradigmas, fases del desarrollo, cascada, Scrum, Kanban y XP. Tiene 51 preguntas; las de código Python se comprueban ejecutándolas.
- **App Android nativa** en Kotlin + Jetpack Compose (`android/`, ADR-0011), entrega 1: panel de preparación del PCAP, práctica por bloque con corrección, explicación y enlace a la teoría, preguntas en español o inglés y funcionamiento sin conexión. Usa el mismo banco de preguntas que la web y guarda el progreso en el mismo formato.
- **App Android como curso tipo Duolingo** (entrega 2, ADR-0012):
  - ruta de unidades con lecciones cortas que se desbloquean en orden;
  - la pregunta fallada vuelve al final de la lección;
  - XP, racha derivada de la XP diaria, meta diaria elegible (10/20/30/50);
  - 5 vidas que se recuperan cada 4 h o terminando una tanda de práctica libre;
  - pantalla de celebración y perfil con los últimos 7 días.
- Workflow `android.yml`: tests del dominio en Kotlin, lint de Android y APK de depuración descargable.
- **Backend:** `GET/PUT /api/course-state/{curso}` guarda en la cuenta el estado de los cursos de SQL, JavaScript y Java de la app (ADR-0018). Incluido en la exportación y el borrado de datos.
- **App Android:** la práctica usa `PracticeViewModel` con flujo de datos en un solo sentido (`PracticeUiState`, `PracticeUserAction`) y una barra de progreso. La tanda se conserva al abrir la teoría y volver.
- **Ejercicios de escribir código** (ADR-0017): completar el hueco tecleando, ordenar líneas y encontrar la línea con el error. Hay 30 en el curso de Java y aparecen en la ruta, la práctica y la mazmorra. Cada uno se comprueba compilando y ejecutando la solución y el error.
- **Curso de JavaScript** en la app (ADR-0016). Tiene 10 lecciones, de las variables al event loop y `fetch`, con 50 preguntas y 20 del mini-quiz. Las respuestas de código se comprueban ejecutándolas con Node.js; las del DOM son teóricas.
- **Curso de Java** en la app (ADR-0016). Tiene 10 lecciones, de los tipos a las excepciones, con 50 preguntas y 20 del mini-quiz. Cada respuesta se comprueba compilando y ejecutando el código con Java 17 en la CI, incluidos los errores de compilación y las excepciones.
- **Curso de SQL** en la app (ADR-0016), junto al del PCAP, que no cambia. Tiene 10 lecciones de teoría, 50 preguntas para la ruta, la práctica y el juego, y 20 del mini-quiz. Cada respuesta se comprueba ejecutando el SQL en la CI. La app estrena selector de curso; la XP, la racha, las vidas y los récords son comunes a todos los cursos.
- **Modo «Jugar»** en la app (ADR-0015): la **Mazmorra del Intérprete** (5 plantas, una por bloque del PCAP; salas con bugs, jefes con cronómetro, monedas, comodines 50/50 y Curar; las respuestas cuentan para la preparación) y el minijuego **Bug Rush** (90 s, deslizar sí/no, multiplicador por combo). Récords guardados con el progreso.
- **App Android sin conexión** (ADR-0014): la teoría de las 27 lecciones se lee dentro de la app (explicación, ejemplo, ejercicio, mini-quiz corregido, reto, dudas frecuentes y fuentes). "Teoría" ya no abre la web y la app no pide permiso de internet.
- **Tarjetas de unidad más completas** en la ruta de la app: estado con color e icono (completada, en curso, bloqueada), bloque y peso en el examen, lecciones hechas con su barra y porcentaje de acierto en las preguntas de la unidad. Se leen como un solo elemento con TalkBack.
- **APK de release firmado** en la CI con la clave del proyecto, guardada en secretos de GitHub (ADR-0013). La build de depuración pasa a `io.github.marbi8891.pld.debug` y convive con la release.

### Corregido
- La web conservaba el progreso del PCAP pero **borraba de la cuenta el de la app Android** (XP, racha, ruta y récords) al guardar: ahora lo mantiene (ADR-0018).

## [1.0.0] - 2026-09-27

### Añadido
- **Preparación del PCAP en la cuenta:** simulacros, aciertos, fichas, repaso y plan se guardan en el servidor (`GET/PUT /api/pcap-state`, migración 4) y se fusionan al iniciar sesión en otro dispositivo. Incluido en «Descargar mis datos» y en el borrado de cuenta (ADR-0010).
- **Del fallo a la teoría:** cada pregunta y ficha enlaza a la lección que la explica. Al fallar, «Repasar la teoría» y «Practicar el bloque».
- **Repaso espaciado** (cajas de Leitner: 1, 3, 7, 14 y 30 días) de preguntas y fichas, con «Repaso de hoy» en el panel.
- **Plan de estudio:** con la fecha del examen, tareas de la semana (lecciones, bloques a practicar según lo que más puntos resta, repaso diario y simulacros).
- **Certificado de finalización** (no oficial) imprimible o en PDF, al completar las lecciones del examen y aprobar un simulacro.
- **PWA:** instalable en el móvil y usable sin conexión tras la primera visita; Pyodide queda guardado en el navegador.
- Guía para activar los emails de recuperación con Gmail (contraseña de aplicación) o un servicio transaccional.

### Cambiado
- Acciones de GitHub en sus versiones con Node 24 (checkout v7, setup-python v7, setup-node v5, upload-artifact v7, configure-pages v6, upload-pages-artifact v5, deploy-pages v5).

### Corregido
- Una línea demasiado larga en `e2e/start_backend.py` hacía fallar el lint de la CI desde la 0.8.0.

## [0.9.0] - 2026-09-27

### Añadido
- La web se enfoca en preparar el examen **PCAP-31-03** (ADR-0009): el temario se organiza por los 5 bloques oficiales, más un módulo de bases (nivel PCEP) y un extra fuera del examen.
- 12 lecciones nuevas: math, random y platform; paquetes, `__name__` y `sys.path`; jerarquía de excepciones y excepciones propias; Unicode; slicing y comparación de cadenas; métodos de string; variables de clase e instancia; herencia múltiple y MRO; introspección; comprensiones y lambda; closures y generadores; modos de E/S, binarios y errno.
- Zona **Examen PCAP** (`#/pcap`): simulacro de 40 preguntas y 65 minutos con el reparto oficial, práctica por bloque con corrección inmediata, 48 fichas de repaso y panel de preparación por bloque.
- Banco de 126 preguntas originales en español e inglés (a elegir), 18 % de «elige dos». Cada respuesta se demuestra con código que ejecutan los tests.
- Gamificación del examen: XP por preguntas acertadas y simulacros aprobados, racha de aciertos en la práctica y 7 logros nuevos («Primer simulacro», «Aprobado», «Con nota», «Bloque dominado», «En racha», «Memoria de elefante», «Listo para el PCAP»).

### Cambiado
- La carga de contenido elimina los módulos que se quedan sin lecciones al reorganizar el temario (conserva lecciones y progreso).

## [0.8.0] - 2026-09-26

### Añadido
- La web publicada se conecta a la API en producción (`https://pld-api.onrender.com`): cuentas, progreso sincronizado y RGPD. En localhost sigue usando la API local.
- Al cargar la página se despierta el servidor (el plan gratuito se duerme sin uso) y, si una petición tarda, se avisa de que puede tardar hasta un minuto.
- `/api/health` indica si hay email configurado. Sin SMTP, «¿Has olvidado tu contraseña?» ofrece el email de contacto en lugar de un enlace que nunca llegaría.
- Dependencias `@aws-sdk/client-s3`, `@aws-sdk/s3-request-presigner` y `dotenv` para Object Storage de Neon (S3). Aún no las usa ningún código.

## [0.7.1] - 2026-09-26

### Cambiado
- Despliegue del backend: API en Render (Frankfurt) y PostgreSQL en Neon (plan gratuito permanente, UE) en lugar de la base de datos gratuita de Render, que caduca a los 30 días (ADR-0008).
- Política de privacidad completada: responsable, contacto y proveedores.

### Corregido
- Las conexiones a PostgreSQL se comprueban antes de usarse (`pool_pre_ping`): evita errores tras un rato sin uso cuando la base de datos se suspende.

## [0.7.0] - 2026-09-26

### Añadido
- Estética editorial de academia: tinta, marfil y dorado, titulares en serif (Fraunces, alojada en el sitio) y tema claro en papel crema (ADR-0007).
- Portada como ficha del curso: nivel, duración estimada, qué aprenderás, temario desplegable con el estado de cada lección, qué incluye y requisitos.
- «Mi aprendizaje» (`#/perfil`): nivel, cifras, progreso por módulo, actividad de 12 semanas, logros e historial por lección.
- Cabecera de lección con módulo, número de lección, duración, quiz y dificultad del reto.
- Navegación «El curso» / «Mi aprendizaje» en la barra lateral y nuevo favicon.
- Tests: ficha del curso y perfil (e2e), auditoría WCAG de portada y perfil en los dos temas, datos del curso (backend).

### Corregido
- Un quiz con 0 aciertos no se registraba y la guía no pasaba al paso siguiente.

## [0.6.0] - 2026-09-26

### Añadido
- Portada con «Continuar donde lo dejaste», resumen del progreso y tarjetas por módulo.
- Guía en cada lección (Aprende → Practica → Comprueba) con un botón «Siguiente paso».
- Errores de Python explicados en español, con botón «Ir a la línea» (22 casos probados).
- Tema claro, oscuro o automático y tres tamaños de letra, recordados en el navegador.
- Tests: explicación de errores (backend); portada, guía, errores, apariencia, consola al lado y auditoría WCAG en los dos temas (e2e).

### Cambiado
- En pantallas de 1280 px o más, la consola queda fija al lado de la lección.
- La barra lateral agrupa el progreso y los XP en una sola tarjeta.
- Los colores salen de variables de tema (ADR-0006).

## [0.5.0] - 2026-09-26

### Añadido
- Mini-quiz por lección (45 preguntas), con explicación de cada respuesta y mejor nota guardada.
- Reto extra por lección (★ a ★★★), con plantilla, pista y tests automáticos.
- XP calculados a partir del progreso, 7 niveles, racha de días, 13 logros con vitrina y confeti (respeta la reducción de movimiento).
- API: las lecciones incluyen `quiz` y `challenge` (migración 3, probada en PostgreSQL con datos existentes).
- Tests: estructura de los quizzes y plantillas de reto que no pasan (backend); flujo completo del juego y accesibilidad (e2e).

### Corregido
- El atributo `hidden` no ocultaba los botones con clase `.btn`.

## [0.4.0] - 2026-09-26

### Añadido
- Versión de escritorio: `Iniciar-Dashboard.bat` (doble clic en Windows) y `scripts/run_local.py`. Un solo proceso sirve la web y la API en `127.0.0.1`, con puerto libre automático, base de datos y clave propias persistentes, y apertura del navegador.
- Modo `SERVE_FRONTEND` en el backend: sirve el frontend con `config.js` de mismo origen y tipos MIME fijados (evita el fallo del registro de Windows que marca `.js` como `text/plain`).
- Guía `docs/EJECUTAR-EN-WINDOWS.md` con solución de problemas (SmartScreen y Control de aplicaciones).

## [0.3.0] - 2026-09-26

### Añadido
- Consola interactiva con Python 3.14 (Pyodide) en un Web Worker de tipo módulo: `input()` desde «Entrada», errores con la línea del alumno y corte de bucles infinitos a los 10 s.
- Ejercicios corregibles en las 15 lecciones: plantilla, casos de test y resultado en español. Superarlos completa la lección.
- Asistente por lección: preguntas frecuentes, pista y «Siguiente tema».
- Cuenta en el frontend: registro, login, sesión persistente, sincronización del progreso, recuperación de contraseña, descarga de datos y borrado de cuenta.
- Backend: recuperación de contraseña (token de un solo uso, 30 min, email por SMTP en segundo plano), invalidación de sesiones al cambiar la contraseña, exportación y borrado de datos (RGPD), consentimiento de privacidad registrado.
- Política de privacidad (con campos pendientes de completar).
- Menú lateral deslizante en móvil y orden recomendado de lecciones.
- Tests end-to-end con Playwright contra el backend real, con auditoría WCAG 2.1 AA (axe-core).
- Cobertura del 100 % en el backend, obligatoria en CI. Migraciones probadas en PostgreSQL con datos existentes.
- Despliegue: `render.yaml` (Render Blueprint), `docker-compose.yml` y `docs/DEPLOY.md`.

### Cambiado
- Fuentes y highlight.js alojados en el propio sitio (sin Google Fonts ni CDN de terceros).
- Contrastes corregidos para cumplir WCAG AA (texto tenue, botones azules y comentarios de código).

### Corregido
- Anillo de progreso descolocado por un selector CSS roto.
- La migración 2 fallaba en PostgreSQL con datos existentes (valor por defecto booleano).

## [0.2.0] - 2026-09-25

### Añadido (backend)
- Usuarios: registro, login (OAuth2 + JWT) y `/api/users/me`. Contraseñas con Argon2 y límite de intentos por IP (ADR-0003).
- Progreso por usuario: `GET/PUT/DELETE /api/progress` e importación del progreso del navegador.
- Intentos de ejercicios: `POST/GET /api/lessons/{slug}/attempts`; un intento superado completa la lección.
- Migraciones con Alembic y comprobación en CI contra PostgreSQL 16.
- Dockerfile del backend (usuario sin privilegios, migración y carga de lecciones al arrancar).

### Añadido (contenido)
- Contenido de las 15 lecciones (teoría propia, ejemplo ejecutable, ejercicio y fuentes enlazadas) en `frontend/data/lessons.json`, fuente única compartida por frontend y backend (ADR-0002).
- Frontend: la barra lateral se genera a partir de los datos; navegación por URL (`#/leccion/<slug>`); pestañas accesibles; resaltado de sintaxis; botones "Copiar al portapapeles" y "Abrir en PyCharm" (copia + guía + descarga del `.py`); progreso guardado en el navegador.
- Backend: campo `sources` en las lecciones y test que exige contenido y fuentes en todas.

### Eliminado
- `backend/data/lessons.json` (sustituido por el archivo compartido).

## [0.1.0] - 2026-09-25

### Añadido
- Frontend: estructura HTML base y barra lateral "Ruta de Aprendizaje" con progreso circular y estados de lección.
- Backend: API FastAPI con `/api/health`, `/api/modules` y `/api/lessons/{slug}`; carga de lecciones idempotente.
- CI: lint, formato y tests del backend; despliegue del frontend en GitHub Pages.
