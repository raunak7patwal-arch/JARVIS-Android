package com.jarvis.assistant.device

import android.Manifest
import android.app.NotificationChannel
import android.app.NotificationManager
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.os.BatteryManager
import androidx.core.app.ActivityCompat
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat

data class CommandExecutionResult(
    val success: Boolean,
    val message: String
)

object DeviceCommandExecutor {

    private const val CHANNEL_ID = "jarvis_commands"
    private const val CHANNEL_NAME = "JARVIS Commands"
    private const val NOTIFICATION_ID = 7001

    /*
     * IMPORTANT:
     * Only packages explicitly listed here can be opened.
     *
     * Never execute an arbitrary package name received from
     * the network or AI.
     */
    private val allowedApps = mapOf(
        "settings" to "com.android.settings",
        "chrome" to "com.android.chrome",
        "youtube" to "com.google.android.youtube",
        "maps" to "com.google.android.apps.maps"
    )

    fun execute(
        context: Context,
        action: String?,
        parameters: Map<String, String> = emptyMap()
    ): CommandExecutionResult {

        val normalizedAction =
            action
                ?.trim()
                ?.lowercase()
                ?: return CommandExecutionResult(
                    false,
                    "Command missing है, सर।"
                )

        return when (normalizedAction) {

            "ping" -> {
                CommandExecutionResult(
                    true,
                    "Connection verified, सर।"
                )
            }

            "open_url" -> {
                openUrl(
                    context,
                    parameters["url"]
                )
            }

            "open_app" -> {
                openApp(
                    context,
                    parameters["app"]
                )
            }

            "device_info" -> {
                getDeviceInfo(context)
            }

            "notification" -> {
                showNotification(
                    context,
                    parameters["title"],
                    parameters["message"]
                )
            }

            else -> {
                CommandExecutionResult(
                    false,
                    "यह command सुरक्षित allowlist में नहीं है, सर।"
                )
            }
        }
    }

    private fun openUrl(
        context: Context,
        urlText: String?
    ): CommandExecutionResult {

        val url = urlText?.trim()

        if (url.isNullOrEmpty()) {
            return CommandExecutionResult(
                false,
                "सर, URL नहीं मिला।"
            )
        }

        return try {

            val uri = Uri.parse(url)

            val scheme =
                uri.scheme?.lowercase()

            /*
             * Only web URLs are allowed.
             */
            if (
                scheme != "http" &&
                scheme != "https"
            ) {
                return CommandExecutionResult(
                    false,
                    "सिर्फ HTTP और HTTPS URLs allowed हैं, सर।"
                )
            }

            if (uri.host.isNullOrBlank()) {
                return CommandExecutionResult(
                    false,
                    "URL valid नहीं है, सर।"
                )
            }

            val intent =
                Intent(
                    Intent.ACTION_VIEW,
                    uri
                ).apply {
                    addCategory(
                        Intent.CATEGORY_BROWSABLE
                    )
                }

            val packageManager =
                context.packageManager

            if (
                intent.resolveActivity(
                    packageManager
                ) == null
            ) {
                return CommandExecutionResult(
                    false,
                    "इस URL को खोलने वाला app नहीं मिला, सर।"
                )
            }

            intent.addFlags(
                Intent.FLAG_ACTIVITY_NEW_TASK
            )

            context.startActivity(intent)

            CommandExecutionResult(
                true,
                "Website खोल दी गई, सर।"
            )

        } catch (_: Exception) {

            CommandExecutionResult(
                false,
                "URL खोलने में समस्या आई, सर।"
            )
        }
    }

