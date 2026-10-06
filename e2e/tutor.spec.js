// Tutor Python (ADR-0034): web → API → A2A → agente → respuesta, contra el backend REAL con el
// modelo simulado (start_backend.py activa A2A_MOCK_MODEL).
const AxeBuilder = require("@axe-core/playwright").default;
const { test, expect, uniqueEmail } = require("./fixtures");

const PASSWORD = "contraseña-e2e-123";

async function register(page) {
  await page.getByRole("button", { name: "Iniciar sesión" }).click();
  await page.locator("#account-dialog").getByRole("link", { name: "Crea una" }).click();
  const form = page.locator("#register-form");
  await form.getByLabel("Nombre").fill("Ana");
  await form.getByLabel("Email").fill(uniqueEmail());
  await form.getByLabel(/Contraseña/).fill(PASSWORD);
  await form.getByLabel(/acepto la/).check();
  await form.getByRole("button", { name: "Crear cuenta" }).click();
  await expect(page.locator("#account-label")).toHaveText("Ana");
}

test("sin sesión, el tutor invita a entrar", async ({ page }) => {
  await page.goto("/#/aprender");
  const nav = page.locator("#tutor-nav");
  await expect(nav).toBeVisible(); // el servidor lo ofrece: su Agent Card responde
  await nav.click();
  await expect(page.getByRole("heading", { name: "Pregunta tus dudas de Python" })).toBeVisible();
  await expect(page.locator("#tutor-view").getByRole("button", { name: "Iniciar sesión o crear cuenta" })).toBeVisible();
});

test("pregunta con código y error, respuesta del agente y conversación", async ({ page }) => {
  await page.goto("/#/aprender");
  await register(page);
  await page.locator("#tutor-nav").click();

  const view = page.locator("#tutor-view");
  await view.getByLabel("Tu pregunta").fill("¿Por qué me sale NameError?");
  await view.getByText("Añadir lección, código o error").click();
  await view.getByLabel("Lección").selectOption("variables");
  await view.getByLabel("Tu código").fill("if x = 1\n    print(total)");
  await view.getByLabel("Mensaje de error").fill("NameError: name 'total' is not defined");
  await view.getByRole("button", { name: "Preguntar" }).click();

  const answer = view.locator(".assistant__msg--bot").first();
  await expect(answer).toContainText("NameError");
  await expect(answer).toContainText("Variables y print()");
  await expect(answer).toContainText("no lo he ejecutado");
  await expect(view.locator("#tutor-status")).toHaveText("Respondida");

  // Segunda pregunta en la misma conversación
  await view.getByLabel("Tu pregunta").fill("Propón un ejercicio para practicar");
  await view.getByRole("button", { name: "Preguntar" }).click();
  await expect(view.locator(".assistant__msg--bot")).toHaveCount(2);
  await expect(view.locator(".assistant__msg--bot").last()).toContainText("Ejercicio");

  await view.getByRole("button", { name: "Nueva conversación" }).click();
  await expect(view.locator(".assistant__msg")).toHaveCount(0);
});

test("los errores de comunicación se muestran sin romper la vista", async ({ page }) => {
  await page.goto("/#/aprender");
  await register(page);
  await page.route("**/a2a/python-tutor", (route) => route.fulfill({ status: 429, json: { detail: "Demasiados intentos. Espera un poco y vuelve a probar." } }));
  await page.locator("#tutor-nav").click();
  const view = page.locator("#tutor-view");
  await view.getByLabel("Tu pregunta").fill("Hola");
  await view.getByRole("button", { name: "Preguntar" }).click();
  await expect(view.locator("#tutor-status")).toHaveText(/Demasiados intentos/);
  await expect(view.getByRole("button", { name: "Preguntar" })).toBeEnabled();
});

for (const colorScheme of ["light", "dark"]) {
  test(`tutor con una respuesta sin infracciones WCAG (modo ${colorScheme})`, async ({ page }) => {
    await page.emulateMedia({ colorScheme });
    await page.goto("/#/aprender");
    await register(page);
    await page.locator("#tutor-nav").click();
    const view = page.locator("#tutor-view");
    await view.getByLabel("Tu pregunta").fill("¿Qué es una lista?");
    await view.getByText("Añadir lección, código o error").click();
    await view.getByRole("button", { name: "Preguntar" }).click();
    await expect(view.locator("#tutor-status")).toHaveText("Respondida");
    await page.waitForFunction(() => !document.querySelector("#toast.toast--visible") && document.getAnimations().every((a) => a.playState !== "running"));
    const results = await new AxeBuilder({ page }).include("#tutor-view").withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"]).analyze();
    const summary = results.violations.map((v) => `${v.id} (${v.impact}): ${v.nodes.map((n) => n.target).join(", ")}`);
    expect(summary, summary.join("\n")).toEqual([]);
  });
}
