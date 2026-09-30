package io.github.marbi8891.pld.ui

import android.app.DatePickerDialog
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.Button
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalUriHandler
import androidx.compose.ui.semantics.LiveRegionMode
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.liveRegion
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import io.github.marbi8891.pld.AppModel
import io.github.marbi8891.pld.BuildConfig
import io.github.marbi8891.pld.CourseData
import io.github.marbi8891.pld.pcap.Achievements
import io.github.marbi8891.pld.pcap.ActivityItem
import io.github.marbi8891.pld.pcap.ApiException
import io.github.marbi8891.pld.pcap.CourseOverview
import io.github.marbi8891.pld.pcap.Overview
import kotlinx.coroutines.launch
import java.time.Instant
import java.time.LocalDate
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.util.Locale
import kotlin.math.roundToInt

/*
 * «Mi cuenta» en la app (ADR-0027), igual que en la web (ADR-0025): plan de estudio, progreso de
 * todos los cursos, simulacros, certificados, logros y perfil y seguridad.
 */

private val DAY = DateTimeFormatter.ofPattern("d MMM yyyy", Locale.forLanguageTag("es-ES"))
private val WHEN = DateTimeFormatter.ofPattern("d MMM, HH:mm", Locale.forLanguageTag("es-ES"))

/** Resumen de cada curso; se recalcula cuando cambia el progreso. */
@Composable
fun rememberOverviews(model: AppModel): List<Pair<CourseData, CourseOverview>> =
    remember(model.revision) { model.courses.map { it to Overview.of(it.state, it.bank, it.isPcap) } }

/** Fecha del examen y repaso pendiente de cada curso. */
@Composable
fun StudyPlanPanel(model: AppModel, overviews: List<Pair<CourseData, CourseOverview>>) {
    val context = LocalContext.current
    val palette = LocalPalette.current
    Panel {
        SectionTitle("Mi plan de estudio")
        Text(
            "Pon la fecha de cada examen. Se sincroniza con «Mi cuenta» de la web.",
            style = MaterialTheme.typography.bodySmall,
            color = palette.muted,
        )
        overviews.forEachIndexed { i, (course, o) ->
            if (i > 0) HorizontalDivider()
            Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                Text(course.title, fontWeight = FontWeight.SemiBold)
                Text(
                    buildString {
                        append(o.examDate?.let { "Examen: ${it.format(DAY)} · ${Overview.countdown(o.daysLeft)}" } ?: "Sin fecha de examen")
                        append(" · ")
                        append(if (o.due > 0) "${o.due} por repasar hoy" else "Repaso al día")
                    },
                    style = MaterialTheme.typography.bodyMedium,
                    color = if (o.daysLeft != null && o.daysLeft in 0L..7L) palette.danger else MaterialTheme.colorScheme.onSurface,
                )
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    OutlinedButton(
                        onClick = {
                            val start = o.examDate ?: LocalDate.now().plusMonths(1)
                            DatePickerDialog(
                                context,
                                { _, year, month, day -> model.setExamDate(course.id, LocalDate.of(year, month + 1, day).toString()) },
                                start.year,
                                start.monthValue - 1,
                                start.dayOfMonth,
                            ).show()
                        },
                        modifier = Modifier.semantics { contentDescription = "Elegir la fecha del examen de ${course.title}" },
                    ) { Text(if (o.examDate == null) "Poner fecha" else "Cambiar fecha") }
                    if (o.examDate != null) {
                        TextButton(onClick = { model.setExamDate(course.id, null) }) { Text("Quitar") }
                    }
                }
            }
        }
    }
}

