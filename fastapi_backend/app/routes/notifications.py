from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.notification import Notification
from app.models.order import Order
from app.schemas.notification import (
    NotificationResponse,
    NotificationReadRequest
)

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)


# GET /notifications?user_id=1
@router.get(
    "",
    response_model=list[NotificationResponse]
)
def get_notifications(
    user_id: int,
    db: Session = Depends(get_db)
):
    notifications = (
        db.query(Notification)
        .filter(Notification.user_id == user_id)
        .order_by(Notification.timestamp.desc())
        .all()
    )

    return notifications


# POST /notifications/read
@router.post("/read")
def mark_notification_as_read(
    request: NotificationReadRequest,
    db: Session = Depends(get_db)
):
    notification = (
        db.query(Notification)
        .filter(
            Notification.id == request.notification_id
        )
        .first()
    )

    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )

    notification.read_status = True

    db.commit()

    return {
        "message": "Notification marked as read"
    }


# POST /notifications/test
@router.post("/test")
def create_test_notification(
    user_id: int,
    db: Session = Depends(get_db)
):
    notification = Notification(
        user_id=user_id,
        type="order_confirmed",
        message="Your test order has been confirmed!",
        read_status=False
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    return {
        "message": "Test notification created successfully",
        "notification_id": notification.id
    }


# POST /notifications/order-confirmed
@router.post("/order-confirmed")
def create_order_confirmation_notification(
    order_id: int,
    db: Session = Depends(get_db)
):
    # Find the order
    order = (
        db.query(Order)
        .filter(Order.id == order_id)
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    # Create notification
    notification = Notification(
        user_id=order.user_id,
        type="order_confirmed",
        message=f"Your order #{order.id} has been confirmed!",
        read_status=False
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    return {
        "message": "Order confirmation notification created",
        "notification_id": notification.id,
        "order_id": order.id
    }