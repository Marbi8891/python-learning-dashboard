import assert from "node:assert/strict";
import { test } from "node:test";
import { cleanGame } from "../../frontend/js/game-data.js";
import { cleanLearning } from "../../frontend/js/learn/mastery.js";
import { MAX_BYTES, ProgressFileError, VERSION, buildProgressFile, describeParts, parseProgressFile } from "../../frontend/js/progress-file.js";

const COURSES = ["sql", "java"];
const NOW = new Date("2026-10-21T10:00:00Z");
const sample = () =>
  buildProgressFile(
    {
      completed: new Set(["variables", "bucles"]),
      learn: cleanLearning({ ex: { "var-1": { h: [true], last: "2026-10-20T10:00:00Z", n: 1 } } }),
      pcap: { answers: { q1: [false, true] }, srs: {}, exams: [] },
      game: cleanGame({ badges: ["hola-mundo"], days: ["2026-10-20"] }),
      courses: { sql: { answers: { s1: [true] } } },
    },
    NOW,
  );

test("exporta un archivo versionado que se vuelve a importar igual", () => {
  const file = sample();
  assert.equal(file.format, "pld-progress");
  assert.equal(file.version, VERSION);
  assert.equal(file.exportedAt, "2026-10-21T10:00:00.000Z");
  const parts = parseProgressFile(JSON.stringify(file), COURSES);
  assert.deepEqual(parts.completed, ["variables", "bucles"]);
  assert.deepEqual(parts.learn.ex["var-1"], { h: [true], last: "2026-10-20T10:00:00Z", n: 1 });
  assert.deepEqual(parts.pcap.answers, { q1: [false, true] });
  assert.deepEqual(parts.game.badges, ["hola-mundo"]);
  assert.deepEqual(Object.keys(parts.courses), ["sql"]);
  assert.match(describeParts(parts), /2 lecciones completadas.*1 ejercicios.*1 preguntas del PCAP.*1 cursos de DAW.*logros/);
});

test("rechaza con un mensaje claro lo que no es una copia válida", () => {
  const rejects = (text, pattern) => assert.throws(() => parseProgressFile(text, COURSES), (e) => e instanceof ProgressFileError && pattern.test(e.message));
  rejects("", /vacío/);
  rejects("{no es json", /JSON válido/);
  rejects("[1, 2]", /no es una copia/);
  rejects(JSON.stringify({ format: "otra-app", version: 1, data: {} }), /no es una copia/);
  rejects(JSON.stringify({ format: "pld-progress", version: "1", data: {} }), /versión del archivo no es válida/);
  rejects(JSON.stringify({ format: "pld-progress", version: VERSION + 1, data: {} }), /versión más nueva/);
  rejects(JSON.stringify({ format: "pld-progress", version: 1, data: { nada: 1 } }), /no contiene progreso/);
  rejects(" ".repeat(MAX_BYTES) + "{}", /demasiado grande/);
});

test("limpia los datos manipulados: nada de HTML, ids raros ni cursos desconocidos", () => {
  const text = JSON.stringify({
    format: "pld-progress",
    version: 1,
    data: {
      completed: ["variables", "<img src=x onerror=alert(1)>", 42, "variables"],
      game: { badges: ["<script>"], quiz: { variables: 99 } },
      learn: { ex: { "<b>": { h: [true], last: "2026-10-20T10:00:00Z", n: 1 } } },
      courses: { sql: { answers: { s1: ["sí", true] } }, malicioso: { answers: {} } },
      __proto__: { polluted: true },
    },
  });
  const parts = parseProgressFile(text, COURSES);
  assert.deepEqual(parts.completed, ["variables"]);
  assert.deepEqual(parts.game.badges, []);
  assert.deepEqual(parts.game.quiz, {});
  assert.deepEqual(parts.learn.ex, {});
  assert.deepEqual(parts.courses, { sql: { answers: { s1: [true] } } });
  assert.equal({}.polluted, undefined);
});
