# Marca y uso de la denominación Python

**Estado:** decisión provisional, 5 de noviembre de 2026.  
**Alcance:** repositorio público, portfolio y posible evolución a SaaS.  
**Nota:** este documento es una guía de trabajo, no asesoramiento jurídico.

## Decisión provisional

1. Mantener por ahora el repositorio `python-learning-dashboard` y su historial de GitHub.
2. No cambiar identificadores técnicos, URLs, API, claves de almacenamiento ni nombres internos solo por motivos de marca.
3. Tratar «Python» como referencia descriptiva al lenguaje que se enseña y ejecuta en la plataforma.
4. No presentar el proyecto como oficial, patrocinado, certificado ni respaldado por la Python Software Foundation (PSF).
5. Antes de comercializar una plataforma cuyo nombre de producto incluya «Python», solicitar orientación o autorización escrita a la PSF. La política de la PSF exige aprobación previa para usos comerciales de sus marcas en nombres de productos o empresas.

## Aviso de marca

El proyecto es independiente y no está afiliado, patrocinado ni respaldado por la Python Software Foundation.

Python y los logotipos de Python son marcas de la Python Software Foundation. El nombre se utiliza únicamente para identificar el lenguaje de programación que forma parte de los contenidos y herramientas educativas del proyecto.

Este aviso no concede derechos sobre la marca ni sustituye una autorización cuando sea necesaria.

## Qué se conserva y qué se separa

### Se conserva de momento

- El nombre histórico del repositorio de GitHub.
- El historial de commits, issues, pull requests y enlaces existentes.
- Las rutas de GitHub Pages y las URLs de despliegue actuales.
- Las referencias técnicas necesarias para mantener compatibilidad, incluidas las claves de almacenamiento y los identificadores de sesión.
- La descripción de Python como uno de los lenguajes incluidos.

### Se separa antes de un lanzamiento comercial

- Nombre comercial y dominio del producto.
- Logotipo, icono de aplicación, colores y sistema visual.
- Nombre mostrado en la interfaz, metadatos, PWA y comunicaciones comerciales.
- Nombre de los planes, módulos y cuentas comerciales.
- Documentación legal, condiciones de servicio y avisos de marca.

La nueva marca deberá ser independiente de Python y de la PSF. No se utilizarán las serpientes, el logotipo oficial ni una variante confundible como identidad propia del producto.

## Condiciones para elegir una marca nueva

Antes de adoptar un nombre:

1. Buscar coincidencias exactas, fonéticas y conceptuales en OEPM, EUIPO/TMview y WIPO Global Brand Database.
2. Revisar al menos las clases Niza 9, 41 y 42, ajustadas a los productos y servicios reales.
3. Comprobar nombres de empresas, productos de software, dominios y repositorios.
4. Revisar significados y pronunciación en los idiomas de los mercados objetivo.
5. Obtener una búsqueda profesional de anterioridades y asesoramiento de un agente de propiedad industrial.
6. No anunciar el nombre como definitivo ni comprar activos costosos hasta completar las comprobaciones.

La disponibilidad de un dominio o de un nombre de usuario no demuestra que una marca pueda registrarse.

## Plan técnico de transición

Cuando se apruebe una marca nueva, hacer el cambio en una rama y mediante pull request. Como mínimo, auditar:

- Título, descripción, metadatos Open Graph y textos de interfaz.
- Iconos, favicon, manifest y nombre de la PWA.
- Nombre y claves de caché del service worker.
- URLs de GitHub Pages, configuración de despliegue y enlaces externos.
- Documentación, badges, workflows y ejemplos de comandos.
- Nombre de la aplicación y descripción de `package.json`.
- Variables de entorno, nombres de cookies, cabeceras y claves de almacenamiento.
- Documentación y metadatos del backend.
- Enlaces de OAuth, dominios autorizados, CORS y URLs de recuperación de cuenta.

No renombrar ni migrar claves persistentes, cookies, endpoints o URLs sin una estrategia de compatibilidad. Mantener alias o migraciones cuando sea necesario y probar el flujo de cuentas, progreso, PWA y despliegue antes de publicar.

## Referencias oficiales

- [PSF Trademark Usage Policy](https://www.python.org/psf/trademarks/)
- [PSF Trademark FAQ](https://www.python.org/psf/trademarks-faq/)

La política permite el uso nominativo para identificar correctamente el lenguaje, pero contempla aprobación previa para usos comerciales de marcas PSF en nombres de productos o empresas. Ante dudas sobre este proyecto concreto, consultar a la PSF en psf-trademarks@python.org.
