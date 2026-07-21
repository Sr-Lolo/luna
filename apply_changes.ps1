param(
    [string]$FilePath = "C:\Users\Infinity Tech\Desktop\Mis Cosas\Proyecto Luna\LunaDeck v1.7.55\android\app\src\main\java\com\luna\app\MainActivity.kt"
)

$c = [System.IO.File]::ReadAllText($FilePath, [System.Text.Encoding]::UTF8)
$cr2lf = [string]::new(@(0x0D, 0x0D, 0x0A), 0, 3)

# 1. Add imports after import android.view.WindowManager
$newImports = @'
import android.view.Gravity

import android.view.MotionEvent

import android.view.SoundEffectConstants
'@ -replace "`r`n", $cr2lf

$c = $c.Replace("import android.view.WindowManager$cr2lf$cr2lfimport android.webkit.JavascriptInterface", "import android.view.WindowManager$cr2lf$cr2lf$newImports$cr2lf$cr2lfimport android.webkit.JavascriptInterface")

# 2. Add grid methods before switchGridProfile
$gridMethods = @'
    private fun buildGrid() {
        gridLayout.removeAllViews()
        val profile = profiles[currentProfileName] ?: return
        gridLayout.columnCount = profile.cols
        for (k in profile.keys) {
            gridLayout.addView(createGridCell(k))
        }
    }

    private fun rebuildGrid() {
        runOnUiThread { buildGrid() }
    }

    private fun createGridCell(k: LunaKey): View {
        val btn = Button(this)
        btn.layoutParams = ViewGroup.MarginLayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT,
            ViewGroup.LayoutParams.WRAP_CONTENT
        ).apply { setMargins(3.dpToPx(), 3.dpToPx(), 3.dpToPx(), 3.dpToPx()) }
        btn.minHeight = 0
        btn.minimumHeight = 0
        btn.gravity = Gravity.CENTER
        btn.textSize = 11f
        btn.setTypeface(null, android.graphics.Typeface.BOLD)
        btn.setTextColor(Color.parseColor(currentTheme.gridBtnText))
        val gd = GradientDrawable()
        gd.setColor(Color.parseColor(currentTheme.gridBtnBg))
        gd.cornerRadius = 8f
        gd.setStroke(1, Color.parseColor(currentTheme.gridBtnBorder))
        btn.background = gd
        btn.text = k.label
        if (k.icon.isNotEmpty()) {
            val url = resolveIconUrl(k.icon)
            scope.launch {
                try {
                    val result = Coil.imageLoader(this@MainActivity).execute(
                        ImageRequest.Builder(this@MainActivity).data(url).crossfade(true).build()
                    )
                    if (result.drawable != null) {
                        btn.background = result.drawable
                        btn.text = ""
                    }
                } catch (_: Exception) {}
            }
        }
        btn.setOnTouchListener { v, ev ->
            when (ev.action) {
                MotionEvent.ACTION_DOWN -> {
                    gd.setColor(Color.parseColor(currentTheme.gridBtnActiveBg))
                    btn.background = gd
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
                    restoreGridBtnBg(btn)
                    v.isPressed = false
                }
                MotionEvent.ACTION_CANCEL -> {
                    restoreGridBtnBg(btn)
                    v.isPressed = false
                }
            }
            true
        }
        return btn
    }

    private fun restoreGridBtnBg(btn: Button) {
        if (btn.background !is GradientDrawable) return
        val gd2 = GradientDrawable()
        gd2.setColor(Color.parseColor(currentTheme.gridBtnBg))
        gd2.cornerRadius = 8f
        gd2.setStroke(1, Color.parseColor(currentTheme.gridBtnBorder))
        btn.background = gd2
    }

    private fun resolveIconUrl(icon: String): String {
        val base = "http://$serverIp:$serverPort"
        return if (icon.startsWith("custom/")) {
            "$base/custom-icons/" + icon.removePrefix("custom/")
        } else {
            "$base/icons/" + icon
        }
    }

'@ -replace "`r`n", $cr2lf

# Replace the server IP variables that PowerShell would eat
$gridMethods = $gridMethods.Replace('$serverIp', '${serverIp}')
$gridMethods = $gridMethods.Replace('$serverPort', '${serverPort}')

$c = $c.Replace("    private fun switchGridProfile(name: String) {", $gridMethods + "    private fun switchGridProfile(name: String) {")

# 3. Save
[System.IO.File]::WriteAllText($FilePath, $c, [System.Text.Encoding]::UTF8)
Write-Host "Changes applied successfully"
