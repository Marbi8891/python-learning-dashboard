# ADR-0035: Panel del alumno

- **Estado:** Propuesta (pendiente de que el autor la apruebe en el PR)
- **Fecha:** 2026-10-19
- **Relacionada:** ADR-0005 (gamificación), ADR-0018 (estado de cursos en la cuenta), ADR-0025
  («Mi cuenta» ampliada), ADR-0031 (núcleo por conceptos), ADR-0033 (sesión en cookie)

## Contexto

La información del alumno estaba repartida: «Aprender» y «Progreso» (conceptos), «Mi aprendizaje»
(XP y lecciones del curso PCAP, solo local) y «Mi cuenta» (plan, cursos, logros, perfil). Se pidió
un único panel con datos reales, accesible y adaptable, sin una segunda app ni datos inventados.

Hallazgos al inspeccionar el código:

- En el servidor: usuario, lecciones completadas (con fecha), intentos de ejercicios, documentos
  JSON de PCAP, cursos de DAW y conceptos (`/course-state`) y actividad de la cuenta.
- Solo en el navegador: XP, racha, logros, quizzes y retos (`pld:game`). Al cerrar sesión se
  borraban (ADR-0022), así que **se perdían**.
- No se registraba con qué método se inició sesión. No hay sistema de notificaciones ni se mide el
  tiempo de estudio.

## Decisión

1. **Una ruta, `#/panel/<sección>`**, en el mismo SPA y el mismo contenedor que «Mi cuenta», con
   siete secciones: Resumen, Mis cursos, Mi progreso, Actividad, Planificación, Logros y Mi
   perfil. Cada sección es un enlace (no pestañas ARIA): se puede compartir, volver atrás y se
   muestra una cada vez para no abrumar. `#/cuenta` redirige a `#/panel/perfil`; «Mi aprendizaje»
   (`#/perfil`) sigue para quien no tiene cuenta.
2. **Reutilizar, no duplicar.** El panel usa las piezas de `private.js` (plan, simulacros,
   certificados, seguridad), `profile.js` (días con actividad), `mastery.js` y `recommend.js`
   (dominio, plan de hoy) y los estilos existentes. Lo nuevo es `dashboard.js` (vista),
   `dashboard-data.js` (cálculos puros con tests) y `dashboard.css`.
3. **Un endpoint agregado** `GET /api/v1/dashboard` con lo que solo tiene el servidor (lecciones,
   intentos, actividad diaria en el día local del alumno, documentos sincronizados y método del
   último acceso) y `GET /api/v1/dashboard/activity` paginado. El resto ya llega por
   `/course-state` y `/pcap-state` y se calcula en el navegador con el contenido, como antes. Sin
   migraciones: los índices actuales (`user_id`) bastan.
4. **XP, racha y logros en la cuenta** con el mecanismo existente: `/course-state/game`, validado
   con `cleanGame` y fusionado sin perder nada (`mergeGame`). Se sube con retardo y antes de cerrar
   sesión, como los demás almacenes.
5. **El inicio de sesión con Google se registra como `login_google`.** El método de acceso es el
   del último inicio de sesión registrado; los anteriores a este cambio cuentan como «contraseña»
   hasta el siguiente acceso (la sesión dura 30 minutos).
6. **Sin datos inventados:** porcentajes solo con denominador conocido, estados vacíos con un
   paso útil, sin tiempo de estudio ni notificaciones (no existen).

## Seguridad

- El usuario sale siempre de la sesión validada (`CurrentUser`); ninguna ruta acepta un id.
  Tests: 401 sin sesión, un alumno no ve los datos de otro aunque mande `user_id`, parámetros
  fuera de rango → 422.
- La respuesta no incluye hash, `token_version`, tokens ni el código de los intentos.
- Todo lo que llega a HTML se escapa (`escapeHtml`, `renderInline`). Sin cambios en CORS, CSP,
  cookies ni límites de intentos.

## Consecuencias

- Una petición extra (dos en paralelo) al abrir el panel; el resto de vistas no cambia.
- La app Android muestra el tipo `login_google` con su nombre interno hasta que añada la
  etiqueta (no rompe nada).
- Pendiente: borrar la cuenta pide la contraseña; quien solo entra con Google debe crear una
  antes con «¿Has olvidado tu contraseña?». Notificaciones y tiempo de estudio quedan fuera.
