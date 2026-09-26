// Auditoría automática de accesibilidad (WCAG 2.1 A/AA) con axe-core.
// El tema «Automático» sigue al sistema: se audita la app en claro y en oscuro.
const AxeBuilder = require("@axe-core/playwright").default;
const { test, expect, openLesson } = require("./fixtures");

async function audit(page) {
  const results = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"]).analyze();
  const summary = results.violations.map((v) => `${v.id} (${v.impact}): ${v.nodes.map((n) => n.target).join(", ")}`);
  expect(summary, summary.join("\n")).toEqual([]);
}

for (const colorScheme of ["light", "dark"]) {
  test.describe(`sistema en modo ${colorScheme}`, () => {
    test.use({ colorScheme });
    test("lección y quiz con código sin infracciones WCAG", async ({ page }) => {
      await openLesson(page, "funciones");
      await expect(page.locator("html")).toHaveAttribute("data-theme", colorScheme);
      await audit(page);
      await page.getByRole("tab", { name: "Quiz" }).click();
      await audit(page);
    });
  });
}

test("pestaña de práctica, asistente y diálogo de cuenta sin infracciones", async ({ page }) => {
  await openLesson(page, "bucles");
  await page.getByRole("tab", { name: "Práctica y Ejercicio" }).click();
  await page.getByRole("button", { name: "Abrir asistente" }).click();
  await audit(page);
  await page.keyboard.press("Escape");
  await page.getByRole("button", { name: "Iniciar sesión" }).click();
  await audit(page);
});

test.describe("móvil", () => {
  test.use({ viewport: { width: 390, height: 844 } });
  test("menú abierto sin infracciones", async ({ page }) => {
    await openLesson(page, "funciones");
    await page.getByRole("button", { name: "Lecciones" }).click();
    await audit(page);
  });
});

test("quiz respondido, reto y vitrina de logros sin infracciones", async ({ page }) => {
  await openLesson(page, "funciones");
  await page.getByRole("tab", { name: "Quiz" }).click();
  for (let qi = 0; qi < 3; qi += 1) await page.locator(`input[name=q${qi}]`).first().check();
  await page.getByRole("button", { name: "Comprobar respuestas" }).click();
  await audit(page);
  await page.getByRole("button", { name: /Logros/ }).click();
  await audit(page);
});

test("política de privacidad sin infracciones", async ({ page }) => {
  await page.goto("/privacidad.html");
  await audit(page);
});

test("portada sin infracciones", async ({ page }) => {
  await openLesson(page);
  await expect(page.locator("#home-title")).toBeVisible();
  await audit(page);
});

test("tema claro con error explicado y diálogo de aspecto sin infracciones", async ({ page }) => {
  test.setTimeout(120_000);
  await page.addInitScript(() => localStorage.setItem("pld:prefs", JSON.stringify({ theme: "light", font: "grande" })));
  await openLesson(page, "variables");
  await page.locator("#console-editor").fill("print(x)");
  await page.locator("#console-run").click();
  await expect(page.getByRole("note")).toBeVisible({ timeout: 90_000 });
  await audit(page);
  await page.getByRole("button", { name: "Aspecto" }).click();
  await audit(page);
});
