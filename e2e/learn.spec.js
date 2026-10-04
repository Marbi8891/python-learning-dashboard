// Núcleo educativo (ADR-0031): Aprender, Teoría, Practicar, Progreso y sesiones con
// corrección, explicación de errores, nuevo intento, repaso y sincronización con la cuenta.
const AxeBuilder = require("@axe-core/playwright").default;
const { test, expect, uniqueEmail } = require("./fixtures");

const API = "http://127.0.0.1:8000";

/** Empieza una sesión con ejercicios concretos (los mismos módulos que usa la app). */
async function startSession(page, options) {
  await page.waitForSelector("#learn-title");
  await page.evaluate(async (opts) => {
    const view = await import("./js/learn/session-view.js");
    view.startSession(opts);
  }, options);
  await expect(page).toHaveURL(/#\/sesion$/);
  await page.locator("#lx-form, .lx-intro").first().waitFor();
}

async function audit(page) {
  await page.waitForFunction(() => document.getAnimations().every((a) => a.playState !== "running"), null, { timeout: 20_000 });
  const results = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"]).analyze();
  const summary = results.violations.map((v) => `${v.id} (${v.impact}): ${v.nodes.map((n) => n.target).join(", ")}`);
  expect(summary, summary.join("\n")).toEqual([]);
}

test("la portada responde «¿Qué estudio ahora?» y propone el primer concepto", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveURL(/#\/aprender$/);
  await expect(page.locator("#learn-title")).toHaveText("¿Qué estudio ahora?");
  await expect(page.getByRole("navigation", { name: "Secciones" }).getByRole("link", { name: "Aprender", exact: true })).toHaveAttribute("aria-current", "page");
  const first = page.locator(".lx-plan__item").first();
  await expect(first).toContainText("Comprender el problema y diseñar el algoritmo");
  await expect(first).toContainText("Siguiente concepto de la ruta");
  // La barra lateral del curso PCAP (XP, lecciones) no aparece en el núcleo
  await expect(page.locator(".stats-card")).toBeHidden();
  await expect(page.locator(".path")).toBeHidden();
});

test("menú principal: Aprender, Teoría, Practicar, DAW y Progreso; el PCAP sigue accesible", async ({ page }) => {
  await page.goto("/#/aprender");
  for (const name of ["Teoría", "Practicar", "Progreso"]) {
    await page.getByRole("navigation", { name: "Secciones" }).getByRole("link", { name, exact: true }).click();
    await expect(page.getByRole("navigation", { name: "Secciones" }).getByRole("link", { name, exact: true })).toHaveAttribute("aria-current", "page");
    await expect(page.locator("#learn-title")).toBeVisible();
  }
  await page.getByRole("link", { name: "Curso PCAP" }).click();
  await expect(page.locator("#home-title")).toContainText("Prepara el PCAP");
  await expect(page.locator(".stats-card")).toBeVisible();
});

test("teoría: concepto con explicación, ejemplo línea a línea, cuándo usarlo y errores habituales", async ({ page }) => {
  await page.goto("/#/teoria");
  await expect(page.locator(".lx-concept")).toHaveCount(22);
  await page.getByRole("link", { name: "Bucles: while y for" }).click();
  await expect(page).toHaveURL(/#\/teoria\/bucles$/);
  await expect(page.locator("#learn-title")).toHaveText("Bucles: while y for");
  await expect(page.locator(".prose")).toContainText("range(inicio, fin, paso)"); // teoría reutilizada de la lección
  await expect(page.locator(".lx-code--numbered .lx-line")).toHaveCount(7);
  await expect(page.locator(".lx-lines li").first()).toContainText("Línea 1");
  await expect(page.locator(".lx-output")).toContainText("n final: -2"); // salida real del ejemplo
  await page.locator(".lx-details summary", { hasText: "Confunde la condición del bucle con la condición de salida" }).click();
  await expect(page.locator(".lx-error").first()).toContainText("Cómo evitarlo");
  await expect(page.getByRole("link", { name: /Lección «Bucles/ })).toHaveAttribute("href", "#/leccion/bucles");
  await expect(page.locator(".lx-warning")).toContainText("Necesitas reforzar Condicionales: if, elif y else");
});

test("sesión: fallo con error típico → explicación → nuevo intento al final → resumen con el error explicado", async ({ page }) => {
  await page.goto("/#/aprender");
  await startSession(page, { kind: "practice", title: "Bucles", exercises: ["buc-01", "buc-06"] });
  await expect(page.locator(".lx-session-bar")).toContainText("Ejercicio 1 de 2");

  // Sin respuesta no se corrige
  await page.getByRole("button", { name: "Comprobar", exact: true }).click();
  await expect(page.locator("#lx-message")).toHaveText("Escribe lo que crees que muestra el programa.");

  // buc-01: «2 3 4 5 6» es la trampa de creer que range incluye el final
  await page.getByLabel(/Lo que muestra el programa/).fill("2 3 4 5 6");
  await page.getByRole("button", { name: "Comprobar", exact: true }).click();
  const feedback = page.locator(".lx-feedback");
  await expect(feedback).toBeFocused();
  await expect(feedback).toContainText("No es correcto");
  await expect(feedback).toContainText("Cree que range incluye el valor final");
  await expect(feedback).toContainText("Cómo pensarlo");
  await expect(feedback).toContainText("volverás a intentarlo");
  await expect(page.locator(".lx-session-bar")).toContainText("de 3"); // se ha añadido el nuevo intento

  await page.getByRole("button", { name: "Siguiente →" }).click();
  await page.getByLabel("Lo que va en ___").fill("6");
  await page.getByRole("button", { name: "Comprobar", exact: true }).click();
  await expect(page.locator(".lx-feedback")).toContainText("Correcto");
  await page.getByRole("button", { name: "Siguiente →" }).click();

  await expect(page.locator(".lx-retry")).toContainText("Nuevo intento");
  await page.getByRole("button", { name: "No lo sé: ver la explicación" }).click();
  await page.getByRole("button", { name: "Ver el resumen" }).click();

  const summary = page.locator(".lx-summary");
  await expect(summary).toContainText("1 de 2 correctos");
  await expect(summary).toContainText("Cree que range incluye el valor final");
  await expect(summary.getByRole("button", { name: "Practicar este error" })).toBeVisible();

  // El progreso queda guardado: error pendiente, repaso programado y actividad
  await page.goto("/#/practicar");
  await expect(page.locator(".lx-row--error")).toContainText("Cree que range incluye el valor final");
  await page.goto("/#/progreso");
  await expect(page.locator(".lx-facts")).toContainText("1 errores pendientes");
  await expect(page.locator("#lx-log-title + .lx-list li")).toHaveCount(3);
  await page.reload();
  await expect(page.locator(".lx-facts")).toContainText("1 errores pendientes");
});

test("el plan de hoy prioriza el error reciente y propone corregirlo", async ({ page }) => {
  await page.goto("/#/aprender");
  await startSession(page, { kind: "practice", title: "Tipos", exercises: ["tip-01"] });
  await page.getByLabel(/Lo que muestra el programa/).fill("6");
  await page.getByRole("button", { name: "Comprobar", exact: true }).click();
  await expect(page.locator(".lx-feedback")).toBeVisible();
  await page.goto("/#/aprender");
  const errorsItem = page.locator('.lx-plan__item[data-type="errors"]');
  await expect(errorsItem).toContainText("Tipos de datos y conversiones");
  await expect(errorsItem).toContainText("Error reciente: Trata un texto que parece número");
});

test("aprender un concepto nuevo empieza por el concepto y su ejemplo", async ({ page }) => {
  await page.goto("/#/aprender");
  await page.locator(".lx-plan__item").first().getByRole("button", { name: /Empezar/ }).click();
  await expect(page).toHaveURL(/#\/sesion$/);
  await expect(page.locator(".lx-intro")).toContainText("Comprender el problema y diseñar el algoritmo");
  await expect(page.locator(".lx-intro .lx-lines li").first()).toBeVisible();
  await page.getByRole("button", { name: "Entendido: a practicar →" }).click();
  await expect(page.locator("#lx-form")).toBeVisible();
});

test("ordenar líneas y encontrar el error se corrigen", async ({ page }) => {
  await page.goto("/#/aprender");
  await startSession(page, { kind: "practice", title: "Mixto", exercises: ["pse-05", "acu-02"] });
  for (const text of ["n = int(input())", "while n > 0:", "print(n)", "n = n - 2"]) {
    await page.locator(".daw-order--pool .daw-line", { hasText: text }).first().click();
  }
  await page.getByRole("button", { name: "Comprobar", exact: true }).click();
  await expect(page.locator(".lx-feedback")).toContainText("Correcto");
  await page.getByRole("button", { name: "Siguiente →" }).click();
  await page.locator(".lx-bug__line").nth(2).click(); // línea 3: no es la del error
  await page.getByRole("button", { name: "Comprobar", exact: true }).click();
  await expect(page.locator(".lx-feedback")).toContainText("Inicializa un producto a 0");
  await expect(page.locator('.lx-bug__line[data-correct="true"]')).toContainText("producto = 0");
});

test("escribir código: los tests de Pyodide corrigen y el caso que falla delata el error", async ({ page }) => {
  test.slow(); // la primera carga de Python tarda
  await page.goto("/#/aprender");
  await startSession(page, { kind: "practice", title: "Acumuladores", exercises: ["acu-04"] });
  const editor = page.getByLabel("Tu programa");
  await editor.fill(
    "def media_positivos(numeros):\n    suma = 0\n    cuantos = 0\n    for n in numeros:\n        if n > 0:\n            suma += n\n            cuantos += 1\n    return suma / cuantos",
  );
  await page.getByRole("button", { name: "Comprobar con los tests" }).click();
  const feedback = page.locator(".lx-feedback");
  await expect(feedback).toBeVisible({ timeout: 90_000 });
  await expect(page.locator(".check")).toContainText("Falla la prueba 3 de 4");
  await expect(feedback).toContainText("Calcula la media dentro del bucle o sin proteger la división");
});

test("simulacro de sesión: sin explicación entre preguntas y corrección al final", async ({ page }) => {
  await page.goto("/#/aprender");
  await startSession(page, { kind: "exam", title: "Simulacro", exercises: ["var-04", "ope-04"], timeLimit: 600 });
  await expect(page.locator("#lx-timer")).toBeVisible();
  await page.locator('input[name="lx-choice"]').first().check();
  await page.getByRole("button", { name: "Comprobar", exact: true }).click();
  await expect(page.locator(".lx-feedback")).toHaveCount(0);
  await expect(page.locator(".lx-session-bar")).toContainText("Ejercicio 2 de 2");
  await page.locator('input[name="lx-choice"]').nth(1).check();
  await page.getByRole("button", { name: "Comprobar", exact: true }).click();
  await expect(page.locator(".lx-summary")).toContainText("1 de 2 correctos");
  await expect(page.locator(".lx-reviews li")).toHaveCount(2);
});

test("el progreso por conceptos se sincroniza con la cuenta y se fusiona con el de otro dispositivo", async ({ page, request }) => {
  const email = uniqueEmail();
  await request.post(`${API}/api/auth/register`, { data: { email, password: "contraseña-segura", display_name: "Ana", accept_privacy: true } });
  const login = await request.post(`${API}/api/auth/login`, { form: { username: email, password: "contraseña-segura" } });
  const { access_token: token } = await login.json();
  const headers = { Authorization: `Bearer ${token}` };
  // «Otro dispositivo» (la app) ya guardó un error en la cuenta
  const remote = {
    v: 1,
    ex: { "var-01": { h: [false], last: new Date().toISOString(), n: 1 } },
    errors: { "variables.orden-asignacion": { n: 1, last: new Date().toISOString(), streak: 0 } },
    log: [{ at: new Date().toISOString(), ex: "var-01", ok: false, err: "variables.orden-asignacion" }],
  };
  await request.put(`${API}/api/course-state/learn`, { headers, data: { data: remote } });

  await page.addInitScript((t) => localStorage.setItem("pld:token", t), token);
  await page.goto("/#/aprender");
  await startSession(page, { kind: "practice", title: "Bucles", exercises: ["buc-01"] });
  await page.getByLabel(/Lo que muestra el programa/).fill("2 3 4 5");
  await page.getByRole("button", { name: "Comprobar", exact: true }).click();
  await expect(page.locator(".lx-feedback")).toContainText("Correcto");

  await expect
    .poll(async () => {
      const saved = await (await request.get(`${API}/api/course-state/learn`, { headers })).json();
      return Object.keys(saved.data.ex ?? {}).sort();
    }, { timeout: 15_000 })
    .toEqual(["buc-01", "var-01"]);
  await page.goto("/#/practicar");
  await expect(page.locator(".lx-row--error")).toContainText("asignación funciona de izquierda a derecha");
});

for (const colorScheme of ["light", "dark"]) {
  test.describe(`núcleo educativo en modo ${colorScheme}`, () => {
    test.use({ colorScheme });
    test("Hoy, Teoría, concepto, Practicar, Progreso y una corrección sin infracciones WCAG", async ({ page }) => {
      for (const route of ["/#/aprender", "/#/teoria", "/#/teoria/recorridos", "/#/practicar", "/#/progreso"]) {
        await page.goto(route);
        await page.locator("#learn-title").waitFor();
        await audit(page);
      }
      await startSession(page, { kind: "practice", title: "Mixto", exercises: ["acu-02", "buc-01"] });
      await audit(page);
      await page.locator(".lx-bug__line").first().click();
      await page.getByRole("button", { name: "Comprobar", exact: true }).click();
      await audit(page);
    });
  });
}

test("en el móvil el plan de hoy se lee sin desbordarse", async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 800 });
  await page.goto("/#/aprender");
  await page.locator("#learn-title").waitFor();
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth);
  expect(overflow).toBe(false);
  // Regresión: el rediseño reservaba en el móvil la columna de la barra lateral (272 px vacíos)
  const main = await page.locator("#main").boundingBox();
  expect(main.width).toBe(375);
});

