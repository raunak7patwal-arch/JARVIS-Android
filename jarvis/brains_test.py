
import json
import requests

from jarvis.brain_server.response_engine import ResponseEngine


SERVER = "http://127.0.0.1:8000/ask"

response_engine = ResponseEngine()


def ask_jarvis(question):

    try:
        response = requests.post(
            SERVER,
            json={
                "text": question,
                "language": "auto"
            },
            timeout=60
        )

        if not response.ok:
            return "सर, Knowledge Brain से संपर्क नहीं हो पाया।"

        data = response.json()

        if not data.get("ok"):
            return "माफ कीजिए सर, मुझे इसका उत्तर नहीं मिला।"

        answer = data.get("answer", "")

        return response_engine.generate(
            question,
            answer
        )

    except requests.exceptions.ConnectionError:
        return (
            "सर, Knowledge Brain अभी online नहीं है। "
            "पहले brain server शुरू कीजिए।"
        )

    except Exception:
        return "सर, processing के दौरान समस्या आ गई।"


print()
print("======================================")
print("           JARVIS CORE")
print("======================================")
print("Knowledge Brain : ONLINE")
print("Response System : ONLINE")
print("Conversation     : ONLINE")
print()
print("JARVIS: System online. मैं आपकी सेवा के लिए तैयार हूँ, सर.")
print()

while True:

    try:
        question = input("You: ").strip()

        if not question:
            continue

        if question.lower() in [
            "exit",
            "quit",
            "shutdown",
            "बंद"
        ]:
            print()
            print("JARVIS: Certainly, sir. Shutting down.")
            break

        print()
        print("JARVIS:", ask_jarvis(question))
        print()

    except KeyboardInterrupt:
        print()
        print("JARVIS: Shutting down, sir.")
        break
