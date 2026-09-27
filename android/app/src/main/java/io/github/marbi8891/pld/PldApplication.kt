package io.github.marbi8891.pld

import android.app.Application
import android.content.Context
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
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
 * Datos de la app: banco y temario (assets, los mismos JSON que la web), la ruta generada a partir
 * de ellos y el estado del alumno, guardado como el mismo documento JSON que usa la web.
 */
class AppModel(context: Context) {
    private val prefs = context.getSharedPreferences("pld", Context.MODE_PRIVATE)

    val bank: Bank = Bank.parse(context.readAsset("pcap.json"))
    private val lessonsJson = context.readAsset("lessons.json")
    val lessons: LessonIndex = LessonIndex.parse(lessonsJson)

    /** Teoría completa de cada lección, para leerla sin conexión (ADR-0014). */
    val content: Map<String, LessonContent> = LessonLibrary.parse(lessonsJson)
    val units: List<PathUnit> = Course.build(bank, lessons)
    val pcap: PcapState = PcapState.fromJson(prefs.getString(KEY, null))

    private val questionsById = bank.questions.associateBy { it.id }
    private val nodesById = units.flatMap { it.nodes }.associateBy { it.id }

    /** Cambia con cada guardado: las pantallas que lo leen se vuelven a pintar. */
    var revision by mutableIntStateOf(0)
        private set

    /** Aplica un cambio al estado, lo guarda y avisa a la interfaz. */
    fun <T> update(change: PcapState.() -> T): T {
        val result = pcap.change()
        pcap.updateFlags(bank)
        prefs.edit().putString(KEY, pcap.toJson().toString()).apply()
        revision++
        return result
    }

    /**
     * Partida de la mazmorra en curso (ADR-0015). Vive en memoria: sobrevive a abrir la teoría o cambiar
     * de pestaña, pero no a que Android cierre la app. Los récords sí se guardan.
     */
    var dungeon: DungeonRun? = null

    fun startDungeon() {
        dungeon = DungeonRun.start(bank, pcap)
    }

    /** Abandonar cuenta como partida terminada en la planta actual. */
    fun abandonDungeon() {
        val run = dungeon ?: return
        dungeon = null
        if (!run.finished) update { app.game.recordRun(run) }
    }

    fun node(id: String): PathNode = nodesById.getValue(id)

    fun questions(node: PathNode): List<Question> = node.questionIds.map { questionsById.getValue(it) }

    fun unitOf(node: PathNode): PathUnit = units.first { it.slug == node.unit }

    private companion object {
        const val KEY = "pcap"
    }
}

private fun Context.readAsset(name: String): String = assets.open(name).bufferedReader().use { it.readText() }
