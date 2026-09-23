import hashlib
import json
import os
import threading
import time


class FastCache:

    def __init__(
        self,
        ttl=3600
    ):

        self.path = os.path.join(
            os.path.dirname(__file__),
            "cache.json"
        )

        self.ttl = ttl
        self.lock = threading.Lock()
        self.data = self._load()

    def _load(self):

        try:

            if os.path.exists(self.path):

                with open(
                    self.path,
                    "r",
                    encoding="utf-8"
                ) as f:

                    data = json.load(f)

                if isinstance(data, dict):
                    return data

        except Exception:
            pass

        return {}

    def _save(self):

        temp = self.path + ".tmp"

        with open(
            temp,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                self.data,
                f,
                ensure_ascii=False
            )

        os.replace(
            temp,
            self.path
        )

    def key(self, text):

        normalized = (
            " ".join(
                str(text)
                .lower()
                .strip()
                .split()
            )
        )

        return hashlib.sha256(
            normalized.encode("utf-8")
        ).hexdigest()

    def get(self, text):

        key = self.key(text)

        with self.lock:

            item = self.data.get(key)

            if not item:
                return None

            created = item.get(
                "time",
                0
            )

            if (
                self.ttl > 0
                and time.time() - created
                > self.ttl
            ):

                self.data.pop(
                    key,
                    None
                )

                self._save()

                return None

            return item.get("answer")

    def set(
        self,
        text,
        answer
    ):

        key = self.key(text)

        with self.lock:

            self.data[key] = {
                "answer": answer,
                "time": time.time()
            }

            self._save()

    def clear(self):

        with self.lock:

            self.data = {}
            self._save()
