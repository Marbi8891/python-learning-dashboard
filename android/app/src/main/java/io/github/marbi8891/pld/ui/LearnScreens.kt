package io.github.marbi8891.pld.ui

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.selection.selectable
import androidx.compose.foundation.selection.selectableGroup
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.RadioButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.semantics.LiveRegionMode
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.heading
import androidx.compose.ui.semantics.liveRegion
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import io.github.marbi8891.pld.AppModel
import io.github.marbi8891.pld.learn.Exercise
import io.github.marbi8891.pld.learn.Grader
import io.github.marbi8891.pld.learn.LearnError
import io.github.marbi8891.pld.learn.LearnSession
import io.github.marbi8891.pld.learn.PlanItem
import io.github.marbi8891.pld.learn.Reply
import io.github.marbi8891.pld.learn.Result
import io.github.marbi8891.pld.learn.splitTheory
import io.github.marbi8891.pld.learn.stableOrder

/*
 * Núcleo educativo en el móvil (ADR-0031, fase 4): «Hoy» (¿qué estudio ahora?), teoría de cada
 * concepto y sesiones con corrección, explicación del error y nuevo intento. Misma lógica y mismo
 * progreso que la web; los ejercicios de escribir programas se hacen en la web (necesitan Python).
 */

private val ACTION = mapOf(
    "review" to "Repasar",
    "errors" to "Corregir errores",
    "practice" to "Practicar",
    "learn" to "Aprender",
    "reinforce" to "Reforzar",
)

private val STATUS = mapOf(
    "nuevo" to "Sin empezar",
    "leido" to "Teoría leída",
    "aprendiendo" to "Aprendiendo",
    "progreso" to "En progreso",
    "dominado" to "Dominado",
)

private fun pct(value: Double) = "${Math.round(value * 100)} %"

/** Pestaña «Hoy»: el plan de estudio con su motivo, lo más flojo y los repasos pendientes. */
@Composable
fun TodayScreen(model: AppModel, onStart: (PlanItem) -> Unit, onConcept: (String) -> Unit, modifier: Modifier = Modifier) {
    val revision = model.revision // se vuelve a pintar con cada guardado
    val learning = model.learning
    val plan = remember(revision) { learning.todayPlan() }
    val stats = remember(revision) { learning.allStats() }
    val mastered = stats.values.count { it.status == "dominado" }
    val weak = stats.values.filter { it.attempted > 0 && it.status != "dominado" }.sortedBy { it.score }.take(3)
    val due = stats.values.filter { it.due }
    Column(
        modifier
            .fillMaxSize()
            .statusBarsPadding()
            .verticalScroll(rememberScrollState())
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(14.dp),
    ) {
        Eyebrow("Hoy")
        Text(
            "¿Qué estudio ahora?",
            modifier = Modifier.semantics { heading() },
            style = MaterialTheme.typography.headlineMedium,
            color = MaterialTheme.colorScheme.onBackground,
        )
        if (plan.isEmpty()) Text("Has dominado todo el temario. Repasa o haz un simulacro en la web.")
        plan.forEachIndexed { i, item ->
            val concept = learning.content.concepts.getValue(item.concept)
            Panel(borderColor = if (i == 0) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.outline) {
                Text(ACTION.getValue(item.type).uppercase(), style = MaterialTheme.typography.labelMedium, color = LocalPalette.current.muted)
                Text(concept.title, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)
                Text(item.reason, style = MaterialTheme.typography.bodyMedium, color = LocalPalette.current.muted)
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp), verticalAlignment = Alignment.CenterVertically) {
                    if (i == 0) {
                        Button(onClick = { onStart(item) }) { Text("Empezar") }
                    } else {
                        OutlinedButton(onClick = { onStart(item) }) { Text("Empezar") }
                    }
                    TextButton(onClick = { onConcept(item.concept) }) { Text("Teoría") }
                }
            }
        }
        Panel {
            Text("Progreso", style = MaterialTheme.typography.titleMedium)
            Text("$mastered de ${stats.size} conceptos dominados")
            Meter(mastered.toDouble() / stats.size, "Conceptos dominados")
            if (due.isNotEmpty()) Text("Repasos pendientes: ${due.joinToString { learning.content.concepts.getValue(it.id).title }}.")
        }
        if (weak.isNotEmpty()) {
            Panel {
                Text("Puntos débiles", style = MaterialTheme.typography.titleMedium)
                weak.forEach { s ->
                    TextButton(onClick = { onConcept(s.id) }) { Text("${learning.content.concepts.getValue(s.id).title} · ${pct(s.score)}") }
                }
            }
        }
        Text(
            "Los ejercicios de escribir programas se corrigen con Python: hazlos en la web. El progreso es el mismo si inicias sesión.",
            style = MaterialTheme.typography.bodySmall,
            color = LocalPalette.current.muted,
        )
    }
}

