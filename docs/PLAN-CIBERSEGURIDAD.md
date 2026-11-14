# Curso de ciberseguridad en Python Learning Dashboard

**Estado:** primera integración funcional del itinerario.  
**Carga:** 16 semanas · 320 horas · 20 horas semanales · nivel intermedio.

## Acceso en la aplicación

- Ruta: `#/ciberseguridad`.
- Semana: `#/ciberseguridad/semana-01` a `#/ciberseguridad/semana-16`.
- Datos del curso: `frontend/data/cybersecurity/course.json`.
- Vista y progreso: `frontend/js/cybersecurity.js`.
- Estilos: `frontend/css/cybersecurity.css`.

La sección se incorpora como itinerario independiente para no mezclar sus evaluaciones con PCAP ni con el currículo oficial de DAW. El progreso inicial se guarda localmente en `localStorage` bajo `pld:cybersecurity:v1`; esta primera versión no lo sincroniza con la cuenta ni con la app móvil.

## Estructura

| Semana | Contenido |
|---:|---|
| 1 | Fundamentos y laboratorio |
| 2 | Linux para pentesters |
| 3 | Redes y análisis de tráfico |
| 4 | Reconocimiento con Nmap |
| 5 | Enumeración y vulnerabilidades |
| 6 | Metasploit y validación controlada |
| 7 | Fundamentos de seguridad web |
| 8 | Vulnerabilidades web I |
| 9 | Vulnerabilidades web II |
| 10 | OSINT y reconocimiento de exposición |
| 11 | Windows y Active Directory |
| 12 | Python para automatización |
| 13 | Blue Team: hardening y detección |
| 14 | Análisis forense y respuesta a incidentes |
| 15 | Proyecto final: planificación y ejecución |
| 16 | Proyecto final: reporting y defensa |

Cada semana contiene objetivos, contenidos, laboratorios, entregables, evaluación, recursos y tres preguntas de comprobación. Se requieren al menos dos respuestas correctas de tres para habilitar el marcado de semana completada.

## Metodología

- 4 h de teoría y clases.
- 4 h de bibliografía y documentación.
- 8 h de laboratorios.
- 2 h de Python y automatización.
- 2 h de evaluación y documentación.

## Evaluación global

| Componente | Peso |
|---|---:|
| Cuestionarios y exámenes teóricos | 15 % |
| Laboratorios y prácticas | 35 % |
| Ejercicios y scripts Python | 15 % |
| Documentación y reporting | 15 % |
| Proyecto final y defensa | 20 % |

## Seguridad de los laboratorios

Las máquinas deliberadamente vulnerables deben permanecer en una red interna aislada de VirtualBox, sin adaptador puente ni exposición a Internet. Solo se evalúan sistemas propios o expresamente autorizados. No se incluyen ejercicios de persistencia real, denegación de servicio ni extracción de datos.

## Fuentes principales

- [Kali Linux Documentation](https://www.kali.org/docs/)
- [VirtualBox User Manual](https://www.virtualbox.org/manual/)
- [Nmap Network Scanning](https://nmap.org/book/)
- [Metasploit Documentation](https://docs.metasploit.com/)
- [OWASP Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [PortSwigger Web Security Academy](https://portswigger.net/web-security)
- [MITRE ATT&CK](https://attack.mitre.org/)
- [Python Documentation](https://docs.python.org/3/)

## Pruebas\n\n- `node --test tests/unit/cybersecurity-course.test.mjs`: valida duración, estructura de las 16 semanas, cuestionarios y ponderación de la evaluación.\n- La nueva vista debe probarse manualmente en `#/ciberseguridad`, en enlaces directos a semanas, recarga y persistencia local del progreso.\n\n## Evolución pendiente

1. Sincronización del progreso con la cuenta y la app móvil mediante un documento de curso propio en backend.
2. Evaluaciones prácticas con validación de entregables, no solo autoevaluación.
3. Generador de informes y repositorio de evidencias por alumno.
4. Accesibilidad manual y pruebas e2e de la nueva sección.
5. Revisión editorial de la bibliografía y fechas de verificación de cada recurso.
