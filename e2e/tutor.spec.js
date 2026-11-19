// Tutor con NEXARO en el panel del asistente. El backend de las e2e no tiene NEXARO: sin configurar no
// aparece, y con él se simulan /health y /tutor (la integración real con NEXARO la prueba el backend).
const AxeBuilder = require("@axe-core/playwright").default;
const { test, expect, openLesson } = require("./fixtures");

// `status`: lo que responde /tutor/status (se puede cambiar durante la prueba con status.next)
async function withTutor(page, reply, status = { next: { json: { available: true } } }) {
  const sent = [];
  await page.route("**/api/v1/health", async (route) => {
    const response = await route.fetch();
    await route.fulfill({ response, json: { ...(await response.json()), tutor: true } });
  });
  await page.route("**/api/v1/tutor/status", (route) => route.fulfill(status.next));
  await page.route("**/api/v1/tutor", async (route) => {
    sent.push(route.request().postDataJSON());
    await route.fulfill(reply(sent.length));
  });
  return sent;
}

test("sin NEXARO configurado no se ofrece el tutor", async ({ page }) => {
  await openLesson(page, "tipos");
  await page.getByRole("button", { name: "Abrir asistente" }).click();
  await expect(page.locator("#tutor-form")).toBeHidden();
  await expect(page.locator("#assistant-note")).toHaveText("Respuestas preparadas y revisadas para cada lección.");
});

test("el tutor recibe la lección, la pregunta y el código, y continúa la conversación", async ({ page }) => {
  const sent = await withTutor(page, (n) => ({
    json: { answer: `Pista ${n}: revisa \`type()\`\n\n\`\`\`python\nx = 1\n\`\`\``, conversation: `conv.${n}` },
  }));
  await openLesson(page, "tipos");
  await page.locator("#console-editor").fill("edad = '30'");
  await page.getByRole("button", { name: "Abrir asistente" }).click();
  await expect(page.locator("#assistant-note")).toContainText("NEXARO Personal AI");
  await expect(page.locator("#tutor-status")).toHaveText("Tutor conectado (NEXARO en este equipo)");
  // El código solo viaja si el alumno lo marca: por defecto no se envía
  await expect(page.getByLabel("Enviar también mi código")).not.toBeChecked();
  await page.getByLabel("Enviar también mi código").check();

  const question = page.getByLabel("Pregunta al tutor");
  await question.fill("¿Por qué no puedo sumar?");
  await question.press("Enter");
  const last = page.locator(".assistant__msg--bot").last();
  await expect(last).toContainText("Pista 1");
  await expect(last.locator("pre code")).toHaveText(/x = 1/);
  await expect(question).toHaveValue("");
  expect(sent[0]).toEqual({ lesson: "tipos", question: "¿Por qué no puedo sumar?", code: "edad = '30'", conversation: null });

  await page.getByLabel("Enviar también mi código").uncheck();
  await question.fill("¿Y ahora?");
  await page.getByRole("button", { name: "Preguntar" }).click();
  await expect(page.locator(".assistant__msg--bot").last()).toContainText("Pista 2");
  expect(sent[1]).toMatchObject({ code: "", conversation: "conv.1" });
});

test("un error del tutor se muestra y la siguiente pregunta empieza otra conversación", async ({ page }) => {
  const sent = await withTutor(page, (n) =>
    n === 1
      ? { json: { answer: "Primera", conversation: "conv.1" } }
      : n === 2
        ? { status: 503, json: { detail: "El tutor no responde ahora mismo. Vuelve a probar en un momento." } }
        : { json: { answer: "Otra vez aquí", conversation: "conv.3" } },
  );
  await openLesson(page, "tipos");
  await page.getByRole("button", { name: "Abrir asistente" }).click();
  const question = page.getByLabel("Pregunta al tutor");
  const send = page.getByRole("button", { name: "Preguntar" });
  await question.fill("uno");
  await send.click();
  await expect(page.locator(".assistant__msg--bot").last()).toContainText("Primera");
  await question.fill("dos");
  await send.click();
  await expect(page.locator(".assistant__msg--bot").last()).toContainText("no responde ahora mismo");
  // Tras el fallo se marca como no disponible y se puede reintentar
  await expect(page.locator("#tutor-status")).toHaveAttribute("data-state", "offline");
  await expect(send).toBeDisabled();
  await page.getByRole("button", { name: "Reintentar" }).click();
  await expect(send).toBeEnabled();
  await question.fill("tres");
  await send.click();
  await expect(page.locator(".assistant__msg--bot").last()).toContainText("Otra vez aquí");
  expect(sent.map((body) => body.conversation)).toEqual([null, "conv.1", null]);
});

test("sin sesión se pide iniciarla", async ({ page }) => {
  await withTutor(page, () => ({ status: 401, json: { detail: "Not authenticated" } }), {
    next: { status: 401, json: { detail: "Not authenticated" } },
  });
  await openLesson(page, "tipos");
  await page.getByRole("button", { name: "Abrir asistente" }).click();
  await expect(page.locator("#tutor-status")).toHaveText("Inicia sesión para usar el tutor.");
  await expect(page.getByRole("button", { name: "Preguntar" })).toBeDisabled();
});

test("con NEXARO apagado se avisa, la lección sigue funcionando y se puede reintentar", async ({ page }) => {
  const status = { next: { json: { available: false } } };
  await withTutor(page, () => ({ json: { answer: "Ya estoy", conversation: "c.1" } }), status);
  await openLesson(page, "tipos");
  await page.getByRole("button", { name: "Abrir asistente" }).click();
  await expect(page.locator("#tutor-status")).toContainText("NEXARO no responde");
  await expect(page.getByRole("button", { name: "Preguntar" })).toBeDisabled();
  // Las respuestas preparadas no dependen del tutor
  await expect(page.locator("#assistant-suggestions button").first()).toBeEnabled();
  status.next = { json: { available: true } };
  await page.getByRole("button", { name: "Reintentar" }).click();
  await expect(page.locator("#tutor-status")).toHaveText("Tutor conectado (NEXARO en este equipo)");
  await expect(page.getByRole("button", { name: "Preguntar" })).toBeEnabled();
});

for (const colorScheme of ["light", "dark"]) {
  test(`panel con el tutor y una respuesta sin infracciones WCAG (${colorScheme})`, async ({ page }) => {
    await page.emulateMedia({ colorScheme });
    await withTutor(page, () => ({ json: { answer: "Piensa en `int()`.\n\n```python\nn = 1\n```", conversation: "c.1" } }));
    await openLesson(page, "tipos");
    await page.getByRole("button", { name: "Abrir asistente" }).click();
    await page.getByLabel("Pregunta al tutor").fill("¿Cómo convierto?");
    await page.getByRole("button", { name: "Preguntar" }).click();
    await expect(page.locator(".assistant__msg--bot").last()).toContainText("int()");
    await page.waitForFunction(() => document.getAnimations().every((a) => a.playState !== "running"));
    const results = await new AxeBuilder({ page })
      .include("#assistant-panel")
      .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"])
      .analyze();
    const summary = results.violations.map((v) => `${v.id} (${v.impact}): ${v.nodes.map((n) => n.target).join(", ")}`);
    expect(summary, summary.join("\n")).toEqual([]);
  });
}
