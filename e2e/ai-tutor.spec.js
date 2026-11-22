// Tutor IA del asistente (Fase 4 de la integración con NEXARO, docs/architecture/).
// El backend es el real (cuentas y lecciones); la IA se simula con page.route: en CI no hay NEXARO.
const AxeBuilder = require("@axe-core/playwright").default;
const { test, expect, uniqueEmail, openLesson } = require("./fixtures");

const PASSWORD = "contraseña-e2e-123";
const ORIGIN = "http://localhost:5500";
const CORS = { "Access-Control-Allow-Origin": ORIGIN, "Access-Control-Allow-Credentials": "true" };
const section = (page) => page.locator("#assistant-ai");
const status = (page) => page.locator("#assistant-ai-status");
const form = (page) => page.locator("#assistant-ai-form");
const lastBot = (page) => page.locator(".assistant__msg--bot").last();

async function register(page, name = "Ana") {
  await page.getByRole("button", { name: "Iniciar sesión" }).click();
  await page.locator("#account-dialog").getByRole("link", { name: "Crea una" }).click();
  const register = page.locator("#register-form");
  await register.getByLabel("Nombre").fill(name);
  await register.getByLabel("Email").fill(uniqueEmail());
  await register.getByLabel(/Contraseña/).fill(PASSWORD);
  await register.getByLabel(/He leído la política/).check();
  await register.getByRole("button", { name: "Crear cuenta" }).click();
  await expect(page.locator("#account-label")).toHaveText(name);
  await expect(page.locator("#account-dialog")).toBeHidden();
}

/**
 * El servidor ofrece la IA (`health.ai`) y responde /ai/* como diga `ai`.
 * Devuelve las peticiones que hizo la web a /ai/*, con su cuerpo.
 */
async function fakeAi(page, ai = {}) {
  const calls = [];
  const settings = { offered: true, status: { enabled: true, available: true }, answer: "Una variable guarda un valor.", ...ai };
  await page.route(/\/api\/v1\/health$/, async (route) => {
    const response = await route.fetch();
    const body = { ...(await response.json()), ai: settings.offered };
    await route.fulfill({ response, json: body });
  });
  await page.route(/\/api\/v1\/ai\//, async (route) => {
    const request = route.request();
    if (request.method() === "OPTIONS") {
      await route.fulfill({
        status: 204,
        headers: { ...CORS, "Access-Control-Allow-Methods": "GET, POST", "Access-Control-Allow-Headers": "Content-Type, X-PLD-Session, Authorization" },
      });
      return;
    }
    const path = new URL(request.url()).pathname.replace("/api/v1/ai/", "");
    calls.push({ path, body: request.postDataJSON(), headers: request.headers() });
    if (path === "status") {
      const modes = ["chat", "hint", "explain-error", "review-code"];
      await route.fulfill({ headers: CORS, json: { ...settings.status, modes } });
      return;
    }
    if (settings.failure) {
      await route.fulfill({ status: settings.failure.status, headers: CORS, json: { detail: settings.failure.detail } });
      return;
    }
    await route.fulfill({
      headers: CORS,
      json: { answer: settings.answer, mode: path, ai_generated: true, official_evaluation: false, request_id: "r-1" },
    });
  });
  return { calls, settings };
}

async function openTutor(page) {
  await page.locator("#assistant-toggle").click();
  await expect(section(page)).toBeVisible();
  // <details open> vale "" (cadena vacía) cuando está abierto: solo se pulsa si no tiene el atributo
  if ((await section(page).getAttribute("open")) === null) await section(page).locator("summary").click();
}

async function audit(page) {
  await page.waitForFunction(
    () => !document.querySelector("#toast.toast--visible") && document.getAnimations().every((a) => a.playState !== "running"),
    null,
    { timeout: 20_000 },
  );
  const results = await new AxeBuilder({ page })
    .include(".assistant")
    .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"])
    .analyze();
  const summary = results.violations.map((v) => `${v.id} (${v.impact}): ${v.nodes.map((n) => n.target).join(", ")}`);
  expect(summary, summary.join("\n")).toEqual([]);
}

test("sin IA en el servidor el tutor no aparece y el asistente sigue igual", async ({ page }) => {
  const asked = [];
  page.on("request", (request) => request.url().includes("/api/v1/ai/") && asked.push(request.url()));
  await openLesson(page, "variables");
  await register(page);
  await page.locator("#assistant-toggle").click();
  await expect(section(page)).toBeHidden();
  await page.getByRole("button", { name: "Dame una pista del ejercicio" }).click();
  await expect(lastBot(page)).toContainText("f-string");
  expect(asked).toEqual([]); // health.ai = false: ni siquiera se pregunta el estado
});

