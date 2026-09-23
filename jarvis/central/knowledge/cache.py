import json
import os
import threading
import time
import hashlib


class KnowledgeCache:

    def __init__(
        self,
        path="jarvis/central/cache/knowledge.json",
        ttl=3600
    ):
        self.path = path
        self.ttl = ttl
        self.lock = threading.RLock()
        self.data = {}

        os.makedirs(
            os.path.dirname(path),
            exist_ok=True
        )

        self._load()

    def _load(self):
        try:
            with open(
                self.path,
                "r",
                encoding="utf-8"
            ) as f:
                self.data = json.load(f)
        except Exception:
            self.data = {}

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

    @staticmethod
    def _key(
        question,
        language
    ):
        raw = (
            language.lower().strip()
            + ":"
            + question.lower().strip()
        )

        return hashlib.sha256(
            raw.encode("utf-8")
        ).hexdigest()

    def get(
        self,
        question,
        language
    ):
        key = self._key(
            question,
            language
        )

        with self.lock:
            item = self.data.get(key)

            if not item:
                return None

            timestamp = item.get(
                "timestamp",
                0
            )

            if (
                time.time()
                - timestamp
                > self.ttl
            ):
                self.data.pop(
                    key,
                    None
                )
                self._save()
                return None

            return item.get(
                "value"
            )

    def set(
        self,
        question,
        language,
        value
    ):
        key = self._key(
            question,
            language
        )

        with self.lock:
            self.data[key] = {
                "timestamp": time.time(),
                "value": value
            }

            self._save()
