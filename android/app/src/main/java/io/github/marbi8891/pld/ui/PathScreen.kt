package io.github.marbi8891.pld.ui

import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.pager.HorizontalPager
import androidx.compose.foundation.pager.rememberPagerState
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.semantics.clearAndSetSemantics
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.heading
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import io.github.marbi8891.pld.AppModel
import io.github.marbi8891.pld.pcap.Book
import io.github.marbi8891.pld.pcap.PathNode
import io.github.marbi8891.pld.pcap.PathUnit
import io.github.marbi8891.pld.pcap.UnitState
import io.github.marbi8891.pld.pcap.UnitSummary
import io.github.marbi8891.pld.pcap.unitSummary
import kotlinx.coroutines.launch
import java.time.Duration
import kotlin.math.roundToInt

/*
 * Pestaña «Ruta» como un libro (ADR-0029). Cada tema es una página que se pasa deslizando.
 * Arriba, siempre, el nombre del tema de la página y dos desplegables: sus lecciones y el índice
 * de todos los temas. La página abre con una entradilla sacada de la teoría y el botón de lo que toca.
 */

private enum class LessonState { DONE, CURRENT, LOCKED }

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
    val units = model.units
    val current = remember(revision) { app.currentNode(units) }
    val pager = rememberPagerState(initialPage = Book.openingPage(units, current)) { units.size }
    val scope = rememberCoroutineScope()
    var noHeartsFor by remember { mutableStateOf<PathNode?>(null) }
    val goTo: (Int) -> Unit = { page -> scope.launch { pager.animateScrollToPage(page) } }
    val start: (PathNode) -> Unit = { node -> if (app.heartsNow() > 0) onStart(node) else noHeartsFor = node }
    val stateOf: (PathNode) -> LessonState = { node ->
        when {
            node.id in app.done -> LessonState.DONE
            node == current -> LessonState.CURRENT
            else -> LessonState.LOCKED
        }
    }

    if (units.isEmpty()) return
    val shown = units[pager.currentPage.coerceIn(0, units.lastIndex)]

    Column(modifier.fillMaxSize()) {
        StatusBar(model)
        BookHeader(
            units = units,
            page = pager.currentPage,
            unit = shown,
            stateOf = stateOf,
            onLesson = start,
            onChapter = goTo,
        )
        HorizontalDivider()
        HorizontalPager(state = pager, modifier = Modifier.weight(1f), beyondViewportPageCount = 1) { page ->
            val unit = units[page]
            val summary = remember(revision, page) { model.pcap.unitSummary(unit, current) }
            val next = unit.nodes.firstOrNull { stateOf(it) == LessonState.CURRENT }
            BookPage(
                unit = unit,
                number = page + 1,
                summary = summary,
                intro = remember(unit.slug) { Book.intro(model.content[unit.slug]?.theory.orEmpty()) },
                next = next,
                onStart = start,
                onPractice = { onPractice(unit.block) },
                onTheory = { onTheory(unit.slug) },
            )
        }
        PageFooter(page = pager.currentPage, pages = units.size, onPrevious = { goTo(pager.currentPage - 1) }, onNext = { goTo(pager.currentPage + 1) })
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

/** Racha, XP de hoy frente a la meta y vidas: tres cifras tranquilas. */
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
    Row(verticalAlignment = Alignment.Bottom, modifier = Modifier.clearAndSetSemantics { contentDescription = "$value $label" }) {
        Text(value, color = color, fontWeight = FontWeight.SemiBold, fontSize = 17.sp)
        Text(" $label", color = LocalPalette.current.muted, style = MaterialTheme.typography.labelMedium)
    }
}

/**
 * Cabecera del libro: el tema de la página, el desplegable con sus lecciones y el índice.
 * Cambia sola al pasar de página.
 */
