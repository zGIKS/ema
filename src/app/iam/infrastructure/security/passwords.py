from __future__ import annotations

import base64
import hashlib
import hmac
import os

PASSWORD_ENCODER_ID = "pbkdf2_sha256"
PASSWORD_ITERATIONS = 120_000


def encode_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PASSWORD_ITERATIONS)
    return "{%s}$%s$%s$%s" % (
        PASSWORD_ENCODER_ID,
        PASSWORD_ITERATIONS,
        base64.b64encode(salt).decode("ascii"),
        base64.b64encode(digest).decode("ascii"),
    )


def verify_password(password: str, encoded: str) -> bool:
    if not encoded.startswith("{") or "}" not in encoded:
        return False

    encoder_id, payload = encoded[1:].split("}", 1)
    if encoder_id != PASSWORD_ENCODER_ID:
        return False

    try:
        iterations_str, salt_b64, digest_b64 = payload.lstrip("$").split("$", 2)
    except ValueError:
        return False

    try:
        iterations = int(iterations_str)
    except ValueError:
        return False

    salt = base64.b64decode(salt_b64)
    expected = base64.b64decode(digest_b64)
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return hmac.compare_digest(derived, expected)
