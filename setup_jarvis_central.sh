#!/data/data/com.termux/files/usr/bin/bash

set -e

ROOT="$HOME/JARVIS-Android/jarvis"

echo "======================================"
echo "       JARVIS CENTRAL CORE SETUP"
echo "======================================"

mkdir -p \
"$ROOT/central" \
"$ROOT/central/knowledge" \
"$ROOT/central/ai" \
"$ROOT/central/memory" \
"$ROOT/central/devices" \
"$ROOT/central/security" \
"$ROOT/agent"

touch \
"$ROOT/central/__init__.py" \
"$ROOT/central/knowledge/__init__.py" \
"$ROOT/central/ai/__init__.py" \
"$ROOT/central/memory/__init__.py" \
"$ROOT/central/devices/__init__.py" \
"$ROOT/central/security/__init__.py" \
"$ROOT/agent/__init__.py"

cat > "$ROOT/central/config.py" <<'PY'
HOST = "0.0.0.0"
PORT = 8787

# केवल पहले से paired/authorized devices
AUTHORIZED_DEVICES = {}

JARVIS_NAME = "JARVIS"
PY

cat > "$ROOT/central/knowledge/gateway.py" <<'PY'
import requests


class KnowledgeGateway:

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "JARVIS-Knowledge-Gateway/1.0"
        })

    def search(self, query, language="en"):
        """
        Heavy knowledge retrieval stays on the central server.
        The phone receives only the relevant result.
        """

        if not query.strip():
            return []

        results = []

        try:
            url = f"https://{language}.wikipedia.org/w/api.php"

            r = self.session.get(
                url,
                params={
                    "action": "query",
                    "list": "search",
                    "srsearch": query,
                    "srlimit": 8,
                    "format": "json"
                },
                timeout=15
            )

            if r.ok:
                for item in r.json().get(
                    "query", {}
                ).get("search", []):

                    results.append({
                        "source": "Wikimedia",
                        "title": item.get("title", ""),
                        "text": item.get("snippet", "")
                    })

        except Exception:
            pass

        return results
PY

cat > "$ROOT/central/ai/engine.py" <<'PY'
class AIEngine:

    def answer(self, question, evidence):
        """
        Reasoning layer.

        This deliberately does not contain hardcoded world facts.
        A real remote model can be connected here later.
        """

        if not evidence:
            return (
                "माफ कीजिए सर, मुझे इस सवाल के लिए "
                "विश्वसनीय जानकारी नहीं मिली।"
            )

        best = evidence[0]

        text = best.get("text", "").strip()

        if not text:
            return (
                "माफ कीजिए सर, मुझे पर्याप्त जानकारी नहीं मिली।"
            )

        # Temporary evidence fallback.
        # This will later be replaced by the central AI model.
        import re

        text = re.sub(r"<.*?>", "", text)

        return (
            "सर, उपलब्ध जानकारी के अनुसार "
            + text[:700]
        )
PY

cat > "$ROOT/central/devices/registry.py" <<'PY'
import secrets


class DeviceRegistry:

    def __init__(self):
        self.devices = {}

    def pair(self, device_name):
        token = secrets.token_urlsafe(32)

        self.devices[device_name] = {
            "token": token,
            "authorized": True
        }

        return token

    def authorize(self, device_name, token):
        device = self.devices.get(device_name)

        if not device:
            return False

        return (
            device["authorized"]
            and secrets.compare_digest(
                device["token"],
                token
            )
        )
PY

cat > "$ROOT/central/security/policy.py" <<'PY'
ALLOWED_ACTIONS = {
    "open_app",
    "open_url",
    "device_info",
    "ping",
    "notification"
}


def allowed(action):
    return action in ALLOWED_ACTIONS
PY

cat > "$ROOT/central/server.py" <<'PY'
import json
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

