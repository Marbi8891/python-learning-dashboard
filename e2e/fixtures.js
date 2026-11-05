// Fixture común: permite servir Pyodide desde otra URL (PYODIDE_URL) y ajustar la configuración.
const base = require("@playwright/test");

const test = base.test.extend({
  page: async ({ page }, use) => {
    const config = {};
    if (process.env.PYODIDE_URL) config.pyodideUrl = process.env.PYODIDE_URL;
    await page.addInitScript((values) => {
      window.PLD_CONFIG = Object.assign(window.PLD_CONFIG ?? {}, values);
    }, config);
    await use(page);
  },
});

/** Email único por test: los tests se ejecutan en paralelo contra el mismo backend. */
const uniqueEmail = () => `e2e-${Date.now()}-${Math.random().toString(36).slice(2, 8)}@example.com`;

/** Espera a que la app haya cargado las lecciones. Sin lección, abre la presentación de la app
 *  (la raíz lleva a la portada, que no tiene el menú lateral). */
async function openLesson(page, slug = "") {
  await page.goto(slug ? `/#/leccion/${slug}` : "/#/bienvenida");
  await page.locator(".lesson[data-slug]").first().waitFor({ state: "attached" });
}

/* Portapapeles en los tres motores. Playwright no da los mismos permisos en todos (ver los mapas
   de permisos de playwright-core): Chromium acepta «clipboard-read» y «clipboard-write», WebKit solo
   «clipboard-read» (pedir «clipboard-write» lanza «Unknown permission») y Firefox ninguno de los dos.
   Escribir no necesita permiso en ninguno si viene de un clic del usuario; leer sí. */
const CLIPBOARD_PERMISSIONS = { chromium: ["clipboard-read", "clipboard-write"], webkit: ["clipboard-read"] };

/**
 * Prepara la página para comprobar lo que copia la web sin cambiar lo que hace:
 * - envuelve navigator.clipboard.writeText para anotar cada texto que se copió BIEN (la llamada
 *   real se hace igual; si el navegador la rechaza, no se anota y la web muestra su aviso);
 * - da solo los permisos que admite el motor, para poder leer el portapapeles real.
 * Devuelve { writes(), read() }: read() es null en los motores que no dejan leerlo (Firefox).
 */
async function watchClipboard(page, browserName) {
  const permissions = CLIPBOARD_PERMISSIONS[browserName];
  if (permissions) await page.context().grantPermissions(permissions);
  await page.addInitScript(() => {
    const clipboard = navigator.clipboard;
    const writeText = clipboard.writeText.bind(clipboard);
    window.__clipboardWrites = [];
    clipboard.writeText = (text) => writeText(text).then(() => void window.__clipboardWrites.push(text));
  });
  return {
    writes: () => page.evaluate(() => window.__clipboardWrites),
    read: permissions ? () => page.evaluate(() => navigator.clipboard.readText()) : null,
  };
}

module.exports = { test, expect: base.expect, uniqueEmail, openLesson, watchClipboard };
