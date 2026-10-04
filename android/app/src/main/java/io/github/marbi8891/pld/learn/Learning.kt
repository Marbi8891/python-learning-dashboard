package io.github.marbi8891.pld.learn

import org.json.JSONArray
import org.json.JSONObject
import java.time.Instant
import java.time.LocalDate
import java.time.ZoneId
import java.time.temporal.ChronoUnit

/*
 * Núcleo educativo por conceptos en la app (ADR-0031, fase 4). Es la misma lógica que la web
 * (frontend/js/learn/mastery.js, recommend.js y session.js) y el mismo documento JSON
 * (/api/course-state/learn), así que el progreso se comparte. Sin dependencias de Android:
 * se prueba en la JVM con LearningTest.
 */

/* ---------- Contenido (frontend/data/learning.json) ---------- */

data class LearnError(val id: String, val concept: String, val label: String, val why: String, val think: String, val avoid: String)

data class Example(val code: String, val output: String, val lines: List<Pair<Int, String>>)

data class Concept(
    val id: String,
    val title: String,
    val area: String,
    val requires: List<String>,
    val daw: Int,
    val summary: String,
    /** Teoría propia; si es null, se usa la de las lecciones de `lessons` (lessons.json). */
    val theory: String?,
    val lessons: List<String>,
    val whenToUse: String,
    val example: Example,
    val errors: List<LearnError>,
)

data class Option(val text: String, val error: String?)

data class Check(val stdin: String, val error: String?)

data class Exercise(
    val id: String,
    val concept: String,
    val kind: String,
    val level: Int,
    val daw: Boolean,
    val q: String,
    val code: String?,
    val explain: String,
    val options: List<Option> = emptyList(),
    val answer: Int = 0,
    val codeOptions: Boolean = false,
    val expect: String? = null,
    val stdin: String = "",
    val traps: Map<String, String> = emptyMap(),
    val accept: List<String> = emptyList(),
    val lines: List<String> = emptyList(),
    val pseudo: Boolean = false,
    val line: Int = 0,
    val fix: String = "",
    val error: String? = null,
    val checks: List<Check> = emptyList(),
    val solution: String = "",
) {
    /** Errores típicos que este ejercicio puede detectar. */
    val errorsTested: Set<String>
        get() = (options.mapNotNull { it.error } + traps.values + checks.mapNotNull { it.error } + listOfNotNull(error)).toSet()
}

data class Competency(val id: String, val title: String, val summary: String, val requires: List<String>, val concepts: List<String>, val weight: Int)

