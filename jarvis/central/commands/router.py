import re


APP_ALIASES = {
    "google chrome": "chrome",
    "chrome": "chrome",
    "क्रोम": "chrome",
    "youtube": "youtube",
    "यूट्यूब": "youtube",
    "google maps": "maps",
    "maps": "maps",
    "मैप": "maps",
    "मैप्स": "maps",
    "settings": "settings",
    "setting": "settings",
    "सेटिंग": "settings",
    "सेटिंग्स": "settings",
}


OPEN_WORDS = (
    "open", "launch", "start",
    "खोल", "खोलो", "खोलना",
    "चालू करो", "chalu karo",
    "khol", "kholo",
)


# ---------------------------------------------------------
# SAFE CYBERSECURITY COMMANDS
# ---------------------------------------------------------

SECURITY_COMMANDS = {
    "security audit": "security_audit",
    "security check": "security_audit",
    "security scan": "security_audit",
    "सिक्योरिटी ऑडिट": "security_audit",
    "सिक्योरिटी चेक": "security_audit",
    "सुरक्षा जांच": "security_audit",

    "wifi audit": "wifi_audit",
    "wifi security": "wifi_audit",
    "वाईफाई ऑडिट": "wifi_audit",
    "वाईफाई सिक्योरिटी": "wifi_audit",

    "network audit": "network_audit",
    "network security": "network_audit",
    "नेटवर्क ऑडिट": "network_audit",
    "नेटवर्क सिक्योरिटी": "network_audit",

    "cctv audit": "cctv_audit",
    "camera audit": "cctv_audit",
    "सीसीटीवी ऑडिट": "cctv_audit",
    "कैमरा ऑडिट": "cctv_audit",

    "tls audit": "tls_audit",
    "tls security": "tls_audit",
    "टीएलएस ऑडिट": "tls_audit",

    "url audit": "url_security_audit",
    "url security": "url_security_audit",
    "यूआरएल ऑडिट": "url_security_audit",

    "bug audit": "bug_pattern_audit",
    "code security audit": "bug_pattern_audit",
    "बग ऑडिट": "bug_pattern_audit",

    "password audit": "password_audit",
    "password security": "password_audit",
    "पासवर्ड ऑडिट": "password_audit",
    "पासवर्ड सिक्योरिटी": "password_audit",

    "termux audit": "termux_audit",
    "termux security": "termux_audit",
    "टर्मक्स ऑडिट": "termux_audit",
    "टर्मक्स सिक्योरिटी": "termux_audit",

    "list listening services": "list_listening_services",
    "list open services": "list_listening_services",
    "list network services": "list_listening_services",
    "कौन सी सर्विस चल रही है": "list_listening_services",

    "security report": "security_report",
    "सिक्योरिटी रिपोर्ट": "security_report",
    "सुरक्षा रिपोर्ट": "security_report",

    "system inventory": "system_inventory",
    "hardware inventory": "system_inventory",
    "software inventory": "system_inventory",
    "hardware info": "system_inventory",
    "system info": "system_inventory",
}


def _normalize(text: str) -> str:
    return " ".join(
        str(text).strip().lower().split()
    )


def _detect_app(text: str):
    for alias, app in APP_ALIASES.items():
        if alias in text:
            return app
    return None


def _has_open_intent(text: str) -> bool:
    return any(
        word in text
        for word in OPEN_WORDS
    )


def _extract_url(text: str):
    match = re.search(
        r"(https?://[^\s]+)",
        text,
        re.IGNORECASE
    )

    if match:
        return match.group(1).rstrip(".,!?")

    return None


def _extract_security_target(text: str):
    """
    Extracts a target only when the user explicitly supplies one.
    No scanning of arbitrary devices is triggered here.
    """
    url = _extract_url(text)

    if url:
        return {
            "url": url
        }

    host = re.search(
        r"(?:host|hostname|server|target)\s*[:=]?\s*"
        r"([a-zA-Z0-9._:-]+)",
        text,
        re.IGNORECASE
    )

    if host:
        return {
            "host": host.group(1)
        }

    return {}


def _security_command(normalized: str, original: str):
    for phrase, action in sorted(
        SECURITY_COMMANDS.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    ):
        if phrase in normalized:

            parameters = _extract_security_target(
                normalized
            )

            return {
                "is_command": True,
                "action": action,
                "parameters": parameters,
                "text": original,
            }

    return None


def route(text: str):
    original = str(text)
    normalized = _normalize(original)

    # -----------------------------------------------------
    # PING
    # -----------------------------------------------------

    if normalized in {
        "ping",
        "test connection",
        "connection test",
        "कनेक्शन टेस्ट",
    }:
        return {
            "is_command": True,
            "action": "ping",
            "parameters": {},
            "text": original,
        }

    # -----------------------------------------------------
    # SECURITY COMMANDS
    # -----------------------------------------------------

    security = _security_command(
        normalized,
        original
    )

    if security:
        return security

    # -----------------------------------------------------
    # DEVICE INFO
    # -----------------------------------------------------

    device_words = (
        "device info",
        "device information",
        "phone info",
        "mobile info",
        "फोन की जानकारी",
        "मोबाइल की जानकारी",
        "डिवाइस की जानकारी",
    )

    if any(
        word in normalized
        for word in device_words
    ):
        return {
            "is_command": True,
            "action": "device_info",
            "parameters": {},
            "text": original,
        }

    # -----------------------------------------------------
    # URL
    # -----------------------------------------------------

    url = _extract_url(normalized)

    if url:
        return {
            "is_command": True,
            "action": "open_url",
            "parameters": {
                "url": url
            },
            "text": original,
        }

    # -----------------------------------------------------
    # WEBSITE BY DOMAIN
    # -----------------------------------------------------

    website_match = re.search(
        r"(?:open|launch|खोलो?|खोलना)\s+"
        r"(?:website|site|वेबसाइट)?\s*"
        r"([a-z0-9-]+\.(?:com|in|org|net|io|ai))",
        normalized,
        re.IGNORECASE
    )

    if website_match:
        domain = website_match.group(1)

        return {
            "is_command": True,
            "action": "open_url",
            "parameters": {
                "url": "https://" + domain
            },
            "text": original,
        }

    # -----------------------------------------------------
    # OPEN APP
    # -----------------------------------------------------

    app = _detect_app(normalized)

    if app and _has_open_intent(normalized):
        return {
            "is_command": True,
            "action": "open_app",
            "parameters": {
                "app": app
            },
            "text": original,
        }

    # -----------------------------------------------------
    # NOTIFICATION
    # -----------------------------------------------------

    notification_words = (
        "notification",
        "notify",
        "नोटिफिकेशन",
        "सूचना",
    )

    if any(
        word in normalized
        for word in notification_words
    ):
        message = normalized

        for word in notification_words:
            message = message.replace(
                word,
                ""
            )

        message = message.strip(" :,-")

        return {
            "is_command": True,
            "action": "notification",
            "parameters": {
                "title": "JARVIS",
                "message": (
                    message
                    or "सर, आपका notification तैयार है।"
                ),
            },
            "text": original,
        }

    # -----------------------------------------------------
    # NO COMMAND
    # -----------------------------------------------------

    return {
        "is_command": False,
        "action": None,
        "parameters": {},
        "text": original,
    }


class CommandRouter:

    def route(self, text: str):
        return route(text)
