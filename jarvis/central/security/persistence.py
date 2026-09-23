from __future__ import annotations

import json
import time
from pathlib import Path

from jarvis.central.security.persistent_vault import (
    PersistentVault,
)


BASE = Path("jarvis/central/persistent_data")
STATE_FILE = BASE / "state.json"
LINEAGE_FILE = BASE / "lineage.json"


class JARVISPersistence:

    def __init__(self):
        BASE.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.vault = PersistentVault()

    def status(self):
        return {
            "persistent": True,
            "master_configured":
                self.vault.configured,
            "vault_unlocked":
                self.vault.unlocked,
            "state_exists":
                STATE_FILE.exists(),
            "lineage_exists":
                LINEAGE_FILE.exists(),
        }

    def save_state(self, state: dict):
        if not isinstance(state, dict):
            raise TypeError(
                "state must be a dictionary"
            )

        state = dict(state)

        state["updated"] = int(
            time.time()
        )

        STATE_FILE.write_text(
            json.dumps(
                state,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    def load_state(self):
        if not STATE_FILE.exists():
            return {}

        try:
            data = json.loads(
                STATE_FILE.read_text(
                    encoding="utf-8"
                )
            )

            return (
                data
                if isinstance(data, dict)
                else {}
            )

        except Exception:
            return {}

    def create_lineage(self):
        if LINEAGE_FILE.exists():
            return

        lineage = {
            "system": "JARVIS",
            "format": 1,
            "created": int(time.time()),
            "purpose": (
                "Persistent JARVIS installation lineage"
            ),
            "persistent_storage": True,
            "portable_data_supported": True,
            "master_password_required": True,
        }

        LINEAGE_FILE.write_text(
            json.dumps(
                lineage,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    def save_runtime_state(self, **values):
        state = self.load_state()

        for key, value in values.items():
            state[str(key)] = value

        self.save_state(state)

    def record_startup(self):
        state = self.load_state()

        count = int(
            state.get("startup_count", 0)
        )

        state["startup_count"] = count + 1
        state["last_startup"] = int(time.time())

        self.save_state(state)

    def record_shutdown(self):
        state = self.load_state()

        state["last_shutdown"] = int(time.time())

        self.save_state(state)


if __name__ == "__main__":
    p = JARVISPersistence()
    p.create_lineage()

    print("======================================")
    print("JARVIS PERSISTENCE")
    print("======================================")
    print(
        "Persistent storage :",
        p.status()["persistent"],
    )
    print(
        "Lineage            :",
        LINEAGE_FILE.exists(),
    )
    print("State              :", p.load_state())
    print("======================================")
    print("SUCCESS")
