package io.github.marbi8891.pld.pcap

import org.json.JSONObject

/*
 * Teoría completa de cada lección, leída del mismo `frontend/data/lessons.json` que usa la web.
 * La app la muestra sin conexión (ADR-0014).
 */

data class QuizItem(val q: String, val code: String?, val options: List<String>, val answer: Int, val explain: String)

data class Challenge(val title: String, val stars: Int, val exercise: String, val starter: String, val hint: String?)

data class Faq(val q: String, val a: String)

data class LessonContent(
    val slug: String,
    val title: String,
    val module: String,
    val theory: String,
    val exampleCode: String,
    val exercise: String,
    val starter: String,
    val hint: String?,
    val quiz: List<QuizItem>,
    val challenge: Challenge?,
    val faq: List<Faq>,
    val sources: List<String>,
)

object LessonLibrary {
    fun parse(json: String): Map<String, LessonContent> {
        val result = linkedMapOf<String, LessonContent>()
        JSONObject(json).getJSONArray("modules").objects().forEach { module ->
            val moduleTitle = module.getString("title")
            module.getJSONArray("lessons").objects().forEach { l ->
                val assistant = l.optJSONObject("assistant")
                result[l.getString("slug")] = LessonContent(
                    slug = l.getString("slug"),
                    title = l.getString("title"),
                    module = moduleTitle,
                    theory = l.optString("theory"),
                    exampleCode = l.optString("example_code"),
                    exercise = l.optString("exercise"),
                    starter = l.optString("starter"),
                    hint = assistant?.optStringOrNull("hint"),
                    quiz = l.optJSONArray("quiz")?.objects()?.map { q ->
                        QuizItem(
                            q = q.getString("q"),
                            code = q.optStringOrNull("code"),
                            options = q.getJSONArray("options").let { o -> List(o.length()) { o.getString(it) } },
                            answer = q.getInt("answer"),
                            explain = q.optString("explain"),
                        )
                    }.orEmpty(),
                    challenge = l.optJSONObject("challenge")?.let { c ->
                        Challenge(
                            title = c.getString("title"),
                            stars = c.optInt("stars", 1),
                            exercise = c.optString("exercise"),
                            starter = c.optString("starter"),
                            hint = c.optStringOrNull("hint"),
                        )
                    },
                    faq = assistant?.optJSONArray("faq")?.objects()?.map { Faq(it.getString("q"), it.getString("a")) }.orEmpty(),
                    sources = l.optJSONArray("sources")?.objects()?.map { it.getString("title") }.orEmpty(),
                )
            }
        }
        return result
    }
}

/** Bloques de texto del temario: párrafos y listas con «- » o «1. », con la misma regla que la web (markdown.js). */
sealed interface MdBlock {
    data class Paragraph(val text: String) : MdBlock

    data class Bullets(val items: List<String>) : MdBlock

    data class Numbered(val items: List<String>) : MdBlock
}

private val BULLET = Regex("^- (.*)")
private val NUMBERED = Regex("^\\d+\\. (.*)")

fun parseBlocks(markdown: String): List<MdBlock> {
    val blocks = mutableListOf<MdBlock>()
    val paragraph = mutableListOf<String>()
    var items = mutableListOf<String>()
    var numbered = false

    fun flushParagraph() {
        if (paragraph.isNotEmpty()) blocks += MdBlock.Paragraph(paragraph.joinToString(" "))
        paragraph.clear()
    }
    fun flushList() {
        if (items.isNotEmpty()) blocks += if (numbered) MdBlock.Numbered(items) else MdBlock.Bullets(items)
        items = mutableListOf()
    }

    for (line in markdown.split("\n")) {
        val bullet = BULLET.find(line)
        val number = NUMBERED.find(line)
        when {
            bullet != null || number != null -> {
                flushParagraph()
                val isNumbered = bullet == null
                if (items.isNotEmpty() && numbered != isNumbered) flushList()
                numbered = isNumbered
                items += (bullet ?: number)!!.groupValues[1]
            }
            line.isBlank() -> {
                flushParagraph()
                flushList()
            }
            else -> {
                flushList()
                paragraph += line.trim()
            }
        }
    }
    flushParagraph()
    flushList()
    return blocks
}
