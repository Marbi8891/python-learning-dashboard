package io.github.marbi8891.pld.ui

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalUriHandler
import androidx.compose.ui.semantics.LiveRegionMode
import androidx.compose.ui.semantics.liveRegion
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import io.github.marbi8891.pld.AppModel
import io.github.marbi8891.pld.BuildConfig
import io.github.marbi8891.pld.pcap.ApiException
import kotlinx.coroutines.launch

/**
 * Cuenta de la web en la app (ADR-0026): iniciar sesión, sincronizar y cerrar sesión.
 * La cuenta se crea en la web, donde se acepta la política de privacidad.
 */
@Composable
fun AccountPanel(model: AppModel) {
    val session = model.session
    val palette = LocalPalette.current
    val scope = rememberCoroutineScope()

    Panel {
        SectionTitle("Tu cuenta")
        if (session != null) {
            Text("Conectado como ${session.name} (${session.email}).", style = MaterialTheme.typography.bodyMedium)
            Text(
                model.lastSync?.let { "Última sincronización: $it. Se sincroniza sola al abrir y al salir de la app." }
                    ?: "Todavía sin sincronizar.",
                style = MaterialTheme.typography.bodySmall,
                color = palette.muted,
            )
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Button(onClick = { scope.launch { model.sync() } }, enabled = !model.syncing) {
                    Text(if (model.syncing) "Sincronizando…" else "Sincronizar ahora")
                }
                OutlinedButton(onClick = { model.logout("Sesión cerrada en este móvil. Tu progreso sigue aquí y en tu cuenta.") }) {
                    Text("Cerrar sesión")
                }
            }
        } else {
            LoginForm(model, onLogin = { email, password, onError ->
                scope.launch {
                    try {
                        model.login(email, password)
                    } catch (error: ApiException) {
                        onError(error.message.orEmpty())
                    }
                }
            })
        }
        if (model.syncMessage.isNotEmpty()) {
            Text(
                model.syncMessage,
                modifier = Modifier.semantics { liveRegion = LiveRegionMode.Polite },
                style = MaterialTheme.typography.bodyMedium,
                color = if (model.syncMessage.startsWith("Progreso")) palette.accent else palette.muted,
            )
        }
    }
}

@Composable
private fun LoginForm(model: AppModel, onLogin: (String, String, (String) -> Unit) -> Unit) {
    val uri = LocalUriHandler.current
    var email by remember { mutableStateOf(model.lastEmail) }
    var password by remember { mutableStateOf("") }
    var error by remember { mutableStateOf("") }
    var busy by remember { mutableStateOf(false) }
    val submit = {
        if (email.isBlank() || password.isEmpty()) {
            error = "Escribe tu email y tu contraseña."
        } else {
            busy = true
            error = ""
            onLogin(email, password) { message ->
                error = message
                busy = false
            }
        }
    }

    Text(
        "Inicia sesión con tu cuenta de la web para juntar tu progreso del móvil y del ordenador. " +
            "Sin cuenta, la app funciona igual: todo se guarda en el móvil.",
        style = MaterialTheme.typography.bodyMedium,
    )
    OutlinedTextField(
        value = email,
        onValueChange = { email = it },
        label = { Text("Email") },
        singleLine = true,
        enabled = !busy,
        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Email, imeAction = ImeAction.Next),
        modifier = Modifier.fillMaxWidth(),
    )
    OutlinedTextField(
        value = password,
        onValueChange = { password = it },
        label = { Text("Contraseña") },
        singleLine = true,
        enabled = !busy,
        visualTransformation = PasswordVisualTransformation(),
        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password, imeAction = ImeAction.Done),
        modifier = Modifier.fillMaxWidth(),
    )
    Button(onClick = submit, enabled = !busy, modifier = Modifier.fillMaxWidth()) {
        // El servidor gratuito puede tardar hasta un minuto en despertar
        Text(if (busy) "Conectando… (puede tardar un minuto)" else "Iniciar sesión")
    }
    if (error.isNotEmpty()) {
        Text(error, color = MaterialTheme.colorScheme.error, modifier = Modifier.semantics { liveRegion = LiveRegionMode.Assertive })
    }
    TextButton(onClick = { uri.openUri(BuildConfig.WEB_URL) }) { Text("¿No tienes cuenta? Créala en la web") }
}
