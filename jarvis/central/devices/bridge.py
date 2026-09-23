import threading
import time


class DeviceBridge:

    SAFE_ACTIONS = {
        "ping",
        "device_info",
        "open_app",
        "open_url",
        "notification",
    }

    def __init__(self):
        self.pending = {}
        self.lock = threading.RLock()

    def create_command(
        self,
        device_id,
        action,
        parameters=None
    ):
        if action not in self.SAFE_ACTIONS:
            raise ValueError(
                "Action not allowed"
            )

        command_id = (
            f"{device_id}-"
            f"{int(time.time() * 1000)}"
        )

        command = {
            "id": command_id,
            "device_id": device_id,
            "action": action,
            "parameters": (
                parameters
                if isinstance(
                    parameters,
                    dict
                )
                else {}
            ),
            "created": time.time(),
            "status": "pending",
        }

        with self.lock:
            self.pending[
                command_id
            ] = command

        return dict(command)

    def complete(
        self,
        command_id,
        result
    ):
        with self.lock:
            command = self.pending.get(
                command_id
            )

            if not command:
                return False

            command["status"] = "completed"
            command["result"] = result
            command["completed"] = time.time()

            return True

    def fail(
        self,
        command_id,
        error
    ):
        with self.lock:
            command = self.pending.get(
                command_id
            )

            if not command:
                return False

            command["status"] = "failed"
            command["error"] = str(error)

            return True

    def get(
        self,
        command_id
    ):
        with self.lock:
            command = self.pending.get(
                command_id
            )

            if command is None:
                return None

            return dict(command)

    def cleanup(
        self,
        max_age=3600
    ):
        cutoff = (
            time.time()
            - max_age
        )

        with self.lock:
            expired = []

            for command_id, command in list(
                self.pending.items()
            ):
                if command.get(
                    "created",
                    0
                ) < cutoff:
                    expired.append(
                        command_id
                    )

            for command_id in expired:
                self.pending.pop(
                    command_id,
                    None
                )

            return len(expired)
