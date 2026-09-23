import re


class QueryEngine:

    QUESTION_WORDS = {
        "क्या", "कौन", "कहां", "कहाँ",
        "कब", "क्यों", "कैसे", "कितना",
        "what", "who", "where", "when",
        "why", "how", "which"
    }

    STOP_WORDS = {
        "क्या", "है", "हैं", "था", "थे",
        "की", "के", "का", "में", "से",
        "को", "और", "यह", "वह",
        "what", "is", "are", "the",
        "of", "in", "to", "and"
    }

    HINGLISH = {
        "bharat": "भारत",
        "india": "भारत",
        "ki": "की",
        "ka": "का",
        "ke": "के",
        "rajdhani": "राजधानी",
        "kya": "क्या",
        "hai": "है",
        "kaun": "कौन",
        "kahan": "कहाँ",
        "kab": "कब",
        "kyun": "क्यों",
        "kyu": "क्यों",
        "kaise": "कैसे",
        "kese": "कैसे"
    }

    def normalize(self, text):

        words = text.lower().strip().split()

        converted = []

        for word in words:
            clean = re.sub(
                r"[^\w\u0900-\u097F]",
                "",
                word
            )

            converted.append(
                self.HINGLISH.get(
                    clean,
                    clean
                )
            )

        return " ".join(converted)

    def keywords(self, text):

        normalized = self.normalize(text)

        words = normalized.split()

        useful = []

        for word in words:

            if not word:
                continue

            if word in self.STOP_WORDS:
                continue

            if len(word) < 2:
                continue

            useful.append(word)

        return useful

    def build_queries(self, text):

        normalized = self.normalize(text)

        words = self.keywords(text)

        queries = []

        # Original normalized question
        if normalized:
            queries.append(normalized)

        # Important keywords
        if words:
            queries.append(
                " ".join(words)
            )

        # Remove question words
        content = [
            word for word in words
            if word not in self.QUESTION_WORDS
        ]

        if content:
            queries.append(
                " ".join(content)
            )

        # Remove duplicates
        final = []

        for query in queries:

            query = query.strip()

            if query and query not in final:
                final.append(query)

        return final[:5]

    def analyze(self, text):

        normalized = self.normalize(text)
        keywords = self.keywords(text)
        queries = self.build_queries(text)

        return {
            "original": text,
            "normalized": normalized,
            "keywords": keywords,
            "queries": queries
        }
