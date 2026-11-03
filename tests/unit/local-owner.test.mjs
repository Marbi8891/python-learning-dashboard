// AUTH-02: el progreso que queda en un navegador compartido no se sube a otra cuenta, ni se borra.
import assert from "node:assert/strict";
import { test } from "node:test";
import { claimLocalProgress, isProgressKey, OWNER_KEY, STASH_PREFIX } from "../../frontend/js/local-owner.js";

/** localStorage en memoria con la misma interfaz. */
function memoryStorage(initial = {}) {
  const map = new Map(Object.entries(initial));
  return {
    get length() {
      return map.size;
    },
    key: (i) => [...map.keys()][i] ?? null,
    getItem: (k) => (map.has(k) ? map.get(k) : null),
    setItem: (k, v) => map.set(k, String(v)),
    removeItem: (k) => map.delete(k),
    dump: () => Object.fromEntries(map),
  };
}

test("solo cuenta como progreso lo que es de un alumno", () => {
  assert.ok(isProgressKey("pld:pcap"));
  assert.ok(isProgressKey("pld:course:sql"));
  assert.ok(isProgressKey("pld:draft:variables"));
  for (const key of ["pld:prefs", "pld:session", OWNER_KEY, "pld:flash", `${STASH_PREFIX}7`, "otra:cosa"]) {
    assert.equal(isProgressKey(key), false, key);
  }
});

test("progreso sin dueño (sin cuenta o de antes): se queda para fusionarlo con la cuenta que entra", () => {
  const storage = memoryStorage({ "pld:pcap": '{"known":["a"]}' });
  assert.deepEqual(claimLocalProgress(1, storage), { swapped: false });
  assert.equal(storage.getItem("pld:pcap"), '{"known":["a"]}');
  assert.equal(storage.getItem(OWNER_KEY), "1");
});

test("mismo dueño: no se toca nada", () => {
  const storage = memoryStorage({ [OWNER_KEY]: "1", "pld:learn": "{}" });
  assert.deepEqual(claimLocalProgress(1, storage), { swapped: false });
  assert.equal(storage.getItem("pld:learn"), "{}");
});

test("progreso de otra cuenta: se aparta sin mezclarlo ni borrarlo, y vuelve cuando esa cuenta entra", () => {
  const storage = memoryStorage({ [OWNER_KEY]: "1", "pld:pcap": "A", "pld:course:sql": "A-sql", "pld:prefs": "p" });

  // Entra la cuenta 2 en el mismo navegador
  assert.deepEqual(claimLocalProgress(2, storage), { swapped: true });
  assert.equal(storage.getItem("pld:pcap"), null, "la cuenta 2 no ve ni sube lo de la 1");
  assert.equal(storage.getItem("pld:prefs"), "p", "las preferencias de aspecto se quedan");
  assert.deepEqual(JSON.parse(storage.getItem(`${STASH_PREFIX}1`)), { "pld:pcap": "A", "pld:course:sql": "A-sql" });
  assert.equal(storage.getItem(OWNER_KEY), "2");

  // La cuenta 2 hace algo; después vuelve la cuenta 1
  storage.setItem("pld:pcap", "B");
  assert.deepEqual(claimLocalProgress(1, storage), { swapped: true });
  assert.equal(storage.getItem("pld:pcap"), "A");
  assert.equal(storage.getItem("pld:course:sql"), "A-sql");
  assert.equal(storage.getItem(`${STASH_PREFIX}1`), null);
  assert.deepEqual(JSON.parse(storage.getItem(`${STASH_PREFIX}2`)), { "pld:pcap": "B" });
});

test("lo apartado no pisa progreso sin cuenta en la misma clave, y no provoca recargas en bucle", () => {
  const storage = memoryStorage({ [`${STASH_PREFIX}1`]: JSON.stringify({ "pld:pcap": "A", "pld:learn": "A-learn" }), "pld:pcap": "anon" });
  assert.deepEqual(claimLocalProgress(1, storage), { swapped: true });
  assert.equal(storage.getItem("pld:pcap"), "anon");
  assert.equal(storage.getItem("pld:learn"), "A-learn");
  assert.deepEqual(JSON.parse(storage.getItem(`${STASH_PREFIX}1`)), { "pld:pcap": "A" });
  // Al volver a cargar la página con la misma sesión no cambia nada más: no se recarga otra vez
  assert.deepEqual(claimLocalProgress(1, storage), { swapped: false });
});

test("una cuenta sin progreso en el navegador simplemente pasa a ser la dueña", () => {
  const storage = memoryStorage({ [OWNER_KEY]: "1", "pld:prefs": "p" });
  assert.deepEqual(claimLocalProgress(2, storage), { swapped: false });
  assert.equal(storage.getItem(OWNER_KEY), "2");
});
