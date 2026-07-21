package com.luna.app

import kotlinx.coroutines.*
import okhttp3.*
import okio.ByteString
import org.json.JSONObject
import java.util.concurrent.TimeUnit

class LunaWebSocket(
    private val ip: String,
    private val port: Int,
    private val onConnected: () -> Unit,
    private val onDisconnected: () -> Unit,
    private val onProfileSwitch: (profile: String, window: String) -> Unit,
    private val onProStatus: (Boolean) -> Unit,
    private val onError: (String) -> Unit,
    private val onThemeUpdate: ((JSONObject) -> Unit)? = null,
    private val onConfigUpdated: (() -> Unit)? = null
) {
    private var ws: WebSocket? = null
    private val client = OkHttpClient.Builder()
        .pingInterval(10, TimeUnit.SECONDS)
        .readTimeout(0, TimeUnit.SECONDS)
        .build()
    private var closed = false
    private var reconnectJob: Job? = null
    private var reconnectAttempts = 0
    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())

    fun cancelScope() {
        scope.cancel()
    }

    fun connect() {
        closed = false
        val url = "ws://$ip:$port/ws"
        val request = Request.Builder().url(url).build()
        ws = client.newWebSocket(request, object : WebSocketListener() {
            override fun onOpen(ws: WebSocket, response: Response) {
                onConnected()
            }

            override fun onMessage(ws: WebSocket, text: String) {
                try {
                    val msg = JSONObject(text)
                    when (msg.optString("type")) {
                        "switch_profile" -> {
                            val profile = msg.optString("profile", "")
                            val window = msg.optString("window", "")
                            onProfileSwitch(profile, window)
                        }
                        "init" -> {
                            if (msg.has("is_pro_version")) {
                                onProStatus(msg.getBoolean("is_pro_version"))
                            }
                        }
                        "theme_update" -> {
                            val themes = msg.optJSONObject("themes")
                            if (themes != null) onThemeUpdate?.invoke(themes)
                        }
                        "config_updated" -> {
                            onConfigUpdated?.invoke()
                        }
                    }
                } catch (_: Exception) {}
            }

            override fun onClosing(ws: WebSocket, code: Int, reason: String) {
                ws.close(1000, null)
            }

            override fun onClosed(ws: WebSocket, code: Int, reason: String) {
                if (!closed) {
                    onDisconnected()
                    scheduleReconnect()
                }
            }

            override fun onFailure(ws: WebSocket, t: Throwable, response: Response?) {
                if (!closed) {
                    onDisconnected()
                    onError(t.message ?: "WebSocket error")
                    scheduleReconnect()
                }
            }
        })
    }

    fun disconnect() {
        closed = true
        reconnectAttempts = 0
        reconnectJob?.cancel()
        ws?.close(1000, "User disconnected")
        scope.cancel()
    }

    private fun scheduleReconnect() {
        if (closed || reconnectAttempts >= 10) return
        reconnectAttempts++
        reconnectJob?.cancel()
        reconnectJob = scope.launch {
            val delayMs = (3000L * (1 shl (reconnectAttempts - 1))).coerceAtMost(60000)
            delay(delayMs)
            if (!closed) connect()
        }
    }

    fun sendKeyPress(keyCode: Int, mods: Int) {
        sendBin(0x01, 0x01, mods, keyCode)
    }

    fun sendKeyRelease(keyCode: Int, mods: Int) {
        sendBin(0x01, 0x02, mods, keyCode)
    }

    fun sendKeyTap(keyCode: Int, mods: Int) {
        sendBin(0x01, 0x03, mods, keyCode)
    }

    fun sendSlider(sliderId: Int, value: Int) {
        sendBin(0x02, sliderId, value, 0x00)
    }

    private fun sendBin(b0: Int, b1: Int, b2: Int, b3: Int) {
        val data = byteArrayOf(b0.toByte(), b1.toByte(), b2.toByte(), b3.toByte(), 0)
        var xor = 0
        for (i in 0..3) xor = xor xor data[i].toInt()
        data[4] = xor.toByte()
        ws?.send(ByteString.of(data[0], data[1], data[2], data[3], data[4]))
    }
}
