package io.github.marbi8891.pld.pcap

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.File
import kotlin.random.Random

/** Los cursos de DAW (ADR-0016) se leen con los mismos lectores que el PCAP y no chocan con él ni entre sí. */
class CoursesTest {
    private class Loaded(id: String) {
        private val dir = File("src/main/assets/courses/$id")
        val bank = Bank.parse(File(dir, "bank.json").readText())
        private val lessonsJson = File(dir, "lessons.json").readText()
        val lessons = LessonIndex.parse(lessonsJson)
        val content = LessonLibrary.parse(lessonsJson)
        val units = Course.build(bank, lessons)
    }

    private val courses = listOf("sql", "java").map { Loaded(it) }

    private val pcapBank = Bank.parse(File("../../frontend/data/pcap.json").readText())
    private val pcapUnits = Course.build(pcapBank, LessonIndex.parse(File("../../frontend/data/lessons.json").readText()))

    @Test
    fun rutaCompletaConTeoriaParaCadaUnidad() {
        courses.forEach { c ->
            assertEquals(5, c.bank.exam.blocks.size)
            assertEquals(100, c.bank.exam.blocks.sumOf { it.weight })
            assertEquals(10, c.units.size)
            assertEquals(c.bank.questions.size, c.units.sumOf { u -> u.nodes.sumOf { it.questionIds.size } })
            assertTrue(c.units.all { it.slug in c.content })
            assertTrue(c.bank.questions.all { it.lesson in c.content && it.answer.single() in it.options.indices })
        }
    }

    @Test
    fun identificadoresUnicosEntreTodosLosCursos() {
        // El progreso de la ruta es compartido: nodos, preguntas y bloques no pueden llamarse igual en dos cursos
        val nodes = (listOf(pcapUnits) + courses.map { it.units }).flatMap { units -> units.flatMap { u -> u.nodes.map { it.id } } }
        assertEquals(nodes.size, nodes.toSet().size)
        val questions = (listOf(pcapBank) + courses.map { it.bank }).flatMap { b -> b.questions.map { it.id } }
        assertEquals(questions.size, questions.toSet().size)
        val blocks = (listOf(pcapBank) + courses.map { it.bank }).flatMap { b -> b.exam.blocks.map { it.slug } }
        assertEquals(blocks.size, blocks.toSet().size)
    }

    @Test
    fun losJuegosFuncionanConCadaCurso() {
        courses.forEach { c ->
            val run = DungeonRun.start(c.bank, PcapState(), Random(1))
            assertTrue(run.floors.all { it.questions.size == DungeonRun.ROOMS + DungeonRun.BOSS })
            assertTrue(RushGame.pool(c.bank).size >= 20)
        }
    }

    @Test
    fun elProgresoCompartidoSeGuardaSoloConElPcap() {
        val pcap = PcapState()
        val sql = PcapState().apply { shareApp(pcap.app) }
        sql.app.addXp(10)
        assertEquals(10, pcap.app.totalXp())
        assertFalse(sql.toJson(withApp = false).has("app"))
        assertTrue(pcap.toJson().has("app"))
    }
}
