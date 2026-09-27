package io.github.marbi8891.pld.ui

import androidx.compose.foundation.border
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.selection.selectable
import androidx.compose.foundation.selection.selectableGroup
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.RadioButton
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.heading
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.AnnotatedString
import androidx.compose.ui.text.SpanStyle
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.buildAnnotatedString
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.withStyle
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import io.github.marbi8891.pld.pcap.Span
import io.github.marbi8891.pld.pcap.parseInline

val CardShape = RoundedCornerShape(12.dp)

/** Texto con `código`, **negrita** y *cursiva*, como en la web. */
@Composable
fun rich(text: String): AnnotatedString {
    val codeColor = LocalPalette.current.codeInline
    return buildAnnotatedString {
        for (span in parseInline(text)) {
            val style = when (span.style) {
                Span.Style.PLAIN -> null
                Span.Style.CODE -> SpanStyle(fontFamily = FontFamily.Monospace, color = codeColor)
                Span.Style.BOLD -> SpanStyle(fontWeight = FontWeight.Bold)
                Span.Style.ITALIC -> SpanStyle(fontStyle = FontStyle.Italic)
            }
            if (style == null) append(span.text) else withStyle(style) { append(span.text) }
        }
    }
}

@Composable
fun RichText(text: String, modifier: Modifier = Modifier, style: TextStyle = MaterialTheme.typography.bodyLarge, color: Color = Color.Unspecified) {
    Text(rich(text), modifier = modifier, style = style, color = color)
}

@Composable
fun SectionTitle(text: String, modifier: Modifier = Modifier) {
    Text(
        text,
        modifier = modifier.semantics { heading() },
        style = MaterialTheme.typography.headlineSmall,
        color = MaterialTheme.colorScheme.onBackground,
    )
}

@Composable
fun Eyebrow(text: String) {
    Text(text.uppercase(), style = MaterialTheme.typography.labelMedium, color = MaterialTheme.colorScheme.primary, letterSpacing = 1.5.sp)
}

/** Bloque de código: siempre oscuro y con desplazamiento horizontal para no partir las líneas. */
@Composable
fun CodeBlock(source: String, modifier: Modifier = Modifier) {
    val palette = LocalPalette.current
    Surface(color = palette.codeBg, shape = RoundedCornerShape(8.dp), modifier = modifier.fillMaxWidth()) {
        Text(
            source,
            modifier = Modifier
                .horizontalScroll(rememberScrollState())
                .padding(14.dp)
                .semantics { contentDescription = "Código: $source" },
            fontFamily = FontFamily.Monospace,
            fontSize = 14.sp,
            lineHeight = 20.sp,
            color = palette.codeText,
            softWrap = false,
        )
    }
}

/** Barra de progreso de 0 a 1 (null = sin datos). */
@Composable
fun Meter(value: Double?, label: String, color: Color = MaterialTheme.colorScheme.secondary) {
    val pct = ((value ?: 0.0) * 100).toInt()
    LinearProgressIndicator(
        progress = { (value ?: 0.0).toFloat() },
        modifier = Modifier
            .fillMaxWidth()
            .semantics { contentDescription = "$label: $pct %" },
        color = color,
        trackColor = MaterialTheme.colorScheme.outline,
    )
}

/** Tarjeta con borde fino, como las de la web. */
@Composable
fun Panel(modifier: Modifier = Modifier, borderColor: Color = MaterialTheme.colorScheme.outline, content: @Composable () -> Unit) {
    Surface(
        modifier = modifier
            .fillMaxWidth()
            .border(1.dp, borderColor, CardShape),
        shape = CardShape,
        color = MaterialTheme.colorScheme.surface,
    ) {
        Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) { content() }
    }
}

/** Selector del idioma de las preguntas (el examen real está en inglés). */
@Composable
fun LangSwitch(lang: String, onChange: (String) -> Unit) {
    Column {
        Text("Idioma de las preguntas", style = MaterialTheme.typography.labelLarge, color = MaterialTheme.colorScheme.onSurfaceVariant)
        Column(Modifier.selectableGroup()) {
            listOf("es" to "Español", "en" to "English (como el examen)").forEach { (code, label) ->
                Row(
                    Modifier
                        .selectable(selected = lang == code, onClick = { onChange(code) }, role = Role.RadioButton)
                        .padding(vertical = 4.dp, horizontal = 2.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    RadioButton(selected = lang == code, onClick = null)
                    Text(label, Modifier.padding(start = 4.dp), style = MaterialTheme.typography.bodyMedium)
                }
            }
        }
    }
}
