# Validación del resultado por el que pagaría un estudiante

**Fecha:** 30 de octubre de 2026  
**Estado:** hipótesis y diseño; no se han realizado entrevistas, encuestas ni pruebas de demanda.  
**Alcance:** análisis de lectura del estado visible en main. Sin cambios de código, arquitectura, datos ni despliegue.

**Etiquetas:** **OBSERVADO** = visible en los archivos revisados; **ESTIMACIÓN** = aproximación de esfuerzo o diseño; **HIPÓTESIS** = debe validarse; **UNKNOWN** = no disponible; **VERIFY** = requiere confirmación externa.

> **Limitación importante:** los documentos docs/business/market-validation.md y el resto de documentos comerciales indicados no aparecen en main. No se pueden recuperar sus umbrales. Los umbrales que se proponen aquí son nuevos, provisionales y requieren aprobación del fundador.

## 1. Tres formulaciones del resultado

Son hipótesis para probar, no afirmaciones de eficacia demostrada.

### A. Preparación PCAP

**HIPÓTESIS — mensaje candidato**

> Para personas que preparan el examen PCAP, en un ciclo de estudio de 4 semanas podrás identificar qué bloques del temario te cuestan más y comprobar si mejora tu resultado entre un simulacro inicial y otro final, con un registro de errores y repasos. Mediremos nota, aciertos por bloque, tiempo y cambio en puntos porcentuales. No prometemos aprobar ni que el simulacro prediga la nota oficial.

- **A quién:** candidatos con fecha de examen prevista dentro de las próximas 4–8 semanas.
- **Qué consigue:** una imagen cuantificada de los bloques débiles y comparación pre/post.
- **Tiempo:** 4 semanas, **ESTIMACIÓN**, no duración validada.
- **Medición:** nota sobre 100, acierto por bloque, tiempo y proporción que completa ambos simulacros.
- **No promete:** aprobar, aprobar a la primera, equivalencia psicométrica con el examen oficial ni ahorro económico garantizado.
- **OBSERVADO:** el contenido del repositorio configura PCAP-31-03, 40 preguntas, 65 minutos, 70 % de aprobado y cinco bloques. Hay 126 preguntas de práctica y 48 fichas. El código presenta simulacros con nota, aciertos, duración e historial, además de acierto por bloque.
- **VERIFY:** el código examinado identifica PCAP-31-03, no PCAP-31-04. Confirmar la versión y el blueprint vigentes con la fuente oficial antes de anunciar compatibilidad.
- **Riesgo comercial:** necesidad potencialmente intensa pero temporal; el usuario puede dejar de pagar después del examen.

### B. Evaluación de DAM/DAW

**HIPÓTESIS — mensaje candidato**

> Para estudiantes de primero de DAW que preparan una evaluación de Programación, en 3 semanas podrás ver qué conceptos y competencias llevas más flojos, practicar esos puntos y comparar tus resultados en dos simulacros. Mediremos nota, acierto por competencia y conceptos que cambian de estado según los criterios actuales de la plataforma. No prometemos aprobar ni que la puntuación equivalga a la nota del centro.

- **A quién:** estudiantes de primero de DAW que preparan una evaluación del módulo de Programación. Ampliar a DAM u otros módulos solo tras verificar cobertura.
- **Qué consigue:** identificar lagunas y comparar el resultado antes y después de practicar.
- **Tiempo:** 3 semanas, **ESTIMACIÓN**, ajustable a la fecha real de evaluación.
- **Medición:** puntuación inicial y final, cambio en puntos porcentuales, acierto por competencia y conceptos que pasan de no dominados a dominados.
- **No promete:** aprobar, mejorar la nota oficial, cubrir todo el currículo ni que el dominio interno sea una evaluación académica validada.
- **OBSERVADO:** learning.json contiene 22 conceptos, 131 ejercicios y tres competencias DAW: Fundamentos, Programación y Lógica. exam.js calcula estadísticas por competencia y compone simulacros; daw-prep.js presenta conceptos flojos, preparación estimada e historial.
- **HIPÓTESIS:** «sabrás qué te falla y qué repasar antes de la evaluación» puede ser más creíble y diferencial que «un plan diario automático». Hay que probarlo con estudiantes y compararlo con sus métodos actuales, incluido ChatGPT.
- **Límite de alcance:** el contenido revisado se centra en Python, lógica y programación. No anunciar preparación integral de DAM/DAW sin mapear el temario real del módulo y del centro.

