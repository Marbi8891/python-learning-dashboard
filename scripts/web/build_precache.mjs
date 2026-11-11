// Lista de archivos que el service worker guarda al instalarse (frontend/precache.js), para que la web
// funcione sin conexión después de la primera visita aunque no se haya abierto cada página (AUD-008).
//
// Uso:  node scripts/web/build_precache.mjs           (genera frontend/precache.js)
//       node scripts/web/build_precache.mjs --check   (falla si no está al día; también lo prueba
//                                                      tests/unit/precache.test.mjs)
import { readdirSync, readFileSync, statSync, writeFileSync } from "node:fs";
import { join, relative } from "node:path";
import { fileURLToPath } from "node:url";

const FRONTEND = fileURLToPath(new URL("../../frontend/", import.meta.url));
export const OUT = join(FRONTEND, "precache.js");

const FILES = ["index.html", "404.html", "aviso-legal.html", "privacidad.html", "config.js", "manifest.webmanifest", "favicon.svg", "i18n/en.json", "py/runner.py"];
const FOLDERS = [
  ["js", /\.js$/],
  ["css", /\.css$/],
  ["fonts", /\.woff2$/],
  ["vendor", /\.(js|css)$/],
  ["icons", /^icon-.*\.png$/],
  ["data", /\.json$/],
];

function walk(folder, pattern) {
  const out = [];
  for (const name of readdirSync(join(FRONTEND, folder)).sort()) {
    const path = join(folder, name);
    if (statSync(join(FRONTEND, path)).isDirectory()) out.push(...walk(path, pattern));
    else if (pattern.test(name)) out.push(relative(FRONTEND, join(FRONTEND, path)).split("\\").join("/"));
  }
  return out;
}

export function precacheList() {
  return ["./", ...FILES, ...FOLDERS.flatMap(([folder, pattern]) => walk(folder, pattern))];
}

export function precacheSource(list = precacheList()) {
  return `/* Generado por scripts/web/build_precache.mjs: no editar a mano.
   Archivos que sw.js guarda al instalarse para que la web funcione sin conexión (AUD-008). */
self.PLD_PRECACHE = ${JSON.stringify(list, null, 1)};
`;
}

if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) {
  const source = precacheSource();
  if (process.argv.includes("--check")) {
    let current = "";
    try {
      current = readFileSync(OUT, "utf8");
    } catch {
      // no existe
    }
    if (current !== source) {
      console.error("frontend/precache.js no está al día: ejecuta node scripts/web/build_precache.mjs");
      process.exit(1);
    }
    console.log(`precache.js al día: ${precacheList().length} archivos`);
  } else {
    writeFileSync(OUT, source);
    console.log(`Escrito frontend/precache.js: ${precacheList().length} archivos`);
  }
}
