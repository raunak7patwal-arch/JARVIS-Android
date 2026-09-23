#!/data/data/com.termux/files/usr/bin/bash

cd "$(dirname "$0")"

export PYTHONPATH="$PWD"

python jarvis/main.py
