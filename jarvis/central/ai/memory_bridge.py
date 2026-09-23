class MemoryBridge:

    REMEMBER_WORDS = (
        "remember that",
        "remember",
        "याद रखो",
        "याद रखना",
        "याद रखिए",
    )

    def __init__(self, memory):
        self.memory = memory

    def detect(self, text):
        original = str(text).strip()
        lowered = original.lower()

        for word in self.REMEMBER_WORDS:
            if lowered.startswith(word):
                value = original[
                    len(word):
                ].strip(" :-,")

                if value:
                    return value

        return None

    def handle(self, text):
        value = self.detect(text)

        if not value:
            return None

        self.memory.remember(
            value,
            "user_preference",
            5
        )

        return "जी सर। मैंने इसे याद रख लिया है।"
