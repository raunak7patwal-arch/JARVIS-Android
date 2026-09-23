package com.jarvis.assistant.network

import android.content.Context
import com.jarvis.assistant.context.DeviceContext
import com.jarvis.assistant.config.ServerConfig
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import java.util.concurrent.Executors

object ContextApi {

    private val executor = Executors.newSingleThreadExecutor()

    fun update(
        context: Context,
        deviceId: String,
        deviceContext: DeviceContext,
        callback: (Boolean) -> Unit
    ) {
        executor.execute {
            var connection: HttpURLConnection? = null

            try {
                val server = ServerConfig.getServerAddress(context)

                val url = URL("$server/context/update")
                connection = url.openConnection() as HttpURLConnection

                connection.requestMethod = "POST"
                connection.connectTimeout = 5000
                connection.readTimeout = 5000
                connection.doOutput = true
                connection.setRequestProperty(
                    "Content-Type",
                    "application/json"
                )

                val json = JSONObject()
                    .put("device_id", deviceId)
                    .put(
                        "context",
                        JSONObject()
                            .put("screen", deviceContext.screen)
                            .put("app", deviceContext.app)
                            .put("activity", deviceContext.activity)
                            .put("battery", deviceContext.battery)
                            .put("network", deviceContext.network)
                            .put("orientation", deviceContext.orientation)
                            .put("locale", deviceContext.locale)
                            .put("timestamp", deviceContext.timestamp)
                    )

                connection.outputStream.use {
                    it.write(json.toString().toByteArray(Charsets.UTF_8))
                }

                callback(connection.responseCode in 200..299)

            } catch (_: Exception) {
                callback(false)
            } finally {
                connection?.disconnect()
            }
        }
    }
}
