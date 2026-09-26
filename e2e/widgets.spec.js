const { test, expect, openLesson } = require("./fixtures");

test("el asistente responde por lección, da pistas y lleva al siguiente tema", async ({ page }) => {
  await openLesson(page, "variables");
  const toggle = page.getByRole("button", { name: "Abrir asistente" });
  await toggle.click();
  await expect(toggle).toHaveAttribute("aria-expanded", "true");
  await expect(page.locator(".assistant__msg").first()).toContainText("Variables y print()");

  await page.getByRole("button", { name: "¿Qué diferencia hay entre = y ==?" }).click();
  await expect(page.locator(".assistant__msg--bot").last()).toContainText("asigna");

  await page.getByRole("button", { name: "Dame una pista del ejercicio" }).click();
  await expect(page.locator(".assistant__msg--bot").last()).toContainText("f-string");

  await page.getByRole("button", { name: /Siguiente tema: Tipos de datos/ }).click();
  await expect(page).toHaveURL(/#\/leccion\/tipos$/);
  await expect(page.locator(".assistant__msg").first()).toContainText("Tipos de datos");

  await page.locator(".assistant__panel .chip").first().focus();
  await page.keyboard.press("Escape");
  await expect(page.locator("#assistant-panel")).toBeHidden();
  await expect(toggle).toBeFocused();
});

test.describe("móvil", () => {
  test.use({ viewport: { width: 390, height: 844 } });

  test("menú lateral deslizante accesible", async ({ page }) => {
    await openLesson(page, "funciones");
    const sidebar = page.locator("#sidebar");
    const menu = page.getByRole("button", { name: "Lecciones" });
    expect(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth)).toBe(false);
    expect(await sidebar.evaluate((el) => el.inert)).toBe(true);

    await menu.click();
    await expect(menu).toHaveAttribute("aria-expanded", "true");
    expect(await sidebar.evaluate((el) => el.inert)).toBe(false);
    await expect(page.locator(".lesson[data-slug=funciones]")).toBeFocused();

    await page.keyboard.press("Escape");
    await expect(menu).toHaveAttribute("aria-expanded", "false");
    await expect(menu).toBeFocused();

    await menu.click();
    await page.locator(".lesson[data-slug=colecciones]").click();
    await expect(page).toHaveURL(/#\/leccion\/colecciones$/);
    await expect(menu).toHaveAttribute("aria-expanded", "false");
  });
});

test("la política de privacidad es accesible desde la app", async ({ page }) => {
  await openLesson(page);
  await page.getByRole("link", { name: "Privacidad" }).click();
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("Política de privacidad");
  await expect(page.getByText("Eliminar mi cuenta", { exact: false }).first()).toBeVisible();
});
