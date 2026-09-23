from __future__ import annotations

import getpass
import hashlib
import json
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

BACKUP_NAME = "JARVIS-SECURE-TRANSFER"
BACKUP_DIR = ROOT / BACKUP_NAME

PERSISTENT_DIR = ROOT / "jarvis/central/persistent_data"
SECURITY_DIR = ROOT / "jarvis/central/security"

FILES = [
    ROOT / "jarvis/central/security/master.json",
    ROOT / "jarvis/central/security/vault.bin",
    ROOT / "jarvis/central/security/security_audit.jsonl",
    ROOT / "jarvis/central/persistent_data/state.json",
    ROOT / "jarvis/central/persistent_data/lineage.json",

    ROOT / "jarvis/central/memory/memory.json",
    ROOT / "jarvis/central/memory/advanced_memory.json",

    ROOT / "jarvis/central/cache/cache.json",
    ROOT / "jarvis/central/cache/knowledge.json",

    ROOT / "jarvis/central/conversation/conversation.json",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()

    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)

    return h.hexdigest()


def verify_password() -> bool:
    from jarvis.central.security.persistent_vault import PersistentVault

    password = getpass.getpass(
        "Enter JARVIS master password: "
    )

    vault = PersistentVault()

    if not vault.configured:
        print("ERROR: JARVIS master password is not configured.")
        return False

    if not vault.unlock(password):
        print("ERROR: Invalid JARVIS master password.")
        return False

    vault.lock()

    print("Master password : VERIFIED")
    return True


