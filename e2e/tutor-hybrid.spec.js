// Tutor híbrido (ADR-0038): selector de modalidad, conversación educativa y respuestas cuando la
// IA avanzada no está disponible. Backend REAL con el tutor y la IA avanzada simulados
// (start_backend.py: A2A_MOCK_MODEL y A2A_ADVANCED_PROVIDER=mock): nunca se llama a OpenAI.
const AxeBuilder = require("@axe-core/playwright").default;
const { test, expect, uniqueEmail } = require("./fixtures");

const PASSWORD = "contraseña-e2e-123";
const QUESTION = "No entiendo la diferencia entre una lista y una tupla en Python";

async function openTutor(page) {
  await page.goto("/#/aprender");
  await page.getByRole("button", { name: "Iniciar sesión" }).click();
  await page.locator("#account-dialog").getByRole("link", { name: "Crea una" }).click();
  const form = page.locator("#register-form");
  await form.getByLabel("Nombre").fill("Ana");
  await form.getByLabel("Email").fill(uniqueEmail());
  await form.getByLabel(/Contraseña/).fill(PASSWORD);
  await form.getByLabel(/acepto la/).check();
  await form.getByRole("button", { name: "Crear cuenta" }).click();
  await expect(page.locator("#account-label")).toHaveText("Ana");
  await page.locator("#tutor-nav").click();
  return page.locator("#tutor-view");
}

function taskResponse(state, text, metadata) {
  const message = { parts: [{ text }], metadata };
  return { jsonrpc: "2.0", id: 1, result: { task: { id: "t", contextId: "c", status: { state, message } } } };
}

test("modo gratuito por defecto: explica lista frente a tupla y corrige la comprobación", async ({ page }) => {
  const view = await openTutor(page);
  const modes = view.getByRole("group", { name: "Modalidad del tutor" });
  await expect(modes.getByRole("radio", { name: "Gratuito", exact: true })).toBeChecked();
  await expect(view.locator("#tutor-advanced-status")).toHaveText(/Modo de pruebas.*Te quedan 10 de 10 consultas hoy/);

  await view.getByLabel("Tu pregunta").fill(QUESTION);
  await view.getByRole("button", { name: "Preguntar" }).click();
  const first = view.locator(".assistant__msg--bot").first();
  await expect(first).toContainText("mutable");
  await expect(first).toContainText("inmutable");
  await expect(first).toContainText("Resultado esperado");
  await expect(first).toContainText("Comprueba que lo has entendido");
  await expect(first.locator(".tutor__source")).toHaveText(/^Tutor sin IA/);

  // Se equivoca: explica el motivo y le da otra oportunidad (el texto lo dice, no solo un color)
  await view.getByLabel("Tu pregunta").fill("[9, 2, 3] (9, 2, 3)");
  await view.getByRole("button", { name: "Preguntar" }).click();
  const wrong = view.locator(".assistant__msg--bot").nth(1);
  await expect(wrong).toContainText("No exactamente");
  await expect(wrong).toContainText("Prueba con este parecido");

  // Acierta: lo reconoce y propone algo más difícil
  await view.getByLabel("Tu pregunta").fill("[5, 7, 9] 4");
  await view.getByRole("button", { name: "Preguntar" }).click();
  const right = view.locator(".assistant__msg--bot").nth(2);
  await expect(right).toContainText("¡Correcto!");
  await expect(right).toContainText("Otra un poco más difícil");
  // El modo gratuito no gasta cuota de la avanzada
  await expect(view.locator("#tutor-advanced-status")).toHaveText(/Te quedan 10 de 10/);
});

