package com.pariksha.copilot.ui.screens

import androidx.compose.animation.*
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.pariksha.copilot.AppUiState
import com.pariksha.copilot.data.QuizItem
import com.pariksha.copilot.data.QuizQuestion
import com.pariksha.copilot.ui.theme.*

private val Emerald500 = Color(0xFF10B981)
private val Emerald400 = Color(0xFF34D399)
private val Rose500 = Color(0xFFF43F5E)
private val Rose400 = Color(0xFFFB7185)

@Composable
fun QuizScreen(
    uiState: AppUiState,
    onStartQuiz: (QuizItem) -> Unit,
    onSelectOption: (Int) -> Unit,
    onNextQuestion: () -> Unit,
    onPrevQuestion: () -> Unit,
    onJumpToQuestion: (Int) -> Unit,
    onSubmitQuiz: () -> Unit,
    onRetakeQuiz: () -> Unit,
    onExitQuiz: () -> Unit
) {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Slate950)
    ) {
        when {
            uiState.activeQuiz == null -> {
                QuizLibraryView(
                    quizzes = uiState.quizzes,
                    targetExam = uiState.targetExam,
                    onStartQuiz = onStartQuiz
                )
            }
            uiState.quizAttemptResult != null -> {
                QuizResultView(
                    quiz = uiState.activeQuiz,
                    result = uiState.quizAttemptResult,
                    onRetakeQuiz = onRetakeQuiz,
                    onExitQuiz = onExitQuiz
                )
            }
            else -> {
                ActiveQuizCbtView(
                    quiz = uiState.activeQuiz,
                    currentIndex = uiState.activeQuizQuestionIndex,
                    selectedAnswers = uiState.selectedQuizAnswers,
                    timeLeftSeconds = uiState.quizTimeLeftSeconds,
                    onSelectOption = onSelectOption,
                    onNextQuestion = onNextQuestion,
                    onPrevQuestion = onPrevQuestion,
                    onJumpToQuestion = onJumpToQuestion,
                    onSubmitQuiz = onSubmitQuiz,
                    onExitQuiz = onExitQuiz
                )
            }
        }
    }
}

// ==========================================
// 1. QUIZ LIBRARY & CBT OVERVIEW
// ==========================================

@Composable
private fun QuizLibraryView(
    quizzes: List<QuizItem>,
    targetExam: String,
    onStartQuiz: (QuizItem) -> Unit
) {
    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .padding(horizontal = 16.dp, vertical = 20.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        item {
            // Header Banner
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = Slate900),
                shape = RoundedCornerShape(20.dp),
                border = androidx.compose.foundation.BorderStroke(1.dp, Slate800)
            ) {
                Column(modifier = Modifier.padding(20.dp)) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Surface(
                            shape = CircleShape,
                            color = Blue500.copy(alpha = 0.15f),
                            modifier = Modifier.size(36.dp)
                        ) {
                            Box(contentAlignment = Alignment.Center) {
                                Icon(
                                    imageVector = Icons.Default.Quiz,
                                    contentDescription = null,
                                    tint = Blue400,
                                    modifier = Modifier.size(20.dp)
                                )
                            }
                        }
                        Column {
                            Text(
                                "CBT Examination Simulator",
                                style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold),
                                color = Slate100
                            )
                            Text(
                                "Timed Mock Papers • Negative Marking Analysis",
                                style = MaterialTheme.typography.labelSmall,
                                color = Slate400
                            )
                        }
                    }

                    Spacer(modifier = Modifier.height(14.dp))
                    Text(
                        "Simulate official computer-based exam conditions for $targetExam. Build question selection accuracy and speed under countdown timer pressure.",
                        style = MaterialTheme.typography.bodySmall,
                        color = Slate300,
                        lineHeight = 20.sp
                    )

                    Spacer(modifier = Modifier.height(14.dp))
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        CbtStatBadge(
                            label = "Test Standard",
                            value = "Mains / Phase 2",
                            color = Amber400
                        )
                        CbtStatBadge(
                            label = "Marking Scheme",
                            value = "+1.00 / -0.25",
                            color = Blue400
                        )
                        CbtStatBadge(
                            label = "Available Sets",
                            value = "${quizzes.size} Papers",
                            color = Emerald400
                        )
                    }
                }
            }
        }

        item {
            Text(
                "Available Mock Examination Sets",
                style = MaterialTheme.typography.titleSmall.copy(fontWeight = FontWeight.Bold),
                color = Slate200,
                modifier = Modifier.padding(start = 4.dp, top = 4.dp)
            )
        }

        items(quizzes) { quiz ->
            QuizPaperCard(quiz = quiz, onStartQuiz = { onStartQuiz(quiz) })
        }
    }
}

