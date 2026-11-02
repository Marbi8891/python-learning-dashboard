# Auditoría legal integral · Python Learning Dashboard

| Campo | Valor |
|---|---|
| Fecha de la auditoría | 2 de noviembre de 2026 |
| Código revisado | `main` en el commit `23872f8` (después de los PR #72, #74, #75 y #76) |
| Producción consultada | `https://pld-api.onrender.com/api/health` y `https://marbi8891.github.io/python-learning-dashboard/privacidad.html` (2/11/2026) |
| Fase | 1, solo lectura. No se ha cambiado código ni ningún texto publicado |
| Documentos relacionados | [RIESGOS_LEGALES.md](RIESGOS_LEGALES.md) · [PLAN_ADECUACION_LEGAL.md](PLAN_ADECUACION_LEGAL.md) · [AUDITORIA_TECNICA.md](AUDITORIA_TECNICA.md) · [AUDITORIA-Y-LICENCIAS.md](AUDITORIA-Y-LICENCIAS.md) |
| Estado | **Borrador técnico.** Lo ha preparado una IA a partir del repositorio y de fuentes públicas. No lo ha revisado un abogado |

> **Esta auditoría no es un dictamen jurídico** y no certifica que el proyecto cumpla la ley. Describe
> lo que se ha podido comprobar en el código, en producción y en las fuentes oficiales el 2/11/2026, y
> deja marcado lo que no se ha podido comprobar.

## Índice

1. [Método y leyenda](#1-método-y-leyenda)
2. [Resumen del estado legal](#2-resumen-del-estado-legal)
3. [Qué hay realmente en el sistema](#3-qué-hay-realmente-en-el-sistema)
4. [Inventario de tratamientos de datos](#4-inventario-de-tratamientos-de-datos)
5. [Almacenamiento en el dispositivo](#5-almacenamiento-en-el-dispositivo)
6. [Terceros que intervienen](#6-terceros-que-intervienen)
7. [Análisis por norma](#7-análisis-por-norma)
8. [Matriz de cumplimiento](#8-matriz-de-cumplimiento)
9. [Pruebas técnicas ejecutadas](#9-pruebas-técnicas-ejecutadas)
10. [Datos que faltan y cómo afectan](#10-datos-que-faltan-y-cómo-afectan)
11. [Cuestiones para un abogado](#11-cuestiones-para-un-abogado)
12. [Fuentes](#12-fuentes)
13. [Relación con el trabajo legal anterior](#13-relación-con-el-trabajo-legal-anterior)

## 1. Método y leyenda

1. Se leyó el repositorio: README, `docs/`, `CLAUDE.md`, `SECURITY.md`, el frontend (`frontend/`), el
   backend (`backend/app/`), la configuración de despliegue (`render.yaml`, `backend/Dockerfile`,
   `.github/workflows/pages.yml`) y las auditorías anteriores.
2. Se buscó en el código todo lo que recoge, guarda o envía datos: formularios, `localStorage`,
   `sessionStorage`, cookies, Service Worker, Cache Storage, IndexedDB, scripts y dominios externos.
3. Se comparó cada afirmación de `privacidad.html` y `aviso-legal.html` con el código y con producción.
4. Se consultaron fuentes oficiales (BOE, EUR-Lex, Ministerio de Consumo) y la documentación de los
   proveedores. Cuando una página llegó truncada, se indica.
5. Se ejecutaron las pruebas técnicas que permite el entorno (apartado 9). No se hicieron pruebas
   intrusivas contra Render, Neon, Google ni GitHub, y no se accedió a datos de ningún usuario.

**Tipo de conclusión** (se usa en la matriz y en el análisis):

| Etiqueta | Significado |
|---|---|
| **Demostrado** | Hay evidencia directa en el código o en producción |
| **Sospecha** | Hay indicios razonables, pero falta una comprobación |
| **Pendiente de información** | No se puede decidir sin datos del titular o de un proveedor |

**Aplicabilidad:** Obligatoria · Condicionada (depende de un hecho futuro o desconocido) · No aplicable ·
Pendiente de determinar.

**Estado:** Cumple · Incumple · Parcial · No verificado. «Cumple» significa que **no se ha encontrado
incumplimiento en lo revisado**, nunca que el proyecto sea conforme en todo.

**Tres planos de cumplimiento** que este documento separa:

- **Técnico:** lo que hace el código (por ejemplo, que el borrado de la cuenta borre todas las tablas).
- **Documental:** lo que dicen los textos publicados y si coinciden con el código.
- **Jurídico:** si la interpretación de la norma es correcta para este caso. Solo puede confirmarlo un
  profesional.

No se da ningún porcentaje global de cumplimiento, porque no hay una metodología que lo justifique.

## 2. Resumen del estado legal

**Situación de partida.** Python Learning Dashboard es hoy una web educativa **gratuita**, sin
publicidad, sin pagos y sin inteligencia artificial en el producto. Se puede usar sin cuenta (todo queda
en el navegador) o con una cuenta opcional (email y contraseña, o Google) que guarda el progreso en una
base de datos de Neon a través de una API en Render. El titular declarado es una persona física.

**Lo que está bien hecho (técnico).** El diseño minimiza datos de forma notable: contraseñas con
Argon2id, cookie de sesión `HttpOnly` de 30 minutos, actividad de la cuenta sin IP, registro de
seguridad seudonimizado, Google cargado solo cuando el usuario lo pide, exportación en JSON y borrado
completo de la cuenta, también para cuentas de Google. El fallo P0 de sincronización de la auditoría
técnica (AUD-001) **está corregido en `main`** (`frontend/js/sync-gate.js`). No hay cookies de
análisis ni publicidad, y por eso **no hace falta un banner de cookies**.

**Lo que falla (documental), demostrado en producción el 2/11/2026:**

1. La política de privacidad **no menciona Google**, aunque producción tiene activado «Continuar con
   Google» (`/api/health` → `"google": true`). Falta informar de esa vía de registro, de los datos que
   llegan de Google y de la cookie que puede dejar Google (`g_state`).
2. La política dice que los emails de recuperación **«todavía no están activados»**, pero producción
   los tiene activados (`"email": true`). Hay un proveedor de envío (Brevo o un servidor SMTP) que no
   aparece como destinatario.
3. La política se contradice sobre la sesión: 30 minutos (§5) y «a la hora» (§7). El código usa 30
   minutos (`backend/app/config.py:28`).

**Lo que falta (documental y de procesos):** registro de actividades de tratamiento, procedimiento de
brechas de seguridad, procedimiento interno para atender derechos, plazos de conservación concretos
(cuentas inactivas, copias de Neon, logs de Render), condiciones de uso con edad mínima y la copia de los
contratos de encargo (DPA) de Render, Neon y el proveedor de email.

**Riesgo técnico abierto:** dos pestañas o dispositivos a la vez pueden pisarse el progreso (el último
que guarda gana). Lo corrige el PR #77, pendiente de merge en otro hilo.

**Comercialización.** Hoy no hay actividad comercial en `main`. Si se venden cursos, se activan de golpe
obligaciones que **hoy no se cumplen ni se necesitan**: datos completos del prestador (LSSI art. 10),
condiciones de contratación, información precontractual, desistimiento, conformidad de contenidos
digitales, facturación e IVA, y probablemente la función de desistimiento en línea. Están en el
apartado P1-C del plan.

**No hay ningún P0.** Ningún hallazgo obliga a parar una funcionalidad: no hay exposición de datos
demostrada ni un tratamiento sin base legal. Los fallos de la política son reales y deben corregirse
pronto (P1), pero no son una brecha.

## 3. Qué hay realmente en el sistema

Comprobado en el código de `main@23872f8`. «Producción» indica si se ha visto funcionando en la web
publicada.

| Componente | Estado en el código | Producción | Evidencia |
|---|---|---|---|
| Web estática (HTML, CSS, módulos ES) | Sí | Sí, GitHub Pages | `frontend/`, `.github/workflows/pages.yml` |
| Pyodide en un Web Worker | Sí, cargado de jsDelivr (v314.0.7) | No comprobado en esta sesión (jsDelivr bloqueado desde la nube) | `frontend/js/pyodide-worker.js`, CSP en `frontend/index.html:8` |
| API FastAPI | Sí | Sí, `pld-api.onrender.com` responde | `backend/app/main.py`, `/api/health` |
| Base de datos | PostgreSQL en Neon (prod), SQLite (local) | Neon según `render.yaml`; cadena real no vista | `render.yaml:17-18`, `backend/app/config.py` |
| Registro con email y contraseña | Sí | Sí (formulario visible) | `backend/app/routers/auth.py:121`, `frontend/index.html:308` |
| Inicio de sesión con Google | Sí, script bajo demanda | **Activado** (`"google": true`) | `frontend/js/google-identity.js`, `auth.py:58` |
| Recuperación de contraseña por email | Sí (Brevo o SMTP) | **Activada** (`"email": true`); proveedor real desconocido | `backend/app/mailer.py`, `auth.py:213` |
| Sincronización del progreso | Sí, con puerta de fusión (AUD-001 corregido) | No comprobado sin cuenta | `frontend/js/sync-gate.js`, `pcap-sync.js`, `course-store.js`, `learn/learn-store.js`, `game.js` |
| Control de versiones al sincronizar (dos pestañas) | **No** en `main` | No | PR #77 abierto |
| Exportación y borrado de cuenta | Sí | No probado (no se crean cuentas reales) | `backend/app/routers/account.py:87` y `:139` |
| Analítica GoatCounter | Código presente, **desactivado** | No se carga | `frontend/config.js` (`goatcounter: ""`), `frontend/js/analytics.js` |
| Service Worker y Cache Storage | Sí (sin conexión; nunca guarda la API) | Sí (solo fuera de localhost) | `frontend/sw.js` |
| «Asistente» de la lección | Respuestas fijas, **no es IA** | Sí | `frontend/js/assistant.js:1-2` |
| Tutor con IA, A2A, app Android | **Retirados** por el PR #62 | No | Historial de git; PR #65 (tutor con OpenAI) sigue abierto sin merge |
| Pagos, donaciones, publicidad | **No** | No | Búsqueda en `frontend/` sin resultados; PR #63 (Pack PCAP y donaciones) abierto sin merge |
| Funciones sociales (rankings, perfiles públicos) | No | No | Búsqueda en `frontend/js/` |
| Certificado de finalización | Sí, generado en el navegador, con aviso «no oficial» | Sí | `frontend/js/certificate.js:1`, `:78-79` |

## 4. Inventario de tratamientos de datos

Responsable declarado: Mrabeh Fathi Boussayff, persona física (`frontend/privacidad.html` §1). Que sea
el responsable real y su lugar de residencia son **pendiente de información** (DF-01).

| # | Datos | Dónde se guardan | Finalidad | Base jurídica propuesta | Conservación real | Evidencia |
|---|---|---|---|---|---|---|
| T1 | Email, nombre, hash Argon2id de la contraseña, fecha de alta | Neon, tabla `users` | Cuenta e inicio de sesión | Ejecución del servicio pedido (RGPD 6.1.b) | Mientras exista la cuenta. **Sin plazo para cuentas inactivas** | `backend/app/models.py:63-76` |
| T2 | Email verificado y nombre que envía Google | Neon, `users` (`email_verified_at`) | Registro o inicio con Google | 6.1.b | Igual que T1 | `auth.py:58-118` |
| T3 | Fecha de aceptación de la política | Neon, `users.privacy_accepted_at` | Demostrar que se informó | Responsabilidad proactiva (5.2). La política cita también el art. 7.1, que es de consentimiento: incoherente (LEG-004) | Igual que T1 | `models.py:71`, `privacidad.html` §2 |
| T4 | Lecciones completadas | Neon, `lesson_progress` | Guardar el progreso | 6.1.b | Igual que T1 | `models.py:79` |
| T5 | Código enviado en ejercicios y si pasó | Neon, `exercise_attempts` (50 por lección) | Historial del alumno | 6.1.b | 50 últimos por lección, mientras exista la cuenta | `models.py:93`, `config.py:39` |
| T6 | Documentos de progreso (PCAP, cursos DAW, núcleo, XP, racha, logros) | Neon, `pcap_states` y `course_states` (JSON) | Sincronizar entre dispositivos | 6.1.b | Igual que T1 | `models.py:120-153` |
| T7 | Actividad de la cuenta: tipo, fecha y dispositivo aproximado («Windows · Firefox»), sin IP | Neon, `account_events` (20 últimos) | Que el usuario vea accesos sospechosos | Interés legítimo en la seguridad (6.1.f) | 20 últimos eventos | `backend/app/activity.py:14`, `models.py:156` |
| T8 | Hash del enlace de recuperación | Neon, `password_reset_tokens` | Restablecer la contraseña | 6.1.b | Caduca a los 30 min; la fila se borra al pedir otro o al borrar la cuenta | `models.py:107`, `auth.py:218-241` |
| T9 | Email del destinatario y cuerpo del mensaje de recuperación | Proveedor de email (Brevo o SMTP) | Enviar el enlace | 6.1.b | **Desconocida** (depende del proveedor) | `backend/app/mailer.py:60-80` |
| T10 | IP en memoria | Memoria del proceso (no en disco) | Limitar intentos | 6.1.f | Ventana de 1 a 15 min; se pierde al reiniciar | `backend/app/rate_limit.py` |
| T11 | Registro de seguridad: evento, id interno, seudónimo HMAC de IP y email, ruta | Logs de Render | Detectar ataques | 6.1.f. Los seudónimos siguen siendo datos personales (RGPD cdo. 26) | **Desconocida** (la de Render) | `backend/app/security_events.py:80-85` |
| T12 | IP y datos técnicos de cada petición | Logs de Render y de GitHub Pages | Funcionamiento del servicio | 6.1.f | **Desconocida** | Proveedores |
| T13 | IP al descargar Pyodide | jsDelivr | Descargar Python | 6.1.f / servicio pedido | De jsDelivr | `pyodide-worker.js`, `privacidad.html` §4 |
| T14 | Progreso, borradores y nombre del certificado sin cuenta | Navegador del usuario (`localStorage`) | Funcionar sin cuenta | No hay tratamiento por el titular: los datos no salen del dispositivo | Hasta que el usuario los borre | Apartado 5 |

**Lo que no se trata (comprobado en el código):** no hay analítica activa, ni publicidad, ni perfiles,
ni datos de pago, ni categorías especiales (art. 9), ni decisiones automatizadas con efectos jurídicos
(art. 22). La puntuación, la XP y el «dominio» son cálculos para el propio alumno, sin consecuencias
fuera de la web.

**Copias de seguridad:** el plan gratuito de Neon conserva un historial de **6 horas** (fuente F-17).
Un dato borrado puede recuperarse técnicamente durante ese tiempo; la política dice que se borra «de
inmediato». No se sabe qué plan de Neon se usa (DF-05).

## 5. Almacenamiento en el dispositivo

Inventario completo de lo que la web escribe o lee en el navegador (búsqueda de `localStorage`,
`sessionStorage`, `document.cookie`, `indexedDB` y `caches` en `frontend/`).

| Elemento | Tipo | Quién lo pone | Finalidad | ¿Estrictamente necesario para un servicio pedido? | ¿Lo menciona la política? |
|---|---|---|---|---|---|
| `__Host-pld_session` | Cookie `HttpOnly`, `Secure`, `SameSite=None`, `Partitioned`, 30 min | API (Render) al iniciar sesión | Mantener la sesión | Sí: la sesión que el usuario abre | Sí (§5) |
| `g_state` | Cookie | Script de Google, **solo después de que el usuario abra el inicio de sesión o el borrado con Google** | Estado del botón de Google | Interpretación: sí, porque se carga a petición del usuario. **Sospecha** sobre su contenido exacto | **No** (la política dice «una sola cookie») |
| `pld:completed`, `pld:learn`, `pld:pcap`, `pld:game`, `pld:draft:<lección>`, `pld:daily-study-minutes`, `pld:cert-name` | `localStorage` | La web | Progreso, borradores, plan de estudio, nombre del certificado | Sí, son la función que el usuario usa | Sí, de forma general |
| `pld:prefs` | `localStorage` | La web | Tema y preferencias de aspecto | Sí (preferencia de interfaz pedida por el usuario) | De forma general |
| `pld:session`, `pld:session-expired` | `localStorage` | La web | Saber que hay sesión abierta (no guarda el token) | Sí | Sí |
| `pld:flash` | `sessionStorage` | La web | Mensaje tras borrar los datos | Sí | No (irrelevante, se borra al cerrar) |
| `pld-site-v8`, `pld-pyodide` | Cache Storage del Service Worker | La web | Funcionar sin conexión y no volver a descargar Python | Sí | **No** |
| IndexedDB | — | No se usa | — | — | — |

**Conclusión:** no hay ninguna tecnología de análisis, publicidad ni seguimiento activa. Todo lo que
se guarda sirve a una función que el usuario usa, y el script de Google ya no se descarga al entrar en
la web. **No es necesario un banner de cookies ni un panel de preferencias** con la configuración actual
(LSSI art. 22.2, excepción de lo estrictamente necesario). Sí hace falta **completar la información**:
la cookie de Google, la Cache Storage y una tabla de lo que se guarda. Si se activa GoatCounter, hay que
reevaluarlo (la política prevé interés legítimo; la AEPD admite exenciones para analítica muy limitada,
pero no se ha podido leer su guía en esta sesión, ver F-19).

Riesgo técnico menor: el origen `marbi8891.github.io` es común a **todos** los proyectos de GitHub Pages
del titular. Otro proyecto suyo publicado en ese origen podría leer este `localStorage` (LEG-047).

## 6. Terceros que intervienen

| Proveedor | Qué hace | Rol RGPD (interpretación) | Ubicación de los datos | Documentación contractual | Estado |
|---|---|---|---|---|---|
| **Render** (Render Services, Inc., EE. UU.) | Ejecuta la API, recibe todas las peticiones con cuenta y guarda logs | Encargado (art. 28) | Frankfurt según `render.yaml:10` | DPA publicado (19/12/2024) que **se incorpora a sus condiciones** e incluye cláusulas tipo (Decisión 2021/914) y el Marco UE-EE. UU. (F-16) | Contrato aparentemente automático; falta guardar copia y confirmar que la cuenta lo aceptó (DF-04) |
| **Neon** (ahora bajo Databricks) | Base de datos con todos los datos de cuenta | Encargado (art. 28) | UE según `docs/DEPLOY.md`; región real no vista | Página «DPA» actualizada el 14/10/2026 que remite al *Master Cloud Services Agreement* de Databricks. **No se ven las cláusulas tipo** en esa página (F-17) | **No verificado** (DF-04) |
| **Brevo o servidor SMTP** | Envía los emails de recuperación | Encargado (art. 28) | Desconocida | Desconocida | **No verificado; no aparece en la política** (DF-03) |
| **Google** (Google Identity Services) | Autentica al usuario que elige «Continuar con Google» y envía a la API un token con email y nombre | Responsable independiente respecto a su propio usuario; no es encargado del titular (interpretación, ver §7.A) | Global | Condiciones de Google Identity y de Google Cloud (proyecto OAuth) | No mencionado en la política |
| **GitHub Pages** (GitHub, Inc., EE. UU.) | Sirve la web; registra IP en sus logs | Lo razonable es tratarlo como encargado o proveedor de alojamiento según sus condiciones. **Pendiente de determinar** | Global | GitHub Privacy Statement / DPA de GitHub (no consultados) | Mencionado en la política |
| **jsDelivr** | Sirve Pyodide la primera vez | Proveedor de CDN que recibe la IP | Global | No hay relación contractual | Mencionado en la política |
| GitHub Actions, Dependabot | Integración continua | No trata datos de usuarios | — | — | No aplica |
| Claude Code (Anthropic) | Herramienta de desarrollo del titular | No trata datos de usuarios del producto | — | — | No aplica al producto (§7.H) |

**Transferencias internacionales.** Render, Neon y GitHub tienen matriz en EE. UU. Aunque los datos
estén en Frankfurt, el acceso desde EE. UU. es posible. El Marco de Privacidad UE-EE. UU. sigue vigente
tras la sentencia del Tribunal General del 3/9/2025, con recurso pendiente ante el TJUE (dato del
diagnóstico del 19/10/2026, de fuente secundaria, no reverificado hoy). La política afirma que Render y
Neon aplican cláusulas tipo: es cierto para Render según su DPA; **para Neon no se ha podido
comprobar**.

## 7. Análisis por norma

### A. Protección de datos: RGPD y LOPDGDD

**Por qué se aplica.** El RGPD se aplica al tratamiento automatizado de datos personales (art. 2.1). La
excepción doméstica (art. 2.2.c) no encaja: es una web pública que crea cuentas de terceros y guarda su
email, su código y su progreso. La LOPDGDD se aplica si el responsable está establecido en España
(DF-01), que es lo que declara el aviso legal.

**Obligaciones y conclusiones:**

- **Información (arts. 12-13).** La política existe y es clara, pero **no describe el sistema real** en
  tres puntos demostrados en producción: Google (LEG-001), el proveedor de email (LEG-002) y la duración
  de la sesión (LEG-003). Tampoco da plazos de conservación concretos (LEG-005). La casilla «He leído y
  acepto la política» mezcla información con consentimiento; la base real es el contrato (6.1.b), así
  que la casilla no es un consentimiento y no debe presentarse como tal (LEG-004).
- **Origen de los datos de Google (art. 13 o 14).** Cuando la persona elige Google, es ella quien pide
  que Google envíe su email y su nombre. Lo razonable es tratarlo como datos obtenidos del interesado
  (art. 13), pero hay que informar de esa vía y de qué datos llegan. Interpretación.
- **Rol de Google.** En «Sign in with Google» Google trata los datos de su propio usuario para
  autenticarlo. No actúa por cuenta del titular, así que **no es encargado** y no hace falta un DPA con
  Google para el inicio de sesión. Basta con identificarlo y enlazar su política. Interpretación, sin
  criterio de la AEPD consultado sobre este caso concreto.
- **Derechos (arts. 15-22).** Acceso y portabilidad: exportación JSON con todas las tablas del usuario
  (`account.py:87-115`). Supresión: borrado explícito de todas las tablas, con contraseña o con Google
  reciente (`account.py:139-172`). Rectificación: el nombre se cambia desde la web; **el email no**
  (solo por correo). Falta un **procedimiento interno** que garantice responder en un mes (art. 12.3) y
  registrar las solicitudes (LEG-008, LEG-009).
- **Conservación (art. 5.1.e).** Las cuentas inactivas se conservan sin límite, igual que los intentos
  de código. El historial de Neon (6 h en el plan gratuito) y los logs de Render tienen plazos que la
  política no explica (LEG-005).
- **Encargados (art. 28).** Render: DPA aparentemente incorporado a sus condiciones. Neon: no
  verificado. Proveedor de email: desconocido (LEG-010 a LEG-012).
- **Transferencias (cap. V).** Ver apartado 6 (LEG-013).
- **Registro de actividades (art. 30).** La exención del art. 30.5 para organizaciones de menos de 250
  personas **no se aplica** si el tratamiento no es ocasional, y aquí es continuo. Por tanto es
  **probablemente obligatorio**. No existe en el repositorio; hay un borrador en
  `/mnt/project-files/legal/borradores/registro-actividades.md` del 19/10, desfasado (LEG-014).
- **Privacidad desde el diseño (art. 25).** Buen nivel, con evidencias concretas (LEG-015).
- **Seguridad (art. 32).** Medidas técnicas sólidas para un proyecto de este tamaño. Faltan el control
  de versiones al sincronizar (PR #77), copias de seguridad útiles y medidas organizativas (LEG-016 a
  LEG-018, LEG-044 a LEG-047).
- **Brechas (arts. 33-34).** No hay procedimiento escrito: quién decide, cómo se valora el riesgo, cómo
  se notifica a la AEPD en 72 horas y cómo se registra (LEG-019).
- **Evaluación de impacto (art. 35). No obligatoria a fecha de hoy.** No hay tratamiento a gran escala,
  ni datos sensibles, ni perfiles con efectos jurídicos, ni seguimiento sistemático, ni decisiones
  automatizadas. Tampoco encaja en los criterios de la lista de la AEPD por lo revisado (lista no releída
  en esta sesión). Habría que reevaluarlo si se añade IA que analice el código del alumno, si se dirige
  a menores de forma específica o si se crece mucho (LEG-020).
- **Delegado de protección de datos (art. 37 y LOPDGDD art. 34).** No aplicable: no es autoridad
  pública, ni la actividad principal es observación sistemática a gran escala, ni está en la lista del
  art. 34 LOPDGDD para centros docentes (no es un centro reglado) (LEG-021).
- **Menores (RGPD art. 8 y LOPDGDD art. 7).** Esas normas regulan el **consentimiento** de menores (14
  años en España). Aquí la base es el contrato, así que no fijan por sí solas una edad mínima. El público
  objetivo declarado (DAW y PCAP) es mayoritariamente adulto, pero nada impide registrarse a un menor.
  Ver §7.I (LEG-022).

### B. Cookies y almacenamiento: LSSI art. 22.2

**Por qué se aplica.** El art. 22.2 de la LSSI regula cualquier dispositivo de almacenamiento y
recuperación de datos en el equipo del usuario, no solo las cookies, y exige consentimiento salvo para
lo estrictamente necesario para un servicio expresamente solicitado (F-03, art. 22.2 consultado el
2/11/2026).

**Conclusión.** Todo lo inventariado en el apartado 5 entra en la excepción técnica, **con la
interpretación** de que el progreso, los borradores, las preferencias de tema y la caché sin conexión
son funciones que el usuario usa a propósito. La cookie `g_state` solo aparece cuando el usuario ya ha
pedido iniciar sesión con Google. **No hace falta banner, panel de preferencias ni registro de
consentimientos.** Sí hace falta corregir la información (LEG-023, LEG-024). Este es un ejemplo claro
de que «usar localStorage» no exige por sí mismo un banner.

### C. LSSI-CE (Ley 34/2002): servicios de la sociedad de la información

**Por qué podría aplicarse.** La LSSI se aplica a los «servicios de la sociedad de la información», que
según su Anexo incluyen también servicios no remunerados por el destinatario **cuando constituyen una
actividad económica** para el prestador. El Anexo **no se ha podido releer** en esta sesión (el texto
del BOE llega truncado); la regla se cita del conocimiento general del texto y queda como
**[VERIFICAR]**.

| Escenario | ¿Actividad económica? | Consecuencia |
|---|---|---|
| 1. Web personal o demostración (hoy, proyecto de clase) | Probablemente no | La LSSI podría no aplicarse. El aviso legal actual (nombre y email) es una buena práctica |
| 2. Plataforma educativa gratuita sin ingresos | Dudoso: depende de si forma parte de una actividad profesional | Prudente: cumplir el art. 10 |
| 3. Con publicidad, patrocinio o donaciones | Sí | Art. 10 completo; art. 20 (identificar la publicidad); art. 22.2 para cookies publicitarias |
| 4. Cursos de pago | Sí | Arts. 10, 23-28 (contratación electrónica: información previa, confirmación) y normativa de consumo |
| 5. Suscripción | Sí | Lo del escenario 4 más renovación, cancelación y desistimiento continuo |

**Art. 10.1 (consultado):** nombre, residencia o domicilio y email; datos registrales si existen; NIF;
precios con impuestos si se mencionan precios; códigos de conducta. El aviso legal actual tiene nombre y
email, **no domicilio ni NIF**. Hoy es un hallazgo **condicionado** (LEG-025). No se inventa ningún dato:
la lista de lo que falta está en el plan (DF-02).

**Comunicaciones comerciales (arts. 19-21).** Hoy solo hay emails transaccionales (recuperación de
contraseña), que no son comunicaciones comerciales. No aplicable (LEG-026).

### D. Consumidores y contratación digital

**Hoy no aplicable**, porque no hay contratos onerosos con consumidores. Un matiz importante: la
Directiva (UE) 2019/770 también se aplica cuando el consumidor **facilita datos personales** en lugar de
pagar (art. 3.1, párrafo segundo), **salvo** que esos datos se traten solo para prestar el servicio o
cumplir obligaciones legales. Aquí los datos de la cuenta se usan solo para prestar el servicio (sin
publicidad ni perfiles, comprobado en el código), así que esa excepción encaja. Si algún día se usan
para otra cosa, la normativa de contenidos digitales se aplicaría aunque el curso sea gratis (LEG-027).
La transposición española está en el TRLCU (Real Decreto-ley 7/2021); el artículo concreto **no se ha
releído** [VERIFICAR].

**Si se venden cursos** (escenarios 4 y 5), hacen falta como mínimo (texto del TRLCU no consultado en
esta sesión salvo lo indicado):

- **Información precontractual** clara antes del pago: identidad, características del curso, precio
  total con impuestos, duración del acceso, requisitos técnicos y compatibilidad (Pyodide necesita un
  navegador moderno y unos 10 MB), funcionalidades, renovaciones, cancelación, garantías y reclamaciones
  (LEG-028).
- **Derecho de desistimiento de 14 días** en contratos a distancia (LEG-029). Excepción para
  **contenido digital sin soporte material** (por ejemplo, un curso que se desbloquea al pagar): el
  derecho se pierde solo si la ejecución empieza con el **consentimiento previo y expreso** del
  consumidor y su **reconocimiento** de que pierde el derecho, y el empresario lo **confirma**. La guía
  del Ministerio de Consumo de septiembre de 2026 lo resume así para cursos en línea (F-05). Para un
  **servicio digital continuado** (suscripción) la regla es otra: si el consumidor pide empezar durante
  el plazo y luego desiste, paga la parte proporcional. **No se debe redactar una renuncia general**: la
  excepción exige esos pasos concretos en el flujo de compra.
- **Función de desistimiento en línea** («botón de desistimiento»), Directiva (UE) 2023/2673, aplicable
  en la UE desde el 19/6/2026. Según la OCU, España no la había transpuesto en esa fecha (F-07, fuente
  secundaria). **Pendiente de verificar** la situación en el BOE antes de vender (LEG-030).
- **Conformidad** de contenidos y servicios digitales, actualizaciones y modificaciones del servicio
  (Directiva 2019/770 y su transposición) (LEG-031).
- **Condiciones generales de contratación** (Ley 7/1998) y confirmación del contrato en soporte
  duradero (LEG-032).
- **Atención al cliente y reclamaciones**: dirección de contacto y procedimiento (LEG-033).

### E. Accesibilidad

| Norma | ¿Se aplica? | Motivo |
|---|---|---|
| Directiva (UE) 2019/882 y Ley 11/2023 | **Hoy no. Si se vende: probablemente no mientras sea microempresa** | Se aplica a «servicios de comercio electrónico» (art. 2.2.f), definidos como servicios a distancia a petición del consumidor **para celebrar un contrato** (art. 3.30). Una web gratuita no encaja. Además, **las microempresas que prestan servicios están exentas** (art. 4.5; microempresa: menos de 10 personas y hasta 2 M€ de volumen de negocio o balance, art. 3.23). Aplicable desde el 28/6/2025. El precepto español equivalente **no se ha leído** en el BOE (fuente secundaria F-09) |
| Real Decreto 1112/2018 | **No** | Es para el sector público. Solo se aplicaría si el servicio lo prestara o encargara una administración o un centro público |
| WCAG 2.2 | Referencia técnica | No es una ley, pero es el estándar que usan las normas anteriores (a través de la EN 301 549) |

**Estado técnico (apartado 9):** axe-core no encuentra infracciones WCAG 2.0/2.1/2.2 A y AA en 10 rutas,
en tema claro y oscuro, en escritorio y móvil. El foco es visible en los 25 primeros elementos con
tabulador, hay enlace para saltar al contenido y el idioma está declarado. **Limitaciones:** las
herramientas automáticas detectan una parte de los problemas; no se ha probado con un lector de
pantalla, ni la consola con Python ejecutándose (jsDelivr bloqueado en la nube), ni el diálogo de cuenta
contra un backend real. El editor de código es un `<textarea>` con descripción asociada
(`frontend/index.html:235`), lo que es una buena base.

**Declaración de accesibilidad:** no es obligatoria hoy. El README afirma «accesibilidad WCAG 2.1 AA»
sin una auditoría manual que lo respalde: conviene decir «objetivo WCAG 2.1 AA, con pruebas automáticas»
(LEG-034, LEG-035).

### F. Propiedad intelectual y licencias

- **Código:** `LICENSE` MIT con «Copyright (c) 2026 Mrabeh Fathi». Que todo el código sea del titular
  es **declarado, no verificado**: hay contribuciones generadas con asistentes de IA y por Dependabot.
  Las de Dependabot son triviales. Sobre el código generado con IA, su protección por derechos de autor
  es una cuestión jurídica abierta (§11).
- **Contenido educativo:** el MIT del `LICENSE` no distingue entre código y contenido, así que hoy
  cualquiera puede copiar y vender el temario. **Decisión pendiente del titular** antes de comercializar
  (LEG-036, ya señalado como P1 en `docs/AUDITORIA-Y-LICENCIAS.md`).
- **Dependencias:** sus licencias están revisadas en `docs/AUDITORIA-Y-LICENCIAS.md` §5 (MIT, BSD,
  Apache-2.0, MPL-2.0, LGPL-3.0 para psycopg en servidor). highlight.js (BSD-3) y las fuentes (SIL OFL
  1.1) incluyen su licencia junto a los archivos. Pyodide (MPL-2.0) no se distribuye: se carga de
  jsDelivr. Compatible con uso comercial por lo revisado (LEG-037).
- **Iconos e imagen de redes** (`frontend/icons/*.png`, `favicon.svg`): **procedencia no
  documentada**. Pendiente de revisión (LEG-038).
- **Currículo oficial** (`frontend/data/curriculum/daw-cyl.json`): reproduce textos del Real Decreto
  405/2023 y de la Orden EDU/1311/2024. Las disposiciones legales y reglamentarias no son objeto de
  propiedad intelectual (art. 13 del TRLPI, no releído en esta sesión) (LEG-039).
- **Fuentes externas de ejercicios:** el informe de licencias del 26/10 declara que no se ha copiado
  nada de las seis fuentes revisadas. **No se ha comprobado** comparando textos (LEG-040).
- **Marcas:** «Python» (PSF) y «PCAP» (Python Institute). El aviso legal y el certificado aclaran que no
  hay afiliación y que el certificado no es oficial. La política de marcas de la PSF no se ha revisado
  (LEG-041).

### G. Seguridad de la aplicación (RGPD arts. 25 y 32)

| Control | Estado | Evidencia |
|---|---|---|
| Contraseñas | Argon2id, rehash automático, lista de contraseñas comunes | `backend/app/security.py`, `password_policy.py` |
| Sesión | Cookie `__Host-`, `HttpOnly`, `Secure`, 30 min; `token_version` revoca todas | `session_cookie.py`, `config.py:28` |
| CSRF | Cabecera `X-PLD-Session` obligatoria y CORS limitado a `marbi8891.github.io` | `main.py`, `render.yaml:21` |
| Límite de intentos | Por IP (con `TRUSTED_PROXY_HOPS=1`), por cuenta y por email; en memoria, una sola instancia | `rate_limit.py`, `backend/Dockerfile:29` |
| Cabeceras de la API | `nosniff`, `DENY`, HSTS, CSP `default-src 'none'`, `no-store` | `main.py` |
| CSP de la web | En `<meta>` (GitHub Pages no permite cabeceras); `style-src 'unsafe-inline'`; la publicada quita los orígenes de desarrollo | `index.html:8`, `scripts/security/production_csp.py` |
| Pyodide | Red cortada en el worker; corte a los 10 s; **sin SRI** | `pyodide-worker.js` |
| Tamaño de petición | 300 KB como máximo | `main.py` (`BodySizeLimit`) |
| Registro de eventos | Seudonimizado, con técnica ATT&CK | `security_events.py` |
| Secretos | Variables de entorno; la API no arranca sin `JWT_SECRET` | `main.py`, `render.yaml` |
| Dependencias | 0 vulnerabilidades conocidas (npm audit y pip-audit, 2/11/2026); `requirements.txt` sin versiones fijadas ni hashes | Apartado 9 |
| Integridad del progreso | AUD-001 corregido (no se sube nada antes de fusionar). **Dos pestañas: el último gana** hasta que se fusione el PR #77 | `sync-gate.js`, PR #77 |
| Copias de seguridad | Solo el historial de Neon (6 h en el plan gratuito) | F-17 |
| Gestión de vulnerabilidades | `SECURITY.md` con canal privado y respuesta en 7 días | `SECURITY.md` |
| Incidentes | Sin procedimiento escrito | — |

No se ha afirmado que el backend sea seguro por responder bien: la revisión es de código y
configuración, sin pruebas activas contra producción.

### H. Inteligencia artificial: Reglamento (UE) 2024/1689

- **El producto no usa IA hoy.** El «asistente» da respuestas fijas revisadas a mano
  (`assistant.js:1-2`). El tutor con IA se retiró en el PR #62. No hay generación automática de
  ejercicios en la web (los genera el titular con scripts deterministas) ni evaluación con IA: la
  corrección ejecuta el código y compara la salida (`frontend/py/runner.py`).
- **Uso de Claude Code por el desarrollador** y los agentes de `.claude/agents/`: son herramientas de
  desarrollo. No convierten el producto en un sistema de IA y **no se le atribuyen sus obligaciones**.
  La obligación de alfabetización en IA (art. 4, reformado por el Reglamento 2026/1744, que ahora pide
  «tomar medidas para apoyar» esa alfabetización y aclara que no exige garantizar un nivel) recae en
  proveedores y responsables del despliegue; el uso por una persona física en una actividad personal no
  profesional queda fuera de la definición de responsable del despliegue (art. 3.4, no releído hoy).
  **Condicionado** a si el proyecto pasa a ser una actividad profesional (LEG-042).
- **Si se recupera el tutor con OpenAI (PR #65 abierto):** el titular sería responsable del despliegue
  de un sistema que interactúa con personas. Habría que informar de que se habla con una IA (art. 50.1,
  aplicable desde el 2/8/2026 según la FAQ de la Comisión, F-13), revisar las transferencias a OpenAI,
  qué código del alumno se envía y con qué conservación, y actualizar la política. Es un cambio que
  exige revisar esta auditoría antes del merge (LEG-043).
- **Alto riesgo en educación (anexo III, punto 3):** no aplicable. No hay sistema de IA y, aunque lo
  hubiera, la web no decide el acceso ni evalúa resultados de enseñanza reglada. Además, el Reglamento
  2026/1744 retrasa esas obligaciones al 2/12/2027 (considerando 40, F-12).

### I. Menores de edad

- **Público:** la web se dirige a alumnado de DAW y a quien prepara el PCAP, que suele ser mayor de
  edad, pero cualquiera puede registrarse y no hay edad mínima (comprobado en `frontend/index.html` y
  `backend/app/schemas.py`).
- **Obligación legal:** ninguna norma revisada impone una edad mínima concreta a un servicio gratuito
  basado en el contrato. El art. 7 LOPDGDD (14 años) se refiere al consentimiento.
- **Medidas preventivas recomendables:** fijar en unas condiciones de uso **14 años** como edad mínima,
  coherente con la LOPDGDD, y pedir autorización de los padres o tutores por debajo. La política
  debería tener un apartado comprensible para menores. No hay rankings, perfiles públicos, publicidad ni
  funciones sociales, lo que reduce mucho el riesgo. Que un menor pueda aceptar unas condiciones es una
  cuestión de Derecho civil para un abogado (§11).

### J. Otras obligaciones

| Norma | ¿Aplicable? | Motivo |
|---|---|---|
| Reglamento de Servicios Digitales (UE) 2022/2065 | **Condicionada** | La web guarda el código de cada alumno a petición suya, lo que podría ser «alojamiento», pero no lo difunde al público (no es plataforma en línea). Solo se aplicaría si el servicio es una actividad económica. Si se aplica: punto de contacto (arts. 11-12), condiciones (art. 14) y mecanismo de notificación (art. 16). Texto no releído en esta sesión (LEG-048) |
| Fiscalidad y facturación (Ley 37/1992 del IVA, Reglamento de facturación RD 1619/2012) | **Condicionada** a vender | Alta censal, facturas, IVA de servicios electrónicos a consumidores de la UE (régimen OSS). No releído (LEG-049) |
| Servicios de pago (RDL 19/2018) | **No aplicable** si se usa una pasarela autorizada | El titular no prestaría servicios de pago (LEG-050) |
| Competencia desleal y publicidad (Ley 3/1991, Ley 34/1988) | **Condicionada** | Hoy no hay publicidad. El certificado podría inducir a error si se vendiera como acreditación; hoy lleva un aviso claro (LEG-051) |
| Títulos oficiales de FP | **No aplicable** | El certificado no es ni pretende ser un título oficial |
| Ley 10/2010 de blanqueo, normativa sectorial educativa | No aplicable | Sin indicios |

## 8. Matriz de cumplimiento

Fecha de comprobación de todas las filas: **02/11/2026**, salvo que se indique otra. Las fuentes F-xx
están en el apartado 12. Abreviaturas: Obl. = obligatoria; Cond. = condicionada; N/A = no aplicable;
PD = pendiente de determinar; Dem. = demostrado; Sosp. = sospecha; Info = pendiente de información.

| Id | Norma | Artículo | Aplicabilidad | Requisito | Evidencia | Estado | Riesgo | Corrección | Prioridad | Fuente | Fecha |
|---|---|---|---|---|---|---|---|---|---|---|---|
| LEG-001 | RGPD | 13.1.c, 13.1.e | Obl. | Informar de la vía de registro con Google, los datos que llegan y la cookie de Google | `privacidad.html` no menciona Google; producción `"google": true`; `auth.py:58-118` | **Incumple (Dem.)** | Alto | Añadir apartado de Google a la política | P1 | F-01 | 02/11/2026 |
| LEG-002 | RGPD | 13.1.e | Obl. | Identificar al proveedor de email como destinatario | Política: «todavía no están activados»; producción `"email": true`; `mailer.py` | **Incumple (Dem.)** | Alto | Nombrar al proveedor real y su ubicación | P1 | F-01 | 02/11/2026 |
| LEG-003 | RGPD | 5.1.a, 12.1 | Obl. | Información exacta y coherente | §5 dice 30 min; §7 «a la hora»; `config.py:28` = 30 | **Incumple (Dem.)** | Bajo | Corregir §7 | P1 | F-01 | 02/11/2026 |
| LEG-004 | RGPD | 6.1.b, 7.1 | Obl. | No presentar como consentimiento lo que es contrato | Casilla «acepto la política» (`index.html:292`, `:308`); política cita art. 7.1 | Parcial (Dem.) | Bajo | Texto «He leído la política» y quitar la cita al 7.1 | P2 | F-01 | 02/11/2026 |
| LEG-005 | RGPD | 5.1.e, 13.2.a | Obl. | Plazos de conservación concretos | Cuentas inactivas sin límite; Neon 6 h; logs de Render sin plazo; política: «se borran de inmediato» | Parcial (Dem.) | Medio | Fijar plazos, explicarlos y, si se decide, purgar cuentas inactivas | P2 | F-01, F-17 | 02/11/2026 |
| LEG-006 | RGPD | 15, 20 | Obl. | Acceso y portabilidad | `account.py:87-115` exporta todas las tablas del usuario | Cumple (técnico, código) | Bajo | Prueba e2e de exportación ya existe; mantener | P3 | F-01 | 02/11/2026 |
| LEG-007 | RGPD | 17 | Obl. | Supresión | `account.py:139-172` borra todas las tablas, también para cuentas Google | Cumple (técnico, código) | Bajo | Explicar el historial de 6 h de Neon | P2 | F-01 | 02/11/2026 |
| LEG-008 | RGPD | 16 | Obl. | Rectificación | Nombre editable (`account.py:46`); email no editable desde la web | Parcial (Dem.) | Bajo | Documentar la vía por email; valorar cambio de email | P3 | F-01 | 02/11/2026 |
| LEG-009 | RGPD | 12.3, 12.4 | Obl. | Responder en un mes y registrar solicitudes | Solo un email de contacto; sin procedimiento | Incumple (documental, Dem.) | Medio | Procedimiento de derechos | P2 | F-01 | 02/11/2026 |
| LEG-010 | RGPD | 28.3 | Obl. | Contrato de encargo con Render | DPA de Render incorporado a sus condiciones (F-16); aceptación de la cuenta no vista | No verificado (Info) | Medio | Guardar copia del DPA y fecha de aceptación | P2 | F-16 | 02/11/2026 |
| LEG-011 | RGPD | 28.3 | Obl. | Contrato de encargo con Neon | Página de Neon remite al MCSA de Databricks; sin cláusulas tipo visibles | No verificado (Info) | Medio | Descargar y guardar DPA y lista de subencargados | P2 | F-17 | 02/11/2026 |
| LEG-012 | RGPD | 28.3 | Obl. | Contrato con el proveedor de email | Proveedor real desconocido | No verificado (Info) | Medio | Identificar proveedor y su DPA | P1 | F-01 | 02/11/2026 |
| LEG-013 | RGPD | 44-46 | Obl. | Garantías para transferencias a EE. UU. | Render: DPF + cláusulas tipo; Neon: no visto; política afirma cláusulas para ambos | Parcial (Sosp.) | Medio | Verificar Neon y ajustar el texto | P2 | F-16, F-17 | 02/11/2026 |
| LEG-014 | RGPD | 30 | Obl. (interp.) | Registro de actividades | No existe en el repo; borrador desfasado del 19/10 | Incumple (documental, Sosp.) | Medio | Crear registro con T1-T13 | P2 | F-01 | 02/11/2026 |
| LEG-015 | RGPD | 25 | Obl. | Privacidad desde el diseño | Actividad sin IP, logs seudonimizados, GSI bajo demanda, borrado local al cerrar sesión (`store.js:115`) | Cumple (técnico) | Bajo | Mantener | P3 | F-01 | 02/11/2026 |
| LEG-016 | RGPD | 32.1.b | Obl. | Integridad del progreso | AUD-001 corregido (`sync-gate.js`); dos pestañas sin control (PR #77 abierto) | Parcial (Dem.) | Medio | Fusionar PR #77 tras revisión | P1 | F-01 | 02/11/2026 |
| LEG-017 | RGPD | 32.1.c | Obl. | Restaurar datos tras un incidente | Solo historial de Neon de 6 h (plan gratuito, plan real no visto) | Parcial (Info) | Medio | Copia periódica cifrada o plan con más historial | P2 | F-17 | 02/11/2026 |
| LEG-018 | RGPD | 32.1.d | Obl. | Verificar la eficacia de las medidas | CI con pytest, e2e, axe; auditorías AppSec y red team | Cumple (técnico) | Bajo | Mantener | P3 | F-01 | 02/11/2026 |
| LEG-019 | RGPD | 33, 34 | Obl. | Procedimiento de brechas (72 h a la AEPD) | No existe | Incumple (documental, Dem.) | Medio | Procedimiento y registro de incidentes | P2 | F-01 | 02/11/2026 |
| LEG-020 | RGPD | 35 | N/A hoy | Evaluación de impacto | Sin criterios de alto riesgo (ver §7.A) | No aplicable | Bajo | Reevaluar si hay IA, menores o gran escala | P3 | F-01 | 02/11/2026 |
| LEG-021 | RGPD / LOPDGDD | 37 / 34 | N/A | Delegado de protección de datos | No es autoridad pública ni centro docente reglado | No aplicable | Bajo | — | — | F-01, F-02 | 02/11/2026 |
| LEG-022 | RGPD / LOPDGDD | 8 / 7 | Cond. | Tratamiento de datos de menores | Sin edad mínima ni condiciones de uso | No verificado (Info) | Medio | Edad mínima en condiciones y apartado para menores | P2 | F-02 | 19/10/2026 |
| LEG-023 | LSSI | 22.2 | Obl. | Consentimiento salvo almacenamiento estrictamente necesario | Inventario §5: todo técnico; GSI bajo demanda (`google-identity.js`) | Cumple (interp.) | Bajo | Reevaluar si se activa analítica | P3 | F-03 | 02/11/2026 |
| LEG-024 | LSSI / RGPD | 22.2 / 13 | Obl. | Información clara del almacenamiento | Política: «una sola cookie»; falta `g_state` y Cache Storage | Incumple (documental, Dem.) | Bajo | Tabla de almacenamiento en la política | P1 | F-03 | 02/11/2026 |
| LEG-025 | LSSI | 10.1 | Cond. | Datos del prestador (domicilio, NIF…) | Aviso legal: nombre y email, sin domicilio ni NIF | Parcial (Info) | Medio | Completar si hay actividad económica | P1 antes de comercializar | F-03 | 02/11/2026 |
| LEG-026 | LSSI | 19-21 | N/A hoy | Comunicaciones comerciales | Solo emails transaccionales | No aplicable | Bajo | Consentimiento si hay boletín | P3 | F-03 | 02/11/2026 |
| LEG-027 | Directiva 2019/770 | 3.1 párr. 2 | N/A hoy (excepción) | Contenidos digitales a cambio de datos | Datos usados solo para prestar el servicio | No aplicable | Bajo | Reevaluar si los datos se usan para otros fines | P3 | F-06 | 02/11/2026 |
| LEG-028 | TRLCU | Información precontractual (arts. 60 y 97, no releídos) | Cond. | Información antes del pago | No hay pagos | No aplicable hoy | Alto si se vende | Diseñar la información previa | P1 antes de comercializar | F-04 | 02/11/2026 |
| LEG-029 | TRLCU | 102-103 (no releídos) | Cond. | Desistimiento y su excepción para contenido digital | No hay pagos | No aplicable hoy | Alto si se vende | Flujo con consentimiento expreso, reconocimiento y confirmación | P1 antes de comercializar | F-04, F-05 | 02/11/2026 |
| LEG-030 | Directiva 2023/2673 | Art. 11 bis Directiva 2011/83 (no releído) | Cond. | Función de desistimiento en línea | No hay pagos; transposición española no confirmada | Pendiente (Info) | Medio si se vende | Verificar BOE antes de vender | P1 antes de comercializar | F-07 | 02/11/2026 |
| LEG-031 | Directiva 2019/770 / TRLCU | Conformidad (no releído) | Cond. | Garantía de conformidad y actualizaciones | No hay pagos | No aplicable hoy | Medio si se vende | Condiciones de conformidad | P1 antes de comercializar | F-06 | 02/11/2026 |
| LEG-032 | Ley 7/1998 · LSSI | CGC · 27-28 | Cond. | Condiciones generales y confirmación del contrato | No existen condiciones | No aplicable hoy | Alto si se vende | Condiciones de contratación | P1 antes de comercializar | F-03 | 02/11/2026 |
| LEG-033 | TRLCU | Atención al cliente (no releído) | Cond. | Canal de reclamaciones | Email de contacto | Parcial | Bajo | Procedimiento al vender | P2 | F-04 | 02/11/2026 |
| LEG-034 | Directiva 2019/882 / Ley 11/2023 | 2.2.f, 3.30, 4.5 | Cond. (exención microempresa) | Accesibilidad del comercio electrónico | axe sin infracciones (§9); hoy no hay comercio | No aplicable hoy | Bajo | Reevaluar al crecer por encima de microempresa | P3 | F-08, F-09 | 02/11/2026 |
| LEG-035 | Buenas prácticas / veracidad | — | Recom. | Afirmaciones públicas verificables | README: «accesibilidad WCAG 2.1 AA» sin auditoría manual | Parcial (Dem.) | Bajo | Reformular como objetivo con pruebas automáticas | P3 | — | 02/11/2026 |
| LEG-036 | TRLPI | Titularidad y licencia | Obl. | Licencia del contenido acorde al uso comercial | `LICENSE` MIT sin distinguir contenido | Parcial (Dem.) | Medio | Decidir licencia del contenido | P1 antes de comercializar | F-14 | 02/11/2026 |
| LEG-037 | Licencias de terceros | MIT, BSD-3, OFL, MPL | Obl. | Avisos de licencia de lo distribuido | `frontend/vendor/highlight/LICENSE`, `frontend/fonts/LICENSE-*` | Cumple | Bajo | Mantener | P3 | `AUDITORIA-Y-LICENCIAS.md` | 02/11/2026 |
| LEG-038 | TRLPI | — | Obl. | Procedencia de iconos e imágenes | `frontend/icons/*`, `favicon.svg` sin origen documentado | No verificado (Info) | Bajo | Documentar autoría o licencia | P3 | F-14 | 02/11/2026 |
| LEG-039 | TRLPI | 13 | Obl. | Uso de textos oficiales del currículo | `data/curriculum/daw-cyl.json` reproduce RD 405/2023 | Cumple (interp.) | Bajo | Citar la fuente oficial (ya se hace) | P3 | F-14 | 02/11/2026 |
| LEG-040 | TRLPI | — | Obl. | Originalidad del temario | Declarada en el aviso legal; no comparada con fuentes | No verificado | Bajo | Muestreo de originalidad antes de vender | P3 | F-14 | 02/11/2026 |
| LEG-041 | Marcas (Ley 17/2001) | — | Obl. | Uso descriptivo de «Python» y «PCAP» | Aviso legal y certificado con descargo | Parcial | Bajo | Revisar política de marcas de la PSF | P3 | — | 02/11/2026 |
| LEG-042 | RIA | 4 (mod. por Rgto. 2026/1744) | Cond. | Alfabetización en IA del personal | Uso de Claude Code como herramienta de desarrollo | Pendiente (Info) | Bajo | Reevaluar si es actividad profesional | P3 | F-11, F-12 | 02/11/2026 |
| LEG-043 | RIA | 50.1 | N/A hoy | Informar de que se interactúa con una IA | Sin IA en el producto (`assistant.js:1-2`); PR #65 la reintroduciría | No aplicable hoy | Medio si se fusiona #65 | Revisar antes del merge de #65 | P2 | F-11, F-13 | 02/11/2026 |
| LEG-044 | RGPD | 32 | Obl. | Dependencias sin vulnerabilidades conocidas | npm audit y pip-audit: 0 (§9); requisitos sin fijar ni hashes | Parcial (Dem.) | Bajo | Fijar versiones con hashes (PLD-SEC-005) | P3 | F-01 | 02/11/2026 |
| LEG-045 | RGPD | 32 | Obl. | Integridad de código de terceros | Pyodide de jsDelivr sin SRI | Parcial (Dem.) | Bajo | SRI o alojar Pyodide | P3 | F-01 | 02/11/2026 |
| LEG-046 | RGPD | 32 | Obl. | Límite de intentos robusto | En memoria, una instancia; se pierde al reiniciar | Parcial (Dem.) | Bajo | Aceptable hoy; revisar si hay varias instancias | P3 | F-01 | 02/11/2026 |
| LEG-047 | RGPD | 32 | Obl. | Aislamiento del almacenamiento local | Origen `marbi8891.github.io` compartido con otros proyectos del titular | Parcial (Sosp.) | Bajo | Dominio propio o no publicar código ajeno en ese origen | P3 | F-01 | 02/11/2026 |
| LEG-048 | Rgto. 2022/2065 (DSA) | 11, 12, 14, 16 | Cond. | Obligaciones de alojamiento | Código del alumno guardado en privado; sin difusión pública | PD | Bajo | Reevaluar si hay actividad económica | P3 | F-15 | 02/11/2026 |
| LEG-049 | Ley 37/1992 · RD 1619/2012 | IVA · facturación | Cond. | Facturas e IVA de servicios electrónicos | No hay ventas | No aplicable hoy | Alto si se vende | Asesoría fiscal antes de vender | P1 antes de comercializar | — | 02/11/2026 |
| LEG-050 | RDL 19/2018 | — | N/A | Servicios de pago | No hay pagos; se usaría pasarela autorizada | No aplicable | Bajo | — | — | — | 02/11/2026 |
| LEG-051 | Ley 3/1991 | 5 (actos de engaño) | Cond. | No inducir a error con el certificado | `certificate.js:78-79`: «No es una certificación oficial» | Cumple (hoy) | Bajo | Mantener el aviso si se vende | P3 | — | 02/11/2026 |
| LEG-052 | LSSI / RGPD | 10 / 13 | Obl. (prudente) | Documentos legales coherentes entre sí | Aviso legal: «Solo se usa una cookie técnica»; fecha 29/09/2026 | Parcial (Dem.) | Bajo | Actualizar con la política | P2 | F-03 | 02/11/2026 |

## 9. Pruebas técnicas ejecutadas

Todas el 2/11/2026 sobre `main@23872f8`, desde el entorno en la nube, sin tocar el repositorio.

| Prueba | Herramienta | Resultado | Limitaciones |
|---|---|---|---|
| Estado de producción | `GET https://pld-api.onrender.com/api/health` | `{"status":"ok","email":true,"google":true}`: Google y el envío de emails **están activados** | No revela el proveedor de email |
| Política publicada | Lectura de `privacidad.html` en GitHub Pages | Coincide con el repo: actualizada el 26/10/2026, sin Google, sesión «a la hora» en §7, emails «no activados» | — |
| Vulnerabilidades del frontend | `npm audit` (con y sin dependencias de desarrollo) | 0 vulnerabilidades | Solo dependencias de pruebas; el frontend no tiene dependencias de ejecución salvo Pyodide y highlight.js |
| Vulnerabilidades del backend | `pip-audit -r backend/requirements.txt` | 0 vulnerabilidades conocidas | Resuelve las versiones del día, no las desplegadas |
| Accesibilidad automática | axe-core 4.10 con Playwright, etiquetas `wcag2a`, `wcag2aa`, `wcag21a`, `wcag21aa`, `wcag22aa` | **0 infracciones** en 10 rutas (`#/portada`, `#/aprender`, `#/practicar`, `#/progreso`, `#/pcap`, `#/daw/curriculo`, `#/leccion/variables`, `privacidad.html`, `aviso-legal.html`, `404.html`) × tema claro y oscuro × 1280 px y 360 px. 2 comprobaciones «incompletas» (revisión manual) en la portada y en la lección | Sin lector de pantalla; sin Pyodide (jsDelivr bloqueado); sin backend para el diálogo de cuenta |
| Teclado | 25 pulsaciones de Tab en la portada | Los 25 elementos muestran foco visible; existe enlace para saltar al contenido; `lang="es"` | Solo la portada |
| Inventario de almacenamiento | Búsqueda en `frontend/` | Apartado 5 | No se ha medido en un navegador con sesión real |
| Dominios externos | Búsqueda de URLs en `frontend/` | Solo `accounts.google.com`, `cdn.jsdelivr.net`, `pld-api.onrender.com`, `gc.zgo.at` (desactivado), enlaces a la AEPD y GitHub | — |
| Seguridad de la API | Revisión de código | Apartado 7.G | Sin pruebas activas contra producción |

**No ejecutado:** pruebas de los flujos de cuenta contra producción (crearían datos reales), pytest del
backend (no forma parte de una auditoría documental; lo ejecuta la CI), lectores de pantalla y pruebas
de usuario.

## 10. Datos que faltan y cómo afectan

| Id | Dato que debe aportar el titular | Afecta a |
|---|---|---|
| DF-01 | Identidad confirmada del responsable, país de residencia y si actúa como particular o como profesional (autónomo, empresa) | Aplicación de LOPDGDD y LSSI (LEG-021, LEG-025); quién firma los contratos |
| DF-02 | Domicilio o dirección de contacto postal y NIF, **solo si** hay actividad económica | LSSI art. 10 (LEG-025). No se publicará nada sin su decisión |
| DF-03 | Proveedor real de email en Render (Brevo o SMTP, y cuál) | LEG-002, LEG-012 |
| DF-04 | Confirmación de que las cuentas de Render, Neon y el proveedor de email aceptaron sus DPA, con copia y fecha | LEG-010, LEG-011, LEG-012, LEG-013 |
| DF-05 | Plan de Neon y región real; retención de logs de Render | LEG-005, LEG-017 |
| DF-06 | Público objetivo y edad mínima que quiere fijar | LEG-022 |
| DF-07 | Modelo de negocio y calendario (donaciones, Pack PCAP, cursos, suscripción) | Todo el bloque P1-C del plan |
| DF-08 | Países a los que se dirige el servicio | Consumo, IVA, idioma de los textos |
| DF-09 | Licencia deseada para el contenido educativo | LEG-036 |
| DF-10 | Autoría o licencia de iconos e imagen de redes | LEG-038 |
| DF-11 | Si hay otros proyectos publicados en `marbi8891.github.io` | LEG-047 |
| DF-12 | Intención con los PR #65 (tutor con OpenAI) y #63 (Pack PCAP y donaciones) | LEG-043 y escenarios de comercialización |

## 11. Cuestiones para un abogado

1. Si un proyecto educativo gratuito de un estudiante es «actividad económica» a efectos de la LSSI, y
   desde cuándo lo sería (donaciones, portfolio, venta de un PDF).
2. Rol de Google en el inicio de sesión federado (responsable independiente frente a corresponsable) y
   si basta con informar.
3. Capacidad de un menor de 14 a 17 años para aceptar unas condiciones de uso gratuitas (Código Civil).
4. Flujo exacto de desistimiento para cursos de acceso inmediato y para suscripciones, y estado de la
   transposición de la Directiva 2023/2673.
5. Titularidad y protección del código y del contenido generados con asistentes de IA, y licencia
   adecuada para el temario si se comercializa.
6. Uso de las marcas «Python» y «PCAP» en el nombre comercial y en los materiales de pago.
7. Fiscalidad de las primeras ventas (alta, IVA OSS, facturación) con una asesoría.

## 12. Fuentes

«Consultada» significa leída en esta sesión; «no releída» significa que se cita por conocimiento del
texto y debe comprobarse antes de usarla en un documento definitivo.

| Id | Fuente | Tipo | URL | Estado de la consulta |
|---|---|---|---|---|
| F-01 | Reglamento (UE) 2016/679 (RGPD) | Norma UE | https://eur-lex.europa.eu/eli/reg/2016/679/oj | **No releída** hoy (EUR-Lex llegó truncado el 19/10). Artículos citados por su numeración conocida [VERIFICAR] |
| F-02 | Ley Orgánica 3/2018 (LOPDGDD) | Ley | https://www.boe.es/buscar/act.php?id=BOE-A-2018-16673 | Arts. 7 y 11 consultados el 19/10/2026 (diagnóstico previo); art. 34 no releído |
| F-03 | Ley 34/2002 (LSSI-CE), texto consolidado de 23/01/2025 | Ley | https://www.boe.es/buscar/act.php?id=BOE-A-2002-13758 | Consultada el 2/11/2026: art. 10.1 a-g y art. 22.2. **Anexo no leído** (truncado) |
| F-04 | Real Decreto Legislativo 1/2007 (TRLCU) | Ley | https://www.boe.es/buscar/act.php?id=BOE-A-2007-20555 | **No consultada** en esta sesión |
| F-05 | Ministerio de Derechos Sociales, Consumo y Agenda 2030: guía sobre desistimiento en productos digitales (sept. 2026, NIPO 233-26-013-0) | Guía oficial | https://www.dsca.gob.es/sites/default/files/DGC_desistimiento_productos_digitales.rev_.pdf | Consultada el 2/11/2026 |
| F-06 | Directiva (UE) 2019/770 | Norma UE | https://eur-lex.europa.eu/eli/dir/2019/770/oj | **No releída** |
| F-07 | Directiva (UE) 2023/2673 y nota de prensa de la OCU del 19/6/2026 | Norma UE + fuente secundaria | https://www.ocu.org/organizacion/prensa/notas-de-prensa/2026/normabotondesistimiento190626 | Nota consultada; texto de la Directiva no leído |
| F-08 | Directiva (UE) 2019/882 | Norma UE | https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32019L0882 | Consultada: arts. 2.2.f, 3.23, 3.30 y 4.5 |
| F-09 | Ley 11/2023 (accesibilidad de productos y servicios) | Ley | Comentario de Cuatrecasas: https://www.cuatrecasas.com/es/global/propiedad-intelectual/art/claves-proxima-entrada-vigor-ley-accesibilidad-espana | **Solo fuente secundaria** (art. 2.2, disposición final 18ª: 28/6/2025). Texto del BOE no leído |
| F-10 | Real Decreto 1112/2018 | Norma | BOE | No releído; su ámbito (sector público) es conocido |
| F-11 | Reglamento (UE) 2024/1689 (RIA) | Norma UE | https://eur-lex.europa.eu/eli/reg/2024/1689/oj | Arts. 3.4, 4 y 50 **no releídos** en el texto consolidado |
| F-12 | Reglamento (UE) 2026/1744 «Ómnibus digital sobre IA», de 8/7/2026 | Norma UE | https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32026R1744 | Consultado el 2/11/2026 (parcial): título, fecha, nuevo art. 4, considerando 40 (anexo III al 2/12/2027) |
| F-13 | Comisión Europea, FAQ sobre el art. 50 del RIA | Guía | https://digital-strategy.ec.europa.eu/en/faqs/transparency-obligations-under-article-50-ai-act | Consultada el 19/10/2026 |
| F-14 | Real Decreto Legislativo 1/1996 (TRLPI) | Ley | https://www.boe.es/buscar/act.php?id=BOE-A-1996-8930 | **No releída** (art. 13 citado por conocimiento) |
| F-15 | Reglamento (UE) 2022/2065 (DSA) | Norma UE | https://eur-lex.europa.eu/eli/reg/2022/2065/oj | **No releído** |
| F-16 | Render, Data Processing Addendum (19/12/2024) | Contrato del proveedor | https://render.com/dpa | Consultado el 2/11/2026 |
| F-17 | Neon, página «DPA» (14/10/2026) e historial de restauración | Proveedor | https://neon.com/dpa · https://neon.com/docs/postgres/backup-restore/history-window | Consultadas el 2/11/2026 |
| F-18 | Google Identity Services | Proveedor | https://developers.google.com/identity/gsi | Consultada el 19/10/2026 |
| F-19 | AEPD, Guía sobre el uso de las cookies (actualizada en 2023) | Guía de autoridad | https://www.aepd.es/es/prensa-y-comunicacion/notas-de-prensa/aepd-actualiza-guia-cookies-para-adaptarla-a-nuevas-directrices-cepd | **No se pudo leer** (la web de la AEPD devolvió un script en lugar del contenido) |

Ningún artículo se ha inventado. Donde la fuente no se ha leído, se dice.

## 13. Relación con el trabajo legal anterior

El hilo «LegalDocs AI» dejó un diagnóstico del 19/10/2026 (copia en `/mnt/project-files/legal/`). El PR
#62 retiró `docs/legal/` del repositorio. Estado de sus hallazgos a 2/11/2026:

| Hallazgo del 19/10 | Estado hoy | Evidencia |
|---|---|---|
| H5: script de Google en cada visita | **Resuelto**: se carga bajo demanda | `frontend/js/google-identity.js:1-3` |
| H6: cuentas de Google sin borrado | **Resuelto**: borrado con confirmación de Google | `account.py:118-172` |
| H8: sesión 30 min frente a «una hora» | **Sigue** (LEG-003) | `privacidad.html` §7 |
| H9: GoatCounter descrito como activo | **Resuelto**: el apartado se oculta si está desactivado | `privacy-note.js`, `privacidad.html:73` |
| H10-H11: tutor con IA | **Ya no existe** en `main` | PR #62 |
| H18: cookie `g_state` no mencionada | **Sigue** (LEG-024) | `e2e/account.spec.js:110` |
| Política sin Google | **Sigue** y ahora está activo en producción (LEG-001) | `/api/health` |
| Preguntas P1-P7 | **Sin respuesta**. P4 y P6 ya no aplican (sin tutor ni Android). P3 se responde en parte: hay email activo, falta saber el proveedor | DF-01 a DF-07 |

Los borradores de `/mnt/project-files/legal/borradores/` (privacidad, condiciones, registro) se pueden
reutilizar en la fase 2, quitando las partes del tutor y de Android.
