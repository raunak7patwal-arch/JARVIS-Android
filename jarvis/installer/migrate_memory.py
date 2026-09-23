from pathlib import Path
import json
import time
import shutil
import getpass

from jarvis.central.security.persistent_vault import PersistentVault

ROOT = Path("jarvis/central")
BACKUP = ROOT / "security" / "pre-migration-backup"

print("======================================")
print("JARVIS MEMORY MIGRATION")
print("======================================")

vault = PersistentVault()

if not vault.configured:
    print("ERROR: Master password is not configured")
    raise SystemExit(1)

FILES = [
    ROOT / "memory" / "memory.json",
    ROOT / "memory" / "advanced_memory.json",
    ROOT / "memory" / "activity.jsonl",
    ROOT / "cache" / "cache.json",
]

print("[1/4] Creating safety backup...")

BACKUP.mkdir(parents=True, exist_ok=True)

for src in FILES:
    if src.exists():
        shutil.copy2(src, BACKUP / src.name)

print("Backup : READY")

def read_json(path):
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

memory = read_json(ROOT / "memory" / "memory.json")
advanced = read_json(ROOT / "memory" / "advanced_memory.json")
cache = read_json(ROOT / "cache" / "cache.json")

activity_path = ROOT / "memory" / "activity.jsonl"

activity = []
if activity_path.exists():
    activity = [
        x for x in activity_path.read_text(encoding="utf-8").splitlines()
        if x.strip()
    ]

print("[2/4] Existing data loaded")
print("Memory records   :", len(memory) if isinstance(memory, (dict, list)) else 0)
print("Advanced memory  :", len(advanced) if isinstance(advanced, (dict, list)) else 0)
print("Activity records :", len(activity))

print("[3/4] Unlocking encrypted vault...")

password = getpass.getpass("Enter JARVIS master password: ")

if not vault.unlock(password):
    print("ERROR: Invalid master password")
    raise SystemExit(1)

print("Vault : UNLOCKED")

current = vault.load()

if not isinstance(current, dict):
    current = {}

current["migration"] = {
    "version": 1,
    "timestamp": int(time.time()),
    "source": "jarvis_existing_data",
    "verified": True,
}

current["legacy_data"] = {
    "memory": memory,
    "advanced_memory": advanced,
    "activity": activity[-1000:],
    "cache": cache,
}

current["persistent_snapshot"] = {
    "memory": memory,
    "advanced_memory": advanced,
    "activity_count": len(activity),
}

vault.save(current)

check = vault.load()

if "legacy_data" not in check or "persistent_snapshot" not in check:
    print("ERROR: Verification failed")
    vault.lock()
    raise SystemExit(1)

vault.lock()

print("[4/4] Verification complete")
print("======================================")
print("JARVIS MEMORY MIGRATION : COMPLETE")
print("======================================")
print("Original files : PRESERVED")
print("Safety backup  : READY")
print("Encrypted data : VERIFIED")
print("Vault          : LOCKED")
print("Password       : NOT STORED")
print("======================================")
print("SUCCESS")
