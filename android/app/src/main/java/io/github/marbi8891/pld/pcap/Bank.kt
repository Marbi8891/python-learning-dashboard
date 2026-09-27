package io.github.marbi8891.pld.pcap

import org.json.JSONArray
import org.json.JSONObject

/** Texto en los dos idiomas de las preguntas. */
data class Text(val es: String, val en: String) {
    fun get(lang: String): String = if (lang == "en") en else es
}

/** Opción de respuesta: código o salida de un programa (igual en los dos idiomas) o texto traducido. */
sealed interface Option {
    data class Code(val source: String) : Option
    data class Prose(val text: Text) : Option
}

data class Block(val slug: String, val weight: Int, val items: Int, val title: Text)

data class Exam(val code: String, val questions: Int, val minutes: Int, val pass: Int, val blocks: List<Block>)

/**
 * Tipo de ejercicio (ADR-0017). CHOICE es el test de siempre, y también «encontrar el error», en el que
 * las opciones son las líneas del programa. FILL: escribir lo que falta en `___`. ORDER: ordenar líneas.
 */
enum class Kind { CHOICE, FILL, ORDER }

/** Lo que ha respondido el alumno, según el tipo de ejercicio. */
data class Answer(val selected: Set<Int> = emptySet(), val text: String = "", val order: List<Int> = emptyList())

data class Question(
    val id: String,
    val block: String,
    val q: Text,
    val code: String?,
    val options: List<Option>,
    val answer: List<Int>,
    val explain: Text,
    val lesson: String?,
    val kind: Kind = Kind.CHOICE,
    /** FILL: respuestas aceptadas para el hueco `___` del código. */
    val accept: List<String> = emptyList(),
    /** ORDER: líneas en el orden correcto; la app las muestra desordenadas. */
    val lines: List<String> = emptyList(),
) {
    val multi: Boolean get() = answer.size > 1

    fun isCorrect(chosen: Collection<Int>): Boolean = chosen.size == answer.size && chosen.containsAll(answer)

    fun isCorrect(response: Answer): Boolean = when (kind) {
        Kind.CHOICE -> isCorrect(response.selected)
        Kind.FILL -> normalize(response.text).let { typed -> typed.isNotEmpty() && accept.any { normalize(it) == typed } }
        // Se comparan los textos: dos líneas iguales (como dos "}") son intercambiables
        Kind.ORDER -> response.order.size == lines.size && response.order.map { lines[it] } == lines
    }

    /** Si ya se puede pulsar «Comprobar». */
    fun isComplete(response: Answer): Boolean = when (kind) {
        Kind.CHOICE -> response.selected.size == answer.size
        Kind.FILL -> response.text.isNotBlank()
        Kind.ORDER -> response.order.size == lines.size
    }

    companion object {
        /** Los espacios y un punto y coma final no cuentan: `i<10;` vale igual que `i < 10`. */
        fun normalize(code: String): String = code.filterNot { it.isWhitespace() }.removeSuffix(";")
    }
}

data class Card(val id: String, val block: String, val front: Text, val back: Text, val code: String?, val lesson: String?)

/** Banco del PCAP: el mismo `frontend/data/pcap.json` que usa la web. */
data class Bank(val exam: Exam, val questions: List<Question>, val cards: List<Card>) {
    fun block(slug: String): Block = exam.blocks.first { it.slug == slug }

    companion object {
        fun parse(json: String): Bank {
            val root = JSONObject(json)
            val exam = root.getJSONObject("exam")
            return Bank(
                exam = Exam(
                    code = exam.getString("code"),
                    questions = exam.getInt("questions"),
                    minutes = exam.getInt("minutes"),
                    pass = exam.getInt("pass"),
                    blocks = exam.getJSONArray("blocks").objects().map {
                        Block(it.getString("slug"), it.getInt("weight"), it.getInt("items"), text(it.getJSONObject("title")))
                    },
                ),
                questions = root.getJSONArray("questions").objects().map { q ->
                    Question(
                        id = q.getString("id"),
                        block = q.getString("block"),
                        q = text(q.getJSONObject("q")),
                        code = q.optStringOrNull("code"),
                        options = q.getJSONArray("options").let { options ->
                            (0 until options.length()).map { i ->
                                val option = options.get(i)
                                if (option is JSONObject) Option.Prose(text(option)) else Option.Code(option.toString())
                            }
                        },
                        answer = q.getJSONArray("answer").let { a -> (0 until a.length()).map { a.getInt(it) } },
                        explain = text(q.getJSONObject("explain")),
                        lesson = q.optStringOrNull("lesson"),
                        kind = when (q.optString("kind")) {
                            "fill" -> Kind.FILL
                            "order" -> Kind.ORDER
                            else -> Kind.CHOICE
                        },
                        accept = q.optJSONArray("accept").strings(),
                        lines = q.optJSONArray("lines").strings(),
                    )
                },
                cards = root.getJSONArray("cards").objects().map { c ->
                    Card(
                        id = c.getString("id"),
                        block = c.getString("block"),
                        front = text(c.getJSONObject("front")),
                        back = text(c.getJSONObject("back")),
                        code = c.optStringOrNull("code"),
                        lesson = c.optStringOrNull("lesson"),
                    )
                },
            )
        }

        private fun text(json: JSONObject) = Text(json.getString("es"), json.getString("en"))
    }
}

internal fun JSONArray.objects(): List<JSONObject> = (0 until length()).map { getJSONObject(it) }

internal fun JSONArray?.strings(): List<String> = if (this == null) emptyList() else (0 until length()).map { getString(it) }

internal fun JSONObject.optStringOrNull(name: String): String? =
    if (has(name) && !isNull(name)) getString(name) else null
