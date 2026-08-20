"""add product category

Revision ID: 5efa75a2de3a
Revises: 43bc3dbbd114
Create Date: 2026-08-19 16:24:53.630654
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5efa75a2de3a"
down_revision: Union[str, Sequence[str], None] = "43bc3dbbd114"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create order_items table
    op.create_table(
        'order_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id']),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_index(
        op.f('ix_order_items_id'),
        'order_items',
        ['id'],
        unique=False
    )

    # Create payments table
    op.create_table(
        'payments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('payment_method', sa.String(length=50), nullable=False),
        sa.Column('transaction_id', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=30), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id']),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_index(
        op.f('ix_payments_id'),
        'payments',
        ['id'],
        unique=False
    )

    # DO NOT CHANGE CART TABLE
    # Existing cart structure is preserved.

    # Product columns
    op.add_column(
        'products',
        sa.Column(
            'category',
            sa.String(length=100),
            nullable=True
        )
    )

    op.add_column(
        'products',
        sa.Column(
            'popularity',
            sa.Integer(),
            nullable=True
        )
    )

    op.add_column(
        'products',
        sa.Column(
            'image_url',
            sa.String(length=500),
            nullable=True
        )
    )

    op.add_column(
        'products',
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            nullable=True
        )
    )

    op.add_column(
        'products',
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            nullable=True
        )
    )

    # Existing product rows need values
    op.execute(
        "UPDATE products SET category = 'general' WHERE category IS NULL"
    )

    op.execute(
        "UPDATE products SET popularity = 0 WHERE popularity IS NULL"
    )

    # Make required fields non-null
    op.alter_column(
        'products',
        'category',
        existing_type=sa.String(length=100),
        nullable=False
    )

    op.alter_column(
        'products',
        'popularity',
        existing_type=sa.Integer(),
        nullable=False
    )

    # Name
    op.alter_column(
        'products',
        'name',
        existing_type=mysql.VARCHAR(length=200),
        type_=sa.String(length=255),
        existing_nullable=False
    )

    # Price
    op.alter_column(
        'products',
        'price',
        existing_type=mysql.DECIMAL(precision=12, scale=2),
        type_=sa.Numeric(precision=10, scale=2),
        existing_nullable=False
    )

    # Category index
    op.create_index(
        op.f('ix_products_category'),
        'products',
        ['category'],
        unique=False
    )

    # DO NOT DROP products.images yet