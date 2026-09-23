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
