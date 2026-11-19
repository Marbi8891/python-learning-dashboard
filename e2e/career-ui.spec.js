// «Mi Carrera en IA» (DEC-012, Fase C): navegación, estados (carga, vacío, error), plan editable,
// objetivo económico solo local, avisos de la cuenta, WCAG 2.2 AA en claro y oscuro, 320/768/1440 px,
// inglés y sin conexión. El almacén y la sincronización se prueban en career.spec.js.
const AxeBuilder = require("@axe-core/playwright").default;
const { test, expect, uniqueEmail } = require("./fixtures");

const API = "http://127.0.0.1:8000";
const PASSWORD = "contraseña-segura";
const FINANCE_KEY = "pld:career-finance";
const SECTIONS = ["resumen", "ruta", "competencias", "proyectos", "plan", "objetivo", "preparacion"];

const view = (page) => page.locator("#career-view");
const title = (page) => page.locator("#career-title");

/** Abre una sección y espera a que esté pintada (ya no está el «Cargando…»). */
async function open(page, section = "") {
  await page.goto(`/#/carrera${section ? `/${section}` : ""}`);
  await expect(view(page).locator(".career-nav")).toBeVisible();
}

const finance = (page) => page.evaluate((key) => JSON.parse(localStorage.getItem(key)), FINANCE_KEY);

test("el menú lleva a Mi Carrera en IA y cada sección se marca como actual", async ({ page }) => {
  await page.goto("/#/aprender");
  await page.locator(".site-nav").getByRole("link", { name: /Mi Carrera en IA/ }).click();
  await expect(title(page)).toHaveText("Mi Carrera en IA");
  await expect(page).toHaveTitle("Mi Carrera en IA · Python Learning Dashboard");
  await expect(page.locator('.site-nav a[data-nav="carrera"]')).toHaveAttribute("aria-current", "page");
  const nav = view(page).getByRole("navigation", { name: "Secciones de Mi Carrera en IA" });
  for (const [name, heading] of [
    ["Ruta", "Ruta de 8 módulos"],
    ["Competencias", "Competencias"],
    ["Proyectos", "Proyectos reales"],
    ["Plan", "Plan de 36 meses"],
    ["Objetivo", "Objetivo económico"],
    ["Preparación", "Listas de comprobación"],
    ["Resumen", "Siguiente actividad"],
  ]) {
    await nav.getByRole("link", { name, exact: true }).click();
    await expect(nav.getByRole("link", { name, exact: true })).toHaveAttribute("aria-current", "page");
    await expect(view(page).getByRole("heading", { level: 2, name: heading }).first()).toBeVisible();
  }
});

test("una sección que no existe dice que no está y vuelve al itinerario", async ({ page }) => {
  await page.goto("/#/carrera/nada");
  await expect(title(page)).toContainText("No encontramos");
  await view(page).getByRole("link", { name: "Volver a Mi Carrera en IA" }).click();
  await expect(title(page)).toHaveText("Mi Carrera en IA");
});

test("sin empezar se ve entero; al empezarlo arranca el plan y se puede ajustar", async ({ page }) => {
  await open(page, "plan");
  await expect(view(page).locator("form[data-career-stage]")).toHaveCount(0);
  await view(page).getByRole("button", { name: "Empezar el itinerario" }).click();
  await expect(view(page).getByRole("button", { name: "Empezar el itinerario" })).toHaveCount(0);
  const started = await page.evaluate(() => JSON.parse(localStorage.getItem("pld:career")).roadmaps["applied-ai-engineer"].startedAt);
  expect(started).toBeTruthy();

  // Alargar la primera etapa desplaza la segunda
  const second = view(page).locator("#stage-s2 input[name=start]");
  const before = await second.inputValue();
  const first = view(page).locator("#stage-s1");
  await first.getByLabel("Meses").fill("9");
  await first.getByRole("button", { name: "Guardar" }).click();
  await expect(second).not.toHaveValue(before);
  await expect(view(page).locator("#stage-s1").getByRole("button", { name: "Volver al plan original" })).toBeVisible();
  await view(page).locator("#stage-s1").getByRole("button", { name: "Volver al plan original" }).click();
  await expect(second).toHaveValue(before);
});

