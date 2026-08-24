"""add order id to notifications

Revision ID: 4088abb175b8
Revises: 1481d7e60bff
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "4088abb175b8"
down_revision: Union[str, None] = "1481d7e60bff"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add order_id to notifications
    op.add_column(
        "notifications",
        sa.Column(
            "order_id",
            sa.Integer(),
            nullable=True
        )
    )

    # Add foreign key from notifications.order_id -> orders.id
    op.create_foreign_key(
        "fk_notifications_order_id",
        "notifications",
        "orders",
        ["order_id"],
        ["id"]
    )

    # Add index
    op.create_index(
        "ix_notifications_order_id",
        "notifications",
        ["order_id"]
    )


def downgrade() -> None:
    op.drop_index(
        "ix_notifications_order_id",
        table_name="notifications"
    )

    op.drop_constraint(
        "fk_notifications_order_id",
        "notifications",
        type_="foreignkey"
    )

    op.drop_column(
        "notifications",
        "order_id"
    )