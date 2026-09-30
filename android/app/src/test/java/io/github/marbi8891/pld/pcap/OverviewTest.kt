package io.github.marbi8891.pld.pcap

import org.json.JSONObject
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.File
import java.time.Instant
import java.time.LocalDate

/** «Mi cuenta» en la app (ADR-0027): mismas cuentas que la web y llamadas de perfil y seguridad. */
class OverviewTest {
    private val sql = Bank.parse(File("../../frontend/data/courses/sql/bank.json").readText())
    private val today = LocalDate.parse("2026-09-30")
    private val now = Instant.parse("2026-09-30T10:00:00Z")

    @Test
    fun cursoSinEmpezarProponeElPrimerBloqueYNoTieneFecha() {
        val o = Overview.of(PcapState(), sql, isPcap = false, today = today)
        assertEquals(0, o.score)
        assertEquals(sql.exam.blocks.first(), o.focus)
        assertNull(o.focusRate)
        assertNull(o.daysLeft)
        assertEquals("Sin fecha", Overview.countdown(o.daysLeft))
        assertFalse(o.certificate)
    }

    @Test
    fun elTemaMasFlojoLosRepasosYLaCuentaAtras() {
        val state = PcapState().apply { examDate = "2026-10-20" }
        val ud1 = sql.questions.filter { it.block == "bd-ud1" }.take(2)
        val ud2 = sql.questions.filter { it.block == "bd-ud2" }.take(2)
        ud1.forEach { state.recordAnswer(it.id, false, today.minusDays(3), now) } // repaso: mañana tras fallar → atrasado
        ud2.forEach { state.recordAnswer(it.id, true, today, now) }
        val o = Overview.of(state, sql, isPcap = false, today = today)
        assertEquals("bd-ud1", o.focus!!.slug)
        assertEquals(0.0, o.focusRate!!, 1e-9)
        assertEquals(2, o.due)
        assertEquals(20L, o.daysLeft)
        assertEquals("Faltan 20 días", Overview.countdown(o.daysLeft))
        assertEquals("Es mañana", Overview.countdown(1))
        assertEquals("¡Es hoy!", Overview.countdown(0))
        assertEquals("Ya pasó", Overview.countdown(-2))
    }

    @Test
    fun certificadoConLasReglasDeLaWeb() {
        val state = PcapState()
        sql.exam.blocks.forEach { b -> sql.questions.filter { it.block == b.slug }.take(5).forEach { state.recordAnswer(it.id, true, today, now) } }
        val o = Overview.of(state, sql, isPcap = false, today = today)
        assertEquals(100, o.score)
        assertTrue(o.certificate)
        // En el PCAP hace falta un simulacro aprobado
        val pcap = Bank.parse(File("../../frontend/data/pcap.json").readText())
        val s = PcapState()
        assertFalse(Overview.of(s, pcap, isPcap = true, today = today).certificate)
        s.exams += ExamResult("2026-09-30T10:00:00.000Z", 30, 40, 75, 3000, emptyMap())
        assertTrue(Overview.of(s, pcap, isPcap = true, today = today).certificate)
    }

    @Test
    fun logrosCalculadosConElProgreso() {
        val state = PcapState()
        val empty = Achievements.of(AppProgress(), listOf(state to Overview.of(state, sql, false, today)), today)
        assertEquals(8, empty.size)
        assertTrue(empty.none { it.done })
        state.exams += ExamResult("2026-09-30T10:00:00.000Z", 20, 30, 67, 1800, emptyMap())
        val after = Achievements.of(AppProgress(), listOf(state to Overview.of(state, sql, false, today)), today)
        assertTrue(after.first { it.name == "Aprobado" }.done)
    }

    @Test
    fun perfilYSeguridadContraLaApi() {
        val sent = mutableListOf<Triple<String, String, String?>>()
        val api = AccountApi("https://api.test", Http { method, url, _, _, body ->
            sent += Triple(method, url, body)
            when {
                url.endsWith("/api/users/me") -> HttpResponse(200, """{"display_name":"Ana María"}""")
                url.endsWith("/password") && JSONObject(body!!).getString("current_password") == "buena" ->
                    HttpResponse(200, """{"access_token":"nuevo"}""")
                url.endsWith("/password") -> HttpResponse(403, """{"detail":"Contraseña actual incorrecta"}""")
                url.endsWith("/activity") ->
                    HttpResponse(200, """[{"kind":"login","created_at":"2026-09-30T10:00:00Z","device":"Android · App"},{"kind":"raro","created_at":"2026-09-29T10:00:00Z","device":""}]""")
                else -> HttpResponse(404, "{}")
            }
        })
        assertEquals("Ana María", api.rename("tok", "Ana María"))
        assertEquals("PATCH", sent[0].first)
        assertEquals("nuevo", api.changePassword("tok", "buena", "tortuga-azul-en-bici"))
        val wrong = runCatching { api.changePassword("tok", "mala", "x") }.exceptionOrNull() as ApiException
        assertEquals(403, wrong.code)
        assertEquals("Contraseña actual incorrecta", wrong.message)
        val events = api.activity("tok")
        assertEquals("Inicio de sesión", events[0].label)
        assertEquals("Android · App", events[0].device)
        assertEquals("raro", events[1].label) // un tipo nuevo no rompe la app
    }
}
