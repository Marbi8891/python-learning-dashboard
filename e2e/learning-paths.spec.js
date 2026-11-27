const { test, expect } = require("./fixtures");

test("Learning Paths detail route loads once and renders progress", async ({ page }) => {
  await page.addInitScript(() => localStorage.removeItem("pld:learning-paths:selected"));
  let learningRequests = 0;
  page.on("request", (request) => {
    if (new URL(request.url()).pathname.endsWith("/data/learning.json")) learningRequests += 1;
  });

  await page.goto("/#/paths/python-developer");
  await expect(page.locator("#paths-view")).toBeVisible();
  await expect(page.locator("#paths-title")).toHaveText("Python Developer");
  await expect(page.locator(".path-step")).toHaveCount(7);
  await expect(page.locator(".path-progress")).toContainText("conceptos");
  await expect.poll(() => learningRequests).toBe(1);
});

test("Learning Paths selection is optional and persisted locally", async ({ page }) => {
  await page.addInitScript(() => localStorage.removeItem("pld:learning-paths:selected"));
  await page.goto("/#/paths");

  await expect(page.locator("#paths-title")).toHaveText("Learning Paths");
  await page.getByRole("button", { name: "Añadir Path" }).first().click();
  await expect(page.locator("#paths-view")).toContainText("Mis Paths");
  await expect(page.getByRole("button", { name: "Quitar de mis Paths" }).first()).toBeVisible();

  await page.reload();
  await expect(page.locator("#paths-view")).toContainText("Mis Paths");
  await expect(page.getByRole("button", { name: "Quitar de mis Paths" }).first()).toBeVisible();
});
