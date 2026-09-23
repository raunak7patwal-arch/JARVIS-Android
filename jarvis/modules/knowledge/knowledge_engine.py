import requests


class KnowledgeEngine:

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "JARVIS-Android/1.0"
        })

    def search(self, question):
        url = "https://en.wikipedia.org/w/api.php"

        params = {
            "action": "query",
            "list": "search",
            "srsearch": question,
            "format": "json",
            "utf8": 1,
            "srlimit": 3
        }

        try:
            response = self.session.get(
                url,
                params=params,
                timeout=10
            )

            response.raise_for_status()

            results = response.json().get(
                "query", {}
            ).get("search", [])

            if not results:
                return None

            return results[0].get("snippet")

        except Exception as e:
            print("Knowledge error:", e)
            return None

    def answer(self, question):
        result = self.search(question)

        if result:
            return result.replace(
                "<span class=\"searchmatch\">", ""
            ).replace("</span>", "")

        return "इस सवाल की जानकारी अभी नहीं मिली।"
