package io.github.marbi8891.pld.pcap

import org.json.JSONArray
import org.json.JSONObject
import java.time.Instant
import java.time.LocalDate
import java.time.ZoneOffset
import java.time.format.DateTimeFormatter
import java.time.temporal.ChronoUnit
import kotlin.math.roundToLong
import kotlin.random.Random

/*
 * Estado de la preparación del PCAP. Es el mismo documento que guarda la web (clave `pld:pcap`)
 * y que se sincroniza con /api/pcap-state, así que las reglas copian las de frontend/js/pcap-store.js.
 */

data class SrsItem(val box: Int, val due: String, val last: String)

data class ExamResult(
    val date: String,
    val correct: Int,
    val total: Int,
    val score: Int,
    val seconds: Int,
    val blocks: Map<String, List<Int>>,
)

data class BlockStat(val answered: Int, val rate: Double?)

data class Status(val stats: Map<String, BlockStat>, val score: Int, val lastExam: ExamResult?, val weak: List<Block>, val ready: Boolean)

class PcapState {
    var lang: String = "es"
    val answers: MutableMap<String, MutableList<Boolean>> = linkedMapOf()
    val exams: MutableList<ExamResult> = mutableListOf()
    val known: MutableList<String> = mutableListOf()
    var bestCombo: Int = 0
    val flags: MutableMap<String, Boolean> = linkedMapOf("mastered" to false, "ready" to false, "allCards" to false)
    val srs: MutableMap<String, SrsItem> = linkedMapOf()
    var examDate: String? = null

    /** Progreso propio de la app: ruta, XP diaria, meta y vidas (ADR-0012). */
    var app: AppProgress = AppProgress()
        private set

    /* ---------- Repaso espaciado (cajas de Leitner) ---------- */

    /** Acierto: sube de caja y el repaso se aleja. Fallo: vuelve a la caja 1 (repaso mañana). */
    fun review(id: String, ok: Boolean, today: LocalDate = LocalDate.now(), now: Instant = Instant.now()) {
        val box = if (ok) minOf((srs[id]?.box ?: 0) + 1, MAX_BOX) else 1
        srs[id] = SrsItem(box, today.plusDays(INTERVAL_DAYS[box].toLong()).toString(), iso(now))
    }

    /** Ids que toca repasar hoy (o que se quedaron atrasados). */
    fun dueIds(ids: List<String>, today: LocalDate = LocalDate.now()): List<String> {
        val day = today.toString()
        return ids.filter { id -> srs[id]?.let { it.due <= day } ?: false }
    }

    fun recordAnswer(id: String, ok: Boolean, today: LocalDate = LocalDate.now(), now: Instant = Instant.now()) {
        val history = answers.getOrPut(id) { mutableListOf() }
        history.add(ok)
        if (history.size > HISTORY) history.removeAt(0)
        review(id, ok, today, now)
    }

    /* ---------- Preparación ---------- */

    fun questionsMastered(): Int = answers.values.count { true in it }

    fun examsPassed(min: Int = 70): Int = exams.count { it.score >= min }

    /** Acierto por bloque: último intento de cada pregunta respondida del bloque. */
    fun blockStats(bank: Bank): Map<String, BlockStat> = bank.exam.blocks.associate { block ->
        val last = bank.questions.filter { it.block == block.slug }.mapNotNull { answers[it.id]?.lastOrNull() }
        block.slug to BlockStat(last.size, if (last.isEmpty()) null else last.count { it }.toDouble() / last.size)
    }

    /** Preparación estimada: acierto de cada bloque ponderado por su peso en el examen (0-100). */
    fun readiness(stats: Map<String, BlockStat>, blocks: List<Block>): Int =
        blocks.sumOf { (stats.getValue(it.slug).rate ?: 0.0) * it.weight }.roundToLong().toInt()

    fun status(bank: Bank): Status {
        val stats = blockStats(bank)
        val score = readiness(stats, bank.exam.blocks)
        val lastExam = exams.lastOrNull()
        val weak = bank.exam.blocks.filter {
            val stat = stats.getValue(it.slug)
            stat.answered < READY_BLOCK_ANSWERED || (stat.rate ?: 0.0) < READY_BLOCK_RATE
        }
        val ready = score >= READY_SCORE && weak.isEmpty() && (lastExam?.score ?: 0) >= READY_LAST_EXAM
        return Status(stats, score, lastExam, weak, ready)
    }

    /** Actualiza los indicadores que usan los logros (una vez conseguidos, no se pierden). */
    fun updateFlags(bank: Bank) {
        val status = status(bank)
        if (bank.exam.blocks.any { b -> status.stats.getValue(b.slug).let { it.answered >= 10 && (it.rate ?: 0.0) >= 0.9 } }) {
            flags["mastered"] = true
        }
        if (status.ready) flags["ready"] = true
        if (bank.cards.all { it.id in known }) flags["allCards"] = true
    }

    /** Tanda de práctica de un bloque: primero las falladas, luego las nuevas y por último las acertadas. */
    fun practiceSet(bank: Bank, slug: String, random: Random = Random.Default): List<Question> {
        val pool = bank.questions.filter { it.block == slug }
        val failed = pool.filter { answers[it.id]?.lastOrNull() == false }.shuffled(random)
        val fresh = pool.filter { it.id !in answers }.shuffled(random)
        val rest = pool.filter { answers[it.id]?.lastOrNull() == true }.shuffled(random)
        return (failed + fresh + rest).take(PRACTICE_SIZE)
    }

