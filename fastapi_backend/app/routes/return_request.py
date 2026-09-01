from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.order import Order
from app.models.return_request import ReturnRequest
from app.schemas.return_request import ReturnRequestCreate

# Change this import to match your existing authentication dependency
from app.api.auth import get_current_user


router = APIRouter(
    prefix="/orders",
    tags=["Returns"]
)


RETURN_WINDOW_DAYS = 7


@router.post("/{order_id}/return")
def request_return(
    order_id: int,
    request: ReturnRequestCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    # 1. Find order
    order = (
        db.query(Order)
        .filter(
            Order.id == order_id,
            Order.user_id == current_user.id
        )
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    # 2. Check order status
    if order.status != "Delivered":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Return can only be requested for delivered orders"
        )

    # 3. Check delivered_at
    if not order.delivered_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Delivery date is not available"
        )

    # 4. Check 7-day return window
    return_deadline = (
        order.delivered_at +
        timedelta(days=RETURN_WINDOW_DAYS)
    )

    if datetime.utcnow() > return_deadline:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Return window has expired"
        )

    # 5. Check existing return request
    existing_request = (
        db.query(ReturnRequest)
        .filter(
            ReturnRequest.order_id == order.id
        )
        .first()
    )

    if existing_request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Return request already exists"
        )

    # 6. Create return request
    return_request = ReturnRequest(
        order_id=order.id,
        user_id=current_user.id,
        reason=request.reason,
        comment=request.comment,
        status="pending"
    )

    db.add(return_request)

    # 7. Update order status
    order.status = "Return Requested"

    db.commit()
    db.refresh(return_request)

    return {
        "message": "Return request submitted successfully",
        "return_request": {
            "id": return_request.id,
            "order_id": return_request.order_id,
            "reason": return_request.reason,
            "comment": return_request.comment,
            "status": return_request.status,
            "created_at": return_request.created_at
        },
        "order_status": order.status
    }