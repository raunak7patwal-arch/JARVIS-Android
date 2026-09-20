package com.jarvis.assistant

import android.content.Context
import android.content.Intent
import android.provider.Settings

object CommandRouter {

    fun execute(context: Context, command: String): String {
        val c = command.lowercase()

        return when {
            c.contains("settings") || c.contains("सेटिंग") -> {
                context.startActivity(
                    Intent(Settings.ACTION_SETTINGS).apply {
                        addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                    }
                )
                "Settings खोल रहा हूँ।"
            }

            c.contains("youtube") -> {
                open(context, "com.google.android.youtube")
                "YouTube खोल रहा हूँ।"
            }

            c.contains("instagram") -> {
                open(context, "com.instagram.android")
                "Instagram खोल रहा हूँ।"
            }

            c.contains("camera") || c.contains("कैमरा") -> {
                openCamera(context)
                "Camera के लिए आपकी अनुमति चाहिए।"
            }

            else -> "Command received."
        }
    }

    private fun open(context: Context, pkg: String) {
        context.packageManager
            .getLaunchIntentForPackage(pkg)
            ?.apply { addFlags(Intent.FLAG_ACTIVITY_NEW_TASK) }
            ?.let(context::startActivity)
    }

    private fun openCamera(context: Context) {
        val i = Intent("android.media.action.IMAGE_CAPTURE")
        i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        context.startActivity(i)
    }
}
