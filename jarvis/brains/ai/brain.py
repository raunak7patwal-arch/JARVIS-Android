from jarvis.brains.ai.local_model import LocalAI
from jarvis.knowledge.retriever import KnowledgeRetriever
from jarvis.knowledge.web_brain import WebKnowledge


class KnowledgeBrain:
    def __init__(self):
        self.ai = LocalAI()
        self.knowledge = KnowledgeRetriever()
        self.web = WebKnowledge()

    def answer(self, text):
        text = text.strip()

        if not text:
            return "मैं सुन रहा हूँ।"

        # पहले local verified facts
        local = self.knowledge.search(text)
        if local:
            return local

        # फिर online knowledge
        online = self.web.search(text)

        if online:
            prompt = f"""
तुम JARVIS हो।
यूज़र का सवाल:
{text}

नीचे online source से मिली जानकारी है:
{online}

केवल इसी जानकारी के आधार पर हिंदी में छोटा और स्पष्ट उत्तर दो।
अगर जानकारी पर्याप्त नहीं है तो साफ कहो कि जानकारी पर्याप्त नहीं है।
"""

            return self.ai.ask(prompt)

        # आखिर में local AI
        return self.ai.ask(text)
