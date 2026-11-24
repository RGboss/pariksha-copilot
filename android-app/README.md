# Pariksha Copilot — Android Application

A complete full-stack Android application for **Pariksha Copilot** (Govt Exam Preparation Platform & AI Tutor) that hosts **both backend and frontend directly on the Android device** and uses the **customer-provided Gemini API key** for AI chat interactions.

---

## 🌟 Key Features

### 1. Dual Interface
- **Native AI Tutor (Jetpack Compose):**
  - Instant streaming responses via Google Generative AI SDK.
  - Multi-model selection: `gemini-2.5-flash`, `gemini-2.5-pro`, `gemini-2.0-flash`, `gemini-1.5-flash`, `gemini-1.5-pro`.
  - Automatic resilience fallback (falls back from Flash to Pro or 1.5 on `503` / `429` errors).
  - Exam-focused system prompt customized for SEBI Grade A, RBI Grade B, UPSC, SSC CGL, IBPS, and more.
  - Markdown rendering with code blocks, lists, bold/italic, and quotes.
- **Web Browser Interface (WebView + LAN):**
  - Embedded WebView running the React SPA frontend.
  - Switch between **Local Embedded Server (`:8080`)** and **Network Gateway Server (`:8000` / `:8082`)**.
  - One-tap button to open in external browser (Chrome / Firefox).

### 2. Embedded Server Hosting (Backend + Frontend)
- Runs a multi-threaded HTTP server (`EmbeddedHttpServer`) on `0.0.0.0:8080`.
- **Hosts Frontend:** Serves pre-compiled production React SPA assets directly from `app/src/main/assets/web/`.
- **Hosts Backend API:**
  - `GET /health` — Health check endpoint.
  - `GET /api/health` — Application metadata.
  - `GET /api/models` — Available Gemini models.
  - `GET /api/settings` — Configuration status.
  - `POST /api/chat` — AI chat endpoint using the customer's configured API key.
- **LAN Access:** Other devices on the same Wi-Fi can open `http://<phone-ip>:8080` to access the full portal!

### 3. Customer-Provided API Key & Privacy
- Users enter their own Gemini API key in the in-app **Settings** tab.
- Key is securely stored on-device using Jetpack **DataStore Preferences**.
- Keys are never hardcoded or transmitted to third-party tracking servers.
- Clear key option allows instant local wiping.

---

## 🏗️ Project Architecture

```
android-app/
├── app/
│   ├── src/main/
│   │   ├── AndroidManifest.xml
│   │   ├── assets/web/                  # Bundled React SPA frontend (HTML/JS/CSS)
│   │   ├── java/com/pariksha/copilot/
│   │   │   ├── MainActivity.kt          # App entrypoint; starts embedded HTTP server
│   │   │   ├── ParikshaApp.kt           # Navigation & Scaffold (Chat / Web / Settings)
│   │   │   ├── ChatViewModel.kt         # StateFlow viewmodel & fallback engine
│   │   │   ├── data/
│   │   │   │   ├── Models.kt            # ChatMessage, ModelInfo, Exam lists
│   │   │   │   └── SettingsRepository.kt # DataStore for API key, model & URLs
│   │   │   ├── network/
│   │   │   │   ├── GeminiChatService.kt  # Google Generative AI SDK client
│   │   │   │   └── EmbeddedHttpServer.kt# Multi-threaded server (assets + API)
│   │   │   └── ui/
│   │   │       ├── components/
│   │   │       │   └── MarkdownText.kt  # Compose Markdown parser & renderer
│   │   │       ├── screens/
│   │   │       │   ├── ChatScreen.kt    # Native AI Tutor chat interface
│   │   │       │   ├── SettingsScreen.kt# API key, model & profile settings
│   │   │       │   └── WebPortalScreen.kt# Interactive WebView + external browser
│   │   │       └── theme/
│   │   │           └── Theme.kt         # Pariksha design system colors & typography
│   │   └── res/
│   │       ├── values/ (strings.xml, colors.xml, themes.xml)
│   │       └── xml/network_security_config.xml
│   ├── build.gradle.kts
│   └── proguard-rules.pro
├── gradle/
│   ├── libs.versions.toml               # Modern Gradle Version Catalog
│   └── wrapper/
│       └── gradle-wrapper.properties
├── build.gradle.kts                     # Root build script
├── settings.gradle.kts                  # Project settings
├── gradlew
└── gradlew.bat
```

---

## 🚀 How to Build & Run

### Prerequisites
- Android Studio Hedgehog (2023.1.1) or newer / JDK 17+
- Android SDK 35 (minimum supported: Android 8.0, API 26)

### Option 1: Using Android Studio
1. Open Android Studio.
2. Select **Open** and choose the `prep_platform/android-app` folder.
3. Allow Gradle sync to complete.
4. Connect an Android device (e.g. Redmi Note 5 Pro over ADB: `adb connect 192.168.29.94:5555`) or start an emulator.
5. Click **Run 'app'** (`Shift + F10`).

### Option 2: Using Command Line
```bash
cd android-app
# Debug APK
./gradlew assembleDebug

# Install on connected device
./gradlew installDebug
```

---

## 🔒 Security Best Practices
- The customer API key is stored strictly on the local device via `DataStore`.
- No proprietary API keys are bundled or hardcoded into the APK.
- Cleartext traffic is restricted strictly to local network domains (`127.0.0.1`, `10.0.2.2`, `192.168.*`) via `network_security_config.xml`.