def create_backup():
    print("======================================")
    print("     JARVIS SECURE TRANSFER BACKUP")
    print("======================================")

    if not verify_password():
        return 1

    if BACKUP_DIR.exists():
        print("Removing previous transfer package...")
        shutil.rmtree(BACKUP_DIR)

    DATA = BACKUP_DIR / "DATA"
    DATA.mkdir(parents=True)

    manifest = {
        "name": "JARVIS",
        "format": "JARVIS-SECURE-TRANSFER",
        "version": "1.0",
        "created_at": int(time.time()),
        "password_included": False,
        "api_keys_included": False,
        "credentials_included": False,
        "files": {},
    }

    copied = 0

    print("--------------------------------------")
    print("[1/3] Copying JARVIS persistent data...")

    for source in FILES:
        if not source.exists() or not source.is_file():
            continue

        relative = source.relative_to(ROOT)
        destination = DATA / relative

        destination.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        shutil.copy2(source, destination)

        manifest["files"][str(relative)] = {
            "sha256": sha256(destination),
            "size": destination.stat().st_size,
        }

        copied += 1

    print(f"Files copied : {copied}")

    print("[2/3] Creating integrity manifest...")

    (BACKUP_DIR / "manifest.json").write_text(
        json.dumps(
            manifest,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8",
    )

    (BACKUP_DIR / "README.txt").write_text(
        """JARVIS SECURE TRANSFER PACKAGE
================================

This package contains JARVIS-managed
persistent data for authorized transfer.

Included:
- Encrypted JARVIS vault
- Master-password metadata
- Persistent runtime state
- Installation lineage
- Memory
- Cache
- Conversation data when present
- Integrity manifest

NOT included:
- Master password
- API keys
- Private credentials
- Android permissions
- APK installation bypass

The encrypted vault remains protected by
the existing JARVIS master password.

Restore only on a device you own or are
authorized to configure.
""",
        encoding="utf-8",
    )

    print("[3/3] Final verification...")

    check = json.loads(
        (BACKUP_DIR / "manifest.json").read_text(
            encoding="utf-8"
        )
    )

    failed = []

    for relative, info in check["files"].items():
        path = DATA / relative

        if not path.exists():
            failed.append(relative)
            continue

        if sha256(path) != info["sha256"]:
            failed.append(relative)

    if failed:
        print("ERROR: Integrity verification failed.")
        for item in failed:
            print(" -", item)
        return 1

    print("Integrity : VERIFIED")

    print("======================================")
    print("JARVIS SECURE BACKUP : READY")
    print("======================================")
    print(f"Package : {BACKUP_DIR}")
    print("Password stored : NO")
    print("API keys stored : NO")
    print("Credentials stored : NO")
    print("Integrity : VERIFIED")
    print("SUCCESS")

    return 0


def restore_backup():
    print("======================================")
    print("       JARVIS SECURE RESTORE")
    print("======================================")

    if not BACKUP_DIR.exists():
        print("ERROR: JARVIS-SECURE-TRANSFER not found.")
        return 1

    manifest_file = BACKUP_DIR / "manifest.json"

    if not manifest_file.exists():
        print("ERROR: Backup manifest is missing.")
        return 1

    manifest = json.loads(
        manifest_file.read_text(
            encoding="utf-8"
        )
    )

    if manifest.get("format") != "JARVIS-SECURE-TRANSFER":
        print("ERROR: Unsupported JARVIS transfer package.")
        return 1

    DATA = BACKUP_DIR / "DATA"

    print("[1/4] Verifying backup integrity...")

    for relative, info in manifest["files"].items():
        path = DATA / relative

        if not path.exists():
            print("ERROR: Missing:", relative)
            return 1

        if sha256(path) != info["sha256"]:
            print("ERROR: Hash mismatch:", relative)
            return 1

    print("Backup integrity : VERIFIED")

    print("[2/4] Verifying JARVIS master password...")

    password = getpass.getpass(
        "Enter backup JARVIS master password: "
    )

    from jarvis.central.security.persistent_vault import PersistentVault

    current_vault = PersistentVault()

    backup_master = DATA / (
        "jarvis/central/security/master.json"
    )

    backup_vault = DATA / (
        "jarvis/central/security/vault.bin"
    )

    if not backup_master.exists() or not backup_vault.exists():
        print("ERROR: Encrypted vault files are missing.")
        return 1

    # Save the current installation before changing anything.
    rollback = ROOT / (
        "JARVIS-RESTORE-ROLLBACK-"
        + str(int(time.time()))
    )

    rollback.mkdir(parents=True)

    current_files = []

    for relative in manifest["files"]:
        target = ROOT / relative

        if target.exists() and target.is_file():
            backup_target = rollback / relative
            backup_target.parent.mkdir(
                parents=True,
                exist_ok=True
            )
            shutil.copy2(target, backup_target)
            current_files.append(relative)

    print("[3/4] Restoring JARVIS data...")

    restored = 0

    try:
        for relative in manifest["files"]:
            source = DATA / relative
            target = ROOT / relative

            target.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            shutil.copy2(source, target)
            restored += 1

        # Verify the restored encrypted vault with the supplied password.
        test_vault = PersistentVault()

        if not test_vault.unlock(password):
            raise RuntimeError(
                "Restored vault rejected the supplied master password."
            )

        test_vault.lock()

    except Exception as exc:
        print("RESTORE ERROR:", type(exc).__name__, str(exc))
        print("Rolling back current installation...")

        for relative in manifest["files"]:
            target = ROOT / relative
            old = rollback / relative

            if old.exists():
                target.parent.mkdir(
                    parents=True,
                    exist_ok=True
                )
                shutil.copy2(old, target)

        print("Rollback : COMPLETE")
        return 1

    print("[4/4] Final verification...")

    final_vault = PersistentVault()

    if not final_vault.unlock(password):
        print("ERROR: Final vault verification failed.")
        return 1

    final_vault.lock()

    print("Restored files :", restored)
    print("Vault          : VERIFIED")
    print("Password       : NOT STORED")
    print("Rollback copy  :", rollback)

    print("======================================")
    print("JARVIS SECURE RESTORE : SUCCESS")
    print("======================================")

    return 0


def main():
    if len(sys.argv) != 2:
        print("Usage:")
        print("  python jarvis/installer/jarvis_transfer.py backup")
        print("  python jarvis/installer/jarvis_transfer.py restore")
        return 1

    command = sys.argv[1].lower()

    if command == "backup":
        return create_backup()

    if command == "restore":
        return restore_backup()

    print("ERROR: Use 'backup' or 'restore'.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