class LearningContent(
    val path: List<String>,
    val concepts: Map<String, Concept>,
    val exercises: Map<String, Exercise>,
    val competencies: List<Competency>,
) {
    val byConcept: Map<String, List<Exercise>> = exercises.values.groupBy { it.concept }
    val errors: Map<String, LearnError> = concepts.values.flatMap { it.errors }.associateBy { it.id }

    companion object {
        fun parse(json: String): LearningContent {
            val root = JSONObject(json)
            val concepts = root.getJSONArray("concepts").objects().map { c ->
                val id = c.getString("id")
                val example = c.getJSONObject("example")
                Concept(
                    id = id,
                    title = c.getString("title"),
                    area = c.getString("area"),
                    requires = c.getJSONArray("requires").strings(),
                    daw = c.getInt("daw"),
                    summary = c.getString("summary"),
                    theory = c.optStringOrNull("theory"),
                    lessons = c.optJSONArray("lessons")?.strings() ?: emptyList(),
                    whenToUse = c.getString("when"),
                    example = Example(
                        code = example.getString("code"),
                        output = example.optString("output"),
                        lines = example.getJSONArray("lines").let { lines ->
                            (0 until lines.length()).map { i -> lines.getJSONArray(i).let { it.getInt(0) to it.getString(1) } }
                        },
                    ),
                    errors = c.getJSONArray("errors").objects().map {
                        LearnError(it.getString("id"), id, it.getString("label"), it.getString("why"), it.getString("think"), it.getString("avoid"))
                    },
                )
            }
            val exercises = root.getJSONArray("exercises").objects().map { e ->
                Exercise(
                    id = e.getString("id"),
                    concept = e.getString("concept"),
                    kind = e.getString("kind"),
                    level = e.getInt("level"),
                    daw = e.getBoolean("daw"),
                    q = e.getString("q"),
                    code = e.optStringOrNull("code"),
                    explain = e.getString("explain"),
                    options = e.optJSONArray("options")?.objects()?.map { Option(it.getString("text"), it.optStringOrNull("error")) } ?: emptyList(),
                    answer = e.optInt("answer", 0),
                    codeOptions = e.optBoolean("codeOptions", false),
                    expect = e.optStringOrNull("expect"),
                    stdin = e.optString("stdin", ""),
                    traps = e.optJSONObject("traps")?.let { t -> t.keys().asSequence().associateWith { t.getString(it) } } ?: emptyMap(),
                    accept = e.optJSONArray("accept")?.strings() ?: emptyList(),
                    lines = e.optJSONArray("lines")?.strings() ?: emptyList(),
                    pseudo = e.optBoolean("pseudo", false),
                    line = e.optInt("line", 0),
                    fix = e.optString("fix", ""),
                    error = e.optStringOrNull("error"),
                    checks = e.optJSONArray("checks")?.objects()?.map { Check(it.optString("stdin", ""), it.optStringOrNull("error")) } ?: emptyList(),
                    solution = e.optString("solution", ""),
                )
            }
            val competencies = root.optJSONArray("daw")?.objects()?.map {
                Competency(
                    it.getString("id"), it.getString("title"), it.getString("summary"),
                    it.optJSONArray("requires")?.strings() ?: emptyList(), it.getJSONArray("concepts").strings(), it.getInt("weight"),
                )
            } ?: emptyList()
            return LearningContent(
                path = root.getJSONArray("path").strings(),
                concepts = concepts.associateBy { it.id },
                exercises = exercises.associateBy { it.id },
                competencies = competencies,
            )
        }
    }
}

/* ---------- Corrección (mismas reglas que learn/answers.js) ---------- */

data class Result(val ok: Boolean, val error: String?)

/** Respuesta del alumno; cada tipo usa su campo. */
data class Reply(val choice: Int? = null, val text: String = "", val order: List<Int> = emptyList(), val line: Int? = null)

object Grader {
    fun normalizeOutput(text: String): String = text.replace("\r\n", "\n").split("\n").joinToString("\n") { it.trimEnd() }.trimEnd('\n')

    fun normalizeFill(code: String): String = code.replace(Regex("\\s+"), "").removeSuffix(";")

    /** Ejercicios que se pueden hacer en el móvil (los de escribir código necesitan Python: van en la web). */
    fun supported(exercise: Exercise): Boolean = exercise.kind != "code"

    fun missing(exercise: Exercise, reply: Reply): String? = when (exercise.kind) {
        "choice" -> if (reply.choice == null) "Elige una respuesta." else null
        "bug" -> if (reply.line == null) "Señala la línea que tiene el error." else null
        "output" -> if (reply.text.isBlank()) "Escribe lo que crees que muestra el programa." else null
        "fill" -> if (reply.text.isBlank()) "Escribe lo que va en el hueco." else null
        "order" -> if (reply.order.size != exercise.lines.size) "Coloca todas las líneas." else null
        else -> null
    }

    fun grade(exercise: Exercise, reply: Reply): Result = when (exercise.kind) {
        "choice" -> {
            val ok = reply.choice == exercise.answer
            Result(ok, if (ok) null else exercise.options.getOrNull(reply.choice ?: -1)?.error)
        }
        "output" -> {
            val given = normalizeOutput(reply.text)
            val ok = given == normalizeOutput(exercise.expect.orEmpty())
            Result(ok, if (ok) null else exercise.traps.entries.firstOrNull { normalizeOutput(it.key) == given }?.value)
        }
        "fill" -> {
            val given = normalizeFill(reply.text)
            val ok = exercise.accept.any { normalizeFill(it) == given }
            Result(ok, if (ok) null else exercise.traps.entries.firstOrNull { normalizeFill(it.key) == given }?.value)
        }
        "order" -> {
            val ok = reply.order.size == exercise.lines.size && reply.order.withIndex().all { (k, i) -> exercise.lines[i] == exercise.lines[k] }
            Result(ok, if (ok) null else exercise.error)
        }
        "bug" -> {
            val ok = reply.line == exercise.line
            Result(ok, if (ok) null else exercise.error)
        }
        else -> throw IllegalArgumentException("En el móvil no se corrigen ejercicios de tipo ${exercise.kind}")
    }
}

