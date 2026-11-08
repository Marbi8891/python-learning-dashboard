#!/usr/bin/env node
// Validación estática del frontend (HTML + CSS + ES modules), sin navegador y sin red.
//
// Comprueba, sin ejecutar el código de la web:
//   - sintaxis de cada archivo JavaScript (módulo o script clásico, según cómo se carga)
//   - que cada import apunta a un archivo que existe y que exporta los nombres que se importan
//     (enlace real de ES modules con node:vm, el mismo algoritmo que el navegador)
//   - import() dinámicos y Web Workers (new Worker(new URL(...), { type: "module" }))
//   - referencias de los HTML (src, href), de los CSS (url(), @import) y del manifiesto
//   - rutas de archivos escritas en el JavaScript ("data/lessons.json", "../py/runner.py", ...)
//   - scripts inline y atributos on* en los HTML (la CSP los bloquearía en producción)
//   - que cada JSON de frontend/ se puede leer
//
// Uso:  node --experimental-vm-modules scripts/qa/frontend_static.mjs [--root frontend] [--json salida.json]
// Sale con código 1 si hay errores. Las advertencias no hacen fallar.

import { spawnSync } from "node:child_process";
import { existsSync, readdirSync, readFileSync, statSync, writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import vm from "node:vm";

const REPO = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..");
const EXTERNAL = /^(?:[a-z][a-z0-9+.-]*:|\/\/|#)/i; // http:, https:, data:, mailto:, //cdn, #ancla
const RESOURCE_EXT = /\.(?:json|js|mjs|css|svg|png|jpg|jpeg|webp|ico|woff2?|py|html|webmanifest|txt|xml)$/i;

function walk(dir, filter) {
  const out = [];
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isSymbolicLink()) continue; // enlaces temporales (frontend/_pyo) no son de la web
    if (entry.isDirectory()) out.push(...walk(full, filter));
    else if (filter(full)) out.push(full);
  }
  return out.sort();
}