from jarvis.central.config import HOST, PORT
from jarvis.central.knowledge.gateway import KnowledgeGateway
from jarvis.central.ai.engine import AIEngine
from jarvis.central.devices.registry import DeviceRegistry
from jarvis.central.security.policy import allowed


knowledge = KnowledgeGateway()
ai = AIEngine()
devices = DeviceRegistry()


class Handler(BaseHTTPRequestHandler):

    def send_json(self, data, status=200):
        raw = json.dumps(
            data,
            ensure_ascii=False
        ).encode("utf-8")

        self.send_response(status)
        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )
        self.send_header(
            "Content-Length",
            str(len(raw))
        )
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):

        if self.path == "/health":
            self.send_json({
                "ok": True,
                "service": "JARVIS CENTRAL",
                "status": "ONLINE"
            })
            return

        self.send_json({
            "ok": False,
            "error": "Not found"
        }, 404)

    def do_POST(self):

        length = int(
            self.headers.get(
                "Content-Length",
                "0"
            )
        )

        try:
            body = json.loads(
                self.rfile.read(length)
            )
        except Exception:
            self.send_json({
                "ok": False,
                "error": "Invalid JSON"
            }, 400)
            return

        if self.path == "/ask":

            question = str(
                body.get("text", "")
            ).strip()

            if not question:
                self.send_json({
                    "ok": False,
                    "error": "Empty question"
                }, 400)
                return

            language = body.get(
                "language",
                "en"
            )

            evidence = knowledge.search(
                question,
                language
            )

            answer = ai.answer(
                question,
                evidence
            )

            self.send_json({
                "ok": True,
                "answer": answer,
                "evidence_count": len(evidence)
            })
            return

        if self.path == "/pair":

            device = str(
                body.get("device", "")
            ).strip()

            if not device:
                self.send_json({
                    "ok": False,
                    "error": "Device name required"
                }, 400)
                return

            token = devices.pair(device)

            self.send_json({
                "ok": True,
                "device": device,
                "token": token
            })
            return

        if self.path == "/command":

            device = body.get("device", "")
            token = body.get("token", "")
            action = body.get("action", "")

            if not devices.authorize(
                device,
                token
            ):
                self.send_json({
                    "ok": False,
                    "error": "Device not authorized"
                }, 403)
                return

            if not allowed(action):
                self.send_json({
                    "ok": False,
                    "error": "Action not permitted"
                }, 403)
                return

            self.send_json({
                "ok": True,
                "device": device,
                "action": action,
                "status": "AUTHORIZED"
            })
            return

        self.send_json({
            "ok": False,
            "error": "Unknown endpoint"
        }, 404)


def main():

    print()
    print("======================================")
    print("          JARVIS CENTRAL")
    print("======================================")
    print("Knowledge Gateway : ONLINE")
    print("AI Engine         : ONLINE")
    print("Device Registry   : ONLINE")
    print("Security Policy   : ONLINE")
    print(f"Port              : {PORT}")
    print()
    print("Waiting for JARVIS requests...")
    print()

    server = ThreadingHTTPServer(
        (HOST, PORT),
        Handler
    )

    server.serve_forever()


if __name__ == "__main__":
    main()
PY

cat > "$ROOT/agent/client.py" <<'PY'
import requests


class JarvisAgent:

    def __init__(self, server):
        self.server = server.rstrip("/")

    def ask(self, text):
        response = requests.post(
            self.server + "/ask",
            json={
                "text": text,
                "language": "auto"
            },
            timeout=60
        )

        response.raise_for_status()

        data = response.json()

        return data.get(
            "answer",
            "माफ कीजिए सर, उत्तर नहीं मिला।"
        )
PY

cat > "$ROOT/central/__init__.py" <<'PY'
PY

echo
echo "======================================"
echo "        JARVIS CORE CREATED"
echo "======================================"
echo
echo "Folders : CREATED"
echo "Central : CREATED"
echo "Agent   : CREATED"
echo "Security policy : CREATED"
echo
echo "Next:"
echo "python jarvis/central/server.py"