/* ---------- Estado del alumno (documento compartido con la web) ---------- */

data class ExerciseEntry(val history: List<Boolean>, val last: String, val count: Int)

data class ConceptEntry(val box: Int = 0, val due: String? = null, val last: String? = null, val read: String? = null, val placed: String? = null)

data class ErrorEntry(val count: Int, val last: String, val streak: Int)

data class LogEntry(val at: String, val exercise: String, val ok: Boolean, val error: String?)

class LearningState {
    val ex = linkedMapOf<String, ExerciseEntry>()
    val concepts = linkedMapOf<String, ConceptEntry>()
    val errors = linkedMapOf<String, ErrorEntry>()
    val log = mutableListOf<LogEntry>()

    /** Simulacros: se conservan tal cual llegan de la web (la app no los hace todavía). */
    var exams: JSONArray = JSONArray()

    fun toJson(): JSONObject {
        val json = JSONObject().put("v", 1)
        json.put("ex", JSONObject().also { o -> ex.forEach { (id, e) -> o.put(id, JSONObject().put("h", JSONArray(e.history)).put("last", e.last).put("n", e.count)) } })
        json.put(
            "concepts",
            JSONObject().also { o ->
                concepts.forEach { (id, c) ->
                    o.put(id, JSONObject().put("box", c.box).put("due", c.due ?: JSONObject.NULL).put("last", c.last ?: JSONObject.NULL).put("read", c.read ?: JSONObject.NULL).put("placed", c.placed ?: JSONObject.NULL))
                }
            },
        )
        json.put("errors", JSONObject().also { o -> errors.forEach { (id, e) -> o.put(id, JSONObject().put("n", e.count).put("last", e.last).put("streak", e.streak)) } })
        json.put("log", JSONArray().also { a -> log.forEach { a.put(JSONObject().put("at", it.at).put("ex", it.exercise).put("ok", it.ok).put("err", it.error ?: JSONObject.NULL)) } })
        json.put("exams", exams)
        return json
    }

    companion object {
        private val ID = Regex("^[a-z0-9][a-z0-9.-]{0,60}$")
        private val ISO = Regex("^\\d{4}-\\d{2}-\\d{2}T[\\d:.+-]+Z?$")
        private val DAY = Regex("^\\d{4}-\\d{2}-\\d{2}$")

        /** Lee y valida (como cleanLearning en la web): lo que no tiene el formato esperado se descarta. */
        fun fromJson(text: String?): LearningState {
            val state = LearningState()
            val root = text?.let { runCatching { JSONObject(it) }.getOrNull() } ?: return state
            fun iso(o: JSONObject, key: String): String? = o.optStringOrNull(key)?.takeIf { ISO.matches(it) }
            root.optJSONObject("ex")?.let { o ->
                o.keys().forEach { id ->
                    val e = o.optJSONObject(id) ?: return@forEach
                    val last = iso(e, "last") ?: return@forEach
                    val history = e.optJSONArray("h")?.let { h -> (0 until h.length()).mapNotNull { h.opt(it) as? Boolean } } ?: return@forEach
                    if (ID.matches(id)) state.ex[id] = ExerciseEntry(history.takeLast(HISTORY), last, e.optInt("n", history.size))
                }
            }
            root.optJSONObject("concepts")?.let { o ->
                o.keys().forEach { id ->
                    val c = o.optJSONObject(id) ?: return@forEach
                    if (!ID.matches(id)) return@forEach
                    val box = c.optInt("box", 0).takeIf { it in 0..MAX_BOX } ?: 0
                    state.concepts[id] = ConceptEntry(box, c.optStringOrNull("due")?.takeIf { DAY.matches(it) }, iso(c, "last"), iso(c, "read"), iso(c, "placed"))
                }
            }
            root.optJSONObject("errors")?.let { o ->
                o.keys().forEach { id ->
                    val e = o.optJSONObject(id) ?: return@forEach
                    val last = iso(e, "last") ?: return@forEach
                    if (ID.matches(id)) state.errors[id] = ErrorEntry(e.optInt("n", 1), last, e.optInt("streak", 0).coerceAtLeast(0))
                }
            }
            root.optJSONArray("log")?.objects()?.forEach { l ->
                val at = iso(l, "at") ?: return@forEach
                val id = l.optString("ex")
                val ok = l.opt("ok") as? Boolean ?: return@forEach
                if (ID.matches(id)) state.log.add(LogEntry(at, id, ok, l.optStringOrNull("err")?.takeIf { ID.matches(it) }))
            }
            root.optJSONArray("exams")?.let { state.exams = it }
            return state
        }

        const val HISTORY = 5
        const val LOG_SIZE = 300
        val INTERVAL_DAYS = listOf(0, 1, 3, 7, 14, 30)
        val MAX_BOX = INTERVAL_DAYS.size - 1
    }
}

