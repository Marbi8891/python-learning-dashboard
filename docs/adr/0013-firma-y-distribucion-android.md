# ADR-0013: Firma de release y distribución de la app Android

- **Estado:** Aceptada
- **Fecha:** 2026-09-27

## Contexto

El APK de la entrega 2 se instala en el móvil del autor, pero Play Protect y la seguridad de Xiaomi lo marcan como app no segura. Hay tres causas:

1. **Instalación fuera de la tienda.** Cualquier APK desconocido recibe el aviso.
2. **Firma de depuración de la CI.** Cada runner de GitHub Actions genera su propia clave de depuración. VERIFY: `setup-java` guarda en caché `~/.gradle`, no `~/.android`, así que cada ejecución firmaría con una clave distinta. Si es así, un APK nuevo no se instala encima del anterior.
3. **Desarrollador desconocido para Google.** Desde 2027 Android exige en todo el mundo que el desarrollador esté verificado. Sin eso, la app no se podrá instalar en móviles certificados. En Brasil, Indonesia, Singapur y Tailandia la exigencia empieza el 30 de septiembre de 2026.

## Opciones

| Opción | Pros | Contras |
|---|---|---|
| A. Firma de release propia en la CI | Gratis. La firma es estable y las actualizaciones se instalan sin desinstalar. Es requisito de B y C | Si se pierde la clave, no se puede volver a actualizar la app |
| B. Cuenta gratuita de distribución limitada en Android Developer Console | Gratis y sin documento de identidad. Registra el paquete y la clave. Cumple la norma de 2027 para un máximo de 20 dispositivos | VERIFY: no está confirmado que quite ya el aviso de Xiaomi |
| C. Google Play (prueba interna) | Instalación desde la tienda, sin avisos | 25 $. Para producción, las cuentas personales nuevas necesitan una prueba cerrada de 12 testers durante 14 días. Obliga a mantener ficha y política de privacidad |
| D. Solo ADB | Queda fuera de la norma de 2027 | Necesita cable USB. El aviso de app desconocida sigue |
| E. Desactivar Play Protect o la seguridad de Xiaomi | Quita el aviso | Quita también la protección real. Descartada |

## Decisión

**A + B.** C queda para cuando otras personas quieran instalar la app.

- La CI genera `app-release.apk` firmado solo si existen tres secretos: `PLD_KEYSTORE_BASE64`, `PLD_KEYSTORE_PASSWORD` y `PLD_KEY_ALIAS`. La clave se escribe en el disco temporal del runner y se borra al terminar. Nunca se firman los pull requests.
- Gradle lee la clave de variables de entorno. En el repo no hay claves ni contraseñas, y `.gitignore` excluye `*.jks`, `*.keystore` y `*.p12`.
- `apksigner verify` comprueba la firma en la CI e imprime la huella SHA-256 que pide Android Developer Console.
- La build de depuración usa el sufijo `.debug` y se llama "Python PCAP (debug)". Así convive con la release sin pisarla.
- R8 sigue activado en release para reducir el tamaño. VERIFY: el APK minificado tiene que probarse en el móvil.

## Consecuencias

- **Un solo cambio de firma:** para pasar a la release hay que desinstalar la app actual, que tiene el mismo paquete y otra firma. Se pierde el progreso guardado en el móvil. Es poco, porque se instaló el 26/09. No merece la pena programar una exportación, porque tampoco se podría instalar encima sin desinstalar.
- **La clave es un activo crítico.** Hay que guardar una copia del `.jks` y su contraseña fuera del PC, por ejemplo en un gestor de contraseñas. Si se pierde, la app tendría que publicarse con otro paquete.
- **ASSUMPTION:** una sola contraseña para el almacén y la clave (el formato PKCS12 que crea `keytool` las iguala).
- **Pasos manuales del autor:** crear la clave, subir los secretos y crear la cuenta de Android Developer Console. El asistente no maneja claves ni cuentas.

## Fuentes

- Google, verificación de desarrolladores: https://support.google.com/android-developer-console/answer/16561738?hl=en
- https://thehackernews.com/2026/06/google-sets-sept-30-deadline-for.html
- https://www.testerscommunity.com/blog/google-play-closed-testing-requirements-2026
