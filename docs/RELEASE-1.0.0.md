# Python Learning Dashboard 1.0.0

Primera versión estable: academia web para preparar el examen PCAP, con API, cuenta opcional y app Android.

## Incluye

- 27 lecciones del PCAP con consola de Python en el navegador y ejercicios corregidos automáticamente.
- Zona de examen: simulacro de 40 preguntas en 65 minutos, práctica por bloque, 48 fichas y 126 preguntas en español e inglés.
- Estudio guiado con repaso espaciado y plan semanal.
- Cuenta opcional con sincronización, recuperación de contraseña y derechos RGPD (exportar y borrar).
- PWA con funcionamiento sin conexión.
- App Android nativa (APK firmado) con cursos de Python/PCAP, Bases de datos, Entornos de desarrollo, JavaScript y Java.
- Aviso legal, página 404, vista previa al compartir, `robots.txt` y `sitemap.xml`.
- Analítica opcional sin cookies (GoatCounter), desactivada por defecto.
- Cabeceras de seguridad en la API.

## Calidad

412 pruebas de backend al 100 % de cobertura, pruebas end-to-end con Playwright, auditoría WCAG 2.1 AA automática, migraciones probadas en PostgreSQL 16 y 19 ADR.

## Limitaciones conocidas

Recuperación por email pendiente de configurar SMTP; simulacro y Python real en la app Android pendientes.

## Cómo publicarla

```
git tag -a v1.0.0 -m "Versión 1.0.0"
git push origin v1.0.0
```

Después, en GitHub: Releases, Draft a new release, elige `v1.0.0`, pega este texto y adjunta `app-release.apk` desde la última ejecución del workflow Android.
