# Rediseño del frontend

**Estado:** primera capa visual integrada en feat/cybersecurity-course.  
**Archivo principal:** frontend/css/redesign.css.

## Objetivo

Unificar la presentación de la plataforma sin cambiar el modelo de navegación, el contenido académico, el motor adaptativo ni la API. La capa nueva se carga al final de index.html, por lo que puede renovar los componentes existentes sin reescribir sus módulos JavaScript.

## Dirección visual

- Interfaz de estudio sobria, con jerarquía tipográfica y espacio suficiente para leer.
- Ámbar para acciones principales y foco; verde para progreso y aciertos; rojo para errores.
- Superficies claras y oscuras coherentes con la preferencia de tema.
- Tarjetas con bordes discretos y radios consistentes, sin sombras pesadas ni adornos.
- Código en superficies oscuras en ambos temas.
- Navegación lateral con estados activos claros y menú móvil.
- Contenido adaptable a pantallas pequeñas y escritorio.

## Áreas cubiertas

| Área | Tratamiento |
|---|---|
| Marco general | Anchos, márgenes, fondo y jerarquía |
| Navegación | Sidebar, enlaces, estado activo, módulos y lecciones |
| Panel del alumno | KPIs, tarjetas, navegación secundaria y avisos |
| Aprender | Plan diario, conceptos, paneles y estados |
| Lecciones | Cabecera, pasos, pestañas, teoría y ejemplos |
| Consola Python | Editor, estado, acciones y salida |
| PCAP y DAW | Portadas de cursos, temario, ejercicios y exámenes |
| Perfil y cuenta | Formularios, tarjetas y estados |
| Portada pública | Navegación, hero, llamadas a la acción y rutas |
| Asistente y notificaciones | Panel flotante y avisos |
| Ciberseguridad | Catálogo, semanas y detalle del curso |

## Restricciones técnicas

- No se introduce React, Vue, Tailwind ni otra dependencia.
- Se mantienen HTML, CSS, JavaScript ES Modules, Pyodide y Web Workers.
- No se cambian rutas hash, identificadores usados por JavaScript, contratos de API ni claves de almacenamiento.
- El CSS nuevo no debe ocultar controles ni eliminar indicadores de estado.
- frontend/precache.js debe incluir la nueva hoja para el uso offline. La lista se genera con node scripts/web/build_precache.mjs.

## Accesibilidad y validación

Se mantienen los controles de foco visible, el enlace para saltar al contenido, los tamaños táctiles, el tema de alto contraste, el zoom de texto y prefers-reduced-motion. El CSS por sí solo no acredita conformidad WCAG. Antes de publicar hay que ejecutar las pruebas unitarias y E2E, comprobar los temas claro y oscuro, revisar móvil y escritorio y hacer una pasada manual con teclado y lector de pantalla.

## Siguientes iteraciones

1. Capturas comparativas de portada, panel, lección, consola, PCAP, DAW y móvil.
2. Pruebas visuales de los estados vacíos, error, carga, progreso y cuenta.
3. Auditoría manual de accesibilidad y contraste de los componentes heredados.
4. Revisión de las páginas legales y de la experiencia de autenticación.
