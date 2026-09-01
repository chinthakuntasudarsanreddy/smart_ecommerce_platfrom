from sqlalchemy import Column, Integer, Numeric, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Order(Base):
    __tablename__ = "orders"

    # ============================================================
    # PRIMARY KEY
    # ============================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # ============================================================
    # USER
    # ============================================================

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    # ============================================================
    # ORDER TOTAL
    # ============================================================

    total = Column(
        Numeric(10, 2),
        nullable=False
    )

    # ============================================================
    # PAYMENT STATUS
    # ============================================================

    payment_status = Column(
        String(50),
        default="pending",
        nullable=False
    )

    # ============================================================
    # ORDER STATUS
    # ============================================================

    order_status = Column(
        String(50),
        default="pending",
        nullable=False
    )

    # ============================================================
    # CREATED DATE
    # ============================================================

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # ============================================================
    # DELIVERED DATE
    # ============================================================

    delivered_at = Column(
        DateTime,
        nullable=True
    )

    # ============================================================
    # RELATIONSHIP WITH USER
    # ============================================================

    user = relationship(
        "User",
        back_populates="orders"
    )

    # ============================================================
    # RELATIONSHIP WITH ORDER ITEMS
    # ============================================================

    items = relationship(
        "OrderItem",
        back_populates="order"
    )

    # ============================================================
    # RELATIONSHIP WITH RETURN REQUESTS
    # ============================================================

    return_requests = relationship(
        "ReturnRequest",
        back_populates="order",
        cascade="all, delete-orphan"
    )

    # ============================================================
    # RELATIONSHIP WITH NOTIFICATIONS
    # ============================================================

    notifications = relationship(
        "Notification",
        back_populates="order",
        cascade="all, delete-orphan"
    )