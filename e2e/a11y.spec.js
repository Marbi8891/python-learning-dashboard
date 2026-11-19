// Auditoría automática de accesibilidad (WCAG 2.2 A/AA) con axe-core.
// El tema «Automático» sigue al sistema: se audita la app en claro y en oscuro.
const AxeBuilder = require("@axe-core/playwright").default;
const { test, expect, openLesson } = require("./fixtures");

// Los avisos van en cola (app.js): entre uno y el siguiente pasan 250 ms sin aviso visible. Esperar
// solo a «no hay aviso» deja empezar axe en ese hueco, y el siguiente aparece a media transición
// con el contraste rebajado por la opacidad. Por eso la calma tiene que durar más que ese hueco.
const QUIET_MS = 400;

async function waitForQuietUi(page) {
  await page.evaluate(() => delete window.__pldQuietSince);
  // Espera a que acaben las animaciones de entrada y a que se vacíe la cola de avisos (toast):
  // a media transición el contraste es menor y axe lo cuenta como fallo
  await page.waitForFunction(
    (quietMs) => {
      const busy =
        document.querySelector("#toast.toast--visible") ||
        document.getAnimations().some((a) => a.playState === "running");
      if (busy) {
        delete window.__pldQuietSince;
        return false;
      }
      window.__pldQuietSince ??= performance.now();
      return performance.now() - window.__pldQuietSince >= quietMs;
    },
    QUIET_MS,
    { timeout: 20_000, polling: 50 },
  );
}

async function audit(page) {
  await waitForQuietUi(page);
  const results = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"]).analyze();
  const summary = results.violations.map((v) => `${v.id} (${v.impact}): ${v.nodes.map((n) => n.target).join(", ")}`);
  expect(summary, summary.join("\n")).toEqual([]);
}

for (const colorScheme of ["light", "dark"]) {
  test.describe(`sistema en modo ${colorScheme}`, () => {
    test.use({ colorScheme });
    test("lección y quiz con código sin infracciones WCAG", async ({ page }) => {
      await openLesson(page, "funciones");
      await expect(page.locator("html")).toHaveAttribute("data-theme", colorScheme);
      await audit(page);
      await page.getByRole("tab", { name: "Quiz" }).click();
      await audit(page);
    });
  });
}

test("pestaña de práctica, asistente y diálogo de cuenta sin infracciones", async ({ page }) => {
  await openLesson(page, "bucles");
  await page.getByRole("tab", { name: "Práctica y Ejercicio" }).click();
  await page.getByRole("button", { name: "Abrir asistente" }).click();
  await audit(page);
  await page.keyboard.press("Escape");
  await page.getByRole("button", { name: "Iniciar sesión" }).click();
  await audit(page);
});

test.describe("móvil", () => {
  test.use({ viewport: { width: 390, height: 844 } });
  test("menú abierto sin infracciones", async ({ page }) => {
    await openLesson(page, "funciones");
    await page.getByRole("button", { name: "Menú" }).click();
    await audit(page);
  });
});

test("quiz respondido, reto y vitrina de logros sin infracciones", async ({ page }) => {
  await openLesson(page, "funciones");
  await page.getByRole("tab", { name: "Quiz" }).click();
  for (let qi = 0; qi < 3; qi += 1) await page.locator(`input[name=q${qi}]`).first().check();
  await page.getByRole("button", { name: "Comprobar respuestas" }).click();
  await audit(page);
  await page.getByRole("button", { name: /Logros/ }).click();
  await audit(page);
});

test("política de privacidad sin infracciones", async ({ page }) => {
  await page.goto("/privacidad.html");
  await audit(page);
});

for (const colorScheme of ["light", "dark"]) {
  test.describe(`portada y perfil en modo ${colorScheme}`, () => {
    test.use({ colorScheme });
    test("portada con temario y «Mi aprendizaje» sin infracciones", async ({ page }) => {
      await openLesson(page, "variables");
      await page.getByRole("tab", { name: "Práctica y Ejercicio" }).click();
      await page.getByRole("button", { name: "Marcar como completada" }).click();
      await page.getByRole("link", { name: "Curso PCAP" }).click();
      await expect(page.locator("#home-title")).toBeVisible();
      for (const module of await page.locator(".syllabus__module").all()) await module.evaluate((d) => (d.open = true));
      await audit(page);
      await page.goto("/#/perfil");
      await expect(page.locator("#profile-title")).toBeVisible();
      await audit(page);
    });
  });
}

test("tema claro con error explicado y diálogo de aspecto sin infracciones", async ({ page }) => {
  test.setTimeout(120_000);
  await page.addInitScript(() => localStorage.setItem("pld:prefs", JSON.stringify({ theme: "light", font: "grande" })));
  await openLesson(page, "variables");
  await page.locator("#console-editor").fill("print(x)");
  await page.locator("#console-run").click();
  await expect(page.getByRole("note")).toBeVisible({ timeout: 90_000 });
  await audit(page);
  await page.getByRole("button", { name: "Aspecto" }).click();
  await audit(page);
});

