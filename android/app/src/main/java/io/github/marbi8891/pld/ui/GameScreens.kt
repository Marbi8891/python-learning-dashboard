package io.github.marbi8891.pld.ui

import androidx.compose.foundation.gestures.detectHorizontalDragGestures
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableLongStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.semantics.LiveRegionMode
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.heading
import androidx.compose.ui.semantics.liveRegion
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.IntOffset
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import io.github.marbi8891.pld.AppModel
import io.github.marbi8891.pld.pcap.AppProgress
import io.github.marbi8891.pld.pcap.DungeonRun
import io.github.marbi8891.pld.pcap.DungeonRun.Phase
import io.github.marbi8891.pld.pcap.Option
import io.github.marbi8891.pld.pcap.RushGame
import kotlinx.coroutines.delay
import kotlin.math.roundToInt

// Jefe de cada planta: solo ambientación, un nombre por bloque de cada curso
private val BOSSES = mapOf(
    "modulos" to "El Guardián de los Imports",
    "excepciones" to "La Hidra de las Excepciones",
    "strings" to "El Tejedor de Cadenas",
    "poo" to "El Arquitecto de Clases",
    "miscelanea" to "El Caos Final",
    "consultas" to "El Oráculo del SELECT",
    "agregacion" to "El Recaudador de Grupos",
    "joins" to "El Tejedor de Tablas",
    "ddl-dml" to "El Arquitecto de Esquemas",
    "diseno" to "El Guardián de la Transacción",
)

/* ---------------------------------------------------------------- Pestaña «Jugar» */

@Composable
fun GameHomeScreen(model: AppModel, onDungeon: () -> Unit, onRush: () -> Unit, modifier: Modifier = Modifier) {
    val revision = model.revision
    val records = remember(revision) { model.pcap.app.game }
    val active = model.dungeon?.takeIf { !it.finished }
    val palette = LocalPalette.current

    LazyColumn(
        modifier = modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        item {
            Text("Jugar", style = MaterialTheme.typography.headlineMedium, color = MaterialTheme.colorScheme.onBackground)
            Text("Aprende ${model.course.title} jugando. Aquí no gastas las vidas de la ruta.", color = palette.muted)
        }
        item {
            Panel {
                Eyebrow("Roguelite · 10-15 min")
                SectionTitle("⚔ La Mazmorra del Intérprete")
                Text(
                    "${model.bank.exam.blocks.size} plantas, una por bloque de ${model.course.title}. En cada sala te espera un bug: acierta para ganar monedas; " +
                        "si fallas, pierdes una de tus 5 vidas. Al final de cada planta, un jefe con cronómetro. " +
                        "Los bugs empiezan por lo que más fallas y tus respuestas cuentan para la preparación.",
                )
                Text(
                    "Récord: ${records.bestFloors} de ${model.bank.exam.blocks.size} plantas · ${records.bestScore} 🪙 · ${records.runs} partidas",
                    style = MaterialTheme.typography.bodySmall,
                    color = palette.muted,
                )
                if (active != null) {
                    Button(onClick = onDungeon, modifier = Modifier.fillMaxWidth()) {
                        Text("Continuar partida (planta ${active.floor + 1})")
                    }
                    OutlinedButton(onClick = { model.abandonDungeon() }, modifier = Modifier.fillMaxWidth()) { Text("Abandonar partida") }
                } else {
                    Button(
                        onClick = {
                            model.startDungeon()
                            onDungeon()
                        },
                        modifier = Modifier.fillMaxWidth(),
                    ) { Text("Entrar en la mazmorra") }
                }
            }
        }
        item {
            Panel {
                Eyebrow("Minijuego · 90 s")
                SectionTitle("⚡ Bug Rush")
                Text(
                    "Código y una respuesta propuesta: ¿es la correcta? Desliza a la derecha si lo es y a la izquierda si no. " +
                        "Los aciertos seguidos multiplican los puntos; cada fallo te quita ${RushGame.PENALTY_SECONDS} segundos.",
                )
                Text("Récord: ${records.bestRush} puntos", style = MaterialTheme.typography.bodySmall, color = palette.muted)
                Button(onClick = onRush, modifier = Modifier.fillMaxWidth()) { Text("Jugar") }
            }
        }
    }
}

