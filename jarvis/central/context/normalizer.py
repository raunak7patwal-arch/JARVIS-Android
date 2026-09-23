class ContextNormalizer:

    ALLOWED_FIELDS = {
        "screen",
        "app",
        "activity",
        "battery",
        "network",
        "orientation",
        "locale",
        "timestamp",
    }

    @classmethod
    def normalize(cls, context):
        if not isinstance(context, dict):
            return {}

        result = {}

        for key, value in context.items():
            if key not in cls.ALLOWED_FIELDS:
                continue

            if isinstance(
                value,
                (str, int, float, bool)
            ):
                result[key] = value

        return result