/** Dominio de cada curso y su tema más flojo, con un botón para practicarlo. */
@Composable
fun CoursesProgressPanel(overviews: List<Pair<CourseData, CourseOverview>>, onPractice: (String, String) -> Unit) {
    val palette = LocalPalette.current
    Panel {
        SectionTitle("Mi progreso en todos los cursos")
        Text("Incluye lo que haces en la web si has iniciado sesión.", style = MaterialTheme.typography.bodySmall, color = palette.muted)
        overviews.forEachIndexed { i, (course, o) ->
            if (i > 0) HorizontalDivider()
            Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(course.title, modifier = Modifier.weight(1f), fontWeight = FontWeight.SemiBold)
                    Text("${o.score} %", color = MaterialTheme.colorScheme.primary, fontWeight = FontWeight.Bold)
                }
                Meter(o.score / 100.0, "Dominio de ${course.title}")
                Text(
                    "${o.answered} preguntas respondidas · ${o.exams} ${if (o.exams == 1) "simulacro" else "simulacros"}" +
                        (o.bestExam?.let { " (mejor: $it %)" } ?: ""),
                    style = MaterialTheme.typography.bodySmall,
                    color = palette.muted,
                )
                val focus = o.focus
                if (focus != null) {
                    Text(
                        o.focusRate?.let { "Tema más flojo: ${focus.title.es} (${(it * 100).roundToInt()} %)" }
                            ?: "Siguiente tema sin empezar: ${focus.title.es}",
                        style = MaterialTheme.typography.bodyMedium,
                    )
                    OutlinedButton(onClick = { onPractice(course.id, focus.slug) }) {
                        Text(if (o.focusRate != null) "Practicarlo" else "Empezar")
                    }
                } else {
                    Text("Vas bien en todos los temas. Haz un simulacro para comprobarlo.", style = MaterialTheme.typography.bodyMedium)
                }
            }
        }
    }
}

/** Los 10 últimos simulacros de todos los cursos (del móvil y, con cuenta, de la web). */
@Composable
fun ExamHistoryPanel(model: AppModel) {
    val palette = LocalPalette.current
    val exams = remember(model.revision) {
        model.courses
            .flatMap { c -> c.state.exams.map { c.title to it } }
            .sortedByDescending { it.second.date }
            .take(10)
    }
    Panel {
        SectionTitle("Últimos simulacros")
        if (exams.isEmpty()) {
            Text("Aún no has hecho ninguno. Están en la pestaña Examen (o Práctica) de cada curso.", color = palette.muted)
        }
        exams.forEach { (title, e) ->
            val day = runCatching { Instant.parse(e.date).atZone(ZoneId.systemDefault()).toLocalDate().format(DAY) }.getOrDefault("")
            Row(verticalAlignment = Alignment.CenterVertically) {
                Column(Modifier.weight(1f)) {
                    Text(title, fontWeight = FontWeight.SemiBold)
                    Text("$day · ${e.correct}/${e.total} · ${e.seconds / 60} min", style = MaterialTheme.typography.bodySmall, color = palette.muted)
                }
                Text("${e.score} %", fontWeight = FontWeight.Bold, color = if (e.score >= 50) palette.accent else palette.danger)
            }
        }
    }
}

/** Certificados (se ven y descargan en la web) y logros de la app. */
@Composable
fun AchievementsPanel(model: AppModel, overviews: List<Pair<CourseData, CourseOverview>>) {
    val palette = LocalPalette.current
    val uri = LocalUriHandler.current
    val achievements = remember(model.revision) { Achievements.of(model.pcap.app, overviews.map { it.first.state to it.second }) }
    Column(verticalArrangement = Arrangement.spacedBy(16.dp)) {
        Panel {
            SectionTitle("Certificados")
            Text(
                "No oficiales. En los cursos de DAW: 70 % de dominio y 5 preguntas de cada bloque. Se descargan en PDF desde la web.",
                style = MaterialTheme.typography.bodySmall,
                color = palette.muted,
            )
            overviews.forEach { (course, o) ->
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(
                        "${if (o.certificate) "✓" else "·"} ${course.title}",
                        modifier = Modifier.weight(1f),
                        color = if (o.certificate) palette.accent else MaterialTheme.colorScheme.onSurface,
                    )
                    if (o.certificate) {
                        val path = if (course.isPcap) "#/certificado" else "#/certificado/${course.id}"
                        TextButton(onClick = { uri.openUri(BuildConfig.WEB_URL + path) }) { Text("Ver en la web") }
                    } else {
                        Text("${o.score} % de 70 %", style = MaterialTheme.typography.bodySmall, color = palette.muted)
                    }
                }
            }
        }
        Panel {
            SectionTitle("Logros · ${achievements.count { it.done }} de ${achievements.size}")
            achievements.forEach { a ->
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    modifier = Modifier.semantics(mergeDescendants = true) {
                        contentDescription = "${a.name}: ${a.goal}. ${if (a.done) "Conseguido" else "Pendiente"}"
                    },
                ) {
                    Text(a.icon, modifier = Modifier.width(32.dp), color = if (a.done) palette.accent else palette.muted)
                    Column(Modifier.weight(1f)) {
                        Text(a.name, fontWeight = FontWeight.SemiBold, color = if (a.done) MaterialTheme.colorScheme.onSurface else palette.muted)
                        Text(a.goal, style = MaterialTheme.typography.bodySmall, color = palette.muted)
                    }
                }
            }
        }
    }
}

