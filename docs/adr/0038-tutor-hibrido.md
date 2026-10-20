# ADR-0038: Tutor híbrido con una modalidad «IA avanzada» opcional

- **Estado:** Propuesta (pendiente de que el autor la apruebe en el PR).
- **Fecha:** 2026-10-20
- **Relacionada:** ADR-0034 (agentes A2A), ADR-0036 (tutor adaptativo)

## Contexto

El tutor de Python responde con un plan pedagógico determinista (ADR-0036) y, si hay modelo, con
un proveedor gratuito (Ollama local) o simulado. Se quiere ofrecer además una modalidad de más
calidad con OpenAI sin que eso cree un gasto sin control, sin que el navegador decida quién paga y
sin que el tutor deje de funcionar cuando OpenAI está apagado, mal configurado o falla.

## Decisión

1. **Dos modalidades** en el mismo agente: `free` (la de siempre) y `advanced` (opcional). La
   modalidad la pide el mensaje (`mode`), pero la **decide el backend**: solo se concede si
   `A2A_ADVANCED_PROVIDER` la tiene configurada, la entrada cabe en el límite y queda cuota. El
   cliente no puede elegir proveedor ni modelo.
2. **OpenAI como un `AgentModelProvider` más** (`OpenAIProvider`), con el SDK oficial y la API de
   Responses, destino fijo, `store=False`, sin identificadores del alumno, tiempo máximo por
   llamada y **sin reintentos** (cada consulta reservada es como mucho una llamada facturable).
   Ollama, Anthropic y el modelo simulado no cambian.
3. **Cuotas en la base de datos** (tabla `tutor_usage`, por usuario, día UTC y modalidad): la
   consulta avanzada se reserva **antes** de llamar al proveedor y se devuelve si el proveedor no
   la atiende (429, clave o modelo inválidos). Límite por usuario y día y límite global por día.
4. **Sin escalada de coste**: si falla el proveedor gratuito, nunca se llama al de pago; si la IA
   avanzada no se puede usar, se explica el motivo y se ofrece la respuesta gratuita.
5. **La IA no corrige ni concede progreso**: las comprobaciones las corrige el backend con la
   salida verificada en CI, y una respuesta del modelo no marca nada como completado.
6. **Desactivada por defecto** (`none`). Activarla en producción exige revisar antes la privacidad
   (borrador en `docs/legal/expediente/borradores/tutor-hibrido-openai.md`).

## Consecuencias

- Una tabla nueva (migración aditiva) y un endpoint nuevo (`GET /api/v1/tutor/modes`); los
  clientes actuales, incluida la futura app Android, siguen funcionando sin cambios.
- Con varias instancias del backend, el cerrojo es por proceso: dos peticiones simultáneas podrían
  pasarse del límite en una consulta. Con una sola instancia (el despliegue actual) es exacto.
- El coste máximo queda acotado por configuración; la estimación está en
  [tutor-hibrido.md](../tutor-hibrido.md).
- Nueva dependencia: `openai` (solo se usa si se activa).

## Alternativas descartadas

- **Llamar a OpenAI desde el navegador**: expondría la clave y el cliente decidiría el gasto.
- **Reintentar automáticamente**: podría cobrar dos veces una sola consulta de la cuota.
- **Cuotas en memoria**: un reinicio del servidor devolvería consultas de pago.
- **Pagos, suscripciones o créditos**: fuera de esta fase.
