package io.github.marbi8891.pld.pcap

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.File
import kotlin.random.Random

/** El curso de SQL (ADR-0016) se lee con los mismos lectores que el PCAP y no choca con él. */
class SqlCourseTest {
    private val dir = File("src/main/assets/courses/sql")
    private val bank = Bank.parse(File(dir, "bank.json").readText())
    private val lessonsJson = File(dir, "lessons.json").readText()
    private val lessons = LessonIndex.parse(lessonsJson)
    private val content = LessonLibrary.parse(lessonsJson)
    private val units = Course.build(bank, lessons)

    private val pcapBank = Bank.parse(File("../../frontend/data/pcap.json").readText())
    private val pcapUnits = Course.build(pcapBank, LessonIndex.parse(File("../../frontend/data/lessons.json").readText()))

    @Test
    fun rutaCompletaConTeoriaParaCadaUnidad() {
        assertEquals(5, bank.exam.blocks.size)
        assertEquals(100, bank.exam.blocks.sumOf { it.weight })
        assertEquals(10, units.size)
        assertEquals(bank.questions.size, units.sumOf { u -> u.nodes.sumOf { it.questionIds.size } })
        assertTrue(units.all { it.slug in content })
        assertTrue(bank.questions.all { it.lesson in content && it.answer.single() in it.options.indices })
    }

    @Test
    fun identificadoresDistintosDeLosDelPcap() {
        // El progreso de la ruta es compartido: los nodos de dos cursos no pueden llamarse igual
        val pcapNodes = pcapUnits.flatMap { u -> u.nodes.map { it.id } }.toSet()
        assertTrue(units.flatMap { u -> u.nodes.map { it.id } }.none { it in pcapNodes })
        val pcapIds = pcapBank.questions.map { it.id }.toSet()
        assertTrue(bank.questions.none { it.id in pcapIds })
    }

    @Test
    fun losJuegosFuncionanConElCurso() {
        val run = DungeonRun.start(bank, PcapState(), Random(1))
        assertTrue(run.floors.all { it.questions.size == DungeonRun.ROOMS + DungeonRun.BOSS })
        assertTrue(RushGame.pool(bank).size >= 20)
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
