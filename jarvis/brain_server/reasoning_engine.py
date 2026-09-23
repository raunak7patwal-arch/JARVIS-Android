import re


class ReasoningEngine:

    def __init__(self):
        self.max_context = 12000

    def tokens(self, text):
        return re.findall(
            r"[A-Za-z0-9\u0900-\u097F]+",
            text.lower()
        )

    def useful_tokens(self, text):
        stop = {
            "क्या", "कौन", "कहाँ", "कहां", "कब",
            "क्यों", "कैसे", "कितना", "कितनी", "कितने",
            "है", "हैं", "था", "थे", "हो",
            "what", "who", "where", "when",
            "why", "how", "which",
            "is", "are", "was", "were"
        }

        return [
            x for x in self.tokens(text)
            if x not in stop
        ]

    def score(self, question, evidence):

        q_tokens = self.useful_tokens(question)

        title = evidence.get("title", "").lower()
        text = evidence.get("text", "").lower()

        title_tokens = self.tokens(title)
        text_tokens = self.tokens(text)

        score = 0

        # --------------------------------
        # 1. Exact useful phrase
        # --------------------------------
        if len(q_tokens) >= 2:

            for size in range(
                min(4, len(q_tokens)),
                1,
                -1
            ):
                for i in range(len(q_tokens) - size + 1):

                    phrase = " ".join(
                        q_tokens[i:i + size]
                    )

                    if phrase in text:
                        score += size * 15

                    if phrase in title:
                        score += size * 25

        # --------------------------------
        # 2. Individual useful words
        # --------------------------------
        for word in q_tokens:

            if len(word) < 2:
                continue

            if word in title_tokens:
                score += 8

            if word in text_tokens:
                score += 2

        # --------------------------------
        # 3. Question concepts appearing
        #    close together
        # --------------------------------
        for i in range(len(text_tokens) - 1):

            pair = (
                text_tokens[i],
                text_tokens[i + 1]
            )

            for j in range(len(q_tokens) - 1):

                if pair == (
                    q_tokens[j],
                    q_tokens[j + 1]
                ):
                    score += 12

        return score

    def rank(self, question, results):

        ranked = []

        for item in results:

            if item.get("error"):
                continue

            item = dict(item)

            item["_score"] = self.score(
                question,
                item
            )

            ranked.append(item)

        ranked.sort(
            key=lambda x: x.get("_score", 0),
            reverse=True
        )

        return ranked

    def prepare_evidence(self, question, results):

        ranked = self.rank(
            question,
            results
        )

        context = []

        for item in ranked[:6]:

            title = item.get(
                "title", ""
            ).strip()

            text = item.get(
                "text", ""
            ).strip()

            if not text:
                continue

            context.append(
                f"SOURCE: {item.get('source', 'unknown')}\n"
                f"TITLE: {title}\n"
                f"TEXT: {text}\n"
            )

        return "\n".join(context)[:self.max_context]

    def build_prompt(
        self,
        question,
        evidence,
        language="auto"
    ):

        if language.startswith("hi"):

            language_instruction = (
                "उत्तर बहुत सरल और स्वाभाविक हिंदी में दो। "
                "सिर्फ जरूरी बात बताओ। "
                "ऐसा जवाब दो जैसे JARVIS अपने मालिक को "
                "सीधे और संक्षेप में जवाब दे रहा हो।"
            )

        elif language.startswith("en"):

            language_instruction = (
                "Answer in simple, natural English. "
                "Be direct and concise."
            )

        else:

            language_instruction = (
                "Answer in the user's language. "
                "Be direct and concise."
            )

        return f"""
You are JARVIS, a factual knowledge assistant.

USER QUESTION:
{question}

LANGUAGE:
{language}

RULES:
- {language_instruction}
- Use the evidence below.
- Prefer the evidence most directly related to the question.
- Ignore unrelated articles.
- Never invent facts.
- Do not mention sources, scoring, retrieval or internal systems.
- Do not repeat long source text.
- Give only the answer the user actually needs.

EVIDENCE:
{evidence}

ANSWER:
""".strip()

    def fallback(self, question, ranked):

        if not ranked:
            return (
                "मुझे इस सवाल की पर्याप्त जानकारी नहीं मिली।"
            )

        # सबसे relevant evidence
        best = ranked[0]

        text = best.get(
            "text",
            ""
        ).strip()

        if not text:
            return (
                "मुझे इस सवाल की पर्याप्त जानकारी नहीं मिली।"
            )

        # पहले ऐसा sentence ढूँढो जिसमें
        # question के मुख्य शब्द मिलते हों
        useful = self.useful_tokens(question)

        sentences = re.split(
            r"(?<=[।.!?])\s+",
            text
        )

        candidates = []

        for sentence in sentences:

            sentence_lower = sentence.lower()

            hits = sum(
                1
                for word in useful
                if word in sentence_lower
            )

            if hits:
                candidates.append(
                    (hits, sentence.strip())
                )

        if candidates:

            candidates.sort(
                key=lambda x: x[0],
                reverse=True
            )

            return candidates[0][1][:500]

        return text[:500]

    def process(
        self,
        question,
        results,
        language="auto"
    ):

        ranked = self.rank(
            question,
            results
        )

        evidence = self.prepare_evidence(
            question,
            ranked
        )

        prompt = self.build_prompt(
            question,
            evidence,
            language
        )

        return {
            "prompt": prompt,
            "evidence": evidence,
            "ranked_results": ranked,
            "fallback": self.fallback(
                question,
                ranked
            )
        }
