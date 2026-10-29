# Guion de demo y defensa

Duración orientativa: 10-12 minutos de exposición. **[VERIFY: ajusta al tiempo que fije el centro.]**

## Antes de empezar (15 minutos antes)

- Abre la demo pública e inicia sesión una vez: el backend gratuito de Render se duerme tras 15 minutos sin tráfico y tarda cerca de un minuto en despertar. Para comprobarlo, abre `https://pld-api.onrender.com/api/health` y espera a ver `"status": "ok"`.
- Ten una cuenta de demostración con progreso ya cargado, para enseñar «Mi aprendizaje» sin esperar.
- Plan B sin internet: `Iniciar-Dashboard.bat` en el portátil (funciona sin internet).
- Ten abiertas en pestañas: la demo, el repositorio, la pestaña Actions con el CI en verde y la memoria.

## Guion

| Min | Qué enseñas | Qué dices |
|---|---|---|
| 0-1 | Portada | Problema: preparar el PCAP exige recursos dispersos y un entorno instalado. Solución: una academia en español que funciona en el navegador. |
| 1-3 | Una lección: teoría, ejemplo en la consola, ejercicio | Python real en el navegador (Pyodide, Web Worker), corte de bucles infinitos, corrección automática con pruebas. |
| 3-5 | Simulacro PCAP y panel de preparación | 40 preguntas en 65 minutos con el reparto oficial. Cada respuesta se comprueba ejecutando Python. |
| 5-6 | Cuenta, sincronización y descarga de datos | Cuenta opcional, también con Google. RGPD: exportar y borrar. Una sola cookie, técnica y de sesión, y solo si inicias sesión. |
| 6-8 | Arquitectura y modelo de datos (diagramas de la memoria) | Frontend estático más API mínima. Por qué elegí Pyodide y JavaScript sin framework. |
| 8-9 | Cursos de DAW, núcleo por conceptos y currículo oficial (`#/daw/curriculo`) | El temario se genera con scripts que ejecutan cada respuesta, así no hay preguntas mal corregidas. Cada pregunta está asociada a uno de los 17 módulos oficiales de DAW. |
| 9-11 | Calidad: CI en verde, cobertura, Playwright, WCAG | 557 pruebas de backend al 100 % de cobertura, 68 unitarias del frontend, 17 ficheros e2e con auditoría de accesibilidad y migraciones en PostgreSQL 16. |
| 11-12 | Conclusiones y líneas futuras | Qué queda: revisión manual de accesibilidad, Lighthouse, curso de HTML/CSS y los módulos de 2.º sin curso. |

## Preguntas que pueden hacerte (y una respuesta corta)

- **¿Por qué no ejecutas el código en un servidor?** Coste, riesgo de seguridad con código ajeno y no funcionaría sin conexión. Pyodide lo evita.
- **¿Por qué sin framework?** El contenido es casi estático. Menos peso y menos dependencias que mantener.
- **¿Cómo sabes que las preguntas están bien?** Cada una lleva una comprobación en Python que se ejecuta en CI.
- **¿Qué pasa con los datos personales?** Datos mínimos, servidores en la UE (Render y Neon en Frankfurt), exportación y borrado en cascada, y solo la cookie técnica de sesión. La analítica está preparada pero desactivada.
- **¿Qué falla o falta?** La revisión manual de accesibilidad y el arranque lento del backend gratuito. Dilo tú antes de que lo pregunten.
- **¿Qué harías distinto?** [VERIFY: respuesta personal. Un tribunal valora más una reflexión honesta que la perfección.] Un dato que puedes usar: hiciste una app Android y un tutor con IA y los retiraste el 26/10 para simplificar (memoria, 9.1).
- **¿Cuánto tiempo te llevó y cómo lo planificaste?** Según Git, del 25/09/2026 al 26/10/2026, con commits en 16 días (fases en la memoria, 9.1). [VERIFY: añade las horas reales y si hubo trabajo antes del 25/09.]
- **¿Qué parte has escrito tú y qué parte con ayuda de IA?** 63 de los 93 commits llevan `Co-Authored-By: Claude` (memoria, 9.3). [VERIFY: prepara una respuesta clara y honesta sobre qué decidiste, revisaste y probaste tú. Es una pregunta probable y conviene que la memoria y tú digáis lo mismo.]

## Checklist final

- [ ] Memoria revisada y datos `[VERIFY]` completados
- [ ] Resultados de Lighthouse añadidos al apartado 6.5
- [ ] Pruebas manuales del apartado 6.3 rellenadas
- [x] Versión 1.0.0 publicada (la etiqueta `v1.0.0` es del 29/09/2026)
- [ ] Nueva versión con el estado de la defensa (la `v1.0.0` es anterior al currículo oficial y a la simplificación del 26/10)
- [ ] Ensayo cronometrado al menos una vez
