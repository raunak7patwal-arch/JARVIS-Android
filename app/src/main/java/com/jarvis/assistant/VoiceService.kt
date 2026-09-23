package com.jarvis.assistant

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Intent
import android.os.Bundle
import android.os.IBinder
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import android.speech.tts.TextToSpeech
import java.util.Locale

class VoiceService : Service(), TextToSpeech.OnInitListener {

    private lateinit var speech: SpeechRecognizer
    private lateinit var tts: TextToSpeech

    private var listening = false
    private var awake = false

    override fun onCreate() {
        super.onCreate()

        createNotificationChannel()

        tts = TextToSpeech(this, this)

        speech = SpeechRecognizer.createSpeechRecognizer(this)

        speech.setRecognitionListener(
            object : RecognitionListener {

                override fun onReadyForSpeech(params: Bundle?) {
                    listening = true
                }

                override fun onBeginningOfSpeech() {}

                override fun onRmsChanged(rmsdB: Float) {}

                override fun onBufferReceived(buffer: ByteArray?) {}

                override fun onEndOfSpeech() {
                    listening = false
                }

                override fun onError(error: Int) {
                    listening = false

                    if (!awake) {
                        startListening()
                    }
                }

                override fun onResults(results: Bundle?) {

                    val matches =
                        results?.getStringArrayList(
                            SpeechRecognizer.RESULTS_RECOGNITION
                        )

                    val text =
                        matches?.firstOrNull()
                            ?.trim()
                            ?: ""

                    if (text.isNotEmpty()) {
                        processSpeech(text)
                    }

                    listening = false

                    if (!awake) {
                        startListening()
                    }
                }

                override fun onPartialResults(
                    partialResults: Bundle?
                ) {}

                override fun onEvent(
                    eventType: Int,
                    params: Bundle?
                ) {}
            }
        )

        startListening()
    }

    private fun processSpeech(text: String) {

        val lower = text.lowercase(Locale.getDefault())

        // Wake phrase
        if (
            lower.contains("jarvis") ||
            text.contains("जार्विस")
        ) {
            awake = true

            speak(
                "जी सर। मैं सुन रहा हूँ।"
            )

            // सुनने के लिए छोटा delay
            android.os.Handler(
                mainLooper
            ).postDelayed({

                startListening()

            }, 150)

            return
        }

        if (awake) {

            awake = false

            // अभी local demo response.
            // अगला step: Central Brain API.
            val response =
                "आदेश प्राप्त हुआ, सर।"

            speak(response)

            android.os.Handler(
                mainLooper
            ).postDelayed({

                startListening()

            }, 100)
        }
    }

    private fun startListening() {

        if (listening) {
            return
        }

        val intent =
            Intent(
                RecognizerIntent.ACTION_RECOGNIZE_SPEECH
            )

        intent.putExtra(
            RecognizerIntent.EXTRA_LANGUAGE_MODEL,
            RecognizerIntent.LANGUAGE_MODEL_FREE_FORM
        )

        intent.putExtra(
            RecognizerIntent.EXTRA_PARTIAL_RESULTS,
            true
        )

        intent.putExtra(
            RecognizerIntent.EXTRA_MAX_RESULTS,
            3
        )

        intent.putExtra(
            RecognizerIntent.EXTRA_LANGUAGE,
            "hi-IN"
        )

        try {
            speech.startListening(intent)
        } catch (_: Exception) {
            listening = false
        }
    }

    private fun speak(text: String) {

        if (::tts.isInitialized) {

            tts.stop()

            tts.speak(
                text,
                TextToSpeech.QUEUE_FLUSH,
                null,
                "JARVIS_RESPONSE"
            )
        }
    }

    override fun onInit(status: Int) {

        if (status == TextToSpeech.SUCCESS) {

            tts.language =
                Locale("hi", "IN")

            tts.setSpeechRate(0.92f)
            tts.setPitch(0.72f)
        }
    }

    private fun createNotificationChannel() {

        val channel =
            NotificationChannel(
                "jarvis_voice",
                "JARVIS Voice",
                NotificationManager.IMPORTANCE_LOW
            )

        val manager =
            getSystemService(
                NotificationManager::class.java
            )

        manager.createNotificationChannel(channel)
    }

    private fun notification(): Notification {

        return Notification.Builder(
            this,
            "jarvis_voice"
        )
            .setContentTitle("JARVIS")
            .setContentText(
                "Voice system operational"
            )
            .setSmallIcon(
                android.R.drawable.ic_btn_speak_now
            )
            .build()
    }

    override fun onStartCommand(
        intent: Intent?,
        flags: Int,
        startId: Int
    ): Int {

        startForeground(
            1001,
            notification()
        )

        return START_STICKY
    }

    override fun onDestroy() {

        try {
            speech.destroy()
        } catch (_: Exception) {}

        try {
            tts.stop()
            tts.shutdown()
        } catch (_: Exception) {}

        super.onDestroy()
    }

    override fun onBind(
        intent: Intent?
    ): IBinder? = null
}
