# Registro de actividades de tratamiento y procedimiento de derechos

| Campo | Valor |
|---|---|
| Versión | 0.1 · 2 de noviembre de 2026 · **plantilla** |
| Base | [AUDITORIA_LEGAL.md](AUDITORIA_LEGAL.md), apartado 4 (tratamientos T1-T14) |
| Norma | RGPD art. 30 (registro) y arts. 12-22 (derechos) |
| Estado | Los campos `[[TITULAR: …]]` los rellena el titular. Hasta entonces el registro **no está completo** |

Este archivo no contiene datos de ningún usuario. Las copias de los contratos con proveedores se guardan
fuera del repositorio (acción A-03 del [plan](PLAN_ADECUACION_LEGAL.md)).

## 1. Datos del responsable

| Campo | Valor |
|---|---|
| Responsable | Mrabeh Fathi Boussayff (declarado en `frontend/privacidad.html`) · persona física que publica el proyecto como particular (confirmado por el titular el 2/11/2026) |
| País de establecimiento | España (confirmado el 2/11/2026) |
| Contacto de privacidad | El email publicado en la política de privacidad |
| Delegado de protección de datos | No designado: no es obligatorio (auditoría, LEG-021) |

## 2. Actividades de tratamiento

Todas las actividades comparten estas medidas de seguridad (art. 32): contraseñas con Argon2id, HTTPS
también entre la API y la base de datos, cookie de sesión `HttpOnly` de 30 minutos, límite de intentos,
registro de seguridad seudonimizado, cabeceras de seguridad y CSP. Detalle en `SECURITY.md` y en el
apartado 7.G de la auditoría.

### RAT-1. Cuentas de usuario

| Campo | Contenido |
|---|---|
| Finalidad | Crear la cuenta, iniciar sesión (contraseña o Google) y recuperar la contraseña |
| Base jurídica | Ejecución del servicio solicitado (RGPD art. 6.1.b) |
| Interesados | Personas que crean una cuenta |
| Datos | Email, nombre, hash de la contraseña, fechas de alta, de lectura de la política y de verificación del email; hash del enlace de recuperación |
| Destinatarios | Render (servidor, encargado), Neon (base de datos, encargado), Gmail (Google LLC), cuenta de Gmail personal del titular por SMTP, para los emails de recuperación (sin contrato de encargo del art. 28: ver LEG-012). Google interviene como responsable independiente cuando el usuario elige entrar con Google |
| Transferencias | Render: DPA con Marco UE-EE. UU. y cláusulas tipo. Neon: `[[TITULAR: garantía según su DPA]]`. Email (Gmail): Google LLC, EE. UU., adherida al Marco de Privacidad de Datos UE-EE. UU. [VERIFICAR en dataprivacyframework.gov] |
| Conservación | Mientras exista la cuenta. Cuentas inactivas: `[[TITULAR: plazo, si se decide]]`. Enlaces de recuperación: 30 minutos. Copias de Neon: historial de 6 horas (plan gratuito, confirmado el 2/11/2026) |
| Código | `backend/app/models.py` (`User`, `PasswordResetToken`), `backend/app/routers/auth.py` |

### RAT-2. Progreso de estudio

| Campo | Contenido |
|---|---|
| Finalidad | Guardar y sincronizar el progreso entre dispositivos |
| Base jurídica | Ejecución del servicio (art. 6.1.b) |
| Interesados | Usuarios con cuenta |
| Datos | Lecciones completadas, código enviado en los ejercicios y su resultado (50 por lección), documentos de progreso (PCAP, cursos DAW, núcleo, XP, racha, logros) |
| Destinatarios | Render y Neon (encargados) |
| Transferencias | Las de RAT-1 |
| Conservación | Mientras exista la cuenta |
| Código | `models.py` (`LessonProgress`, `ExerciseAttempt`, `PcapState`, `CourseState`) |

### RAT-3. Seguridad de las cuentas

| Campo | Contenido |
|---|---|
| Finalidad | Que el usuario vea accesos a su cuenta; detectar ataques; limitar intentos |
| Base jurídica | Interés legítimo en la seguridad (art. 6.1.f) |
| Interesados | Usuarios con cuenta y quien intenta entrar |
| Datos | Actividad de la cuenta (tipo, fecha, dispositivo aproximado, sin IP; 20 últimos); registro de seguridad con seudónimos HMAC de IP y email; IP en memoria unos minutos |
| Destinatarios | Render (logs) |
| Conservación | Actividad: 20 eventos. Logs: `[[TITULAR: retención de logs de Render]]`. IP: solo en memoria |
| Código | `backend/app/activity.py`, `security_events.py`, `rate_limit.py` |

### RAT-4. Registros técnicos de acceso

| Campo | Contenido |
|---|---|
| Finalidad | Servir la web y la API |
| Base jurídica | Interés legítimo (art. 6.1.f) |
| Interesados | Visitantes |
| Datos | IP y datos técnicos de cada petición |
| Destinatarios | GitHub Pages, Render, jsDelivr (al descargar Pyodide) |
| Conservación | La de cada proveedor `[[TITULAR: anotar la retención de cada uno]]` |

### RAT-5. Atención de derechos y de incidentes

| Campo | Contenido |
|---|---|
| Finalidad | Atender solicitudes de derechos y gestionar incidentes de seguridad |
| Base jurídica | Obligación legal (art. 6.1.c, en relación con los arts. 12 y 33) |
| Datos | Email del solicitante, contenido de la solicitud o del incidente, fechas |
| Conservación | `[[TITULAR: plazo; se propone 3 años para poder demostrar que se atendió]]` |
| Dónde | Registro privado del titular, fuera del repositorio |

## 3. Procedimiento para atender derechos

1. **Canal.** La solicitud llega al email de privacidad publicado.
2. **Identidad.** Solo se atiende si llega desde el email de la cuenta. Si llega desde otro email, se
   pide que escriba desde el de la cuenta. Nunca se piden documentos de identidad si no hace falta.
3. **Plazo.** Responder en un mes desde la recepción (art. 12.3). Si es complejo, se puede ampliar dos
   meses más avisando dentro del primer mes y explicando por qué.
4. **Qué hacer según el derecho:**
   - **Acceso o portabilidad:** indicar «Tu cuenta → Descargar mis datos (JSON)». Si no puede entrar,
     ayudarle primero a recuperar el acceso (la exportación necesita su sesión) o, si no es posible,
     preparar la exportación con una consulta revisada sobre ese usuario y enviarla a su email.
   - **Supresión:** indicar «Tu cuenta → Eliminar mi cuenta». Si no puede entrar, borrar la cuenta con
     una consulta revisada en la base de datos, sobre ese usuario y nada más, y confirmarlo por email.
   - **Rectificación del email:** cambiarlo en la base de datos tras comprobar que controla los dos
     emails (enlace o código enviado a cada uno).
   - **Oposición o limitación** sobre RAT-3: valorar caso por caso; la seguridad de las cuentas suele
     prevalecer, y hay que explicárselo.
5. **Registro.** Anotar fecha de entrada, derecho, respuesta y fecha de respuesta (RAT-5).
6. **Reclamación.** En cada respuesta negativa, recordar que puede reclamar ante la AEPD.
