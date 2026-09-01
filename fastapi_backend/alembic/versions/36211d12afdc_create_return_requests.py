
"""create return requests

Revision ID: 36211d12afdc
Revises: a2bca159ad1d
"""

from alembic import op
import sqlalchemy as sa


revision = "36211d12afdc"
down_revision = "a2bca159ad1d"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "return_requests",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            autoincrement=True
        ),

        sa.Column(
            "order_id",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "reason",
            sa.String(255),
            nullable=False
        ),

        sa.Column(
            "comment",
            sa.Text(),
            nullable=True
        ),

        sa.Column(
            "status",
            sa.String(20),
            nullable=False,
            server_default="pending"
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP")
        ),

        sa.ForeignKeyConstraint(
            ["order_id"],
            ["orders.id"]
        ),

        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"]
        ),
    )

    op.create_index(
        "ix_return_requests_id",
        "return_requests",
        ["id"]
    )

    op.create_index(
        "ix_return_requests_order_id",
        "return_requests",
        ["order_id"]
    )

    op.create_index(
        "ix_return_requests_user_id",
        "return_requests",
        ["user_id"]
    )


def downgrade():
    op.drop_index(
        "ix_return_requests_user_id",
        table_name="return_requests"
    )

    op.drop_index(
        "ix_return_requests_order_id",
        table_name="return_requests"
    )

    op.drop_index(
        "ix_return_requests_id",
        table_name="return_requests"
    )

    op.drop_table("return_requests")