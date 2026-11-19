# Itinerario DevOps: Linux, Docker, GitHub y Python

Estado: **diseño curricular inicial**. Este documento define el itinerario formativo que se incorporará a Python Learning Dashboard. No implica todavía que exista una nueva sección funcional en la interfaz.

## 1. Objetivo

Añadir a la plataforma un itinerario de formación DevOps de 9 meses, con 20 horas semanales, nivel de entrada intermedio y metodología académica. El alumno debe aprender a administrar Linux, construir y operar contenedores, trabajar con GitHub y automatizar tareas con Python.

El itinerario complementa los cursos de Python y DAW. No los sustituye ni modifica su temario.

## 2. Distribución semanal

| Área | Horas |
|---|---:|
| Linux | 5 |
| Docker | 4 |
| Git y GitHub | 3 |
| Python aplicado a DevOps | 6 |
| Integración, documentación y evaluación | 2 |
| **Total** | **20** |

Ritmo recomendado: cinco sesiones de cuatro horas de lunes a viernes. Cada sesión combina teoría, lectura técnica, laboratorio, ejercicios y registro de aprendizaje.

## 3. Plan de nueve meses

| Mes | Linux | Docker | GitHub | Python e integración |
|---|---|---|---|---|
| 1 | Terminal, sistema de archivos, permisos y procesos | Arquitectura, imágenes y contenedores | Git básico, commits y repositorios remotos | Sintaxis aplicada, módulos, ficheros y scripts |
| 2 | Usuarios, grupos, systemd, paquetes y SSH | Docker Engine, ejecución y ciclo de vida | Ramas, merge, conflictos y Pull Requests | subprocess, pathlib, logging y argparse |
| 3 | Redes, DNS, puertos, firewall y logs | Dockerfiles, capas y construcción | Issues, Projects, releases y versionado | APIs HTTP, JSON, pytest y calidad |
| 4 | Bash, cron, almacenamiento y backups | Redes, volúmenes y persistencia | GitHub Actions: eventos, jobs y artefactos | Automatización de tareas y consumo de APIs |
| 5 | Administración remota y hardening | Docker Compose y aplicaciones multicontenedor | CI para lint, tests y seguridad | FastAPI, configuración y PostgreSQL |
| 6 | Servicios y operación de servidores | Registros, publicación y despliegue | CD y GitHub Container Registry (GHCR) | Scripts de despliegue y operaciones idempotentes |
| 7 | SSH hardening, UFW y AppArmor | Seguridad de imágenes y contenedores | Secretos, permisos, Dependabot y CodeQL | Gestión segura de configuración y dependencias |
| 8 | Monitorización, journald y recuperación | Healthchecks, logs y límites de recursos | Releases, entornos y protección de ramas | Métricas, comprobaciones y automatización de backups |
| 9 | Operación y recuperación de infraestructura | Despliegue completo y mantenimiento | Pipeline completo y documentación | Proyecto final, pruebas y defensa técnica |

## 4. Primer mes: programa semanal

### Semana 1 — Fundamentos de entorno y Linux

**Linux**
- Arquitectura general de GNU/Linux: kernel, shell, procesos y espacio de usuario.
- Jerarquía de directorios y rutas absolutas y relativas.
- Comandos: pwd, ls, cd, find, grep, cat, less, head, tail, man.
- Usuarios, grupos, permisos básicos y sudo.

**Git y GitHub**
- Diferencia entre Git y GitHub.
- Configuración de identidad.
- init, status, add, commit, log, diff y .gitignore.
- Crear repositorio remoto y conectar origin.

**Docker**
- Qué problema resuelven los contenedores.
- Diferencias entre imagen, contenedor y máquina virtual.
- Arquitectura cliente-servidor y Docker Engine.
- Ejecutar, listar, inspeccionar y eliminar contenedores.

**Python**
- Repaso de tipos, control de flujo, funciones y módulos.
- Ejecución desde terminal y argumentos sencillos.
- Estructura de un proyecto y uso de venv.

**Laboratorio:** crear Ubuntu Server en VirtualBox, configurar red y usuario, instalar Git y Docker Engine, y publicar en GitHub un primer repositorio de ejercicios Python.

### Semana 2 — Administración básica y automatización

**Linux:** usuarios y grupos, chmod, chown, umask, procesos, señales, ps, top, htop, systemctl y journalctl.

**GitHub:** clone, fetch, pull, push, ramas, merge y resolución de conflictos sencillos.

**Docker:** docker run, ps, logs, exec, stop, start, rm, rmi y gestión de imágenes.

**Python:** listas, diccionarios, excepciones, lectura y escritura de ficheros, pathlib, os y logging.

**Laboratorio:** desarrollar SysMonitor v0.1, un script que recoja información del sistema y genere un informe local. Guardar el código y la documentación en GitHub.

### Semana 3 — Redes, imágenes y herramientas de sistema

**Linux:** SSH, claves, permisos, scp, ss, ip, ping, curl, DNS y puertos.

**GitHub:** Pull Requests, revisión de cambios, etiquetas y plantillas de Issues.

**Docker:** Dockerfile, FROM, WORKDIR, COPY, RUN, CMD, EXPOSE y construcción de imágenes.

**Python:** subprocess, argparse, variables de entorno y validación de entradas.

**Laboratorio:** crear una herramienta Python que compruebe conectividad y disponibilidad de servicios propios. Construir una imagen Docker para una aplicación Python sencilla.

