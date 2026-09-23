from __future__ import annotations

from typing import Any, Dict


class ContextAIBridge:
    """Converts safe device context into a compact AI-readable context."""

    SAFE_FIELDS = (
        "screen",
        "app",
        "activity",
        "battery",
        "network",
        "orientation",
        "locale",
        "timestamp",
    )

    def build(self, context: Dict[str, Any] | None) -> str:
        if not context:
            return ""

        parts = []

        for key in self.SAFE_FIELDS:
            value = context.get(key)
            if value is None or value == "":
                continue

            if isinstance(value, dict):
                clean = ", ".join(
                    f"{k}={v}"
                    for k, v in value.items()
                    if v is not None and v != ""
                )
                if clean:
                    parts.append(f"{key}: {clean}")
            else:
                parts.append(f"{key}: {value}")

        if not parts:
            return ""

        return "Current authorized device context:\n" + "\n".join(
            f"- {item}" for item in parts
        )
