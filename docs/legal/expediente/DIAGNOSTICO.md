# Diagnóstico jurídico · Python Learning Dashboard

| Campo | Valor |
|---|---|
| Estado | **BORRADOR**: generado por IA, sin revisión humana ni jurídica |
| Versión | 0.1 · 19/10/2026 |
| Producto analizado | Rama `main`, commit `730d78d` (repositorio `Marbi8891/python-learning-dashboard`) |
| Jurisdicción | **Hipótesis provisional: España y UE.** Se basa en que el aviso legal declara «legislación española (LSSI-CE y RGPD)» y en que el titular es una persona física con contacto en España. Falta que el titular lo confirme. |
| Agente | LegalDocs AI ([prompt maestro](../PROMPT_MAESTRO.md) v1.0 + sección 24) |
| Próxima revisión | Al activar el envío de emails, al cambiar el proveedor del tutor o, como tarde, el 19/04/2027 |

> Este documento no es asesoramiento jurídico ni certifica el cumplimiento de ninguna norma. Ningún
> documento publicado se ha modificado: las propuestas están en [`borradores/`](borradores/).

## 1. Resumen ejecutivo

El proyecto está mejor documentado de lo habitual en un proyecto educativo: ya tiene política de
privacidad, aviso legal, licencia MIT, exportación de datos en JSON, borrado de cuenta y una política de
seguridad. Pero la política de privacidad **ya no describe el producto real** en tres puntos, y eso es
lo prioritario:

1. **El inicio de sesión con Google no aparece en la política.** El script de Google se carga en cada
   visita a la web, aunque la persona no inicie sesión (`frontend/index.html:50`). La política dice
   que solo hay terceros como GitHub Pages, jsDelivr, Render y Neon.
2. **Quien se registra con Google no puede borrar su cuenta desde la web.** Su cuenta recibe una
   contraseña aleatoria que nunca conoce (`backend/app/routers/auth.py:82`), y borrar la cuenta exige
   la contraseña (`backend/app/routers/account.py:124`). Sin email de recuperación activado no hay forma
   de autoservicio. La política dice «Supresión: desde Tu cuenta → Eliminar mi cuenta».
3. **Hay contradicciones menores:** la política describe GoatCounter como activo pero está desactivado
   (`frontend/config.js`: `goatcounter: ""`), y dice a la vez que la sesión dura 30 minutos (§5) y una
   hora (§7). El código usa 30 minutos (`backend/app/config.py:32`).

Además faltan unas **condiciones de uso** (edad mínima, uso aceptable, tutor, ausencia de garantía) y un
**registro de actividades de tratamiento** sencillo, que con la información disponible parece exigible.
El Reglamento de IA no parece imponer más que la transparencia del art. 50.1, y el tutor ya indica el
origen de cada respuesta.

Nada de esto indica un riesgo alto. Es un proyecto gratuito, sin publicidad ni datos sensibles. Las
correcciones son baratas y no requieren servicios de pago.

## 2. Hechos verificados

«Revisado en el código disponible» significa leído en `main@730d78d`, sin ejecutar pruebas ni consultar
producción. La web publicada se despliega desde `main` (`.github/workflows/pages.yml`, según CLAUDE.md),
pero no se ha comprobado de forma independiente que coincida.

