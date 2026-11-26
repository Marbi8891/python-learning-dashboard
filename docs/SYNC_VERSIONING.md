# Versiones de los documentos sincronizados (PLD-003)

Cómo se evita que dos pestañas, dos dispositivos o un cliente antiguo se pisen el progreso guardado
en la cuenta. Código: `backend/app/state_documents.py` (servidor) y `frontend/js/doc-sync.js`
(cliente). Contrato de la API: [API.md](API.md) § *Progress documents and versions*.

## 1. Qué había antes de este cambio

El control de versiones existe desde #77 (AUD-001): cada documento (`pcap_states`, `course_states`)
tiene una columna `version`; el `PUT` lleva la versión leída y el servidor compara y escribe en una sola
sentencia `UPDATE … WHERE version = :leída`. Si no coincide, 409, y la web relee, fusiona y reintenta.
Eso ya era correcto y no se ha cambiado.

## 2. Hallazgos

| Id | Archivo y función | Descripción | Impacto | Prob. | Severidad |
|---|---|---|---|---|---|
| PLD-003-A | `state_documents.save` | Un `PUT` **sin** `version` (o con `null`) sobre un documento que ya existía se guardaba sin comprobar nada: `UPDATE` sin condición de versión. | Una pestaña con la web anterior a #77, un script o un fallo futuro del cliente borra en silencio lo guardado desde otro dispositivo (pérdida de progreso del propio alumno). No afecta a otros usuarios: la clave sale siempre del token. | Baja (la web actual siempre manda versión; el service worker usa primero la red) | Media |
| PLD-003-B | `doc-sync.js`, `push()` | La versión empieza en `null` hasta que la puerta de sincronización llama a `adopt()`. Hoy todos los almacenes la llaman antes de subir, pero nada en `doc-sync.js` lo garantizaba: un almacén nuevo que se olvidara de `adopt()` caería en PLD-003-A. | Igual que A, pero desde la web actual. | Baja | Baja |
| PLD-003-C | `state_documents.save` | Los conflictos no dejaban rastro en los logs: no se podía saber si había clientes antiguos ni cuántos 409 se producían. | Diagnóstico. | — | Baja |

Comprobado que **no** son fallos: dos `PUT` simultáneos con la misma versión (gana uno, el otro 409),
dos creaciones a la vez (la segunda choca con la clave primaria → 409), versión de un documento que ya
no existe (409), versión negativa (422), documentos de otro usuario o de otro curso (independientes).

## 3. Qué se ha cambiado

**Servidor.** Sin `version`:

- si el documento **no existe**, se crea (versión 1), como antes: no hay nada que pisar y así un
  cliente antiguo puede seguir haciendo su primer guardado;
- si **ya existe**, se responde **428 Precondition Required** y no se toca. Se registra un aviso
  `sync.version_missing` en el logger `pld.sync`.

Los 409 se registran como `sync.conflict` (nivel INFO) con el motivo (`version_antigua`, `no_existe`,
`creado_a_la_vez`) y las versiones. Los logs solo llevan el id interno del usuario y el curso, nunca el
contenido del progreso (probado en `test_conflict_is_logged_without_progress_data`).

**Cliente.** `doc-sync.js` nunca sube sin versión: si aún no la conoce, primero lee la cuenta, fusiona
y adopta su versión. Un 428 se trata igual que un 409 (releer, fusionar y reintentar, con el mismo
límite de `MAX_CONFLICT_RETRIES`).

### Por qué 428 y no 409 o 422

- 409 dice «la versión que leíste es vieja»; aquí no se leyó ninguna. 428 es el código de HTTP para
  «esta petición necesita una condición previa» (RFC 6585) y permite distinguirlo en los logs.
- 422 rechazaría también la creación sin versión y rompería el primer guardado de los clientes antiguos.

## 4. Compatibilidad

| Cliente | Antes | Ahora |
|---|---|---|
| Web actual (manda `version`) | Igual | Igual: no cambia ninguna respuesta |
| Web anterior a #77, primer guardado | 200 | 200 |
| Web anterior a #77, documento ya existente | 200 y **pisaba** lo de otro dispositivo | 428: queda «con fallo» en esa pestaña, sus datos siguen en el navegador y al recargar la web (versión nueva) se fusionan y se suben |
| Sin conexión | Se guarda en el navegador y se sube al volver | Igual: el modo sin conexión no depende del servidor |

La forma del JSON (`PcapStateIn`, `PcapStateOut`) no cambia: `version` sigue siendo opcional en el
esquema.

## 5. Fronteras de confianza

El documento de progreso es del propio alumno y lo escribe su navegador: el servidor no puede saber si
el contenido es «verdad», y no lo necesita (es progreso normal de estudio). Lo que sí garantiza:

- que cada usuario solo lee y escribe sus documentos (la clave sale del token);
- que un guardado no borra otro hecho entre medias sin que el cliente lo haya visto (versión);
- el tamaño máximo y el límite de escrituras por usuario.

Los exámenes verificados no usan estos documentos: los corrige el servidor
([HITOS_VERIFICADOS.md](HITOS_VERIFICADOS.md)).

## 6. Pruebas

- `backend/tests/test_state_versions.py` (SQLite, siempre): versiones que coinciden, antiguas, del
  futuro, inexistentes, 0 sobre un documento que existe, sin versión (crear sí, pisar no), `null`
  explícito, reintento del mismo `PUT` tras un éxito, logs sin datos del alumno.
- `backend/tests/test_state_versions_postgres.py` (PostgreSQL real, en CI con
  `STATE_TEST_DATABASE_URL`): 16 peticiones a la vez con la misma versión (gana exactamente una),
  16 creaciones a la vez, 16 pestañas que releen y fusionan hasta guardar (no se pierde ninguna
  respuesta), clientes sin versión a la vez que uno actual, usuarios y cursos distintos en paralelo y
  rollback tras un 409 con la misma sesión. Cada ejecución crea y borra su propio esquema.
- `tests/unit/doc-sync.test.mjs`: ningún `PUT` sale con `version: null`, lectura previa cuando no hay
  versión, 428 tratado como 409, reintento tras un fallo de red, cambio durante una subida, cambio de
  sesión mientras se lee.
- e2e `sync.spec.js`, `learn.spec.js`, `daw.spec.js`, `career.spec.js` y `account.spec.js`: la
  sincronización real con el navegador sigue funcionando.

Con el código anterior, 7 de estas pruebas fallan (se comprobó revirtiendo `state_documents.py`).

## 7. Límites y siguiente paso

- **No hay fusión en el servidor.** La fusión la hace cada almacén del navegador. El servidor solo
  impide escribir sobre lo que el cliente no ha visto.
- **Reintentos agotados.** Si hay más de `MAX_CONFLICT_RETRIES` conflictos seguidos, la subida queda
  «con fallo» y `uploader.js` la reintenta con espera; los datos no salen del navegador hasta entonces.
- **Versión obligatoria en el futuro.** Recomendación: en una próxima versión de la API (`/api/v2`)
  `version` pasa a ser obligatorio (422 si falta), también para crear (con `version: 0`). Antes de
  hacerlo en `/api/v1`, mirar en los logs de Render si sigue apareciendo `sync.version_missing`: si
  durante unas semanas no aparece, ya no quedan clientes que lo necesiten.