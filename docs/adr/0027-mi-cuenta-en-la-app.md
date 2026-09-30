# ADR-0027: «Mi cuenta» en la app Android

- **Estado:** Aceptada e implementada (app 0.13.0)
- **Fecha:** 2026-09-30
- **Relacionada con:** [ADR-0025](0025-mi-cuenta-ampliada.md) (web) y [ADR-0026](0026-cuenta-y-sincronizacion-en-la-app.md) (sincronización)

## Contexto

El autor quiso en la app lo mismo que la «Mi cuenta» ampliada de la web. En la app, esa función la cumple la pestaña **Perfil**: ya tenía la racha, la XP, la meta diaria y, desde ADR-0026, el inicio de sesión.

## Decisión

La pestaña Perfil pasa a titularse «Mi cuenta» y tiene, en este orden, las mismas partes que la web:

1. **Tu cuenta:** iniciar sesión y sincronizar (ADR-0026).
2. **Mi plan de estudio:**
    - la fecha del examen de cada curso, con el selector de fecha del sistema, la cuenta atrás (en rojo la última semana) y las preguntas por repasar hoy;
    - la fecha se guarda en `plan.examDate`, el mismo campo que la web, así que se sincroniza.
3. **Mi progreso en todos los cursos:** el dominio, las respuestas y los simulacros, y el tema más flojo (por debajo del 80 %) o el siguiente sin empezar. El botón **«Practicarlo» cambia a ese curso y abre la tanda de ese bloque**.
4. Las estadísticas de siempre: racha, XP, últimos 7 días y meta diaria de XP.
5. **Últimos simulacros:** los 10 últimos de todos los cursos, del móvil y, con cuenta, de la web.
6. **Certificados:**
    - estado de cada curso, con las mismas reglas que la web (70 % de dominio y 5 preguntas de cada bloque; en el PCAP, un simulacro aprobado como estimación);
    - **se ven y descargan en la web** («Ver en la web» abre `#/certificado/<curso>`), porque la web ya los imprime en PDF y el navegador del móvil también sabe hacerlo.
7. **Logros:** 8 logros calculados a partir del progreso (primera lección, racha de 7 días, 500 XP, 100 aciertos, simulacro aprobado, 70 % en un curso, bloque dominado y certificado). No se guardan, así que nunca se desincronizan.
8. **Perfil y seguridad** (solo con sesión): cambiar el nombre y la contraseña, y la actividad reciente de la cuenta.
    - Al cambiar la contraseña, el servidor cierra las demás sesiones y devuelve un token nuevo que sustituye al guardado, así que **el móvil sigue conectado**.

**Código:**

- `pcap/Overview.kt`: resumen de cada curso y logros, sin Android y con tests (`OverviewTest`);
- `AccountApi.rename`, `changePassword` y `activity` en `Sync.kt`;
- los paneles de interfaz, en `ui/MyAccountPanels.kt`.

**No se añaden endpoints:** la app usa los de ADR-0025.

## Alternativas descartadas

| Opción | Por qué no |
| --- | --- |
| Generar el PDF del certificado en la app | Supone código de impresión en Android para algo que la web ya hace bien. |
| Una pestaña nueva «Cuenta» | Cinco pestañas en la barra inferior quedan justas en un móvil, y Perfil ya era esa zona. |
| Guardar los logros | Es estado extra que sincronizar y que se puede desincronizar. Calcularlos es barato. |

## Consecuencias

- **DONE:** el dominio Kotlin compila y pasan 61 tests, 5 nuevos (tema más flojo, repasos, cuenta atrás, certificado con las reglas de la web, logros, y nombre, contraseña y actividad contra un servidor falso).
- **VERIFY:**
  - la interfaz se compila en la CI;
  - hay que probar en el móvil el selector de fecha, «Practicarlo» (cambia de curso), «Ver en la web» y el cambio de contraseña sin perder la sesión.