/* ---------- Reglas (mismas constantes y prioridades que la web) ---------- */

data class ConceptStats(
    val id: String,
    val score: Double,
    val status: String,
    val attempted: Int,
    val due: Boolean,
    val nextReview: String?,
    val last: String?,
    val placed: Boolean,
)

data class PlanItem(val type: String, val concept: String, val reason: String)

class Learning(val content: LearningContent, val state: LearningState, private val zone: ZoneId = ZoneId.systemDefault()) {

    private fun day(instant: Instant): LocalDate = instant.atZone(zone).toLocalDate()

    private fun daysSince(iso: String, now: Instant): Long = ChronoUnit.DAYS.between(day(Instant.parse(iso)), day(now))

    /* --- Registrar --- */

    fun recordAttempt(exercise: Exercise, result: Result, now: Instant = Instant.now(), retry: Boolean = false) {
        val at = now.toString()
        if (!retry) {
            val old = state.ex[exercise.id]
            state.ex[exercise.id] = ExerciseEntry(((old?.history ?: emptyList()) + result.ok).takeLast(LearningState.HISTORY), at, (old?.count ?: 0) + 1)
        }
        state.concepts[exercise.concept] = (state.concepts[exercise.concept] ?: ConceptEntry()).copy(last = at)
        val error = result.error
        if (error != null) {
            val old = state.errors[error]
            state.errors[error] = ErrorEntry((old?.count ?: 0) + 1, at, 0)
        } else if (result.ok && !retry) {
            exercise.errorsTested.forEach { id -> state.errors[id]?.let { state.errors[id] = it.copy(streak = minOf(it.streak + 1, 99)) } }
        }
        state.log.add(LogEntry(at, exercise.id, result.ok, error))
        while (state.log.size > LearningState.LOG_SIZE) state.log.removeAt(0)
    }

    fun markRead(conceptId: String, now: Instant = Instant.now()) {
        val entry = state.concepts[conceptId] ?: ConceptEntry()
        state.concepts[conceptId] = entry.copy(read = now.toString(), last = entry.last ?: now.toString())
    }

    /** Repaso espaciado al cerrar una sesión: ≥ 80 % sube de caja, < 50 % vuelve a la 1, entre medias se mantiene. */
    fun reviewConcept(conceptId: String, accuracy: Double, now: Instant = Instant.now()) {
        val entry = state.concepts[conceptId] ?: ConceptEntry()
        val box = when {
            accuracy >= 0.8 -> minOf(entry.box + 1, LearningState.MAX_BOX)
            accuracy < 0.5 -> 1
            else -> maxOf(entry.box, 1)
        }
        state.concepts[conceptId] = entry.copy(box = box, due = day(now).plusDays(LearningState.INTERVAL_DAYS[box].toLong()).toString())
    }

    /* --- Consultar --- */

    fun activeErrors(now: Instant = Instant.now()): List<Pair<String, ErrorEntry>> =
        state.errors.entries
            .filter { (_, e) -> e.streak < FIXED_STREAK && daysSince(e.last, now) <= ERROR_DAYS }
            .sortedByDescending { it.value.last }
            .map { it.key to it.value }

    private fun lastOk(id: String) = state.ex[id]?.history?.lastOrNull() == true

