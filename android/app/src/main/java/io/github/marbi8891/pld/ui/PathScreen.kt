package io.github.marbi8891.pld.ui

import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.slideInVertically
import androidx.compose.animation.slideOutVertically
import androidx.compose.foundation.ExperimentalFoundationApi
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.derivedStateOf
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.drawBehind
import androidx.compose.ui.draw.scale
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.clearAndSetSemantics
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.heading
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import io.github.marbi8891.pld.AppModel
import io.github.marbi8891.pld.pcap.PathNode
import io.github.marbi8891.pld.pcap.PathUnit
import io.github.marbi8891.pld.pcap.UnitSummary
import io.github.marbi8891.pld.pcap.UnitState
import io.github.marbi8891.pld.pcap.unitSummary
import kotlinx.coroutines.launch
import java.time.Duration
import kotlin.math.hypot
import kotlin.math.roundToInt

/*
 * Pestaña «Ruta» (ADR-0028): un camino tranquilo, sin ruido visual.
 * Un solo color de acento (la lección que toca), una línea fina que une las lecciones y se colorea
 * hasta donde has llegado, cabeceras de unidad finas que se quedan fijas arriba y movimiento suave.
 */

// Desplazamiento horizontal de cada lección: una curva suave, no un zigzag brusco
private val CURVE = listOf(0, 34, 48, 34, 0, -34, -48, -34)
private val ROW: Dp = 84.dp // alto fijo de cada lección: así la línea sabe dónde está la anterior
private val NODE: Dp = 52.dp
private val CURRENT_NODE: Dp = 64.dp

private enum class NodeState { DONE, CURRENT, LOCKED }

@OptIn(ExperimentalFoundationApi::class)
@Composable
fun PathScreen(
    model: AppModel,
    onStart: (PathNode) -> Unit,
    onPractice: (String) -> Unit,
    onTheory: (String) -> Unit,
    modifier: Modifier = Modifier,
) {
    val app = model.pcap.app
    val revision = model.revision
    val current = remember(revision) { app.currentNode(model.units) }
    val units = model.units
    // Índice en la lista (cada unidad es su cabecera más sus lecciones) de cada lección
    val indexOf = remember(units) {
        var index = 0
        buildMap {
            units.forEach { unit ->
                index++ // cabecera
                unit.nodes.forEach { put(it.id, index++) }
            }
        }
    }
    // Posición de cada lección en la curva, seguida a lo largo de todo el curso
    val curveOf = remember(units) { units.flatMap { it.nodes }.withIndex().associate { (i, node) -> node.id to i } }
    val currentIndex = current?.let { indexOf[it.id] }
    val listState = rememberLazyListState()
    val scope = rememberCoroutineScope()
    var noHeartsFor by remember { mutableStateOf<PathNode?>(null) }

    // Al abrir, el camino se coloca en la lección que toca (con la anterior a la vista)
    LaunchedEffect(Unit) {
        if (currentIndex != null && currentIndex > 1) listState.scrollToItem(currentIndex - 1)
    }
    val currentVisible by remember(currentIndex) {
        derivedStateOf { currentIndex == null || listState.layoutInfo.visibleItemsInfo.any { it.index == currentIndex } }
    }

    Column(modifier.fillMaxSize()) {
        StatusBar(model)
        Box(Modifier.fillMaxSize()) {
            LazyColumn(
                state = listState,
                modifier = Modifier.fillMaxSize(),
                contentPadding = PaddingValues(bottom = 96.dp),
            ) {
                units.forEachIndexed { u, unit ->
                    stickyHeader(key = "u-${unit.slug}") {
                        val summary = remember(revision) { model.pcap.unitSummary(unit, current) }
                        UnitHeader(unit, u + 1, summary) { onTheory(unit.slug) }
                    }
                    items(unit.nodes.size, key = { unit.nodes[it].id }) { i ->
                        val node = unit.nodes[i]
                        val state = when {
                            node.id in app.done -> NodeState.DONE
                            node == current -> NodeState.CURRENT
                            else -> NodeState.LOCKED
                        }
                        val position = curveOf.getValue(node.id)
                        // La línea sube hasta la lección anterior de la misma unidad
                        val previous = if (i == 0) null else CURVE[(position - 1) % CURVE.size]
                        LessonNode(node, CURVE[position % CURVE.size], previous, state, unit.title) {
                            if (app.heartsNow() > 0) onStart(node) else noHeartsFor = node
                        }
                    }
                }
            }

            // Solo cuando tu lección no se ve: vuelve a ella con un desplazamiento suave
            // Nombre completo: dentro de un Box que está en un Column, la versión «de Column» no se puede usar
            androidx.compose.animation.AnimatedVisibility(
                visible = !currentVisible,
                enter = fadeIn() + slideInVertically { it / 2 },
                exit = fadeOut() + slideOutVertically { it / 2 },
                modifier = Modifier
                    .align(Alignment.BottomCenter)
                    .padding(bottom = 20.dp),
            ) {
                Button(onClick = { scope.launch { if (currentIndex != null) listState.animateScrollToItem(maxOf(0, currentIndex - 1)) } }) {
                    Text("Ir a mi lección")
                }
            }
        }
    }

    noHeartsFor?.let { node ->
        OutOfHeartsDialog(
            wait = app.nextHeartIn(),
            onPractice = {
                noHeartsFor = null
                onPractice(model.unitOf(node).block)
            },
            onDismiss = { noHeartsFor = null },
        )
    }
}

