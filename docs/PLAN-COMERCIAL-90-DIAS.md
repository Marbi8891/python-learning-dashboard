# Plan comercial y de ejecución de PLD — 90 días

**Producto:** Python Learning Dashboard (PLD)  
**Marca:** PLD  
**Mercado:** particulares (B2C) y academias/centros (B2B)  
**Objetivo:** alcanzar 4.000 € de facturación recurrente mensual (MRR)  
**Horizonte:** 90 días desde el inicio del plan  
**Estado:** planificación inicial; precios y demanda pendientes de validación

## 1. Tesis de producto

PLD será una plataforma de aprendizaje práctico para estudiantes de DAM/DAW y personas que preparan Python/PCAP o empiezan en ciberseguridad. La ventaja inicial es reunir contenidos, ejercicios ejecutables en navegador, itinerarios y seguimiento del aprendizaje en una aplicación web ligera.

No se debe vender como una academia acreditada ni prometer aprobar exámenes o conseguir empleo. La propuesta es ayudar a practicar y organizar el estudio.

## 2. Segmentos y propuesta de valor

### B2C — estudiantes y particulares

- Estudiantes de DAM/DAW que necesitan practicar programación.
- Personas que aprenden Python desde cero o preparan PCAP.
- Alumnos que quieren una introducción guiada a fundamentos de ciberseguridad.

Problema que resuelve: dispersión de recursos y falta de práctica guiada con seguimiento.

### B2B — academias y docentes

- Academias pequeñas de programación y formación tecnológica.
- Docentes que necesitan ejercicios, itinerarios y visibilidad del progreso.
- Centros que quieren complementar sus clases, sin sustituir su LMS.

Problema que resuelve: preparación y seguimiento de actividades prácticas en un entorno común.

## 3. Hipótesis iniciales de precio

Los precios siguientes son hipótesis para entrevistas y pruebas de conversión. No deben codificarse como definitivos hasta validar disposición de pago.

| Plan | Precio de prueba | Alcance inicial |
|---|---:|---|
| Free | 0 € | Contenido de muestra, ejercicios introductorios y uso básico |
| Pro mensual | 7,99 €/mes | Acceso individual a itinerarios y funciones premium |
| Pro anual | 59,99 €/año | Mismo acceso Pro con descuento anual |
| Academy piloto | 99 €/mes | Hasta 25 alumnos; un docente y panel básico, cuando exista |
| Academy ampliado | A validar | Más alumnos, docentes e informes |

Las condiciones de renovación, cancelación, impuestos y desistimiento deben quedar claras antes de aceptar pagos. El checkout debe mostrar el precio final aplicable.

## 4. Combinaciones para llegar a 4.000 € MRR

Son escenarios aritméticos, no previsiones de ventas:

- 501 suscripciones Pro mensuales a 7,99 € ≈ 4.003 € MRR.
- 300 Pro a 7,99 € + 17 academias a 99 € = 4.077 € MRR.
- 250 Pro a 7,99 € + 21 academias a 99 € = 4.078,50 € MRR.

El objetivo de 90 días es validar el canal y conseguir los primeros clientes recurrentes. Alcanzar 4.000 € en ese plazo es una meta ambiciosa y no debe darse por garantizada.

## 5. Plan de ejecución

### Días 1–15 — preparar la oferta y validar el problema

- Auditar el producto actual, el registro, el progreso sincronizado y el curso de ciberseguridad.
- Entrevistar al menos a 15 estudiantes y 5 docentes/academias.
- Identificar qué contenidos justifican el pago y qué debe permanecer gratuito.
- Definir alcance de Free y Pro, y redactar la página de precios.
- Medir activación: registro, primera lección, primer ejercicio completado y retorno a los 7 días.
- Revisar privacidad, cookies, condiciones de contratación, política de reembolso/desistimiento y tratamiento de datos de menores.

**Salida:** oferta validada de forma preliminar, mapa de funcionalidades Free/Pro y lista priorizada.

### Días 16–30 — base técnica de monetización

- Diseñar el modelo de suscripción y los permisos de acceso en FastAPI.
- Añadir migraciones para clientes, suscripciones, eventos de facturación y derechos de acceso.
- Integrar Stripe Checkout en modo prueba.
- Implementar webhooks firmados, idempotentes y tolerantes a eventos repetidos o desordenados.
- Añadir portal de cliente para actualizar medio de pago y cancelar.
- No almacenar números de tarjeta ni datos sensibles de pago en PLD.
- Crear pruebas de altas, renovaciones, cancelaciones, pagos fallidos, reembolsos y acceso caducado.

**Salida:** flujo de compra completo en sandbox, sin cobros reales.

### Días 31–45 — producto Pro y piloto cerrado

- Aplicar permisos premium en el backend; ocultar controles en el frontend no cuenta como control de acceso.
- Definir qué rutas, cursos y funciones son premium.
- Añadir estados de suscripción y mensajes claros al usuario.
- Probar con 20–30 usuarios y recoger incidencias.
- Medir conversión de prueba a pago, activación, uso semanal y cancelaciones.
- Preparar soporte y proceso de incidencias de cobro.

**Salida:** piloto funcional y decisión documentada sobre el lanzamiento público.

### Días 46–60 — lanzamiento B2C

