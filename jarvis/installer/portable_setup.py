#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
import time
from pathlib import Path


APP_NAME = "JARVIS"
PACKAGE_VERSION = "1.0"
ROOT = Path(__file__).resolve().parents[2]
PACKAGE_DIR = ROOT / "JARVIS-PORTABLE"
MANIFEST = PACKAGE_DIR / "manifest.json"
SETUP_SCRIPT = PACKAGE_DIR / "SETUP-JARVIS.sh"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def collect_files():
    files = []

    for folder in (
        ROOT / "jarvis",
        ROOT / "app",
    ):
        if not folder.exists():
            continue

        for p in folder.rglob("*"):
            if not p.is_file():
                continue

            if any(
                part in {
                    ".gradle",
                    "build",
                    ".git",
                    "__pycache__",
                }
                for part in p.parts
            ):
                continue

            # Never put secrets into a portable package.
            if p.name in {
                "api.env",
                "credentials.json",
                "token.json",
                "memory.json",
                "advanced_memory.json",
            }:
                continue

            files.append(p)

    return files


def build_package():
    if PACKAGE_DIR.exists():
        shutil.rmtree(PACKAGE_DIR)

    source = PACKAGE_DIR / "JARVIS"
    source.mkdir(parents=True)

    copied = []

    for file in collect_files():
        relative = file.relative_to(ROOT)
        destination = source / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file, destination)

        copied.append({
            "path": str(relative),
            "sha256": sha256(destination),
            "size": destination.stat().st_size,
        })

    manifest = {
        "name": APP_NAME,
        "version": PACKAGE_VERSION,
        "format": "portable-setup",
        "created_at": int(time.time()),
        "files": copied,
        "security": {
            "secrets_included": False,
            "silent_install": False,
            "permission_bypass": False,
            "user_confirmation_required": True,
        },
    }

    MANIFEST.write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )

    SETUP_SCRIPT.write_text(
        """#!/data/data/com.termux/files/usr/bin/bash
set -e

BASE="$(cd "$(dirname "$0")" && pwd)"
JARVIS="$BASE/JARVIS"

echo
echo "======================================"
echo "          JARVIS PORTABLE SETUP"
echo "======================================"
echo
echo "JARVIS files detected."
echo
echo "This setup will NOT silently install apps"
echo "or bypass Android permissions."
echo "Android will ask for required permissions"
echo "when the application is installed."
echo

read -r -p "Continue with JARVIS setup? [y/N]: " ANSWER

case "$ANSWER" in
    y|Y)
        ;;
    *)
        echo "Setup cancelled."
        exit 0
        ;;
esac

if [ ! -d "$JARVIS" ]; then
    echo "ERROR: JARVIS package is missing."
    exit 1
fi

echo
echo "[1/3] Checking package..."

if [ ! -f "$BASE/manifest.json" ]; then
    echo "ERROR: manifest.json missing."
    exit 1
fi

echo "Package OK."

echo
echo "[2/3] Preparing JARVIS configuration..."

mkdir -p "$HOME/.jarvis"

cat > "$HOME/.jarvis/setup.json" <<EOF
{
  "name": "JARVIS",
  "version": "1.0",
  "portable_setup": true,
  "user_confirmed": true
}
EOF

echo "Configuration prepared."

echo
echo "[3/3] Setup complete."

echo
echo "======================================"
echo "       JARVIS SETUP READY"
echo "======================================"
echo
echo "Next step:"
echo "Install the Android application normally"
echo "and grant only the permissions you approve."
echo
""",
        encoding="utf-8",
    )

    SETUP_SCRIPT.chmod(0o755)

    readme = PACKAGE_DIR / "README.txt"
    readme.write_text(
        """JARVIS Portable Setup
======================

This folder is designed to be copied to a USB/Pendrive.

Important:
- It does not bypass Android security.
- It does not silently install an application.
- The Android user must approve installation and permissions.
- API keys and private credentials are intentionally excluded.
- The same package can be copied to another computer/Termux environment.

Main setup file:
SETUP-JARVIS.sh
""",
        encoding="utf-8",
    )

    print("SUCCESS")
    print(f"Package: {PACKAGE_DIR}")
    print(f"Files: {len(copied)}")


if __name__ == "__main__":
    build_package()