/* ---------------------------------------------------------------- Mazmorra */

@Composable
fun DungeonScreen(model: AppModel, onExit: () -> Unit, onTheory: (String) -> Unit) {
    val run = model.dungeon
    if (run == null) {
        LaunchedEffect(Unit) { onExit() }
        return
    }
    // DungeonRun no es observable: cada acción suma 1 y la pantalla se repinta
    var tick by remember { mutableIntStateOf(0) }
    val phase = remember(tick) { run.phase }
    val act: (() -> Unit) -> Unit = { change ->
        change()
        if (run.finished) model.update { app.game.recordRun(run) }
        tick++
    }
    val lang = remember(model.revision) { model.pcap.lang }
    val palette = LocalPalette.current
    val scroll = rememberScrollState()
    LaunchedEffect(run.floor, run.room, phase) { if (phase == Phase.ASK) scroll.scrollTo(0) }

    Scaffold(containerColor = MaterialTheme.colorScheme.background) { padding ->
        Column(
            Modifier
                .fillMaxSize()
                .padding(padding)
                .verticalScroll(scroll)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp),
        ) {
            TextButton(onClick = onExit) { Text("← Salir (la partida se guarda)") }
            DungeonHeader(model, run)
            when (phase) {
                Phase.ASK, Phase.FEEDBACK -> Room(model, run, phase, lang, onTheory, act = act, next = { act { run.next() } })
                Phase.FLOOR_CLEARED -> Panel(borderColor = palette.accent) {
                    SectionTitle("Planta ${run.floor + 1} superada")
                    Text("Has derrotado a ${BOSSES[run.block] ?: "el jefe"}. +${DungeonRun.FLOOR_BONUS} 🪙 de botín.")
                    HealButton(run) { act { run.heal() } }
                    Button(onClick = { act { run.enterNextFloor() } }, modifier = Modifier.fillMaxWidth()) {
                        Text("Bajar a la planta ${run.floor + 2}")
                    }
                }
                Phase.WON, Phase.LOST -> Summary(model, run, onExit = {
                    model.dungeon = null
                    onExit()
                }, onAgain = {
                    model.startDungeon()
                    tick++
                })
            }
        }
    }
}

@Composable
private fun DungeonHeader(model: AppModel, run: DungeonRun) {
    val palette = LocalPalette.current
    val block = model.bank.block(run.block)
    Row(verticalAlignment = Alignment.CenterVertically) {
        Text(
            "Planta ${run.floor + 1}/${run.floors.size} · ${block.title.es}",
            modifier = Modifier
                .weight(1f)
                .semantics { heading() },
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold,
        )
        Text(
            "♥".repeat(run.hp.coerceAtLeast(0)) + "♡".repeat((DungeonRun.MAX_HP - run.hp).coerceAtLeast(0)),
            modifier = Modifier
                .padding(end = 12.dp)
                .semantics { contentDescription = "Vidas de la partida: ${run.hp} de ${DungeonRun.MAX_HP}" },
            color = palette.danger,
            fontSize = 18.sp,
        )
        Text(
            "🪙 ${run.coins}",
            modifier = Modifier.semantics { contentDescription = "${run.coins} monedas" },
            fontWeight = FontWeight.Bold,
        )
    }
    LinearProgressIndicator(
        progress = { (run.room + if (run.phase == Phase.ASK) 0 else 1).toFloat() / run.roomsInFloor },
        modifier = Modifier
            .fillMaxWidth()
            .semantics { contentDescription = "Sala ${run.room + 1} de ${run.roomsInFloor}" },
        color = palette.accent,
        trackColor = MaterialTheme.colorScheme.outline,
    )
}

