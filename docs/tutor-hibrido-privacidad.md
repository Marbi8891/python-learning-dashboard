# Tutor híbrido: modalidad «IA avanzada» con OpenAI. Análisis previo a la activación

| Campo | Valor |
|---|---|
| Estado | **BORRADOR** (no aprobado; no se publica) |
| Versión | 0.1 · 20/10/2026 |
| Commit analizado | Rama `claude/tutor-hibrido-3s4dln`, `HEAD a0c6dac` **más cambios sin confirmar** en el árbol de trabajo (`openai_provider.py` con `MAX_RETRIES = 0`, `docs/tutor-hibrido.md` nuevo). Las líneas citadas corresponden a ese estado del 20/10/2026 |
| Jurisdicción | España y UE, **como hipótesis** (sin confirmar por el titular, P1) |
| Estado técnico | La modalidad está **desactivada** (`A2A_ADVANCED_PROVIDER=none` por defecto, `backend/app/config.py:89`). Según el encargo y `docs/tutor-hibrido.md:11`, nunca se ha llamado a OpenAI. No se ha consultado producción |
| Documentos afectados | `frontend/privacidad.html` (no se modifica aquí), registro de actividades del tratamiento (fila nueva, ver §3.2) |
| Quién decide | El titular. LegalDocs AI no es abogado; esto no es asesoramiento jurídico ni certifica cumplimiento |

> Recuperado el 29/10/2026 junto con el tutor. El expediente legal donde vivía (`docs/legal/`) se
> retiró en el PR #62, así que las referencias a sus apartados (P1-P7, §20, §24) son de esa versión;
> el original está en el historial de Git (commit `aebaed8`). Las líneas de código citadas también.

> Nada de este documento afirma que la aplicación cumpla el RGPD, la LOPDGDD ni el Reglamento de IA.
> Describe lo que hace el código, lo que dicen las fuentes leídas y lo que queda por decidir.

---

## 1. Datos personales, finalidad, base jurídica y conservación

### 1.1 Qué sale hacia OpenAI (hechos del código)

Solo cuando el backend tiene `A2A_ADVANCED_PROVIDER=openai` con clave y modelo
(`backend/app/a2a/server.py:139-167`) y el alumno elige la modalidad «IA avanzada» (el servidor la
valida, `backend/app/a2a/executors/python_tutor.py:286-292`).

| Dato | Dónde | Evidencia |
|---|---|---|
| Instrucciones fijas del tutor (`SYSTEM_PROMPT`); no contienen datos del alumno | `python_tutor.py:194`, `openai_provider.py:96` (`instructions`) | Revisado en el código disponible |
| Pregunta del alumno (máx. 4 000 caracteres) | `python_tutor.py:65`, `:949` | Revisado en el código disponible |
| Código que pega el alumno (máx. 20 000) y mensaje de error (máx. 4 000) | `python_tutor.py:66-67`, `:950-956` | Revisado en el código disponible |
| Tope conjunto de pregunta + código + error en modo avanzado: 6 000 caracteres por defecto | `config.py:101`, `executors/python_tutor.py:122-123`, `:291` | Revisado en el código disponible |
| Nivel estimado del alumno («inicial», «intermedio», «avanzado»), su base y evidencias | `python_tutor.py:902-909` | Revisado en el código disponible |
| Conceptos comprobados y «hipótesis de dificultad» de los conceptos de esa pregunta | `python_tutor.py:962-981` | Revisado en el código disponible |
| Lección elegida: módulo, título, enunciado, si está superada y nº de intentos (y fallidos) | `python_tutor.py:918-929` | Revisado en el código disponible |
| Extractos de los **3 últimos turnos** de la conversación: pregunta del alumno (≤240 car.) **y respuesta del tutor** (≤480 car.) | `python_tutor.py:68`, `:983-990`; `conversation.py:19-21` | Revisado en el código disponible |
| Guía preparada por el tutor (contenido del curso y análisis) | `python_tutor.py:957-959` | Revisado en el código disponible |

