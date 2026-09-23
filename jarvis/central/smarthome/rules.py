class SmartHomeRule:

    def __init__(
        self,
        rule_id,
        name,
        condition,
        action,
        enabled=True
    ):
        self.rule_id = rule_id
        self.name = name
        self.condition = condition
        self.action = action
        self.enabled = enabled

    def matches(self, context):
        if not self.enabled:
            return False

        if not isinstance(context, dict):
            return False

        return all(
            context.get(key) == value
            for key, value in self.condition.items()
        )

    def execute(self, manager):
        device_id = self.action.get(
            "device_id"
        )

        action = self.action.get(
            "action"
        )

        value = self.action.get(
            "value"
        )

        return manager.set_state(
            device_id,
            action,
            value
        )


class SmartHomeRules:

    def __init__(self):
        self.rules = {}

    def add(self, rule):
        self.rules[rule.rule_id] = rule

    def remove(self, rule_id):
        return (
            self.rules.pop(
                rule_id,
                None
            )
            is not None
        )

    def evaluate(
        self,
        context,
        manager
    ):
        results = []

        for rule in self.rules.values():
            if rule.matches(context):
                results.append({
                    "rule_id": rule.rule_id,
                    "executed": rule.execute(
                        manager
                    ),
                })

        return results
