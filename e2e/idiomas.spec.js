// Idiomas (F3): interfaz en inglés, código protegido del traductor y aviso para otros navegadores.
const AxeBuilder = require("@axe-core/playwright").default;
const { test, expect, openLesson } = require("./fixtures");

test("se cambia a inglés desde Aspecto y se recuerda", async ({ page }) => {
  await openLesson(page, "variables");
  await page.getByRole("button", { name: "Aspecto" }).click();
  // Elegir idioma recarga la página
  const root = page.locator("html");
  await page.getByLabel("English").click();
  await expect(root).toHaveAttribute("lang", "en");
  await expect(page.getByRole("button", { name: "Run", exact: true })).toBeVisible();
  await expect(page.getByRole("link", { name: "Skip to content" })).toBeAttached();
  await expect(page.locator("#console-status")).toHaveText("Python loads the first time you run code");
  await expect(page.locator("#xp-streak")).toHaveText("Streak: 0 days");
  await expect(page.locator("#xp-level")).toHaveText("Level 1 · Newbie");
  // La lección sigue en español y se marca como tal (WCAG 3.1.2); el código no se traduce
  await expect(page.locator("#lesson-view .prose").first()).toHaveAttribute("lang", "es");
  await expect(page.locator("#lesson-view pre").first()).toHaveAttribute("translate", "no");

  await page.reload();
  await expect(root).toHaveAttribute("lang", "en");
  await page.getByRole("button", { name: "Appearance" }).click();
  await expect(page.locator("#lang-note")).toBeVisible();
  await page.getByLabel("Español").click();
  await expect(root).toHaveAttribute("lang", "es");
  await expect(page.getByRole("button", { name: "Ejecutar", exact: true })).toBeVisible();
});

test("en inglés no hay infracciones WCAG", async ({ page }) => {
  await page.addInitScript(() => localStorage.setItem("pld:prefs", JSON.stringify({ lang: "en" })));
  await openLesson(page, "funciones");
  await expect(page.locator("html")).toHaveAttribute("lang", "en");
  await expect(page.locator("html")).not.toHaveAttribute("data-i18n-pending", "");
  const results = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"]).analyze();
  const summary = results.violations.map((v) => `${v.id}: ${v.nodes.map((n) => n.target).join(", ")}`);
  expect(summary, summary.join("\n")).toEqual([]);
});

test("en español el código también lleva translate=no para el traductor del navegador", async ({ page }) => {
  await openLesson(page, "variables");
  await expect(page.locator("#console-editor")).toHaveAttribute("translate", "no");
  await expect(page.locator("#lesson-view pre").first()).toHaveAttribute("translate", "no");
  await expect(page.locator(".lang-banner")).toHaveCount(0); // el navegador de las pruebas está en español
});

test.describe("navegador en otro idioma", () => {
  test.use({ locale: "fr-FR" });
  test("ofrece la interfaz en inglés una sola vez", async ({ page }) => {
    await openLesson(page, "variables");
    const banner = page.getByRole("complementary", { name: "Language" });
    await expect(banner).toBeVisible();
    await banner.getByRole("button", { name: "Seguir en español" }).click();
    await expect(banner).toHaveCount(0);
    await page.reload();
    await expect(page.locator(".lang-banner")).toHaveCount(0);
  });

  test("«Use English» cambia la interfaz", async ({ page }) => {
    await openLesson(page, "variables");
    await page.getByRole("button", { name: "Use English" }).click();
    await page.waitForLoadState("load");
    await expect(page.locator("html")).toHaveAttribute("lang", "en");
    await expect(page.getByRole("button", { name: "Run", exact: true })).toBeVisible();
  });
});
