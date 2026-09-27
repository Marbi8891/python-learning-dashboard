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
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.semantics.LiveRegionMode
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.liveRegion
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import io.github.marbi8891.pld.AppModel
import io.github.marbi8891.pld.pcap.LessonRun
import io.github.marbi8891.pld.pcap.PathNode

/**
 * Lección corta de la ruta: la barra avanza con cada acierto, cada fallo cuesta una vida
 * y la pregunta fallada vuelve al final hasta acertarla (ADR-0012).
 */
@Composable
fun LessonScreen(
    model: AppModel,
    node: PathNode,
    onExit: () -> Unit,
    onFinished: (xp: Int, perfect: Boolean) -> Unit,
    onPractice: (String) -> Unit,
) {
    val lesson = remember(node.id) { LessonRun(model.questions(node).shuffled()) }
    var step by remember(node.id) { mutableIntStateOf(0) } // LessonRun no es observable: esto repinta
    var chosen by remember(node.id, step) { mutableStateOf(setOf<Int>()) }
    var result by remember(node.id, step) { mutableStateOf<Boolean?>(null) } // null = sin comprobar
    val hearts = remember(model.revision) { model.pcap.app.heartsNow() }
    val lang = remember(model.revision) { model.pcap.lang }
    val unit = model.unitOf(node)
    val haptics = LocalHapticFeedback.current
    val palette = LocalPalette.current
    val scroll = rememberScrollState()
    LaunchedEffect(step) { scroll.scrollTo(0) }

    Scaffold(containerColor = MaterialTheme.colorScheme.background) { padding ->
        Column(Modifier.fillMaxSize().padding(padding)) {
            // Cabecera: salir, progreso y vidas
            Row(Modifier.padding(horizontal = 8.dp, vertical = 8.dp), verticalAlignment = Alignment.CenterVertically) {
                TextButton(onClick = onExit, modifier = Modifier.semantics { contentDescription = "Salir de la lección" }) { Text("✕") }
                val progress = lesson.progress // se lee aquí para que la barra se repinte en cada paso
                LinearProgressIndicator(
                    progress = { progress },
                    modifier = Modifier
                        .weight(1f)
                        .semantics { contentDescription = "Progreso de la lección: ${(progress * 100).toInt()} %" },
                    color = palette.accent,
                    trackColor = MaterialTheme.colorScheme.outline,
                )
                Text(
                    "♥ $hearts",
                    modifier = Modifier
                        .padding(start = 12.dp, end = 8.dp)
                        .semantics { contentDescription = "Vidas: $hearts" },
                    color = palette.danger,
                    fontWeight = FontWeight.Bold,
                )
            }

            val question = lesson.current
            if (question == null) {
                // La lección ya ha terminado: la pantalla de celebración toma el relevo
            } else if (hearts == 0 && result == null) {
                OutOfHearts(onPractice = { onPractice(unit.block) }, onExit = onExit)
            } else {
                Column(
                    Modifier
                        .weight(1f)
                        .verticalScroll(scroll)
                        .padding(horizontal = 16.dp, vertical = 8.dp),
                    verticalArrangement = Arrangement.spacedBy(16.dp),
                ) {
                    Text(unit.title, color = palette.muted, style = MaterialTheme.typography.labelLarge)
                    QuestionView(question, lang, chosen, result != null) { option ->
                        chosen = when {
                            !question.multi -> setOf(option)
                            option in chosen -> chosen - option
                            else -> chosen + option
                        }
                    }
                }

                // Barra inferior: «Comprobar» o el veredicto con la explicación y «Continuar»
                val verdict = result
                if (verdict == null) {
                    Button(
                        onClick = {
                            val ok = question.isCorrect(chosen)
                            result = ok
                            model.update {
                                recordAnswer(question.id, ok)
                                if (!ok) app.loseHeart()
                            }
                            haptics.performHapticFeedback(if (ok) HapticFeedbackType.TextHandleMove else HapticFeedbackType.LongPress)
                        },
                        enabled = chosen.size == question.answer.size,
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp),
                    ) { Text("Comprobar") }
                } else {
                    Surface(color = MaterialTheme.colorScheme.surface, modifier = Modifier.fillMaxWidth()) {
                        Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                            Text(
                                if (verdict) "¡Correcto!" else "No es correcta. Volverá al final de la lección.",
                                modifier = Modifier.semantics { liveRegion = LiveRegionMode.Polite },
                                color = if (verdict) palette.accent else palette.danger,
                                fontWeight = FontWeight.Bold,
                                style = MaterialTheme.typography.titleMedium,
                            )
                            RichText(question.explain.get(lang), style = MaterialTheme.typography.bodyMedium)
                            Button(
                                onClick = {
                                    lesson.answer(verdict)
                                    if (lesson.finished) {
                                        val xp = model.update { app.complete(node, lesson.perfect) }
                                        onFinished(xp, lesson.perfect)
                                    } else {
                                        step++
                                    }
                                },
                                colors = ButtonDefaults.buttonColors(
                                    containerColor = if (verdict) palette.accent else palette.danger,
                                    contentColor = MaterialTheme.colorScheme.background,
                                ),
                                modifier = Modifier.fillMaxWidth(),
                            ) { Text("Continuar") }
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun OutOfHearts(onPractice: () -> Unit, onExit: () -> Unit) {
    Column(Modifier.padding(24.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
        SectionTitle("Te has quedado sin vidas")
        Text(
            "Recuperas una cada 4 horas, o ahora mismo terminando una tanda de práctica libre de este bloque " +
                "(la práctica no gasta vidas). Lo que has respondido ya cuenta para tu repaso.",
        )
        Button(onClick = onPractice, modifier = Modifier.fillMaxWidth()) { Text("Practicar para recuperar una vida") }
        OutlinedButton(onClick = onExit, modifier = Modifier.fillMaxWidth()) { Text("Salir") }
    }
}
