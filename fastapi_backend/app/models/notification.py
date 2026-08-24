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

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    order_id = Column(
        Integer,
        ForeignKey("orders.id"),
        nullable=True,
        index=True
    )

    type = Column(
        String(100),
        nullable=False
    )

    message = Column(
        Text,
        nullable=False
    )

    read_status = Column(
        Boolean,
        default=False,
        nullable=False
    )

    timestamp = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    order = relationship(
        "Order",
        back_populates="notifications"
    )