### C. Docente o centro como pagador

**HIPÓTESIS — mensaje candidato**

> Para docentes de Programación que quieran detectar dificultades comunes antes de una evaluación, en un piloto de 4 semanas podrán revisar un resumen agregado de conceptos practicados y errores frecuentes de un grupo participante, si el centro autoriza el tratamiento y el producto incorpora esa capacidad. Mediremos participación, cobertura y evolución agregada entre dos pruebas. Hoy no ofrecemos un panel docente ni prometemos reducir suspensos.

- **A quién:** docentes o responsables de formación de ciclos DAM/DAW.
- **Qué consigue:** una señal agregada potencialmente útil para orientar repasos en clase.
- **Tiempo:** piloto de 4 semanas, **ESTIMACIÓN**.
- **Medición prevista:** participación, finalización pre/post, conceptos trabajados y evolución agregada.
- **No promete:** reducir suspensos, mejorar notas oficiales, ahorrar horas ni disponer hoy de un panel docente.
- **OBSERVADO:** el progreso pertenece al usuario y se guarda localmente o en su cuenta. No se verificó una vista de grupo/docente ni informes agregados multiusuario.
- **HIPÓTESIS:** un centro podría pagar si el informe cambia una decisión docente y ahorra tiempo; el interés verbal no basta.
- **Dependencias:** roles, permisos, minimización, base jurídica, información a alumnos/familias cuando proceda, retención, contrato y control de acceso. No implementar antes de revisión legal.

## 2. Viabilidad de medición con lo que ya existe

Revisión de frontend/js/learn/mastery.js, recommend.js, exam.js, daw-prep.js, learn-store.js, frontend/js/pcap.js, pcap-store.js, pcap-sync.js, frontend/data/learning.json y frontend/data/pcap.json.