### Semana 4 — Integración y evaluación

**Linux:** lectura de logs, diagnóstico por capas y documentación de incidencias.

**GitHub:** README técnico, ramas de trabajo, Pull Request y revisión del historial.

**Docker:** redes bridge, publicación de puertos, volúmenes y persistencia básica.

**Python:** entornos virtuales, dependencias fijadas, pytest y estructura de paquetes.

**Laboratorio final:** empaquetar SysMonitor como proyecto Python, añadir pruebas, Dockerfile, documentación y workflow de CI básico.

## 5. Laboratorios y entregables

| Código | Laboratorio | Entregable verificable |
|---|---|---|
| LAB-LNX-01 | Instalación y configuración de Ubuntu Server en VirtualBox | Evidencias de red, usuarios y permisos |
| LAB-GIT-01 | Flujo Git local y remoto | Repositorio con ramas, commits y PR |
| LAB-DKR-01 | Ciclo de vida de contenedores | Registro de comandos y resultados |
| LAB-PY-01 | SysMonitor | Script, README y pruebas |
| LAB-DKR-02 | Construcción de imagen Python | Dockerfile y ejecución reproducible |
| LAB-INT-01 | Integración del proyecto | CI básico y documentación de ejecución |

Los laboratorios de Linux y Docker se ejecutan en máquinas virtuales propias. El navegador no ejecutará comandos arbitrarios del sistema anfitrión. Las actividades de terminal serán guías reproducibles y ejercicios de interpretación; las prácticas de ejecución se harán en el entorno local del alumno.

## 6. Evaluación

Cada módulo se evalúa con esta ponderación:

- Examen teórico: 20 %.
- Ejercicios individuales: 20 %.
- Laboratorios: 30 %.
- Proyecto práctico: 30 %.

La nota mínima para superar un módulo será 70/100. Una evaluación debe medir resultados observables: comandos ejecutados, pruebas superadas, repositorio entregado, logs, configuración y explicación de decisiones. No se considerará dominada una competencia por marcar una lección como leída.

## 7. Proyecto integrador final

**NEXARO DevOps Lab** será el proyecto de cierre. Se construirá una aplicación de administración y monitorización con:

- Ubuntu Server como entorno de despliegue.
- Python y FastAPI para la API de gestión.
- Docker y Docker Compose para los servicios.
- GitHub para el código, Issues, Pull Requests y releases.
- GitHub Actions para lint, pruebas, construcción y publicación de imágenes.
- GHCR como registro de contenedores.
- Logs, healthchecks, backups y documentación de recuperación.

La defensa técnica incluirá arquitectura, decisiones, amenazas, pruebas, procedimiento de despliegue y recuperación ante fallos.

## 8. Integración prevista en Python Learning Dashboard

La incorporación a la aplicación debe seguir la arquitectura actual:

1. Crear un área independiente de DAW, con catálogo y ruta propia para el itinerario DevOps.
2. Mantener HTML, CSS y JavaScript ES Modules; no introducir React ni un bundler.
3. Crear contenido fuente y un generador validable con modo `--check`. No editar manualmente JSON generado.
4. Modelar módulos, unidades, lecciones, preguntas, laboratorios, objetivos y fuentes verificables.
5. Reutilizar los componentes visuales, navegación, internacionalización, accesibilidad y patrones de progreso existentes cuando encajen.
6. Diseñar persistencia de progreso compatible con el patrón de documentos JSON sincronizados y aislamiento por usuario. Revisar el esquema permitido de cursos antes de reutilizar `CourseState`; no ampliar permisos ni aceptar identificadores de usuario desde el cliente.
7. Añadir los archivos nuevos al precache generado y probar el funcionamiento offline.
8. Añadir pruebas unitarias, de generación, de integración y E2E para catálogo, lecciones, progreso y accesibilidad.
9. Mantener las pruebas y cobertura existentes. No rebajar umbrales ni desactivar controles para introducir el itinerario.

### Secuencia de implementación

- **Sprint 0:** revisar los modelos de curso, sincronización, rutas, i18n, generadores y tests existentes; cerrar el contrato de datos.
- **Sprint 1:** catálogo DevOps, navegación y progreso básico.
- **Sprint 2:** contenido del primer mes y banco de preguntas.
- **Sprint 3:** laboratorios guiados, entregables y rúbricas.
- **Sprint 4:** evaluaciones, seguimiento y recomendaciones de estudio.
- **Sprint 5:** ampliar contenido del resto del itinerario y completar accesibilidad/offline.

## 9. Fuentes técnicas principales

Se priorizará documentación oficial y se verificará la versión de cada recurso al incorporarlo al catálogo:

- Linux: https://www.kernel.org/doc/html/latest/ y https://ubuntu.com/server/docs
- Bash: https://www.gnu.org/software/bash/manual/
- Git: https://git-scm.com/book/es/v2
- GitHub: https://docs.github.com/es
- GitHub Actions: https://docs.github.com/es/actions
- Docker: https://docs.docker.com/
- Python: https://docs.python.org/es/3/
- pytest: https://docs.pytest.org/
- FastAPI: https://fastapi.tiangolo.com/

Los recursos externos se incorporarán al catálogo de la plataforma con título, autor o entidad responsable, idioma, licencia o condiciones de uso, URL y fecha de verificación. No se copiará material protegido sin permiso.
