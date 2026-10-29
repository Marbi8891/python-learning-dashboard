// Tutor Python: web → API → A2A → agente → respuesta, contra el backend REAL con el
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

// Tutor adaptativo: origen de cada respuesta, comprobación evaluada, fallos y conversación
test("dice de dónde sale cada respuesta y corrige la pregunta de comprobación", async ({ page }) => {
  await page.goto("/#/aprender");
  await register(page);
  await page.locator("#tutor-nav").click();
  const view = page.locator("#tutor-view");

  await view.getByLabel("Tu pregunta").fill("¿Qué es una variable?");
  await view.getByRole("button", { name: "Preguntar" }).click();
  const first = view.locator(".assistant__msg--bot").first();
  await expect(first).toContainText("Comprueba que lo has entendido");
  await expect(first.locator(".tutor__source")).toHaveText(/^Tutor sin IA/); // nunca «generada por IA»
  await expect(first.getByRole("button", { name: "Ejecutar en tu navegador" }).first()).toBeVisible();
  await expect(view.getByLabel("Tu pregunta")).toHaveAttribute("placeholder", /Escribe tu respuesta/);

  await view.getByLabel("Tu pregunta").fill("3");
  await view.getByRole("button", { name: "Preguntar" }).click();
  const second = view.locator(".assistant__msg--bot").nth(1);
  await expect(second).toContainText("¡Correcto!");
  await expect(second.locator(".tutor__source")).toHaveText("Respuesta preparada por el tutor, sin IA.");
});

test("si el modelo falla explica el motivo y deja reintentar a mano", async ({ page }) => {
  await page.goto("/#/aprender");
  await register(page);
  let calls = 0;
  await page.route("**/a2a/python-tutor", async (route) => {
    calls += 1;
    if (calls > 1) return route.continue();
    const message = { parts: [{ text: "El tutor local no está disponible ahora mismo." }], metadata: { reason: "provider_unavailable" } };
    return route.fulfill({ json: { jsonrpc: "2.0", id: 1, result: { task: { id: "t", contextId: "c", status: { state: "TASK_STATE_FAILED", message } } } } });
  });
  await page.locator("#tutor-nav").click();
  const view = page.locator("#tutor-view");
  await view.getByLabel("Tu pregunta").fill("¿Qué es una lista?");
  await view.getByRole("button", { name: "Preguntar" }).click();
  await expect(view.locator("#tutor-status")).toHaveText("El modelo de IA no está disponible ahora mismo");
  await view.getByRole("button", { name: "Reintentar" }).click();
  await expect(view.locator("#tutor-status")).toHaveText("Respondida");
  await expect(view.locator(".assistant__msg--user")).toHaveCount(1); // reintentar no repite la pregunta
  await expect(view.getByRole("button", { name: "Reintentar" })).toBeHidden();
});

test("una respuesta que llega tarde no aparece en la conversación nueva", async ({ page }) => {
  await page.goto("/#/aprender");
  await register(page);
  let release;
  const held = new Promise((resolve) => {
    release = resolve;
  });
  await page.route("**/a2a/python-tutor", async (route) => {
    await held;
    await route.continue();
  });
  await page.locator("#tutor-nav").click();
  const view = page.locator("#tutor-view");
  await view.getByLabel("Tu pregunta").fill("¿Qué es una tupla?");
  await view.getByRole("button", { name: "Preguntar" }).click();
  await expect(view.getByRole("button", { name: "Cancelar" })).toBeVisible();
  await view.getByRole("button", { name: "Nueva conversación" }).click();
  release();
  await expect(view.locator("#tutor-status")).toHaveText("Conversación nueva.");
  await page.waitForTimeout(500);
  await expect(view.locator(".assistant__msg")).toHaveCount(0);
  await expect(view.getByRole("button", { name: "Preguntar" })).toBeEnabled();
});

test("cancelar deja de esperar sin romper la vista", async ({ page }) => {
  await page.goto("/#/aprender");
  await register(page);
  await page.route("**/a2a/python-tutor", () => {}); // nunca responde
  await page.locator("#tutor-nav").click();
  const view = page.locator("#tutor-view");
  await view.getByLabel("Tu pregunta").fill("¿Qué es un bucle?");
  await view.getByRole("button", { name: "Preguntar" }).click();
  await view.getByRole("button", { name: "Cancelar" }).click();
  await expect(view.locator("#tutor-status")).toHaveText(/Has cancelado la espera/);
  await expect(view.getByRole("button", { name: "Preguntar" })).toBeEnabled();
  await expect(view.getByRole("button", { name: "Cancelar" })).toBeHidden();
});

test("desde una lección, el tutor propone esa lección", async ({ page }) => {
  await page.goto("/#/leccion/bucles");
  await register(page);
  await page.locator("#tutor-nav").click();
  await expect(page.locator("#tutor-view").getByLabel("Lección")).toHaveValue("bucles");
});
