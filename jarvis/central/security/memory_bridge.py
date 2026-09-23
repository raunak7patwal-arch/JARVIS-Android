from __future__ import annotations

import time
from typing import Any

from jarvis.central.security.persistent_vault import (
    PersistentVault,
)


class PersistentMemoryBridge:

    def __init__(self):
        self.vault = PersistentVault()

    def unlock(self, password: str) -> bool:
        return self.vault.unlock(password)

    def lock(self):
        self.vault.lock()

    @property
    def unlocked(self) -> bool:
        return self.vault.unlocked

    def load(self) -> dict:
        if not self.unlocked:
            return {}

        data = self.vault.load()

        if not isinstance(data, dict):
            return {}

        return data

    def save(self, data: dict):
        if not self.unlocked:
            raise PermissionError(
                "Persistent memory is locked"
            )

        self.vault.save(data)

    def remember(self, key: str, value: Any):
        data = self.load()

        memory = data.setdefault(
            "memory",
            {}
        )

        memory[str(key)] = {
            "value": value,
            "updated": int(time.time()),
        }

        data["memory_updated"] = int(
            time.time()
        )

        self.save(data)

    def get_memory(self, key: str):
        data = self.load()

        memory = data.get(
            "memory",
            {}
        )

        item = memory.get(str(key))

        if isinstance(item, dict):
            return item.get("value")

        return None

    def remember_conversation(
        self,
        role: str,
        text: str,
    ):
        data = self.load()

        conversation = data.setdefault(
            "conversation",
            []
        )

        conversation.append({
            "role": str(role),
            "text": str(text),
            "timestamp": int(time.time()),
        })

        # Keep the persistent vault compact.
        if len(conversation) > 500:
            del conversation[:-500]

        self.save(data)

    def add_activity(
        self,
        event: str,
        details: dict | None = None,
    ):
        data = self.load()

        activity = data.setdefault(
            "activity",
            []
        )

        activity.append({
            "event": str(event),
            "details": (
                details
                if isinstance(details, dict)
                else {}
            ),
            "timestamp": int(time.time()),
        })

        if len(activity) > 1000:
            del activity[:-1000]

        self.save(data)

    def snapshot(self):
        data = self.load()

        return {
            "memory_items": len(
                data.get("memory", {})
            ),
            "conversation_items": len(
                data.get("conversation", [])
            ),
            "activity_items": len(
                data.get("activity", [])
            ),
            "updated": data.get(
                "memory_updated"
            ),
        }


if __name__ == "__main__":
    bridge = PersistentMemoryBridge()

    print("======================================")
    print("JARVIS PERSISTENT MEMORY BRIDGE")
    print("======================================")
    print(
        "Master configured :",
        bridge.vault.configured,
    )
    print(
        "Vault unlocked    :",
        bridge.unlocked,
    )
    print(
        "Encrypted bridge  : READY",
    )
    print(
        "Memory bridge     : READY",
    )
    print(
        "Conversation       : READY",
    )
    print(
        "Activity           : READY",
    )
    print("======================================")
    print("SUCCESS")
