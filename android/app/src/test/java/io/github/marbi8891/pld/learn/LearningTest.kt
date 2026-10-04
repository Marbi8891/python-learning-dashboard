package io.github.marbi8891.pld.learn

import org.json.JSONObject
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.File
import java.time.Instant
import java.time.ZoneOffset
import kotlin.random.Random

/**
 * El núcleo educativo de la app (ADR-0031) se comporta como el de la web: mismas reglas de dominio,
 * errores, repaso, plan de hoy, selección y sesiones, y el mismo documento JSON. Usa el learning.json real.
 */
class LearningTest {
    private val content = LearningContent.parse(File("../../frontend/data/learning.json").readText())
    private val now: Instant = Instant.parse("2026-10-04T10:00:00Z")

    private fun learning(state: LearningState = LearningState()) = Learning(content, state, ZoneOffset.UTC)

    private fun daysAgo(n: Long): Instant = now.minusSeconds(n * 86_400)

    private fun ex(id: String) = content.exercises.getValue(id)

    private fun master(l: Learning, concept: String, at: Instant = now) {
        content.byConcept.getValue(concept).forEach { l.recordAttempt(it, Result(true, null), at) }
    }

    @Test
    fun contenidoCompletoYCoherente() {
        assertEquals(22, content.concepts.size)
        assertEquals(content.concepts.keys, content.path.toSet())
        assertEquals(3, content.competencies.size)
        // Índice de la teoría: todas las áreas con sus conceptos, cada concepto una vez y en orden de ruta
        assertEquals(listOf("fundamentos", "programacion", "logica", "avanzado"), content.index.map { it.first.id })
        assertEquals(content.path, content.index.flatMap { it.second }.map { it.id }.sortedBy { content.path.indexOf(it) })
        assertEquals(content.concepts.size, content.index.sumOf { it.second.size })
        assertEquals(100, content.competencies.sumOf { it.weight })
        content.exercises.values.forEach { assertTrue(it.id, it.concept in content.concepts) }
        content.exercises.values.flatMap { it.errorsTested }.forEach { assertTrue(it, it in content.errors) }
    }

    @Test
    fun laRespuestaCorrectaDeCadaEjercicioSeAcepta() {
        content.exercises.values.filter(Grader::supported).forEach { e ->
            val reply = when (e.kind) {
                "choice" -> Reply(choice = e.answer)
                "output" -> Reply(text = e.expect.orEmpty() + "  \n")
                "fill" -> Reply(text = " ${e.accept.first()} ")
                "order" -> Reply(order = e.lines.indices.toList())
                else -> Reply(line = e.line)
            }
            assertTrue(e.id, Grader.grade(e, reply).ok)
        }
    }

    @Test
    fun losFallosDelatanElErrorTipico() {
        assertEquals(Result(false, "bucles.range-fin"), Grader.grade(ex("buc-01"), Reply(text = "2 3 4 5 6")))
        assertEquals(Result(false, "variables.asigna-compara"), Grader.grade(ex("var-04"), Reply(choice = 1)))
        assertEquals(Result(false, "acumuladores.producto-cero"), Grader.grade(ex("acu-02"), Reply(line = 3)))
        assertEquals("Coloca todas las líneas.", Grader.missing(ex("pse-05"), Reply(order = listOf(0))))
        assertFalse(Grader.supported(ex("acu-04")))
    }

    @Test
    fun dominioYErroresComoEnLaWeb() {
        val l = learning()
        assertEquals("nuevo", l.stats("bucles", now).status)
        l.recordAttempt(content.byConcept.getValue("bucles").first(), Result(true, null), now)
        assertEquals("aprendiendo", l.stats("bucles", now).status)
        master(l, "condicionales")
        assertEquals("dominado", l.stats("condicionales", now).status)
        // Un error activo impide «dominado» hasta acertar dos ejercicios que lo detectan
        l.recordAttempt(ex("con-01"), Result(false, "condicionales.orden-elif"), now)
        l.recordAttempt(ex("con-01"), Result(true, null), now)
        assertEquals("progreso", l.stats("condicionales", now).status)
        l.recordAttempt(ex("con-05"), Result(true, null), now)
        assertTrue(l.activeErrors(now).isEmpty())
        assertEquals("dominado", l.stats("condicionales", now).status)
    }

    @Test
    fun repasoEspaciado() {
        val l = learning()
        l.reviewConcept("bucles", 1.0, now)
        assertEquals(ConceptEntry(box = 1, due = "2026-10-05"), l.state.concepts["bucles"])
        l.reviewConcept("bucles", 0.9, now)
        assertEquals("2026-10-07", l.state.concepts.getValue("bucles").due)
        l.reviewConcept("bucles", 0.2, now)
        assertEquals(1, l.state.concepts.getValue("bucles").box)
        assertTrue(l.stats("bucles", Instant.parse("2026-10-05T09:00:00Z")).due)
    }

    @Test
    fun planDeHoyConLaMismaPrioridad() {
        assertEquals(listOf(PlanItem("learn", "algoritmos", "Siguiente concepto de la ruta.")), learning().todayPlan(now))

        val l = learning()
        master(l, "algoritmos", daysAgo(10))
        master(l, "variables", daysAgo(10))
        l.reviewConcept("variables", 1.0, daysAgo(10))
        l.recordAttempt(ex("tip-01"), Result(false, "tipos.texto-numero"), daysAgo(1))
        l.recordAttempt(ex("ope-02"), Result(true, null), daysAgo(1))
        val plan = l.todayPlan(now)
        assertEquals(listOf("review", "errors", "practice"), plan.take(3).map { it.type })
        assertEquals(listOf("variables", "tipos", "operadores"), plan.take(3).map { it.concept })
        assertTrue(plan[0].reason.contains("hace 10 días"))
    }

