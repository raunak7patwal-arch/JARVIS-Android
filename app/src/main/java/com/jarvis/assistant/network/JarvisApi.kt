package com.jarvis.assistant.network

import android.content.Context
import android.os.Handler
import android.os.Looper
import com.jarvis.assistant.config.ServerConfig
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import java.util.concurrent.Executors

data class JarvisCommand(
    val isCommand: Boolean,
    val action: String?,
    val parameters: Map<String, String>,
    val text: String
)

data class JarvisResponse(
    val ok: Boolean,
    val answer: String,
    val cached: Boolean,
    val command: JarvisCommand?,
    val evidenceCount: Int,
    val error: String?
)

object JarvisApi {

    @Volatile
    var serverAddress: String =
        "http://127.0.0.1:8787"

    private val executor =
        Executors.newCachedThreadPool()

    private val mainHandler =
        Handler(Looper.getMainLooper())

    fun initialize(context: Context) {
        serverAddress =
            ServerConfig.getServerAddress(context)
    }

    fun askDetailed(
        question: String,
        language: String,
        callback: (JarvisResponse) -> Unit
    ) {
        executor.execute {
            try {
                val connection =
                    URL("$serverAddress/ask")
                        .openConnection() as HttpURLConnection

                connection.requestMethod = "POST"
                connection.connectTimeout = 10000
                connection.readTimeout = 30000
                connection.setRequestProperty(
                    "Content-Type",
                    "application/json"
                )
                connection.doOutput = true

                val body =
                    JSONObject()
                        .put("text", question)
                        .put("language", language)
                        .toString()

                connection.outputStream.use {
                    it.write(body.toByteArray(Charsets.UTF_8))
                }

                val code = connection.responseCode

                val stream =
                    if (code in 200..299) {
                        connection.inputStream
                    } else {
                        connection.errorStream
                    }

                val responseText =
                    stream?.bufferedReader()?.use {
                        it.readText()
                    } ?: ""

                connection.disconnect()

                val json =
                    JSONObject(responseText)

                val commandJson =
                    json.optJSONObject("command")

                val command =
                    if (commandJson != null) {

                        val parameters =
                            mutableMapOf<String, String>()

                        val params =
                            commandJson.optJSONObject(
                                "parameters"
                            )

                        if (params != null) {
                            val keys = params.keys()

                            while (keys.hasNext()) {
                                val key = keys.next()

                                parameters[key] =
                                    params.optString(
                                        key,
                                        ""
                                    )
                            }
                        }

                        JarvisCommand(
                            isCommand =
                                commandJson.optBoolean(
                                    "is_command",
                                    false
                                ),
                            action =
                                commandJson.optString(
                                    "action",
                                    null
                                ),
                            parameters = parameters,
                            text =
                                commandJson.optString(
                                    "text",
                                    question
                                )
                        )

                    } else {
                        null
                    }

                val result =
                    JarvisResponse(
                        ok =
                            json.optBoolean(
                                "ok",
                                false
                            ),
                        answer =
                            json.optString(
                                "answer",
                                ""
                            ),
                        cached =
                            json.optBoolean(
                                "cached",
                                false
                            ),
                        command = command,
                        evidenceCount =
                            json.optInt(
                                "evidence_count",
                                0
                            ),
                        error =
                            json.optString(
                                "error",
                                null
                            )
                    )

                mainHandler.post {
                    callback(result)
                }

            } catch (e: Exception) {

                mainHandler.post {
                    callback(
                        JarvisResponse(
                            ok = false,
                            answer = "",
                            cached = false,
                            command = null,
                            evidenceCount = 0,
                            error =
                                e.message
                                    ?: "Server connection failed"
                        )
                    )
                }
            }
        }
    }

    fun ask(
        question: String,
        language: String,
        callback: (String) -> Unit
    ) {
        askDetailed(
            question,
            language
        ) { response ->

            callback(
                if (response.ok) {
                    response.answer
                } else {
                    response.error
                        ?: "JARVIS server error"
                }
            )
        }
    }

    fun health(
        callback: (Boolean) -> Unit
    ) {
        executor.execute {
            try {
                val connection =
                    URL("$serverAddress/health")
                        .openConnection() as HttpURLConnection

                connection.requestMethod = "GET"
                connection.connectTimeout = 5000
                connection.readTimeout = 5000

                val code =
                    connection.responseCode

                connection.disconnect()

                mainHandler.post {
                    callback(code in 200..299)
                }

            } catch (e: Exception) {

                mainHandler.post {
                    callback(false)
                }
            }
        }
    }
}
