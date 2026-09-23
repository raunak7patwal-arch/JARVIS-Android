#!/usr/bin/env python3

import os
import re
import sys
import json
import time
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "central" / "data"

WIKIDATA_URL = "https://dumps.wikimedia.org/other/wikidata/latest/"

USER_AGENT = (
    "JARVIS-Central-Knowledge/1.0 "
    "(personal knowledge project)"
)


def request(url):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT
        }
    )

    return urllib.request.urlopen(
        req,
        timeout=60
    )


def find_latest_dump():
    print("Wikidata dump directory:")
    print(WIKIDATA_URL)

    with request(WIKIDATA_URL) as r:
        html = r.read().decode(
            "utf-8",
            errors="ignore"
        )

    files = re.findall(
        r'href="([^"]+\.json\.bz2)"',
        html
    )

    if not files:
        raise RuntimeError(
            "Latest Wikidata JSON dump नहीं मिला।"
        )

    # Prefer the complete dump.
    candidates = [
        x for x in files
        if "all" in x.lower()
    ]

    if not candidates:
        candidates = files

    filename = candidates[-1]

    return WIKIDATA_URL + filename, filename


def download(url, filename):
    DATA.mkdir(
        parents=True,
        exist_ok=True
    )

    target = DATA / filename

    if target.exists():
        print()
        print("Already downloaded:")
        print(target)
        return target

    print()
    print("SOURCE:")
    print(url)
    print()

    print("TARGET:")
    print(target)
    print()

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT
        }
    )

    with urllib.request.urlopen(
        req,
        timeout=120
    ) as response:

        total = response.headers.get(
            "Content-Length"
        )

        total = int(total) if total else 0

        downloaded = 0
        started = time.time()

        with open(target, "wb") as f:

            while True:

                chunk = response.read(
                    4 * 1024 * 1024
                )

                if not chunk:
                    break

                f.write(chunk)
                downloaded += len(chunk)

                elapsed = max(
                    time.time() - started,
                    0.001
                )

                speed = downloaded / elapsed

                if total:
                    percent = (
                        downloaded * 100 / total
                    )

                    print(
                        f"\r{percent:6.2f}% "
                        f"{downloaded/1024/1024/1024:.2f} GB "
                        f"{speed/1024/1024:.2f} MB/s",
                        end="",
                        flush=True
                    )
                else:
                    print(
                        f"\r"
                        f"{downloaded/1024/1024/1024:.2f} GB",
                        end="",
                        flush=True
                    )

    print()
    print()
    print("DOWNLOAD COMPLETE")
    print(target)

    return target


def save_manifest(url, filename):
    manifest = {
        "project": "JARVIS Central",
        "dataset": "Wikidata",
        "source": url,
        "filename": filename,
        "downloaded_at": time.strftime(
            "%Y-%m-%dT%H:%M:%SZ",
            time.gmtime()
        ),
        "status": "downloaded"
    }

    path = DATA / "manifest.json"

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            manifest,
            f,
            ensure_ascii=False,
            indent=2
        )

    print("Manifest saved:")
    print(path)


def main():

    print()
    print("======================================")
    print("     JARVIS WORLD DATA DOWNLOADER")
    print("======================================")
    print()

    if len(sys.argv) > 1:

        if sys.argv[1] == "find":

            url, filename = find_latest_dump()

            print()
            print("LATEST DUMP:")
            print(filename)
            print()
            print("URL:")
            print(url)

            return

        if sys.argv[1] == "download":

            url, filename = find_latest_dump()

            print()
            print("Latest dump found:")
            print(filename)

            target = download(
                url,
                filename
            )

            save_manifest(
                url,
                filename
            )

            return

    print("Commands:")
    print()
    print("  find")
    print("      Latest Wikidata dump खोजें")
    print()
    print("  download")
    print("      Latest dump download करें")
    print()
    print("IMPORTANT:")
    print("Full dump बहुत बड़ा हो सकता है.")
    print("इसे Android/Termux पर मत चलाना")
    print("जब तक यह CENTRAL SERVER की storage")
    print("न हो।")


if __name__ == "__main__":
    main()
