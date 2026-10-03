package io.github.marbi8891.pld

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.BackHandler
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.selection.selectableGroup
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.key
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.role
import androidx.compose.ui.semantics.selected
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.unit.dp
import io.github.marbi8891.pld.ui.CelebrationScreen
import io.github.marbi8891.pld.ui.DungeonScreen
import io.github.marbi8891.pld.ui.GameHomeScreen
import io.github.marbi8891.pld.ui.LessonScreen
import io.github.marbi8891.pld.ui.LearningHomeScreen
import io.github.marbi8891.pld.ui.LearningPracticeScreen
import io.github.marbi8891.pld.ui.MockScreen
import io.github.marbi8891.pld.ui.PathScreen
import io.github.marbi8891.pld.ui.PcapHomeScreen
import io.github.marbi8891.pld.ui.PldTheme
import io.github.marbi8891.pld.ui.PracticeScreen
import io.github.marbi8891.pld.ui.ProfileScreen
import io.github.marbi8891.pld.ui.RushScreen
import io.github.marbi8891.pld.ui.TheoryHomeScreen
import io.github.marbi8891.pld.ui.TheoryScreen

/** Pantallas a pantalla completa por encima de las pestañas. Una pila propia basta (ADR-0011). */
sealed interface Screen {
    data class Practice(val block: String) : Screen

    data class LearningPractice(val questionId: String) : Screen

    data object TheoryHome : Screen

    data class Lesson(val nodeId: String) : Screen

    data class Done(val xp: Int, val perfect: Boolean) : Screen

    data class Theory(val slug: String) : Screen

    data object Dungeon : Screen

    data object Rush : Screen

    /** Simulacro cronometrado del curso elegido (ADR-0024). */
    data object Mock : Screen
}

enum class Tab(val label: String, val symbol: String) {
    LEARN("Aprender", "▶"),
    PATH("Ruta", "◆"),
    PLAY("Jugar", "⚔"),
    EXAM("Examen", "✎"),
    PROFILE("Perfil", "●"),
}

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        val model = (application as PldApplication).model
        setContent {
            PldTheme { App(model) }
        }
    }

    // Con sesión iniciada: se trae lo nuevo al abrir y se sube lo hecho al salir (ADR-0026)
    override fun onStart() {
        super.onStart()
        (application as PldApplication).model.syncInBackground()
    }

    override fun onStop() {
        super.onStop()
        (application as PldApplication).model.syncInBackground()
    }
}

@Composable
fun App(model: AppModel) {
    var tab by remember { mutableStateOf(Tab.LEARN) }
    var stack by remember { mutableStateOf(listOf<Screen>()) }
    val open: (Screen) -> Unit = { stack = stack + it }
    val back: () -> Unit = { stack = stack.dropLast(1) }
    // Al terminar una lección, la celebración sustituye a la lección en la pila
    val replaceTop: (Screen) -> Unit = { stack = stack.dropLast(1) + it }

    BackHandler(enabled = stack.isNotEmpty(), onBack = back)

    when (val screen = stack.lastOrNull()) {
        null -> Tabs(model, tab, onTab = { tab = it }, open = open)
        is Screen.Practice -> PracticeScreen(model, screen.block, onBack = back, onTheory = { open(Screen.Theory(it)) })
        is Screen.LearningPractice -> LearningPracticeScreen(model, screen.questionId, onBack = back)
        Screen.TheoryHome -> TheoryHomeScreen(model, onOpen = { open(Screen.Theory(it)) }, onBack = back)
        is Screen.Lesson -> LessonScreen(
            model,
            model.node(screen.nodeId),
            onExit = back,
            onFinished = { xp, perfect -> replaceTop(Screen.Done(xp, perfect)) },
            onPractice = { block -> replaceTop(Screen.Practice(block)) },
        )
        is Screen.Done -> CelebrationScreen(model, screen.xp, screen.perfect, onContinue = back)
        is Screen.Theory -> TheoryScreen(model, screen.slug, onBack = back)
        Screen.Dungeon -> DungeonScreen(model, onExit = back, onTheory = { open(Screen.Theory(it)) })
        Screen.Rush -> RushScreen(model, onExit = back)
        Screen.Mock -> MockScreen(model, onBack = back)
    }
}

@Composable
private fun Tabs(model: AppModel, tab: Tab, onTab: (Tab) -> Unit, open: (Screen) -> Unit) {
    val course = model.course
    Scaffold(
        containerColor = MaterialTheme.colorScheme.background,
        topBar = { CourseSwitcher(model) },
        bottomBar = {
            NavigationBar {
                Tab.entries.forEach { item ->
                    NavigationBarItem(
                        selected = tab == item,
                        onClick = { onTab(item) },
                        icon = { Text(item.symbol) },
                        // Fuera del PCAP no hay examen oficial: la pestaña es de práctica
                        label = { Text(if (item == Tab.EXAM && !course.isPcap) "Práctica" else item.label) },
                    )
                }
            }
        },
    ) { padding ->
        val modifier = Modifier.padding(padding)
        // Al cambiar de curso, cada pestaña empieza de cero (listas, scroll y datos recordados)
        key(course.id) {
            when (tab) {
                Tab.LEARN -> LearningHomeScreen(
                    model,
                    onStart = { open(Screen.LearningPractice(it)) },
                    onTheoryHome = { open(Screen.TheoryHome) },
                    modifier = modifier,
                )
                Tab.PATH -> PathScreen(
                    model,
                    onStart = { open(Screen.Lesson(it.id)) },
                    onPractice = { open(Screen.Practice(it)) },
                    onTheory = { open(Screen.Theory(it)) },
                    modifier = modifier,
                )
                Tab.PLAY -> GameHomeScreen(
                    model,
                    onDungeon = { open(Screen.Dungeon) },
                    onRush = { open(Screen.Rush) },
                    modifier = modifier,
                )
                Tab.EXAM -> PcapHomeScreen(
                    model,
                    onPractice = { open(Screen.Practice(it)) },
                    onTheory = { open(Screen.Theory(it)) },
                    onMock = { open(Screen.Mock) },
                    modifier = modifier,
                )
                Tab.PROFILE -> ProfileScreen(
                    model,
                    // Practicar el tema flojo de otro curso: se cambia a ese curso y se abre la tanda
                    onPractice = { courseId, block ->
                        model.selectCourse(courseId)
                        open(Screen.Practice(block))
                    },
                    modifier = modifier,
                )
            }
        }
    }
}

/** Selector de curso (ADR-0016): Python · PCAP, SQL… Los pulsadores se leen como pestañas con TalkBack. */
@Composable
private fun CourseSwitcher(model: AppModel) {
    Row(
        Modifier
            .fillMaxWidth()
            .statusBarsPadding()
            .horizontalScroll(rememberScrollState())
            .padding(horizontal = 12.dp, vertical = 6.dp)
            .selectableGroup(),
        horizontalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        model.courses.forEach { item ->
            val selected = item.id == model.course.id
            val modifier = Modifier.semantics {
                role = Role.Tab
                this.selected = selected
                contentDescription = "Curso ${item.title}, ${item.subtitle}"
            }
            if (selected) {
                Button(onClick = {}, modifier = modifier) { Text(item.title) }
            } else {
                OutlinedButton(onClick = { model.selectCourse(item.id) }, modifier = modifier) { Text(item.title) }
            }
        }
    }
}
