# Idiomas

La web está escrita en español y se puede usar con la interfaz en inglés (Aspecto > Idioma). No usa
ningún framework ni servicio de traducción: todo está en `frontend/js/i18n.js` y `frontend/i18n/`.

## Cómo funciona

- El español es el texto original del HTML y del JavaScript. No hay claves.
- Con otro idioma, `i18n.js` descarga `frontend/i18n/<idioma>.json` y sustituye cada texto (o
  `aria-label`, `title`, `placeholder`, `alt`) cuyo contenido completo esté en el diccionario. Un
  `MutationObserver` traduce también lo que las vistas pintan después.
- Huecos: `"Racha: {n} días": "Streak: {n} days"`. Si el valor de un hueco está en el diccionario,
  también se traduce (por ejemplo, el nombre del nivel).
- Las lecciones siguen en español: van marcadas con `lang="es"` y el aviso de Aspecto explica que se
  pueden traducir con el navegador.
- El código (`pre`, `code`, `kbd`, `samp`, `textarea`) lleva siempre `translate="no"`: ningún
  traductor, ni el nuestro ni el del navegador, cambia un programa.
- A un navegador que no está en español se le ofrece el inglés una vez.

## Añadir o corregir una traducción

1. Copia el texto español tal como se ve (los espacios y saltos de línea cuentan como uno).
2. Añade la pareja a `frontend/i18n/en.json`.
3. Ejecuta `npm run test:unit`: `tests/unit/i18n.test.mjs` falla si un texto fijo de `index.html` no
   tiene traducción.

## Añadir un idioma

Crea `frontend/i18n/<código>.json`, añade el idioma a `LANGUAGES` y `LOCALES` en `i18n.js` y una opción
en el `fieldset` de Idioma de `index.html`. Para un idioma que se escribe de derecha a izquierda (árabe,
hebreo) habría que añadir `dir="rtl"` y revisar el CSS.