/** Racha, XP de hoy frente a la meta y vidas: tres cifras tranquilas, sin iconos de colores. */
@Composable
fun StatusBar(model: AppModel) {
    val revision = model.revision
    val app = model.pcap.app
    val streak = remember(revision) { app.streak() }
    val today = remember(revision) { app.xpOn(java.time.LocalDate.now()) }
    val hearts = remember(revision) { app.heartsNow() }
    val palette = LocalPalette.current
    val ink = MaterialTheme.colorScheme.onBackground
    Row(
        Modifier
            .fillMaxWidth()
            .background(MaterialTheme.colorScheme.background)
            .padding(horizontal = 20.dp, vertical = 8.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
    ) {
        Figure("$streak", if (streak == 1) "día de racha" else "días de racha", ink)
        Figure("$today/${app.goal}", "XP hoy", if (today >= app.goal) palette.accent else ink)
        Figure("$hearts", if (hearts == 1) "vida" else "vidas", if (hearts == 0) palette.danger else ink)
    }
}

@Composable
private fun Figure(value: String, label: String, color: Color) {
    Row(
        verticalAlignment = Alignment.Bottom,
        modifier = Modifier.clearAndSetSemantics { contentDescription = "$value $label" },
    ) {
        Text(value, color = color, fontWeight = FontWeight.SemiBold, fontSize = 17.sp)
        Text(" $label", color = LocalPalette.current.muted, style = MaterialTheme.typography.labelMedium)
    }
}

/** Cabecera fina de unidad: se queda fija arriba mientras recorres sus lecciones. */
@Composable
private fun UnitHeader(unit: PathUnit, number: Int, summary: UnitSummary, onTheory: () -> Unit) {
    val palette = LocalPalette.current
    val colors = MaterialTheme.colorScheme
    val progress by animateFloatAsState(summary.progress, tween(600), label = "unidad")
    val state = summary.state
    val accuracy = summary.rate?.let { "aciertas el ${(it * 100).roundToInt()} %" } ?: "aún sin responder"
    val stateLabel = when (state) {
        UnitState.DONE -> "completada"
        UnitState.CURRENT -> "en curso"
        UnitState.LOCKED -> "por empezar"
    }
    Column(
        Modifier
            .fillMaxWidth()
            .background(colors.background) // opaca: las lecciones pasan por debajo
            .padding(start = 20.dp, end = 8.dp, top = 16.dp, bottom = 10.dp),
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Column(
                Modifier
                    .weight(1f)
                    .clearAndSetSemantics {
                        heading()
                        contentDescription = "Unidad $number, ${unit.title}, $stateLabel. " +
                            "${summary.lessonsDone} de ${summary.lessons} lecciones. ${summary.questions} preguntas, $accuracy."
                    },
            ) {
                Text(
                    "UNIDAD $number",
                    style = MaterialTheme.typography.labelSmall,
                    letterSpacing = 1.2.sp,
                    color = if (state == UnitState.CURRENT) colors.primary else palette.muted,
                    fontWeight = FontWeight.SemiBold,
                )
                Text(
                    unit.title,
                    style = MaterialTheme.typography.titleMedium,
                    color = if (state == UnitState.LOCKED) palette.muted else colors.onBackground,
                )
            }
            Text(
                "${summary.lessonsDone}/${summary.lessons}",
                style = MaterialTheme.typography.labelMedium,
                color = palette.muted,
                modifier = Modifier.clearAndSetSemantics { },
            )
            TextButton(onClick = onTheory, modifier = Modifier.semantics { contentDescription = "Teoría de ${unit.title}" }) {
                Text("Teoría", color = palette.muted)
            }
        }
        // Barra fina de progreso: se rellena con suavidad al completar una lección
        Box(
            Modifier
                .padding(top = 6.dp, end = 12.dp)
                .fillMaxWidth()
                .height(3.dp)
                .background(colors.outline, RoundedCornerShape(2.dp)),
        ) {
            Box(
                Modifier
                    .fillMaxWidth(progress)
                    .height(3.dp)
                    .background(if (state == UnitState.DONE) palette.accent else colors.primary, RoundedCornerShape(2.dp)),
            )
        }
    }
}

