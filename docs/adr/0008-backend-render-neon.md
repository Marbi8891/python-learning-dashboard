# ADR-0008: Backend en Render y base de datos en Neon

- **Estado:** Aceptada
- **Fecha:** 2026-09-26

## Contexto

Para activar las cuentas hace falta publicar el backend. El Blueprint original creaba también la base de datos en Render, pero la PostgreSQL gratuita de Render caduca a los 30 días (con 14 días de gracia) y después se borra con todas las cuentas.

## Opciones

- **A. Render + Neon:** API gratis en Render y PostgreSQL gratis y permanente en Neon (0,5 GB, 100 h de cómputo al mes), las dos en Frankfurt.
- **B. Todo en Render gratis:** un clic, pero se pierden los datos al mes.
- **C. Render de pago:** sin caducidad, con coste mensual.

## Decisión

A, elegida por el autor: coste cero, datos permanentes y servidores en la UE (RGPD).

## Consecuencias

- `render.yaml` ya no crea la base de datos: `DATABASE_URL` se pega a mano desde Neon (es un secreto, no va al repositorio). El servicio se crea en `frankfurt`.
- Neon suspende la base de datos sin uso y cierra las conexiones: el motor usa `pool_pre_ping` y `pool_recycle=300` para no devolver errores 500 tras un rato inactivo.
- Plan gratuito de Render: la API se duerme tras 15 min sin tráfico y tarda ~1 min en despertar. Aceptable para un proyecto educativo.
- Si se superan los 0,5 GB, Neon bloquea las escrituras (no borra datos); el paso natural es su plan de pago por uso.
