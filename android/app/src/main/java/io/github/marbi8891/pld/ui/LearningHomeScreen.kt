package io.github.marbi8891.pld.ui

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.semantics.heading
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.unit.dp
import io.github.marbi8891.pld.AppModel
import io.github.marbi8891.pld.pcap.Question

data class LearningRecommendation(
    val question: Question,
    val reason: String,
    val blockTitle: String,
)

fun AppModel.learningRecommendation(): LearningRecommendation? {
    val bank = course.bank
    if (bank.questions.isEmpty()) return null

    val due = bank.questions.filter { pcap.dueIds(listOf(it.id)).isNotEmpty() }
    val failed = bank.questions.filter { pcap.answers[it.id]?.lastOrNull() == false }
    val fresh = bank.questions.filter { it.id !in pcap.answers }

    val candidate = due.firstOrNull() ?: failed.firstOrNull() ?: fresh.firstOrNull() ?: bank.questions.first()
    val block = bank.block(candidate.block)

    val reason = when {
        candidate.id in due.map { it.id } -> "Te toca repasar este concepto."
        candidate.id in failed.map { it.id } -> "Lo fallaste recientemente. Vamos a intentarlo otra vez."
        candidate.id in fresh.map { it.id } -> "Es un concepto nuevo para ti."
        else -> "Repaso general para mantener lo aprendido."
    }

    return LearningRecommendation(candidate, reason, block.title.get(pcap.lang))
}

@Composable
fun LearningHomeScreen(
    model: AppModel,
    onStart: (String) -> Unit,
    onTheoryHome: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val recommendation = remember(model.revision, model.course.id) { model.learningRecommendation() }
    val status = remember(model.revision, model.course.id) { model.pcap.status(model.bank) }
    val scroll = rememberScrollState()
    val answered = model.bank.questions.count { it.id in model.pcap.answers }
    val mastered = model.pcap.questionsMastered()

    Scaffold(containerColor = MaterialTheme.colorScheme.background) { padding ->
        Column(
            modifier
                .fillMaxSize()
                .padding(padding)
                .verticalScroll(scroll)
                .padding(horizontal = 20.dp, vertical = 24.dp),
            verticalArrangement = Arrangement.spacedBy(18.dp),
        ) {
            Text(
                "Aprender",
                style = MaterialTheme.typography.headlineLarge,
                modifier = Modifier.semantics { heading() },
            )
            Text(
                "Una sesión corta, centrada en lo que todavía no dominas.",
                color = LocalPalette.current.muted,
            )

            if (recommendation != null) {
                Panel {
                    Text("PARA HOY", style = MaterialTheme.typography.labelMedium, color = LocalPalette.current.muted)
                    Text(
                        recommendation.blockTitle,
                        style = MaterialTheme.typography.headlineSmall,
                        modifier = Modifier.semantics { heading() },
                    )
                    Text(recommendation.reason, color = LocalPalette.current.muted)
                    Text(
                        recommendation.question.q.get(model.pcap.lang),
                        style = MaterialTheme.typography.bodyLarge,
                    )
                    Button(onClick = { onStart(recommendation.question.id) }, modifier = Modifier.fillMaxWidth()) {
                        Text("Empezar")
                    }
                }
            }

            Panel {
                Text("TU PROGRESO", style = MaterialTheme.typography.labelMedium, color = LocalPalette.current.muted)
                Text("${mastered} de ${model.bank.questions.size} preguntas dominadas")
                LinearProgressIndicator(
                    progress = {
                        if (model.bank.questions.isEmpty()) 0f
                        else mastered.toFloat() / model.bank.questions.size
                    },
                    modifier = Modifier.fillMaxWidth(),
                )
                Text("${answered} preguntas respondidas", color = LocalPalette.current.muted)
            }

            Panel {
                Text("QUÉ NECESITAS", style = MaterialTheme.typography.labelMedium, color = LocalPalette.current.muted)
                if (status.weak.isEmpty()) {
                    Text("No hay bloques especialmente débiles.")
                } else {
                    status.weak.take(3).forEach { block ->
                        val stat = status.stats.getValue(block.slug)
                        val percent = stat.rate?.let { "${(it * 100).toInt()}%" } ?: "sin datos"
                        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                            Text(block.title.get(model.pcap.lang))
                            Text(percent, color = LocalPalette.current.muted)
                        }
                    }
                }
            }

            OutlinedButton(onClick = onTheoryHome, modifier = Modifier.fillMaxWidth()) {
                Text("Estudiar teoría")
            }
        }
    }
}
