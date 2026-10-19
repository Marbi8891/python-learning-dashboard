# Documentación técnica del proyecto

**Proyecto:** Python Learning Dashboard  
**Repositorio:** https://github.com/Marbi8891/python-learning-dashboard  
**Demo web:** https://marbi8891.github.io/python-learning-dashboard/  
**Versión declarada por la API:** 1.0.0  
**Estado de referencia:** rama `main`. Consulta el repositorio para comprobar los cambios más recientes.

## 1. Descripción

Python Learning Dashboard es una plataforma educativa para aprender Python y preparar contenidos de programación de Desarrollo de Aplicaciones Web (DAW). Incluye teoría, ejemplos ejecutables, ejercicios con corrección automática, un plan de estudio adaptativo, seguimiento del progreso y un módulo de preparación del examen PCAP.

El proyecto dispone de una aplicación web, una API REST en Python y una aplicación Android nativa. Comparten las fuentes de contenido educativo y, cuando el alumno inicia sesión y el backend está configurado, pueden sincronizar parte del progreso.

## 2. Objetivos

- Explicar los conceptos de Python con ejemplos pequeños y trazables.
- Permitir practicar y recibir información concreta sobre los errores.
- Recomendar qué estudiar a continuación a partir de resultados y repasos.
- Preparar el examen PCAP y reforzar contenidos de programación de DAW.
- Registrar el progreso de forma local y, opcionalmente, sincronizarlo entre dispositivos.
- Mantener el código verificable mediante pruebas automatizadas y documentación de decisiones.

## 3. Funcionalidades

### Aprendizaje por conceptos

El ciclo didáctico es: concepto, explicación, ejemplo, intento, análisis del resultado, nuevo intento y repaso. El núcleo educativo está organizado en cuatro áreas y 22 conceptos. El sistema da prioridad a los repasos pendientes y errores recientes; después propone conceptos importantes aún no dominados y contenido nuevo si se cumplen sus prerrequisitos.

El banco del núcleo educativo contiene 128 ejercicios de seis tipos: opción múltiple, predicción de salida, completar código, ordenar instrucciones, localizar errores y escribir un programa con tests.

### Curso y examen PCAP

El curso incluye 27 lecciones. La zona de examen ofrece un simulacro de 40 preguntas en 65 minutos, práctica por bloques, fichas de repaso y una vista de preparación. El repositorio declara 126 preguntas originales en español e inglés, con comprobaciones asociadas.

### Consola Python

La ejecución de código educativo se realiza en el navegador con Pyodide, dentro de un Web Worker. El servidor no ejecuta el código arbitrario escrito por el alumno. La ejecución en navegador tiene un límite de tiempo para interrumpir programas que no terminan.

### Seguimiento y planificación

La aplicación permite consultar dominio por conceptos, repasos pendientes, errores frecuentes, actividad y resultados de simulacros. Ofrece XP, rachas, logros y un certificado imprimible no oficial. Con una cuenta configurada, parte de ese estado puede sincronizarse con el backend.

### Cuenta y privacidad

El backend incluye registro e inicio de sesión, recuperación de contraseña cuando el correo saliente está configurado, consulta del perfil, exportación de datos y borrado de cuenta. Los recursos de cada usuario se obtienen de la sesión validada, no de un identificador arbitrario enviado por el cliente.

### Python Tutor mediante A2A

El backend contiene una integración opcional del protocolo A2A para el tutor de Python. Está desactivada por defecto. La documentación del proyecto describe Ollama local como proveedor predeterminado al activarla; Anthropic es opcional. El tutor analiza el código como texto y no lo ejecuta en el servidor.

### Aplicación Android

El directorio `android/` contiene una aplicación nativa desarrollada con Kotlin y Jetpack Compose. Reutiliza los datos del curso y replica parte de la lógica educativa. El propio README diferencia funciones probadas, pendientes y por validar en un dispositivo; revisa esa tabla antes de presentar todas las funciones móviles como terminadas.

## 4. Arquitectura

El sistema se divide en cuatro componentes principales:

| Componente | Tecnologías | Responsabilidad |
| --- | --- | --- |
| Web, `frontend/` | HTML, CSS, JavaScript ES Modules, Pyodide | Interfaz, cursos, consola, ejercicios y progreso local |
| API, `backend/` | FastAPI, SQLAlchemy, Alembic, Pydantic Settings | API REST, autenticación, persistencia y sincronización |
| Aplicación móvil, `android/` | Kotlin, Jetpack Compose | Aprendizaje y práctica en Android |
| Herramientas de contenido, `scripts/` | Python y scripts de comprobación | Generar/verificar bancos de ejercicios y contenido del curso |

