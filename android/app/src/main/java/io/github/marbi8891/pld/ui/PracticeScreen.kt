package io.github.marbi8891.pld.ui

import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.selection.selectable
import androidx.compose.foundation.selection.selectableGroup
import androidx.compose.foundation.selection.toggleable
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.Checkbox
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.RadioButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.semantics.LiveRegionMode
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.heading
import androidx.compose.ui.semantics.liveRegion
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import io.github.marbi8891.pld.AppModel
import io.github.marbi8891.pld.pcap.Answer
import io.github.marbi8891.pld.pcap.Option
import io.github.marbi8891.pld.pcap.PracticeUserAction
import io.github.marbi8891.pld.pcap.Question
import kotlin.math.roundToInt

/**
 * Tanda de práctica de un bloque, con corrección y explicación inmediatas. El estado vive en
 * [PracticeViewModel] (flujo de datos en un solo sentido, ADR-0018): aquí solo se pinta y se envían acciones.
 */
@Composable
fun PracticeScreen(model: AppModel, blockSlug: String, onBack: () -> Unit, onTheory: (String) -> Unit) {
    val course = model.course
    val vm: PracticeViewModel = viewModel(key = "practica-${course.id}-$blockSlug") { PracticeViewModel(model, course, blockSlug) }
    val state by vm.state.collectAsState()
    val block = model.bank.block(blockSlug)
    val lang = remember(model.revision) { model.pcap.lang }
    val palette = LocalPalette.current
    val scroll = rememberScrollState()
    LaunchedEffect(state.index, state.round) { scroll.scrollTo(0) } // cada pregunta empieza arriba

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
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    "Práctica · ${block.title.es}",
                    modifier = Modifier
                        .weight(1f)
                        .semantics { heading() },
                    style = MaterialTheme.typography.headlineSmall,
                )
                Text(
                    "Racha: ${state.streak}",
                    modifier = Modifier.semantics { liveRegion = LiveRegionMode.Polite },
                    color = if (state.streak >= 3) palette.streak else palette.muted,
                    fontWeight = FontWeight.SemiBold,
                )
            }
            LinearProgressIndicator(
                progress = { state.progress },
                modifier = Modifier
                    .fillMaxWidth()
                    .semantics { contentDescription = "Progreso de la tanda: ${(state.progress * 100).roundToInt()} %" },
                color = palette.accent,
                trackColor = MaterialTheme.colorScheme.outline,
            )

            val question = state.currentQuestion
            if (state.isCompleted || question == null) {
                Panel {
                    SectionTitle("${state.score} de ${state.questions.size} correctas")
                    Text(
                        "+${state.score} XP · recuperas una vida · tu mejor racha: ${model.pcap.bestCombo} aciertos seguidos.",
                        color = palette.muted,
                    )
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        Button(onClick = { vm.onAction(PracticeUserAction.RestartSession) }) { Text("Otra tanda") }
                        OutlinedButton(onClick = onBack) { Text("Volver") }
                    }
                }
            } else {
                QuestionStep(
                    question = question,
                    number = state.index + 1,
                    total = state.questions.size,
                    lang = lang,
                    response = state.answer,
                    checked = state.isAnswerSubmitted,
                    message = state.message,
                    model = model,
                    onChange = { vm.onAction(PracticeUserAction.ChangeAnswer(it)) },
                    onCheck = { vm.onAction(PracticeUserAction.SubmitAnswer) },
                    onNext = { vm.onAction(PracticeUserAction.NextQuestion) },
                    onTheory = onTheory,
                )
            }

            // Solo el PCAP tiene las preguntas también en inglés, como el examen
            if (course.isPcap) LangSwitch(lang) { value -> model.update { this.lang = value } }
        }
    }
}

