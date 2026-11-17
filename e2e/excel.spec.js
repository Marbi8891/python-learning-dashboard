// Excel profesional.
// P0: el curso está registrado en el catálogo (familia academia) y su progreso se fusiona y sincroniza
// con la cuenta como el de cualquier curso, sin aparecer todavía en la web ni entre los cursos de DAW.
// P1: el motor de fórmulas da lo mismo en el navegador que en Node, y los ejercicios de fórmulas se
// pueden usar con teclado y sin infracciones de accesibilidad.
// P2: el curso tiene su ruta (#/academia/excel, con el alias #/excel-academy), sus avisos, sus 9
// unidades y su práctica, guarda el progreso y no tiene infracciones de accesibilidad.
const { readFileSync } = require("node:fs");
const path = require("node:path");
const { pathToFileURL } = require("node:url");
const AxeBuilder = require("@axe-core/playwright").default;
const { test, expect, uniqueEmail } = require("./fixtures");

const CASES = JSON.parse(readFileSync(path.join(__dirname, "..", "tests", "fixtures", "excel", "reference-cases.json"), "utf8")).cases;
const ENGINE = pathToFileURL(path.join(__dirname, "..", "frontend", "js", "excel", "formula", "index.js")).href;

const API = "http://127.0.0.1:8000";

test("el progreso de Excel profesional se fusiona con la cuenta en los dos sentidos", async ({ page, request }) => {
  const email = uniqueEmail();
  const password = "contraseña-e2e-123";
  await request.post(`${API}/api/v1/auth/register`, { data: { email, password, display_name: "Ana", accept_privacy: true } });
  const login = await request.post(`${API}/api/v1/auth/login`, { form: { username: email, password } });
  const headers = { Authorization: `Bearer ${(await login.json()).access_token}` };
  // Otro dispositivo ya había completado una unidad
  await request.put(`${API}/api/v1/course-state/excel`, {
    headers,
    data: { data: { done: { "xl1-interfaz": "2026-11-15T10:00:00.000Z" } } },
  });
  // Y en este navegador, sin sesión, se completó otra
  await page.addInitScript(() => {
    if (!localStorage.getItem("pld:course:excel")) {
      localStorage.setItem("pld:course:excel", JSON.stringify({ done: { "xl1-datos": "2026-11-16T09:00:00.000Z" } }));
    }
  });

  await page.goto("/#/daw/cursos");
  await page.getByRole("button", { name: "Iniciar sesión" }).click();
  await page.locator("#login-form").getByLabel("Email").fill(email);
  await page.locator("#login-form").getByLabel("Contraseña").fill(password);
  await page.locator("#login-form").getByRole("button", { name: "Entrar" }).click();
  await expect(page.locator("#account-label")).toHaveText("Ana");

  // La cuenta recibe lo de este navegador sin perder lo del otro dispositivo
  await expect
    .poll(async () => Object.keys((await (await request.get(`${API}/api/v1/course-state/excel`, { headers })).json()).data.done ?? {}).sort())
    .toEqual(["xl1-datos", "xl1-interfaz"]);
  // Y el navegador, lo de la cuenta
  const local = await page.evaluate(() => JSON.parse(localStorage.getItem("pld:course:excel")));
  expect(Object.keys(local.done).sort()).toEqual(["xl1-datos", "xl1-interfaz"]);
});

test("Excel profesional no aparece entre los cursos de DAW", async ({ page }) => {
  await page.goto("/#/daw/cursos");
  await expect(page.locator(".daw-card")).toHaveCount(6);
  await expect(page.locator("#daw-view")).not.toContainText("Excel");
});

test("el motor de fórmulas da en el navegador lo mismo que en Node con los casos de referencia", async ({ page }) => {
  const { evaluate, parseFormula } = await import(ENGINE);
  const inNode = CASES.map((c) => evaluate(parseFormula(c.formula), { grid: c.grid ?? {}, at: c.at ?? null, sheet: c.sheet }));
  await page.goto("/#/portada");
  const inBrowser = await page.evaluate(async (cases) => {
    const engine = await import("/js/excel/formula/index.js");
    return cases.map((c) => engine.evaluate(engine.parseFormula(c.formula), { grid: c.grid ?? {}, at: c.at ?? null, sheet: c.sheet }));
  }, CASES);
  expect(CASES.length).toBeGreaterThanOrEqual(150);
  expect(inBrowser).toEqual(inNode);
});

