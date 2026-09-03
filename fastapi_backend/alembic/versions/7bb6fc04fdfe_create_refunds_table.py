from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7bb6fc04fdfe"
down_revision = "7f83a91bc210"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "refunds",
        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "order_id",
            sa.Integer(),
            sa.ForeignKey("orders.id"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        sa.Column(
            "amount",
            sa.Float(),
            nullable=False,
        ),
        sa.Column(
            "refund_method",
            sa.String(length=50),
            nullable=False,
            server_default="original_payment",
        ),
        sa.Column(
            "transaction_id",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
            server_default="pending",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )

    op.create_index(
        "ix_refunds_id",
        "refunds",
        ["id"],
        unique=False,
    )

    op.create_index(
        "ix_refunds_order_id",
        "refunds",
        ["order_id"],
        unique=False,
    )

    op.create_index(
        "ix_refunds_user_id",
        "refunds",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_refunds_user_id",
        table_name="refunds",
    )

    op.drop_index(
        "ix_refunds_order_id",
        table_name="refunds",
    )

    op.drop_index(
        "ix_refunds_id",
        table_name="refunds",
    )

    op.drop_table("refunds")