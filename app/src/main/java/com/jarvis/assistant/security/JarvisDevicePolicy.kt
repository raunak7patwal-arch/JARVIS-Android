package com.jarvis.assistant.security

object JarvisDevicePolicy {

    private val blockedActions = setOf(
        "payment",
        "upi_payment",
        "money_transfer",
        "paytm_transaction",
        "otp_access",
        "password_access",
        "credential_access",
        "security_bypass",
        "root_escalation",
        "permission_bypass"
    )

    private val consentActions = setOf(
        "microphone",
        "camera",
        "screen_capture",
        "accessibility"
    )

    fun isBlocked(action: String?): Boolean {
        return action?.trim()?.lowercase() in blockedActions
    }

    fun requiresUserConsent(action: String?): Boolean {
        return action?.trim()?.lowercase() in consentActions
    }

    fun isAllowed(action: String?): Boolean {
        if (action.isNullOrBlank()) return false
        if (isBlocked(action)) return false
        return true
    }
}
