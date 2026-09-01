
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    # ============================================================
    # PRIMARY KEY
    # ============================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # ============================================================
    # USER ID
    # ============================================================

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    # ============================================================
    # ORDER ID
    # ============================================================

    order_id = Column(
        Integer,
        ForeignKey("orders.id"),
        nullable=True,
        index=True
    )

    # ============================================================
    # NOTIFICATION TYPE
    # ============================================================

    type = Column(
        String(100),
        nullable=False
    )

    # ============================================================
    # MESSAGE
    # ============================================================

    message = Column(
        Text,
        nullable=False
    )

    # ============================================================
    # READ STATUS
    # ============================================================

    read_status = Column(
        Boolean,
        default=False,
        nullable=False
    )

    # ============================================================
    # TIMESTAMP
    # ============================================================

    timestamp = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    # ============================================================
    # RELATIONSHIP WITH USER
    # ============================================================

    user = relationship(
        "User",
        back_populates="notifications"
    )

    # ============================================================
    # RELATIONSHIP WITH ORDER
    # ============================================================

    order = relationship(
        "Order",
        back_populates="notifications"
    )