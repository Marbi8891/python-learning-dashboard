// Catálogo de cursos por familias (Excel profesional, fase P0): los cursos de DAW no cambian y las
// academias se sincronizan como un curso más sin aparecer entre los de DAW.
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import { ACADEMY_COURSES, COURSE_FAMILIES, DAW_COURSES, familyOf, SYNCED_COURSES } from "../../frontend/js/catalog.js";

// Copia literal de DAW_COURSES tal como estaba en main (3b2dd8b) antes de crear el catálogo
const DAW_BEFORE = [
  {
    "id": "programacion",
    "module": "0485",
    "title": "Programación",
    "subtitle": "Módulo 0485 en Python · UT1-UT9",
    "lang": "python",
    "structure": "Sigue el orden y los contenidos de las UT1-UT9 del curso «DAW-Programacion» de César San Juan Pastor (IES Arcipreste de Hita, licencia CC BY-NC), sin copiar su texto."
  },
  {
    "id": "sql",
    "module": "0484",
    "title": "Bases de datos",
    "subtitle": "Módulo 0484 · SQL · UD1-UD3 del centro",
    "lang": "sql",
    "structure": "Sigue el orden de las UD1-UD3 del temario del centro, con un bloque de ampliación propio."
  },
  {
    "id": "entornos",
    "module": "0487",
    "title": "Entornos de desarrollo",
    "subtitle": "Módulo 0487 · UD1 del centro",
    "lang": "python",
    "structure": "Sigue el orden de la UD1 «Desarrollo de software» del temario del centro."
  },
  {
    "id": "marcas",
    "module": "0373",
    "title": "Lenguajes de marcas",
    "subtitle": "Módulo 0373 · XML, HTML, JSON y XPath",
    "lang": "python",
    "structure": "Las unidades se organizan por los resultados de aprendizaje del Real Decreto 405/2023. Los objetivos de cada lección los resumen con palabras propias y citan el RA y sus criterios."
  },
  {
    "id": "js",
    "module": "0612",
    "title": "JavaScript",
    "subtitle": "Entorno cliente",
    "lang": "javascript",
    "structure": "Selección propia de la plataforma para el módulo 0612; no sigue ningún temario."
  },
  {
    "id": "java",
    "module": "0485",
    "title": "Java",
    "subtitle": "Para más adelante: Java desde cero",
    "lang": "java",
    "structure": "Curso propio de la plataforma para practicar Java; no sigue ningún temario."
  }
];

test("DAW_COURSES es idéntico al de antes: mismos cursos, orden y campos", () => {
  assert.deepEqual(DAW_COURSES, DAW_BEFORE);
  for (const course of DAW_COURSES) assert.equal("family" in course, false, `${course.id} no cambia de forma`);
});

test("course-store.js sigue exportando DAW_COURSES, ahora desde el catálogo", () => {
  const source = readFileSync(new URL("../../frontend/js/course-store.js", import.meta.url), "utf8");
  assert.match(source, /export \{ DAW_COURSES \} from "\.\/catalog\.js";/);
  assert.doesNotMatch(source, /export const DAW_COURSES/);
  // La sincronización recorre todos los cursos con documento, no solo los de DAW
  assert.match(source, /for \(const \{ id \} of SYNCED_COURSES\)/);
});

test("Excel profesional es de la familia academia y no está entre los cursos de DAW", () => {
  assert.deepEqual(ACADEMY_COURSES.map((c) => c.id), ["excel"]);
  const [excel] = ACADEMY_COURSES;
  assert.equal(excel.title, "Excel profesional");
  assert.equal(excel.route, "#/academia/excel");
  assert.equal(excel.status, "active"); // fase P2: con contenido y en el menú
  assert.equal("module" in excel, false, "una academia no tiene módulo oficial de DAW");
  assert.equal(DAW_COURSES.some((c) => c.id === "excel"), false);
  assert.equal(familyOf("excel"), "academia");
  assert.equal(familyOf("sql"), "daw");
  assert.equal(familyOf("pcap"), null);
  assert.ok(COURSE_FAMILIES[excel.family]);
});

test("SYNCED_COURSES: primero DAW y después las academias, con ids únicos y válidos para la API", () => {
  assert.deepEqual(SYNCED_COURSES, [...DAW_COURSES, ...ACADEMY_COURSES]);
  const ids = SYNCED_COURSES.map((c) => c.id);
  assert.equal(new Set(ids).size, ids.length);
  // course_states.course es String(20) y la ruta acepta como mucho 20 caracteres
  for (const id of ids) assert.match(id, /^[a-z][a-z0-9-]{1,19}$/);
});
