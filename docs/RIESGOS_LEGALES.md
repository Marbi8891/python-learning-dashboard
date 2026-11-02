# Registro de riesgos legales · Python Learning Dashboard

| Campo | Valor |
|---|---|
| Fecha | 2 de noviembre de 2026 |
| Base | [AUDITORIA_LEGAL.md](AUDITORIA_LEGAL.md) (commit `23872f8`) |
| Estado | Borrador técnico, sin revisión jurídica |

Recoge los riesgos de mayor impacto. Cada uno remite a los hallazgos LEG-xxx de la matriz y a las
acciones del [plan de adecuación](PLAN_ADECUACION_LEGAL.md).

**Escala.** Probabilidad: *alta* (ya ocurre o es casi seguro), *media* (plausible en el próximo año),
*baja* (poco probable). Impacto: *alto* (exposición o pérdida de datos, contratación irregular,
sanción relevante), *medio* (derechos de los usuarios afectados, corrección urgente), *bajo*
(inexactitud sin daño previsible).

**Responsable de la decisión.** En todos los casos es el titular (MRABEH). Donde se indica, conviene
que decida con un abogado o una asesoría.

## Resumen

| Id | Riesgo | Probabilidad | Impacto | Prioridad | Tipo |
|---|---|---|---|---|---|
| R-01 | La política de privacidad no describe Google ni el envío de emails, que están activos en producción | Alta (demostrado) | Medio | P1 | Documental |
| R-02 | Dos pestañas o dispositivos pueden sobrescribir el progreso | Media | Medio | P1 | Técnico |
| R-03 | Sin procedimiento de brechas ni copias de seguridad que permitan recuperarse | Baja | Alto | P2 | Organizativo y técnico |
| R-04 | Encargados y transferencias sin evidencia contractual guardada | Media | Medio | P1-P2 | Documental y contractual |
| R-05 | Empezar a cobrar sin el marco legal de comercio y consumo | Alta si se comercializa | Alto | P1 antes de vender | Jurídico |
| R-06 | Menores registrados sin edad mínima ni condiciones de uso | Media | Medio | P2 | Documental |
| R-07 | El temario queda bajo licencia MIT y cualquiera puede revenderlo | Alta si se comercializa | Alto (económico) | P1 antes de vender | Jurídico |
| R-08 | Reintroducir IA (PR #65) sin revisar privacidad ni transparencia | Media | Medio | P2 | Jurídico y técnico |
| R-09 | Conservación indefinida de cuentas inactivas y de código enviado | Alta (demostrado) | Bajo | P2 | Documental y técnico |
| R-10 | Afirmaciones públicas que no se pueden demostrar | Media | Bajo | P2-P3 | Documental |
| R-11 | Confusión con las marcas «Python» y «PCAP» o con el certificado | Baja | Medio si se vende | P3 | Jurídico |

No hay ningún riesgo que exija detener una funcionalidad (P0): no se ha encontrado exposición de datos
ni tratamiento sin base legal.

## R-01. La política no describe el sistema real

- **Situación detectada.** Producción tiene activos el inicio de sesión con Google y el envío de emails
  de recuperación. La política publicada (26/10/2026) no menciona Google, dice que los emails «todavía
  no están activados», afirma que solo hay «una sola cookie» (Google puede dejar `g_state`) y da dos
  duraciones distintas de la sesión.
- **Norma afectada.** RGPD arts. 5.1.a, 12.1 y 13.1.c y e; LSSI art. 22.2 (información del
  almacenamiento).
- **Probabilidad.** Alta: ya ocurre con cada registro.
- **Impacto.** Medio. No hay daño material conocido, pero la información del art. 13 es incompleta para
  todos los usuarios con cuenta, y es lo primero que revisaría una reclamación.
- **Evidencia.** `GET /api/health` → `"email": true, "google": true` (2/11/2026);
  `frontend/privacidad.html` §4, §5 y §7; `backend/app/routers/auth.py:58-118`;
  `backend/app/config.py:28`; `e2e/account.spec.js:110`. Hallazgos LEG-001, LEG-002, LEG-003, LEG-024,
  LEG-052.
- **Medida correctora.** Actualizar la política y el aviso legal (acción A-01 del plan). Requiere saber
  el proveedor de email (DF-03).
- **Responsable de la decisión.** Titular.
- **Condición para darlo por resuelto.** La política publicada menciona Google, el proveedor real de
  email, la tabla de almacenamiento del apartado 5 de la auditoría y 30 minutos de sesión; una prueba
  automática comprueba que la duración citada coincide con `access_token_minutes`, y se ha leído la
  versión publicada en GitHub Pages.

## R-02. Pérdida de progreso por escrituras simultáneas

- **Situación detectada.** El fallo P0 de la auditoría técnica (AUD-001: subir antes de la fusión
  inicial) está corregido en `main`. Queda otro caso: con dos pestañas o dos dispositivos abiertos a la
  vez, cada uno sube su documento entero y el último que guarda borra lo del otro.
- **Norma afectada.** RGPD art. 5.1.f (integridad) y art. 32.1.b.
- **Probabilidad.** Media: es habitual tener la web abierta en el móvil y en el ordenador.
- **Impacto.** Medio: pérdida de progreso del propio usuario, sin exposición a terceros.
- **Evidencia.** `frontend/js/sync-gate.js` (corrección de AUD-001); `PUT` sin control de versión en
  `backend/app/routers/pcap.py` y `course_state.py`; PR #77 abierto. Hallazgo LEG-016.
- **Medida correctora.** Revisar y fusionar el PR #77 (versión + 409), que lleva otro hilo (A-02).
- **Responsable de la decisión.** Titular (merge).
- **Condición para darlo por resuelto.** PR #77 en `main`, con la prueba de dos pestañas en verde en la
  CI y la web publicada después del merge.

## R-03. Brechas e incidentes sin preparar

- **Situación detectada.** No hay un procedimiento escrito para detectar, valorar, notificar y registrar
  una brecha. La única copia de seguridad es el historial de Neon, que en el plan gratuito dura 6 horas.
- **Norma afectada.** RGPD arts. 32.1.c, 33 y 34.
- **Probabilidad.** Baja: las medidas técnicas son buenas y no hay datos sensibles.
- **Impacto.** Alto si ocurre: la notificación a la AEPD tiene un plazo de 72 horas y sin procedimiento
  es fácil incumplirlo; un borrado accidental de la base de datos descubierto tarde no se podría
  recuperar.
- **Evidencia.** Ningún documento de incidentes en el repositorio (búsqueda en `docs/` y `SECURITY.md`);
  historial de Neon (F-17). Hallazgos LEG-017, LEG-019.
- **Medida correctora.** Procedimiento de incidentes con registro (A-08) y copia periódica cifrada de la
  base de datos fuera de Neon, con prueba de restauración (A-09).
- **Responsable de la decisión.** Titular.
- **Condición para darlo por resuelto.** Procedimiento en `docs/`, registro de incidentes creado (aunque
  esté vacío), y una restauración de prueba documentada en una base de datos local.

## R-04. Encargados y transferencias sin evidencia

- **Situación detectada.** La política afirma que Render y Neon son encargados con acuerdos que incluyen
  cláusulas tipo. Para Render es coherente con su DPA público, que se incorpora a sus condiciones. Para
  Neon, la página actual remite al contrato marco de Databricks y no muestra las cláusulas. El
  proveedor de email es desconocido. No hay copia de ningún contrato.
- **Norma afectada.** RGPD arts. 28.3 y 44-46.
- **Probabilidad.** Media.
- **Impacto.** Medio.
- **Evidencia.** F-16 (Render DPA, 19/12/2024), F-17 (Neon, 14/10/2026); `render.yaml`. Hallazgos
  LEG-010 a LEG-013.
- **Medida correctora.** Descargar y guardar los DPA y listas de subencargados, anotar la fecha de
  aceptación y ajustar la política a lo que digan (A-03).
- **Responsable de la decisión.** Titular.
- **Condición para darlo por resuelto.** Copias guardadas fuera del repositorio público, referencia en
  el registro de actividades y frase de la política coherente con cada contrato.

## R-05. Comercializar sin el marco legal

- **Situación detectada.** Hay planes de ingresos (Pack PCAP, donaciones, PR #63 abierto). Hoy no hay
  datos completos del prestador, ni condiciones de contratación, ni información precontractual, ni
  flujo de desistimiento, ni facturación.
- **Norma afectada.** LSSI arts. 10 y 23-28; TRLCU (información precontractual, desistimiento,
  conformidad); Directivas 2019/770 y 2023/2673; Ley 7/1998; normativa de IVA y facturación.
- **Probabilidad.** Alta si se empieza a cobrar sin preparar esto; nula mientras sea gratuito.
- **Impacto.** Alto: contratos impugnables, devoluciones, sanciones de consumo y problemas fiscales.
- **Evidencia.** Ausencia de pagos en `main`; `frontend/aviso-legal.html` sin domicilio ni NIF.
  Hallazgos LEG-025, LEG-028 a LEG-033, LEG-049.
- **Medida correctora.** Bloque P1-C del plan (A-10 a A-15), con revisión de un abogado y una asesoría
  fiscal.
- **Responsable de la decisión.** Titular, con abogado y asesoría.
- **Condición para darlo por resuelto.** Ningún cobro antes de que exista cada documento del bloque
  P1-C, revisado por un profesional, y de que el flujo de compra pase una prueba que compruebe la
  información previa, el consentimiento para el acceso inmediato y la confirmación en soporte duradero.

## R-06. Menores sin edad mínima

- **Situación detectada.** Cualquiera puede crear una cuenta. No hay condiciones de uso ni edad mínima.
- **Norma afectada.** RGPD art. 8 y LOPDGDD art. 7 (de forma indirecta: regulan el consentimiento);
  Código Civil (capacidad para contratar, no consultado).
- **Probabilidad.** Media: el público es sobre todo adulto, pero hay alumnado de FP menor de edad.
- **Impacto.** Medio.
- **Evidencia.** `frontend/index.html` (formularios de registro), `backend/app/schemas.py`. Hallazgo
  LEG-022.
- **Medida correctora.** Condiciones de uso con edad mínima justificada (14 años propuesto) y apartado
  de la política comprensible para menores (A-07).
- **Responsable de la decisión.** Titular (edad y público objetivo, DF-06).
- **Condición para darlo por resuelto.** Condiciones publicadas y enlazadas desde el registro; el
  formulario informa de la edad mínima.

## R-07. Licencia del contenido

- **Situación detectada.** El `LICENSE` MIT cubre todo el repositorio, incluido el temario.
- **Norma afectada.** TRLPI (titularidad y cesión de derechos).
- **Probabilidad.** Alta si se comercializa el mismo contenido.
- **Impacto.** Alto en lo económico: cualquiera podría copiar y vender el temario legalmente.
- **Evidencia.** `LICENSE`; `docs/AUDITORIA-Y-LICENCIAS.md` P1. Hallazgo LEG-036.
- **Medida correctora.** Elegir licencia para el contenido (por ejemplo, separar código MIT y contenido
  con otra licencia) antes de vender (A-15). Lo ya publicado bajo MIT sigue disponible bajo MIT.
- **Responsable de la decisión.** Titular, con abogado.
- **Condición para darlo por resuelto.** `LICENSE` y README indican qué licencia tiene cada parte.

## R-08. Reintroducir IA sin revisión

- **Situación detectada.** El PR #65 (abierto) recupera un tutor que puede usar OpenAI. Enviaría código
  y preguntas del alumno a un tercero de EE. UU.
- **Norma afectada.** RIA art. 50.1; RGPD arts. 13, 28 y 44-46.
- **Probabilidad.** Media.
- **Impacto.** Medio.
- **Evidencia.** PR #65; `frontend/js/assistant.js:1-2` (hoy sin IA). Hallazgo LEG-043.
- **Medida correctora.** Antes del merge: aviso de interacción con IA, DPA de OpenAI, política
  actualizada, minimización de lo enviado y revisión de esta auditoría (A-16).
- **Responsable de la decisión.** Titular.
- **Condición para darlo por resuelto.** El PR incluye esas piezas y una prueba que comprueba el aviso
  de IA visible.

## R-09. Conservación indefinida

- **Situación detectada.** Las cuentas y el código enviado se conservan sin límite mientras exista la
  cuenta, aunque nadie la use en años. La política no da plazos para logs ni copias.
- **Norma afectada.** RGPD arts. 5.1.e y 13.2.a.
- **Probabilidad.** Alta (es el comportamiento actual).
- **Impacto.** Bajo.
- **Evidencia.** `backend/app/models.py` (sin fecha de último acceso ni purga). Hallazgo LEG-005.
- **Medida correctora.** Decidir un plazo para cuentas inactivas (por ejemplo, aviso por email y borrado
  tras un periodo), y explicar los plazos de Neon y Render (A-05).
- **Responsable de la decisión.** Titular.
- **Condición para darlo por resuelto.** Plazos en la política y, si se decide purgar, tarea programada
  con prueba automática.

## R-10. Afirmaciones que no se pueden demostrar

- **Situación detectada.** El README afirma «accesibilidad WCAG 2.1 AA» sin auditoría manual; la
  política dice que los datos se borran «de inmediato» (hay un historial de 6 h en Neon) y que Neon
  aplica cláusulas tipo (no comprobado).
- **Norma afectada.** RGPD art. 5.1.a (lealtad y transparencia); Ley 3/1991 si se usara en publicidad.
- **Probabilidad.** Media.
- **Impacto.** Bajo.
- **Evidencia.** `README.md`; `privacidad.html` §3 y §4. Hallazgos LEG-007, LEG-013, LEG-035.
- **Medida correctora.** Reformular con lo que se puede demostrar (A-01, A-18).
- **Responsable de la decisión.** Titular.
- **Condición para darlo por resuelto.** Cada afirmación pública tiene una evidencia enlazable.

## R-11. Marcas y certificado

- **Situación detectada.** Uso de «Python» y «PCAP» y un certificado «Se certifica que…». Hay descargo
  en el aviso legal y en el propio certificado.
- **Norma afectada.** Ley 17/2001 de Marcas; Ley 3/1991 de Competencia Desleal.
- **Probabilidad.** Baja mientras sea gratuito.
- **Impacto.** Medio si se vende un producto con esas marcas en el nombre.
- **Evidencia.** `frontend/aviso-legal.html`; `frontend/js/certificate.js:78-79`. Hallazgos LEG-041,
  LEG-051.
- **Medida correctora.** Revisar la política de marcas de la PSF y de Python Institute antes de vender
  (A-19).
- **Responsable de la decisión.** Titular, con abogado si se usa en el nombre comercial.
- **Condición para darlo por resuelto.** Revisión documentada y nombres de productos que no sugieran
  afiliación.
