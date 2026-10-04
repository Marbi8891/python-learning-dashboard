/* Corrección de las respuestas del núcleo educativo (ADR-0031).
   Funciones puras: no tocan el DOM ni el almacenamiento, así que se prueban con `node --test`.
   Los ejercicios de escribir código (`code`) los corrige runner.py en el Worker de Pyodide;
   aquí solo se traduce su resultado (`codeResult`). */

/** Igual que normalize() en scripts/learning/build_learning.py. */
export function normalizeOutput(text) {
  return String(text ?? "")
    .replace(/\r\n/g, "\n")
    .split("\n")
    .map((line) => line.trimEnd())
    .join("\n")
    .replace(/\n+$/, "");
}

/** Código de un hueco: sin espacios y sin el ";" final (mismas reglas que los cursos de DAW, ADR-0017). */
export const normalizeFill = (code) => String(code ?? "").replace(/\s+/g, "").replace(/;$/, "");

/** ¿Hay respuesta suficiente para corregir? Si no, devuelve el aviso para el alumno. */
export function missingAnswer(exercise, answer) {
  switch (exercise.kind) {
    case "choice":
      return Number.isInteger(answer?.choice) ? null : "Elige una respuesta.";
    case "bug":
      return Number.isInteger(answer?.line) ? null : "Señala la línea que tiene el error.";
    case "output":
      return (answer?.text ?? "").trim() ? null : "Escribe lo que crees que muestra el programa.";
    case "fill":
      return (answer?.text ?? "").trim() ? null : "Escribe lo que va en el hueco.";
    case "order":
      return answer?.order?.length === exercise.lines.length ? null : "Coloca todas las líneas.";
    default:
      return null;
  }
}

/**
 * Corrige una respuesta. Devuelve { ok, error }: `error` es el id del error típico que delata
 * la respuesta (o null si no se reconoce ninguno). Para `code`, usa codeResult().
 */
export function grade(exercise, answer) {
  switch (exercise.kind) {
    case "choice": {
      const ok = answer.choice === exercise.answer;
      return { ok, error: ok ? null : (exercise.options[answer.choice]?.error ?? null) };
    }
    case "output": {
      const given = normalizeOutput(answer.text);
      const ok = given === normalizeOutput(exercise.expect);
      const trap = Object.entries(exercise.traps ?? {}).find(([text]) => normalizeOutput(text) === given);
      return { ok, error: ok ? null : (trap?.[1] ?? null) };
    }
    case "fill": {
      const given = normalizeFill(answer.text);
      const ok = exercise.accept.some((accepted) => normalizeFill(accepted) === given);
      const trap = Object.entries(exercise.traps ?? {}).find(([text]) => normalizeFill(text) === given);
      return { ok, error: ok ? null : (trap?.[1] ?? null) };
    }
    case "order": {
      // Se comparan los textos: si dos líneas son iguales, da igual cuál vaya primero
      const ok = answer.order.length === exercise.lines.length && answer.order.every((i, k) => exercise.lines[i] === exercise.lines[k]);
      return { ok, error: ok ? null : (exercise.error ?? null) };
    }
    case "bug": {
      const ok = answer.line === exercise.line;
      return { ok, error: ok ? null : exercise.error };
    }
    default:
      throw new Error(`grade() no corrige ejercicios de tipo ${exercise.kind}: usa codeResult()`);
  }
}

/** Traduce el resultado de runner.check (Pyodide) al mismo formato que grade(). */
export function codeResult(exercise, result) {
  if (result.passed) return { ok: true, error: null };
  const failed = exercise.checks[Number(result.case) - 1];
  return { ok: false, error: failed?.error ?? null };
}

/** Ids de todos los errores típicos que un ejercicio puede detectar. */
export function errorsTested(exercise) {
  const ids = [
    ...(exercise.options ?? []).map((o) => o.error),
    ...Object.values(exercise.traps ?? {}),
    ...(exercise.checks ?? []).map((c) => c.error),
    exercise.error,
  ];
  return [...new Set(ids.filter(Boolean))];
}
