package io.github.marbi8891.pld.pcap

import java.time.Instant
import kotlin.math.floor
import kotlin.math.roundToInt
import kotlin.random.Random

/*
 * Simulacro cronometrado (ADR-0024). Mismas reglas que el de la web (frontend/js/pcap.js):
 * preguntas por bloque según el examen, se corrige todo al entregar o al acabar el tiempo,
 * las no respondidas cuentan como falladas y el resultado se guarda en `exams`, que se sincroniza.
 * Flujo de datos en un solo sentido, como la práctica (ADR-0018): [reduce] no tiene efectos.
 */

/** Cuántas preguntas de cada bloque, cuántos minutos y qué nota hace falta. */
data class MockPlan(val perBlock: Map<String, Int>, val minutes: Int, val pass: Int) {
    val total: Int get() = perBlock.values.sum()
}

object Mock {
    /** Cursos de DAW sin examen oficial: un simulacro tipo examen del centro. ASSUMPTION (ADR-0024). */
    const val COURSE_QUESTIONS = 30
    const val SECONDS_PER_QUESTION = 90
    const val COURSE_PASS = 50

    fun plan(bank: Bank): MockPlan {
        val exam = bank.exam
        val available = bank.exam.blocks.associate { b -> b.slug to bank.questions.count { it.block == b.slug } }
        if (exam.questions > 0) {
            // Examen oficial (PCAP): el reparto del propio examen
            return MockPlan(exam.blocks.associate { it.slug to minOf(it.items, available.getValue(it.slug)) }, exam.minutes, exam.pass)
        }
        val total = minOf(COURSE_QUESTIONS, bank.questions.size)
        val perBlock = share(total, exam.blocks.map { it.slug to it.weight }, available)
        return MockPlan(perBlock, maxOf(1, (perBlock.values.sum() * SECONDS_PER_QUESTION) / 60), COURSE_PASS)
    }

    /**
     * Reparte [total] preguntas según el peso de cada bloque (método del mayor resto), sin pedir a un
     * bloque más preguntas de las que tiene. Suma exactamente [total] si hay preguntas suficientes.
     */
    fun share(total: Int, weights: List<Pair<String, Int>>, available: Map<String, Int>): Map<String, Int> {
        val sum = weights.sumOf { it.second }.coerceAtLeast(1)
        val exact = weights.associate { (slug, w) -> slug to total.toDouble() * w / sum }
        val counts = exact.mapValues { (slug, v) -> minOf(floor(v).toInt(), available[slug] ?: 0) }.toMutableMap()
        var left = total - counts.values.sum()
        // Primero los bloques con mayor parte decimal (y, a igualdad, más peso); vueltas hasta repartirlo todo
        val order = weights
            .sortedWith(compareByDescending<Pair<String, Int>> { exact.getValue(it.first) - floor(exact.getValue(it.first)) }.thenByDescending { it.second })
            .map { it.first }
        while (left > 0) {
            var added = false
            for (slug in order) {
                if (left == 0) break
                if (counts.getValue(slug) < (available[slug] ?: 0)) {
                    counts[slug] = counts.getValue(slug) + 1
                    left--
                    added = true
                }
            }
            if (!added) break // no quedan preguntas en ningún bloque
        }
        return weights.associate { (slug, _) -> slug to counts.getValue(slug) }
    }

    /** Preguntas al azar de cada bloque, mezcladas entre sí, como en la web. */
    fun build(bank: Bank, plan: MockPlan, random: Random = Random.Default): List<Question> =
        bank.exam.blocks
            .flatMap { b -> bank.questions.filter { it.block == b.slug }.shuffled(random).take(plan.perBlock[b.slug] ?: 0) }
            .shuffled(random)

    /** Bien respondida: completa y correcta. Una sin responder cuenta como fallada. */
    fun isRight(question: Question, answer: Answer): Boolean = question.isComplete(answer) && question.isCorrect(answer)

    /** Corrige el simulacro. Las no respondidas cuentan como falladas. */
    fun grade(questions: List<Question>, answers: List<Answer>, seconds: Int, now: Instant = Instant.now()): ExamResult {
        val blocks = linkedMapOf<String, MutableList<Int>>()
        var correct = 0
        questions.forEachIndexed { i, q ->
            val answer = answers.getOrElse(i) { Answer() }
            val ok = isRight(q, answer)
            if (ok) correct++
            val tally = blocks.getOrPut(q.block) { mutableListOf(0, 0) }
            tally[0] += if (ok) 1 else 0
            tally[1] += 1
        }
        val total = questions.size
        val score = if (total == 0) 0 else (correct * 100.0 / total).roundToInt()
        return ExamResult(PcapState.iso(now), correct, total, score, seconds, blocks)
    }
}

data class MockUiState(
    val questions: List<Question> = emptyList(),
    val answers: List<Answer> = emptyList(),
    val index: Int = 0,
    val minutes: Int = 0,
    val pass: Int = 0,
    /** Instante (ms) en que empezó y en que se acaba el tiempo. */
    val startedAt: Long = 0,
    val deadline: Long = 0,
    val result: ExamResult? = null,
    /** Pide confirmación al entregar con preguntas sin responder. */
    val confirming: Boolean = false,
) {
    val currentQuestion: Question? get() = questions.getOrNull(index)
    val finished: Boolean get() = result != null
    val answered: Int get() = questions.indices.count { questions[it].isComplete(answers[it]) }
    val unanswered: Int get() = questions.size - answered
    val passed: Boolean get() = (result?.score ?: 0) >= pass

    fun secondsLeft(now: Long): Int = maxOf(0L, (deadline - now + 999) / 1000).toInt()

    companion object {
        fun start(questions: List<Question>, plan: MockPlan, now: Long): MockUiState = MockUiState(
            questions = questions,
            answers = List(questions.size) { Answer() },
            minutes = plan.minutes,
            pass = plan.pass,
            startedAt = now,
            deadline = now + plan.minutes * 60_000L,
        )
    }
}

sealed interface MockAction {
    data class ChangeAnswer(val answer: Answer) : MockAction

    data class GoTo(val index: Int) : MockAction

    /** Pulsar «Entregar»: si faltan respuestas, primero pide confirmación. */
    data class Submit(val now: Long) : MockAction

    data object CancelSubmit : MockAction

    /** Entregar ya (confirmado o fin del tiempo). */
    data class Finish(val now: Long, val instant: Instant = Instant.ofEpochMilli(now)) : MockAction
}

fun MockUiState.reduce(action: MockAction): MockUiState {
    if (finished) return this
    return when (action) {
        is MockAction.ChangeAnswer ->
            if (currentQuestion == null) this else copy(answers = answers.toMutableList().also { it[index] = action.answer })
        is MockAction.GoTo -> copy(index = action.index.coerceIn(0, maxOf(0, questions.size - 1)), confirming = false)
        is MockAction.Submit -> if (unanswered > 0) copy(confirming = true) else reduce(MockAction.Finish(action.now))
        MockAction.CancelSubmit -> copy(confirming = false)
        is MockAction.Finish -> {
            val limit = minutes * 60
            val seconds = ((action.now - startedAt) / 1000).toInt().coerceIn(0, limit)
            copy(result = Mock.grade(questions, answers, seconds, action.instant), confirming = false, index = 0)
        }
    }
}
