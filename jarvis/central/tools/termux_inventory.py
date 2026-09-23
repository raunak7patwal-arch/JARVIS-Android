from __future__ import annotations

import json
import shutil
import subprocess
import time
from pathlib import Path


OUTPUT = Path("jarvis/central/tools/termux_tools.json")


SAFE_COMMANDS = [
    "python",
    "python3",
    "pip",
    "pip3",
    "git",
    "curl",
    "wget",
    "ssh",
    "openssl",
    "ping",
    "nslookup",
    "dig",
    "traceroute",
    "ip",
    "ss",
    "netstat",
    "grep",
    "awk",
    "sed",
    "jq",
    "tar",
    "zip",
    "unzip",
    "sqlite3",
    "node",
    "npm",
]


def version(command: str) -> str:
    path = shutil.which(command)

    if not path:
        return ""

    try:
        result = subprocess.run(
            [command, "--version"],
            capture_output=True,
            text=True,
            timeout=3,
        )

        output = (
            result.stdout.strip()
            or result.stderr.strip()
        )

        return output.splitlines()[0][:300] if output else ""

    except Exception:
        return ""


def scan():
    tools = []

    for command in SAFE_COMMANDS:
        path = shutil.which(command)

        if not path:
            continue

        tools.append({
            "name": command,
            "path": path,
            "version": version(command),
        })

    data = {
        "generated_at": int(time.time()),
        "environment": "Termux",
        "tool_count": len(tools),
        "tools": tools,
    }

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT.write_text(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    return data


if __name__ == "__main__":
    data = scan()

    print("======================================")
    print("JARVIS TERMUX TOOL INVENTORY")
    print("======================================")
    print(f"Tools detected : {data['tool_count']}")

    for tool in data["tools"]:
        print(
            f"- {tool['name']} : "
            f"{tool['version'] or 'available'}"
        )

    print()
    print(f"Saved to : {OUTPUT}")
    print("INSTALL/EXPLOIT AUTOMATION : DISABLED")
    print("SUCCESS")