/** Teoría de un concepto: explicación, ejemplo línea a línea, cuándo usarlo y errores habituales. */
@Composable
fun ConceptScreen(model: AppModel, id: String, onBack: () -> Unit, onPractice: () -> Unit) {
    val learning = model.learning
    val concept = learning.content.concepts.getValue(id)
    val stats = learning.stats(id)
    // Sin teoría propia, se reutiliza la de las lecciones del curso PCAP (no se duplica)
    val theory = concept.theory ?: concept.lessons.mapNotNull { model.pcapLesson(it)?.theory }.joinToString("\n\n")
    Scaffold(containerColor = MaterialTheme.colorScheme.background) { padding ->
        Column(
            Modifier
                .fillMaxSize()
                .padding(padding)
                .verticalScroll(rememberScrollState())
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp),
        ) {
            TextButton(onClick = onBack) { Text("← Volver") }
            Eyebrow(if (concept.daw == 3) "Imprescindible para DAW" else "Importante para DAW")
            Text(concept.title, modifier = Modifier.semantics { heading() }, style = MaterialTheme.typography.headlineMedium)
            RichText(concept.summary, color = LocalPalette.current.muted)
            Text("${STATUS.getValue(stats.status)} · ${pct(stats.score)} de dominio", style = MaterialTheme.typography.labelLarge)
            SectionTitle("Explicación")
            splitTheory(theory).forEach { part -> if (part.code) CodeBlock(part.text) else Markdown(part.text) }
            SectionTitle("Ejemplo, línea a línea")
            CodeBlock(concept.example.code.lines().mapIndexed { i, line -> "${(i + 1).toString().padStart(2)}  $line" }.joinToString("\n"))
            concept.example.lines.forEach { (n, text) ->
                Row {
                    Text("Línea $n", Modifier.width(72.dp), fontFamily = FontFamily.Monospace, color = LocalPalette.current.muted)
                    RichText(text, Modifier.weight(1f))
                }
            }
            if (concept.example.output.isNotBlank()) {
                Text("Salida", style = MaterialTheme.typography.titleSmall)
                CodeBlock(concept.example.output.trimEnd())
            }
            SectionTitle("Cuándo usarlo")
            RichText(concept.whenToUse)
            SectionTitle("Errores habituales")
            concept.errors.forEach { ErrorCard(it) }
            Button(onClick = onPractice, modifier = Modifier.fillMaxWidth()) { Text("Comprobar que lo entiendo") }
        }
    }
}

@Composable
private fun ErrorCard(error: LearnError) {
    Panel(borderColor = LocalPalette.current.danger) {
        RichText(error.label, style = MaterialTheme.typography.titleSmall)
        Labeled("Por qué está mal", error.why)
        Labeled("Cómo pensarlo", error.think)
        Labeled("Cómo evitarlo", error.avoid)
    }
}

@Composable
private fun Labeled(label: String, text: String) {
    Column {
        Text(label.uppercase(), style = MaterialTheme.typography.labelSmall, color = LocalPalette.current.muted)
        RichText(text, style = MaterialTheme.typography.bodyMedium)
    }
}

