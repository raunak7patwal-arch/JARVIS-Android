from __future__ import annotations

import json
import shutil
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PORTABLE = ROOT / "JARVIS-PORTABLE"
ANDROID = PORTABLE / "ANDROID"
SOURCE_APK = ROOT / "app" / "build" / "outputs" / "apk" / "debug" / "app-debug.apk"


def run(cmd):
    return subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )


def build_apk():
    print("[1/4] Building JARVIS Android package...")
    result = run(["gradle", ":app:assembleDebug", "--no-daemon"])

    if result.returncode != 0:
        print(result.stdout)
        raise SystemExit("APK_BUILD_FAILED")

    if not SOURCE_APK.exists():
        raise SystemExit("APK_NOT_FOUND")


def create_installer():
    print("[2/4] Preparing portable installer...")

    if ANDROID.exists():
        shutil.rmtree(ANDROID)

    ANDROID.mkdir(parents=True)

    apk = ANDROID / "JARVIS.apk"
    shutil.copy2(SOURCE_APK, apk)

    installer = ANDROID / "INSTALL-JARVIS.sh"

    installer.write_text(
        """#!/data/data/com.termux/files/usr/bin/bash
set -e

BASE="$(cd "$(dirname "$0")" && pwd)"
APK="$BASE/JARVIS.apk"

echo
echo "=========================================="
echo "          JARVIS ANDROID INSTALLER"
echo "=========================================="
echo

if [ ! -f "$APK" ]; then
    echo "ERROR: JARVIS.apk not found."
    exit 1
fi

echo "JARVIS package found."
echo
echo "Android security requires the device owner"
echo "to approve the installation."
echo

if command -v termux-open >/dev/null 2>&1; then
    echo "Opening Android installer..."
    termux-open "$APK"
    echo
    echo "Approve the installation on the phone."
else
    echo "Termux API launcher is not available."
    echo
    echo "Open this file manually:"
    echo "$APK"
fi

echo
echo "After installation:"
echo "1. Open JARVIS."
echo "2. Enter the Central Server address."
echo "3. Grant only the permissions you approve."
echo "4. Complete JARVIS first-run setup."
echo
echo "JARVIS INSTALLER READY."
""",
        encoding="utf-8",
    )

    installer.chmod(0o755)


def create_manifest():
    print("[3/4] Creating release manifest...")

    manifest = {
        "name": "JARVIS",
        "package": "com.jarvis.assistant",
        "version": "1.0",
        "type": "portable-android-installer",
        "created_at": int(time.time()),
        "installer": "ANDROID/INSTALL-JARVIS.sh",
        "android_package": "ANDROID/JARVIS.apk",
        "security": {
            "silent_install": False,
            "permission_bypass": False,
            "user_confirmation_required": True,
        },
    }

    (PORTABLE / "INSTALL-MANIFEST.json").write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )


def create_readme():
    print("[4/4] Creating portable instructions...")

    (PORTABLE / "PENDRIVE-INSTALL.txt").write_text(
        """JARVIS Portable Android Package
=================================

1. Copy the complete JARVIS-PORTABLE folder to a Pendrive.
2. Copy it to the target Android device.
3. Open:
   ANDROID/INSTALL-JARVIS.sh

4. Android will show its normal installation confirmation.
5. Approve installation.
6. Open JARVIS.
7. Configure the Central Server.
8. Grant the permissions you choose.

IMPORTANT
---------
Android security is intentionally respected.
This package does not silently install applications,
bypass permissions, or disable device security.

The package is portable and can be copied to another
compatible Android device.
""",
        encoding="utf-8",
    )


def main():
    build_apk()
    create_installer()
    create_manifest()
    create_readme()

    print()
    print("==========================================")
    print("       JARVIS PORTABLE PACKAGE READY")
    print("==========================================")
    print()
    print("SUCCESS")
    print(f"Package: {PORTABLE}")
    print(f"APK:     {ANDROID / 'JARVIS.apk'}")


if __name__ == "__main__":
    main()
