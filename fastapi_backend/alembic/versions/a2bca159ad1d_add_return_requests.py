"""add return requests

Revision ID: a2bca159ad1d
Revises: 4088abb175b8
Create Date: 2026-08-31
"""

from alembic import op
import sqlalchemy as sa


# Revision identifiers
revision = "a2bca159ad1d"
down_revision = "4088abb175b8"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "return_requests",

        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
            autoincrement=True,
        ),

        sa.Column(
            "order_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "reason",
            sa.String(length=255),
            nullable=False,
        ),

        sa.Column(
            "comment",
            sa.Text(),
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
            server_default=sa.func.now(),
        ),

        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("return_requests")