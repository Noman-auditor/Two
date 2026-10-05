
package com.nora.tunnel.ui.navigation; import androidx.compose.runtime.Composable; import androidx.navigation.NavHostController; import androidx.navigation.compose.NavHost; import androidx.navigation.compose.composable; import com.nora.tunnel.ui.screens.home.HomeScreen
@Composable fun NoraNavHost(n: NavHostController){ NavHost(n, startDestination="home"){ composable("home"){ HomeScreen() } } }
