package io.github.marbi8891.pld.ui

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.selection.selectable
import androidx.compose.foundation.selection.selectableGroup
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.RadioButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.semantics.LiveRegionMode
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.heading
import androidx.compose.ui.semantics.liveRegion
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import io.github.marbi8891.pld.AppModel
import io.github.marbi8891.pld.pcap.Challenge
import io.github.marbi8891.pld.pcap.LessonContent
import io.github.marbi8891.pld.pcap.MdBlock
import io.github.marbi8891.pld.pcap.QuizItem
import io.github.marbi8891.pld.pcap.parseBlocks

/**
 * Teoría de una lección dentro de la app, sin conexión (ADR-0014): explicación, ejemplo,
 * ejercicio, mini-quiz, reto, dudas frecuentes y fuentes. El contenido es el mismo que el de la web.
 */
@Composable
fun TheoryScreen(model: AppModel, slug: String, onBack: () -> Unit) {
    val lesson = model.content.getValue(slug)
    Scaffold(containerColor = MaterialTheme.colorScheme.background) { padding ->
        Column(
            Modifier
                .fillMaxSize()
                .padding(padding)
                .verticalScroll(rememberScrollState())
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp),
        ) {
            TextButton(onClick = onBack) { Text("← Volver") }
            Eyebrow(lesson.module)
            Text(
                lesson.title,
                modifier = Modifier.semantics { heading() },
                style = MaterialTheme.typography.headlineMedium,
                color = MaterialTheme.colorScheme.onBackground,
            )
            Markdown(lesson.theory)

            SectionTitle("Ejemplo")
            CodeBlock(lesson.exampleCode)
            Note("Para ejecutarlo, cópialo en tu editor. Ejecutar Python dentro de la app llegará en la entrega 5.")

            SectionTitle("Ejercicio")
            Markdown(lesson.exercise)
            if (lesson.starter.isNotBlank()) {
                Text("Punto de partida", style = MaterialTheme.typography.titleSmall)
                CodeBlock(lesson.starter)
            }
            lesson.hint?.let { Reveal("Ver pista") { Markdown(it) } }

            if (lesson.quiz.isNotEmpty()) {
                SectionTitle("Comprueba lo aprendido")
                lesson.quiz.forEachIndexed { i, item -> QuizCard(item, i + 1, lesson.quiz.size) }
            }

            lesson.challenge?.let { ChallengeSection(it) }

            if (lesson.faq.isNotEmpty()) {
                SectionTitle("Dudas frecuentes")
                lesson.faq.forEach { faq -> Reveal(faq.q) { Markdown(faq.a) } }
            }

            Sources(lesson)
        }
    }
}

/** Párrafos y listas del temario, con `código`, **negrita** y *cursiva*. */
@Composable
fun Markdown(text: String) {
    Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
        parseBlocks(text).forEach { block ->
            when (block) {
                is MdBlock.Paragraph -> RichText(block.text)
                is MdBlock.Bullets -> ListItems(block.items) { "•" }
                is MdBlock.Numbered -> ListItems(block.items) { "${it + 1}." }
            }
        }
    }
}

@Composable
private fun ListItems(items: List<String>, marker: (Int) -> String) {
    Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
        items.forEachIndexed { i, item ->
            Row {
                Text(marker(i), Modifier.width(24.dp), style = MaterialTheme.typography.bodyLarge)
                RichText(item, Modifier.weight(1f))
            }
        }
    }
}

@Composable
private fun Note(text: String) {
    Text(text, style = MaterialTheme.typography.bodySmall, color = LocalPalette.current.muted)
}

/** Contenido plegado (pistas y dudas): se abre al tocar, como <details> en la web. */
@Composable
private fun Reveal(label: String, content: @Composable () -> Unit) {
    var open by remember { mutableStateOf(false) }
    Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
        TextButton(onClick = { open = !open }) { Text((if (open) "▾ " else "▸ ") + label) }
        if (open) Column(Modifier.padding(start = 12.dp)) { content() }
    }
}

/** Pregunta del mini-quiz: se elige, se comprueba y se ve la explicación. No cuenta para la preparación. */
@Composable
private fun QuizCard(item: QuizItem, number: Int, total: Int) {
    var chosen by remember { mutableStateOf<Int?>(null) }
    var checked by remember { mutableStateOf(false) }
    val palette = LocalPalette.current
    val ok = chosen == item.answer
    Panel(borderColor = if (!checked) MaterialTheme.colorScheme.outline else if (ok) palette.accent else palette.danger) {
        Text("Pregunta $number de $total", style = MaterialTheme.typography.labelMedium, color = palette.muted)
        RichText(item.q, style = MaterialTheme.typography.titleMedium)
        item.code?.let { CodeBlock(it) }
        Column(Modifier.selectableGroup()) {
            item.options.forEachIndexed { i, option ->
                Row(
                    Modifier
                        .fillMaxWidth()
                        .selectable(selected = chosen == i, enabled = !checked, role = Role.RadioButton, onClick = { chosen = i })
                        .padding(vertical = 6.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    RadioButton(selected = chosen == i, onClick = null, enabled = !checked)
                    val color = when {
                        checked && i == item.answer -> palette.accent
                        checked && i == chosen -> palette.danger
                        else -> MaterialTheme.colorScheme.onSurface
                    }
                    RichText(option, Modifier.padding(start = 8.dp), color = color)
                }
            }
        }
        if (!checked) {
            Button(onClick = { checked = true }, enabled = chosen != null) { Text("Comprobar") }
        } else {
            Text(
                if (ok) "¡Correcto!" else "No es correcta.",
                modifier = Modifier.semantics { liveRegion = LiveRegionMode.Polite },
                color = if (ok) palette.accent else palette.danger,
                fontWeight = FontWeight.Bold,
            )
            Markdown(item.explain)
            OutlinedButton(onClick = {
                chosen = null
                checked = false
            }) { Text("Intentar de nuevo") }
        }
    }
}

@Composable
private fun ChallengeSection(challenge: Challenge) {
    val stars = "★".repeat(challenge.stars) + "☆".repeat((3 - challenge.stars).coerceAtLeast(0))
    SectionTitle("Reto extra: ${challenge.title}")
    Text(stars, color = MaterialTheme.colorScheme.primary, modifier = Modifier.semantics { contentDescription = "Dificultad ${challenge.stars} de 3" })
    Markdown(challenge.exercise)
    if (challenge.starter.isNotBlank()) CodeBlock(challenge.starter)
    challenge.hint?.let { Reveal("Ver pista del reto") { Markdown(it) } }
}

/** Solo los títulos: la app no abre enlaces para funcionar entera sin conexión. */
@Composable
private fun Sources(lesson: LessonContent) {
    if (lesson.sources.isEmpty()) return
    SectionTitle("Fuentes y ampliación")
    Note("Explicación propia basada en estas fuentes. Búscalas cuando tengas conexión si quieres profundizar.")
    ListItems(lesson.sources) { "•" }
}
