package com.luna.app



import android.Manifest

import android.app.AlertDialog

import android.content.Context

import android.content.Intent

import android.content.pm.PackageManager

import android.graphics.Bitmap

import android.graphics.Color

import android.graphics.drawable.GradientDrawable

import android.graphics.PorterDuff

import android.net.Uri

import android.os.Bundle

import android.os.Build

import android.view.KeyEvent

import android.view.View

import android.view.ViewGroup

import android.view.WindowManager

import android.view.Gravity

import android.view.MotionEvent

import android.view.SoundEffectConstants

import android.webkit.JavascriptInterface

import android.webkit.WebSettings

import android.webkit.WebView

import android.webkit.WebViewClient

import android.widget.*

import androidx.activity.result.contract.ActivityResultContracts

import androidx.appcompat.app.AppCompatActivity

import androidx.core.content.ContextCompat

import androidx.core.content.FileProvider

import kotlinx.coroutines.*

import okhttp3.*

import org.json.JSONObject

import java.io.File

import java.io.FileOutputStream
import java.security.MessageDigest

import java.net.InetSocketAddress
import java.net.Socket
import java.net.URL
import java.net.DatagramSocket
import java.net.DatagramPacket
import java.net.InetAddress
import java.net.HttpURLConnection
import java.util.Collections
import java.util.concurrent.CountDownLatch
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit
import android.net.nsd.NsdManager
import android.net.nsd.NsdServiceInfo
import kotlin.concurrent.thread
import android.app.NotificationChannel

import android.app.NotificationManager

import android.content.res.ColorStateList
import android.content.res.Configuration

import androidx.core.app.NotificationCompat



class MainActivity : AppCompatActivity() {



    private lateinit var webView: WebView

    private lateinit var nativeUi: ViewGroup

    private lateinit var statusDot: View

    private lateinit var modeGridBtn: ImageButton

    private lateinit var modeSlidersBtn: ImageButton

    private lateinit var uiToggleBtn: ImageButton

    private lateinit var rescanQrBtn: ImageButton

    private lateinit var disconnectBtn: Button

    private lateinit var profileBar: LinearLayout

    private lateinit var gridLayout: GridLayout

    private lateinit var slidersPanel: View

    private lateinit var volumeSlider: SeekBar

    private lateinit var volumeValue: TextView

    private lateinit var brightnessSlider: SeekBar

    private lateinit var brightnessValue: TextView

    private lateinit var scrollPadV: ScrollPadView

    private lateinit var scrollPadH: ScrollPadView

    private lateinit var ipText: TextView

    private lateinit var spinnerOverlay: View

    private lateinit var headerBar: View

    private lateinit var connInfo: View

    private lateinit var menuBtn: Button

    private var adWebView: WebView? = null

    private var adRefreshJob: Job? = null

    private var adsRemoved = false

    private var currentTheme: LunaTheme = ThemeManager.themes[0]

    private var keepScreenOn = true

    private var notificationsEnabled = false
    private val onboardingLang: String
        get() = getSharedPreferences("luna_prefs", MODE_PRIVATE).getString("luna_lang", "en") ?: "en"
    private fun onboardingUrl(error: Boolean = false): String {
        val lang = onboardingLang
        val err = if (error) "&error=1" else ""
        return "file:///android_asset/onboarding/index.html?lang=$lang$err"
    }


    private lateinit var contentArea: FrameLayout



    private var serverIp = ""

    private var serverPort = 9120

    private var isConnected = false

    private var isUiHidden = false

    private var currentMode = "grid"

    private var currentProfileName = ""

    private val apkDownloadUrl = "https://sr-lolo.github.io/luna/Luna.apk"

    private val fallbackApkDownloadUrl = "https://github.com/Sr-Lolo/luna/releases/latest/download/Luna.apk"

    private var isUpdateDialogShowing = false

    private var lastUpdateCheckTime: Long
        get() = getSharedPreferences("luna_prefs", MODE_PRIVATE).getLong("last_update_check_time", 0L)
        set(value) = getSharedPreferences("luna_prefs", MODE_PRIVATE).edit().putLong("last_update_check_time", value).apply()

    private var lastUpdateDismissTime: Long
        get() = getSharedPreferences("luna_prefs", MODE_PRIVATE).getLong("last_update_dismiss", 0L)
        set(value) = getSharedPreferences("luna_prefs", MODE_PRIVATE).edit().putLong("last_update_dismiss", value).apply()

    private var wsClient: LunaWebSocket? = null

    private var configPolling: Job? = null

