# Plan de adecuación legal · Python Learning Dashboard

| Campo | Valor |
|---|---|
| Fecha | 2 de noviembre de 2026 |
| Base | [AUDITORIA_LEGAL.md](AUDITORIA_LEGAL.md) y [RIESGOS_LEGALES.md](RIESGOS_LEGALES.md) |
| Estado | Propuesta. **Nada de este plan se ha aplicado.** Cada acción espera la decisión del titular |

**Prioridades:**

- **P0:** detener o limitar una funcionalidad. **No hay ninguna**: no se ha encontrado exposición de
  datos ni un tratamiento sin base legal.
- **P1:** corregir pronto o antes de comercializar.
- **P2:** documentación, procesos y controles.
- **P3:** mejoras preventivas y mantenimiento.

Una acción **no se da por cumplida** porque exista un archivo: hace falta la prueba y la evidencia
indicadas. Ningún texto legal se publica sin que el titular lo apruebe, y el merge a `main` (que
publica la web) lo hace siempre él.

## 1. Las cuatro categorías de la fase 2

| Categoría | Acciones |
|---|---|
| **1. Correcciones técnicas que se pueden implementar directamente** (rama propia, pruebas, sin cambiar textos legales ni datos) | A-04 (prueba que compara la política con el código), A-09 (copia y restauración en local), A-17 (SRI o Pyodide alojado), A-18 (texto del README), A-20 (versiones fijadas con hashes) |
| **2. Documentación que necesita información del titular** | A-01 (política y aviso legal), A-03 (DPA), A-05 (conservación), A-06 (registro de actividades), A-07 (condiciones de uso), A-08 (incidentes), A-21 (procedencia de iconos) |
| **3. Decisiones que necesitan revisión jurídica** | A-07 (edad mínima de menores), A-10 a A-15 (comercialización), A-19 (marcas) |
| **4. Cambios que afectan a usuarios o producción y requieren autorización** | A-02 (merge del PR #77), A-05 si incluye borrar cuentas inactivas, A-16 (IA del PR #65), cualquier publicación de la política nueva |

## 2. P1: corregir pronto

### A-01. Actualizar la política de privacidad y el aviso legal

- **Qué cambiar.** En `privacidad.html`: apartado de Google (vía de registro, datos que llegan, rol,
  enlace a su política, cookie `g_state`); proveedor real de email y su ubicación; sesión de 30 minutos
  también en §7; tabla de almacenamiento (cookie, `localStorage`, `sessionStorage`, Cache Storage);
  plazos de conservación (A-05); historial de copias de Neon; texto de la casilla («He leído la
  política», no «acepto») y quitar la cita al art. 7.1 como base; procedimiento de derechos (A-06);
  frase de las cláusulas tipo ajustada a cada DPA (A-03). En `aviso-legal.html`: quitar «solo una
  cookie» y actualizar la fecha. En `index.html:292` y `:308`, el texto de las casillas.
- **Archivos.** `frontend/privacidad.html`, `frontend/aviso-legal.html`, `frontend/index.html`.
- **Información del titular.** DF-01 (identidad y residencia), DF-03 (proveedor de email), DF-04 (DPA),
  DF-05 (plan de Neon y logs de Render).
- **Prueba.** La prueba de A-04 en verde; lectura de la versión publicada en GitHub Pages después del
  merge; e2e de registro sin cambios.
- **Evidencia que conservar.** La versión anterior y la nueva de cada texto, con la fecha de
  publicación (el historial de git lo guarda) y el commit desplegado.
- **Revisión jurídica externa.** Recomendable, no imprescindible. Se puede partir del borrador de
  `/mnt/project-files/legal/borradores/privacidad-cambios.md`, quitando tutor y Android.
- **Hallazgos.** LEG-001 a LEG-004, LEG-024, LEG-052. Riesgo R-01.

### A-02. Fusionar el control de versiones de la sincronización

- **Qué cambiar.** Revisar y fusionar el PR #77 (versión + 409), que lleva el hilo «Consolidar y
  fusionar PR #71 y #69». Este plan no toca ese código.
- **Archivo.** `backend/app/routers/pcap.py`, `course_state.py`, almacenes del frontend (en el PR #77).
- **Información del titular.** Ninguna; solo su revisión y merge.
- **Prueba.** CI del PR en verde, incluida la prueba de dos pestañas.
- **Evidencia.** Enlace al PR fusionado y a la ejecución de Pages posterior.
- **Revisión jurídica.** No.
- **Hallazgos.** LEG-016. Riesgo R-02.

### A-03. Guardar los contratos de encargo y comprobar las transferencias

- **Qué cambiar.** Descargar el DPA de Render (incorporado a sus condiciones), el de Neon/Databricks y
  el del proveedor de email, con sus listas de subencargados y garantías de transferencia. Anotar la
  fecha de aceptación de cada cuenta.
- **Proceso.** Carpeta privada del titular, **fuera del repositorio público**. Referencia desde el
  registro de actividades (A-06).
- **Información del titular.** DF-03, DF-04.
- **Prueba.** Lista de comprobación: cada proveedor que trata datos tiene contrato, ubicación y
  garantía de transferencia identificados.
- **Evidencia.** PDF o captura fechada de cada contrato.
- **Revisión jurídica.** Solo si algún proveedor no ofrece DPA.
- **Hallazgos.** LEG-010 a LEG-013. Riesgo R-04.

### A-04. Prueba automática de coherencia entre la política y el código

- **Qué cambiar.** Una prueba (pytest o node) que lea `privacidad.html` y falle si: la duración de la
  sesión citada no coincide con `access_token_minutes`; el texto de emails dice «no activados»; falta la
  palabra «Google» mientras `googleClientId` tenga valor en `config.js`; aparece una clave `pld:` en el
  código que no está en la tabla de almacenamiento.
- **Archivos.** Nueva prueba en `backend/tests/` o `tests/unit/`; `docs/TESTING.md`.
- **Información del titular.** Ninguna para escribirla; pasará a verde con A-01.
- **Prueba.** Falla hoy (demuestra LEG-001 a LEG-003) y pasa tras A-01.
- **Evidencia.** Ejecución de la CI.
- **Revisión jurídica.** No.
- **Nota.** Por las reglas del proyecto no se puede fusionar una prueba en rojo: se entrega junto con
  A-01 en el mismo PR.

### P1-C. Antes de comercializar (bloqueante para cualquier cobro)

Este bloque **no se activa mientras el servicio sea gratuito**. Si el titular decide cobrar (donaciones
con contraprestación, Pack PCAP, cursos o suscripción), nada se cobra hasta completar A-10 a A-15.

| Acción | Qué hace falta | Información del titular | Prueba | Revisión jurídica |
|---|---|---|---|---|
| **A-10** Datos del prestador (LSSI art. 10) | Domicilio o dirección postal, NIF y, si hay, datos registrales en el aviso legal | DF-01, DF-02 | Aviso legal publicado con todos los campos del art. 10.1 aplicables | Sí, para decidir si actúa como particular, autónomo o sociedad |
| **A-11** Condiciones de contratación | Objeto, precio con impuestos, duración del acceso, requisitos técnicos, actualizaciones, conformidad, cancelación, reclamaciones, ley aplicable | DF-07, DF-08 | Las condiciones se muestran y se aceptan antes de pagar; copia enviada en soporte duradero | Sí |
| **A-12** Información precontractual | Pantalla previa al pago con todo lo anterior de forma clara | DF-07 | Prueba e2e del flujo de compra en un entorno de pruebas de la pasarela | Sí |
| **A-13** Desistimiento | Para acceso inmediato a contenido digital: casilla de consentimiento expreso, reconocimiento de la pérdida del derecho y confirmación posterior. Para suscripciones: desistimiento en 14 días con pago proporcional. **Nunca una renuncia general**. Comprobar si España ya ha transpuesto la Directiva 2023/2673 y, en ese caso, añadir la función de desistimiento en línea | DF-07 | Prueba e2e de cada caso; email de confirmación con la información | Sí |
| **A-14** Fiscalidad y facturación | Alta censal, facturas, IVA (OSS para consumidores de otros Estados de la UE) | DF-01, DF-08 | Factura de prueba revisada por la asesoría | Asesoría fiscal |
| **A-15** Licencia del contenido | Separar la licencia del código (MIT) y la del contenido de pago | DF-09 | `LICENSE` y README actualizados | Sí |

Además, para cobrar hace falta una pasarela de pago autorizada (no se añade en esta auditoría) y
revisar de nuevo la política de privacidad (nuevo encargado: la pasarela).

## 3. P2: documentación, procesos y controles

### A-05. Política de conservación

- **Qué cambiar.** Fijar plazos: cuentas sin actividad (por ejemplo, aviso y borrado tras un periodo que
  decida el titular), intentos de código, logs de Render, historial de Neon. Si se decide purgar,
  añadir `last_seen_at` y una tarea programada.
- **Archivos.** `privacidad.html` §3; si hay purga, `backend/app/models.py`, una migración de Alembic y
  una tarea (por ejemplo, un workflow programado que llame a un comando).
- **Información del titular.** El plazo elegido; DF-05.
- **Prueba.** Prueba automática de la purga con fechas simuladas; nunca contra datos reales.
- **Evidencia.** Política publicada y registro de ejecuciones de la tarea.
- **Revisión jurídica.** No necesaria.
- **Autorización.** Borrar cuentas reales afecta a usuarios: requiere autorización expresa y aviso
  previo.
- **Hallazgos.** LEG-005, LEG-007. Riesgo R-09.

### A-06. Registro de actividades y procedimiento de derechos

- **Qué cambiar.** Registro de actividades (art. 30) con los tratamientos T1-T13 de la auditoría. Un
  procedimiento breve para atender derechos: canal, verificación de identidad (responder solo al email
  de la cuenta), plazo de un mes, registro de solicitudes.
- **Archivos.** Documentos privados del titular; una versión sin datos personales puede ir en `docs/`.
- **Información del titular.** DF-01, DF-04, DF-05.
- **Prueba.** Revisión cruzada con el inventario del apartado 4 de la auditoría: ningún tratamiento sin
  fila.
- **Evidencia.** Registro fechado y su historial de versiones.
- **Revisión jurídica.** No necesaria.
- **Hallazgos.** LEG-008, LEG-009, LEG-014.

### A-07. Condiciones de uso con edad mínima

- **Qué cambiar.** Unas condiciones de uso gratuitas: objeto, uso aceptable (no atacar la consola ni la
  API), cuenta, edad mínima (14 años propuesto, con autorización de padres o tutores por debajo, ver
  §7.I de la auditoría), ausencia de garantía, propiedad intelectual, contacto, ley aplicable. Enlazarlas
  desde el registro y el pie.
- **Archivos.** Nuevo `frontend/condiciones.html`; `frontend/index.html`; `privacidad.html` (apartado
  para menores).
- **Información del titular.** DF-06.
- **Prueba.** e2e: el enlace aparece en el registro y en el pie; axe sin infracciones en la página nueva.
- **Evidencia.** Versión publicada y fecha.
- **Revisión jurídica.** **Sí** para la edad mínima y la capacidad del menor.
- **Base.** Borrador `/mnt/project-files/legal/borradores/condiciones-de-uso.md` (quitar el tutor).
- **Hallazgo.** LEG-022. Riesgo R-06.

### A-08. Procedimiento de incidentes y brechas

- **Qué cambiar.** Documento con: cómo se detecta (alertas sobre `pld.security` en los logs de Render),
  quién valora, criterios de riesgo, notificación a la AEPD en 72 horas cuando proceda, comunicación a
  los afectados si el riesgo es alto, y registro de todos los incidentes (art. 33.5), aunque no se
  notifiquen.
- **Archivos.** `docs/INCIDENTES.md` (sin datos personales) y referencia desde `SECURITY.md`.
- **Información del titular.** Medio de contacto de urgencia.
- **Prueba.** Simulacro en papel con un caso ficticio, anotado en el registro como prueba.
- **Evidencia.** El simulacro fechado.
- **Revisión jurídica.** No necesaria.
- **Hallazgo.** LEG-019. Riesgo R-03.

### A-09. Copia de seguridad y restauración

- **Qué cambiar.** Copia periódica cifrada de la base de datos (por ejemplo, `pg_dump` desde un workflow
  programado de GitHub Actions con la cadena en un secreto, cifrada antes de guardarla) o un plan de
  Neon con más historial si es gratuito. Documentar la restauración.
- **Archivos.** Workflow nuevo y `docs/DEPLOY.md`. **Los secretos los configura el titular.**
- **Información del titular.** Dónde guardar la copia y quién tiene la clave.
- **Prueba.** Restauración en una base de datos local, sin datos reales en el repositorio.
- **Evidencia.** Registro de la restauración de prueba.
- **Revisión jurídica.** No. La copia es otro tratamiento que debe figurar en el registro (A-06).
- **Hallazgo.** LEG-017. Riesgo R-03.

### A-16. Revisión previa si se recupera la IA (PR #65)

- **Qué cambiar.** Antes de fusionar el PR #65: aviso visible de que se habla con una IA (RIA art.
  50.1), DPA de OpenAI y garantías de transferencia, minimización de lo que se envía, política
  actualizada y reevaluación de la EIPD.
- **Información del titular.** DF-12.
- **Prueba.** e2e que comprueba el aviso de IA; prueba de que no se envía el email ni el nombre del
  usuario al proveedor.
- **Revisión jurídica.** Recomendable.
- **Hallazgo.** LEG-043. Riesgo R-08.

## 4. P3: mejoras preventivas

| Acción | Qué cambiar | Archivo | Prueba | Revisión jurídica | Hallazgo |
|---|---|---|---|---|---|
| A-17 | SRI para Pyodide o alojar Pyodide en el propio sitio | `pyodide-worker.js`, CSP | e2e de la consola | No | LEG-045 |
| A-18 | README: «objetivo WCAG 2.1 AA, con pruebas automáticas axe» en lugar de afirmar conformidad; mismo criterio para cualquier afirmación pública | `README.md` | Revisión del texto | No | LEG-035 |
| A-19 | Revisar las políticas de marca de la PSF y de Python Institute | — | Nota fechada | Sí, si se usa en un nombre comercial | LEG-041 |
| A-20 | Fijar versiones del backend con hashes (PLD-SEC-005) | `backend/requirements.txt` | CI y `pip-audit` | No | LEG-044 |
| A-21 | Documentar autoría o licencia de iconos e imagen de redes | `frontend/icons/`, `docs/AUDITORIA-Y-LICENCIAS.md` | Revisión | No | LEG-038 |
| A-22 | Cambio de email desde la web, con verificación | Backend y «Mi cuenta» | pytest y e2e | No | LEG-008 |
| A-23 | Dominio propio o no publicar otros proyectos en `marbi8891.github.io` | Despliegue | Revisión | No | LEG-047 |
| A-24 | Muestreo de originalidad del temario antes de vender | `frontend/data/` | Informe | No | LEG-040 |
| A-25 | Reevaluar esta auditoría cada seis meses o al cambiar el modelo de negocio, añadir un proveedor o activar analítica | Este documento | Nueva fecha de comprobación | — | — |

## 5. Documentos legales según el escenario

| Documento | Hoy (gratuito) | Con publicidad o donaciones | Con cursos o suscripción | Estado |
|---|---|---|---|---|
| Aviso legal | Recomendable (existe) | Obligatorio completo (art. 10 LSSI) | Obligatorio completo | Existe; incompleto si hay actividad económica |
| Política de privacidad | Obligatoria | Obligatoria | Obligatoria | Existe; **desactualizada** (A-01) |
| Política de cookies separada | No necesaria (basta la tabla en la política) | Necesaria si hay cookies publicitarias o analíticas no exentas, con banner y panel | Igual | No hace falta hoy |
| Condiciones de uso | Recomendable | Recomendable | Integradas en las de contratación | No existe (A-07) |
| Condiciones de contratación | No | Solo si hay contraprestación | Obligatorias | No existe (A-11) |
| Información precontractual | No | Solo si hay contrato | Obligatoria | No existe (A-12) |
| Procedimiento de derechos | Obligatorio (interno) | Igual | Igual | No existe (A-06) |
| Procedimiento de eliminación de cuenta | Existe en la web | Igual | Igual | Existe; explicar el historial de Neon |
| Información de accesibilidad | Recomendable | Recomendable | Obligatoria solo si deja de ser microempresa | No hace falta hoy |
| Contratos con proveedores | Obligatorios (art. 28) | Igual | Igual + pasarela | Sin copia (A-03) |
| Registro de actividades | Probablemente obligatorio | Igual | Igual | No existe (A-06) |
| Procedimiento de incidentes | Obligatorio en la práctica (arts. 33-34) | Igual | Igual | No existe (A-08) |
| Información sobre IA | No (no hay IA) | — | Si se añade IA | No hace falta hoy (A-16) |

**Plantillas.** No se redacta ningún documento definitivo con datos inventados. En la fase 2, cada
documento se preparará como plantilla con los campos pendientes marcados así: `[[TITULAR: nombre
completo]]`, `[[TITULAR: domicilio o dirección postal]]`, `[[TITULAR: NIF]]`, `[[TITULAR: proveedor de
email]]`, `[[TITULAR: plazo de conservación de cuentas inactivas]]`, `[[TITULAR: edad mínima]]`,
`[[TITULAR: precio con impuestos]]`, `[[TITULAR: duración del acceso]]`. Los borradores del 19/10 en
`/mnt/project-files/legal/borradores/` sirven de punto de partida.

## 6. Información que debe aportar el titular

Ordenada por lo que desbloquea:

1. **Proveedor de email configurado en Render** (DF-03): desbloquea A-01 y A-03.
2. **Confirmación de identidad, residencia y si actúa como particular** (DF-01): desbloquea A-01, A-06
   y la decisión sobre la LSSI.
3. **Plan de Neon y retención de logs de Render** (DF-05): desbloquea A-05 y A-09.
4. **Copias de los DPA** (DF-04): desbloquea A-03.
5. **Público objetivo y edad mínima** (DF-06): desbloquea A-07.
6. **Plazo para cuentas inactivas**: desbloquea A-05.
7. **Modelo de negocio y calendario** (DF-07, DF-08): decide cuándo se activa P1-C.
8. **Licencia del contenido** (DF-09), **procedencia de iconos** (DF-10), **otros proyectos en el
   mismo origen** (DF-11) e **intención con los PR #63 y #65** (DF-12).

## 7. Condiciones antes de comercializar

No se debería cobrar nada hasta que se cumpla todo esto:

1. A-01 publicado (política y aviso legal coherentes con el sistema).
2. A-02 fusionado (sin pérdida de progreso por escrituras simultáneas).
3. A-03 hecho, incluida la pasarela de pago como nuevo encargado.
4. A-10 a A-15 completos y revisados por un abogado y una asesoría fiscal.
5. A-06, A-07 y A-08 en vigor.
6. Estado de la transposición de la Directiva 2023/2673 comprobado en el BOE.
7. Esta auditoría repetida con el flujo de compra real.

## 8. Próximos pasos recomendados

1. El titular responde a las preguntas del apartado 6 (una línea por pregunta basta).
2. Primer PR de la fase 2: A-01 + A-04 juntos (política corregida y prueba que la vigila), sin tocar la
   lógica de sincronización. Se publica solo cuando el titular lo fusione.
3. Fusionar el PR #77 (A-02) en su propio hilo.
4. Después: A-06, A-07 y A-08 (documentos), y A-05 y A-09 (técnicos).
5. El bloque P1-C solo cuando el titular decida cobrar.
