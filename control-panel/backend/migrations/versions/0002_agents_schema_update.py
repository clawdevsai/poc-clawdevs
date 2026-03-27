"""agents schema update

Revision ID: 0002
Revises: 0001
Create Date: 2026-03-24 00:00:00.000000

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename model -> current_model
    op.alter_column("agents", "model", new_column_name="current_model")

    # Rename last_heartbeat -> last_heartbeat_at
    op.alter_column("agents", "last_heartbeat", new_column_name="last_heartbeat_at")

    # Add missing columns
    op.add_column("agents", sa.Column("avatar_url", sa.String(), nullable=True))
    op.add_column(
        "agents", sa.Column("openclaw_session_id", sa.String(), nullable=True)
    )
    op.add_column("agents", sa.Column("cron_last_run_at", sa.DateTime(), nullable=True))
    op.add_column("agents", sa.Column("cron_next_run_at", sa.DateTime(), nullable=True))

    # Drop obsolete column
    op.drop_column("agents", "heartbeat_count")


def downgrade() -> None:
    op.add_column(
        "agents",
        sa.Column("heartbeat_count", sa.Integer(), nullable=False, server_default="0"),
    )
    op.drop_column("agents", "cron_next_run_at")
    op.drop_column("agents", "cron_last_run_at")
    op.drop_column("agents", "openclaw_session_id")
    op.drop_column("agents", "avatar_url")
    op.alter_column("agents", "last_heartbeat_at", new_column_name="last_heartbeat")
    op.alter_column("agents", "current_model", new_column_name="model")