const lineOf = (source, index) => (index < 0 ? 1 : source.slice(0, index).split("\n").length);
const stripQuery = (ref) => ref.split(/[?#]/)[0];

export async function checkFrontend(root = path.join(REPO, "frontend")) {
  root = path.resolve(root);
  const issues = [];
  const rel = (file) => path.relative(REPO, file).split(path.sep).join("/");
  const add = (severity, check, file, line, message, cause, fix) =>
    issues.push({ severity, check, file: rel(file), line, message, cause, fix });
  const error = (...args) => add("error", ...args);
  const warning = (...args) => add("warning", ...args);
  const stats = { js: 0, modules: 0, classic: 0, html: 0, css: 0, json: 0, references: 0, imports: 0 };

  const read = (file) => readFileSync(file, "utf8");
  const exists = (file) => existsSync(file) && statSync(file).isFile();
  // En GitHub Pages la web vive en /<repositorio>/: lo dice el <link rel="canonical"> de index.html
  const indexHtml = path.join(root, "index.html");
  const canonical = existsSync(indexHtml)
    ? /<link\s+rel="canonical"\s+href="([^"]+)"/.exec(read(indexHtml))?.[1]
    : undefined;
  const basePath = canonical ? new URL(canonical).pathname : "/";
  /** Ruta de un recurso de la web en disco ("/<repo>/css/x.css", "css/x.css", "../x.css"). */
  const resolveRef = (ref, fromDir) => {
    const clean = decodeURI(stripQuery(ref));
    if (!clean.startsWith("/")) return path.resolve(fromDir, clean);
    const inSite = clean.startsWith(basePath) ? clean.slice(basePath.length) : clean.slice(1);
    return path.resolve(root, inSite);
  };
  /** Existe como archivo, o es una carpeta con index.html (enlaces a "/<repo>/"). */
  const existsRef = (target) => exists(target) || exists(path.join(target, "index.html"));

  const moduleRoots = new Set(); // archivos que el navegador carga como módulo
  const classicScripts = new Set(); // <script src> sin type=module, service worker, importScripts

  // ---------- HTML ----------
  const htmlFiles = walk(root, (f) => f.endsWith(".html"));
  for (const file of htmlFiles) {
    stats.html++;
    const html = read(file);
    const tagRe = /<([a-zA-Z][a-zA-Z0-9-]*)\b([^>]*)>/g;
    for (let m; (m = tagRe.exec(html)); ) {
      const [, tag, attrs] = m;
      const line = lineOf(html, m.index);
      if (/\son[a-z]+\s*=/i.test(attrs)) {
        error(
          "html-inline-handler",
          file,
          line,
          `Atributo on* en <${tag}>`,
          "La CSP (script-src sin 'unsafe-inline') bloquea los manejadores inline: el botón no haría nada en producción.",
          "Quita el atributo y registra el evento con addEventListener en un módulo de frontend/js/.",
        );
      }
      for (const a of attrs.matchAll(/\s(src|href)\s*=\s*("([^"]*)"|'([^']*)')/gi)) {
        const ref = a[3] ?? a[4];
        if (!ref || EXTERNAL.test(ref)) continue;
        stats.references++;
        if (!stripQuery(ref)) continue;
        const target = resolveRef(ref, path.dirname(file));
        if (!existsRef(target)) {
          error(
            "html-missing-reference",
            file,
            line,
            `<${tag} ${a[1]}="${ref}">: el archivo no existe`,
            "Se ha borrado o renombrado el archivo, o la ruta tiene una errata.",
            `Crea ${rel(target)} o corrige la ruta en ${rel(file)}.`,
          );
          continue;
        }
        if (tag.toLowerCase() === "script") {
          (/\btype\s*=\s*["']module["']/i.test(attrs) ? moduleRoots : classicScripts).add(target);
        }
      }
    }
    const inlineRe = /<script\b(?![^>]*\bsrc\s*=)([^>]*)>([\s\S]*?)<\/script>/gi;
    for (let m; (m = inlineRe.exec(html)); ) {
      if (/type\s*=\s*["']application\/(ld\+)?json["']/i.test(m[1]) || !m[2].trim()) continue;
      error(
        "html-inline-script",
        file,
        lineOf(html, m.index),
        "Script inline",
        "La CSP de la web solo permite scripts de archivos propios ('self'): este código no se ejecutaría.",
        "Mueve el código a un archivo de frontend/js/ y cárgalo con <script src>.",
      );
    }
  }

  // ---------- CSS ----------
  for (const file of walk(root, (f) => f.endsWith(".css"))) {
    stats.css++;
    const css = read(file).replace(/\/\*[\s\S]*?\*\//g, (c) => c.replace(/[^\n]/g, " "));
    const refRe = /url\(\s*(?:"([^"]*)"|'([^']*)'|([^)\s]*))\s*\)|@import\s+["']([^"']+)["']/g;
    for (let m; (m = refRe.exec(css)); ) {
      const ref = m[1] ?? m[2] ?? m[3] ?? m[4];
      if (!ref || EXTERNAL.test(ref)) continue;
      stats.references++;
      const target = resolveRef(ref, path.dirname(file));
      if (!exists(target)) {
        error(
          "css-missing-reference",
          file,
          lineOf(css, m.index),
          `url(${ref}): el archivo no existe`,
          "Fuente, imagen o hoja de estilos borrada, renombrada o con la ruta mal escrita.",
          `Recupera ${rel(target)} o corrige la ruta (es relativa al CSS, no a la página).`,
        );
      }
    }
  }

  // ---------- JSON y manifiesto ----------
  for (const file of walk(root, (f) => /\.(json|webmanifest)$/.test(f))) {
    stats.json++;
    let data;
    try {
      data = JSON.parse(read(file));
    } catch (e) {
      error(
        "json-invalid",
        file,
        Number(/line (\d+)/.exec(e.message)?.[1] ?? 1),
        `JSON no válido: ${e.message}`,
        "Un JSON roto hace fallar la carga de la página o del curso que lo usa.",
        "Si es un JSON generado, regenéralo con su script (CLAUDE.md); si no, corrige la sintaxis.",
      );
      continue;
    }
    if (file.endsWith(".webmanifest")) {
      const refs = [data.start_url, data.scope, ...(data.icons ?? []).map((i) => i.src)];
      for (const ref of refs) {
        if (!ref || EXTERNAL.test(ref)) continue;
        stats.references++;
        const target = resolveRef(ref, path.dirname(file));
        if (!existsRef(target)) {
          error(
            "manifest-missing-reference",
            file,
            1,
            `${ref}: el archivo no existe`,
            "El manifiesto de la PWA apunta a un icono o una página que no está.",
            `Crea ${rel(target)} o corrige manifest.webmanifest.`,
          );
        }
      }
    }
  }

  // ---------- JavaScript: grafo de módulos ----------
  const jsFiles = walk(root, (f) => /\.(m?js)$/.test(f) && !f.includes(`${path.sep}vendor${path.sep}`));
  const sources = new Map(jsFiles.map((f) => [f, read(f)]));
  const sourceOf = (f) => sources.get(f) ?? read(f);

  // Service worker y lo que importa con importScripts: scripts clásicos
  for (const [file, src] of sources) {
    for (const m of src.matchAll(/serviceWorker\.register\(\s*["']([^"']+)["']/g)) {
      const target = path.resolve(root, stripQuery(m[1]));
      if (exists(target)) classicScripts.add(target);
    }
    for (const m of src.matchAll(/importScripts\(\s*["']([^"']+)["']/g)) {
      const target = path.resolve(path.dirname(file), stripQuery(m[1]));
      if (exists(target)) classicScripts.add(target);
      else
        error(
          "js-missing-import",
          file,
          lineOf(src, m.index),
          `importScripts("${m[1]}"): el archivo no existe`,
          "El service worker no se instalaría y la web dejaría de funcionar sin conexión.",
          `Crea ${rel(target)} o corrige la ruta.`,
        );
    }
  }

  // Workers de tipo módulo: new Worker(new URL("./x.js", import.meta.url), { type: "module" })
  const workerRe = /new\s+Worker\(\s*new\s+URL\(\s*["']([^"']+)["']\s*,\s*import\.meta\.url\s*\)\s*(?:,\s*\{([^}]*)\})?/g;
  const workers = [];
  for (const [file, src] of sources) {
    for (const m of src.matchAll(workerRe)) {
      const target = path.resolve(path.dirname(file), m[1]);
      const isModule = /type\s*:\s*["']module["']/.test(m[2] ?? "");
      if (!exists(target)) {
        error(
          "worker-missing",
          file,
          lineOf(src, m.index),
          `new Worker("${m[1]}"): el archivo no existe`,
          "El Web Worker no arrancaría (en esta web, la consola de Python dejaría de funcionar).",
          `Crea ${rel(target)} o corrige la ruta del Worker.`,
        );
        continue;
      }
      workers.push({ file: target, from: file, isModule });
      (isModule ? moduleRoots : classicScripts).add(target);
    }
  }

  // Sintaxis
  const syntaxOk = new Set();
  const checkSyntax = (file, asModule) => {
    try {
      if (asModule) new vm.SourceTextModule(sourceOf(file), { identifier: pathToFileURL(file).href });
      else new vm.Script(sourceOf(file), { filename: file });
      syntaxOk.add(file);
      return true;
    } catch (e) {
      if (!(e instanceof SyntaxError)) throw e;
      // node --check da la línea exacta del error
      const out = spawnSync(process.execPath, ["--check", file], { encoding: "utf8" });
      const line = Number(new RegExp(`${path.basename(file).replace(/\./g, "\\.")}:(\\d+)`).exec(out.stderr)?.[1] ?? 1);
      error(
        "js-syntax",
        file,
        line,
        `Error de sintaxis: ${e.message}`,
        "El navegador no carga el archivo y todo lo que depende de él deja de funcionar.",
        `Revisa ${rel(file)}:${line} (paréntesis, llaves o comillas sin cerrar, coma de más...).`,
      );
      return false;
    }
  };

  // Enlace de módulos: resuelve cada import y comprueba que el nombre importado se exporta
  const modules = new Map();
  const getModule = (file) => {
    if (!modules.has(file)) {
      modules.set(file, new vm.SourceTextModule(sourceOf(file), { identifier: pathToFileURL(file).href }));
    }
    return modules.get(file);
  };
  const visited = new Set();
  const queue = [...moduleRoots];
  const failedResolution = new Set();
  while (queue.length) {
    const file = queue.shift();
    if (visited.has(file)) continue;
    visited.add(file);
    stats.modules++;
    if (!checkSyntax(file, true)) continue;
    const src = sourceOf(file);
    const mod = getModule(file);
    const specs = [...mod.dependencySpecifiers];
    // import("./x.js") con ruta literal: también se comprueba (no se enlaza: se carga al usarse)
    for (const m of src.matchAll(/\bimport\(\s*["']([^"']+)["']\s*\)/g)) specs.push(m[1]);
    for (const spec of specs) {
      stats.imports++;
      const at = lineOf(src, src.indexOf(`"${spec}"`) >= 0 ? src.indexOf(`"${spec}"`) : src.indexOf(`'${spec}'`));
      if (EXTERNAL.test(spec)) continue;
      if (!spec.startsWith(".") && !spec.startsWith("/")) {
        error(
          "js-bare-specifier",
          file,
          at,
          `import "${spec}": especificador sin ruta`,
          "La web no usa bundler ni import map: el navegador no sabe resolver nombres de paquete.",
          `Usa una ruta relativa ("./${spec}.js") o un archivo de frontend/vendor/.`,
        );
        failedResolution.add(file);
        continue;
      }
      const resolved = spec.startsWith("/") ? path.join(root, spec) : path.resolve(path.dirname(file), spec);
      if (!exists(resolved)) {
        error(
          "js-missing-import",
          file,
          at,
          `import "${spec}": el módulo no existe (${rel(resolved)})`,
          "Archivo borrado o renombrado, o falta la extensión .js (el navegador no la añade).",
          `Crea ${rel(resolved)} o corrige el import en ${rel(file)}.`,
        );
        failedResolution.add(file);
        continue;
      }
      queue.push(resolved);
    }
  }

  // Enlazar solo los grafos sin rutas rotas (si no, el error ya está anotado)
  const linkErrors = new Set();
  for (const file of visited) {
    if (!syntaxOk.has(file) || failedResolution.has(file)) continue;
    const mod = getModule(file);
    if (mod.status !== "unlinked") continue;
    const linker = (spec, referencing) => {
      const from = fileURLToPath(referencing.identifier);
      const resolved = spec.startsWith("/") ? path.join(root, spec) : path.resolve(path.dirname(from), spec);
      if (failedResolution.has(resolved) || !syntaxOk.has(resolved)) {
        throw Object.assign(new Error("dependencia rota"), { skip: true });
      }
      return getModule(resolved);
    };
    try {
      await mod.link(linker);
    } catch (e) {
      if (e.skip) continue;
      const match = /module '([^']+)' does not provide an export named '([^']+)'/.exec(e.message);
      const key = e.message;
      if (linkErrors.has(key)) continue;
      linkErrors.add(key);
      // El error lo da el módulo que importa: buscarlo por el especificador y el nombre
      let culprit = file;
      let line = 1;
      if (match) {
        for (const f of visited) {
          const s = sourceOf(f);
          const idx = s.search(new RegExp(`\\b${match[2]}\\b[^;]*from\\s*["']${match[1].replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}["']`));
          if (idx >= 0) {
            culprit = f;
            line = lineOf(s, idx);
            break;
          }
        }
      }
      error(
        "js-missing-export",
        culprit,
        line,
        match ? `import { ${match[2]} } from "${match[1]}": ese módulo no exporta «${match[2]}»` : e.message,
        "Se ha renombrado o quitado una exportación, o el nombre del import tiene una errata.",
        match ? `Exporta «${match[2]}» en ${match[1]} o corrige el nombre importado.` : "Revisa los imports del módulo.",
      );
    }
  }

  // Scripts clásicos: solo sintaxis
  for (const file of classicScripts) {
    stats.classic++;
    checkSyntax(file, false);
  }

  // Archivos JS que nadie carga: advertencia (puede ser código muerto o un import olvidado)
  for (const file of jsFiles) {
    stats.js++;
    if (visited.has(file) || classicScripts.has(file)) continue;
    const src = sourceOf(file);
    const looksModule = /^\s*(import|export)\s/m.test(src);
    checkSyntax(file, looksModule);
    if (path.basename(file) === "package.json") continue;
    warning(
      "js-unreferenced",
      file,
      1,
      "Ningún HTML, módulo ni Worker carga este archivo",
      "Puede ser código sin usar o un import que se ha perdido.",
      "Si se usa, impórtalo; si no, plantéate quitarlo en un cambio aparte.",
    );
  }

  // Rutas de archivos escritas en el JavaScript: "data/lessons.json", "../py/runner.py"...
  for (const [file, src] of sources) {
    for (const m of src.matchAll(/["'`]((?:\.{1,2}\/)?[A-Za-z0-9_][A-Za-z0-9_./-]*)["'`]/g)) {
      const ref = m[1];
      if (!RESOURCE_EXT.test(ref) || EXTERNAL.test(ref)) continue;
      const before = src.slice(Math.max(0, m.index - 60), m.index);
      const lineText = src.slice(src.lastIndexOf("\n", m.index) + 1, src.indexOf("\n", m.index));
      // Nombre de un archivo descargado (a.download / downloadJson(..., "x.json")), no una ruta
      if (/download/i.test(lineText)) continue;
      // Los imports ya se han comprobado con el grafo de módulos
      if (/\bfrom\s*$|\bimport\s*\(?\s*$/.test(before)) continue;
      // Workers e importScripts: ya tienen su propia comprobación
      if (/(new\s+Worker\(\s*new\s+URL\(|importScripts\()\s*$/.test(before)) continue;
      stats.references++;
      const candidates = [path.resolve(path.dirname(file), ref), path.resolve(root, ref)];
      if (candidates.some(exists)) continue;
      error(
        "js-missing-resource",
        file,
        lineOf(src, m.index),
        `"${ref}": el archivo no existe`,
        "El fetch, la ruta o el import dinámico que lo usa fallaría con un 404.",
        `Crea el archivo o corrige la ruta (se busca relativa a ${rel(file)} y a la raíz de la web).`,
      );
    }
  }

  for (const w of workers) {
    if (!w.isModule && /^\s*(import|export)\s/m.test(sourceOf(w.file))) {
      error(
        "worker-type",
        w.from,
        1,
        `${rel(w.file)} usa import/export pero se crea sin { type: "module" }`,
        "Un Worker clásico no admite import/export: fallaría al arrancar.",
        'Crea el Worker con new Worker(url, { type: "module" }).',
      );
    }
  }

  const errors = issues.filter((i) => i.severity === "error");
  const warnings = issues.filter((i) => i.severity === "warning");
  return { ok: errors.length === 0, errors, warnings, stats };
}

function printReport(result) {
  const { stats } = result;
  console.log(
    `Frontend: ${stats.html} HTML, ${stats.css} CSS, ${stats.json} JSON, ${stats.js} JS ` +
      `(${stats.modules} módulos, ${stats.classic} clásicos), ${stats.imports} imports y ${stats.references} referencias comprobadas`,
  );
  for (const i of [...result.errors, ...result.warnings]) {
    const tag = i.severity === "error" ? "ERROR" : "AVISO";
    console.log(`\n[${tag}] ${i.check} · ${i.file}:${i.line}\n  ${i.message}\n  Causa probable: ${i.cause}\n  Solución: ${i.fix}`);
  }
  console.log(`\n${result.errors.length} errores, ${result.warnings.length} advertencias`);
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const args = process.argv.slice(2);
  const opt = (name) => (args.includes(name) ? args[args.indexOf(name) + 1] : undefined);
  const result = await checkFrontend(opt("--root"));
  printReport(result);
  if (opt("--json")) writeFileSync(opt("--json"), JSON.stringify(result, null, 2));
  process.exit(result.ok ? 0 : 1);
}
