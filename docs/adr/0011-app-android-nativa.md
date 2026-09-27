# ADR-0011: App Android nativa en Kotlin

- **Estado:** Aceptada. El plan de entregas lo revisa ADR-0012 (app tipo Duolingo).
- **Fecha:** 2026-09-27

## Contexto

La web ya es instalable como PWA (ADR-0010). El autor quiere además una **app nativa en Kotlin** para su móvil (Xiaomi 13T Pro, Android) y para la defensa del proyecto, con todo el alcance de la web, incluida la ejecución de Python. No se publicará en Google Play por ahora.

## Opciones

| Opción | Pros | Contras |
|---|---|---|
| A. TWA (la web en un APK) | 1 h de trabajo, se actualiza sola | No es nativa: es la web |
| B. Capacitor (web empaquetada) | Sin conexión desde el primer uso | Sigue siendo HTML en un WebView |
| **C. Kotlin + Jetpack Compose** | Nativa de verdad; buen material para la defensa (DAM) | Semanas de trabajo; duplica la interfaz |

## Decisión

**C**, por entregas verificables:

1. **E1:** proyecto `android/`, APK generado por GitHub Actions, dominio PCAP (banco, estado, repaso espaciado, preparación) con tests, panel y práctica por bloque en ES/EN.
2. **E2:** simulacro cronometrado, fichas y repaso de hoy.
3. **E3:** lecciones y ejercicios con **Python real en el móvil (Chaquopy)**.
4. **E4:** cuenta (login contra la API de Render) y sincronización con `/api/pcap-state`.

Reglas:

- **Una sola fuente de datos:** la app empaqueta `frontend/data/*.json` tal cual (Gradle los añade como *assets*); no hay copia que se desincronice.
- **Mismo formato de estado que la web** (`pld:pcap`): la sincronización de E4 reutiliza el endpoint y la fusión existentes sin cambiar el backend.
- **Pocas dependencias:** Compose + Material 3 + `activity-compose`. JSON con `org.json` (incluido en Android), red con `HttpURLConnection`, navegación con una pila propia. Sin Retrofit, Room, Hilt ni Navigation: el tamaño de la app no los justifica.
- **Compilación en la CI:** el APK de depuración se genera en GitHub Actions (`android.yml`) y se descarga como *artifact*. No hace falta Android Studio en el PC del autor.

## Versiones

AGP 8.13.0, Gradle 8.14.3, Kotlin 2.2.0, Compose BOM 2025.06.00, compileSdk/targetSdk 36, minSdk 26. Se eligen para que encaje **Chaquopy 16.1** (AGP 8.9–8.13, Python 3.10–3.13) en E3; Chaquopy 17 exige AGP 9.

## Consecuencias

- La lógica del PCAP existe dos veces (JS y Kotlin). Mitigación: los tests Kotlin comprueban las mismas reglas (cajas 1/3/7/14/30, fusión, preparación ponderada) y leen el mismo `pcap.json`.
- Cada cambio de la app se prueba instalando el APK de la CI.
- VERIFY: el entorno de desarrollo del asistente no tiene acceso a los repositorios de Google/Maven. La lógica de dominio se compila y prueba allí con `kotlinc`, pero la interfaz Compose solo se compila en la CI.
- ~~ASSUMPTION: el APK de depuración basta para uso propio y la defensa.~~ Refutada: el móvil lo marca como no seguro y la firma cambia en cada ejecución. Lo sustituye la firma de release de ADR-0013.
