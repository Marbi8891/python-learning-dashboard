// Seguridad del frontend (ADR-0022): CSP sin bloqueos, datos manipulados, cierre de sesión y marcos.
const { test, expect, uniqueEmail } = require("./fixtures");

const API = "http://127.0.0.1:8000";

test("la política de seguridad (CSP) está activa y no bloquea nada de la app", async ({ page }) => {
  await page.addInitScript(() => {
    window.__violations = [];
    document.addEventListener("securitypolicyviolation", (e) => window.__violations.push(`${e.violatedDirective} ${e.blockedURI}`));
  });
  for (const route of ["/#/inicio", "/#/leccion/variables", "/#/pcap", "/#/daw/sql/practica/bd-ud3", "/#/perfil"]) {
    await page.goto(route);
    await page.locator("main").waitFor();
    await page.waitForLoadState("networkidle");
  }
  const csp = await page.locator('meta[http-equiv="Content-Security-Policy"]').getAttribute("content");
  expect(csp).toContain("object-src 'none'");
  expect(await page.evaluate(() => window.__violations)).toEqual([]);
});

test("un dato manipulado en el navegador no se convierte en HTML", async ({ page }) => {
  await page.addInitScript(() => {
    const payload = '"><img src=x onerror="window.__pwned=1">';
    localStorage.setItem(
      "pld:pcap",
      JSON.stringify({
        plan: { examDate: payload },
        exams: [{ date: payload, correct: payload, total: 1, score: 1, seconds: 1 }],
        answers: { "oop-01": [payload] },
      }),
    );
  });
  await page.goto("/#/pcap");
  await expect(page.locator("#pcap-title")).toBeVisible();
  await page.waitForTimeout(300);
  expect(await page.evaluate(() => window.__pwned)).toBeUndefined();
  await expect(page.locator(".plan-form input[name=exam-date]")).toHaveValue("");
});

test("cerrar sesión borra del navegador los datos personales, salvo las preferencias", async ({ page, request }) => {
  const email = uniqueEmail();
  const password = "contraseña-e2e-123";
  await request.post(`${API}/api/auth/register`, { data: { email, password, display_name: "Ana", accept_privacy: true } });
  await page.addInitScript(() => {
    if (sessionStorage.getItem("seeded")) return;
    sessionStorage.setItem("seeded", "1");
    localStorage.setItem("pld:prefs", JSON.stringify({ theme: "light" }));
    localStorage.setItem("pld:draft:variables", "print('mi código')");
    localStorage.setItem("pld:course:sql", JSON.stringify({ answers: { "sql-01": [true] } }));
  });
  await page.goto("/#/daw");
  await page.getByRole("button", { name: "Iniciar sesión" }).click();
  await page.locator("#login-form").getByLabel("Email").fill(email);
  await page.locator("#login-form").getByLabel("Contraseña").fill(password);
  await page.locator("#login-form").getByRole("button", { name: "Entrar" }).click();
  await expect(page.locator("#account-label")).toHaveText("Ana");

  await page.locator("#account-button").click();
  await page.getByLabel("Cerrar también la sesión en mis otros dispositivos").check();
  await page.getByRole("button", { name: "Cerrar sesión" }).click();
  await expect(page.locator("#toast")).toContainText("Sesión cerrada en todos tus dispositivos");
  await expect(page.locator("#account-label")).toHaveText("Iniciar sesión");
  const left = await page.evaluate(() => Object.keys(localStorage).filter((k) => k.startsWith("pld:")));
  expect(left.filter((k) => !["pld:prefs", "pld:game"].includes(k))).toEqual([]);
  expect(left).toContain("pld:prefs");
  // El progreso del curso sí se subió a la cuenta antes de borrarlo del navegador
  const login = await request.post(`${API}/api/auth/login`, { form: { username: email, password } });
  const headers = { Authorization: `Bearer ${(await login.json()).access_token}` };
  const sql = await (await request.get(`${API}/api/course-state/sql`, { headers })).json();
  expect(sql.data.answers["sql-01"]).toEqual([true]);
});

test("la web no se muestra dentro de un marco de otra página (clickjacking)", async ({ page }) => {
  await page.setContent('<iframe src="http://localhost:5500/#/inicio" width="800" height="600"></iframe>');
  const frame = page.frameLocator("iframe");
  await expect(frame.locator("html")).toHaveCSS("display", "none");
});
