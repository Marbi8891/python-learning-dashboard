/* Markdown mínimo y seguro: el contenido se escapa siempre, nunca se inyecta HTML. */

const ESCAPES = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" };

export const escapeHtml = (text) => String(text ?? "").replace(/[&<>"']/g, (c) => ESCAPES[c]);

/** Solo enlaces https:// (ni javascript: ni data:), por si un dato llega manipulado. */
export const safeUrl = (url) => (/^https:\/\//i.test(String(url ?? "")) ? escapeHtml(url) : "#");

/** Admite `código`, **negrita** y *cursiva*. */
export function renderInline(text) {
  const codeSpans = [];
  // Aparta el código para que sus * (por ejemplo el operador **) no se lean como formato
  const withPlaceholders = String(text).replace(/`([^`]+)`/g, (_, code) => {
    codeSpans.push(`<code>${escapeHtml(code)}</code>`);
    return `\u0000${codeSpans.length - 1}\u0000`;
  });
  return escapeHtml(withPlaceholders)
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*([^*\s][^*]*?)\*/g, "<em>$1</em>")
    .replace(/\u0000(\d+)\u0000/g, (_, i) => codeSpans[Number(i)]);
}

const tableCells = (line) =>
  line
    .trim()
    .replace(/^\||\|$/g, "")
    .split("|")
    .map((cell) => cell.trim());

function renderTable(rows) {
  const [head, , ...body] = rows.map(tableCells);
  const th = head.map((cell) => `<th scope="col">${renderInline(cell)}</th>`).join("");
  const trs = body.map((row) => `<tr>${row.map((cell) => `<td>${renderInline(cell)}</td>`).join("")}</tr>`).join("");
  return `<div class="table-wrap" tabindex="0"><table class="md-table"><thead><tr>${th}</tr></thead><tbody>${trs}</tbody></table></div>`;
}

/**
 * Párrafos (separados por una línea en blanco), listas con "- " o "1. ",
 * bloques de código entre ``` y tablas con | (cabecera, separador |---| y filas).
 */
export function renderMarkdown(markdown = "") {
  const html = [];
  let paragraph = [];
  let list = null;
  let code = null; // líneas del bloque de código abierto
  let table = null; // filas de la tabla abierta

  const flushParagraph = () => {
    if (paragraph.length) html.push(`<p>${renderInline(paragraph.join(" "))}</p>`);
    paragraph = [];
  };
  const flushList = () => {
    if (list) {
      const items = list.items.map((item) => `<li>${renderInline(item)}</li>`).join("");
      html.push(`<${list.tag}>${items}</${list.tag}>`);
    }
    list = null;
  };
  const flushTable = () => {
    if (table) html.push(table.length >= 2 && /^\|?\s*:?-{3,}/.test(table[1].trim()) ? renderTable(table) : `<p>${renderInline(table.join(" "))}</p>`);
    table = null;
  };

  for (const line of String(markdown).split("\n")) {
    if (code) {
      if (line.trim().startsWith("```")) {
        html.push(`<pre class="md-code" tabindex="0"><code>${escapeHtml(code.join("\n"))}</code></pre>`);
        code = null;
      } else {
        code.push(line);
      }
      continue;
    }
    if (line.trim().startsWith("```")) {
      flushParagraph();
      flushList();
      flushTable();
      code = [];
      continue;
    }
    if (line.trim().startsWith("|")) {
      flushParagraph();
      flushList();
      (table ??= []).push(line);
      continue;
    }
    flushTable();
    const bullet = line.match(/^- (.*)/);
    const numbered = line.match(/^\d+\. (.*)/);
    if (bullet || numbered) {
      flushParagraph();
      const tag = bullet ? "ul" : "ol";
      if (list && list.tag !== tag) flushList();
      list ??= { tag, items: [] };
      list.items.push((bullet || numbered)[1]);
    } else if (line.trim() === "") {
      flushParagraph();
      flushList();
    } else {
      flushList();
      paragraph.push(line.trim());
    }
  }
  if (code) html.push(`<pre class="md-code" tabindex="0"><code>${escapeHtml(code.join("\n"))}</code></pre>`);
  flushParagraph();
  flushList();
  flushTable();
  return html.join("");
}
