package io.github.marbi8891.pld.ui

import androidx.compose.animation.core.Spring
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.spring
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.scale
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.semantics.heading
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import io.github.marbi8891.pld.AppModel
import java.time.LocalDate

/** Fin de una lección de la ruta: XP ganada, racha y avance de la meta diaria. */
@Composable
fun CelebrationScreen(model: AppModel, xp: Int, perfect: Boolean, onContinue: () -> Unit) {
    val app = model.pcap.app
    val today = LocalDate.now()
    val streak = app.streak(today)
    val todayXp = app.xpOn(today)
    val goalMet = todayXp >= app.goal
    // La meta se ha cumplido justo con esta lección: se celebra aparte
    val goalJustMet = goalMet && todayXp - xp < app.goal

    var shown by remember { mutableStateOf(false) }
    val scale by animateFloatAsState(if (shown) 1f else 0.4f, spring(dampingRatio = Spring.DampingRatioMediumBouncy), label = "celebracion")
    val haptics = LocalHapticFeedback.current
    LaunchedEffect(Unit) {
        shown = true
        haptics.performHapticFeedback(HapticFeedbackType.LongPress)
    }
    val palette = LocalPalette.current

    Scaffold(containerColor = MaterialTheme.colorScheme.background) { padding ->
        Column(
            Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(20.dp, Alignment.CenterVertically),
        ) {
            Text(if (perfect) "★" else "✓", fontSize = 96.sp, color = MaterialTheme.colorScheme.primary, modifier = Modifier.scale(scale))
            Text(
                if (perfect) "¡Lección perfecta!" else "¡Lección completada!",
                modifier = Modifier.semantics { heading() },
                style = MaterialTheme.typography.headlineMedium,
                textAlign = TextAlign.Center,
            )
            Text("+$xp XP${if (perfect) " (incluye +5 por no fallar)" else ""}", color = MaterialTheme.colorScheme.primary, fontWeight = FontWeight.Bold)
            Text("🔥 Racha de $streak ${if (streak == 1) "día" else "días"}", color = palette.streak, fontWeight = FontWeight.Bold)
            Column(Modifier.fillMaxWidth(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                Text(
                    if (goalJustMet) "¡Meta diaria cumplida!" else "Meta diaria: $todayXp de ${app.goal} XP",
                    style = MaterialTheme.typography.titleMedium,
                )
                Meter(minOf(1.0, todayXp.toDouble() / app.goal), "Meta diaria", palette.accent)
            }
            Button(onClick = onContinue, modifier = Modifier.fillMaxWidth()) { Text("Continuar") }
        }
    }
}
