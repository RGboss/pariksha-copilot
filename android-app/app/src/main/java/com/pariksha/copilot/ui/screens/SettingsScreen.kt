package com.pariksha.copilot.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.input.VisualTransformation
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.pariksha.copilot.AppUiState
import com.pariksha.copilot.data.AVAILABLE_MODELS
import com.pariksha.copilot.data.EXAM_OPTIONS
import com.pariksha.copilot.ui.theme.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsScreen(
    uiState: AppUiState,
    onSaveApiKey: (String) -> Unit,
    onClearApiKey: () -> Unit,
    onSaveServerUrl: (String) -> Unit,
    onSelectModel: (String) -> Unit,
    onSaveUserName: (String) -> Unit,
    onSaveTargetExam: (String) -> Unit,
    onLogout: () -> Unit
) {
    var apiKeyInput by remember(uiState.apiKey) { mutableStateOf(uiState.apiKey) }
    var showApiKey by remember { mutableStateOf(false) }
    var serverUrlInput by remember(uiState.serverUrl) { mutableStateOf(uiState.serverUrl) }
    var showModelDialog by remember { mutableStateOf(false) }
    var showExamDialog by remember { mutableStateOf(false) }
    var showLogoutDialog by remember { mutableStateOf(false) }
    var showKeySavedSnackbar by remember { mutableStateOf(false) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        Text(
                            "Profile & AI Config",
                            style = MaterialTheme.typography.titleMedium.copy(
                                fontWeight = FontWeight.Bold,
                                color = Color.White
                            )
                        )
                        Text(
                            "Manage Gemini key, models, and study preferences",
                            style = MaterialTheme.typography.labelSmall.copy(color = Slate400)
                        )
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = Slate900
                )
            )
        },
        containerColor = Slate950
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .verticalScroll(rememberScrollState())
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Aspirant Profile Summary Card
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(14.dp),
                colors = CardDefaults.cardColors(containerColor = Slate900),
                border = CardDefaults.outlinedCardBorder().copy(
                    brush = androidx.compose.ui.graphics.SolidColor(Slate800)
                )
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Surface(
                            modifier = Modifier.size(52.dp),
                            shape = CircleShape,
                            color = Amber500.copy(alpha = 0.2f),
                            border = androidx.compose.foundation.BorderStroke(1.5.dp, Amber500)
                        ) {
                            Box(contentAlignment = Alignment.Center) {
                                Text(
                                    if (uiState.userName.isNotBlank()) uiState.userName.take(2).uppercase() else "AR",
                                    style = MaterialTheme.typography.titleMedium.copy(
                                        color = Amber400,
                                        fontWeight = FontWeight.Bold
                                    )
                                )
                            }
                        }

                        Spacer(Modifier.width(14.dp))

                        Column(modifier = Modifier.weight(1f)) {
                            Text(
                                if (uiState.userName.isNotBlank()) uiState.userName else "Aspirant Rahul",
                                style = MaterialTheme.typography.titleMedium.copy(
                                    fontWeight = FontWeight.Bold,
                                    color = Color.White
                                )
                            )
                            Spacer(Modifier.height(2.dp))
                            Text(
                                if (uiState.userEmail.isNotBlank()) uiState.userEmail else "aspirant@pariksha.gov",
                                style = MaterialTheme.typography.bodySmall.copy(color = Slate400)
                            )
                            Spacer(Modifier.height(6.dp))
                            Surface(
                                shape = RoundedCornerShape(4.dp),
                                color = Slate800,
                                modifier = Modifier.clickable { showExamDialog = true }
                            ) {
                                Row(
                                    modifier = Modifier.padding(horizontal = 8.dp, vertical = 3.dp),
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Text(
                                        uiState.targetExam,
                                        style = MaterialTheme.typography.labelSmall.copy(
                                            color = Amber400,
                                            fontWeight = FontWeight.SemiBold
                                        )
                                    )
                                    Spacer(Modifier.width(4.dp))
                                    Icon(Icons.Default.Edit, contentDescription = "Change Exam", tint = Amber400, modifier = Modifier.size(12.dp))
                                }
                            }
                        }
                    }

                    Spacer(Modifier.height(14.dp))
                    HorizontalDivider(color = Slate800)
                    Spacer(Modifier.height(14.dp))

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Column {
                            Text("Current Streak", style = MaterialTheme.typography.labelSmall.copy(color = Slate400))
                            Text("${uiState.streakDays} Days 🔥", style = MaterialTheme.typography.bodyMedium.copy(color = Color.White, fontWeight = FontWeight.Bold))
                        }
                        Column {
                            Text("Today's Target", style = MaterialTheme.typography.labelSmall.copy(color = Slate400))
                            Text("${uiState.dailyHours} hrs / day", style = MaterialTheme.typography.bodyMedium.copy(color = Color.White, fontWeight = FontWeight.Bold))
                        }
                        Column {
                            Text("Target Rank", style = MaterialTheme.typography.labelSmall.copy(color = Slate400))
                            Text("Top 50 (AIR)", style = MaterialTheme.typography.bodyMedium.copy(color = Amber400, fontWeight = FontWeight.Bold))
                        }
                    }
                }
            }

            // Customer Gemini API Key Management
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(14.dp),
                colors = CardDefaults.cardColors(containerColor = Slate900),
                border = CardDefaults.outlinedCardBorder().copy(
                    brush = androidx.compose.ui.graphics.SolidColor(Amber500.copy(alpha = 0.4f))
                )
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(Icons.Default.Key, contentDescription = null, tint = Amber400, modifier = Modifier.size(18.dp))
                            Spacer(Modifier.width(8.dp))
                            Text(
                                "Gemini API Key",
                                style = MaterialTheme.typography.titleSmall.copy(
                                    fontWeight = FontWeight.Bold,
                                    color = Color.White
                                )
                            )
                        }

                        Surface(
                            shape = RoundedCornerShape(4.dp),
                            color = if (uiState.isApiKeyConfigured) Emerald500.copy(alpha = 0.15f) else Rose500.copy(alpha = 0.15f)
                        ) {
                            Text(
                                if (uiState.isApiKeyConfigured) "Active & Valid" else "Not Configured",
                                modifier = Modifier.padding(horizontal = 8.dp, vertical = 2.dp),
                                style = MaterialTheme.typography.labelSmall.copy(
                                    color = if (uiState.isApiKeyConfigured) Emerald400 else Rose400,
                                    fontWeight = FontWeight.Bold
                                )
                            )
                        }
                    }

                    Spacer(Modifier.height(8.dp))
                    Text(
                        "Your key stays strictly private on this device in Android Encrypted DataStore. Obtain a free key from Google AI Studio (aistudio.google.com).",
                        style = MaterialTheme.typography.bodySmall.copy(color = Slate400, lineHeight = 18.sp)
                    )

                    Spacer(Modifier.height(14.dp))

                    OutlinedTextField(
                        value = apiKeyInput,
                        onValueChange = { newKey -> apiKeyInput = newKey },
                        modifier = Modifier.fillMaxWidth(),
                        placeholder = { Text("Paste AIzaSy... here", color = Slate500) },
                        singleLine = true,
                        visualTransformation = if (showApiKey) VisualTransformation.None else PasswordVisualTransformation(),
                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
                        trailingIcon = {
                            IconButton(onClick = { showApiKey = !showApiKey }) {
                                Icon(
                                    if (showApiKey) Icons.Default.VisibilityOff else Icons.Default.Visibility,
                                    contentDescription = "Toggle Visibility",
                                    tint = Slate400
                                )
                            }
                        },
                        shape = RoundedCornerShape(10.dp),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedContainerColor = Slate950,
                            unfocusedContainerColor = Slate950,
                            focusedBorderColor = Amber500,
                            unfocusedBorderColor = Slate700,
                            focusedTextColor = Color.White,
                            unfocusedTextColor = Slate100
                        )
                    )

                    Spacer(Modifier.height(12.dp))

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(10.dp)
                    ) {
                        Button(
                            onClick = {
                                onSaveApiKey(apiKeyInput.trim())
                                showKeySavedSnackbar = true
                            },
                            modifier = Modifier.weight(1f),
                            shape = RoundedCornerShape(8.dp),
                            colors = ButtonDefaults.buttonColors(
                                containerColor = Amber500,
                                contentColor = Slate950
                            )
                        ) {
                            Icon(Icons.Default.Save, contentDescription = null, modifier = Modifier.size(16.dp))
                            Spacer(Modifier.width(6.dp))
                            Text("Save Key", style = MaterialTheme.typography.labelMedium.copy(fontWeight = FontWeight.Bold))
                        }

                        if (uiState.isApiKeyConfigured) {
                            OutlinedButton(
                                onClick = {
                                    apiKeyInput = ""
                                    onClearApiKey()
                                },
                                shape = RoundedCornerShape(8.dp),
                                colors = ButtonDefaults.outlinedButtonColors(contentColor = Rose400),
                                border = ButtonDefaults.outlinedButtonBorder.copy(
                                    brush = androidx.compose.ui.graphics.SolidColor(Rose500.copy(alpha = 0.5f))
                                )
                            ) {
                                Text("Clear")
                            }
                        }
                    }

                    if (showKeySavedSnackbar) {
                        Spacer(Modifier.height(8.dp))
                        Text("API Key saved securely!", color = Emerald400, style = MaterialTheme.typography.labelSmall)
                    }
                }
            }

            // AI Model Selection Card
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .clickable { showModelDialog = true },
                shape = RoundedCornerShape(14.dp),
                colors = CardDefaults.cardColors(containerColor = Slate900),
                border = CardDefaults.outlinedCardBorder().copy(
                    brush = androidx.compose.ui.graphics.SolidColor(Slate800)
                )
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Surface(
                        shape = CircleShape,
                        color = Blue500.copy(alpha = 0.15f),
                        modifier = Modifier.size(40.dp)
                    ) {
                        Box(contentAlignment = Alignment.Center) {
                            Icon(Icons.Default.Memory, contentDescription = null, tint = Blue400, modifier = Modifier.size(20.dp))
                        }
                    }

                    Spacer(Modifier.width(14.dp))

                    Column(modifier = Modifier.weight(1f)) {
                        Text(
                            "AI Cognitive Model",
                            style = MaterialTheme.typography.titleSmall.copy(fontWeight = FontWeight.Bold, color = Color.White)
                        )
                        Spacer(Modifier.height(2.dp))
                        Text(
                            uiState.selectedModel,
                            style = MaterialTheme.typography.bodySmall.copy(color = Amber400, fontWeight = FontWeight.SemiBold)
                        )
                    }

                    Icon(Icons.Default.ChevronRight, contentDescription = "Change", tint = Slate400)
                }
            }

            // Target Exam Selection Card
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .clickable { showExamDialog = true },
                shape = RoundedCornerShape(14.dp),
                colors = CardDefaults.cardColors(containerColor = Slate900),
                border = CardDefaults.outlinedCardBorder().copy(
                    brush = androidx.compose.ui.graphics.SolidColor(Slate800)
                )
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Surface(
                        shape = CircleShape,
                        color = Purple500.copy(alpha = 0.15f),
                        modifier = Modifier.size(40.dp)
                    ) {
                        Box(contentAlignment = Alignment.Center) {
                            Icon(Icons.Default.School, contentDescription = null, tint = Purple400, modifier = Modifier.size(20.dp))
                        }
                    }

                    Spacer(Modifier.width(14.dp))

                    Column(modifier = Modifier.weight(1f)) {
                        Text(
                            "Target Exam Syllabus",
                            style = MaterialTheme.typography.titleSmall.copy(fontWeight = FontWeight.Bold, color = Color.White)
                        )
                        Spacer(Modifier.height(2.dp))
                        Text(
                            uiState.targetExam,
                            style = MaterialTheme.typography.bodySmall.copy(color = Slate300)
                        )
                    }

                    Icon(Icons.Default.ChevronRight, contentDescription = "Change", tint = Slate400)
                }
            }

            // Sync Endpoint Settings Card
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(14.dp),
                colors = CardDefaults.cardColors(containerColor = Slate900),
                border = CardDefaults.outlinedCardBorder().copy(
                    brush = androidx.compose.ui.graphics.SolidColor(Slate800)
                )
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(
                        "Cloud / Worker Sync Endpoint",
                        style = MaterialTheme.typography.titleSmall.copy(fontWeight = FontWeight.Bold, color = Color.White)
                    )
                    Spacer(Modifier.height(6.dp))
                    Text(
                        "Synchronize candidate logs & PDF vector RAG with primary cluster or worker node (e.g. 192.168.29.94:8082).",
                        style = MaterialTheme.typography.bodySmall.copy(color = Slate400)
                    )
                    Spacer(Modifier.height(10.dp))

                    OutlinedTextField(
                        value = serverUrlInput,
                        onValueChange = { newUrl -> serverUrlInput = newUrl },
                        modifier = Modifier.fillMaxWidth(),
                        singleLine = true,
                        shape = RoundedCornerShape(10.dp),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedContainerColor = Slate950,
                            unfocusedContainerColor = Slate950,
                            focusedBorderColor = Amber500,
                            unfocusedBorderColor = Slate700,
                            focusedTextColor = Color.White,
                            unfocusedTextColor = Slate100
                        )
                    )

                    Spacer(Modifier.height(10.dp))

                    OutlinedButton(
                        onClick = { onSaveServerUrl(serverUrlInput.trim()) },
                        shape = RoundedCornerShape(8.dp),
                        colors = ButtonDefaults.outlinedButtonColors(contentColor = Amber400),
                        border = ButtonDefaults.outlinedButtonBorder.copy(
                            brush = androidx.compose.ui.graphics.SolidColor(Slate700)
                        )
                    ) {
                        Icon(Icons.Default.Sync, contentDescription = null, modifier = Modifier.size(16.dp))
                        Spacer(Modifier.width(6.dp))
                        Text("Update Endpoint")
                    }
                }
            }

            // Sign Out / End Session Card
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(14.dp),
                colors = CardDefaults.cardColors(containerColor = Slate900),
                border = CardDefaults.outlinedCardBorder().copy(
                    brush = androidx.compose.ui.graphics.SolidColor(Rose500.copy(alpha = 0.3f))
                )
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(
                        "Aspirant Study Session",
                        style = MaterialTheme.typography.titleSmall.copy(fontWeight = FontWeight.Bold, color = Color.White)
                    )
                    Spacer(Modifier.height(6.dp))
                    Text(
                        "Sign out to return to the Aspirant Login Portal or switch candidate profiles.",
                        style = MaterialTheme.typography.bodySmall.copy(color = Slate400)
                    )
                    Spacer(Modifier.height(14.dp))

                    Button(
                        onClick = { showLogoutDialog = true },
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(8.dp),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = Rose500,
                            contentColor = Color.White
                        )
                    ) {
                        Icon(Icons.Default.ExitToApp, contentDescription = null, modifier = Modifier.size(18.dp))
                        Spacer(Modifier.width(8.dp))
                        Text("Sign Out of Study Desk", style = MaterialTheme.typography.labelMedium.copy(fontWeight = FontWeight.Bold))
                    }
                }
            }
        }
    }

    // Model Picker Dialog
    if (showModelDialog) {
        AlertDialog(
            onDismissRequest = { showModelDialog = false },
            containerColor = Slate900,
            title = {
                Text(
                    "Select Cognitive Model",
                    style = MaterialTheme.typography.titleMedium.copy(color = Color.White, fontWeight = FontWeight.Bold)
                )
            },
            text = {
                Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    AVAILABLE_MODELS.forEach { modelInfo ->
                        val isSelected = modelInfo.id == uiState.selectedModel
                        Card(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clickable {
                                    onSelectModel(modelInfo.id)
                                    showModelDialog = false
                                },
                            shape = RoundedCornerShape(8.dp),
                            colors = CardDefaults.cardColors(
                                containerColor = if (isSelected) Slate800 else Slate950
                            ),
                            border = if (isSelected) CardDefaults.outlinedCardBorder().copy(
                                brush = androidx.compose.ui.graphics.SolidColor(Amber500)
                            ) else null
                        ) {
                            Row(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(12.dp),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                RadioButton(
                                    selected = isSelected,
                                    onClick = {
                                        onSelectModel(modelInfo.id)
                                        showModelDialog = false
                                    },
                                    colors = RadioButtonDefaults.colors(selectedColor = Amber500)
                                )
                                Spacer(Modifier.width(8.dp))
                                Column {
                                    Text(
                                        modelInfo.name,
                                        style = MaterialTheme.typography.bodyMedium.copy(
                                            color = Color.White,
                                            fontWeight = FontWeight.SemiBold
                                        )
                                    )
                                    Text(
                                        modelInfo.description,
                                        style = MaterialTheme.typography.labelSmall.copy(color = Slate400)
                                    )
                                }
                            }
                        }
                    }
                }
            },
            confirmButton = {
                TextButton(onClick = { showModelDialog = false }) {
                    Text("Cancel", color = Amber400)
                }
            }
        )
    }

    // Exam Picker Dialog
    if (showExamDialog) {
        AlertDialog(
            onDismissRequest = { showExamDialog = false },
            containerColor = Slate900,
            title = {
                Text(
                    "Choose Target Exam",
                    style = MaterialTheme.typography.titleMedium.copy(color = Color.White, fontWeight = FontWeight.Bold)
                )
            },
            text = {
                Column(
                    modifier = Modifier.verticalScroll(rememberScrollState()),
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    EXAM_OPTIONS.forEach { exam ->
                        val isSelected = exam == uiState.targetExam
                        Card(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clickable {
                                    onSaveTargetExam(exam)
                                    showExamDialog = false
                                },
                            shape = RoundedCornerShape(8.dp),
                            colors = CardDefaults.cardColors(
                                containerColor = if (isSelected) Slate800 else Slate950
                            ),
                            border = if (isSelected) CardDefaults.outlinedCardBorder().copy(
                                brush = androidx.compose.ui.graphics.SolidColor(Amber500)
                            ) else null
                        ) {
                            Row(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(12.dp),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                RadioButton(
                                    selected = isSelected,
                                    onClick = {
                                        onSaveTargetExam(exam)
                                        showExamDialog = false
                                    },
                                    colors = RadioButtonDefaults.colors(selectedColor = Amber500)
                                )
                                Spacer(Modifier.width(8.dp))
                                Text(
                                    exam,
                                    style = MaterialTheme.typography.bodyMedium.copy(
                                        color = Color.White,
                                        fontWeight = FontWeight.Medium
                                    )
                                )
                            }
                        }
                    }
                }
            },
            confirmButton = {
                TextButton(onClick = { showExamDialog = false }) {
                    Text("Close", color = Amber400)
                }
            }
        )
    }

    // Logout Confirmation Dialog
    if (showLogoutDialog) {
        AlertDialog(
            onDismissRequest = { showLogoutDialog = false },
            containerColor = Slate900,
            title = {
                Text("Confirm Sign Out", color = Color.White, fontWeight = FontWeight.Bold)
            },
            text = {
                Text(
                    "Are you sure you want to exit your study desk session? Your flashcards and tasks remain safely persisted on this device.",
                    color = Slate300
                )
            },
            confirmButton = {
                Button(
                    onClick = {
                        showLogoutDialog = false
                        onLogout()
                    },
                    colors = ButtonDefaults.buttonColors(containerColor = Rose500)
                ) {
                    Text("Sign Out", color = Color.White)
                }
            },
            dismissButton = {
                TextButton(onClick = { showLogoutDialog = false }) {
                    Text("Cancel", color = Slate400)
                }
            }
        )
    }
}
