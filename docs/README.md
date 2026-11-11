# Documentación

Índice de todo lo que hay en `docs/`. Si buscas cómo arrancar el proyecto, empieza por el
[README](../README.md). Si vas a cambiar algo, lee antes [CONTRIBUTING.md](../CONTRIBUTING.md).

## Empezar

| Documento | Para qué sirve |
|---|---|
| [EJECUTAR-EN-WINDOWS.md](EJECUTAR-EN-WINDOWS.md) | Usar la web y la API en tu PC con `Iniciar-Dashboard.bat` |
| [TESTING.md](TESTING.md) | Todas las pruebas y cuáles ejecutar según lo que cambies |
| [CI_CD_MONITORING.md](CI_CD_MONITORING.md) | Cómo se vigila cada subida a GitHub Actions, cómo se avisa y cómo se corrigen los fallos |
| [DEPLOY.md](DEPLOY.md) | Desplegar la web en GitHub Pages y la API en Render con Neon |

## Arquitectura y funcionamiento

| Documento | Para qué sirve |
|---|---|
| [API.md](API.md) | Endpoints de la API REST (`/api/v1`) |
| [auth.md](auth.md) | Recuperación de contraseña e inicio de sesión con Google |
| [ADAPTIVE_ENGINE.md](ADAPTIVE_ENGINE.md) | Motor adaptativo: dominio, olvido, repaso espaciado y planificador |
| [MODULO_POO.md](MODULO_POO.md) | Módulo de POO: unidades, formato, validadores, progreso y currículo |
| [DECISIONS.md](DECISIONS.md) | Registro de decisiones de arquitectura (DEC-NNN) |
| [CAREER_ROADMAP_ARCHITECTURE.md](CAREER_ROADMAP_ARCHITECTURE.md) | Career Roadmap: auditoría y arquitectura propuesta (Sprint 0) |
| [CAREER_ROADMAP_AGENT_LOG.md](CAREER_ROADMAP_AGENT_LOG.md) | Career Roadmap: registro de sprints y decisiones |
| [DISENO.md](DISENO.md) | Sistema visual: tokens, colores, tipografía y componentes |
| [IDIOMAS.md](IDIOMAS.md) | Interfaz en inglés y cómo añadir textos traducidos |

## Temario

| Documento | Para qué sirve |
|---|---|
| [PLAN-CURRICULO-DAW.md](PLAN-CURRICULO-DAW.md) | Currículo oficial de DAW y cómo se genera el catálogo |
| [AMPLIAR-TEMARIO-DAW.md](AMPLIAR-TEMARIO-DAW.md) | Cómo añadir asignaturas, unidades y recursos |
| [AUDITORIA-Y-LICENCIAS.md](AUDITORIA-Y-LICENCIAS.md) | Origen y licencias de las fuentes de contenido |

## Privacidad y cumplimiento legal

Son borradores técnicos que no ha revisado un abogado.

| Documento | Para qué sirve |
|---|---|
| [REGISTRO_TRATAMIENTOS.md](REGISTRO_TRATAMIENTOS.md) | Registro de actividades de tratamiento y derechos RGPD |
| [INCIDENTES.md](INCIDENTES.md) | Qué hacer ante un incidente o una brecha de datos |
| [RIESGOS_LEGALES.md](RIESGOS_LEGALES.md) | Riesgos legales abiertos y su estado |
| [PLAN_ADECUACION_LEGAL.md](PLAN_ADECUACION_LEGAL.md) | Plan de adecuación legal por fases |
| [AUDITORIA_LEGAL.md](AUDITORIA_LEGAL.md) | Auditoría legal del 02/11/2026 |

La política de seguridad está en [SECURITY.md](../SECURITY.md).

## Proyecto académico

| Documento | Para qué sirve |
|---|---|
| [memoria/memoria.md](memoria/memoria.md) | Memoria del proyecto de 2º de DAW |
| [DEMO-Y-DEFENSA.md](DEMO-Y-DEFENSA.md) | Guion de la demo y de la defensa |

## Auditorías e informes

Son fotos de un momento concreto: llevan fecha y commit, y no se actualizan después. Lo que sigue
vigente de ellas está en el código, en [DECISIONS.md](DECISIONS.md) o en el [CHANGELOG](../CHANGELOG.md).

| Documento | Fecha | Tema |
|---|---|---|
| [AUDITORIA_TECNICA.md](AUDITORIA_TECNICA.md) | 02/11/2026 | Técnica y seguridad (hallazgos `AUD-*`) |
| [INFORME_CONSOLIDACION_PR71_PR69.md](INFORME_CONSOLIDACION_PR71_PR69.md) | 02/11/2026 | Consolidación de los PR #71 y #69 |
| [AUDITORIA_TEMARIO_DAW.md](AUDITORIA_TEMARIO_DAW.md) | 03/11/2026 | Temario de DAW (Fase D) |
| [AUDITORIA_EVOLUCION_PLD.md](AUDITORIA_EVOLUCION_PLD.md) | 04/11/2026 | Evolución al aprendizaje adaptativo (Fase 0) |

## Convenciones para documentos nuevos

- En español, con frases cortas y sin datos inventados: lo que no esté comprobado se marca.
- Nombre en mayúsculas con guiones (`NOMBRE-DEL-TEMA.md`) y un enlace en este índice.
- Una auditoría o un informe lleva fecha y commit al principio, y va en la última sección.
- Antes de crear un documento, mira si el tema cabe en uno que ya existe.
