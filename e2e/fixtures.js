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

/** Espera a que la app haya cargado las lecciones. */
async function openLesson(page, slug = "") {
  await page.goto(slug ? `/#/leccion/${slug}` : "/");
  await page.locator(".lesson[data-slug]").first().waitFor({ state: "attached" });
}

module.exports = { test, expect: base.expect, uniqueEmail, openLesson };
