# ADR-0030: Una sola app en el móvil

- **Estado:** Aceptada
- **Fecha:** 2026-09-30
- **Relacionada con:** [ADR-0013](0013-firma-y-distribucion-android.md) (release firmado) y [ADR-0026](0026-cuenta-y-sincronizacion-en-la-app.md) (sincronización)

## Contexto

En el móvil del autor hay dos iconos: «Python PCAP» (release) y «Python PCAP (debug)».

- **Son dos apps distintas para Android:**
  - el APK de depuración usa `applicationId` `io.github.marbi8891.pld.debug` y está firmado con la clave de depuración del runner;
  - el de release usa `io.github.marbi8891.pld` y la clave del proyecto.
- **Cada una tiene su propio progreso:** Android no deja que una lea los datos de la otra.
- **Una no puede instalarse encima de la otra,** porque las firmas son distintas.
- **Origen del problema:** la CI publicaba los dos APK en cada ejecución de `main`, así que era fácil descargar e instalar el que no era.

## Decisión

1. **La app de uso diario es la de release** (`python-pcap-release`), que es la única que se actualiza encima sin perder nada.
2. **La CI solo genera y publica el APK de depuración cuando no hay release:**
   - en los pull requests;
   - o si faltan los secretos de firma.

   En `main` solo aparece `python-pcap-release`. Los tests y el lint siguen compilando la variante de depuración en cada ejecución.
3. **El progreso de la app de depuración se lleva a la de release con la sincronización que ya existe** (ADR-0026). No hace falta código nuevo:
   1. en «Python PCAP (debug)», iniciar sesión y pulsar «Sincronizar ahora»;
   2. en «Python PCAP», iniciar sesión con la misma cuenta y pulsar «Sincronizar ahora»;
   3. `PcapState.merge` junta los dos progresos sin perder nada de ninguno;
   4. el usuario desinstala «Python PCAP (debug)».

## Alternativas descartadas

| Opción | Por qué no |
| --- | --- |
| Quitar `applicationIdSuffix` para que la de depuración sustituya a la de release | Las firmas son distintas: Android rechazaría la instalación, o habría que desinstalar la release y se perdería su progreso. |
| Firmar la de depuración con la clave de release | La clave saldría a más compilaciones sin necesidad (ADR-0013). |
| Exportar e importar el progreso a un archivo en la app | Es código nuevo para un traspaso de una sola vez que la sincronización ya resuelve. Solo se haría si la app de depuración instalada es anterior a la 0.13.0, que no tiene inicio de sesión. |
| Dejar de compilar el APK de depuración | Sigue siendo útil para probar un pull request sin la clave de firma. |

## Consecuencias

- **DONE:** el YAML del workflow es válido y las condiciones de los dos APK son complementarias: en cada ejecución se publica uno de los dos, nunca los dos.
- **VERIFY:**
  - la próxima ejecución en `main` solo publica `python-pcap-release`;
  - la app de depuración instalada es la 0.13.0 o posterior, que tiene «Tu cuenta» en Perfil (la versión se ve en Ajustes → Aplicaciones → «Python PCAP (debug)»);
  - tras sincronizar, el progreso aparece en la release antes de desinstalar la de depuración.
- **NEEDS_HUMAN:** desinstalar «Python PCAP (debug)» lo hace el autor en el móvil.
