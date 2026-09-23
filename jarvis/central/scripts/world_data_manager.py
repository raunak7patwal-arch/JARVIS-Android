#!/usr/bin/env python3

import os
import sys
import json
import shutil
import hashlib
import subprocess
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "central" / "data"
INDEX = ROOT / "central" / "index"

DATA.mkdir(parents=True, exist_ok=True)
INDEX.mkdir(parents=True, exist_ok=True)


SOURCES = {
    "wikidata": {
        "name": "Wikidata structured knowledge",
        "type": "external",
        "info": "https://dumps.wikimedia.org/other/wikidata/"
    },

    "wikimedia": {
        "name": "Wikimedia public datasets",
        "type": "external",
        "info": "https://dumps.wikimedia.org/"
    }
}


def human_size(n):
    units = ["B", "KB", "MB", "GB", "TB"]
    n = float(n)

    for unit in units:
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024

    return f"{n:.1f} PB"


def disk_info():
    total, used, free = shutil.disk_usage(DATA)

    print()
    print("======================================")
    print("       JARVIS CENTRAL STORAGE")
    print("======================================")
    print("Total :", human_size(total))
    print("Used  :", human_size(used))
    print("Free  :", human_size(free))
    print()


def download(url, output):
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)

    print()
    print("Downloading:")
    print(url)
    print()
    print("Target:")
    print(output)
    print()

    req = Request(
        url,
        headers={
            "User-Agent": "JARVIS-Central-DataManager/1.0"
        }
    )

    with urlopen(req, timeout=60) as response:
        total = response.headers.get("Content-Length")

        if total:
            total = int(total)
            print("Expected:", human_size(total))

        with open(output, "wb") as f:
            while True:
                chunk = response.read(1024 * 1024)

                if not chunk:
                    break

                f.write(chunk)

    print()
    print("Download complete.")
    print("Size:", human_size(output.stat().st_size))


def sha256(path):
    h = hashlib.sha256()

    with open(path, "rb") as f:
        while True:
            block = f.read(1024 * 1024)

            if not block:
                break

            h.update(block)

    return h.hexdigest()


def save_manifest():
    manifest = {
        "project": "JARVIS Central Knowledge",
        "purpose": "Large world-knowledge storage",
        "datasets": SOURCES
    }

    path = INDEX / "datasets.json"

    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            manifest,
            f,
            ensure_ascii=False,
            indent=2
        )

    print("Manifest:", path)


def status():
    disk_info()

    print("Datasets:")
    print()

    for item in DATA.rglob("*"):
        if item.is_file():
            print(
                f"{item.relative_to(DATA)}"
                f"  ->  {human_size(item.stat().st_size)}"
            )


def main():
    if len(sys.argv) < 2:
        print("""
JARVIS World Data Manager

Commands:

  status
      Show storage and downloaded datasets.

  manifest
      Create dataset manifest.

  download-info
      Show official dataset sources.

  hash FILE
      Calculate SHA256.

Examples:

  python world_data_manager.py status
  python world_data_manager.py manifest
  python world_data_manager.py download-info
""")
        return

    command = sys.argv[1]

    if command == "status":
        status()

    elif command == "manifest":
        save_manifest()

    elif command == "download-info":

        print()
        print("WIKIDATA")
        print(SOURCES["wikidata"]["info"])

        print()
        print("WIKIMEDIA DUMPS")
        print(SOURCES["wikimedia"]["info"])

        print()
        print("These datasets must be stored on the")
        print("JARVIS CENTRAL server, not on the Android phone.")

    elif command == "hash":

        if len(sys.argv) < 3:
            print("FILE required")
            return

        path = Path(sys.argv[2])

        if not path.exists():
            print("File not found:", path)
            return

        print(sha256(path))

    else:
        print("Unknown command:", command)


if __name__ == "__main__":
    main()
