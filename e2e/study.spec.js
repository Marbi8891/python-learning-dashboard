// v1.0: del fallo a la teoría, repaso espaciado, plan de estudio, sincronización, certificado y PWA.
const { test, expect, uniqueEmail } = require("./fixtures");

const seedPcap = (page, state) =>
  page.addInitScript((value) => localStorage.setItem("pld:pcap", JSON.stringify(value)), state);
const bank = async (request) => (await request.get("/data/pcap.json")).json();

test("una pregunta fallada enlaza a su lección y a la práctica del bloque", async ({ page, request }) => {
  const question = (await bank(request)).questions.find((q) => q.id === "oop-01");
  const wrong = question.options.findIndex((_, i) => !question.answer.includes(i));
  await seedPcap(page, { answers: { "oop-01": [false] } }); // la práctica empieza por las falladas
  await page.goto("/#/pcap/practica/poo");
  await page.locator(".exam-q input").nth(wrong).check();
  await page.getByRole("button", { name: "Comprobar" }).click();
  const links = page.locator(".study-links");
  await expect(links.getByRole("link", { name: /^Repasar la teoría:/ })).toHaveAttribute("href", `#/leccion/${question.lesson}`);
  await links.getByRole("link", { name: /^Repasar la teoría:/ }).click();
  await expect(page).toHaveURL(new RegExp(`#/leccion/${question.lesson}$`));
});

test("repaso espaciado: lo que toca hoy aparece en el panel y se repasa", async ({ page }) => {
  const due = { box: 1, due: "2026-01-01", last: "2026-01-01T00:00:00Z" };
  await seedPcap(page, { answers: { "str-01": [false] }, srs: { "str-01": due, "str-f01": due } });
  await page.goto("/#/pcap");
  await expect(page.locator(".today").first()).toContainText(/1\s*pregunta para repasar/);
  await expect(page.locator(".today").nth(1)).toContainText(/1\s*ficha para repasar/);
  await page.getByRole("link", { name: "Repasar preguntas" }).click();
  await expect(page.locator(".exam-bar")).toContainText("Pregunta 1 de 1");
  await page.locator(".exam-q input").first().check();
  await page.getByRole("button", { name: "Comprobar" }).click();
  await page.getByRole("link", { name: "Examen PCAP" }).click();
  await expect(page.locator(".today").first()).toContainText(/0\s*preguntas/); // pasa a mañana o más tarde
});

test("plan de estudio a partir de la fecha del examen", async ({ page }) => {
  await page.goto("/#/pcap");
  await expect(page.locator(".plan-intro")).toContainText("Pon la fecha de tu examen");
  const date = await page.evaluate(() => {
    const d = new Date();
    d.setDate(d.getDate() + 30);
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
  });
  await page.getByLabel("Fecha de tu examen").fill(date);
  await page.getByRole("button", { name: "Guardar fecha" }).click();
  await expect(page.locator(".plan-intro")).toContainText("Quedan 30 días");
  await expect(page.locator(".plan-tasks li")).toHaveCount(4);
  await expect(page.locator(".plan-tasks")).toContainText("Siguiente: Variables y print()");
  await page.reload();
  await expect(page.locator(".plan-intro")).toContainText("Quedan 30 días");
});

test("la preparación del PCAP se guarda en la cuenta y llega a otro dispositivo", async ({ page, browser }) => {
  const email = uniqueEmail();
  const password = "contraseña-e2e-123";
  await page.goto("/#/pcap/fichas");
  await page.getByRole("button", { name: "Ver respuesta" }).click();
  await page.getByRole("button", { name: "Lo sé →" }).click();
  await page.getByRole("button", { name: "Iniciar sesión" }).click();
  await page.getByRole("link", { name: "Crea una" }).click();
  const form = page.locator("#register-form");
  await form.getByLabel("Nombre").fill("Ana");
  await form.getByLabel("Email").fill(email);
  await form.getByLabel(/Contraseña/).fill(password);
  await form.getByLabel(/acepto la/).check();
  await form.getByRole("button", { name: "Crear cuenta" }).click();
  await expect(page.locator("#account-label")).toHaveText("Ana");
  await expect
    .poll(async () => (await page.evaluate(() => JSON.parse(localStorage.getItem("pld:pcap")).known.length)))
    .toBe(1);

  // «Otro dispositivo»: navegador limpio que inicia sesión con la misma cuenta
  const other = await browser.newContext({ baseURL: "http://localhost:5500" });
  const page2 = await other.newPage();
  await page2.goto("/#/pcap/fichas");
  await page2.getByRole("button", { name: "Iniciar sesión" }).click();
  await page2.locator("#login-form").getByLabel("Email").fill(email);
  await page2.locator("#login-form").getByLabel("Contraseña").fill(password);
  await page2.locator("#login-form").getByRole("button", { name: "Entrar" }).click();
  await expect(page2.locator("#account-label")).toHaveText("Ana");
  await expect(page2.locator("#pcap-view .course-hero__lead")).toContainText("1 de 48 fichas dominadas");
  await other.close();
});

test("la web conserva el progreso de la app Android guardado en la cuenta", async ({ page, request }) => {
  // ADR-0018: la app guarda su XP, racha y ruta en el objeto «app»; la web no debe borrarlo al guardar
  const api = "http://127.0.0.1:8000";
  const email = uniqueEmail();
  const password = "contraseña-e2e-123";
  await request.post(`${api}/api/auth/register`, {
    data: { email, password, display_name: "Ana", accept_privacy: true },
  });
  const login = await request.post(`${api}/api/auth/login`, { form: { username: email, password } });
  const headers = { Authorization: `Bearer ${(await login.json()).access_token}` };
  const app = { done: { "variables-1": { perfect: true, date: "2026-09-27" } }, daily: { "2026-09-27": 15 }, goal: 30 };
  await request.put(`${api}/api/pcap-state`, { headers, data: { data: { answers: { "oop-01": [true] }, app } } });

  await page.goto("/#/pcap/fichas");
  await page.getByRole("button", { name: "Iniciar sesión" }).click();
  await page.locator("#login-form").getByLabel("Email").fill(email);
  await page.locator("#login-form").getByLabel("Contraseña").fill(password);
  await page.locator("#login-form").getByRole("button", { name: "Entrar" }).click();
  await expect(page.locator("#account-label")).toHaveText("Ana");
  // Un cambio en la web provoca un nuevo guardado en la cuenta
  await page.getByRole("button", { name: "Ver respuesta" }).click();
  await page.getByRole("button", { name: "Lo sé →" }).click();
  await expect
    .poll(async () => (await (await request.get(`${api}/api/pcap-state`, { headers })).json()).data.known?.length ?? 0)
    .toBe(1);
  expect((await (await request.get(`${api}/api/pcap-state`, { headers })).json()).data.app).toEqual(app);
});

test("certificado: requisitos y certificado imprimible", async ({ page, request }) => {
  await page.goto("/#/certificado");
  await expect(page.locator(".cert-requirements li")).toHaveCount(2);

  const { modules } = await (await request.get("/data/lessons.json")).json();
  const lessons = modules.filter((m) => m.slug !== "especializacion").flatMap((m) => m.lessons.map((l) => l.slug));
  await page.addInitScript((slugs) => localStorage.setItem("pld:completed", JSON.stringify(slugs)), lessons);
  await seedPcap(page, { exams: [{ date: "2026-09-20T10:00:00Z", correct: 32, total: 40, score: 80, seconds: 3000, blocks: {} }] });
  await page.reload();
  await page.getByLabel("Nombre en el certificado").fill("Ana López");
  await page.getByRole("button", { name: "Actualizar" }).click();
  await expect(page.locator(".certificate__name")).toHaveText("Ana López");
  await expect(page.locator(".certificate")).toContainText("80 %");
  await expect(page.locator(".certificate__disclaimer")).toContainText("No es una certificación oficial");
  await page.emulateMedia({ media: "print" });
  await expect(page.locator(".certificate")).toBeVisible();
  await expect(page.locator("#sidebar")).toBeHidden();
});

test.describe("PWA", () => {
  test.use({ serviceWorkers: "allow" });
  test("instalable y funciona sin conexión tras la primera visita", async ({ page, context }) => {
    await page.addInitScript(() => {
      window.PLD_CONFIG = Object.assign(window.PLD_CONFIG ?? {}, { serviceWorker: true });
    });
    await page.goto("/");
    await expect(page.locator('link[rel="manifest"]')).toHaveAttribute("href", "manifest.webmanifest");
    await page.evaluate(() => navigator.serviceWorker.ready);
    await page.reload(); // ya controlada por el service worker: guarda lo que carga
    await expect(page.locator("#home-title")).toBeVisible();
    await context.setOffline(true);
    await page.reload();
    await expect(page.locator("#home-title")).toContainText("Prepara el PCAP");
    await context.setOffline(false);
  });
});
