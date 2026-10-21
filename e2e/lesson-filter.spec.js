const { test, expect, openLesson } = require("./fixtures");

test("el buscador de la barra lateral filtra lecciones sin tildes y con «Solo pendientes»", async ({ page }) => {
  await page.addInitScript(() => localStorage.setItem("pld:completed", JSON.stringify(["variables"])));
  await openLesson(page, "bucles");
  const search = page.getByRole("searchbox", { name: "Buscar lección" });
  const visible = page.locator("#modules .lesson[data-slug]:visible");
  const total = await page.locator("#modules .lesson[data-slug]").count();

  await search.fill("VARIABLE");
  await expect(page.locator("#lesson-filter-status")).toHaveText(/^\d+ lecci/);
  await expect(visible.first()).toBeVisible();
  for (const name of await visible.allTextContents()) expect(name.toLowerCase()).toMatch(/variable/);

  await page.getByLabel("Solo pendientes").check();
  await expect(page.locator('#modules .lesson[data-slug="variables"]')).toBeHidden();

  await search.fill("zzzz");
  await expect(page.locator("#lesson-filter-status")).toHaveText("Ninguna lección coincide");

  await page.getByLabel("Solo pendientes").uncheck();
  await search.press("Escape");
  await expect(search).toHaveValue("");
  await expect(page.locator("#lesson-filter-status")).toHaveText("");
  expect(await page.locator("#modules li:not([hidden]) .lesson[data-slug]").count()).toBe(total);
});
