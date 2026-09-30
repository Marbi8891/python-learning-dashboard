# ADR-0026: Cuenta y sincronización en la app Android

- **Estado:** Aceptada e implementada (app 0.13.0)
- **Fecha:** 2026-09-30
- **Revisa:** [ADR-0014](0014-app-sin-conexion.md). La app deja de ser «sin permiso de internet», pero **sigue funcionando entera sin conexión**.
- **Es la fase 2 de:** [ADR-0024](0024-completar-la-app-android.md)

## Contexto

El progreso del móvil y el de la web estaban separados. La API ya sincronizaba la web (`/api/pcap-state` y `/api/course-state/<curso>`) con un formato que la app ya leía y escribía (ADR-0018). Faltaban tres cosas en la app:

- iniciar sesión;
- el permiso de red;
- el cuándo sincronizar.

## Decisión

1. **Iniciar sesión** en la pestaña Perfil («Tu cuenta») con el email y la contraseña de la web: el mismo login OAuth2. **La cuenta se crea en la web**, donde se acepta la política de privacidad; la app enlaza allí.
2. **Sincronización:**
    - Por cada curso (PCAP y los 5 de DAW): traer la copia de la cuenta, fusionarla con la del móvil con `PcapState.merge` (la misma regla que la web, que no pierde nada de ningún lado) y subir el resultado entero.
    - El PCAP lleva también el progreso compartido de la app (XP, racha, vidas y ruta); los cursos, no.
    - **Cuándo:** al iniciar sesión, al abrir la app (`onStart`), al salir (`onStop`) y con el botón «Sincronizar ahora».
    - **Hilos:** la red va en segundo plano (`Dispatchers.IO`) y la fusión en el hilo principal, que es el único que modifica el estado.
3. **Compatibilidad hacia delante:**
    - la app conserva `plan.dailyGoal` (la meta diaria de «Mi cuenta» de la web, ADR-0025);
    - conserva también cualquier campo de primer nivel que no conozca, para que una versión antigua de la app no borre datos nuevos de la web.
4. **Código probable sin Android:**
    - `pcap/Sync.kt` tiene `AccountApi`, `Sync.merge` y la interfaz `Http`;
    - la red real es `UrlConnectionHttp`, con `HttpURLConnection`: **sin librerías nuevas**;
    - `SyncTest` usa un servidor falso.
5. **Seguridad:**
    - **Solo HTTPS:** `usesCleartextTraffic="false"`.
    - **La contraseña no se guarda nunca.** Se guardan el token (caduca en 1 hora), el email y el nombre, en un archivo propio (`pld-session`) **excluido de las copias de seguridad** y de la transferencia entre móviles (`res/xml/backup_rules.xml` y `data_extraction_rules.xml`). El progreso sí viaja en las copias.
    - Si el token caduca (401), la sesión se cierra en el móvil, el email queda escrito y se pide la contraseña otra vez.
    - La app se identifica como `PLD-App/<versión> (Android)`. En «Actividad de la cuenta» de la web aparece como «Android · App».
6. **Configuración sin tocar el código:** `BuildConfig.API_URL` y `BuildConfig.WEB_URL`, con valores por defecto de producción, se cambian con `-PpldApiUrl` y `-PpldWebUrl`.

## Alternativas descartadas

| Opción | Por qué no |
| --- | --- |
| Retrofit + OkHttp | Dos dependencias (y su configuración de R8) para 4 peticiones. `HttpURLConnection` basta y es fácil de sustituir en los tests. |
| Registro dentro de la app | Duplicaría la aceptación de la privacidad y la validación. La web ya lo hace bien. |
| Tokens de refresco para no volver a pedir la contraseña cada hora | Es un cambio de seguridad en el servidor (rotación, revocación, almacenamiento). Se hace aparte si la sesión corta molesta de verdad. |
| Sincronizar en cada respuesta | Una petición por pregunta. Al abrir y al salir cubre el uso normal con muchas menos peticiones. |
| WorkManager para sincronizar en segundo plano | Una dependencia más para un caso raro (cerrar la app sin conexión). Queda como mejora. |

## Consecuencias

- **DONE:**
  - el dominio Kotlin compila y pasan 56 tests, 4 de ellos nuevos de sincronización (formulario OAuth2 con caracteres especiales, errores en español, 401, sin conexión, rutas por curso, fusión que conserva la meta diaria y los campos desconocidos);
  - el backend pasa 465 tests con cobertura del 100 %.
- **VERIFY:**
  - la interfaz y el manifiesto solo se compilan en la CI;
  - hay que probar en el móvil: iniciar sesión, «Sincronizar ahora», que un simulacro hecho en el móvil aparezca en «Mi cuenta» de la web y que la fecha de examen puesta en la web llegue al móvil.
- **Límite conocido:** con el plan gratuito de Render, la primera sincronización tras un rato sin uso tarda hasta un minuto. La app lo avisa en el botón.
- La política de privacidad añade que la app se conecta al servidor solo con sesión iniciada.
