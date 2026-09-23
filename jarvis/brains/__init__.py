from jarvis.brains.ai.brain import KnowledgeBrain
from jarvis.brains.software.brain import SoftwareBrain
from jarvis.brains.security.brain import SecurityBrain


class JarvisBrain:
    def __init__(self):
        self.knowledge = KnowledgeBrain()
        self.software = SoftwareBrain()
        self.security = SecurityBrain()

    def process(self, text):
        t = text.lower().strip()

        if t.startswith("security ") or t.startswith("सिक्योरिटी "):
            return self.security.analyze(text.split(" ", 1)[1])

        if t.startswith("software ") or t.startswith("सॉफ्टवेयर "):
            return self.software.execute(text.split(" ", 1)[1])

        return self.knowledge.answer(text)
