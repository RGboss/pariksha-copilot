package com.pariksha.copilot

import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Chat
import androidx.compose.material.icons.filled.Dashboard
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.Style
import androidx.compose.material.icons.outlined.Chat
import androidx.compose.material.icons.outlined.Dashboard
import androidx.compose.material.icons.outlined.Person
import androidx.compose.material.icons.outlined.Style
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.pariksha.copilot.ui.screens.AuthScreen
import com.pariksha.copilot.ui.screens.ChatScreen
import com.pariksha.copilot.ui.screens.FlashcardsScreen
import com.pariksha.copilot.ui.screens.SettingsScreen
import com.pariksha.copilot.ui.screens.StudyDeskScreen
import com.pariksha.copilot.ui.theme.*

enum class AppTab(
    val label: String,
    val selectedIcon: ImageVector,
    val unselectedIcon: ImageVector
) {
    DESK("Study Desk", Icons.Filled.Dashboard, Icons.Outlined.Dashboard),
    CHAT("AI Tutor", Icons.Filled.Chat, Icons.Outlined.Chat),
    CARDS("Flashcards", Icons.Filled.Style, Icons.Outlined.Style),
    SETTINGS("Profile", Icons.Filled.Person, Icons.Outlined.Person)
}

@Composable
fun ParikshaApp(
    embeddedPort: Int = 8080,
    viewModel: ChatViewModel = viewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    var selectedTab by remember { mutableStateOf(AppTab.DESK) }

    // If user is not logged in, enforce the Aspirant Authentication Gate
    if (!uiState.isLoggedIn) {
        AuthScreen(
            isLoading = uiState.isGenerating,
            errorMessage = uiState.errorMessage,
            onLogin = viewModel::login,
            onSignup = viewModel::signup,
            onDemoLogin = viewModel::demoLogin,
            onDismissError = viewModel::clearError
        )
        return
    }

    // Authenticated Aspirant Experience
    Scaffold(
        bottomBar = {
            NavigationBar(
                containerColor = Slate900,
                contentColor = Slate300,
                tonalElevation = 8.dp
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
                        label = {
                            Text(
                                tab.label,
                                style = MaterialTheme.typography.labelSmall
                            )
                        },
                        colors = NavigationBarItemDefaults.colors(
                            selectedIconColor = Amber400,
                            selectedTextColor = Amber400,
                            unselectedIconColor = Slate400,
                            unselectedTextColor = Slate400,
                            indicatorColor = Amber500.copy(alpha = 0.18f)
                        )
                    )
                }
            }
        },
        containerColor = Slate950
    ) { innerPadding ->
        Box(modifier = Modifier.padding(innerPadding)) {
            when (selectedTab) {
                AppTab.DESK -> StudyDeskScreen(
                    uiState = uiState,
                    onToggleTask = viewModel::toggleTask,
                    onLaunchChatWithPrompt = { query ->
                        viewModel.sendMessage(query)
                        selectedTab = AppTab.CHAT
                    },
                    onNavigateToFlashcards = { selectedTab = AppTab.CARDS }
                )
                AppTab.CHAT -> ChatScreen(
                    uiState = uiState,
                    onSendMessage = viewModel::sendMessage,
                    onClearChat = viewModel::clearChat,
                    onDismissError = viewModel::clearError,
                    onNavigateToSettings = { selectedTab = AppTab.SETTINGS }
                )
                AppTab.CARDS -> FlashcardsScreen(
                    uiState = uiState,
                    onFlipCard = viewModel::flipFlashcard,
                    onReviewCard = viewModel::reviewFlashcard
                )
                AppTab.SETTINGS -> SettingsScreen(
                    uiState = uiState,
                    onSaveApiKey = viewModel::saveApiKey,
                    onClearApiKey = viewModel::clearApiKey,
                    onSaveServerUrl = viewModel::saveServerUrl,
                    onSelectModel = viewModel::saveSelectedModel,
                    onSaveUserName = viewModel::saveUserName,
                    onSaveTargetExam = viewModel::saveTargetExam,
                    onLogout = viewModel::logout
                )
            }
        }
    }
}
