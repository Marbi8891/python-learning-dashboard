const { test, expect } = require("./fixtures");

test.describe("PLD ACADEMY institutional workspace MVP", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/#/academy");
    await expect(page.locator("#academy-view")).toBeVisible();
    await expect(page.getByRole("heading", { name: "Buenos días" })).toBeVisible();
  });

  test("shows the center workspace and group overview", async ({ page }) => {
    await expect(page.getByText("Centro de Formación PLD", { exact: true })).toBeVisible();
    await expect(page.getByText("1.º DAW A", { exact: true }).first()).toBeVisible();
    await expect(page.getByRole("button", { name: "Grupos" })).toBeVisible();
  });

  test("creates a group and persists it in the demo workspace", async ({ page }) => {
    await page.getByRole("button", { name: "＋ Crear grupo" }).click();
    await page.getByRole("heading", { name: "Crear grupo" }).waitFor();
    await page.locator("#academy-group-form [name=name]").fill("2.º DAW B");
    await page.locator("#academy-group-form [name=program]").fill("Desarrollo Web");
    await page.locator("#academy-group-form [name=subject]").fill("Entorno cliente");
    await page.locator("#academy-group-form [name=teacher]").fill("Docente Demo");
    await page.locator("#academy-group-form [name=students]").fill("22");
    await page.getByRole("button", { name: "Crear grupo", exact: true }).click();
    await expect(page.getByText("2.º DAW B", { exact: true })).toBeVisible();
    await page.reload();
    await expect(page.getByRole("link", { name: /PLD ACADEMY/ })).toBeVisible();
    await page.getByRole("link", { name: /PLD ACADEMY/ }).click();
    await page.getByRole("button", { name: "Grupos" }).click();
    await expect(page.getByText("2.º DAW B", { exact: true })).toBeVisible();
  });

  test("creates an activity and switches to teacher/student preview", async ({ page }) => {
    await page.getByRole("button", { name: "＋ Crear actividad" }).click();
    await page.locator("#academy-assignment-form [name=title]").fill("Repaso de funciones");
    await page.locator("#academy-assignment-form [name=groupId]").selectOption("g-dam1");
    await page.locator("#academy-assignment-form [name=type]").selectOption("Práctica");
    await page.locator("#academy-assignment-form [name=due]").fill("2026-12-08");
    await page.getByRole("button", { name: "Guardar actividad" }).click();
    await expect(page.getByText("Repaso de funciones", { exact: true })).toBeVisible();
    await page.locator("#academy-role").selectOption("teacher");
    await expect(page.getByRole("heading", { name: "Mis clases" })).toBeVisible();
    await page.locator("#academy-role").selectOption("student");
    await expect(page.getByRole("heading", { name: "Mi aprendizaje" })).toBeVisible();
    await expect(page.getByText("Repaso de funciones", { exact: true })).toBeVisible();
  });
});
