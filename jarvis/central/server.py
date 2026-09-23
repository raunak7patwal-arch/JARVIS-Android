import json
from http.server import (
    ThreadingHTTPServer,
    BaseHTTPRequestHandler
)

from jarvis.central.config import HOST, PORT
from jarvis.central.knowledge.gateway import KnowledgeGateway
from jarvis.central.ai.engine import AIEngine
from jarvis.central.devices.registry import DeviceRegistry
from jarvis.central.security.policy import allowed


knowledge = KnowledgeGateway()
ai = AIEngine()
devices = DeviceRegistry()


class Handler(BaseHTTPRequestHandler):

    server_version = "JARVIS-CENTRAL/1.0"

    def log_message(
        self,
        format,
        *args
    ):

        print(
            "[JARVIS]",
            format % args
        )

    def send_json(
        self,
        data,
        status=200
    ):

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

        self.send_header(
            "Cache-Control",
            "no-store"
        )

        self.end_headers()

        self.wfile.write(raw)

    def read_json(self):

        try:

            length = int(
                self.headers.get(
                    "Content-Length",
                    "0"
                )
            )

            if length <= 0:
                return None

            raw = self.rfile.read(
                length
            )

            return json.loads(
                raw.decode("utf-8")
            )

        except Exception:

            return None

    def do_GET(self):

        if self.path == "/":

            self.send_json({
                "ok": True,
                "service": "JARVIS CENTRAL",
                "version": "1.0",
                "status": "ONLINE"
            })

            return

        if self.path == "/health":

            self.send_json({
                "ok": True,
                "service": "JARVIS CENTRAL",
                "status": "ONLINE",
                "ai": "ONLINE",
                "memory": "ONLINE",
                "conversation": "ONLINE",
                "knowledge": "ONLINE",
                "security": "ONLINE"
            })

            return

        if self.path == "/memory":

            self.send_json({
                "ok": True,
                "memory": ai.memory.recent(
                    limit=20
                )
            })

            return

        if self.path == "/conversation":

            self.send_json({
                "ok": True,
                "conversation":
                    ai.conversation.recent(
                        limit=20
                    )
            })

            return

        self.send_json(
            {
                "ok": False,
                "error": "Not found"
            },
            404
        )

    def do_POST(self):

        body = self.read_json()

        if body is None:

            self.send_json(
                {
                    "ok": False,
                    "error": "Invalid JSON"
                },
                400
            )

            return

        if self.path == "/ask":

            question = str(
                body.get("question", body.get("text", ""))
            ).strip()

            language = str(
                body.get("language", "auto")
            ).strip()

            if not question:
                self.send_json(
                    {
                        "ok": False,
                        "error": "Empty question"
                    },
                    400
                )
                return

            try:
                # One AIEngine call only.
                # AIEngine itself decides whether the request
                # can be answered instantly or needs Gemini.
                result = ai.answer(
                    question,
                    []
                )

                answer = result.get(
                    "answer",
                    ""
                )

                command = result.get(
                    "command"
                ) or {
                    "is_command": False,
                    "action": None,
                    "parameters": {},
                    "text": question
                }

                if not isinstance(command, dict):
                    command = {
                        "is_command": False,
                        "action": None,
                        "parameters": {},
                        "text": question
                    }

                if not isinstance(
                    command.get("parameters"),
                    dict
                ):
                    command["parameters"] = {}

                self.send_json(
                    {
                        "ok": True,
                        "answer": answer,
                        "cached": result.get(
                            "cached",
                            False
                        ),
                        "command": command,
                        "evidence_count": 0
                    }
                )

            except Exception as e:

                print(
                    "ASK ERROR:",
                    repr(e)
                )

                self.send_json(
                    {
                        "ok": False,
                        "error": "Internal AI error"
                    },
                    500
                )

            return

        if self.path == "/remember":

            text = str(
                body.get(
                    "text",
                    ""
                )
            ).strip()

            category = str(
                body.get(
                    "category",
                    "general"
                )
            ).strip()

            if not text:

                self.send_json(
                    {
                        "ok": False,
                        "error":
                            "Memory text required"
                    },
                    400
                )

                return

            saved = ai.memory.remember(
                text,
                category
            )

            self.send_json({
                "ok": saved,
                "saved": saved
            })

            return

        if self.path == "/memory/clear":

            ai.memory.clear()

            self.send_json({
                "ok": True,
                "cleared": True
            })

            return

        if self.path == "/conversation/clear":

            ai.conversation.clear()

            self.send_json({
                "ok": True,
                "cleared": True
            })

            return

        if self.path == "/pair":

            device = str(
                body.get(
                    "device",
                    ""
                )
            ).strip()

            if not device:

                self.send_json(
                    {
                        "ok": False,
                        "error":
                            "Device name required"
                    },
                    400
                )

                return

            token = devices.pair(
                device
            )

            self.send_json({
                "ok": True,
                "device": device,
                "token": token
            })

            return

        if self.path == "/command":

            device = str(
                body.get(
                    "device",
                    ""
                )
            ).strip()

            token = str(
                body.get(
                    "token",
                    ""
                )
            ).strip()

            action = str(
                body.get(
                    "action",
                    ""
                )
            ).strip()

            if not devices.authorize(
                device,
                token
            ):

                self.send_json(
                    {
                        "ok": False,
                        "error":
                            "Device not authorized"
                    },
                    403
                )

                return

            if not allowed(action):

                self.send_json(
                    {
                        "ok": False,
                        "error":
                            "Action not permitted"
                    },
                    403
                )

                return

            self.send_json({
                "ok": True,
                "device": device,
                "action": action,
                "status": "AUTHORIZED"
            })

            return

        self.send_json(
            {
                "ok": False,
                "error": "Unknown endpoint"
            },
            404
        )


def main():

    print()
    print("======================================")
    print("          JARVIS CENTRAL")
    print("======================================")
    print("Knowledge Gateway : ONLINE")
    print("AI Engine         : ONLINE")
    print("Memory System     : ONLINE")
    print("Conversation       : ONLINE")
    print("Command Router    : ONLINE")
    print("Device Registry   : ONLINE")
    print("Security Policy   : ONLINE")
    print(f"Port              : {PORT}")
    print()
    print("JARVIS Central Brain ready.")
    print("Waiting for requests...")
    print()

    server = ThreadingHTTPServer(
        (HOST, PORT),
        Handler
    )

    try:
        server.serve_forever()

    except KeyboardInterrupt:

        print(
            "\nJARVIS Central shutting down..."
        )

    finally:

        server.server_close()


if __name__ == "__main__":
    main()
