package com.pariksha.copilot

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.pariksha.copilot.data.AVAILABLE_MODELS
import com.pariksha.copilot.data.ChatMessage
import com.pariksha.copilot.data.SettingsRepository
import com.pariksha.copilot.network.GeminiChatService
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch

data class AppUiState(
    val apiKey: String = "",
    val serverUrl: String = "http://192.168.29.94:8000",
    val selectedModel: String = "gemini-2.5-flash",
    val userName: String = "",
    val targetExam: String = "SEBI Grade A (IT Stream)",
    val messages: List<ChatMessage> = emptyList(),
    val isGenerating: Boolean = false,
    val errorMessage: String? = null,
    val isApiKeyConfigured: Boolean = false,
    val streamingText: String = ""
)

class ChatViewModel(application: Application) : AndroidViewModel(application) {

    private val settingsRepo = SettingsRepository(application)
    private val chatService = GeminiChatService()

    private val _uiState = MutableStateFlow(AppUiState())
    val uiState: StateFlow<AppUiState> = _uiState.asStateFlow()

    init {
        // Collect all settings flows
        viewModelScope.launch {
            combine(
                settingsRepo.apiKey,
                settingsRepo.serverUrl,
                settingsRepo.selectedModel,
                settingsRepo.userName,
                settingsRepo.targetExam
            ) { apiKey, serverUrl, model, name, exam ->
                AppUiState(
                    apiKey = apiKey,
                    serverUrl = serverUrl,
                    selectedModel = model,
                    userName = name,
                    targetExam = exam,
                    isApiKeyConfigured = apiKey.isNotBlank(),
                    messages = _uiState.value.messages,
                    isGenerating = _uiState.value.isGenerating,
                    errorMessage = _uiState.value.errorMessage,
                    streamingText = _uiState.value.streamingText
                )
            }.collect { state ->
                _uiState.value = state
                // Initialize chat service if key is available
                if (state.apiKey.isNotBlank()) {
                    try {
                        chatService.initializeChat(state.apiKey, state.selectedModel, state.targetExam)
                    } catch (e: Exception) {
                        _uiState.value = _uiState.value.copy(
                            errorMessage = "Failed to initialize Gemini: ${e.message}"
                        )
                    }
                }
            }
        }
    }

    fun saveApiKey(key: String) {
        viewModelScope.launch {
            settingsRepo.saveApiKey(key.trim())
        }
    }

    fun clearApiKey() {
        viewModelScope.launch {
            settingsRepo.clearApiKey()
            _uiState.value = _uiState.value.copy(
                messages = emptyList(),
                isApiKeyConfigured = false
            )
        }
    }

    fun saveServerUrl(url: String) {
        viewModelScope.launch {
            settingsRepo.saveServerUrl(url.trim())
        }
    }

    fun saveSelectedModel(model: String) {
        viewModelScope.launch {
            settingsRepo.saveSelectedModel(model)
            // Reinitialize chat with new model
            val state = _uiState.value
            if (state.apiKey.isNotBlank()) {
                chatService.initializeChat(state.apiKey, model, state.targetExam)
            }
        }
    }

    fun saveUserName(name: String) {
        viewModelScope.launch {
            settingsRepo.saveUserName(name.trim())
        }
    }

    fun saveTargetExam(exam: String) {
        viewModelScope.launch {
            settingsRepo.saveTargetExam(exam)
            chatService.resetChat(exam)
        }
    }

    fun sendMessage(text: String) {
        if (text.isBlank() || _uiState.value.isGenerating) return

        val state = _uiState.value
        if (!state.isApiKeyConfigured) {
            _uiState.value = state.copy(
                errorMessage = "Please configure your Gemini API key in Settings first"
            )
            return
        }

        val userMessage = ChatMessage(role = "user", content = text)

        _uiState.value = _uiState.value.copy(
            messages = _uiState.value.messages + userMessage,
            isGenerating = true,
            errorMessage = null,
            streamingText = ""
        )

        viewModelScope.launch {
            try {
                val fullResponse = StringBuilder()
                chatService.sendMessageStream(text).collect { chunk ->
                    fullResponse.append(chunk)
                    _uiState.value = _uiState.value.copy(
                        streamingText = fullResponse.toString()
                    )
                }

                val modelMessage = ChatMessage(
                    role = "model",
                    content = fullResponse.toString()
                )

                _uiState.value = _uiState.value.copy(
                    messages = _uiState.value.messages + modelMessage,
                    isGenerating = false,
                    streamingText = ""
                )
            } catch (e: Exception) {
                val errorMsg = when {
                    e.message?.contains("503") == true -> "Gemini API temporarily unavailable. Trying fallback..."
                    e.message?.contains("429") == true -> "Rate limit exceeded. Please wait a moment."
                    e.message?.contains("INVALID_API_KEY") == true || 
                    e.message?.contains("API_KEY_INVALID") == true -> "Invalid API Key. Check Settings."
                    e.message?.contains("PERMISSION_DENIED") == true -> "API key doesn't have access to this model."
                    else -> "Error: ${e.message}"
                }

                val errorMessage = ChatMessage(
                    role = "model",
                    content = "⚠️ $errorMsg",
                    isError = true
                )

                _uiState.value = _uiState.value.copy(
                    messages = _uiState.value.messages + errorMessage,
                    isGenerating = false,
                    streamingText = "",
                    errorMessage = errorMsg
                )

                // Try fallback model on 503/429
                if (e.message?.contains("503") == true || e.message?.contains("429") == true) {
                    tryFallbackModel(text)
                }
            }
        }
    }

    private suspend fun tryFallbackModel(originalMessage: String) {
        val fallbackChain = listOf(
            "gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash",
            "gemini-1.5-flash", "gemini-1.5-pro"
        )
        val currentIdx = fallbackChain.indexOf(_uiState.value.selectedModel)
        val nextModels = fallbackChain.drop(currentIdx + 1)

        for (model in nextModels) {
            try {
                val state = _uiState.value
                chatService.initializeChat(state.apiKey, model, state.targetExam)
                val response = chatService.sendMessage(originalMessage)

                val successMsg = ChatMessage(
                    role = "model",
                    content = "*(Fallback to $model)*\n\n$response"
                )
                _uiState.value = _uiState.value.copy(
                    messages = _uiState.value.messages + successMsg,
                    isGenerating = false,
                    selectedModel = model
                )
                settingsRepo.saveSelectedModel(model)
                return
            } catch (_: Exception) {
                continue
            }
        }
    }

    fun clearChat() {
        _uiState.value = _uiState.value.copy(
            messages = emptyList(),
            streamingText = ""
        )
        chatService.resetChat(_uiState.value.targetExam)
    }

    fun clearError() {
        _uiState.value = _uiState.value.copy(errorMessage = null)
    }

    fun getModelDisplayName(modelId: String): String {
        return AVAILABLE_MODELS.find { it.id == modelId }?.name ?: modelId
    }
}
