# Operación: vigilar, copiar, restaurar y volver atrás

Guía para mantener la web en marcha durante el piloto (#111). Las tareas marcadas **(tú)** las hace la persona dueña de las cuentas de Render, Neon y GitHub: el código no puede hacerlas.

Cada dato va marcado:

- **[verificado]**: comprobado en este repositorio.
- **[comprueba]**: depende de un servicio externo y hay que mirarlo en su panel, porque sus planes cambian.

## 1. Dos comprobaciones de salud

| Ruta | Qué dice | Toca la base de datos | Quién la usa |
|---|---|---|---|
| `GET /api/health` | El proceso está vivo. También dice si el email y Google están activos | No | Render (`healthCheckPath`): si falla, reinicia el servicio |
| `GET /api/v1/ready` | La API puede atender: la base de datos responde y el esquema está en la última migración | Sí (`SELECT 1` y `alembic_version`) | El monitor externo |

`/api/health` no mira la base de datos a propósito: si Neon tarda en despertar, Render entraría en un bucle de reinicios que no arregla nada.

Respuestas de `/api/v1/ready` **[verificado contra PostgreSQL 16 en local y en las pruebas]**:

| Situación | Código | Cuerpo |
|---|---|---|
| Todo bien | 200 | `{"status":"ok","database":"ok","migrations":"ok","database_ms":17}` |
| Falta una migración | 503 | `{"status":"error","database":"ok","migrations":"pending",…}` |
| La base de datos no responde | 503 | `{"status":"error","database":"error","migrations":"unknown"}` |

El error de verdad (host, causa) solo va al log de Render, nunca a la respuesta. La respuesta lleva `Cache-Control: no-store`.

## 2. Monitor externo y alertas (tú)

Un monitor gratuito avisa por email si la web o la API dejan de responder. Por ejemplo, UptimeRobot o Better Stack, en su plan gratuito **[comprueba sus límites al darte de alta]**. Crea tres monitores HTTP(S):

| Monitor | URL | Cada | Alerta si |
|---|---|---|---|
| Web | `https://marbi8891.github.io/python-learning-dashboard/` | 5 min | no responde 200 |
| API viva | `https://<tu-servicio>.onrender.com/api/health` | 5 min | no responde 200 |
| API lista | `https://<tu-servicio>.onrender.com/api/v1/ready` | 60 min | no responde 200 |

Por qué `/ready` va cada hora y no cada 5 minutos:

- Cada llamada despierta la base de datos de Neon.
- Con una llamada cada 5 minutos no se dormiría nunca y gastaría horas de cómputo del plan gratuito **[comprueba en Neon cuántas incluye]**.
- La ruta que más se usa, `/api/health`, mantiene despierto el servicio de Render sin tocar Neon.
- Ojo: un ping cada 5 minutos también gasta horas del plan gratuito de Render todo el mes **[comprueba en Render que te llegan para un servicio]**.

Pon como destino de las alertas tu email y, si quieres, el del profesor del piloto.

## 3. Copias de la base de datos

### Qué copia hay

1. **El historial de Neon (tú).** Neon permite restaurar la base de datos a un momento anterior durante un tiempo que depende del plan **[comprueba en Neon › tu proyecto › Restore cuánto cubre el tuyo]**. Es la vía más rápida para «ayer a las 10:00». No sirve si se borra el proyecto o la cuenta.
2. **Copias propias con `pg_dump` (tú, con el script).** Viven fuera de Neon. Sirven si el proyecto desaparece o si hace falta volver más atrás de lo que guarda el historial.

### Cuándo copiar (propuesta para el piloto)

- Antes de cada despliegue que traiga una migración nueva: un archivo nuevo en `backend/migrations/versions/`.
- Una vez por semana mientras dure el piloto.
- Antes de cualquier operación a mano sobre la base de datos.

Con copias semanales se pierde como mucho una semana (RPO de 7 días). El historial de Neon, mientras cubra, lo deja en minutos.

### Cómo copiar

Necesitas las herramientas cliente de PostgreSQL, de la misma versión que Neon o mayor:

- En Windows, el instalador de PostgreSQL, marcando solo «Command Line Tools».
- En Mac, `brew install libpq`.

```bash
python scripts/ops/copia_bd.py copia --origen "postgresql://…neon.tech/…?sslmode=require" --carpeta copias
```

El script:

- hace un volcado en formato personalizado;
- comprueba que se puede leer;
- guarda al lado un `.json` con las filas de cada tabla y el SHA-256 del archivo.

Nunca enseña la contraseña: la URL sale como `postgresql://usuario:***@…`.

**Las copias tienen datos personales** (emails y progreso de los alumnos). Normas:

- Guárdalas cifradas, por ejemplo en un disco cifrado o en un `.zip` con contraseña fuerte.
- Nunca en el repositorio: `copias/` y `*.dump` están en `.gitignore`.
- Nunca como artefacto de GitHub Actions: en un repositorio público cualquiera podría descargarlas.
- Borra las que tengan más de 3 meses, o las del piloto cuando acabe, según el registro de tratamientos (`docs/REGISTRO_TRATAMIENTOS.md`).

## 4. Restaurar

Nunca se restaura encima de producción a la primera. Primero se restaura en una base aparte, se comprueba, y solo entonces se cambia `DATABASE_URL`.

1. En Neon, crea una base de datos o una rama nueva y vacía, por ejemplo `pld_restaurada`.
2. Restaura la copia:

   ```bash
   python scripts/ops/copia_bd.py restaura copias/pld-AAAAMMDD-HHMMSS.dump \
     --destino "postgresql://…/pld_restaurada?sslmode=require" --confirmo pld_restaurada
   ```

   El script se niega a seguir si:

   - `--confirmo` no repite el nombre de la base de datos de destino;
   - el destino ya tiene tablas y no se ha pasado `--limpia`;
   - el archivo no coincide con su SHA-256.

   Al terminar, compara las filas de cada tabla con las de la copia.

   Si tus herramientas son más nuevas que el servidor, puede salir «Aviso: el servidor no conoce transaction_timeout». Es normal: `pg_dump` 17 o posterior escribe un ajuste que PostgreSQL 16 no tiene. El script solo pasa por alto ese tipo de error; cualquier otro detiene la restauración. **[verificado en CI: `pg_dump` 18 contra PostgreSQL 16]**
3. En Render › Environment, cambia `DATABASE_URL` por la de `pld_restaurada`. Render se reinicia y aplica las migraciones que falten (`alembic upgrade head`).
4. Comprueba que `/api/v1/ready` da 200 y que puedes entrar con una cuenta de prueba.
5. Anota el incidente según `docs/INCIDENTES.md`.

### Ensayo medido [verificado el 12/11/2026, PostgreSQL 16 en local]

Datos sintéticos: 503 usuarios y 2.500 estados de curso, unos 10 MB en la base de datos. Es mucho más que un piloto de una clase.

| Paso | Tiempo |
|---|---|
| Copia (`pg_dump`, 0,2 MB comprimido) | 0,2 s |
| Restauración en una base vacía, con la comparación de filas | 0,3 s |
| API arrancada sobre la base restaurada: `/ready` da 200 y una cuenta de prueba entra (y una contraseña mala da 401) | menos de 5 s |

Con Neon por internet los tiempos subirán, sobre todo la red y el despertar de la base de datos **[comprueba haciendo tú el ensayo una vez]**. Aun así, el tiempo de vuelta (RTO) lo marcan los pasos a mano: crear la base, cambiar la variable en Render y esperar el reinicio. Calcula unos 15 a 30 minutos.

El mismo ensayo se repite en cada CI: `backend/tests/test_copia_bd.py` usa el PostgreSQL del job. Migra una base, la copia, la restaura en otra, compara las filas y comprueba que no restaura sin confirmar ni una copia alterada.

## 5. Volver atrás tras un despliegue malo

| Parte | Cómo se despliega | Cómo se vuelve atrás |
|---|---|---|
| Web (GitHub Pages) | Cada merge a `main` | En GitHub, botón **Revert** del PR culpable. Hace un PR nuevo; al fusionarlo, Pages publica la versión anterior en unos minutos |
| API (Render) | Cada cambio en `main` (Render despliega solo; `render.yaml` no filtra rutas) | En Render › Events, **Rollback** al despliegue anterior. Es inmediato y no toca la base de datos |
| Base de datos | Migraciones de Alembic al arrancar | Ver abajo |

Con migraciones, cuidado:

- Si el despliegue malo trae una migración, un rollback de Render deja código viejo con un esquema nuevo.
- Las migraciones de este proyecto solo añaden: columnas con valor por defecto, tablas nuevas. El código anterior suele seguir funcionando con ellas, y `/api/v1/ready` lo dirá.
- Si no funciona:
  1. Restaura la copia hecha justo antes del despliegue (sección 4).
  2. Después, haz el rollback de Render.
- No ejecutes `alembic downgrade` sobre producción sin una copia reciente: algunas bajadas borran columnas y sus datos.

Después de volver atrás, arregla el fallo en una rama nueva con su prueba de regresión, como pide `CLAUDE.md`.
