package io.github.marbi8891.pld.ui

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.semantics.heading
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.unit.dp
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.lifecycle.ViewModelProvider
import io.github.marbi8891.pld.AppModel
import io.github.marbi8891.pld.pcap.Answer
import io.github.marbi8891.pld.pcap.LessonRun
import io.github.marbi8891.pld.pcap.Question
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.update

data class LearningSessionState(
    val questions: List<Question>,
    val current: Question?,
    val index: Int,
    val checked: Boolean = false,
    val answer: Answer = Answer(),
    val correct: Boolean? = null,
    val finished: Boolean = false,
)

class LearningSessionViewModel(
    private val model: AppModel,
    startQuestionId: String,
) : ViewModel() {
    private val seed = model.bank.questions
    private val start = seed.firstOrNull { it.id == startQuestionId }
    private val selected = buildList {
        if (start != null) add(start)
        val pool = seed.filter { it.id != startQuestionId }
        addAll(
            pool.sortedWith(
                compareBy<Question> {
                    when {
                        model.pcap.dueIds(listOf(it.id)).isNotEmpty() -> 0
                        model.pcap.answers[it.id]?.lastOrNull() == false -> 1
                        it.id !in model.pcap.answers -> 2
                        else -> 3
                    }
                }.thenBy { it.id }
            ).take(4)
        )
    }
    private val run = LessonRun(selected)
    private val _state = MutableStateFlow(LearningSessionState(selected, run.current, 0))
    val state: StateFlow<LearningSessionState> = _state

    fun change(answer: Answer) {
        if (!_state.value.checked) _state.update { it.copy(answer = answer) }
    }

    fun check() {
        val state = _state.value
        val question = state.current ?: return
        if (!question.isComplete(state.answer)) return
        val ok = question.isCorrect(state.answer)
        model.update { recordAnswer(question.id, ok) }
        run.answer(ok)
        _state.value = state.copy(checked = true, correct = ok)
    }

    fun next() {
        if (!_state.value.checked) return
        val current = run.current
        if (current == null) {
            _state.value = _state.value.copy(current = null, finished = true)
            return
        }
        _state.value = LearningSessionState(_state.value.questions, current, _state.value.index + 1)
    }
}

class LearningSessionVmFactory(
    private val model: AppModel,
    private val questionId: String,
) : ViewModelProvider.Factory {
    @Suppress("UNCHECKED_CAST")
    override fun <T : ViewModel> create(modelClass: Class<T>): T =
        LearningSessionViewModel(model, questionId) as T
}

@Composable
fun LearningPracticeScreen(model: AppModel, questionId: String, onBack: () -> Unit) {
    val vm: LearningSessionViewModel = viewModel(
        key = "learning-${questionId}-${model.revision}",
        factory = LearningSessionVmFactory(model, questionId),
    )
    val state by vm.state.collectAsState()
    val scroll = rememberScrollState()

    LaunchedEffect(state.current?.id, state.checked) { scroll.scrollTo(0) }

    Scaffold(containerColor = MaterialTheme.colorScheme.background) { padding ->
        Column(
            Modifier
                .fillMaxSize()
                .padding(padding)
                .verticalScroll(scroll)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp),
        ) {
            TextButton(onClick = onBack) { Text("← Volver") }

            if (state.finished) {
                Panel {
                    Text("Sesión terminada", style = MaterialTheme.typography.headlineSmall)
                    Text("Has completado la sesión adaptativa.")
                    Button(onClick = onBack, modifier = Modifier.fillMaxWidth()) { Text("Volver a Aprender") }
                }
            } else {
                Text(
                    "Práctica · ${state.index + 1}",
                    style = MaterialTheme.typography.headlineSmall,
                    modifier = Modifier.semantics { heading() },
                )
                LinearProgressIndicator(
                    progress = {
                        (state.index.toFloat() / state.questions.size.coerceAtLeast(1)).coerceIn(0f, 1f)
                    },
                    modifier = Modifier.fillMaxWidth(),
                )

                state.current?.let { question ->
                    QuestionInput(
                        question = question,
                        lang = model.pcap.lang,
                        response = state.answer,
                        checked = state.checked,
                        onChange = vm::change,
                    )

                    if (state.checked) {
                        Panel {
                            Text(
                                if (state.correct == true) "Correcto" else "Vamos a corregirlo",
                                color = if (state.correct == true) LocalPalette.current.accent else LocalPalette.current.danger,
                                modifier = Modifier.semantics { heading() },
                            )
                            RichText(question.explain.get(model.pcap.lang))
                            Button(onClick = vm::next, modifier = Modifier.fillMaxWidth()) {
                                Text(if (state.index + 1 >= state.questions.size) "Terminar" else "Siguiente")
                            }
                        }
                    } else {
                        Button(
                            onClick = vm::check,
                            enabled = question.isComplete(state.answer),
                            modifier = Modifier.fillMaxWidth(),
                        ) { Text("Comprobar") }
                    }
                }
            }
        }
    }
}
