"""initial schema

Revision ID: 20260611_0001
Revises:
Create Date: 2026-06-11 00:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "20260611_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "iam_users",
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("username", sa.String(length=120), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("user_id"),
        sa.UniqueConstraint("username"),
    )
    op.create_index("ix_iam_users_username", "iam_users", ["username"], unique=False)

    op.create_table(
        "persons",
        sa.Column("person_id", sa.String(length=36), nullable=False),
        sa.Column("first_name", sa.String(length=120), nullable=False),
        sa.Column("last_name", sa.String(length=120), nullable=False),
        sa.Column("dni", sa.String(length=20), nullable=False),
        sa.Column("image_url", sa.Text(), nullable=True),
        sa.Column("samples", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("person_id"),
        sa.UniqueConstraint("dni"),
    )
    op.create_index("ix_persons_dni", "persons", ["dni"], unique=False)

    op.create_table(
        "usage_logs",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=True),
        sa.Column("operation", sa.String(length=64), nullable=False),
        sa.Column("person_id", sa.String(length=36), nullable=True),
        sa.Column("first_name", sa.String(length=120), nullable=True),
        sa.Column("last_name", sa.String(length=120), nullable=True),
        sa.Column("dni", sa.String(length=20), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("samples_added", sa.Integer(), nullable=True),
        sa.Column("total_samples", sa.Integer(), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=False),
        sa.Column("image_url", sa.Text(), nullable=True),
        sa.Column("used_at", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_usage_logs_user_id", "usage_logs", ["user_id"], unique=False)
    op.create_index("ix_usage_logs_operation", "usage_logs", ["operation"], unique=False)
    op.create_index("ix_usage_logs_person_id", "usage_logs", ["person_id"], unique=False)
    op.create_index("ix_usage_logs_used_at", "usage_logs", ["used_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_usage_logs_used_at", table_name="usage_logs")
    op.drop_index("ix_usage_logs_person_id", table_name="usage_logs")
    op.drop_index("ix_usage_logs_operation", table_name="usage_logs")
    op.drop_index("ix_usage_logs_user_id", table_name="usage_logs")
    op.drop_table("usage_logs")

    op.drop_index("ix_persons_dni", table_name="persons")
    op.drop_table("persons")

    op.drop_index("ix_iam_users_username", table_name="iam_users")
    op.drop_table("iam_users")

