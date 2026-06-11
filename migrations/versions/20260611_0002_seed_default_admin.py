"""seed default admin

Revision ID: 20260611_0002
Revises: 20260611_0001
Create Date: 2026-06-11 00:00:00.000000
"""

from __future__ import annotations

import base64
import hashlib
from datetime import UTC, datetime

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260611_0002"
down_revision = "20260611_0001"
branch_labels = None
depends_on = None

ADMIN_USERNAME = "U000000001"
ADMIN_PASSWORD = "Admin12345!A"
ADMIN_USER_ID = "00000000-0000-0000-0000-000000000001"
PASSWORD_ITERATIONS = 120_000
SALT = b"ema-default-admin-salt"


def _hash_password(password: str) -> str:
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), SALT, PASSWORD_ITERATIONS)
    return "pbkdf2_sha256$%s$%s$%s" % (
        PASSWORD_ITERATIONS,
        base64.b64encode(SALT).decode("ascii"),
        base64.b64encode(digest).decode("ascii"),
    )


def upgrade() -> None:
    bind = op.get_bind()
    exists = bind.execute(
        sa.text("SELECT 1 FROM iam_users WHERE username = :username LIMIT 1"),
        {"username": ADMIN_USERNAME},
    ).scalar_one_or_none()

    if exists is not None:
        return

    now_epoch = int(datetime.now(UTC).timestamp())
    bind.execute(
        sa.text(
            """
            INSERT INTO iam_users (
                user_id,
                username,
                password_hash,
                role,
                is_active,
                created_at,
                updated_at
            ) VALUES (
                :user_id,
                :username,
                :password_hash,
                :role,
                :is_active,
                :created_at,
                :updated_at
            )
            """
        ),
        {
            "user_id": ADMIN_USER_ID,
            "username": ADMIN_USERNAME,
            "password_hash": _hash_password(ADMIN_PASSWORD),
            "role": "admin",
            "is_active": True,
            "created_at": now_epoch,
            "updated_at": now_epoch,
        },
    )


def downgrade() -> None:
    op.execute(sa.text("DELETE FROM iam_users WHERE username = :username"), {"username": ADMIN_USERNAME})

