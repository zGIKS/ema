"""add refresh tokens

Revision ID: 20260612_0003
Revises: 20260611_0002
Create Date: 2026-06-12 00:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260612_0003"
down_revision = "20260611_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "iam_refresh_tokens",
        sa.Column("token_id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("token_hash", sa.Text(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("replaced_by_token_id", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["iam_users.user_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("token_id"),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_index("ix_iam_refresh_tokens_user_id", "iam_refresh_tokens", ["user_id"], unique=False)
    op.create_index("ix_iam_refresh_tokens_expires_at", "iam_refresh_tokens", ["expires_at"], unique=False)
    op.create_index("ix_iam_refresh_tokens_revoked_at", "iam_refresh_tokens", ["revoked_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_iam_refresh_tokens_revoked_at", table_name="iam_refresh_tokens")
    op.drop_index("ix_iam_refresh_tokens_expires_at", table_name="iam_refresh_tokens")
    op.drop_index("ix_iam_refresh_tokens_user_id", table_name="iam_refresh_tokens")
    op.drop_table("iam_refresh_tokens")
