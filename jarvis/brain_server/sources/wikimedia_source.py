import requests
import re
import html


class WikimediaSource:

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "JARVIS-Knowledge-Brain/1.0"
        })

    def search(self, query, language="en"):

        # Hindi queries को पहले English search
        # में भी try करेंगे ताकि multilingual
        # knowledge retrieval बेहतर हो।
        queries = [query]

        if language.startswith("hi"):
            queries.append(
                self._roman_to_english_hint(query)
            )

        results = []

        for q in queries:

            if not q:
                continue

            try:

                response = self.session.get(
                    f"https://{language}.wikipedia.org/w/api.php",
                    params={
                        "action": "query",
                        "list": "search",
                        "srsearch": q,
                        "srlimit": 10,
                        "format": "json"
                    },
                    timeout=15
                )

                if not response.ok:
                    continue

                data = response.json()

                for item in data.get(
                    "query", {}
                ).get("search", []):

                    title = item.get(
                        "title",
                        ""
                    )

                    snippet = item.get(
                        "snippet",
                        ""
                    )

                    snippet = re.sub(
                        r"<.*?>",
                        "",
                        snippet
                    )

                    snippet = html.unescape(
                        snippet
                    )

                    if title:

                        results.append({
                            "source": "Wikimedia",
                            "title": title,
                            "text": snippet,
                            "search_query": q
                        })

            except Exception:
                continue

        return self._unique(results)

    def _roman_to_english_hint(self, query):

        replacements = {
            "bharat": "India",
            "india": "India",
            "rajdhani": "capital",
            "kya": "",
            "hai": "",
            "kaun": "who",
            "kahan": "where",
            "kab": "when",
            "kyun": "why",
            "kaise": "how",
            "minister": "minister",
            "pradhanmantri": "prime minister",
            "rashtrapati": "president"
        }

        words = query.lower().split()

        output = []

        for word in words:

            replacement = replacements.get(
                word,
                word
            )

            if replacement:
                output.append(replacement)

        return " ".join(output)

    def _unique(self, results):

        seen = set()
        output = []

        for item in results:

            key = (
                item.get("source"),
                item.get("title")
            )

            if key in seen:
                continue

            seen.add(key)
            output.append(item)

        return output