| # | Hecho | Evidencia | Tipo |
|---|---|---|---|
| H1 | El titular es una persona física, Mrabeh Fathi Boussayff, con contacto `mrabehfathiprofesional@gmail.com` | `frontend/aviso-legal.html`, `frontend/privacidad.html` §1, `LICENSE` | Declarado en documentos del repo |
| H2 | Es gratuito, sin publicidad ni pagos | Aviso legal «Objeto»; en el código no hay pasarelas de pago | Declarado + revisado en el código |
| H3 | Datos de cuenta: email, nombre, hash Argon2id y fecha de aceptación de la privacidad | `backend/app/models.py:71`, `backend/app/routers/auth.py:113-125` | Revisado en el código |
| H4 | Hay inicio de sesión con Google: el servidor verifica el ID token y crea la cuenta con el email y el nombre de Google | `backend/app/routers/auth.py:37-107`, `frontend/config.js` (`googleClientId`) | Revisado en el código |
| H5 | El script `https://accounts.google.com/gsi/client` se carga en todas las visitas, no solo al abrir el inicio de sesión | `frontend/index.html:50`, CSP en `frontend/index.html:8` | Revisado en el código |
| H6 | Las cuentas de Google reciben una contraseña aleatoria, y borrar la cuenta o cambiar la contraseña exige la actual | `auth.py:82`, `account.py:63` y `124` | Revisado en el código |
| H7 | La recuperación de contraseña solo envía emails si hay `BREVO_API_KEY` o `SMTP_HOST`. `render.yaml` prevé Brevo porque Render gratis bloquea SMTP | `backend/app/mailer.py:33-64`, `render.yaml:26-35` | Revisado en el código. Si está configurado en Render: **no verificado** |
| H8 | La sesión dura 30 minutos por defecto | `backend/app/config.py:32`; la política dice 30 min (§5) y «a la hora» (§7); un comentario de Android dice 1 hora (`android/.../Sync.kt:43`) | Revisado en el código; contradicción documental |
| H9 | La analítica GoatCounter está desactivada | `frontend/config.js` (`goatcounter: ""`), `frontend/js/analytics.js:6` | Revisado en el código |
| H10 | El tutor está desactivado por defecto, puede usar `ollama`, `anthropic` o `mock`, y cada respuesta indica su origen; la respuesta simulada dice «Tutor sin IA» | `backend/app/config.py:59-84`, `backend/app/a2a/providers/mock.py:11-14`, `frontend/js/tutor.js:91-95` | Revisado en el código |
| H11 | En producción el tutor usa el modelo simulado (`A2A_MODEL_PROVIDER=mock`) | Memoria del proyecto (decisión del 7/10) | Declarado por el usuario, **no verificado** |
| H12 | Render (región Frankfurt, plan gratis) y Neon (UE) | `render.yaml:10-13`, `docs/DEPLOY.md` | Revisado en la configuración. Ningún contrato consultado |
| H13 | Hay exportación JSON y borrado de cuenta con supresión explícita de todas las tablas del usuario | `account.py:86-112` y `115-143` | Revisado en el código, sin ejecutar pruebas |
| H14 | Una cookie técnica `__Host-pld_session`; `localStorage` para progreso y preferencias | `backend/app/session_cookie.py`, `privacidad.html` §5 | Revisado en parte |
| H15 | No hay edad mínima en el registro ni condiciones de uso | Búsqueda en `frontend/index.html`, `frontend/js/`, `backend/app/schemas.py` | Revisado en el código |
| H16 | Licencia MIT; fuentes y highlight.js alojados con sus licencias | `LICENSE`, `frontend/fonts/LICENSE-*.txt`, `frontend/vendor/highlight/LICENSE` | Revisado en el código; contenido de las licencias no analizado |
| H17 | Hay política de divulgación de vulnerabilidades | `SECURITY.md` | Revisado en el repo |

## 3. Hipótesis y datos pendientes

Solo las preguntas que cambian el resultado:

| # | Pregunta para el titular | Por qué importa |
|---|---|---|
| P1 | ¿Confirmas España como país de residencia y la web dirigida sobre todo a España? | Decide LOPDGDD y LSSI. Hoy es hipótesis. |
| P2 | ¿Hay o habrá ingresos (donaciones, anuncios, cursos de pago, uso como portfolio para clientes)? | La LSSI se aplica a servicios que son «actividad económica». Si no lo son, el art. 10 LSSI (NIF, etc.) podría no aplicarse. |
| P3 | ¿Está configurado `BREVO_API_KEY` o `SMTP_HOST` en Render? ¿Con qué proveedor? | Decide si hay un encargado más (Brevo/Gmail) y si los usuarios de Google pueden recuperar la contraseña. |
| P4 | ¿Sigue el tutor en `mock` en producción? ¿Piensas usar Ollama u otro modelo allí? | Con `mock` no hay sistema de IA en producción; con un modelo sí se aplica el art. 50.1 RIA. |
| P5 | ¿Pueden registrarse menores? ¿A qué edad apuntas (alumnado de DAW, adultos)? | Decide la edad mínima de las condiciones de uso. |
| P6 | ¿La app Android está publicada en Google Play? | Si lo está, Google exige su propia ficha de seguridad de datos y una URL de privacidad. |
| P7 | ¿Has aceptado el DPA de Render y de Neon en sus paneles, o solo sus condiciones generales? | La política afirma que actúan como encargados «según sus acuerdos de tratamiento de datos»; no se ha visto ningún contrato. |

