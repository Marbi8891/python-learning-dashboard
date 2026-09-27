package io.github.marbi8891.pld.pcap

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.File

class LessonContentTest {
    private val json = File("../../frontend/data/lessons.json").readText()
    private val library = LessonLibrary.parse(json)

    @Test
    fun todasLasLeccionesTienenSuTeoriaDentroDeLaApp() {
        val index = LessonIndex.parse(json)
        assertEquals(index.titles.keys, library.keys)
        library.values.forEach { l ->
            assertTrue(l.slug, l.theory.isNotBlank() && l.exampleCode.isNotBlank() && l.exercise.isNotBlank())
            assertTrue(l.slug, l.quiz.isNotEmpty() && l.quiz.all { it.answer in it.options.indices })
        }
        val variables = library.getValue("variables")
        assertEquals("Bases de Python", variables.module)
        assertEquals("Tarjeta de presentación", variables.challenge?.title)
        assertTrue(variables.faq.isNotEmpty() && variables.sources.isNotEmpty())
    }

    @Test
    fun todaUnidadDeLaRutaTieneTeoria() {
        val units = Course.build(Bank.parse(File("../../frontend/data/pcap.json").readText()), LessonIndex.parse(json))
        assertTrue(units.all { it.slug in library })
    }

    @Test
    fun parrafosYListasComoEnLaWeb() {
        val blocks = parseBlocks("Intro **uno**\nsigue aquí\n\nReglas:\n- a\n- b\n1. x\n2. y\n\nFin")
        assertEquals(
            listOf(
                MdBlock.Paragraph("Intro **uno** sigue aquí"),
                MdBlock.Paragraph("Reglas:"),
                MdBlock.Bullets(listOf("a", "b")),
                MdBlock.Numbered(listOf("x", "y")),
                MdBlock.Paragraph("Fin"),
            ),
            blocks,
        )
    }
}
