from jarvis.central.integration import integration
from jarvis.central.security.policy import SecurityPolicy


class DeviceAPI:

    def register(
        self,
        device_id,
        name="Android",
        platform="android"
    ):
        return integration.register_device(
            device_id,
            name,
            platform
        )

    def heartbeat(
        self,
        device_id
    ):
        return integration.heartbeat(
            device_id
        )

    def list_devices(self):
        return integration.devices.all()

    def create_command(
        self,
        device_id,
        action,
        parameters=None
    ):
        valid, message = SecurityPolicy.validate(
            action,
            parameters or {}
        )

        if not valid:
            return {
                "ok": False,
                "error": message,
            }

        command = integration.create_device_command(
            device_id,
            action,
            parameters or {}
        )

        return {
            "ok": True,
            "command": command,
        }

    def complete(
        self,
        command_id,
        result
    ):
        ok = integration.complete_device_command(
            command_id,
            result
        )

        return {
            "ok": ok
        }

    def fail(
        self,
        command_id,
        error
    ):
        ok = integration.fail_device_command(
            command_id,
            error
        )

        return {
            "ok": ok
        }


device_api = DeviceAPI()
