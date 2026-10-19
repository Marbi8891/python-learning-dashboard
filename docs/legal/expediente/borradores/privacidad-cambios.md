# Política de privacidad: cambios propuestos

| Campo | Valor |
|---|---|
| Estado | **BORRADOR**, no publicar |
| Documento afectado | `frontend/privacidad.html` (versión del 6/10/2026) |
| Versión propuesta | 2026-10-XX · [FECHA DE APROBACIÓN] |
| Responsable | Mrabeh Fathi Boussayff (declarado en el repo; confirmar P1) |
| Requiere | Respuestas a P3 y P4 del [diagnóstico](../DIAGNOSTICO.md) y decisión sobre el borrado de cuentas de Google |

Solo se proponen los apartados que cambian. El resto de la política actual se mantiene.

---

## Texto propuesto para publicación

### 2. Qué datos tratamos y para qué (fila nueva en la tabla)

| Datos | Finalidad | Base legal (RGPD) |
|---|---|---|
| Si eliges «Continuar con Google»: tu email, tu nombre y la confirmación de que Google ha verificado tu email, que Google nos envía con tu permiso. No recibimos tu contraseña de Google ni tu foto, y no publicamos nada en tu cuenta de Google | Crear tu cuenta o iniciar sesión sin contraseña | Ejecución del servicio que solicitas (art. 6.1.b) |

### 3. Cuánto tiempo los conservamos (añadir)

Los registros de acceso del servidor los conserva Render durante [PLAZO DE CONSERVACIÓN DE LOGS DE
RENDER POR VALIDAR] y después se borran automáticamente.

### 4. Quién más interviene (añadir y sustituir)

- **Inicio de sesión con Google:** Google LLC / Google Ireland Ltd. [ENTIDAD POR CONFIRMAR EN LAS
  CONDICIONES DE GOOGLE IDENTITY]. Si eliges «Continuar con Google», Google te identifica y nos envía los
  datos de la tabla anterior. Para ello trata tus datos según su
  [política de privacidad](https://policies.google.com/privacy). Google indica que los datos de «Sign in
  with Google» no se usan para publicidad.
  - *Opción A (si se carga el script solo bajo demanda):* el componente de Google solo se descarga
    cuando abres «Entrar» o «Crear cuenta».
  - *Opción B (situación actual):* el componente de Google se descarga al abrir la web, para mostrar el
    botón; Google recibe tu IP y los datos técnicos del navegador aunque no inicies sesión.
- **Emails de recuperación de contraseña:** [PROVEEDOR PENDIENTE DE VERIFICACIÓN: Brevo (Sendinblue SAS,
  Francia) u otro], que recibe tu email y el contenido del mensaje para enviarlo, como encargado del
  tratamiento. *(Mantener «todavía no están activados» mientras no se configure.)*

### 5. Almacenamiento en tu navegador. Estadísticas de visitas (sustituir el bloque)

**Estadísticas de visitas.** Ahora mismo no medimos visitas. Si en el futuro activamos GoatCounter, lo
indicaremos aquí antes. No usa cookies ni guarda tu IP, y no cuenta tu visita si tu navegador envía
«No rastrear» o «Global Privacy Control».

### 6. Tus derechos (sustituir la línea de supresión)

- **Supresión:** desde «Tu cuenta → Eliminar mi cuenta».
  - *Mientras no se corrija el código:* si creaste la cuenta con Google, todavía no puedes eliminarla tú
    desde la web. Escríbenos a [CORREO DE PRIVACIDAD] desde el email de tu cuenta y la borraremos en un
    plazo máximo de un mes.

### 7. Seguridad (corregir)

- Sesiones que caducan a los 30 minutos; puedes cerrar la sesión en todos tus dispositivos, y cambiar
  la contraseña las cierra todas.

---

## Notas internas (no publicar)

- **Evidencias:** `backend/app/routers/auth.py:37-107` (Google), `frontend/index.html:50` (script en cada
  visita), `backend/app/routers/account.py:124` y `auth.py:82` (borrado imposible para cuentas de Google),
  `backend/app/config.py:32` (30 min), `frontend/config.js` (GoatCounter vacío).
- **Google como tercero y no como encargado:** es una interpretación (D2 del diagnóstico). No se ha
  consultado un criterio de la AEPD sobre este caso.
- **Plazo de un mes:** RGPD art. 12.3 (no releído en esta sesión; verificar antes de publicar).
- **Capa básica:** junto a las casillas de aceptación (`index.html:290` y `:306`) conviene añadir una
  línea: «Responsable: Mrabeh Fathi Boussayff. Finalidad: tu cuenta y tu progreso. Derechos: acceso,
  rectificación, supresión y otros, en la política de privacidad.» (LOPDGDD art. 11).
- La app Android y la política dicen «1 hora» en otro sitio (`Sync.kt:43`, comentario). Conviene
  revisarlo con auth-security, porque el servidor da 30 minutos salvo que Render cambie
  `ACCESS_TOKEN_MINUTES`.

## Lista de comprobación antes de publicar

- [ ] P3 respondida: proveedor de email real o «no activado».
- [ ] Decidida la opción A o B para Google (y, si es A, PR de código fusionado antes).
- [ ] Decidido cómo borrar cuentas de Google (y, si se corrige, quitar el texto provisional).
- [ ] Plazo de logs de Render comprobado en su documentación.
- [ ] Entidad de Google comprobada.
- [ ] Fecha de «Última actualización» cambiada.
- [ ] Aprobación del titular para esta versión concreta.
