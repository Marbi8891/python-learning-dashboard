# ADR-0012: La app Android como curso tipo Duolingo

- **Estado:** Aceptada (revisa el plan de entregas de ADR-0011). ADR-0015 vuelve a revisar el plan de entregas.
- **Fecha:** 2026-09-27

## Contexto

Tras la entrega 1 (panel y práctica por bloque), el autor quiere que la app **se parezca a Duolingo**. Pidió cuatro cosas: ruta de unidades, racha y meta diaria, nuevos tipos de ejercicio y vidas. Solo la app cambia; la web sigue como está.

## Decisión

1. **Ruta como pantalla principal.** Cada lección del temario que tiene preguntas del PCAP es una **unidad**. Si una lección tiene menos de 3 preguntas, se une a la siguiente del mismo bloque, o a la anterior si es la última. Cada unidad se divide en **lecciones cortas de unas 5 preguntas**, que son los nodos del camino, y se desbloquean en orden.
   - Se genera a partir de `pcap.json` y `lessons.json` al abrir la app, así que no hay otro fichero que mantener.
   - Los ids de los nodos (`<unidad>-<n>`) se mantienen estables mientras no cambie el número de nodos de una unidad.
2. **Lección:**
   - Una pregunta fallada **vuelve al final de la cola** hasta acertarla, como en Duolingo.
   - La lección termina cuando todas están acertadas.
   - Cada respuesta cuenta también para el repaso espaciado y la preparación del PCAP.
3. **XP diaria y racha, derivadas:**
   - Se guarda **XP por día** (`daily`). La racha se calcula al vuelo: días seguidos con XP, y el día de hoy no la rompe hasta que termina. No hay contador que se desincronice.
   - Premios: 10 XP por lección completada, +5 si no hay ningún fallo, y 1 XP por acierto en la práctica libre.
   - Meta diaria elegible: 10, 20, 30 o 50 XP.
4. **Vidas, con límites.** Son 5 y se pierde una por fallo en las lecciones de la ruta. Se recupera una cada 4 horas y otra al terminar una tanda de práctica libre. La práctica libre, el repaso y los simulacros **no gastan vidas**.
   - Razón: el autor las pidió. La objeción era que castigar el error hace practicar menos justo donde más se necesita. La mitigación es que siempre hay una forma de estudiar sin vidas, que además sirve para recuperarlas.
5. **Nuevos tipos de ejercicio** en la entrega siguiente: ordenar líneas de código y completar el hueco.
   - Cada ejercicio se comprueba **ejecutando Python en pytest**, como el banco actual.
   - Son contenido original, no copiado de ningún examen.
6. **Identidad propia:** sin mascota, colores ni nombres de Duolingo. Se usan los tokens de la web (dorado y verde).

## Estado guardado

El progreso nuevo va en `app` dentro del mismo documento `pcap`: `done`, `daily`, `goal`, `hearts` y `heartsAt`.

- ASSUMPTION: para la sincronización hay que adaptar la fusión de la web (`mergePcap`) para que conserve el objeto `app`. Hoy la web lo perdería al guardar en el servidor. Se hará en la entrega de la cuenta.

## Nuevo plan de entregas

| Entrega | Contenido |
|---|---|
| 1 ✔ | Proyecto, CI con APK, panel y práctica por bloque |
| 2 | Ruta, lecciones cortas, XP, racha, meta diaria, vidas, celebración y perfil |
| 3 | Ordenar código y completar el hueco (contenido nuevo probado) |
| 4 | Simulacro cronometrado, fichas y repaso de hoy |
| 5 | Python real en el móvil (Chaquopy) para los ejercicios de las lecciones |
| 6 | Cuenta y sincronización |

## Consecuencias

- La app y la web dejan de verse igual. Es intencionado: la app es la experiencia diaria y corta, y la web el curso completo y el simulacro.
- El recordatorio diario por notificación queda fuera por ahora: necesita permiso de notificaciones y programar alarmas, y aporta poco hasta que haya uso diario real.
