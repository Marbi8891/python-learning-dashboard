// Panel del alumno (#/panel) contra el backend REAL (lo arranca playwright.config.js).
const AxeBuilder = require("@axe-core/playwright").default;
const { test, expect, uniqueEmail, openLesson } = require("./fixtures");

const PASSWORD = "contraseña-e2e-123";
const API = "http://127.0.0.1:8000";
const dialog = (page) => page.locator("#account-dialog");
const panel = (page) => page.locator("#private-view");

async function register(page, email, name = "Ana") {
  await page.getByRole("button", { name: "Iniciar sesión" }).click();
  await dialog(page).getByRole("link", { name: "Crea una" }).click();
  const form = page.locator("#register-form");
  await form.getByLabel("Nombre").fill(name);
  await form.getByLabel("Email").fill(email);
  await form.getByLabel(/Contraseña/).fill(PASSWORD);
  await form.getByLabel(/acepto la/).check();
  await form.getByRole("button", { name: "Crear cuenta" }).click();
  await expect(page.locator("#account-label")).toHaveText(name);
}

async function login(page, email) {
  await page.locator("#account-button").click();
  await dialog(page).getByLabel("Email").first().fill(email);
  await dialog(page).locator("#login-form").getByLabel("Contraseña").fill(PASSWORD);
  await dialog(page).getByRole("button", { name: "Entrar" }).click();
}

/** Token de una sesión aparte (Bearer), para consultar la API como un cliente cualquiera. */
async function tokenFor(request, email) {
  const response = await request.post(`${API}/api/v1/auth/login`, { form: { username: email, password: PASSWORD } });
  return (await response.json()).access_token;
}

async function audit(page) {
  await page.waitForFunction(
    () => !document.querySelector("#toast.toast--visible") && document.getAnimations().every((a) => a.playState !== "running"),
    null,
    { timeout: 20_000 },
  );
  const results = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"]).analyze();
  const summary = results.violations.map((v) => `${v.id} (${v.impact}): ${v.nodes.map((n) => n.target).join(", ")}`);
  expect(summary, summary.join("\n")).toEqual([]);
}

