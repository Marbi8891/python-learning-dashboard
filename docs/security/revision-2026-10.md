# Revisión de seguridad: núcleo educativo (octubre de 2026, ADR-0031)

Esta revisión cubre los cambios del núcleo educativo y repasa las medidas que ya había. **No significa que el proyecto sea «seguro»**: las medidas reducen riesgos concretos y abajo se listan los que siguen abiertos.

## Qué se ha comprobado

| Área | Comprobación | Resultado |
|---|---|---|
| **Contenido nuevo** (`learning.json`) | Todo el texto se pinta con `escapeHtml`/`renderInline`, y el código con highlight.js, que escapa. El Markdown nuevo (bloques ``` y tablas) también escapa. | Test `markdown.test.mjs` con `<script>` e `<img>` |
| **Progreso por conceptos** (`pld:learn` y `/api/course-state/learn`) | `cleanLearning` (web) y `LearningState.fromJson` (app) solo aceptan ids con formato `[a-z0-9.-]`, fechas ISO y números. Los errores y ejercicios se buscan en el contenido antes de mostrarlos. | Tests `cleanLearning descarta datos manipulados` y `documentoCompatibleConLaWeb` |
| **API** | `learn` se añade a la lista cerrada `COURSES`. Mismo límite de tamaño (200 KB), misma autenticación y mismo export/borrado RGPD. El registro guarda como máximo 300 entradas para no acercarse al límite. | `test_learning_progress_is_saved_and_exported` y 100 % de cobertura |
| **Ejecución de código** | Los ejercicios de escribir código usan el mismo Worker de Pyodide y el mismo límite de tiempo que la consola. Se usa un solo Worker, no uno más. El resultado del Worker se trata como no fiable: se escapa y los números se convierten con `Number()`. | e2e de código con Pyodide local |
| **CSP** | Sin orígenes nuevos ni scripts en línea. | Sin cambios en `index.html` |
| **Dependencias** | Ninguna nueva. Los tests unitarios usan `node --test`. | `npm audit` y `pip-audit`: 0 vulnerabilidades conocidas |
| **Almacenamiento local** | `pld:learn` se borra al cerrar sesión con el resto de `pld:*` (`clearLocalData`). | e2e `security.spec.js` |
| **Android** | Sin permisos nuevos. El documento `learn` se valida al leerlo. Si el servidor no conoce `learn` (404), la sincronización no falla. | `LearningTest` en la JVM |
| **Accesibilidad** (requisito de diseño) | Auditoría WCAG 2.1 AA de las vistas nuevas en los dos temas. Se corrigen los contrastes que el rediseño anterior había roto en `main`. | e2e `learn.spec.js` y `a11y.spec.js` |

## Riesgos que siguen abiertos

| Riesgo | Por qué sigue | Mitigación actual | Qué haría falta |
|---|---|---|---|
| **Sesión en una cookie de terceros** (ADR-0033; antes, token en memoria y en `localStorage`) | Un XSS ya no puede llevarse el token, pero sí hacer peticiones mientras la página está abierta. En los navegadores que bloquean la cookie, el token vuelve a estar en memoria. | Cookie `HttpOnly; Secure; SameSite=None; Partitioned`, aceptada solo con la cabecera `X-PLD-Session` (CSRF), CORS con lista explícita, CSP estricta y token de 30 minutos | Web y API en el mismo dominio, con `SameSite=Strict`, y un token de refresco |
| **Rutas antiguas `/api/...` (sin versión)** | La app Android publicada todavía las usa. | Se sirven marcadas como *deprecated* y fuera de OpenAPI | Pasar la app a `/api/v1` y retirarlas |
| **`style-src 'unsafe-inline'`** | Las barras de progreso usan `style="--value: …"`. | Solo afecta a estilos. Los scripts no admiten código en línea | Pasar a clases o a `attr()` cuando los navegadores lo soporten |
| **CSP en `<meta>`** (GitHub Pages no permite cabeceras) | No se puede usar `frame-ancestors`. | Defensa contra marcos en JavaScript (`theme-init.js`) | Servir la web con cabeceras propias |
| **Pyodide desde jsDelivr sin SRI** | Se importa en el Worker con `import()` dinámico. | La CSP limita el origen a esa versión exacta | Alojar Pyodide en el propio sitio (unos 14 MB) |
| **El progreso lo declara el propio alumno** | La corrección se hace en el navegador. El alumno puede falsear su resultado desde la consola del navegador. | Solo afecta a su propio progreso. No hay rankings ni certificados oficiales | Corregir en el servidor con un sandbox (ADR-0001), si algún día hiciera falta |
| **Límites de intentos en memoria** | Pensados para una sola instancia. | Render ejecuta una instancia | Redis si se escala a varias instancias |
| **Token en el móvil** (`SharedPreferences`) | Sin cifrar, aunque excluido de las copias de seguridad. | El token caduca a la hora y la contraseña no se guarda | Android Keystore |
| **App Android de la fase 4 sin compilar en desarrollo** | El entorno no tenía SDK de Android. | Lógica probada en la JVM | Pasar la CI de Android y probar en el móvil (**VERIFY**) |
