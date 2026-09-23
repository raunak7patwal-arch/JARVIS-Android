import os
import json
import hashlib
import requests


class WebKnowledge:

    WIKIDATA = "https://www.wikidata.org/w/api.php"

    def __init__(self):
        self.headers = {
            "User-Agent": "JARVIS-Android/1.0"
        }

        self.cache_dir = os.path.join(
            os.path.dirname(__file__),
            "cache"
        )

        os.makedirs(self.cache_dir, exist_ok=True)

    def cache_path(self, question):
        key = hashlib.sha256(
            question.encode("utf-8")
        ).hexdigest()

        return os.path.join(
            self.cache_dir,
            key + ".json"
        )

    def search_wikidata(self, question):

        # सामान्य सवाल को searchable keywords में बदलना
        q = question.strip()

        r = requests.get(
            self.WIKIDATA,
            params={
                "action": "wbsearchentities",
                "search": q,
                "language": "hi",
                "uselang": "hi",
                "format": "json",
                "limit": 5
            },
            headers=self.headers,
            timeout=15
        )

        r.raise_for_status()

        results = r.json().get("search", [])

        if not results:
            return None

        return results

    def search(self, question):

        question = question.strip()

        if not question:
            return None

        # Cache
        cache = self.cache_path(question)

        if os.path.exists(cache):
            try:
                with open(cache, "r", encoding="utf-8") as f:
                    data = json.load(f)

                return data.get("text")

            except Exception:
                pass

        try:

            # --------------------------------
            # EXACT COMMON FACTS
            # --------------------------------

            q = question.lower()

            if (
                "भारत की राजधानी" in q
                or "capital of india" in q
            ):
                answer = "भारत की राजधानी नई दिल्ली है।"

                self.save_cache(
                    cache,
                    question,
                    answer
                )

                return answer

            if (
                "जापान की राजधानी" in q
                or "capital of japan" in q
            ):
                answer = "जापान की राजधानी टोक्यो है।"

                self.save_cache(
                    cache,
                    question,
                    answer
                )

                return answer

            # --------------------------------
            # WIKIDATA SEARCH
            # --------------------------------

            results = self.search_wikidata(question)

            if results:

                best = results[0]

                label = best.get("label", "")
                description = best.get("description", "")

                if label:

                    text = label

                    if description:
                        text += " — " + description

                    self.save_cache(
                        cache,
                        question,
                        text
                    )

                    return text

            return None

        except Exception as e:

            print(
                "ONLINE KNOWLEDGE ERROR:",
                e
            )

            return None

    def save_cache(
        self,
        path,
        question,
        text
    ):

        data = {
            "question": question,
            "text": text
        }

        try:

            with open(
                path,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    data,
                    f,
                    ensure_ascii=False,
                    indent=2
                )

        except Exception:
            pass
