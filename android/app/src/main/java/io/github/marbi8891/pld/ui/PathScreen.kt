package io.github.marbi8891.pld.ui

import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalUriHandler
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.heading
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import io.github.marbi8891.pld.AppModel
import io.github.marbi8891.pld.pcap.PathNode
import io.github.marbi8891.pld.pcap.PathUnit
import java.time.Duration

private sealed interface PathRow {
    data class UnitHeader(val unit: PathUnit, val number: Int) : PathRow

    data class Node(val node: PathNode, val position: Int) : PathRow
}

// Desplazamiento horizontal de los nodos para dibujar el camino en zigzag
private val ZIGZAG = listOf(0, 44, 64, 44, 0, -44, -64, -44)

/** Pestaña principal: el camino de unidades y lecciones cortas, con la racha, la meta y las vidas arriba. */
@Composable
fun PathScreen(model: AppModel, onStart: (PathNode) -> Unit, onPractice: (String) -> Unit, modifier: Modifier = Modifier) {
    val app = model.pcap.app
    val revision = model.revision
    val current = remember(revision) { app.currentNode(model.units) }
    val rows = remember {
        var position = 0
        model.units.flatMapIndexed { i, unit ->
            listOf<PathRow>(PathRow.UnitHeader(unit, i + 1)) + unit.nodes.map { PathRow.Node(it, position++) }
        }
    }
    val listState = rememberLazyListState()
    var noHeartsFor by remember { mutableStateOf<PathNode?>(null) }
    val uri = LocalUriHandler.current

    // Al abrir, el camino se coloca en la lección que toca
    LaunchedEffect(Unit) {
        val index = rows.indexOfFirst { it is PathRow.Node && it.node == current }
        if (index > 1) listState.scrollToItem(index - 1)
    }

    Column(modifier.fillMaxSize()) {
        StatusBar(model)
        LazyColumn(
            state = listState,
            modifier = Modifier.fillMaxSize(),
            contentPadding = PaddingValues(start = 16.dp, end = 16.dp, top = 8.dp, bottom = 32.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp),
        ) {
            items(rows, key = { row -> if (row is PathRow.Node) row.node.id else "u-" + (row as PathRow.UnitHeader).unit.slug }) { row ->
                when (row) {
                    is PathRow.UnitHeader -> UnitCard(row.unit, row.number, model) { uri.openUri(model.lessonUrl(row.unit.slug)) }
                    is PathRow.Node -> {
                        val state = when {
                            row.node.id in app.done -> NodeState.DONE
                            row.node == current -> NodeState.CURRENT
                            else -> NodeState.LOCKED
                        }
                        NodeButton(row.node, row.position, state, model.unitOf(row.node).title) {
                            if (app.heartsNow() > 0) onStart(row.node) else noHeartsFor = row.node
                        }
                    }
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

/** Racha, XP de hoy frente a la meta y vidas. */
@Composable
fun StatusBar(model: AppModel) {
    val revision = model.revision
    val app = model.pcap.app
    val streak = remember(revision) { app.streak() }
    val today = remember(revision) { app.xpOn(java.time.LocalDate.now()) }
    val hearts = remember(revision) { app.heartsNow() }
    val palette = LocalPalette.current
    Surface(color = MaterialTheme.colorScheme.surface, modifier = Modifier.fillMaxWidth()) {
        Row(
            Modifier.padding(horizontal = 16.dp, vertical = 10.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Stat("🔥 $streak", "Racha: $streak ${if (streak == 1) "día" else "días"}", palette.streak)
            Stat("⚡ $today/${app.goal}", "XP de hoy: $today de ${app.goal}", MaterialTheme.colorScheme.primary)
            Stat("♥ $hearts", "Vidas: $hearts de 5", palette.danger)
        }
    }
}

@Composable
private fun Stat(text: String, description: String, color: Color) {
    Text(
        text,
        modifier = Modifier.semantics { contentDescription = description },
        color = color,
        fontWeight = FontWeight.Bold,
        fontSize = 17.sp,
    )
}

@Composable
private fun UnitCard(unit: PathUnit, number: Int, model: AppModel, onTheory: () -> Unit) {
    val block = model.bank.block(unit.block)
    Surface(
        color = MaterialTheme.colorScheme.primary,
        contentColor = MaterialTheme.colorScheme.onPrimary,
        shape = CardShape,
        modifier = Modifier
            .fillMaxWidth()
            .padding(top = 12.dp),
    ) {
        Row(Modifier.padding(16.dp), verticalAlignment = Alignment.CenterVertically) {
            Column(Modifier.weight(1f)) {
                Text("UNIDAD $number · ${block.title.es.uppercase()}", style = MaterialTheme.typography.labelMedium)
                Text(unit.title, modifier = Modifier.semantics { heading() }, style = MaterialTheme.typography.titleLarge)
            }
            TextButton(onClick = onTheory) { Text("Teoría", color = MaterialTheme.colorScheme.onPrimary) }
        }
    }
}

private enum class NodeState { DONE, CURRENT, LOCKED }

@Composable
private fun NodeButton(node: PathNode, position: Int, state: NodeState, unitTitle: String, onClick: () -> Unit) {
    val palette = LocalPalette.current
    val (background, content) = when (state) {
        NodeState.DONE -> palette.accent to MaterialTheme.colorScheme.background
        NodeState.CURRENT -> MaterialTheme.colorScheme.primary to MaterialTheme.colorScheme.onPrimary
        NodeState.LOCKED -> MaterialTheme.colorScheme.surfaceVariant to MaterialTheme.colorScheme.onSurfaceVariant
    }
    val label = when (state) {
        NodeState.DONE -> "completada"
        NodeState.CURRENT -> "disponible, toca para empezar"
        NodeState.LOCKED -> "bloqueada"
    }
    val ring = if (state == NodeState.CURRENT) Modifier.border(4.dp, MaterialTheme.colorScheme.outline, CircleShape) else Modifier
    Box(Modifier.fillMaxWidth(), contentAlignment = Alignment.Center) {
        Column(
            Modifier.offset(x = ZIGZAG[position % ZIGZAG.size].dp),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            if (state == NodeState.CURRENT) {
                Text("EMPEZAR", color = MaterialTheme.colorScheme.primary, fontWeight = FontWeight.Bold, style = MaterialTheme.typography.labelLarge)
            }
            Surface(
                shape = CircleShape,
                color = background,
                contentColor = content,
                modifier = Modifier
                    .size(if (state == NodeState.CURRENT) 76.dp else 64.dp)
                    .then(ring)
                    .clickable(enabled = state != NodeState.LOCKED, role = Role.Button, onClick = onClick)
                    .semantics { contentDescription = "Lección ${node.number} de $unitTitle: $label" },
            ) {
                Box(contentAlignment = Alignment.Center) {
                    Text(if (state == NodeState.DONE) "✓" else "${node.number}", fontSize = 24.sp, fontWeight = FontWeight.Bold)
                }
            }
        }
    }
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
