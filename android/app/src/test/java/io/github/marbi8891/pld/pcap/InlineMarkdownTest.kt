package io.github.marbi8891.pld.pcap

import io.github.marbi8891.pld.pcap.Span.Style.BOLD
import io.github.marbi8891.pld.pcap.Span.Style.CODE
import io.github.marbi8891.pld.pcap.Span.Style.ITALIC
import io.github.marbi8891.pld.pcap.Span.Style.PLAIN
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.File

class InlineMarkdownTest {
    @Test
    fun codigoNegritaYCursiva() {
        assertEquals(
            listOf(Span("usa ", PLAIN), Span("ceil", CODE), Span(" y ", PLAIN), Span("no", BOLD), Span(" ", PLAIN), Span("floor", ITALIC)),
            parseInline("usa `ceil` y **no** *floor*"),
        )
    }

    @Test
    fun elCodigoPuedeLlevarAsteriscos() {
        assertEquals(listOf(Span("a ", PLAIN), Span("x * y", CODE)), parseInline("a `x * y`"))
    }

    @Test
    fun marcadoresSinCerrarSeQuedanComoTexto() {
        assertEquals(listOf(Span("2 * 3 y `abierto", PLAIN)), parseInline("2 * 3 y `abierto"))
        assertEquals(listOf(Span("``", PLAIN)), parseInline("``"))
        assertEquals(listOf(Span("2 * 3 * 4", PLAIN)), parseInline("2 * 3 * 4"))
    }

    @Test
    fun todoElBancoSeInterpretaSinMarcasSueltas() {
        val bank = Bank.parse(File("../../frontend/data/pcap.json").readText())
        val texts = bank.questions.flatMap { q ->
            listOf(q.q, q.explain) + q.options.filterIsInstance<Option.Prose>().map { it.text }
        } + bank.cards.flatMap { listOf(it.front, it.back) }
        val spans = texts.flatMap { listOf(it.es, it.en) }.flatMap { parseInline(it) }
        assertTrue(spans.count { it.style == CODE } > 400)
        assertFalse(spans.filter { it.style != CODE }.any { '`' in it.text })
    }
}