**Qué no se envía** (revisado en el código disponible): email, nombre, id de usuario, cookies ni
token; tampoco los campos `user` o `safety_identifier` de la API. Los únicos parámetros de la llamada
son `model`, `instructions`, `input`, `max_output_tokens`, `store=False` y, opcionalmente,
`reasoning` (`openai_provider.py:93-101`). La IP que verá OpenAI será la del servidor (Render), no la
del alumno (interpretación técnica razonada; no comprobado mediante una prueba ejecutada).

**Por qué siguen siendo datos personales (interpretación razonada).** Aunque no se envíen
identificadores directos, el texto libre (pregunta, código, error) puede contener nombres, correos,
rutas de usuario del sistema operativo (`C:\Users\<nombre>\...` en un traceback) u otros datos que el
alumno escriba. Además, el titular puede vincular cada petición a una cuenta (la reserva de cuota
usa el `user_id`, y el log guarda el identificador de petición de OpenAI con hora,
`openai_provider.py:174-187`). Por eso conviene tratar el envío como tratamiento de datos personales
seudonimizados, no como datos anónimos. El aviso «No incluyas datos personales»
(`frontend/js/tutor.js:165`) reduce el riesgo pero no lo elimina.

**Datos sensibles y menores.** El tutor no pide categorías especiales (art. 9 RGPD), pero el texto
libre podría contenerlas de forma accidental. La edad del público sigue sin resolver (P5).

### 1.2 Qué se guarda en la aplicación

| Dato | Dónde y cuánto | Evidencia |
|---|---|---|
| Recuento por usuario, día (UTC) y modalidad (`free`/`advanced`): nº de consultas y tokens de entrada y salida que informa el proveedor. Sin preguntas, respuestas ni código | Tabla `tutor_usage` (`backend/app/models.py:171-189`; servicio `backend/app/services/tutor_usage.py`). **Sin purga automática**: no se ha encontrado ningún borrado periódico; se conserva hasta que se borra la cuenta | Revisado en el código disponible |
| Incluida en la exportación de la cuenta | `backend/app/routers/account.py:114-127` | Revisado en el código disponible |
| Borrada al eliminar la cuenta | `account.py:172-181` (borrado explícito, más `ON DELETE CASCADE` en `models.py:181-183`) | Revisado en el código disponible |
| Conversación (extractos) en memoria del proceso: 6 turnos, 2 h sin uso, se pierde al reiniciar | `backend/app/a2a/conversation.py:1-24` | Revisado en el código disponible |
| Log por llamada: proveedor, modelo, estado, tokens, id de petición de OpenAI y duración, sin contenido | `openai_provider.py:174-187` | Revisado en el código disponible. Plazo de conservación de los logs en Render: **no verificado** (ya pendiente en T2) |

### 1.3 Finalidad y base jurídica posible

- **Finalidad:** generar, a petición del alumno, una respuesta del tutor con un modelo de OpenAI; y
  controlar el coste y el uso (cuotas diarias por usuario y totales, `config.py:99-100`).
- **Base jurídica (interpretación razonada, estado CONDICIONADA):**
  - Respuesta del tutor: **ejecución del contrato / servicio solicitado (art. 6.1.b RGPD)**, como
    la fila 6 del registro, porque el alumno elige expresamente la modalidad y el envío es necesario
    para darla. Alternativa que algunos responsables usan: **consentimiento (6.1.a)**, que exigiría
    poder retirarlo y que fuera libre (lo es: el modo gratuito sigue disponible sin OpenAI). Elegir
    una u otra es decisión del titular; si el público incluye menores de 14 años (P5) y se optara por
    consentimiento, entra el art. 7 LOPDGDD y el art. 8 RGPD.
  - Contabilidad `tutor_usage`: **interés legítimo (6.1.f)** en limitar el gasto y prevenir abusos,
    o necesidad para prestar un servicio con cuota (6.1.b). Si se elige 6.1.f, hay que documentar la
    ponderación.
- **Conservación propuesta (recomendación preventiva, no obligación verificada):** fijar un plazo
  para `tutor_usage` (por ejemplo, 12 meses, o solo los días necesarios para la cuota si no se usa
  para estadística) y aplicarlo en código, en lugar de «hasta borrar la cuenta». El principio de
  limitación del plazo (art. 5.1.e RGPD) no se ha releído en esta sesión.

---

## 2. Tratamiento de datos de OpenAI: qué hay que revisar