    private fun openApp(
        context: Context,
        appName: String?
    ): CommandExecutionResult {

        val key =
            appName
                ?.trim()
                ?.lowercase()

        if (key.isNullOrEmpty()) {
            return CommandExecutionResult(
                false,
                "सर, कौन-सा app खोलना है यह नहीं मिला।"
            )
        }

        val packageName =
            allowedApps[key]

        if (packageName == null) {
            return CommandExecutionResult(
                false,
                "यह app अभी JARVIS की safe allowlist में नहीं है, सर।"
            )
        }

        return try {

            val packageManager =
                context.packageManager

            val launchIntent =
                packageManager.getLaunchIntentForPackage(
                    packageName
                )

            if (launchIntent == null) {
                return CommandExecutionResult(
                    false,
                    "$appName app इस device पर installed नहीं है, सर।"
                )
            }

            launchIntent.addFlags(
                Intent.FLAG_ACTIVITY_NEW_TASK
            )

            context.startActivity(
                launchIntent
            )

            CommandExecutionResult(
                true,
                "$appName खोल दिया गया, सर।"
            )

        } catch (_: Exception) {

            CommandExecutionResult(
                false,
                "$appName खोलने में समस्या आई, सर।"
            )
        }
    }

    private fun getDeviceInfo(
        context: Context
    ): CommandExecutionResult {

        return try {

            val batteryManager =
                context.getSystemService(
                    Context.BATTERY_SERVICE
                ) as BatteryManager

            val battery =
                batteryManager.getIntProperty(
                    BatteryManager.BATTERY_PROPERTY_CAPACITY
                )

            val manufacturer =
                Build.MANUFACTURER

            val model =
                Build.MODEL

            val androidVersion =
                Build.VERSION.RELEASE

            val sdk =
                Build.VERSION.SDK_INT

            val result =
                """
                Device: $manufacturer $model
                Android: $androidVersion
                SDK: $sdk
                Battery: ${battery.coerceIn(0, 100)}%
                """.trimIndent()

            CommandExecutionResult(
                true,
                result
            )

        } catch (_: Exception) {

            CommandExecutionResult(
                false,
                "Device information पढ़ने में समस्या आई, सर।"
            )
        }
    }

    private fun showNotification(
        context: Context,
        title: String?,
        message: String?
    ): CommandExecutionResult {

        val notificationTitle =
            title
                ?.trim()
                ?.takeIf { it.isNotEmpty() }
                ?: "JARVIS"

        val notificationMessage =
            message
                ?.trim()
                ?.takeIf { it.isNotEmpty() }
                ?: "सर, JARVIS notification ready है।"

        if (
            Build.VERSION.SDK_INT >=
            Build.VERSION_CODES.TIRAMISU
        ) {

            if (
                ActivityCompat.checkSelfPermission(
                    context,
                    Manifest.permission.POST_NOTIFICATIONS
                ) != PackageManager.PERMISSION_GRANTED
            ) {
                return CommandExecutionResult(
                    false,
                    "Notification permission अभी granted नहीं है, सर।"
                )
            }
        }

        createNotificationChannel(
            context
        )

        val notification =
            NotificationCompat.Builder(
                context,
                CHANNEL_ID
            )
                .setSmallIcon(
                    android.R.drawable.ic_dialog_info
                )
                .setContentTitle(
                    notificationTitle
                )
                .setContentText(
                    notificationMessage
                )
                .setPriority(
                    NotificationCompat.PRIORITY_DEFAULT
                )
                .setAutoCancel(true)
                .build()

        return try {

            NotificationManagerCompat
                .from(context)
                .notify(
                    NOTIFICATION_ID,
                    notification
                )

            CommandExecutionResult(
                true,
                "Notification दिखा दी गई, सर।"
            )

        } catch (_: SecurityException) {

            CommandExecutionResult(
                false,
                "Notification permission उपलब्ध नहीं है, सर।"
            )

        } catch (_: Exception) {

            CommandExecutionResult(
                false,
                "Notification दिखाने में समस्या आई, सर।"
            )
        }
    }

    private fun createNotificationChannel(
        context: Context
    ) {

        if (
            Build.VERSION.SDK_INT >=
            Build.VERSION_CODES.O
        ) {

            val manager =
                context.getSystemService(
                    Context.NOTIFICATION_SERVICE
                ) as NotificationManager

            val channel =
                NotificationChannel(
                    CHANNEL_ID,
                    CHANNEL_NAME,
                    NotificationManager.IMPORTANCE_DEFAULT
                ).apply {
                    description =
                        "JARVIS command notifications"
                }

            manager.createNotificationChannel(
                channel
            )
        }
    }
}