test("botones de explicación alternativa y de otro ejercicio", async ({ page }) => {
  const view = await openTutor(page);
  await view.getByLabel("Tu pregunta").fill(QUESTION);
  await view.getByRole("button", { name: "Preguntar" }).click();
  await expect(view.locator(".assistant__msg--bot")).toHaveCount(1);

  await view.getByRole("button", { name: "Explícamelo de otra forma" }).click();
  await expect(view.locator(".assistant__msg--bot").nth(1)).toContainText("Otra forma de verlo");
  await view.getByRole("button", { name: "Otro ejercicio" }).click();
  await expect(view.locator(".assistant__msg--bot").nth(2)).toContainText("Ejercicio");
  await view.getByRole("button", { name: "Pedir una pista" }).click();
  await expect(view.locator(".assistant__msg--bot")).toHaveCount(4);
});

test("IA avanzada: se elige, responde y descuenta la cuota", async ({ page }) => {
  const view = await openTutor(page);
  const advanced = view.getByRole("radio", { name: "IA avanzada", exact: true });
  await expect(advanced).toBeEnabled();
  await advanced.check();
  await expect(view.locator("#tutor-status")).toHaveText(/Modalidad: IA avanzada/);
  await expect(view.locator("#tutor-advanced-privacy")).toHaveText(/Modo de pruebas.*no envía nada/);

  await view.getByLabel("Tu pregunta").fill(QUESTION);
  await view.getByRole("button", { name: "Preguntar" }).click();
  await expect(view.locator(".assistant__msg--bot").first()).toContainText("mutable");
  await expect(view.locator("#tutor-advanced-status")).toHaveText(/Te quedan 9 de 10 consultas hoy/);
});

test("sin IA avanzada en el servidor, la opción no se puede elegir y el tutor gratuito funciona", async ({ page }) => {
  await page.route("**/api/v1/tutor/modes", (route) =>
    route.fulfill({ json: { default: "free", free: { available: true, provider: "mock", simulated: true }, advanced: { available: false } } }),
  );
  const view = await openTutor(page);
  await expect(view.getByRole("radio", { name: "IA avanzada", exact: true })).toBeDisabled();
  await expect(view.locator("#tutor-advanced-status")).toHaveText(/^No disponible/);
  await expect(view.locator("#tutor-advanced-privacy")).toBeHidden();
  await view.getByLabel("Tu pregunta").fill(QUESTION);
  await view.getByRole("button", { name: "Preguntar" }).click();
  await expect(view.locator("#tutor-status")).toHaveText("Respondida");
});

test("si no se puede consultar la disponibilidad, se queda en modo gratuito", async ({ page }) => {
  await page.route("**/api/v1/tutor/modes", (route) => route.fulfill({ status: 500, json: { detail: "error" } }));
  const view = await openTutor(page);
  await expect(view.getByRole("radio", { name: "IA avanzada", exact: true })).toBeDisabled();
  await expect(view.locator("#tutor-advanced-status")).toHaveText(/No se ha podido comprobar/);
});

test("límite de IA avanzada: explica qué pasa y ofrece seguir en modo gratuito", async ({ page }) => {
  const view = await openTutor(page);
  await view.getByRole("radio", { name: "IA avanzada", exact: true }).check();
  await page.route("**/a2a/python-tutor", (route) =>
    route.fulfill({
      json: taskResponse("TASK_STATE_REJECTED", "Has usado todas tus consultas de IA avanzada de hoy (10).", { reason: "advanced_limit_reached" }),
    }),
  );
  await page.route("**/api/v1/tutor/modes", (route) =>
    route.fulfill({
      json: { default: "free", free: { available: true, provider: "mock", simulated: true }, advanced: { available: true, provider: "mock", simulated: true, daily_limit: 10, used_today: 10, remaining: 0, global_available: true } },
    }),
  );
  await view.getByLabel("Tu pregunta").fill(QUESTION);
  await view.getByRole("button", { name: "Preguntar" }).click();
  await expect(view.locator("#tutor-status")).toHaveText(/Has usado tus consultas de IA avanzada de hoy/);
  await expect(view.locator(".assistant__msg--bot").first()).toContainText("Has usado todas tus consultas");
  await expect(view.getByRole("button", { name: "Reintentar" })).toBeHidden();
  // Se vuelve a preguntar la cuota: la opción avanzada se desactiva y se vuelve a la gratuita
  await expect(view.locator("#tutor-advanced-status")).toHaveText(/Has usado tus 10 consultas de hoy/);
  await expect(view.getByRole("radio", { name: "Gratuito", exact: true })).toBeChecked();
});

