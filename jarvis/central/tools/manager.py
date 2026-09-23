from __future__ import annotations

import json
from pathlib import Path


TOOLS_FILE = Path("jarvis/central/tools/termux_tools.json")


class TermuxToolManager:

    def list_tools(self) -> list[dict]:
        if not TOOLS_FILE.exists():
            return []

        try:
            data = json.loads(
                TOOLS_FILE.read_text(
                    encoding="utf-8"
                )
            )

            tools = data.get("tools", [])

            return tools if isinstance(tools, list) else []

        except Exception:
            return []

    def summary(self) -> str:
        tools = self.list_tools()

        if not tools:
            return (
                "सर, अभी Termux की tool inventory उपलब्ध नहीं है।"
            )

        names = [
            str(item.get("name", "")).strip()
            for item in tools
            if str(item.get("name", "")).strip()
        ]

        if not names:
            return (
                "सर, अभी कोई supported Termux tool नहीं मिला।"
            )

        return (
            f"सर, Termux में {len(names)} supported tools "
            "available हैं: "
            + ", ".join(names)
        )

    def has_tool(self, name: str) -> bool:
        name = str(name).strip().lower()

        return any(
            str(item.get("name", "")).strip().lower() == name
            for item in self.list_tools()
        )


if __name__ == "__main__":
    manager = TermuxToolManager()

    print(manager.summary())
    print("SUCCESS")
