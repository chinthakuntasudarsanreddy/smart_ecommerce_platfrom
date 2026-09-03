from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    total = Column(
        Float,
        nullable=False
    )

    order_status = Column(
        String(50),
        default="pending",
        nullable=False
    )

    payment_status = Column(
        String(50),
        default="pending",
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )
    delivered_at = Column(
    DateTime,
    nullable=True
)

    # ============================================================
    # USER
    # ============================================================

    user = relationship(
        "User",
        back_populates="orders"
    )

    # ============================================================
    # ORDER ITEMS
    # ============================================================

    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan"
    )

    # ============================================================
    # RETURN REQUESTS
    # ============================================================

    return_requests = relationship(
        "ReturnRequest",
        back_populates="order",
        cascade="all, delete-orphan"
    )

    # ============================================================
    # NOTIFICATIONS
    # ============================================================

    notifications = relationship(
        "Notification",
        back_populates="order",
        cascade="all, delete-orphan"
    )