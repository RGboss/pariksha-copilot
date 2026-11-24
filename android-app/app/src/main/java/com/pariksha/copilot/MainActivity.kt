package com.pariksha.copilot

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import com.pariksha.copilot.network.EmbeddedHttpServer
import com.pariksha.copilot.ui.theme.ParikshaTheme

class MainActivity : ComponentActivity() {

    private var embeddedServer: EmbeddedHttpServer? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        // Start embedded HTTP server hosting backend + frontend
        embeddedServer = EmbeddedHttpServer(applicationContext, port = 8080).apply {
            start()
        }

        setContent {
            ParikshaTheme {
                ParikshaApp(embeddedPort = 8080)
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        embeddedServer?.stop()
    }
}
