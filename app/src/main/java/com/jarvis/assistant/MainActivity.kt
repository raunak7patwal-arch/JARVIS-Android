package com.jarvis.assistant

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.Color
import android.graphics.Typeface
import android.os.Bundle
import android.view.Gravity
import android.view.ViewGroup
import android.widget.Button
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat

class MainActivity : AppCompatActivity() {

    private lateinit var status: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        buildStableInterface()
    }

    private fun buildStableInterface() {

        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(32, 50, 32, 32)
            gravity = Gravity.CENTER_HORIZONTAL
        }

        val title = TextView(this).apply {
            text = "JARVIS"
            textSize = 38f
            typeface = Typeface.DEFAULT_BOLD
            gravity = Gravity.CENTER
        }

        val subtitle = TextView(this).apply {
            text = "Your Personal AI Assistant"
            textSize = 17f
            gravity = Gravity.CENTER
            setPadding(0, 8, 0, 30)
        }

        status = TextView(this).apply {
            text = "● JARVIS READY"
            textSize = 18f
            gravity = Gravity.CENTER
            setTextColor(Color.rgb(0, 160, 180))
            setPadding(0, 20, 0, 30)
        }

        val conversation = TextView(this).apply {
            text = "जी सर।\\n\\nJARVIS आपके आदेश के लिए तैयार है।"
            textSize = 19f
            setPadding(20, 20, 20, 20)
        }

        val scroll = ScrollView(this).apply {
            addView(
                conversation,
                ViewGroup.LayoutParams(
                    ViewGroup.LayoutParams.MATCH_PARENT,
                    ViewGroup.LayoutParams.WRAP_CONTENT
                )
            )
        }

        val voiceButton = Button(this).apply {
            text = "🎙 START JARVIS"
            textSize = 18f

            setOnClickListener {
                requestVoiceAndStart()
            }
        }

        val testButton = Button(this).apply {
            text = "TEST JARVIS"
            textSize = 16f

            setOnClickListener {
                status.text = "● JARVIS ONLINE"
                conversation.text =
                    "जी सर।\\n\\nJARVIS सही तरीके से चल रहा है।"
            }
        }

        root.addView(
            title,
            LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT
            )
        )

        root.addView(
            subtitle,
            LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT
            )
        )

        root.addView(
            status,
            LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT
            )
        )

        root.addView(
            scroll,
            LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                0,
                1f
            )
        )

        root.addView(
            voiceButton,
            LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT
            )
        )

        root.addView(
            testButton,
            LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT
            )
        )

        setContentView(root)
    }

    private fun requestVoiceAndStart() {

        if (
            ContextCompat.checkSelfPermission(
                this,
                Manifest.permission.RECORD_AUDIO
            ) != PackageManager.PERMISSION_GRANTED
        ) {
            ActivityCompat.requestPermissions(
                this,
                arrayOf(Manifest.permission.RECORD_AUDIO),
                7101
            )
            return
        }

        startJarvisVoice()
    }

    private fun startJarvisVoice() {

        try {
            val intent = Intent(this, VoiceService::class.java)

            ContextCompat.startForegroundService(
                this,
                intent
            )

            status.text = "● JARVIS VOICE ACTIVE"

        } catch (e: Exception) {
            status.text = "● VOICE START FAILED"
        }
    }
}
