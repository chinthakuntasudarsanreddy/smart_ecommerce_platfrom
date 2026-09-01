"""add delivered at to orders"""

from alembic import op
import sqlalchemy as sa


revision = "7f83a91bc210"
down_revision = "36211d12afdc"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "orders",
        sa.Column(
            "delivered_at",
            sa.DateTime(),
            nullable=True
        )
    )


def downgrade():
    op.drop_column(
        "orders",
        "delivered_at"
    )