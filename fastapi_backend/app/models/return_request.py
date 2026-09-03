from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class ReturnRequest(Base):
    __tablename__ = "return_requests"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    order_id = Column(
        Integer,
        ForeignKey("orders.id"),
        nullable=False
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    reason = Column(
        Text,
        nullable=False
    )

    comment = Column(
        Text,
        nullable=True
    )

    status = Column(
        String(50),
        default="pending",
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    # ============================================================
    # USER
    # ============================================================

    user = relationship(
        "User",
        back_populates="return_requests"
    )

    # ============================================================
    # ORDER
    # ============================================================

    order = relationship(
        "Order",
        back_populates="return_requests"
    )