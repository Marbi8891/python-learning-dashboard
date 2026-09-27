package io.github.marbi8891.pld.pcap

/** Trozo de texto con el formato que usan las preguntas: `código`, **negrita** y *cursiva*. */
data class Span(val text: String, val style: Style) {
    enum class Style { PLAIN, CODE, BOLD, ITALIC }
}

/** Markdown en línea mínimo (sin enlaces ni HTML: el banco no los usa). Un marcador sin cerrar se queda como texto. */
fun parseInline(text: String): List<Span> {
    val spans = mutableListOf<Span>()
    val plain = StringBuilder()
    fun flush() {
        if (plain.isNotEmpty()) spans.add(Span(plain.toString(), Span.Style.PLAIN))
        plain.clear()
    }

    var i = 0
    while (i < text.length) {
        val (marker, style) = when {
            text[i] == '`' -> "`" to Span.Style.CODE
            text.startsWith("**", i) -> "**" to Span.Style.BOLD
            // Como en la web: `2 * 3 * 4` no es cursiva (tras el asterisco tiene que haber texto)
            text[i] == '*' && i + 1 < text.length && !text[i + 1].isWhitespace() -> "*" to Span.Style.ITALIC
            else -> null to Span.Style.PLAIN
        }
        val end = if (marker == null) -1 else text.indexOf(marker, i + marker.length)
        if (marker == null || end <= i + marker.length - 1 || end == i + marker.length) {
            plain.append(text[i])
            i++
            continue
        }
        flush()
        spans.add(Span(text.substring(i + marker.length, end), style))
        i = end + marker.length
    }
    flush()
    return spans
}