    /* ---------- Fusión con la copia guardada en la cuenta ---------- */

    /** Combina el estado de la cuenta con el local sin perder nada de ninguno de los dos. */
    fun merge(remote: PcapState) {
        for ((id, history) in remote.answers) {
            val local = answers[id]
            if (local == null || history.size > local.size) answers[id] = history.toMutableList()
        }
        val byDate = linkedMapOf<String, ExamResult>()
        (remote.exams + exams).forEach { byDate[it.date] = it }
        exams.clear()
        exams.addAll(byDate.values.sortedBy { it.date }.takeLast(MAX_EXAMS))
        remote.known.filter { it !in known }.forEach { known.add(it) }
        bestCombo = maxOf(bestCombo, remote.bestCombo)
        for (flag in flags.keys.toList()) flags[flag] = flags[flag] == true || remote.flags[flag] == true
        for ((id, item) in remote.srs) {
            val local = srs[id]
            srs[id] = if (local != null && local.last >= item.last) local else item
        }
        if (examDate == null) examDate = remote.examDate
        app.merge(remote.app)
    }

    /* ---------- JSON (mismo formato que la web) ---------- */

    fun toJson(): JSONObject = JSONObject().apply {
        put("lang", lang)
        put("answers", JSONObject().apply { answers.forEach { (id, h) -> put(id, JSONArray().apply { h.forEach { put(it) } }) } })
        put(
            "exams",
            JSONArray().apply {
                exams.forEach { e ->
                    put(
                        JSONObject().apply {
                            put("date", e.date)
                            put("correct", e.correct)
                            put("total", e.total)
                            put("score", e.score)
                            put("seconds", e.seconds)
                            put("blocks", JSONObject().apply { e.blocks.forEach { (slug, v) -> put(slug, JSONArray().apply { v.forEach { put(it) } }) } })
                        },
                    )
                }
            },
        )
        put("known", JSONArray().apply { known.forEach { put(it) } })
        put("bestCombo", bestCombo)
        put("flags", JSONObject().apply { flags.forEach { (k, v) -> put(k, v) } })
        put(
            "srs",
            JSONObject().apply {
                srs.forEach { (id, s) -> put(id, JSONObject().apply { put("box", s.box); put("due", s.due); put("last", s.last) }) }
            },
        )
        put("plan", JSONObject().apply { put("examDate", examDate ?: JSONObject.NULL) })
        put("app", app.toJson())
    }

    companion object {
        val INTERVAL_DAYS = listOf(0, 1, 3, 7, 14, 30) // días hasta el siguiente repaso según la caja
        val MAX_BOX = INTERVAL_DAYS.size - 1
        const val HISTORY = 5
        const val MAX_EXAMS = 30
        const val PRACTICE_SIZE = 10
        const val READY_SCORE = 80
        const val READY_BLOCK_RATE = 0.6
        const val READY_BLOCK_ANSWERED = 5
        const val READY_LAST_EXAM = 75

        private val ISO = DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss.SSS'Z'").withZone(ZoneOffset.UTC)

        /** Igual que `Date.toISOString()` de JavaScript, para que las fechas se comparen como texto. */
        fun iso(instant: Instant): String = ISO.format(instant.truncatedTo(ChronoUnit.MILLIS))

        /** Lee el estado tolerando campos ausentes o de tipo inesperado (copias antiguas o dañadas). */
        fun fromJson(json: String?): PcapState {
            val state = PcapState()
            if (json.isNullOrBlank()) return state
            val root = runCatching { JSONObject(json) }.getOrNull() ?: return state
            state.lang = if (root.optString("lang") == "en") "en" else "es"
            root.optJSONObject("answers")?.let { answers ->
                answers.keys().forEach { id ->
                    val list = answers.optJSONArray(id) ?: return@forEach
                    state.answers[id] = (0 until list.length()).map { list.optBoolean(it) }.toMutableList()
                }
            }
            root.optJSONArray("exams")?.let { exams ->
                for (i in 0 until exams.length()) {
                    val e = exams.optJSONObject(i) ?: continue
                    val blocks = linkedMapOf<String, List<Int>>()
                    e.optJSONObject("blocks")?.let { b ->
                        b.keys().forEach { slug -> b.optJSONArray(slug)?.let { v -> blocks[slug] = (0 until v.length()).map { v.optInt(it) } } }
                    }
                    state.exams.add(
                        ExamResult(e.optString("date"), e.optInt("correct"), e.optInt("total"), e.optInt("score"), e.optInt("seconds"), blocks),
                    )
                }
            }
            root.optJSONArray("known")?.let { k -> for (i in 0 until k.length()) state.known.add(k.optString(i)) }
            state.bestCombo = root.optInt("bestCombo")
            root.optJSONObject("flags")?.let { f -> state.flags.keys.toList().forEach { state.flags[it] = f.optBoolean(it) } }
            root.optJSONObject("srs")?.let { srs ->
                srs.keys().forEach { id ->
                    val s = srs.optJSONObject(id) ?: return@forEach
                    state.srs[id] = SrsItem(s.optInt("box", 1), s.optString("due"), s.optString("last"))
                }
            }
            state.examDate = root.optJSONObject("plan")?.optStringOrNull("examDate")
            state.app = AppProgress.fromJson(root.optJSONObject("app"))
            return state
        }
    }
}