## 4. Obligaciones potenciales

Leyenda: **Ley** = exigencia expresa; **Interp.** = interpretación razonada; **Recom.** = recomendación
preventiva; **ND** = no determinable con lo disponible.

| Id | Obligación | Hecho que la activa | Tipo | Estado de la conclusión |
|---|---|---|---|---|
| O1 | Informar de identidad, finalidades, bases, destinatarios, transferencias, plazos y derechos (RGPD art. 13.1-13.2) | Cuentas, sesiones, tutor y Google | Ley | **VERIFICADA** la norma; el cumplimiento falla en los destinatarios (Google, H4-H5) |
| O2 | Facilitar el ejercicio de derechos (RGPD art. 12.2) y la supresión (art. 17) | H6: Google sin autoservicio de borrado | Interp. | **CONDICIONADA**: el derecho se puede ejercer por email, pero la política promete otra cosa |
| O3 | Contrato de encargado con Render, Neon, Google (si aplica) y el proveedor de email (RGPD art. 28.3) | H12, H7 | Ley | **CONDICIONADA** a P7 y P3; art. 28.3 no releído en esta sesión |
| O4 | Transferencias a EE. UU. con garantías (RGPD cap. V) | Proveedores con matriz en EE. UU. | Ley | **CONDICIONADA**: el Marco de Privacidad UE-EE. UU. sigue vigente (TG 3/9/2025), pero hay recurso ante el TJUE pendiente |
| O5 | Registro de actividades de tratamiento (RGPD art. 30) | Tratamiento continuo de cuentas | Interp. | **CONDICIONADA**: la exención del art. 30.5 cae si el tratamiento «no es ocasional» (consultado). Depende de que el RGPD se aplique, es decir, de que no sea actividad doméstica (art. 2.2.c). Una web pública con cuentas de terceros difícilmente lo es. |
| O6 | Consentimiento para el almacenamiento no técnico en el navegador (LSSI art. 22.2) | Script de Google en todas las visitas; GoatCounter si se activa | Interp. | **INCIERTA** para Google (ver D1); **NO APLICABLE** hoy a GoatCounter (desactivado) |
| O7 | Información general del prestador (LSSI art. 10.1) | Web pública | Ley | **CONDICIONADA** a P2 (ámbito «actividad económica» del Anexo LSSI, no releído en esta sesión) |
| O8 | Edad de consentimiento de menores (LOPDGDD art. 7, RGPD art. 8) | H15 | Ley | **NO APLICABLE directamente**: la base es el contrato (6.1.b), no el consentimiento. La capacidad del menor para contratar es una duda civil (D3). |
| O9 | Informar de que se interactúa con una IA (RIA art. 50.1) | Tutor con modelo | Ley | **CONDICIONADA** a P4: hoy, con `mock`, no hay sistema de IA en producción. Con modelo, el diseño de H10 parece cumplirlo (no probado en ejecución). |
| O10 | Alto riesgo en educación (RIA anexo III, punto 3) | Tutor que adapta el nivel | Interp. | **CONDICIONADA**: probablemente no aplica. El nivel lo decide un plan determinista (ADR-0036), no es una institución educativa y la fecha se ha aplazado al 2/12/2027 (Reglamento 2026/1744). El texto del anexo III no se ha releído en esta sesión. |
| O11 | Atribución en licencias de terceros | H16 | Ley (contractual) | **PENDIENTE**: revisar Pyodide (CDN) y las licencias de fuentes |

## 5. Dudas detectadas (protocolo de duda)

**D1. ¿Cargar el script de Google en cada visita requiere consentimiento?**
- Falta saber qué almacena o lee Google en el dispositivo al cargar el script, antes del clic.
- LSSI art. 22.2 exime lo «estrictamente necesario» para un servicio «expresamente solicitado por el
  destinatario» (BOE, consultado el 19/10/2026). Quien solo visita la web no ha pedido iniciar sesión.
