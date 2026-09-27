package io.github.marbi8891.pld.pcap

import org.json.JSONObject
import kotlin.random.Random

/*
 * Modo «Jugar» (ADR-0015): la Mazmorra del Intérprete y el minijuego Bug Rush.
 * Solo reglas, sin interfaz, para poder probarlas con tests.
 */

/**
 * Una partida de la mazmorra: una planta por bloque del PCAP, en el orden del examen.
 * Cada planta tiene [ROOMS] salas con un bug (una pregunta) y un jefe de [BOSS] preguntas con tiempo.
 * Acertar da monedas; fallar quita una vida de la partida (no las de la ruta).
 */
class DungeonRun(val floors: List<Floor>, private val random: Random = Random.Default) {
    data class Floor(val block: String, val questions: List<Question>)

    enum class Phase { ASK, FEEDBACK, FLOOR_CLEARED, WON, LOST }

    data class Answer(val chosen: Set<Int>, val correct: Boolean, val timedOut: Boolean, val coins: Int)

    var floor = 0
        private set
    var room = 0
        private set
    var hp = MAX_HP
        private set
    var coins = 0
        private set

    /** Monedas ganadas en total (gastarlas no baja la puntuación). */
    var score = 0
        private set
    var correct = 0
        private set
    var answered = 0
        private set
    var phase = Phase.ASK
        private set
    var last: Answer? = null
        private set

    /** Opciones ocultas por el comodín 50/50 en la pregunta actual. */
    var hidden: Set<Int> = emptySet()
        private set

    val current: Question get() = floors[floor].questions[room]
    val block: String get() = floors[floor].block
    val isBoss: Boolean get() = room >= ROOMS
    val roomsInFloor: Int get() = floors[floor].questions.size
    val finished: Boolean get() = phase == Phase.WON || phase == Phase.LOST
    val floorsCleared: Int get() = if (phase == Phase.FLOOR_CLEARED || phase == Phase.WON) floor + 1 else floor

    /** Devuelve si ha acertado. */
    fun answer(chosen: Set<Int>): Boolean {
        check(phase == Phase.ASK)
        val ok = current.isCorrect(chosen)
        resolve(chosen, ok, timedOut = false)
        return ok
    }

    /** Se acabó el tiempo del jefe: cuenta como fallo. */
    fun timeout() {
        check(phase == Phase.ASK)
        resolve(emptySet(), ok = false, timedOut = true)
    }

    private fun resolve(chosen: Set<Int>, ok: Boolean, timedOut: Boolean) {
        answered++
        val earned = if (ok) (if (isBoss) BOSS_COINS else ROOM_COINS) else 0
        if (ok) {
            correct++
            earn(earned)
        } else {
            hp--
        }
        last = Answer(chosen, ok, timedOut, earned)
        phase = Phase.FEEDBACK
    }

    /** Tras ver la explicación: siguiente sala, planta superada, victoria o derrota. */
    fun next() {
        check(phase == Phase.FEEDBACK)
        hidden = emptySet()
        phase = when {
            hp <= 0 -> Phase.LOST
            room + 1 < roomsInFloor -> {
                room++
                Phase.ASK
            }
            else -> {
                earn(FLOOR_BONUS)
                if (floor + 1 < floors.size) Phase.FLOOR_CLEARED else Phase.WON
            }
        }
    }

    fun enterNextFloor() {
        check(phase == Phase.FLOOR_CLEARED)
        floor++
        room = 0
        phase = Phase.ASK
    }

    fun canFiftyFifty(): Boolean =
        phase == Phase.ASK && !current.multi && current.options.size >= 3 && hidden.isEmpty() && coins >= FIFTY_COST

    /** Comodín 50/50: oculta dos opciones incorrectas. */
    fun fiftyFifty(): Boolean {
        if (!canFiftyFifty()) return false
        val wrong = current.options.indices.filter { it !in current.answer }
        hidden = wrong.shuffled(random).take(minOf(2, wrong.size - 1)).toSet()
        coins -= FIFTY_COST
        return true
    }

    fun canHeal(): Boolean = (phase == Phase.ASK || phase == Phase.FLOOR_CLEARED) && hp < MAX_HP && coins >= HEAL_COST

    fun heal(): Boolean {
        if (!canHeal()) return false
        hp++
        coins -= HEAL_COST
        return true
    }

    private fun earn(amount: Int) {
        coins += amount
        score += amount
    }

