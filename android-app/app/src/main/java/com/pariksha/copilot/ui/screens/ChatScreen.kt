package com.pariksha.copilot.ui.screens

import androidx.compose.animation.*
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.Send
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalFocusManager
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.pariksha.copilot.AppUiState
import com.pariksha.copilot.data.ChatMessage
import com.pariksha.copilot.ui.components.MarkdownText
import com.pariksha.copilot.ui.theme.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ChatScreen(
    uiState: AppUiState,
    onSendMessage: (String) -> Unit,
    onClearChat: () -> Unit,
    onDismissError: () -> Unit,
    onNavigateToSettings: () -> Unit
) {
    var inputText by remember { mutableStateOf("") }
    val listState = rememberLazyListState()
    val focusManager = LocalFocusManager.current

    // Auto-scroll to bottom when new messages arrive
    LaunchedEffect(uiState.messages.size, uiState.streamingText) {
        if (uiState.messages.isNotEmpty() || uiState.streamingText.isNotEmpty()) {
            val targetIndex = uiState.messages.size + (if (uiState.streamingText.isNotEmpty()) 1 else 0)
            listState.animateScrollToItem(maxOf(0, targetIndex))
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Text(
                                "AI Tutor & Copilot",
                                style = MaterialTheme.typography.titleMedium.copy(
                                    fontWeight = FontWeight.Bold,
                                    color = Color.White
                                )
                            )
                            Spacer(Modifier.width(8.dp))
                            Surface(
                                color = Amber500.copy(alpha = 0.15f),
                                shape = RoundedCornerShape(4.dp)
                            ) {
                                Text(
                                    uiState.targetExam.take(14) + if (uiState.targetExam.length > 14) "…" else "",
                                    modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp),
                                    style = MaterialTheme.typography.labelSmall.copy(
                                        color = Amber400,
                                        fontWeight = FontWeight.SemiBold
                                    )
                                )
                            }
                        }
                        Text(
                            "Multi-model cognitive reasoning & syllabus retrieval",
                            style = MaterialTheme.typography.labelSmall.copy(
                                color = Slate400
                            )
                        )
                    }
                },
                actions = {
                    // Model indicator chip
                    AssistChip(
                        onClick = onNavigateToSettings,
                        label = {
                            Text(
                                uiState.selectedModel.replace("gemini-", "").uppercase(),
                                style = MaterialTheme.typography.labelSmall.copy(
                                    fontWeight = FontWeight.Bold,
                                    color = Amber400
                                )
                            )
                        },
                        leadingIcon = {
                            Icon(
                                Icons.Default.Memory,
                                contentDescription = "Model",
                                tint = Amber400,
                                modifier = Modifier.size(14.dp)
                            )
                        },
                        colors = AssistChipDefaults.assistChipColors(
                            containerColor = Slate800,
                            labelColor = Amber400
                        ),
                        border = AssistChipDefaults.assistChipBorder(
                            enabled = true,
                            borderColor = Amber500.copy(alpha = 0.4f)
                        ),
                        modifier = Modifier.height(28.dp)
                    )

                    Spacer(Modifier.width(4.dp))

                    IconButton(onClick = onClearChat) {
                        Icon(Icons.Default.DeleteSweep, "Clear chat", tint = Slate400)
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
        ) {
            // API Key Warning
            if (!uiState.isApiKeyConfigured) {
                Surface(
                    modifier = Modifier.fillMaxWidth(),
                    color = Amber500.copy(alpha = 0.15f),
                    border = androidx.compose.foundation.BorderStroke(1.dp, Amber500.copy(alpha = 0.3f))
                ) {
                    Row(
                        modifier = Modifier.padding(12.dp),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Icon(Icons.Default.VpnKey, "Key Missing", tint = Amber400, modifier = Modifier.size(20.dp))
                        Text(
                            "Gemini API key is not configured. Add your key to start chats.",
                            color = Slate200,
                            style = MaterialTheme.typography.bodySmall,
                            modifier = Modifier.weight(1f)
                        )
                        Button(
                            onClick = onNavigateToSettings,
                            shape = RoundedCornerShape(6.dp),
                            colors = ButtonDefaults.buttonColors(
                                containerColor = Amber500,
                                contentColor = Slate950
                            ),
                            contentPadding = PaddingValues(horizontal = 10.dp, vertical = 4.dp)
                        ) {
                            Text("Setup Key", style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold))
                        }
                    }
                }
            }

            // Error Banner
            uiState.errorMessage?.let { error ->
                Surface(
                    modifier = Modifier.fillMaxWidth(),
                    color = Rose500.copy(alpha = 0.15f),
                    border = androidx.compose.foundation.BorderStroke(1.dp, Rose500.copy(alpha = 0.3f))
                ) {
                    Row(
                        modifier = Modifier.padding(8.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(Icons.Default.Error, "Error", tint = Rose400, modifier = Modifier.size(16.dp))
                        Spacer(Modifier.width(8.dp))
                        Text(error, color = Rose400, style = MaterialTheme.typography.bodySmall, modifier = Modifier.weight(1f))
                        IconButton(onClick = onDismissError, modifier = Modifier.size(24.dp)) {
                            Icon(Icons.Default.Close, "Dismiss", tint = Rose400, modifier = Modifier.size(16.dp))
                        }
                    }
                }
            }

            // Chat Messages List
            LazyColumn(
                modifier = Modifier
                    .weight(1f)
                    .fillMaxWidth()
                    .padding(horizontal = 14.dp),
                state = listState,
                verticalArrangement = Arrangement.spacedBy(12.dp),
                contentPadding = PaddingValues(vertical = 14.dp)
            ) {
                if (uiState.messages.isEmpty() && uiState.streamingText.isEmpty()) {
                    item {
                        ScholarlyWelcomeCard(
                            targetExam = uiState.targetExam,
                            onSuggestionClick = { suggestion ->
                                onSendMessage(suggestion)
                            }
                        )
                    }
                }

                items(uiState.messages, key = { it.id }) { message ->
                    ScholarlyChatBubble(message = message)
                }

                if (uiState.streamingText.isNotEmpty()) {
                    item {
                        ScholarlyChatBubble(
                            message = ChatMessage(
                                role = "model",
                                content = uiState.streamingText
                            )
                        )
                    }
                }

                if (uiState.isGenerating && uiState.streamingText.isEmpty()) {
                    item {
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(start = 8.dp, top = 4.dp),
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(10.dp)
                        ) {
                            CircularProgressIndicator(
                                modifier = Modifier.size(16.dp),
                                strokeWidth = 2.dp,
                                color = Amber400
                            )
                            Text(
                                "Analyzing syllabus and generating response...",
                                style = MaterialTheme.typography.bodySmall,
                                color = Slate400
                            )
                        }
                    }
                }
            }

            // Input Section
            Surface(
                modifier = Modifier.fillMaxWidth(),
                color = Slate900,
                border = androidx.compose.foundation.BorderStroke(1.dp, Slate800)
            ) {
                Row(
                    modifier = Modifier
                        .padding(horizontal = 12.dp, vertical = 10.dp)
                        .navigationBarsPadding(),
                    verticalAlignment = Alignment.Bottom,
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    OutlinedTextField(
                        value = inputText,
                        onValueChange = { inputText = it },
                        modifier = Modifier.weight(1f),
                        placeholder = {
                            Text(
                                "Ask syllabus, PYQs, high-yield notes…",
                                style = MaterialTheme.typography.bodyMedium,
                                color = Slate500
                            )
                        },
                        maxLines = 4,
                        keyboardOptions = KeyboardOptions(imeAction = ImeAction.Send),
                        keyboardActions = KeyboardActions(
                            onSend = {
                                if (inputText.isNotBlank() && !uiState.isGenerating) {
                                    onSendMessage(inputText)
                                    inputText = ""
                                    focusManager.clearFocus()
                                }
                            }
                        ),
                        shape = RoundedCornerShape(16.dp),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedContainerColor = Slate950,
                            unfocusedContainerColor = Slate950,
                            focusedBorderColor = Amber500,
                            unfocusedBorderColor = Slate700,
                            focusedTextColor = Color.White,
                            unfocusedTextColor = Slate100
                        )
                    )

                    FilledIconButton(
                        onClick = {
                            if (inputText.isNotBlank() && !uiState.isGenerating) {
                                onSendMessage(inputText)
                                inputText = ""
                                focusManager.clearFocus()
                            }
                        },
                        enabled = inputText.isNotBlank() && !uiState.isGenerating,
                        modifier = Modifier.size(50.dp),
                        shape = RoundedCornerShape(14.dp),
                        colors = IconButtonDefaults.filledIconButtonColors(
                            containerColor = Amber500,
                            contentColor = Slate950,
                            disabledContainerColor = Slate800,
                            disabledContentColor = Slate600
                        )
                    ) {
                        Icon(
                            Icons.AutoMirrored.Filled.Send,
                            contentDescription = "Send",
                            modifier = Modifier.size(20.dp)
                        )
                    }
                }
            }
        }
    }
}

