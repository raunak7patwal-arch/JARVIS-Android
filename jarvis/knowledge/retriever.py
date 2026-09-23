import json
import os


class KnowledgeRetriever:

    def __init__(self):
        path = os.path.join(
            os.path.dirname(__file__),
            "database.json"
        )

        self.data = {}

        if not os.path.exists(path):
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read().strip()

            if content:
                self.data = json.loads(content)

        except (json.JSONDecodeError, OSError):
            self.data = {}

    def search(self, question):
        q = question.lower().strip()

        for country, info in self.data.items():

            if country.lower() not in q:
                continue

            if "राजधानी" in q or "capital" in q:
                return f"{country} की राजधानी {info.get('राजधानी', 'उपलब्ध नहीं')} है।"

            if "मुद्रा" in q or "currency" in q:
                return f"{country} की मुद्रा {info.get('मुद्रा', 'उपलब्ध नहीं')} है।"

            if "महाद्वीप" in q or "continent" in q:
                return f"{country} {info.get('महाद्वीप', 'उपलब्ध नहीं')} में स्थित है।"

        return None
