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
| 0-1 | Portada | Problema: preparar el PCAP y los módulos de DAW exige recursos dispersos y un entorno instalado. Solución: una web gratuita en español que funciona en el navegador. |
| 1-3 | Una lección: teoría, ejemplo en la consola, ejercicio fallado y corregido | Python real en el navegador (Pyodide, Web Worker), botón «Detener», corrección que explica qué falta y qué mostró el programa sin dar la solución. |
| 3-5 | Simulacro PCAP y panel de preparación | 40 preguntas en 65 minutos con el reparto oficial. Cada respuesta se comprueba ejecutando Python. |
| 5-6 | Cuenta, sincronización y descarga de datos | Cuenta opcional, también con Google. El progreso no se pierde: versión por documento, 409 y aviso si algo no se ha guardado al cerrar sesión. RGPD: exportar y borrar. Una sola cookie, técnica y de sesión. |
| 6-8 | Arquitectura y modelo de datos (diagramas de la memoria) | Frontend estático más API mínima. Por qué elegí Pyodide y JavaScript sin framework. |
| 8-9 | Lenguajes de marcas o Entornos (unidad completa), currículo oficial (`#/daw/curriculo`) y Aspecto en inglés | Seis cursos de DAW, 520 preguntas. El temario se genera con scripts que ejecutan cada respuesta. Cada pregunta está asociada a uno de los 17 módulos oficiales. Interfaz en español e inglés y opciones de lectura. |
| 9-11 | Calidad: CI en verde, auditorías y WCAG | 649 pruebas de backend al 100 % de cobertura, 130 unitarias, 197 e2e con axe-core (WCAG 2.2 AA, 0 infracciones en 15 rutas) y migraciones en PostgreSQL 16. Auditorías técnica, de seguridad y legal: cada fallo grave se reprodujo con una prueba antes de corregirlo. |
| 11-12 | Conclusiones y líneas futuras | Qué queda: revisión con lector de pantalla, Lighthouse, unidades completas en el resto de cursos y los módulos 0483, 0613, 0614 y 0615. |

## Preguntas que pueden hacerte (y una respuesta corta)

- **¿Por qué no ejecutas el código en un servidor?** Coste, riesgo de seguridad con código ajeno y no funcionaría sin conexión. Pyodide lo evita.
- **¿Por qué sin framework?** El contenido es casi estático. Menos peso y menos dependencias que mantener.
- **¿Cómo sabes que las preguntas están bien?** Cada una lleva una comprobación en Python que se ejecuta en CI.
- **¿Qué pasa con los datos personales?** Datos mínimos, servidores en la UE (Render y Neon en Frankfurt), exportación y borrado en cascada, y solo la cookie técnica de sesión. La analítica está preparada pero desactivada.
- **¿Qué falla o falta?** La revisión con lector de pantalla, el arranque lento del backend gratuito y que la XP la calcula el navegador (por eso no se presenta como verificada). Dilo tú antes de que lo pregunten.
- **¿Cómo evitas perder el progreso?** Cada documento lleva versión; si otra pestaña guardó antes, el servidor responde 409 y la app fusiona y reintenta. Al cerrar sesión no se borra nada que el servidor no tenga (memoria, 5.3).
- **¿Qué relación tiene con el ciclo?** Tabla de la memoria, 1.3: cada módulo técnico tiene su parte en el proyecto.
- **¿Qué harías distinto?** [VERIFY: respuesta personal. Un tribunal valora más una reflexión honesta que la perfección.] Un dato que puedes usar: hiciste una app Android y un tutor con IA y los retiraste el 26/10 para simplificar (memoria, 3.6).
- **¿Cuánto tiempo te llevó y cómo lo planificaste?** Según Git, del 25/09/2026 al 03/11/2026, con commits en 19 días (fases en la memoria, 3.6). [VERIFY: añade las horas reales y si hubo trabajo antes del 25/09.]
- **¿Qué parte has escrito tú y qué parte con ayuda de IA?** 58 de los 158 commits de `main` llevan una marca explícita de Claude Code, y la parte real es mayor (memoria, 9.4). [VERIFY: prepara una respuesta clara y honesta sobre qué decidiste, revisaste y probaste tú. Es una pregunta probable y conviene que la memoria y tú digáis lo mismo.]

## Checklist final

- [ ] Memoria revisada y datos `[VERIFY]` completados (lista en `docs/memoria/PENDIENTES.md`)
- [ ] Resultados de Lighthouse añadidos al apartado 6.5
- [ ] Pruebas manuales del apartado 6.3 rellenadas
- [x] Versión 1.0.0 publicada (la etiqueta `v1.0.0` es del 29/09/2026)
- [ ] Nueva versión con el estado de la defensa (la `v1.0.0` es anterior al currículo oficial, al rediseño y a las auditorías)
- [ ] Revisión con VoiceOver o NVDA anotada en la memoria, 6.3
- [ ] Memoria exportada a PDF con el formato que pida el centro
- [ ] Ensayo cronometrado al menos una vez