test("marcar una unidad la cuenta como estudiada, pero no sube ninguna competencia", async ({ page }) => {
  await open(page, "ruta");
  const module = view(page).locator("#m-m1");
  await expect(module).toContainText("0 de 10 unidades estudiadas");
  await module.locator("summary").click();
  const unit = module.locator('[data-career-unit="m1.poo"]');
  await unit.check();
  await expect(module).toContainText("1 de 10 unidades estudiadas");
  await expect(module.locator(".career-badge").first()).toHaveText("En curso");
  await expect(module.locator("details")).toHaveAttribute("open", ""); // el repintado no cierra la lista
  await expect(unit).toBeFocused(); // ni le quita el foco a la casilla
  await expect(view(page).locator(".career-facts")).toContainText("0 de 32");

  // Estudiar no basta: lo primero que propone es practicar el concepto de esa unidad
  await view(page).getByRole("link", { name: "Resumen", exact: true }).click();
  const first = view(page).locator(".career-list > li").first();
  await expect(first).toContainText("Has estudiado «Programación orientada a objetos»");
  await expect(first.getByRole("link")).toHaveAttribute("href", "#/teoria/poo");
  // La siguiente unidad enlaza a su sitio en la ruta, con su lista abierta
  await view(page).locator('.career-list a[href^="#/carrera/ruta#u-"]').first().click();
  await expect(page).toHaveURL(/#\/carrera\/ruta#u-/);
  await expect(view(page).locator("details[open]")).toHaveCount(1);
});

test("con un examen de DAW en menos de una semana, la ruta no propone nada", async ({ page }) => {
  await page.addInitScript(() => {
    const soon = new Date(Date.now() + 3 * 86_400_000).toISOString().slice(0, 10);
    const at = new Date().toISOString();
    localStorage.setItem("pld:planner", JSON.stringify({ v: 1, minutes: 45, minutesAt: null, days: {}, exams: [{ id: "ex-1", title: "Examen de Programación", module: null, date: soon, kind: "examen", at }] }));
  });
  await open(page);
  await expect(view(page).locator(".career-note")).toContainText("DAW primero.");
  await expect(view(page).locator(".career-note")).toContainText("«Examen de Programación» dentro de 3 días");
});

test("el objetivo económico se queda en este navegador: guardar, gráfica, exportar, quitar y borrar", async ({ page }) => {
  const sent = [];
  page.on("request", (r) => {
    if (r.url().startsWith(API) && (r.postData() ?? "").includes("revenue")) sent.push(r.url());
  });
  await open(page, "objetivo");
  await expect(view(page).getByText("Aún no has metido ningún año.")).toBeVisible();

  const targets = view(page).locator("#career-targets");
  await targets.getByLabel("Objetivo de ingreso combinado anual (€)").fill("70000");
  await targets.getByRole("button", { name: "Guardar objetivo" }).click();
  await expect(targets.locator(".form-message")).toHaveText("Objetivo guardado en este navegador.");

  const year = view(page).locator("#career-year");
  for (const [y, salary, revenue, expenses] of [
    ["2027", "26000", "12000", "4000"],
    ["2028", "32000", "20000", "6000"],
  ]) {
    await year.getByLabel("Año").fill(y);
    await year.getByLabel("Salario bruto (€)").fill(salary);
    await year.getByLabel("Facturación sin IVA (€)").fill(revenue);
    await year.getByLabel("Gastos del negocio (€)").fill(expenses);
    await year.getByRole("button", { name: "Guardar año" }).click();
    await expect(year.locator(".form-message")).toHaveText(`Año ${y} guardado en este navegador.`);
  }
  // Combinado = salario + (facturación − gastos): 26 000 + 8 000 en 2027
  const table = view(page).getByRole("table", { name: "Datos por año (antes de impuestos)" });
  await expect(table.getByRole("row", { name: /^2027/ })).toContainText("34.000");
  await expect(view(page).getByRole("img", { name: "Evolución económica por año" })).toBeVisible();

  await page.reload();
  await expect(table.getByRole("row")).toHaveCount(3); // cabecera + 2 años: sigue tras recargar

  const download = page.waitForEvent("download");
  await view(page).getByRole("button", { name: "Exportar mis datos económicos (JSON)" }).click();
  const file = await download;
  expect(file.suggestedFilename()).toMatch(/^pld-datos-economicos-\d{4}-\d{2}-\d{2}\.json$/);

  await table.getByRole("button", { name: "Quitar 2027" }).click();
  await expect(table.getByRole("row")).toHaveCount(2);
  await expect(view(page).getByRole("img", { name: "Evolución económica por año" })).toHaveCount(0);

  const clear = view(page).getByRole("button", { name: "Borrar mis datos económicos" });
  await clear.click(); // primera pulsación: pide confirmación
  expect(Object.keys((await finance(page)).years)).toEqual(["2028"]);
  await view(page).getByRole("button", { name: /Pulsa otra vez para borrarlos/ }).click();
  await expect(view(page).locator("#career-finance-status")).toHaveText("Datos económicos borrados de este navegador.");
  expect(await finance(page)).toBeNull();
  expect(sent, "nada económico sale hacia la API").toEqual([]);
});

test("importar una exportación fusiona sin borrar; un archivo ajeno se rechaza", async ({ page }) => {
  await open(page, "objetivo");
  const exported = JSON.stringify({ format: "pld-career-finance", v: 1, exportedAt: "2026-11-19T10:00:00.000Z", data: { v: 1, targets: null, years: { 2030: { salary: 40000, revenue: 0, expenses: 0, at: "2026-11-19T10:00:00.000Z" } } } });
  const input = view(page).locator("[data-career-import]");
  await input.setInputFiles({ name: "copia.json", mimeType: "application/json", buffer: Buffer.from(exported) });
  await expect(view(page).locator("#career-finance-status")).toHaveText("Importado: 1 año(s). No se ha borrado nada de lo que ya había.");
  await expect(view(page).getByRole("row", { name: /^2030/ })).toBeVisible();
  await view(page).locator("[data-career-import]").setInputFiles({ name: "otro.json", mimeType: "application/json", buffer: Buffer.from('{"hola":1}') });
  await expect(view(page).locator("#career-finance-status")).toHaveText("El archivo no es una exportación de datos económicos de PLD.");
});

test("si el catálogo no carga, se dice y se puede reintentar", async ({ page }) => {
  let fail = true;
  await page.route("**/data/career/applied-ai-engineer.json", (route) => (fail ? route.abort() : route.continue()));
  await page.goto("/#/carrera");
  await expect(title(page)).toHaveText("No se pudo cargar el itinerario");
  fail = false;
  await view(page).getByRole("button", { name: "Reintentar" }).click();
  await expect(title(page)).toHaveText("Mi Carrera en IA");
});

test("cerrar sesión avisa de que los datos económicos se quedan; borrar la cuenta ofrece borrarlos", async ({ page, request }) => {
  const email = uniqueEmail();
  await request.post(`${API}/api/v1/auth/register`, { data: { email, password: PASSWORD, display_name: "Ana", accept_privacy: true } });
  await page.addInitScript((key) => {
    if (!localStorage.getItem(key)) localStorage.setItem(key, JSON.stringify({ v: 1, targets: { combined: 70000, salary: null, at: "2026-11-19T10:00:00.000Z" }, years: {} }));
  }, FINANCE_KEY);
  await page.goto("/#/carrera");
  await page.getByRole("button", { name: "Iniciar sesión" }).click();
  await page.locator("#login-form").getByLabel("Email").fill(email);
  await page.locator("#login-form").getByLabel("Contraseña").fill(PASSWORD);
  await page.locator("#login-form").getByRole("button", { name: "Entrar" }).click();
  await expect(page.locator("#account-label")).toHaveText("Ana");

  await page.locator("#account-button").click();
  const dialog = page.locator("#account-dialog");
  const danger = dialog.getByText("Eliminar mi cuenta", { exact: true });
  await danger.click();
  await expect(dialog.locator("#delete-finance")).toBeVisible();
  await expect(dialog.getByLabel("Borrar también mis datos económicos de este navegador")).not.toBeChecked();
  await danger.click();

  await dialog.getByRole("button", { name: "Cerrar sesión" }).click();
  await expect(page.locator("#toast")).toContainText("salvo tus datos económicos del itinerario profesional");
  expect((await finance(page)).targets.combined).toBe(70000);
});

test.describe("tamaños de pantalla", () => {
  for (const width of [320, 768, 1440]) {
    test(`a ${width} px no hay desplazamiento horizontal en ninguna sección`, async ({ page }) => {
      await page.setViewportSize({ width, height: 900 });
      await page.addInitScript((key) => {
        localStorage.setItem(key, JSON.stringify({ v: 1, targets: { combined: 70000, salary: 50000, at: "2026-11-19T10:00:00.000Z" }, years: { 2027: { salary: 26000, revenue: 12000, expenses: 4000, at: "2026-11-19T10:00:00.000Z" }, 2028: { salary: 32000, revenue: 20000, expenses: 6000, at: "2026-11-19T10:00:00.000Z" } } }));
      }, FINANCE_KEY);
      for (const section of SECTIONS) {
        await open(page, section);
        const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
        expect(overflow, `#/carrera/${section} a ${width} px`).toBeLessThanOrEqual(0);
      }
    });
  }
});

for (const colorScheme of ["light", "dark"]) {
  test(`todas las secciones sin infracciones WCAG 2.2 AA en modo ${colorScheme}`, async ({ page }) => {
    await page.emulateMedia({ colorScheme });
    await page.addInitScript((key) => {
      localStorage.setItem(key, JSON.stringify({ v: 1, targets: { combined: 70000, salary: null, at: "2026-11-19T10:00:00.000Z" }, years: { 2027: { salary: 26000, revenue: 12000, expenses: 4000, at: "2026-11-19T10:00:00.000Z" }, 2028: { salary: 32000, revenue: 20000, expenses: 6000, at: "2026-11-19T10:00:00.000Z" } } }));
    }, FINANCE_KEY);
    for (const section of SECTIONS) {
      await open(page, section);
      if (section === "ruta") await view(page).locator("#m-m1 summary").click(); // también una lista abierta
      await page.waitForFunction(() => document.getAnimations().every((a) => a.playState !== "running"));
      const results = await new AxeBuilder({ page }).include("#career-view").withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"]).analyze();
      const summary = results.violations.map((v) => `${v.id}: ${v.nodes.map((n) => n.target).join(", ")}`);
      expect(summary, `#/carrera/${section}\n${summary.join("\n")}`).toEqual([]);
    }
  });
}

test("en inglés: menú, secciones y estados traducidos", async ({ page }) => {
  await page.addInitScript(() => localStorage.setItem("pld:prefs", JSON.stringify({ lang: "en" })));
  await page.goto("/#/carrera/ruta");
  await expect(page.locator("html")).toHaveAttribute("lang", "en");
  await expect(page.locator('.site-nav a[data-nav="carrera"]')).toContainText("My AI Career");
  await expect(title(page)).toHaveText("My AI Career");
  await expect(view(page).getByRole("heading", { level: 2, name: "8-module path" })).toBeVisible();
  await expect(view(page).locator("#m-m1 .career-badge").first()).toHaveText("Available");
  await expect(view(page).locator("#m-m1 .career-module__title")).toContainText("Python Engineering"); // título del catálogo en inglés
});

test.describe("PWA", () => {
  test.use({ serviceWorkers: "allow" });
  test("Mi Carrera en IA abre sin conexión", async ({ page, context }) => {
    await page.addInitScript(() => {
      window.PLD_CONFIG = Object.assign(window.PLD_CONFIG ?? {}, { serviceWorker: true });
    });
    await page.goto("/#/aprender");
    await page.evaluate(() => navigator.serviceWorker.ready);
    await page.reload(); // ya controlada por el service worker
    await context.setOffline(true);
    await page.goto("/#/carrera/competencias");
    await expect(title(page)).toHaveText("Mi Carrera en IA");
    await expect(view(page).getByRole("heading", { level: 2, name: "Competencias" })).toBeVisible();
  });
});