Fuentes leídas el **20/10/2026** (páginas de OpenAI; son documentación contractual y técnica del
proveedor, no normas):

| Id | Fuente | URL | Lo leído | Estado |
|---|---|---|---|---|
| F1 | OpenAI Data Processing Addendum (actualizado 1/12/2025, efectivo 1/1/2026) | https://openai.com/policies/data-processing-addendum/ | Clientes del EEE contratan con **OpenAI Ireland Ltd.**; OpenAI actúa como **encargado** («acts as a Data Processor on the Customer's behalf»); el DPA «is incorporated into» el OpenAI Services Agreement y se acepta al usar los servicios, con un enlace para firmar un DPA aparte; transferencias fuera del EEE con **cláusulas contractuales tipo** o decisión de adecuación (art. 45); lista de subencargados en platform.openai.com/subprocessors con 30 días para oponerse; devolución o borrado al terminar el contrato | Leída mediante un resumen automático de la página; no se ha leído el PDF firmado ni las CCT anexas |
| F2 | Data controls in the OpenAI platform («Your data») | https://developers.openai.com/api/docs/guides/your-data | Los datos de la API **no se usan para entrenar** por defecto salvo opt-in; registros de vigilancia de abusos **hasta 30 días** salvo obligación legal; con `store=true` el estado de la aplicación de Responses se guarda 30 días, con `store=false` en general no; Zero Data Retention (ZDR) para `/v1/responses` previa aprobación de OpenAI; residencia de datos en Europa con `eu.api.openai.com`, que requiere Modified Abuse Monitoring o ZDR | **Truncada**: se leyeron los primeros 100 000 de 111 225 caracteres |
| F3 | Enterprise privacy at OpenAI (actualizado 8/1/2026) | https://openai.com/enterprise-privacy/ | Entradas y salidas de la API conservadas **hasta 30 días** para prestar el servicio e identificar abusos; sin entrenamiento por defecto desde el 1/3/2023; DPA disponible mediante formulario | Leída mediante resumen automático |
| F4 | Lista de subencargados | https://platform.openai.com/subprocessors | La página no devolvió contenido legible | **No verificado** |

### 2.1 Puntos de revisión

| # | Cuestión | Qué dice la fuente | Hecho del proyecto | Estado | Alternativa prudente |
|---|---|---|---|---|---|
| R1 | ¿OpenAI es encargado (art. 28 RGPD)? | F1: sí, con OpenAI Ireland Ltd. para clientes del EEE | El titular contrataría con una cuenta personal o de organización: **no se sabe** qué entidad figura en su cuenta ni si el país de facturación es España | CONDICIONADA | Comprobar en la cuenta que la entidad es OpenAI Ireland Ltd.; descargar o firmar el DPA y guardarlo fuera del repositorio con la fecha |
| R2 | ¿El contrato contiene lo que exige el art. 28.3? | F1 parece cubrirlo (instrucciones, subencargados, borrado) | Art. 28.3 no releído en esta sesión | NO DETERMINABLE sin leer el DPA completo | Lectura del DPA completo por el titular o un profesional |
| R3 | Transferencia internacional | F1: CCT o adecuación. F1 no menciona el Marco de Privacidad de Datos UE-EE. UU.; la certificación de OpenAI en ese marco **no verificada** | El código llama a `https://api.openai.com/v1` (`openai_provider.py:44`), el endpoint global, no el europeo; el destino está fijado en código | CONDICIONADA | Contar con que hay transferencia a EE. UU. (y a los subencargados que haya) cubierta por CCT del DPA; vigilar el recurso ante el TJUE ya anotado en T5. Si se quiere evitarla, valorar `eu.api.openai.com` (exige aprobación de OpenAI y un cambio de código que haría el equipo de desarrollo) |
| R4 | Retención en OpenAI | F2/F3: hasta 30 días para vigilancia de abusos aunque se use `store=false`; ZDR solo con aprobación | `store=False` en `openai_provider.py:99` evita el almacenamiento del estado de la aplicación, **no** la retención por abuso | VERIFICADA como descripción documental del proveedor; no verificado de forma independiente que OpenAI lo aplique | La política debe decir «hasta 30 días según OpenAI», no «OpenAI no guarda nada». Solicitar ZDR solo si se justifica |
| R5 | Uso para entrenamiento | F2/F3: no por defecto en la API | Depende de que nadie active la compartición de datos en la configuración de la organización de OpenAI | CONDICIONADA | Comprobar en el panel que la opción de compartir datos para mejorar modelos está desactivada y guardar captura con fecha |
| R6 | Subencargados | F1 remite a la lista; F4 no se pudo leer | — | NO VERIFICADO | Leer la lista, suscribirse a avisos de cambios |
| R7 | Seguridad (art. 32) | No revisado | Clave como secreto de entorno (`config.py:91`), logs del SDK silenciados (`openai_provider.py:47-54`) | NO DETERMINABLE en lo jurídico | Límite de gasto en la cuenta de OpenAI; rotación de clave |

