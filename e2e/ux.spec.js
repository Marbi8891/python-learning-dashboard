// Experiencia del alumno: portada, guía paso a paso, errores explicados y apariencia.
const { test, expect, openLesson } = require("./fixtures");

test("la portada muestra el progreso y cambia a «Continuar»", async ({ page }) => {
  await openLesson(page, "variables");
  await page.getByRole("tab", { name: "Práctica y Ejercicio" }).click();
  await page.getByRole("button", { name: "Marcar como completada" }).click();
  await page.getByRole("link", { name: /Python Learning/ }).click();
  await expect(page).toHaveURL(/#\/inicio$/);
  await expect(page.locator(".home__stats")).toContainText("1/15");
  await page.getByRole("link", { name: "Continuar: Tipos de datos →" }).click();
  await expect(page.locator("#lesson-title")).toHaveText("Tipos de datos");
});

test("la guía avanza Aprende → Practica → Comprueba", async ({ page }) => {
  await openLesson(page, "variables");
  const next = page.locator("#next-step");
  const current = page.locator('.step[aria-current="step"]');
  await expect(current).toContainText("Aprende");
  await expect(next).toHaveText("Ya lo he leído: a practicar →");

  await next.click();
  await expect(page.getByRole("tab", { name: "Práctica y Ejercicio" })).toHaveAttribute("aria-selected", "true");
  await expect(current).toContainText("Practica");
  await expect(page.locator('.step[data-state="done"]')).toContainText("Aprende");
  await expect(next).toHaveText("Cargar la plantilla y empezar →");
  await next.click();
  await expect(page.locator("#console-editor")).not.toHaveValue("");

  await page.getByRole("button", { name: "Marcar como completada" }).click();
  await expect(current).toContainText("Comprueba");
  await expect(next).toHaveText("Hacer el mini-quiz →");
  await next.click();
  await expect(page.getByRole("tab", { name: "Quiz" })).toHaveAttribute("aria-selected", "true");
  for (let qi = 0; qi < 3; qi += 1) await page.locator(`input[name=q${qi}]`).first().check();
  await page.getByRole("button", { name: "Comprobar respuestas" }).click();
  await expect(next).toHaveText("Siguiente lección: Tipos de datos →");
  await next.click();
  await expect(page).toHaveURL(/#\/leccion\/tipos$/);
});

test("explica el error en español y lleva a la línea", async ({ page }) => {
  test.setTimeout(120_000);
  await openLesson(page, "variables");
  await page.locator("#console-editor").fill("nombre = 'Ana'\nprint(nombre + 5)");
  await page.locator("#console-run").click();
  const help = page.getByRole("note");
  await expect(help).toContainText("Mezclas tipos que no se combinan", { timeout: 90_000 });
  await help.getByRole("button", { name: "Ir a la línea 2" }).click();
  await expect(page.locator("#console-editor")).toBeFocused();
  const selected = await page
    .locator("#console-editor")
    .evaluate((editor) => editor.value.slice(editor.selectionStart, editor.selectionEnd));
  expect(selected).toBe("print(nombre + 5)");
});

test("el tema y el tamaño de letra se recuerdan", async ({ page }) => {
  await openLesson(page, "variables");
  await page.getByRole("button", { name: "Aspecto" }).click();
  await page.getByLabel("Claro").check();
  await page.getByLabel("Grande", { exact: true }).check();
  const root = page.locator("html");
  await expect(root).toHaveAttribute("data-theme", "light");
  await expect(root).toHaveAttribute("data-font", "grande");
  await page.reload();
  await expect(root).toHaveAttribute("data-theme", "light");
  await expect(root).toHaveAttribute("data-font", "grande");
});

test.describe("pantalla ancha", () => {
  test.use({ viewport: { width: 1366, height: 768 } });
  test("la consola queda al lado de la lección", async ({ page }) => {
    await openLesson(page, "variables");
    const lesson = await page.locator(".workspace__lesson").boundingBox();
    const console = await page.locator("#lesson-view > .console").boundingBox();
    expect(console.x).toBeGreaterThanOrEqual(lesson.x + lesson.width);
    expect(console.y).toBeLessThan(lesson.y + 200);
  });
});
