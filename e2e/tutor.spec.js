// Tutor con IA del asistente. El proveedor de IA nunca se llama: /tutor/ask se simula con
// page.route. La cuenta sí es real (backend de playwright.config.js).
const AxeBuilder = require("@axe-core/playwright").default;
const { test, expect, uniqueEmail, openLesson } = require("./fixtures");

const PASSWORD = "contraseña-e2e-123";

async function tutorOn(page) {
  await page.route("**/api/v1/health", (route) =>
    route.fulfill({ json: { status: "ok", email: false, google: false, tutor: true } }),
  );
}

async function register(page, email) {
  await page.getByRole("button", { name: "Iniciar sesión" }).click();
  const dialog = page.locator("#account-dialog");
  await dialog.getByRole("link", { name: "Crea una" }).click();
  const form = page.locator("#register-form");
  await form.getByLabel("Nombre").fill("Ana");
  await form.getByLabel("Email").fill(email);
  await form.getByLabel(/Contraseña/).fill(PASSWORD);
  await form.getByLabel(/He leído la política/).check();
  await form.getByRole("button", { name: "Crear cuenta" }).click();
  await expect(page.locator("#account-label")).toHaveText("Ana");
  await expect(dialog).toBeHidden();
}

test("sin tutor en el servidor solo hay respuestas preparadas", async ({ page }) => {
  await openLesson(page, "variables");
  await page.getByRole("button", { name: "Abrir asistente" }).click();
  await expect(page.locator("#assistant-form")).toBeHidden();
  await expect(page.locator("#assistant-note")).toContainText("Respuestas preparadas");
});

test("sin sesión, el tutor pide iniciar sesión", async ({ page }) => {
  await tutorOn(page);
  let asked = false;
  await page.route("**/api/v1/tutor/ask", (route) => {
    asked = true;
    return route.abort();
  });
  await openLesson(page, "variables");
  await page.getByRole("button", { name: "Abrir asistente" }).click();
  await expect(page.locator("#assistant-note")).toContainText("IA");

  await page.getByLabel("Escribe tu duda").fill("¿Qué es una variable?");
  await page.getByRole("button", { name: "Preguntar" }).click();
  await expect(page.locator(".assistant__msg--user").last()).toHaveText("¿Qué es una variable?");
  await page.locator(".assistant__msg--bot").last().getByRole("button", { name: "Iniciar sesión" }).click();
  await expect(page.locator("#account-dialog")).toBeVisible();
  expect(asked).toBe(false);
});

test("con sesión, el tutor responde con la lección y el código de la consola", async ({ page }) => {
  await tutorOn(page);
  const bodies = [];
  await page.route("**/api/v1/tutor/ask", async (route) => {
    bodies.push(route.request().postDataJSON());
    const reply = bodies.length === 1 ? "Una **variable** guarda un valor: `edad = 20`." : "Porque `print` muestra el valor.";
    await route.fulfill({ json: { answer: reply } });
  });
  await openLesson(page, "variables");
  await register(page, uniqueEmail());
  await page.locator("#console-editor").fill("edad = 20\nprint(edad)");

  await page.getByRole("button", { name: "Abrir asistente" }).click();
  const input = page.getByLabel("Escribe tu duda");
  await input.fill("¿Qué es una variable?");
  await input.press("Enter");
  const answer = page.locator(".assistant__msg--bot").last();
  await expect(answer).toContainText("guarda un valor");
  await expect(answer.locator("strong")).toHaveText("variable");
  expect(bodies[0]).toMatchObject({ question: "¿Qué es una variable?", lesson_slug: "variables", history: [] });
  expect(bodies[0].code).toContain("print(edad)");

  // La segunda pregunta lleva la conversación anterior; sin la casilla no se manda el código
  await page.getByLabel(/Enviar mi código/).uncheck();
  await input.fill("¿Y por qué sale 20?");
  await page.getByRole("button", { name: "Preguntar" }).click();
  await expect(page.locator(".assistant__msg--bot").last()).toContainText("muestra el valor");
  expect(bodies[1].history.map((turn) => turn.role)).toEqual(["user", "assistant"]);
  expect(bodies[1].code).toBeUndefined();

  const results = await new AxeBuilder({ page }).include("#assistant-panel").withTags(["wcag2a", "wcag2aa", "wcag21aa", "wcag22aa"]).analyze();
  expect(results.violations).toEqual([]);
});

test("un fallo del tutor se explica sin romper el asistente", async ({ page }) => {
  await tutorOn(page);
  await page.route("**/api/v1/tutor/ask", (route) =>
    route.fulfill({ status: 502, json: { detail: "El tutor no ha podido contestar. Inténtalo de nuevo en unos segundos." } }),
  );
  await openLesson(page, "variables");
  await register(page, uniqueEmail());
  await page.getByRole("button", { name: "Abrir asistente" }).click();
  await page.getByLabel("Escribe tu duda").fill("Hola");
  await page.getByRole("button", { name: "Preguntar" }).click();
  await expect(page.locator(".assistant__msg--error")).toContainText("Inténtalo de nuevo");
  await expect(page.getByRole("button", { name: "Preguntar" })).toBeEnabled();
  await page.getByRole("button", { name: "Dame una pista del ejercicio" }).click();
  await expect(page.locator(".assistant__msg--bot").last()).toContainText("f-string");
});