@Composable
fun ScholarlyChatBubble(message: ChatMessage) {
    val isUser = message.role == "user"

    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = if (isUser) Arrangement.End else Arrangement.Start
    ) {
        if (!isUser) {
            Surface(
                modifier = Modifier.size(32.dp),
                shape = CircleShape,
                color = Amber500.copy(alpha = 0.2f),
                border = androidx.compose.foundation.BorderStroke(1.dp, Amber500.copy(alpha = 0.4f))
            ) {
                Box(contentAlignment = Alignment.Center) {
                    Text("AI", color = Amber400, fontSize = 11.sp, fontWeight = FontWeight.Bold)
                }
            }
            Spacer(Modifier.width(8.dp))
        }

        Surface(
            modifier = Modifier.widthIn(max = 330.dp),
            shape = RoundedCornerShape(
                topStart = 14.dp,
                topEnd = 14.dp,
                bottomStart = if (isUser) 14.dp else 4.dp,
                bottomEnd = if (isUser) 4.dp else 14.dp
            ),
            color = if (isUser) {
                Blue600
            } else if (message.isError) {
                Rose500.copy(alpha = 0.15f)
            } else {
                Slate900
            },
            border = if (!isUser && !message.isError) androidx.compose.foundation.BorderStroke(1.dp, Slate800) else null
        ) {
            Column(modifier = Modifier.padding(14.dp)) {
                if (isUser) {
                    Text(
                        text = message.content,
                        color = Color.White,
                        style = MaterialTheme.typography.bodyMedium
                    )
                } else {
                    MarkdownText(
                        markdown = message.content,
                        color = if (message.isError) Rose400 else Slate100
                    )
                }
            }
        }

        if (isUser) {
            Spacer(Modifier.width(8.dp))
            Surface(
                modifier = Modifier.size(32.dp),
                shape = CircleShape,
                color = Blue500.copy(alpha = 0.2f),
                border = androidx.compose.foundation.BorderStroke(1.dp, Blue500.copy(alpha = 0.4f))
            ) {
                Box(contentAlignment = Alignment.Center) {
                    Text("YOU", color = Blue400, fontSize = 10.sp, fontWeight = FontWeight.Bold)
                }
            }
        }
    }
}