/** Sesión: intento → corrección → explicación (con el error típico) → nuevo intento al final → resumen. */
@Composable
fun LearnSessionScreen(model: AppModel, title: String, exercises: List<String>, onExit: () -> Unit) {
    val learning = model.learning
    val session = remember { LearnSession(title, exercises) }
    var tick by remember { mutableIntStateOf(0) } // la sesión es un objeto mutable: esto fuerza el repintado
    var reply by remember { mutableStateOf(Reply()) }
    var result by remember { mutableStateOf<Result?>(null) }
    var message by remember { mutableStateOf("") }
    var summary by remember { mutableStateOf<Map<String, Pair<Int, Int>>?>(null) }

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
            Text(title, modifier = Modifier.semantics { heading() }, style = MaterialTheme.typography.titleLarge)
            val item = remember(tick, result) { session.current }
            val done = summary
            when {
                done != null -> SessionSummary(model, session, done, onExit)
                item == null -> Text("No hay ejercicios para esta sesión.")
                else -> {
                    val exercise = learning.content.exercises.getValue(item.id)
                    Text("Ejercicio ${session.index + 1} de ${session.queue.size}", color = LocalPalette.current.muted)
                    if (item.retryOf != null) Text("Nuevo intento: aplica lo que acabas de ver.", fontWeight = FontWeight.SemiBold)
                    ExerciseInput(exercise, reply, reveal = result != null) { reply = it }
                    val current = result
                    if (current == null) {
                        if (message.isNotEmpty()) Text(message, color = LocalPalette.current.danger)
                        Button(onClick = {
                            val missing = Grader.missing(exercise, reply)
                            if (missing != null) {
                                message = missing
                            } else {
                                val graded = Grader.grade(exercise, reply)
                                session.submit(learning, graded)
                                if (item.retry.not()) learning.markRead(exercise.concept)
                                model.saveLearning()
                                result = graded
                                message = ""
                            }
                        }, modifier = Modifier.fillMaxWidth()) { Text("Comprobar") }
                        TextButton(onClick = {
                            session.submit(learning, Result(false, null))
                            model.saveLearning()
                            result = Result(false, null)
                        }) { Text("No lo sé: ver la explicación") }
                    } else {
                        Feedback(model, exercise, current, retry = session.queue.drop(session.index + 1).any { it.retryOf == item.id })
                        Button(onClick = {
                            session.next()
                            reply = Reply()
                            result = null
                            if (session.done) {
                                summary = session.finish(learning)
                                model.saveLearning()
                            }
                            tick++
                        }, modifier = Modifier.fillMaxWidth()) { Text(if (session.index + 1 < session.queue.size) "Siguiente →" else "Ver el resumen") }
                    }
                }
            }
        }
    }
}

@Composable
private fun Feedback(model: AppModel, exercise: Exercise, result: Result, retry: Boolean) {
    val error = result.error?.let { model.learning.content.errors[it] }
    Panel(
        modifier = Modifier.semantics { liveRegion = LiveRegionMode.Polite },
        borderColor = if (result.ok) LocalPalette.current.accent else LocalPalette.current.danger,
    ) {
        Text(if (result.ok) "✓ Correcto" else "✗ No es correcto", style = MaterialTheme.typography.titleMedium)
        Text(if (result.ok) "Por qué funciona" else "Cómo pensarlo", style = MaterialTheme.typography.titleSmall)
        Markdown(exercise.explain)
        if (!result.ok && exercise.kind == "output") {
            Text("Salida correcta", style = MaterialTheme.typography.titleSmall)
            CodeBlock(exercise.expect.orEmpty())
        }
        if (!result.ok && exercise.kind == "bug") {
            Text("Línea ${exercise.line} corregida", style = MaterialTheme.typography.titleSmall)
            CodeBlock(exercise.fix.ifEmpty { "(la línea sobra: hay que eliminarla)" })
        }
        if (error != null) {
            Text("Error típico detectado", style = MaterialTheme.typography.titleSmall)
            ErrorCard(error)
        }
        if (!result.ok && retry) Text("Al final volverás a intentarlo con un ejercicio parecido.", color = LocalPalette.current.muted)
    }
}

@Composable
private fun SessionSummary(model: AppModel, session: LearnSession, byConcept: Map<String, Pair<Int, Int>>, onExit: () -> Unit) {
    val content = model.learning.content
    val correct = byConcept.values.sumOf { it.first }
    val total = byConcept.values.sumOf { it.second }
    val errors = session.results.mapNotNull { it.second.error }.distinct().mapNotNull { content.errors[it] }
    Text("$correct de $total correctos", style = MaterialTheme.typography.headlineSmall)
    byConcept.forEach { (id, pair) ->
        Text("${content.concepts.getValue(id).title}: ${pair.first} de ${pair.second} · ${STATUS.getValue(model.learning.stats(id).status)}")
    }
    if (errors.isEmpty()) Text("No se ha detectado ningún error típico en esta sesión.")
    else {
        SectionTitle("Errores que has cometido")
        errors.forEach { ErrorCard(it) }
    }
    Button(onClick = onExit, modifier = Modifier.fillMaxWidth()) { Text("Volver a Hoy") }
}

