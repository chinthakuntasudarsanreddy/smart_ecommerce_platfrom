from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.models.user import User
from app.websocket.manager import manager
from app.utils.email import send_email


async def create_notification(
    db: Session,
    user_id: int,
    notification_type: str,
    message: str,
    order_id: int | None = None,
):
    notification = Notification(
        user_id=user_id,
        type=notification_type,
        message=message,
        order_id=order_id,
        read_status=False,
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    # Real-time WebSocket notification
    await manager.send_personal_message(
        user_id,
        {
            "id": notification.id,
            "user_id": notification.user_id,
            "order_id": notification.order_id,
            "type": notification.type,
            "message": notification.message,
            "read_status": notification.read_status,
            "timestamp": (
                notification.timestamp.isoformat()
                if notification.timestamp
                else None
            ),
        },
    )

    return notification


async def send_user_email(
    db: Session,
    user_id: int,
    subject: str,
    body: str,
):
    """Send an email without breaking the main API if email fails."""

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        print(f"EMAIL ERROR: User {user_id} not found")
        return

    if not user.email:
        print(f"EMAIL ERROR: User {user_id} has no email")
        return

    try:
        await send_email(
            recipient=user.email,
            subject=subject,
            body=body,
        )

        print(f"EMAIL SENT TO: {user.email}")

    except Exception as exc:
        # Email failure should not break the return/refund operation
        print("EMAIL SEND ERROR:", type(exc).__name__, str(exc))


# ============================================================
# PAYMENT NOTIFICATIONS
# ============================================================

async def payment_success_notification(
    db: Session,
    order_id: int,
    user_id: int,
):
    notification = await create_notification(
        db=db,
        user_id=user_id,
        notification_type="payment_success",
        message=f"Payment for order #{order_id} was successful.",
        order_id=order_id,
    )

    await send_user_email(
        db=db,
        user_id=user_id,
        subject=f"Payment Successful - Order #{order_id}",
        body=(
            f"Hello,\n\n"
            f"Your payment for order #{order_id} was successful.\n\n"
            f"Thank you for shopping with us."
        ),
    )

    return notification


async def payment_failed_notification(
    db: Session,
    order_id: int,
    user_id: int,
):
    notification = await create_notification(
        db=db,
        user_id=user_id,
        notification_type="payment_failed",
        message=f"Payment for order #{order_id} failed.",
        order_id=order_id,
    )

    await send_user_email(
        db=db,
        user_id=user_id,
        subject=f"Payment Failed - Order #{order_id}",
        body=(
            f"Hello,\n\n"
            f"Unfortunately, the payment for order #{order_id} failed.\n\n"
            f"Please try again."
        ),
    )

    return notification


# ============================================================
# RETURN APPROVED
# ============================================================

async def return_approved_notification(
    db: Session,
    order_id: int,
    user_id: int,
):
    notification = await create_notification(
        db=db,
        user_id=user_id,
        notification_type="return_approved",
        message=f"Your return request for order #{order_id} has been approved.",
        order_id=order_id,
    )

    await send_user_email(
        db=db,
        user_id=user_id,
        subject=f"Return Approved - Order #{order_id}",
        body=(
            f"Hello,\n\n"
            f"Your return request for order #{order_id} has been approved.\n\n"
            f"The refund process can now be completed.\n\n"
            f"Thank you."
        ),
    )

    return notification


# ============================================================
# RETURN REJECTED
# ============================================================

async def return_rejected_notification(
    db: Session,
    order_id: int,
    user_id: int,
):
    notification = await create_notification(
        db=db,
        user_id=user_id,
        notification_type="return_rejected",
        message=f"Your return request for order #{order_id} has been rejected.",
        order_id=order_id,
    )

    await send_user_email(
        db=db,
        user_id=user_id,
        subject=f"Return Rejected - Order #{order_id}",
        body=(
            f"Hello,\n\n"
            f"Your return request for order #{order_id} has been rejected.\n\n"
            f"Please check your order details for more information.\n\n"
            f"Thank you."
        ),
    )

    return notification


# ============================================================
# REFUND COMPLETED
# ============================================================

async def refund_completed_notification(
    db: Session,
    order_id: int,
    user_id: int,
):
    notification = await create_notification(
        db=db,
        user_id=user_id,
        notification_type="refund_completed",
        message=f"Your refund for order #{order_id} has been completed successfully.",
        order_id=order_id,
    )

    await send_user_email(
        db=db,
        user_id=user_id,
        subject=f"Refund Completed - Order #{order_id}",
        body=(
            f"Hello,\n\n"
            f"Your refund for order #{order_id} has been completed successfully.\n\n"
            f"Please check your payment account for the refunded amount.\n\n"
            f"Thank you for shopping with us."
        ),
    )

    return notification