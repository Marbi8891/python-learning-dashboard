// AUD-001: si la primera lectura de la cuenta falla, la web no puede pisar con su copia local
// lo que la cuenta ya tenía (de otro dispositivo). Solo sube después de fusionar bien.
const { test, expect, uniqueEmail } = require("./fixtures");

const API = "http://127.0.0.1:8000";
const PASSWORD = "contraseña-segura";

async function account(request) {
  const email = uniqueEmail();
  await request.post(`${API}/api/v1/auth/register`, { data: { email, password: PASSWORD, display_name: "Ana", accept_privacy: true } });
  const login = await request.post(`${API}/api/v1/auth/login`, { form: { username: email, password: PASSWORD } });
  return { email, headers: { Authorization: `Bearer ${(await login.json()).access_token}` } };
}

/** Responde 503 a la primera lectura del documento y apunta el orden de las peticiones. */
async function failFirstRead(page, path) {
  const log = [];
  let failed = false;
  await page.route(`${API}/api/v1/${path}`, async (route) => {
    const method = route.request().method();
    if (method === "GET" && !failed) {
      failed = true;
      log.push("GET 503");
      await route.fulfill({ status: 503, contentType: "application/json", body: '{"detail":"Servidor despertando"}' });
      return;
    }
    log.push(method);
    await route.continue();
  });
  return log;
}

async function login(page, email) {
  await page.getByRole("button", { name: "Iniciar sesión" }).click();
  await page.locator("#login-form").getByLabel("Email").fill(email);
  await page.locator("#login-form").getByLabel("Contraseña").fill(PASSWORD);
  await page.locator("#login-form").getByRole("button", { name: "Entrar" }).click();
  await expect(page.locator("#account-label")).toHaveText("Ana");
}

test("PCAP: con la primera lectura fallida no se pierde lo que había en la cuenta", async ({ page, request }) => {
  const { email, headers } = await account(request);
  await request.put(`${API}/api/v1/pcap-state`, { headers, data: { data: { answers: { "oop-01": [true] } } } });
  const log = await failFirstRead(page, "pcap-state");

  await page.goto("/#/pcap/fichas");
  await login(page, email);
  await page.getByRole("button", { name: "Ver respuesta" }).click();
  await page.getByRole("button", { name: "Lo sé →" }).click();

  // Tras el reintento, la cuenta tiene las dos cosas: lo de antes y la ficha nueva
  await expect
    .poll(async () => {
      const { data } = await (await request.get(`${API}/api/v1/pcap-state`, { headers })).json();
      return { known: data.known?.length ?? 0, before: data.answers?.["oop-01"] ?? null };
    }, { timeout: 20_000 })
    .toEqual({ known: 1, before: [true] });
  // Y no se subió nada antes de leer bien la cuenta
  expect(log[0]).toBe("GET 503");
  expect(log.indexOf("PUT")).toBeGreaterThan(log.indexOf("GET"));
});

test("núcleo por conceptos: con la primera lectura fallida se fusiona al reintentar", async ({ page, request }) => {
  const { email, headers } = await account(request);
  const now = new Date().toISOString();
  const remote = { v: 1, ex: { "var-01": { h: [false], last: now, n: 1 } }, errors: {}, log: [] };
  await request.put(`${API}/api/v1/course-state/learn`, { headers, data: { data: remote } });
  const log = await failFirstRead(page, "course-state/learn");

  await page.goto("/#/aprender");
  await page.waitForSelector("#learn-title");
  await login(page, email);
  await page.evaluate(async () => {
    const view = await import("./js/learn/session-view.js");
    view.startSession({ kind: "practice", title: "Bucles", exercises: ["buc-01"] });
  });
  await page.getByLabel(/Lo que muestra el programa/).fill("2 3 4 5");
  await page.getByRole("button", { name: "Comprobar", exact: true }).click();
  await expect(page.locator(".lx-feedback")).toContainText("Correcto");

  await expect
    .poll(async () => {
      const saved = await (await request.get(`${API}/api/v1/course-state/learn`, { headers })).json();
      return Object.keys(saved.data.ex ?? {}).sort();
    }, { timeout: 20_000 })
    .toEqual(["buc-01", "var-01"]);
  expect(log[0]).toBe("GET 503");
  expect(log.indexOf("PUT")).toBeGreaterThan(log.indexOf("GET"));
});

// Dos pestañas o dispositivos a la vez: el último en guardar ya no borra lo del otro.
test("PCAP: si otro dispositivo guardó después de entrar, se fusiona en vez de pisarlo", async ({ page, request }) => {
  const { email, headers } = await account(request);
  await page.goto("/#/pcap/fichas");
  const merged = page.waitForResponse((r) => r.url().endsWith("/pcap-state") && r.request().method() === "PUT");
  await login(page, email);
  await merged; // la web ya leyó la cuenta y subió su copia fusionada

  // Otro dispositivo guarda con la versión actual de la cuenta (la web no se entera)
  const current = await (await request.get(`${API}/api/v1/pcap-state`, { headers })).json();
  const other = await request.put(`${API}/api/v1/pcap-state`, {
    headers,
    data: { data: { ...current.data, answers: { "oop-01": [true] } }, version: current.version },
  });
  expect(other.status()).toBe(200);

  // La web guarda una ficha con la versión que leyó: recibe 409, relee, fusiona y reintenta
  const conflict = page.waitForResponse((r) => r.url().endsWith("/pcap-state") && r.status() === 409);
  await page.getByRole("button", { name: "Ver respuesta" }).click();
  await page.getByRole("button", { name: "Lo sé →" }).click();
  await conflict;
  await expect
    .poll(async () => {
      const { data } = await (await request.get(`${API}/api/v1/pcap-state`, { headers })).json();
      return { known: data.known?.length ?? 0, other: data.answers?.["oop-01"] ?? null };
    }, { timeout: 20_000 })
    .toEqual({ known: 1, other: [true] });
});
