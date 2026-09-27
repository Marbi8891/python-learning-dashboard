package io.github.marbi8891.pld.pcap

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.File
import java.time.Instant
import java.time.LocalDate
import kotlin.random.Random

/** Mismas reglas que frontend/js/pcap-store.js, sobre el mismo banco de preguntas. */
class PcapStateTest {
    private val bank = Bank.parse(File("../../frontend/data/pcap.json").readText())
    private val today = LocalDate.parse("2026-09-27")
    private val now = Instant.parse("2026-09-27T10:00:00Z")

    @Test
    fun bancoCompleto() {
        assertEquals(126, bank.questions.size)
        assertEquals(48, bank.cards.size)
        assertEquals(100, bank.exam.blocks.sumOf { it.weight })
        assertEquals(bank.exam.questions, bank.exam.blocks.sumOf { it.items })
        assertTrue(bank.questions.any { it.multi })
        assertTrue(bank.questions.all { q -> q.answer.all { it in q.options.indices } })
        val mod01 = bank.questions.first { it.id == "mod-01" }
        assertEquals(Option.Code("-2 -3"), mod01.options[0])
        assertTrue(mod01.isCorrect(listOf(0)))
        assertFalse(mod01.isCorrect(listOf(1)))
    }

    @Test
    fun elegirDosExigeLasDos() {
        val q = bank.questions.first { it.multi }
        assertTrue(q.isCorrect(q.answer.reversed()))
        assertFalse(q.isCorrect(q.answer.take(1)))
        assertFalse(q.isCorrect(q.options.indices.toList()))
    }

    @Test
    fun repasoEspaciadoConCajasDeLeitner() {
        val s = PcapState()
        s.review("a", true, today, now)
        assertEquals(SrsItem(1, "2026-09-28", "2026-09-27T10:00:00.000Z"), s.srs["a"])
        listOf("2026-09-30", "2026-10-04", "2026-10-11", "2026-10-27", "2026-10-27").forEach { due ->
            s.review("a", true, today, now)
            assertEquals(due, s.srs.getValue("a").due)
        }
        assertEquals(5, s.srs.getValue("a").box)
        s.review("a", false, today, now)
        assertEquals(SrsItem(1, "2026-09-28", "2026-09-27T10:00:00.000Z"), s.srs["a"])
        assertEquals(emptyList<String>(), s.dueIds(listOf("a", "b"), today))
        assertEquals(listOf("a"), s.dueIds(listOf("a", "b"), today.plusDays(1)))
    }

    @Test
    fun historialDeLosUltimosCincoIntentos() {
        val s = PcapState()
        repeat(6) { s.recordAnswer("q", it == 5, today, now) }
        assertEquals(listOf(false, false, false, false, true), s.answers["q"])
        assertEquals(1, s.questionsMastered())
    }

    @Test
    fun preparacionPonderadaPorBloque() {
        val s = PcapState()
        assertEquals(0, s.status(bank).score)
        assertNull(s.blockStats(bank).getValue("poo").rate)
        // Todo el bloque de POO (34 %) acertado y nada más
        bank.questions.filter { it.block == "poo" }.forEach { s.recordAnswer(it.id, true, today, now) }
        val status = s.status(bank)
        assertEquals(34, status.score)
        assertFalse(status.ready)
        assertEquals(4, status.weak.size)
        s.updateFlags(bank)
        assertEquals(true, s.flags["mastered"])
    }

    @Test
    fun listoConTodoAcertadoYUnSimulacroAprobado() {
        val s = PcapState()
        bank.questions.forEach { s.recordAnswer(it.id, true, today, now) }
        assertFalse(s.status(bank).ready)
        s.exams.add(ExamResult("2026-09-27T10:00:00.000Z", 32, 40, 80, 3000, emptyMap()))
        assertTrue(s.status(bank).ready)
        assertEquals(100, s.status(bank).score)
    }

    @Test
    fun practicaEmpiezaPorLasFalladas() {
        val s = PcapState()
        val pool = bank.questions.filter { it.block == "strings" }
        s.recordAnswer(pool[3].id, false, today, now)
        s.recordAnswer(pool[4].id, true, today, now)
        val set = s.practiceSet(bank, "strings", Random(1))
        assertEquals(PcapState.PRACTICE_SIZE, set.size)
        assertEquals(pool[3].id, set.first().id)
        assertTrue(set.all { it.block == "strings" })
        set.indexOf(pool[4]).let { assertTrue(it == -1 || it == set.lastIndex) } // la acertada, al final si cabe
    }

    @Test
    fun fusionSinPerderNada() {
        val local = PcapState().apply {
            answers["a"] = mutableListOf(true)
            known.add("c1")
            bestCombo = 3
            srs["a"] = SrsItem(2, "2026-09-30", "2026-09-27T10:00:00.000Z")
        }
        val remote = PcapState().apply {
            answers["a"] = mutableListOf(false, true)
            answers["b"] = mutableListOf(false)
            known.add("c2")
            bestCombo = 7
            flags["ready"] = true
            srs["a"] = SrsItem(1, "2026-09-28", "2026-09-26T10:00:00.000Z")
            exams.add(ExamResult("2026-09-20T10:00:00.000Z", 30, 40, 75, 3000, mapOf("poo" to listOf(10, 14))))
            examDate = "2026-11-02"
        }
        local.merge(remote)
        assertEquals(listOf(false, true), local.answers["a"])
        assertEquals(listOf(false), local.answers["b"])
        assertEquals(listOf("c1", "c2"), local.known)
        assertEquals(7, local.bestCombo)
        assertEquals(true, local.flags["ready"])
        assertEquals(2, local.srs.getValue("a").box) // gana el repaso más reciente
        assertEquals(1, local.exams.size)
        assertEquals("2026-11-02", local.examDate)
    }

    @Test
    fun jsonIdaYVueltaConElFormatoDeLaWeb() {
        val web = """{"lang":"en","answers":{"mod-01":[false,true]},"exams":[{"date":"2026-09-20T10:00:00.000Z","correct":32,"total":40,
            "score":80,"seconds":3000,"blocks":{"poo":[12,14]}}],"known":["mod-f01"],"bestCombo":4,
            "flags":{"mastered":true,"ready":false,"allCards":false},"srs":{"mod-01":{"box":2,"due":"2026-09-30","last":"2026-09-27T10:00:00.000Z"}},
            "plan":{"examDate":null}}"""
        val s = PcapState.fromJson(web)
        assertEquals("en", s.lang)
        assertEquals(listOf(false, true), s.answers["mod-01"])
        assertEquals(listOf(12, 14), s.exams.single().blocks["poo"])
        assertNull(s.examDate)
        val again = PcapState.fromJson(s.toJson().toString())
        assertEquals(s.toJson().toString(), again.toJson().toString())
        assertTrue(again.toJson().getJSONObject("plan").isNull("examDate"))
    }

    @Test
    fun estadoDanadoOVacioEmpiezaDeCero() {
        listOf(null, "", "no es json", "[]", """{"answers":5,"srs":{"x":3}}""").forEach {
            val s = PcapState.fromJson(it)
            assertEquals("es", s.lang)
            assertTrue(s.answers.isEmpty() && s.srs.isEmpty())
        }
    }
}
