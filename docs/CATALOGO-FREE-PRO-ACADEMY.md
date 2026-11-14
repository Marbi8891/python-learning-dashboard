# Propuesta de catálogo Free, Pro y Academy

**Estado:** criterio de producto aceptado por el propietario; todavía no activa restricciones ni cambia permisos.
**Base:** inventario descrito en README y auditoría técnica del catálogo.
**Objetivo:** que PLD siga siendo útil sin pagar y que Pro cobre por profundidad, continuidad y herramientas de aprendizaje.

## Criterios

1. Free debe permitir probar el método de aprendizaje y completar una ruta introductoria real.
2. Pro debe añadir práctica estructurada y seguimiento avanzado, no limitarse a quitar anuncios o botones.
3. Academy debe resolver necesidades de docentes y centros: grupos, asignaciones y seguimiento. No se venderá como disponible hasta construir esas funciones.
4. No se marcará como premium un fichero que siga publicado en GitHub Pages y pueda descargarse sin autenticación.
5. El catálogo y los derechos se separarán del proveedor de pago.

## Distribución aprobada como criterio de producto

| Área | Free | Pro | Academy |
|---|---|---|---|
| Python por conceptos | Conceptos introductorios y una selección de ejercicios | Catálogo completo, retos progresivos y rutas avanzadas | Acceso Pro para alumnos incluidos en un grupo |
| Consola Pyodide | Uso básico y ejecución de prácticas abiertas | Retos guiados, historial y seguimiento ampliado cuando exista backend | Actividades asignadas por docente |
| PCAP | Módulos de muestra y práctica inicial | Itinerario completo, banco ampliado y simulacros | Asignación de bloques y seguimiento de grupo |
| DAW | Muestras y ejercicios introductorios de varios módulos | Rutas completas por módulo, baterías de práctica y preparación de evaluación | Grupos por ciclo/módulo y asignación de actividades |
| Ciberseguridad | Primeros fundamentos y laboratorios introductorios | Itinerario completo, entregables, cuestionarios y seguimiento sincronizado | Itinerarios y tareas asignadas por docente |
| Motor adaptativo | Plan diario básico y repaso esencial | Diagnóstico por conceptos, plan adaptativo ampliado y análisis personal | Vista de progreso por alumno y grupo |
| Cuenta y progreso | Cuenta y sincronización básica | Historial ampliado y exportación/analítica personal avanzada | Roles de alumno y docente |
| Gestión docente | No incluida | No incluida | Grupos, matrículas, asignaciones e informes |

## Qué se puede vender en la primera versión

La primera oferta Pro debería centrarse en capacidades que puedan controlarse desde FastAPI:

- Diagnóstico y seguimiento personal ampliado, una vez que los datos se calculen o validen en servidor.
- Planificación adaptativa avanzada y reportes personales servidos por API.
- Itinerarios guiados con actividades premium servidas desde endpoints protegidos.
- Historial de intentos y estadísticas avanzadas asociadas a la cuenta.

Academy queda como piloto posterior. Antes de cobrar por este plan deben existir organización, pertenencia de usuarios, roles, asignaciones y consultas de progreso autorizadas por grupo.

## Qué debe seguir abierto

- Catálogo público de muestra y páginas que expliquen el producto.
- Una ruta inicial suficiente para que el usuario pueda valorar la calidad.
- Ejercicios introductorios que demuestren el funcionamiento de Pyodide.
- Acceso básico a la cuenta y a la sincronización del progreso.

No recomiendo poner un muro de pago al registro ni al primer ejercicio. El usuario debe experimentar el producto antes de decidir.

## Límites técnicos antes de aplicar precios

El frontend y los datos del curso se publican como recursos estáticos en GitHub Pages. Mientras un contenido permanezca ahí, debe tratarse como público. Para proteger material premium:

1. Mover el contenido premium a almacenamiento privado o a la API.
2. Crear endpoints autenticados que comprueben `require_entitlement`.
3. No enviar contenido premium al navegador antes de comprobar permisos.
4. Evitar que el cliente pueda concederse derechos o modificar el precio.
5. Añadir pruebas de acceso anónimo, Free, Pro caducado y Pro activo.

El progreso, la XP y parte de la actividad se calculan actualmente en cliente. No deben usarse como base de informes de pago hasta validarlos en servidor.

## Hipótesis de precio para validar

Se mantienen únicamente como hipótesis comerciales del plan de 90 días:

- Free: 0 €.
- Pro: 7,99 €/mes o 59,99 €/año.
- Academy piloto: 99 €/mes hasta 25 alumnos, solo cuando exista el producto docente.

No implementar importes definitivos en código hasta validar entrevistas, costes y disposición de pago. Academy debe revisarse por alumno activo, grupo y centro antes de fijar tarifa.

## Estado de las decisiones

El propietario ha aceptado esta distribución como criterio general de producto: ruta inicial gratuita y contenidos/seguimiento avanzados en Pro. La matriz anterior queda aprobada como dirección de trabajo, pero todavía falta concretar qué unidades y ejercicios exactos pertenecen a cada nivel mediante un inventario del catálogo.

Los precios siguen siendo hipótesis para entrevistas y validación. La aceptación de esta distribución no autoriza a activar cobros ni a restringir rutas existentes.

Siguiente paso técnico: inventariar los módulos, unidades, ejercicios y recursos que existen realmente; asignar cada elemento a Free o Pro; y diseñar cómo servir el contenido Pro desde backend sin dejarlo expuesto en GitHub Pages. Academy continúa pendiente de validar con centros y de desarrollar sus funciones.
