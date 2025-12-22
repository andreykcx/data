"""Create data_points table."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0001_create_data_points"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "data_points",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("dataset_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("x", sa.Float(precision=53), nullable=False, server_default="0.0"),
        sa.Column("y", sa.Float(precision=53), nullable=False, server_default="0.0"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("NOW()"), nullable=False),
    )
    op.create_index("idx_data_points_dataset_id", "data_points", ["dataset_id"])


def downgrade() -> None:
    op.drop_index("idx_data_points_dataset_id", table_name="data_points")
    op.drop_table("data_points")
