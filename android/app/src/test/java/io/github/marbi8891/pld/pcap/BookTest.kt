package io.github.marbi8891.pld.pcap

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.File

/** La Ruta como libro (ADR-0029): entradilla de cada tema y página de apertura. */
class BookTest {
    @Test
    fun laEntradillaEsElPrimerParrafoDeTexto() {
        val theory = "- una lista no vale\n\nUna **variable** guarda un valor.\nSe crea al asignarla.\n\n```python\nx = 1\n```"
        assertEquals("Una **variable** guarda un valor. Se crea al asignarla.", Book.intro(theory))
        assertEquals("", Book.intro(""))
    }

    @Test
    fun siEsLargaSeCortaEnUnaFraseOEnUnaPalabra() {
        val long = "Primera frase bastante larga para el ejemplo. " + "palabra ".repeat(60)
        assertEquals("Primera frase bastante larga para el ejemplo.", Book.intro(long, max = 80))
        val words = "uno dos tres cuatro cinco seis siete ocho nueve diez"
        val cut = Book.intro(words, max = 20)
        assertTrue(cut.endsWith("…"))
        assertTrue(cut.length <= 21)
        assertEquals("uno dos tres cuatro…", cut)
    }

    @Test
    fun todosLosTemasDeTodosLosCursosTienenEntradilla() {
        val dirs = listOf("../../frontend/data/lessons.json") +
            listOf("programacion", "sql", "entornos", "js", "java").map { "../../frontend/data/courses/$it/lessons.json" }
        dirs.forEach { path ->
            LessonLibrary.parse(File(path).readText()).values.forEach { lesson ->
                assertTrue("${lesson.slug} sin entradilla", Book.intro(lesson.theory).isNotEmpty())
            }
        }
    }

    @Test
    fun elLibroSeAbreEnElTemaQueToca() {
        val units = listOf(
            PathUnit("a", "b1", "A", listOf(PathNode("a-1", "a", 1, emptyList()))),
            PathUnit("b", "b1", "B", listOf(PathNode("b-1", "b", 1, emptyList()), PathNode("b-2", "b", 2, emptyList()))),
        )
        assertEquals(1, Book.openingPage(units, units[1].nodes[1]))
        assertEquals(1, Book.openingPage(units, null)) // todo hecho: la última página
        assertEquals(0, Book.openingPage(emptyList(), null))
    }
}
