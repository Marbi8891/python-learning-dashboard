package io.github.marbi8891.pld

import android.app.Application
import android.content.Context
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import io.github.marbi8891.pld.learn.Exercise
import io.github.marbi8891.pld.learn.Learning
import io.github.marbi8891.pld.learn.LearningContent
import io.github.marbi8891.pld.learn.LearningState
import io.github.marbi8891.pld.learn.PlanItem
import io.github.marbi8891.pld.pcap.AccountApi
import io.github.marbi8891.pld.pcap.ActivityItem
import io.github.marbi8891.pld.pcap.ApiException
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
import io.github.marbi8891.pld.pcap.Session
import io.github.marbi8891.pld.pcap.Sync
import io.github.marbi8891.pld.pcap.UrlConnectionHttp
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.MainScope
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter

class PldApplication : Application() {
    val model: AppModel by lazy { AppModel(this) }
}

/**
 * Un curso de la app (ADR-0016). El PCAP usa los mismos JSON que la web; los demás cursos de DAW
 * (SQL, ...) viven en `frontend/data/courses/<id>/` (assets `courses/<id>/`, ADR-0021) con el mismo formato, generados y comprobados por
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
            course(context, "programacion", "Programación", "Módulo 0485 en Python · UT1-UT9", "Para probarlo, pégalo en un archivo .py y ejecútalo con «python archivo.py» o en PyCharm. Los ejemplos de ventanas necesitan «pip install pyside6»."),
            course(context, "sql", "Bases de datos", "Módulo 0484 · UD1-UD3 de tu centro (SQL)", "Para probarlo, cópialo en tu gestor de bases de datos (MySQL Workbench, DBeaver…)."),
            course(context, "entornos", "Entornos", "Entornos de desarrollo (0487) · UD1 de tu centro", "Los ejemplos están en Python: pégalos en un archivo .py y ejecútalo con «python archivo.py», o en tu IDE."),
            course(context, "js", "JavaScript", "Entorno cliente (DAW)", "Para probarlo, pégalo en la consola del navegador (F12) o guárdalo en un .js y ejecútalo con Node. El código del DOM necesita una página HTML."),
            course(context, "java", "Java", "Para más adelante: Java desde cero", "Para probarlo, pégalo en tu IDE (IntelliJ, NetBeans…) o guárdalo en Main.java y ejecuta «java Main.java»."),
        )
        others.forEach { it.state.shareApp(pcap.state.app) }
        listOf(pcap) + others
    }

    /* ---------- Núcleo educativo por conceptos (ADR-0031) ---------- */

    /** Conceptos, errores típicos y ejercicios: el mismo learning.json que la web. */
    private val learnContent: LearningContent = LearningContent.parse(context.readAsset("learning.json"))

    /** Progreso por conceptos: el mismo documento que la web (/api/course-state/learn). */
    val learning: Learning = Learning(learnContent, LearningState.fromJson(prefs.getString(KEY_LEARN, null)))

    fun saveLearning() {
        prefs.edit().putString(KEY_LEARN, learning.state.toJson().toString()).apply()
        revision++
    }

    /** Lección del curso PCAP (lessons.json), cuya teoría reutilizan los conceptos. */
    fun pcapLesson(slug: String) = courses.first { it.isPcap }.content[slug]

    /** Título y ejercicios de la sesión que abre una acción del plan de hoy. */
    fun planSession(item: PlanItem): Pair<String, List<String>> {
        val count = if (item.type == "review") 3 else 4
        val label = when (item.type) {
            "learn" -> "Aprender"
            "review" -> "Repaso"
            "errors" -> "Corregir errores"
            "reinforce" -> "Reforzar"
            else -> "Practicar"
        }
        val title = learnContent.concepts.getValue(item.concept).title
        return "$label: $title" to learning.selectExercises(listOf(item.concept), count).map(Exercise::id)
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

    /* ---------- Cuenta y sincronización (ADR-0026) ---------- */

    // La sesión va en su propio archivo, excluido de las copias de seguridad (res/xml/*backup*)
    private val sessionPrefs = context.getSharedPreferences(SESSION_PREFS, Context.MODE_PRIVATE)
    private val api = AccountApi(BuildConfig.API_URL, UrlConnectionHttp("PLD-App/${BuildConfig.VERSION_NAME} (Android)"))
    private val scope = MainScope()

    var session: Session? by mutableStateOf(readSession())
        private set

    /** Email de la última sesión, para no tener que escribirlo otra vez cuando caduca. */
    val lastEmail: String get() = sessionPrefs.getString(KEY_EMAIL, "").orEmpty()

    var syncing by mutableStateOf(false)
        private set
    var syncMessage by mutableStateOf("")
        private set
    var lastSync: String? by mutableStateOf(sessionPrefs.getString(KEY_LAST_SYNC, null))
        private set

    /** Inicia sesión y sincroniza. Lanza [ApiException] con un mensaje para enseñar. */
    suspend fun login(email: String, password: String) {
        val newSession = withContext(Dispatchers.IO) { api.login(email, password) }
        sessionPrefs.edit()
            .putString(KEY_TOKEN, newSession.token)
            .putString(KEY_EMAIL, newSession.email)
            .putString(KEY_NAME, newSession.name)
            .apply()
        session = newSession
        sync()
    }

    /** Cierra la sesión en este móvil. El progreso se queda: es del móvil y ya está en la cuenta. */
    fun logout(message: String = "") {
        sessionPrefs.edit().remove(KEY_TOKEN).remove(KEY_NAME).apply()
        session = null
        syncMessage = message
    }

    /** Sincroniza sin esperar (al abrir y al salir de la app). Sin sesión no hace nada. */
    fun syncInBackground() {
        if (session != null) scope.launch { sync() }
    }

    /**
     * Trae el estado de cada curso de la cuenta, lo fusiona con el del móvil sin perder nada y sube
     * el resultado. La red va en segundo plano; la fusión, en el hilo principal, que es el único que
     * toca el estado.
     */
    suspend fun sync() {
        val current = session ?: return
        if (syncing) return
        syncing = true
        syncMessage = "Sincronizando…"
        try {
            val remote = withContext(Dispatchers.IO) { courses.associate { it.id to api.pull(current.token, it.id) } }
            // Un servidor anterior a ADR-0031 responde 404 a «learn»: entonces solo se sincronizan los cursos
            val remoteLearning = withContext(Dispatchers.IO) {
                try {
                    api.pull(current.token, LEARN)
                } catch (error: ApiException) {
                    if (error.code == 404) null else throw error
                }
            }
            val merged = courses.associate { c -> c.id to Sync.merge(c.state, remote.getValue(c.id), c.isPcap) }
            courses.forEach { it.state.updateFlags(it.bank) }
            // Progreso por conceptos (ADR-0031): misma fusión sin pérdidas que en la web
            remoteLearning?.let { Learning.merge(learning.state, it) }
            val learningDoc = learning.state.toJson()
            saveAll()
            prefs.edit().putString(KEY_LEARN, learningDoc.toString()).apply()
            revision++
            withContext(Dispatchers.IO) {
                merged.forEach { (id, data) -> api.push(current.token, id, data) }
                if (remoteLearning != null) api.push(current.token, LEARN, learningDoc)
            }
            val now = LocalDateTime.now().format(DateTimeFormatter.ofPattern("dd/MM HH:mm"))
            sessionPrefs.edit().putString(KEY_LAST_SYNC, now).apply()
            lastSync = now
            syncMessage = "Progreso sincronizado con tu cuenta."
        } catch (error: ApiException) {
            if (error.code == 401) logout(error.message.orEmpty()) else syncMessage = error.message.orEmpty()
        } finally {
            syncing = false
        }
    }

    /* ---------- «Mi cuenta» en la app (ADR-0027) ---------- */

    /** Fecha del examen de un curso («AAAA-MM-DD» o null). Se sincroniza como en la web. */
    fun setExamDate(courseId: String, date: String?) {
        val course = courses.first { it.id == courseId }
        course.state.examDate = date
        saveAll()
        revision++
    }

    /** Cambia el nombre en la cuenta. Lanza [ApiException] con un mensaje para enseñar. */
    suspend fun rename(name: String) {
        val current = session ?: return
        val saved = withContext(Dispatchers.IO) { api.rename(current.token, name.trim()) }
        sessionPrefs.edit().putString(KEY_NAME, saved).apply()
        session = current.copy(name = saved)
    }

    /** Cambia la contraseña: las demás sesiones se cierran y esta sigue con el token nuevo. */
    suspend fun changePassword(currentPassword: String, newPassword: String) {
        val current = session ?: return
        val token = withContext(Dispatchers.IO) { api.changePassword(current.token, currentPassword, newPassword) }
        sessionPrefs.edit().putString(KEY_TOKEN, token).apply()
        session = current.copy(token = token)
    }

    suspend fun activity(): List<ActivityItem> {
        val current = session ?: return emptyList()
        return try {
            withContext(Dispatchers.IO) { api.activity(current.token) }
        } catch (error: ApiException) {
            if (error.code == 401) logout(error.message.orEmpty())
            throw error
        }
    }

    private fun readSession(): Session? {
        val token = sessionPrefs.getString(KEY_TOKEN, null) ?: return null
        return Session(token, sessionPrefs.getString(KEY_EMAIL, "").orEmpty(), sessionPrefs.getString(KEY_NAME, "").orEmpty())
    }

    /** Guarda el estado de todos los cursos (tras fusionar lo que llega de la cuenta). */
    private fun saveAll() {
        val edit = prefs.edit()
        courses.forEach { edit.putString(it.key, it.state.toJson(withApp = it.isPcap).toString()) }
        edit.apply()
    }

    private companion object {
        const val KEY_COURSE = "course"
        const val KEY_LEARN = "learn"
        const val LEARN = "learn"
        const val SESSION_PREFS = "pld-session"
        const val KEY_TOKEN = "token"
        const val KEY_EMAIL = "email"
        const val KEY_NAME = "name"
        const val KEY_LAST_SYNC = "lastSync"
    }
}

private fun Context.readAsset(name: String): String = assets.open(name).bufferedReader().use { it.readText() }
