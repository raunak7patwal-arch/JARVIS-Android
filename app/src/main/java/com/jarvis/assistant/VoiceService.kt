package com.jarvis.assistant

import android.Manifest
import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Bundle
import android.os.IBinder
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import android.speech.tts.TextToSpeech
import androidx.core.content.ContextCompat
import java.util.Locale

class VoiceService : Service(), TextToSpeech.OnInitListener {

    private var speech: SpeechRecognizer? = null
    private var tts: TextToSpeech? = null

    private var listening = false
    private var awake = false

    override fun onCreate() {
        super.onCreate()

        createNotificationChannel()

        // Android 14+ microphone foreground service:
        // foreground mode FIRST, microphone listening AFTER.
        try {
            startForeground(1001, notification())
        } catch (_: Exception) {
            stopSelf()
            return
        }

        if (
            ContextCompat.checkSelfPermission(
                this,
                Manifest.permission.RECORD_AUDIO
            ) != PackageManager.PERMISSION_GRANTED
        ) {
            stopSelf()
            return
        }

        tts = TextToSpeech(this, this)

        if (!SpeechRecognizer.isRecognitionAvailable(this)) {
            speak("सर, इस फोन पर speech recognition उपलब्ध नहीं है।")
            return
        }

        speech = SpeechRecognizer.createSpeechRecognizer(this)

        speech?.setRecognitionListener(
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
                        restartListening()
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

                    listening = false

                    if (text.isNotEmpty()) {
                        processSpeech(text)
                    } else if (!awake) {
                        restartListening()
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

        // Give foreground service time to initialize.
        android.os.Handler(mainLooper).postDelayed(
            { startListening() },
            500
        )
    }

    private fun processSpeech(text: String) {

        val lower = text.lowercase(Locale.getDefault())

        if (
            lower.contains("jarvis") ||
            text.contains("जार्विस")
        ) {
            awake = true

            speak("जी सर। मैं सुन रहा हूँ।")

            android.os.Handler(mainLooper).postDelayed(
                { startListening() },
                800
            )

            return
        }

        if (awake) {
            awake = false

            // Central Brain integration can be connected here.
            speak("आदेश प्राप्त हुआ, सर।")

            android.os.Handler(mainLooper).postDelayed(
                { startListening() },
                1200
            )
        }
    }

    private fun restartListening() {
        android.os.Handler(mainLooper).postDelayed(
            { startListening() },
            1000
        )
    }

    private fun startListening() {

        if (listening || speech == null) {
            return
        }

        if (
            ContextCompat.checkSelfPermission(
                this,
                Manifest.permission.RECORD_AUDIO
            ) != PackageManager.PERMISSION_GRANTED
        ) {
            stopSelf()
            return
        }

        val intent =
            Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
                putExtra(
                    RecognizerIntent.EXTRA_LANGUAGE_MODEL,
                    RecognizerIntent.LANGUAGE_MODEL_FREE_FORM
                )
                putExtra(
                    RecognizerIntent.EXTRA_PARTIAL_RESULTS,
                    true
                )
                putExtra(
                    RecognizerIntent.EXTRA_MAX_RESULTS,
                    3
                )
                putExtra(
                    RecognizerIntent.EXTRA_LANGUAGE,
                    "hi-IN"
                )
            }

        try {
            speech?.startListening(intent)
        } catch (_: Exception) {
            listening = false
            restartListening()
        }
    }

    private fun speak(text: String) {

        val engine = tts ?: return

        try {
            engine.stop()

            engine.speak(
                text,
                TextToSpeech.QUEUE_FLUSH,
                null,
                "JARVIS_RESPONSE"
            )
        } catch (_: Exception) {}
    }

    override fun onInit(status: Int) {

        if (status == TextToSpeech.SUCCESS) {
            try {
                tts?.language = Locale("hi", "IN")
                tts?.setSpeechRate(0.92f)
                tts?.setPitch(0.72f)
            } catch (_: Exception) {}
        }
    }

    private fun createNotificationChannel() {

        val channel =
            NotificationChannel(
                "jarvis_voice",
                "JARVIS Voice",
                NotificationManager.IMPORTANCE_LOW
            )

        getSystemService(
            NotificationManager::class.java
        ).createNotificationChannel(channel)
    }

    private fun notification(): Notification {

        return Notification.Builder(
            this,
            "jarvis_voice"
        )
            .setContentTitle("JARVIS")
            .setContentText("Voice system operational")
            .setSmallIcon(android.R.drawable.ic_btn_speak_now)
            .build()
    }

    override fun onStartCommand(
        intent: Intent?,
        flags: Int,
        startId: Int
    ): Int {
        return START_STICKY
    }

    override fun onDestroy() {

        try {
            speech?.destroy()
        } catch (_: Exception) {}

        try {
            tts?.stop()
            tts?.shutdown()
        } catch (_: Exception) {}

        speech = null
        tts = null

        super.onDestroy()
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
