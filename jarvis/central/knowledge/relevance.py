import re


class RelevanceEngine:

    STOP_WORDS = {
        "the", "is", "a", "an", "of", "what", "who",
        "was", "were", "where", "when", "are", "in",
        "क्या", "है", "एक", "की", "का", "के", "कौन",
        "कौनसे", "कौनसा", "कहाँ", "कब", "में", "और",
        "बताओ", "बताइए", "मुझे", "के", "से"
    }

    @classmethod
    def tokens(cls, text):
        words = re.findall(
            r"[A-Za-z0-9\u0900-\u097F]+",
            str(text).lower()
        )

        return {
            word
            for word in words
            if word not in cls.STOP_WORDS
            and len(word) > 1
        }

    @classmethod
    def score(cls, question, item):
        q = cls.tokens(question)

        title = item.get("title", "")
        description = item.get("description", "")
        snippet = item.get("snippet", "")

        title_tokens = cls.tokens(title)
        description_tokens = cls.tokens(description)
        snippet_tokens = cls.tokens(snippet)

        score = 0.0

        score += len(q & title_tokens) * 10
        score += len(q & description_tokens) * 4
        score += len(q & snippet_tokens) * 2

        if title.lower().strip() == question.lower().strip():
            score += 100

        # Exact entity phrase
        q_clean = str(question).lower().strip()
        title_clean = str(title).lower().strip()

        if title_clean and title_clean in q_clean:
            score += 50

        # Question intent
        if any(x in q_clean for x in (
            "who", "कौन"
        )):
            if description:
                score += 3

        if any(x in q_clean for x in (
            "what", "क्या"
        )):
            if description or snippet:
                score += 2

        if any(x in q_clean for x in (
            "capital", "राजधानी"
        )):
            if any(x in (
                str(description).lower()
                + " "
                + str(snippet).lower()
            ) for x in (
                "capital",
                "राजधानी"
            )):
                score += 20

        return score

    @classmethod
    def rank(cls, question, results):
        scored = []

        for item in results:
            if not isinstance(item, dict):
                continue

            scored.append((
                cls.score(question, item),
                item
            ))

        scored.sort(
            key=lambda x: x[0],
            reverse=True
        )

        return [
            item
            for _, item in scored
        ]
