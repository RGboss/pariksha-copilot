package com.pariksha.copilot.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextDecoration
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.pariksha.copilot.AppUiState
import com.pariksha.copilot.data.StudyTaskItem
import com.pariksha.copilot.ui.theme.*

@Composable
fun StudyDeskScreen(
    uiState: AppUiState,
    onToggleTask: (String) -> Unit,
    onAddTask: (String, String, Int, String) -> Unit = { _, _, _, _ -> },
    onLaunchChatWithPrompt: (String) -> Unit,
    onNavigateToFlashcards: () -> Unit,
    onNavigateToQuiz: () -> Unit = {}
) {
    val completedCount = uiState.tasks.count { it.isCompleted }
    val totalCount = uiState.tasks.size
    val progressPercent = if (totalCount > 0) (completedCount.toFloat() / totalCount.toFloat()) else 0f
    var showAddTaskDialog by remember { mutableStateOf(false) }

    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .background(Slate950),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // 1. Candidate Hero Card
        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(24.dp),
                colors = CardDefaults.cardColors(containerColor = Slate900),
                border = androidx.compose.foundation.BorderStroke(1.dp, Slate800)
            ) {
                Column(
                    modifier = Modifier.padding(18.dp),
                    verticalArrangement = Arrangement.spacedBy(14.dp)
                ) {
                    // Profile Header
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(12.dp)
                        ) {
                            Box(
                                modifier = Modifier
                                    .size(44.dp)
                                    .clip(CircleShape)
                                    .background(Amber500),
                                contentAlignment = Alignment.Center
                            ) {
                                Text(
                                    text = if (uiState.userName.isNotBlank()) uiState.userName.take(2).uppercase() else "AR",
                                    color = Slate950,
                                    fontWeight = FontWeight.ExtraBold,
                                    fontSize = 16.sp
                                )
                            }
                            Column {
                                Text(
                                    text = if (uiState.userName.isNotBlank()) uiState.userName else "Aspirant Rahul",
                                    style = MaterialTheme.typography.titleMedium,
                                    fontWeight = FontWeight.Bold,
                                    color = Slate100
                                )
                                Text(
                                    text = uiState.userEmail,
                                    style = MaterialTheme.typography.bodySmall,
                                    color = Slate400
                                )
                            }
                        }

                        // Target Rank Badge
                        Surface(
                            color = Amber500.copy(alpha = 0.15f),
                            shape = RoundedCornerShape(12.dp),
                            border = androidx.compose.foundation.BorderStroke(1.dp, Amber500.copy(alpha = 0.4f))
                        ) {
                            Row(
                                modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp),
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.spacedBy(4.dp)
                            ) {
                                Icon(Icons.Default.EmojiEvents, "Rank", tint = Amber400, modifier = Modifier.size(16.dp))
                                Text("AIR Target", style = MaterialTheme.typography.labelSmall, fontWeight = FontWeight.Bold, color = Amber400)
                            }
                        }
                    }

                    // Target Exam Ribbon
                    Surface(
                        modifier = Modifier.fillMaxWidth(),
                        color = Blue900.copy(alpha = 0.35f),
                        shape = RoundedCornerShape(14.dp),
                        border = androidx.compose.foundation.BorderStroke(1.dp, Blue500.copy(alpha = 0.3f))
                    ) {
                        Row(
                            modifier = Modifier.padding(horizontal = 14.dp, vertical = 10.dp),
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            Icon(Icons.Default.Flag, "Target", tint = Blue500, modifier = Modifier.size(18.dp))
                            Text(
                                text = "Mission: " + uiState.targetExam,
                                style = MaterialTheme.typography.bodyMedium,
                                fontWeight = FontWeight.SemiBold,
                                color = Slate100,
                                maxLines = 1,
                                overflow = TextOverflow.Ellipsis
                            )
                        }
                    }

                    // Stats Grid
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(10.dp)
                    ) {
                        StatTile(
                            modifier = Modifier.weight(1f),
                            icon = "🔥",
                            label = "Study Streak",
                            value = "${uiState.streakDays} Days"
                        )
                        StatTile(
                            modifier = Modifier.weight(1f),
                            icon = "🎯",
                            label = "Daily Target",
                            value = "${uiState.dailyHours} Hours"
                        )
                        StatTile(
                            modifier = Modifier.weight(1f),
                            icon = "⚡",
                            label = "Active Tasks",
                            value = "$completedCount/$totalCount Done"
                        )
                    }
                }
            }
        }

        // 2. Daily Study Planner Section
        item {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text(
                        "Daily Study Planner",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        color = Slate100
                    )
                    Text(
                        "Today's high-yield preparation routine",
                        style = MaterialTheme.typography.labelSmall,
                        color = Slate400
                    )
                }

                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    IconButton(
                        onClick = { showAddTaskDialog = true },
                        modifier = Modifier
                            .size(32.dp)
                            .background(Blue500.copy(alpha = 0.15f), RoundedCornerShape(8.dp))
                    ) {
                        Icon(
                            imageVector = Icons.Default.Add,
                            contentDescription = "Add Task",
                            tint = Blue400,
                            modifier = Modifier.size(18.dp)
                        )
                    }

                    Surface(
                        color = Emerald500.copy(alpha = 0.15f),
                        shape = RoundedCornerShape(10.dp),
                        border = androidx.compose.foundation.BorderStroke(1.dp, Emerald500.copy(alpha = 0.3f))
                    ) {
                        Text(
                            text = "${(progressPercent * 100).toInt()}% Done",
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                            style = MaterialTheme.typography.labelSmall,
                            fontWeight = FontWeight.Bold,
                            color = Emerald500
                        )
                    }
                }
            }
        }

        // Task Items
        items(uiState.tasks, key = { it.id }) { task ->
            TaskCard(task = task, onToggle = { onToggleTask(task.id) })
        }

        // 2.5 CBT Mock Exam Simulator Banner
        item {
            Card(
                onClick = onNavigateToQuiz,
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(20.dp),
                colors = CardDefaults.cardColors(containerColor = Slate900),
                border = androidx.compose.foundation.BorderStroke(1.dp, Amber500.copy(alpha = 0.4f))
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(14.dp),
                        modifier = Modifier.weight(1f)
                    ) {
                        Box(
                            modifier = Modifier
                                .size(44.dp)
                                .clip(RoundedCornerShape(14.dp))
                                .background(Amber500.copy(alpha = 0.2f)),
                            contentAlignment = Alignment.Center
                        ) {
                            Icon(Icons.Default.Timer, "CBT Exam", tint = Amber400, modifier = Modifier.size(24.dp))
                        }
                        Column {
                            Text(
                                "CBT Mock Examination Simulator",
                                style = MaterialTheme.typography.titleSmall,
                                fontWeight = FontWeight.Bold,
                                color = Slate100
                            )
                            Text(
                                "${uiState.quizzes.size} Timed Papers Available • Real Negative Marking",
                                style = MaterialTheme.typography.bodySmall,
                                color = Slate400
                            )
                        }
                    }

                    Icon(Icons.Default.ChevronRight, "Start", tint = Amber400)
                }
            }
        }

        // 3. Leitner Active Recall Flashcards Banner
        item {
            Card(
                onClick = onNavigateToFlashcards,
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(20.dp),
                colors = CardDefaults.cardColors(containerColor = Slate900),
                border = androidx.compose.foundation.BorderStroke(1.dp, Purple500.copy(alpha = 0.4f))
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(14.dp),
                        modifier = Modifier.weight(1f)
                    ) {
                        Box(
                            modifier = Modifier
                                .size(44.dp)
                                .clip(RoundedCornerShape(14.dp))
                                .background(Purple500.copy(alpha = 0.2f)),
                            contentAlignment = Alignment.Center
                        ) {
                            Icon(Icons.Default.Style, "Cards", tint = Purple500, modifier = Modifier.size(24.dp))
                        }
                        Column {
                            Text(
                                "Leitner Active Recall Deck",
                                style = MaterialTheme.typography.titleSmall,
                                fontWeight = FontWeight.Bold,
                                color = Slate100
                            )
                            Text(
                                "${uiState.flashcards.size} High-Yield Concept Cards • Box 1-5 Spaced Repetition",
                                style = MaterialTheme.typography.bodySmall,
                                color = Slate400
                            )
                        }
                    }

                    Icon(Icons.Default.ChevronRight, "Open", tint = Slate400)
                }
            }
        }

        // 4. AI Quick Actions
        item {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text(
                    "Quick AI Study Prompts",
                    style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.Bold,
                    color = Slate100
                )

                val prompts = listOf(
                    "📋 Draft a high-yield 30-day study strategy for ${uiState.targetExam}",
                    "📝 Quiz me on Top 10 most recurring concepts for ${uiState.targetExam}",
                    "🧠 Explain SQL Joins vs Subqueries with exam-oriented mnemonics"
                )

                prompts.forEach { prompt ->
                    OutlinedCard(
                        onClick = { onLaunchChatWithPrompt(prompt.substringAfter(" ")) },
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(14.dp),
                        border = androidx.compose.foundation.BorderStroke(1.dp, Slate800),
                        colors = CardDefaults.outlinedCardColors(containerColor = Slate900)
                    ) {
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(12.dp),
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Text(
                                text = prompt,
                                style = MaterialTheme.typography.bodySmall,
                                color = Slate100,
                                modifier = Modifier.weight(1f)
                            )
                            Icon(Icons.Default.ArrowForward, "Send", tint = Amber400, modifier = Modifier.size(16.dp))
                        }
                    }
                }
            }
        }
    }

    if (showAddTaskDialog) {
        var newTaskTitle by remember { mutableStateOf("") }
        var newTaskSubject by remember { mutableStateOf("DBMS") }
        var newTaskMinutes by remember { mutableStateOf("30") }
        val newTaskPriority = "High"

        AlertDialog(
            onDismissRequest = { showAddTaskDialog = false },
            title = {
                Text("Add Preparation Task", fontWeight = FontWeight.Bold, color = Slate100)
            },
            text = {
                Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    OutlinedTextField(
                        value = newTaskTitle,
                        onValueChange = { newTaskTitle = it },
                        label = { Text("Task Description") },
                        placeholder = { Text("e.g. Revise Distributed Systems") },
                        singleLine = true,
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedTextColor = Slate100,
                            unfocusedTextColor = Slate200,
                            focusedBorderColor = Blue500,
                            unfocusedBorderColor = Slate700
                        ),
                        modifier = Modifier.fillMaxWidth()
                    )

                    Text("Subject Area", style = MaterialTheme.typography.labelSmall, color = Slate400)
                    Row(
                        horizontalArrangement = Arrangement.spacedBy(6.dp),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        listOf("DBMS", "Networks", "Securities", "Quant").forEach { subj ->
                            FilterChip(
                                selected = newTaskSubject == subj,
                                onClick = { newTaskSubject = subj },
                                label = { Text(subj, fontSize = 11.sp) }
                            )
                        }
                    }

                    OutlinedTextField(
                        value = newTaskMinutes,
                        onValueChange = { str -> newTaskMinutes = str.filter { it.isDigit() } },
                        label = { Text("Duration (Minutes)") },
                        singleLine = true,
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedTextColor = Slate100,
                            unfocusedTextColor = Slate200,
                            focusedBorderColor = Blue500,
                            unfocusedBorderColor = Slate700
                        ),
                        modifier = Modifier.fillMaxWidth()
                    )
                }
            },
            confirmButton = {
                Button(
                    onClick = {
                        if (newTaskTitle.isNotBlank()) {
                            val mins = newTaskMinutes.toIntOrNull() ?: 30
                            onAddTask(newTaskTitle.trim(), newTaskSubject, mins, newTaskPriority)
                            showAddTaskDialog = false
                        }
                    },
                    colors = ButtonDefaults.buttonColors(containerColor = Blue500)
                ) {
                    Text("Add Task", color = Slate950, fontWeight = FontWeight.Bold)
                }
            },
            dismissButton = {
                TextButton(onClick = { showAddTaskDialog = false }) {
                    Text("Cancel", color = Slate400)
                }
            },
            containerColor = Slate900,
            tonalElevation = 6.dp
        )
    }
}