test("un ejercicio de fórmula se corrige con teclado y es accesible", async ({ page }) => {
  await page.goto("/#/portada");
  await page.evaluate(async () => {
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = "/css/excel.css";
    document.head.append(link);
    const { mountFormulaExercise } = await import("/js/excel/views.js");
    const box = document.createElement("section");
    box.id = "xl-prueba";
    box.setAttribute("aria-label", "Ejercicio de prueba");
    document.querySelector("main").prepend(box);
    mountFormulaExercise(box, {
      id: "xl1-ref-07",
      q: "Escribe en D2 el IVA de B2 con el tipo de E1 y que funcione al copiarla hasta D6.",
      grid: { B1: "Base", B2: 100, B3: 250, B4: 80, B5: 40, B6: 1000, D1: "IVA", E1: { v: 0.21, format: "percent" } },
      cell: "D2",
      expect: 21,
      checks: [{ type: "value" }, { type: "fill", to: "D6", expect: [52.5, 16.8, 8.4, 210] }, { type: "references", must: ["$E$1"] }],
      hints: ["Si copias =B2*E1 hacia abajo, ¿qué pasa con E1?"],
      solution: { formula: "=B2*$E$1" },
    });
  });
  const box = page.locator("#xl-prueba");
  await expect(box.getByRole("table", { name: "Datos del ejercicio" })).toBeVisible();
  await expect(box.getByRole("columnheader", { name: "E" })).toBeVisible();
  await expect(box.getByRole("cell", { name: "21 %" })).toBeVisible();
  const input = box.getByLabel("Fórmula para D2");
  const status = box.getByRole("status");

  await input.fill("=B2*E1");
  await input.press("Enter");
  await expect(status).toContainText("Todavía no.");
  await expect(status).toContainText("Al copiarla, en D3 da 0 y debería dar 52,5");

  await input.fill("=B2*($E$1");
  await input.press("Enter");
  await expect(status).toContainText("Falta cerrar un paréntesis. (carácter 10)");

  await box.getByRole("button", { name: "Pedir una pista" }).click();
  await expect(box.getByText("Si copias =B2*E1 hacia abajo, ¿qué pasa con E1?")).toBeVisible();

  await input.fill("=B2*$E$1");
  await box.getByRole("button", { name: "Comprobar" }).click();
  await expect(status).toHaveText("Correcto. ");

  const results = await new AxeBuilder({ page }).include("#xl-prueba").withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"]).analyze();
  expect(results.violations).toEqual([]);
});

/* ---------- P2: el curso en la web ---------- */

const WCAG = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"];

test("el panel de Excel profesional se abre por enlace directo, resiste la recarga y muestra los avisos", async ({ page }) => {
  await page.goto("/#/academia/excel");
  const view = page.locator("#excel-view");
  await expect(view.getByRole("heading", { level: 1, name: "Excel profesional" })).toBeVisible();
  await page.reload();
  await expect(view.getByRole("heading", { level: 1, name: "Excel profesional" })).toBeVisible();
  await expect(view).toContainText("no está afiliado a Microsoft");
  await expect(view).toContainText("La corrección se hace en tu navegador y sirve para aprender; no es una evaluación oficial");
  await expect(view.locator(".xl-module")).toHaveCount(25);
  await expect(view.locator(".xl-module--soon")).toHaveCount(23);
  await expect(view.locator(".xl-module--soon a")).toHaveCount(0);
  await expect(view.locator(".xl-unit")).toHaveCount(9);
  await expect(page.locator('.site-nav a[data-nav="excel"]')).toHaveAttribute("aria-current", "page");
  await expect(page).toHaveTitle(/Excel profesional/);
});

