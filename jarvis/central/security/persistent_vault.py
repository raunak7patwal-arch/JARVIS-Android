from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from pathlib import Path


ROOT = Path("jarvis/central")
SECURITY_DIR = ROOT / "security"
DATA_DIR = ROOT / "persistent_data"

MASTER_FILE = SECURITY_DIR / "master.json"
VAULT_FILE = SECURITY_DIR / "vault.bin"
AUDIT_FILE = DATA_DIR / "security_audit.jsonl"

PBKDF2_ROUNDS = 300_000
SALT_SIZE = 32
NONCE_SIZE = 32
KEY_SIZE = 64


def _ensure_dirs():
    SECURITY_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    try:
        os.chmod(SECURITY_DIR, 0o700)
        os.chmod(DATA_DIR, 0o700)
    except OSError:
        pass


def _derive_key(password: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PBKDF2_ROUNDS,
        dklen=KEY_SIZE,
    )


def _keystream(key: bytes, nonce: bytes, length: int) -> bytes:
    output = bytearray()
    counter = 0

    while len(output) < length:
        block = hmac.new(
            key,
            nonce + counter.to_bytes(8, "big"),
            hashlib.sha256,
        ).digest()

        output.extend(block)
        counter += 1

    return bytes(output[:length])


def _encrypt(data: bytes, key: bytes) -> bytes:
    nonce = secrets.token_bytes(NONCE_SIZE)
    stream = _keystream(key, nonce, len(data))

    ciphertext = bytes(
        a ^ b
        for a, b in zip(data, stream)
    )

    tag = hmac.new(
        key,
        nonce + ciphertext,
        hashlib.sha256,
    ).digest()

    return b"JRV1" + nonce + tag + ciphertext


def _decrypt(blob: bytes, key: bytes) -> bytes:
    if not blob.startswith(b"JRV1"):
        raise ValueError("Invalid JARVIS vault format")

    offset = 4

    nonce = blob[offset:offset + NONCE_SIZE]
    offset += NONCE_SIZE

    tag = blob[offset:offset + 32]
    offset += 32

    ciphertext = blob[offset:]

    expected = hmac.new(
        key,
        nonce + ciphertext,
        hashlib.sha256,
    ).digest()

    if not hmac.compare_digest(tag, expected):
        raise ValueError("Invalid master password or corrupted vault")

    stream = _keystream(key, nonce, len(ciphertext))

    return bytes(
        a ^ b
        for a, b in zip(ciphertext, stream)
    )


def _audit(event: str, **details):
    _ensure_dirs()

    record = {
        "timestamp": int(time.time()),
        "event": event,
        **details,
    }

    with AUDIT_FILE.open(
        "a",
        encoding="utf-8",
    ) as f:
        f.write(
            json.dumps(
                record,
                ensure_ascii=False,
            )
            + "\n"
        )

    try:
        os.chmod(AUDIT_FILE, 0o600)
    except OSError:
        pass


class PersistentVault:

    def __init__(self):
        _ensure_dirs()
        self._key = None
        self._unlocked = False

    @property
    def configured(self) -> bool:
        return MASTER_FILE.exists()

    @property
    def unlocked(self) -> bool:
        return self._unlocked and self._key is not None

    def setup_master_password(self, password: str):
        password = str(password)

        if len(password) < 8:
            raise ValueError(
                "Master password must contain at least 8 characters"
            )

        if self.configured:
            raise RuntimeError(
                "Master password is already configured"
            )

        salt = secrets.token_bytes(SALT_SIZE)
        key = _derive_key(password, salt)

        verification = hmac.new(
            key,
            b"JARVIS-MASTER-VERIFICATION",
            hashlib.sha256,
        ).digest()

        MASTER_FILE.write_text(
            json.dumps(
                {
                    "version": 1,
                    "algorithm": "PBKDF2-SHA256-HMAC",
                    "rounds": PBKDF2_ROUNDS,
                    "salt": base64.b64encode(salt).decode(),
                    "verification": base64.b64encode(
                        verification
                    ).decode(),
                },
                indent=2,
            ),
            encoding="utf-8",
        )

        try:
            os.chmod(MASTER_FILE, 0o600)
        except OSError:
            pass

        self._key = key
        self._unlocked = True

        if not VAULT_FILE.exists():
            self.save({
                "version": 1,
                "created": int(time.time()),
                "memory": {},
                "settings": {},
                "lineage": {},
            })

        _audit("master_configured")

    def unlock(self, password: str) -> bool:
        if not self.configured:
            raise RuntimeError(
                "Master password has not been configured"
            )

        data = json.loads(
            MASTER_FILE.read_text(
                encoding="utf-8"
            )
        )

        salt = base64.b64decode(
            data["salt"]
        )

        expected = base64.b64decode(
            data["verification"]
        )

        key = _derive_key(
            str(password),
            salt,
        )

        actual = hmac.new(
            key,
            b"JARVIS-MASTER-VERIFICATION",
            hashlib.sha256,
        ).digest()

        if not hmac.compare_digest(
            actual,
            expected,
        ):
            _audit("unlock_failed")
            return False

        self._key = key
        self._unlocked = True

        _audit("vault_unlocked")

        return True

    def lock(self):
        self._key = None
        self._unlocked = False

        _audit("vault_locked")

    def save(self, data: dict):
        if not self.unlocked:
            raise PermissionError(
                "JARVIS vault is locked"
            )

        raw = json.dumps(
            data,
            ensure_ascii=False,
            indent=2,
        ).encode("utf-8")

        encrypted = _encrypt(
            raw,
            self._key,
        )

        temporary = VAULT_FILE.with_suffix(
            ".tmp"
        )

        temporary.write_bytes(encrypted)
        temporary.replace(VAULT_FILE)

        try:
            os.chmod(VAULT_FILE, 0o600)
        except OSError:
            pass

        _audit("vault_saved")

    def load(self) -> dict:
        if not self.unlocked:
            raise PermissionError(
                "JARVIS vault is locked"
            )

        if not VAULT_FILE.exists():
            return {}

        raw = _decrypt(
            VAULT_FILE.read_bytes(),
            self._key,
        )

        data = json.loads(
            raw.decode("utf-8")
        )

        if not isinstance(data, dict):
            raise ValueError(
                "Invalid vault data"
            )

        return data

    def status(self) -> dict:
        return {
            "configured": self.configured,
            "unlocked": self.unlocked,
            "vault_exists": VAULT_FILE.exists(),
            "security_dir": str(
                SECURITY_DIR
            ),
        }


if __name__ == "__main__":
    print("======================================")
    print("JARVIS PERSISTENT VAULT")
    print("======================================")

    vault = PersistentVault()

    print(
        "Master configured :",
        vault.configured,
    )

    print(
        "Vault exists      :",
        VAULT_FILE.exists(),
    )

    print(
        "Encryption        : READY",
    )

    print(
        "Persistent storage: READY",
    )

    print("======================================")
    print("SUCCESS")
