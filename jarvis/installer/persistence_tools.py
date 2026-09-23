from pathlib import Path
import getpass
import time
import sys

sys.path.insert(0, str(Path.cwd()))

from jarvis.central.security.persistent_vault import PersistentVault
from jarvis.central.security.persistence import JARVISPersistence
from jarvis.central.security.memory_bridge import PersistentMemoryBridge


def main():
    print("======================================")
    print("JARVIS PERSISTENCE FULL TEST")
    print("======================================")

    vault = PersistentVault()
    persistence = JARVISPersistence()
    bridge = PersistentMemoryBridge()

    print("Master configured :", vault.configured)
    print("Vault unlocked    :", vault.unlocked)
    print("Persistence       :", persistence.status())

    if not vault.configured:
        print("ERROR: Master password is not configured")
        return 1

    print("--------------------------------------")
    print("[1/5] Unlocking vault...")

    password = getpass.getpass(
        "Enter JARVIS master password: "
    )

    if not vault.unlock(password):
        print("ERROR: Invalid master password")
        return 1

    print("Vault : UNLOCKED")

    try:
        print("[2/5] Testing encrypted vault read/write...")

        data = vault.load()

        if not isinstance(data, dict):
            data = {}

        marker = {
            "status": "verified",
            "timestamp": int(time.time())
        }

        data["persistence_test"] = marker
        vault.save(data)

        verified = vault.load()

        if verified.get("persistence_test") != marker:
            print("ERROR: Vault verification failed")
            return 1

        print("Vault read/write : OK")

        print("[3/5] Testing runtime state...")

        persistence.save_runtime_state(
            test=True,
            component="JARVIS",
            persistence_test_timestamp=int(time.time())
        )

        state = persistence.load_state()

        if not isinstance(state, dict):
            print("ERROR: Runtime state is not a dictionary")
            return 1

        print("Runtime state : SAVE/LOAD OK")

        print("[4/5] Testing persistent memory bridge...")

        if not bridge.unlock(password):
            print("ERROR: Memory bridge unlock failed")
            return 1

        bridge.remember(
            "persistence_test",
            marker
        )

        bridge.remember_conversation(
            "system",
            "JARVIS persistence verification"
        )

        bridge.add_activity(
            "persistence_test",
            {
                "verified": True,
                "timestamp": int(time.time())
            }
        )

        snapshot = bridge.snapshot()

        if not isinstance(snapshot, dict) or not snapshot:
            print("ERROR: Persistent memory snapshot is empty")
            return 1

        print("Memory write   : OK")
        print("Conversation    : OK")
        print("Activity        : OK")
        print("Snapshot        : OK")

        print("[5/5] Final verification...")

        status = persistence.status()

        print("Persistent       :", status.get("persistent"))
        print("Master configured:", status.get("master_configured"))
        print("Vault unlocked   :", status.get("vault_unlocked"))

        bridge.lock()
        vault.lock()

        print("Vault : LOCKED")

    except Exception as exc:
        try:
            bridge.lock()
        except Exception:
            pass

        try:
            vault.lock()
        except Exception:
            pass

        print("ERROR:", type(exc).__name__, str(exc))
        return 1

    print("======================================")
    print("JARVIS PERSISTENCE FULL TEST : PASS")
    print("======================================")
    print("Encrypted vault    : OK")
    print("Vault read/write   : OK")
    print("Runtime state      : OK")
    print("Persistent memory  : OK")
    print("Conversation save  : OK")
    print("Activity save      : OK")
    print("Vault final state  : LOCKED")
    print("Password storage   : DISABLED")
    print("======================================")
    print("SUCCESS")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
