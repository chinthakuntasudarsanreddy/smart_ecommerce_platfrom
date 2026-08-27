from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )

    user_id = Column(
        Integer,
        nullable=False,
        index=True
    )

    total = Column(
        Float,
        nullable=False
    )

    payment_status = Column(
        String(20),
        nullable=False,
        default="pending"
    )

    order_status = Column(
        String(20),
        nullable=False,
        default="pending"
    )

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )

    items = relationship(
        "OrderItem",
        back_populates="order"
    )