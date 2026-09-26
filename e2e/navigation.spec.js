const { test, expect, openLesson } = require("./fixtures");

test("la portada lleva a la primera lección pendiente y la barra lateral navega", async ({ page }) => {
  await openLesson(page);
  await expect(page).toHaveURL(/#\/inicio$/);
  await expect(page.locator("#home-title")).toContainText("Aprende Python paso a paso");
  await page.getByRole("link", { name: "Empezar la primera lección →" }).click();
  await expect(page).toHaveURL(/#\/leccion\/variables$/);
  await expect(page.locator("#lesson-title")).toHaveText("Variables y print()");
  await expect(page.locator(".lesson[data-slug]")).toHaveCount(15);

  await page.locator(".lesson[data-slug=tipos]").click();
  await expect(page).toHaveURL(/#\/leccion\/tipos$/);
  await expect(page.locator("#lesson-title")).toHaveText("Tipos de datos");
  await expect(page.locator(".lesson[data-slug=tipos]")).toHaveAttribute("aria-current", "page");
  await expect(page.locator("#panel-theory code.hljs")).toHaveCount(1); // resaltado de sintaxis
});

test("una URL desconocida redirige a una lección válida", async ({ page }) => {
  await openLesson(page, "no-existe");
  await expect(page).toHaveURL(/#\/leccion\/variables$/);
});

test("pestañas accesibles con teclado", async ({ page }) => {
  await openLesson(page, "variables");
  const theory = page.getByRole("tab", { name: "Teoría y Ejemplos" });
  await theory.focus();
  await page.keyboard.press("ArrowRight");
  const practice = page.getByRole("tab", { name: "Práctica y Ejercicio" });
  await expect(practice).toBeFocused();
  await expect(practice).toHaveAttribute("aria-selected", "true");
  await expect(page.locator("#panel-practice")).toBeVisible();
  await expect(page.locator("#panel-theory")).toBeHidden();
});

test("el anillo de progreso y su porcentaje están superpuestos", async ({ page }) => {
  // Regresión: un selector CSS roto descolocaba el anillo
  await openLesson(page, "variables");
  const ring = await page.locator(".progress__ring").boundingBox();
  const value = await page.locator(".progress__value").boundingBox();
  const centerX = value.x + value.width / 2;
  const centerY = value.y + value.height / 2;
  expect(centerX).toBeGreaterThan(ring.x);
  expect(centerX).toBeLessThan(ring.x + ring.width);
  expect(centerY).toBeGreaterThan(ring.y);
  expect(centerY).toBeLessThan(ring.y + ring.height);
});

test("marcar como completada actualiza el progreso y persiste", async ({ page }) => {
  await openLesson(page, "variables");
  await expect(page.locator(".lesson[data-slug=operadores]")).toHaveAttribute("data-status", "locked");
  await page.getByRole("tab", { name: "Práctica y Ejercicio" }).click();
  await page.getByRole("button", { name: "Marcar como completada" }).click();
  await expect(page.locator("#progress-value")).toHaveText("25%");
  await expect(page.locator("#progress")).toHaveAttribute("aria-valuenow", "25");

  await page.reload();
  await page.locator(".lesson[data-slug]").first().waitFor({ state: "attached" });
  await expect(page.locator(".lesson[data-slug=variables]")).toHaveAttribute("data-status", "active");
  await page.locator(".lesson[data-slug=tipos]").click();
  await expect(page.locator(".lesson[data-slug=variables]")).toHaveAttribute("data-status", "completed");
  await expect(page.locator(".module[data-module=fundamentos] .module__count")).toHaveText("1/4");
});

test("copiar y «Abrir en PyCharm» muestran la guía y la descarga", async ({ page, context }) => {
  await context.grantPermissions(["clipboard-read", "clipboard-write"]);
  await openLesson(page, "variables");
  await page.getByRole("button", { name: "Abrir en PyCharm" }).click();
  await expect(page.locator("#pycharm-hint")).toBeVisible();
  const clipboard = await page.evaluate(() => navigator.clipboard.readText());
  expect(clipboard).toContain('nombre = "Carlos"');

  const download = page.waitForEvent("download");
  await page.getByRole("link", { name: "Descargar variables.py" }).click();
  expect((await download).suggestedFilename()).toBe("variables.py");
});

test("la teoría enlaza sus fuentes", async ({ page }) => {
  await openLesson(page, "funciones");
  const sources = page.locator(".sources a");
  expect(await sources.count()).toBeGreaterThan(0);
  await expect(sources.first()).toHaveAttribute("href", /^https:\/\//);
  await expect(sources.first()).toHaveAttribute("rel", /noopener/);
});
