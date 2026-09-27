package io.github.marbi8891.pld.pcap

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.File
import kotlin.random.Random

class GameTest {
    private val bank = Bank.parse(File("../../frontend/data/pcap.json").readText())

    private fun right(q: Question) = q.answer.toSet()

    private fun wrong(q: Question) = setOf(q.options.indices.first { it !in q.answer })

    @Test
    fun unaPlantaPorBloqueEnElOrdenDelExamen() {
        val state = PcapState()
        val failed = bank.questions.first { it.block == "excepciones" }
        state.recordAnswer(failed.id, false)
        val run = DungeonRun.start(bank, state, Random(1))
        assertEquals(bank.exam.blocks.map { it.slug }, run.floors.map { it.block })
        run.floors.forEach { f ->
            assertEquals(DungeonRun.ROOMS + DungeonRun.BOSS, f.questions.size)
            assertTrue(f.questions.all { it.block == f.block })
        }
        // Lo que fallaste sale antes
        assertEquals(failed, run.floors[1].questions.first())
    }

    @Test
    fun partidaPerfectaGanaConTodasLasMonedas() {
        val run = DungeonRun.start(bank, PcapState(), Random(2))
        while (!run.finished) {
            when (run.phase) {
                DungeonRun.Phase.ASK -> assertTrue(run.answer(right(run.current)))
                DungeonRun.Phase.FEEDBACK -> run.next()
                DungeonRun.Phase.FLOOR_CLEARED -> run.enterNextFloor()
                else -> Unit
            }
        }
        assertEquals(DungeonRun.Phase.WON, run.phase)
        assertEquals(5, run.floorsCleared)
        val perFloor = DungeonRun.ROOMS * DungeonRun.ROOM_COINS + DungeonRun.BOSS * DungeonRun.BOSS_COINS + DungeonRun.FLOOR_BONUS
        assertEquals(5 * perFloor, run.score)
        assertEquals(30, run.correct)
    }

    @Test
    fun cincoFallosTerminanLaPartida() {
        val run = DungeonRun.start(bank, PcapState(), Random(3))
        repeat(DungeonRun.MAX_HP) {
            assertEquals(DungeonRun.Phase.ASK, run.phase)
            if (run.phase == DungeonRun.Phase.FLOOR_CLEARED) run.enterNextFloor()
            assertFalse(run.answer(wrong(run.current)))
            run.next()
            if (run.phase == DungeonRun.Phase.FLOOR_CLEARED) run.enterNextFloor()
        }
        assertEquals(DungeonRun.Phase.LOST, run.phase)
        assertEquals(0, run.hp)
        assertEquals(0, run.score)
    }

    @Test
    fun elJefeTieneTiempoYAgotarloEsFallo() {
        val run = DungeonRun.start(bank, PcapState(), Random(4))
        repeat(DungeonRun.ROOMS) {
            assertFalse(run.isBoss)
            run.answer(right(run.current))
            run.next()
        }
        assertTrue(run.isBoss)
        run.timeout()
        assertTrue(run.last!!.timedOut)
        assertEquals(DungeonRun.MAX_HP - 1, run.hp)
    }

    @Test
    fun comodinesCuestanMonedas() {
        val run = DungeonRun.start(bank, PcapState(), Random(5))
        assertFalse(run.fiftyFifty()) // sin monedas
        repeat(2) {
            run.answer(right(run.current))
            run.next()
        }
        assertEquals(20, run.coins)
        val q = run.current
        if (!q.multi && q.options.size >= 3) {
            assertTrue(run.fiftyFifty())
            assertEquals(20 - DungeonRun.FIFTY_COST, run.coins)
            assertTrue(run.hidden.isNotEmpty() && run.hidden.none { it in q.answer })
            assertFalse(run.fiftyFifty()) // una vez por pregunta
        }
        assertFalse(run.heal()) // vidas llenas
    }

    @Test
    fun bugRushMultiplicaLosAciertosSeguidos() {
        val game = RushGame(RushGame.pool(bank), Random(6))
        repeat(200) {
            val card = game.card
            assertEquals(card.isAnswer, card.option in card.question.answer)
        }
        repeat(RushGame.COMBO_STEP) { game.judge(game.card.isAnswer) }
        assertEquals(RushGame.COMBO_STEP, game.score)
        assertEquals(2, game.multiplier)
        game.judge(game.card.isAnswer)
        assertEquals(RushGame.COMBO_STEP + 2, game.score)
        assertFalse(game.judge(!game.card.isAnswer))
        assertEquals(0, game.combo)
        assertEquals(RushGame.PENALTY_SECONDS, game.penalty)
        assertEquals(RushGame.COMBO_STEP + 1, game.bestCombo)
        assertTrue(RushGame.pool(bank).all { it.code != null && !it.multi })
    }

    @Test
    fun recordsViajanYSeFusionanConElMaximo() {
        val a = PcapState()
        val run = DungeonRun.start(bank, a, Random(7))
        run.answer(right(run.current))
        a.app.game.recordRun(run)
        assertTrue(a.app.game.recordRush(12))
        assertFalse(a.app.game.recordRush(3))
        val again = PcapState.fromJson(a.toJson().toString())
        assertEquals(1, again.app.game.runs)
        assertEquals(10, again.app.game.bestScore)
        assertEquals(12, again.app.game.bestRush)

        val b = PcapState().apply { app.game.recordRush(20) }
        again.merge(b)
        assertEquals(20, again.app.game.bestRush)
        assertEquals(10, again.app.game.bestScore)
    }
}
