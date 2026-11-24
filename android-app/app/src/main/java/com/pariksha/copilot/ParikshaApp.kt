package com.pariksha.copilot

import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Chat
import androidx.compose.material.icons.filled.Language
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.outlined.Chat
import androidx.compose.material.icons.outlined.Language
import androidx.compose.material.icons.outlined.Settings
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.lifecycle.viewmodel.compose.viewModel
import com.pariksha.copilot.ui.screens.ChatScreen
import com.pariksha.copilot.ui.screens.SettingsScreen
import com.pariksha.copilot.ui.screens.WebPortalScreen

enum class AppTab(
    val label: String,
    val selectedIcon: ImageVector,
    val unselectedIcon: ImageVector
) {
    CHAT("AI Tutor", Icons.Filled.Chat, Icons.Outlined.Chat),
    WEB("Web Portal", Icons.Filled.Language, Icons.Outlined.Language),
    SETTINGS("Settings", Icons.Filled.Settings, Icons.Outlined.Settings)
}

@Composable
fun ParikshaApp(
    embeddedPort: Int = 8080,
    viewModel: ChatViewModel = viewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    var selectedTab by remember { mutableStateOf(AppTab.CHAT) }

    // Auto-navigate to settings if no API key
    LaunchedEffect(uiState.isApiKeyConfigured) {
        if (!uiState.isApiKeyConfigured && selectedTab == AppTab.CHAT) {
            selectedTab = AppTab.SETTINGS
        }
    }

    Scaffold(
        bottomBar = {
            NavigationBar(
                containerColor = MaterialTheme.colorScheme.surface,
                contentColor = MaterialTheme.colorScheme.onSurface
            ) {
                AppTab.entries.forEach { tab ->
                    val selected = selectedTab == tab
                    NavigationBarItem(
                        selected = selected,
                        onClick = { selectedTab = tab },
                        icon = {
                            Icon(
                                imageVector = if (selected) tab.selectedIcon else tab.unselectedIcon,
                                contentDescription = tab.label
                            )
                        },
                        label = { Text(tab.label) },
                        colors = NavigationBarItemDefaults.colors(
                            selectedIconColor = MaterialTheme.colorScheme.primary,
                            selectedTextColor = MaterialTheme.colorScheme.primary,
                            indicatorColor = MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.3f)
                        )
                    )
                }
            }
        }
    ) { innerPadding ->
        Box(modifier = Modifier.padding(innerPadding)) {
            when (selectedTab) {
                AppTab.CHAT -> ChatScreen(
                    uiState = uiState,
                    onSendMessage = viewModel::sendMessage,
                    onClearChat = viewModel::clearChat,
                    onDismissError = viewModel::clearError,
                    onNavigateToSettings = { selectedTab = AppTab.SETTINGS }
                )
                AppTab.WEB -> WebPortalScreen(
                    serverUrl = uiState.serverUrl,
                    embeddedPort = embeddedPort
                )
                AppTab.SETTINGS -> SettingsScreen(
                    uiState = uiState,
                    onSaveApiKey = viewModel::saveApiKey,
                    onClearApiKey = viewModel::clearApiKey,
                    onSaveServerUrl = viewModel::saveServerUrl,
                    onSelectModel = viewModel::saveSelectedModel,
                    onSaveUserName = viewModel::saveUserName,
                    onSaveTargetExam = viewModel::saveTargetExam
                )
            }
        }
    }
}