| Capacidad | Estado actual | Qué permite medir | Carencia | Esfuerzo |
|---|---|---|---|---|
| Nota inicial PCAP | **OBSERVADO: parcial** | Al terminar un simulacro se guarda fecha, aciertos, total, nota y duración. | No hay pretest fijo ni cohorte experimental explícita; el banco puede repetirse. | **M** |
| Nota final PCAP | **OBSERVADO: parcial** | Historial de simulacros con puntuación y duración. | No existe protocolo que defina qué intento es el posttest. | **M** |
| Nota inicial DAW | **OBSERVADO: parcial** | Se puede generar un simulacro y guardar resultados. | El constructor es aleatorio; el ámbito studied depende del uso y no garantiza dificultad equivalente. | **M** |
| Nota final DAW | **OBSERVADO: parcial** | Historial y acierto por competencia. | Falta forma equivalente y registro de la ventana experimental. | **M** |
| Detección de lagunas | **OBSERVADO: sí, con límites** | Dominio bajo, errores recientes, conceptos no dominados y competencias débiles. | Es una medida interna, no una evaluación externa validada; depende del banco y del historial. | **S** para definir métricas; **M** para validar |
| Lagunas cerradas | **OBSERVADO: parcial** | Puede compararse el estado de conceptos entre dos instantáneas. | No hay informe de cohorte que cruce laguna inicial, práctica y resultado final. «Dominado» no prueba transferencia a un examen externo. | **M** |
| Evolución por competencia DAW | **OBSERVADO: sí, parcial** | competencyStats calcula dominio ponderado; los simulacros pueden guardar aciertos por concepto. | No se garantiza comparabilidad de formularios ni instantánea completa de competencias en cada fecha. | **M** |
| Evolución por bloque PCAP | **OBSERVADO: sí, parcial** | blockStats calcula aciertos por bloque a partir del último intento; los simulacros guardan nota. | La práctica repetida puede inflar el resultado. Separar práctica de evaluación. | **M** |
| Historial de intentos y errores | **OBSERVADO: sí, limitado** | El aprendizaje guarda hasta 300 eventos de log y errores activos; PCAP conserva hasta cinco respuestas recientes por pregunta. | No es un registro analítico completo e inmutable; existen límites de retención y posibles diferencias entre dispositivos/cuentas. | **M** |
| Conceptos repasados | **OBSERVADO: parcial** | Hay estado, fecha de último intento y repaso programado. PCAP guarda SRS y fechas. | No hay un informe pre/post que vincule automáticamente lagunas, práctica y resultado. | **M** |
| Cohortes, fechas y adherencia | **OBSERVADO: no verificado** | Los estados contienen fechas, pero no se verificó una cohorte experimental. | Definir inicio, finalización, exposición y consentimiento con datos mínimos. | **M** |
| Analítica de landing | **OBSERVADO: no verificado** | No se verificó analítica comercial en los archivos examinados. | Medir fuente, visitas y CTA con privacidad desde el diseño. | **M** |
| Retención semanal | **OBSERVADO: no verificado** | Hay fechas de actividad en el estado local/de cuenta. | Definir eventos y cálculo; actividad no equivale a aprendizaje. | **M** |
| Informe para docentes | **OBSERVADO: no** | No se verificó panel de grupo ni rol docente. | Producto, permisos y revisión legal/privacidad. | **L** |

### Conclusión de medición

**OBSERVADO:** ya existe una base útil de progreso, simulacros, historial y dominio por concepto/competencia. No hace falta crear un segundo motor de maestría.

**No está demostrado** que el producto mida una mejora pre/post comparable con suficiente fiabilidad para sostener una afirmación comercial. La carencia principal es protocolo, comparabilidad de pruebas, captura de cohortes y análisis.

**Mínimo experimento recomendado:** piloto manual supervisado con pretest y posttest documentados, usando las capacidades existentes. Si los formularios no son comparables, tratar los resultados como señales exploratorias, no como prueba de eficacia. No modificar el producto todavía.

## 3. Diseño pre/post

### Protocolo

1. Definir población y resultado primario antes de reclutar. Hacer pilotos separados para PCAP y DAW.
2. Reclutar personas con objetivo real y fecha de examen conocida. Registrar experiencia previa, preparación actual, tiempo disponible y otras herramientas.
3. Informar de finalidad, datos recogidos, retención y voluntariedad. Recabar solo datos necesarios. No incluir menores sin revisar el marco legal y las autorizaciones aplicables.
4. **Pretest, día 0:** simulacro con tiempo y reglas fijadas. Registrar nota, duración, resultados por bloque/competencia y confianza percibida. Guardar versión de la prueba.
5. **Intervención:** tres semanas DAW o cuatro semanas PCAP como hipótesis. Acordar objetivo de uso y preguntar semanalmente por estudio externo, ChatGPT, tutorías y cambios de calendario.
6. **Posttest:** forma equivalente en tiempo, cobertura, dificultad estimada y distribución. Evitar repetir preguntas exactas si es posible. Si el banco es limitado, declarar el efecto de familiaridad.
7. Cierre: medir utilidad, dolor y disposición a pagar; entrevistar a quienes abandonen si aceptan. Informar denominadores: reclutados, iniciados, pretest completado, intervención completada y posttest completado.
8. Analizar diferencia individual en puntos porcentuales, mediana y rango, cambios por bloque/competencia, participantes que mejoran/no cambian/empeoran, adherencia y abandono. Mostrar datos faltantes.
9. Si un participante quiere compartir su nota real, pedir consentimiento claro y tratarla como dato complementario. No atribuir la nota oficial al producto sin un diseño adecuado.

