
package com.nora.tunnel.ui.theme; import androidx.compose.material3.*; import androidx.compose.runtime.Composable; import androidx.compose.ui.graphics.Color
private val s=darkColorScheme(primary=Color(0xFF7C4DFF), background=Color(0xFF0A0E1A)); @Composable fun NoraTheme(c: @Composable ()->Unit){ MaterialTheme(colorScheme=s, content=c)}
