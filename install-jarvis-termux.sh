#!/data/data/com.termux/files/usr/bin/bash

set -e

echo "======================================"
echo "        JARVIS ONE-CODE INSTALLER"
echo "======================================"

PROJECT="$HOME/JARVIS-Android"
REPO="https://github.com/raunak7patwal-arch/JARVIS-Android.git"

echo "[1/7] Checking Termux..."

if [ ! -d "$PREFIX" ]; then
    echo "ERROR: This installer must run inside Termux."
    exit 1
fi

echo "Termux : OK"

echo "[2/7] Installing basic dependencies..."

pkg update -y
pkg install -y git python curl wget openssl

echo "Dependencies : OK"

echo "[3/7] Preparing JARVIS..."

if [ -d "$PROJECT/.git" ]; then
    echo "Existing JARVIS repository found."
    cd "$PROJECT"
    git pull --ff-only || true
else
    if [ -d "$PROJECT" ]; then
        mv "$PROJECT" "${PROJECT}-backup-$(date +%Y%m%d-%H%M%S)"
    fi

    git clone "$REPO" "$PROJECT"
    cd "$PROJECT"
fi

echo "JARVIS source : READY"

echo "[4/7] Preparing Termux storage..."

if command -v termux-setup-storage >/dev/null 2>&1; then
    termux-setup-storage || true
fi

echo "Storage permission request sent if required."

echo "[5/7] Preparing Python environment..."


if [ -f requirements.txt ]; then
    pip install -r requirements.txt
fi

echo "Python environment : READY"

echo "[6/7] Checking JARVIS..."

PYTHONPATH="$PROJECT" python -m py_compile \
    $(find jarvis -name "*.py" -type f)

echo "Python syntax : OK"

echo "[7/7] Creating launcher..."

mkdir -p "$HOME/bin"

cat > "$HOME/bin/jarvis" <<'RUN'
#!/data/data/com.termux/files/usr/bin/bash

PROJECT="$HOME/JARVIS-Android"

cd "$PROJECT" || exit 1

if pgrep -f "python -m jarvis.central.server" >/dev/null 2>&1; then
    echo "JARVIS is already running."
    exit 0
fi

echo "Starting JARVIS Central..."

PYTHONPATH="$PROJECT" \
nohup python -m jarvis.central.server \
    >> "$PROJECT/jarvis-central.log" 2>&1 &

sleep 2

if pgrep -f "python -m jarvis.central.server" >/dev/null 2>&1; then
    echo "JARVIS : ONLINE"
    echo "Port   : 8787"
else
    echo "JARVIS failed to start."
    echo "Check:"
    echo "$PROJECT/jarvis-central.log"
    exit 1
fi
RUN

chmod +x "$HOME/bin/jarvis"

echo ""
echo "======================================"
echo "       JARVIS INSTALLATION READY"
echo "======================================"
echo "Project : $PROJECT"
echo "Launcher: $HOME/bin/jarvis"
echo ""
echo "Starting JARVIS..."
echo "======================================"

"$HOME/bin/jarvis"