### Muestra y límites

- **ESTIMACIÓN:** 12–20 participantes que completen ambos tests en un solo segmento pueden revelar problemas de uso y señales de factibilidad, pero no demuestran eficacia general.
- **ESTIMACIÓN:** reclutar 20–30 para aspirar a 12–20 finalizaciones puede servir para planificar; la tasa real de abandono es **UNKNOWN**.
- No hay tamaño muestral estadístico validado para demostrar mejora. Para un estudio confirmatorio se debe definir efecto mínimo relevante, variabilidad, potencia y diseño.
- Con pocos usuarios se puede decir «en este grupo exploratorio se observó X» y describir abandono, problemas y señales de demanda.
- No se puede concluir causalidad, generalización, predicción de aprobados ni sustitución de un docente.
- Sesgos: autoselección de personas motivadas; regresión a la media; estudio por otras vías; ChatGPT y tutorías; dificultad distinta; memorización de preguntas; abandono; autoinforme inexacto; muestra pequeña; incentivos y diferencias entre centros.
- Para evaluar eficacia en el futuro, considerar grupo de comparación o incorporación escalonada y revisión de una persona con experiencia en evaluación educativa.

## 4. Prueba de mensajes de landing

**No publicar ni construir todavía.** Son textos para una prueba futura. La CTA debe dejar claro que la oferta aún no está disponible. No cobrar depósitos ni simular una compra.

### A — PCAP

**Titular:** «Descubre qué bloques del PCAP necesitas reforzar antes de tu examen»

**Texto:** «Compara un simulacro inicial y otro final, revisa tus resultados por bloque y organiza tus repasos. Estamos validando un piloto; todavía no está disponible y no podemos prometer que aprobarás.»

**CTA:** «Quiero recibir información cuando esté disponible»

### B — DAW

**Titular:** «Llega a la evaluación de Programación sabiendo qué conceptos necesitas repasar»

**Texto:** «Identifica tus puntos débiles, practica los conceptos prioritarios y compara tus resultados antes y después. Estamos validando la propuesta; todavía no está disponible y no garantiza una nota concreta.»

**CTA:** «Quiero participar en la validación»

### C — docente/centro

**Titular:** «Detecta qué conceptos de Programación le cuestan más a tu grupo»

**Texto:** «Estamos explorando un piloto para ayudar a docentes a orientar repasos a partir de resultados agregados. El panel docente aún no existe; queremos entender cómo tomas hoy estas decisiones.»

**CTA:** «Soy docente y quiero hablar del piloto»

### Diseño y métricas

- Mostrar cada propuesta a público relevante por separado. No mezclar tráfico de estudiantes y docentes.
- Aleatorizar orden/asignación cuando sea posible y mantener iguales canal, periodo y diseño.
- Medir visitas únicas cualificadas, clic CTA, conversión visita→CTA, cuestionarios válidos, entrevistas completadas, segmento y canal. Definir cómo se cuentan repetidos y bots.
- Recoger email solo tras informar de finalidad, responsable, uso y baja. No usar una lista de espera como consentimiento genérico e indefinido de marketing.
- No usar urgencia falsa, testimonios ficticios, contadores, porcentajes inventados ni pantallas que hagan creer que una función existe.
- Una suscripción al email indica interés, no disposición a pagar. Validar esto después con entrevistas sobre comportamiento pasado, alternativas, presupuesto y precios concretos.

### Umbral provisional para elegir mensaje

Los umbrales de docs/business/market-validation.md son **UNKNOWN** porque el archivo no está en main. No presentar los siguientes como umbrales ya acordados.

