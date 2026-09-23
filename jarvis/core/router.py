from jarvis.core.brain import Brain
from jarvis.core.memory import Memory


class Router:

    def __init__(self):
        self.brain = Brain()
        self.memory = Memory()

    def handle(self, text):

        command = text.strip()
        lower = command.lower()

        if lower.startswith("remember "):
            value = command[9:].strip()

            if value:
                self.memory.remember(value)
                return "ठीक है सर, मैंने इसे memory में save कर दिया।"

            return "क्या याद रखना है?"

        if "what do you remember" in lower or "क्या याद है" in lower:
            memories = self.memory.get_all()

            if not memories:
                return "अभी मेरी memory खाली है।"

            return "मुझे यह बातें याद हैं:\n- " + "\n- ".join(memories)

        if lower == "clear memory" or "memory साफ" in lower:
            self.memory.clear()
            return "Memory साफ कर दी गई।"

        answer = self.brain.think(command)

        if answer:
            return answer

        return (
            "मैंने आपका command समझा, लेकिन इस feature का AI module "
            "अभी connect नहीं है।"
        )