/**
 * Una lección del camino. Dibuja por detrás la línea hasta la anterior, recortada en los bordes de
 * los círculos para que no los atraviese.
 */
@Composable
private fun LessonNode(node: PathNode, offset: Int, previousOffset: Int?, state: NodeState, unitTitle: String, onClick: () -> Unit) {
    val palette = LocalPalette.current
    val colors = MaterialTheme.colorScheme
    val lineColor = if (state == NodeState.LOCKED) colors.outline else palette.accent.copy(alpha = 0.55f)
    val diameter = if (state == NodeState.CURRENT) CURRENT_NODE else NODE
    val label = when (state) {
        NodeState.DONE -> "completada"
        NodeState.CURRENT -> "la que toca, toca para empezar"
        NodeState.LOCKED -> "bloqueada"
    }

    Box(
        Modifier
            .fillMaxWidth()
            .height(ROW)
            .drawBehind {
                if (previousOffset == null) return@drawBehind
                val here = Offset(size.width / 2 + offset.dp.toPx(), size.height / 2)
                val before = Offset(size.width / 2 + previousOffset.dp.toPx(), size.height / 2 - ROW.toPx())
                val length = hypot(here.x - before.x, here.y - before.y)
                val dir = Offset((here.x - before.x) / length, (here.y - before.y) / length)
                val margin = 6.dp.toPx()
                drawLine(
                    color = lineColor,
                    start = before + dir * (NODE.toPx() / 2 + margin),
                    end = here - dir * (diameter.toPx() / 2 + margin),
                    strokeWidth = 3.dp.toPx(),
                    cap = StrokeCap.Round,
                )
            },
        contentAlignment = Alignment.Center,
    ) {
        Box(Modifier.offset(x = offset.dp), contentAlignment = Alignment.Center) {
            if (state == NodeState.CURRENT) Pulse(colors.primary)
            val (fill, content, border) = when (state) {
                NodeState.DONE -> Triple(palette.accent.copy(alpha = 0.16f), palette.accent, palette.accent.copy(alpha = 0.6f))
                NodeState.CURRENT -> Triple(colors.primary, colors.onPrimary, colors.primary)
                NodeState.LOCKED -> Triple(Color.Transparent, palette.muted, colors.outline)
            }
            Box(
                Modifier
                    .size(diameter)
                    .background(fill, CircleShape)
                    .border(2.dp, border, CircleShape)
                    .clickable(enabled = state != NodeState.LOCKED, role = Role.Button, onClick = onClick)
                    .semantics { contentDescription = "Lección ${node.number} de $unitTitle: $label" },
                contentAlignment = Alignment.Center,
            ) {
                Text(
                    if (state == NodeState.DONE) "✓" else "${node.number}",
                    color = content,
                    fontSize = if (state == NodeState.CURRENT) 22.sp else 18.sp,
                    fontWeight = FontWeight.SemiBold,
                )
            }
        }
    }
}

/** Halo que late despacio alrededor de la lección que toca (quieto si el sistema desactiva las animaciones). */
@Composable
private fun Pulse(color: Color) {
    val transition = rememberInfiniteTransition(label = "pulso")
    val scale by transition.animateFloat(1f, 1.28f, infiniteRepeatable(tween(1400), RepeatMode.Reverse), label = "escala")
    val alpha by transition.animateFloat(0.28f, 0f, infiniteRepeatable(tween(1400), RepeatMode.Reverse), label = "alfa")
    Box(
        Modifier
            .size(CURRENT_NODE)
            .scale(scale)
            .background(color.copy(alpha = alpha), CircleShape),
    )
}

@Composable
private fun OutOfHeartsDialog(wait: Duration?, onPractice: () -> Unit, onDismiss: () -> Unit) {
    val next = wait?.let { "La siguiente llega en ${it.toHours()} h ${it.toMinutes() % 60} min. " } ?: ""
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Te has quedado sin vidas") },
        text = { Text("${next}Termina una tanda de práctica libre de este bloque y recuperas una ahora mismo: la práctica no gasta vidas.") },
        confirmButton = { TextButton(onClick = onPractice) { Text("Practicar") } },
        dismissButton = { TextButton(onClick = onDismiss) { Text("Cerrar") } },
    )
}