### Flujo de una petición típica

1. El alumno interactúa con una vista de la web o de la aplicación Android.
2. La web ejecuta el código de práctica localmente en Pyodide. Para datos sincronizados, llama a la API.
3. FastAPI valida la petición y, cuando corresponde, la sesión y los datos recibidos.
4. La lógica de la API lee o actualiza los modelos de datos mediante SQLAlchemy.
5. La respuesta vuelve al cliente, que actualiza el progreso y la interfaz.

### Esquema simplificado

```text
                         frontend/data/*.json
                         /        |        \
                        v         v         v
                 Web (HTML/JS)  Scripts   Backend (FastAPI)
                     |             |          |
              Pyodide / Worker     |      SQLAlchemy
                     |             |          |
                 Resultado       Tests    PostgreSQL / SQLite
                     |
              API /api/v1 cuando se requiere sincronización

                 Android (Kotlin / Compose)
                         |
                    API /api/v1
```

Los JSON de `frontend/data/` son una fuente compartida para las lecciones y bancos de contenido. Los ficheros generados por scripts deben actualizarse mediante su generador, no editando manualmente el JSON generado.

## 5. Estructura del repositorio

```text
python-learning-dashboard/
├── android/                 Aplicación Android en Kotlin
├── backend/
│   ├── app/                  Aplicación FastAPI, modelos, seguridad y routers
│   ├── migrations/           Migraciones de base de datos con Alembic
│   ├── tests/                Pruebas del backend
│   ├── Dockerfile
│   └── requirements*.txt     Dependencias Python
├── docs/
│   ├── adr/                  Registros de decisiones arquitectónicas
│   ├── API.md                Referencia de endpoints
│   ├── ARCHITECTURE.md       Descripción técnica detallada
│   ├── DEPLOY.md             Despliegue
│   ├── a2a.md                Tutor A2A y proveedores de modelo
│   └── EJECUTAR-EN-WINDOWS.md
├── e2e/                      Pruebas end-to-end y accesibilidad
├── frontend/
│   ├── data/                 Lecciones y bancos de ejercicios
│   ├── js/                   Lógica y vistas de la aplicación
│   ├── py/                   Motor de corrección Python compartido
│   ├── css/
│   └── config.js             Configuración pública del frontend
├── scripts/
│   ├── learning/             Generación/comprobación del núcleo educativo
│   ├── courses/              Generadores de cursos
│   └── run_local.py          Lanzador local
├── tests/unit/               Pruebas unitarias de frontend
├── docker-compose.yml        Entorno local con PostgreSQL, API y web
├── render.yaml               Definición de despliegue de Render
├── Iniciar-Dashboard.bat     Lanzador local para Windows
├── README.md                 Introducción y guía rápida
└── package.json              Comandos de pruebas JavaScript
```

Esta estructura es orientativa; para ubicar todos los archivos y sus responsabilidades, consulta también [ARCHITECTURE.md](ARCHITECTURE.md).

## 6. Tecnologías principales

| Tecnología | Uso |
| --- | --- |
| Python | Backend y herramientas de validación del contenido |
| FastAPI | API HTTP |
| SQLAlchemy y Alembic | Acceso a datos y migraciones |
| PostgreSQL / SQLite | Persistencia remota o local |
| Pydantic Settings | Configuración a partir del entorno |
| PyJWT y Argon2 | Tokens de acceso y hash de contraseñas |
| HTML, CSS y JavaScript | Aplicación web sin framework ni paso de compilación |
| Pyodide y Web Workers | Ejecución aislada del código de práctica en el navegador |
| Kotlin y Jetpack Compose | Aplicación Android |
| Node.js y Playwright | Pruebas unitarias de frontend y pruebas E2E |
| Docker Compose | Entorno reproducible de desarrollo |
| GitHub Actions | Integración continua, comprobaciones y despliegues |

Las versiones y rangos de dependencias vigentes están definidos en los ficheros de configuración del repositorio.

## 7. Instalación y ejecución

### Opción A: Windows

1. Instala Python 3.11 o superior.
2. Descarga o clona el repositorio.
3. Ejecuta `Iniciar-Dashboard.bat`.
4. El lanzador prepara el entorno local y abre el navegador en una dirección de loopback, normalmente `http://127.0.0.1:8000`.

La guía específica, con requisitos y solución de problemas, está en [EJECUTAR-EN-WINDOWS.md](EJECUTAR-EN-WINDOWS.md).

### Opción B: backend en local

Desde la raíz del repositorio:

```bash
git clone https://github.com/Marbi8891/python-learning-dashboard.git
cd python-learning-dashboard

python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1

pip install -r backend/requirements-dev.txt
```

