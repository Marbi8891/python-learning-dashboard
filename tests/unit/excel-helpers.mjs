// Ayudas de las pruebas del motor de fórmulas.

/** ¿El resultado del motor ({ type, value }) es el valor esperado de un caso de referencia? */
export function matches(result, expected) {
  if (expected !== null && typeof expected === "object") return result.type === "error" && result.value === expected.error;
  if (typeof expected === "number") return result.type === "number" && Math.abs(result.value - expected) <= 1e-9 * Math.max(1, Math.abs(expected));
  if (typeof expected === "boolean") return result.type === "boolean" && result.value === expected;
  return result.type === "text" && result.value === expected;
}
