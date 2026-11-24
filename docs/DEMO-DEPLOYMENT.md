# Despliegue de la Demo Edition

La Demo Edition es parte del frontend: **se publica sola con la web** cuando la persona fusiona el PR en
`main` (`.github/workflows/pages.yml`). No hay nada que configurar en Render, en Neon ni en las variables
de entorno, y no hace falta backend para que funcione. Ver también [DEPLOY.md](DEPLOY.md).

## Ejecutarla en local

```bash
# Una vez: dependencias de las pruebas y Python para la web (frontend/pyodide/)
npm ci
python scripts/web/vendor_pyodide.py

# Servir el frontend (sin backend también funciona: la demo no lo usa)
python e2e/serve_frontend.py 5500
```

Abre `http://localhost:5500/?demo=1#/panel`. En Windows también sirve `Iniciar-Dashboard.bat` y después
añadir `?demo=1#/panel` a la dirección.

Si cambias los datos de Alex, se editan en `scripts/demo/build_demo.py` y se regeneran:

```bash
python scripts/demo/build_demo.py          # genera frontend/data/demo/alex.json
python scripts/demo/build_demo.py --check  # lo que comprueba CI
node scripts/web/build_precache.mjs        # si añades o quitas archivos de frontend/
```

## Antes de fusionar

1. CI en verde en el PR (lint, backend al 100 %, unitarias, e2e con axe, WebKit, comprobación del despliegue).
2. Probar en local, en claro y oscuro y en el móvil:
   - Portada → «Probar la demo sin registrarte» → panel de Alex con la franja de aviso.
   - `#/laboratorio`: ejecutar, un error, comprobar un ejercicio, Detener un `while True`.
   - `#/cursos`: siete cursos con su progreso.
   - «Salir de la demo»: vuelve a la portada sin franja y con el progreso propio intacto.

## Después de fusionar

1. Esperar a que termine **Deploy frontend** en Actions.
2. Abrir `https://marbi8891.github.io/python-learning-dashboard/?demo=1#/panel` en una ventana privada y
   repetir la prueba de arriba. La primera vez puede verse la versión anterior unos segundos: el service
   worker se actualiza al recargar.
3. En las herramientas del navegador (pestaña Red), comprobar que en la demo no hay ninguna petición a
   `pld-api.onrender.com`.

Desde el entorno en la nube donde se preparó la demo no se puede abrir github.io, así que este último paso
lo tiene que hacer una persona.

## Enlace para presentar

```
https://marbi8891.github.io/python-learning-dashboard/?demo=1#/panel
```

Sirve tal cual en un CV, un correo o una presentación: abre directamente el panel de Alex. Para enseñar el
laboratorio, `…/?demo=1#/laboratorio`; para los cursos, `…/?demo=1#/cursos`.

## Deshacer

Si algo falla en producción, se revierte el merge del PR (`git revert -m 1 <merge>`) en un PR nuevo y se
fusiona: Pages vuelve a publicar la versión anterior. La demo no deja datos en ningún servidor; en los
navegadores, lo de la demo vive en `sessionStorage` y desaparece al cerrar la pestaña.
