package com.jarvis.assistant.core

import android.content.Context
import android.content.Intent
import android.provider.Settings
import java.text.SimpleDateFormat
import java.util.*

object JarvisCore {

    fun handle(context: Context, raw: String): String {
        val c = raw.trim().lowercase(Locale.getDefault())

        return when {
            c.contains("time") || c.contains("समय") ||
            c.contains("टाइम") -> {
                val t = SimpleDateFormat(
                    "hh:mm a", Locale.getDefault()
                ).format(Date())
                "अभी $t बज रहे हैं।"
            }

            c.contains("settings") ||
            c.contains("सेटिंग") -> {
                launch(context, Intent(Settings.ACTION_SETTINGS))
                "Settings खोल रहा हूँ।"
            }

            c.contains("youtube") -> {
                openApp(context, "com.google.android.youtube")
                "YouTube खोल रहा हूँ।"
            }

            c.contains("instagram") -> {
                openApp(context, "com.instagram.android")
                "Instagram खोल रहा हूँ।"
            }

            c.contains("camera") ||
            c.contains("कैमरा") -> {
                launch(
                    context,
                    Intent("android.media.action.IMAGE_CAPTURE")
                )
                "Camera खोल रहा हूँ।"
            }

            else -> "Command समझ गया। इस feature पर अभी काम चल रहा है।"
        }
    }

    private fun launch(context: Context, intent: Intent) {
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        context.startActivity(intent)
    }

    private fun openApp(context: Context, packageName: String) {
        val intent = context.packageManager
            .getLaunchIntentForPackage(packageName)

        if (intent != null) {
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            context.startActivity(intent)
        }
    }
}
