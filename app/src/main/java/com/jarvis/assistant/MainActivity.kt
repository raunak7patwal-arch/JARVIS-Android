package com.jarvis.assistant

import android.Manifest
import android.content.pm.PackageManager
import android.graphics.Typeface
import android.os.Bundle
import android.view.Gravity
import android.view.ViewGroup
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import com.jarvis.assistant.config.ServerConfig
import com.jarvis.assistant.device.DeviceCommandExecutor
import com.jarvis.assistant.network.JarvisApi
import com.jarvis.assistant.network.JarvisResponse

class MainActivity : AppCompatActivity() {

    private lateinit var statusText: TextView
    private lateinit var conversationText: TextView
    private lateinit var input: EditText
    private lateinit var sendButton: Button

    override fun onCreate(
        savedInstanceState: Bundle?
    ) {
        super.onCreate(savedInstanceState)

        JarvisApi.initialize(this)

        buildInterface()
        checkPermissions()
        checkCentralBrain()
    }

    private fun buildInterface() {

        val root =
            LinearLayout(this).apply {
                orientation =
                    LinearLayout.VERTICAL

                setPadding(
                    32,
                    40,
                    32,
                    32
                )
            }

        val title =
            TextView(this).apply {
                text = "JARVIS"
                textSize = 34f
                typeface =
                    Typeface.DEFAULT_BOLD
                gravity =
                    Gravity.CENTER
            }

        statusText =
            TextView(this).apply {
                text =
                    "Central Brain: checking..."
                textSize = 16f
                gravity =
                    Gravity.CENTER
                setPadding(
                    0,
                    12,
                    0,
                    20
                )
            }

        val settingsButton =
            Button(this).apply {
                text = "⚙ Server Settings"
                textSize = 15f

                setOnClickListener {
                    showServerSettings()
                }
            }

        val scroll =
            ScrollView(this).apply {

                conversationText =
                    TextView(
                        this@MainActivity
                    ).apply {
                        text =
                            "JARVIS ready, सर।\n\n"

                        textSize = 18f

                        setPadding(
                            8,
                            8,
                            8,
                            8
                        )
                    }

                addView(
                    conversationText,
                    ViewGroup.LayoutParams(
                        ViewGroup.LayoutParams.MATCH_PARENT,
                        ViewGroup.LayoutParams.WRAP_CONTENT
                    )
                )
            }

        input =
            EditText(this).apply {
                hint =
                    "JARVIS से कुछ पूछें..."
                textSize = 17f
                setSingleLine(true)
            }

        sendButton =
            Button(this).apply {

                text = "SEND"
                textSize = 16f

                setOnClickListener {
                    sendQuestion()
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
            statusText,
            LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT
            )
        )

        root.addView(
            settingsButton,
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
            input,
            LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT
            )
        )

