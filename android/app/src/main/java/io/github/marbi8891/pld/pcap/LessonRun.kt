package io.github.marbi8891.pld.pcap

/**
 * Una lección de la ruta en curso. Como en Duolingo, la pregunta fallada vuelve al final
 * de la cola y la lección acaba cuando todas están acertadas.
 */
class LessonRun(questions: List<Question>) {
    private val queue = ArrayDeque(questions)
    val total = questions.size
    var mistakes = 0
        private set
    private val solved = mutableSetOf<String>()

    val current: Question? get() = queue.firstOrNull()
    val finished: Boolean get() = queue.isEmpty()
    val perfect: Boolean get() = finished && mistakes == 0

    /** Fracción completada (0-1) para la barra de progreso. */
    val progress: Float get() = if (total == 0) 1f else solved.size.toFloat() / total

    /** Registra la respuesta a la pregunta actual y pasa a la siguiente. */
    fun answer(ok: Boolean) {
        val question = queue.removeFirst()
        if (ok) {
            solved += question.id
        } else {
            mistakes++
            queue.addLast(question)
        }
    }
}
