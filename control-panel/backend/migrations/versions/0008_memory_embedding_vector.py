from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Alter embedding column from TEXT to VECTOR(1536)
    # Note: Requires pgvector extension to be enabled
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Add new vector column (column didn't exist in previous schema)
    with op.batch_alter_table("memory_entries") as batch_op:
        batch_op.add_column(sa.Column("embedding", Vector(1536), nullable=True))


def downgrade() -> None:
    # Remove the vector column (back to original state without embedding column)
    with op.batch_alter_table("memory_entries") as batch_op:
        batch_op.drop_column("embedding")
