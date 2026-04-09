"""Add runtime settings tables

Revision ID: 0018
Revises: 0017
Create Date: 2026-04-06 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0018"
down_revision = "0017"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "runtime_setting",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("key", sa.String(length=128), nullable=False),
        sa.Column("value_json", sa.JSON(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("updated_by_user_id", sa.Uuid(), nullable=True),
        sa.ForeignKeyConstraint(["updated_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_runtime_setting_key",
        "runtime_setting",
        ["key"],
        unique=False,
    )

    op.create_table(
        "runtime_setting_audit",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("setting_key", sa.String(length=128), nullable=False),
        sa.Column("previous_value_json", sa.JSON(), nullable=True),
        sa.Column("new_value_json", sa.JSON(), nullable=True),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("confirm_text", sa.String(length=32), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("created_by_user_id", sa.Uuid(), nullable=True),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_runtime_setting_audit_setting_key",
        "runtime_setting_audit",
        ["setting_key"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_runtime_setting_audit_setting_key", table_name="runtime_setting_audit")
    op.drop_table("runtime_setting_audit")
    op.drop_index("ix_runtime_setting_key", table_name="runtime_setting")
    op.drop_table("runtime_setting")