- La documentación de Google dice que usa FedCM como alternativa a las cookies de terceros y que los
  datos de Sign in with Google no se usan para anuncios. No precisa qué ocurre al cargar el script.
- **Estado: INCIERTA.** Medida prudente y barata: **cargar el script solo al abrir el diálogo de
  inicio de sesión**. Así la excepción técnica es defendible y Google deja de recibir la IP de cada
  visitante. Es una recomendación preventiva, no una obligación confirmada.

**D2. ¿Google es encargado o responsable independiente?**
- En «Sign in with Google» Google trata los datos de su propio usuario para autenticarlo. Lo razonable
  es tratarlo como **tercero o responsable independiente** que comunica datos con permiso del usuario,
  no como encargado. Es una interpretación; no se ha consultado ningún criterio de la AEPD sobre este
  caso concreto. **CONDICIONADA.** En la política basta con identificarlo y enlazar su política.

**D3. Menores.**
- El RGPD (art. 8.1) y la LOPDGDD (art. 7) regulan el **consentimiento** de menores (16 años en el RGPD,
  14 en España). Aquí la base es la ejecución del servicio, así que esos artículos no deciden la edad.
  Sigue abierta la capacidad del menor para aceptar unas condiciones (Código Civil, no consultado).
- **Estado: INCIERTA.** Medida prudente: fijar en las condiciones de uso una **edad mínima de 14 años**
  y pedir la autorización de los padres o tutores por debajo. Es coherente con la LOPDGDD y apenas
  limita a un alumnado de FP. Conviene **revisión profesional** si se quiere dirigir a menores.

**D4. ¿Se aplica la LSSI a un proyecto gratuito sin ingresos?**
- Depende de que sea «actividad económica» (Anexo, letra a). No se ha podido releer el Anexo en esta
  sesión porque el texto consolidado del BOE llegó truncado.
- **Estado: CONDICIONADA** a P2. El aviso legal ya da nombre y email. Mientras no haya ingresos no se
  recomienda publicar el NIF; si llegan, habrá que reevaluarlo.

**D5. Transferencias a EE. UU.**
- El Tribunal General confirmó el 3/9/2025 la decisión de adecuación del Marco UE-EE. UU. (asunto
  Latombe). Hay un recurso ante el TJUE presentado el 31/10/2025 y pendiente (fuentes secundarias). La
  política se apoya en las cláusulas tipo de los DPA, que no se han visto. **CONDICIONADA.**

## 6. Fuentes consultadas

Consultadas el 19/10/2026. «Parcial» significa que la página llegó truncada y solo se leyó lo indicado.

