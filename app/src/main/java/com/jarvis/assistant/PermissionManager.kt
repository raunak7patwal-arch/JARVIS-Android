package com.jarvis.assistant

import android.Manifest
import android.app.Activity
import android.content.pm.PackageManager
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat

object PermissionManager {

    const val REQUEST = 200

    fun requestBasic(activity: Activity) {
        val list = mutableListOf<String>()

        if (ContextCompat.checkSelfPermission(
                activity, Manifest.permission.RECORD_AUDIO
            ) != PackageManager.PERMISSION_GRANTED
        ) list.add(Manifest.permission.RECORD_AUDIO)

        if (android.os.Build.VERSION.SDK_INT >= 33 &&
            ContextCompat.checkSelfPermission(
                activity, Manifest.permission.POST_NOTIFICATIONS
            ) != PackageManager.PERMISSION_GRANTED
        ) list.add(Manifest.permission.POST_NOTIFICATIONS)

        if (list.isNotEmpty()) {
            ActivityCompat.requestPermissions(
                activity, list.toTypedArray(), REQUEST
            )
        }
    }

    fun hasMic(activity: Activity): Boolean =
        ContextCompat.checkSelfPermission(
            activity, Manifest.permission.RECORD_AUDIO
        ) == PackageManager.PERMISSION_GRANTED
}
