package com.pariksha.copilot.network

import com.google.ai.client.generativeai.GenerativeModel
import com.google.ai.client.generativeai.type.*
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow

class GeminiChatService {

    private var currentModel: GenerativeModel? = null
    private var currentChat: com.google.ai.client.generativeai.Chat? = null
    private var currentApiKey: String = ""
    private var currentModelId: String = ""

    private fun getSystemPrompt(targetExam: String): String = """
You are **Pariksha Copilot** — a world-class AI tutor specializing in Indian competitive exam preparation.

## Your Expertise
- Target Exam: $targetExam
- You have deep knowledge of exam patterns, syllabus, previous year questions, and scoring strategies
- You provide structured, exam-focused answers with mnemonics, tables, and key points
- You generate practice questions, explain concepts at multiple difficulty levels, and track preparation progress

## Response Guidelines
1. **Be Exam-Focused**: Every answer should relate to exam preparation — syllabus mapping, question patterns, and scoring strategies
2. **Use Structured Formats**: Tables, bullet points, numbered lists, and bold/italic for key terms
3. **Provide Mnemonics & Shortcuts**: Help students remember facts with memory aids
4. **Include Practice Questions**: End longer explanations with 2-3 MCQs for self-testing
5. **Reference Official Sources**: Cite NCERT, official gazettes, RBI circulars, SEBI regulations where relevant
6. **Be Encouraging**: Motivate students with realistic preparation timelines and strategies
7. **Language**: Respond in the same language the user writes in (Hindi/English/Hinglish)

## Formatting
- Use markdown formatting (headers, bold, lists, tables, code blocks)
- Keep answers concise but comprehensive
- For long topics, provide a summary first, then detailed breakdown
""".trimIndent()

    fun initializeChat(apiKey: String, modelId: String, targetExam: String) {
        if (apiKey == currentApiKey && modelId == currentModelId && currentChat != null) {
            return // Already initialized with same params
        }

        currentApiKey = apiKey
        currentModelId = modelId

        currentModel = GenerativeModel(
            modelName = modelId,
            apiKey = apiKey,
            generationConfig = generationConfig {
                temperature = 0.7f
                topK = 40
                topP = 0.95f
                maxOutputTokens = 8192
            },
            systemInstruction = content {
                text(getSystemPrompt(targetExam))
            }
        )

        currentChat = currentModel!!.startChat()
    }

    suspend fun sendMessage(message: String): String {
        val chat = currentChat ?: throw IllegalStateException("Chat not initialized. Set your API key first.")

        val response = chat.sendMessage(message)
        return response.text ?: "No response generated."
    }

    fun sendMessageStream(message: String): Flow<String> = flow {
        val chat = currentChat ?: throw IllegalStateException("Chat not initialized. Set your API key first.")

        val responseStream = chat.sendMessageStream(message)
        responseStream.collect { chunk ->
            chunk.text?.let { emit(it) }
        }
    }

    fun resetChat(targetExam: String) {
        if (currentApiKey.isNotEmpty() && currentModelId.isNotEmpty()) {
            currentChat = currentModel?.startChat()
        }
    }

    fun isInitialized(): Boolean = currentChat != null && currentApiKey.isNotEmpty()
}
