package io.github.marbi8891.pld.pcap

/*
 * La Ruta como un libro (ADR-0029): cada tema es una página. Aquí, sin Android y con tests,
 * lo que la página necesita saber.
 */
object Book {
    const val INTRO_MAX = 240

    /**
     * Primer párrafo de la teoría, para abrir la página del tema. Si es largo, se corta en el final
     * de una frase (o de una palabra) y se añade «…». Las listas y el código no sirven de entradilla.
     */
    fun intro(theory: String, max: Int = INTRO_MAX): String {
        val paragraph = theory
            .split(Regex("\\n\\s*\\n"))
            .map { it.trim() }
            .firstOrNull { it.isNotEmpty() && !it.startsWith("-") && !it.startsWith("```") && !it.first().isDigit() }
            ?.replace(Regex("\\s+"), " ")
            ?: return ""
        if (paragraph.length <= max) return paragraph
        val cut = paragraph.take(max)
        val sentence = cut.lastIndexOf(". ")
        return if (sentence > max / 2) cut.take(sentence + 1) else cut.substringBeforeLast(' ').trimEnd(',', ';', ':') + "…"
    }

    /** Página en la que se abre el libro: la del tema de la lección que toca (o la última si está todo hecho). */
    fun openingPage(units: List<PathUnit>, current: PathNode?): Int =
        if (current == null) maxOf(0, units.lastIndex) else units.indexOfFirst { it.slug == current.unit }.coerceAtLeast(0)
}