---

## 3. Propuestas de texto (BORRADOR, para aprobación del titular)

### 3.1 Párrafo para la política de privacidad (`frontend/privacidad.html`)

> Estado: **BORRADOR**. No publicar hasta resolver la lista del §4. Los marcadores entre corchetes
> deben sustituirse por datos comprobados.

> **Tutor de Python: modalidad «IA avanzada» (opcional)**
>
> El tutor funciona por defecto sin enviar tus consultas a ningún servicio externo de pago. Si eliges
> la modalidad «IA avanzada», para generar la respuesta enviamos a **OpenAI Ireland Ltd.**
> [ENTIDAD POR CONFIRMAR EN LA CUENTA], que actúa como encargado del tratamiento:
>
> - tu pregunta, el código y el mensaje de error que escribas en el tutor;
> - tu nivel estimado en el tema y el estado de los conceptos relacionados con la pregunta;
> - si eliges una lección, su título y enunciado, si la has superado y cuántos intentos llevas;
> - extractos breves de los últimos turnos de esa conversación (tus preguntas y las respuestas del tutor).
>
> No enviamos tu nombre, tu correo ni tu identificador de usuario. Aun así, no escribas datos
> personales en el tutor: lo que escribas se envía tal cual.
>
> **Finalidad y base jurídica:** responder a la consulta que nos pides, como parte del servicio que
> has elegido (art. 6.1.b RGPD) [O BASE ELEGIDA POR EL TITULAR]. Puedes usar siempre la modalidad
> gratuita, que no envía nada a OpenAI.
>
> **Conservación en OpenAI:** le pedimos que no guarde las respuestas (`store=false`). Según su
> documentación, OpenAI puede conservar las peticiones de la API hasta 30 días para vigilar abusos y
> no las usa para entrenar sus modelos [COMPROBAR EN LA CUENTA ANTES DE PUBLICAR].
>
> **Transferencia internacional:** OpenAI puede tratar los datos fuera del Espacio Económico Europeo,
> en particular en Estados Unidos. La transferencia se ampara en [CLÁUSULAS CONTRACTUALES TIPO DEL
> DPA DE OPENAI / OTRO MECANISMO POR CONFIRMAR].
>
> **Lo que guardamos nosotros:** solo cuántas consultas haces al día en cada modalidad y cuántos
> tokens informa OpenAI, para aplicar los límites diarios y controlar el coste. No guardamos tus
> preguntas ni las respuestas. Este recuento aparece en la exportación de tus datos y se borra al
> eliminar la cuenta [O A LOS PLAZO POR DEFINIR SI SE IMPLANTA UNA PURGA]. La conversación se
> mantiene en memoria del servidor como máximo 2 horas sin uso.

### 3.2 Fila para el registro de actividades 

Propuesta de nueva fila (6 bis) o de ampliación de la fila 6. Estado: **BORRADOR**.

