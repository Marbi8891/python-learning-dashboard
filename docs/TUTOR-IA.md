# Tutor IA de Python Learning Dashboard

Estado: integración en el código de PLD. El servicio externo NEXARO y su modelo deben estar configurados para activarlo.

## Qué puede hacer

Dentro del asistente de una lección, el apartado **Tutor IA** permite:

- **Preguntar:** explica la teoría de la lección con ejemplos pequeños y mantiene un contexto conversacional corto.
- **Pedir pista:** entrega hasta tres niveles de ayuda, de una orientación general a una guía más concreta.
- **Explicar mi error:** interpreta el último error capturado por la consola Python.
- **Revisar mi código:** analiza el código de la consola como texto y propone errores posibles y pruebas. No lo ejecuta.

Las respuestas llevan la marca «IA · no es la corrección oficial». La IA no aprueba ejercicios ni cambia XP, progreso, intentos o resultados.

## Arquitectura

```
Navegador (PLD)
   │ sesión autenticada
   ▼
FastAPI /api/v1/ai/*
   │ contexto de lección obtenido de la base de datos
   ▼
NEXARO AI (agente + modelo)
```

El navegador no recibe ni conoce la URL, token, modelo o agente de NEXARO. La integración usa el cliente de API existente de PLD y la sesión autenticada.

## Activar en backend

La IA está desactivada por defecto. Configura las variables en el entorno del backend (por ejemplo, Render → Environment), no en `frontend/config.js` ni en GitHub Pages:

| Variable | Valor |
|---|---|
| `NEXARO_ENABLED` | `true` |
| `NEXARO_BASE_URL` | URL base de NEXARO, sin ruta ni query |
| `NEXARO_ALLOWED_HOSTS` | Host permitido de esa URL |
| `NEXARO_MODEL` | Nombre exacto del modelo instalado |
| `NEXARO_SERVICE_TOKEN` | Token de servicio cuando la instancia no está en loopback |
| `NEXARO_AGENT_TUTOR` | Agente de tutor (por defecto `tutor-programacion`) |
| `NEXARO_AGENT_REVIEW` | Agente de revisión (por defecto `programador`) |

Otros controles tienen valores predeterminados: timeout de generación de 120 s, límite de 10 peticiones por usuario/minuto y hasta 2 generaciones simultáneas. Los nombres y validaciones están en `backend/app/config.py`.

**Importante:** la configuración del cliente valida el host contra una allowlist y exige HTTPS para hosts remotos. No habilites la integración con una URL pública sin TLS. Si NEXARO está en otro servidor, comprueba que su autenticación de servicio esté habilitada en esa instalación; la compatibilidad depende de la versión de NEXARO desplegada.

## Comprobar el despliegue

Con una cuenta iniciada:

1. `GET /api/v1/health` debe incluir `"ai": true` cuando la integración esté habilitada.
2. `GET /api/v1/ai/status` debe devolver `enabled: true` y `available: true`.
3. Abre una lección, el asistente y el apartado **Tutor IA**.
4. Prueba una pregunta, una pista, una explicación de error y la revisión de código.
5. Si el backend devuelve `available: false`, revisa el log del backend y la disponibilidad del modelo/agente en NEXARO.

Sin IA, el asistente de respuestas preparadas sigue funcionando.

## Privacidad y límites

- Las rutas requieren sesión de PLD.
- El backend construye el contexto de lección; el alumno aporta la pregunta y, opcionalmente, su código.
- El código solo se envía si el alumno marca la casilla o pulsa «Revisar mi código», que implica enviarlo.
- Las preguntas, el código y las respuestas no se escriben en los logs de PLD. Se registran metadatos de la petición.
- El historial de conversación solo vive en memoria del navegador; se borra al cambiar de lección o recargar.
- No se transmite el nombre, email ni ID del alumno al contexto de NEXARO.
- No hay ejecución de código por el tutor ni herramientas disponibles para el modelo.
- No es un evaluador oficial y no modifica el progreso.

## Endpoints

- `GET /api/v1/ai/status`
- `POST /api/v1/ai/chat`
- `POST /api/v1/ai/hint`
- `POST /api/v1/ai/explain-error`
- `POST /api/v1/ai/review-code`
