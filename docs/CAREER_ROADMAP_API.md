# Career Roadmap · API

El Career Roadmap **no añade endpoints**. Usa el mismo mecanismo que el planificador y los cursos
(DEC-011):

| Qué | Dónde |
|---|---|
| Catálogo de itinerarios | `frontend/data/career/index.json` (lista) y `frontend/data/career/<id>.json` (un itinerario). Archivos estáticos de la web, generados por `scripts/career/build_career.py` |
| Progreso del alumno | `GET` y `PUT /api/v1/course-state/career` |

## `GET /api/v1/course-state/career`

Necesita sesión (cookie o `Authorization: Bearer`). Devuelve `{data, updated_at, version}`; sin
documento, `{"data": {}, "updated_at": null, "version": 0}`.

## `PUT /api/v1/course-state/career`

Cuerpo `{"data": {…}, "version": n}`. Guarda el documento entero (la web ya lo ha fusionado con la copia
de la cuenta). Respuestas:

| Código | Cuándo |
|---|---|
| 200 | Guardado; devuelve la versión nueva |
| 401 | Sin sesión o sesión caducada |
| 409 | `version` no coincide: otra pestaña o dispositivo guardó antes. La web relee, fusiona y reintenta |
| 413 | Cuerpo de más de 300 kB |
| 422 | `data` de más de 200 kB o cuerpo no válido |
| 429 | Más de 120 escrituras por minuto del mismo usuario |

El formato de `data` está en [`CAREER_ROADMAP_DATA_MODEL.md`](CAREER_ROADMAP_DATA_MODEL.md). El servidor
lo guarda tal cual; la web lo valida al leerlo (`cleanCareer`), así que un documento manipulado no puede
inyectar HTML ni enlaces que no sean `https:`.

## Seguridad

- **Sin IDOR:** el usuario sale siempre del token. No hay ningún id de usuario en la URL ni en el cuerpo
  (pruebas en `tests/test_course_state.py` y `tests/test_security_isolation.py`).
- El documento entra en la exportación de datos (`/api/v1/users/me/export`, clave `courses.career`) y se
  borra con la cuenta.
- Lista cerrada de documentos (`COURSES` en `app/schemas.py`): un cliente no puede crear otros nombres.

## Por qué no `/api/roadmaps`, `/api/skills`…

El prompt original proponía 15 endpoints. El catálogo es contenido estático (como las lecciones de los
cursos de DAW) y el progreso ya tiene endpoint con versión y aislamiento. Un endpoint nuevo solo tendría
sentido si el servidor tuviera que validar entregas o calificar, algo que hoy no hace ninguna parte de la
plataforma.
