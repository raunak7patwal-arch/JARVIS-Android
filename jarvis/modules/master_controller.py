from jarvis.modules.language.language_engine import LanguageEngine
from jarvis.modules.knowledge.knowledge_engine import KnowledgeEngine


class MasterController:

    def __init__(self):
        self.language = LanguageEngine()
        self.knowledge = KnowledgeEngine()

    def is_knowledge_question(self, text):
        t = text.lower()

        words = [
            "क्या है", "कौन है", "कौन हैं",
            "कहाँ", "कहां", "कब",
            "क्यों", "कैसे",
            "राजधानी", "प्रधानमंत्री",
            "मुख्यमंत्री", "मंत्री",
            "विदेश मंत्री", "राष्ट्रपति",
            "capital", "who is", "what is",
            "where", "when", "why", "how"
        ]

        return any(word in t for word in words)

    def process(self, text):
        text = text.strip()

        if not text:
            return {
                "type": "conversation",
                "reply": "मैं सुन रहा हूँ।"
            }

        lang = self.language.process(text)

        lower = text.lower()

        if any(x in lower for x in [
            "hi", "hii", "hello",
            "नमस्ते", "हेलो",
            "kese ho", "kaise ho"
        ]):
            return {
                "type": "conversation",
                "language": lang,
                "reply": "नमस्ते सर। JARVIS online है।"
            }

        if self.is_knowledge_question(text):
            answer = self.knowledge.answer(text)

            return {
                "type": "knowledge",
                "language": lang,
                "reply": answer
            }

        return {
            "type": "unknown",
            "language": lang,
            "reply": "मैंने command समझ ली है, लेकिन इसके लिए अभी सही module जोड़ना बाकी है।"
        }