**ESTIMACIÓN provisional para aprobar antes del experimento:**
- Objetivo de al menos 100 visitas únicas cualificadas por mensaje, si el canal y presupuesto gratuito lo permiten. Si no se alcanza, el resultado es insuficiente, no un fracaso.
- Señal inicial: conversión a CTA de al menos 10 % y cinco entrevistas cualificadas por segmento.
- Un mensaje solo gana provisionalmente si la diferencia se mantiene al comparar canales similares y las entrevistas confirman problema reciente, consecuencias y alternativas actuales. Con muestra pequeña, no declarar ganador estadístico.
- Para una decisión comercial exigir más que emails: aceptar entrevista, dedicar tiempo al piloto o pedir detalles de precio. Un «me gusta» no prueba intención de compra.
- No elegir precio ganador con esta prueba. La intención de pago se valida con entrevistas y, si procede, una oferta transparente posterior.

## 5. Umbrales de decisión

### Recuperación de umbrales anteriores

**UNKNOWN:** no se pudo leer docs/business/market-validation.md ni docs/business/validation-plan.md en main. Los umbrales de esta sección son una propuesta nueva y provisional, pendiente de aprobación.

### Resultado prometedor (provisional)

No declarar «resultado validado» solo por subir la nota media o conseguir emails. Considerar la hipótesis prometedora para otra fase solo si se cumplen estos criterios:

1. **Dolor observado:** al menos ocho entrevistas del mismo segmento; al menos cinco describen un episodio reciente concreto con consecuencias relevantes y qué hicieron/costó. **ESTIMACIÓN**, señal cualitativa, no ley estadística.
2. **Uso y finalización:** al menos 12 participantes completan pre y post en el piloto exploratorio. Informar reclutamiento y abandono.
3. **Medición interpretable:** formularios con cobertura y dificultad razonablemente comparables; cambios documentados y sin fallo técnico invalidante.
4. **Señal de resultado:** mediana de cambio positiva y más participantes mejoran que empeoran. Definir efecto mínimo relevante antes de ver datos con asesoría de evaluación educativa. Hasta entonces no declarar eficacia validada.
5. **Señal comercial:** al menos cinco personas cualificadas aceptan un siguiente paso concreto después de conocer precio y limitaciones reales. Es señal de interés, no prueba de ingresos recurrentes.
6. **Transparencia:** documentar métodos externos, limitaciones, datos faltantes y resultados negativos.

### Cambiar a docente/centro como pagador

Investigar B2B si, tras ocho entrevistas de estudiantes (umbral provisional), el problema existe pero la disposición individual a pagar es débil, mientras que al menos tres docentes/centros describen el mismo problema operativo y dos aceptan explorar un piloto con condiciones y proceso de decisión concretos. **ESTIMACIÓN provisional**, sin entrevistas realizadas.

No pivotar solo por «suena interesante». Confirmar quién controla presupuesto, ciclo de compra, privacidad, integración y qué decisión docente mejoraría el producto.

### Parar o reformular

Parar o reformular si ocurre cualquiera:
- Tras ocho entrevistas cualificadas, no aparecen episodios recientes con consecuencias importantes ni una alternativa que quieran mejorar.
- La mayoría considera suficiente la alternativa gratuita y no describe un coste, frustración o riesgo que el producto resuelva.
- No se recluta una muestra que complete el protocolo o las pruebas no son comparables.
- Contenido/marcas no pueden usarse comercialmente de forma segura o las obligaciones de privacidad no son asumibles.
- La venta depende de prometer aprobados, empleo o resultados no demostrados.

Estos números son **umbrales exploratorios propuestos**, no datos observados ni decisiones previamente aprobadas. Recuperar la versión original de market-validation.md antes de fijar criterios definitivos.

## 6. Riesgos

