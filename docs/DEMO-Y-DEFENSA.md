# Guion de demo y defensa

Duración orientativa: 10-12 minutos de exposición. **[VERIFY: ajusta al tiempo que fije el centro.]**

## Antes de empezar (15 minutos antes)

- Abre la demo pública y entra una vez: el backend gratuito puede tardar en despertar tras un rato inactivo [VERIFY].
- Ten una cuenta de demostración con progreso ya cargado, para enseñar «Mi aprendizaje» sin esperar.
- Plan B sin internet: `Iniciar-Dashboard.bat` en el portátil y la app Android instalada en el móvil (funciona sin conexión).
- Ten abiertas en pestañas: la demo, el repositorio, la pestaña Actions con el CI en verde y la memoria.

## Guion

| Min | Qué enseñas | Qué dices |
|---|---|---|
| 0-1 | Portada | Problema: preparar el PCAP exige recursos dispersos y un entorno instalado. Solución: una academia en español que funciona en el navegador. |
| 1-3 | Una lección: teoría, ejemplo en la consola, ejercicio | Python real en el navegador (Pyodide, Web Worker), corte de bucles infinitos, corrección automática con pruebas. |
| 3-5 | Simulacro PCAP y panel de preparación | 40 preguntas en 65 minutos con el reparto oficial. Cada respuesta se comprueba ejecutando Python. |
| 5-6 | Cuenta, sincronización y descarga de datos | Cuenta opcional. RGPD: exportar y borrar. Cero cookies. |
| 6-8 | Arquitectura y modelo de datos (diagramas de la memoria) | Frontend estático más API mínima. Decisiones documentadas en 19 ADR. |
| 8-9 | App Android en el móvil, sin conexión | Mismos datos que la web. Ruta, vidas, juego y cursos de DAW. |
| 9-11 | Calidad: CI en verde, cobertura, Playwright, WCAG | 412 pruebas de backend al 100 %, e2e, auditoría de accesibilidad y migraciones en PostgreSQL 16. |
| 11-12 | Conclusiones y líneas futuras | Qué queda: email de recuperación, Python en Android, simulacro en Android. |

## Preguntas que pueden hacerte (y una respuesta corta)

- **¿Por qué no ejecutas el código en un servidor?** Coste, riesgo de seguridad con código ajeno y no funcionaría sin conexión. Pyodide lo evita (ADR-0004).
- **¿Por qué sin framework?** El contenido es casi estático. Menos peso y menos dependencias que mantener (ADR-0001).
- **¿Cómo sabes que las preguntas están bien?** Cada una lleva una comprobación en Python que se ejecuta en CI.
- **¿Qué pasa con los datos personales?** Datos mínimos, servidores en la UE, exportación y borrado en cascada, sin cookies.
- **¿Qué falla o falta?** El email de recuperación (falta SMTP), la revisión manual de accesibilidad y parte de la app Android. Dilo tú antes de que lo pregunten.
- **¿Qué harías distinto?** [VERIFY: respuesta personal. Un tribunal valora más una reflexión honesta que la perfección.]
- **¿Cuánto tiempo te llevó y cómo lo planificaste?** [VERIFY: ten las cifras reales de horas y fechas; el historial de Git empieza el 25/09/2026.]
- **¿Qué parte has escrito tú y qué parte con ayuda de IA?** [VERIFY: prepara una respuesta clara y honesta. Es una pregunta probable y conviene que la memoria y tú digáis lo mismo.]

## Checklist final

- [ ] Memoria revisada y datos `[VERIFY]` completados
- [ ] Resultados de Lighthouse añadidos al apartado 6.5
- [ ] Pruebas manuales del apartado 6.3 rellenadas
- [ ] Versión 1.0.0 publicada (tag y release)
- [ ] Ensayo cronometrado al menos una vez
