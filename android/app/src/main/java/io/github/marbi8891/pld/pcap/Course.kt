package io.github.marbi8891.pld.pcap

import kotlin.math.roundToInt

/** Nodo del camino: una lección corta de unas 5 preguntas. */
data class PathNode(val id: String, val unit: String, val number: Int, val questionIds: List<String>)

/** Unidad del camino: una lección del temario con sus lecciones cortas. */
data class PathUnit(val slug: String, val block: String, val title: String, val nodes: List<PathNode>)

/** Ruta tipo Duolingo generada a partir del banco y del temario (ADR-0012). */
object Course {
    const val LESSON_SIZE = 5
    const val MIN_UNIT = 3

    fun build(bank: Bank, lessons: LessonIndex): List<PathUnit> {
        val units = mutableListOf<PathUnit>()
        for (block in bank.exam.blocks) {
            val pending = mutableListOf<Question>()
            val groups = mutableListOf<Pair<String, MutableList<Question>>>()
            for (slug in lessons.modules[block.slug].orEmpty()) {
                pending += bank.questions.filter { it.block == block.slug && it.lesson == slug }.sortedBy { it.id }
                if (pending.size >= MIN_UNIT) {
                    groups += slug to pending.toMutableList()
                    pending.clear()
                }
            }
            // Lo que sobra al final del bloque se une a la última unidad
            if (pending.isNotEmpty()) {
                if (groups.isEmpty()) groups += (lessons.modules[block.slug]?.lastOrNull() ?: block.slug) to pending.toMutableList()
                else groups.last().second += pending
            }
            groups.forEach { (slug, questions) ->
                units += PathUnit(slug, block.slug, lessons.titles[slug] ?: slug, split(slug, questions.map { it.id }))
            }
        }
        return units
    }

    /** Reparte las preguntas en lecciones de tamaño parecido (difieren como mucho en una). */
    private fun split(unit: String, ids: List<String>): List<PathNode> {
        val count = maxOf(1, (ids.size / LESSON_SIZE.toDouble()).roundToInt())
        val base = ids.size / count
        val extra = ids.size % count
        var start = 0
        return (0 until count).map { i ->
            val size = base + if (i < extra) 1 else 0
            PathNode("$unit-${i + 1}", unit, i + 1, ids.subList(start, start + size)).also { start += size }
        }
    }
}

enum class UnitState { DONE, CURRENT, LOCKED }

/**
 * Resumen de una unidad para su tarjeta: estado, lecciones hechas y acierto.
 * El acierto sigue la misma regla que [PcapState.blockStats]: último intento de cada pregunta respondida.
 */
data class UnitSummary(
    val state: UnitState,
    val lessonsDone: Int,
    val lessons: Int,
    val questions: Int,
    val answered: Int,
    val rate: Double?,
) {
    val progress: Float get() = if (lessons == 0) 0f else lessonsDone.toFloat() / lessons
}

fun PcapState.unitSummary(unit: PathUnit, current: PathNode?): UnitSummary {
    val lessonsDone = unit.nodes.count { it.id in app.done }
    val state = when {
        lessonsDone == unit.nodes.size -> UnitState.DONE
        current != null && current in unit.nodes -> UnitState.CURRENT
        else -> UnitState.LOCKED
    }
    val ids = unit.nodes.flatMap { it.questionIds }
    val last = ids.mapNotNull { answers[it]?.lastOrNull() }
    return UnitSummary(
        state = state,
        lessonsDone = lessonsDone,
        lessons = unit.nodes.size,
        questions = ids.size,
        answered = last.size,
        rate = if (last.isEmpty()) null else last.count { it }.toDouble() / last.size,
    )
}
