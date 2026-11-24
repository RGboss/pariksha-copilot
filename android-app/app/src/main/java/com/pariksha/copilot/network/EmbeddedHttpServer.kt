package com.pariksha.copilot.network

import android.content.Context
import android.util.Log
import com.pariksha.copilot.data.AVAILABLE_MODELS
import com.pariksha.copilot.data.SettingsRepository
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.first
import org.json.JSONArray
import org.json.JSONObject
import java.io.*
import java.net.*
import java.util.concurrent.Executors

/**
 * Lightweight Embedded HTTP Server running directly inside the Android app.
 *
 * Capabilities:
 * 1. Hosts the React SPA Frontend directly from assets (app/src/main/assets/web).
 * 2. Provides REST API endpoints (/health, /api/health, /api/chat, /api/models, /api/settings).
 * 3. Uses the customer-provided Gemini API key to power chat interactions.
 * 4. Listens on 0.0.0.0:8080 so both internal WebView (http://localhost:8080)
 *    and external LAN browsers (http://<device-ip>:8080) can access the platform.
 */
class EmbeddedHttpServer(
    private val context: Context,
    private val port: Int = 8080
) {
    companion object {
        private const val TAG = "EmbeddedHttpServer"
    }

    private var serverSocket: ServerSocket? = null
    private var isRunning = false
    private val threadPool = Executors.newFixedThreadPool(8)
    private val settingsRepo = SettingsRepository(context)
    private val chatService = GeminiChatService()
    private val serverScope = CoroutineScope(Dispatchers.IO + SupervisorJob())

    fun start() {
        if (isRunning) return

        serverScope.launch {
            try {
                serverSocket = ServerSocket(port, 50, InetAddress.getByName("0.0.0.0"))
                isRunning = true
                Log.i(TAG, "Pariksha Copilot embedded server started on port $port")

                while (isRunning) {
                    try {
                        val clientSocket = serverSocket?.accept() ?: break
                        threadPool.execute {
                            handleConnection(clientSocket)
                        }
                    } catch (e: SocketException) {
                        if (!isRunning) break
                        Log.e(TAG, "Socket exception: ${e.message}")
                    }
                }
            } catch (e: Exception) {
                Log.e(TAG, "Failed to start embedded HTTP server: ${e.message}", e)
                isRunning = false
            }
        }
    }

    fun stop() {
        isRunning = false
        try {
            serverSocket?.close()
        } catch (_: Exception) {}
        serverSocket = null
        Log.i(TAG, "Embedded server stopped")
    }

    fun isServerRunning(): Boolean = isRunning

    fun getLocalIpAddress(): String {
        try {
            val interfaces = NetworkInterface.getNetworkInterfaces()
            while (interfaces.hasMoreElements()) {
                val networkInterface = interfaces.nextElement()
                val addresses = networkInterface.inetAddresses
                while (addresses.hasMoreElements()) {
                    val address = addresses.nextElement()
                    if (!address.isLoopbackAddress && address is Inet4Address) {
                        return address.hostAddress ?: "127.0.0.1"
                    }
                }
            }
        } catch (_: Exception) {}
        return "127.0.0.1"
    }

    private fun handleConnection(socket: Socket) {
        try {
            socket.soTimeout = 30000
            val input = BufferedReader(InputStreamReader(socket.getInputStream()))
            val output = BufferedOutputStream(socket.getOutputStream())

            val requestLine = input.readLine() ?: return
            val parts = requestLine.split(" ")
            if (parts.size < 2) return

            val method = parts[0]
            val path = parts[1].substringBefore("?")

            // Read headers
            val headers = mutableMapOf<String, String>()
            var line: String?
            var contentLength = 0
            while (input.readLine().also { line = it } != null) {
                if (line.isNullOrEmpty()) break
                val headerParts = line!!.split(": ", limit = 2)
                if (headerParts.size == 2) {
                    headers[headerParts[0].lowercase()] = headerParts[1]
                    if (headerParts[0].equals("content-length", ignoreCase = true)) {
                        contentLength = headerParts[1].toIntOrNull() ?: 0
                    }
                }
            }

            // Read request body if present
            val body = if (contentLength > 0) {
                val charBuffer = CharArray(contentLength)
                var bytesRead = 0
                while (bytesRead < contentLength) {
                    val read = input.read(charBuffer, bytesRead, contentLength - bytesRead)
                    if (read == -1) break
                    bytesRead += read
                }
                String(charBuffer, 0, bytesRead)
            } else ""

            // Handle CORS preflight
            if (method.equals("OPTIONS", ignoreCase = true)) {
                sendCorsPreflight(output)
                return
            }

            // Route request
            when {
                path == "/health" -> {
                    sendJsonResponse(output, 200, JSONObject().put("status", "healthy").put("mode", "android-embedded").toString())
                }
                path == "/api/health" -> {
                    sendJsonResponse(output, 200, JSONObject()
                        .put("status", "ok")
                        .put("app", "pariksha-copilot")
                        .put("version", "2.3.0-android")
                        .put("embedded", true)
                        .toString()
                    )
                }
                path == "/api/models" -> {
                    val modelsArray = JSONArray()
                    AVAILABLE_MODELS.forEach { m ->
                        modelsArray.put(JSONObject().put("id", m.id).put("name", m.name).put("description", m.description))
                    }
                    sendJsonResponse(output, 200, modelsArray.toString())
                }
                path == "/api/settings" -> {
                    runBlocking {
                        val apiKey = settingsRepo.apiKey.first()
                        val model = settingsRepo.selectedModel.first()
                        sendJsonResponse(output, 200, JSONObject()
                            .put("gemini_api_configured", apiKey.isNotBlank())
                            .put("chat_model", model)
                            .toString()
                        )
                    }
                }
                path == "/api/chat" && method.equals("POST", ignoreCase = true) -> {
                    handleChatRequest(body, output)
                }
                else -> {
                    // Serve static frontend assets
                    serveAsset(path, output)
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error handling client request: ${e.message}")
        } finally {
            try {
                socket.close()
            } catch (_: Exception) {}
        }
    }

    private fun handleChatRequest(body: String, output: OutputStream) {
        try {
            val json = JSONObject(body)
            val userMessage = json.optString("message", "").trim()
            val reqModel = json.optString("model", "")

            if (userMessage.isEmpty()) {
                sendJsonResponse(output, 400, JSONObject().put("error", "Message cannot be empty").toString())
                return
            }

            runBlocking {
                val apiKey = settingsRepo.apiKey.first()
                val savedModel = settingsRepo.selectedModel.first()
                val targetExam = settingsRepo.targetExam.first()
                val activeModel = if (reqModel.isNotBlank()) reqModel else savedModel

                if (apiKey.isBlank()) {
                    sendJsonResponse(output, 400, JSONObject()
                        .put("error", "Gemini API key is not configured. Please enter your key in the Android app Settings.")
                        .toString()
                    )
                    return@runBlocking
                }

                try {
                    chatService.initializeChat(apiKey, activeModel, targetExam)
                    val responseText = chatService.sendMessage(userMessage)

                    val resp = JSONObject()
                        .put("response", responseText)
                        .put("model", activeModel)
                        .put("exam", targetExam)

                    sendJsonResponse(output, 200, resp.toString())
                } catch (e: Exception) {
                    val errorMsg = e.message ?: "Chat generation failed"
                    sendJsonResponse(output, 500, JSONObject().put("error", errorMsg).toString())
                }
            }
        } catch (e: Exception) {
            sendJsonResponse(output, 400, JSONObject().put("error", "Invalid JSON body").toString())
        }
    }

    private fun serveAsset(requestedPath: String, output: OutputStream) {
        var cleanPath = requestedPath.substringBefore("?").trimStart('/')
        if (cleanPath.isEmpty()) {
            cleanPath = "index.html"
        }

        // Try direct asset path under web/
        val assetPath = "web/$cleanPath"
        val mimeType = getMimeType(cleanPath)

        val assetStream = try {
            context.assets.open(assetPath)
        } catch (_: Exception) {
            // SPA fallback: Return index.html for unknown frontend routes
            try {
                context.assets.open("web/index.html")
            } catch (_: Exception) {
                null
            }
        }

        if (assetStream != null) {
            try {
                val bytes = assetStream.readBytes()
                assetStream.close()

                val header = "HTTP/1.1 200 OK\r\n" +
                        "Content-Type: $mimeType\r\n" +
                        "Content-Length: ${bytes.size}\r\n" +
                        "Access-Control-Allow-Origin: *\r\n" +
                        "Cache-Control: public, max-age=3600\r\n" +
                        "Connection: close\r\n\r\n"

                output.write(header.toByteArray(Charsets.UTF_8))
                output.write(bytes)
                output.flush()
            } catch (e: Exception) {
                sendNotFound(output)
            }
        } else {
            sendNotFound(output)
        }
    }

    private fun getMimeType(fileName: String): String {
        return when {
            fileName.endsWith(".html", ignoreCase = true) -> "text/html; charset=utf-8"
            fileName.endsWith(".js", ignoreCase = true) -> "application/javascript; charset=utf-8"
            fileName.endsWith(".css", ignoreCase = true) -> "text/css; charset=utf-8"
            fileName.endsWith(".json", ignoreCase = true) -> "application/json; charset=utf-8"
            fileName.endsWith(".svg", ignoreCase = true) -> "image/svg+xml"
            fileName.endsWith(".png", ignoreCase = true) -> "image/png"
            fileName.endsWith(".jpg", ignoreCase = true) || fileName.endsWith(".jpeg", ignoreCase = true) -> "image/jpeg"
            fileName.endsWith(".ico", ignoreCase = true) -> "image/x-icon"
            fileName.endsWith(".woff2", ignoreCase = true) -> "font/woff2"
            fileName.endsWith(".woff", ignoreCase = true) -> "font/woff"
            fileName.endsWith(".ttf", ignoreCase = true) -> "font/ttf"
            else -> "application/octet-stream"
        }
    }

    private fun sendJsonResponse(output: OutputStream, statusCode: Int, json: String) {
        val bytes = json.toByteArray(Charsets.UTF_8)
        val statusText = if (statusCode == 200) "OK" else if (statusCode == 400) "Bad Request" else "Error"
        val response = "HTTP/1.1 $statusCode $statusText\r\n" +
                "Content-Type: application/json; charset=utf-8\r\n" +
                "Content-Length: ${bytes.size}\r\n" +
                "Access-Control-Allow-Origin: *\r\n" +
                "Access-Control-Allow-Methods: GET, POST, OPTIONS\r\n" +
                "Access-Control-Allow-Headers: Content-Type, Authorization\r\n" +
                "Connection: close\r\n\r\n"

        output.write(response.toByteArray(Charsets.UTF_8))
        output.write(bytes)
        output.flush()
    }

    private fun sendCorsPreflight(output: OutputStream) {
        val response = "HTTP/1.1 204 No Content\r\n" +
                "Access-Control-Allow-Origin: *\r\n" +
                "Access-Control-Allow-Methods: GET, POST, OPTIONS\r\n" +
                "Access-Control-Allow-Headers: Content-Type, Authorization\r\n" +
                "Access-Control-Max-Age: 86400\r\n" +
                "Connection: close\r\n\r\n"
        output.write(response.toByteArray(Charsets.UTF_8))
        output.flush()
    }

    private fun sendNotFound(output: OutputStream) {
        val body = "<h1>404 Not Found</h1>"
        val response = "HTTP/1.1 404 Not Found\r\n" +
                "Content-Type: text/html\r\n" +
                "Content-Length: ${body.length}\r\n" +
                "Connection: close\r\n\r\n$body"
        output.write(response.toByteArray(Charsets.UTF_8))
        output.flush()
    }
}
