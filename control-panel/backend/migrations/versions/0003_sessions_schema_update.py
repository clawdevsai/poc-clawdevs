"""sessions schema update

Revision ID: 0003
Revises: 0002
Create Date: 2026-03-25 00:00:00.000000

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add missing columns to sessions table
    op.add_column("sessions", sa.Column("channel_peer", sa.String(), nullable=True))
    op.add_column("sessions", sa.Column("last_active_at", sa.DateTime(), nullable=True))
    op.add_column(
        "sessions",
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")
        ),
    )


def downgrade() -> None:
    op.drop_column("sessions", "created_at")
    op.drop_column("sessions", "last_active_at")
    op.drop_column("sessions", "channel_peer")
