param(
    [string]$FilePath = "C:\Users\Infinity Tech\Desktop\Mis Cosas\Proyecto Luna\LunaDeck v1.7.55\android\app\src\main\java\com\luna\app\MainActivity.kt"
)

$c = [System.IO.File]::ReadAllText($FilePath, [System.Text.Encoding]::UTF8)
$cr2lf = [string]::new(@(0x0D, 0x0D, 0x0A), 0, 3)

# Define regex patterns for buildGrid and createGridCell
$buildGridPattern = '(?s)private fun buildGrid\(\)\s*\{.*?\}'
$createGridCellPattern = '(?s)private fun createGridCell\(k: LunaKey\):\s*View\s*\{.*?\}'
$restoreGridBtnBgPattern = '(?s)private fun restoreGridBtnBg\(btn: Button\)\s*\{.*?\}'

# New code blocks
$newBuildGrid = @'
    private fun buildGrid() {
        gridLayout.removeAllViews()
        val profile = profiles[currentProfileName] ?: return
        val cols = getGridCols(profile.cols)
        val keys = profile.keys
        gridLayout.columnCount = cols
        val gap = 3.dpToPx()
        val availWidth = resources.displayMetrics.widthPixels
        val btnSize = (availWidth - gap * (cols + 1)) / cols
        for ((index, k) in keys.withIndex()) {
            val row = index / cols
            val col = index % cols
            val cell = createGridCell(k, btnSize)
            cell.layoutParams = GridLayout.LayoutParams().apply {
                width = btnSize
                height = btnSize
                columnSpec = GridLayout.spec(col)
                rowSpec = GridLayout.spec(row)
                setMargins(gap, gap, gap, gap)
            }
            gridLayout.addView(cell)
        }
    }
'@ -replace "`r`n", $cr2lf

$newCreateGridCell = @'
    private fun createGridCell(k: LunaKey, btnSize: Int): View {
        val container = FrameLayout(this)
        val gd = GradientDrawable().apply {
            setColor(Color.parseColor(currentTheme.gridBtnBg))
            cornerRadius = 8.dpToPx().toFloat()
            setStroke(1.dpToPx(), Color.parseColor(currentTheme.gridBtnBorder))
        }
        container.background = gd

        if (k.icon.isNotEmpty()) {
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

            val url = resolveIconUrl(k.icon)
            Coil.imageLoader(this@MainActivity).enqueue(
                ImageRequest.Builder(this@MainActivity)
                    .data(url)
                    .crossfade(true)
                    .target { drawable ->
                        imageView.setImageDrawable(drawable)
                    }
                    .build()
            )
        }

        if (k.label.isNotEmpty()) {
            val textView = TextView(this).apply {
                text = k.label
                textSize = 10f
                setTypeface(null, android.graphics.Typeface.BOLD)
                setTextColor(Color.parseColor(currentTheme.gridBtnText))
                gravity = Gravity.CENTER
                
                if (k.icon.isNotEmpty()) {
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
'@ -replace "`r`n", $cr2lf

# Run Regex replacements
if ($c -match $buildGridPattern) {
    $c = [regex]::Replace($c, $buildGridPattern, $newBuildGrid)
    Write-Host "buildGrid replaced"
} else {
    Write-Host "buildGrid pattern not matched"
}

if ($c -match $createGridCellPattern) {
    $c = [regex]::Replace($c, $createGridCellPattern, $newCreateGridCell)
    Write-Host "createGridCell replaced"
} else {
    Write-Host "createGridCell pattern not matched"
}

if ($c -match $restoreGridBtnBgPattern) {
    $c = [regex]::Replace($c, $restoreGridBtnBgPattern, "") # Removed because we merged it into newCreateGridCell
    Write-Host "restoreGridBtnBg removed"
} else {
    Write-Host "restoreGridBtnBg pattern not matched"
}

# Apply theme layout update
$oldThemeBlockPattern = '(?s)// apply native grid colors.*?for\s*\(i in 0 until gridLayout\.childCount\)\s*\{.*?\}'
$newThemeBlock = @'
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
'@ -replace "`r`n", $cr2lf

if ($c -match $oldThemeBlockPattern) {
    $c = [regex]::Replace($c, $oldThemeBlockPattern, $newThemeBlock)
    Write-Host "theme block replaced"
} else {
    Write-Host "theme block pattern not matched"
}

# Fix templates
$c = $c.Replace('$serverIp', '${serverIp}')
$c = $c.Replace('$serverPort', '${serverPort}')

[System.IO.File]::WriteAllText($FilePath, $c, [System.Text.Encoding]::UTF8)
Write-Host "Done"
