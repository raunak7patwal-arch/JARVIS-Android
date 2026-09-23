import json
import re
import time
import urllib.parse
import urllib.request
from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed
)

from jarvis.central.knowledge.relevance import (
    RelevanceEngine
)

from jarvis.central.knowledge.facts import (
    FactExtractor
)

from jarvis.central.knowledge.cache import (
    KnowledgeCache
)

from jarvis.central.knowledge.live import (
    LiveSearchProvider
)


class KnowledgeGateway:

    WIKIPEDIA_API = {
        "en": "https://en.wikipedia.org/w/api.php",
        "hi": "https://hi.wikipedia.org/w/api.php",
    }

    WIKIPEDIA_REST = {
        "en":
            "https://en.wikipedia.org/api/rest_v1/page/summary/",
        "hi":
            "https://hi.wikipedia.org/api/rest_v1/page/summary/",
    }

    MAX_WORKERS = 6
    MAX_RESULTS = 10

    def __init__(self):
        self.executor = ThreadPoolExecutor(
            max_workers=self.MAX_WORKERS
        )

        self.cache = KnowledgeCache()
        self.live = LiveSearchProvider()

    def _request_json(
        self,
        url,
        timeout=5
    ):
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent":
                    "JARVIS-Central/1.0",
                "Accept":
                    "application/json",
            }
        )

        with urllib.request.urlopen(
            request,
            timeout=timeout
        ) as response:
            return json.loads(
                response.read().decode(
                    "utf-8"
                )
            )

    # ==============================================
    # Wikipedia search
    # ==============================================

    def wikipedia_search(
        self,
        question,
        language="en"
    ):
        cached = self.cache.get(
            "wiki-search:" + question,
            language
        )

        if cached is not None:
            return cached

        base = self.WIKIPEDIA_API.get(
            language,
            self.WIKIPEDIA_API["en"]
        )

        params = urllib.parse.urlencode({
            "action": "query",
            "list": "search",
            "srsearch": question,
            "format": "json",
            "utf8": 1,
            "srlimit": 8,
        })

        try:
            data = self._request_json(
                base + "?" + params
            )

            results = []

            for item in data.get(
                "query",
                {}
            ).get(
                "search",
                []
            ):
                results.append({
                    "title": item.get(
                        "title",
                        ""
                    ),
                    "snippet": re.sub(
                        r"<[^>]+>",
                        "",
                        item.get(
                            "snippet",
                            ""
                        )
                    ),
                    "source":
                        "Wikipedia"
                })

            self.cache.set(
                "wiki-search:" + question,
                language,
                results
            )

            return results

        except Exception as e:
            print(
                "Wikipedia search error:",
                e
            )
            return []

    # ==============================================
    # Wikipedia summary
    # ==============================================

    def wikipedia_summary(
        self,
        title,
        language="en"
    ):
        cached = self.cache.get(
            "wiki-summary:" + title,
            language
        )

        if cached is not None:
            return cached

        base = self.WIKIPEDIA_REST.get(
            language,
            self.WIKIPEDIA_REST["en"]
        )

        encoded = urllib.parse.quote(
            title.replace(
                " ",
                "_"
            )
        )

        try:
            data = self._request_json(
                base + encoded
            )

            extract = data.get(
                "extract",
                ""
            )

            if not extract:
                return None

            result = {
                "title": data.get(
                    "title",
                    title
                ),
                "description": data.get(
                    "description",
                    ""
                ),
                "snippet": extract,
                "source":
                    "Wikipedia",
                "url": (
                    data.get(
                        "content_urls",
                        {}
                    )
                    .get(
                        "desktop",
                        {}
                    )
                    .get(
                        "page",
                        ""
                    )
                )
            }

            self.cache.set(
                "wiki-summary:" + title,
                language,
                result
            )

            return result

        except Exception as e:
            print(
                "Wikipedia summary error:",
                e
            )
            return None

    # ==============================================
    # Target generation
    # ==============================================

    def _clean_question(
        self,
        question
    ):
        text = str(
            question
        ).strip()

        patterns = [
            r"^(who is|who was)\s+",
            r"^(what is|what are)\s+",
            r"^(where is|where was)\s+",
            r"^(when was|when is)\s+",
            r"^(क्या है|कौन है|कौन थे|कहाँ है|कब हुआ)\s+",
        ]

        for pattern in patterns:
            text = re.sub(
                pattern,
                "",
                text,
                flags=re.IGNORECASE
            )

        text = re.sub(
            r"[?।!]+$",
            "",
            text
        )

        return text.strip()

    def _search_targets(
        self,
        question,
        language
    ):
        targets = []

        cleaned = self._clean_question(
            question
        )

        if cleaned:
            targets.append(
                cleaned
            )

        match = re.search(
            r"(.+?)\s+की\s+राजधानी",
            question
        )

        if match:
            targets.append(
                match.group(1).strip()
            )

        match = re.search(
            r"capital\s+of\s+(.+?)(?:\?|$)",
            question,
            re.IGNORECASE
        )

        if match:
            targets.append(
                match.group(1).strip()
            )

        match = re.search(
            r"^(?:who is|who was)\s+(.+?)(?:\?|$)",
            question,
            re.IGNORECASE
        )

        if match:
            targets.append(
                match.group(1).strip()
            )

        return list(
            dict.fromkeys(
                x for x in targets
                if x
            )
        )

    # ==============================================
    # Parallel entity search
    # ==============================================

    def entity_search(
        self,
        question,
        language="en"
    ):
        targets = self._search_targets(
            question,
            language
        )

        if not targets:
            return []

        futures = {
            self.executor.submit(
                self.wikipedia_search,
                target,
                language
            ): target
            for target in targets[:4]
        }

        results = []

        for future in as_completed(
            futures
        ):
            try:
                results.extend(
                    future.result()
                )
            except Exception:
                pass

        return RelevanceEngine.rank(
            question,
            results
        )

    # ==============================================
    # Main search
    # ==============================================

    def search(
        self,
        question,
        language="en"
    ):
        started = time.perf_counter()

        cache_key = (
            "final:"
            + question
        )

        cached = self.cache.get(
            cache_key,
            language
        )

        if cached is not None:
            return cached

        wiki = self.entity_search(
            question,
            language
        )

        candidates = wiki[:6]

        futures = {
            self.executor.submit(
                self.wikipedia_summary,
                item.get(
                    "title",
                    ""
                ),
                language
            ): item
            for item in candidates
            if item.get("title")
        }

        evidence = []

        for future in as_completed(
            futures
        ):
            try:
                result = future.result()

                if result:
                    evidence.append(
                        result
                    )
            except Exception:
                pass

        evidence.extend(
            wiki
        )

        # Live search is fallback only.
        # This prevents unnecessary external
        # requests for ordinary questions.
        if len(evidence) < 2:
            try:
                evidence.extend(
                    self.live.search(
                        question,
                        language
                    )
                )
            except Exception:
                pass

        evidence = RelevanceEngine.rank(
            question,
            evidence
        )

        final = []
        seen = set()

        for item in evidence:

            title = str(
                item.get(
                    "title",
                    ""
                )
            ).strip()

            key = title.lower()

            if not key or key in seen:
                continue

            seen.add(key)
            final.append(item)

            if len(final) >= self.MAX_RESULTS:
                break

        self.cache.set(
            cache_key,
            language,
            final
        )

        elapsed = (
            time.perf_counter()
            - started
        )

        print(
            f"Knowledge search: "
            f"{elapsed:.3f}s | "
            f"{len(final)} results"
        )

        return final