/** Respuesta de cada tipo de ejercicio (salvo escribir código, que va en la web). */
@Composable
private fun ExerciseInput(exercise: Exercise, reply: Reply, reveal: Boolean, onChange: (Reply) -> Unit) {
    RichText(exercise.q, style = MaterialTheme.typography.titleMedium)
    when (exercise.kind) {
        "choice" -> {
            exercise.code?.let { CodeBlock(it) }
            Column(Modifier.selectableGroup()) {
                exercise.options.forEachIndexed { i, option ->
                    val correct = reveal && i == exercise.answer
                    Row(
                        Modifier
                            .fillMaxWidth()
                            .selectable(selected = reply.choice == i, enabled = !reveal, onClick = { onChange(reply.copy(choice = i)) }, role = Role.RadioButton)
                            .padding(vertical = 6.dp),
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        RadioButton(selected = reply.choice == i, onClick = null, enabled = !reveal)
                        val text = (if (correct) "✓ " else "") + option.text
                        if (exercise.codeOptions) Text(text, Modifier.padding(start = 6.dp), fontFamily = FontFamily.Monospace) else RichText(text, Modifier.padding(start = 6.dp))
                    }
                }
            }
        }
        "output", "fill" -> {
            exercise.code?.let { code ->
                CodeBlock(if (exercise.kind == "output") code.lines().mapIndexed { i, l -> "${(i + 1).toString().padStart(2)}  $l" }.joinToString("\n") else code)
            }
            if (exercise.stdin.isNotBlank()) Text("El usuario escribe: ${exercise.stdin.trim().replace("\n", " ⏎ ")}", color = LocalPalette.current.muted)
            OutlinedTextField(
                value = reply.text,
                onValueChange = { onChange(reply.copy(text = it)) },
                label = { Text(if (exercise.kind == "output") "Lo que muestra el programa" else "Lo que va en ___") },
                textStyle = TextStyle(fontFamily = FontFamily.Monospace),
                enabled = !reveal,
                minLines = if (exercise.kind == "output") 2 else 1,
                modifier = Modifier.fillMaxWidth(),
            )
            if (reveal && exercise.kind == "fill") Text("Solución: ${exercise.accept.first()}", fontFamily = FontFamily.Monospace)
        }
        "bug" -> {
            Text("Toca la línea que tiene el error", color = LocalPalette.current.muted)
            Column(Modifier.selectableGroup()) {
                exercise.code.orEmpty().lines().forEachIndexed { i, line ->
                    val n = i + 1
                    Row(
                        Modifier
                            .fillMaxWidth()
                            .selectable(selected = reply.line == n, enabled = !reveal, onClick = { onChange(reply.copy(line = n)) }, role = Role.RadioButton)
                            .padding(vertical = 4.dp),
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        RadioButton(selected = reply.line == n, onClick = null, enabled = !reveal)
                        Text("$n  $line" + if (reveal && n == exercise.line) "   ← aquí" else "", fontFamily = FontFamily.Monospace)
                    }
                }
            }
        }
        "order" -> {
            Text("Tu orden (toca una línea para quitarla)", style = MaterialTheme.typography.labelLarge)
            reply.order.forEachIndexed { k, i ->
                OutlinedButton(onClick = { onChange(reply.copy(order = reply.order - i)) }, enabled = !reveal, modifier = Modifier.fillMaxWidth()) {
                    Text("${k + 1}. ${exercise.lines[i]}", fontFamily = FontFamily.Monospace, modifier = Modifier.fillMaxWidth())
                }
            }
            val available = stableOrder(exercise.id, exercise.lines.size).filter { it !in reply.order }
            if (available.isNotEmpty()) Text("Líneas disponibles (toca para añadir)", style = MaterialTheme.typography.labelLarge)
            available.forEach { i ->
                OutlinedButton(onClick = { onChange(reply.copy(order = reply.order + i)) }, enabled = !reveal, modifier = Modifier.fillMaxWidth()) {
                    Text(exercise.lines[i], fontFamily = FontFamily.Monospace, modifier = Modifier.fillMaxWidth())
                }
            }
            if (reveal) CodeBlock(exercise.lines.joinToString("\n"))
        }
    }
}