@Composable
private fun QuizPaperCard(
    quiz: QuizItem,
    onStartQuiz: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Slate900),
        shape = RoundedCornerShape(16.dp),
        border = androidx.compose.foundation.BorderStroke(1.dp, Slate800)
    ) {
        Column(modifier = Modifier.padding(18.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Surface(
                    shape = RoundedCornerShape(8.dp),
                    color = Blue500.copy(alpha = 0.15f),
                    border = androidx.compose.foundation.BorderStroke(1.dp, Blue500.copy(alpha = 0.25f))
                ) {
                    Text(
                        text = quiz.subject,
                        modifier = Modifier.padding(horizontal = 10.dp, vertical = 4.dp),
                        style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.SemiBold),
                        color = Blue400
                    )
                }

                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    Icon(
                        imageVector = Icons.Default.Timer,
                        contentDescription = null,
                        tint = Amber400,
                        modifier = Modifier.size(16.dp)
                    )
                    Text(
                        "${quiz.durationMinutes} Mins",
                        style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold),
                        color = Amber400
                    )
                }
            }

            Spacer(modifier = Modifier.height(12.dp))
            Text(
                text = quiz.title,
                style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold),
                color = Slate100
            )
            Spacer(modifier = Modifier.height(6.dp))
            Text(
                text = quiz.description,
                style = MaterialTheme.typography.bodySmall,
                color = Slate400,
                maxLines = 3,
                overflow = TextOverflow.Ellipsis
            )

            Spacer(modifier = Modifier.height(16.dp))
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "${quiz.questions.size} Questions • 10 Marks",
                    style = MaterialTheme.typography.labelMedium,
                    color = Slate300
                )

                Button(
                    onClick = onStartQuiz,
                    colors = ButtonDefaults.buttonColors(
                        containerColor = Amber500,
                        contentColor = Slate950
                    ),
                    shape = RoundedCornerShape(10.dp),
                    contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp)
                ) {
                    Text(
                        "Start Exam →",
                        style = MaterialTheme.typography.labelLarge.copy(fontWeight = FontWeight.Bold)
                    )
                }
            }
        }
    }
}

// ==========================================
// 2. ACTIVE CBT EXAMINATION VIEW
// ==========================================

