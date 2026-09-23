import hashlib
import hmac
import time


class SecurityHardening:

    MAX_REQUESTS_PER_WINDOW = 30
    WINDOW_SECONDS = 60

    def __init__(self):
        self.requests = {}

    @staticmethod
    def constant_time_equal(
        first,
        second
    ):
        return hmac.compare_digest(
            str(first).encode("utf-8"),
            str(second).encode("utf-8")
        )

    @staticmethod
    def hash_identifier(identifier):
        return hashlib.sha256(
            str(identifier)
            .encode("utf-8")
        ).hexdigest()

    def allow_request(
        self,
        device_id
    ):
        now = time.time()

        history = self.requests.setdefault(
            str(device_id),
            []
        )

        cutoff = (
            now
            - self.WINDOW_SECONDS
        )

        history[:] = [
            timestamp
            for timestamp in history
            if timestamp >= cutoff
        ]

        if len(history) >= (
            self.MAX_REQUESTS_PER_WINDOW
        ):
            return False

        history.append(now)

        return True

    def clear(self, device_id=None):
        if device_id is None:
            self.requests.clear()
        else:
            self.requests.pop(
                str(device_id),
                None
            )


security_hardening = SecurityHardening()
