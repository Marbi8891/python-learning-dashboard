package io.github.marbi8891.pld.pcap

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.File
import java.time.Duration
import java.time.Instant
import java.time.LocalDate

class CourseTest {
    private val bank = Bank.parse(File("../../frontend/data/pcap.json").readText())
    private val lessons = LessonIndex.parse(File("../../frontend/data/lessons.json").readText())
    private val units = Course.build(bank, lessons)
    private val today = LocalDate.parse("2026-09-27")

    @Test
    fun laRutaIncluyeCadaPreguntaUnaSolaVez() {
        val ids = units.flatMap { u -> u.nodes.flatMap { it.questionIds } }
        assertEquals(bank.questions.size, ids.size)
        assertEquals(bank.questions.map { it.id }.toSet(), ids.toSet())
    }

    @Test
    fun unidadesEnElOrdenDelExamenYSinUnidadesMinimas() {
        assertEquals(bank.exam.blocks.map { it.slug }, units.map { it.block }.distinct())
        assertTrue(units.all { u -> u.nodes.sumOf { it.questionIds.size } >= Course.MIN_UNIT })
        // La lección «Módulos y paquetes» tiene una sola pregunta: se une a la siguiente
        assertEquals("math-random-platform", units.first().slug)
        assertEquals("math, random y platform", units.first().title)
    }

    @Test
    fun leccionesCortasDeTamanoParecido() {
        val sizes = units.flatMap { u -> u.nodes.map { it.questionIds.size } }
        assertTrue(sizes.all { it in 3..7 })
        units.forEach { u -> assertTrue(u.nodes.maxOf { it.questionIds.size } - u.nodes.minOf { it.questionIds.size } <= 1) }
        assertEquals(units.sumOf { it.nodes.size }, units.flatMap { u -> u.nodes.map { it.id } }.toSet().size)
    }

    @Test
    fun desbloqueoEnOrden() {
        val p = AppProgress()
        val all = units.flatMap { it.nodes }
        assertEquals(all[0], p.currentNode(units))
        assertTrue(p.isUnlocked(all[0], units))
        assertFalse(p.isUnlocked(all[1], units))
        assertEquals(15, p.complete(all[0], perfect = true, today = today))
        assertEquals(all[1], p.currentNode(units))
        assertTrue(p.isUnlocked(all[0], units))
        assertEquals(10, p.complete(all[1], perfect = false, today = today))
        assertEquals(25, p.xpOn(today))
    }

    @Test
    fun leccionRepiteLasFalladasHastaAcertarlas() {
        val qs = bank.questions.take(3)
        val run = LessonRun(qs)
        run.answer(false) // falla la 1.ª: vuelve al final
        assertEquals(qs[1], run.current)
        run.answer(true)
        run.answer(true)
        assertEquals(qs[0], run.current)
        assertFalse(run.finished)
        run.answer(true)
        assertTrue(run.finished)
        assertFalse(run.perfect)
        assertEquals(1, run.mistakes)
        assertEquals(1f, run.progress)
    }

    @Test
    fun rachaDerivadaDeLaXpDiaria() {
        val p = AppProgress()
        assertEquals(0, p.streak(today))
        p.addXp(10, today.minusDays(2))
        p.addXp(5, today.minusDays(1))
        assertEquals(2, p.streak(today)) // hoy aún no ha estudiado: la racha sigue viva
        p.addXp(10, today)
        assertEquals(3, p.streak(today))
        assertEquals(0, p.streak(today.plusDays(2))) // un día entero sin estudiar la rompe
        p.addXp(0, today.plusDays(5))
        assertEquals(25, p.totalXp())
    }

    @Test
    fun vidasSePierdenYSeRecuperanConElTiempo() {
        val p = AppProgress()
        val t0 = Instant.parse("2026-09-27T10:00:00Z")
        assertEquals(5, p.heartsNow(t0))
        assertNull(p.nextHeartIn(t0))
        repeat(5) { p.loseHeart(t0) }
        assertEquals(0, p.heartsNow(t0))
        assertEquals(Duration.ofHours(4), p.nextHeartIn(t0))
        assertEquals(1, p.heartsNow(t0.plus(Duration.ofHours(5))))
        assertEquals(Duration.ofHours(3), p.nextHeartIn(t0.plus(Duration.ofHours(5))))
        p.gainHeart(t0.plus(Duration.ofHours(5))) // una tanda de práctica
        assertEquals(2, p.heartsNow(t0.plus(Duration.ofHours(5))))
        assertEquals(5, p.heartsNow(t0.plus(Duration.ofDays(2))))
        p.loseHeart(t0.plus(Duration.ofDays(2)))
        assertEquals(Duration.ofHours(4), p.nextHeartIn(t0.plus(Duration.ofDays(2))))
    }

    @Test
    fun progresoDeLaAppViajaEnElMismoDocumento() {
        val s = PcapState()
        s.app.complete(units[0].nodes[0], perfect = true, today = today)
        s.app.goal = 30
        s.app.loseHeart(Instant.parse("2026-09-27T10:00:00Z"))
        val again = PcapState.fromJson(s.toJson().toString())
        assertEquals(s.toJson().toString(), again.toJson().toString())
        assertEquals(30, again.app.goal)
        assertEquals(15, again.app.xpOn(today))

        val other = PcapState().apply {
            app.complete(units[0].nodes[1], perfect = false, today = today)
            app.addXp(40, today)
        }
        again.merge(other)
        assertEquals(2, again.app.done.size)
        assertEquals(50, again.app.xpOn(today)) // la XP de un día: la mayor de los dos dispositivos
        assertEquals(30, again.app.goal)
    }

    @Test
    fun progresoDanadoEmpiezaDeCero() {
        val s = PcapState.fromJson("""{"app":{"goal":7,"hearts":99,"heartsAt":"ayer","daily":{"2026-09-27":-3}}}""")
        assertEquals(20, s.app.goal)
        assertEquals(5, s.app.heartsNow())
        assertEquals(0, s.app.totalXp())
    }

    @Test
    fun resumenDeUnidadParaSuTarjeta() {
        val s = PcapState()
        val first = units[0]
        val fresh = s.unitSummary(first, s.app.currentNode(units))
        assertEquals(UnitState.CURRENT, fresh.state)
        assertEquals(0, fresh.lessonsDone)
        assertEquals(first.nodes.sumOf { it.questionIds.size }, fresh.questions)
        assertNull(fresh.rate)
        assertEquals(UnitState.LOCKED, s.unitSummary(units[1], s.app.currentNode(units)).state)

        // Acierto: cuenta el último intento de cada pregunta respondida
        val (a, b) = first.nodes[0].questionIds
        s.recordAnswer(a, false)
        s.recordAnswer(a, true)
        s.recordAnswer(b, false)
        first.nodes.forEach { s.app.complete(it, perfect = false, today = today) }
        val done = s.unitSummary(first, s.app.currentNode(units))
        assertEquals(UnitState.DONE, done.state)
        assertEquals(1f, done.progress)
        assertEquals(2, done.answered)
        assertEquals(0.5, done.rate) // 1 de 2, exacto en coma flotante
        assertEquals(UnitState.CURRENT, s.unitSummary(units[1], s.app.currentNode(units)).state)
    }
}