@Composable
private fun BookHeader(
    units: List<PathUnit>,
    page: Int,
    unit: PathUnit,
    stateOf: (PathNode) -> LessonState,
    onLesson: (PathNode) -> Unit,
    onChapter: (Int) -> Unit,
) {
    val palette = LocalPalette.current
    var lessonsOpen by remember { mutableStateOf(false) }
    var indexOpen by remember { mutableStateOf(false) }

    Column(Modifier.padding(start = 20.dp, end = 8.dp, top = 4.dp, bottom = 10.dp)) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Column(Modifier.weight(1f)) {
                Text(
                    "TEMA ${page + 1} DE ${units.size}",
                    style = MaterialTheme.typography.labelSmall,
                    letterSpacing = 1.2.sp,
                    color = palette.muted,
                    fontWeight = FontWeight.SemiBold,
                )
                Text(
                    unit.title,
                    modifier = Modifier.semantics { heading() },
                    style = MaterialTheme.typography.titleLarge,
                    maxLines = 2,
                    overflow = TextOverflow.Ellipsis,
                )
            }
            // Índice de todos los temas, como el de un libro
            Box {
                TextButton(onClick = { indexOpen = true }) { Text("Índice", color = palette.muted) }
                DropdownMenu(expanded = indexOpen, onDismissRequest = { indexOpen = false }) {
                    units.forEachIndexed { i, u ->
                        DropdownMenuItem(
                            text = {
                                Text(
                                    "${i + 1}. ${u.title}",
                                    fontWeight = if (i == page) FontWeight.Bold else FontWeight.Normal,
                                    maxLines = 1,
                                    overflow = TextOverflow.Ellipsis,
                                )
                            },
                            onClick = {
                                indexOpen = false
                                onChapter(i)
                            },
                        )
                    }
                }
            }
        }
        // Desplegable con todas las lecciones del tema
        Box(Modifier.padding(top = 6.dp)) {
            val done = unit.nodes.count { stateOf(it) == LessonState.DONE }
            OutlinedButton(
                onClick = { lessonsOpen = true },
                modifier = Modifier.semantics { contentDescription = "Lecciones del tema: $done de ${unit.nodes.size} hechas. Abrir la lista" },
            ) {
                Text("${unit.nodes.size} ${if (unit.nodes.size == 1) "lección" else "lecciones"} · $done hechas  ▾")
            }
            DropdownMenu(expanded = lessonsOpen, onDismissRequest = { lessonsOpen = false }) {
                unit.nodes.forEach { node ->
                    val state = stateOf(node)
                    val questions = "${node.questionIds.size} preguntas"
                    DropdownMenuItem(
                        enabled = state != LessonState.LOCKED,
                        leadingIcon = {
                            Text(
                                when (state) {
                                    LessonState.DONE -> "✓"
                                    LessonState.CURRENT -> "▶"
                                    LessonState.LOCKED -> "·"
                                },
                                color = when (state) {
                                    LessonState.DONE -> palette.accent
                                    LessonState.CURRENT -> MaterialTheme.colorScheme.primary
                                    LessonState.LOCKED -> palette.muted
                                },
                                fontWeight = FontWeight.Bold,
                            )
                        },
                        text = {
                            Column {
                                Text("Lección ${node.number}", fontWeight = if (state == LessonState.CURRENT) FontWeight.Bold else FontWeight.Normal)
                                Text(
                                    when (state) {
                                        LessonState.DONE -> "Hecha · $questions · repetir"
                                        LessonState.CURRENT -> "La que toca · $questions"
                                        LessonState.LOCKED -> "Bloqueada · $questions"
                                    },
                                    style = MaterialTheme.typography.bodySmall,
                                    color = palette.muted,
                                )
                            }
                        },
                        onClick = {
                            lessonsOpen = false
                            onLesson(node)
                        },
                    )
                }
            }
        }
    }
}

