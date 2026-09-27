package io.github.marbi8891.pld

import android.app.Application
import android.content.Context
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import io.github.marbi8891.pld.pcap.Bank
import io.github.marbi8891.pld.pcap.Course
import io.github.marbi8891.pld.pcap.DungeonRun
import io.github.marbi8891.pld.pcap.LessonContent
import io.github.marbi8891.pld.pcap.LessonIndex
import io.github.marbi8891.pld.pcap.LessonLibrary
import io.github.marbi8891.pld.pcap.PathNode
import io.github.marbi8891.pld.pcap.PathUnit
import io.github.marbi8891.pld.pcap.PcapState
import io.github.marbi8891.pld.pcap.Question

class PldApplication : Application() {
    val model: AppModel by lazy { AppModel(this) }
}

/**
 * Un curso de la app (ADR-0016). El PCAP usa los mismos JSON que la web; los demás cursos de DAW
 * (SQL, ...) viven en `assets/courses/<id>/` con el mismo formato, generados y comprobados por
 * `scripts/courses/`.
 */
class CourseData(
    val id: String,
    /** Nombre corto para el selector y los textos: «Python · PCAP», «SQL». */
    val title: String,
    /** Módulo de DAW o certificación de la que sale el curso. */
    val subtitle: String,
    /** Cómo probar los ejemplos fuera de la app, mientras no se puedan ejecutar dentro. */
    val tryHint: String,
    val bank: Bank,
    val lessons: LessonIndex,
    val content: Map<String, LessonContent>,
    val state: PcapState,
) {
    val units: List<PathUnit> = Course.build(bank, lessons)
    val isPcap: Boolean get() = id == PCAP
    val questionsById = bank.questions.associateBy { it.id }
    val nodesById = units.flatMap { it.nodes }.associateBy { it.id }

    /** Clave de SharedPreferences. La del PCAP no cambia para no perder el progreso guardado. */
    val key: String get() = if (isPcap) "pcap" else "course:$id"

    companion object {
        const val PCAP = "pcap"
    }
}

/**
 * Datos de la app: los cursos (assets), la ruta de cada uno y el estado del alumno. El estado del PCAP
 * es el mismo documento JSON que usa la web; la XP, la racha, la meta, las vidas y los récords del juego
 * se guardan con él y los comparten todos los cursos.
 */
class AppModel(context: Context) {
    private val prefs = context.getSharedPreferences("pld", Context.MODE_PRIVATE)

    val courses: List<CourseData> = run {
        val pcap = load(
            context, CourseData.PCAP, "Python · PCAP", "Certificación PCAP-31-03", "pcap.json", "lessons.json",
            "Para ejecutarlo, cópialo en tu editor. Ejecutar Python dentro de la app llegará en la entrega 6.",
        )
        val others = listOf(
            course(context, "sql", "SQL", "Bases de datos (DAW)", "Para probarlo, cópialo en tu gestor de bases de datos (MySQL Workbench, DBeaver…)."),
            course(context, "java", "Java", "Programación (DAW)", "Para probarlo, pégalo en tu IDE (IntelliJ, NetBeans…) o guárdalo en Main.java y ejecuta «java Main.java»."),
        )
        others.forEach { it.state.shareApp(pcap.state.app) }
        listOf(pcap) + others
    }

    /** Curso elegido en el selector; se recuerda entre sesiones. */
    var course: CourseData by mutableStateOf(courses.firstOrNull { it.id == prefs.getString(KEY_COURSE, null) } ?: courses.first())
        private set

    fun selectCourse(id: String) {
        course = courses.first { it.id == id }
        prefs.edit().putString(KEY_COURSE, id).apply()
        revision++
    }

    // Accesos al curso elegido: las pantallas no necesitan saber cuántos cursos hay
    val bank: Bank get() = course.bank
    val lessons: LessonIndex get() = course.lessons
    val content: Map<String, LessonContent> get() = course.content
    val units: List<PathUnit> get() = course.units
    val pcap: PcapState get() = course.state

    /** Cambia con cada guardado: las pantallas que lo leen se vuelven a pintar. */
    var revision by mutableIntStateOf(0)
        private set

    /** Aplica un cambio al estado del curso elegido, lo guarda y avisa a la interfaz. */
    fun <T> update(change: PcapState.() -> T): T {
        val current = course
        val result = current.state.change()
        current.state.updateFlags(current.bank)
        val edit = prefs.edit().putString(current.key, current.state.toJson(withApp = current.isPcap).toString())
        // El progreso compartido (XP, racha, vidas, récords) se guarda siempre con el PCAP
        if (!current.isPcap) courses.first { it.isPcap }.let { edit.putString(it.key, it.state.toJson().toString()) }
        edit.apply()
        revision++
        return result
    }

    /**
     * Partida de la mazmorra en curso de cada curso (ADR-0015). Vive en memoria: sobrevive a abrir la
     * teoría o cambiar de pestaña, pero no a que Android cierre la app. Los récords sí se guardan.
     */
    private val runs = mutableMapOf<String, DungeonRun>()

    var dungeon: DungeonRun?
        get() = runs[course.id]
        set(value) {
            if (value == null) runs.remove(course.id) else runs[course.id] = value
        }

    fun startDungeon() {
        dungeon = DungeonRun.start(bank, pcap)
    }

    /** Abandonar cuenta como partida terminada en la planta actual. */
    fun abandonDungeon() {
        val run = dungeon ?: return
        dungeon = null
        if (!run.finished) update { app.game.recordRun(run) }
    }

    fun node(id: String): PathNode = course.nodesById.getValue(id)

    fun questions(node: PathNode): List<Question> = node.questionIds.map { course.questionsById.getValue(it) }

    fun unitOf(node: PathNode): PathUnit = units.first { it.slug == node.unit }

    /** Curso de DAW generado por `scripts/courses/<id>_course.py`. */
    private fun course(context: Context, id: String, title: String, subtitle: String, tryHint: String): CourseData =
        load(context, id, title, subtitle, "courses/$id/bank.json", "courses/$id/lessons.json", tryHint)

    private fun load(
        context: Context,
        id: String,
        title: String,
        subtitle: String,
        bankFile: String,
        lessonsFile: String,
        tryHint: String,
    ): CourseData {
        val lessonsJson = context.readAsset(lessonsFile)
        return CourseData(
            id = id,
            title = title,
            subtitle = subtitle,
            tryHint = tryHint,
            bank = Bank.parse(context.readAsset(bankFile)),
            lessons = LessonIndex.parse(lessonsJson),
            content = LessonLibrary.parse(lessonsJson),
            state = PcapState.fromJson(prefs.getString(if (id == CourseData.PCAP) "pcap" else "course:$id", null)),
        )
    }

    private companion object {
        const val KEY_COURSE = "course"
    }
}

private fun Context.readAsset(name: String): String = assets.open(name).bufferedReader().use { it.readText() }
