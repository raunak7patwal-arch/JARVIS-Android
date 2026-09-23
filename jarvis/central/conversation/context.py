class ConversationContext:

    def __init__(self, manager):
        self.manager = manager

    def build(self):
        try:
            return self.manager.context()
        except Exception:
            return ""

    def add_user(self, text):
        return self.manager.add_user(text)

    def add_assistant(self, text):
        return self.manager.add_assistant(text)