/** Una página del libro: número y título del tema, entradilla de la teoría y lo que toca hacer. */
@Composable
private fun BookPage(
    unit: PathUnit,
    number: Int,
    summary: UnitSummary,
    intro: String,
    next: PathNode?,
    onStart: (PathNode) -> Unit,
    onPractice: () -> Unit,
    onTheory: () -> Unit,
) {
    val palette = LocalPalette.current
    val colors = MaterialTheme.colorScheme
    val progress by animateFloatAsState(summary.progress, tween(600), label = "tema")
    val accuracy = summary.rate?.let { "aciertas el ${(it * 100).roundToInt()} %" } ?: "aún sin responder"
    val status = when (summary.state) {
        UnitState.DONE -> "Tema completado"
        UnitState.CURRENT -> "En curso"
        UnitState.LOCKED -> "Por empezar"
    }

    Column(
        Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(horizontal = 28.dp, vertical = 20.dp),
        verticalArrangement = Arrangement.spacedBy(14.dp),
    ) {
        // Número de capítulo grande y en serif, como en un libro
        Text(
            "$number",
            fontFamily = FontFamily.Serif,
            fontSize = 56.sp,
            lineHeight = 56.sp,
            color = if (summary.state == UnitState.LOCKED) colors.outline else colors.primary.copy(alpha = 0.85f),
            modifier = Modifier.clearAndSetSemantics { },
        )
        Text(unit.title, style = MaterialTheme.typography.headlineMedium)
        Text(
            "$status · ${summary.lessonsDone} de ${summary.lessons} lecciones · $accuracy",
            style = MaterialTheme.typography.bodyMedium,
            color = palette.muted,
        )
        Box(
            Modifier
                .fillMaxWidth()
                .height(3.dp)
                .background(colors.outline, RoundedCornerShape(2.dp)),
        ) {
            Box(
                Modifier
                    .fillMaxWidth(progress)
                    .height(3.dp)
                    .background(if (summary.state == UnitState.DONE) palette.accent else colors.primary, RoundedCornerShape(2.dp)),
            )
        }

        if (intro.isNotEmpty()) {
            RichText(intro, style = MaterialTheme.typography.bodyLarge.copy(fontFamily = FontFamily.Serif, lineHeight = 26.sp))
        }
        TextButton(onClick = onTheory, modifier = Modifier.semantics { contentDescription = "Leer la teoría de ${unit.title}" }) {
            Text("Leer la teoría completa ›")
        }

        Spacer(Modifier.height(4.dp))
        when {
            next != null -> Button(onClick = { onStart(next) }, modifier = Modifier.fillMaxWidth()) {
                Text("Continuar · Lección ${next.number} de ${unit.nodes.size}")
            }
            summary.state == UnitState.DONE -> Button(onClick = onPractice, modifier = Modifier.fillMaxWidth()) {
                Text("Repasar este tema")
            }
            else -> Text(
                "Termina el tema anterior para empezar este. Mientras, puedes leer la teoría o practicar.",
                style = MaterialTheme.typography.bodyMedium,
                color = palette.muted,
            )
        }
        if (summary.state != UnitState.DONE) {
            OutlinedButton(onClick = onPractice, modifier = Modifier.fillMaxWidth()) { Text("Practicar este tema (sin gastar vidas)") }
        }
    }
}

/** Pie de página: anterior, número de página y siguiente. */
@Composable
private fun PageFooter(page: Int, pages: Int, onPrevious: () -> Unit, onNext: () -> Unit) {
    val palette = LocalPalette.current
    HorizontalDivider()
    Row(
        Modifier
            .fillMaxWidth()
            .padding(horizontal = 8.dp, vertical = 4.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        TextButton(onClick = onPrevious, enabled = page > 0) { Text("‹ Anterior") }
        Text(
            "${page + 1} / $pages",
            modifier = Modifier
                .weight(1f)
                .semantics { contentDescription = "Página ${page + 1} de $pages" },
            color = palette.muted,
            style = MaterialTheme.typography.labelLarge,
            textAlign = androidx.compose.ui.text.style.TextAlign.Center,
        )
        TextButton(onClick = onNext, enabled = page < pages - 1) { Text("Siguiente ›") }
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
