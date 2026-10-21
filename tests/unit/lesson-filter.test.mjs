import assert from "node:assert/strict";
import { test } from "node:test";
import { matchesQuery, normalize } from "../../frontend/js/lesson-filter.js";

test("busca sin distinguir mayúsculas ni tildes", () => {
  assert.equal(normalize("  FUNCIÓN "), "funcion");
  assert.ok(matchesQuery("funcion", "Funciones y parámetros"));
  assert.ok(matchesQuery("PARÁMETROS", "Funciones y parametros"));
});

test("todas las palabras deben aparecer, en cualquier campo y orden", () => {
  assert.ok(matchesQuery("bucle while", "Bucles", "while-loops"));
  assert.ok(matchesQuery("while bucle", "Bucles", "while-loops"));
  assert.equal(matchesQuery("bucle for", "Bucles", "while-loops"), false);
  assert.ok(matchesQuery("", "Cualquier lección"), "sin búsqueda, todo coincide");
});
