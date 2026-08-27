from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from app.core.database import get_db
from app.models.notification import Notification
from app.models.user import User


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)


# ---------------------------------------------------------
# Response schema
# ---------------------------------------------------------

class NotificationResponse(BaseModel):
    id: int
    user_id: int
    order_id: int | None
    type: str
    message: str
    read_status: bool
    timestamp: object

    class Config:
        from_attributes = True


# ---------------------------------------------------------
# Mark notification as read request
# ---------------------------------------------------------

class MarkNotificationReadRequest(BaseModel):
    notification_id: int


# ---------------------------------------------------------
# GET /notifications
# Get all notifications for a user
# ---------------------------------------------------------

@router.get("/", response_model=List[NotificationResponse])
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


# ---------------------------------------------------------
# GET /notifications/unread
# Get unread notifications
# ---------------------------------------------------------

@router.get("/unread", response_model=List[NotificationResponse])
def get_unread_notifications(
    user_id: int,
    db: Session = Depends(get_db)
):
    notifications = (
        db.query(Notification)
        .filter(
            Notification.user_id == user_id,
            Notification.read_status == False
        )
        .order_by(Notification.timestamp.desc())
        .all()
    )

    return notifications


# ---------------------------------------------------------
# POST /notifications/read
# Mark one notification as read
# ---------------------------------------------------------

@router.post("/read")
def mark_notification_as_read(
    data: MarkNotificationReadRequest,
    user_id: int,
    db: Session = Depends(get_db)
):
    notification = (
        db.query(Notification)
        .filter(
            Notification.id == data.notification_id,
            Notification.user_id == user_id
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
    db.refresh(notification)

    return {
        "success": True,
        "message": "Notification marked as read",
        "notification_id": notification.id
    }


# ---------------------------------------------------------
# POST /notifications/read-all
# Mark all notifications as read
# ---------------------------------------------------------

@router.post("/read-all")
def mark_all_notifications_as_read(
    user_id: int,
    db: Session = Depends(get_db)
):
    updated = (
        db.query(Notification)
        .filter(
            Notification.user_id == user_id,
            Notification.read_status == False
        )
        .update(
            {
                Notification.read_status: True
            },
            synchronize_session=False
        )
    )

    db.commit()

    return {
        "success": True,
        "message": "All notifications marked as read",
        "updated_count": updated
    }