| Fuente | Naturaleza | URL | Qué se verificó |
|---|---|---|---|
| LSSI-CE, Ley 34/2002 (BOE consolidado, act. 23/01/2025) | Ley | https://www.boe.es/buscar/act.php?id=BOE-A-2002-13758 | Art. 10.1 a-g; art. 22.2 y su excepción técnica. **Anexo no leído (truncado)** |
| LOPDGDD, LO 3/2018 (BOE consolidado, act. 27/12/2025) | Ley | https://www.boe.es/buscar/act.php?id=BOE-A-2018-16673 | Art. 7 (menores, 14 años); art. 11 (información por capas) |
| RGPD art. 13 | Ley (texto vía gdpr-info.eu, no oficial) | https://gdpr-info.eu/art-13-gdpr/ · oficial: https://eur-lex.europa.eu/eli/reg/2016/679/oj | Elementos de 13.1 y 13.2. **El texto oficial de EUR-Lex no se pudo leer (truncado)** |
| RGPD arts. 2.2.c, 8.1 y 30.5 | Ley (vía gdpr-info.eu) | https://gdpr-info.eu/art-2-gdpr/ · https://gdpr-info.eu/art-8-gdpr/ · https://gdpr-info.eu/art-30-gdpr/ | Exención doméstica; 16 años y rebaja a 13; condiciones de la exención del registro |
| Reglamento (UE) 2024/1689 (RIA) | Ley | https://eur-lex.europa.eu/eli/reg/2024/1689/oj | Solo metadatos. **Arts. 50 y 113 y anexo III no leídos en el texto oficial (truncado)** |
| Corrección de errores del RIA (DOUE 9/10/2025) | Ley | https://boe.es/doue/2025/90802/L00001-00002.pdf | Solo cambios terminológicos |
| Reglamento (UE) 2026/1744 «Ómnibus digital sobre IA» | Ley | https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32026R1744 | Fecha 8/7/2026; anexo III aplazado al 2/12/2027 (cdo. 40); periodo transitorio de 4 meses para el art. 50.2 (cdo. 38); modifica el art. 50.7. **Lectura parcial**: el texto visible no cambia el art. 50.1 |
| Comisión Europea, FAQ sobre el art. 50 RIA (act. 24/7/2026) | Guía de autoridad | https://digital-strategy.ec.europa.eu/en/faqs/transparency-obligations-under-article-50-ai-act | Art. 50.1 obliga al proveedor y se aplica desde el 2/8/2026; excepción «obvio» de interpretación estricta |
| Google Identity Services | Proveedor | https://developers.google.com/identity/gsi | FedCM; «no se usa para anuncios»; nada concreto sobre cookies al cargar el script |
| Sentencia Latombe y recurso | Secundaria | https://www.wilmerhale.com/en/insights/blogs/wilmerhale-privacy-and-cybersecurity-law-blog/20251201-european-court-of-justice-to-review-challenge-to-eu-us-data-privacy-framework | Fechas 3/9/2025 y 31/10/2025; número de asunto **no verificado** (consultar CURIA) |
| ActuIA sobre el Reglamento 2026/1744 | Secundaria | https://www.actuia.com/en/news/ai-act-obligations-in-force-and-delays-under-omnibus-2026-1744/ | Solo para localizar el texto oficial |

**No consultadas** (falta de acceso o de tiempo): guía de cookies de la AEPD (la página no cargó), DPA
de Render, Neon, Google y Brevo, Código Civil sobre la capacidad de los menores y criterios de la AEPD
sobre inicio de sesión federado.

## 7. Riesgos y prioridades

| Prioridad | Riesgo | Por qué | Acción |
|---|---|---|---|
| **Alta** | Política inexacta sobre Google (H4-H5) | Falta un destinatario en la información del art. 13; afecta a todos los visitantes | Añadir Google a la política ([borrador](borradores/privacidad-cambios.md)) y cargar el script solo al iniciar sesión |
| **Alta** | Borrado imposible por autoservicio para cuentas de Google (H6) | La política promete un borrado que no funciona para ellas | Corregir el código (borrar con confirmación por Google o escribiendo el email) y, mientras tanto, corregir la política |
| Media | Contradicciones de duración de sesión y de GoatCounter (H8-H9) | Inexactitud, sin daño probable | Corregir los textos |
| Media | Sin condiciones de uso (H15) | Sin edad mínima, uso aceptable ni límites del tutor | [Borrador de condiciones](borradores/condiciones-de-uso.md) |
| Media | Sin registro de actividades (O5) | Probablemente exigible | [Borrador de registro](borradores/registro-actividades.md) |
| Baja | DPA no comprobados (P7) | La afirmación de la política no tiene evidencia | Descargar o aceptar los DPA y guardarlos fuera del repo |
| Baja | Proveedor de email por decidir (P3) | Encargado nuevo cuando se active | Añadirlo a la política al activarlo |

## 8. Próximas acciones

1. **El titular** responde P1-P7. Basta una línea por pregunta.
2. **El titular** decide si se corrige el código: cargar Google solo bajo demanda y permitir el borrado
   de cuentas de Google. Cada cambio se haría en su propio PR, con pruebas y con el equipo AppSec.
3. Con las respuestas, LegalDocs AI pasa los borradores a **REVISIÓN PENDIENTE**.
4. **El titular** revisa el texto final y lo aprueba. Solo entonces se sustituye `privacidad.html` y se
   publica `condiciones.html` en un PR que fusiona él mismo.
5. Revisión profesional recomendada solo si se dirige el servicio a menores de 14 años o si llegan
   ingresos o un proveedor de IA externo.

Matriz de trazabilidad completa: [MATRIZ.md](MATRIZ.md).
