from __future__ import annotations

import json
from urllib.request import Request, urlopen


class ContextClient:
    def __init__(self, base_url: str, timeout: float = 5.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def update(self, device_id: str, context: dict) -> dict:
        payload = {
            "device_id": device_id,
            "context": context,
        }

        request = Request(
            f"{self.base_url}/context/update",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urlopen(request, timeout=self.timeout) as response:
            return json.loads(response.read().decode("utf-8"))

    def latest(self, device_id: str) -> dict:
        request = Request(
            f"{self.base_url}/context/latest?device_id={device_id}",
            method="GET",
        )

        with urlopen(request, timeout=self.timeout) as response:
            return json.loads(response.read().decode("utf-8"))
