package io.github.marbi8891.pld.pcap

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.File

/** Práctica con flujo de datos en un solo sentido (ADR-0018): solo transiciones, sin efectos. */
class PracticeTest {
    private val bank = Bank.parse(File("../../frontend/data/pcap.json").readText())
    private val single = bank.questions.first { !it.multi }
    private val multi = bank.questions.first { it.multi }

    private fun right(q: Question) = Answer(selected = q.answer.toSet())

    private fun wrong(q: Question) = Answer(selected = setOf(q.options.indices.first { it !in q.answer }))

    @Test
    fun comprobarSinResponderAvisaYNoCorrige() {
        val start = PracticeUiState("poo", listOf(multi))
        val after = start.reduce(PracticeUserAction.SubmitAnswer) { emptyList() }
        assertFalse(after.isAnswerSubmitted)
        assertEquals("Elige ${multi.answer.size} respuestas.", after.message)
        // Al cambiar la respuesta, el aviso desaparece
        assertEquals("", after.reduce(PracticeUserAction.ChangeAnswer(wrong(multi))) { emptyList() }.message)
    }

    @Test
    fun aciertosRachaYProgreso() {
        var s = PracticeUiState("x", listOf(single, single, single))
        fun act(a: PracticeUserAction) {
            s = s.reduce(a) { emptyList() }
        }
        act(PracticeUserAction.ChangeAnswer(right(single)))
        act(PracticeUserAction.SubmitAnswer)
        assertTrue(s.isAnswerSubmitted && s.isCorrect)
        assertEquals(1, s.streak)
        assertEquals(1f / 3, s.progress, 1e-6f)
        // Una vez corregida, la respuesta no cambia ni se vuelve a puntuar
        act(PracticeUserAction.ChangeAnswer(wrong(single)))
        act(PracticeUserAction.SubmitAnswer)
        assertEquals(1, s.score)
        act(PracticeUserAction.NextQuestion)
        assertEquals(Answer(), s.answer)

        act(PracticeUserAction.ChangeAnswer(wrong(single)))
        act(PracticeUserAction.SubmitAnswer)
        assertFalse(s.isCorrect)
        assertEquals(0, s.streak)
        act(PracticeUserAction.NextQuestion)
        act(PracticeUserAction.ChangeAnswer(right(single)))
        act(PracticeUserAction.SubmitAnswer)
        act(PracticeUserAction.NextQuestion)
        assertTrue(s.isCompleted)
        assertEquals(2, s.score)
        assertEquals(1f, s.progress, 1e-6f)
    }

    @Test
    fun siguienteSoloTrasCorregirYReiniciarEmpiezaDeCero() {
        val s = PracticeUiState("x", listOf(single, single), score = 1, streak = 1)
        assertEquals(s, s.reduce(PracticeUserAction.NextQuestion) { emptyList() })
        val again = s.reduce(PracticeUserAction.RestartSession) { listOf(multi) }
        assertEquals(listOf(multi), again.questions)
        assertEquals(0, again.score)
        assertEquals(1, again.round)
    }
}