@Composable
private fun Room(
    model: AppModel,
    run: DungeonRun,
    phase: Phase,
    lang: String,
    onTheory: (String) -> Unit,
    act: (() -> Unit) -> Unit,
    next: () -> Unit,
) {
    val palette = LocalPalette.current
    val haptics = LocalHapticFeedback.current
    val question = run.current
    val buzz: (Boolean) -> Unit = { ok ->
        haptics.performHapticFeedback(if (ok) HapticFeedbackType.TextHandleMove else HapticFeedbackType.LongPress)
    }
    var chosen by remember(run, run.floor, run.room) { mutableStateOf(setOf<Int>()) }
    var secondsLeft by remember(run, run.floor, run.room) { mutableIntStateOf(DungeonRun.BOSS_SECONDS) }

    // Cronómetro del jefe: al llegar a cero cuenta como fallo
    if (run.isBoss && phase == Phase.ASK) {
        LaunchedEffect(run, run.floor, run.room) {
            while (secondsLeft > 0) {
                delay(1_000)
                secondsLeft--
            }
            act {
                run.timeout()
                model.update { recordAnswer(question.id, false) }
            }
            buzz(false)
        }
    }

    if (run.isBoss) {
        Text(
            "JEFE: ${BOSSES[run.block] ?: "Jefe"} · golpe ${run.room - DungeonRun.ROOMS + 1} de ${DungeonRun.BOSS}",
            color = palette.danger,
            fontWeight = FontWeight.Bold,
        )
        if (phase == Phase.ASK) {
            Text(
                "⏱ $secondsLeft s",
                modifier = Modifier.semantics { if (secondsLeft % 15 == 0 || secondsLeft <= 5) liveRegion = LiveRegionMode.Polite },
                color = if (secondsLeft <= 10) palette.danger else palette.muted,
                fontWeight = FontWeight.Bold,
            )
        }
    } else {
        Text("Sala ${run.room + 1} de ${DungeonRun.ROOMS} · 🐛 Un bug salvaje aparece", color = palette.muted)
    }

    QuestionView(
        question,
        lang,
        chosen,
        reveal = phase == Phase.FEEDBACK,
        hidden = run.hidden,
        onSelect = { option ->
            chosen = when {
                !question.multi -> setOf(option)
                option in chosen -> chosen - option
                else -> chosen + option
            }
        },
    )

    if (phase == Phase.ASK) {
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            OutlinedButton(onClick = { act { run.fiftyFifty() } }, enabled = run.canFiftyFifty(), modifier = Modifier.weight(1f)) {
                Text("50/50 · ${DungeonRun.FIFTY_COST} 🪙")
            }
            HealButton(run, Modifier.weight(1f)) { act { run.heal() } }
        }
        Button(
            onClick = {
                act {
                    val ok = run.answer(chosen)
                    model.update {
                        recordAnswer(question.id, ok)
                        if (ok) app.addXp(AppProgress.XP_PRACTICE)
                    }
                    buzz(ok)
                }
            },
            enabled = chosen.size == question.answer.size,
            modifier = Modifier.fillMaxWidth(),
        ) { Text("⚔ Atacar") }
    } else {
        val last = run.last
        val ok = last?.correct == true
        Panel(borderColor = if (ok) palette.accent else palette.danger) {
            Text(
                when {
                    ok -> "¡Golpe certero! +${last?.coins} 🪙"
                    last?.timedOut == true -> "¡Se acabó el tiempo! El jefe te golpea: −1 ♥"
                    else -> "El bug te golpea: −1 ♥"
                },
                modifier = Modifier.semantics { liveRegion = LiveRegionMode.Polite },
                color = if (ok) palette.accent else palette.danger,
                fontWeight = FontWeight.Bold,
                style = MaterialTheme.typography.titleMedium,
            )
            RichText(question.explain.get(lang))
            val lesson = question.lesson
            if (lesson != null && lesson in model.content) {
                TextButton(onClick = { onTheory(lesson) }) { Text("Ver la teoría: ${model.content.getValue(lesson).title}") }
            }
        }
        Button(onClick = next, modifier = Modifier.fillMaxWidth()) { Text(if (run.hp <= 0) "Ver resultado" else "Continuar") }
    }
}

@Composable
private fun HealButton(run: DungeonRun, modifier: Modifier = Modifier, onHeal: () -> Unit) {
    OutlinedButton(onClick = onHeal, enabled = run.canHeal(), modifier = modifier) {
        Text("Curar ♥ · ${DungeonRun.HEAL_COST} 🪙")
    }
}