test("sin sesión invita a entrar y no deja preguntar", async ({ page }) => {
  const { calls } = await fakeAi(page);
  await openLesson(page, "variables");
  await openTutor(page);
  await expect(status(page)).toHaveText("Inicia sesión para preguntar al tutor IA.");
  await expect(form(page).getByRole("button", { name: "Preguntar" })).toBeDisabled();
  expect(calls).toEqual([]); // sin sesión no se consulta /ai/status (evita el aviso de sesión caducada)
});

test("pregunta, pinta la respuesta escapada y marcada como IA, sin enviar el código", async ({ page }) => {
  const { calls, settings } = await fakeAi(page);
  settings.answer = 'Mira **esto** <img src=x onerror="window.__xss=1"><script>window.__xss=2</script>';
  await openLesson(page, "variables");
  await register(page);
  await openTutor(page);
  await expect(status(page)).toHaveText("Tutor IA conectado.");

  await page.getByLabel("Tu pregunta").fill("¿Qué es una variable?");
  await form(page).getByRole("button", { name: "Preguntar" }).click();
  const reply = lastBot(page);
  await expect(reply).toContainText("IA · no es la corrección oficial");
  await expect(reply.locator("strong")).toHaveText("esto");
  await expect(reply.locator("img, script")).toHaveCount(0);
  expect(await page.evaluate(() => window.__xss)).toBeUndefined();
  await expect(page.getByLabel("Tu pregunta")).toHaveValue("");

  const ask = calls.find((call) => call.path === "chat");
  expect(ask.body).toEqual({ lesson_slug: "variables", locale: "es", question: "¿Qué es una variable?", history: [] });
  expect(ask.headers["x-pld-session"]).toBe("cookie"); // la sesión de siempre, sin tokens nuevos

  // La segunda pregunta lleva la conversación anterior (solo en memoria)
  await page.getByLabel("Tu pregunta").fill("¿Y una constante?");
  await form(page).getByRole("button", { name: "Preguntar" }).click();
  await expect(page.locator(".assistant__msg--ai")).toHaveCount(2);
  const second = calls.filter((call) => call.path === "chat")[1];
  expect(second.body.history).toEqual([
    { role: "user", content: "¿Qué es una variable?" },
    { role: "assistant", content: settings.answer },
  ]);
});

test("el código solo viaja si se marca la casilla o se pide revisarlo", async ({ page }) => {
  const { calls } = await fakeAi(page);
  await openLesson(page, "variables");
  await register(page);
  await page.locator("#console-editor").fill("precio = 2.5\nprint(precio)");
  await openTutor(page);
  await expect(status(page)).toHaveText("Tutor IA conectado.");

  await form(page).getByRole("button", { name: "Pedir pista" }).click();
  await expect(page.locator(".assistant__msg--ai")).toHaveCount(1);
  await page.getByLabel("Enviar también mi código").check();
  await form(page).getByRole("button", { name: "Pedir pista" }).click();
  await expect(page.locator(".assistant__msg--ai")).toHaveCount(2);
  await page.getByLabel("Enviar también mi código").uncheck();
  await form(page).getByRole("button", { name: "Revisar mi código" }).click();
  await expect(page.locator(".assistant__msg--ai")).toHaveCount(3);

  const [first, second] = calls.filter((call) => call.path === "hint");
  expect(first.body).toEqual({ lesson_slug: "variables", locale: "es", question: "Dame una pista del ejercicio", hint_level: 1 });
  expect(second.body.code).toBe("precio = 2.5\nprint(precio)");
  expect(second.body.hint_level).toBe(2);
  expect(calls.find((call) => call.path === "review-code").body.code).toBe("precio = 2.5\nprint(precio)");
  for (const call of calls) {
    for (const field of ["user_id", "model", "agent_id", "system"]) expect(call.body ?? {}).not.toHaveProperty(field);
  }
});

test("«Explicar mi error» pide ejecutar antes y después envía el error de la consola", async ({ page }) => {
  test.setTimeout(120_000); // la primera ejecución descarga Pyodide
  const { calls } = await fakeAi(page);
  await openLesson(page, "variables");
  await register(page);
  await openTutor(page);
  await expect(status(page)).toHaveText("Tutor IA conectado.");
  await form(page).getByRole("button", { name: "Explicar mi error" }).click();
  await expect(lastBot(page)).toHaveText("Ejecuta tu código primero: no hay ningún error que explicar.");
  expect(calls.filter((call) => call.path === "explain-error")).toEqual([]);

  await page.locator("#assistant-close").click();
  await page.locator("#console-editor").fill("print(total)");
  await page.locator("#console-run").click();
  await expect(page.locator("#console-run")).toBeEnabled({ timeout: 90_000 });
  await expect(page.locator("#console-output")).toContainText("NameError");
  await openTutor(page);
  await form(page).getByRole("button", { name: "Explicar mi error" }).click();
  await expect(page.locator(".assistant__msg--ai")).toHaveCount(1);
  const sent = calls.find((call) => call.path === "explain-error").body;
  expect(sent.error).toContain("NameError");
  expect(sent).not.toHaveProperty("code"); // sin marcar la casilla
});