Configura el entorno:

```bash
cp backend/.env.example backend/.env
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Copia el valor generado a `JWT_SECRET` en `backend/.env`. No reutilices la cadena de ejemplo ni subas secretos a Git. Continúa desde la carpeta `backend`:

```bash
cd backend
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

La API estará disponible en `http://127.0.0.1:8000`. Los endpoints interactivos de FastAPI solo se muestran si `ENABLE_DOCS=true` está configurado en el entorno.

### Opción C: Docker Compose

Necesitas Docker y Docker Compose. Define un secreto suficientemente largo en la variable `JWT_SECRET` y ejecuta:

```bash
# Linux/macOS
export JWT_SECRET="$(python3 -c 'import secrets; print(secrets.token_urlsafe(48))')"
docker compose up --build
```

En PowerShell:

```powershell
$env:JWT_SECRET = py -c "import secrets; print(secrets.token_urlsafe(48))"
docker compose up --build
```

Direcciones del entorno Compose definido en el repositorio:

- Web: http://localhost:5500
- API: http://localhost:8000
- Documentación interactiva, con `ENABLE_DOCS=true`: http://localhost:8000/docs

### Frontend estático por separado

Para servir la carpeta web sin compilar:

```bash
cd frontend
python -m http.server 5500
```

Abre http://localhost:5500. Para usar funciones de cuenta y sincronización, configura una API accesible desde el navegador y sus orígenes CORS permitidos. Sin backend, la experiencia de aprendizaje que depende solo del navegador puede seguir funcionando, pero la cuenta y la sincronización remota no estarán disponibles.

## 8. Configuración

La configuración del servidor se lee desde variables de entorno y, en desarrollo, desde `backend/.env`. No incluyas en Git contraseñas, claves privadas ni cadenas de conexión reales.

| Variable | Para qué sirve | Consideraciones |
| --- | --- | --- |
| `DATABASE_URL` | Base de datos | SQLite para local; PostgreSQL en el despliegue |
| `JWT_SECRET` | Firma de los tokens de sesión | Obligatoria para arrancar; genera un valor aleatorio |
| `CORS_ORIGINS` | Orígenes autorizados para llamar a la API | Lista JSON de orígenes, sin comodín en despliegues con credenciales |
| `FRONTEND_URL` | URL pública de la web usada en enlaces | Debe coincidir con el despliegue |
| `ENABLE_DOCS` | Activa Swagger/OpenAPI | Mantener desactivado en producción salvo decisión explícita |
| `BREVO_API_KEY` / `SMTP_*` | Envío de recuperación de contraseña | Sin un proveedor configurado, los correos no se envían |
| `A2A_ENABLED` | Activa las rutas del tutor A2A | Desactivado por defecto |
| `A2A_MODEL_PROVIDER` | Proveedor del modelo del tutor | Ollama, Anthropic o mock según configuración y dependencias |
| `A2A_OLLAMA_BASE_URL` | Dirección del servicio Ollama | Configuración del backend, no de una petición del alumno |
| `ANTHROPIC_API_KEY` | Clave para el proveedor Anthropic | Secreto opcional; no colocarlo en el frontend |

La referencia completa y los valores predeterminados se encuentran en `backend/app/config.py` y `backend/.env.example`. Consulta [DEPLOY.md](DEPLOY.md) para Render, la base de datos remota, correo y publicación.

## 9. API REST

La superficie recomendada para integraciones nuevas está versionada bajo `/api/v1`. Las rutas heredadas bajo `/api` se conservan temporalmente para compatibilidad y están marcadas como obsoletas.

| Recurso | Ejemplos de operaciones |
| --- | --- |
| Salud | `GET /api/health` |
| Módulos y lecciones | `GET /api/v1/modules`, `GET /api/v1/lessons/{slug}` |
| Autenticación | Registro, login, logout y cierre global de sesiones |
| Perfil y datos personales | Perfil actual, actividad, exportación y eliminación |
| Progreso | Consultar, marcar y desmarcar lecciones |
| Intentos | Registrar intentos y consultar los más recientes |
| PCAP | Consultar y guardar el estado de preparación |
| Cursos DAW | Leer y guardar el estado por curso |
| Panel del alumno | Resumen y actividad paginada |

Los recursos privados deben resolver el usuario desde la sesión validada; nunca debe confiarse en un `user_id` enviado en la petición. La lista completa de rutas, autenticación y compatibilidad está en [API.md](API.md).

## 10. Seguridad, privacidad y límites

