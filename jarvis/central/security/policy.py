class SecurityPolicy:

    ALLOWED_COMMANDS = {
        "ping",
        "device_info",
        "open_app",
        "open_url",
        "notification",
    }

    BLOCKED_COMMANDS = {
        "shell",
        "exec",
        "root",
        "su",
        "delete_system",
        "wipe_device",
        "install_unknown",
        "stealth",
        "surveillance",
    }

    @classmethod
    def allowed(cls, action):
        action = str(action).strip().lower()

        if action in cls.BLOCKED_COMMANDS:
            return False

        return action in cls.ALLOWED_COMMANDS

    @classmethod
    def validate(cls, action, parameters=None):
        if not cls.allowed(action):
            return False, "Command not allowed"

        if not isinstance(parameters, dict):
            return False, "Invalid parameters"

        if action == "open_url":
            url = str(
                parameters.get(
                    "url",
                    ""
                )
            ).strip().lower()

            if not (
                url.startswith("http://")
                or url.startswith("https://")
            ):
                return False, "Only HTTP/HTTPS URLs are allowed"

        if action == "open_app":
            app = str(
                parameters.get(
                    "app",
                    ""
                )
            ).strip().lower()

            if not app:
                return False, "App is required"

        if action == "notification":
            message = str(
                parameters.get(
                    "message",
                    ""
                )
            ).strip()

            if len(message) > 1000:
                return False, "Notification too long"

        return True, "OK"

# Backward-compatible module-level helper
def allowed(action):
    return SecurityPolicy.allowed(action)
