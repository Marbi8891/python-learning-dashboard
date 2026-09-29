package io.github.marbi8891.pld.pcap

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.File
import kotlin.random.Random

/** Los cursos de DAW (ADR-0016) se leen con los mismos lectores que el PCAP y no chocan con él ni entre sí. */
class CoursesTest {
    private class Loaded(val id: String) {
        private val dir = File("../../frontend/data/courses/$id")
        val bank = Bank.parse(File(dir, "bank.json").readText())
        private val lessonsJson = File(dir, "lessons.json").readText()
        val lessons = LessonIndex.parse(lessonsJson)
        val content = LessonLibrary.parse(lessonsJson)
        val units = Course.build(bank, lessons)
    }

    private val courses = listOf("programacion", "sql", "js", "java", "entornos").map { Loaded(it) }

    private val pcapBank = Bank.parse(File("../../frontend/data/pcap.json").readText())
    private val pcapUnits = Course.build(pcapBank, LessonIndex.parse(File("../../frontend/data/lessons.json").readText()))

    @Test
    fun rutaCompletaConTeoriaParaCadaUnidad() {
        courses.forEach { c ->
            assertTrue(c.bank.exam.blocks.size >= 4)
            assertEquals(100, c.bank.exam.blocks.sumOf { it.weight })
            // Cada lección del curso es una unidad de la ruta
            assertEquals(c.content.size, c.units.size)
            assertEquals(c.bank.questions.size, c.units.sumOf { u -> u.nodes.sumOf { it.questionIds.size } })
            assertTrue(c.units.all { it.slug in c.content })
            assertTrue(c.bank.questions.all { it.lesson in c.content && (it.kind != Kind.CHOICE || it.answer.single() in it.options.indices) })
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

    @Test
    fun ejerciciosDeEscribirCodigo() {
        // ADR-0017: completar el hueco, ordenar líneas y encontrar el error
        val java = courses.first { it.id == "java" }.bank
        val fills = java.questions.filter { it.kind == Kind.FILL }
        val orders = java.questions.filter { it.kind == Kind.ORDER }
        assertEquals(10, fills.size)
        assertEquals(10, orders.size)
        fills.forEach { q ->
            assertTrue(q.code!!.contains("___") && q.accept.isNotEmpty())
            assertTrue(q.isCorrect(Answer(text = q.accept.first())))
            // Los espacios y el punto y coma final no cuentan
            assertTrue(q.isCorrect(Answer(text = "  " + q.accept.first().replace(" ", "") + ";")))
            assertFalse(q.isCorrect(Answer(text = "")))
            assertFalse(q.isComplete(Answer(text = "   ")))
        }
        orders.forEach { q ->
            assertTrue(q.isCorrect(Answer(order = q.lines.indices.toList())))
            assertFalse(q.isCorrect(Answer(order = q.lines.indices.reversed().toList())))
            assertFalse(q.isComplete(Answer(order = listOf(0))))
        }
        // Encontrar el error: un test cuyas opciones son las líneas del programa
        val bug = java.questions.first { it.id == "java-p03" }
        assertEquals(Kind.CHOICE, bug.kind)
        assertEquals("double r = a / b;", (bug.options[bug.answer.single()] as Option.Code).source)
        // Los ejercicios de escribir no van al Bug Rush (es de sí/no)
        assertTrue(RushGame.pool(java).none { it.kind != Kind.CHOICE })
    }

    @Test
    fun laMazmorraCorrigeCualquierTipoDeEjercicio() {
        val java = courses.first { it.id == "java" }.bank
        val fill = java.questions.first { it.kind == Kind.FILL }
        val run = DungeonRun(listOf(DungeonRun.Floor("x", listOf(fill, fill, fill, fill))))
        assertTrue(run.answer(Answer(text = fill.accept.first())))
        run.next()
        assertFalse(run.answer(Answer(text = "nada")))
        assertEquals(DungeonRun.MAX_HP - 1, run.hp)
    }

    @Test
    fun basesDeDatosSigueElTemarioDelCentroSinPerderProgreso() {
        // ADR-0019: bloques = UD del centro; las preguntas de antes conservan su id
        val bd = courses.first { it.id == "sql" }
        assertEquals(listOf("bd-ud1", "bd-ud2", "bd-ud3", "bd-ampliacion"), bd.bank.exam.blocks.map { it.slug })
        val ids = bd.bank.questions.map { it.id }.toSet()
        assertTrue((1..50).all { "sql-%02d".format(it) in ids })
        // Cada unidad del centro tiene teoría propia y ejercicios de escribir SQL
        assertTrue(bd.bank.questions.filter { it.block == "bd-ud1" }.size >= 20)
        assertTrue(bd.bank.questions.any { it.block == "bd-ud2" && it.kind == Kind.FILL })
        assertTrue(bd.bank.questions.any { it.block == "bd-ud3" && it.kind == Kind.ORDER })
    }

    @Test
    fun programacionSigueLasNueveUnidades() {
        // ADR-0020: un bloque por UT, con ejercicios de escribir código en Python
        val prog = courses.first { it.id == "programacion" }
        assertEquals((1..9).map { "prog-ut$it" }, prog.bank.exam.blocks.map { it.slug })
        assertTrue(prog.bank.questions.size >= 150)
        assertTrue(prog.bank.questions.any { it.kind == Kind.FILL } && prog.bank.questions.any { it.kind == Kind.ORDER })
        assertTrue(prog.bank.exam.blocks.all { b -> prog.bank.questions.count { it.block == b.slug } >= DungeonRun.ROOMS + DungeonRun.BOSS })
    }
}
