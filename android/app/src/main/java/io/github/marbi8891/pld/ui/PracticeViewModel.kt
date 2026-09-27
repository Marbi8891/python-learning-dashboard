package io.github.marbi8891.pld.ui

import androidx.lifecycle.ViewModel
import io.github.marbi8891.pld.AppModel
import io.github.marbi8891.pld.CourseData
import io.github.marbi8891.pld.pcap.AppProgress
import io.github.marbi8891.pld.pcap.PracticeUiState
import io.github.marbi8891.pld.pcap.PracticeUserAction
import io.github.marbi8891.pld.pcap.reduce
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

/**
 * Tanda de práctica de un bloque (ADR-0018). La pantalla envía acciones; el estado lo calcula
 * [reduce] (sin efectos, con tests) y aquí solo se aplican los efectos: guardar la respuesta,
 * la XP y la vida recuperada al terminar. Sobrevive a abrir la teoría y volver.
 */
class PracticeViewModel(private val model: AppModel, private val course: CourseData, block: String) : ViewModel() {
    private val _state = MutableStateFlow(PracticeUiState(block, course.state.practiceSet(course.bank, block)))
    val state: StateFlow<PracticeUiState> = _state.asStateFlow()

    fun onAction(action: PracticeUserAction) {
        val before = _state.value
        val after = before.reduce(action) { course.state.practiceSet(course.bank, before.block) }
        _state.value = after

        val question = before.currentQuestion
        if (question != null && after.isAnswerSubmitted && !before.isAnswerSubmitted) {
            val ok = after.isCorrect
            val streak = after.streak
            model.update {
                recordAnswer(question.id, ok)
                bestCombo = maxOf(bestCombo, streak)
                if (ok) app.addXp(AppProgress.XP_PRACTICE)
            }
        }
        // Terminar una tanda de práctica libre devuelve una vida (ADR-0012)
        if (after.isCompleted && !before.isCompleted) model.update { app.gainHeart() }
    }
}
