package com.pariksha.copilot

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.pariksha.copilot.data.*
import com.pariksha.copilot.network.GeminiChatService
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch

data class AppUiState(
    val isLoggedIn: Boolean = false,
    val userName: String = "",
    val userEmail: String = "",
    val targetExam: String = "SEBI Grade A (IT Stream)",
    val streakDays: Int = 7,
    val dailyHours: Int = 5,
    val apiKey: String = "",
    val isApiKeyConfigured: Boolean = false,
    val selectedModel: String = "gemini-2.5-flash",
    val serverUrl: String = "http://192.168.29.94:8082",
    val messages: List<ChatMessage> = emptyList(),
    val isGenerating: Boolean = false,
    val streamingText: String = "",
    val errorMessage: String? = null,
    val authError: String? = null,
    val isAuthLoading: Boolean = false,
    val tasks: List<StudyTaskItem> = DEFAULT_TASKS,
    val flashcards: List<FlashcardItem> = DEFAULT_FLASHCARDS,
    val activeFlashcardIndex: Int = 0,
    val isFlashcardFlipped: Boolean = false
)

class ChatViewModel(application: Application) : AndroidViewModel(application) {

    private val settingsRepo = SettingsRepository(application)
    private val chatService = GeminiChatService()

    private val _uiState = MutableStateFlow(AppUiState())
    val uiState: StateFlow<AppUiState> = _uiState.asStateFlow()

    init {
        // Collect persistent settings
        viewModelScope.launch {
            val authFlow = combine(
                settingsRepo.isLoggedIn,
                settingsRepo.userName,
                settingsRepo.userEmail,
                settingsRepo.targetExam,
                settingsRepo.apiKey
            ) { loggedIn, name, email, exam, key ->
                listOf(loggedIn, name, email, exam, key)
            }

            val studyFlow = combine(
                settingsRepo.selectedModel,
                settingsRepo.streakDays,
                settingsRepo.dailyHours
            ) { model, streak, hours ->
                Triple(model, streak, hours)
            }

            authFlow.combine(studyFlow) { auth, study ->
                _uiState.value.copy(
                    isLoggedIn = auth[0] as Boolean,
                    userName = auth[1] as String,
                    userEmail = auth[2] as String,
                    targetExam = auth[3] as String,
                    apiKey = auth[4] as String,
                    isApiKeyConfigured = (auth[4] as String).isNotBlank(),
                    selectedModel = study.first,
                    streakDays = study.second,
                    dailyHours = study.third
                )
            }.collect { newState ->
                _uiState.value = newState
                if (newState.apiKey.isNotBlank()) {
                    try {
                        chatService.initializeChat(newState.apiKey, newState.selectedModel, newState.targetExam)
                    } catch (_: Exception) {}
                }
            }
        }
    }

    // ==========================================
    // AUTHENTICATION HANDLERS
    // ==========================================

    fun login(email: String, pass: String) {
        if (email.isBlank() || pass.isBlank()) {
            _uiState.value = _uiState.value.copy(authError = "Please enter both email and password")
            return
        }

        _uiState.value = _uiState.value.copy(isAuthLoading = true, authError = null)
        viewModelScope.launch {
            kotlinx.coroutines.delay(600) // Smooth transition
            val derivedName = email.substringBefore("@").replace(".", " ").capitalizeWords()
            val token = "jwt_token_" + System.currentTimeMillis()
            settingsRepo.saveAuthSession(
                name = if (_uiState.value.userName.isNotBlank()) _uiState.value.userName else derivedName,
                email = email.trim(),
                exam = _uiState.value.targetExam,
                token = token
            )
            _uiState.value = _uiState.value.copy(isAuthLoading = false, authError = null)
        }
    }

    fun signup(name: String, email: String, exam: String, pass: String) {
        if (name.isBlank() || email.isBlank() || pass.isBlank()) {
            _uiState.value = _uiState.value.copy(authError = "All fields are required")
            return
        }
        if (pass.length < 6) {
            _uiState.value = _uiState.value.copy(authError = "Password must be at least 6 characters")
            return
        }

        _uiState.value = _uiState.value.copy(isAuthLoading = true, authError = null)
        viewModelScope.launch {
            kotlinx.coroutines.delay(600)
            val token = "jwt_token_" + System.currentTimeMillis()
            settingsRepo.saveAuthSession(name.trim(), email.trim(), exam, token)
            _uiState.value = _uiState.value.copy(isAuthLoading = false, authError = null)
        }
    }

