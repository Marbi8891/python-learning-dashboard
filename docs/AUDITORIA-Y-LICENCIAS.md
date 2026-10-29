# Auditoría inicial y licencias de fuentes de contenido

Fecha: 26 de octubre de 2026. Estado examinado: `main` con cambios locales sin commit (recorte del tutor, la app Android, los agentes y `docs/legal`).

Este documento no es asesoramiento jurídico. La revisión de licencias se ha hecho leyendo los archivos `LICENSE` y los README de cada repositorio; antes de comercializar conviene que lo revise un profesional.

## 1. Estado de Git

- Rama: `main`. Cambios sin commit: archivos borrados, modificados y nuevos (ver el informe final).
- No hay stash ni commits locales sin subir.
- **Recomendación:** antes de seguir, pasar los cambios a una rama. `git switch -c chore/recorte-proyecto` crea la rama y se lleva los cambios sin commit, sin perder nada. Después se puede hacer commit en esa rama y abrir un pull request. `CLAUDE.md` pide no trabajar directamente en `main`.

## 2. Verificación del estado actual

| Prueba | Resultado |
|---|---|
| Ruff (lint y formato) | Sin errores |
| Backend (pytest) | 542 pruebas, 100 % de cobertura |
| Núcleo por conceptos (`build_learning.py --check`) | 22 conceptos y 131 ejercicios comprobados |
| Cursos de DAW (`--check` de los 5 cursos) | Todos al día y con las respuestas comprobadas |
| Frontend (`npm run test:unit`) | 67 pruebas, 0 fallos |
| End-to-end (Playwright) | Ver apartado 2.1 |
| `npm audit` | 0 vulnerabilidades |
| `pip-audit` | No se pudo ejecutar en local (error de certificado SSL al consultar PyPI); lo ejecuta la CI |

### 2.1 End-to-end

La primera ejecución pareció terminar bien, pero el código 0 era el de `tail`, no el de Playwright. En este equipo con Windows fallaban casi todas las pruebas, también con el `HEAD` original: `python -m http.server` (HTTP/1.0) cortaba una de las dos peticiones simultáneas a `data/lessons.json` (`ERR_CONNECTION_RESET`). Se ha corregido con `e2e/serve_frontend.py` (HTTP/1.1). El resto de fallos aparecían solo al ejecutar en paralelo (ver el informe final).

No se encontraron dependencias funcionales de los componentes eliminados: el backend y el frontend arrancan y pasan las pruebas sin ellos. La tabla `tutor_usage` se elimina con una migración nueva en vez de borrar la antigua, para no romper bases de datos que ya la aplicaron.

## 3. Arquitectura confirmada

- Frontend: HTML, CSS y JavaScript con módulos ES, sin framework ni compilación (`frontend/js/`).
- Python en el navegador: Pyodide cargado desde jsDelivr y ejecutado en un Web Worker (`pyodide-worker.js`, `python-runner.js`). El worker corta la ejecución a los 10 s y desactiva `fetch`, `XMLHttpRequest`, `WebSocket` y similares después de cargar Python.
- Backend: FastAPI + SQLAlchemy 2 + Alembic, PostgreSQL en producción y SQLite en local.
- Persistencia: `localStorage` sin cuenta; con cuenta, documentos JSON por usuario en `/api/v1/pcap-state` y `/api/v1/course-state/{curso}`.
- Despliegue: GitHub Pages (web), Render con Docker (API), Neon (BD), GitHub Actions.
- Temario: JSON generados por scripts (`scripts/courses/`, `scripts/learning/`) que ejecutan cada respuesta.

## 4. Problemas encontrados, por impacto y esfuerzo

