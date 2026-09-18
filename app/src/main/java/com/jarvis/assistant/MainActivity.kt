package com.jarvis.assistant

import android.os.Bundle
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val status = TextView(this).apply {
            text = "JARVIS\n\nReady."
            textSize = 28f
            setPadding(40, 80, 40, 40)
        }

        setContentView(status)
    }
}
