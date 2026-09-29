package io.github.marbi8891.pld.pcap

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.File
import java.time.Instant
import kotlin.random.Random

/** Simulacro (ADR-0024): mismo reparto y misma corrección que el de la web. */
class MockTest {
    private val pcap = Bank.parse(File("../../frontend/data/pcap.json").readText())
    private val programacion = Bank.parse(File("../../frontend/data/courses/programacion/bank.json").readText())
    private val courses = listOf("programacion", "sql", "entornos", "js", "java")
        .map { Bank.parse(File("../../frontend/data/courses/$it/bank.json").readText()) }

    @Test
    fun elPcapUsaElRepartoOficial() {
        val plan = Mock.plan(pcap)
        assertEquals(40, plan.total)
        assertEquals(65, plan.minutes)
        assertEquals(70, plan.pass)
        assertEquals(pcap.exam.blocks.associate { it.slug to it.items }, plan.perBlock)
    }

    @Test
    fun losCursosRepartenTreintaPreguntasSegunElPeso() {
        courses.forEach { bank ->
            val plan = Mock.plan(bank)
            assertEquals(Mock.COURSE_QUESTIONS, plan.total)
            assertEquals(Mock.COURSE_QUESTIONS * Mock.SECONDS_PER_QUESTION / 60, plan.minutes)
            assertEquals(Mock.COURSE_PASS, plan.pass)
            bank.exam.blocks.forEach { b ->
                assertTrue(plan.perBlock.getValue(b.slug) <= bank.questions.count { it.block == b.slug })
            }
        }
        // Programación: la UT3 (20 %) lleva más preguntas que la UT1 (8 %)
        val plan = Mock.plan(programacion)
        assertEquals(6, plan.perBlock.getValue("prog-ut3"))
        assertTrue(plan.perBlock.getValue("prog-ut1") < plan.perBlock.getValue("prog-ut3"))
    }

    @Test
    fun elRepartoNoPideMasDeLasQueHayYSumaElTotal() {
        val shared = Mock.share(10, listOf("a" to 50, "b" to 30, "c" to 20), mapOf("a" to 2, "b" to 10, "c" to 10))
        assertEquals(2, shared.getValue("a"))
        assertEquals(10, shared.values.sum())
        // Si no hay preguntas suficientes, se usan todas las que hay
        val few = Mock.share(10, listOf("a" to 50, "b" to 50), mapOf("a" to 1, "b" to 2))
        assertEquals(mapOf("a" to 1, "b" to 2), few)
    }

    @Test
    fun construyePreguntasDistintasDelBloqueQueToca() {
        val plan = Mock.plan(pcap)
        val questions = Mock.build(pcap, plan, Random(7))
        assertEquals(plan.total, questions.size)
        assertEquals(questions.size, questions.map { it.id }.toSet().size)
        plan.perBlock.forEach { (slug, n) -> assertEquals(n, questions.count { it.block == slug }) }
    }

    @Test
    fun corrigeComoLaWeb() {
        val qs = pcap.questions.filter { !it.multi && it.kind == Kind.CHOICE }.take(3)
        val right = Answer(selected = qs[0].answer.toSet())
        val wrong = Answer(selected = setOf(qs[1].options.indices.first { it !in qs[1].answer }))
        val result = Mock.grade(qs, listOf(right, wrong, Answer()), 100, Instant.parse("2026-09-30T10:00:00Z"))
        assertEquals(1, result.correct)
        assertEquals(3, result.total)
        assertEquals(33, result.score) // Math.round(1 / 3 * 100)
        assertEquals("2026-09-30T10:00:00.000Z", result.date)
        assertEquals(qs.size, result.blocks.values.sumOf { it[1] })
    }

    @Test
    fun entregarConHuecosPideConfirmacionYElTiempoLoCierra() {
        val plan = MockPlan(mapOf("x" to 2), minutes = 1, pass = 50)
        val qs = pcap.questions.filter { !it.multi && it.kind == Kind.CHOICE }.take(2)
        var s = MockUiState.start(qs, plan, now = 0)
        s = s.reduce(MockAction.ChangeAnswer(Answer(selected = qs[0].answer.toSet())))
        s = s.reduce(MockAction.Submit(now = 1_000))
        assertTrue(s.confirming)
        assertNull(s.result)
        s = s.reduce(MockAction.CancelSubmit)
        assertFalse(s.confirming)
        s = s.reduce(MockAction.GoTo(1))
        assertEquals(1, s.index)
        // Se acaba el tiempo: se corrige solo y no cuenta más de lo que dura el examen
        s = s.reduce(MockAction.Finish(now = 500_000, instant = Instant.parse("2026-09-30T10:00:00Z")))
        assertEquals(1, s.result!!.correct)
        assertEquals(60, s.result!!.seconds)
        assertTrue(s.passed)
        // Terminado, ya no cambia
        assertEquals(s, s.reduce(MockAction.ChangeAnswer(Answer(selected = setOf(0)))))
        assertEquals(0, s.secondsLeft(now = 70_000))
        assertEquals(30, MockUiState.start(qs, plan, now = 0).secondsLeft(now = 30_000))
    }
}