| # | Actividad | Finalidad | Interesados | Datos | Base | Destinatarios y encargados | Transferencias | Conservación | Medidas |
|---|---|---|---|---|---|---|---|---|---|
| 6 bis | Tutor Python, modalidad «IA avanzada» | Generar la respuesta del tutor con un modelo externo cuando el alumno lo elige; controlar cuotas y coste | Usuarios registrados que eligen la modalidad | Pregunta, código y error escritos por el alumno; nivel estimado y estado de conceptos; datos de la lección (título, enunciado, superada, nº de intentos); extractos de los 3 últimos turnos. En la app: recuento diario de consultas y tokens por usuario y modalidad | 6.1.b [POR CONFIRMAR]; recuento: 6.1.f o 6.1.b [POR CONFIRMAR] | OpenAI Ireland Ltd. [POR CONFIRMAR], encargado (DPA [FECHA DE ACEPTACIÓN PENDIENTE]); subencargados de OpenAI [NO VERIFICADOS] | EE. UU. y otros según subencargados; CCT del DPA [POR CONFIRMAR] | OpenAI: hasta 30 días para vigilancia de abusos según su documentación (F2, F3); `store=false`. App: conversación en memoria ≤2 h sin uso; `tutor_usage` hasta el borrado de la cuenta [PLAZO POR DEFINIR] | Desactivada por defecto; sin identificadores en la petición; destino fijo; logs sin contenido; tope de caracteres, de tokens y de consultas diarias; aviso al alumno antes de elegir |

### 3.3 Reglamento de IA (Reglamento (UE) 2024/1689): transparencia

