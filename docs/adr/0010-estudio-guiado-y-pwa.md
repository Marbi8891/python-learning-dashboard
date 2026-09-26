# ADR-0010: Estudio guiado, sincronización de la preparación y PWA

- **Estado:** Aceptada
- **Fecha:** 2026-09-27

## Contexto

Tras enfocar la web en el PCAP (ADR-0009), la preparación del examen vivía solo en el navegador y no guiaba qué estudiar cada día. El autor pidió añadir todas las mejoras propuestas salvo las desaconsejadas (tutor con IA, ranking y panel de profesor: coste, privacidad o tamaño desproporcionados).

## Decisiones

1. **Sincronización como documento JSON por usuario** (`pcap_states`, `GET/PUT /api/pcap-state`), no como tablas normalizadas: el estado es pequeño (límite 200 KB), solo lo lee su dueño y no se consulta desde el servidor. Al iniciar sesión el navegador **fusiona** local y cuenta sin perder nada (historial más largo por pregunta, unión de simulacros y fichas, máximos y banderas OR, repaso más reciente) y sube el resultado; después cada cambio se envía agrupado (1,5 s). Con dos dispositivos abiertos a la vez gana la última escritura: aceptable para un alumno.
2. **Del fallo a la teoría:** cada pregunta y ficha tiene `lesson` (lección de su bloque que la explica), asignado a mano y comprobado por un test.
3. **Repaso espaciado** con cajas de Leitner (1, 3, 7, 14 y 30 días). Solo entra en el repaso lo ya visto; fallar devuelve a la caja 1. Sin algoritmos más complejos (SM-2): el beneficio extra no compensa en un banco de 174 elementos.
4. **Plan de estudio** calculado al vuelo a partir de la fecha del examen: lecciones pendientes repartidas por semanas, los dos bloques con más puntos por ganar (fallo × peso), repaso diario y simulacros en las últimas semanas. Es orientativo y no guarda tareas.
5. **Certificado** generado en el navegador e impreso con CSS (`window.print`, «Guardar como PDF»): sin librerías de PDF. Exige completar las lecciones del examen y aprobar un simulacro, y declara que **no es oficial**.
6. **PWA:** manifest + service worker. Web en *network-first* (siempre la versión nueva, la copia solo sin conexión), Pyodide en *cache-first* (URL versionadas e inmutables) y la API **nunca** en caché (datos personales). Desactivado en localhost para no depurar contra cachés.
7. **Email:** sin código nuevo; guía para Gmail con contraseña de aplicación o un servicio transaccional. La web detecta el SMTP por `/api/health`.

## Consecuencias

- Una migración nueva (tabla `pcap_states`), incluida en la exportación y el borrado RGPD.
- El service worker puede servir una versión antigua solo sin conexión; con red siempre carga la última.
- VERIFY: versiones de las acciones de GitHub con Node 24 tomadas de sus repositorios y de PRs de Dependabot en septiembre de 2026.
