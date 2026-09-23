import hashlib
import hmac
import os
import secrets
import time


class DeviceAuth:

    def __init__(self):
        self.devices = {}
        self.tokens = {}

    def register(
        self,
        device_id,
        secret=None
    ):
        if not device_id:
            raise ValueError("device_id required")

        if secret is None:
            secret = secrets.token_urlsafe(32)

        secret_hash = hashlib.sha256(
            secret.encode("utf-8")
        ).hexdigest()

        self.devices[device_id] = {
            "secret_hash": secret_hash,
            "created": time.time(),
        }

        return secret

    def verify(
        self,
        device_id,
        secret
    ):
        device = self.devices.get(device_id)

        if not device:
            return False

        supplied = hashlib.sha256(
            str(secret).encode("utf-8")
        ).hexdigest()

        return hmac.compare_digest(
            supplied,
            device["secret_hash"]
        )

    def issue_token(
        self,
        device_id,
        secret,
        ttl=3600
    ):
        if not self.verify(
            device_id,
            secret
        ):
            return None

        token = secrets.token_urlsafe(32)

        self.tokens[token] = {
            "device_id": device_id,
            "expires": time.time() + ttl,
        }

        return token

    def verify_token(
        self,
        token
    ):
        item = self.tokens.get(token)

        if not item:
            return False

        if time.time() >= item["expires"]:
            self.tokens.pop(
                token,
                None
            )
            return False

        return True

    def revoke(
        self,
        token
    ):
        self.tokens.pop(
            token,
            None
        )
