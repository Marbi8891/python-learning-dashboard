// Excel profesional.
// P0: el curso está registrado en el catálogo (familia academia) y su progreso se fusiona y sincroniza
// con la cuenta como el de cualquier curso, sin aparecer todavía en la web ni entre los cursos de DAW.
// P1: el motor de fórmulas da lo mismo en el navegador que en Node, y los ejercicios de fórmulas se
// pueden usar con teclado y sin infracciones de accesibilidad. Todavía no hay ninguna ruta visible.
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
