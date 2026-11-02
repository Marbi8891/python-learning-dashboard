// Inspecciona la web en local y deja capturas y un informe para mejorarla con evidencias.
//
// Abre cada ruta en móvil (390 × 844) y en escritorio (1366 × 900) con el Chromium de Playwright y
// mide, sin servicios externos ni de pago:
//   - infracciones WCAG 2.1 A/AA con axe-core (las mismas reglas que e2e/a11y.spec.js),
//   - errores de la consola y excepciones de JavaScript,
//   - desbordamiento horizontal (la página se sale por la derecha en el móvil),
//   - controles de menos de 24 × 24 px en el móvil (candidatos a revisar según WCAG 2.5.8),
//   - peticiones, bytes transferidos y tiempos de carga (DOMContentLoaded y load).
//
// Uso (desde la raíz del repositorio, después de `npm ci`):
//   node scripts/web/inspeccionar_web.mjs                      # todas las rutas, servidor propio
//   node scripts/web/inspeccionar_web.mjs --rutas portada,pcap # solo esas rutas
//   node scripts/web/inspeccionar_web.mjs --url http://localhost:5500   # web ya arrancada
//   node scripts/web/inspeccionar_web.mjs --comparar <carpeta de una inspección anterior>
//
// Solo inspecciona localhost: el objetivo es medir el código de la rama, no la web publicada.
// No modifica el repositorio: todo se guarda en una carpeta temporal (o en --salida).
import { spawn } from "node:child_process";
import { mkdirSync, mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";

const require = createRequire(import.meta.url);
const { chromium } = require("@playwright/test");
const AxeBuilder = require("@axe-core/playwright").default;

const RAIZ = resolve(import.meta.dirname, "..", "..");
const RUTAS = ["portada", "bienvenida", "inicio", "aprender", "teoria", "practicar", "pcap", "daw", "progreso"];
const VISTAS = {
  movil: { viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true },
  escritorio: { viewport: { width: 1366, height: 900 } },
};
const BACKEND = /127\.0\.0\.1:8000|localhost:8000/;

function leerArgumentos(argv) {
  const args = { rutas: RUTAS, url: "", salida: "", comparar: "", puerto: 5500 };
  for (let i = 0; i < argv.length; i += 1) {
    const valor = argv[i + 1];
    if (argv[i] === "--rutas") args.rutas = valor.split(",").map((r) => r.trim().replace(/^#?\/?/, ""));
    else if (argv[i] === "--url") args.url = valor;
    else if (argv[i] === "--salida") args.salida = valor;
    else if (argv[i] === "--comparar") args.comparar = valor;
    else if (argv[i] === "--puerto") args.puerto = Number(valor);
    else if (argv[i] === "--help" || argv[i] === "-h") {
      console.log(readFileSync(new URL(import.meta.url), "utf8").split("\n").slice(0, 20).join("\n"));
      process.exit(0);
    } else continue;
    i += 1;
  }
  return args;
}

function comprobarLocal(url) {
  const { hostname } = new URL(url);
  if (!["localhost", "127.0.0.1"].includes(hostname)) {
    console.error(`Solo se inspecciona la web en local (localhost o 127.0.0.1), no ${hostname}.`);
    process.exit(2);
  }
}

async function arrancarFrontend(puerto) {
  const python = process.platform === "win32" ? "python" : "python3";
  const servidor = spawn(python, ["e2e/serve_frontend.py", String(puerto)], { cwd: RAIZ, stdio: "ignore" });
  const url = `http://localhost:${puerto}`;
  for (let intento = 0; intento < 50; intento += 1) {
    try {
      if ((await fetch(`${url}/index.html`)).ok) return { servidor, url };
    } catch {
      // todavía arrancando
    }
    await new Promise((r) => setTimeout(r, 200));
  }
  servidor.kill();
  throw new Error(`El servidor del frontend no arrancó en el puerto ${puerto}. ¿Está ocupado? Prueba --puerto.`);
}

async function esperarQuieta(page) {
  await page.waitForLoadState("networkidle", { timeout: 15_000 }).catch(() => {});
  // Como en e2e/a11y.spec.js: a media animación o con un aviso desvaneciéndose el contraste engaña
  await page
    .waitForFunction(
      () =>
        !document.querySelector("#toast.toast--visible") &&
        document.getAnimations().every((a) => a.playState !== "running"),
      null,
      { timeout: 10_000 },
    )
    .catch(() => {});
}

async function medirPagina(page, esMovil) {
  return page.evaluate((movil) => {
    const doc = document.documentElement;
    const desborde = doc.scrollWidth - doc.clientWidth;
    const culpables = [];
    if (desborde > 0) {
      for (const el of document.body.querySelectorAll("*")) {
        const r = el.getBoundingClientRect();
        // Los fijos (fondo del menú lateral, avisos) no ensanchan la página: no son la causa
        const fijo = getComputedStyle(el).position === "fixed";
        if (!fijo && r.right > doc.clientWidth + 1 && r.width > 0 && culpables.length < 5) {
          culpables.push(el.id ? `#${el.id}` : `${el.tagName.toLowerCase()}.${[...el.classList].join(".")}`);
        }
      }
    }
    const pequenas = [];
    if (movil) {
      const interactivos = document.querySelectorAll("a[href], button, input, select, textarea, [role=button], [tabindex]");
      for (const el of interactivos) {
        const r = el.getBoundingClientRect();
        const visible = r.width > 0 && r.height > 0 && getComputedStyle(el).visibility !== "hidden";
        // Los enlaces dentro de un párrafo están exentos en WCAG 2.5.8
        const enTexto = el.tagName === "A" && el.closest("p, li") && el.closest("p, li").textContent.length > el.textContent.length + 20;
        if (visible && !enTexto && (r.width < 24 || r.height < 24)) {
          const nombre = (el.getAttribute("aria-label") || el.textContent || el.getAttribute("name") || "").trim().slice(0, 30);
          pequenas.push(`${el.tagName.toLowerCase()} «${nombre}» ${Math.round(r.width)}×${Math.round(r.height)}`);
        }
      }
    }
    const nav = performance.getEntriesByType("navigation")[0];
    const recursos = performance.getEntriesByType("resource");
    const bytes = recursos.reduce((t, r) => t + (r.transferSize || 0), nav?.transferSize || 0);
    const grandes = [...recursos]
      .sort((a, b) => (b.transferSize || 0) - (a.transferSize || 0))
      .slice(0, 3)
      .map((r) => `${new URL(r.name).pathname.split("/").pop() || r.name} (${Math.round((r.transferSize || 0) / 1024)} KB)`);
    return {
      titulo: document.title,
      desborde: Math.max(desborde, 0),
      culpables,
      pequenas,
      peticiones: recursos.length + 1,
      kb: Math.round(bytes / 1024),
      grandes,
      domListoMs: Math.round(nav?.domContentLoadedEventEnd || 0),
      cargaMs: Math.round(nav?.loadEventEnd || 0),
    };
  }, esMovil);
}

async function inspeccionarRuta(navegador, base, ruta, nombreVista, salida) {
  const contexto = await navegador.newContext(VISTAS[nombreVista]);
  // Cada ruta empieza como en una primera visita: sin progreso guardado ni service worker
  const page = await contexto.newPage();
  const errores = [];
  let sinBackend = 0;
  page.on("console", (m) => {
    if (m.type() !== "error") return;
    if (BACKEND.test(m.text()) || /Failed to load resource/.test(m.text())) sinBackend += 1;
    else errores.push(m.text().slice(0, 200));
  });
  page.on("pageerror", (e) => errores.push(`Excepción: ${e.message.slice(0, 200)}`));
  page.on("requestfailed", (r) => {
    if (BACKEND.test(r.url())) sinBackend += 1;
  });

  await page.goto(`${base}/index.html#/${ruta}`);
  await esperarQuieta(page);
  const medidas = await medirPagina(page, nombreVista === "movil");
  const axe = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"]).analyze();
  const captura = `${ruta}-${nombreVista}.png`;
  await page.screenshot({ path: join(salida, captura), fullPage: true });
  await contexto.close();

  return {
    ruta,
    vista: nombreVista,
    captura,
    errores,
    sinBackend,
    axe: axe.violations.map((v) => ({ id: v.id, impacto: v.impact, nodos: v.nodes.length, ayuda: v.help })),
    ...medidas,
  };
}

function fila(r) {
  const axe = r.axe.length ? r.axe.map((v) => `${v.id} (${v.nodos})`).join(", ") : "0";
  const desborde = r.desborde ? `**${r.desborde} px**` : "0";
  return `| #/${r.ruta} | ${r.vista} | ${axe} | ${r.errores.length} | ${desborde} | ${r.vista === "movil" ? r.pequenas.length : "—"} | ${r.peticiones} | ${r.kb} | ${r.cargaMs} |`;
}

function comparar(actual, anterior) {
  const clave = (r) => `${r.ruta}|${r.vista}`;
  const previos = new Map(anterior.map((r) => [clave(r), r]));
  const lineas = [];
  for (const r of actual) {
    const p = previos.get(clave(r));
    if (!p) continue;
    const cambios = [];
    const nAxe = (x) => x.axe.reduce((t, v) => t + v.nodos, 0);
    for (const [nombre, a, b] of [
      ["nodos axe", nAxe(p), nAxe(r)],
      ["errores consola", p.errores.length, r.errores.length],
      ["desborde px", p.desborde, r.desborde],
      ["zonas táctiles pequeñas", p.pequenas.length, r.pequenas.length],
      ["KB", p.kb, r.kb],
      ["peticiones", p.peticiones, r.peticiones],
    ]) {
      if (a !== b) cambios.push(`${nombre} ${a} → ${b}`);
    }
    if (cambios.length) lineas.push(`- #/${r.ruta} (${r.vista}): ${cambios.join(", ")}`);
  }
  return lineas.length ? lineas : ["- Sin cambios medibles."];
}

function informe(resultados, commit, base, lineasComparacion) {
  const detalle = [];
  for (const r of resultados) {
    const partes = [];
    for (const v of r.axe) partes.push(`  - axe \`${v.id}\` (${v.impacto}, ${v.nodos} nodos): ${v.ayuda}`);
    for (const e of r.errores) partes.push(`  - consola: ${e}`);
    if (r.desborde) partes.push(`  - se desborda ${r.desborde} px; elementos que se salen: ${r.culpables.join(", ")}`);
    for (const p of r.pequenas.slice(0, 5)) partes.push(`  - zona táctil pequeña: ${p}`);
    if (partes.length) detalle.push(`- **#/${r.ruta} · ${r.vista}** (\`${r.captura}\`)`, ...partes);
  }
  const sinBackend = resultados.reduce((t, r) => t + r.sinBackend, 0);
  return [
    `# Inspección de la web — ${new Date().toISOString().slice(0, 16).replace("T", " ")}`,
    "",
    `Commit: \`${commit}\` · Servidor: ${base}`,
    "",
    "| Ruta | Vista | axe (nodos) | Errores consola | Desborde | Zonas táctiles a revisar | Peticiones | KB | load (ms) |",
    "|---|---|---|---|---|---|---|---|---|",
    ...resultados.map(fila),
    "",
    "## Detalle",
    "",
    ...(detalle.length ? detalle : ["Nada que señalar."]),
    "",
    ...(lineasComparacion ? ["## Comparación con la inspección anterior", "", ...lineasComparacion, ""] : []),
    "## Notas",
    "",
    `- Fallos de red hacia el backend ignorados: ${sinBackend}${sinBackend ? " (el backend no estaba arrancado; las vistas con sesión no se ven completas)" : ""}.`,
    "- Los tiempos son de un servidor local sin caché: sirven para comparar antes y después, no como dato de la web publicada.",
    "- «Zonas táctiles a revisar» son controles de menos de 24 × 24 px en el móvil. WCAG 2.5.8 los admite si tienen espacio libre alrededor: son candidatos, no fallos seguros.",
    "- Pyodide se descarga al ejecutar código, no en estas vistas, así que no cuenta en los KB.",
    "",
  ].join("\n");
}

async function main() {
  const args = leerArgumentos(process.argv.slice(2));
  const salida = args.salida ? resolve(args.salida) : mkdtempSync(join(tmpdir(), "pld-inspeccion-"));
  mkdirSync(salida, { recursive: true });

  let servidor = null;
  let base = args.url.replace(/\/+$/, "");
  if (base) comprobarLocal(base);
  else ({ servidor, url: base } = await arrancarFrontend(args.puerto));

  const navegador = await chromium.launch();
  const resultados = [];
  try {
    for (const ruta of args.rutas) {
      for (const vista of Object.keys(VISTAS)) {
        process.stdout.write(`· #/${ruta} (${vista})… `);
        const r = await inspeccionarRuta(navegador, base, ruta, vista, salida);
        console.log(`axe ${r.axe.length} · errores ${r.errores.length} · desborde ${r.desborde} px`);
        resultados.push(r);
      }
    }
  } finally {
    await navegador.close();
    servidor?.kill();
  }

  const commit = await new Promise((ok) => {
    const git = spawn("git", ["rev-parse", "--short", "HEAD"], { cwd: RAIZ });
    let texto = "";
    git.stdout.on("data", (d) => (texto += d));
    git.on("close", () => ok(texto.trim() || "desconocido"));
    git.on("error", () => ok("desconocido"));
  });
  let lineasComparacion = null;
  if (args.comparar) {
    const anterior = JSON.parse(readFileSync(join(resolve(args.comparar), "resultados.json"), "utf8"));
    lineasComparacion = comparar(resultados, anterior);
  }
  writeFileSync(join(salida, "resultados.json"), JSON.stringify(resultados, null, 2));
  writeFileSync(join(salida, "informe.md"), informe(resultados, commit, base, lineasComparacion));
  console.log(`\nInforme y capturas en: ${salida}`);
  if (lineasComparacion) console.log(lineasComparacion.join("\n"));
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
