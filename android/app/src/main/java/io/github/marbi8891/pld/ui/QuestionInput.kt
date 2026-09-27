package io.github.marbi8891.pld.ui

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardCapitalization
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import io.github.marbi8891.pld.pcap.Answer
import io.github.marbi8891.pld.pcap.Kind
import io.github.marbi8891.pld.pcap.Question
import kotlin.random.Random

/**
 * Pregunta de cualquier tipo (ADR-0017): test (también «encontrar el error»), completar el hueco u
 * ordenar líneas. Las pantallas solo guardan el [Answer] y preguntan a la pregunta si está bien.
 */
@Composable
fun QuestionInput(
    question: Question,
    lang: String,
    answer: Answer,
    reveal: Boolean,
    hidden: Set<Int> = emptySet(),
    onChange: (Answer) -> Unit,
) {
    when (question.kind) {
        Kind.CHOICE -> QuestionView(question, lang, answer.selected, reveal, hidden) { option ->
            val selected = when {
                !question.multi -> setOf(option)
                option in answer.selected -> answer.selected - option
                else -> answer.selected + option
            }
            onChange(answer.copy(selected = selected))
        }
        Kind.FILL -> FillInput(question, lang, answer, reveal, onChange)
        Kind.ORDER -> OrderInput(question, lang, answer, reveal, onChange)
    }
}

/** Completar el hueco: el código con `___` y un campo para escribir lo que falta. */
@Composable
private fun FillInput(question: Question, lang: String, answer: Answer, reveal: Boolean, onChange: (Answer) -> Unit) {
    val palette = LocalPalette.current
    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
        RichText(question.q.get(lang), style = MaterialTheme.typography.titleMedium)
        question.code?.let { CodeBlock(it) }
        OutlinedTextField(
            value = answer.text,
            onValueChange = { onChange(answer.copy(text = it)) },
            enabled = !reveal,
            singleLine = true,
            label = { Text("Lo que va en ___") },
            textStyle = TextStyle(fontFamily = FontFamily.Monospace, fontSize = 16.sp),
            // Sin autocorrector ni mayúscula inicial: estropearían el código
            keyboardOptions = KeyboardOptions(
                capitalization = KeyboardCapitalization.None,
                autoCorrectEnabled = false,
                keyboardType = KeyboardType.Ascii,
            ),
            modifier = Modifier.fillMaxWidth(),
        )
        if (reveal && !question.isCorrect(answer)) {
            Text("Solución: ${question.accept.first()}", color = palette.accent, fontFamily = FontFamily.Monospace, fontWeight = FontWeight.Bold)
        }
    }
}

/**
 * Ordenar líneas (problema de Parsons): se tocan las líneas disponibles en el orden correcto y se
 * tocan las ya puestas para quitarlas. Sin arrastrar, para que funcione igual con TalkBack.
 */
@Composable
private fun OrderInput(question: Question, lang: String, answer: Answer, reveal: Boolean, onChange: (Answer) -> Unit) {
    val palette = LocalPalette.current
    // Orden de presentación estable para cada pregunta y nunca ya resuelto
    val shuffled = remember(question.id) {
        val indices = question.lines.indices.toList()
        val mixed = indices.shuffled(Random(question.id.hashCode()))
        if (mixed == indices) indices.reversed() else mixed
    }
    val context = question.code?.lines().orEmpty()
    val slot = context.indexOfFirst { it.trim() == "___" }
    val before = if (slot >= 0) context.take(slot) else emptyList()
    val after = if (slot >= 0) context.drop(slot + 1) else emptyList()
    val correct = reveal && question.isCorrect(answer)

    Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
        RichText(question.q.get(lang), style = MaterialTheme.typography.titleMedium)
        if (before.isNotEmpty()) CodeBlock(before.joinToString("\n"))
        Text("Tu programa · toca una línea para quitarla", style = MaterialTheme.typography.labelLarge, color = palette.muted)
        Panel(borderColor = if (!reveal) MaterialTheme.colorScheme.outline else if (correct) palette.accent else palette.danger) {
            if (answer.order.isEmpty()) Text("Toca las líneas de abajo en orden.", color = palette.muted)
            answer.order.forEachIndexed { position, index ->
                CodeLine(
                    text = question.lines[index],
                    description = "Línea ${position + 1}: ${question.lines[index].trim()}. Toca para quitarla.",
                    enabled = !reveal,
                ) { onChange(answer.copy(order = answer.order - index)) }
            }
        }
        if (after.isNotEmpty()) CodeBlock(after.joinToString("\n"))
        val available = shuffled.filter { it !in answer.order }
        if (available.isNotEmpty()) {
            Text("Líneas disponibles · toca para añadir", style = MaterialTheme.typography.labelLarge, color = palette.muted)
            available.forEach { index ->
                CodeLine(
                    text = question.lines[index],
                    description = "${question.lines[index].trim()}. Toca para añadirla al final.",
                    enabled = !reveal,
                ) { onChange(answer.copy(order = answer.order + index)) }
            }
        }
        if (reveal && !correct) {
            Text("Solución:", color = palette.accent, fontWeight = FontWeight.Bold)
            CodeBlock(question.lines.joinToString("\n"))
        }
    }
}

@Composable
private fun CodeLine(text: String, description: String, enabled: Boolean, onClick: () -> Unit) {
    Surface(
        color = LocalPalette.current.codeBg,
        contentColor = LocalPalette.current.codeText,
        shape = CardShape,
        modifier = Modifier
            .fillMaxWidth()
            .clickable(enabled = enabled, role = Role.Button, onClick = onClick)
            .semantics { contentDescription = description },
    ) {
        Text(text, modifier = Modifier.padding(horizontal = 12.dp, vertical = 10.dp), fontFamily = FontFamily.Monospace, fontSize = 14.sp)
    }
}
