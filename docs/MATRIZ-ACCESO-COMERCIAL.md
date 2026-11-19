# Matriz de acceso y diseño de permisos comerciales

**Estado:** propuesta técnica para revisión. No activa restricciones ni modifica el comportamiento actual.

## 1. Hallazgos de la auditoría

La API actual autentica usuarios mediante `CurrentUser` y persiste progreso, pero no tiene conceptos de plan, suscripción o entitlement.

Rutas relevantes:

- `GET /api/v1/modules` y `GET /api/v1/lessons/{slug}`: contenido de lecciones público, sin autenticación.
- `GET/PUT /api/v1/course-state/{course}`: estado de cursos DAW, requiere sesión.
- `GET/PUT /api/v1/pcap-state`: estado PCAP, requiere sesión.
- `GET/PUT/DELETE /api/v1/progress`: progreso personal, requiere sesión.
- `POST/GET /api/v1/lessons/{slug}/attempts`: intentos personales, requiere sesión.
- `GET /api/v1/dashboard`: panel personal, requiere sesión.

El catálogo y el frontend se sirven también como archivos estáticos desde GitHub Pages. Por tanto, ocultar un botón o una ruta en JavaScript no protege un curso: cualquier recurso JSON/HTML/JS publicado está disponible públicamente.

## 2. Principio de diseño

El servidor será la autoridad para conceder derechos de acceso. El frontend solo presenta el resultado.

No se debe marcar como premium contenido que siga publicado íntegramente en GitHub Pages o en ficheros estáticos accesibles sin autenticación. Para cobrar por contenido concreto habrá que servirlo desde endpoints protegidos por la API, o vender funciones de servicio que realmente estén controladas por el backend.

## 3. Matriz inicial propuesta

Esta matriz es una hipótesis de producto, pendiente de confirmar antes de implementar bloqueos:

| Capacidad | Visitante | Free | Pro | Academy |
|---|---|---|---|---|
| Ver catálogo y muestras públicas | Sí | Sí | Sí | Sí |
| Ejecutar prácticas públicas en navegador | Sí | Sí | Sí | Sí |
| Crear cuenta y sincronizar progreso | No | Sí | Sí | Sí |
| Acceder a itinerario ampliado Python/PCAP | Muestra | Por definir | Propuesto | Según licencia |
| Acceder a itinerario ampliado DAW | Muestra | Por definir | Propuesto | Según licencia |
| Curso de ciberseguridad | Muestra | Por definir | Propuesto | Según licencia |
| Informes personales avanzados | No | No | Propuesto | Propuesto para docente |
| Gestión de grupos y alumnos | No | No | No | Pendiente de MVP B2B |
| Panel docente y asignación de tareas | No | No | No | Pendiente de validación |

**Importante:** no se propone bloquear ahora el catálogo actual. Hay que definir primero qué material será realmente exclusivo, y migrarlo fuera de los recursos estáticos públicos si se decide cobrar por él.

## 4. Entidades recomendadas

Separar el plan comercial del proveedor de pago:

- `Plan`: identificador estable (`free`, `pro_monthly`, `pro_annual`, `academy`), nombre y estado comercial.
- `Subscription`: usuario o cuenta cliente, proveedor, ID externo, estado normalizado, periodo vigente y fecha de cancelación.
- `Entitlement`: derecho concedido, origen y vigencia. Permite que un plan dé varios permisos y que promociones o licencias Academy se gestionen sin acoplar la lógica a Stripe.
- `BillingEvent`: ID único del evento externo, tipo, fecha de recepción y resultado de procesamiento. No guardar datos de tarjeta ni el payload completo si contiene datos personales innecesarios.

Para la primera versión, cada usuario puede tener como máximo una suscripción individual activa. La suscripción Academy requiere modelar organización, miembros y roles; no se debe simular con una suscripción individual.

## 5. Resolución de permisos

Crear una dependencia FastAPI, por ejemplo `require_entitlement("feature_key")`, que:

1. Reciba el usuario autenticado desde `CurrentUser`.
2. Consulte derechos vigentes desde la base de datos.
3. Considere fecha de expiración y estado de suscripción.
4. Devuelva 403 con un código estable cuando falte el derecho.
5. No acepte el plan ni el estado desde el cuerpo, query string, localStorage o cabeceras del cliente.

El plan Free debe ser el comportamiento por defecto para cuentas existentes y nuevas. Una indisponibilidad de base de datos no debe conceder acceso premium.

## 6. Reglas de sincronización con Stripe

- El Checkout Session se crea en backend a partir de un identificador de precio permitido por configuración; nunca se acepta un importe libre del navegador.
- El webhook verifica la firma sobre el cuerpo HTTP original.
- Los eventos se deduplican por ID del proveedor y se procesan en transacción.
- El orden de llegada puede variar: antes de actualizar se consulta/valida el estado más reciente de la suscripción cuando haga falta.
- La vuelta a la URL de éxito no concede acceso. El acceso cambia cuando el webhook verificado confirma el estado.
- La cancelación al final del periodo conserva acceso hasta la fecha pagada, según la política de producto.
- Los pagos fallidos pasan a un estado de gracia definido por negocio; al vencer, se retiran los derechos Pro.
- Reembolsos y disputas deben tener política explícita y trazabilidad.

## 7. Orden de implementación

1. Confirmar la matriz de producto y decidir qué contenidos/funciones son premium.
2. Crear catálogo de planes, suscripciones, derechos y eventos con migración Alembic.
3. Implementar consulta de derechos y endpoint de estado de suscripción.
4. Añadir Stripe en modo test y webhooks idempotentes.
5. Aplicar permisos únicamente a recursos que ya estén protegidos por backend.
6. Si se vende contenido, moverlo de ficheros estáticos públicos a endpoints protegidos.
7. Construir la UI de precios y cuenta.
8. Añadir pruebas de acceso, ciclo de vida y regresión.

## 8. Decisiones que requieren confirmación del propietario

- Qué cursos o unidades serán gratuitos y cuáles Pro.
- Si el usuario podrá probar Pro durante un periodo gratuito.
- Si la suscripción se cancela inmediatamente o al final del periodo (recomendación: al final).
- Si Academy se venderá por alumno, por grupo o por centro.
- Si el progreso y los informes serán parte de Pro o de Academy.

Hasta confirmar estas decisiones, el backend debe seguir funcionando como hasta ahora y no se deben denegar rutas existentes.