| Id | Problema | Impacto | Esfuerzo |
|---|---|---|---|
| P1 | El `LICENSE` (MIT) no distingue entre código y contenido. Si el temario también es MIT, cualquiera puede copiarlo y venderlo. Hay que decidir la licencia del contenido antes de comercializar. | Alto | Bajo (decisión tuya) |
| P2 | El progreso, la XP y los certificados los declara el navegador: el servidor guarda lo que recibe sin comprobarlo. Para un producto de pago con certificados haría falta verificarlo en el servidor. | Alto | Alto |
| P3 | Marcas: «Python» es una marca de la PSF y «PCAP», de Python Institute. El uso descriptivo suele estar permitido, pero el nombre comercial y los logotipos hay que revisarlos con sus políticas de marca. | Alto | Bajo |
| P4 | Huecos del temario respecto a la ruta pedida: CSV y JSON, codificación de texto, entornos virtuales y `pip`, iteradores, decoradores, context managers, anotaciones de tipos, `unittest`, HTTP y consumo de APIs, FastAPI (ahora solo hay Flask en «Después del PCAP») y proyectos guiados. Las expresiones regulares solo aparecen en la UT5 de Programación. | Alto | Alto |
| P5 | El plan gratuito de Render apaga la API sin uso y los límites de intentos viven en memoria (una sola instancia). Vale para un proyecto educativo, no para un servicio de pago. | Medio | Medio |
| P6 | Pyodide se carga de jsDelivr sin SRI, y la CSP va en `<meta>` con `style-src 'unsafe-inline'`. GitHub Pages no permite cabeceras propias, así que `frame-ancestors` no se puede aplicar por `<meta>`. | Medio | Medio |
| P7 | El modelo de ejercicio (`learning.json`) no tiene campos de procedencia ni de licencia. Hacen falta si algún día se incorpora material de terceros. | Medio | Bajo |
| P8 | ~~Dos pruebas fallaban en Windows sin `PYTHONUTF8=1`~~. **Resuelto:** las pruebas abren los archivos en UTF-8 y ejecutan los ejemplos en modo UTF-8, como Pyodide. | Bajo | Bajo |
| P9 | ~~Las imágenes de la memoria (`docs/memoria/img/*.png`) siguen mostrando la app Android~~. **Resuelto:** los PNG se han regenerado con Graphviz desde los `.dot`, y el modelo de datos incluye ya `account_events` y `email_verified_at`. | Bajo | Bajo |
| P10 | ~~Rutas antiguas `/api/...` mantenidas por la app Android~~. **Resuelto:** se han quitado; solo queda `/api/health` porque Render la usa como `healthCheckPath`. | Bajo | Bajo |

Límites conocidos del Web Worker: es aislamiento de hilo, no una barrera de seguridad completa. El código del alumno se ejecuta en el mismo origen que la web, el corte de red depende de sobrescribir APIs del worker y la memoria no está limitada más allá de lo que imponga el navegador.

### Limitaciones de Pyodide para el curso

- Sin red después de cargar (por diseño del proyecto): no se pueden hacer ejemplos reales de `requests` ni de consumo de APIs. Habría que simularlos o explicarlos sin ejecutarlos.
- `pytest` se instala con `micropip` desde la red, así que no está disponible con la red cerrada. `unittest` y `assert` sí funcionan.
- No hay hilos ni subprocesos, y el sistema de archivos es virtual y se pierde al recargar.
- FastAPI, `venv` y `pip` no se pueden ejecutar en el navegador: esos temas solo pueden tener ejemplos para copiar y ejecutar en el ordenador del alumno.

## 5. Licencias de dependencias del proyecto

| Componente | Licencia | Observación |
|---|---|---|
| FastAPI, SQLAlchemy, Alembic, Pydantic, Uvicorn, PyJWT | MIT o BSD | Compatibles con uso comercial |
| argon2-cffi, httpx, google-auth | MIT, BSD o Apache-2.0 | Compatibles |
| psycopg / psycopg-binary | LGPL-3.0 | Uso en servidor sin modificarla: compatible; si se distribuye modificada, hay obligaciones de la LGPL |
| certifi | MPL-2.0 | Compatible |
| email-validator | Unlicense | Compatible |
| Pyodide | MPL-2.0 | Se carga de jsDelivr, no se distribuye en el repositorio |
| highlight.js (`frontend/vendor/highlight/`) | BSD-3-Clause | Licencia incluida en la carpeta |
| Fuentes Inter, JetBrains Mono y Fraunces | SIL OFL 1.1 | Licencias incluidas en `frontend/fonts/` |
| Playwright, axe-core (solo pruebas) | Apache-2.0 y MPL-2.0 | No se distribuyen con la web |

