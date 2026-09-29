package io.github.marbi8891.pld.ui

import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableLongStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.semantics.LiveRegionMode
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.heading
import androidx.compose.ui.semantics.liveRegion
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import io.github.marbi8891.pld.AppModel
import io.github.marbi8891.pld.pcap.Mock
import io.github.marbi8891.pld.pcap.MockAction
import io.github.marbi8891.pld.pcap.MockUiState
import kotlinx.coroutines.delay

/**
 * Simulacro cronometrado (ADR-0024): se responde sin ver la corrección, se puede ir y volver entre
 * preguntas y al entregar (o al acabarse el tiempo) se corrige todo y se revisan los fallos.
 * Si sales a mitad, el simulacro sigue en marcha y lo retomas al volver a entrar.
 */
@Composable
fun MockScreen(model: AppModel, onBack: () -> Unit) {
    val course = model.course
    val vm: MockViewModel = viewModel(key = "simulacro-${course.id}") { MockViewModel(model, course) }
    // Al entrar de nuevo tras terminar, empieza uno nuevo; a mitad, se retoma el que estaba en marcha
    remember { if (vm.state.value.finished) vm.restart() }
    val state by vm.state.collectAsState()
    val lang = remember(model.revision) { model.pcap.lang }
    val scroll = rememberScrollState()
    var now by remember { mutableLongStateOf(System.currentTimeMillis()) }

    // Reloj: al llegar a cero se entrega solo
    LaunchedEffect(state.finished, state.deadline) {
        while (!vm.state.value.finished) {
            now = System.currentTimeMillis()
            if (vm.state.value.secondsLeft(now) == 0) vm.onAction(MockAction.Finish(now))
            delay(1_000)
        }
    }
    LaunchedEffect(state.index, state.finished) { scroll.scrollTo(0) }

    Scaffold(containerColor = MaterialTheme.colorScheme.background) { padding ->
        Column(
            Modifier
                .fillMaxSize()
                .padding(padding)
                .verticalScroll(scroll)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp),
        ) {
            TextButton(onClick = onBack) { Text(if (state.finished) "← Volver" else "← Salir (el tiempo sigue)") }
            Text(
                "Simulacro · ${course.title}",
                modifier = Modifier.semantics { heading() },
                style = MaterialTheme.typography.headlineSmall,
            )
            if (state.finished) {
                MockResult(model, state, lang, onRestart = vm::restart, onBack = onBack)
            } else {
                MockQuestion(state, lang, now, onAction = vm::onAction)
            }
        }
    }

    if (state.confirming) {
        AlertDialog(
            onDismissRequest = { vm.onAction(MockAction.CancelSubmit) },
            title = { Text("¿Entregar el simulacro?") },
            text = {
                Text(
                    "Tienes ${state.unanswered} ${if (state.unanswered == 1) "pregunta" else "preguntas"} sin responder. " +
                        "Contarán como falladas.",
                )
            },
            confirmButton = { TextButton(onClick = { vm.onAction(MockAction.Finish(System.currentTimeMillis())) }) { Text("Entregar") } },
            dismissButton = { TextButton(onClick = { vm.onAction(MockAction.CancelSubmit) }) { Text("Seguir respondiendo") } },
        )
    }
}

