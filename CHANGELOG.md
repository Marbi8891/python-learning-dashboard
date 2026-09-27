# Changelog

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/). Versionado [SemVer](https://semver.org/lang/es/).

## [Unreleased]

### Añadido
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
