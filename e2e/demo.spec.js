// Demo Edition: modo demostración, laboratorio de Python y centro de aprendizaje (docs/DEMO-TESTING.md)
const AxeBuilder = require("@axe-core/playwright").default;
const { test, expect } = require("./fixtures");

// El laboratorio ejecuta Python de verdad: la primera vez se carga Pyodide
test.describe.configure({ timeout: 120_000 });

const WCAG = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"];
const API = /127\.0\.0\.1:8000|localhost:8000|onrender\.com/;

const settled = (page) => page.waitForFunction(() => document.getAnimations().every((a) => a.playState !== "running"));

/** Peticiones al servidor desde que se llama hasta el final de la prueba. */
function watchApi(page) {
  const calls = [];
  page.on("request", (request) => {
    if (API.test(request.url())) calls.push(request.url());
  });
  return calls;
}

test("la demo entra sin registro como Alex Developer, con datos ficticios y sin tocar el progreso real", async ({ page }) => {
  await page.goto("/#/portada");
  await page.evaluate(() => localStorage.setItem("pld:completed", JSON.stringify(["paquetes"])));
  const before = await page.evaluate(() => JSON.stringify(Object.entries(localStorage).sort()));

  const api = watchApi(page);
  await page.getByRole("link", { name: "Probar la demo sin registrarte" }).click();
  await expect(page.locator("#private-title")).toHaveText("Hola, Alex Developer");
  await expect(page).toHaveURL(/#\/panel$/);
  expect(page.url()).not.toContain("demo=1"); // la marca se quita de la dirección

  const banner = page.getByRole("complementary", { name: "Modo demostración" });
  await expect(banner).toBeVisible();
  await expect(banner).toContainText("alumno ficticio");
  await expect(page.locator("#private-nav")).toBeVisible();

  // Datos deterministas: el mismo resumen cada vez
  const kpis = page.locator(".dash-kpis");
  await expect(kpis).toContainText("6/27"); // lecciones del curso PCAP
  await expect(kpis).toContainText("Programador/a en prácticas");
  await expect(kpis).toContainText("6 días"); // racha que termina hoy
  await expect(kpis).toContainText("7/20"); // logros
  await expect(kpis).toContainText("Tiempo estimado");
  // Los logros de Alex ya vienen ganados: entrar no «desbloquea» nada
  await expect(page.locator("#toast")).not.toContainText("Logro desbloqueado");

  for (const section of ["cursos", "progreso", "actividad", "planificacion", "logros", "perfil"]) {
    await page.goto(`/#/panel/${section}`);
    await expect(page.locator("#dash-body")).toBeVisible();
  }
  await expect(page.locator("#dash-body")).toContainText("Cuenta de demostración");
  await expect(page.locator("#dash-body")).not.toContainText("Descargar mis datos");

  // Recargar sigue en la demo
  await page.reload();
  await expect(page.locator("#private-title")).toHaveText("Hola, Alex Developer");

  expect(api, "la demo no llama al servidor").toEqual([]);
  expect(await page.evaluate(() => JSON.stringify(Object.entries(localStorage).sort()))).toBe(before);

  await banner.getByRole("button", { name: "Salir de la demo" }).click();
  await expect(page).toHaveURL(/#\/portada$/);
  await expect(page.locator("#demo-banner")).toBeHidden();
  expect(await page.evaluate(() => Object.keys(sessionStorage).filter((k) => k.startsWith("pld-demo:")))).toEqual([]);
  expect(await page.evaluate(() => localStorage.getItem("pld:completed"))).toBe('["paquetes"]');
});

test("reiniciar la demo deshace lo que hizo el visitante", async ({ page }) => {
  await page.goto("/?demo=1#/panel");
  await expect(page.locator("#private-title")).toHaveText("Hola, Alex Developer");
  await page.evaluate(() => sessionStorage.setItem("pld-demo:pld:completed", JSON.stringify([])));
  await page.reload();
  await expect(page.locator(".dash-kpis")).toContainText("0/27");
  await page.locator("#demo-banner").getByRole("button", { name: "Reiniciar" }).click();
  await expect(page.locator(".dash-kpis")).toContainText("6/27");
});

test("fuera de la demo no se ve nada de la demo", async ({ page }) => {
  await page.goto("/#/aprender");
  await expect(page.locator("#demo-banner")).toBeHidden();
  await page.goto("/#/panel");
  await expect(page.locator("#private-view")).not.toContainText("Alex Developer");
});

test("el laboratorio ejecuta Python de verdad, muestra errores y corrige ejercicios", async ({ page }) => {
  await page.goto("/#/laboratorio");
  await expect(page.locator("#lab-title")).toHaveText("Laboratorio de Python");
  await expect(page.locator(".lab__items a")).toHaveCount(14);
  const editor = page.locator("#lab-editor");
  const output = page.locator("#lab-output");

  // Ejecución real (Pyodide en el Web Worker), con color en el editor
  await editor.fill('numeros = [3, 1, 2]\nprint(sorted(numeros), sum(numeros) ** 2)\n');
  await expect(page.locator("#lab-highlight .hljs-built_in").first()).toBeVisible();
  await page.locator("#lab-run").click();
  await expect(output).toHaveText("[1, 2, 3] 36", { timeout: 90_000 });
  await expect(page.locator("#lab-status")).toHaveText("Python 3 listo");

  // Errores comprensibles
  await editor.fill("total = 10\nprint(total / 0)");
  await page.locator("#lab-run").click();
  await expect(output).toHaveAttribute("data-state", "error");
  await expect(output).toContainText("ZeroDivisionError");
  await expect(output.locator(".error-help")).toBeVisible();

  // Detener un bucle infinito
  await editor.fill("while True:\n    pass\n");
  await page.locator("#lab-run").click();
  await page.locator("#lab-stop").click();
  await expect(output).toContainText("Has detenido el programa");

  // Ejercicio de diccionarios: falla y después pasa con sus pruebas reales
  await page.getByRole("link", { name: /frecuencias\(palabras\)/ }).click();
  await expect(page.locator("#lab-task-title")).toContainText("frecuencias");
  await editor.fill("def frecuencias(palabras):\n    return {}\n");
  await page.locator("#lab-check").click();
  await expect(page.locator("#lab-result")).toHaveAttribute("data-passed", "false");
  await expect(page.locator("#lab-result")).toContainText("Todavía no");
  await editor.fill("def frecuencias(palabras):\n    cuenta = {}\n    for p in palabras:\n        cuenta[p] = cuenta.get(p, 0) + 1\n    return cuenta\n");
  await page.locator("#lab-check").click();
  await expect(page.locator("#lab-result")).toHaveAttribute("data-passed", "true");
  await expect(page.locator(".lab__items a[aria-current='page']")).toContainText("✓");

  // Restablecer vuelve a la plantilla y los ejemplos cargan código de las lecciones
  await page.locator("#lab-reset").click();
  await expect(editor).not.toHaveValue(/cuenta\[p\]/);
  await page.locator("#lab-example").selectOption("bucles");
  await expect(editor).toHaveValue(/for /);
});

test("el editor del laboratorio no atrapa el teclado: Esc y Tab salen", async ({ page }) => {
  await page.goto("/#/laboratorio");
  const editor = page.locator("#lab-editor");
  await editor.fill("");
  await editor.focus();
  await page.keyboard.press("Tab");
  await expect(editor).toHaveValue("    ");
  await page.keyboard.press("Escape");
  await page.keyboard.press("Tab");
  await expect(editor).not.toBeFocused();
});

test("el centro de aprendizaje enseña los siete cursos con su progreso y sus lecciones", async ({ page }) => {
  await page.goto("/?demo=1#/cursos");
  await expect(page.locator("#hub-title")).toHaveText("Cursos");
  const cards = page.locator(".hub-card");
  await expect(cards).toHaveCount(7);
  await expect(cards.locator(".hub-card__title")).toHaveText(["Python", "PCAP", "Programación (DAW)", "JavaScript", "Java", "Bases de datos", "Ciberseguridad"]);
  await expect(cards.nth(1)).toContainText("6 de 27 lecciones completadas");
  await expect(cards.nth(3)).toContainText("3 de 10 lecciones completadas");
  await expect(cards.nth(6)).toContainText("1 de 16 semanas completadas");
  await cards.nth(3).getByText("Ver 10 lecciones").click();
  await expect(cards.nth(3).locator("li.is-done")).toHaveCount(3);
  await cards.nth(3).getByRole("link", { name: "Continuar" }).click();
  await expect(page).toHaveURL(/#\/daw\/js\/leccion\//);
});

for (const colorScheme of ["light", "dark"]) {
  test(`la demo, el laboratorio y los cursos no tienen infracciones WCAG en tema ${colorScheme}`, async ({ page }) => {
    await page.emulateMedia({ colorScheme });
    await page.goto("/?demo=1#/panel");
    for (const [route, title] of [["/#/panel", "#private-title"], ["/#/laboratorio", "#lab-title"], ["/#/cursos", "#hub-title"]]) {
      await page.goto(route);
      await expect(page.locator(title)).toBeVisible();
      await settled(page);
      const results = await new AxeBuilder({ page }).withTags(WCAG).analyze();
      expect(results.violations, route).toEqual([]);
    }
  });
}

test("en un móvil de 320 px las páginas nuevas no se desplazan en horizontal", async ({ page }) => {
  await page.setViewportSize({ width: 320, height: 720 });
  await page.goto("/?demo=1#/panel");
  for (const [route, title] of [["/#/panel", "#private-title"], ["/#/laboratorio", "#lab-title"], ["/#/cursos", "#hub-title"]]) {
    await page.goto(route);
    await expect(page.locator(title)).toBeVisible();
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
    expect(overflow, route).toBeLessThanOrEqual(0);
  }
});