    fun stats(conceptId: String, now: Instant = Instant.now()): ConceptStats {
        val exercises = content.byConcept[conceptId].orEmpty()
        val entry = state.concepts[conceptId]
        val total = exercises.sumOf { weight(it.level) }
        val earned = exercises.filter { lastOk(it.id) }.sumOf { weight(it.level) }
        val attempted = exercises.count { it.id in state.ex }
        val score = if (total > 0) earned / total else 0.0
        val advanced = exercises.filter { it.level >= 2 }
        val appliedOk = advanced.isEmpty() || advanced.any { lastOk(it.id) }
        val errors = activeErrors(now).count { content.errors[it.first]?.concept == conceptId }
        val status = when {
            attempted == 0 -> if (entry?.read != null) "leido" else "nuevo"
            score >= 0.8 && appliedOk && errors == 0 -> "dominado"
            score >= 0.5 -> "progreso"
            else -> "aprendiendo"
        }
        val due = entry?.due != null && entry.due <= day(now).toString()
        return ConceptStats(conceptId, score, status, attempted, due, entry?.due, entry?.last, entry?.placed != null)
    }

    fun allStats(now: Instant = Instant.now()): Map<String, ConceptStats> = content.path.associateWith { stats(it, now) }

    private fun isReady(s: ConceptStats) = s.score >= READY_SCORE || s.placed

    fun missingPrerequisites(conceptId: String, all: Map<String, ConceptStats>): List<String> =
        content.concepts.getValue(conceptId).requires.filter { !isReady(all.getValue(it)) }

    /** Plan de hoy: repasos → errores recientes → DAW sin dominar → nuevo (si la base está firme) → repaso general. */
    fun todayPlan(now: Instant = Instant.now()): List<PlanItem> {
        val all = allStats(now)
        val plan = mutableListOf<PlanItem>()
        fun push(item: PlanItem) {
            if (plan.size < PLAN_SIZE && plan.none { it.concept == item.concept }) plan.add(item)
        }
        fun title(id: String) = content.concepts.getValue(id).title

        all.values.filter { it.due }.sortedBy { it.nextReview }.take(2).forEach { s ->
            val days = s.last?.let { daysSince(it, now) } ?: 0
            push(PlanItem("review", s.id, if (days > 0) "Toca repasarlo: lo practicaste hace $days ${if (days == 1L) "día" else "días"}." else "Toca repasarlo hoy."))
        }
        activeErrors(now).groupBy { content.errors[it.first]?.concept }.forEach { (concept, list) ->
            if (concept != null) push(PlanItem("errors", concept, "Error reciente: ${content.errors.getValue(list.first().first).label}."))
        }
        val next = content.path.firstOrNull { all.getValue(it).attempted == 0 && !all.getValue(it).placed }
        val blockers = next?.let { missingPrerequisites(it, all) }.orEmpty()
        fun reinforce(id: String) = PlanItem("reinforce", id, "Necesitas reforzar ${title(id)} antes de pasar a ${title(next!!)}.")
        all.values
            .filter { it.attempted > 0 && !it.placed && it.status != "dominado" && content.concepts.getValue(it.id).daw == 3 }
            .sortedBy { it.score }
            .forEach { s -> push(if (s.id in blockers) reinforce(s.id) else PlanItem("practice", s.id, "Importante para DAW y aún no lo dominas (${Math.round(s.score * 100)} %).")) }
        if (next != null && blockers.isEmpty()) push(PlanItem("learn", next, "Siguiente concepto de la ruta."))
        blockers.forEach { push(reinforce(it)) }
        if (plan.size < 3) {
            all.values.filter { it.placed && it.status != "dominado" }
                .forEach { push(PlanItem("practice", it.id, "Lo superaste en la prueba de nivel: practícalo para consolidarlo.")) }
        }
        if (plan.size < 3) {
            all.values.filter { it.status == "dominado" && it.last != null && daysSince(it.last, now) >= GENERAL_REVIEW_DAYS }
                .sortedBy { it.last }
                .forEach { push(PlanItem("review", it.id, "Repaso general para que no se olvide.")) }
        }
        return plan
    }

