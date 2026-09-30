# ADR-0025: «Mi cuenta» ampliada: plan, progreso, logros y seguridad

- **Estado:** Aceptada e implementada
- **Fecha:** 2026-09-30

## Contexto

El autor encontró «Mi cuenta» muy pobre: un resumen y poder descargar los datos o borrar la cuenta. Pidió que cada usuario tuviera más posibilidades en su zona, y eligió las cuatro áreas propuestas:

1. Editar el perfil y la seguridad.
2. Ver el progreso en todos los cursos.
3. Objetivos y plan de estudio.
4. Logros y certificados.

## Decisión

Una sola página (`#/cuenta`, `frontend/js/private.js`) con cuatro secciones. Reutiliza lo que ya existe y solo añade backend donde hace falta un servidor.

### 1. Plan de estudio (sin backend nuevo)

- **Fecha de examen de cada curso:** el PCAP y los cinco de DAW. Se guarda en `plan.examDate` del estado de cada curso, el mismo campo que ya usan la web y la app, así que se sincroniza con la cuenta. Muestra los días que faltan.
- **Repaso de hoy por curso:** las preguntas del repaso espaciado que vencen hoy, con un enlace a la tanda de repaso.
- **Meta diaria:** 10, 20, 30 o 50 preguntas. Cuenta las preguntas distintas practicadas hoy en todos los cursos, según la fecha del último intento en `srs`. Se guarda en `plan.dailyGoal` del PCAP, que sincroniza con la cuenta. `progress-guard.js` la valida entre 1 y 200.

### 2. Progreso en todos los cursos (sin backend nuevo)

- **Una tarjeta por curso** con las preguntas respondidas, los simulacros y la mejor nota. Al llegar el banco de preguntas (`loadCourseBank`, cacheado) se añaden:
  - el dominio, que es el acierto ponderado por el peso de cada bloque (la misma regla que la web y la app);
  - el tema más flojo, con un enlace para practicarlo, o el siguiente tema sin empezar.
- **Historial de los 10 últimos simulacros de todos los cursos.** Incluye los de la app Android, que se guardan en `exams` con el mismo formato (ADR-0024).

### 3. Logros y certificados

- Los logros de siempre (`badgesHtml`), además del nivel y la XP.
- **Certificado de cada curso de DAW** (`#/certificado/<curso>`), no oficial, como el del PCAP.
  - **Requisitos:** un dominio del 70 % y al menos 5 preguntas respondidas en cada bloque (`courseCertificateStatus`).
  - Si faltan, la página dice exactamente qué.
  - Se imprime o se guarda en PDF desde el navegador.

### 4. Perfil y seguridad (backend nuevo)

| Endpoint | Qué hace |
| --- | --- |
| `PATCH /api/users/me` | Cambiar el nombre visible |
| `POST /api/users/me/password` | Cambiar la contraseña con la actual. Aplica la política de contraseñas (ADR-0023), sube `token_version` (cierra las demás sesiones) y **devuelve un token nuevo** para seguir en esta. Tiene límite de intentos por IP. |
| `GET /api/users/me/activity` | Actividad reciente de la cuenta |

- **Tabla nueva `account_events`** (migración `7c3e9a1d4b20`): el tipo (inicio de sesión, intento fallido, contraseña cambiada o restablecida, cierre de sesiones, nombre cambiado), la fecha y un **dispositivo aproximado** («Android · Chrome») sacado del User-Agent.
  - **Sin IP y sin el User-Agent completo** (minimización, RGPD art. 5.1.c).
  - Se conservan los **últimos 20 eventos** por usuario.
  - Se borran con la cuenta y se incluyen en la exportación.
- **Diferencia con el registro de seguridad (ADR-0023):** aquel es para el servidor y va seudonimizado. Este es para que **el titular** detecte un acceso que no reconoce (T1078 Valid Accounts, desde el lado del usuario).
- CORS admite `PATCH`.

## Alternativas descartadas

| Opción | Por qué no |
| --- | --- |
| Varias páginas o pestañas dentro de «Mi cuenta» | Más rutas y navegación para cuatro secciones cortas. Una página con encabezados es más simple y accesible. |
| Cambiar el email desde la cuenta | Exige verificar el email nuevo (SMTP, que aún no está configurado). Queda para cuando haya email. |
| Guardar la IP en la actividad | Daría más detalle, pero es un dato personal que no hace falta para reconocer un acceso. El dispositivo aproximado basta. |
| Meta diaria solo en el navegador | No se vería en otros dispositivos. Guardándola en el plan del PCAP se sincroniza sin tablas nuevas. |

## Consecuencias

- **DONE:**
  - backend: 465 tests con 100 % de cobertura (9 nuevos en `tests/test_my_account.py`), ruff limpio y la migración coincide con los modelos;
  - e2e: los 4 de `e2e/my-account.spec.js`, que cubren el plan, el progreso, el certificado, el nombre, la contraseña, la actividad y WCAG 2.1 AA, además de la cuenta, la seguridad, DAW, el estudio, la navegación y la accesibilidad en verde (menos los 2 que necesitan Pyodide del CDN, igual que antes).
- **VERIFY en la fase 2 de la app (ADR-0024):** el `PcapState` de Android solo lee `plan.examDate`. Al sincronizar debe conservar `plan.dailyGoal`, igual que la web conserva el campo `app` que no conoce.
- **Privacidad:** la política describe el nuevo dato (actividad de la cuenta), su finalidad, su base legal y cuánto se conserva.