- Las contraseñas se almacenan mediante hash Argon2; los tokens de acceso se firman con JWT.
- La API define límites de peticiones, validación de esquemas, cabeceras de seguridad y tamaño máximo de cuerpo.
- Los datos personales y el progreso son de cada cuenta; se ofrecen funciones de exportación y borrado.
- La web ejecuta el código de prácticas en un Web Worker con Pyodide y límite de tiempo. El backend no debe ejecutar código proporcionado por el alumno.
- El frontend y el backend tienen orígenes CORS explícitos.
- Las claves de proveedores, secretos de sesión y credenciales de base de datos deben almacenarse como variables de entorno o secretos del proveedor.
- A2A está desactivado por defecto. Al activarlo, deben revisarse sus límites, la disponibilidad del proveedor y la política de tratamiento de consultas.

La documentación describe controles técnicos; no equivale a una auditoría de seguridad ni constituye por sí sola una garantía de cumplimiento legal. Antes de abrir el servicio a usuarios reales, revisa la política de privacidad, los acuerdos de tratamiento de proveedores, el correo de recuperación y la configuración del despliegue. Consulta [SECURITY.md](../SECURITY.md) y [a2a.md](a2a.md).

## 11. Pruebas y calidad

Los comandos que figuran a continuación están declarados por el proyecto. Para obtener una conclusión sobre el estado actual, ejecútalos en el commit que se vaya a publicar; la existencia de una suite no implica que haya pasado en el entorno local.

### Backend

```bash
cd backend
pip install -r requirements-dev.txt
ruff check . ../e2e ../scripts
ruff format --check . ../e2e ../scripts
python -m pytest -q --cov=app --cov-report=term-missing --cov-fail-under=100
```

### Frontend: lógica unitaria

Desde la raíz:

```bash
npm ci
npm run test:unit
```

### Contenido educativo generado

```bash
python scripts/learning/build_learning.py --check
```

### Pruebas E2E y accesibilidad

```bash
npx playwright install --with-deps chromium
npm run test:e2e
```

La integración continua de GitHub Actions incluye lint, formato, auditoría de dependencias, pruebas de backend, comprobaciones de contenido, migraciones y pruebas end-to-end. Consulta la pestaña **Actions** y el workflow correspondiente para conocer el resultado de la última ejecución.

## 12. Despliegue

El diseño previsto separa servicios:

- **Frontend:** GitHub Pages.
- **Backend:** contenedor Docker desplegable en Render u otro servidor compatible.
- **Base de datos remota:** PostgreSQL.
- **Android:** compilación y artefactos mediante GitHub Actions.

La guía operativa está en [DEPLOY.md](DEPLOY.md). Antes de publicar una versión, comprueba que la URL de API, CORS, las variables secretas, el correo de recuperación y la política de privacidad coinciden con el entorno real.

## 13. Decisiones de diseño

Las decisiones de arquitectura se documentan en registros ADR situados en [`docs/adr/`](adr/). Entre los temas documentados están la separación frontend/API, el modelo de contenido, autenticación, ejecución de ejercicios, gamificación, despliegue, estudio por conceptos, agentes A2A y panel del alumno.

No todas las ADR tienen necesariamente el mismo estado: algunas reflejan funciones implementadas y otras siguen siendo propuestas. Verifica el encabezado de la ADR antes de describir una decisión propuesta como definitiva.

## 14. Documentación relacionada

- [README del proyecto](../README.md): presentación y guía rápida.
- [Arquitectura](ARCHITECTURE.md): detalle por componentes, módulos y datos.
- [Referencia de API](API.md): rutas, autenticación y reglas de compatibilidad.
- [Despliegue](DEPLOY.md): GitHub Pages, Render, base de datos y correo.
- [Ejecución en Windows](EJECUTAR-EN-WINDOWS.md): instalación y resolución de problemas.
- [Tutor A2A](a2a.md): arquitectura, proveedor, límites y minimización de datos.
- [Guion de demostración y defensa](DEMO-Y-DEFENSA.md): recorrido de presentación y preguntas técnicas.
- [Seguridad](../SECURITY.md): cómo reportar problemas.
- [Contribución](../CONTRIBUTING.md): normas para colaborar.
- [Licencia MIT](../LICENSE).

## 15. Cómo mantener esta documentación

Al introducir una nueva funcionalidad, actualiza el documento que corresponda y enlázalo desde el README si es una guía de uso frecuente. Si cambia la arquitectura, registra el motivo y las consecuencias en una ADR. Si cambia una ruta, actualiza `docs/API.md`. Si cambia el proceso de instalación o despliegue, actualiza la guía específica y valida las instrucciones ejecutándolas en un entorno limpio.
