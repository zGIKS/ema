from __future__ import annotations

from secrets import randbelow


ADMIN_USER_ID = "U000000001"
ADMIN_USERNAME = ADMIN_USER_ID
ADMIN_PASSWORD = "Admin12345!"


def _hash_password(password: str) -> str:
    import base64
    import hashlib
    import os as _os

    salt = _os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000)
    return "pbkdf2_sha256$120000$%s$%s" % (
        base64.b64encode(salt).decode("ascii"),
        base64.b64encode(digest).decode("ascii"),
    )


async def upgrade(db) -> None:
    existing = await db.iam_users.find_one({"username": ADMIN_USERNAME})
    if existing is not None:
        return

    for _ in range(100):
        user_id = ADMIN_USER_ID if _ == 0 else f"U{randbelow(1_000_000_000):09d}"
        if await db.iam_users.find_one({"user_id": user_id}) is None:
            await db.iam_users.insert_one(
                {
                    "user_id": user_id,
                    "username": ADMIN_USERNAME,
                    "password_hash": _hash_password(ADMIN_PASSWORD),
                    "role": "admin",
                    "is_active": True,
                }
            )
            return

    raise RuntimeError("Unable to generate unique admin user_id")
