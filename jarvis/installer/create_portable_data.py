from __future__ import annotations

import hashlib
import json
import shutil
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "JARVIS-DATA-PORTABLE"


def now():
    return int(time.time())


def sha256(path: Path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def copy_if_exists(src: Path, dst: Path):
    if not src.exists() or not src.is_file():
        return False

    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return True


def main():
    if PACKAGE.exists():
        shutil.rmtree(PACKAGE)

    data = PACKAGE / "DATA"
    memory = data / "MEMORY"
    history = data / "ACTIVITY"
    config = data / "CONFIG"

    memory.mkdir(parents=True)
    history.mkdir(parents=True)
    config.mkdir(parents=True)

    created = now()
    portable_id = uuid.uuid4().hex

    # Persistent JARVIS memory
    memory_files = [
        ROOT / "jarvis/central/memory/memory.json",
        ROOT / "jarvis/central/memory/advanced_memory.json",
        ROOT / "jarvis/central/memory.json",
    ]

    copied_memory = []

    for src in memory_files:
        if copy_if_exists(src, memory / src.name):
            copied_memory.append(src.name)

    # Existing cache / conversation data
    optional_data = [
        ROOT / "jarvis/central/cache",
        ROOT / "jarvis/central/conversation",
    ]

    for src in optional_data:
        if src.exists() and src.is_dir():
            dst = data / src.name
            shutil.copytree(src, dst, dirs_exist_ok=True)

    # Portable activity database
    activity_file = history / "activity.jsonl"

    if not activity_file.exists():
        activity_file.write_text("", encoding="utf-8")

    # Add a portable-package creation event.
    event = {
        "timestamp": created,
        "event": "portable_package_created",
        "portable_id": portable_id,
        "source": "JARVIS-Android",
        "memory_files": copied_memory,
    }

    with activity_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

    # Configuration that is safe to move.
    config_data = {
        "name": "JARVIS",
        "portable_format": "JARVIS-DATA",
        "version": "1.0",
        "portable_id": portable_id,
        "created_at": created,
        "parent_portable_id": None,
        "device_history": [],
        "security": {
            "api_keys_included": False,
            "credentials_included": False,
            "activity_log_included": True,
            "memory_included": True,
        },
    }

    config_file = config / "portable.json"
    config_file.write_text(
        json.dumps(config_data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    # Device lineage/history.
    lineage = data / "DEVICE-LINEAGE.json"

    lineage_data = {
        "portable_id": portable_id,
        "created_at": created,
        "copies": [
            {
                "copy_id": portable_id,
                "created_at": created,
                "source": "original-build",
            }
        ],
    }

    lineage.write_text(
        json.dumps(lineage_data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    # Human-readable activity description.
    (history / "README.txt").write_text(
        """JARVIS ACTIVITY DATA
=====================

This directory stores portable JARVIS activity history.

activity.jsonl:
One event per line.

DEVICE-LINEAGE.json:
Tracks portable package copies/instances.

The package does not silently install anything
and does not bypass Android permissions.
""",
        encoding="utf-8",
    )

    # Main portable README.
    (PACKAGE / "README.txt").write_text(
        """JARVIS PORTABLE DATA
=====================

This package is DATA, not an APK.

It is designed to be copied to a Pendrive
and moved between compatible JARVIS installations.

Contains:
- JARVIS memory
- Portable configuration
- Activity history
- Device/copy lineage
- Integrity manifest

It intentionally does NOT copy API keys or
private authentication credentials.

IMPORTANT:
A copied package carries its previous data/history,
but a new Android device must still be separately
authorized and configured.
""",
        encoding="utf-8",
    )

    # Integrity manifest.
    manifest = {
        "format": "JARVIS-DATA",
        "version": "1.0",
        "portable_id": portable_id,
        "created_at": created,
        "files": {},
    }

    for p in PACKAGE.rglob("*"):
        if not p.is_file():
            continue

        relative = p.relative_to(PACKAGE)

        if relative.as_posix() == "manifest.json":
            continue

        manifest["files"][str(relative)] = {
            "sha256": sha256(p),
            "size": p.stat().st_size,
        }

    (PACKAGE / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print()
    print("======================================")
    print("       JARVIS PORTABLE DATA")
    print("======================================")
    print()
    print("SUCCESS")
    print(f"Portable ID : {portable_id}")
    print(f"Package     : {PACKAGE}")
    print()
    print("NO APK BUILT")
    print("NO APP INSTALLATION")
    print("MEMORY + ACTIVITY DATA PACKAGED")


if __name__ == "__main__":
    main()
