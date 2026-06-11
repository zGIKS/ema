"""seed default admin

Revision ID: 20260611_0002
Revises: 20260611_0001
Create Date: 2026-06-11 00:00:00.000000
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import NAMESPACE_DNS, uuid5

from alembic import op
import sqlalchemy as sa

from src.app.iam.infrastructure.security.passwords import encode_password


# revision identifiers, used by Alembic.
revision = "20260611_0002"
down_revision = "20260611_0001"
branch_labels = None
depends_on = None

ADMIN_USERNAME = "U000000001"
ADMIN_PASSWORD = "Admin12345!A"
ADMIN_USER_ID = str(uuid5(NAMESPACE_DNS, "ema-default-admin"))


def upgrade() -> None:
    bind = op.get_bind()
    exists = bind.execute(
        sa.text("SELECT 1 FROM iam_users WHERE username = :username LIMIT 1"),
        {"username": ADMIN_USERNAME},
    ).scalar_one_or_none()

    if exists is not None:
        return

    now = datetime.now(UTC)
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
            "password_hash": encode_password(ADMIN_PASSWORD),
            "role": "admin",
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        },
    )


def downgrade() -> None:
    op.execute(sa.text("DELETE FROM iam_users WHERE username = :username"), {"username": ADMIN_USERNAME})
