import re


class ResponseEngine:

    def __init__(self):
        self.name = "JARVIS"

    def detect_language(self, text):
        if re.search(r"[\u0900-\u097F]", text):
            return "hi"

        hinglish = [
            "kya", "kaise", "kyun", "kahan",
            "kab", "hai", "ho", "batao"
        ]

        words = text.lower().split()

        if any(word in hinglish for word in words):
            return "hi"

        return "en"

    def clean_answer(self, answer):
        if not answer:
            return ""

        answer = answer.strip()

        # मॉडल के unwanted prefixes हटाना
        prefixes = [
            "Answer:",
            "ANSWER:",
            "JARVIS:",
            "Jarvis:",
            "उत्तर:",
            "जवाब:"
        ]

        for prefix in prefixes:
            if answer.startswith(prefix):
                answer = answer[len(prefix):].strip()

        # Markdown हटाना
        answer = answer.replace("**", "")
        answer = answer.replace("##", "")

        return answer.strip()

    def is_greeting(self, text):
        t = text.lower().strip()

        greetings = [
            "hello",
            "hi",
            "hey",
            "नमस्ते",
            "हेलो",
            "कैसे हो",
            "kaise ho",
            "kese ho"
        ]

        return any(x in t for x in greetings)

    def greeting(self, language):
        if language == "hi":
            return "पूरी तरह operational हूँ, सर। आपकी सेवा के लिए तैयार।"

        return "Fully operational, sir. At your service."

    def add_personality(self, answer, language):
        answer = self.clean_answer(answer)

        if not answer:
            if language == "hi":
                return "माफ कीजिए सर, मुझे इसका विश्वसनीय उत्तर नहीं मिला।"
            return "I'm sorry, sir. I couldn't find a reliable answer."

        # बहुत लंबा जवाब नहीं
        sentences = re.split(r"(?<=[।.!?])\s+", answer)

        if len(sentences) > 4:
            answer = " ".join(sentences[:4])

        # अगर पहले से sir/सर नहीं है तो naturally जोड़ें
        if language == "hi":
            if not re.search(r"\b(सर|sir)\b", answer, re.IGNORECASE):
                answer = answer.rstrip("।.!?") + "।"

        else:
            if not re.search(r"\bsir\b", answer, re.IGNORECASE):
                answer = answer.rstrip(".!?") + "."

        return answer

    def generate(self, question, answer):
        language = self.detect_language(question)

        if self.is_greeting(question):
            return self.greeting(language)

        return self.add_personality(answer, language)
