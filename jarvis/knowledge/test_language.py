from jarvis.knowledge.language_engine import LanguageEngine

engine = LanguageEngine()

print("JARVIS MULTILINGUAL ENGINE")
print("Type exit to stop.")
print()

while True:

    text = input("You: ").strip()

    if text.lower() in ("exit", "quit"):
        break

    result = engine.process(text)

    print("Language:", result["language_name"])
    print("Normalized:", result["normalized"])
    print()
