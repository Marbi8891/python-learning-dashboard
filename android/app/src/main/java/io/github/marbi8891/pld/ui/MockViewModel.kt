package io.github.marbi8891.pld.ui

import androidx.lifecycle.ViewModel
import io.github.marbi8891.pld.AppModel
import io.github.marbi8891.pld.CourseData
import io.github.marbi8891.pld.pcap.AppProgress
import io.github.marbi8891.pld.pcap.Mock
import io.github.marbi8891.pld.pcap.MockAction
import io.github.marbi8891.pld.pcap.MockUiState
import io.github.marbi8891.pld.pcap.PcapState
import io.github.marbi8891.pld.pcap.reduce
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

/**
 * Simulacro en curso (ADR-0024). El estado lo calcula [reduce] (sin efectos, con tests); aquí solo se
 * guarda el resultado al terminar: cada respuesta al repaso espaciado y el simulacro en `exams`,
 * el mismo campo que usa la web, así que cuenta para «Listo para examinarte» y se sincroniza.
 */
class MockViewModel(private val model: AppModel, private val course: CourseData) : ViewModel() {
    val plan = Mock.plan(course.bank)

    private val _state = MutableStateFlow(newSession())
    val state: StateFlow<MockUiState> = _state.asStateFlow()

    fun onAction(action: MockAction) {
        val before = _state.value
        val after = before.reduce(action)
        _state.value = after
        val result = after.result
        if (result != null && before.result == null) {
            model.update {
                after.questions.forEachIndexed { i, q -> recordAnswer(q.id, Mock.isRight(q, after.answers[i])) }
                exams.add(result)
                while (exams.size > PcapState.MAX_EXAMS) exams.removeAt(0)
                app.addXp(result.correct * AppProgress.XP_PRACTICE)
            }
        }
    }

    /** Empieza otro simulacro con preguntas nuevas. */
    fun restart() {
        _state.value = newSession()
    }

    private fun newSession(): MockUiState = MockUiState.start(Mock.build(course.bank, plan), plan, System.currentTimeMillis())
}
