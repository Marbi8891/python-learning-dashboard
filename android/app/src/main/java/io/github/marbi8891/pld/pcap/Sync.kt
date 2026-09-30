package io.github.marbi8891.pld.pcap

import org.json.JSONArray
import org.json.JSONObject
import java.io.IOException
import java.net.HttpURLConnection
import java.net.URL
import java.net.URLEncoder

/*
 * Cuenta y sincronización de la app (ADR-0026). Sin dependencias de Android para poder probarlo:
 * la red se inyecta con [Http]. Usa la misma API que la web: login OAuth2, /api/pcap-state y
 * /api/course-state/<curso>. Cada lado fusiona sin perder nada ([PcapState.merge]) y guarda el
 * resultado entero, así que da igual quién sincronice primero.
 */

data class HttpResponse(val code: Int, val body: String)

/** Una petición HTTP. En la app es [UrlConnectionHttp]; en los tests, un falso. */
fun interface Http {
    fun send(method: String, url: String, token: String?, contentType: String?, body: String?): HttpResponse
}

/** Error que se puede enseñar tal cual. [code] 0 = sin conexión; 401 = sesión caducada. */
class ApiException(val code: Int, message: String) : Exception(message)

/** Un evento de «Actividad de la cuenta» (ADR-0025): tipo, fecha ISO y dispositivo aproximado. */
data class ActivityItem(val kind: String, val createdAt: String, val device: String) {
    val label: String get() = LABELS[kind] ?: kind

    companion object {
        val LABELS = mapOf(
            "login" to "Inicio de sesión",
            "login_failed" to "Intento con contraseña incorrecta",
            "password_changed" to "Contraseña cambiada",
            "password_reset" to "Contraseña restablecida por email",
            "logout_all" to "Sesión cerrada en todos los dispositivos",
            "name_changed" to "Nombre cambiado",
        )
    }
}

/** Sesión guardada en el móvil: el token caduca en 1 hora (el servidor no da tokens de refresco). */
data class Session(val token: String, val email: String, val name: String)

class AccountApi(baseUrl: String, private val http: Http) {
    private val base = baseUrl.trimEnd('/')

    fun login(email: String, password: String): Session {
        val form = "username=${enc(email.trim())}&password=${enc(password)}"
        val token = call("POST", "/api/auth/login", null, "application/x-www-form-urlencoded", form, login = true)
            .getString("access_token")
        val me = call("GET", "/api/users/me", token)
        return Session(token, me.getString("email"), me.getString("display_name"))
    }

    /** Estado guardado en la cuenta; `{}` si todavía no hay nada. */
    fun pull(token: String, course: String): JSONObject = call("GET", path(course), token).optJSONObject("data") ?: JSONObject()

    fun push(token: String, course: String, data: JSONObject) {
        call("PUT", path(course), token, "application/json", JSONObject().put("data", data).toString())
    }

    /* ---------- Perfil y seguridad (ADR-0027) ---------- */

    /** Cambia el nombre visible. Devuelve el nombre guardado. */
    fun rename(token: String, name: String): String =
        call("PATCH", "/api/users/me", token, "application/json", JSONObject().put("display_name", name).toString())
            .getString("display_name")

    /** Cambia la contraseña. El servidor cierra las demás sesiones y devuelve un token nuevo para esta. */
    fun changePassword(token: String, current: String, new: String): String {
        val body = JSONObject().put("current_password", current).put("new_password", new).toString()
        return call("POST", "/api/users/me/password", token, "application/json", body).getString("access_token")
    }

    fun activity(token: String): List<ActivityItem> {
        val list = callArray("/api/users/me/activity", token)
        return (0 until list.length()).map { i ->
            val e = list.getJSONObject(i)
            ActivityItem(e.getString("kind"), e.getString("created_at"), e.optString("device"))
        }
    }

    private fun callArray(path: String, token: String): JSONArray {
        val response = try {
            http.send("GET", base + path, token, null, null)
        } catch (error: IOException) {
            throw ApiException(0, OFFLINE)
        }
        if (response.code in 200..299) return runCatching { JSONArray(response.body) }.getOrElse { JSONArray() }
        throw ApiException(response.code, message(response, login = false))
    }

    private fun path(course: String) = if (course == PCAP) "/api/pcap-state" else "/api/course-state/$course"

    private fun call(
        method: String,
        path: String,
        token: String?,
        contentType: String? = null,
        body: String? = null,
        login: Boolean = false,
    ): JSONObject {
        val response = try {
            http.send(method, base + path, token, contentType, body)
        } catch (error: IOException) {
            throw ApiException(0, OFFLINE)
        }
        if (response.code in 200..299) return runCatching { JSONObject(response.body) }.getOrElse { JSONObject() }
        throw ApiException(response.code, message(response, login))
    }

    private fun message(response: HttpResponse, login: Boolean): String {
        val detail = runCatching { JSONObject(response.body).opt("detail") }.getOrNull()
        return when {
            response.code == 401 && !login -> "Tu sesión ha caducado. Vuelve a iniciar sesión."
            detail is String -> detail
            detail is JSONArray -> "Revisa el email y la contraseña."
            response.code >= 500 -> "El servidor no responde bien ahora mismo (error ${response.code}). Prueba en un rato."
            else -> "Error ${response.code}"
        }
    }

    companion object {
        const val PCAP = "pcap"
        private const val OFFLINE = "No hay conexión con el servidor. Comprueba internet y vuelve a probar."

        private fun enc(value: String): String = URLEncoder.encode(value, "UTF-8")
    }
}

object Sync {
    /**
     * Fusiona en [local] lo que haya en la cuenta. Devuelve el documento que hay que subir:
     * el PCAP lleva también el progreso compartido de la app (XP, racha, vidas); los cursos, no.
     */
    fun merge(local: PcapState, remote: JSONObject, isPcap: Boolean): JSONObject {
        local.merge(PcapState.fromJson(remote.toString()))
        val merged = local.toJson(withApp = isPcap)
        // Campos que esta versión de la app no conoce (los añada la web en el futuro): se conservan
        remote.keys().forEach { key -> if (!merged.has(key)) merged.put(key, remote.get(key)) }
        return merged
    }
}

/** [Http] con HttpURLConnection. Tiempos generosos: el servidor gratuito tarda en despertar. */
class UrlConnectionHttp(private val userAgent: String) : Http {
    override fun send(method: String, url: String, token: String?, contentType: String?, body: String?): HttpResponse {
        val connection = URL(url).openConnection() as HttpURLConnection
        try {
            connection.requestMethod = method
            connection.connectTimeout = TIMEOUT_MS
            connection.readTimeout = TIMEOUT_MS
            connection.setRequestProperty("User-Agent", userAgent)
            connection.setRequestProperty("Accept", "application/json")
            token?.let { connection.setRequestProperty("Authorization", "Bearer $it") }
            if (body != null) {
                connection.doOutput = true
                connection.setRequestProperty("Content-Type", "$contentType; charset=utf-8")
                connection.outputStream.use { it.write(body.toByteArray(Charsets.UTF_8)) }
            }
            val code = connection.responseCode
            val stream = if (code >= 400) connection.errorStream else connection.inputStream
            val text = stream?.bufferedReader(Charsets.UTF_8)?.use { it.readText() }.orEmpty()
            return HttpResponse(code, text)
        } finally {
            connection.disconnect()
        }
    }

    private companion object {
        const val TIMEOUT_MS = 70_000
    }
}