@Composable
private fun ActiveQuizCbtView(
    quiz: QuizItem,
    currentIndex: Int,
    selectedAnswers: Map<Int, Int>,
    timeLeftSeconds: Int,
    onSelectOption: (Int) -> Unit,
    onNextQuestion: () -> Unit,
    onPrevQuestion: () -> Unit,
    onJumpToQuestion: (Int) -> Unit,
    onSubmitQuiz: () -> Unit,
    onExitQuiz: () -> Unit
) {
    val currentQuestion = quiz.questions.getOrNull(currentIndex) ?: return
    var showSubmitConfirm by remember { mutableStateOf(false) }

    val minutes = timeLeftSeconds / 60
    val seconds = timeLeftSeconds % 60
    val formattedTime = String.format("%02d:%02d", minutes, seconds)
    val timerColor = when {
        timeLeftSeconds < 60 -> Rose400
        timeLeftSeconds < 180 -> Amber400
        else -> Slate200
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        // Top CBT Action Bar
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            IconButton(
                onClick = onExitQuiz,
                modifier = Modifier
                    .size(36.dp)
                    .background(Slate900, CircleShape)
            ) {
                Icon(
                    imageVector = Icons.Default.Close,
                    contentDescription = "Exit CBT",
                    tint = Slate300,
                    modifier = Modifier.size(18.dp)
                )
            }

            // Countdown Timer Pill
            Surface(
                shape = RoundedCornerShape(12.dp),
                color = Slate900,
                border = androidx.compose.foundation.BorderStroke(1.dp, timerColor.copy(alpha = 0.4f))
            ) {
                Row(
                    modifier = Modifier.padding(horizontal = 14.dp, vertical = 6.dp),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(6.dp)
                ) {
                    Icon(
                        imageVector = Icons.Default.Timer,
                        contentDescription = null,
                        tint = timerColor,
                        modifier = Modifier.size(16.dp)
                    )
                    Text(
                        text = formattedTime,
                        style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold),
                        color = timerColor
                    )
                }
            }

            // Submit Button
            Button(
                onClick = { showSubmitConfirm = true },
                colors = ButtonDefaults.buttonColors(
                    containerColor = Emerald500,
                    contentColor = Slate950
                ),
                shape = RoundedCornerShape(10.dp),
                contentPadding = PaddingValues(horizontal = 14.dp, vertical = 6.dp)
            ) {
                Text(
                    "Submit",
                    style = MaterialTheme.typography.labelMedium.copy(fontWeight = FontWeight.Bold)
                )
            }
        }

        Spacer(modifier = Modifier.height(14.dp))

        // Question Palette (1..N)
        Text(
            text = "Question Palette (${selectedAnswers.size}/${quiz.questions.size} Answered)",
            style = MaterialTheme.typography.labelSmall,
            color = Slate400
        )
        Spacer(modifier = Modifier.height(6.dp))
        LazyRow(
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            modifier = Modifier.fillMaxWidth()
        ) {
            itemsIndexed(quiz.questions) { idx, _ ->
                val isAnswered = selectedAnswers.containsKey(idx)
                val isCurrent = idx == currentIndex

                Box(
                    modifier = Modifier
                        .size(38.dp)
                        .clip(RoundedCornerShape(8.dp))
                        .background(
                            when {
                                isCurrent -> Amber500.copy(alpha = 0.25f)
                                isAnswered -> Emerald500.copy(alpha = 0.2f)
                                else -> Slate900
                            }
                        )
                        .border(
                            width = if (isCurrent) 2.dp else 1.dp,
                            color = when {
                                isCurrent -> Amber400
                                isAnswered -> Emerald500
                                else -> Slate800
                            },
                            shape = RoundedCornerShape(8.dp)
                        )
                        .clickable { onJumpToQuestion(idx) },
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = "${idx + 1}",
                        style = MaterialTheme.typography.labelMedium.copy(fontWeight = FontWeight.Bold),
                        color = when {
                            isCurrent -> Amber400
                            isAnswered -> Emerald400
                            else -> Slate300
                        }
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Active Question Card
        Card(
            modifier = Modifier
                .weight(1f)
                .fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = Slate900),
            shape = RoundedCornerShape(18.dp),
            border = androidx.compose.foundation.BorderStroke(1.dp, Slate800)
        ) {
            LazyColumn(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(18.dp),
                verticalArrangement = Arrangement.spacedBy(14.dp)
            ) {
                item {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = "Question ${currentIndex + 1} of ${quiz.questions.size}",
                            style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold),
                            color = Amber400
                        )
                        Text(
                            text = "+1.00 / -0.25 Marks",
                            style = MaterialTheme.typography.labelSmall,
                            color = Slate400
                        )
                    }

                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = currentQuestion.prompt,
                        style = MaterialTheme.typography.bodyMedium.copy(
                            fontWeight = FontWeight.SemiBold,
                            fontSize = 15.sp
                        ),
                        color = Slate100,
                        lineHeight = 22.sp
                    )
                }

                itemsIndexed(currentQuestion.options) { optIdx, optText ->
                    val isSelected = selectedAnswers[currentIndex] == optIdx
                    OptionCard(
                        text = optText,
                        isSelected = isSelected,
                        onClick = { onSelectOption(optIdx) }
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(14.dp))

        // Bottom Navigation (Prev / Next)
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            OutlinedButton(
                onClick = onPrevQuestion,
                enabled = currentIndex > 0,
                colors = ButtonDefaults.outlinedButtonColors(
                    contentColor = Slate200,
                    disabledContentColor = Slate600
                ),
                shape = RoundedCornerShape(10.dp)
            ) {
                Text("← Previous")
            }

            Button(
                onClick = {
                    if (currentIndex < quiz.questions.size - 1) {
                        onNextQuestion()
                    } else {
                        showSubmitConfirm = true
                    }
                },
                colors = ButtonDefaults.buttonColors(
                    containerColor = if (currentIndex == quiz.questions.size - 1) Emerald500 else Amber500,
                    contentColor = Slate950
                ),
                shape = RoundedCornerShape(10.dp)
            ) {
                Text(
                    if (currentIndex < quiz.questions.size - 1) "Next Question →" else "Review & Submit ✓",
                    fontWeight = FontWeight.Bold
                )
            }
        }
    }

    if (showSubmitConfirm) {
        AlertDialog(
            onDismissRequest = { showSubmitConfirm = false },
            title = {
                Text(
                    "Submit CBT Mock Exam?",
                    style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold),
                    color = Slate100
                )
            },
            text = {
                Text(
                    "You have answered ${selectedAnswers.size} out of ${quiz.questions.size} questions with $formattedTime remaining. Do you wish to calculate your final All India Rank score?",
                    color = Slate300
                )
            },
            confirmButton = {
                Button(
                    onClick = {
                        showSubmitConfirm = false
                        onSubmitQuiz()
                    },
                    colors = ButtonDefaults.buttonColors(containerColor = Emerald500, contentColor = Slate950)
                ) {
                    Text("Submit Test Now", fontWeight = FontWeight.Bold)
                }
            },
            dismissButton = {
                TextButton(onClick = { showSubmitConfirm = false }) {
                    Text("Return to Test", color = Slate400)
                }
            },
            containerColor = Slate900,
            tonalElevation = 8.dp
        )
    }
}

