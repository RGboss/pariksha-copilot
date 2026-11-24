package com.pariksha.copilot.ui.screens

import android.annotation.SuppressLint
import android.content.Intent
import android.graphics.Bitmap
import android.net.Uri
import android.view.ViewGroup
import android.webkit.*
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import com.pariksha.copilot.ui.theme.PrimaryBlue
import com.pariksha.copilot.ui.theme.Success
import com.pariksha.copilot.ui.theme.Warning

enum class WebPortalSource(val label: String) {
    LOCAL_EMBEDDED("Local Embedded (:8080)"),
    REMOTE_GATEWAY("Network Gateway")
}

@SuppressLint("SetJavaScriptEnabled")
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun WebPortalScreen(
    serverUrl: String,
    embeddedPort: Int = 8080
) {
    val context = LocalContext.current
    var selectedSource by remember { mutableStateOf(WebPortalSource.LOCAL_EMBEDDED) }
    val embeddedUrl = "http://127.0.0.1:$embeddedPort"
    val activeUrl = if (selectedSource == WebPortalSource.LOCAL_EMBEDDED) embeddedUrl else serverUrl

    var webViewInstance by remember { mutableStateOf<WebView?>(null) }
    var canGoBack by remember { mutableStateOf(false) }
    var canGoForward by remember { mutableStateOf(false) }
    var isLoading by remember { mutableStateOf(false) }
    var currentTitle by remember { mutableStateOf("Web Portal") }
    var currentLoadedUrl by remember { mutableStateOf(activeUrl) }
    var showSourceMenu by remember { mutableStateOf(false) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
    ) {
        // Web Toolbar
        TopAppBar(
            title = {
                Column {
                    Text(
                        currentTitle,
                        style = MaterialTheme.typography.titleSmall,
                        fontWeight = FontWeight.Bold,
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis
                    )
                    Text(
                        currentLoadedUrl,
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis
                    )
                }
            },
            navigationIcon = {
                IconButton(
                    onClick = { webViewInstance?.goBack() },
                    enabled = canGoBack
                ) {
                    Icon(Icons.Default.ArrowBack, "Back")
                }
            },
            actions = {
                IconButton(
                    onClick = { webViewInstance?.goForward() },
                    enabled = canGoForward
                ) {
                    Icon(Icons.Default.ArrowForward, "Forward")
                }

                IconButton(
                    onClick = { webViewInstance?.reload() }
                ) {
                    Icon(Icons.Default.Refresh, "Reload")
                }

                // Switch Source Dropdown (Embedded vs Remote Gateway)
                Box {
                    IconButton(onClick = { showSourceMenu = true }) {
                        Icon(Icons.Default.Dns, "Switch Server")
                    }

                    DropdownMenu(
                        expanded = showSourceMenu,
                        onDismissRequest = { showSourceMenu = false }
                    ) {
                        DropdownMenuItem(
                            text = {
                                Row(verticalAlignment = Alignment.CenterVertically) {
                                    Icon(
                                        Icons.Default.Smartphone,
                                        contentDescription = null,
                                        modifier = Modifier.size(18.dp)
                                    )
                                    Spacer(Modifier.width(8.dp))
                                    Text("Local Embedded (On-Device)")
                                }
                            },
                            onClick = {
                                selectedSource = WebPortalSource.LOCAL_EMBEDDED
                                showSourceMenu = false
                                webViewInstance?.loadUrl(embeddedUrl)
                            }
                        )

                        DropdownMenuItem(
                            text = {
                                Row(verticalAlignment = Alignment.CenterVertically) {
                                    Icon(
                                        Icons.Default.Cloud,
                                        contentDescription = null,
                                        modifier = Modifier.size(18.dp)
                                    )
                                    Spacer(Modifier.width(8.dp))
                                    Text("Network Gateway ($serverUrl)")
                                }
                            },
                            onClick = {
                                selectedSource = WebPortalSource.REMOTE_GATEWAY
                                showSourceMenu = false
                                webViewInstance?.loadUrl(serverUrl)
                            }
                        )
                    }
                }

                // Open in External Web Browser
                IconButton(
                    onClick = {
                        val browserIntent = Intent(Intent.ACTION_VIEW, Uri.parse(currentLoadedUrl))
                        context.startActivity(browserIntent)
                    }
                ) {
                    Icon(Icons.Default.OpenInBrowser, "Open in Browser")
                }
            },
            colors = TopAppBarDefaults.topAppBarColors(
                containerColor = MaterialTheme.colorScheme.surface
            )
        )

        // Loading Progress Bar
        if (isLoading) {
            LinearProgressIndicator(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(2.dp),
                color = PrimaryBlue
            )
        }

        // Mode Pill Bar
        Surface(
            modifier = Modifier.fillMaxWidth(),
            color = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.4f)
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 12.dp, vertical = 6.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(6.dp)
                ) {
                    Box(
                        modifier = Modifier
                            .size(8.dp)
                            .background(
                                color = if (selectedSource == WebPortalSource.LOCAL_EMBEDDED) Success else Warning,
                                shape = RoundedCornerShape(4.dp)
                            )
                    )
                    Text(
                        selectedSource.label,
                        style = MaterialTheme.typography.labelSmall,
                        fontWeight = FontWeight.Medium
                    )
                }

                Text(
                    "SPA Web View",
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }

        // Embedded WebView
        AndroidView(
            modifier = Modifier.fillMaxSize(),
            factory = { ctx ->
                WebView(ctx).apply {
                    layoutParams = ViewGroup.LayoutParams(
                        ViewGroup.LayoutParams.MATCH_PARENT,
                        ViewGroup.LayoutParams.MATCH_PARENT
                    )

                    settings.apply {
                        javaScriptEnabled = true
                        domStorageEnabled = true
                        databaseEnabled = true
                        allowFileAccess = true
                        allowContentAccess = true
                        useWideViewPort = true
                        loadWithOverviewMode = true
                        builtInZoomControls = true
                        displayZoomControls = false
                        mixedContentMode = WebSettings.MIXED_CONTENT_ALWAYS_ALLOW
                        cacheMode = WebSettings.LOAD_DEFAULT
                    }

                    webViewClient = object : WebViewClient() {
                        override fun onPageStarted(view: WebView?, url: String?, favicon: Bitmap?) {
                            isLoading = true
                            url?.let { currentLoadedUrl = it }
                            canGoBack = canGoBack()
                            canGoForward = canGoForward()
                        }

                        override fun onPageFinished(view: WebView?, url: String?) {
                            isLoading = false
                            url?.let { currentLoadedUrl = it }
                            currentTitle = view?.title ?: "Pariksha Portal"
                            canGoBack = canGoBack()
                            canGoForward = canGoForward()
                        }

                        override fun shouldOverrideUrlLoading(view: WebView?, request: WebResourceRequest?): Boolean {
                            return false // Keep inside WebView
                        }
                    }

                    webChromeClient = object : WebChromeClient() {
                        override fun onReceivedTitle(view: WebView?, title: String?) {
                            title?.let { currentTitle = it }
                        }

                        override fun onProgressChanged(view: WebView?, newProgress: Int) {
                            isLoading = newProgress < 100
                        }
                    }

                    loadUrl(activeUrl)
                    webViewInstance = this
                }
            },
            update = { webView ->
                webViewInstance = webView
            }
        )
    }
}
