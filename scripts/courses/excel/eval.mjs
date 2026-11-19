// Puente entre el generador de cursos (Python) y el motor de fórmulas (JavaScript).
//
// Lee de la entrada estándar una lista de ejercicios `formula` y `formula-result` en JSON y escribe en
// la salida estándar { "<id>": ["problema", ...] }. Una lista vacía significa que el ejercicio está bien:
// la solución pasa sus comprobaciones, cada error frecuente falla alguna y los resultados escritos por
// el autor coinciden con los que calcula el motor. Es el mismo código que corrige en la web.
//
// Uso (lo llama scripts/courses/course_builder.py):  node scripts/courses/excel/eval.mjs < ejercicios.json

import { verifyQuestion } from "../../../frontend/js/excel/checks.js";
import { ENGINE_VERSION } from "../../../frontend/js/excel/formula/index.js";

const chunks = [];
for await (const chunk of process.stdin) chunks.push(chunk);
const questions = JSON.parse(Buffer.concat(chunks).toString("utf8"));

const report = { engine: ENGINE_VERSION, problems: {} };
for (const question of questions) {
  try {
    report.problems[question.id] = verifyQuestion(question);
  } catch (error) {
    report.problems[question.id] = [`${question.id}: ${error.message}`];
  }
}
process.stdout.write(JSON.stringify(report));
