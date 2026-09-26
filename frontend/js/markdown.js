/* Markdown mínimo y seguro: el contenido se escapa siempre, nunca se inyecta HTML. */

const ESCAPES = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" };

export const escapeHtml = (text) => String(text ?? "").replace(/[&<>"']/g, (c) => ESCAPES[c]);

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

/** Párrafos (separados por una línea en blanco) y listas con "- " o "1. ". */
export function renderMarkdown(markdown = "") {
  const html = [];
  let paragraph = [];
  let list = null;

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

  for (const line of String(markdown).split("\n")) {
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
  flushParagraph();
  flushList();
  return html.join("");
}
