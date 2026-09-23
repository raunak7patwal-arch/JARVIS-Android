import threading
import time


class SmartHomeManager:

    ALLOWED_TYPES = {
        "light",
        "switch",
        "fan",
        "thermostat",
        "sensor",
        "plug",
    }

    ALLOWED_ACTIONS = {
        "turn_on",
        "turn_off",
        "set_level",
        "set_temperature",
        "read",
    }

    def __init__(self):
        self.devices = {}
        self.lock = threading.RLock()

    def register(
        self,
        device_id,
        name,
        device_type,
        room="unknown"
    ):
        device_type = str(
            device_type
        ).lower().strip()

        if device_type not in self.ALLOWED_TYPES:
            return False

        if not device_id or not name:
            return False

        with self.lock:
            self.devices[device_id] = {
                "id": device_id,
                "name": name,
                "type": device_type,
                "room": room,
                "state": "unknown",
                "level": None,
                "temperature": None,
                "online": True,
                "updated": time.time(),
            }

        return True

    def get(self, device_id):
        with self.lock:
            device = self.devices.get(
                device_id
            )

            return (
                dict(device)
                if device
                else None
            )

    def list_devices(self):
        with self.lock:
            return [
                dict(device)
                for device in self.devices.values()
            ]

    def set_state(
        self,
        device_id,
        action,
        value=None
    ):
        action = str(
            action
        ).strip().lower()

        if action not in self.ALLOWED_ACTIONS:
            return False

        with self.lock:
            device = self.devices.get(
                device_id
            )

            if not device:
                return False

            if action == "turn_on":
                device["state"] = "on"

            elif action == "turn_off":
                device["state"] = "off"

            elif action == "set_level":
                try:
                    level = int(value)
                except (TypeError, ValueError):
                    return False

                if not 0 <= level <= 100:
                    return False

                device["level"] = level

            elif action == "set_temperature":
                try:
                    temperature = float(value)
                except (TypeError, ValueError):
                    return False

                if not -20 <= temperature <= 60:
                    return False

                device["temperature"] = temperature

            elif action == "read":
                pass

            device["updated"] = time.time()

            return True


smart_home = SmartHomeManager()
