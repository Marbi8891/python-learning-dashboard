package io.github.marbi8891.pld.ui

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Typography
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.Immutable
import androidx.compose.runtime.staticCompositionLocalOf
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight

/* Los mismos tokens que la web (frontend/css/base.css): tinta, marfil, dorado y verde. */

@Immutable
data class Palette(
    val accent: Color,
    val danger: Color,
    val muted: Color,
    val codeBg: Color,
    val codeText: Color,
    val codeInline: Color,
    val streak: Color,
)

private val DarkPalette = Palette(
    accent = Color(0xFF4FD18B),
    danger = Color(0xFFF87171),
    muted = Color(0xFFA9A498),
    codeBg = Color(0xFF0A0B0E),
    codeText = Color(0xFFE6EBF5),
    codeInline = Color(0xFF86E0B0),
    streak = Color(0xFFF4A66A),
)

// Los bloques de código son siempre oscuros, también en el tema claro (como en la web)
private val LightPalette = DarkPalette.copy(
    accent = Color(0xFF166534),
    danger = Color(0xFFB91C1C),
    muted = Color(0xFF57534A),
    codeInline = Color(0xFF0F6B4A),
    streak = Color(0xFFB4410C),
)

private val DarkColors = darkColorScheme(
    primary = Color(0xFFD4AF6A),
    onPrimary = Color(0xFF1A1407),
    secondary = Color(0xFF4FD18B),
    onSecondary = Color(0xFF06210F),
    background = Color(0xFF0C0D10),
    onBackground = Color(0xFFEEEAE2),
    surface = Color(0xFF14161B),
    onSurface = Color(0xFFEEEAE2),
    surfaceVariant = Color(0xFF1B1E24),
    onSurfaceVariant = Color(0xFFA9A498),
    outline = Color(0xFF2A2D35),
    error = Color(0xFFF87171),
)

private val LightColors = lightColorScheme(
    primary = Color(0xFF1B1A17),
    onPrimary = Color(0xFFFBF8F1),
    secondary = Color(0xFF166534),
    onSecondary = Color(0xFFFFFFFF),
    background = Color(0xFFF7F4EC),
    onBackground = Color(0xFF1B1A17),
    surface = Color(0xFFFFFDF8),
    onSurface = Color(0xFF1B1A17),
    surfaceVariant = Color(0xFFEFEADF),
    onSurfaceVariant = Color(0xFF57534A),
    outline = Color(0xFFE2DCCD),
    error = Color(0xFFB91C1C),
)

val LocalPalette = staticCompositionLocalOf { DarkPalette }

private val Serif = FontFamily.Serif

private val AppTypography = Typography().let {
    it.copy(
        displaySmall = it.displaySmall.copy(fontFamily = Serif, fontWeight = FontWeight.Medium),
        headlineMedium = it.headlineMedium.copy(fontFamily = Serif, fontWeight = FontWeight.Medium),
        headlineSmall = it.headlineSmall.copy(fontFamily = Serif, fontWeight = FontWeight.Medium),
        titleLarge = it.titleLarge.copy(fontFamily = Serif),
    )
}

@Composable
fun PldTheme(content: @Composable () -> Unit) {
    val dark = isSystemInDarkTheme()
    CompositionLocalProvider(LocalPalette provides if (dark) DarkPalette else LightPalette) {
        MaterialTheme(colorScheme = if (dark) DarkColors else LightColors, typography = AppTypography, content = content)
    }
}
