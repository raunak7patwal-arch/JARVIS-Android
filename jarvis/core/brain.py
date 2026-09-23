from datetime import datetime


class Brain:

    def think(self, text):
        t = text.lower().strip()

        if not t:
            return "मैं सुन रहा हूँ।"

        if any(x in t for x in ["hello", "hi", "hey", "नमस्ते", "हेलो"]):
            return "नमस्ते सर। JARVIS online है।"

        if "who are you" in t or "तुम कौन" in t:
            return "मैं JARVIS हूँ — आपका personal AI assistant."

        if "time" in t or "समय" in t or "टाइम" in t:
            return "अभी " + datetime.now().strftime("%I:%M %p") + " बज रहे हैं।"

        if "date" in t or "तारीख" in t:
            return "आज " + datetime.now().strftime("%d-%m-%Y") + " है।"

        if "status" in t or "स्टेटस" in t:
            return "All core systems are operational."

        return None
