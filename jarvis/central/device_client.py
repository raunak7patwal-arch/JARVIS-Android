import json
import urllib.request
import urllib.error


class DeviceClient:

    def __init__(
        self,
        server_address,
        timeout=8
    ):
        self.server_address = (
            server_address
            .rstrip("/")
        )
        self.timeout = timeout

    def _post(
        self,
        path,
        payload
    ):
        data = json.dumps(
            payload,
            ensure_ascii=False
        ).encode("utf-8")

        request = urllib.request.Request(
            self.server_address + path,
            data=data,
            headers={
                "Content-Type":
                    "application/json",
                "User-Agent":
                    "JARVIS-Android/1.0",
            },
            method="POST"
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=self.timeout
            ) as response:
                body = response.read().decode(
                    "utf-8"
                )

                return json.loads(body)

        except urllib.error.HTTPError as e:
            try:
                body = e.read().decode(
                    "utf-8"
                )
                return json.loads(body)
            except Exception:
                return {
                    "ok": False,
                    "error": (
                        f"HTTP {e.code}"
                    )
                }

        except Exception as e:
            return {
                "ok": False,
                "error": str(e)
            }

    def register(
        self,
        device_id,
        name="JARVIS Android",
        platform="android"
    ):
        return self._post(
            "/device/register",
            {
                "device_id": device_id,
                "name": name,
                "platform": platform,
            }
        )

    def heartbeat(
        self,
        device_id
    ):
        return self._post(
            "/device/heartbeat",
            {
                "device_id": device_id
            }
        )

    def command(
        self,
        device_id,
        action,
        parameters=None
    ):
        return self._post(
            "/device/command",
            {
                "device_id": device_id,
                "action": action,
                "parameters": (
                    parameters or {}
                ),
            }
        )

    def complete(
        self,
        command_id,
        result
    ):
        return self._post(
            "/device/complete",
            {
                "command_id": command_id,
                "result": result,
            }
        )

    def fail(
        self,
        command_id,
        error
    ):
        return self._post(
            "/device/fail",
            {
                "command_id": command_id,
                "error": str(error),
            }
        )