test("sin sesión, el panel solo invita a entrar y la API lo protege", async ({ page, request }) => {
  await openLesson(page);
  await page.goto("/#/panel");
  await expect(panel(page).getByRole("heading", { level: 1 })).toHaveText("Tu panel de alumno");
  await expect(panel(page).getByRole("button", { name: "Iniciar sesión o crear cuenta" })).toBeVisible();
  await expect(page.locator("#private-nav")).toBeHidden();
  // La antigua «Mi cuenta» lleva al perfil del panel
  await page.goto("/#/cuenta");
  await expect(page).toHaveURL(/#\/panel\/perfil$/);
  for (const path of ["/api/v1/dashboard", "/api/v1/dashboard/activity"]) {
    expect((await request.get(`${API}${path}`)).status()).toBe(401);
  }
});

test("alumno nuevo: estado vacío útil; el progreso se actualiza y sigue tras salir y volver a entrar", async ({ page, request }) => {
  const email = uniqueEmail();
  await openLesson(page);
  await register(page, email);
  await page.getByRole("link", { name: /Mi panel/ }).click();
  await expect(page).toHaveURL(/#\/panel$/);
  await expect(panel(page).getByRole("heading", { level: 1 })).toHaveText("Hola, Ana");
  await expect(panel(page).locator("time").first()).toHaveText(/\d{4}$/); // fecha en español
  await expect(panel(page).getByRole("heading", { name: "Empieza a aprender" })).toBeVisible();
  const lessons = panel(page).locator(".kpi", { hasText: "Lecciones del curso PCAP" }).locator(".kpi__value");
  await expect(lessons).toHaveText("0/27");

  // Completar una actividad: el panel lo refleja
  await openLesson(page, "variables");
  await page.getByRole("tab", { name: "Práctica y Ejercicio" }).click();
  await page.getByRole("button", { name: "Marcar como completada" }).click();
  await page.goto("/#/panel");
  await expect(lessons).toHaveText("1/27");
  await expect(panel(page).getByRole("heading", { name: "Continuar aprendiendo" })).toBeVisible();
  await expect(panel(page).getByRole("link", { name: "Continuar aprendiendo" })).toHaveAttribute("href", "#/leccion/tipos");

  // Cada sección se abre y sus enlaces llevan a pantallas que existen
  await panel(page).getByRole("link", { name: "Mis cursos" }).click();
  await expect(page).toHaveURL(/#\/panel\/cursos$/);
  const pcapCard = panel(page).locator('[data-course-card="pcap-curso"]');
  await expect(pcapCard).toContainText("1 de 27 lecciones completadas");
  await pcapCard.getByRole("link", { name: /Continuar aprendiendo/ }).click();
  await expect(page.locator("#lesson-title")).toHaveText(/Tipos/);
  await page.goto("/#/panel/actividad");
  await expect(panel(page).locator("#dash-feed")).toContainText("Lección completada");
  await page.goto("/#/panel/progreso");
  await expect(panel(page).getByRole("heading", { name: "Evolución" })).toBeVisible();
  await expect(panel(page).locator(".dash-chart svg")).toHaveAttribute("aria-label", /1 actividad/);
  await page.goto("/#/panel/planificacion");
  await expect(panel(page).getByRole("heading", { name: "Objetivo de hoy" })).toBeVisible();
  await page.goto("/#/panel/logros");
  await expect(panel(page).getByRole("heading", { name: "Logros y certificados" })).toBeVisible();
  await page.goto("/#/panel/perfil");
  await expect(panel(page).getByText(email)).toBeVisible();
  await expect(panel(page).locator(".dash-facts")).toContainText("Email y contraseña");

  // El XP y los logros se guardan en la cuenta (antes solo en el navegador)
  const token = await tokenFor(request, email);
  await expect
    .poll(async () => (await (await request.get(`${API}/api/v1/course-state/game`, { headers: { Authorization: `Bearer ${token}` } })).json()).data.days?.length ?? 0)
    .toBeGreaterThan(0);

  // Cerrar sesión desde el panel: se borran los datos del navegador
  await panel(page).getByRole("button", { name: "Cerrar sesión", exact: true }).click();
  await expect(page.locator("#toast")).toContainText("Sesión cerrada");
  await expect(page.locator("#private-nav")).toBeHidden();
  // (al recargar, la app vuelve a crear el documento, vacío: no queda nada de la sesión anterior)
  expect(await page.evaluate(() => JSON.parse(localStorage.getItem("pld:game") ?? "{}").days ?? [])).toEqual([]);

  // Volver a entrar: el panel recupera lo de la cuenta
  await login(page, email);
  await expect(page.locator("#account-label")).toHaveText("Ana");
  await page.goto("/#/panel");
  await expect(lessons).toHaveText("1/27");
  await expect.poll(() => page.evaluate(() => JSON.parse(localStorage.getItem("pld:game") ?? "{}").days?.length ?? 0)).toBeGreaterThan(0);
});

test("un alumno no ve los datos de otro", async ({ page, request }) => {
  const ana = uniqueEmail();
  const luis = uniqueEmail();
  for (const [email, name] of [
    [ana, "Ana"],
    [luis, "Luis"],
  ]) {
    await request.post(`${API}/api/v1/auth/register`, { data: { email, password: PASSWORD, display_name: name, accept_privacy: true } });
  }
  const anaToken = await tokenFor(request, ana);
  await request.put(`${API}/api/v1/progress/variables`, { headers: { Authorization: `Bearer ${anaToken}` } });

  const luisToken = await tokenFor(request, luis);
  const data = await (await request.get(`${API}/api/v1/dashboard?user_id=1`, { headers: { Authorization: `Bearer ${luisToken}` } })).json();
  expect(data.user.email).toBe(luis);
  expect(data.lessons.completed).toBe(0);

  await openLesson(page);
  await login(page, luis);
  await page.goto("/#/panel/perfil");
  await expect(panel(page).getByText(luis)).toBeVisible();
  await expect(panel(page).getByText(ana)).toHaveCount(0);
});

test("un fallo de red se explica y se puede reintentar", async ({ page }) => {
  const email = uniqueEmail();
  await openLesson(page);
  await register(page, email);
  let fail = true;
  await page.route("**/api/v1/dashboard?**", (route) => (fail ? route.abort() : route.continue()));
  await page.goto("/#/panel");
  const alert = panel(page).getByRole("alert");
  await expect(alert).toContainText("No se ha podido cargar parte de tu panel");
  await expect(alert).toContainText("No se pudo conectar con el servidor");
  fail = false;
  await alert.getByRole("button", { name: "Reintentar" }).click();
  await expect(panel(page).getByRole("alert")).toHaveCount(0);
  await expect(panel(page).locator(".kpi", { hasText: "Lecciones del curso PCAP" }).locator(".kpi__value")).toHaveText("0/27");
});

for (const colorScheme of ["light", "dark"]) {
  test.describe(`panel en modo ${colorScheme}`, () => {
    test.use({ colorScheme });
    test("todas las secciones sin infracciones WCAG", async ({ page }) => {
      test.setTimeout(120_000);
      await openLesson(page);
      await register(page, uniqueEmail());
      for (const section of ["resumen", "cursos", "progreso", "actividad", "planificacion", "logros", "perfil"]) {
        await page.goto(`/#/panel/${section}`);
        await expect(panel(page).locator(".dash-nav [aria-current=page]")).toBeVisible();
        await expect(panel(page).locator(".dash-status")).toHaveCount(0); // ya ha cargado
        await audit(page);
      }
    });
  });
}

test("en el móvil, el panel cabe sin desplazamiento horizontal y se navega con teclado", async ({ page }) => {
  await page.setViewportSize({ width: 360, height: 780 });
  await openLesson(page);
  await page.locator("#menu-toggle").click();
  await register(page, uniqueEmail());
  await page.goto("/#/panel/cursos");
  await expect(panel(page).locator('[data-course-card="learn"]')).toBeVisible();
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  expect(overflow).toBeLessThanOrEqual(0);
  // Las secciones son enlaces normales: se llega con Tab y se abren con Enter
  await page.locator(".dash-nav a", { hasText: "Logros" }).focus();
  await page.keyboard.press("Enter");
  await expect(page).toHaveURL(/#\/panel\/logros$/);
  await expect(page.locator("#private-title")).toBeFocused();
});

test("Mi progreso: cada módulo de DAW separa preguntas practicadas y dominadas", async ({ page }) => {
  // sql-01 acertada dos veces seguidas (dominada) · sql-02 un acierto suelto · sql-03 fallada
  await page.addInitScript(() => {
    if (sessionStorage.getItem("seeded")) return; // solo la primera carga: después manda la cuenta
    sessionStorage.setItem("seeded", "1");
    localStorage.setItem("pld:course:sql", JSON.stringify({ answers: { "sql-01": [true, true], "sql-02": [true], "sql-03": [false] } }));
  });
  await page.goto("/#/bienvenida");
  await register(page, uniqueEmail());
  await page.goto("/#/panel/progreso");
  const modules = panel(page).locator("[data-module-progress]");
  const bd = modules.locator("li", { hasText: "0484 · Bases de datos" });
  await expect(bd).toContainText("Practicadas: 3 de 110");
  await expect(bd).toContainText("Dominadas: 1 de 110");
  await expect(modules.locator("li", { hasText: "0485 · Programación" })).toContainText("Practicadas: 0 de 243");
  await expect(modules).toContainText("13 módulos del ciclo aún no tienen preguntas en la plataforma");
  await expect(panel(page).getByText("no una calificación del centro")).toBeVisible();
  await audit(page);
  await bd.getByRole("link", { name: "0484 · Bases de datos" }).click();
  await expect(page.locator("#daw-title")).toHaveText("Bases de datos");
});
