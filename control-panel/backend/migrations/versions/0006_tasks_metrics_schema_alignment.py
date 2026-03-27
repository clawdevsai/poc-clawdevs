"""tasks and metrics schema alignment

Revision ID: 0006
Revises: 0005
Create Date: 2026-03-27
"""

from alembic import op

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE tasks
        ADD COLUMN IF NOT EXISTS assigned_agent_id UUID,
        ADD COLUMN IF NOT EXISTS github_issue_url VARCHAR,
        ADD COLUMN IF NOT EXISTS github_repo VARCHAR,
        ADD COLUMN IF NOT EXISTS due_at TIMESTAMP
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_tasks_assigned_agent_id
        ON tasks (assigned_agent_id)
        """
    )
    op.execute(
        """
        ALTER TABLE metrics
        ADD COLUMN IF NOT EXISTS period_end TIMESTAMP
        """
    )


def downgrade() -> None:
    op.execute("ALTER TABLE metrics DROP COLUMN IF EXISTS period_end")
    op.execute("DROP INDEX IF EXISTS ix_tasks_assigned_agent_id")
    op.execute("ALTER TABLE tasks DROP COLUMN IF EXISTS due_at")
    op.execute("ALTER TABLE tasks DROP COLUMN IF EXISTS github_repo")
    op.execute("ALTER TABLE tasks DROP COLUMN IF EXISTS github_issue_url")
    op.execute("ALTER TABLE tasks DROP COLUMN IF EXISTS assigned_agent_id")
