package io.github.marbi8891.pld.pcap

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.File

class LessonIndexTest {
    @Test
    fun cadaPreguntaYFichaEnlazaAUnaLeccionExistente() {
        val lessons = LessonIndex.parse(File("../../frontend/data/lessons.json").readText())
        val bank = Bank.parse(File("../../frontend/data/pcap.json").readText())
        assertEquals(27, lessons.titles.size)
        assertEquals("Variables y print()", lessons.titles["variables"])
        assertEquals("variables", lessons.modules.getValue("fundamentos").first())
        // Cada bloque del examen es un módulo del temario: el panel enlaza a su teoría
        assertTrue(bank.exam.blocks.all { !lessons.modules[it.slug].isNullOrEmpty() })
        assertTrue((bank.questions.mapNotNull { it.lesson } + bank.cards.mapNotNull { it.lesson }).all { it in lessons.titles })
    }
}
