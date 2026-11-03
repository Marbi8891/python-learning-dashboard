# Procedimiento de incidentes y brechas de datos

| Campo | Valor |
|---|---|
| Versión | 0.1 · 2 de noviembre de 2026 |
| Norma | RGPD arts. 33 y 34 |
| Relacionado | [SECURITY.md](../SECURITY.md) (avisos de vulnerabilidades) · [REGISTRO_TRATAMIENTOS.md](REGISTRO_TRATAMIENTOS.md) · [PLAN_ADECUACION_LEGAL.md](PLAN_ADECUACION_LEGAL.md) (A-08) |

Una **brecha** es cualquier incidente de seguridad que destruye, pierde, altera, revela o da acceso
sin permiso a datos personales. Ejemplos en este proyecto: alguien lee la base de datos de Neon, se
filtra `JWT_SECRET` o la cadena de conexión, un fallo borra el progreso de muchos usuarios, o un error
muestra los datos de un usuario a otro.

## 1. Detectar

- Avisos por el canal de `SECURITY.md`.
- Logs de Render: eventos `pld.security` de nivel WARNING (`auth.token_forged`,
  `auth.token_revoked_used`, `auth.rate_limited` en ráfagas, `request.too_large`).
- Avisos de GitHub (Dependabot, escaneo de secretos) y de los proveedores (Render, Neon, email).
- Quejas de usuarios (por ejemplo, «he perdido mi progreso» o «veo datos que no son míos»).

## 2. Contener (en las primeras horas)

| Situación | Acción |
|---|---|
| Secreto filtrado (`JWT_SECRET`, `DATABASE_URL`, clave del proveedor de email) | Cambiarlo en el panel del proveedor y en Render. Cambiar `JWT_SECRET` cierra todas las sesiones |
| Cuenta de usuario comprometida | El usuario cambia la contraseña o usa «Cerrar sesión en todos los dispositivos» |
| Fallo de código que expone o borra datos | Revertir el commit en una rama y que el titular fusione el revert; si urge, suspender el servicio en Render |
| Proveedor comprometido | Seguir sus instrucciones y valorar el riesgo con el apartado 3 |

No borrar logs ni pruebas: se necesitan para valorar el alcance.

## 3. Valorar el riesgo

Responder por escrito:

1. ¿Qué datos se han visto afectados (email, nombre, código, progreso, hashes)?
2. ¿Cuántas personas, aproximadamente?
3. ¿Los datos estaban protegidos (hash Argon2id, seudónimos) o en claro?
4. ¿Qué puede pasarles a las personas (spam, suplantación, pérdida de trabajo de estudio)?

| Resultado | Qué hacer |
|---|---|
| Sin riesgo probable para las personas (p. ej., se filtró un seudónimo sin la clave) | Solo registrarlo (apartado 5) |
| Riesgo probable | **Notificar a la AEPD en 72 horas** desde que se tiene constancia (art. 33), por su sede electrónica. Si falta información, notificar lo que se sepa y completar después |
| Riesgo alto (p. ej., emails y hashes de contraseñas filtrados) | Notificar a la AEPD **y** avisar a los afectados sin demora, en lenguaje claro: qué ha pasado, qué datos, qué hemos hecho y qué deben hacer (art. 34) |

## 4. Avisar a los afectados

Por email a cada afectado, o con un aviso visible en la web si son muchos. Incluir el contacto de
privacidad. No culpar al usuario ni minimizar el problema.

## 5. Registrar

Todo incidente se anota, se notifique o no (art. 33.5), en un registro privado del titular, fuera del
repositorio:

| Fecha de detección | Qué pasó | Datos y personas afectadas | Riesgo | ¿Notificado a la AEPD? (fecha) | ¿Aviso a afectados? | Medidas tomadas |
|---|---|---|---|---|---|---|

## 6. Aprender

Después de cada incidente: una prueba automática que lo reproduzca (si es de código), una entrada en
`SECURITY.md` si cambia alguna medida y una revisión de este procedimiento.

## 7. Simulacro

Una vez al año, repasar este procedimiento con un caso ficticio (por ejemplo, «se ha filtrado
`DATABASE_URL` en un commit») y anotarlo en el registro como simulacro.

Responsable de decidir y notificar: el titular. Contacto de urgencia: `[[TITULAR: medio de contacto]]`.