| Riesgo | Estado | Mitigación antes de comunicar comercialmente |
|---|---|---|
| Prometer aprobar o insinuar causalidad | **VERIFY** legal | Hablar de diagnóstico, práctica y cambio medido; no garantizar aprobado ni nota. Conservar evidencia para cada afirmación. |
| Marca PCAP / Python Institute y marca Python | **VERIFY** | Confirmar versión, reglas de marca, logos y descargos. No insinuar afiliación ni aprobación oficial. |
| Menores | **VERIFY** | FP puede incluir menores. Definir edad mínima o proceso de información/consentimiento y autorización cuando corresponda antes de captar datos. |
| RGPD y LOPDGDD | **VERIFY** | Definir responsable, finalidad, base jurídica, minimización, retención, derechos, encargados, transferencias y seguridad. El consentimiento a participar no sustituye automáticamente una base jurídica válida. |
| Analítica y cookies | **VERIFY** | Medición mínima; revisar si identificadores/cookies requieren consentimiento. No activar scripts externos sin revisión. |
| Datos educativos y panel docente | **HIPÓTESIS de riesgo alto** | No compartir perfiles individuales sin diseño jurídico y de acceso. Empezar, si se aprueba, por agregados que eviten reidentificación. |
| Pruebas no comparables | **OBSERVADO como limitación** | Documentar formas, separar práctica de evaluación, informar familiaridad y estudio externo. |
| Retención baja en PCAP | **HIPÓTESIS** | Medir retorno semanal; no asumir suscripción recurrente hasta observar uso sostenido o un nuevo objetivo. |
| Banco insuficiente o desactualizado | **OBSERVADO / VERIFY** | 126 preguntas no equivalen a 126 ítems validados. Revisar cobertura, calidad, licencia y versión oficial. |
| Licencias y contenido | **VERIFY** | docs/AUDITORIA-Y-LICENCIAS.md indica que la licencia del contenido debe aclararse y que los ejercicios carecen de procedencia/licencia. Resolver antes de comercializar. |
| Progreso local y entre dispositivos | **OBSERVADO** | Progreso puede estar en localStorage o sincronizarse con cuenta. El protocolo debe contemplar pérdida de datos y varias cuentas/dispositivos. |
| Autoselección y abandono | **HIPÓTESIS metodológica** | Informar denominadores y abandonos; no generalizar desde una muestra voluntaria. |

## 7. Fuentes y referencias

### Fuentes internas revisadas

- Repositorio: https://github.com/Marbi8891/python-learning-dashboard — consultado el 30-10-2026.
- Motor de dominio: https://github.com/Marbi8891/python-learning-dashboard/blob/main/frontend/js/learn/mastery.js — consultado el 30-10-2026.
- Recomendación: https://github.com/Marbi8891/python-learning-dashboard/blob/main/frontend/js/learn/recommend.js — consultado el 30-10-2026.
- Simulacros y competencias: https://github.com/Marbi8891/python-learning-dashboard/blob/main/frontend/js/learn/exam.js — consultado el 30-10-2026.
- Preparación DAW: https://github.com/Marbi8891/python-learning-dashboard/blob/main/frontend/js/learn/daw-prep.js — consultado el 30-10-2026.
- Persistencia del aprendizaje: https://github.com/Marbi8891/python-learning-dashboard/blob/main/frontend/js/learn/learn-store.js — consultado el 30-10-2026.
- PCAP: https://github.com/Marbi8891/python-learning-dashboard/blob/main/frontend/js/pcap.js y https://github.com/Marbi8891/python-learning-dashboard/blob/main/frontend/js/pcap-store.js — consultados el 30-10-2026.
- Banco PCAP: https://github.com/Marbi8891/python-learning-dashboard/blob/main/frontend/data/pcap.json — consultado el 30-10-2026.
- Banco de conceptos: https://github.com/Marbi8891/python-learning-dashboard/blob/main/frontend/data/learning.json — consultado el 30-10-2026.
- Auditoría de licencias/arquitectura: https://github.com/Marbi8891/python-learning-dashboard/blob/main/docs/AUDITORIA-Y-LICENCIAS.md — consultada el 30-10-2026.
- Reglas del proyecto: https://github.com/Marbi8891/python-learning-dashboard/blob/main/CLAUDE.md — consultadas el 30-10-2026.