    /** Igual que selectExercises en la web. En el móvil, sin ejercicios de escribir código. */
    fun selectExercises(conceptIds: List<String>, count: Int, now: Instant = Instant.now(), random: () -> Double = Math::random): List<Exercise> {
        val all = allStats(now)
        val active = activeErrors(now).map { it.first }.toSet()
        return conceptIds.flatMap { content.byConcept[it].orEmpty() }
            .filter(Grader::supported)
            .map { exercise ->
                val history = state.ex[exercise.id]?.history.orEmpty()
                val level = targetLevel(all.getValue(exercise.concept).score)
                var score = random()
                if (exercise.errorsTested.any { it in active }) score += 6
                when {
                    history.isEmpty() -> score += 3
                    history.last() == false -> score += 4
                    history.size >= 2 && history[history.size - 2] -> score -= 6
                    daysSince(state.ex.getValue(exercise.id).last, now) == 0L -> score -= 3
                }
                if (exercise.level > level + 1) score -= 4 else if (exercise.level > level) score -= 1
                exercise to score
            }
            .sortedByDescending { it.second }
            .take(count)
            .map { it.first }
            .sortedBy { it.level }
    }

    fun similarExercise(exercise: Exercise, errorId: String?, exclude: Set<String>): Exercise? {
        val pool = content.byConcept[exercise.concept].orEmpty().filter { it.id != exercise.id && it.id !in exclude && Grader.supported(it) }
        return errorId?.let { e -> pool.firstOrNull { e in it.errorsTested } } ?: pool.firstOrNull { it.level <= exercise.level }
    }

    companion object {
        const val PLAN_SIZE = 4
        const val READY_SCORE = 0.6
        const val FIXED_STREAK = 2
        const val ERROR_DAYS = 21
        const val GENERAL_REVIEW_DAYS = 3

        fun weight(level: Int): Double = when (level) {
            2 -> 1.5
            3 -> 2.0
            else -> 1.0
        }

        fun targetLevel(score: Double): Int = if (score < 0.4) 1 else if (score < 0.8) 2 else 3

        /** Fusión con la copia de la cuenta (como mergeLearning en la web): no se pierde nada de ninguno. */
        fun merge(local: LearningState, remoteJson: JSONObject) {
            val remote = LearningState.fromJson(remoteJson.toString())
            remote.ex.forEach { (id, e) -> if ((local.ex[id]?.count ?: -1) < e.count) local.ex[id] = e }
            remote.concepts.forEach { (id, c) ->
                val mine = local.concepts[id]
                if (mine == null) {
                    local.concepts[id] = c
                } else {
                    val newer = if ((mine.last ?: "") >= (c.last ?: "")) mine else c
                    fun latest(a: String?, b: String?) = listOfNotNull(a, b).maxOrNull()
                    local.concepts[id] = newer.copy(read = latest(mine.read, c.read), placed = latest(mine.placed, c.placed))
                }
            }
            remote.errors.forEach { (id, e) ->
                val mine = local.errors[id]
                local.errors[id] = if (mine == null) e else (if (mine.last >= e.last) mine else e).copy(count = maxOf(mine.count, e.count))
            }
            val log = (remote.log + local.log).associateBy { "${it.at}|${it.exercise}" }.values.sortedBy { it.at }.takeLast(LearningState.LOG_SIZE)
            local.log.clear()
            local.log.addAll(log)
            if (local.exams.length() < remote.exams.length()) local.exams = remote.exams
        }
    }
}

/* ---------- Sesión (como session.js): fallo → explicación → nuevo intento al final ---------- */

data class QueueItem(val id: String, val retry: Boolean = false, val retryOf: String? = null)

class LearnSession(val title: String, exercises: List<String>) {
    val queue = exercises.map { QueueItem(it) }.toMutableList()
    val results = mutableListOf<Pair<String, Result>>()
    var index = 0
        private set
    private var retries = 0

    val current: QueueItem? get() = queue.getOrNull(index)
    val done: Boolean get() = index >= queue.size

    fun submit(learning: Learning, result: Result, now: Instant = Instant.now()) {
        val item = current ?: return
        val exercise = learning.content.exercises.getValue(item.id)
        learning.recordAttempt(exercise, result, now, retry = item.retry)
        results.add(item.id to result)
        if (!result.ok && retries < MAX_RETRIES && item.retryOf == null) {
            val similar = learning.similarExercise(exercise, result.error, queue.map { it.id }.toSet())
            queue.add(if (similar != null) QueueItem(similar.id, retryOf = item.id) else QueueItem(item.id, retry = true, retryOf = item.id))
            retries++
        }
    }

