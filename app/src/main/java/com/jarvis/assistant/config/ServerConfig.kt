package com.jarvis.assistant.config

import android.content.Context

object ServerConfig {

    private const val PREFS_NAME =
        "jarvis_config"

    private const val SERVER_ADDRESS =
        "server_address"

    private const val DEFAULT_ADDRESS =
        "http://127.0.0.1:8787"

    fun getServerAddress(
        context: Context
    ): String {

        val prefs =
            context.getSharedPreferences(
                PREFS_NAME,
                Context.MODE_PRIVATE
            )

        return prefs.getString(
            SERVER_ADDRESS,
            DEFAULT_ADDRESS
        ) ?: DEFAULT_ADDRESS
    }

    fun setServerAddress(
        context: Context,
        address: String
    ): Boolean {

        val cleanAddress =
            address
                .trim()
                .removeSuffix("/")

        if (
            cleanAddress.isEmpty() ||
            !cleanAddress.startsWith(
                "http://"
            ) &&
            !cleanAddress.startsWith(
                "https://"
            )
        ) {
            return false
        }

        prefs(context)
            .edit()
            .putString(
                SERVER_ADDRESS,
                cleanAddress
            )
            .apply()

        return true
    }

    fun resetServerAddress(
        context: Context
    ) {

        prefs(context)
            .edit()
            .remove(SERVER_ADDRESS)
            .apply()
    }

    private fun prefs(
        context: Context
    ) =
        context.getSharedPreferences(
            PREFS_NAME,
            Context.MODE_PRIVATE
        )
}
