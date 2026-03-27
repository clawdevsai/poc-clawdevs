from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20260327_update_memory_embedding_type"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Alter embedding column from TEXT to VECTOR(1536)
    # Note: Requires pgvector extension to be enabled
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Drop the old column and create new one
    # Since pgvector type is different, we need to recreate the column
    with op.batch_alter_table("memory_entries") as batch_op:
        # First, we need to drop the existing embedding column
        batch_op.drop_column("embedding")
        # Add new vector column
        batch_op.add_column(
            sa.Column("embedding", postgresql.VECTOR(1536), nullable=True)
        )


def downgrade() -> None:
    # Revert back to TEXT (JSON string)
    with op.batch_alter_table("memory_entries") as batch_op:
        batch_op.drop_column("embedding")
        batch_op.add_column(sa.Column("embedding", sa.Text(), nullable=True))
