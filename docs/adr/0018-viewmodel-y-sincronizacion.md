# ADR-0018: ViewModel en la práctica y sincronización de la app con la cuenta

- **Estado:** Aceptada. La primera parte (B1) está implementada; la segunda (B2), pendiente.
- **Fecha:** 2026-09-27
- **Revisa:** ADR-0014 (la app sigue funcionando sin conexión; la red solo sirve para sincronizar)

## Contexto

El autor propuso una especificación con estas piezas:

- `PcapPracticeUiState` y `PracticeUserAction`, con flujo de datos en un solo sentido (UDF);
- un `PracticeViewModel`;
- Retrofit para descargar y **corregir** las preguntas en el servidor;
- un endpoint `/api/v1/users/progress/sync` que recibe el `user_id` en el cuerpo de la petición.

Aplicada tal cual, habría causado varios problemas:

- **Pérdida de progreso:** el paquete era otro, y Android la habría tratado como otra app.
- **Adiós al modo sin conexión** (ADR-0014).
- **Ejercicios rotos:** un único `selectedOptionIndex` no sirve para las preguntas de varias respuestas, los huecos ni ordenar líneas.
- **Fallo de seguridad (IDOR):** con el `user_id` en el cuerpo, cualquiera podría escribir el progreso de otro.
- **Dos sistemas de sincronización** paralelos.

Al revisarlo apareció además un **error real**: la fusión de la web (`mergePcap`) descartaba el objeto `app` del estado. Cuando la web guardaba, borraba de la cuenta la XP, la racha, la ruta y los récords de la app.

## Opciones

| Opción | Resumen | Veredicto |
|---|---|---|
| A. Especificación literal | Preguntas y corrección en el servidor, `user_id` en el cuerpo | Descartada por los problemas del contexto |
| **B. Sincronización opcional + ViewModel adaptado** | Preguntas dentro del APK; la red solo sincroniza el estado; usuario sacado del token | **Elegida** |
| C. Solo ViewModel | Sin red | Se queda corta: la sincronización ya estaba prevista (entrega 7) |

## Decisión (B)

### B1 (implementada)

- **Web:** `mergePcap` conserva `app` tal como está en la cuenta. La web no lo modifica, y la app fusiona el suyo al sincronizar. Hay un test end-to-end que **falla sin el arreglo**.
- **Backend:** `GET/PUT /api/course-state/{curso}` para SQL, JavaScript y Java.
  - Mismo modelo que `/api/pcap-state`: un documento JSON por usuario y curso, con el mismo límite de tamaño.
  - El usuario sale **del token**. La lista de cursos es cerrada (`COURSES`).
  - Se incluye en la exportación RGPD y en el borrado de la cuenta.
  - Migración `5b1d2f8c9a31`. Los tests siguen al 100 % de cobertura.
  - El PCAP sigue usando `/api/pcap-state`.
- **Android:** `PracticeUiState` y `PracticeUserAction` (los nombres de la especificación, adaptados) y `PracticeViewModel` con `StateFlow`.
  - El estado siguiente lo calcula una función pura `reduce`, con tests.
  - El ViewModel solo aplica los efectos: guardar la respuesta, la XP y la vida.
  - La respuesta es un `Answer`, no un índice, así que sirve para todos los tipos de ejercicio (ADR-0017).
  - La tanda sobrevive a abrir la teoría y volver, cosa que antes se perdía.
  - Se añade barra de progreso de la tanda.

### B2 (pendiente)

- **Login opcional en el Perfil** contra `/api/auth/login`, guardando solo el token, nunca la contraseña.
- **Sincronizar** = para cada curso, GET → fusionar (`PcapState.merge`) → PUT.
- **Retrofit** con `kotlinx.serialization`.
- **URL del servidor según el tipo de compilación:** en release, `https://pld-api.onrender.com`; en debug se puede cambiar, por ejemplo a `http://10.0.2.2:8000/` para el emulador, con permiso de tráfico sin cifrar solo en debug.
- **Permiso `INTERNET`.** Todo lo demás sigue funcionando sin conexión.

## Consecuencias

- **Una dependencia nueva:** `lifecycle-viewmodel-compose`. En B2 llegarán Retrofit y `kotlinx.serialization`.
- **Pantalla de ruta sin cambios:** ya tenía los tres estados (completada, en curso y bloqueada), calculados a partir del progreso, no guardados.
- **Sincronización fusionada, no sobrescrita:** si la web guarda un `app` antiguo, la siguiente sincronización de la app lo fusiona con el suyo (unión de lecciones hechas y XP máxima por día). Nunca pierde el más reciente.
- **VERIFY:** que la interfaz compile en la CI y que la práctica funcione igual en el móvil.