@Composable
private fun OptionCard(
    text: String,
    isSelected: Boolean,
    onClick: () -> Unit
) {
    Surface(
        onClick = onClick,
        shape = RoundedCornerShape(12.dp),
        color = if (isSelected) Amber500.copy(alpha = 0.15f) else Slate800.copy(alpha = 0.5f),
        border = androidx.compose.foundation.BorderStroke(
            width = if (isSelected) 1.5.dp else 1.dp,
            color = if (isSelected) Amber400 else Slate700
        ),
        modifier = Modifier.fillMaxWidth()
    ) {
        Row(
            modifier = Modifier.padding(14.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Surface(
                shape = CircleShape,
                color = if (isSelected) Amber400 else Slate700,
                modifier = Modifier.size(24.dp)
            ) {
                Box(contentAlignment = Alignment.Center) {
                    if (isSelected) {
                        Icon(
                            imageVector = Icons.Default.Check,
                            contentDescription = null,
                            tint = Slate950,
                            modifier = Modifier.size(14.dp)
                        )
                    }
                }
            }

            Text(
                text = text,
                style = MaterialTheme.typography.bodyMedium,
                color = if (isSelected) Slate100 else Slate300,
                lineHeight = 20.sp
            )
        }
    }
}

// ==========================================
// 3. CBT SCORE CARD & ANSWER KEY REVIEW
// ==========================================

@Composable
private fun QuizResultView(
    quiz: QuizItem,
    result: com.pariksha.copilot.data.QuizAttemptResult,
    onRetakeQuiz: () -> Unit,
    onExitQuiz: () -> Unit
) {
    val isGoodScore = result.scorePercentage >= 60.0
    val resultColor = if (isGoodScore) Emerald400 else Amber400

    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        item {
            // Score Summary Card
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = Slate900),
                shape = RoundedCornerShape(20.dp),
                border = androidx.compose.foundation.BorderStroke(1.dp, resultColor.copy(alpha = 0.4f))
            ) {
                Column(
                    modifier = Modifier.padding(24.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Surface(
                        shape = CircleShape,
                        color = resultColor.copy(alpha = 0.15f),
                        modifier = Modifier.size(56.dp)
                    ) {
                        Box(contentAlignment = Alignment.Center) {
                            Icon(
                                imageVector = if (isGoodScore) Icons.Default.Star else Icons.Default.Analytics,
                                contentDescription = null,
                                tint = resultColor,
                                modifier = Modifier.size(32.dp)
                            )
                        }
                    }

                    Spacer(modifier = Modifier.height(12.dp))
                    Text(
                        text = "CBT Mock Performance Report",
                        style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold),
                        color = Slate100
                    )
                    Text(
                        text = quiz.title,
                        style = MaterialTheme.typography.bodySmall,
                        color = Slate400
                    )

                    Spacer(modifier = Modifier.height(16.dp))
                    Text(
                        text = "${result.correctCount} / ${result.totalQuestions}",
                        style = MaterialTheme.typography.displaySmall.copy(fontWeight = FontWeight.ExtraBold),
                        color = resultColor
                    )
                    Text(
                        text = String.format("%.1f%% Final Score", result.scorePercentage),
                        style = MaterialTheme.typography.titleSmall.copy(fontWeight = FontWeight.SemiBold),
                        color = Slate300
                    )

                    Spacer(modifier = Modifier.height(16.dp))
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceEvenly
                    ) {
                        CbtStatBadge(
                            label = "Correct",
                            value = "${result.correctCount}",
                            color = Emerald400
                        )
                        CbtStatBadge(
                            label = "Incorrect",
                            value = "${result.totalQuestions - result.correctCount}",
                            color = Rose400
                        )
                        CbtStatBadge(
                            label = "Time Taken",
                            value = "${result.timeSpentSeconds}s",
                            color = Blue400
                        )
                    }

                    Spacer(modifier = Modifier.height(20.dp))
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        OutlinedButton(
                            onClick = onExitQuiz,
                            modifier = Modifier.weight(1f),
                            shape = RoundedCornerShape(10.dp),
                            colors = ButtonDefaults.outlinedButtonColors(contentColor = Slate300)
                        ) {
                            Text("Test Library")
                        }

                        Button(
                            onClick = onRetakeQuiz,
                            modifier = Modifier.weight(1f),
                            shape = RoundedCornerShape(10.dp),
                            colors = ButtonDefaults.buttonColors(containerColor = Amber500, contentColor = Slate950)
                        ) {
                            Text("Retake Test", fontWeight = FontWeight.Bold)
                        }
                    }
                }
            }
        }

        item {
            Text(
                "Complete Answer Key & Rationales",
                style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold),
                color = Slate100,
                modifier = Modifier.padding(start = 4.dp, top = 6.dp)
            )
        }

        itemsIndexed(quiz.questions) { idx, q ->
            val userAnswer = result.answers[idx]
            val isCorrect = userAnswer != null && userAnswer == q.correctOptionIndex

            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = Slate900),
                shape = RoundedCornerShape(16.dp),
                border = androidx.compose.foundation.BorderStroke(
                    1.dp,
                    if (isCorrect) Emerald500.copy(alpha = 0.3f) else Rose500.copy(alpha = 0.3f)
                )
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = "Question ${idx + 1}",
                            style = MaterialTheme.typography.labelMedium.copy(fontWeight = FontWeight.Bold),
                            color = Amber400
                        )

                        Surface(
                            shape = RoundedCornerShape(6.dp),
                            color = if (isCorrect) Emerald500.copy(alpha = 0.15f) else Rose500.copy(alpha = 0.15f)
                        ) {
                            Text(
                                text = if (isCorrect) "✓ Correct (+1.0)" else "✗ Incorrect (-0.25)",
                                modifier = Modifier.padding(horizontal = 8.dp, vertical = 2.dp),
                                style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold),
                                color = if (isCorrect) Emerald400 else Rose400
                            )
                        }
                    }

                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = q.prompt,
                        style = MaterialTheme.typography.bodyMedium.copy(fontWeight = FontWeight.SemiBold),
                        color = Slate100
                    )

                    Spacer(modifier = Modifier.height(10.dp))
                    Text(
                        text = "Correct Answer: ${q.options.getOrNull(q.correctOptionIndex) ?: ""}",
                        style = MaterialTheme.typography.bodySmall.copy(fontWeight = FontWeight.Bold),
                        color = Emerald400
                    )

                    if (userAnswer != null && userAnswer != q.correctOptionIndex) {
                        Text(
                            text = "Your Answer: ${q.options.getOrNull(userAnswer) ?: ""}",
                            style = MaterialTheme.typography.bodySmall,
                            color = Rose400
                        )
                    }

                    Spacer(modifier = Modifier.height(10.dp))
                    Surface(
                        shape = RoundedCornerShape(8.dp),
                        color = Slate800.copy(alpha = 0.5f),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Column(modifier = Modifier.padding(10.dp)) {
                            Text(
                                text = "💡 Detailed Rationale:",
                                style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold),
                                color = Amber400
                            )
                            Spacer(modifier = Modifier.height(4.dp))
                            Text(
                                text = q.explanation,
                                style = MaterialTheme.typography.bodySmall,
                                color = Slate300,
                                lineHeight = 18.sp
                            )
                            if (q.citation.isNotBlank()) {
                                Spacer(modifier = Modifier.height(6.dp))
                                Text(
                                    text = "📖 Source Citation: ${q.citation}",
                                    style = MaterialTheme.typography.labelSmall,
                                    color = Slate500
                                )
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun CbtStatBadge(
    label: String,
    value: String,
    color: Color
) {
    Surface(
        shape = RoundedCornerShape(10.dp),
        color = color.copy(alpha = 0.12f),
        border = androidx.compose.foundation.BorderStroke(1.dp, color.copy(alpha = 0.25f))
    ) {
        Column(
            modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                text = value,
                style = MaterialTheme.typography.labelMedium.copy(fontWeight = FontWeight.Bold),
                color = color
            )
            Text(
                text = label,
                style = MaterialTheme.typography.labelSmall.copy(fontSize = 10.sp),
                color = Slate400
            )
        }
    }
}
