package com.pariksha.copilot.data

import kotlinx.serialization.Serializable

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

val AVAILABLE_MODELS = listOf(
    ModelInfo("gemini-2.5-flash", "Gemini 2.5 Flash", "Fast, versatile, great for exam prep"),
    ModelInfo("gemini-2.5-pro", "Gemini 2.5 Pro", "Highest quality reasoning"),
    ModelInfo("gemini-2.0-flash", "Gemini 2.0 Flash", "Quick responses, good for summaries"),
    ModelInfo("gemini-1.5-flash", "Gemini 1.5 Flash", "Lightweight, cost-effective"),
    ModelInfo("gemini-1.5-pro", "Gemini 1.5 Pro", "Advanced reasoning, long context")
)

val EXAM_OPTIONS = listOf(
    "SEBI Grade A (IT Stream)",
    "RBI Grade B",
    "UPSC Civil Services",
    "SSC CGL",
    "IBPS PO",
    "SBI PO",
    "GATE CSE",
    "UGC NET",
    "NABARD Grade A",
    "IBBI Grade A",
    "Custom"
)