test("no disponible: lo dice, ofrece reintentar y se recupera", async ({ page }) => {
  const { settings } = await fakeAi(page, { status: { enabled: true, available: false } });
  await openLesson(page, "variables");
  await register(page);
  await openTutor(page);
  await expect(status(page)).toHaveText("El tutor IA no está disponible ahora mismo.");
  await expect(form(page).getByRole("button", { name: "Preguntar" })).toBeDisabled();
  settings.status = { enabled: true, available: true };
  await page.getByRole("button", { name: "Reintentar" }).click();
  await expect(status(page)).toHaveText("Tutor IA conectado.");
  await expect(page.getByRole("button", { name: "Reintentar" })).toBeHidden();
});

test("si el tutor falla se ve un mensaje genérico y el panel pasa a no disponible", async ({ page }) => {
  const { settings } = await fakeAi(page);
  await openLesson(page, "variables");
  await register(page);
  await openTutor(page);
  await expect(status(page)).toHaveText("Tutor IA conectado.");
  settings.failure = { status: 503, detail: "El tutor no responde ahora mismo. Vuelve a probar en un momento." };
  await page.getByLabel("Tu pregunta").fill("¿Qué es print?");
  await form(page).getByRole("button", { name: "Preguntar" }).click();
  await expect(lastBot(page)).toHaveText("El tutor no responde ahora mismo. Vuelve a probar en un momento.");
  await expect(status(page)).toHaveText("El tutor IA no está disponible ahora mismo.");
  // Las respuestas preparadas siguen funcionando
  await page.getByRole("button", { name: "Dame una pista del ejercicio" }).click();
  await expect(lastBot(page)).toContainText("f-string");
});

test("nada del tutor queda en el almacenamiento del navegador", async ({ page }) => {
  await fakeAi(page);
  await openLesson(page, "variables");
  await register(page);
  await openTutor(page);
  await page.getByLabel("Tu pregunta").fill("pregunta-privada");
  await form(page).getByRole("button", { name: "Preguntar" }).click();
  await expect(page.locator(".assistant__msg--ai")).toHaveCount(1);
  const stored = await page.evaluate(() => JSON.stringify([{ ...localStorage }, { ...sessionStorage }]));
  for (const secret of ["pregunta-privada", "Una variable guarda", "nexaro", "NEXARO", "Bearer", "8080"]) {
    expect(stored).not.toContain(secret);
  }
});

test("se usa con el teclado y el panel cabe en el móvil", async ({ page }) => {
  await fakeAi(page);
  await openLesson(page, "variables");
  await register(page); // en el móvil «Iniciar sesión» está dentro del menú
  await page.setViewportSize({ width: 375, height: 740 });
  await page.locator("#assistant-toggle").click();
  await section(page).locator("summary").focus();
  await page.keyboard.press("Enter");
  await expect(section(page)).toHaveAttribute("open", "");
  await expect(status(page)).toHaveText("Tutor IA conectado.");
  await page.getByLabel("Tu pregunta").focus();
  await page.keyboard.type("¿Qué hace print?");
  await page.keyboard.press("Tab"); // casilla del código
  await page.keyboard.press("Tab"); // «Preguntar»
  await expect(form(page).getByRole("button", { name: "Preguntar" })).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(page.locator(".assistant__msg--ai")).toHaveCount(1);
  // El botón se desactiva mientras se espera: el foco no se pierde, pasa a la conversación
  await expect(page.locator("#assistant-messages")).toBeFocused();

  const box = await page.locator("#assistant-panel").boundingBox();
  expect(box.x).toBeGreaterThanOrEqual(0);
  expect(box.x + box.width).toBeLessThanOrEqual(375);
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(375);

  await page.keyboard.press("Escape");
  await expect(page.locator("#assistant-panel")).toBeHidden();
  await expect(page.locator("#assistant-toggle")).toBeFocused();
});

for (const colorScheme of ["light", "dark"]) {
  test.describe(`tutor IA en modo ${colorScheme}`, () => {
    test.use({ colorScheme });

    test("cumple WCAG 2.2 AA con una respuesta en pantalla", async ({ page }) => {
      await fakeAi(page, { answer: "Usa `print()` para **mostrar** el valor." });
      await openLesson(page, "variables");
      await register(page);
      await openTutor(page);
      await expect(status(page)).toHaveText("Tutor IA conectado.");
      await page.getByLabel("Tu pregunta").fill("¿Cómo lo muestro?");
      await form(page).getByRole("button", { name: "Preguntar" }).click();
      await expect(page.locator(".assistant__msg--ai")).toHaveCount(1);
      await audit(page);
    });
  });
}
