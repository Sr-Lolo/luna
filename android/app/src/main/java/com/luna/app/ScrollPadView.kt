package com.luna.app

import android.content.Context
import android.graphics.Canvas
import android.graphics.Paint
import android.graphics.Path
import android.util.AttributeSet
import android.view.MotionEvent
import android.view.View

class ScrollPadView @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null, defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    private val bgPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = 0xFF1A1A1A.toInt()
        style = Paint.Style.FILL
    }
    private val thumbPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = 0xFF4FC3F7.toInt()
        style = Paint.Style.FILL
    }
    private val trackPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = 0xFF333333.toInt()
        strokeWidth = 2f
        style = Paint.Style.STROKE
    }
    private val arrowPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = 0xFF555555.toInt()
        style = Paint.Style.STROKE
        strokeWidth = 2f
    }

    private var thumbPos = 0.5f
    private var isHorizontal = false
    private var onValueChange: ((Int) -> Unit)? = null

    private var isTracking = false

    init {
        val tag = attrs?.let {
            val a = context.obtainStyledAttributes(it, intArrayOf(android.R.attr.tag))
            val t = a.getString(0)
            a.recycle()
            t
        }
        isHorizontal = tag == "horizontal"
    }

    fun setOnValueChangeListener(l: (Int) -> Unit) { onValueChange = l }

    fun setColors(bg: Int, thumb: Int, track: Int, arrow: Int) {
        bgPaint.color = bg
        thumbPaint.color = thumb
        trackPaint.color = track
        arrowPaint.color = arrow
        invalidate()
    }

    override fun onTouchEvent(event: MotionEvent): Boolean {
        when (event.action) {
            MotionEvent.ACTION_DOWN -> {
                isTracking = true
                performHapticFeedback(android.view.HapticFeedbackConstants.VIRTUAL_KEY)
                updateThumb(event)
                return true
            }
            MotionEvent.ACTION_MOVE -> {
                updateThumb(event)
                return true
            }
            MotionEvent.ACTION_UP, MotionEvent.ACTION_CANCEL -> {
                isTracking = false
                thumbPos = 0.5f
                invalidate()
                onValueChange?.invoke(128)
                return true
            }
        }
        return false
    }

    private fun updateThumb(event: MotionEvent) {
        val halfRange = 80f.coerceAtMost((if (isHorizontal) width else height) / 2f)
        val center = if (isHorizontal) width / 2f else height / 2f
        val pos = if (isHorizontal) event.x else event.y
        val offset = ((pos - center) / halfRange).coerceIn(-1f, 1f)
        thumbPos = 0.5f + offset * 0.5f
        val value = (128 + (offset * 127).toInt()).coerceIn(0, 255)
        invalidate()
        onValueChange?.invoke(value)
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        val cx = width / 2f
        val cy = height / 2f
        val r = minOf(width, height) / 2f - 4f

        canvas.drawRoundRect(4f, 4f, width - 4f, height - 4f, 12f, 12f, bgPaint)
        canvas.drawRoundRect(4f, 4f, width - 4f, height - 4f, 12f, 12f, trackPaint)

        val thumbRadius = 10f
        val thumbX = if (isHorizontal) thumbPos * width else cx
        val thumbY = if (isHorizontal) cy else thumbPos * height
        canvas.drawCircle(thumbX, thumbY, thumbRadius, thumbPaint)

        val arrowSize = 8f
        val arrowY1 = cy - arrowSize
        val arrowY2 = cy + arrowSize
        if (isHorizontal) {
            val ax1 = cx - arrowSize
            val ax2 = cx + arrowSize
            val pathL = Path().apply {
                moveTo(ax1, cy); lineTo(cx - 3f, arrowY1); lineTo(cx - 3f, arrowY2); close()
            }
            val pathR = Path().apply {
                moveTo(ax2, cy); lineTo(cx + 3f, arrowY1); lineTo(cx + 3f, arrowY2); close()
            }
            canvas.drawPath(pathL, arrowPaint)
            canvas.drawPath(pathR, arrowPaint)
        } else {
            val ax1 = cx - arrowSize
            val ax2 = cx + arrowSize
            val pathUp = Path().apply {
                moveTo(cx, arrowY1); lineTo(ax1, cy - 3f); lineTo(ax2, cy - 3f); close()
            }
            val pathDown = Path().apply {
                moveTo(cx, arrowY2); lineTo(ax1, cy + 3f); lineTo(ax2, cy + 3f); close()
            }
            canvas.drawPath(pathUp, arrowPaint)
            canvas.drawPath(pathDown, arrowPaint)
        }
    }
}
