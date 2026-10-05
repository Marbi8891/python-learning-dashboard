# ADR-0033: Sesión de la web en una cookie `HttpOnly`

- **Estado:** Propuesta (pendiente de que el autor la apruebe en el PR).
- **Fecha:** 2026-10-05
- **Revisa:** ADR-0032 (token solo en memoria), ADR-0022 (seguridad integral)

## Contexto

ADR-0032 dejó el token de acceso en una variable en memoria como paso intermedio. Tiene dos
problemas: recargar la página cierra la sesión y, mientras la página está abierta, un XSS puede
leer el token y llevárselo para usarlo fuera del navegador (T1539). El objetivo marcado era la
opción C: una cookie `HttpOnly`.

La web (GitHub Pages) y la API (Render) siguen en sitios distintos, así que la cookie es «de
terceros» para el navegador.

## Decisión

La web pide la sesión en cookie con la cabecera `X-PLD-Session: cookie`. Entonces la API:

- pone el JWT en la cookie `__Host-pld_session` con `HttpOnly; Secure; SameSite=None; Partitioned; Path=/`
  y la misma duración que el token (30 minutos), y **no lo devuelve en el cuerpo**;
- acepta la cookie **solo si la petición trae también esa cabecera**. Es la protección CSRF: otra
  web puede hacer que el navegador envíe la cookie, pero no añadir una cabecera propia sin pasar
  el *preflight* de CORS, que solo admite los orígenes de `CORS_ORIGINS`;
- borra la cookie en `POST /auth/logout` (nuevo) y en `logout-all`, y la renueva al cambiar la contraseña.

`Partitioned` (CHIPS) hace que la cookie solo exista cuando la API se usa desde la web del
proyecto, y es lo que permite que funcione en los navegadores que limitan las cookies de terceros.

**Plan B en el navegador.** Si el navegador no guarda la cookie (bloqueo de cookies de terceros,
por ejemplo en Safari), la web lo detecta al pedir `/users/me` justo después del login, vuelve a
iniciar sesión sin la cabecera y guarda el token en memoria, como en ADR-0032. Nadie se queda sin
poder entrar.

**Sin cambios para los demás clientes.** Sin la cabecera, la API responde como antes (`Bearer`
en el cuerpo). La app Android y los scripts no cambian. Si llegan cabecera `Authorization` y
cookie, manda la cabecera.

En `localStorage` solo queda `pld:session = "cookie"`, un aviso para no preguntar a la API al
cargar la página si no hubo sesión. No contiene el token.

## Alternativas descartadas

- **Mismo dominio y `SameSite=Strict`:** lo más limpio, pero exige un dominio propio para la web y
  la API. Queda como siguiente paso si se compra un dominio.
- **Token de refresco:** alargaría la sesión más allá de 30 minutos. No hacía falta para resolver
  el riesgo y añade una tabla y otro flujo. Se puede añadir más adelante.

## Consecuencias

- **La sesión sobrevive a recargar** durante los 30 minutos del token.
- **Un XSS ya no puede llevarse el token.** Sí podría hacer peticiones mientras la página esté
  abierta; la defensa contra eso sigue siendo la CSP y el escapado.
- **Hay una cookie.** Es técnica y estrictamente necesaria para el servicio que pide el usuario, así
  que no requiere consentimiento (art. 22.2 LSSI). La política de privacidad y el aviso legal lo indican.
- **CORS con credenciales:** `allow_credentials=True`. `CORS_ORIGINS` debe seguir siendo una lista
  explícita; nunca `*`.
- `Set-Cookie` se escribe a mano porque `set_cookie` de Starlette solo admite `Partitioned` con Python 3.14.
