const { test, expect, openLesson } = require("./fixtures");

// La primera ejecución descarga Pyodide (unos segundos)
test.describe.configure({ timeout: 120_000 });

const output = (page) => page.locator("#console-output");

async function run(page, code, stdin = "") {
  await page.locator("#console-editor").fill(code);
  if (stdin) {
    await page.locator("#console-stdin-box summary").click();
    await page.locator("#console-stdin").fill(stdin);
  }
  await page.locator("#console-run").click();
  await expect(page.locator("#console-run")).toBeEnabled({ timeout: 90_000 });
}

test("ejecuta el ejemplo con input() usando la entrada preparada", async ({ page }) => {
  await openLesson(page, "input");
  await page.locator("#console-run").click();
  await expect(output(page)).toContainText("Carlos, este año cumples 30 años", { timeout: 90_000 });
  await expect(page.locator("#console-status")).toHaveText("Python 3 listo");
});

test("muestra errores con la línea del alumno y pistas", async ({ page }) => {
  await openLesson(page, "variables");
  await run(page, "x = 1\nprint(x / 0)");
  await expect(output(page)).toContainText("line 2");
  await expect(output(page)).toContainText("ZeroDivisionError");

  await run(page, "nombre = input()");
  await expect(output(page)).toContainText("EOFError");
  await expect(output(page)).toContainText("Escríbelos en «Entrada»");

  await run(page, "import flask");
  await expect(output(page)).toContainText("Ejecuta este código en PyCharm");
});

test("corta un bucle infinito y la consola sigue funcionando", async ({ page }) => {
  await page.addInitScript(() => {
    window.PLD_CONFIG = Object.assign(window.PLD_CONFIG ?? {}, { runTimeoutMs: 4000 });
  });
  await openLesson(page, "bucles");
  await run(page, "print('calentando')"); // primera carga de Pyodide, fuera del límite
  await run(page, "while True:\n    pass");
  await expect(output(page)).toContainText("bucle infinito");
  await run(page, "print('sigo vivo')");
  await expect(output(page)).toContainText("sigo vivo");
});

test("Ctrl+Enter ejecuta y Tab inserta 4 espacios", async ({ page }) => {
  await openLesson(page, "variables");
  const editor = page.locator("#console-editor");
  await editor.fill("if True:\n");
  await editor.press("End");
  await editor.press("Tab");
  await editor.type("print('tab ok')");
  expect(await editor.inputValue()).toBe("if True:\n    print('tab ok')");
  await editor.press("Control+Enter");
  await expect(output(page)).toContainText("tab ok", { timeout: 90_000 });
});

test("el borrador del editor se conserva al recargar", async ({ page }) => {
  await openLesson(page, "tipos");
  await page.locator("#console-editor").fill("# mi borrador\nprint(1)");
  await page.reload();
  await page.locator(".lesson[data-slug]").first().waitFor({ state: "attached" });
  await expect(page.locator("#console-editor")).toHaveValue("# mi borrador\nprint(1)");
  await page.getByRole("button", { name: "Cargar ejemplo" }).click();
  await expect(page.locator("#console-editor")).toHaveValue(/precio = float/);
});

test("la plantilla de un ejercicio no supera los tests", async ({ page }) => {
  await openLesson(page, "funciones");
  await page.getByRole("tab", { name: "Práctica y Ejercicio" }).click();
  await page.getByRole("button", { name: "Cargar plantilla en la consola" }).click();
  await expect(page.locator("#console-editor")).toHaveValue(/def es_par/);
  await page.getByRole("button", { name: "Comprobar solución" }).click();
  const result = page.locator("#check-result");
  await expect(result).toHaveAttribute("data-passed", "false", { timeout: 90_000 });
  await expect(result).toContainText("Todavía no");
  await expect(page.locator(".lesson[data-slug=funciones]")).toHaveAttribute("data-status", "active");
});

test("superar los tests completa la lección", async ({ page }) => {
  // Ejercicio de prueba propio (así el repositorio no contiene soluciones de los reales)
  await page.route("**/data/lessons.json", async (route) => {
    const data = await (await route.fetch()).json();
    data.modules[0].lessons[0].checks = [{ stdin: "", test: "assert resultado == 42, 'resultado debe ser 42'" }];
    await route.fulfill({ json: data });
  });
  await openLesson(page, "variables");
  await page.getByRole("tab", { name: "Práctica y Ejercicio" }).click();

  await page.locator("#console-editor").fill("resultado = 41");
  await page.getByRole("button", { name: "Comprobar solución" }).click();
  await expect(page.locator("#check-result")).toContainText("resultado debe ser 42", { timeout: 90_000 });

  await page.locator("#console-editor").fill("resultado = 6 * 7");
  await page.getByRole("button", { name: "Comprobar solución" }).click();
  await expect(page.locator("#check-result")).toHaveAttribute("data-passed", "true");
  await expect(page.locator("#progress-value")).toHaveText("25%");
  await expect(page.getByRole("button", { name: "Marcar como pendiente" })).toBeVisible();
});
