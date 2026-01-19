"""Initial schema - users, metrics, config, archive_policy

Revision ID: 001_initial
Revises:
Create Date: 2025-01-19

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
    )
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)

    # Create metrics_snapshot table
    op.create_table(
        "metrics_snapshot",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("metric_type", sa.String(length=50), nullable=False),
        sa.Column("metric_data", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_metrics_snapshot_id"), "metrics_snapshot", ["id"], unique=False)
    op.create_index(
        op.f("ix_metrics_snapshot_timestamp"), "metrics_snapshot", ["timestamp"], unique=False
    )
    op.create_index(
        "idx_metrics_type_timestamp",
        "metrics_snapshot",
        ["metric_type", "timestamp"],
        unique=False,
    )

    # Create config table
    op.create_table(
        "config",
        sa.Column("key", sa.String(length=100), nullable=False),
        sa.Column("value", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("key"),
    )

    # Create archive_policy table
    op.create_table(
        "archive_policy",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("retention_days", sa.Integer(), nullable=False),
        sa.Column("archive_enabled", sa.Boolean(), nullable=False),
        sa.Column("downsample_after_days", sa.Integer(), nullable=False),
        sa.Column("downsample_interval", sa.String(length=20), nullable=False),
        sa.Column("last_archive_run", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("archive_policy")
    op.drop_table("config")
    op.drop_index("idx_metrics_type_timestamp", table_name="metrics_snapshot")
    op.drop_index(op.f("ix_metrics_snapshot_timestamp"), table_name="metrics_snapshot")
    op.drop_index(op.f("ix_metrics_snapshot_id"), table_name="metrics_snapshot")
    op.drop_table("metrics_snapshot")
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_table("users")
