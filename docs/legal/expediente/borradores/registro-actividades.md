# Registro de actividades de tratamiento: borrador

| Campo | Valor |
|---|---|
| Estado | **BORRADOR**, documento interno (no se publica) |
| Versión | 0.1 · 19/10/2026 · producto `main@730d78d` |
| Responsable | Mrabeh Fathi Boussayff · [CORREO DE PRIVACIDAD] · [DOMICILIO POR CONFIRMAR] |
| Delegado de protección de datos | No designado. No se ha analizado el art. 37 RGPD; con los datos actuales no parece obligatorio (interpretación, sin verificar) |
| Base del documento | RGPD art. 30.1; la exención del 30.5 no parece aplicable porque el tratamiento no es ocasional (T6 de la [matriz](../MATRIZ.md)) |

| # | Actividad | Finalidad | Interesados | Datos | Base | Destinatarios y encargados | Transferencias | Conservación | Medidas |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Cuentas de usuario | Crear la cuenta e iniciar sesión | Usuarios registrados | Email, nombre, hash Argon2id, fecha de aceptación | 6.1.b | Render (servidor), Neon (BD); Google si se usa «Continuar con Google» (tercero) | Proveedores con matriz en EE. UU. [DPA PENDIENTE DE VERIFICACIÓN] | Mientras exista la cuenta | Argon2id, HTTPS, cookie `__Host-` HttpOnly, límites de intentos |
| 2 | Progreso de aprendizaje | Guardar y sincronizar el progreso | Usuarios registrados | Lecciones, intentos (código y resultado, 50 por lección), estado PCAP y cursos, XP y logros | 6.1.b | Render, Neon | Ídem | Mientras exista la cuenta | Aislamiento por usuario (pruebas de seguridad del repo) |
| 3 | Actividad de la cuenta | Que el usuario detecte accesos ajenos | Usuarios registrados | Últimos 20 eventos: tipo, fecha y dispositivo aproximado | 6.1.f | Render, Neon | Ídem | 20 últimos; se borran con la cuenta | Sin IP ni navegador exacto (`backend/app/activity.py`) |
| 4 | Registro de seguridad | Detectar ataques | Usuarios y visitantes | Tipo de evento, id interno, seudónimos de IP y email | 6.1.f | Render (logs) | Ídem | [PLAZO DE CONSERVACIÓN DE LOGS DE RENDER POR VALIDAR] | Seudonimización con clave del servidor |
| 5 | Limitación de intentos | Proteger las cuentas | Visitantes que intentan entrar | IP en memoria | 6.1.f | — | — | En memoria; se pierde al reiniciar | — |
| 6 | Tutor Python | Responder dudas | Usuarios que lo usan | Pregunta, código, error, estado de la lección | 6.1.b | Hoy ninguno (`mock`, P4). Con Ollama, en el propio servidor. Con Anthropic, encargado [NO ACTIVADO] | Solo con Anthropic | En memoria, 2 h sin uso | Sin email ni nombre en la consulta |
| 7 | Recuperación de contraseña | Restablecer el acceso | Usuarios | Email, token (hash), fecha | 6.1.b | [PROVEEDOR PENDIENTE DE VERIFICACIÓN] | [POR CONFIRMAR] | 30 minutos | Un solo uso; el token no se escribe en los logs |
| 8 | Contacto por email | Atender derechos y consultas | Quien escribe | Email y contenido del mensaje | 6.1.c (derechos) / 6.1.f | Google (Gmail del titular) | EE. UU. | [PLAZO POR VALIDAR] | — |

Notas: las actividades 1, 2, 3, 6 y 7 se han revisado en el código. Las 4, 5 y 8, en parte en el código y en
parte en la política actual. Los destinatarios y transferencias dependen de contratos que no se han visto.