@Composable
private fun Summary(model: AppModel, run: DungeonRun, onExit: () -> Unit, onAgain: () -> Unit) {
    val palette = LocalPalette.current
    val records = model.pcap.app.game
    val won = run.phase == Phase.WON
    Panel(borderColor = if (won) palette.accent else palette.danger) {
        Text(if (won) "🏆" else "💀", fontSize = 56.sp)
        SectionTitle(if (won) "¡Has conquistado la mazmorra!" else "Has caído en la planta ${run.floor + 1}")
        Text("Plantas superadas: ${run.floorsCleared} de ${run.floors.size}")
        Text("Puntuación: ${run.score} 🪙")
        Text("Aciertos: ${run.correct} de ${run.answered}")
        Text(
            "Récord: ${records.bestFloors} plantas · ${records.bestScore} 🪙",
            color = palette.muted,
            style = MaterialTheme.typography.bodySmall,
        )
        Text(
            "Lo que has fallado saldrá antes en la próxima partida y en la práctica.",
            color = palette.muted,
            style = MaterialTheme.typography.bodySmall,
        )
        Button(onClick = onAgain, modifier = Modifier.fillMaxWidth()) { Text("Otra partida") }
        OutlinedButton(onClick = onExit, modifier = Modifier.fillMaxWidth()) { Text("Salir") }
    }
}

/* ---------------------------------------------------------------- Bug Rush */

@Composable
fun RushScreen(model: AppModel, onExit: () -> Unit) {
    val pool = remember { RushGame.pool(model.bank) }
    var round by remember { mutableIntStateOf(0) }
    val game = remember(round) { RushGame(pool) }
    var playing by remember(round) { mutableStateOf(false) }
    var finished by remember(round) { mutableStateOf(false) }
    var elapsed by remember(round) { mutableLongStateOf(0L) }
    var tick by remember(round) { mutableIntStateOf(0) }
    var newRecord by remember(round) { mutableStateOf(false) }
    val lang = remember(model.revision) { model.pcap.lang }
    val palette = LocalPalette.current
    val haptics = LocalHapticFeedback.current

    val left = (RushGame.DURATION_SECONDS - (elapsed / 1000).toInt() - remember(tick) { game.penalty }).coerceAtLeast(0)

    if (playing) {
        LaunchedEffect(round) {
            val start = System.currentTimeMillis()
            while (RushGame.DURATION_SECONDS * 1000L - (System.currentTimeMillis() - start) - game.penalty * 1000L > 0) {
                delay(200)
                elapsed = System.currentTimeMillis() - start
            }
            playing = false
            finished = true
            newRecord = model.update {
                app.addXp(game.xp)
                app.game.recordRush(game.score)
            }
        }
    }

    Scaffold(containerColor = MaterialTheme.colorScheme.background) { padding ->
        Column(
            Modifier
                .fillMaxSize()
                .padding(padding)
                .verticalScroll(rememberScrollState())
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp),
        ) {
            TextButton(onClick = onExit) { Text("← Salir") }
            Text("⚡ Bug Rush", style = MaterialTheme.typography.headlineSmall, modifier = Modifier.semantics { heading() })

            when {
                finished -> Panel(borderColor = palette.accent) {
                    SectionTitle(if (newRecord) "¡Récord nuevo: ${game.score} puntos!" else "${game.score} puntos")
                    Text("Aciertos: ${game.correct} de ${game.answered} · mejor combo: ${game.bestCombo}")
                    Text("+${game.xp} XP", color = MaterialTheme.colorScheme.primary, fontWeight = FontWeight.Bold)
                    Text("Récord: ${model.pcap.app.game.bestRush} puntos", color = palette.muted, style = MaterialTheme.typography.bodySmall)
                    Button(onClick = { round++ }, modifier = Modifier.fillMaxWidth()) { Text("Otra vez") }
                    OutlinedButton(onClick = onExit, modifier = Modifier.fillMaxWidth()) { Text("Salir") }
                }
                !playing -> Panel {
                    Text("Verás código y una respuesta propuesta. ¿Es la correcta?")
                    Text("→ Desliza a la derecha (o toca «Sí») si lo es.\n← Desliza a la izquierda (o toca «No») si no.")
                    Text(
                        "Cada ${RushGame.COMBO_STEP} aciertos seguidos suben el multiplicador (hasta ×${RushGame.MAX_MULTIPLIER}). " +
                            "Cada fallo te quita ${RushGame.PENALTY_SECONDS} s.",
                        color = palette.muted,
                    )
                    Button(onClick = { playing = true }, modifier = Modifier.fillMaxWidth()) {
                        Text("Empezar (${RushGame.DURATION_SECONDS} s)")
                    }
                }
                else -> {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text(
                            "⏱ $left s",
                            modifier = Modifier.weight(1f),
                            color = if (left <= 10) palette.danger else MaterialTheme.colorScheme.onBackground,
                            fontWeight = FontWeight.Bold,
                        )
                        Text("×${game.multiplier}", modifier = Modifier.padding(end = 12.dp), color = palette.streak, fontWeight = FontWeight.Bold)
                        Text("${game.score} pts", fontWeight = FontWeight.Bold)
                    }
                    val judge: (Boolean) -> Unit = { yes ->
                        val ok = game.judge(yes)
                        haptics.performHapticFeedback(if (ok) HapticFeedbackType.TextHandleMove else HapticFeedbackType.LongPress)
                        tick++
                    }
                    RushCard(game.card, lang, judge)
                    Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                        Button(
                            onClick = { judge(false) },
                            modifier = Modifier.weight(1f),
                            colors = ButtonDefaults.buttonColors(containerColor = palette.danger, contentColor = MaterialTheme.colorScheme.background),
                        ) { Text("✗ No") }
                        Button(
                            onClick = { judge(true) },
                            modifier = Modifier.weight(1f),
                            colors = ButtonDefaults.buttonColors(containerColor = palette.accent, contentColor = MaterialTheme.colorScheme.background),
                        ) { Text("✓ Sí") }
                    }
                    game.last?.let { (card, ok) ->
                        val right = card.question.options[card.question.answer.single()]
                        Text(
                            if (ok) "✓ Bien" else "✗ Fallo. La respuesta correcta era: ${optionLabel(right, lang)}",
                            modifier = Modifier.semantics { liveRegion = LiveRegionMode.Polite },
                            color = if (ok) palette.accent else palette.danger,
                        )
                    }
                }
            }
        }
    }
}

