package com.pariksha.copilot.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

// Scholarly Exam Portal Theme Colors (Matching Web Portal)
val Slate950 = Color(0xFF0A0F1D) // Deep Midnight Background
val Slate900 = Color(0xFF0F172A) // Surface Card Background
val Slate800 = Color(0xFF1E293B) // Card Border / Elevated Surface
val Slate700 = Color(0xFF334155) // Subtle Borders
val Slate600 = Color(0xFF475569) // Outline / Disabled
val Slate500 = Color(0xFF64748B) // Muted Icon
val Slate400 = Color(0xFF94A3B8) // Secondary Text
val Slate300 = Color(0xFFCBD5E1) // Soft Text
val Slate200 = Color(0xFFE2E8F0) // Subtle Header
val Slate100 = Color(0xFFF1F5F9) // Primary High Contrast Text
val Slate50  = Color(0xFFF8FAFC) // Bright White Accent

val Amber500 = Color(0xFFF59E0B) // Topper Gold Accent
val Amber400 = Color(0xFFFBBF24) // Bright Gold Accent
val Amber600 = Color(0xFFD97706) // Darker Gold Container

val Blue600 = Color(0xFF2563EB)  // Primary Govt Brand Blue
val Blue500 = Color(0xFF3B82F6)  // Vibrant Blue
val Blue400 = Color(0xFF60A5FA)  // Soft Blue
val Blue900 = Color(0xFF1E3A8A)  // Dark Blue Container

val Emerald500 = Color(0xFF10B981) // Success / AIR Badges
val Emerald400 = Color(0xFF34D399) // Soft Green
val Rose500 = Color(0xFFF43F5E)    // High Priority / Alert
val Rose400 = Color(0xFFFB7185)    // Soft Red
val Purple500 = Color(0xFF8B5CF6)  // Flashcard AI Badge
val Purple400 = Color(0xFFA78BFA)  // Soft Purple

// Backward compatibility aliases for components
val PrimaryBlue = Blue600
val PrimaryBlueDark = Blue900
val AccentGold = Amber500
val SurfaceDark = Slate950
val CardDark = Slate900
val Success = Emerald500
val Warning = Amber500
val Error = Rose500

private val ScholarlyDarkColorScheme = darkColorScheme(
    primary = Amber500,
    onPrimary = Slate950,
    primaryContainer = Amber600,
    onPrimaryContainer = Color.White,
    secondary = Blue500,
    onSecondary = Color.White,
    secondaryContainer = Blue900,
    onSecondaryContainer = Slate100,
    tertiary = Emerald500,
    background = Slate950,
    onBackground = Slate100,
    surface = Slate900,
    onSurface = Slate100,
    surfaceVariant = Slate800,
    onSurfaceVariant = Slate400,
    outline = Slate700,
    error = Rose500,
    onError = Color.White
)

private val ScholarlyLightColorScheme = lightColorScheme(
    primary = Blue600,
    onPrimary = Color.White,
    primaryContainer = Amber500,
    onPrimaryContainer = Slate950,
    secondary = Amber600,
    onSecondary = Color.White,
    background = Color(0xFFF8FAFC),
    onBackground = Color(0xFF0F172A),
    surface = Color.White,
    onSurface = Color(0xFF0F172A),
    surfaceVariant = Color(0xFFF1F5F9),
    onSurfaceVariant = Slate600,
    outline = Color(0xFFCBD5E1),
    error = Rose500,
    onError = Color.White
)

@Composable
fun ParikshaTheme(
    darkTheme: Boolean = true, // Default to deep scholarly dark mode
    content: @Composable () -> Unit
) {
    val colorScheme = if (darkTheme) ScholarlyDarkColorScheme else ScholarlyLightColorScheme

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography(),
        content = content
    )
}
