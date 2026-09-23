import json
import os
import urllib.parse
import urllib.request


class LiveSearchProvider:

    def __init__(self):
        self.provider = os.getenv(
            "JARVIS_SEARCH_PROVIDER",
            "duckduckgo"
        ).lower()

    def search(
        self,
        question,
        language="en"
    ):
        if self.provider == "duckduckgo":
            return self._duckduckgo(
                question
            )

        return []

    def _duckduckgo(
        self,
        question
    ):
        params = urllib.parse.urlencode({
            "q": question,
            "format": "json",
            "no_html": "1",
            "skip_disambig": "0",
        })

        url = (
            "https://api.duckduckgo.com/?"
            + params
        )

        request = urllib.request.Request(
            url,
            headers={
                "User-Agent":
                    "JARVIS-Central/1.0",
                "Accept":
                    "application/json",
            }
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=5
            ) as response:
                data = json.loads(
                    response.read().decode(
                        "utf-8"
                    )
                )

            results = []

            abstract = data.get(
                "AbstractText",
                ""
            )

            if abstract:
                results.append({
                    "title": data.get(
                        "Heading",
                        question
                    ),
                    "description": abstract,
                    "snippet": abstract,
                    "source":
                        "DuckDuckGo",
                    "url": data.get(
                        "AbstractURL",
                        ""
                    )
                })

            for item in data.get(
                "RelatedTopics",
                []
            ):
                if not isinstance(
                    item,
                    dict
                ):
                    continue

                text = item.get(
                    "Text",
                    ""
                )

                if not text:
                    continue

                results.append({
                    "title": text[:120],
                    "description": text,
                    "snippet": text,
                    "source":
                        "DuckDuckGo",
                    "url": item.get(
                        "FirstURL",
                        ""
                    )
                })

                if len(results) >= 8:
                    break

            return results

        except Exception as e:
            print(
                "Live search error:",
                e
            )
            return []
