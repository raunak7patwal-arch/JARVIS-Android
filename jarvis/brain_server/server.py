from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import requests
import re
import html
from jarvis.brain_server.query_engine import QueryEngine
from jarvis.brain_server.reasoning_engine import ReasoningEngine
from jarvis.brain_server.sources.wikimedia_source import WikimediaSource


HOST = "0.0.0.0"
PORT = 8000


class KnowledgeBrain:

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "JARVIS-Knowledge-Brain/1.0"
        })

    def search_wikimedia(self, query, lang="en"):
        try:
            url = f"https://{lang}.wikipedia.org/w/api.php"

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

            if not r.ok:
                return []

            items = r.json().get(
                "query", {}
            ).get("search", [])

            results = []

            for item in items:
                title = item.get("title", "")
                snippet = item.get("snippet", "")

                snippet = re.sub(
                    r"<.*?>",
                    "",
                    snippet
                )

                snippet = html.unescape(snippet)

                if title and snippet:
                    results.append({
                        "source": "Wikimedia",
                        "title": title,
                        "text": snippet
                    })

            return results

        except Exception as e:
            print("Wikimedia error:", e)
            return []

    def get_wikipedia_page(self, title, lang="en"):
        try:
            encoded = requests.utils.quote(
                title,
                safe=""
            )

            url = (
                f"https://{lang}.wikipedia.org"
                f"/api/rest_v1/page/summary/{encoded}"
            )

            r = self.session.get(
                url,
                timeout=15
            )

            if not r.ok:
                return None

            data = r.json()

            extract = data.get("extract")

            if not extract:
                return None

            return {
                "source": "Wikimedia",
                "title": data.get("title", title),
                "text": extract[:6000]
            }

        except Exception:
            return None

    def search_wikidata(self, query):
        try:
            r = self.session.get(
                "https://www.wikidata.org/w/api.php",
                params={
                    "action": "wbsearchentities",
                    "search": query,
                    "language": "en",
                    "uselang": "en",
                    "format": "json",
                    "limit": 8
                },
                timeout=15
            )

            if not r.ok:
                return []

            results = []

            for item in r.json().get("search", []):

                label = item.get("label")
                description = item.get("description")
                entity = item.get("id")

                if label:
                    results.append({
                        "source": "Wikidata",
                        "title": label,
                        "entity": entity,
                        "text": description or label
                    })

            return results

        except Exception as e:
            print("Wikidata error:", e)
            return []

    def search(self, query, language="en"):

        return wikimedia_source.search(
            query,
            language
        )


brain = KnowledgeBrain()
query_engine = QueryEngine()
reasoning_engine = ReasoningEngine()
wikimedia_source = WikimediaSource()


def clean_query(text):

    text = text.strip()

    text = re.sub(
        r"\b(jarvis|जार्विस)\b",
        "",
        text,
        flags=re.IGNORECASE
    )

    return " ".join(text.split())


class JarvisHandler(BaseHTTPRequestHandler):

    def send_json(self, data, status=200):

        body = json.dumps(
            data,
            ensure_ascii=False,
            indent=2
        ).encode("utf-8")

        self.send_response(status)

        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )

        self.send_header(
            "Content-Length",
            str(len(body))
        )

        self.end_headers()

        self.wfile.write(body)

    def do_GET(self):

        if self.path == "/health":

            self.send_json({
                "status": "online",
                "brain": "knowledge"
            })

            return

        if self.path == "/":

            self.send_json({
                "system": "JARVIS Knowledge Brain",
                "status": "online"
            })

            return

        self.send_json({
            "error": "Not found"
        }, 404)

    def do_POST(self):

        if self.path != "/ask":

            self.send_json({
                "error": "Not found"
            }, 404)

            return

        try:

            length = int(
                self.headers.get(
                    "Content-Length",
                    0
                )
            )

            raw = self.rfile.read(length)

            data = json.loads(
                raw.decode("utf-8")
            )

            question = str(
                data.get("text", "")
            ).strip()

            language = str(
                data.get("language", "auto")
            )

            if not question:

                self.send_json({
                    "ok": False,
                    "error": "Question is empty"
                }, 400)

                return

            query = clean_query(question)

            analysis = query_engine.analyze(query)

            print()
            print("================================")
            print("JARVIS QUERY:", query)
            print("NORMALIZED:", analysis["normalized"])
            print("SEARCH QUERIES:", analysis["queries"])
            print("================================")

            all_results = []

            for search_query in analysis["queries"]:
                all_results.extend(
                    brain.search(search_query, language)
                )

            unique = {}

            for item in all_results:
                key = (
                    item.get("source"),
                    item.get("title")
                )

                if key not in unique:
                    unique[key] = item

            results = list(unique.values())[:10]

            reasoning = reasoning_engine.process(
                query,
                results,
                language
            )

            # Use the reasoning engine's ranked evidence
            ranked_results = reasoning.get(
                "ranked_results",
                results
            )

            self.send_json({
                "ok": True,
                "query": query,
                "language": language,
                "count": len(ranked_results),
                "answer": reasoning["fallback"],
                "reasoning_prompt": reasoning["prompt"],
                "results": ranked_results
            })

        except Exception as e:

            self.send_json({
                "ok": False,
                "error": str(e)
            }, 500)


def main():

    server = ThreadingHTTPServer(
        (HOST, PORT),
        JarvisHandler
    )

    print()
    print("================================")
    print("     JARVIS KNOWLEDGE BRAIN")
    print("================================")
    print("Status : ONLINE")
    print("Port   :", PORT)
    print()
    print("Evidence Engine : ONLINE")
    print("Wikimedia       : CONNECTED")
    print("Wikidata        : CONNECTED")
    print()
    print("Waiting for questions...")
    print("Press CTRL+C to stop.")
    print()

    try:
        server.serve_forever()

    except KeyboardInterrupt:

        print()
        print("JARVIS Brain shutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()
