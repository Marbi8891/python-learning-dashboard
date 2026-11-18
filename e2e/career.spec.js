// Itinerario profesional (DEC-012, Fase B): el documento `career` se sincroniza con la cuenta con las
// mismas protecciones que el resto del progreso, y su catálogo funciona sin conexión.
// La pantalla «Mi Carrera en IA» llega en la Fase C: aquí se prueba el almacén desde la propia página.
const { test, expect, uniqueEmail } = require("./fixtures");

const API = "http://127.0.0.1:8000";
const PASSWORD = "contraseña-segura";
const RID = "applied-ai-engineer";
const AT = "2026-11-18T10:00:00.000Z";

async function account(request) {
  const email = uniqueEmail();
  await request.post(`${API}/api/v1/auth/register`, { data: { email, password: PASSWORD, display_name: "Ana", accept_privacy: true } });
  const login = await request.post(`${API}/api/v1/auth/login`, { form: { username: email, password: PASSWORD } });
  return { email, headers: { Authorization: `Bearer ${(await login.json()).access_token}` } };
}

async function login(page, email) {
  await page.getByRole("button", { name: "Iniciar sesión" }).click();
  await page.locator("#login-form").getByLabel("Email").fill(email);
  await page.locator("#login-form").getByLabel("Contraseña").fill(PASSWORD);
  await page.locator("#login-form").getByRole("button", { name: "Entrar" }).click();
  await expect(page.locator("#account-label")).toHaveText("Ana");
}

const remoteDoc = () => ({ v: 1, active: RID, activeAt: AT, roadmaps: { [RID]: { startedAt: AT, units: { "m1.git": { status: "hecha", at: AT } } } } });

const savedUnits = async (request, headers) => {
  const saved = await (await request.get(`${API}/api/v1/course-state/career`, { headers })).json();
  return Object.keys(saved.data.roadmaps?.[RID]?.units ?? {}).sort();
};

/** Marca una unidad desde la página con los módulos reales de la web y espera a que suba. */
const markUnit = (page, unit) =>
  page.evaluate(async ({ rid, unit }) => {
    const store = await import("/js/career/career-store.js");
    const data = await import("/js/career/career-data.js");
    const progress = data.enroll(store.career, rid);
    data.setUnitStatus(progress, unit, "hecha");
    store.saveCareer();
    return store.flushCareerSync();
  }, { rid: RID, unit });

test("al entrar se fusiona con la copia de la cuenta y lo nuevo se sube sin perder nada", async ({ page, request }) => {
  const { email, headers } = await account(request);
  await request.put(`${API}/api/v1/course-state/career`, { headers, data: { data: remoteDoc() } });
  await page.goto("/#/aprender");
  const read = page.waitForResponse((r) => r.url().endsWith("/course-state/career") && r.request().method() === "GET" && r.ok());
  await login(page, email);
  await read;

  // La respuesta llega antes de que termine la fusión: se espera a ver la copia de la cuenta aquí
  const localUnits = () => page.evaluate(async () => Object.keys((await import("/js/career/career-store.js")).career.roadmaps["applied-ai-engineer"]?.units ?? {}));
  await expect.poll(localUnits).toEqual(["m1.git"]);
  // Sin depender del momento: la subida inicial tras entrar ya ha terminado
  await expect.poll(() => page.evaluate(async () => (await import("/js/sync-status.js")).syncState("career"))).toBe("saved");
  expect(await markUnit(page, "m1.poo")).toBe(true);
  await expect.poll(() => savedUnits(request, headers)).toEqual(["m1.git", "m1.poo"]);
});

test("AUD-001: si la primera lectura falla, no se pisa lo que la cuenta ya tenía", async ({ page, request }) => {
  const { email, headers } = await account(request);
  await request.put(`${API}/api/v1/course-state/career`, { headers, data: { data: remoteDoc() } });
  // Este navegador ya tenía progreso propio del itinerario
  const mine = { v: 1, active: RID, activeAt: AT, roadmaps: { [RID]: { startedAt: AT, units: { "m1.poo": { status: "hecha", at: AT } } } } };
  await page.addInitScript((value) => {
    if (!localStorage.getItem("pld:career")) localStorage.setItem("pld:career", JSON.stringify(value));
  }, mine);
  const log = [];
  let failed = false;
  await page.route(`${API}/api/v1/course-state/career`, async (route) => {
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

  await page.goto("/#/aprender");
  await login(page, email);
  await expect.poll(() => savedUnits(request, headers), { timeout: 20_000 }).toEqual(["m1.git", "m1.poo"]);
  expect(log[0]).toBe("GET 503");
  expect(log.indexOf("PUT")).toBeGreaterThan(log.indexOf("GET"), "no sube nada antes de leer bien la cuenta");
});

test("sin sesión, el progreso del itinerario se queda en este navegador y no se envía", async ({ page }) => {
  const requests = [];
  page.on("request", (r) => {
    if (r.url().includes("/course-state/career")) requests.push(r.method());
  });
  await page.goto("/#/aprender");
  expect(await markUnit(page, "m1.poo")).toBe(true);
  const stored = await page.evaluate(() => JSON.parse(localStorage.getItem("pld:career")));
  expect(Object.keys(stored.roadmaps[RID].units)).toEqual(["m1.poo"]);
  expect(requests).toEqual([]);
});

test.describe("PWA", () => {
  test.use({ serviceWorkers: "allow" });
  test("el catálogo del itinerario se guarda al instalarse y se lee sin conexión", async ({ page, context }) => {
    await page.addInitScript(() => {
      window.PLD_CONFIG = Object.assign(window.PLD_CONFIG ?? {}, { serviceWorker: true });
    });
    await page.goto("/#/aprender");
    await page.evaluate(() => navigator.serviceWorker.ready);
    await page.reload(); // ya controlada por el service worker
    await context.setOffline(true);
    const roadmap = await page.evaluate(async () => {
      const store = await import("/js/career/career-store.js");
      const data = await import("/js/career/career-data.js");
      const catalog = await store.loadRoadmap("applied-ai-engineer");
      const index = data.indexRoadmap(catalog);
      return { modules: catalog.modules.length, units: index.units.size };
    });
    expect(roadmap).toEqual({ modules: 8, units: 90 });
  });
});
