package io.github.marbi8891.pld.pcap

import org.json.JSONObject
import java.time.Duration
import java.time.Instant
import java.time.LocalDate

/** Resultado guardado de un nodo de la ruta. */
data class NodeResult(val perfect: Boolean, val date: String)

/**
 * Progreso de la app (ADR-0012): ruta, XP por día, meta diaria, vidas y récords del modo «Jugar».
 * La racha no se guarda: se deriva de la XP de cada día.
 */
class AppProgress {
    val done: MutableMap<String, NodeResult> = linkedMapOf()
    val daily: MutableMap<String, Int> = sortedMapOf()
    var goal: Int = 20

    /** Récords del modo «Jugar» (ADR-0015). */
    var game = GameRecords()
        private set
    private var hearts: Int = MAX_HEARTS
    private var heartsAt: Instant = Instant.EPOCH

    /* ---------- XP, meta y racha ---------- */

    fun addXp(xp: Int, today: LocalDate = LocalDate.now()) {
        if (xp <= 0) return
        val day = today.toString()
        daily[day] = (daily[day] ?: 0) + xp
        // Un año de historial basta para la racha y el calendario
        while (daily.size > MAX_DAYS) daily.remove(daily.keys.first())
    }

    fun xpOn(day: LocalDate): Int = daily[day.toString()] ?: 0

    fun totalXp(): Int = daily.values.sum()

    /** Días seguidos con XP. Hoy sin XP todavía no rompe la racha: el día no ha terminado. */
    fun streak(today: LocalDate = LocalDate.now()): Int {
        var day = if (xpOn(today) > 0) today else today.minusDays(1)
        var count = 0
        while (xpOn(day) > 0) {
            count++
            day = day.minusDays(1)
        }
        return count
    }

    /* ---------- Ruta ---------- */

    fun complete(node: PathNode, perfect: Boolean, today: LocalDate = LocalDate.now()): Int {
        val before = done[node.id]
        done[node.id] = NodeResult(perfect || before?.perfect == true, today.toString())
        val xp = XP_LESSON + if (perfect) XP_PERFECT else 0
        addXp(xp, today)
        return xp
    }

    /** Primer nodo sin completar: el único desbloqueado además de los ya hechos. */
    fun currentNode(units: List<PathUnit>): PathNode? = units.flatMap { it.nodes }.firstOrNull { it.id !in done }

    fun isUnlocked(node: PathNode, units: List<PathUnit>): Boolean = node.id in done || node == currentNode(units)

    /* ---------- Vidas ---------- */

    /** Vidas disponibles ahora (se recupera una cada [REFILL]). */
    fun heartsNow(now: Instant = Instant.now()): Int {
        normalize(now)
        return hearts
    }

    /** Tiempo hasta la siguiente vida, o null si están todas. */
    fun nextHeartIn(now: Instant = Instant.now()): Duration? {
        normalize(now)
        return if (hearts >= MAX_HEARTS) null else REFILL.minus(Duration.between(heartsAt, now))
    }

    fun loseHeart(now: Instant = Instant.now()) {
        normalize(now)
        if (hearts == MAX_HEARTS) heartsAt = now // el reloj de recarga empieza con la primera vida perdida
        hearts = maxOf(0, hearts - 1)
    }

    fun gainHeart(now: Instant = Instant.now()) {
        normalize(now)
        hearts = minOf(MAX_HEARTS, hearts + 1)
    }

    private fun normalize(now: Instant) {
        if (hearts >= MAX_HEARTS) return
        val gained = Duration.between(heartsAt, now).toMillis() / REFILL.toMillis()
        if (gained <= 0) return
        hearts = minOf(MAX_HEARTS, hearts + gained.toInt())
        heartsAt = if (hearts >= MAX_HEARTS) now else heartsAt.plus(REFILL.multipliedBy(gained))
    }

    /* ---------- Fusión y JSON ---------- */

    /** Une el progreso de otro dispositivo: nodos hechos, XP máxima de cada día. Meta y vidas son de este dispositivo. */
    fun merge(other: AppProgress) {
        for ((id, result) in other.done) {
            val local = done[id]
            done[id] = if (local == null) result else NodeResult(local.perfect || result.perfect, maxOf(local.date, result.date))
        }
        for ((day, xp) in other.daily) daily[day] = maxOf(daily[day] ?: 0, xp)
        game.merge(other.game)
    }

    fun toJson(): JSONObject = JSONObject().apply {
        put("done", JSONObject().apply { done.forEach { (id, r) -> put(id, JSONObject().apply { put("perfect", r.perfect); put("date", r.date) }) } })
        put("daily", JSONObject().apply { daily.forEach { (day, xp) -> put(day, xp) } })
        put("goal", goal)
        put("hearts", hearts)
        put("heartsAt", PcapState.iso(heartsAt))
        put("game", game.toJson())
    }

    companion object {
        const val MAX_HEARTS = 5
        val REFILL: Duration = Duration.ofHours(4)
        const val XP_LESSON = 10
        const val XP_PERFECT = 5
        const val XP_PRACTICE = 1
        const val MAX_DAYS = 400
        val GOALS = listOf(10, 20, 30, 50)

        fun fromJson(json: JSONObject?): AppProgress {
            val progress = AppProgress()
            if (json == null) return progress
            json.optJSONObject("done")?.let { done ->
                done.keys().forEach { id ->
                    val r = done.optJSONObject(id) ?: return@forEach
                    progress.done[id] = NodeResult(r.optBoolean("perfect"), r.optString("date"))
                }
            }
            json.optJSONObject("daily")?.let { daily ->
                daily.keys().forEach { day -> daily.optInt(day).takeIf { it > 0 }?.let { progress.daily[day] = it } }
            }
            progress.goal = json.optInt("goal", 20).takeIf { it in GOALS } ?: 20
            progress.hearts = json.optInt("hearts", MAX_HEARTS).coerceIn(0, MAX_HEARTS)
            progress.game = GameRecords.fromJson(json.optJSONObject("game"))
            progress.heartsAt = runCatching { Instant.parse(json.optString("heartsAt")) }.getOrDefault(Instant.EPOCH)
            return progress
        }
    }
}
