// Cursos de DAW en la web (ADR-0021): catálogo, teoría, práctica con los tres tipos de ejercicio
// y progreso compartido con la app a través de la cuenta.
const AxeBuilder = require("@axe-core/playwright").default;
const { test, expect, uniqueEmail } = require("./fixtures");

const API = "http://127.0.0.1:8000";

test("el catálogo muestra los cinco cursos y se entra en uno", async ({ page }) => {
  // #/daw es la Preparación DAW (ADR-0031); el catálogo de cursos sigue en #/daw/cursos
  await page.goto("/#/daw");
  await page.getByRole("link", { name: "Otros módulos de DAW" }).click();
  await expect(page).toHaveURL(/#\/daw\/cursos$/);
  await expect(page.locator("#daw-title")).toContainText("Cursos de DAW");
  await expect(page.getByRole("navigation", { name: "Secciones" }).getByRole("link", { name: "DAW", exact: true })).toHaveAttribute("aria-current", "page");
  await expect(page.locator(".daw-card")).toHaveCount(5);
  await page.getByRole("link", { name: "Programación" }).click();
  await expect(page.locator("#daw-title")).toHaveText("Programación");
  await expect(page.locator(".block-row")).toHaveCount(9);
});

test("la teoría se lee dentro de la web y el mini-quiz se corrige", async ({ page }) => {
  await page.goto("/#/daw/sql/leccion/bd-tipos-y-modelos");
  await expect(page.locator("#daw-title")).toHaveText("Tipos y modelos de bases de datos");
  await expect(page.locator(".daw-theory")).toContainText("Fragmentación");
  await page.locator("#daw-quiz fieldset").first().locator("input").first().check();
  await page.getByRole("button", { name: "Corregir" }).click();
  await expect(page.locator("#daw-quiz-result")).toContainText("de 2 correctas");
  await page.getByRole("link", { name: "Practicar este bloque" }).click();
  await expect(page.locator("#daw-title")).toContainText("Práctica · UD1");
});

test("práctica: completar el hueco y ordenar líneas se corrigen y guardan el progreso", async ({ page }) => {
  // Solo quedan sin responder las dos preguntas de escribir código del bloque UT7 → salen primero
  await page.addInitScript(() => {
    const answers = {};
    for (let n = 126; n <= 133; n += 1) answers[`prog-${n}`] = [true];
    localStorage.setItem("pld:course:programacion", JSON.stringify({ answers }));
  });
  await page.goto("/#/daw/programacion/practica/prog-ut7");
  await expect(page.locator("#daw-title")).toContainText("Práctica · UT7");
  await page.getByRole("button", { name: "Comprobar" }).click();
  await expect(page.locator("#daw-message")).toHaveText("Escribe lo que va en el hueco.");
  await page.getByLabel("Lo que va en ___").fill(" 21 ");
  await page.getByRole("button", { name: "Comprobar" }).click();
  await expect(page.locator(".quiz__verdict")).toHaveText("¡Correcto!");
  const saved = await page.evaluate(() => JSON.parse(localStorage.getItem("pld:course:programacion")));
  expect(saved.answers["prog-134"]).toEqual([true]);
  expect(saved.srs["prog-134"].box).toBe(1);
});

test("ordenar líneas: se añaden y quitan pulsando, y se corrige", async ({ page }) => {
  await page.addInitScript(() => {
    // Todas las del bloque UT3 respondidas salvo la de ordenar (prog-45)
    const answers = {};
    for (let n = 32; n <= 56; n += 1) if (n !== 45) answers[`prog-${n}`] = [true];
    localStorage.setItem("pld:course:programacion", JSON.stringify({ answers }));
  });
  await page.goto("/#/daw/programacion/practica/prog-ut3");
  const order = ["total = 0", "for n in range(1, 11):", "if n % 2 == 0:", "total += n", "print(total)"];
  await expect(page.locator(".daw-order--pool .daw-line")).toHaveCount(5);
  await page.locator(".daw-order--pool .daw-line", { hasText: "print(total)" }).click();
  await page.locator(".daw-order:not(.daw-order--pool) .daw-line").first().click(); // quitarla
  for (const line of order) await page.locator(".daw-order--pool .daw-line", { hasText: line }).first().click();
  await page.getByRole("button", { name: "Comprobar" }).click();
  await expect(page.locator(".quiz__verdict")).toHaveText("¡Correcto!");
});

test("el progreso de un curso se guarda en la cuenta y conserva lo que haya puesto la app", async ({ page, request }) => {
  const email = uniqueEmail();
  const password = "contraseña-e2e-123";
  await request.post(`${API}/api/auth/register`, { data: { email, password, display_name: "Ana", accept_privacy: true } });
  const login = await request.post(`${API}/api/auth/login`, { form: { username: email, password } });
  const headers = { Authorization: `Bearer ${(await login.json()).access_token}` };
  // La app ya había respondido una pregunta y guarda un campo que la web no conoce
  await request.put(`${API}/api/course-state/sql`, { headers, data: { data: { answers: { "sql-01": [true] }, extra: 1 } } });

  await page.goto("/#/daw/sql/practica/bd-ud1");
  await page.getByRole("button", { name: "Iniciar sesión" }).click();
  await page.locator("#login-form").getByLabel("Email").fill(email);
  await page.locator("#login-form").getByLabel("Contraseña").fill(password);
  await page.locator("#login-form").getByRole("button", { name: "Entrar" }).click();
  await expect(page.locator("#account-label")).toHaveText("Ana");

  await page.locator(".quiz__option input").first().check();
  await page.getByRole("button", { name: "Comprobar" }).click();
  await expect
    .poll(async () => Object.keys((await (await request.get(`${API}/api/course-state/sql`, { headers })).json()).data.answers ?? {}).length)
    .toBe(2);
  const remote = (await (await request.get(`${API}/api/course-state/sql`, { headers })).json()).data;
  expect(remote.answers["sql-01"]).toEqual([true]);
  expect(remote.extra).toBe(1);
});

test("catálogo, lección y práctica sin infracciones WCAG", async ({ page }) => {
  for (const route of ["/#/daw/cursos", "/#/daw/programacion/leccion/prog-ut2-elementos", "/#/daw/js/practica/js-fundamentos"]) {
    await page.goto(route);
    await expect(page.locator("#daw-title")).toBeVisible();
    await page.waitForFunction(() => document.getAnimations().every((a) => a.playState !== "running"));
    const results = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"]).analyze();
    const summary = results.violations.map((v) => `${v.id}: ${v.nodes.map((n) => n.target).join(", ")}`);
    expect(summary, `${route}\n${summary.join("\n")}`).toEqual([]);
  }
});