## 6. Fuentes de contenido revisadas

Ninguna de estas fuentes se ha copiado al proyecto. Sirven como referencia para escribir contenido propio.

| Id | Recurso | Titular | URL | Commit | Licencia | Uso comercial | Estado | Observaciones |
|---|---|---|---|---|---|---|---|---|
| F1 | Exercism Python track | Exercism | https://github.com/exercism/python | `6105f6d9d3ef` | MIT (repositorio). Incluye material de la documentación de Python con sus licencias propias | Sí, conservando el aviso MIT | Revisado | Muchos enunciados vienen de `exercism/problem-specifications` (MIT). Se puede reutilizar con atribución, pero están en inglés y hay que traducirlos y adaptarlos |
| F2 | Python Handbook | neikiri | https://github.com/neikiri/python-handbook | `a9ab920a1fe7` | MIT | Sí, conservando el aviso | Revisado con dudas | Repositorio reciente (mayo de 2026) con una sola estrella; no se ha comprobado si su contenido procede de otras fuentes. Usar solo como referencia |
| F3 | Python for Everyone | sajankoira | https://github.com/sajankoira/python-for-everyone | `a311fc28f58b` | MIT | Según la licencia, sí | **Procedencia dudosa** | Creado en agosto de 2026. Su `FOR_SAJAN_README.md` indica que el repositorio se generó en otro espacio de trabajo y se subió como zip. El nombre coincide con *Python for Everybody* de C. Severance (CC BY-NC-SA). No copiar nada hasta aclarar su origen |
| F4 | 30 Days of Python | Asabeneh Yetayeh | https://github.com/asabeneh/30-days-of-python | `50c11a80a6e3` | **Sin licencia** (no hay `LICENSE` ni aviso en el README) | **No**: sin licencia, todos los derechos son del autor | Bloqueado | Solo referencia para inspirarse en el orden de los temas. No copiar textos ni ejercicios |
| F5 | Documentación oficial de Python | Python Software Foundation | https://docs.python.org/3/ | Python 3.14 | Documentación: PSF License Agreement. Ejemplos de código (desde 3.8.6): PSF y Zero-Clause BSD | Sí | Revisado | Los ejemplos de código se pueden usar sin atribución (0BSD). Los textos, bajo la licencia PSF, conservando su aviso. Mejor enlazar y escribir explicaciones propias |
| F6 | Python Regular Expressions | Sundeep Agarwal | https://github.com/learnbyexample/py_regular_expressions | `b2c5735f5ba4` | Código: MIT. **Libro: CC BY-NC-SA 4.0** | Código: sí. **Texto del libro: no** | Bloqueado para el texto | Los ejemplos de código se pueden usar con atribución MIT; las explicaciones del libro no se pueden usar en una versión comercial |

Requisitos si en el futuro se reutiliza algo:

- F1, F2, F6 (código): incluir el aviso de copyright y el texto de la licencia MIT de cada uno.
- F5: conservar el aviso de la licencia PSF si se reproduce texto de la documentación.
- Registrar en cada ejercicio de dónde viene (ver P7).

## 7. Pendiente de tu decisión

1. Pasar los cambios a una rama (apartado 1).
2. Licencia del contenido para la versión comercial (P1).
3. Si el curso nuevo amplía el temario existente o es un curso aparte. Ya hay tres rutas de Python: PCAP, núcleo por conceptos y Programación de DAW.
4. El resto de tus instrucciones: el texto pegado se cortaba en el apartado 6 («Excepc…»), así que no he empezado el curso ni el motor de ejercicios.