    private var lastConfigJson = ""

    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())



    private val okHttp = OkHttpClient.Builder()

        .connectTimeout(5, java.util.concurrent.TimeUnit.SECONDS)

        .readTimeout(5, java.util.concurrent.TimeUnit.SECONDS)

        .build()



    private var profiles: Map<String, LunaProfile> = emptyMap()



    private val qrLauncher = registerForActivityResult(ActivityResultContracts.StartActivityForResult()) { result ->

        if (result.resultCode == RESULT_OK) {

            val qrResult = result.data?.getStringExtra("SCAN_RESULT")

            if (qrResult != null) parseAndConnect(qrResult)

        }

    }



    private val permissionLauncher = registerForActivityResult(ActivityResultContracts.RequestPermission()) { granted ->

        if (granted) {

            qrLauncher.launch(Intent(this, QrScannerActivity::class.java))

        } else {

            Toast.makeText(this, getString(R.string.camera_perm_required), Toast.LENGTH_SHORT).show()

        }

    }



    override fun onCreate(savedInstanceState: Bundle?) {

        super.onCreate(savedInstanceState)

        setContentView(R.layout.activity_main)



        webView = findViewById(R.id.webView)

        nativeUi = findViewById(R.id.nativeUi)

        spinnerOverlay = findViewById(R.id.spinnerOverlay)



        setupNativeViews()

        setupWebView()



        adsRemoved = getSharedPreferences("luna_prefs", MODE_PRIVATE).getBoolean("ads_removed", false)



        val prefs = getSharedPreferences("luna_prefs", MODE_PRIVATE)

        val savedTheme = prefs.getString("theme", "oscuro") ?: "oscuro"

        currentTheme = ThemeManager.getTheme(savedTheme)

        keepScreenOn = prefs.getBoolean("keep_screen_on", true)

        notificationsEnabled = prefs.getBoolean("notifications", false)

        if (keepScreenOn) window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)



        val savedIp = getSharedPreferences("luna_prefs", MODE_PRIVATE)

            .getString("server_ip", "")



        if (savedIp.isNullOrEmpty()) {

            webView.visibility = View.VISIBLE

            nativeUi.visibility = View.GONE

            webView.loadUrl(onboardingUrl())

        } else {

            val parts = savedIp.split(":")

            serverIp = parts[0].trim()

            serverPort = if (parts.size > 1) parts[1].trim().toIntOrNull() ?: 9120 else 9120

            connectToServer()

        }
    }

    override fun onResume() {
        super.onResume()
        val now = System.currentTimeMillis()
        if (lastUpdateCheckTime != 0L && now - lastUpdateCheckTime > 86400000L) {
            lastUpdateCheckTime = now
            checkForUpdateFromWeb()
        }
    }



    private fun setupNativeViews() {
        statusDot = findViewById(R.id.statusDot)

        modeGridBtn = findViewById(R.id.modeGridBtn)

        modeSlidersBtn = findViewById(R.id.modeSlidersBtn)

        uiToggleBtn = findViewById(R.id.uiToggleBtn)

        rescanQrBtn = findViewById(R.id.rescanQrBtn)

        disconnectBtn = findViewById(R.id.disconnectBtn)

        profileBar = findViewById(R.id.profileBar)

        gridLayout = findViewById(R.id.gridLayout)

        slidersPanel = findViewById(R.id.slidersPanel)

        volumeSlider = findViewById(R.id.volumeSlider)

        volumeValue = findViewById(R.id.volumeValue)

        brightnessSlider = findViewById(R.id.brightnessSlider)

        brightnessValue = findViewById(R.id.brightnessValue)

        scrollPadV = findViewById(R.id.scrollPadV)

        scrollPadH = findViewById(R.id.scrollPadH)

        ipText = findViewById(R.id.ipText)

        headerBar = findViewById(R.id.headerBar)

        connInfo = findViewById(R.id.connInfo)

        menuBtn = findViewById(R.id.menuBtn)

        adWebView = findViewById(R.id.adWebView)

        adWebView?.settings?.javaScriptEnabled = true

        adWebView?.settings?.domStorageEnabled = true

        val cookieManager = android.webkit.CookieManager.getInstance()

        cookieManager.setAcceptCookie(true)

        cookieManager.setAcceptThirdPartyCookies(adWebView, true)

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {

            adWebView?.settings?.mixedContentMode = android.webkit.WebSettings.MIXED_CONTENT_ALWAYS_ALLOW

        }

        adWebView?.webViewClient = object : WebViewClient() {

            override fun shouldOverrideUrlLoading(view: WebView, request: android.webkit.WebResourceRequest): Boolean {

                val url = request.url.toString()

                if (url.isNotEmpty()) {

                    try {

                        startActivity(Intent(Intent.ACTION_VIEW, android.net.Uri.parse(url)))

                    } catch (e: Exception) {

                        view.loadUrl(url)

                    }

                }

                return true

            }

        }

        contentArea = findViewById(R.id.contentArea)



        modeGridBtn.setOnClickListener { switchMode("grid") }

        modeSlidersBtn.setOnClickListener { switchMode("sliders") }



        uiToggleBtn.setOnClickListener {

            isUiHidden = !isUiHidden

            val target = if (isUiHidden) View.GONE else View.VISIBLE

            headerBar.visibility = target

            findViewById<View>(R.id.profileBarScroll).visibility = target

            connInfo.visibility = target

            uiToggleBtn.setImageResource(

                if (isUiHidden) R.drawable.show_ui else R.drawable.hide

            )

        }



        rescanQrBtn.setOnClickListener { openQRScanner() }



        disconnectBtn.setOnClickListener {

            disconnect()

            webView.visibility = View.VISIBLE

            nativeUi.visibility = View.GONE

            webView.loadUrl(onboardingUrl())

        }



        menuBtn.setOnClickListener { showMenuDialog() }



        setupSliders()

        applyTheme(currentTheme)

    }



    private fun setupSliders() {

        volumeSlider.setOnSeekBarChangeListener(sliderListener(1, volumeValue, "%"))

        brightnessSlider.setOnSeekBarChangeListener(sliderListener(2, brightnessValue, "%"))



        scrollPadV.setOnValueChangeListener { value ->

            wsClient?.sendSlider(3, value)

        }

        scrollPadH.setOnValueChangeListener { value ->

            wsClient?.sendSlider(4, value)

        }

    }



    private fun sliderListener(id: Int, valueView: TextView, suffix: String) =

        object : SeekBar.OnSeekBarChangeListener {

            private var lastSent = -1

            override fun onProgressChanged(sb: SeekBar?, p: Int, fromUser: Boolean) {

                if (fromUser) {

                    val pct = (p * 100f / 255f).toInt()

                    valueView.text = "$pct$suffix"

                    if (kotlin.math.abs(p - lastSent) > 2) {

                        wsClient?.sendSlider(id, p)

                        lastSent = p

                    }

                }

            }

            override fun onStartTrackingTouch(sb: SeekBar?) {}

            override fun onStopTrackingTouch(sb: SeekBar?) { lastSent = -1 }

        }



    private fun setupWebView() {

        webView.apply {

            settings.apply {

                javaScriptEnabled = true

                domStorageEnabled = true

                cacheMode = WebSettings.LOAD_DEFAULT

                allowContentAccess = true

                allowFileAccess = true

                allowFileAccessFromFileURLs = false

                allowUniversalAccessFromFileURLs = false

                loadWithOverviewMode = true

                useWideViewPort = true

                builtInZoomControls = false

                displayZoomControls = false

                setSupportZoom(false)

                userAgentString = settings.userAgentString + " LunaApp/1.0"

            }

            addJavascriptInterface(WebAppInterface(), "LunaBridge")

            webViewClient = object : WebViewClient() {

                override fun onPageStarted(view: WebView?, url: String?, favicon: Bitmap?) {

                    super.onPageStarted(view, url, favicon)

                    if (url?.contains("onboarding") == false && url?.contains("spinner") == false) {

                        isConnected = true

                    }

                }

                override fun onPageFinished(view: WebView?, url: String?) {

                    super.onPageFinished(view, url)

                }

            }

        }

    }



    private fun connectToServer() {

        if (serverIp.isEmpty()) return

        val url = "http://${serverIp}:${serverPort}/"

        showConnecting(true)

        thread {

            try {

                val socket = Socket()

                socket.connect(InetSocketAddress(serverIp, serverPort), 800)

                socket.close()

                runOnUiThread { onServerReachable(url) }

            } catch (e: Exception) {

                isConnected = false

                runOnUiThread {

                    showConnecting(false)

                    webView.visibility = View.VISIBLE

                    nativeUi.visibility = View.GONE

                    val errMsg = e.localizedMessage ?: e.javaClass.simpleName

                    Toast.makeText(this@MainActivity, errMsg, Toast.LENGTH_LONG).show()

                    webView.loadUrl(onboardingUrl(error = true))

                }

            }

        }

    }



    private fun onServerReachable(url: String) {

        fetchConfigAndConnect()

    }



    private fun fetchConfigAndConnect() {

        scope.launch {

            try {

                val url = java.net.URL("http://${serverIp}:${serverPort}/api/config")

                val conn = url.openConnection() as java.net.HttpURLConnection

                conn.connectTimeout = 8000

                conn.readTimeout = 8000

                val body = conn.inputStream.bufferedReader().use { it.readText() }

                if (body.isNotEmpty()) {

                    lastConfigJson = body

                    val config = ConfigParser.parse(body)

                    runOnUiThread { onConfigLoaded(config) }

                }

            } catch (e: Exception) {

                runOnUiThread {

                    showConnecting(false)

                    webView.visibility = View.VISIBLE

                    nativeUi.visibility = View.GONE

                    Toast.makeText(this@MainActivity, getString(R.string.config_error), Toast.LENGTH_SHORT).show()

                    webView.loadUrl(onboardingUrl(error = true))

                }

            }

        }

    }



    private fun onConfigLoaded(config: LunaConfig) {

        profiles = config.profiles

        currentProfileName = config.activeProfile.ifEmpty {

            config.profiles.keys.firstOrNull() ?: ""

        }



        lastUpdateCheckTime = System.currentTimeMillis()
        checkForUpdate()

        checkForUpdateFromWeb()



        wsClient = LunaWebSocket(

            ip = serverIp,

            port = serverPort,

            onConnected = { runOnUiThread { onWsConnected() } },

            onDisconnected = { runOnUiThread { onWsDisconnected() } },

            onProfileSwitch = { profile, window ->

                runOnUiThread { handleProfileSwitch(profile, window) }

            },

            onProStatus = { isPro ->

                runOnUiThread { handleProStatus(isPro) }

            },

            onError = { msg -> runOnUiThread { Toast.makeText(this, msg, Toast.LENGTH_SHORT).show() } },

            onThemeUpdate = { themes ->

                val mobile = themes.optJSONObject("mobile")

                if (mobile != null) {

                    val c = JSONObject()

                    c.put("gridBtnBg", mobile.optString("grid_btn_bg", "#2A2A2A"))

                    c.put("gridBtnBorder", mobile.optString("grid_btn_border", "#3A3A3A"))

                    c.put("gridBtnActiveBg", mobile.optString("grid_btn_active_bg", "#4FC3F7"))

                    runOnUiThread {

                        rebuildGrid()

                    }

                }

            },

            onConfigUpdated = {

                runOnUiThread {

                    rebuildGrid()

                }

            }

        )

        wsClient?.connect()



        showNativeUI(config)

        startConfigPolling()



        scope.launch(Dispatchers.IO) {

            delay(1500)

            try {

                val req = Request.Builder().url("http://${serverIp}:${serverPort}/api/themes").build()

                val res = okHttp.newCall(req).execute()

                val body = res.body?.string() ?: ""

                if (body.isNotEmpty()) {

                    val themes = JSONObject(body)

                    val mobile = themes.optJSONObject("mobile")

                    if (mobile != null) {

                        val c = JSONObject()

                        c.put("gridBtnBg", mobile.optString("grid_btn_bg", "#2A2A2A"))

                        c.put("gridBtnBorder", mobile.optString("grid_btn_border", "#3A3A3A"))

                        c.put("gridBtnActiveBg", mobile.optString("grid_btn_active_bg", "#4FC3F7"))

                        runOnUiThread {

                            rebuildGrid()

                        }

                    }

                }

            } catch (e: Exception) {}

        }

    }



    private fun showNativeUI(config: LunaConfig) {

        showConnecting(false)

        webView.visibility = View.GONE

        nativeUi.visibility = View.VISIBLE

        isConnected = true

        statusDot.setBackgroundResource(R.drawable.circle_green)

        ipText.text = "${serverIp}:${serverPort}"



        adsRemoved = getSharedPreferences("luna_prefs", MODE_PRIVATE).getBoolean("ads_removed", false)



        buildProfileBar(config)

        buildPresetChips(config)

        buildGrid()

        showBannerIfNeeded()

        applyTheme(currentTheme)

    }



    private fun onWsConnected() {

        isConnected = true

        statusDot.setBackgroundResource(R.drawable.circle_green)

        showToast(getString(R.string.connected))

        showConnectionNotification(true)

    }



    private fun onWsDisconnected() {

        isConnected = false

        statusDot.setBackgroundResource(R.drawable.circle_red)

        showToast(getString(R.string.disconnected))

        showConnectionNotification(false)

    }



    private fun showToast(msg: String) {

        val toast = Toast.makeText(this, msg, Toast.LENGTH_SHORT)

        toast.setGravity(android.view.Gravity.TOP or android.view.Gravity.CENTER, 0, 120)

        toast.show()

    }



    private fun showBannerIfNeeded() {

        if (!adsRemoved) {

            adWebView?.let {

                it.visibility = View.VISIBLE

                it.loadUrl("https://sr-lolo.github.io/luna/ad_banner.html")

            }

            startAdRefresh()

        }

    }



    private fun startAdRefresh() {

        adRefreshJob?.cancel()

        adRefreshJob = scope.launch {

            while (isActive) {

                delay(30000)

                withContext(Dispatchers.Main) {

                    adWebView?.loadUrl("https://sr-lolo.github.io/luna/ad_banner.html?_=${System.currentTimeMillis()}")

                }

            }

        }

    }



    private fun stopAdRefresh() {

        adRefreshJob?.cancel()

        adRefreshJob = null

    }



    private fun showMenuDialog() {

        val t = currentTheme

        val container = LinearLayout(this).apply {

            orientation = LinearLayout.VERTICAL

            setPadding(8, 8, 8, 8)

        }

        fun menuItem(iconRes: Int, labelText: String, onClick: () -> Unit) {

            val row = LinearLayout(this).apply {

                orientation = LinearLayout.HORIZONTAL

                gravity = android.view.Gravity.CENTER_VERTICAL

                setPadding(16, 14, 16, 14)

                isClickable = true

                isFocusable = true

                setOnClickListener {

                    (tag as? android.app.Dialog)?.dismiss()

                    onClick()

                }

                val iv = ImageView(this@MainActivity).apply {

                    setImageResource(iconRes)

                    setColorFilter(t.accent, PorterDuff.Mode.SRC_IN)

                    layoutParams = LinearLayout.LayoutParams(28, 28).apply { setMargins(0, 0, 16, 0) }

                }

                addView(iv)

                val tv = TextView(this@MainActivity).apply {

                    text = labelText

                    textSize = 16f

                    setTextColor(t.textPrimary)

                }

                addView(tv)

            }

            container.addView(row)

        }

        menuItem(android.R.drawable.ic_dialog_info, getString(R.string.menu_help)) { showHelpDialog() }

        menuItem(android.R.drawable.ic_menu_manage, getString(R.string.menu_settings)) { showSettingsDialog() }
        menuItem(android.R.drawable.ic_menu_directions, getString(R.string.connect_usb)) {
            startWifiDiscovery()
        }

        val dialog = AlertDialog.Builder(this, R.style.Theme_Luna_Dialog)

            .setTitle(getString(R.string.menu_title))

            .setView(container)

            .setNegativeButton(getString(R.string.menu_close), null)

            .show()

        for (i in 0 until container.childCount) container.getChildAt(i).tag = dialog

    }



    private fun showHelpDialog() {

        val t = currentTheme

        val steps = listOf(

            getString(R.string.help_step1) to android.R.drawable.ic_menu_save,

            getString(R.string.help_step2) to android.R.drawable.ic_menu_camera,

            getString(R.string.help_step3) to android.R.drawable.ic_menu_crop,

            getString(R.string.help_step4) to android.R.drawable.ic_media_play

        )

        val container = LinearLayout(this).apply {

            orientation = LinearLayout.VERTICAL

            setPadding(16, 8, 16, 8)

        }

        for ((i, step) in steps.withIndex()) {

            val row = LinearLayout(this).apply {

                orientation = LinearLayout.HORIZONTAL

                gravity = android.view.Gravity.CENTER_VERTICAL

                setPadding(8, 10, 8, 10)

                val numBg = FrameLayout(this@MainActivity).apply {

                    layoutParams = LinearLayout.LayoutParams(32, 32).apply { setMargins(0, 0, 12, 0) }

                    background = GradientDrawable().apply {

                        shape = GradientDrawable.OVAL

                        setColor(t.accent)

                    }

                    val numTv = TextView(this@MainActivity).apply {

                        text = "${i + 1}"

                        textSize = 14f

                        setTextColor(Color.WHITE)

                        gravity = android.view.Gravity.CENTER

                    }

                    addView(numTv, FrameLayout.LayoutParams(32, 32))

                }

                addView(numBg)

                val icon = ImageView(this@MainActivity).apply {

                    setImageResource(step.second)

                    setColorFilter(t.textSecondary, PorterDuff.Mode.SRC_IN)

                    layoutParams = LinearLayout.LayoutParams(24, 24).apply { setMargins(0, 0, 12, 0) }

                }

                addView(icon)

                val tv = TextView(this@MainActivity).apply {

                    text = step.first

                    textSize = 13f

                    setTextColor(t.textPrimary)

                }

                addView(tv)

            }

            container.addView(row)

        }

        val extra = TextView(this).apply {

            text = getString(R.string.help_hint)

            textSize = 12f

            setTextColor(t.textSecondary)

            setPadding(8, 8, 8, 4)

            gravity = android.view.Gravity.CENTER

        }

        container.addView(extra)

        AlertDialog.Builder(this, R.style.Theme_Luna_Dialog)

            .setTitle(getString(R.string.menu_help))

            .setView(container)

            .setPositiveButton(getString(R.string.help_got_it), null)

            .show()

    }



    private fun handleProfileSwitch(profile: String, window: String) {

        if (profiles.containsKey(profile)) {

            currentProfileName = profile

            switchGridProfile(profile)

            highlightProfileChip(profile)

            showToast("$profile${if (window.isNotEmpty()) " - $window" else ""}")

        }

    }



    private fun handleProStatus(isPro: Boolean) {

        if (isPro && !adsRemoved) {

            adsRemoved = true

            getSharedPreferences("luna_prefs", MODE_PRIVATE).edit()

                .putBoolean("ads_removed", true).apply()

            adWebView?.visibility = View.GONE

            stopAdRefresh()

            if (profiles.isNotEmpty()) {

                val cfg = LunaConfig(profiles, currentProfileName, emptyList())

                buildProfileBar(cfg)

                buildPresetChips(cfg)

            }

        } else if (!isPro && adsRemoved) {

            adsRemoved = false

            getSharedPreferences("luna_prefs", MODE_PRIVATE).edit()

                .putBoolean("ads_removed", false).apply()

            showBannerIfNeeded()

            if (profiles.isNotEmpty()) {

                val cfg = LunaConfig(profiles, currentProfileName, emptyList())

                buildProfileBar(cfg)

                buildPresetChips(cfg)

            }

        }

    }



    private fun buildProfileBar(config: LunaConfig) {

        val t = currentTheme

        profileBar.removeAllViews()

        val entries = if (adsRemoved) config.profiles.entries else config.profiles.entries.take(3)

        for ((name, _) in entries) {

            val chip = Button(this).apply {

                text = name

                setTextColor(t.chipText)

                textSize = 11f

                setBackgroundColor(t.chipBg)

                setPadding(12, 4, 12, 4)

                layoutParams = LinearLayout.LayoutParams(

                    LinearLayout.LayoutParams.WRAP_CONTENT,

                    30.dpToPx()

                ).apply { setMargins(0, 0, 6, 0) }

                setOnClickListener {

                    currentProfileName = name

                    switchGridProfile(name)

                    highlightProfileChip(name)

                }

            }

            profileBar.addView(chip)

        }

        highlightProfileChip(currentProfileName)

    }



    private fun buildPresetChips(config: LunaConfig) {

        val t = currentTheme

        val validProfiles = if (adsRemoved) config.profiles.keys else config.profiles.keys.take(3).toSet()

        for (rule in config.appSwitchRules) {

            if (rule.label.isNotEmpty() && rule.profile in validProfiles) {

                val chip = Button(this).apply {

                    text = "${rule.label} \u2192 ${rule.profile}"

                    setTextColor(t.textSecondary)

                    textSize = 10f

                    setBackgroundColor(t.chipBg)

                    setPadding(10, 3, 10, 3)

                    layoutParams = LinearLayout.LayoutParams(

                        LinearLayout.LayoutParams.WRAP_CONTENT,

                        26.dpToPx()

                    ).apply { setMargins(0, 0, 6, 0) }

                    setOnClickListener {

                        if (profiles.containsKey(rule.profile)) {

                            currentProfileName = rule.profile

                            switchGridProfile(rule.profile)

                        }

                    }

                }

                profileBar.addView(chip)

            }

        }

    }



    private fun highlightProfileChip(name: String) {

        val t = currentTheme

        for (i in 0 until profileBar.childCount) {

            val chip = profileBar.getChildAt(i) as? Button ?: continue

            val isActive = chip.text.toString() == name || chip.text.toString().startsWith(name)

            chip.setTextColor(if (isActive) t.chipTextActive else t.chipText)

            chip.setBackgroundColor(if (isActive) t.chipBgActive else t.chipBg)

        }

    }



    private fun switchMode(mode: String) {

        currentMode = mode

        if (mode == "grid") {

            gridLayout.visibility = View.VISIBLE

            slidersPanel.visibility = View.GONE

            modeGridBtn.setBackgroundResource(R.drawable.mode_bg_active)

            modeSlidersBtn.setBackgroundResource(R.drawable.mode_bg)

        } else {

            gridLayout.visibility = View.GONE

            slidersPanel.visibility = View.VISIBLE

            modeGridBtn.setBackgroundResource(R.drawable.mode_bg)

            modeSlidersBtn.setBackgroundResource(R.drawable.mode_bg_active)

        }

    }



    private fun startConfigPolling() {

        configPolling?.cancel()

        configPolling = scope.launch {

            while (isActive) {

                delay(5000)

                try {

                    val request = Request.Builder().url("http://${serverIp}:${serverPort}/api/config").build()

                    val response = okHttp.newCall(request).execute()

                    val body = response.body?.string() ?: ""

                    if (body.isNotEmpty() && body != lastConfigJson) {

                        val config = ConfigParser.parse(body)

                        profiles = config.profiles

                        runOnUiThread {

                            try {

                                buildProfileBar(config)

                                applyTheme(currentTheme)

                                rebuildGrid()

                                if (config.activeProfile.isNotEmpty() && config.activeProfile != currentProfileName) {

                                    currentProfileName = config.activeProfile

                                    switchGridProfile(config.activeProfile)

                                }

                                lastConfigJson = body



                            } catch (e: Exception) {}



                        }

                    }

                } catch (e: Exception) {}

            }

        }

    }



    private fun showConnecting(show: Boolean) {

        spinnerOverlay.visibility = if (show) View.VISIBLE else View.GONE

    }



    private fun disconnect() {

        isConnected = false

        wsClient?.disconnect()

        wsClient = null

        configPolling?.cancel()

        val prefs = getSharedPreferences("luna_prefs", MODE_PRIVATE)

        prefs.edit().remove("server_ip").remove("luna_first_connection_done").apply()

        serverIp = ""

    }



    private fun showSettingsDialog() {

        val t = currentTheme

        val prefs = getSharedPreferences("luna_prefs", MODE_PRIVATE)

        val container = LinearLayout(this).apply {

            orientation = LinearLayout.VERTICAL

            setPadding(16, 8, 16, 8)

        }

        fun sectionLabel(text: String): TextView = TextView(this).apply {

            this.text = text

            textSize = 11f

            setTextColor(t.accent)

            setPadding(4, 16, 4, 4)

            isAllCaps = true

        }

        fun settingsRow(iconRes: Int, title: String, summary: String, onClick: () -> Unit) {

            val row = LinearLayout(this).apply {

                orientation = LinearLayout.HORIZONTAL

                gravity = android.view.Gravity.CENTER_VERTICAL

                setPadding(12, 12, 12, 12)

                isClickable = true

                isFocusable = true

                setOnClickListener { onClick() }

                val iv = ImageView(this@MainActivity).apply {

                    setImageResource(iconRes)

                    setColorFilter(t.textSecondary, PorterDuff.Mode.SRC_IN)

                    layoutParams = LinearLayout.LayoutParams(24, 24).apply { setMargins(0, 0, 12, 0) }

                }

                addView(iv)

                val inner = LinearLayout(this@MainActivity).apply {

                    orientation = LinearLayout.VERTICAL

                    val tv = TextView(this@MainActivity).apply {

                        text = title

                        textSize = 15f

                        setTextColor(t.textPrimary)

                    }

                    addView(tv)

                    val sv = TextView(this@MainActivity).apply {

                        text = summary

                        textSize = 12f

                        setTextColor(t.textSecondary)

                    }

                    addView(sv)

                }

                addView(inner)

            }

            container.addView(row)

        }

        fun settingsSwitch(iconRes: Int, title: String, summary: String, checked: Boolean, onToggle: (Boolean) -> Unit) {

            val row = LinearLayout(this).apply {

                orientation = LinearLayout.HORIZONTAL

                gravity = android.view.Gravity.CENTER_VERTICAL

                setPadding(12, 12, 12, 12)

                val iv = ImageView(this@MainActivity).apply {

                    setImageResource(iconRes)

                    setColorFilter(t.textSecondary, PorterDuff.Mode.SRC_IN)

                    layoutParams = LinearLayout.LayoutParams(24, 24).apply { setMargins(0, 0, 12, 0) }

                }

                addView(iv)

                val inner = LinearLayout(this@MainActivity).apply {

                    orientation = LinearLayout.VERTICAL

                    layoutParams = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f)

                    val tv = TextView(this@MainActivity).apply {

                        text = title

                        textSize = 15f

                        setTextColor(t.textPrimary)

                    }

                    addView(tv)

                    val sv = TextView(this@MainActivity).apply {

                        text = summary

                        textSize = 12f

                        setTextColor(t.textSecondary)

                    }

                    addView(sv)

                }

                addView(inner)

                val sw = Switch(this@MainActivity).apply {

                    isChecked = checked

                    thumbTintList = ColorStateList.valueOf(if (checked) t.accent else t.textSecondary)

                    trackTintList = ColorStateList.valueOf(if (checked) t.accent else 0x33FFFFFF.toInt())

                    setOnCheckedChangeListener { _, isChecked ->

                        onToggle(isChecked)

                        thumbTintList = ColorStateList.valueOf(if (isChecked) t.accent else t.textSecondary)

                        trackTintList = ColorStateList.valueOf(if (isChecked) t.accent else 0x33FFFFFF.toInt())

                    }

                }

                addView(sw)

            }

            container.addView(row)

        }



        container.addView(sectionLabel(getString(R.string.settings_connection)))

        settingsRow(android.R.drawable.ic_menu_compass, getString(R.string.settings_server), serverIp.ifEmpty { getString(R.string.settings_not_connected) }) {

            WebAppInterface().showManualEntry()

        }

        settingsRow(android.R.drawable.ic_menu_close_clear_cancel, getString(R.string.settings_change_connection), getString(R.string.settings_change_connection_summary)) {
            disconnect()
            webView.visibility = View.VISIBLE
            nativeUi.visibility = View.GONE
            webView.loadUrl(onboardingUrl())
        }

        container.addView(sectionLabel(getString(R.string.settings_personalization)))

        settingsRow(android.R.drawable.ic_menu_gallery, getString(R.string.settings_themes), getString(currentTheme.displayNameRes)) {

            showDesignsDialog()

        }

        container.addView(sectionLabel(getString(R.string.settings_behavior)))

        settingsSwitch(

            android.R.drawable.ic_menu_view, getString(R.string.settings_wakelock),

            getString(R.string.settings_wakelock_summary), keepScreenOn

        ) { enabled ->

            keepScreenOn = enabled

            prefs.edit().putBoolean("keep_screen_on", enabled).apply()

            if (enabled) window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)

            else window.clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)

        }

        settingsSwitch(

            android.R.drawable.ic_dialog_info, getString(R.string.settings_notifications),

            getString(R.string.settings_notif_summary), notificationsEnabled

        ) { enabled ->

            notificationsEnabled = enabled

            prefs.edit().putBoolean("notifications", enabled).apply()

            if (!enabled) {

                val nm = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager

                nm.cancelAll()

            }

        }

        AlertDialog.Builder(this, R.style.Theme_Luna_Dialog)

            .setTitle(getString(R.string.settings_title))

            .setView(container)

            .setNegativeButton(getString(R.string.menu_close), null)

            .show()

    }



    private fun showDesignsDialog() {

        val grid = GridLayout(this).apply {

            columnCount = 2

            setPadding(8, 8, 8, 8)

        }

        for (theme in ThemeManager.themes) {

            val card = LinearLayout(this).apply {

                orientation = LinearLayout.VERTICAL

                gravity = android.view.Gravity.CENTER

                setPadding(12, 12, 12, 12)

                isClickable = true

                isFocusable = true

                val lp = GridLayout.LayoutParams().apply {

                    width = 0

                    height = GridLayout.LayoutParams.WRAP_CONTENT

                    columnSpec = GridLayout.spec(GridLayout.UNDEFINED, 1f)

                    rowSpec = GridLayout.spec(GridLayout.UNDEFINED)

                    setMargins(6, 6, 6, 6)

                }

                layoutParams = lp

                background = GradientDrawable().apply {

                    shape = GradientDrawable.RECTANGLE

                    cornerRadius = 12f

                    setColor(theme.bgSurface)

                    setStroke(2, if (theme.name == currentTheme.name) theme.accent else theme.bgSurface)

                }

                val preview = View(this@MainActivity).apply {

                    layoutParams = LinearLayout.LayoutParams(48, 48).apply { setMargins(0, 0, 0, 6) }

                    background = GradientDrawable().apply {

                        shape = GradientDrawable.OVAL

                        setColor(theme.accent)

                    }

                }

                addView(preview)

                val name = TextView(this@MainActivity).apply {

                    text = getString(theme.displayNameRes)

                    textSize = 13f

                    setTextColor(if (theme.name == currentTheme.name) theme.accent else theme.textPrimary)

                }

                addView(name)

                setOnClickListener {

                    currentTheme = theme

                    getSharedPreferences("luna_prefs", MODE_PRIVATE).edit()

                        .putString("theme", theme.name).apply()

                    applyTheme(theme)

                    (tag as? android.app.Dialog)?.dismiss()

                }

            }

            grid.addView(card)

        }

        val dialog = AlertDialog.Builder(this, R.style.Theme_Luna_Dialog)

            .setTitle(getString(R.string.theme_picker_title))

            .setView(grid)

            .setNegativeButton(getString(R.string.menu_close), null)

            .show()

        for (i in 0 until grid.childCount) grid.getChildAt(i).tag = dialog

    }



    private fun buildGrid() {
        gridLayout.removeAllViews()
        val profile = profiles[currentProfileName] ?: return
        val keys = profile.keys
        if (keys.isEmpty()) return
        val gap = 3.dpToPx()
        val availWidth = resources.displayMetrics.widthPixels
        val availHeight = resources.displayMetrics.heightPixels - 48.dpToPx() - 40.dpToPx() - 36.dpToPx()
        var bestCols = 4
        var bestSize = 0
        var bestScore = 0f
        for (c in 2..7) {
            val r = Math.ceil(keys.size.toDouble() / c).toInt()
            val sz = (availWidth - gap * (c + 1)) / c
            val gridH = sz * r + gap * (r + 1)
            val penalty = if (gridH > availHeight) availHeight.toFloat() / gridH else 1f
            val score = sz * penalty
            if (score > bestScore) {
                bestScore = score
                bestSize = sz
                bestCols = c
            }
        }
        gridLayout.columnCount = bestCols
        for ((index, k) in keys.withIndex()) {
            val row = index / bestCols
            val col = index % bestCols
            val cell = createGridCell(k, bestSize)
            cell.layoutParams = GridLayout.LayoutParams().apply {
                width = bestSize
                height = bestSize
                columnSpec = GridLayout.spec(col)
                rowSpec = GridLayout.spec(row)
                setMargins(gap, gap, gap, gap)
            }
            gridLayout.addView(cell)
        }
    }

    private fun rebuildGrid() {
        runOnUiThread { buildGrid() }
    }

    companion object {
        private val ICON_MAP = mapOf(
            "\u232B" to "backspace", "\u23CE" to "enter", "\u238B" to "escape",
            "\u21E7" to "shift", "Tab" to "tap", "\u2423" to "space",
            "\u25C1" to "arrow-left", "\u25B2" to "arrow-up",
            "\u25BC" to "arrow-down", "\u25B7" to "arrow-right",
            "PTT" to "mic", "MicSil" to "mic-off",
            "Vol+" to "vol-up", "Vol-" to "vol-down",
            "obs1" to "esc-1", "obs2" to "esc-2", "obs3" to "esc-3", "obs4" to "esc-4",
            "Str On" to "stream-on", "Str Off" to "stream-off",
            "Rec On" to "rec-on", "Rec Off" to "rec-off",
            "Silen" to "silent", "Mute" to "silent",
            "P/P" to "play-pause2", "\u23EF" to "play-pause2",
            "Next" to "skip-next", "Prev" to "skip-prev",
            "+Pest" to "tab-new", "Cerrar" to "tap-close",
            "Sig" to "skip-next", "Ant" to "skip-prev",
            "URL" to "url", "Recarg" to "reload",
            "Atr\u00E1s" to "back", "Adel" to "forward",
            "Reabrir" to "tab-reopen", "Fav" to "fav",
            "Desc" to "downloads", "Hist" to "history",
            "Buscar" to "search", "Esc" to "escape"
        )
    }

    private fun createGridCell(k: LunaKey, btnSize: Int): View {
        val container = FrameLayout(this)
        val gd = GradientDrawable().apply {
            setColor(Color.parseColor(currentTheme.gridBtnBg))
            cornerRadius = 8.dpToPx().toFloat()
            setStroke(1.dpToPx(), Color.parseColor(currentTheme.gridBtnBorder))
        }
        container.background = gd

        val iconName = if (k.icon.isNotEmpty()) k.icon else ICON_MAP[k.label]
        if (iconName != null) {
            val imageView = ImageView(this).apply {
                val margin = 4.dpToPx()
                layoutParams = FrameLayout.LayoutParams(
                    FrameLayout.LayoutParams.MATCH_PARENT,
                    FrameLayout.LayoutParams.MATCH_PARENT
                ).apply {
                    setMargins(margin, margin, margin, margin)
                }
                scaleType = ImageView.ScaleType.FIT_CENTER
            }
            container.addView(imageView)

            val url = resolveIconUrl(iconName)
            scope.launch {
                try {
                    val conn = java.net.URL(url).openConnection() as java.net.HttpURLConnection
                    conn.connectTimeout = 8000
                    conn.readTimeout = 8000
                    conn.doInput = true
                    val bytes = conn.inputStream.use { it.readBytes() }
                    val bitmap = android.graphics.BitmapFactory.decodeByteArray(bytes, 0, bytes.size)
                    runOnUiThread {
                        if (imageView.isAttachedToWindow) {
                            imageView.setImageBitmap(bitmap)
                        }
                    }
                } catch (e: Exception) {
                    runOnUiThread {
                        if (imageView.isAttachedToWindow) {
                            imageView.setImageResource(android.R.drawable.ic_menu_gallery)
                        }
                    }
                }
            }
        }

        if (k.label.isNotEmpty()) {
            val textView = TextView(this).apply {
                text = k.label
                textSize = 10f
                setTypeface(null, android.graphics.Typeface.BOLD)
                setTextColor(Color.parseColor(currentTheme.gridBtnText))
                gravity = Gravity.CENTER
                
                if (iconName != null) {
                    layoutParams = FrameLayout.LayoutParams(
                        FrameLayout.LayoutParams.MATCH_PARENT,
                        FrameLayout.LayoutParams.WRAP_CONTENT,
                        Gravity.BOTTOM or Gravity.CENTER_HORIZONTAL
                    ).apply {
                        setMargins(4.dpToPx(), 0, 4.dpToPx(), 4.dpToPx())
                    }
                    setShadowLayer(3f, 1f, 1f, Color.BLACK)
                    setBackgroundColor(Color.parseColor("#80000000")) 
                    setPadding(2.dpToPx(), 2.dpToPx(), 2.dpToPx(), 2.dpToPx())
                } else {
                    layoutParams = FrameLayout.LayoutParams(
                        FrameLayout.LayoutParams.MATCH_PARENT,
                        FrameLayout.LayoutParams.MATCH_PARENT,
                        Gravity.CENTER
                    )
                    setPadding(4.dpToPx(), 4.dpToPx(), 4.dpToPx(), 4.dpToPx())
                }
            }
            container.addView(textView)
        }

        container.setOnTouchListener { v, ev ->
            when (ev.action) {
                MotionEvent.ACTION_DOWN -> {
                    val activeGd = GradientDrawable().apply {
                        setColor(Color.parseColor(currentTheme.gridBtnActiveBg))
                        cornerRadius = 8.dpToPx().toFloat()
                        setStroke(1.dpToPx(), Color.parseColor(currentTheme.gridBtnBorder))
                    }
                    v.background = activeGd
                    if (k.mods != 0) {
                        wsClient?.sendKeyTap(k.keyCode, k.mods)
                    } else {
                        wsClient?.sendKeyPress(k.keyCode, 0)
                    }
                    v.playSoundEffect(SoundEffectConstants.CLICK)
                    v.isPressed = true
                }
                MotionEvent.ACTION_UP -> {
                    if (k.mods == 0) wsClient?.sendKeyRelease(k.keyCode, 0)
                    restoreContainerBg(v)
                    v.isPressed = false
                }
                MotionEvent.ACTION_CANCEL -> {
                    restoreContainerBg(v)
                    v.isPressed = false
                }
            }
            true
        }

        return container
    }

    private fun restoreContainerBg(v: View) {
        val gd = GradientDrawable().apply {
            setColor(Color.parseColor(currentTheme.gridBtnBg))
            cornerRadius = 8.dpToPx().toFloat()
            setStroke(1.dpToPx(), Color.parseColor(currentTheme.gridBtnBorder))
        }
        v.background = gd
    }


    

    private fun resolveIconUrl(icon: String): String {
        val base = "http://${serverIp}:${serverPort}"
        return if (icon.startsWith("custom/")) {
            "$base/custom-icons/" + icon.removePrefix("custom/")
        } else {
            val name = if ('.' in icon) icon else "$icon.png"
            "$base/icons/$name"
        }
    }
    private fun switchGridProfile(name: String) {

        currentProfileName = name

        rebuildGrid()

    }



    private fun applyTheme(t: LunaTheme) {

        nativeUi.setBackgroundColor(t.bgPrimary)

        headerBar.setBackgroundColor(t.bgSurface)

        connInfo.setBackgroundColor(t.bgSurface)

        contentArea.setBackgroundColor(t.bgPrimary)

        ipText.setTextColor(t.textSecondary)

        menuBtn.setTextColor(t.textPrimary)

        rescanQrBtn.setColorFilter(t.textSecondary, PorterDuff.Mode.SRC_IN)

        for (i in 0 until (headerBar as ViewGroup).childCount) {

            val child = (headerBar as ViewGroup).getChildAt(i)

            if (child is ImageButton && child != modeGridBtn && child != modeSlidersBtn && child != uiToggleBtn && child != rescanQrBtn) {

                child.setColorFilter(t.textSecondary, PorterDuff.Mode.SRC_IN)

            }

        }

        for (i in 0 until profileBar.childCount) {

            val chip = profileBar.getChildAt(i) as? Button ?: continue

            val isActive = chip.text.toString() == currentProfileName

            chip.setTextColor(if (isActive) t.chipTextActive else t.chipText)

            chip.setBackgroundColor(if (isActive) t.chipBgActive else t.chipBg)

        }

        volumeSlider.progressTintList = ColorStateList.valueOf(t.sliderThumb)

        volumeSlider.thumbTintList = ColorStateList.valueOf(t.sliderThumb)

        brightnessSlider.progressTintList = ColorStateList.valueOf(t.sliderThumb)

        brightnessSlider.thumbTintList = ColorStateList.valueOf(t.sliderThumb)

        volumeValue.setTextColor(t.textPrimary)

        brightnessValue.setTextColor(t.textPrimary)

        scrollPadV.setColors(t.scrollPadBg, t.scrollPadThumb, t.scrollPadTrack, t.scrollPadArrow)

        scrollPadH.setColors(t.scrollPadBg, t.scrollPadThumb, t.scrollPadTrack, t.scrollPadArrow)

        fun recolorText(vg: ViewGroup) {

            for (i in 0 until vg.childCount) {

                val child = vg.getChildAt(i)

                if (child is TextView && child != volumeValue && child != brightnessValue) {

                    child.setTextColor(t.textSecondary)

                }

                if (child is ViewGroup) recolorText(child)

            }

        }

        recolorText(slidersPanel as ViewGroup)

        try {

            val c = JSONObject()

            c.put("gridBtnBg", t.gridBtnBg)

            c.put("gridBtnBorder", t.gridBtnBorder)

            c.put("gridBtnActiveBg", t.gridBtnActiveBg)

            c.put("gridBtnText", t.gridBtnText)

                        // apply native grid colors
            for (i in 0 until gridLayout.childCount) {
                val cell = gridLayout.getChildAt(i) as? ViewGroup ?: continue
                val gd = cell.background as? GradientDrawable
                if (gd != null) {
                    gd.setColor(Color.parseColor(t.gridBtnBg))
                    gd.setStroke(1.dpToPx(), Color.parseColor(t.gridBtnBorder))
                }
                for (j in 0 until cell.childCount) {
                    val child = cell.getChildAt(j)
                    if (child is TextView) {
                        child.setTextColor(Color.parseColor(t.gridBtnText))
                    }
                }
            }

        } catch (e: Exception) {}

    }



    private fun showConnectionNotification(connected: Boolean) {

        if (!notificationsEnabled) return

        val channelId = "luna_connection"

        val nm = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {

            val channel = NotificationChannel(channelId, getString(R.string.notif_channel), NotificationManager.IMPORTANCE_DEFAULT)

            nm.createNotificationChannel(channel)

        }

        val notification = NotificationCompat.Builder(this, channelId)

            .setSmallIcon(android.R.drawable.ic_dialog_info)

            .setContentTitle(getString(R.string.notif_title))

            .setContentText(if (connected) getString(R.string.notif_connected, serverIp, serverPort.toString()) else getString(R.string.notif_disconnected))

            .setAutoCancel(true)

            .setColor(currentTheme.accent)

            .build()

        nm.notify(1, notification)

    }

    override fun onConfigurationChanged(newConfig: Configuration) {

        super.onConfigurationChanged(newConfig)

        if (::gridLayout.isInitialized) gridLayout.post { rebuildGrid() }

    }
    override fun onKeyDown(keyCode: Int, event: KeyEvent?): Boolean {

        if (keyCode == KeyEvent.KEYCODE_BACK) {

            if (isUiHidden) {

                isUiHidden = false

                headerBar.visibility = View.VISIBLE

                findViewById<View>(R.id.profileBarScroll).visibility = View.VISIBLE

                connInfo.visibility = View.VISIBLE

                uiToggleBtn.setImageResource(R.drawable.hide)

            }

            return true

        }

        return super.onKeyDown(keyCode, event)

    }



    override fun onDestroy() {

        super.onDestroy()

        wsClient?.disconnect()

        configPolling?.cancel()

        scope.cancel()

        val nm = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager

        nm.cancelAll()

    }



    private fun openQRScanner() {

        if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED) {

            permissionLauncher.launch(Manifest.permission.CAMERA)

            return

        }

        qrLauncher.launch(Intent(this, QrScannerActivity::class.java))

    }

    private fun parseAndConnect(text: String) {
        try {
            val json = org.json.JSONObject(text)
            if (json.optString("type") == "luna_pair") {
                val ip = json.optString("ip", "")
                val port = json.optInt("port", 9120)
                val code = json.optString("code", "")
                if (ip.isNotEmpty() && code.isNotEmpty()) {
                    pairWithServer(DiscoveredServer(ip, port), code)
                    return
                }
            }
        } catch (e: Exception) {}

        val ipPort = extractIpPort(text)
        val parts = ipPort.split(":")

        serverIp = parts[0]

        serverPort = 9120

        saveIp(ipPort)

        connectToServer()

    }



    private fun extractIpPort(text: String): String {

        var clean = text.trim()

        if (clean.startsWith("http://") || clean.startsWith("https://"))

            clean = clean.substringAfter("://")

        val slashIdx = clean.indexOf('/')

        if (slashIdx >= 0) clean = clean.substring(0, slashIdx)

        val ip = clean.split(":")[0].trim()

        return "$ip:9120"

    }



    private fun saveIp(ipPort: String) {

        getSharedPreferences("luna_prefs", MODE_PRIVATE)

            .edit().putString("server_ip", ipPort).apply()

    }



    private fun checkForUpdate() {

        if (isUpdateDialogShowing) return

        val now = System.currentTimeMillis()
        if (now - lastUpdateDismissTime < 604800000L) return

        thread {

            try {

                val conn = URL("http://${serverIp}:${serverPort}/api/version").openConnection()

                conn.connectTimeout = 3000

                conn.readTimeout = 3000

                val json = conn.inputStream.bufferedReader().readText()

                val serverVersion = JSONObject(json).getString("apk_version")

                val currentVersion = packageManager.getPackageInfo(packageName, android.content.pm.PackageManager.PackageInfoFlags.of(0L)).versionName ?: "1.0.0"

                if (compareVersions(serverVersion, currentVersion) > 0) {
                    val localUrl = "http://$serverIp:$serverPort/apk"
                    runOnUiThread { showUpdateDialog(serverVersion, "", false, "", localUrl, fallbackApkDownloadUrl) }
                }

            } catch (_: Exception) {}

        }

    }



    private fun checkForUpdateFromWeb() {

        if (isUpdateDialogShowing) return

        val now = System.currentTimeMillis()
        if (now - lastUpdateDismissTime < 604800000L) return

        thread {

            try {

                val conn = URL("https://sr-lolo.github.io/luna/version.json").openConnection()

                conn.connectTimeout = 5000

                conn.readTimeout = 5000

                val json = conn.inputStream.bufferedReader().readText()

                val obj = JSONObject(json)

                val webVersion = obj.getString("latest")

                val apkUrl = obj.optString("url", apkDownloadUrl)

                val fbUrl = obj.optString("fallback_url", fallbackApkDownloadUrl)

                val sha = obj.optString("sha256", "")

                val force = obj.optBoolean("force_update", false)

                val changelog = obj.optString("changelog", "")

                val currentVersion = packageManager.getPackageInfo(packageName, android.content.pm.PackageManager.PackageInfoFlags.of(0L)).versionName ?: "1.0.0"

                if (compareVersions(webVersion, currentVersion) > 0) {

                    runOnUiThread { showUpdateDialog(webVersion, changelog, force, sha, apkUrl, fbUrl) }

                }

            } catch (_: Exception) {}

        }

    }



    private fun showUpdateDialog(version: String, changelog: String, forceUpdate: Boolean, sha256: String, apkUrl: String, fallbackUrl: String) {

        if (isUpdateDialogShowing) return
        isUpdateDialogShowing = true

        val builder = AlertDialog.Builder(this@MainActivity, R.style.Theme_Luna_Dialog)
            .setCancelable(false)

        val dialogView = layoutInflater.inflate(R.layout.dialog_update, null)
        builder.setView(dialogView)

        val dialog = builder.create()

        val titleView = dialogView.findViewById<TextView>(R.id.updateTitle)
        val versionView = dialogView.findViewById<TextView>(R.id.updateVersion)
        val changelogScroll = dialogView.findViewById<ScrollView>(R.id.changelogScroll)
        val changelogView = dialogView.findViewById<TextView>(R.id.updateChangelog)
        val progressSection = dialogView.findViewById<View>(R.id.progressSection)
        val progressBar = dialogView.findViewById<ProgressBar>(R.id.updateProgress)
        val progressText = dialogView.findViewById<TextView>(R.id.progressText)
        val btnLater = dialogView.findViewById<Button>(R.id.btnLater)
        val btnUpdate = dialogView.findViewById<Button>(R.id.btnUpdate)

        versionView.text = "v$version"
        btnLater.text = getString(R.string.update_later)
        btnUpdate.text = getString(R.string.update_btn)

        if (changelog.isNotEmpty()) {
            changelogView.text = changelog
        } else {
            changelogView.text = getString(R.string.update_message, version)
        }

        if (forceUpdate) {
            titleView.text = getString(R.string.update_force_title)
            btnLater.visibility = View.GONE
        } else {
            titleView.text = getString(R.string.update_title)
        }

        btnLater.setOnClickListener {
            lastUpdateDismissTime = System.currentTimeMillis()
            isUpdateDialogShowing = false
            dialog.dismiss()
        }

        btnUpdate.setOnClickListener {
            changelogScroll.visibility = View.GONE
            progressSection.visibility = View.VISIBLE
            btnLater.isEnabled = false
            btnUpdate.isEnabled = false
            btnUpdate.text = getString(R.string.update_downloading)

            thread { downloadWithRetry(version, apkUrl, fallbackUrl, sha256, progressBar, progressText, dialog) }
        }

        dialog.setOnDismissListener { isUpdateDialogShowing = false }
        dialog.show()
    }



    private fun downloadWithRetry(version: String, apkUrl: String, fallbackUrl: String, sha256: String, progressBar: ProgressBar, progressText: TextView, dialog: android.app.Dialog) {

        val urlsToTry = mutableListOf(apkUrl)
        if (fallbackUrl.isNotEmpty() && fallbackUrl != apkUrl) urlsToTry.add(fallbackUrl)

        var lastError: String? = null

        for ((attempt, url) in urlsToTry.withIndex()) {
            try {
                val conn = URL(url).openConnection()

                conn.connectTimeout = 10000

                conn.readTimeout = 30000

                val contentLength = conn.contentLength

                val input = conn.getInputStream()

                val file = File(cacheDir, "Luna.apk")

                input.use { inp ->
                    FileOutputStream(file).use { out ->
                        val buffer = ByteArray(8192)
                        var bytesRead: Int
                        var totalRead = 0L
                        while (inp.read(buffer).also { bytesRead = it } != -1) {
                            out.write(buffer, 0, bytesRead)
                            totalRead += bytesRead
                            if (contentLength > 0) {
                                val p = (totalRead * 100 / contentLength).toInt()
                                runOnUiThread {
                                    progressBar.progress = p
                                    progressText.text = getString(R.string.update_progress, p)
                                }
                            }
                        }
                    }
                }

                if (sha256.isNotEmpty()) {
                    val hash = sha256hex(file)
                    if (!hash.equals(sha256, ignoreCase = true)) {
                        if (attempt < urlsToTry.size - 1) {
                            runOnUiThread { progressText.text = getString(R.string.update_checksum_error) }
                            Thread.sleep(2000L * (attempt + 1))
                            continue
                        } else {
                            throw Exception("SHA-256 mismatch")
                        }
                    }
                }

                runOnUiThread { dialog.dismiss() }

                val uri = FileProvider.getUriForFile(this@MainActivity, "${packageName}.fileprovider", file)
                val intent = Intent(Intent.ACTION_INSTALL_PACKAGE).apply {
                    data = uri
                    flags = Intent.FLAG_GRANT_READ_URI_PERMISSION or Intent.FLAG_ACTIVITY_NEW_TASK
                }
                runOnUiThread {
                    try { startActivity(intent) }
                    catch (e: Exception) {
                        Toast.makeText(this@MainActivity, getString(R.string.error_install), Toast.LENGTH_LONG).show()
                    }
                }
                return
            } catch (e: Exception) {
                lastError = e.localizedMessage
                if (attempt < urlsToTry.size - 1) {
                    Thread.sleep(2000L * (attempt + 1))
                }
            }
        }

        runOnUiThread {
            dialog.dismiss()
            Toast.makeText(this@MainActivity, getString(R.string.error_download, lastError ?: "Unknown"), Toast.LENGTH_LONG).show()
        }
    }



    private fun sha256hex(file: File): String {
        val digest = MessageDigest.getInstance("SHA-256")
        file.inputStream().use { fis ->
            val buffer = ByteArray(8192)
            var bytesRead: Int
            while (fis.read(buffer).also { bytesRead = it } != -1) {
                digest.update(buffer, 0, bytesRead)
            }
        }
        return digest.digest().joinToString("") { "%02x".format(it) }
    }



    private fun compareVersions(a: String, b: String): Int {
        val pa = a.split(".").map { it.toIntOrNull() ?: 0 }
        val pb = b.split(".").map { it.toIntOrNull() ?: 0 }
        for (i in 0 until maxOf(pa.size, pb.size)) {
            val va = pa.getOrElse(i) { 0 }
            val vb = pb.getOrElse(i) { 0 }
            if (va != vb) return va - vb
        }
        return 0
    }

    // -- Wi-Fi Discovery & Pairing --

    private data class DiscoveredServer(
        val ip: String,
        val port: Int = 9120,
        val name: String = "",
        val needsPairing: Boolean = true
    )

    private fun startWifiDiscovery() {
        showConnecting(true)
        thread {
            findServer { server ->
                runOnUiThread {
                    showConnecting(false)
                    if (server != null) {
                        showServerList(listOf(server))
                    } else {
                        showNoServerFound()
                    }
                }
            }
        }
    }

    private fun findServer(callback: (DiscoveredServer?) -> Unit) {
        val prefs = getSharedPreferences("luna_prefs", MODE_PRIVATE)
        val savedIp = prefs.getString("server_ip", "") ?: ""
        val savedUuid = prefs.getString("pc_uuid", "") ?: ""

        if (savedIp.isNotEmpty() && savedUuid.isNotEmpty()) {
            val parts = savedIp.split(":")
            val ip = parts[0].trim()
            val port = if (parts.size > 1) parts[1].trim().toIntOrNull() ?: 9120 else 9120
            try {
                val sock = Socket()
                sock.connect(InetSocketAddress(ip, port), 200)
                sock.close()
                val url = URL("http://$ip:$port/api/uuid")
                val conn = url.openConnection() as java.net.HttpURLConnection
                conn.connectTimeout = 500
                conn.readTimeout = 500
                val resp = conn.inputStream.bufferedReader().readText()
                conn.disconnect()
                val json = org.json.JSONObject(resp)
                if (json.optString("uuid", "") == savedUuid) {
                    callback(DiscoveredServer(ip, port, json.optString("name", ""), false))
                    return
                }
            } catch (e: Exception) {}
        }

        val udpResults = discoverServers()
        if (udpResults.isNotEmpty()) {
            callback(udpResults.first())
            return
        }

        val mdnsResults = discoverMDNS()
        if (mdnsResults.isNotEmpty()) {
            callback(mdnsResults.first())
            return
        }

        val httpResults = discoverByHTTPScan()
        if (httpResults.isNotEmpty()) {
            callback(httpResults.first())
            return
        }

        callback(null)
    }

    private fun discoverServers(): List<DiscoveredServer> {
        val results = mutableListOf<DiscoveredServer>()
        val wifi = applicationContext.getSystemService(Context.WIFI_SERVICE) as? android.net.wifi.WifiManager
        val multicastLock = wifi?.createMulticastLock("luna_discovery")
        multicastLock?.acquire()
        try {
            val sock = DatagramSocket(null)
            sock.reuseAddress = true
            sock.broadcast = true
            sock.soTimeout = 2000
            try {
                val d = wifi?.dhcpInfo
                if (d != null && d.ipAddress != 0) {
                    val ipInt = d.ipAddress
                    val phoneIpStr = "${ipInt and 0xFF}.${(ipInt shr 8) and 0xFF}.${(ipInt shr 16) and 0xFF}.${(ipInt shr 24) and 0xFF}"
                    sock.bind(InetSocketAddress(InetAddress.getByName(phoneIpStr), 0))
                } else {
                    sock.bind(InetSocketAddress(InetAddress.getByName("0.0.0.0"), 0))
                }
            } catch (e: Exception) {
                try { sock.bind(InetSocketAddress(InetAddress.getByName("0.0.0.0"), 0)) } catch (e: Exception) {}
            }

            val targets = mutableListOf("255.255.255.255")
            try {
                val dhcp = wifi?.dhcpInfo
                if (dhcp != null && dhcp.ipAddress != 0) {
                    val ipInt = dhcp.ipAddress
                    val maskInt = dhcp.netmask
                    if (maskInt != 0) {
                        val netAddr = ipInt and maskInt
                        val bcastInt = netAddr or maskInt.inv()
                        val bcastIp = "${bcastInt and 0xFF}.${(bcastInt shr 8) and 0xFF}.${(bcastInt shr 16) and 0xFF}.${(bcastInt shr 24) and 0xFF}"
                        if (bcastIp != "255.255.255.255") targets.add(bcastIp)
                    }
                }
            } catch (e: Exception) {}

            val msg = "LUNA_DISCOVER".toByteArray(Charsets.UTF_8)
            for (target in targets) {
                repeat(3) {
                    try {
                        sock.send(DatagramPacket(msg, msg.size, InetAddress.getByName(target), 53210))
                    } catch (e: Exception) {}
                    try { Thread.sleep(200) } catch (e: Exception) {}
                }
            }

            val buf = ByteArray(1024)
            val endTime = System.currentTimeMillis() + 3000
            while (System.currentTimeMillis() < endTime) {
                try {
                    val p = DatagramPacket(buf, buf.size)
                    sock.receive(p)
                    val json = String(p.data, 0, p.length, Charsets.UTF_8)
                    val obj = org.json.JSONObject(json)
                    if (obj.optString("type") == "luna_server") {
                        results.add(DiscoveredServer(
                            ip = try { obj.getJSONArray("ips").getString(0) } catch (e: Exception) { obj.optString("ip", "") },
                            port = obj.optInt("port", 9120),
                            name = obj.optString("name", ""),
                            needsPairing = obj.optBoolean("needs_pairing", true)
                        ))
                    }
                } catch (_: java.net.SocketTimeoutException) {
                    break
                }
            }
            sock.close()
        } catch (e: Exception) {
        } finally {
            try { multicastLock?.release() } catch (e: Exception) {}
        }
        return results.distinctBy { it.ip }
    }

    private fun discoverMDNS(): List<DiscoveredServer> {
        val results = mutableListOf<DiscoveredServer>()
        val latch = CountDownLatch(1)
        try {
            val nsdManager = getSystemService(Context.NSD_SERVICE) as? NsdManager ?: return results
            val discoveryListener = object : NsdManager.DiscoveryListener {
                override fun onDiscoveryStarted(regType: String) {}
                override fun onServiceFound(serviceInfo: NsdServiceInfo) {
                    nsdManager.resolveService(serviceInfo, object : NsdManager.ResolveListener {
                        override fun onServiceResolved(info: NsdServiceInfo) {
                            val host = info.host ?: return
                            results.add(DiscoveredServer(
                                ip = host.hostAddress ?: "",
                                port = info.port.takeIf { it > 0 } ?: 9120,
                                name = info.serviceName
                            ))
                            latch.countDown()
                        }
                        override fun onResolveFailed(info: NsdServiceInfo, errorCode: Int) {}
                    })
                }
                override fun onServiceLost(serviceInfo: NsdServiceInfo) {}
                override fun onDiscoveryStopped(regType: String) {}
                override fun onStartDiscoveryFailed(regType: String, errorCode: Int) { latch.countDown() }
                override fun onStopDiscoveryFailed(regType: String, errorCode: Int) {}
            }
            nsdManager.discoverServices("_luna._tcp", NsdManager.PROTOCOL_DNS_SD, discoveryListener)
            latch.await(3, TimeUnit.SECONDS)
            try { nsdManager.stopServiceDiscovery(discoveryListener) } catch (e: Exception) {}
        } catch (e: Exception) {}
        return results
    }

    private fun discoverByHTTPScan(): List<DiscoveredServer> {
        val results = Collections.synchronizedList(mutableListOf<DiscoveredServer>())
        try {
            val wifi = applicationContext.getSystemService(Context.WIFI_SERVICE) as? android.net.wifi.WifiManager ?: return results
            val dhcp = wifi.dhcpInfo ?: return results
            if (dhcp.ipAddress == 0 || dhcp.netmask == 0) return results
            val ipInt = dhcp.ipAddress
            val maskInt = dhcp.netmask
            val netAddr = ipInt and maskInt
            val phoneIp = "${ipInt and 0xFF}.${(ipInt shr 8) and 0xFF}.${(ipInt shr 16) and 0xFF}.${(ipInt shr 24) and 0xFF}"
            val prefix = "${netAddr and 0xFF}.${(netAddr shr 8) and 0xFF}.${(netAddr shr 16) and 0xFF}."
            val executor = Executors.newFixedThreadPool(10)
            val latch = CountDownLatch(254)
            for (host in 1..254) {
                val targetIp = "$prefix$host"
                if (targetIp == phoneIp) { latch.countDown(); continue }
                executor.execute {
                    try {
                        val url = URL("http://$targetIp:9120/api/ip")
                        val conn = url.openConnection() as HttpURLConnection
                        conn.connectTimeout = 200
                        conn.readTimeout = 200
                        val resp = conn.inputStream.bufferedReader().readText()
                        conn.disconnect()
                        val json = org.json.JSONObject(resp)
                        results.add(DiscoveredServer(
                            ip = try { json.getJSONArray("ips").getString(0) } catch (e: Exception) { json.optString("ip", targetIp) },
                            port = 9120,
                            name = json.optString("name", "")
                        ))
                    } catch (e: Exception) {}
                    finally { latch.countDown() }
                }
            }
            latch.await(5, TimeUnit.SECONDS)
            executor.shutdownNow()
        } catch (e: Exception) {}
        return results.distinctBy { it.ip }
    }

    private fun showNoServerFound() {
        runOnUiThread {
            val input = EditText(this@MainActivity).apply {
                hint = getString(R.string.manual_connect_hint)
            }
            AlertDialog.Builder(this@MainActivity, R.style.Theme_Luna_Dialog)
                .setTitle(getString(R.string.wifi_not_found_title))
                .setMessage(getString(R.string.wifi_not_found_msg))
                .setView(input)
                .setPositiveButton(getString(R.string.manual_connect_btn)) { _, _ ->
                    val text = input.text.toString().trim()
                    if (text.isNotEmpty()) parseAndConnect(text)
                }
                .setNeutralButton(getString(R.string.scan_qr)) { _, _ -> openQRScanner() }
                .setNegativeButton(getString(R.string.connect_cancel), null)
                .show()
        }
    }

    private fun showServerList(servers: List<DiscoveredServer>) {
        runOnUiThread {
            val items = servers.map { "${it.name} (${it.ip})" }.toTypedArray()
            AlertDialog.Builder(this@MainActivity, R.style.Theme_Luna_Dialog)
                .setTitle(getString(R.string.wifi_servers_found_title))
                .setItems(items) { _, which ->
                    val server = servers[which]
                    if (server.needsPairing) {
                        showPairingCodeDialog(server)
                    } else {
                        serverIp = server.ip
                        serverPort = server.port
                        saveIp("${server.ip}:${server.port}")
                        connectToServer()
                    }
                }
                .setNeutralButton(getString(R.string.manual_connect_title)) { _, _ ->
                    showManualEntry()
                }
                .setNegativeButton(getString(R.string.connect_cancel), null)
                .show()
        }
    }

    private fun showPairingCodeDialog(server: DiscoveredServer) {
        runOnUiThread {
            val codeInput = EditText(this@MainActivity).apply {
                hint = getString(R.string.pairing_code_hint)
                inputType = android.text.InputType.TYPE_CLASS_NUMBER
            }
            val container = LinearLayout(this@MainActivity).apply {
                orientation = LinearLayout.VERTICAL
                setPadding(48, 24, 48, 24)
                addView(TextView(this@MainActivity).apply {
                    text = getString(R.string.pairing_code_msg, server.name)
                    textSize = 14f
                    setTextColor(0xFFAAAAAA.toInt())
                    setPadding(0, 0, 0, 16)
                })
                addView(codeInput)
            }
            AlertDialog.Builder(this@MainActivity, R.style.Theme_Luna_Dialog)
                .setTitle(getString(R.string.pairing_code_title))
                .setView(container)
                .setPositiveButton(getString(R.string.pairing_btn)) { _, _ ->
                    val code = codeInput.text.toString().trim()
                    if (code.isNotEmpty()) pairWithServer(server, code)
                }
                .setNegativeButton(getString(R.string.connect_cancel), null)
                .show()
        }
    }

    private fun pairWithServer(server: DiscoveredServer, code: String) {
        thread {
            try {
                val url = URL("http://${server.ip}:${server.port}/api/pair")
                val conn = url.openConnection() as java.net.HttpURLConnection
                conn.requestMethod = "POST"
                conn.doOutput = true
                conn.setRequestProperty("Content-Type", "application/json")
                conn.connectTimeout = 5000
                conn.readTimeout = 5000
                val body = org.json.JSONObject().apply {
                    put("code", code)
                    put("device_name", android.os.Build.MODEL)
                }
                conn.outputStream.write(body.toString().toByteArray(Charsets.UTF_8))
                val response = conn.inputStream.bufferedReader().readText()
                val json = org.json.JSONObject(response)
                if (json.optBoolean("paired", false)) {
                    val token = json.optString("token", "")
                    val deviceName = json.optString("device_name", server.name)
                    val pcUuid = json.optString("uuid", "")
                    getSharedPreferences("luna_prefs", MODE_PRIVATE).edit().apply {
                        putString("server_ip", "${server.ip}:${server.port}")
                        putString("pairing_token", token)
                        putString("paired_pc_name", deviceName)
                        putString("pc_uuid", pcUuid)
                        apply()
                    }
                    runOnUiThread {
                        serverIp = server.ip
                        serverPort = server.port
                        connectToServer()
                    }
                } else {
                    runOnUiThread {
                        showToast(json.optString("error", "Error al emparejar"))
                    }
                }
                conn.disconnect()
            } catch (e: Exception) {
                runOnUiThread {
                    showToast("Error: ${e.localizedMessage ?: e.javaClass.simpleName}")
                }
            }
        }
    }

    private fun showManualEntry() {
        runOnUiThread {
            val input = EditText(this@MainActivity).apply { hint = getString(R.string.manual_connect_hint) }
            val container = LinearLayout(this@MainActivity).apply {
                orientation = LinearLayout.VERTICAL; setPadding(48, 24, 48, 24); addView(input)
            }
            AlertDialog.Builder(this@MainActivity, R.style.Theme_Luna_Dialog)
                .setTitle(getString(R.string.manual_connect_title))
                .setMessage(getString(R.string.manual_connect_msg))
                .setView(container)
                .setPositiveButton(getString(R.string.manual_connect_btn)) { _, _ ->
                    val text = input.text.toString().trim()
                    if (text.isNotEmpty()) parseAndConnect(text)
                }
                .setNeutralButton(getString(R.string.scan_qr)) { _, _ -> openQRScanner() }
                .setNegativeButton(getString(R.string.connect_cancel), null).show()
        }
    }

    private inner class WebAppInterface {
        @JavascriptInterface

        fun scanQR() { runOnUiThread { openQRScanner() } }


        @JavascriptInterface

        fun searchWiFi() { runOnUiThread { startWifiDiscovery() } }
        @JavascriptInterface

        fun checkUpdate() { runOnUiThread { checkForUpdate() } }



        @JavascriptInterface

        fun shareDownloadLink() {

            runOnUiThread {

                val intent = Intent(Intent.ACTION_SEND).apply {

                    type = "text/plain"

                    putExtra(Intent.EXTRA_TEXT, getString(R.string.share_text))

                }

                startActivity(Intent.createChooser(intent, getString(R.string.share_title)))

            }

        }



        @JavascriptInterface

        fun clearConnection() {

            runOnUiThread {

                disconnect()

                webView.visibility = View.VISIBLE

                nativeUi.visibility = View.GONE

                webView.loadUrl(onboardingUrl())

            }

        }



        @JavascriptInterface

        fun hasSavedConnection(): Boolean {

            val ip = getSharedPreferences("luna_prefs", MODE_PRIVATE).getString("server_ip", "")

            return !ip.isNullOrEmpty()

        }



        @JavascriptInterface

        fun retryConnection() {

            val savedIp = getSharedPreferences("luna_prefs", MODE_PRIVATE).getString("server_ip", "")

            if (!savedIp.isNullOrEmpty()) {

                val parts = savedIp.split(":")

                serverIp = parts[0].trim()

                serverPort = if (parts.size > 1) parts[1].trim().toIntOrNull() ?: 9120 else 9120

                runOnUiThread {             val savedUuid = getSharedPreferences("luna_prefs", MODE_PRIVATE).getString("pc_uuid", "") ?: ""

            if (savedUuid.isNotEmpty()) {
                thread {
                    try {
                        val sock = Socket()
                        sock.connect(InetSocketAddress(serverIp, serverPort), 200)
                        sock.close()
                        val url = URL("http://$serverIp:$serverPort/api/uuid")
                        val conn = url.openConnection() as java.net.HttpURLConnection
                        conn.connectTimeout = 500
                        conn.readTimeout = 500
                        val resp = conn.inputStream.bufferedReader().readText()
                        conn.disconnect()
                        val json = org.json.JSONObject(resp)
                        if (json.optString("uuid", "") == savedUuid) {
                            runOnUiThread { connectToServer() }
                            return@thread
                        }
                    } catch (e: Exception) {}
                    getSharedPreferences("luna_prefs", MODE_PRIVATE).edit()
                        .remove("server_ip").remove("pc_uuid").remove("pairing_token").apply()
                    runOnUiThread {
                        webView.visibility = View.VISIBLE
                        nativeUi.visibility = View.GONE
                        webView.loadUrl(onboardingUrl())
                    }
                }
            } else {
                connectToServer()
            }

        }

            }

        }



        @JavascriptInterface
        fun showManualEntry() {
            runOnUiThread {
                val input = EditText(this@MainActivity).apply { hint = getString(R.string.manual_connect_hint) }
                val container = LinearLayout(this@MainActivity).apply {
                    orientation = LinearLayout.VERTICAL; setPadding(48, 24, 48, 24); addView(input)
                }
                AlertDialog.Builder(this@MainActivity, R.style.Theme_Luna_Dialog)
                    .setTitle(getString(R.string.manual_connect_title))
                    .setMessage(getString(R.string.manual_connect_msg))
                    .setView(container)
                    .setPositiveButton(getString(R.string.manual_connect_btn)) { _, _ ->
                        val text = input.text.toString().trim()
                        if (text.isNotEmpty()) parseAndConnect(text)
                    }
                    .setNeutralButton(getString(R.string.scan_qr)) { _, _ -> openQRScanner() }
                    .setNegativeButton(getString(R.string.connect_cancel), null).show()
            }
        }

        @JavascriptInterface
        fun connectUSB() {
            runOnUiThread {
                AlertDialog.Builder(this@MainActivity, R.style.Theme_Luna_Dialog)
                    .setTitle("Conexi\u00f3n USB Tethering")
                    .setMessage("Activa \u00abAnclaje USB\u00bb en tu m\u00f3vil:\nAjustes > Redes > Zona WiFi/Anclaje > Anclaje USB\n\nDespu\u00e9s pulsa Buscar para encontrar tu PC.")
                    .setPositiveButton("Buscar") { _, _ -> startWifiDiscovery() }
                    .setNegativeButton("Cancelar", null)
                    .show()
            }
        }


        @JavascriptInterface

        fun finishApp() { runOnUiThread { finish() } }

    }



    private fun Int.dpToPx(): Int =

        (this * resources.displayMetrics.density).toInt()

}


