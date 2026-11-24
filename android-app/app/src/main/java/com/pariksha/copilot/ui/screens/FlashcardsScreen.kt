package com.pariksha.copilot.ui.screens

import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
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
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.pariksha.copilot.AppUiState
import com.pariksha.copilot.data.FlashcardItem
import com.pariksha.copilot.ui.theme.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun FlashcardsScreen(
    uiState: AppUiState,
    onFlipCard: () -> Unit,
    onReviewCard: (Boolean) -> Unit
) {
    val cards = uiState.flashcards
    val activeIndex = uiState.activeFlashcardIndex.coerceIn(0, (cards.size - 1).coerceAtLeast(0))
    var activeCardIndex by remember(activeIndex) { mutableIntStateOf(activeIndex) }
    val currentCard = cards.getOrNull(activeCardIndex.coerceIn(0, (cards.size - 1).coerceAtLeast(0)))

    // Box counts
    val boxCounts = (1..5).associateWith { boxNum ->
        cards.count { it.box == boxNum }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Text(
                                "Leitner Active Recall",
                                style = MaterialTheme.typography.titleMedium.copy(
                                    fontWeight = FontWeight.Bold,
                                    color = Color.White
                                )
                            )
                            Spacer(Modifier.width(8.dp))
                            Surface(
                                color = Amber500.copy(alpha = 0.2f),
                                shape = RoundedCornerShape(4.dp)
                            ) {
                                Text(
                                    "5-Box Spaced Repetition",
                                    modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp),
                                    style = MaterialTheme.typography.labelSmall.copy(
                                        color = Amber400,
                                        fontWeight = FontWeight.SemiBold
                                    )
                                )
                            }
                        }
                        Text(
                            "Master high-yield concepts through systematic spaced review",
                            style = MaterialTheme.typography.labelSmall.copy(
                                color = Slate400
                            )
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
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(horizontal = 16.dp, vertical = 12.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Leitner Box Distribution Bar
            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(12.dp),
                    colors = CardDefaults.cardColors(containerColor = Slate900)
                ) {
                    Column(modifier = Modifier.padding(14.dp)) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(
                                "Retention Mastery Distribution",
                                style = MaterialTheme.typography.labelMedium.copy(
                                    fontWeight = FontWeight.SemiBold,
                                    color = Slate200
                                )
                            )
                            Text(
                                "${cards.size} Total Cards",
                                style = MaterialTheme.typography.labelSmall.copy(color = Amber400)
                            )
                        }
                        Spacer(Modifier.height(10.dp))
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            (1..5).forEach { boxNum ->
                                val count = boxCounts[boxNum] ?: 0
                                BoxCardIndicator(
                                    box = boxNum,
                                    count = count,
                                    modifier = Modifier.weight(1f)
                                )
                            }
                        }
                    }
                }
            }

            // Current Flashcard Interactive Surface
            item {
                if (currentCard != null) {
                    FlashcardInteractiveSurface(
                        card = currentCard,
                        cardIndex = activeIndex + 1,
                        totalCards = cards.size,
                        isFlipped = uiState.isFlashcardFlipped,
                        onFlip = onFlipCard,
                        onReview = onReviewCard
                    )
                } else {
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(200.dp),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(
                            "No flashcards loaded yet.",
                            color = Slate400,
                            style = MaterialTheme.typography.bodyMedium
                        )
                    }
                }
            }

            // Card Navigation Slider / Selector
            item {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    OutlinedButton(
                        onClick = {
                            if (activeCardIndex > 0) activeCardIndex--
                        },
                        enabled = activeCardIndex > 0,
                        colors = ButtonDefaults.outlinedButtonColors(
                            contentColor = Amber400
                        ),
                        border = ButtonDefaults.outlinedButtonBorder.copy(
                            brush = androidx.compose.ui.graphics.SolidColor(Slate700)
                        )
                    ) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Previous Card", modifier = Modifier.size(16.dp))
                        Spacer(Modifier.width(6.dp))
                        Text("Previous")
                    }

                    Text(
                        "Card ${activeCardIndex + 1} of ${cards.size}",
                        style = MaterialTheme.typography.bodySmall.copy(
                            color = Slate300,
                            fontWeight = FontWeight.Medium
                        )
                    )

                    OutlinedButton(
                        onClick = {
                            if (activeCardIndex < cards.size - 1) activeCardIndex++
                        },
                        enabled = activeCardIndex < cards.size - 1,
                        colors = ButtonDefaults.outlinedButtonColors(
                            contentColor = Amber400
                        ),
                        border = ButtonDefaults.outlinedButtonBorder.copy(
                            brush = androidx.compose.ui.graphics.SolidColor(Slate700)
                        )
                    ) {
                        Text("Next")
                        Spacer(Modifier.width(6.dp))
                        Icon(Icons.Default.ArrowForward, contentDescription = "Next Card", modifier = Modifier.size(16.dp))
                    }
                }
            }

            // All Flashcards Quick Glance List
            item {
                Text(
                    "All Deck Cards",
                    style = MaterialTheme.typography.titleSmall.copy(
                        color = Color.White,
                        fontWeight = FontWeight.Bold
                    ),
                    modifier = Modifier.padding(top = 8.dp)
                )
            }

            items(cards) { card ->
                val isSelected = cards.indexOf(card) == activeCardIndex
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable { activeCardIndex = cards.indexOf(card) },
                    shape = RoundedCornerShape(10.dp),
                    colors = CardDefaults.cardColors(
                        containerColor = if (isSelected) Slate800 else Slate900
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
                        Surface(
                            shape = CircleShape,
                            color = when (card.box) {
                                1 -> Rose500.copy(alpha = 0.2f)
                                2 -> Amber500.copy(alpha = 0.2f)
                                3 -> Blue500.copy(alpha = 0.2f)
                                4 -> Purple500.copy(alpha = 0.2f)
                                else -> Emerald500.copy(alpha = 0.2f)
                            },
                            modifier = Modifier.size(32.dp)
                        ) {
                            Box(contentAlignment = Alignment.Center) {
                                Text(
                                    "B${card.box}",
                                    style = MaterialTheme.typography.labelSmall.copy(
                                        fontWeight = FontWeight.Bold,
                                        color = when (card.box) {
                                            1 -> Rose400
                                            2 -> Amber400
                                            3 -> Blue400
                                            4 -> Purple400
                                            else -> Emerald400
                                        }
                                    )
                                )
                            }
                        }

                        Spacer(Modifier.width(12.dp))

                        Column(modifier = Modifier.weight(1f)) {
                            Text(
                                card.question,
                                style = MaterialTheme.typography.bodySmall.copy(
                                    color = Color.White,
                                    fontWeight = FontWeight.Medium
                                ),
                                maxLines = 1
                            )
                            Spacer(Modifier.height(2.dp))
                            Text(
                                "${card.topic} • ${card.difficulty}",
                                style = MaterialTheme.typography.labelSmall.copy(
                                    color = Slate400,
                                    fontSize = 10.sp
                                )
                            )
                        }

                        if (isSelected) {
                            Icon(
                                Icons.Default.CheckCircle,
                                contentDescription = "Active",
                                tint = Amber400,
                                modifier = Modifier.size(18.dp)
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun BoxCardIndicator(
    box: Int,
    count: Int,
    modifier: Modifier = Modifier
) {
    val (label, accentColor) = when (box) {
        1 -> "Box 1" to Rose500
        2 -> "Box 2" to Amber500
        3 -> "Box 3" to Blue500
        4 -> "Box 4" to Purple500
        else -> "Box 5" to Emerald500
    }

    Surface(
        modifier = modifier,
        shape = RoundedCornerShape(8.dp),
        color = accentColor.copy(alpha = 0.12f),
        border = androidx.compose.foundation.BorderStroke(1.dp, accentColor.copy(alpha = 0.35f))
    ) {
        Column(
            modifier = Modifier.padding(vertical = 8.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                count.toString(),
                style = MaterialTheme.typography.titleMedium.copy(
                    fontWeight = FontWeight.Bold,
                    color = accentColor
                )
            )
            Text(
                label,
                style = MaterialTheme.typography.labelSmall.copy(
                    fontSize = 10.sp,
                    color = Slate300
                )
            )
        }
    }
}

@Composable
fun FlashcardInteractiveSurface(
    card: FlashcardItem,
    cardIndex: Int,
    totalCards: Int,
    isFlipped: Boolean,
    onFlip: () -> Unit,
    onReview: (Boolean) -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { onFlip() },
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = Slate900),
        border = CardDefaults.outlinedCardBorder().copy(
            brush = androidx.compose.ui.graphics.SolidColor(if (isFlipped) Blue500.copy(alpha = 0.6f) else Amber500.copy(alpha = 0.6f))
        )
    ) {
        Column(
            modifier = Modifier.padding(20.dp)
        ) {
            // Card Header: Box Level + Topic + Difficulty + Flip hint
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Surface(
                        shape = RoundedCornerShape(4.dp),
                        color = Amber500.copy(alpha = 0.15f)
                    ) {
                        Text(
                            "Box ${card.box} / 5",
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 3.dp),
                            style = MaterialTheme.typography.labelSmall.copy(
                                color = Amber400,
                                fontWeight = FontWeight.Bold
                            )
                        )
                    }
                    Spacer(Modifier.width(8.dp))
                    Surface(
                        shape = RoundedCornerShape(4.dp),
                        color = Slate800
                    ) {
                        Text(
                            card.topic,
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 3.dp),
                            style = MaterialTheme.typography.labelSmall.copy(
                                color = Slate300
                            )
                        )
                    }
                }

                Surface(
                    shape = CircleShape,
                    color = Slate800,
                    modifier = Modifier.size(28.dp)
                ) {
                    Box(contentAlignment = Alignment.Center) {
                        Icon(
                            Icons.Default.FlipCameraAndroid,
                            contentDescription = "Tap to Flip",
                            tint = Amber400,
                            modifier = Modifier.size(16.dp)
                        )
                    }
                }
            }

            Spacer(Modifier.height(20.dp))

            // Front or Back Content
            if (!isFlipped) {
                // FRONT
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 16.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text(
                        "QUESTION",
                        style = MaterialTheme.typography.labelSmall.copy(
                            color = Amber400,
                            fontWeight = FontWeight.Bold,
                            letterSpacing = 1.sp
                        )
                    )
                    Spacer(Modifier.height(12.dp))
                    Text(
                        card.question,
                        style = MaterialTheme.typography.titleMedium.copy(
                            color = Color.White,
                            fontWeight = FontWeight.SemiBold,
                            textAlign = TextAlign.Center,
                            lineHeight = 26.sp
                        ),
                        modifier = Modifier.fillMaxWidth()
                    )
                    Spacer(Modifier.height(20.dp))
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.Center
                    ) {
                        Icon(
                            Icons.Default.TouchApp,
                            contentDescription = null,
                            tint = Slate400,
                            modifier = Modifier.size(14.dp)
                        )
                        Spacer(Modifier.width(6.dp))
                        Text(
                            "Tap card surface to reveal explanation & answer",
                            style = MaterialTheme.typography.labelSmall.copy(color = Slate400)
                        )
                    }
                }
            } else {
                // BACK (REVEALED)
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 12.dp)
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Default.CheckCircle, contentDescription = null, tint = Emerald400, modifier = Modifier.size(16.dp))
                        Spacer(Modifier.width(6.dp))
                        Text(
                            "CORRECT FORMULATION & KEY INSIGHT",
                            style = MaterialTheme.typography.labelSmall.copy(
                                color = Emerald400,
                                fontWeight = FontWeight.Bold,
                                letterSpacing = 1.sp
                            )
                        )
                    }
                    Spacer(Modifier.height(10.dp))
                    Text(
                        card.answer,
                        style = MaterialTheme.typography.bodyMedium.copy(
                            color = Slate100,
                            lineHeight = 22.sp
                        )
                    )
                    Spacer(Modifier.height(14.dp))
                    HorizontalDivider(color = Slate800)
                    Spacer(Modifier.height(14.dp))
                    Text(
                        "Self-Assessment (Leitner Progression):",
                        style = MaterialTheme.typography.labelSmall.copy(
                            color = Slate400,
                            fontWeight = FontWeight.Medium
                        )
                    )
                    Spacer(Modifier.height(10.dp))
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(10.dp)
                    ) {
                        OutlinedButton(
                            onClick = { onReview(false) },
                            modifier = Modifier.weight(1f),
                            shape = RoundedCornerShape(8.dp),
                            colors = ButtonDefaults.outlinedButtonColors(
                                contentColor = Rose400
                            ),
                            border = ButtonDefaults.outlinedButtonBorder.copy(
                                brush = androidx.compose.ui.graphics.SolidColor(Rose500.copy(alpha = 0.5f))
                            )
                        ) {
                            Icon(Icons.Default.Close, contentDescription = null, modifier = Modifier.size(16.dp))
                            Spacer(Modifier.width(6.dp))
                            Text("Reset to Box 1", style = MaterialTheme.typography.labelMedium)
                        }

                        Button(
                            onClick = { onReview(true) },
                            modifier = Modifier.weight(1f),
                            shape = RoundedCornerShape(8.dp),
                            colors = ButtonDefaults.buttonColors(
                                containerColor = Emerald500,
                                contentColor = Color.White
                            )
                        ) {
                            Icon(Icons.Default.Done, contentDescription = null, modifier = Modifier.size(16.dp))
                            Spacer(Modifier.width(6.dp))
                            Text("Got It! (+1 Box)", style = MaterialTheme.typography.labelMedium)
                        }
                    }
                }
            }
        }
    }
}
