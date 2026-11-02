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
});