- Publicar página de precios y preguntas frecuentes.
- Activar cobros reales solo después de revisar legalidad, fiscalidad, seguridad y pruebas.
- Lanzar a la comunidad de estudiantes de FP, programación y Python.
- Publicar demostraciones breves del editor, ejercicios y rutas.
- Contactar con los primeros docentes para validar Academy.
- Revisar semanalmente embudo, ingresos y soporte.

**Salida:** primeras suscripciones reales y datos de conversión.

### Días 61–90 — ventas B2B y mejora por datos

- Contactar de forma personalizada con 30 academias/centros.
- Ofrecer un piloto limitado con objetivos y duración definidos.
- Priorizar las funciones B2B que los docentes pidan y estén dispuestos a pagar.
- Mejorar onboarding, contenidos con baja finalización y puntos de abandono.
- Revisar precios con datos de uso y entrevistas.
- Elaborar informe de MRR, ingresos netos, costes, churn y previsión.

**Salida:** decisión de escalar B2C, B2B o ambos según ventas reales.

## 6. Alcance técnico del MVP comercial

La arquitectura actual se conserva: HTML, CSS, JavaScript ES Modules, Pyodide, Web Workers y FastAPI. No migrar a React ni reescribir el frontend.

### Backend

- Catálogo de planes y derechos de acceso.
- Suscripción asociada al usuario.
- Stripe Checkout Session creada exclusivamente desde el servidor.
- Webhook con verificación de firma usando el cuerpo original.
- Registro de eventos procesados para idempotencia.
- Estados normalizados: incomplete, trialing, active, past_due, canceled, unpaid.
- Fecha de periodo actual y fecha de cancelación.
- Endpoint autenticado para consultar el plan y los permisos.
- Portal de facturación del proveedor.
- Logs sin datos de tarjeta ni secretos.

### Frontend

- Página de precios accesible desde la navegación.
- Comparativa Free/Pro.
- Checkout mediante redirección segura.
- Estado de suscripción en cuenta.
- Mensajes para pago correcto, cancelación y pago pendiente.
- No confiar en parámetros de URL para conceder acceso.

### Operación

- Configuración separada de test y live.
- Secretos únicamente en variables de entorno del proveedor de despliegue.
- Migraciones revisadas y copia de seguridad antes de producción.
- Monitorización de API, webhooks y errores de facturación.
- Proceso de reembolso y atención al cliente.

## 7. Seguridad, privacidad y cumplimiento

Antes de cobrar a usuarios en España/UE, revisar con asesoría adecuada:

- Identidad del vendedor, datos fiscales, facturación e IVA aplicable.
- Condiciones generales, precio total, renovación automática y cancelación.
- Derecho de desistimiento en servicios/contenido digital y consentimiento expreso cuando corresponda.
- Política de privacidad, base jurídica, encargados de tratamiento y transferencias internacionales.
- Cookies y analítica, con consentimiento cuando sea necesario.
- Edad mínima, consentimiento parental y tratamiento de datos de menores.
- Accesibilidad y atención al consumidor.

La integración de Stripe no resuelve por sí sola estas obligaciones.

## 8. Métricas y criterios de decisión

### Métricas de producto

- Visitante → registro.
- Registro → primera lección.
- Registro → primer ejercicio superado.
- Retención a 7 y 30 días.
- Usuarios activos semanales.
- Finalización por itinerario.

### Métricas comerciales

- Conversión Free → Pro.
- MRR y crecimiento neto de MRR.
- Ingreso medio por cuenta.
- Churn de clientes e ingresos.
- Pagos fallidos y recuperación.
- Coste de adquisición por canal.
- Academias contactadas, demos, pilotos y contratos.

### Puertas de decisión

- No activar cobros reales si no están aprobadas las pruebas de webhooks, permisos, cancelación y reembolso.
- No desarrollar un panel Academy completo sin al menos 3 docentes/centros que confirmen el problema y el precio.
- No aumentar gasto de captación hasta conocer conversión y retención.
- Si la retención es baja, corregir el valor del producto antes de comprar tráfico.

## 9. Riesgos conocidos que deben resolverse

- El progreso y la XP se calculan en el navegador; no deben usarse como dato fiable para recompensas o informes comerciales sin validación del servidor.
- El curso de ciberseguridad guarda actualmente parte del progreso en localStorage; debe revisarse la sincronización antes de vender seguimiento multidispositivo.
- El backend documentado usa el plan gratuito de Render y puede dormir; habrá que evaluar disponibilidad y coste antes del lanzamiento.
- El proyecto tiene licencia MIT. Antes de vender acceso exclusivo o licencias comerciales, revisar el alcance de la licencia y dependencias, y decidir qué valor se vende: servicio alojado, soporte, contenidos propios y funciones gestionadas.
- Las metas de facturación son objetivos, no ingresos garantizados.

## 10. Primer backlog de trabajo

1. Auditar estructura real de rutas, modelos, migraciones, pruebas y despliegue.
2. Definir matriz de permisos Free/Pro/Academy.
3. Diseñar entidades de facturación y migraciones.
4. Integrar Stripe en modo prueba y procesar webhooks.
5. Aplicar permisos en backend y frontend.
6. Crear página de precios, cuenta y portal de facturación.
7. Completar pruebas end-to-end y revisión de seguridad.
8. Preparar lanzamiento y piloto comercial.

**Regla de ejecución:** cambios en ramas feature, pruebas antes de abrir PR y ningún despliegue/cobro real sin validación explícita.
