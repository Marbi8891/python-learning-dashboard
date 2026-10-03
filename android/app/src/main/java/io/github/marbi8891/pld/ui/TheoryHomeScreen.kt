package io.github.marbi8891.pld.ui

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.semantics.heading
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.unit.dp
import io.github.marbi8891.pld.AppModel

@Composable
fun TheoryHomeScreen(
    model: AppModel,
    onOpen: (String) -> Unit,
    onBack: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val units = model.units
    Scaffold(containerColor = MaterialTheme.colorScheme.background) { padding ->
        Column(
            modifier.fillMaxSize().padding(padding).verticalScroll(rememberScrollState()).padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp),
        ) {
            TextButton(onClick = onBack) { Text("← Volver a Aprender") }
            Text("Teoría", style = MaterialTheme.typography.headlineLarge, modifier = Modifier.semantics { heading() })
            Text(
                "Estudia cada tema con explicación, ejemplos y comprobaciones antes de pasar a los ejercicios.",
                color = LocalPalette.current.muted,
            )
            units.forEachIndexed { index, unit ->
                val lesson = model.content[unit.slug]
                Panel {
                    Text("TEMA ${index + 1}", style = MaterialTheme.typography.labelMedium, color = LocalPalette.current.muted)
                    Text(unit.title, style = MaterialTheme.typography.titleLarge)
                    Text("Explicación · ejemplo · ejercicio · mini-quiz", color = LocalPalette.current.muted)
                    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        Button(onClick = { onOpen(unit.slug) }, modifier = Modifier.weight(1f), enabled = lesson != null) {
                            Text("Estudiar")
                        }
                        OutlinedButton(onClick = { onOpen(unit.slug) }, modifier = Modifier.weight(1f), enabled = lesson != null) {
                            Text("Repasar")
                        }
                    }
                }
            }
        }
    }
}
