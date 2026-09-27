package io.github.marbi8891.pld.pcap

/*
 * Práctica libre por bloque con flujo de datos en un solo sentido (ADR-0018):
 * la pantalla pinta un [PracticeUiState] y envía [PracticeUserAction]; [reduce] calcula el estado
 * siguiente sin efectos. Guardar respuestas, XP y vidas lo hace el PracticeViewModel.
 */

data class PracticeUiState(
    val block: String,
    val questions: List<Question> = emptyList(),
    val index: Int = 0,
    /** Respuesta en curso: opciones marcadas, texto del hueco o líneas ordenadas. */
    val answer: Answer = Answer(),
    val isAnswerSubmitted: Boolean = false,
    val isCorrect: Boolean = false,
    /** Aciertos de la tanda. */
    val score: Int = 0,
    /** Aciertos seguidos en la tanda. */
    val streak: Int = 0,
    /** Aviso si se intenta comprobar sin haber respondido. */
    val message: String = "",
    val round: Int = 0,
) {
    val currentQuestion: Question? get() = questions.getOrNull(index)
    val isCompleted: Boolean get() = questions.isNotEmpty() && index >= questions.size

    /** Parte de la tanda ya respondida, de 0 a 1. */
    val progress: Float
        get() = if (questions.isEmpty()) 0f else (index + if (isAnswerSubmitted) 1 else 0).toFloat() / questions.size
}

sealed interface PracticeUserAction {
    data class ChangeAnswer(val answer: Answer) : PracticeUserAction

    data object SubmitAnswer : PracticeUserAction

    data object NextQuestion : PracticeUserAction

    data object RestartSession : PracticeUserAction
}

/** Estado siguiente. [newSet] da las preguntas de una tanda nueva (empieza por las falladas). */
fun PracticeUiState.reduce(action: PracticeUserAction, newSet: () -> List<Question>): PracticeUiState {
    val question = currentQuestion
    return when (action) {
        is PracticeUserAction.ChangeAnswer ->
            if (isAnswerSubmitted || question == null) this else copy(answer = action.answer, message = "")
        PracticeUserAction.SubmitAnswer -> when {
            isAnswerSubmitted || question == null -> this
            !question.isComplete(answer) -> copy(message = missing(question))
            else -> {
                val ok = question.isCorrect(answer)
                copy(
                    isAnswerSubmitted = true,
                    isCorrect = ok,
                    score = score + if (ok) 1 else 0,
                    streak = if (ok) streak + 1 else 0,
                    message = "",
                )
            }
        }
        PracticeUserAction.NextQuestion ->
            if (!isAnswerSubmitted) this else copy(index = index + 1, answer = Answer(), isAnswerSubmitted = false, isCorrect = false)
        PracticeUserAction.RestartSession -> PracticeUiState(block = block, questions = newSet(), round = round + 1)
    }
}

private fun missing(question: Question): String = when {
    question.kind == Kind.FILL -> "Escribe lo que va en el hueco."
    question.kind == Kind.ORDER -> "Coloca todas las líneas."
    question.multi -> "Elige ${question.answer.size} respuestas."
    else -> "Elige una respuesta."
}
