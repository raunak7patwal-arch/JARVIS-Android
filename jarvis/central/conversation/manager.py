import threading
import time


class ConversationManager:

    def __init__(self, max_turns=12):
        self.max_turns = max_turns
        self.history = []
        self.lock = threading.Lock()

    def add_user(self, text):
        text = str(text).strip()

        if not text:
            return

        with self.lock:
            self.history.append({
                "role": "user",
                "text": text,
                "timestamp": time.time()
            })
            self._trim()

    def add_assistant(self, text):
        text = str(text).strip()

        if not text:
            return

        with self.lock:
            self.history.append({
                "role": "assistant",
                "text": text,
                "timestamp": time.time()
            })
            self._trim()

    def _trim(self):
        maximum = self.max_turns * 2

        if len(self.history) > maximum:
            self.history = self.history[-maximum:]

    def context(self):
        with self.lock:

            if not self.history:
                return ""

            lines = []

            for item in self.history:
                role = item.get("role", "")
                text = item.get("text", "")

                if role == "user":
                    lines.append(f"User: {text}")

                elif role == "assistant":
                    lines.append(f"JARVIS: {text}")

            return "\n".join(lines)

    def recent(self, limit=10):

        with self.lock:
            return self.history[-limit:]

    def clear(self):

        with self.lock:
            self.history = []

    def size(self):

        with self.lock:
            return len(self.history)