    @Test
    fun pideReforzarAntesDeAvanzar() {
        val l = learning()
        master(l, "algoritmos")
        master(l, "variables")
        l.recordAttempt(content.byConcept.getValue("tipos").first(), Result(false, null), now)
        assertEquals(
            listOf(PlanItem("reinforce", "tipos", "Necesitas reforzar Tipos de datos y conversiones antes de pasar a Operadores y expresiones.")),
            l.todayPlan(now),
        )
    }

    @Test
    fun seleccionSinCodigoYSinRepetirLoDominado() {
        val l = learning()
        val bucles = content.byConcept.getValue("bucles").filter(Grader::supported)
        bucles.take(2).forEach {
            l.recordAttempt(it, Result(true, null), daysAgo(3))
            l.recordAttempt(it, Result(true, null), daysAgo(2))
        }
        l.recordAttempt(ex("buc-05"), Result(false, "bucles.bucle-infinito"), daysAgo(1))
        val random = Random(3)
        val chosen = l.selectExercises(listOf("bucles", "acumuladores"), 4, now) { random.nextDouble() }
        assertEquals(4, chosen.size)
        assertTrue(chosen.none { it.kind == "code" })
        assertTrue(chosen.any { it.id == "buc-05" })
        assertTrue(chosen.none { it in bucles.take(2) })
        assertEquals(chosen.map { it.level }.sorted(), chosen.map { it.level })
    }

    @Test
    fun sesionConNuevoIntentoYResumen() {
        val l = learning()
        val session = LearnSession("Bucles", listOf("buc-01", "buc-06"))
        session.submit(l, Result(false, "bucles.range-fin"), now)
        assertEquals(3, session.queue.size)
        assertEquals("buc-01", session.queue[2].retryOf)
        session.next()
        session.submit(l, Result(true, null), now)
        session.next()
        session.submit(l, Result(true, null), now)
        session.next()
        assertTrue(session.done)
        assertEquals(mapOf("bucles" to (1 to 2)), session.finish(l, now))
        assertEquals(1, l.state.concepts.getValue("bucles").box)
    }

    @Test
    fun documentoCompatibleConLaWebYFusionSinPerdidas() {
        // Documento tal como lo guarda la web (toISOString con milisegundos)
        val web = """
            {"v":1,"ex":{"var-01":{"h":[false,true],"last":"2026-10-03T08:00:00.000Z","n":2},"<x>":{"h":[],"last":"2026-10-03T08:00:00.000Z","n":1}},
             "concepts":{"variables":{"box":2,"due":"2026-10-06","last":"2026-10-03T08:00:00.000Z","read":null,"placed":"2026-10-01T08:00:00.000Z"}},
             "errors":{"variables.orden-asignacion":{"n":3,"last":"2026-10-03T08:00:00.000Z","streak":1}},
             "log":[{"at":"2026-10-03T08:00:00.000Z","ex":"var-01","ok":true,"err":null}],
             "exams":[{"date":"2026-10-02T08:00:00.000Z","kind":"daw-completo","correct":5,"total":12,"seconds":900,"concepts":{}}]}
        """.trimIndent()
        val parsed = LearningState.fromJson(web)
        assertNull(parsed.ex["<x>"])
        assertEquals(listOf(false, true), parsed.ex.getValue("var-01").history)
        assertNotNull(parsed.concepts.getValue("variables").placed)

        val l = learning()
        l.recordAttempt(ex("buc-01"), Result(true, null), now)
        Learning.merge(l.state, JSONObject(web))
        assertEquals(setOf("buc-01", "var-01"), l.state.ex.keys)
        assertEquals(3, l.state.errors.getValue("variables.orden-asignacion").count)
        assertEquals(2, l.state.log.size)
        assertEquals(1, l.state.exams.length())
        // Ida y vuelta: lo que guarda la app lo vuelve a leer igual
        val again = LearningState.fromJson(l.state.toJson().toString())
        assertEquals(l.state.ex, again.ex)
        assertEquals(l.state.concepts, again.concepts)
        assertEquals(l.state.errors, again.errors)
        assertEquals(l.state.log, again.log)
        // Fusionar dos veces no duplica
        Learning.merge(l.state, JSONObject(web))
        assertEquals(2, l.state.log.size)
    }

    @Test
    fun teoriaSeparaCodigoYTablas() {
        val parts = splitTheory("Texto\n\n```\nx = 1\n  y\n```\nMás\n| a | b |\n|---|---|\n| 1 | 2 |\nFin")
        assertEquals(
            listOf(TheoryPart(false, "Texto"), TheoryPart(true, "x = 1\n  y"), TheoryPart(false, "Más"), TheoryPart(true, "| a | b |\n| 1 | 2 |"), TheoryPart(false, "Fin")),
            parts,
        )
        // Toda la teoría propia del contenido real se separa sin perder texto
        content.concepts.values.mapNotNull { it.theory }.forEach { theory -> assertTrue(splitTheory(theory).isNotEmpty()) }
    }

    @Test
    fun ordenDeLineasIgualQueEnLaWeb() {
        // Valores calculados con stableShuffle de frontend/js/learn/ui.js
        assertEquals(WEB_ORDER_PSE05, stableOrder("pse-05", 4))
        content.exercises.values.filter { it.kind == "order" }.forEach { e ->
            val order = stableOrder(e.id, e.lines.size)
            assertEquals(e.lines.indices.toSet(), order.toSet())
            assertFalse(e.id, order == e.lines.indices.toList())
        }
    }

    private companion object {
        val WEB_ORDER_PSE05 = listOf(1, 3, 2, 0)
    }
}
