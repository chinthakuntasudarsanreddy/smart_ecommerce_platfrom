from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.websocket.manager import manager


async def create_notification(
    db: Session,
    user_id: int,
    notification_type: str,
    message: str
):
    notification = Notification(
        user_id=user_id,
        type=notification_type,
        message=message,
        read_status=False
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    await manager.send_personal_message(
        user_id,
        {
            "event": notification_type,
            "notification": {
                "id": notification.id,
                "type": notification.type,
                "message": notification.message,
                "read_status": notification.read_status,
                "timestamp": str(notification.timestamp)
            }
        }
    )

    return notification


async def order_confirmed_notification(
    db: Session,
    order_id: int,
    user_id: int
):
    return await create_notification(
        db=db,
        user_id=user_id,
        notification_type="order_confirmed",
        message=f"Your order #{order_id} has been confirmed!"
    )


async def payment_success_notification(
    db: Session,
    order_id: int,
    user_id: int
):
    return await create_notification(
        db=db,
        user_id=user_id,
        notification_type="payment_success",
        message=f"Payment for order #{order_id} was successful."
    )


async def payment_failed_notification(
    db: Session,
    order_id: int,
    user_id: int
):
    return await create_notification(
        db=db,
        user_id=user_id,
        notification_type="payment_failed",
        message=f"Payment for order #{order_id} failed."
    )


async def order_shipped_notification(
    db: Session,
    order_id: int,
    user_id: int
):
    return await create_notification(
        db=db,
        user_id=user_id,
        notification_type="order_shipped",
        message=f"Your order #{order_id} has been shipped."
    )


async def order_delivered_notification(
    db: Session,
    order_id: int,
    user_id: int
):
    return await create_notification(
        db=db,
        user_id=user_id,
        notification_type="order_delivered",
        message=f"Your order #{order_id} has been delivered."
    )