package com.jarvis.assistant.context

import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import android.os.BatteryManager
import android.os.Build
import android.view.Surface
import android.view.WindowManager
import java.util.Locale

data class DeviceContext(
    val screen: String = "unknown",
    val app: String = "JARVIS",
    val activity: String = "MainActivity",
    val battery: Int = -1,
    val network: String = "unknown",
    val orientation: String = "unknown",
    val locale: String = Locale.getDefault().toLanguageTag(),
    val timestamp: Long = System.currentTimeMillis()
)

class DeviceContextCollector(private val context: Context) {

    fun collect(): DeviceContext {
        return DeviceContext(
            battery = batteryLevel(),
            network = networkType(),
            orientation = orientation()
        )
    }

    private fun batteryLevel(): Int {
        val intent = context.registerReceiver(
            null,
            IntentFilter(Intent.ACTION_BATTERY_CHANGED)
        ) ?: return -1

        val level = intent.getIntExtra(BatteryManager.EXTRA_LEVEL, -1)
        val scale = intent.getIntExtra(BatteryManager.EXTRA_SCALE, -1)

        if (level < 0 || scale <= 0) return -1

        return ((level * 100f) / scale).toInt().coerceIn(0, 100)
    }

    private fun networkType(): String {
        val manager = context.getSystemService(
            Context.CONNECTIVITY_SERVICE
        ) as? ConnectivityManager ?: return "unknown"

        val network = manager.activeNetwork ?: return "offline"
        val capabilities = manager.getNetworkCapabilities(network)
            ?: return "unknown"

        return when {
            capabilities.hasTransport(NetworkCapabilities.TRANSPORT_WIFI) ->
                "wifi"

            capabilities.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR) ->
                "mobile"

            capabilities.hasTransport(NetworkCapabilities.TRANSPORT_ETHERNET) ->
                "ethernet"

            else -> "online"
        }
    }

    private fun orientation(): String {
        val manager = context.getSystemService(
            Context.WINDOW_SERVICE
        ) as? WindowManager ?: return "unknown"

        val rotation = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            context.display?.rotation ?: Surface.ROTATION_0
        } else {
            @Suppress("DEPRECATION")
            manager.defaultDisplay.rotation
        }

        return when (rotation) {
            Surface.ROTATION_0,
            Surface.ROTATION_180 -> "portrait"

            Surface.ROTATION_90,
            Surface.ROTATION_270 -> "landscape"

            else -> "unknown"
        }
    }
}
