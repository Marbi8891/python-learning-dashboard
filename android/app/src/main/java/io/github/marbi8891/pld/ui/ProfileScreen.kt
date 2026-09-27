package io.github.marbi8891.pld.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.selection.selectable
import androidx.compose.foundation.selection.selectableGroup
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.RadioButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import io.github.marbi8891.pld.AppModel
import io.github.marbi8891.pld.pcap.AppProgress
import java.time.LocalDate
import java.time.format.TextStyle
import java.util.Locale

/** Pestaña «Perfil»: racha, XP, últimos 7 días, meta diaria y avance en la ruta. */
@Composable
fun ProfileScreen(model: AppModel, modifier: Modifier = Modifier) {
    val revision = model.revision
    val app = model.pcap.app
    val today = LocalDate.now()
    val week = remember(revision) { (6 downTo 0).map { today.minusDays(it.toLong()) }.map { it to app.xpOn(it) } }
    val totalNodes = model.units.sumOf { it.nodes.size }
    val doneNodes = remember(revision) { model.units.flatMap { it.nodes }.count { it.id in app.done } }
    val readiness = remember(revision) { model.pcap.status(model.bank).score }
    val palette = LocalPalette.current

    LazyColumn(
        modifier = modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        item {
            Text("Tu progreso", style = MaterialTheme.typography.headlineMedium, color = MaterialTheme.colorScheme.onBackground)
        }
        item {
            Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                BigStat("🔥 ${app.streak(today)}", "días de racha", Modifier.weight(1f))
                BigStat("⚡ ${app.totalXp()}", "XP en total", Modifier.weight(1f))
            }
        }
        item {
            Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                BigStat("$doneNodes/$totalNodes", "lecciones de la ruta", Modifier.weight(1f))
                BigStat("$readiness %", "preparación PCAP", Modifier.weight(1f))
            }
        }
        item {
            Panel {
                SectionTitle("Últimos 7 días")
                WeekChart(week, app.goal)
                Text(
                    "La línea de cada barra llena es tu meta diaria. La racha cuenta los días seguidos con algo de XP.",
                    style = MaterialTheme.typography.bodySmall,
                    color = palette.muted,
                )
            }
        }
        item {
            Panel {
                SectionTitle("Meta diaria")
                Column(Modifier.selectableGroup()) {
                    AppProgress.GOALS.forEach { goal ->
                        val label = when (goal) {
                            10 -> "Tranquila · 10 XP (1 lección)"
                            20 -> "Normal · 20 XP (2 lecciones)"
                            30 -> "Seria · 30 XP (3 lecciones)"
                            else -> "Intensa · 50 XP (5 lecciones)"
                        }
                        Row(
                            Modifier
                                .fillMaxWidth()
                                .selectable(selected = app.goal == goal, onClick = { model.update { app.goal = goal } }, role = Role.RadioButton)
                                .padding(vertical = 6.dp),
                            verticalAlignment = Alignment.CenterVertically,
                        ) {
                            RadioButton(selected = app.goal == goal, onClick = null)
                            Text(label, Modifier.padding(start = 8.dp))
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun BigStat(value: String, label: String, modifier: Modifier = Modifier) {
    Panel(modifier) {
        Text(value, style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.Bold)
        Text(label, style = MaterialTheme.typography.bodySmall, color = LocalPalette.current.muted)
    }
}

/** Barras de XP por día; la altura máxima corresponde a la meta (lo que la supera se recorta). */
@Composable
private fun WeekChart(week: List<Pair<LocalDate, Int>>, goal: Int) {
    val palette = LocalPalette.current
    val maxHeight = 96.dp
    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.Bottom) {
        week.forEach { (day, xp) ->
            val name = day.dayOfWeek.getDisplayName(TextStyle.SHORT, Locale.forLanguageTag("es-ES"))
            Column(
                Modifier.semantics(mergeDescendants = true) { contentDescription = "$name: $xp XP" },
                horizontalAlignment = Alignment.CenterHorizontally,
            ) {
                Text("$xp", style = MaterialTheme.typography.labelSmall, color = palette.muted)
                Box(
                    Modifier
                        .padding(vertical = 4.dp)
                        .height(maxHeight * minOf(1f, xp.toFloat() / goal).coerceAtLeast(0.04f))
                        .width(20.dp)
                        .background(if (xp >= goal) palette.accent else MaterialTheme.colorScheme.primary, RoundedCornerShape(4.dp)),
                )
                Text(name, style = MaterialTheme.typography.labelSmall)
            }
        }
    }
}
