from __future__ import annotations


def _hash_password(password: str) -> str:
    import base64
    import hashlib
    import os

    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000)
    return "pbkdf2_sha256$120000$%s$%s" % (
        base64.b64encode(salt).decode("ascii"),
        base64.b64encode(digest).decode("ascii"),
    )


async def upgrade(db) -> None:
    cursor = db.iam_users.find({})
    async for doc in cursor:
        if isinstance(doc.get("password_hash"), str) and doc["password_hash"].startswith("pbkdf2_sha256$"):
            continue

        raw_password = doc.get("password")
        if raw_password is None:
            continue

        await db.iam_users.update_one(
            {"_id": doc["_id"]},
            {
                "$set": {"password_hash": _hash_password(raw_password)},
                "$unset": {"password": ""},
            },
        )
