from jarvis.knowledge.public_knowledge import PublicKnowledge


knowledge = PublicKnowledge()

print("JARVIS PUBLIC KNOWLEDGE GATEWAY")
print("Type exit to stop.")
print()

while True:
    question = input("You: ").strip()

    if question.lower() in ("exit", "quit"):
        break

    answer = knowledge.search(question)

    if answer:
        print("\nJARVIS SOURCE DATA:")
        print(answer)
    else:
        print("\nJARVIS: जानकारी नहीं मिली।")

    print()
