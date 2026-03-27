"""repositories table and task label column

Revision ID: 0004
Revises: 0003
Create Date: 2026-03-25
"""

from alembic import op
import sqlalchemy as sa

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "repositories",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("full_name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("default_branch", sa.String(), nullable=False, server_default="main"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")
        ),
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("full_name"),
    )
    op.create_index("ix_repositories_is_active", "repositories", ["is_active"])

    op.add_column("tasks", sa.Column("label", sa.String(), nullable=True))
    op.create_index("ix_tasks_label", "tasks", ["label"])


def downgrade() -> None:
    op.drop_index("ix_tasks_label", "tasks")
    op.drop_column("tasks", "label")
    op.drop_index("ix_repositories_is_active", "repositories")
    op.drop_table("repositories")