/** Tarjeta que se desliza: más de 120 px a un lado cuenta como respuesta. */
@Composable
private fun RushCard(card: RushGame.Card, lang: String, onJudge: (Boolean) -> Unit) {
    var dx by remember(card) { mutableFloatStateOf(0f) }
    val palette = LocalPalette.current
    val border = when {
        dx > 60f -> palette.accent
        dx < -60f -> palette.danger
        else -> MaterialTheme.colorScheme.outline
    }
    Panel(
        modifier = Modifier
            .offset { IntOffset(dx.roundToInt(), 0) }
            .pointerInput(card) {
                detectHorizontalDragGestures(
                    onDragEnd = {
                        when {
                            dx > 120f -> onJudge(true)
                            dx < -120f -> onJudge(false)
                        }
                        dx = 0f
                    },
                    onDragCancel = { dx = 0f },
                ) { _, amount -> dx += amount }
            },
        borderColor = border,
    ) {
        RichText(card.question.q.get(lang), style = MaterialTheme.typography.titleMedium)
        card.question.code?.let { CodeBlock(it) }
        Text("¿Es esta la respuesta?", color = palette.muted, style = MaterialTheme.typography.labelLarge)
        Text(
            optionLabel(card.question.options[card.option], lang),
            fontFamily = if (card.question.options[card.option] is Option.Code) FontFamily.Monospace else null,
            fontWeight = FontWeight.Bold,
            style = MaterialTheme.typography.titleLarge,
        )
    }
}

private fun optionLabel(option: Option, lang: String): String = when (option) {
    is Option.Code -> option.source
    is Option.Prose -> option.text.get(lang)
}