test("el botón «Seguir en modo gratuito» cambia la modalidad", async ({ page }) => {
  const view = await openTutor(page);
  await view.getByRole("radio", { name: "IA avanzada", exact: true }).check();
  await page.route("**/a2a/python-tutor", (route) =>
    route.fulfill({ json: taskResponse("TASK_STATE_REJECTED", "Tu mensaje es demasiado largo para la IA avanzada.", { reason: "advanced_input_too_long" }) }),
  );
  await view.getByLabel("Tu pregunta").fill(QUESTION);
  await view.getByRole("button", { name: "Preguntar" }).click();
  const free = view.getByRole("button", { name: "Seguir en modo gratuito" });
  await expect(free).toBeVisible();
  await free.click();
  await expect(view.getByRole("radio", { name: "Gratuito", exact: true })).toBeChecked();
  await expect(view.locator("#tutor-status")).toHaveText("Sigues en el modo gratuito.");
  await expect(free).toBeHidden();
  await expect(view.getByLabel("Tu pregunta")).toBeFocused();
});

test("estado de carga: botones desactivados mientras el tutor piensa", async ({ page }) => {
  const view = await openTutor(page);
  let release;
  const held = new Promise((resolve) => {
    release = resolve;
  });
  await page.route("**/a2a/python-tutor", async (route) => {
    await held;
    await route.continue();
  });
  await view.getByLabel("Tu pregunta").fill(QUESTION);
  await view.getByRole("button", { name: "Preguntar" }).click();
  await expect(view.locator(".tutor")).toHaveAttribute("aria-busy", "true");
  await expect(view.locator("#tutor-status")).toHaveText(/pensando/);
  for (const name of ["Preguntar", "Pedir una pista", "Explícamelo de otra forma", "Otro ejercicio"]) {
    await expect(view.getByRole("button", { name, exact: true })).toBeDisabled();
  }
  release();
  await expect(view.locator("#tutor-status")).toHaveText("Respondida");
  await expect(view.locator(".tutor")).toHaveAttribute("aria-busy", "false");
});

test("en el móvil: sin desplazamiento lateral, con teclado y sin infracciones WCAG", async ({ page }) => {
  const view = await openTutor(page);
  await page.setViewportSize({ width: 360, height: 740 }); // el registro se hace antes, en escritorio
  // Con el teclado: flechas entre las dos modalidades del grupo
  await view.getByRole("radio", { name: "Gratuito", exact: true }).focus();
  await page.keyboard.press("ArrowDown");
  await expect(view.getByRole("radio", { name: "IA avanzada", exact: true })).toBeChecked();
  await page.keyboard.press("ArrowUp");
  await expect(view.getByRole("radio", { name: "Gratuito", exact: true })).toBeChecked();

  await view.getByLabel("Tu pregunta").fill(QUESTION);
  await view.getByRole("button", { name: "Preguntar" }).click();
  await expect(view.locator("#tutor-status")).toHaveText("Respondida");
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  expect(overflow).toBeLessThanOrEqual(0);
  // La respuesta larga se muestra desde su principio
  const top = await view.locator(".assistant__msg--bot").first().evaluate((el) => el.getBoundingClientRect().top);
  expect(top).toBeGreaterThanOrEqual(-1);
  expect(top).toBeLessThan(740);

  await page.waitForFunction(() => !document.querySelector("#toast.toast--visible") && document.getAnimations().every((a) => a.playState !== "running"));
  const results = await new AxeBuilder({ page }).include("#tutor-view").withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"]).analyze();
  const summary = results.violations.map((v) => `${v.id} (${v.impact}): ${v.nodes.map((n) => n.target).join(", ")}`);
  expect(summary, summary.join("\n")).toEqual([]);
});
