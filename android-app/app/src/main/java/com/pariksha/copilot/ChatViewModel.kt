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
    val isFlashcardFlipped: Boolean = false,
    val quizzes: List<QuizItem> = DEFAULT_QUIZZES,
    val activeQuiz: QuizItem? = null,
    val activeQuizQuestionIndex: Int = 0,
    val selectedQuizAnswers: Map<Int, Int> = emptyMap(),
    val quizTimeLeftSeconds: Int = 600,
    val isQuizTimerActive: Boolean = false,
    val quizAttemptResult: QuizAttemptResult? = null
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

    private var timerJob: kotlinx.coroutines.Job? = null

    // ==========================================
    // STUDY PLANNER / TASKS
    // ==========================================

    fun toggleTask(taskId: String) {
        val updated = _uiState.value.tasks.map { task ->
            if (task.id == taskId) task.copy(isCompleted = !task.isCompleted) else task
        }
        _uiState.value = _uiState.value.copy(tasks = updated)
    }

    fun addTask(title: String, subject: String, minutes: Int, priority: String = "High") {
        if (title.isBlank()) return
        val newTask = StudyTaskItem(
            id = "task-" + System.currentTimeMillis(),
            title = title.trim(),
            subject = if (subject.isBlank()) "Core Syllabus" else subject.trim(),
            estimatedMinutes = if (minutes <= 0) 30 else minutes,
            isCompleted = false,
            priority = priority
        )
        _uiState.value = _uiState.value.copy(tasks = listOf(newTask) + _uiState.value.tasks)
    }

    fun deleteTask(taskId: String) {
        _uiState.value = _uiState.value.copy(
            tasks = _uiState.value.tasks.filterNot { it.id == taskId }
        )
    }

    // ==========================================
    // CBT MOCK EXAM & QUIZ SIMULATOR ENGINE
    // ==========================================

    fun startQuiz(quiz: QuizItem) {
        timerJob?.cancel()
        val totalSecs = quiz.durationMinutes * 60
        _uiState.value = _uiState.value.copy(
            activeQuiz = quiz,
            activeQuizQuestionIndex = 0,
            selectedQuizAnswers = emptyMap(),
            quizTimeLeftSeconds = totalSecs,
            isQuizTimerActive = true,
            quizAttemptResult = null
        )

        // Launch countdown timer
        timerJob = viewModelScope.launch {
            while (_uiState.value.quizTimeLeftSeconds > 0 && _uiState.value.quizAttemptResult == null) {
                kotlinx.coroutines.delay(1000)
                val remaining = _uiState.value.quizTimeLeftSeconds - 1
                _uiState.value = _uiState.value.copy(quizTimeLeftSeconds = maxOf(0, remaining))
                if (remaining <= 0) {
                    submitQuiz()
                    break
                }
            }
        }
    }

    fun selectQuizOption(optionIndex: Int) {
        if (_uiState.value.quizAttemptResult != null) return // Already submitted
        val qIdx = _uiState.value.activeQuizQuestionIndex
        val currentAnswers = _uiState.value.selectedQuizAnswers.toMutableMap()
        currentAnswers[qIdx] = optionIndex
        _uiState.value = _uiState.value.copy(selectedQuizAnswers = currentAnswers)
    }

    fun nextQuizQuestion() {
        val current = _uiState.value.activeQuizQuestionIndex
        val maxIdx = (_uiState.value.activeQuiz?.questions?.size ?: 1) - 1
        if (current < maxIdx) {
            _uiState.value = _uiState.value.copy(activeQuizQuestionIndex = current + 1)
        }
    }

    fun prevQuizQuestion() {
        val current = _uiState.value.activeQuizQuestionIndex
        if (current > 0) {
            _uiState.value = _uiState.value.copy(activeQuizQuestionIndex = current - 1)
        }
    }

    fun jumpToQuizQuestion(index: Int) {
        val maxIdx = (_uiState.value.activeQuiz?.questions?.size ?: 1) - 1
        if (index in 0..maxIdx) {
            _uiState.value = _uiState.value.copy(activeQuizQuestionIndex = index)
        }
    }

    fun submitQuiz() {
        timerJob?.cancel()
        val quiz = _uiState.value.activeQuiz ?: return
        val answers = _uiState.value.selectedQuizAnswers
        var correctCount = 0

        quiz.questions.forEachIndexed { idx, q ->
            val userSelected = answers[idx]
            if (userSelected != null && userSelected == q.correctOptionIndex) {
                correctCount++
            }
        }

        val totalQ = quiz.questions.size
        val scorePct = if (totalQ > 0) (correctCount.toDouble() / totalQ.toDouble()) * 100.0 else 0.0
        val timeSpent = (quiz.durationMinutes * 60) - _uiState.value.quizTimeLeftSeconds

        val result = QuizAttemptResult(
            quizId = quiz.id,
            totalQuestions = totalQ,
            correctCount = correctCount,
            scorePercentage = scorePct,
            timeSpentSeconds = maxOf(1, timeSpent),
            answers = answers
        )

        _uiState.value = _uiState.value.copy(
            isQuizTimerActive = false,
            quizAttemptResult = result
        )
    }

    fun retakeCurrentQuiz() {
        val quiz = _uiState.value.activeQuiz ?: return
        startQuiz(quiz)
    }

    fun exitQuiz() {
        timerJob?.cancel()
        _uiState.value = _uiState.value.copy(
            activeQuiz = null,
            quizAttemptResult = null,
            isQuizTimerActive = false,
            selectedQuizAnswers = emptyMap()
        )
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
        val userMessage = ChatMessage(role = "user", content = text)

        if (!state.isApiKeyConfigured) {
            // Instant Offline High-Yield Faculty Fallback
            _uiState.value = _uiState.value.copy(
                messages = _uiState.value.messages + userMessage,
                isGenerating = true,
                errorMessage = null,
                streamingText = ""
            )

            viewModelScope.launch {
                kotlinx.coroutines.delay(400) // Brief natural pause
                val offlineReply = generateOfflineFallback(text, state.targetExam)
                val modelMessage = ChatMessage(role = "model", content = offlineReply)
                _uiState.value = _uiState.value.copy(
                    messages = _uiState.value.messages + modelMessage,
                    isGenerating = false,
                    streamingText = ""
                )
            }
            return
        }

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
                // If API fails (quota or network), gracefully fall back to curated syllabus knowledge
                val offlineReply = generateOfflineFallback(text, state.targetExam)
                val fallbackMessage = ChatMessage(
                    role = "model",
                    content = offlineReply + "\n\n*(Cloud API notice: ${e.message?.take(80) ?: "Offline fallback active"} - showing syllabus cache)*"
                )
                _uiState.value = _uiState.value.copy(
                    messages = _uiState.value.messages + fallbackMessage,
                    isGenerating = false,
                    streamingText = "",
                    errorMessage = null
                )
            }
        }
    }

    private fun generateOfflineFallback(query: String, exam: String): String {
        val q = query.lowercase()
        return when {
            "sql" in q || "normalization" in q || "dbms" in q -> """
### 💡 High-Yield Faculty Notes: SQL Normalization & DBMS ($exam)

1. **1NF (First Normal Form):**
   - Eliminate repeating groups; ensure all attributes contain **atomic (indivisible)** values.
2. **2NF (Second Normal Form):**
   - Must be in 1NF and **no partial dependency** exists (every non-prime attribute is fully functionally dependent on candidate key).
3. **3NF (Third Normal Form):**
   - Must be in 2NF and **no transitive dependency** (X -> Y implies X is superkey or Y is prime).
4. **BCNF (Boyce-Codd Normal Form):**
   - Strictly requires that in every functional dependency X -> Y, **X MUST be a superkey**.

> **Exam Tip:** In 3NF, Y can be prime even if X is not a superkey. BCNF strictly disallows this!

*(Note: Operating in Curated Syllabus Faculty Mode. Add your Gemini API Key in Profile for live real-time chats!)*
""".trimIndent()
            "sebi" in q || "icdr" in q || "regulation" in q || "insider" in q -> """
### 📜 High-Yield Notes: SEBI & Securities Regulations

1. **SEBI Act, 1992:**
   - Established to protect investor interests, promote market development, and regulate securities markets.
2. **SEBI (PIT) Regulations, 2015:**
   - **UPSI:** Unpublished Price Sensitive Information.
   - Mandates Trading Windows closure prior to financial result disclosures.
3. **Settlement Cycle:**
   - India operates on standard **T+1 rolling settlement** with optional T+0 beta.

*(Note: Operating in Curated Syllabus Faculty Mode. Add your Gemini API Key in Profile for live real-time chats!)*
""".trimIndent()
            "network" in q || "osi" in q || "tcp" in q || "ip" in q -> """
### 🌐 High-Yield Notes: Networking & Protocol Architecture

- **OSI 7 Layers (Bottom-to-Top):** Physical -> Data Link -> Network -> Transport -> Session -> Presentation -> Application.
- **TCP vs UDP:**
  - **TCP:** Connection-oriented, 3-way handshake (SYN, SYN-ACK, ACK), flow control via sliding window, reliable.
  - **UDP:** Connectionless, zero handshake overhead, unreliable, ideal for DNS (port 53) and real-time streaming.

*(Note: Operating in Curated Syllabus Faculty Mode. Add your Gemini API Key in Profile for live real-time chats!)*
""".trimIndent()
            "strategy" in q || "timetable" in q || "30-day" in q -> """
### 🎯 30-Day High-Scoring Preparation Blueprint ($exam)

- **Week 1 (Foundations & Core Tech):** DBMS Normalization, SQL joins, Indexing, and Transaction Isolation.
- **Week 2 (Systems & Networks):** TCP/IP, OSI layers, Process scheduling, Deadlocks, Memory management.
- **Week 3 (Securities Laws / Quant):** SEBI Act, ICDR, PIT Regulations, Financial Awareness capsules.
- **Week 4 (Intense CBT Mocks & PYQ Revision):** 2 full-length CBT mock tests daily, reviewing every missed MCQ rationale.

*(Note: Operating in Curated Syllabus Faculty Mode. Add your Gemini API Key in Profile for live real-time chats!)*
""".trimIndent()
            else -> """
### 📘 Pariksha Copilot: Exam Insights for $exam

Thank you for your question on **"$query"**.

To excel in this domain:
1. **Core Concept Mastery:** Focus on statutory definitions, algorithmic complexities, and standard ISO/IEEE/SEBI frameworks.
2. **Daily Practice Routine:** Solve 15-25 topic-wise MCQs daily to build rapid pattern recognition under exam countdown timers.
3. **Error Log Notebook:** Document all incorrect attempts from the CBT Mock Exam simulator.

*(💡 Tip: Enter your free Gemini API Key under Profile to unlock unconstrained live tutoring and paper reviews!)*
""".trimIndent()
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
