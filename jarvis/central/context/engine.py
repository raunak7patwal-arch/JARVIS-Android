import time
import threading


class ContextEngine:

    def __init__(self, max_items=100):
        self.max_items = max_items
        self.items = []
        self.lock = threading.RLock()

    def update(
        self,
        device_id,
        context
    ):
        if not device_id:
            return False

        if not isinstance(context, dict):
            return False

        item = {
            "device_id": str(device_id),
            "context": dict(context),
            "timestamp": time.time(),
        }

        with self.lock:
            self.items.append(item)

            if len(self.items) > self.max_items:
                self.items = self.items[
                    -self.max_items:
                ]

        return True

    def latest(
        self,
        device_id=None
    ):
        with self.lock:
            if device_id is None:
                if not self.items:
                    return None

                return dict(self.items[-1])

            for item in reversed(self.items):
                if item["device_id"] == device_id:
                    return dict(item)

        return None

    def clear(
        self,
        device_id=None
    ):
        with self.lock:
            if device_id is None:
                self.items = []
            else:
                self.items = [
                    item
                    for item in self.items
                    if item["device_id"]
                    != device_id
                ]


context_engine = ContextEngine()
