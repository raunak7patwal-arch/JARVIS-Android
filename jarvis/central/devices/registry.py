import threading
import time


class DeviceRegistry:

    def __init__(self):
        self.devices = {}
        self.lock = threading.RLock()

    def register(
        self,
        device_id,
        name="Android",
        platform="android"
    ):
        with self.lock:
            self.devices[device_id] = {
                "device_id": device_id,
                "name": name,
                "platform": platform,
                "online": True,
                "last_seen": time.time(),
            }

    def heartbeat(
        self,
        device_id
    ):
        with self.lock:
            if device_id not in self.devices:
                self.register(
                    device_id
                )

            self.devices[
                device_id
            ]["online"] = True

            self.devices[
                device_id
            ]["last_seen"] = time.time()

    def offline(
        self,
        device_id
    ):
        with self.lock:
            if device_id in self.devices:
                self.devices[
                    device_id
                ]["online"] = False

    def get(
        self,
        device_id
    ):
        with self.lock:
            item = self.devices.get(
                device_id
            )

            if item is None:
                return None

            return dict(item)

    def all(self):
        with self.lock:
            return [
                dict(item)
                for item in self.devices.values()
            ]
