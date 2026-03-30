"""Add openclaw_session_key to sessions table

Revision ID: 0016
Revises: 0015
Create Date: 2026-03-30 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0016"
down_revision = "0015"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "sessions",
        sa.Column("openclaw_session_key", sa.String(), nullable=True),
    )
    op.create_index(
        "ix_sessions_agent_slug_openclaw_session_key",
        "sessions",
        ["agent_slug", "openclaw_session_key"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_sessions_agent_slug_openclaw_session_key", table_name="sessions")
    op.drop_column("sessions", "openclaw_session_key")
