from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy import String

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.core.database import Base


class UserRole(str, Enum):
    ADMIN = "admin"
    STAFF = "staff"
    CUSTOMER = "customer"


class User(Base):
    __tablename__ = "users"

    # ============================================================
    # PRIMARY KEY
    # ============================================================

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    # ============================================================
    # USER NAME
    # ============================================================

    name: Mapped[str] = mapped_column(
        String(120),
        nullable=False
    )

    # ============================================================
    # EMAIL
    # ============================================================

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )

    # ============================================================
    # PASSWORD
    # ============================================================

    password: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    # ============================================================
    # ROLE
    # ============================================================

    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole),
        default=UserRole.CUSTOMER,
        nullable=False
    )

    # ============================================================
    # CREATED DATE
    # ============================================================

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # ============================================================
    # AUTH0
    # ============================================================

    auth0_sub: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        nullable=True
    )

    # ============================================================
    # CART
    # ============================================================

    cart = relationship(
        "Cart",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    # ============================================================
    # ORDERS
    # ============================================================

    orders = relationship(
        "Order",
        back_populates="user"
    )

    # ============================================================
    # RETURN REQUESTS
    # ============================================================

    return_requests = relationship(
        "ReturnRequest",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # ============================================================
    # NOTIFICATIONS
    # ============================================================

    notifications = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan"
    )