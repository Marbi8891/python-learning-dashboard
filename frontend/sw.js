/* Service worker: la web funciona sin conexión después de la primera visita.
   - Archivos de la web: primero la red (siempre la versión nueva) y, sin conexión o si la red tarda
     más de NETWORK_TIMEOUT_MS, la copia guardada (la red sigue y actualiza la copia, MWG-06).
   - Pyodide (Python en el navegador, en pyodide/v<versión>/ de la propia web): primero la copia guardada;
     sus URL llevan la versión y no cambian.
   - API del backend: nunca se guarda (datos personales y siempre actuales).
   - Al instalarse guarda también toda la web (precache.js, AUD-008): así se puede estudiar sin conexión
     aunque no se hayan abierto antes todas las páginas. */

importScripts("precache.js");

const VERSION = "v13";
const SITE_CACHE = `pld-site-${VERSION}`;
const PYODIDE_CACHE = "pld-pyodide"; // se conserva entre versiones: son ~10 MB inmutables
const NETWORK_TIMEOUT_MS = 4000; // con «lie-fi» (conectado pero sin datos) no se espera para siempre
const SHELL = ["./", "index.html", "config.js", "js/analytics.js", "manifest.webmanifest", "favicon.svg"];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(SITE_CACHE).then(async (cache) => {
      await cache.addAll(SHELL);
      // El resto, uno a uno: si falta un archivo, la instalación sigue (se guardará al pedirlo)
      const rest = (self.PLD_PRECACHE ?? []).filter((file) => !SHELL.includes(file));
      await Promise.all(rest.map((file) => cache.add(file).catch(() => {})));
    }),
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches
      .keys()
      // Solo las cachés propias: el origen marbi8891.github.io lo comparten otros proyectos de Pages
      .then((keys) =>
        Promise.all(
          keys.filter((k) => k.startsWith("pld-site-") && k !== SITE_CACHE).map((k) => caches.delete(k)),
        ),
      )
      // Python ya no se descarga de un CDN (RT-002): se borran las copias de otro origen (~13 MB)
      .then(() => caches.open(PYODIDE_CACHE))
      .then(async (cache) => {
        const old = (await cache.keys()).filter((request) => new URL(request.url).origin !== self.location.origin);
        await Promise.all(old.map((request) => cache.delete(request)));
      })
      .then(() => self.clients.claim()),
  );
});

const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

/** `network` es la descarga ya lanzada (ver el evento fetch): si tarda, se responde con la copia. */
async function networkFirst(request, network) {
  const cache = await caches.open(SITE_CACHE);
  const cached = () =>
    cache.match(request, { ignoreSearch: true }).then(
      (hit) => hit ?? (request.mode === "navigate" ? cache.match("index.html") : undefined),
    );
  try {
    return await Promise.race([network, wait(NETWORK_TIMEOUT_MS).then(async () => (await cached()) ?? network)]);
  } catch (error) {
    const hit = await cached();
    if (hit) return hit;
    if (request.mode === "navigate") return Response.error();
    throw error;
  }
}

/** Descarga y guarda la copia (solo respuestas correctas). */
async function fetchAndStore(request) {
  const response = await fetch(request);
  if (response.ok) {
    const cache = await caches.open(SITE_CACHE);
    await cache.put(request, response.clone());
  }
  return response;
}

async function cacheFirst(request) {
  const cache = await caches.open(PYODIDE_CACHE);
  const cached = await cache.match(request);
  if (cached) return cached;
  const response = await fetch(request);
  if (response.ok) cache.put(request, response.clone());
  return response;
}

self.addEventListener("fetch", (event) => {
  const { request } = event;
  if (request.method !== "GET") return;
  const url = new URL(request.url);
  if (url.pathname.startsWith("/api/") || url.pathname.includes("/api/")) return; // API: sin caché
  // Python (pyodide/v<versión>/) no cambia nunca dentro de una versión: primero la copia (RT-002)
  if (url.pathname.includes("/pyodide/")) {
    event.respondWith(cacheFirst(request));
  } else if (url.origin === self.location.origin) {
    const network = fetchAndStore(request);
    event.waitUntil(network.catch(() => {})); // aunque se responda con la copia, la descarga termina
    event.respondWith(networkFirst(request, network));
  }
});
