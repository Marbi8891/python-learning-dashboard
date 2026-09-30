package io.github.marbi8891.pld.pcap

import java.time.LocalDate
import java.time.temporal.ChronoUnit

/*
 * «Mi cuenta» en la app (ADR-0027): las mismas cuentas que la web (frontend/js/private.js) sobre el
 * estado de cada curso. Sin Android, con tests.
 */

/** Resumen de un curso para el plan de estudio y la tarjeta de progreso. */
data class CourseOverview(
    /** Dominio: acierto ponderado por el peso de cada bloque (0-100). */
    val score: Int,
    val answered: Int,
    val exams: Int,
    val bestExam: Int?,
    /** Bloque con menos acierto (si baja del 80 %) o, si no, el primero sin empezar. */
    val focus: Block?,
    val focusRate: Double?,
    /** Preguntas del repaso espaciado que tocan hoy o están atrasadas. */
    val due: Int,
    val examDate: LocalDate?,
    val daysLeft: Long?,
    /** Certificado de finalización (no oficial) disponible, con las reglas de la web. */
    val certificate: Boolean,
)

object Overview {
    const val FOCUS_BELOW = 0.8
    const val CERT_SCORE = 70 // mismas reglas que COURSE_PASS y COURSE_BLOCK_ANSWERED de la web
    const val CERT_BLOCK_ANSWERED = 5
    const val PCAP_CERT_EXAM = 70

    fun of(state: PcapState, bank: Bank, isPcap: Boolean, today: LocalDate = LocalDate.now()): CourseOverview {
        val stats = state.blockStats(bank)
        val blocks = bank.exam.blocks
        val score = state.readiness(stats, blocks)
        val weakest = blocks.filter { stats.getValue(it.slug).answered > 0 }.minByOrNull { stats.getValue(it.slug).rate ?: 0.0 }
        val weakRate = weakest?.let { stats.getValue(it.slug).rate }
        val (focus, focusRate) = when {
            weakest != null && (weakRate ?: 0.0) < FOCUS_BELOW -> weakest to weakRate
            else -> blocks.firstOrNull { stats.getValue(it.slug).answered == 0 } to null
        }
        val date = state.examDate?.let { runCatching { LocalDate.parse(it) }.getOrNull() }
        val todayText = today.toString()
        // El PCAP da el certificado en la web (lecciones + simulacro); aquí se estima con el simulacro
        val certificate = if (isPcap) {
            state.exams.any { it.score >= PCAP_CERT_EXAM }
        } else {
            score >= CERT_SCORE && blocks.all { stats.getValue(it.slug).answered >= CERT_BLOCK_ANSWERED }
        }
        return CourseOverview(
            score = score,
            answered = state.answers.size,
            exams = state.exams.size,
            bestExam = state.exams.maxOfOrNull { it.score },
            focus = focus,
            focusRate = focusRate,
            due = state.srs.values.count { it.due <= todayText },
            examDate = date,
            daysLeft = date?.let { ChronoUnit.DAYS.between(today, it) },
            certificate = certificate,
        )
    }

    /** «20 días», «Mañana», «¡Hoy!», «Ya pasó». */
    fun countdown(days: Long?): String = when {
        days == null -> "Sin fecha"
        days > 1 -> "Faltan $days días"
        days == 1L -> "Es mañana"
        days == 0L -> "¡Es hoy!"
        else -> "Ya pasó"
    }
}

/** Logro de la app: se calcula con el progreso, no se guarda (así no se desincroniza). */
data class Achievement(val icon: String, val name: String, val goal: String, val done: Boolean)

object Achievements {
    fun of(app: AppProgress, courses: List<Pair<PcapState, CourseOverview>>, today: LocalDate = LocalDate.now()): List<Achievement> {
        val states = courses.map { it.first }
        val right = states.sumOf { s -> s.answers.values.count { true in it } }
        val passed = states.sumOf { s -> s.exams.count { it.score >= 50 } }
        return listOf(
            Achievement("▶", "Primer paso", "Completa tu primera lección de la ruta", app.done.isNotEmpty()),
            Achievement("🔥", "Constancia", "Consigue una racha de 7 días", app.streak(today) >= 7),
            Achievement("⚡", "500 XP", "Suma 500 XP en total", app.totalXp() >= 500),
            Achievement("✓", "Cien aciertos", "Acierta 100 preguntas distintas", right >= 100),
            Achievement("✎", "Aprobado", "Aprueba un simulacro", passed >= 1),
            Achievement("★", "Experto/a", "Llega al 70 % de dominio en un curso", courses.any { it.second.score >= 70 }),
            Achievement("◆", "Bloque dominado", "Acierta el 90 % de un bloque con 10 preguntas o más", states.any { it.flags["mastered"] == true }),
            Achievement("🎓", "Certificado", "Consigue el certificado de un curso", courses.any { it.second.certificate }),
        )
    }
}
