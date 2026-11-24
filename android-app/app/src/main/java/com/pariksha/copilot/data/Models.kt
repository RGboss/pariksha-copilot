package com.pariksha.copilot.data

import kotlinx.serialization.Serializable

@Serializable
data class UserProfile(
    val name: String,
    val email: String,
    val targetExam: String = "SEBI Grade A (IT Stream)",
    val token: String = "",
    val isLoggedIn: Boolean = false,
    val streakDays: Int = 7,
    val dailyTargetHours: Int = 5
)

@Serializable
data class ChatMessage(
    val id: String = java.util.UUID.randomUUID().toString(),
    val role: String, // "user" or "model"
    val content: String,
    val timestamp: Long = System.currentTimeMillis(),
    val isLoading: Boolean = false,
    val isError: Boolean = false
)

@Serializable
data class ModelInfo(
    val id: String,
    val name: String,
    val description: String = ""
)

@Serializable
data class FlashcardItem(
    val id: String,
    val question: String,
    val answer: String,
    val topic: String,
    val box: Int = 1, // Leitner box 1 to 5
    val difficulty: String = "Medium",
    val isFlipped: Boolean = false
)

@Serializable
data class StudyTaskItem(
    val id: String,
    val title: String,
    val subject: String,
    val estimatedMinutes: Int,
    val isCompleted: Boolean = false,
    val priority: String = "High" // High, Medium, Low
)

val AVAILABLE_MODELS = listOf(
    ModelInfo("gemini-2.5-flash", "Gemini 2.5 Flash", "Super fast, high quality exam tutor"),
    ModelInfo("gemini-2.5-pro", "Gemini 2.5 Pro", "Deepest reasoning for complex mains"),
    ModelInfo("gemini-2.0-flash", "Gemini 2.0 Flash", "Latest generation low-latency model"),
    ModelInfo("gemini-1.5-flash", "Gemini 1.5 Flash", "Lightweight, cost-effective"),
    ModelInfo("gemini-1.5-pro", "Gemini 1.5 Pro", "Long context analysis for full papers")
)

val EXAM_OPTIONS = listOf(
    "SEBI Grade A (IT Stream)",
    "SBI SCO (Deputy Manager IT)",
    "IBPS SO (IT Officer Scale-I)",
    "RBI Grade B (General/DEPR)",
    "UPSC CSE 2027 (IAS/IPS)",
    "SSC CGL (Tier 1 & 2)",
    "Railways RRB NTPC",
    "GATE CSE / IT",
    "NABARD Grade A Officer",
    "Custom / State PSC"
)

val DEFAULT_FLASHCARDS = listOf(
    FlashcardItem(
        id = "fc-1",
        question = "What is the primary role and statutory objective of SEBI under the SEBI Act, 1992?",
        answer = "To protect the interests of investors in securities, promote the development of, and regulate the securities market in India through registration, insider trading prevention, and market surveillance.",
        topic = "Securities Market Regulations",
        box = 1,
        difficulty = "High Yield"
    ),
    FlashcardItem(
        id = "fc-2",
        question = "What are the 4 ACID properties in Database Management Systems (DBMS)?",
        answer = "1. Atomicity (All or nothing)\n2. Consistency (Maintains schema constraints)\n3. Isolation (Transactions execute independently)\n4. Durability (Committed changes survive system crash)",
        topic = "Database Management Systems",
        box = 2,
        difficulty = "Core Concept"
    ),
    FlashcardItem(
        id = "fc-3",
        question = "Differentiate between TCP and UDP protocols in Computer Networking.",
        answer = "TCP is connection-oriented, reliable (3-way handshake, retransmissions, flow control via sliding window). UDP is connectionless, unreliable, low-overhead, ideal for real-time streaming and DNS queries.",
        topic = "Computer Networks",
        box = 3,
        difficulty = "High Yield"
    ),
    FlashcardItem(
        id = "fc-4",
        question = "What is the difference between Symmetric and Asymmetric Key Encryption?",
        answer = "Symmetric uses a single secret key for encryption & decryption (AES, DES). Asymmetric uses a mathematically linked public-private key pair (RSA, ECC), solving the key exchange problem.",
        topic = "Cybersecurity & IT",
        box = 1,
        difficulty = "Mains Level"
    )
)

val DEFAULT_TASKS = listOf(
    StudyTaskItem(
        id = "task-1",
        title = "Solve 25 MCQs on SQL Normalization (1NF, 2NF, 3NF, BCNF)",
        subject = "DBMS",
        estimatedMinutes = 45,
        isCompleted = false,
        priority = "High"
    ),
    StudyTaskItem(
        id = "task-2",
        title = "Revise SEBI Regulations & ICDR Guidelines (Chapter 3)",
        subject = "Securities Law",
        estimatedMinutes = 60,
        isCompleted = true,
        priority = "High"
    ),
    StudyTaskItem(
        id = "task-3",
        title = "Active Recall Flashcards: OSI vs TCP/IP Protocol Stack",
        subject = "Networking",
        estimatedMinutes = 30,
        isCompleted = false,
        priority = "Medium"
    ),
    StudyTaskItem(
        id = "task-4",
        title = "Read Monthly Financial & Banking Awareness Capsule",
        subject = "General Awareness",
        estimatedMinutes = 40,
        isCompleted = false,
        priority = "Medium"
    )
)
