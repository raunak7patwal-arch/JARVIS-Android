import json
from pathlib import Path

MEMORY_FILE = Path("memory/memory.json")


class Memory:
    def __init__(self):
        MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)

        if not MEMORY_FILE.exists():
            MEMORY_FILE.write_text(
                json.dumps({"memories": []}, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )

    def _load(self):
        try:
            return json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {"memories": []}

    def _save(self, data):
        MEMORY_FILE.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    def remember(self, text):
        data = self._load()
        data["memories"].append(text)
        self._save(data)

    def get_all(self):
        return self._load().get("memories", [])

    def clear(self):
        self._save({"memories": []})
