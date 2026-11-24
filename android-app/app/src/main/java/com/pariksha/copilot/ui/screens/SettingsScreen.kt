package com.pariksha.copilot.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.input.VisualTransformation
import androidx.compose.ui.unit.dp
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
    onSaveTargetExam: (String) -> Unit
) {
    var apiKeyInput by remember(uiState.apiKey) { mutableStateOf(uiState.apiKey) }
    var showApiKey by remember { mutableStateOf(false) }
    var serverUrlInput by remember(uiState.serverUrl) { mutableStateOf(uiState.serverUrl) }
    var userNameInput by remember(uiState.userName) { mutableStateOf(uiState.userName) }
    var showModelPicker by remember { mutableStateOf(false) }
    var showExamPicker by remember { mutableStateOf(false) }
    var showSavedSnackbar by remember { mutableStateOf(false) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
    ) {
        // Header
        TopAppBar(
            title = {
                Text(
                    "Settings",
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold
                )
            },
            colors = TopAppBarDefaults.topAppBarColors(
                containerColor = MaterialTheme.colorScheme.surface
            )
        )

        Column(
            modifier = Modifier.padding(horizontal = 16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // === API Key Section ===
            SettingsSection(title = "🔑 Gemini API Key", subtitle = "Required for AI features") {
                OutlinedTextField(
                    value = apiKeyInput,
                    onValueChange = { apiKeyInput = it },
                    modifier = Modifier.fillMaxWidth(),
                    label = { Text("API Key") },
                    placeholder = { Text("AIzaSy...") },
                    singleLine = true,
                    visualTransformation = if (showApiKey) VisualTransformation.None else PasswordVisualTransformation(),
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
                    trailingIcon = {
                        Row {
                            IconButton(onClick = { showApiKey = !showApiKey }) {
                                Icon(
                                    if (showApiKey) Icons.Default.VisibilityOff else Icons.Default.Visibility,
                                    "Toggle visibility"
                                )
                            }
                        }
                    },
                    shape = RoundedCornerShape(12.dp),
                    supportingText = {
                        if (uiState.isApiKeyConfigured) {
                            Text("✅ Key configured", color = Success)
                        } else {
                            Text("Get your key from aistudio.google.com")
                        }
                    }
                )

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Button(
                        onClick = {
                            onSaveApiKey(apiKeyInput)
                            showSavedSnackbar = true
                        },
                        modifier = Modifier.weight(1f),
                        enabled = apiKeyInput.isNotBlank(),
                        shape = RoundedCornerShape(12.dp)
                    ) {
                        Icon(Icons.Default.Save, "Save", modifier = Modifier.size(18.dp))
                        Spacer(Modifier.width(6.dp))
                        Text("Save Key")
                    }

                    OutlinedButton(
                        onClick = {
                            onClearApiKey()
                            apiKeyInput = ""
                        },
                        modifier = Modifier.weight(1f),
                        shape = RoundedCornerShape(12.dp),
                        colors = ButtonDefaults.outlinedButtonColors(
                            contentColor = Error
                        )
                    ) {
                        Icon(Icons.Default.Delete, "Clear", modifier = Modifier.size(18.dp))
                        Spacer(Modifier.width(6.dp))
                        Text("Clear Key")
                    }
                }
            }

            // === Model Selection ===
            SettingsSection(title = "🤖 AI Model", subtitle = "Choose your Gemini model") {
                OutlinedCard(
                    onClick = { showModelPicker = true },
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column {
                            Text(
                                AVAILABLE_MODELS.find { it.id == uiState.selectedModel }?.name
                                    ?: uiState.selectedModel,
                                style = MaterialTheme.typography.bodyLarge,
                                fontWeight = FontWeight.Medium
                            )
                            Text(
                                AVAILABLE_MODELS.find { it.id == uiState.selectedModel }?.description ?: "",
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }
                        Icon(Icons.Default.ArrowDropDown, "Select model")
                    }
                }
            }

            // Model Picker Dialog
            if (showModelPicker) {
                AlertDialog(
                    onDismissRequest = { showModelPicker = false },
                    title = { Text("Select AI Model") },
                    text = {
                        Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                            AVAILABLE_MODELS.forEach { model ->
                                val selected = model.id == uiState.selectedModel
                                Surface(
                                    onClick = {
                                        onSelectModel(model.id)
                                        showModelPicker = false
                                    },
                                    modifier = Modifier.fillMaxWidth(),
                                    color = if (selected) MaterialTheme.colorScheme.primaryContainer
                                    else MaterialTheme.colorScheme.surface,
                                    shape = RoundedCornerShape(12.dp)
                                ) {
                                    Row(
                                        modifier = Modifier.padding(12.dp),
                                        verticalAlignment = Alignment.CenterVertically
                                    ) {
                                        RadioButton(
                                            selected = selected,
                                            onClick = null
                                        )
                                        Spacer(Modifier.width(8.dp))
                                        Column {
                                            Text(model.name, fontWeight = FontWeight.Medium)
                                            Text(
                                                model.description,
                                                style = MaterialTheme.typography.bodySmall,
                                                color = MaterialTheme.colorScheme.onSurfaceVariant
                                            )
                                        }
                                    }
                                }
                            }
                        }
                    },
                    confirmButton = {
                        TextButton(onClick = { showModelPicker = false }) { Text("Done") }
                    }
                )
            }

            // === Target Exam ===
            SettingsSection(title = "🎯 Target Exam", subtitle = "AI tutor specializes for your exam") {
                OutlinedCard(
                    onClick = { showExamPicker = true },
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(uiState.targetExam, style = MaterialTheme.typography.bodyLarge)
                        Icon(Icons.Default.ArrowDropDown, "Select exam")
                    }
                }
            }

            // Exam Picker Dialog
            if (showExamPicker) {
                AlertDialog(
                    onDismissRequest = { showExamPicker = false },
                    title = { Text("Select Target Exam") },
                    text = {
                        Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                            EXAM_OPTIONS.forEach { exam ->
                                val selected = exam == uiState.targetExam
                                Surface(
                                    onClick = {
                                        onSaveTargetExam(exam)
                                        showExamPicker = false
                                    },
                                    modifier = Modifier.fillMaxWidth(),
                                    color = if (selected) MaterialTheme.colorScheme.primaryContainer
                                    else MaterialTheme.colorScheme.surface,
                                    shape = RoundedCornerShape(12.dp)
                                ) {
                                    Row(
                                        modifier = Modifier.padding(12.dp),
                                        verticalAlignment = Alignment.CenterVertically
                                    ) {
                                        RadioButton(selected = selected, onClick = null)
                                        Spacer(Modifier.width(8.dp))
                                        Text(exam)
                                    }
                                }
                            }
                        }
                    },
                    confirmButton = {
                        TextButton(onClick = { showExamPicker = false }) { Text("Done") }
                    }
                )
            }

            // === Web Portal Server URL ===
            SettingsSection(title = "🌐 Web Portal Server", subtitle = "Backend URL for the web portal tab") {
                OutlinedTextField(
                    value = serverUrlInput,
                    onValueChange = { serverUrlInput = it },
                    modifier = Modifier.fillMaxWidth(),
                    label = { Text("Server URL") },
                    placeholder = { Text("http://192.168.29.94:8000") },
                    singleLine = true,
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Uri),
                    shape = RoundedCornerShape(12.dp),
                    supportingText = { Text("The pariksha-copilot server address") }
                )

                Button(
                    onClick = { onSaveServerUrl(serverUrlInput) },
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Icon(Icons.Default.Save, "Save", modifier = Modifier.size(18.dp))
                    Spacer(Modifier.width(6.dp))
                    Text("Save Server URL")
                }
            }

            // === User Profile ===
            SettingsSection(title = "👤 Profile", subtitle = "Your name for personalized responses") {
                OutlinedTextField(
                    value = userNameInput,
                    onValueChange = { userNameInput = it },
                    modifier = Modifier.fillMaxWidth(),
                    label = { Text("Your Name") },
                    placeholder = { Text("Aspirant Rahul") },
                    singleLine = true,
                    shape = RoundedCornerShape(12.dp)
                )

                Button(
                    onClick = { onSaveUserName(userNameInput) },
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Icon(Icons.Default.Person, "Save", modifier = Modifier.size(18.dp))
                    Spacer(Modifier.width(6.dp))
                    Text("Save Profile")
                }
            }

            // === About ===
            SettingsSection(title = "ℹ️ About", subtitle = "Pariksha Copilot v1.0.0") {
                Text(
                    "AI-powered competitive exam preparation platform.\n" +
                            "Uses Google Gemini for intelligent tutoring, with your own API key.\n\n" +
                            "Features:\n" +
                            "• Native AI Chat with streaming responses\n" +
                            "• Model fallback (2.5 Flash → Pro → 1.5 Flash)\n" +
                            "• Web Portal for full platform access\n" +
                            "• Offline API key storage (never leaves device)\n\n" +
                            "Built with Jetpack Compose + Google Generative AI SDK",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }

            Spacer(Modifier.height(24.dp))
        }
    }

    // Saved Snackbar
    if (showSavedSnackbar) {
        LaunchedEffect(Unit) {
            kotlinx.coroutines.delay(2000)
            showSavedSnackbar = false
        }
    }
}

@Composable
fun SettingsSection(
    title: String,
    subtitle: String,
    content: @Composable ColumnScope.() -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surface
        )
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Column {
                Text(
                    title,
                    style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    subtitle,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            content()
        }
    }
}