    companion object {
        const val ROOMS = 3
        const val BOSS = 3
        const val MAX_HP = 5
        const val ROOM_COINS = 10
        const val BOSS_COINS = 15
        const val FLOOR_BONUS = 25
        const val FIFTY_COST = 15
        const val HEAL_COST = 40
        const val BOSS_SECONDS = 45

        /** Las preguntas de cada planta empiezan por las falladas y las nuevas, como la práctica libre. */
        fun start(bank: Bank, state: PcapState, random: Random = Random.Default): DungeonRun =
            DungeonRun(bank.exam.blocks.map { Floor(it.slug, state.practiceSet(bank, it.slug, random).take(ROOMS + BOSS)) }, random)
    }
}

/**
 * Bug Rush: un fragmento de código y una respuesta propuesta. ¿Es la correcta?
 * Los aciertos seguidos multiplican los puntos; cada fallo resta [PENALTY_SECONDS] segundos.
 * No cuenta para la preparación: un «sí/no» rápido no mide lo mismo que elegir entre cuatro opciones.
 */
class RushGame(private val pool: List<Question>, private val random: Random = Random.Default) {
    data class Card(val question: Question, val option: Int, val isAnswer: Boolean)

    init {
        require(pool.isNotEmpty())
    }

    var card: Card = draw(null)
        private set
    var score = 0
        private set
    var combo = 0
        private set
    var bestCombo = 0
        private set
    var correct = 0
        private set
    var answered = 0
        private set
    var penalty = 0
        private set

    /** Última tarjeta respondida y si se acertó, para enseñar la respuesta buena al fallar. */
    var last: Pair<Card, Boolean>? = null
        private set

    val multiplier: Int get() = minOf(MAX_MULTIPLIER, 1 + combo / COMBO_STEP)

    fun judge(saysYes: Boolean): Boolean {
        val ok = saysYes == card.isAnswer
        answered++
        if (ok) {
            correct++
            score += multiplier
            combo++
            bestCombo = maxOf(bestCombo, combo)
        } else {
            combo = 0
            penalty += PENALTY_SECONDS
        }
        last = card to ok
        card = draw(card.question)
        return ok
    }

    val xp: Int get() = correct / CORRECT_PER_XP

    private fun draw(previous: Question?): Card {
        val options = if (pool.size > 1) pool.filter { it != previous } else pool
        val question = options.random(random)
        val isAnswer = random.nextBoolean()
        val option = if (isAnswer) question.answer.single() else question.options.indices.filter { it !in question.answer }.random(random)
        return Card(question, option, isAnswer)
    }

    companion object {
        const val DURATION_SECONDS = 90
        const val PENALTY_SECONDS = 3
        const val COMBO_STEP = 5
        const val MAX_MULTIPLIER = 4
        const val CORRECT_PER_XP = 3

        /** Preguntas de código con una sola respuesta: se pueden juzgar de un vistazo. */
        fun pool(bank: Bank): List<Question> = bank.questions.filter { it.code != null && !it.multi && it.options.size > 1 }
    }
}

/** Récords del modo «Jugar». Se guardan con el progreso de la app y se fusionan quedándose con el máximo. */
class GameRecords {
    var runs = 0
    var bestFloors = 0
    var bestScore = 0
    var bestRush = 0

    fun recordRun(run: DungeonRun) {
        runs++
        bestFloors = maxOf(bestFloors, run.floorsCleared)
        bestScore = maxOf(bestScore, run.score)
    }

    /** Devuelve si es un récord nuevo. */
    fun recordRush(score: Int): Boolean {
        val record = score > bestRush
        bestRush = maxOf(bestRush, score)
        return record
    }

    fun merge(other: GameRecords) {
        runs = maxOf(runs, other.runs)
        bestFloors = maxOf(bestFloors, other.bestFloors)
        bestScore = maxOf(bestScore, other.bestScore)
        bestRush = maxOf(bestRush, other.bestRush)
    }

    fun toJson(): JSONObject = JSONObject().apply {
        put("runs", runs)
        put("bestFloors", bestFloors)
        put("bestScore", bestScore)
        put("bestRush", bestRush)
    }

    companion object {
        fun fromJson(json: JSONObject?): GameRecords = GameRecords().apply {
            if (json == null) return@apply
            runs = json.optInt("runs").coerceAtLeast(0)
            bestFloors = json.optInt("bestFloors").coerceAtLeast(0)
            bestScore = json.optInt("bestScore").coerceAtLeast(0)
            bestRush = json.optInt("bestRush").coerceAtLeast(0)
        }
    }
}