    fun demoLogin() {
        _uiState.value = _uiState.value.copy(isAuthLoading = true, authError = null)
        viewModelScope.launch {
            kotlinx.coroutines.delay(400)
            settingsRepo.saveAuthSession(
                name = "Aspirant Rahul",
                email = "rahul@aspirant.gov.in",
                exam = "SEBI Grade A (IT Stream)",
                token = "demo_jwt_token_aspirant_rahul"
            )
            _uiState.value = _uiState.value.copy(isAuthLoading = false, authError = null)
        }
    }

    fun logout() {
        viewModelScope.launch {
            settingsRepo.logout()
            _uiState.value = _uiState.value.copy(
                isLoggedIn = false,
                messages = emptyList()
            )
        }
    }

    fun clearAuthError() {
        _uiState.value = _uiState.value.copy(authError = null)
    }

    // ==========================================
    // STUDY PLANNER / TASKS
    // ==========================================

    fun toggleTask(taskId: String) {
        val updated = _uiState.value.tasks.map { task ->
            if (task.id == taskId) task.copy(isCompleted = !task.isCompleted) else task
        }
        _uiState.value = _uiState.value.copy(tasks = updated)
    }

    // ==========================================
    // FLASHCARDS (LEITNER 5-BOX ACTIVE RECALL)
    // ==========================================

    fun flipFlashcard() {
        _uiState.value = _uiState.value.copy(isFlashcardFlipped = !_uiState.value.isFlashcardFlipped)
    }

    fun reviewFlashcard(gotRight: Boolean) {
        val currentIdx = _uiState.value.activeFlashcardIndex
        val cards = _uiState.value.flashcards.toMutableList()
        val card = cards[currentIdx]

        val newBox = if (gotRight) minOf(5, card.box + 1) else 1
        cards[currentIdx] = card.copy(box = newBox)

        val nextIdx = (currentIdx + 1) % cards.size
        _uiState.value = _uiState.value.copy(
            flashcards = cards,
            activeFlashcardIndex = nextIdx,
            isFlashcardFlipped = false
        )
    }

    // ==========================================
    // GEMINI AI CHAT & SETTINGS
    // ==========================================

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

    fun saveSelectedModel(model: String) {
        viewModelScope.launch {
            settingsRepo.saveSelectedModel(model)
            val state = _uiState.value
            if (state.apiKey.isNotBlank()) {
                chatService.initializeChat(state.apiKey, model, state.targetExam)
            }
        }
    }

    fun saveTargetExam(exam: String) {
        viewModelScope.launch {
            settingsRepo.saveTargetExam(exam)
            chatService.resetChat(exam)
        }
    }

    fun saveUserName(name: String) {
        viewModelScope.launch {
            settingsRepo.saveUserName(name)
        }
    }

    fun saveServerUrl(url: String) {
        _uiState.value = _uiState.value.copy(serverUrl = url)
    }

    fun sendMessage(text: String) {
        if (text.isBlank() || _uiState.value.isGenerating) return

        val state = _uiState.value
        if (!state.isApiKeyConfigured) {
            _uiState.value = state.copy(
                errorMessage = "Configure your Gemini API key in Settings to chat with the AI Faculty."
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

                val modelMessage = ChatMessage(role = "model", content = fullResponse.toString())
                _uiState.value = _uiState.value.copy(
                    messages = _uiState.value.messages + modelMessage,
                    isGenerating = false,
                    streamingText = ""
                )
            } catch (e: Exception) {
                val errorMsg = when {
                    e.message?.contains("503") == true -> "AI Server busy (503). Retrying fallback model..."
                    e.message?.contains("429") == true -> "Rate limit (429). Please wait a few seconds."
                    e.message?.contains("API_KEY_INVALID") == true || e.message?.contains("INVALID_API_KEY") == true -> 
                        "Invalid API Key. Please verify in Settings."
                    else -> e.message ?: "Chat request failed."
                }

                val errorMessage = ChatMessage(role = "model", content = "⚠️ $errorMsg", isError = true)
                _uiState.value = _uiState.value.copy(
                    messages = _uiState.value.messages + errorMessage,
                    isGenerating = false,
                    streamingText = "",
                    errorMessage = errorMsg
                )
            }
        }
    }

    fun clearChat() {
        _uiState.value = _uiState.value.copy(messages = emptyList(), streamingText = "")
        chatService.resetChat(_uiState.value.targetExam)
    }

    fun clearError() {
        _uiState.value = _uiState.value.copy(errorMessage = null)
    }

    private fun String.capitalizeWords(): String = split(" ").joinToString(" ") { word ->
        word.replaceFirstChar { if (it.isLowerCase()) it.titlecase() else it.toString() }
    }
}
