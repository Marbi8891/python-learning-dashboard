// Web para todo el mundo (F2): preferencias de lectura, contraste alto, teclado y reflujo.
const AxeBuilder = require("@axe-core/playwright").default;
const { test, expect, openLesson } = require("./fixtures");

const cssVar = (page, name) =>
  page.evaluate((n) => getComputedStyle(document.documentElement).getPropertyValue(n).trim(), name);
const horizontalOverflow = (page) =>
  page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);

async function openAppearance(page) {
  await page.getByRole("button", { name: "Aspecto" }).click();
  await expect(page.locator("#appearance-dialog")).toBeVisible();
}

test("texto espaciado, contraste alto y sin animaciones se aplican y se recuerdan", async ({ page }) => {
  await openLesson(page, "variables");
  const paragraph = page.locator("#lesson-view p").first();
  const before = await paragraph.evaluate((el) => parseFloat(getComputedStyle(el).lineHeight));

  await openAppearance(page);
  await page.getByLabel("Texto más espaciado").check();
  await page.getByLabel("Contraste alto").check();
  await page.getByLabel("Sin animaciones").check();
  const root = page.locator("html");
  await expect(root).toHaveAttribute("data-spacing", "amplio");
  await expect(root).toHaveAttribute("data-contrast", "alto");
  await expect(root).toHaveAttribute("data-motion", "reducido");

  const after = await paragraph.evaluate((el) => parseFloat(getComputedStyle(el).lineHeight));
  expect(after).toBeGreaterThan(before);
  expect(await cssVar(page, "--color-text-muted")).toBe(await cssVar(page, "--color-text"));
  // El código no se espacia: las columnas siguen alineadas
  const codeSpacing = await page
    .locator("#lesson-view pre")
    .first()
    .evaluate((el) => getComputedStyle(el).letterSpacing);
  expect(codeSpacing).toBe("normal");

  await page.reload();
  await expect(root).toHaveAttribute("data-spacing", "amplio");
  await expect(root).toHaveAttribute("data-contrast", "alto");
  await expect(root).toHaveAttribute("data-motion", "reducido");
  await openAppearance(page);
  await expect(page.getByLabel("Texto más espaciado")).toBeChecked();
  await page.getByLabel("Contraste alto").uncheck();
  await expect(root).not.toHaveAttribute("data-contrast", "alto");
});

test("el contraste alto del sistema se respeta sin tocar nada", async ({ page }) => {
  await page.emulateMedia({ contrast: "more" });
  await openLesson(page, "variables");
  expect(await cssVar(page, "--color-text-faint")).toBe(await cssVar(page, "--color-text"));
});

for (const colorScheme of ["light", "dark"]) {
  test(`con las tres opciones de lectura no hay infracciones WCAG (${colorScheme})`, async ({ page }) => {
    await page.emulateMedia({ colorScheme });
    await page.addInitScript(() =>
      localStorage.setItem("pld:prefs", JSON.stringify({ spacing: true, contrast: true, motion: true })),
    );
    await openLesson(page, "funciones");
    const results = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"]).analyze();
    const summary = results.violations.map((v) => `${v.id}: ${v.nodes.map((n) => n.target).join(", ")}`);
    expect(summary, summary.join("\n")).toEqual([]);
  });
}

test("con el teclado: el primer Tab ofrece saltar al contenido y se ve dónde está el foco", async ({ page }) => {
  await openLesson(page, "variables");
  await page.keyboard.press("Tab");
  const skip = page.getByRole("link", { name: "Saltar al contenido" });
  await expect(skip).toBeFocused();
  await expect(skip).toBeInViewport();
  await page.keyboard.press("Enter");
  await expect(page.locator("#main")).toBeFocused();

  // El panel de Aspecto se abre, se usa y se cierra solo con el teclado
  const appearance = page.getByRole("button", { name: "Aspecto" });
  await appearance.focus();
  const outline = await appearance.evaluate((el) => getComputedStyle(el).outlineStyle);
  expect(outline).not.toBe("none");
  await page.keyboard.press("Enter");
  await expect(page.locator("#appearance-dialog")).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(page.locator("#appearance-dialog")).toBeHidden();
});

// WCAG 1.4.10: a 320 px (o con zoom al 200 % en una pantalla de 1280 × 720) no hay scroll lateral
const ROUTES = ["/#/portada", "/#/aprender", "/#/leccion/variables", "/#/practicar", "/#/progreso", "/#/pcap", "/#/daw"];
for (const viewport of [
  { width: 320, height: 640 },
  { width: 640, height: 360 },
]) {
  test(`sin desplazamiento lateral a ${viewport.width} px`, async ({ page }) => {
    await page.setViewportSize(viewport);
    for (const route of ROUTES) {
      await page.goto(route);
      await page.waitForLoadState("networkidle");
      expect(await horizontalOverflow(page), route).toBeLessThanOrEqual(0);
    }
  });
}

test("WCAG 1.4.12: la lección aguanta el espaciado de texto máximo sin cortarse", async ({ page }) => {
  await openLesson(page, "variables");
  await page.addStyleTag({
    content: `* { line-height: 1.5 !important; letter-spacing: 0.12em !important; word-spacing: 0.16em !important; }
              p { margin-bottom: 2em !important; }`,
  });
  expect(await horizontalOverflow(page)).toBeLessThanOrEqual(0);
});
