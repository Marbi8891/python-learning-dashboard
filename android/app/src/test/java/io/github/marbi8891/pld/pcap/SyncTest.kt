package io.github.marbi8891.pld.pcap

import org.json.JSONObject
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.IOException

/** Cuenta y sincronización (ADR-0026) contra un servidor falso con las mismas respuestas que la API. */
class SyncTest {
    private class Call(val method: String, val url: String, val token: String?, val contentType: String?, val body: String?)

    private class FakeServer(private val routes: (Call) -> HttpResponse) : Http {
        val calls = mutableListOf<Call>()

        override fun send(method: String, url: String, token: String?, contentType: String?, body: String?): HttpResponse {
            val call = Call(method, url, token, contentType, body)
            calls += call
            return routes(call)
        }
    }

    @Test
    fun iniciaSesionConElFormularioOAuth2YLeeElNombre() {
        val server = FakeServer { call ->
            when {
                call.url.endsWith("/api/auth/login") -> HttpResponse(200, """{"access_token":"tok","token_type":"bearer"}""")
                call.url.endsWith("/api/users/me") && call.token == "tok" ->
                    HttpResponse(200, """{"id":1,"email":"ana@example.com","display_name":"Ana","created_at":"2026-09-30T10:00:00Z"}""")
                else -> HttpResponse(404, "{}")
            }
        }
        val session = AccountApi("https://api.test/", server).login(" ana@example.com ", "contraseña & más")
        assertEquals(Session("tok", "ana@example.com", "Ana"), session)
        val login = server.calls.first()
        assertEquals("https://api.test/api/auth/login", login.url)
        assertEquals("application/x-www-form-urlencoded", login.contentType)
        assertEquals("username=ana%40example.com&password=contrase%C3%B1a+%26+m%C3%A1s", login.body)
        assertNull(login.token)
    }

    @Test
    fun losErroresSeExplicanEnEspanol() {
        fun failing(code: Int, body: String) = AccountApi("https://api.test", FakeServer { HttpResponse(code, body) })

        val wrong = runCatching { failing(401, """{"detail":"Email o contraseña incorrectos"}""").login("a@b.c", "x") }
        assertEquals("Email o contraseña incorrectos", wrong.exceptionOrNull()!!.message)

        val expired = runCatching { failing(401, """{"detail":"Sesión no válida o caducada"}""").pull("tok", "sql") }
        val error = expired.exceptionOrNull() as ApiException
        assertEquals(401, error.code)
        assertEquals("Tu sesión ha caducado. Vuelve a iniciar sesión.", error.message)

        val invalid = runCatching { failing(422, """{"detail":[{"loc":["body","username"]}]}""").login("", "") }
        assertEquals("Revisa el email y la contraseña.", invalid.exceptionOrNull()!!.message)
        val down = runCatching { failing(502, "Bad gateway").pull("tok", "pcap") }
        assertTrue(down.exceptionOrNull()!!.message!!.contains("error 502"))

        val offline = AccountApi("https://api.test", Http { _, _, _, _, _ -> throw IOException("sin red") })
        val noNet = runCatching { offline.pull("tok", "pcap") }.exceptionOrNull() as ApiException
        assertEquals(0, noNet.code)
    }

    @Test
    fun cadaCursoTieneSuRutaYElPcapLaSuya() {
        val server = FakeServer { HttpResponse(200, """{"data":{},"updated_at":null}""") }
        val api = AccountApi("https://api.test", server)
        assertEquals(0, api.pull("tok", "pcap").length())
        api.push("tok", "sql", JSONObject().put("bestCombo", 3))
        assertEquals("https://api.test/api/pcap-state", server.calls[0].url)
        assertEquals("https://api.test/api/course-state/sql", server.calls[1].url)
        assertEquals("PUT", server.calls[1].method)
        assertEquals(3, JSONObject(server.calls[1].body!!).getJSONObject("data").getInt("bestCombo"))
    }

    @Test
    fun laFusionNoPierdeNadaDeNingunLado() {
        val local = PcapState().apply {
            recordAnswer("prog-01", true)
            examDate = "2026-06-10"
        }
        val remote = JSONObject(
            """{"answers":{"prog-02":[false,true]},"exams":[{"date":"2026-09-29T10:00:00.000Z","correct":20,"total":30,"score":67,"seconds":1800,"blocks":{}}],
               "plan":{"examDate":null,"dailyGoal":30},"futuro":{"campo":"que la app no conoce"}}""",
        )
        val merged = Sync.merge(local, remote, isPcap = false)

        assertEquals(listOf(true), local.answers["prog-01"])
        assertEquals(listOf(false, true), local.answers["prog-02"])
        assertEquals(1, local.exams.size)
        assertEquals(30, local.dailyGoal) // la meta diaria de la web se conserva
        assertEquals("2026-06-10", merged.getJSONObject("plan").getString("examDate"))
        assertEquals(30, merged.getJSONObject("plan").getInt("dailyGoal"))
        assertEquals("que la app no conoce", merged.getJSONObject("futuro").getString("campo"))
        assertFalse(merged.has("app")) // el progreso compartido solo viaja con el PCAP
        assertTrue(Sync.merge(PcapState(), JSONObject(), isPcap = true).has("app"))
    }
}