@Composable
fun ScholarlyWelcomeCard(
    targetExam: String,
    onSuggestionClick: (String) -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 12.dp),
        colors = CardDefaults.cardColors(containerColor = Slate900),
        shape = RoundedCornerShape(16.dp),
        border = CardDefaults.outlinedCardBorder().copy(
            brush = androidx.compose.ui.graphics.SolidColor(Slate800)
        )
    ) {
        Column(
            modifier = Modifier.padding(20.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(14.dp)
        ) {
            Surface(
                shape = CircleShape,
                color = Amber500.copy(alpha = 0.12f),
                modifier = Modifier.size(56.dp)
            ) {
                Box(contentAlignment = Alignment.Center) {
                    Icon(
                        Icons.Default.School,
                        contentDescription = null,
                        tint = Amber400,
                        modifier = Modifier.size(28.dp)
                    )
                }
            }

            Text(
                "Aspirant Copilot Active",
                style = MaterialTheme.typography.titleMedium.copy(
                    fontWeight = FontWeight.Bold,
                    color = Color.White
                )
            )

            Text(
                "Trained on official syllabus guides, previous year question trends, and high-yield retention summaries for $targetExam.",
                style = MaterialTheme.typography.bodySmall.copy(
                    color = Slate300,
                    textAlign = TextAlign.Center,
                    lineHeight = 20.sp
                )
            )

            HorizontalDivider(color = Slate800)

            Text(
                "High-Yield Starting Prompts",
                style = MaterialTheme.typography.labelSmall.copy(
                    color = Amber400,
                    fontWeight = FontWeight.Bold,
                    letterSpacing = 0.5.sp
                )
            )

            val suggestions = listOf(
                "Explain the high-scoring strategy & weightage for $targetExam",
                "Give me a 30-day revision timetable with daily mock goals",
                "Generate 5 tricky MCQs on current financial & regulatory norms",
                "Break down the hardest topic in my syllabus with analogies"
            )

            suggestions.forEach { suggestion ->
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(10.dp),
                    colors = CardDefaults.cardColors(containerColor = Slate950),
                    border = CardDefaults.outlinedCardBorder().copy(
                        brush = androidx.compose.ui.graphics.SolidColor(Slate800)
                    ),
                    onClick = { onSuggestionClick(suggestion) }
                ) {
                    Row(
                        modifier = Modifier.padding(12.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            Icons.Default.Bolt,
                            contentDescription = null,
                            tint = Amber400,
                            modifier = Modifier.size(16.dp)
                        )
                        Spacer(Modifier.width(8.dp))
                        Text(
                            suggestion,
                            style = MaterialTheme.typography.bodySmall.copy(color = Slate200),
                            modifier = Modifier.weight(1f)
                        )
                    }
                }
            }
        }
    }
}
