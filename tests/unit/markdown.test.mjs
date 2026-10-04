import assert from "node:assert/strict";
import { test } from "node:test";
import { renderInline, renderMarkdown, safeUrl } from "../../frontend/js/markdown.js";

test("escapa siempre el HTML, también dentro del código y de las tablas", () => {
  assert.equal(renderInline("<b>x</b>"), "&lt;b&gt;x&lt;/b&gt;");
  assert.match(renderMarkdown("```\n<script>alert(1)</script>\n```"), /&lt;script&gt;/);
  assert.doesNotMatch(renderMarkdown("| a | b |\n|---|---|\n| <img> | x |"), /<img>/);
});

test("bloques de código con ```", () => {
  assert.equal(renderMarkdown("Texto\n\n```\nx = 1\n  y\n```"), '<p>Texto</p><pre class="md-code" tabindex="0"><code>x = 1\n  y</code></pre>');
});

test("tablas con cabecera y separador", () => {
  const html = renderMarkdown("| paso | i |\n|---|---|\n| 1 | `0` |");
  assert.match(html, /<th scope="col">paso<\/th>/);
  assert.match(html, /<td><code>0<\/code><\/td>/);
});

test("una línea con | sin separador no es una tabla", () => {
  assert.equal(renderMarkdown("| solo"), "<p>| solo</p>");
});

test("listas y párrafos siguen funcionando", () => {
  assert.equal(renderMarkdown("- a\n- b\n\nfin"), "<ul><li>a</li><li>b</li></ul><p>fin</p>");
});

test("safeUrl solo admite https", () => {
  assert.equal(safeUrl("javascript:alert(1)"), "#");
  assert.equal(safeUrl("https://docs.python.org/es/3/"), "https://docs.python.org/es/3/");
});