- **Qué exige el art. 50.1 (según la guía de la Comisión, leída el 20/10/2026, actualizada el
  24/7/2026,
  https://digital-strategy.ec.europa.eu/en/faqs/transparency-obligations-under-article-50-ai-act):**
  los **proveedores** de sistemas de IA que interactúan directamente con personas deben diseñarlos
  para que estas sepan que interactúan con una IA, salvo que sea obvio; la información debe darse de
  forma clara y distinguible, a más tardar en la primera interacción. El art. 50 se aplica **desde el
  2/8/2026**. El texto oficial del artículo **no se ha leído** en esta sesión (EUR-Lex llegó
  truncado antes del articulado).
- **Reglamento (UE) 2026/1744 (Ómnibus digital sobre IA), leído parcialmente en EUR-Lex
  (https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32026R1744, 20/10/2026):** en lo
  leído (hasta la modificación del art. 75) cambia el art. 50.7 (códigos de prácticas) y prevé un
  periodo transitorio de cuatro meses para el art. 50.2 (marcado de contenido generado) de sistemas
  ya comercializados (cdo. 38). **No se ha encontrado** ningún cambio en el art. 50.1 ni en su fecha,
  pero la parte final del texto (incluido el art. 113 y la entrada en vigor) **no se ha leído**:
  **no verificado**.
- **¿Quién es proveedor aquí? (interpretación razonada, INCIERTA).** OpenAI provee el modelo; el
  titular integra ese modelo en su propio tutor y lo ofrece bajo su nombre, por lo que podría ser
  **proveedor del sistema de IA** (el tutor) y no solo responsable del despliegue. Las definiciones
  del art. 3 no se han releído en esta sesión.
- **Hechos del proyecto:** el selector dice «IA avanzada» y explica que se envían datos a OpenAI
  (`tutor.js:134-165`), y el aviso general dice que puede responder «un modelo de IA» y que «cada
  respuesta indica su origen» (`tutor.js:110-111`). Revisado en el código disponible; **no
  comprobado mediante una prueba ejecutada** en la web ni con el modelo real.
- **Conclusión: CONDICIONADA.** Si el titular es proveedor y el sistema se pone en servicio en la UE,
  el deber del art. 50.1 sería relevante; el diseño actual parece orientado a cumplirlo, pero no se
  ha probado. El art. 50.2 (marcado legible por máquina de texto generado) podría ser aplicable a
  sistemas que generan texto; su alcance para un tutor que muestra la respuesta en pantalla **no se
  ha verificado** (pregunta para revisión profesional). La clasificación de alto riesgo (anexo III.3,
  educación) se mantiene como en T13: probablemente no aplicable mientras el tutor no evalúe ni
  certifique al alumno.

---

## 4. Comprobaciones pendientes antes de habilitar OpenAI en producción

### 4.1 Contradicción detectada (§24.B)

**Aviso del selector frente al código.** El texto del selector (`frontend/js/tutor.js:163-165`) dice
que se envían «tu pregunta, el código y el error que escribas … y tu nivel en el tema». El código
envía además los **extractos de los 3 últimos turnos, incluidas las respuestas del tutor**
(`python_tutor.py:983-990`), el **estado de los conceptos** (`:962-981`) y los **datos de la lección
con el nº de intentos** (`:918-929`). El aviso general (`tutor.js:110-112`) menciona el estado de la
lección, pero no los turnos anteriores. Fuente más fiable: el código (rama analizada). Lo que queda
respaldado: el aviso no es falso, pero es **incompleto**. Propuesta para el equipo de desarrollo (no
la aplica LegalDocs AI): añadir «y extractos de los últimos mensajes de esta conversación y tu
estado en la lección elegida».

`docs/tutor-hibrido.md:164-183` sí describe el envío completo y coincide con el código.

### 4.2 Lista de comprobación

Decisiones y documentos del titular:

- [ ] P1: confirmar España como jurisdicción.
- [ ] P5: decidir la edad mínima. Si puede haber menores de 14 años, **recomendada revisión
      profesional** antes de activar (envío de texto libre de menores a un proveedor de EE. UU.).
- [ ] Elegir la base jurídica (6.1.b o 6.1.a) para la modalidad avanzada y la del recuento.
- [ ] Comprobar en la cuenta de OpenAI la entidad contratante (¿OpenAI Ireland Ltd.?) y el país.
- [ ] Aceptar o firmar el DPA y guardar copia fechada fuera del repositorio (R1, R2).
- [ ] Leer el DPA completo y sus CCT; confirmar el mecanismo de transferencia (R3).
- [ ] Leer la lista de subencargados y suscribirse a sus cambios (R6, F4 no verificada).
- [ ] Confirmar en el panel que la compartición de datos para entrenamiento está desactivada (R5).
- [ ] Decidir si se pide ZDR o residencia en la UE (R3, R4); si es así, encargar el cambio de
      endpoint al equipo de desarrollo.
- [ ] Configurar un límite de gasto en la cuenta de OpenAI.

Documentación:

- [ ] Aprobar y publicar el párrafo del §3.1 en `frontend/privacidad.html` **antes** de activar la
      variable en Render (lo publica la persona con el merge).
- [ ] Añadir la fila 6 bis al registro de actividades (§3.2).
- [ ] Actualizar la matriz: T4 (encargados), T5 (transferencias), T12 (art. 50) con OpenAI.
- [ ] Fijar y documentar el plazo de conservación de `tutor_usage`; si se acorta, pedir la purga en
      código al equipo de desarrollo.
- [ ] Confirmar el plazo de los logs de Render (contienen el id de petición de OpenAI).

Técnicas (al equipo de desarrollo / AppSec, a través de la persona):

- [ ] Completar el aviso del selector (§4.1).
- [ ] Prueba en un entorno controlado con una llamada real: comprobar que la petición solo lleva los
      campos de `openai_provider.py:93-101` y que la respuesta muestra su origen (IA).
- [ ] Valorar si conviene un filtro básico de datos personales evidentes (correos, rutas
      `C:\Users\…`) antes de enviar (recomendación preventiva).
- [ ] Verificar el art. 50 en el texto oficial de EUR-Lex y la parte no leída del Reglamento
      2026/1744 (art. 113 y disposiciones transitorias).

Escalado a revisión profesional (§20): recomendado si hay menores entre el público, si aparecen
ingresos (P2) o si persiste la duda sobre la calificación del titular como proveedor del sistema
de IA y el alcance del art. 50.2.

---

## 5. Limitaciones

- Producción no consultada: no se sabe qué variables tiene Render.
- Páginas de OpenAI leídas mediante resumen automático; F2 truncada (último ~10 % sin leer); F4 sin
  contenido. Ningún contrato firmado visto.
- EUR-Lex: el texto del Reglamento 2024/1689 llegó truncado antes del articulado (arts. 3, 50 y 113
  no leídos); el Reglamento 2026/1744 se leyó hasta el art. 75 aprox.
- Certificación de OpenAI en el Marco de Privacidad de Datos UE-EE. UU.: no verificada.
- RGPD arts. 5, 6, 28 y 44-46 citados por su contenido conocido, **no releídos** en esta sesión.
- El análisis se basa en un árbol de trabajo con cambios sin confirmar; si cambian antes del merge,
  hay que revisar las líneas citadas.