/** Nombre, contraseña y actividad reciente de la cuenta. Solo con sesión iniciada. */
@Composable
fun SecurityPanel(model: AppModel) {
    val session = model.session ?: return
    val palette = LocalPalette.current
    val scope = rememberCoroutineScope()
    var name by remember(session.name) { mutableStateOf(session.name) }
    var current by remember { mutableStateOf("") }
    var fresh by remember { mutableStateOf("") }
    var repeat by remember { mutableStateOf("") }
    var message by remember { mutableStateOf("") }
    var busy by remember { mutableStateOf(false) }
    var activity by remember { mutableStateOf<List<ActivityItem>?>(null) }
    var activityError by remember { mutableStateOf("") }

    LaunchedEffect(session.token) {
        activity = try {
            model.activity()
        } catch (error: ApiException) {
            activityError = error.message.orEmpty()
            emptyList()
        }
    }

    fun perform(action: suspend () -> Unit, done: String) {
        busy = true
        message = ""
        scope.launch {
            message = try {
                action()
                done
            } catch (error: ApiException) {
                error.message.orEmpty()
            }
            busy = false
        }
    }

    Panel {
        SectionTitle("Perfil y seguridad")
        OutlinedTextField(
            value = name,
            onValueChange = { name = it.take(80) },
            label = { Text("Nombre que se muestra") },
            singleLine = true,
            enabled = !busy,
            modifier = Modifier.fillMaxWidth(),
        )
        OutlinedButton(onClick = { perform({ model.rename(name) }, "Nombre guardado.") }, enabled = !busy && name.isNotBlank() && name.trim() != session.name) {
            Text("Guardar nombre")
        }
        HorizontalDivider()
        Text("Cambiar la contraseña", fontWeight = FontWeight.SemiBold)
        PasswordField("Contraseña actual", current, !busy) { current = it }
        PasswordField("Nueva contraseña (mínimo 8)", fresh, !busy) { fresh = it }
        PasswordField("Repite la nueva", repeat, !busy) { repeat = it }
        Button(
            onClick = {
                when {
                    fresh.length < 8 -> message = "La nueva contraseña necesita al menos 8 caracteres."
                    fresh != repeat -> message = "Las dos contraseñas nuevas no coinciden."
                    else -> perform(
                        {
                            model.changePassword(current, fresh)
                            current = ""
                            fresh = ""
                            repeat = ""
                        },
                        "Contraseña cambiada. Se han cerrado tus otras sesiones; esta sigue abierta.",
                    )
                }
            },
            enabled = !busy && current.isNotEmpty() && fresh.isNotEmpty(),
        ) { Text("Cambiar contraseña") }
        if (message.isNotEmpty()) {
            Text(message, modifier = Modifier.semantics { liveRegion = LiveRegionMode.Polite }, style = MaterialTheme.typography.bodyMedium)
        }
        HorizontalDivider()
        Text("Actividad reciente de la cuenta", fontWeight = FontWeight.SemiBold)
        val items = activity
        when {
            items == null -> Text("Cargando…", color = palette.muted)
            activityError.isNotEmpty() -> Text(activityError, color = palette.muted)
            items.isEmpty() -> Text("Todavía no hay actividad.", color = palette.muted)
            else -> items.take(10).forEach { e ->
                val time = runCatching { Instant.parse(e.createdAt).atZone(ZoneId.systemDefault()).format(WHEN) }.getOrDefault(e.createdAt)
                Column {
                    Text(e.label, color = if (e.kind == "login_failed") palette.danger else MaterialTheme.colorScheme.onSurface)
                    Text("$time · ${e.device}", style = MaterialTheme.typography.bodySmall, color = palette.muted)
                }
            }
        }
        Text(
            "Si ves un acceso que no reconoces, cambia la contraseña: se cerrarán las demás sesiones.",
            style = MaterialTheme.typography.bodySmall,
            color = palette.muted,
        )
    }
}

@Composable
private fun PasswordField(label: String, value: String, enabled: Boolean, onChange: (String) -> Unit) {
    OutlinedTextField(
        value = value,
        onValueChange = onChange,
        label = { Text(label) },
        singleLine = true,
        enabled = enabled,
        visualTransformation = PasswordVisualTransformation(),
        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
        modifier = Modifier.fillMaxWidth(),
    )
}