@Composable
private fun StatTile(
    modifier: Modifier = Modifier,
    icon: String,
    label: String,
    value: String
) {
    Surface(
        modifier = modifier,
        color = Slate950,
        shape = RoundedCornerShape(14.dp),
        border = androidx.compose.foundation.BorderStroke(1.dp, Slate800)
    ) {
        Column(
            modifier = Modifier.padding(10.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(4.dp)
        ) {
            Text(icon, fontSize = 20.sp)
            Text(value, style = MaterialTheme.typography.bodySmall, fontWeight = FontWeight.ExtraBold, color = Slate100)
            Text(label, style = MaterialTheme.typography.labelSmall, color = Slate400, fontSize = 9.sp)
        }
    }
}

@Composable
private fun TaskCard(
    task: StudyTaskItem,
    onToggle: () -> Unit
) {
    Card(
        onClick = onToggle,
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(
            containerColor = if (task.isCompleted) Slate900.copy(alpha = 0.6f) else Slate900
        ),
        border = androidx.compose.foundation.BorderStroke(
            1.dp,
            if (task.isCompleted) Emerald500.copy(alpha = 0.3f) else Slate800
        )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(14.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Checkbox(
                checked = task.isCompleted,
                onCheckedChange = { onToggle() },
                colors = CheckboxDefaults.colors(
                    checkedColor = Emerald500,
                    checkmarkColor = Slate950,
                    uncheckedColor = Slate600
                )
            )

            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = task.title,
                    style = MaterialTheme.typography.bodyMedium,
                    fontWeight = FontWeight.Medium,
                    color = if (task.isCompleted) Slate400 else Slate100,
                    textDecoration = if (task.isCompleted) TextDecoration.LineThrough else TextDecoration.None
                )
                Spacer(Modifier.height(4.dp))
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Surface(
                        color = Blue900.copy(alpha = 0.4f),
                        shape = RoundedCornerShape(6.dp)
                    ) {
                        Text(
                            text = task.subject,
                            modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp),
                            style = MaterialTheme.typography.labelSmall,
                            color = Blue500,
                            fontSize = 10.sp
                        )
                    }

                    Surface(
                        color = if (task.priority == "High") Rose500.copy(alpha = 0.15f) else Amber500.copy(alpha = 0.15f),
                        shape = RoundedCornerShape(6.dp)
                    ) {
                        Text(
                            text = "${task.estimatedMinutes} mins • ${task.priority} Priority",
                            modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp),
                            style = MaterialTheme.typography.labelSmall,
                            color = if (task.priority == "High") Rose500 else Amber400,
                            fontSize = 10.sp
                        )
                    }
                }
            }
        }
    }
}