for (const colorScheme of ["light", "dark"]) {
  test.describe(`zona PCAP en modo ${colorScheme}`, () => {
    test.use({ colorScheme });
    test("panel, simulacro, resultado, práctica y fichas sin infracciones", async ({ page }) => {
      await page.goto("/#/pcap");
      await expect(page.locator(".readiness")).toBeVisible();
      await audit(page);
      await page.getByRole("link", { name: "Hacer un simulacro →" }).click();
      await page.getByRole("button", { name: "Empezar el simulacro" }).click();
      await page.locator(".exam-q input").first().check();
      await audit(page);
      await page.locator(".exam-form").getByRole("button", { name: "Siguiente →" }).click();
      await page.locator(".exam-nav").getByRole("button", { name: "Terminar examen" }).click();
      await page.getByRole("button", { name: "Sí, terminar" }).click();
      await page.locator(".review-item summary").first().click();
      await audit(page);
      await page.goto("/#/pcap/practica/excepciones");
      await page.locator(".exam-q input").first().check();
      await page.getByRole("button", { name: "Comprobar" }).click();
      await audit(page);
      await page.goto("/#/pcap/fichas");
      await page.getByRole("button", { name: "Ver respuesta" }).click();
      await audit(page);
    });
  });
}

// Regresión del fallo de contraste en #toast (Sprint 0): terminar un simulacro encola dos avisos
// («Simulacro terminado» y «Logro desbloqueado»), con un hueco de 250 ms entre ellos
async function finishExamWithToasts(page) {
  await page.addInitScript(() => {
    window.__toastsShown = [];
    document.addEventListener("DOMContentLoaded", () => {
      const toast = document.querySelector("#toast");
      new MutationObserver(() => {
        if (toast.classList.contains("toast--visible")) window.__toastsShown.push(toast.textContent);
      }).observe(toast, { attributes: true, attributeFilter: ["class"] });
    });
  });
  await page.goto("/#/pcap/simulacro");
  await page.getByRole("button", { name: "Empezar el simulacro" }).click();
  await page.locator(".exam-q input").first().check();
  await page.locator(".exam-nav").getByRole("button", { name: "Terminar examen" }).click();
  await page.getByRole("button", { name: "Sí, terminar" }).click();
}

test("la auditoría espera a que se vacíe la cola de avisos", async ({ page }) => {
  await finishExamWithToasts(page);
  await waitForQuietUi(page);
  const shown = await page.evaluate(() => window.__toastsShown);
  expect(shown).toHaveLength(2);
  expect(shown[1]).toContain("Logro desbloqueado");
  await expect(page.locator("#toast")).not.toHaveClass(/toast--visible/);
});

for (const colorScheme of ["light", "dark"]) {
  test(`el aviso visible tiene contraste suficiente en modo ${colorScheme}`, async ({ page }) => {
    await page.emulateMedia({ colorScheme });
    await finishExamWithToasts(page);
    const toast = page.locator("#toast.toast--visible");
    await expect(toast).toBeVisible();
    // Contraste del aviso ya aparecido (opacidad 1), no a media transición
    await expect(toast).toHaveCSS("opacity", "1");
    const results = await new AxeBuilder({ page }).include("#toast").withRules(["color-contrast"]).analyze();
    expect(results.violations.map((v) => v.id)).toEqual([]);
    expect(results.passes.map((p) => p.id)).toContain("color-contrast");
  });
}

test("plan de estudio, repaso de hoy y certificado sin infracciones", async ({ page }) => {
  await page.addInitScript(() =>
    localStorage.setItem(
      "pld:pcap",
      JSON.stringify({
        plan: { examDate: "2099-01-01" },
        srs: { "oop-01": { box: 1, due: "2026-01-01", last: "2026-01-01T00:00:00Z" } },
      }),
    ),
  );
  await page.goto("/#/pcap");
  await expect(page.locator(".plan-tasks")).toBeVisible();
  await audit(page);
  await page.goto("/#/certificado");
  await expect(page.locator(".cert-requirements")).toBeVisible();
  await audit(page);
});

test("al comprobar el quiz el foco pasa a la nota, no se pierde (WCAG 2.4.3)", async ({ page }) => {
  await openLesson(page, "funciones");
  await page.getByRole("tab", { name: "Quiz" }).click();
  for (let qi = 0; qi < 3; qi += 1) await page.locator(`input[name=q${qi}]`).first().check();
  await page.getByRole("button", { name: "Comprobar respuestas" }).press("Enter");
  await expect(page.locator("#quiz-score")).toBeFocused();
  await expect(page.locator("#quiz-score")).toContainText("/3");
});

test("la confirmación de terminar el simulacro devuelve el foco y se cierra con Esc", async ({ page }) => {
  await page.goto("/#/pcap/simulacro");
  await page.getByRole("button", { name: "Empezar el simulacro" }).click();
  const opener = page.locator(".exam-nav").getByRole("button", { name: "Terminar examen" });
  await opener.click();
  await expect(page.getByRole("button", { name: "Sí, terminar" })).toBeFocused();
  await page.getByRole("button", { name: "Seguir con el examen" }).click();
  await expect(page.locator("#exam-confirm")).toBeHidden();
  await expect(opener).toBeFocused();
  await opener.press("Enter");
  await expect(page.getByRole("button", { name: "Sí, terminar" })).toBeFocused();
  await page.keyboard.press("Escape");
  await expect(page.locator("#exam-confirm")).toBeHidden();
  await expect(opener).toBeFocused();
});

test.describe("letra al 200 % (WCAG 1.4.4)", () => {
  test.use({ viewport: { width: 768, height: 900 } });
  for (const route of ["portada", "aprender", "pcap", "daw", "leccion/funciones"]) {
    test(`#/${route} no se sale por la derecha`, async ({ page }) => {
      await page.goto(`/#/${route}`);
      await page.waitForLoadState("networkidle");
      await page.evaluate(() => (document.documentElement.style.fontSize = "200%"));
      const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
      expect(overflow).toBeLessThanOrEqual(0);
    });
  }
});