test("el alias #/excel-academy lleva a la ruta del curso", async ({ page }) => {
  await page.goto("/#/excel-academy/xl1-datos");
  await expect(page).toHaveURL(/#\/academia\/excel\/xl1-datos$/);
  await expect(page.locator("#excel-view").getByRole("heading", { level: 1, name: "Introducir datos" })).toBeVisible();
});

test("una unidad o una página que no existen dan la página 404", async ({ page }) => {
  await page.goto("/#/academia/excel/xl9-nada");
  await expect(page.locator("#excel-view [data-not-found]")).toBeVisible();
  await page.goto("/#/academia/excel/xl1-datos/otra-cosa");
  await expect(page.locator("#excel-view [data-not-found]")).toBeVisible();
});

test("una unidad tiene sus apartados, se completa y «Continuar» la recuerda", async ({ page }) => {
  await page.goto("/#/academia/excel/xl1-referencias");
  const view = page.locator("#excel-view");
  for (const name of ["Al terminar sabrás", "Ejemplos resueltos", "Ejercicio guiado", "Errores frecuentes", "Resumen", "Para superar la unidad", "Fuentes"]) {
    await expect(view.getByRole("heading", { level: 2, name })).toBeVisible();
  }
  await expect(view.getByRole("table", { name: /Datos del ejemplo: IVA con la tasa fija/ })).toBeVisible();
  await view.getByRole("button", { name: "Marcar la unidad como completada" }).click();
  await expect(view.locator(".daw-complete .daw-done")).toBeFocused();
  await page.reload();
  await expect(view.getByText("Completada", { exact: true })).toBeVisible();
  const saved = await page.evaluate(() => JSON.parse(localStorage.getItem("pld:course:excel")));
  expect(Object.keys(saved.done)).toEqual(["xl1-referencias"]);
  expect(saved.lastLesson.slug).toBe("xl1-referencias");
  await page.goto("/#/academia/excel");
  await expect(view.getByRole("link", { name: /^Continuar: Interfaz, libros y hojas/ })).toBeVisible();
});

test("la práctica corrige test y fórmulas con teclado, guarda las respuestas y da la unidad por superada", async ({ page }) => {
  await page.goto("/#/academia/excel/xl1-referencias/practica");
  const view = page.locator("#excel-view");
  const formula = view.locator(".xl-item").filter({ hasText: "xl1-ref-07" });
  const input = formula.getByLabel("Fórmula para D2");
  await input.fill("=B2*E1");
  await input.press("Enter");
  await expect(formula.getByRole("status").first()).toContainText("Todavía no.");
  await input.fill("=B2*$E$1");
  await input.press("Enter");
  await expect(formula.getByRole("status").first()).toContainText("Correcto.");
  await expect(formula).toContainText("Último intento: bien");
  await expect(view.locator("#xl-status")).toContainText("obligatorios: 1 de 2");

  const choice = view.locator(".xl-item").filter({ hasText: "xl1-ref-02" });
  await choice.getByRole("radio", { name: "$E$1" }).check();
  await choice.getByRole("button", { name: "Comprobar" }).click();
  await expect(choice.getByRole("status")).toContainText("Correcto.");
  await expect(choice).toContainText("Con $ delante de la columna y de la fila");

  const saved = await page.evaluate(() => JSON.parse(localStorage.getItem("pld:course:excel")));
  expect(saved.answers["xl1-ref-07"]).toEqual([false, true]);
  expect(saved.answers["xl1-ref-02"]).toEqual([true]);

  // xl1-archivos solo tiene test: con todo bien, queda superada
  await page.goto("/#/academia/excel/xl1-archivos/practica");
  for (const item of await view.locator(".xl-item").all()) {
    await item.locator('input[type="radio"][value="0"]').check();
    await item.getByRole("button", { name: "Comprobar" }).click();
  }
  await expect(view.locator("#xl-status")).toContainText("8 de 8 bien");
  await expect(view.locator("#xl-status")).toContainText("✓ Unidad superada.");
  await page.goto("/#/academia/excel");
  await expect(view.locator(".xl-unit").filter({ hasText: "Guardar, exportar y compatibilidad" })).toContainText("✓ Superada");
});

for (const colorScheme of ["light", "dark"]) {
  test(`las páginas de Excel profesional no tienen infracciones WCAG en tema ${colorScheme}`, async ({ page }) => {
    await page.emulateMedia({ colorScheme });
    for (const route of ["/#/academia/excel", "/#/academia/excel/xl2-hojas", "/#/academia/excel/xl1-formatos/practica"]) {
      await page.goto(route);
      await expect(page.locator("#excel-view h1")).toBeVisible();
      await expect(page.locator("#excel-view [data-xl-question]").first().or(page.locator("#xl-path-title"))).toBeVisible();
      const results = await new AxeBuilder({ page }).include("#excel-view").withTags(WCAG).analyze();
      expect(results.violations, route).toEqual([]);
    }
  });
}

test("en un móvil de 320 px la práctica no se desplaza en horizontal", async ({ page }) => {
  await page.setViewportSize({ width: 320, height: 720 });
  await page.goto("/#/academia/excel/xl1-referencias/practica");
  await expect(page.locator("#excel-view h1")).toBeVisible();
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  expect(overflow).toBeLessThanOrEqual(0);
});
