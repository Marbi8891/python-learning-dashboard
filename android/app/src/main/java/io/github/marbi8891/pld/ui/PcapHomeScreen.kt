package io.github.marbi8891.pld.ui

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.semantics.heading
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import io.github.marbi8891.pld.AppModel
import io.github.marbi8891.pld.pcap.PcapState
import io.github.marbi8891.pld.pcap.Status
import kotlin.math.roundToInt

/** Pestaña «Examen»: nota estimada, criterios para estar listo y práctica libre por bloque (sin vidas). */
@Composable
fun PcapHomeScreen(model: AppModel, onPractice: (String) -> Unit, onTheory: (String) -> Unit, modifier: Modifier = Modifier) {
    val bank = model.bank
    val pcap = model.pcap
    val status = remember(model.revision) { pcap.status(bank) }
    val palette = LocalPalette.current

    LazyColumn(
        modifier = modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        item {
            val course = model.course
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                if (!course.isPcap) {
                    // Otros cursos de DAW (ADR-0016): sin examen oficial, solo práctica por bloque
                    Eyebrow(course.subtitle)
                    Text(
                        "Practica ${course.title}",
                        modifier = Modifier.semantics { heading() },
                        style = MaterialTheme.typography.headlineMedium,
                        color = MaterialTheme.colorScheme.onBackground,
                    )
                    Text(
                        "Practica por bloque sin gastar vidas; cada tanda terminada te devuelve una.",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                } else {
                    Eyebrow("Examen ${bank.exam.code} · Python Institute")
                    Text(
                        "Prepara el examen PCAP",
                        modifier = Modifier.semantics { heading() },
                        style = MaterialTheme.typography.headlineMedium,
                        color = MaterialTheme.colorScheme.onBackground,
                    )
                    Text(
                        "${bank.exam.questions} preguntas · ${bank.exam.minutes} minutos · ${bank.exam.pass} % para aprobar. " +
                            "Aquí practicas por bloque sin gastar vidas, y cada tanda terminada te devuelve una.",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                    LangSwitch(pcap.lang) { lang -> model.update { this.lang = lang } }
                }
            }
        }

        item {
            Panel(borderColor = if (status.ready) palette.accent else MaterialTheme.colorScheme.outline) {
                SectionTitle(if (model.course.isPcap) "Tu preparación" else "Tu dominio")
                Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                    Text("${status.score} %", style = MaterialTheme.typography.displaySmall, color = MaterialTheme.colorScheme.primary)
                    Text("preparación estimada", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
                }
                Meter(status.score / 100.0, "Preparación estimada", MaterialTheme.colorScheme.primary)
                if (model.course.isPcap) Text(advice(status), style = MaterialTheme.typography.bodyMedium)
                Text(
                    if (model.course.isPcap) {
                        "Es tu acierto en cada bloque ponderado por su peso en el examen. Orientativo: no es una predicción oficial."
                    } else {
                        "Es tu acierto en cada bloque ponderado por su importancia en el módulo."
                    },
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
        }

        items(bank.exam.blocks, key = { it.slug }) { block ->
            val stat = status.stats.getValue(block.slug)
            val lesson = model.lessons.modules[block.slug]?.firstOrNull()
            Panel {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(
                        block.title.es,
                        modifier = Modifier
                            .weight(1f)
                            .semantics { heading() },
                        style = MaterialTheme.typography.titleLarge,
                    )
                    Text("${block.weight} % del examen", color = MaterialTheme.colorScheme.primary, fontWeight = FontWeight.SemiBold)
                }
                Meter(stat.rate, "Acierto en ${block.title.es}")
                Text(
                    if (stat.answered > 0) {
                        "${((stat.rate ?: 0.0) * 100).roundToInt()} % de acierto · ${stat.answered} preguntas respondidas"
                    } else {
                        "Sin datos todavía"
                    },
                    style = MaterialTheme.typography.bodyMedium,
                    color = palette.muted,
                )
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp), verticalAlignment = Alignment.CenterVertically) {
                    OutlinedButton(onClick = { onPractice(block.slug) }) { Text("Practicar") }
                    if (lesson != null) TextButton(onClick = { onTheory(lesson) }) { Text("Teoría") }
                }
            }
        }

        item {
            Text(
                "Mejor racha: ${pcap.bestCombo} aciertos seguidos · ${pcap.questionsMastered()} de ${bank.questions.size} preguntas acertadas alguna vez",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
    }
}

private fun advice(status: Status): String {
    if (status.ready) {
        return "Listo para examinarte. Cumples los criterios: preparación del ${PcapState.READY_SCORE} % o más, " +
            "todos los bloques por encima del 60 % y el último simulacro con ${PcapState.READY_LAST_EXAM} % o más."
    }
    val steps = listOfNotNull(
        if (status.score < PcapState.READY_SCORE) "sube tu preparación al ${PcapState.READY_SCORE} % (ahora ${status.score} %)" else null,
        if (status.weak.isNotEmpty()) {
            "practica ${status.weak.joinToString(", ") { it.title.es }} (mínimo ${PcapState.READY_BLOCK_ANSWERED} preguntas y 60 % de acierto)"
        } else {
            null
        },
        if ((status.lastExam?.score ?: 0) < PcapState.READY_LAST_EXAM) {
            "aprueba un simulacro con ${PcapState.READY_LAST_EXAM} % o más"
        } else {
            null
        },
    )
    return "Aún no. Para estar listo: ${steps.joinToString("; ")}."
}
