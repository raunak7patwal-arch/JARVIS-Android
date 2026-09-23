from jarvis.modules.master_controller import MasterController

jarvis = MasterController()

print("JARVIS MASTER CONTROLLER")
print("Type 'exit' to shutdown.")
print()

while True:
    text = input("You: ").strip()

    if text.lower() in ("exit", "quit"):
        print("JARVIS: System shutdown.")
        break

    result = jarvis.process(text)

    print("Language:", result["language"]["language_name"])
    print("Type:", result["type"])
    print("JARVIS:", result["reply"])
    print()
