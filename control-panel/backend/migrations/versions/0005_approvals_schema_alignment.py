"""approvals schema alignment

Revision ID: 0005
Revises: 0004
Create Date: 2026-03-27
"""

from alembic import op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE approvals
        ADD COLUMN IF NOT EXISTS openclaw_approval_id VARCHAR,
        ADD COLUMN IF NOT EXISTS action_type VARCHAR NOT NULL DEFAULT 'unknown',
        ADD COLUMN IF NOT EXISTS confidence DOUBLE PRECISION
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_approvals_openclaw_approval_id
        ON approvals (openclaw_approval_id)
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_approvals_openclaw_approval_id")
    op.execute("ALTER TABLE approvals DROP COLUMN IF EXISTS confidence")
    op.execute("ALTER TABLE approvals DROP COLUMN IF EXISTS action_type")
    op.execute("ALTER TABLE approvals DROP COLUMN IF EXISTS openclaw_approval_id")
