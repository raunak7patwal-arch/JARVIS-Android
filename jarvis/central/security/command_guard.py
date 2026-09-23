from jarvis.central.security.policy import SecurityPolicy


class CommandGuard:

    @staticmethod
    def validate(
        device_id,
        action,
        parameters=None
    ):
        if not device_id:
            return False, "Device required"

        valid, message = (
            SecurityPolicy.validate(
                action,
                parameters or {}
            )
        )

        if not valid:
            return False, message

        return True, "OK"

    @staticmethod
    def require_confirmation(action):
        return str(
            action
        ).strip().lower() in {
            "open_url",
            "open_app",
            "notification",
        }
