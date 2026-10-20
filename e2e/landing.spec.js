// Portada pública (#/portada): navegación, demostración real, menú móvil, enlaces y WCAG.
const AxeBuilder = require("@axe-core/playwright").default;
const { test, expect } = require("./fixtures");

async function audit(page) {
  await page.waitForFunction(() => document.getAnimations().every((a) => a.playState !== "running"), null, { timeout: 20_000 });
  const results = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"]).analyze();
  const summary = results.violations.map((v) => `${v.id} (${v.impact}): ${v.nodes.map((n) => n.target).join(", ")}`);
  expect(summary, summary.join("\n")).toEqual([]);
}

const header = (page) => page.getByRole("banner");

test("la portada tiene su propia cabecera, oculta la app y lleva a cada sección por su ruta", async ({ page }) => {
  await page.goto("/#/portada");
  await expect(page.locator("#lp-title")).toHaveText("Aprende programación entendiendo lo que haces");
  await expect(page).toHaveTitle(/Aprende programación entendiendo lo que haces/);
  await expect(page.locator("#sidebar")).toBeHidden();
  await expect(page.locator("#assistant-toggle")).toBeHidden();
  await expect(page.getByRole("heading", { level: 1 })).toHaveCount(1);

  await header(page).getByRole("link", { name: "Funcionalidades" }).click();
  await expect(page).toHaveURL(/#\/portada\/funcionalidades$/);
  await expect(page.locator("#lp-funcionalidades-title")).toBeFocused();
  await expect(page.locator("#lp-funcionalidades-title")).toBeInViewport();

  // «Descubrir cómo funciona» y el enlace profundo con recarga
  await page.goto("/#/portada");
  await page.getByRole("link", { name: "Descubrir cómo funciona" }).click();
  await expect(page).toHaveURL(/#\/portada\/como-funciona$/);
  await expect(page.locator(".lp-step")).toHaveCount(4);
  await page.goto("/#/portada/preguntas");
  await page.reload();
  await expect(page.locator("#lp-preguntas-title")).toBeInViewport();

  // Volver atrás desde la app regresa a la portada
  await page.goto("/#/portada");
  await page.getByRole("link", { name: "Entrar en Python Learning Dashboard" }).click();
  await expect(page).toHaveURL(/#\/aprender$/);
  await expect(page.locator("#landing-view")).toBeHidden();
  await page.goBack();
  await expect(page.locator("#lp-title")).toBeVisible();
});

test("demostración: el ejercicio real se corrige y explica el error de la respuesta trampa", async ({ page }) => {
  await page.goto("/#/portada/demo");
  const demo = page.locator("#lp-demo");
  await expect(demo.getByRole("heading", { name: "Bucles: while y for" })).toBeVisible();
  await expect(demo.locator(".lx-code").first()).toContainText('print("vuelta", i)');
  await expect(demo.locator(".lx-code code .hljs-keyword").first()).toBeVisible(); // resaltado de sintaxis
  const quiz = demo.locator("[data-lp-quiz]");
  await quiz.getByRole("button", { name: "Comprobar" }).click();
  await expect(quiz.locator("[data-lp-feedback]")).toHaveText("Elige una respuesta.");
  await quiz.getByLabel("2 3 4 5 6").check();
  await quiz.getByRole("button", { name: "Comprobar" }).click();
  await expect(quiz.locator("[data-lp-feedback]")).toContainText("Cree que range incluye el valor final");
  await expect(quiz.locator("[data-lp-feedback]")).toContainText("Cómo evitarlo");
  await quiz.getByLabel("2 3 4 5", { exact: true }).check();
  await quiz.getByRole("button", { name: "Comprobar" }).click();
  await expect(quiz.locator("[data-lp-feedback]")).toContainText("Correcto");
  // Lo que es un ejemplo se dice
  await expect(demo).toContainText("Ejemplo ilustrativo, no es una conversación real");
  await expect(demo).toContainText("Datos de ejemplo");
});

test("CodeFeed aparece como propuesta en desarrollo, sin vídeos ni botones", async ({ page }) => {
  await page.goto("/#/portada/codefeed");
  const section = page.locator("#lp-codefeed");
  await expect(section).toContainText("todavía no está disponible");
  await expect(section.locator("video, iframe, a, button")).toHaveCount(0);
});

test("todos los enlaces internos de la portada llevan a una ruta que existe", async ({ page }) => {
  await page.goto("/#/portada");
  await page.locator("#lp-temario a").first().waitFor();
  const hrefs = await page.locator("#landing-view a[href^='#/']").evaluateAll((links) => [...new Set(links.map((a) => a.getAttribute("href")))]);
  expect(hrefs.length).toBeGreaterThan(20);
  for (const href of hrefs) {
    await page.goto(`/${href}`);
    await expect(page, href).toHaveURL(new RegExp(`${href.replace(/[/#]/g, "\\$&")}$`)); // el router no la cambia
  }
  await page.goto("/#/portada");
  for (const href of ["privacidad.html", "aviso-legal.html"]) {
    expect((await page.request.get(`/${href}`)).status()).toBe(200);
    await expect(page.locator(`.lp-footer a[href="${href}"]`)).toHaveCount(1);
  }
  await expect(page.locator(`#landing-view a[href^="http"]`).first()).toHaveAttribute("href", /^https:\/\/github\.com\/Marbi8891\/python-learning-dashboard/);
});

test("«Iniciar sesión» abre el diálogo de cuenta real y «Saltar al contenido» no cambia la ruta", async ({ page }) => {
  await page.goto("/#/portada");
  await header(page).getByRole("button", { name: "Iniciar sesión" }).click();
  await expect(page.locator("#account-dialog")).toBeVisible();
  await page.keyboard.press("Escape");
  await page.reload();
  await page.locator("#lp-title").waitFor();
  await page.keyboard.press("Tab");
  await expect(page.locator(".skip-link")).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(page).toHaveURL(/#\/portada$/);
  await expect(page.locator("#landing-main")).toBeFocused();
});

for (const colorScheme of ["light", "dark"]) {
  test(`portada sin infracciones WCAG en tema ${colorScheme}`, async ({ page }) => {
    await page.emulateMedia({ colorScheme, reducedMotion: "reduce" });
    await page.goto("/#/portada");
    await page.locator("#lp-temario a").first().waitFor();
    await expect(page.locator("html")).toHaveAttribute("data-theme", colorScheme);
    await page.locator(".lp-faq__item summary").first().click();
    await audit(page);
  });
}

test.describe("móvil", () => {
  test.use({ viewport: { width: 375, height: 760 } });
  test("menú accesible: se abre, navega, se cierra con Escape y no hay desbordamiento", async ({ page }) => {
    await page.goto("/#/portada");
    const toggle = page.getByRole("button", { name: "Menú" });
    await expect(toggle).toHaveAttribute("aria-expanded", "false");
    await expect(page.getByRole("navigation", { name: "Portada" })).toBeHidden();
    await toggle.click();
    await expect(toggle).toHaveAttribute("aria-expanded", "true");
    await audit(page);
    await page.keyboard.press("Escape");
    await expect(toggle).toHaveAttribute("aria-expanded", "false");
    await expect(toggle).toBeFocused();
    await toggle.click();
    await page.getByRole("navigation", { name: "Portada" }).getByRole("link", { name: "Temario" }).click();
    await expect(page).toHaveURL(/#\/portada\/temario$/);
    await expect(toggle).toHaveAttribute("aria-expanded", "false");
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
    expect(overflow).toBeLessThanOrEqual(0);
  });
});