test.describe("Preparación DAW", () => {
  test("competencias, aviso de qué reforzar y temario del centro", async ({ page }) => {
    // Fundamentos empezado y flojo, Programación empezada: debe pedir reforzar Fundamentos
    await page.addInitScript(() => {
      const now = new Date().toISOString();
      localStorage.setItem(
        "pld:learn",
        JSON.stringify({ v: 1, ex: { "var-01": { h: [true], last: now, n: 1 }, "fun-01": { h: [false], last: now, n: 1 } } }),
      );
    });
    await page.goto("/#/daw");
    await expect(page.locator("#learn-title")).toHaveText("Preparación DAW");
    await expect(page.getByRole("navigation", { name: "Secciones" }).getByRole("link", { name: "DAW", exact: true })).toHaveAttribute("aria-current", "page");
    await expect(page.locator(".lx-competency")).toHaveCount(3);
    await expect(page.locator("#comp-programacion + .lx-muted ~ .lx-warning")).toContainText(/Necesitas reforzar .+ antes de pasar a Programación/);
    await expect(page.getByRole("link", { name: /Programación por unidades de trabajo/ })).toHaveAttribute("href", "#/daw/programacion");
  });

  test("simulacro del temario completo: cronometrado, con problemas de código y guardado en el historial", async ({ page }) => {
    await page.goto("/#/daw");
    await page.getByRole("button", { name: /Simulacro del temario completo/ }).click();
    await expect(page).toHaveURL(/#\/sesion$/);
    await expect(page.locator("#lx-timer")).toHaveText(/^\d+:\d\d$/);
    await expect(page.locator(".lx-session-bar")).toContainText("de 12");
    await page.getByRole("button", { name: "Terminar el simulacro" }).click();
    await expect(page.locator(".lx-summary")).toContainText("0 de 12 correctos");
    await expect(page.locator(".lx-summary")).toContainText("Sin responder: 12");
    await page.goto("/#/daw");
    await expect(page.locator("#lx-hist-title + .lx-list li")).toHaveCount(1);
    await expect(page.locator("#lx-hist-title + .lx-list")).toContainText("Temario completo");
  });

  test("Preparación DAW sin infracciones WCAG", async ({ page }) => {
    await page.goto("/#/daw");
    await page.locator("#learn-title").waitFor();
    await audit(page);
  });
});

test("prueba de nivel: se ofrece al empezar y lo acertado se salta en la ruta personal", async ({ page }) => {
  await page.goto("/#/aprender");
  await page.getByRole("button", { name: "Hacer la prueba de nivel" }).click();
  await expect(page.locator(".lx-session-bar")).toContainText("de 21"); // un concepto por pregunta, sin POO

  // Prueba corta con ejercicios conocidos: acierta Comprender el problema y Variables
  await startSession(page, { kind: "diagnostic", title: "Prueba de nivel", exercises: ["alg-01", "var-01", "tip-01"] });
  await page.locator('input[name="lx-choice"]').first().check();
  await page.getByRole("button", { name: "Comprobar", exact: true }).click();
  await page.getByLabel(/Lo que muestra el programa/).fill("3");
  await page.getByRole("button", { name: "Comprobar", exact: true }).click();
  await page.getByRole("button", { name: "No lo sé", exact: true }).click();
  await expect(page.locator(".lx-summary")).toContainText("Superados en la prueba");
  await expect(page.locator(".lx-reviews li")).toHaveCount(3);

  await page.goto("/#/aprender");
  await expect(page.getByRole("button", { name: "Hacer la prueba de nivel" })).toHaveCount(0);
  await page.locator(".lx-route summary").click();
  // Tipos se falló en la prueba: el siguiente concepto nuevo (Operadores) pide reforzarlo antes
  await expect(page.locator('.lx-route__item[data-status="next"]')).toContainText("Operadores y expresiones");
  await expect(page.locator('.lx-route__item[data-status="next"]')).toContainText("antes refuerza Tipos de datos");
  await expect(page.locator(".lx-route__item").nth(1)).toContainText("Superado en la prueba de nivel");
});