    fun next() {
        index++
    }

    /** Aciertos de los primeros intentos por concepto: [aciertos, total]. */
    fun byConcept(content: LearningContent): Map<String, Pair<Int, Int>> {
        val out = linkedMapOf<String, Pair<Int, Int>>()
        results.forEachIndexed { i, (id, result) ->
            if (queue[i].retryOf != null) return@forEachIndexed
            val concept = content.exercises.getValue(id).concept
            val (ok, total) = out[concept] ?: (0 to 0)
            out[concept] = (ok + if (result.ok) 1 else 0) to (total + 1)
        }
        return out
    }

    /** Cierra la sesión: programa el repaso de cada concepto trabajado. */
    fun finish(learning: Learning, now: Instant = Instant.now()): Map<String, Pair<Int, Int>> {
        val summary = byConcept(learning.content)
        summary.forEach { (concept, pair) -> learning.reviewConcept(concept, pair.first.toDouble() / pair.second, now) }
        return summary
    }

    companion object {
        const val MAX_RETRIES = 3
    }
}

/**
 * Orden estable de las líneas de «ordenar» (nunca ya resuelto): el mismo algoritmo que la web
 * (stableShuffle en learn/ui.js), así que las líneas salen en el mismo orden en los dos sitios.
 */
fun stableOrder(id: String, count: Int): List<Int> {
    val mask = 0xFFFFFFFFL
    var seed = id.fold(7L) { h, c -> (h * 31 + c.code) and mask }
    val indices = (0 until count).toMutableList()
    for (i in count - 1 downTo 1) {
        // La web multiplica en coma flotante (number de JavaScript) y luego aplica >>> 0: se imita
        // tal cual para obtener exactamente el mismo orden
        seed = (seed.toDouble() * 1103515245.0 + 12345.0).toLong() and mask
        val j = (seed % (i + 1)).toInt()
        val tmp = indices[i]
        indices[i] = indices[j]
        indices[j] = tmp
    }
    return if (indices.withIndex().all { (k, v) -> k == v }) indices.reversed() else indices
}

/* ---------- Teoría con bloques de código y tablas ---------- */

/** Trozo de la teoría: texto (Markdown en línea y listas) o bloque monoespaciado (código o tabla). */
data class TheoryPart(val code: Boolean, val text: String)

/**
 * Separa los bloques ``` y las tablas (líneas que empiezan por |) del texto, para pintarlos en
 * monoespaciado: el Markdown de la app (parseBlocks) solo entiende párrafos y listas.
 */
fun splitTheory(text: String): List<TheoryPart> {
    val parts = mutableListOf<TheoryPart>()
    val buffer = mutableListOf<String>()
    var inFence = false
    var inTable = false
    fun flush(code: Boolean) {
        val joined = buffer.joinToString("\n").let { if (code) it.trimEnd() else it.trim() }
        if (joined.isNotEmpty()) parts.add(TheoryPart(code, joined))
        buffer.clear()
    }
    for (line in text.split("\n")) {
        when {
            line.trim().startsWith("```") -> {
                flush(code = inFence)
                inFence = !inFence
            }
            inFence -> buffer.add(line)
            line.trim().startsWith("|") -> {
                if (!inTable) flush(code = false)
                inTable = true
                // La fila separadora |---|---| no aporta nada en monoespaciado
                if (!Regex("^\\|?[\\s:|-]+$").matches(line.trim())) buffer.add(line.trim())
            }
            else -> {
                if (inTable) flush(code = true)
                inTable = false
                buffer.add(line)
            }
        }
    }
    flush(code = inFence || inTable)
    return parts
}

/* ---------- Utilidades JSON ---------- */

private fun JSONArray.objects(): List<JSONObject> = (0 until length()).map { getJSONObject(it) }

private fun JSONArray.strings(): List<String> = (0 until length()).map { getString(it) }

private fun JSONObject.optStringOrNull(key: String): String? = if (has(key) && !isNull(key)) getString(key) else null
