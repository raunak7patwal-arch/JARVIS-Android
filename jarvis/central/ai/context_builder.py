from jarvis.central.memory.context import MemoryContext
from jarvis.central.conversation.context import ConversationContext


class AIContextBuilder:

    def __init__(self, conversation):
        self.memory = MemoryContext()
        self.conversation = ConversationContext(
            conversation
        )

    def build(self, question):
        memory_text = self.memory.build(
            question,
            5
        )

        conversation_text = (
            self.conversation.build()
        )

        parts = []

        if conversation_text:
            parts.append(
                "CONVERSATION:\n"
                + conversation_text
            )

        if memory_text:
            parts.append(
                "LONG-TERM MEMORY:\n"
                + memory_text
            )

        if not parts:
            return ""

        return "\n\n".join(parts)

    def remember(
        self,
        text,
        category="general",
        importance=1
    ):
        return self.memory.remember(
            text,
            category,
            importance
        )
