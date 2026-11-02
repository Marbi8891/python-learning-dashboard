// Regresiones de las mejoras de la web (MW-NNN) detectadas por el agente mejorador-web.
// Cada test falla con el CSS anterior a su mejora. Se miden en el móvil (390 px) y, cuando importa, a 320 px.
const { test, expect, openLesson } = require("./fixtures");

const MOVIL = { width: 390, height: 844 };

/** Rectángulo de un elemento en la ventana. */
const rect = (locator) => locator.evaluate((el) => el.getBoundingClientRect().toJSON());

test.describe("móvil", () => {
  test.use({ viewport: MOVIL, hasTouch: true });

  test("MW-005: el botón del asistente es más pequeño en el móvil y no tapa el final del contenido", async ({ page }) => {
    await openLesson(page, "variables");
    const toggle = page.locator("#assistant-toggle");
    await expect(toggle).toBeVisible();
    const box = await rect(toggle);
    // Sigue siendo cómodo de tocar (≥ 44 px) pero tapa menos texto que los 60 px de antes
    expect(box.width).toBeGreaterThanOrEqual(44);
    expect(box.width).toBeLessThanOrEqual(48);
    // Al final de la página, el último bloque de la lección queda por encima del botón
    await page.evaluate(() => window.scrollTo(0, document.documentElement.scrollHeight));
    const last = await page.locator("#main").evaluate((main) => {
      const visible = [...main.querySelectorAll("*")].filter((el) => el.getBoundingClientRect().height > 0);
      return Math.max(...visible.map((el) => el.getBoundingClientRect().bottom));
    });
    expect(last).toBeLessThanOrEqual((await rect(toggle)).top);
  });

  test("MW-006: las tres pestañas de la lección caben en la pantalla", async ({ page }) => {
    for (const width of [320, 390]) {
      await page.setViewportSize({ width, height: 844 });
      await openLesson(page, "variables");
      for (const name of ["Teoría y Ejemplos", "Práctica y Ejercicio", "Quiz"]) {
        const box = await rect(page.getByRole("tab", { name }));
        expect(box.right, `${name} a ${width} px`).toBeLessThanOrEqual(width);
        expect(box.height).toBeGreaterThanOrEqual(24);
      }
    }
  });

  test("MW-002: los enlaces del pie del menú lateral miden al menos 24 px de alto", async ({ page }) => {
    await openLesson(page);
    await page.locator("#menu-toggle").click();
    const links = page.locator(".sidebar__footer a");
    expect(await links.count()).toBeGreaterThan(0);
    for (const link of await links.all()) {
      if (!(await link.isVisible())) continue;
      expect((await rect(link)).height, await link.textContent()).toBeGreaterThanOrEqual(24);
    }
  });

  test("MW-007: el editor no parte las líneas y los números de línea coinciden con el código", async ({ page }) => {
    await openLesson(page, "variables");
    await page.getByRole("tab", { name: "Práctica y Ejercicio" }).click();
    await page.getByRole("button", { name: "Cargar ejemplo" }).click();
    const medida = await page.locator("#console-editor").evaluate((editor) => {
      const style = getComputedStyle(editor);
      const lines = editor.value.split("\n").length;
      const content = editor.scrollHeight - parseFloat(style.paddingTop) - parseFloat(style.paddingBottom);
      return { lines, visualLines: Math.round(content / parseFloat(style.lineHeight)), whiteSpace: style.whiteSpace };
    });
    // Con ajuste de línea, una línea larga ocupaba dos y el número 5 salía al lado de la mitad de la línea 4
    expect(medida.whiteSpace).toBe("pre");
    expect(medida.visualLines).toBeLessThanOrEqual(Math.max(medida.lines, 10)); // rows="10" como mínimo
  });

  test("MW-004: los enlaces de las listas de la portada miden al menos 24 px de alto", async ({ page }) => {
    await page.goto("/#/portada");
    const links = page.locator(".lp-area li > a, .lp-courses li > a, .lp-footer li > a");
    await expect(links.nth(10)).toBeAttached(); // la portada pinta el temario al cargar los datos
    expect(await links.count()).toBeGreaterThan(10);
    for (const link of await links.all()) {
      expect((await rect(link)).height, await link.textContent()).toBeGreaterThanOrEqual(24);
    }
  });
});