@Composable
private fun MockQuestion(state: MockUiState, lang: String, now: Long, onAction: (MockAction) -> Unit) {
    val palette = LocalPalette.current
    val question = state.currentQuestion ?: return
    val left = state.secondsLeft(now)

    Row(verticalAlignment = Alignment.CenterVertically) {
        Text(
            "Pregunta ${state.index + 1} de ${state.questions.size} · ${state.answered} respondidas",
            modifier = Modifier.weight(1f),
            color = palette.muted,
        )
        Text(
            clock(left),
            modifier = Modifier.semantics { contentDescription = "Tiempo restante: ${left / 60} minutos y ${left % 60} segundos" },
            color = if (left <= 300) palette.danger else MaterialTheme.colorScheme.onBackground,
            fontWeight = FontWeight.Bold,
            style = MaterialTheme.typography.titleLarge,
        )
    }
    // Avisos para TalkBack solo al cruzar 10, 5 y 1 minutos, como en la web
    val warning = when {
        left in 1..60 -> "Queda 1 minuto."
        left in 61..300 -> "Quedan 5 minutos."
        left in 301..600 -> "Quedan 10 minutos."
        else -> ""
    }
    if (warning.isNotEmpty()) {
        Text(warning, modifier = Modifier.semantics { liveRegion = LiveRegionMode.Polite }, color = palette.danger)
    }

    QuestionInput(question, lang, state.answers[state.index], reveal = false) { onAction(MockAction.ChangeAnswer(it)) }

    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
        OutlinedButton(onClick = { onAction(MockAction.GoTo(state.index - 1)) }, enabled = state.index > 0) { Text("← Anterior") }
        if (state.index < state.questions.size - 1) {
            Button(onClick = { onAction(MockAction.GoTo(state.index + 1)) }) { Text("Siguiente →") }
        }
    }

    // Ir directamente a cualquier pregunta; las respondidas llevan una marca
    Text("Ir a la pregunta", style = MaterialTheme.typography.labelLarge, color = palette.muted)
    Row(Modifier.horizontalScroll(rememberScrollState()), horizontalArrangement = Arrangement.spacedBy(6.dp)) {
        state.questions.indices.forEach { i ->
            val done = state.questions[i].let { q -> q.isComplete(state.answers[i]) }
            val label = "${i + 1}${if (done) " ✓" else ""}"
            val description = "Pregunta ${i + 1}, ${if (done) "respondida" else "sin responder"}"
            if (i == state.index) {
                Button(onClick = {}, modifier = Modifier.semantics { contentDescription = "$description, actual" }) { Text(label) }
            } else {
                OutlinedButton(onClick = { onAction(MockAction.GoTo(i)) }, modifier = Modifier.semantics { contentDescription = description }) {
                    Text(label)
                }
            }
        }
    }

    Button(onClick = { onAction(MockAction.Submit(System.currentTimeMillis())) }, modifier = Modifier.fillMaxWidth()) {
        Text("Entregar y corregir")
    }
}

@Composable
private fun MockResult(model: AppModel, state: MockUiState, lang: String, onRestart: () -> Unit, onBack: () -> Unit) {
    val palette = LocalPalette.current
    val result = state.result ?: return
    Panel(borderColor = if (state.passed) palette.accent else palette.danger) {
        Text(
            "${result.score} % · ${if (state.passed) "Aprobado" else "No aprobado"}",
            modifier = Modifier.semantics { liveRegion = LiveRegionMode.Polite },
            style = MaterialTheme.typography.displaySmall,
            color = if (state.passed) palette.accent else palette.danger,
        )
        Text(
            "${result.correct} de ${result.total} correctas en ${clock(result.seconds)}. Para aprobar hace falta un ${state.pass} %. +${result.correct} XP.",
            color = palette.muted,
        )
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Button(onClick = onRestart) { Text("Otro simulacro") }
            OutlinedButton(onClick = onBack) { Text("Volver") }
        }
    }

    Panel {
        SectionTitle("Por bloques")
        model.bank.exam.blocks.forEach { block ->
            val tally = result.blocks[block.slug] ?: return@forEach
            val rate = if (tally[1] == 0) null else tally[0].toDouble() / tally[1]
            Text("${block.title.es}: ${tally[0]} de ${tally[1]}", style = MaterialTheme.typography.bodyMedium)
            Meter(rate, "Acierto en ${block.title.es}")
        }
    }

    val failed = state.questions.indices.filter { !Mock.isRight(state.questions[it], state.answers[it]) }
    if (failed.isEmpty()) {
        Text("¡Sin fallos! Todas correctas.", color = palette.accent, fontWeight = FontWeight.Bold)
    } else {
        SectionTitle("Revisa tus fallos (${failed.size})")
        failed.forEach { i ->
            val question = state.questions[i]
            Panel(borderColor = palette.danger) {
                Text(
                    if (question.isComplete(state.answers[i])) "Pregunta ${i + 1}" else "Pregunta ${i + 1} · sin responder",
                    color = palette.muted,
                )
                QuestionInput(question, lang, state.answers[i], reveal = true) {}
                RichText(question.explain.get(lang))
            }
        }
    }
}

/** 125 → «02:05». */
private fun clock(seconds: Int): String = "%02d:%02d".format(seconds / 60, seconds % 60)
