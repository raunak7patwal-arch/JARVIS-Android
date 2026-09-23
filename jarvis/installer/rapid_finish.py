from pathlib import Path
import os
import json
import py_compile
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]

print("=" * 46)
print("        JARVIS RAPID FINISH PATCH")
print("=" * 46)

# 1. Cybersecurity token hook
env_dir = Path.home() / ".config" / "jarvis"
env_dir.mkdir(parents=True, exist_ok=True)
env_file = env_dir / "env.sh"

if not env_file.exists():
    env_file.write_text(
        "# JARVIS environment configuration\n"
        "# Never commit real tokens to GitHub.\n"
        "export CYBER_API_TOKEN=\"${CYBER_API_TOKEN:-}\"\n",
        encoding="utf-8",
    )
env_file.chmod(0o600)

# 2. Verify existing security modules
required = [
    ROOT / "jarvis/central/security/persistent_vault.py",
    ROOT / "jarvis/central/security/persistence.py",
    ROOT / "jarvis/central/security/policy.py",
    ROOT / "jarvis/central/security/request_guard.py",
    ROOT / "jarvis/central/security/command_guard.py",
    ROOT / "jarvis/central/ai/engine.py",
    ROOT / "jarvis/central/ai/gemini.py",
    ROOT / "jarvis/central/commands/router.py",
    ROOT / "jarvis/installer/jarvis_transfer.py",
]

missing = [str(p.relative_to(ROOT)) for p in required if not p.exists()]
if missing:
    print("MISSING FILES:")
    for item in missing:
        print(" -", item)
    raise SystemExit(1)

print("[1/4] Core modules : OK")

# 3. Compile all project Python files
errors = []
for path in (ROOT / "jarvis").rglob("*.py"):
    if "__pycache__" in path.parts:
        continue
    try:
        py_compile.compile(str(path), doraise=True)
    except Exception as exc:
        errors.append((str(path.relative_to(ROOT)), str(exc)))

if errors:
    print("[2/4] Python syntax : FAILED")
    for path, err in errors[:20]:
        print(path, "->", err)
    raise SystemExit(1)

print("[2/4] Python syntax : OK")

# 4. Verify persistence state
try:
    sys.path.insert(0, str(ROOT))
    from jarvis.central.security.persistence import JARVISPersistence

    p = JARVISPersistence()
    status = p.status()
    print("[3/4] Persistence :", status)

    if not status.get("persistent"):
        raise RuntimeError("Persistent storage is not enabled")

    if not status.get("master_configured"):
        raise RuntimeError("Master password is not configured")

except Exception as exc:
    print("[3/4] Persistence : FAILED")
    print(type(exc).__name__, exc)
    raise SystemExit(1)

# 5. Verify transfer package
transfer = ROOT / "JARVIS-SECURE-TRANSFER"
if transfer.exists():
    manifest = transfer / "manifest.json"
    if manifest.exists():
        data = json.loads(manifest.read_text(encoding="utf-8"))
        print("[4/4] Secure transfer : READY")
        print("       Files :", len(data.get("files", {})))
    else:
        print("[4/4] Secure transfer : PACKAGE EXISTS / MANIFEST MISSING")
else:
    print("[4/4] Secure transfer : NOT PRESENT")

print("=" * 46)
print("JARVIS RAPID FINISH PATCH : PASS")
print("=" * 46)