### Fuentes oficiales que requieren verificación antes de publicar

- PCAP certification: https://pythoninstitute.org/pcap — **VERIFY**, versión y blueprint vigentes en la fecha de lanzamiento.
- Marcas de Python: https://www.python.org/psf/trademarks/ — **VERIFY**, uso comercial concreto.
- RGPD, EUR-Lex: https://eur-lex.europa.eu/eli/reg/2016/679/oj — referencia normativa; **VERIFY** aplicación concreta.
- LOPDGDD, BOE: https://www.boe.es/buscar/act.php?id=BOE-A-2018-16673 — referencia normativa; **VERIFY** aplicación concreta.
- Ley General de Publicidad: https://www.boe.es/buscar/act.php?id=BOE-A-1988-26156 — **VERIFY** texto consolidado y aplicación.
- Ley de Competencia Desleal: https://www.boe.es/buscar/act.php?id=BOE-A-2007-20555 — **VERIFY** texto consolidado y aplicación.

Estas fuentes se incluyen para revisión, no como dictamen jurídico ni confirmación de que una marca, contenido o campaña concreta esté autorizada.

---

## Resumen ejecutivo

**Recomendación: probar primero DAW en entrevistas y usar PCAP como hipótesis comercial alternativa en un experimento separado.** No poner ambas propuestas en una misma landing ni declarar una ganadora antes de medir.

DAW tiene una necesidad que puede repetirse a lo largo del curso: identificar conceptos flojos y orientar el repaso antes de una evaluación. El producto ya dispone de 22 conceptos, 131 ejercicios, plan «Hoy», dominio orientativo, estadísticas de tres competencias y simulacros. Esto permite una prueba exploratoria sin reconstruir el motor. La promesa debe limitarse a «ver qué falla y comparar resultados antes y después», sin prometer aprobar ni mejorar la nota oficial.

PCAP es más fácil de explicar y puede tener un dolor concreto, pero el uso puede acabar tras el examen. Además, el repositorio indica PCAP-31-03: hay que confirmar la versión oficial antes de anunciar compatibilidad. El banco tiene 126 preguntas y el código registra simulacros, notas y aciertos por bloque, pero no se ha validado la equivalencia de las pruebas ni su capacidad predictiva.

La medición es **parcialmente viable**: hay progreso e historial, pero falta un protocolo de cohortes y pruebas pre/post comparables. No hace falta un segundo sistema de maestría. Primero realizar entrevistas; si el dolor es real, ejecutar un piloto manual documentado. Una muestra exploratoria de 12–20 finalizaciones puede revelar problemas y señales, no demostrar causalidad o eficacia general.

Investigar al docente/centro como pagador si los estudiantes reconocen el problema pero no pagarían individualmente. No existe un panel docente verificado; sería otra línea de producto y añade obligaciones de privacidad.

**Bloqueo:** los documentos comerciales de Fase 1 y sus umbrales no están en main. Los umbrales aquí son provisionales; recuperar la versión original antes de fijarlos.

### Decisiones del fundador antes de la Fase 2

1. Confirmar si el primer segmento será estudiantes DAW y PCAP una prueba separada, o priorizar PCAP.
2. Aprobar/modificar los umbrales provisionales y aportar la versión original de market-validation.md si existe en otra rama o archivo.
3. Aprobar protocolo de entrevistas, datos mínimos, privacidad y tratamiento de menores.
4. Autorizar expresamente la Fase 2 (analítica mínima, landing y cuestionario). Hasta esa aprobación no se implementará ni desplegará nada.