        root.addView(
            sendButton,
            LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT
            )
        )

        setContentView(root)
    }

    private fun showServerSettings() {

        val container =
            LinearLayout(this).apply {
                orientation =
                    LinearLayout.VERTICAL

                setPadding(
                    40,
                    10,
                    40,
                    0
                )
            }

        val input =
            EditText(this).apply {
                hint =
                    "http://192.168.1.100:8787"
                setText(
                    ServerConfig.getServerAddress(
                        this@MainActivity
                    )
                )
                setSingleLine(true)
                textSize = 16f
            }

        container.addView(
            input,
            LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT
            )
        )

        val dialog =
            AlertDialog.Builder(this)
                .setTitle("JARVIS Server")
                .setMessage(
                    "Central Brain का server address डालें:"
                )
                .setView(container)
                .setNegativeButton(
                    "Cancel",
                    null
                )
                .setNeutralButton(
                    "Reset",
                    null
                )
                .setPositiveButton(
                    "Save & Test",
                    null
                )
                .create()

        dialog.setOnShowListener {

            dialog.getButton(
                AlertDialog.BUTTON_NEUTRAL
            ).setOnClickListener {

                ServerConfig.resetServerAddress(
                    this
                )

                JarvisApi.initialize(this)

                Toast.makeText(
                    this,
                    "Server address reset हो गया, सर।",
                    Toast.LENGTH_SHORT
                ).show()

                checkCentralBrain()

                dialog.dismiss()
            }

            dialog.getButton(
                AlertDialog.BUTTON_POSITIVE
            ).setOnClickListener {

                val address =
                    input.text
                        .toString()
                        .trim()

                if (
                    !ServerConfig.setServerAddress(
                        this,
                        address
                    )
                ) {

                    Toast.makeText(
                        this,
                        "Valid HTTP/HTTPS server address डालें, सर।",
                        Toast.LENGTH_LONG
                    ).show()

                    return@setOnClickListener
                }

                JarvisApi.initialize(this)

                statusText.text =
                    "Central Brain: testing..."

                JarvisApi.health { online ->

                    runOnUiThread {

                        statusText.text =
                            if (online) {
                                "Central Brain: ONLINE"
                            } else {
                                "Central Brain: OFFLINE"
                            }

                        Toast.makeText(
                            this,
                            if (online) {
                                "Server connected, सर।"
                            } else {
                                "Server connect नहीं हुआ, सर।"
                            },
                            Toast.LENGTH_SHORT
                        ).show()
                    }
                }

                dialog.dismiss()
            }
        }

        dialog.show()
    }

    private fun sendQuestion() {

        val question =
            input.text
                .toString()
                .trim()

        if (question.isEmpty()) {
            return
        }

        addMessage(
            "आप: $question"
        )

        input.setText("")

        sendButton.isEnabled = false

        statusText.text =
            "Central Brain: processing..."

        val language =
            detectLanguage(question)

        JarvisApi.askDetailed(
            question,
            language
        ) { response ->

            handleResponse(
                response
            )
        }
    }

    private fun handleResponse(
        response: JarvisResponse
    ) {

        if (!response.ok) {

            addMessage(
                "JARVIS: ${
                    response.error
                        ?: "Unknown error"
                }"
            )

            statusText.text =
                "Central Brain: ERROR"

            sendButton.isEnabled = true

            return
        }

        val answer =
            response.answer.trim()

        if (answer.isNotEmpty()) {

            addMessage(
                "JARVIS: $answer"
            )
        }

        val command =
            response.command

        if (
            command != null &&
            command.isCommand &&
            !command.action.isNullOrBlank()
        ) {

            executeDeviceCommand(
                command.action,
                command.parameters
            )
        }

        val sourceInfo =
            if (response.cached) {

                "Cached response"

            } else if (
                response.evidenceCount > 0
            ) {

                "Knowledge sources: ${
                    response.evidenceCount
                }"

            } else {

                "Central response"
            }

        statusText.text =
            "Central Brain: ONLINE • $sourceInfo"

        sendButton.isEnabled = true
    }

    private fun executeDeviceCommand(
        action: String,
        parameters: Map<String, String>
    ) {

        val result =
            DeviceCommandExecutor.execute(
                this,
                action,
                parameters
            )

        addMessage(
            if (result.success) {
                "JARVIS: ${result.message}"
            } else {
                "JARVIS सुरक्षा: ${result.message}"
            }
        )
    }

    private fun addMessage(
        message: String
    ) {

        conversationText.append(
            "\n$message\n"
        )

        conversationText.post {

            val parent =
                conversationText.parent

            if (parent is ScrollView) {

                parent.fullScroll(
                    ScrollView.FOCUS_DOWN
                )
            }
        }
    }

    private fun detectLanguage(
        text: String
    ): String {

        return if (
            text.any {
                it.code in 0x0900..0x097F
            }
        ) {
            "hi"
        } else {
            "en"
        }
    }

    private fun checkCentralBrain() {

        JarvisApi.health { online ->

            statusText.text =
                if (online) {
                    "Central Brain: ONLINE"
                } else {
                    "Central Brain: OFFLINE"
                }
        }
    }

    private fun checkPermissions() {

        val permissions =
            mutableListOf<String>()

        if (
            ContextCompat.checkSelfPermission(
                this,
                Manifest.permission.RECORD_AUDIO
            ) != PackageManager.PERMISSION_GRANTED
        ) {

            permissions.add(
                Manifest.permission.RECORD_AUDIO
            )
        }

        if (
            android.os.Build.VERSION.SDK_INT >= 33 &&
            ContextCompat.checkSelfPermission(
                this,
                Manifest.permission.POST_NOTIFICATIONS
            ) != PackageManager.PERMISSION_GRANTED
        ) {

            permissions.add(
                Manifest.permission.POST_NOTIFICATIONS
            )
        }

        if (permissions.isNotEmpty()) {

            ActivityCompat.requestPermissions(
                this,
                permissions.toTypedArray(),
                100
            )
        }
    }
}