/** Una pregunta de la tanda: opciones, «Comprobar» y, tras corregir, la explicación y «Siguiente». */
@Composable
private fun QuestionStep(
    question: Question,
    number: Int,
    total: Int,
    lang: String,
    response: Answer,
    checked: Boolean,
    message: String,
    model: AppModel,
    onChange: (Answer) -> Unit,
    onCheck: () -> Unit,
    onNext: () -> Unit,
    onTheory: (String) -> Unit,
) {
    Column(verticalArrangement = Arrangement.spacedBy(16.dp)) {
        Text("Pregunta $number de $total", color = LocalPalette.current.muted)
        QuestionInput(question, lang, response, checked, onChange = onChange)
        if (checked) {
            Feedback(question, lang, question.isCorrect(response), model, onTheory)
            Button(onClick = onNext, modifier = Modifier.fillMaxWidth()) {
                Text(if (number < total) "Siguiente →" else "Ver resultado")
            }
        } else {
            Button(onClick = onCheck, modifier = Modifier.fillMaxWidth()) { Text("Comprobar") }
            if (message.isNotEmpty()) {
                Text(message, color = MaterialTheme.colorScheme.error, modifier = Modifier.semantics { liveRegion = LiveRegionMode.Assertive })
            }
        }
    }
}

/** Enunciado, código y opciones. Tras corregir, marca la correcta en verde y la elegida mal en rojo. */
@Composable
fun QuestionView(
    question: Question,
    lang: String,
    chosen: Set<Int>,
    reveal: Boolean,
    hidden: Set<Int> = emptySet(),
    onSelect: (Int) -> Unit,
) {
    val palette = LocalPalette.current
    val text = question.q.get(lang)
    // Las de «elige dos» ya lo dicen en el enunciado, como en el examen real
    val limit = if (question.multi && !Regex("\\((Elige|Choose)").containsMatchIn(text)) {
        if (lang == "en") " (Choose ${question.answer.size}.)" else " (Elige ${question.answer.size}.)"
    } else {
        ""
    }
    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
        RichText(text + limit, style = MaterialTheme.typography.titleMedium)
        question.code?.let { CodeBlock(it) }
        Column(Modifier.selectableGroup(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            question.options.forEachIndexed { i, option ->
                // Opciones descartadas por el comodín 50/50 del modo «Jugar»
                if (i in hidden) return@forEachIndexed
                val selected = i in chosen
                val border = when {
                    reveal && i in question.answer -> palette.accent
                    reveal && selected -> palette.danger
                    selected -> MaterialTheme.colorScheme.primary
                    else -> MaterialTheme.colorScheme.outline
                }
                val role = if (question.multi) Role.Checkbox else Role.RadioButton
                val rowModifier = if (question.multi) {
                    Modifier.toggleable(value = selected, enabled = !reveal, role = role, onValueChange = { onSelect(i) })
                } else {
                    Modifier.selectable(selected = selected, enabled = !reveal, role = role, onClick = { onSelect(i) })
                }
                Row(
                    Modifier
                        .fillMaxWidth()
                        .border(if (border == MaterialTheme.colorScheme.outline) 1.dp else 2.dp, border, CardShape)
                        .then(rowModifier)
                        .padding(horizontal = 8.dp, vertical = 6.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    if (question.multi) {
                        Checkbox(checked = selected, onCheckedChange = null, enabled = !reveal)
                    } else {
                        RadioButton(selected = selected, onClick = null, enabled = !reveal)
                    }
                    when (option) {
                        is Option.Code -> Text(option.source, Modifier.padding(start = 8.dp), fontFamily = FontFamily.Monospace)
                        is Option.Prose -> RichText(option.text.get(lang), Modifier.padding(start = 8.dp), MaterialTheme.typography.bodyLarge)
                    }
                }
            }
        }
    }
}

@Composable
private fun Feedback(question: Question, lang: String, ok: Boolean, model: AppModel, onTheory: (String) -> Unit) {
    val palette = LocalPalette.current
    Panel(borderColor = if (ok) palette.accent else palette.danger) {
        Text(
            if (ok) "¡Correcto!" else "No es correcta.",
            modifier = Modifier.semantics { liveRegion = LiveRegionMode.Polite },
            color = if (ok) palette.accent else palette.danger,
            fontWeight = FontWeight.Bold,
            style = MaterialTheme.typography.titleMedium,
        )
        RichText(question.explain.get(lang), color = Color.Unspecified)
        if (!ok) {
            // Del fallo a la teoría: la lección que lo explica
            val slug = question.lesson
            val title = slug?.let { model.lessons.titles[it] }
            if (slug != null && title != null) {
                TextButton(onClick = { onTheory(slug) }) { Text("Repasar la teoría: $title") }
            }
        }
    }
}
