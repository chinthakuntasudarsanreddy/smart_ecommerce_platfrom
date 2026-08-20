from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from datetime import datetime

from app.core.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)

    order_id = Column(
        Integer,
        ForeignKey("orders.id"),
        nullable=False
    )

    amount = Column(
        Float,
        nullable=False
    )

    payment_method = Column(
        String(50),
        nullable=False
    )

    transaction_id = Column(
        String(255),
        nullable=True
    )

    status = Column(
        String(30),
        default="pending",
        nullable=False
    )

    timestamp = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )