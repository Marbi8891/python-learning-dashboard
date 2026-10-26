// Currículo oficial de DAW (#/daw/curriculo): índice por cursos, un módulo con sus RA y CE,
// módulos pendientes y auditoría de accesibilidad en claro y en oscuro.
const AxeBuilder = require("@axe-core/playwright").default;
const { test, expect } = require("./fixtures");

test("desde la Preparación DAW se llega al currículo con los 17 módulos por curso", async ({ page }) => {
  await page.goto("/#/daw");
  await page.getByRole("link", { name: "Currículo oficial del ciclo" }).click();
  await expect(page).toHaveURL(/#\/daw\/curriculo$/);
  await expect(page.locator("#daw-title")).toHaveText("Currículo oficial de DAW");
  await expect(page.getByRole("note").first()).toContainText("no son evaluaciones oficiales");
  await expect(page.getByRole("heading", { level: 2, name: "Primer curso" })).toBeVisible();
  await expect(page.getByRole("heading", { level: 2, name: "Segundo curso" })).toBeVisible();
  await expect(page.locator(".curr-table tbody tr")).toHaveCount(17);
  const programacion = page.getByRole("row", { name: /0485 · Programación/ });
  await expect(programacion).toContainText("272");
  await expect(programacion).toContainText("9 RA oficiales");
  await expect(programacion).toContainText("Programación, Java (243 preguntas)");
  await expect(page.getByRole("row", { name: /1709/ })).toContainText("RA pendientes");
});

test("un módulo muestra sus datos, sus RA con criterios y la fuente", async ({ page }) => {
  await page.goto("/#/daw/curriculo");
  await page.getByRole("link", { name: "0485 · Programación" }).click();
  await expect(page).toHaveURL(/#\/daw\/curriculo\/0485$/);
  await expect(page.locator("#daw-title")).toHaveText("Programación");
  await expect(page.locator(".curr-facts")).toContainText("272");
  await expect(page.locator(".curr-facts")).toContainText("14");
  await expect(page.getByRole("heading", { name: "Resultados de aprendizaje (9)" })).toBeVisible();
  const first = page.locator("details", { hasText: "RA1. Reconoce la estructura de un programa informático" });
  await first.locator("summary").click();
  await expect(first.locator(".curr-criteria li").first()).toContainText("a)");
  await expect(page.getByRole("link", { name: /Real Decreto 405\/2023/ }).first()).toHaveAttribute("href", /BOE-A-2023-13221/);
  await page.getByRole("link", { name: "Programación", exact: true }).click();
  await expect(page).toHaveURL(/#\/daw\/programacion$/);
});

test("un módulo pendiente dice dónde están sus RA y no inventa ninguno", async ({ page }) => {
  await page.goto("/#/daw/curriculo/1709");
  await expect(page.locator("#daw-title")).toHaveText("Itinerario personal para la empleabilidad I");
  await expect(page.locator(".empty-state")).toContainText("todavía no se han incorporado");
  await expect(page.locator(".empty-state")).toContainText("Real Decreto 659/2023");
  await expect(page.locator(".curr-criteria")).toHaveCount(0);
});

test("un módulo que no existe lleva de vuelta al índice", async ({ page }) => {
  await page.goto("/#/daw/curriculo/9999");
  await expect(page.locator("#daw-title")).toContainText("No hay ningún módulo «9999»");
  await page.getByRole("link", { name: "Ver todos los módulos" }).click();
  await expect(page.locator("#daw-title")).toHaveText("Currículo oficial de DAW");
});

for (const colorScheme of ["light", "dark"]) {
  test(`índice y módulo sin infracciones WCAG en modo ${colorScheme}`, async ({ page }) => {
    await page.emulateMedia({ colorScheme });
    for (const route of ["/#/daw/curriculo", "/#/daw/curriculo/0612", "/#/daw/curriculo/0616"]) {
      await page.goto(route);
      await expect(page.locator("#daw-view .daw-crumb")).toBeVisible(); // ya no está el «Cargando…»
      const summaries = page.locator("#daw-view details summary");
      if ((await summaries.count()) > 0) {
        await summaries.first().click(); // se audita también un RA abierto
        await expect(page.locator("#daw-view details[open] .curr-criteria")).toBeVisible();
      }
      await page.waitForFunction(() => document.getAnimations().every((a) => a.playState !== "running"));
      const results = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"]).analyze();
      const summary = results.violations.map((v) => `${v.id}: ${v.nodes.map((n) => n.target).join(", ")}`);
      expect(summary, `${route}\n${summary.join("\n")}`).toEqual([]);
    }
  });
}
