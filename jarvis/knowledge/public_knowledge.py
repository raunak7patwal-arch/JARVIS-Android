import requests
import time
import re
from urllib.parse import quote


class PublicKnowledge:

    def __init__(self):
        self.session = requests.Session()

        self.session.headers.update({
            "User-Agent": "JARVIS-Android/1.0",
            "Accept": "application/json",
        })

        self.last_request = 0
        self.min_delay = 2.0

    # --------------------------------------------------
    # RATE LIMIT PROTECTION
    # --------------------------------------------------

    def wait(self):
        elapsed = time.time() - self.last_request

        if elapsed < self.min_delay:
            time.sleep(self.min_delay - elapsed)

        self.last_request = time.time()

    # --------------------------------------------------
    # HINGLISH NORMALIZATION
    # --------------------------------------------------

    def normalize(self, text):

        text = text.lower().strip()

        replacements = {

            # Hindi/Hinglish question words
            "kya": "क्या",
            "kyo": "क्यों",
            "kyun": "क्यों",
            "kaise": "कैसे",
            "kaisa": "कैसा",
            "kese": "कैसे",
            "kon": "कौन",
            "kaun": "कौन",
            "kahan": "कहाँ",
            "kaha": "कहाँ",
            "kab": "कब",
            "kitna": "कितना",
            "kitne": "कितने",
            "kitni": "कितनी",

            # Common verbs
            "hai": "है",
            "hain": "हैं",
            "ho": "हो",
            "tha": "था",
            "thi": "थी",
            "the": "थे",

            # Common words
            "mera": "मेरा",
            "meri": "मेरी",
            "mere": "मेरे",
            "tum": "तुम",
            "aap": "आप",
            "main": "मैं",
            "me": "में",

            # Geography
            "bharat": "भारत",
            "india": "भारत",
            "rajdhani": "राजधानी",
            "rajdhani": "राजधानी",

            # Government
            "pradhanmantri": "प्रधानमंत्री",
            "pm": "प्रधानमंत्री",
            "president": "राष्ट्रपति",
            "rashtrapati": "राष्ट्रपति",
            "mukhyamantri": "मुख्यमंत्री",

            # Common English/Hinglish
            "capital": "राजधानी",
            "currency": "मुद्रा",
            "country": "देश",
            "state": "राज्य",
            "city": "शहर",
        }

        words = text.split()

        converted = []

        for word in words:
            clean = re.sub(r"[^\w\u0900-\u097F]", "", word)

            if clean in replacements:
                converted.append(replacements[clean])
            else:
                converted.append(word)

        return " ".join(converted)

    # --------------------------------------------------
    # SPECIAL FACTUAL QUESTIONS
    # --------------------------------------------------

    def special_answer(self, question):

        q = self.normalize(question)

        # India capital
        if (
            "भारत" in q
            and "राजधानी" in q
        ):
            return "भारत की राजधानी नई दिल्ली है।"

        # Japan capital
        if (
            ("जापान" in q or "japan" in q)
            and "राजधानी" in q
        ):
            return "जापान की राजधानी टोक्यो है।"

        return None

    # --------------------------------------------------
    # WIKIPEDIA
    # --------------------------------------------------

    def wikipedia(self, question):

        try:

            normalized = self.normalize(question)

            self.wait()

            url = "https://en.wikipedia.org/w/api.php"

            params = {
                "action": "query",
                "list": "search",
                "srsearch": normalized,
                "format": "json",
                "utf8": 1,
                "srlimit": 5,
            }

            r = self.session.get(
                url,
                params=params,
                timeout=15
            )

            if r.status_code == 429:
                return None

            r.raise_for_status()

            results = (
                r.json()
                .get("query", {})
                .get("search", [])
            )

            if not results:
                return None

            # Try several results instead of blindly
            # taking the first one.
            for result in results:

                title = result.get("title")

                if not title:
                    continue

                self.wait()

                summary_url = (
                    "https://en.wikipedia.org/api/rest_v1/page/summary/"
                    + quote(title)
                )

                r = self.session.get(
                    summary_url,
                    timeout=15
                )

                if r.status_code == 429:
                    return None

                if not r.ok:
                    continue

                data = r.json()

                extract = data.get("extract")

                if extract:
                    return extract[:4000]

        except Exception as e:
            print("Wikipedia:", e)

        return None

    # --------------------------------------------------
    # WIKIDATA
    # --------------------------------------------------

    def wikidata(self, question):

        try:

            normalized = self.normalize(question)

            self.wait()

            url = "https://www.wikidata.org/w/api.php"

            params = {
                "action": "wbsearchentities",
                "search": normalized,
                "language": "en",
                "uselang": "en",
                "format": "json",
                "limit": 5,
            }

            r = self.session.get(
                url,
                params=params,
                timeout=15
            )

            if r.status_code == 429:
                return None

            r.raise_for_status()

            results = r.json().get("search", [])

            if not results:
                return None

            output = []

            for item in results:

                label = item.get("label")
                description = item.get("description")

                if not label:
                    continue

                if description:
                    output.append(
                        f"{label} — {description}"
                    )
                else:
                    output.append(label)

            return "\n".join(output) if output else None

        except Exception as e:
            print("Wikidata:", e)

        return None

    # --------------------------------------------------
    # MAIN SEARCH
    # --------------------------------------------------

    def search(self, question):

        question = question.strip()

        if not question:
            return None

        # 1. Exact/common factual knowledge
        answer = self.special_answer(question)

        if answer:
            return answer

        # 2. Normalize Hinglish
        normalized = self.normalize(question)

        # 3. Search public knowledge
        answer = self.wikipedia(normalized)

        if answer:
            return answer

        # 4. Wikidata fallback
        return self.wikidata(normalized)
